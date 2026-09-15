"""
Real-time FIM watcher.

Uses watchdog to receive filesystem notifications and then verifies file
content through SHA-256 before reporting a security event.
"""

from __future__ import annotations

import logging
import os
import time
from pathlib import Path
from threading import Lock

from watchdog.events import FileSystemEventHandler
from watchdog.observers import Observer

from backend.services.fim import severity_for_path

from agent.fim.baseline import BaselineCache
from agent.fim.hashing import snapshot_file
from agent.fim.reporter import FIMReporter


LOGGER = logging.getLogger("fim.watcher")


class _FileEventHandler(FileSystemEventHandler):
    """
    Converts watchdog events into FIM events.
    """

    def __init__(
        self,
        watcher: "FIMWatcher",
    ) -> None:
        super().__init__()

        self.watcher = watcher

    def on_modified(self, event) -> None:
        if not event.is_directory:
            self.watcher.handle_modified(event.src_path)

    def on_created(self, event) -> None:
        if not event.is_directory:
            self.watcher.handle_created(event.src_path)

    def on_deleted(self, event) -> None:
        if not event.is_directory:
            self.watcher.handle_deleted(event.src_path)

    def on_moved(self, event) -> None:
        if not event.is_directory:
            self.watcher.handle_deleted(event.src_path)
            self.watcher.handle_created(event.dest_path)


class FIMWatcher:
    """
    Watches configured files/directories and sends verified events.
    """

    def __init__(
        self,
        paths: tuple[str, ...],
        baseline_cache: BaselineCache,
        reporter: FIMReporter,
        debounce_seconds: float = 1.0,
    ) -> None:
        self.paths = tuple(
            str(Path(path).expanduser().resolve())
            for path in paths
        )

        self.baseline_cache = baseline_cache
        self.reporter = reporter
        self.debounce_seconds = debounce_seconds

        self._last_events: dict[tuple[str, str], float] = {}
        self._event_lock = Lock()

        self.observer = Observer()

    def start(self) -> None:
        """
        Start filesystem monitoring.
        """

        handler = _FileEventHandler(self)

        watched = 0

        for configured_path in self.paths:
            if os.path.isdir(configured_path):
                self.observer.schedule(
                    handler,
                    configured_path,
                    recursive=True,
                )

                watched += 1
                LOGGER.info(
                    "Watching directory: %s",
                    configured_path,
                )

                continue

            parent = os.path.dirname(configured_path)

            if not parent:
                continue

            if os.path.isdir(parent):
                self.observer.schedule(
                    handler,
                    parent,
                    recursive=False,
                )

                watched += 1
                LOGGER.info(
                    "Watching file: %s",
                    configured_path,
                )
            else:
                LOGGER.warning(
                    "Parent directory does not exist: %s",
                    parent,
                )

        if watched == 0:
            raise RuntimeError(
                "No valid FIM paths/directories were found"
            )

        self.observer.start()

        LOGGER.info(
            "FIM watcher started with %d watch target(s)",
            watched,
        )

    def stop(self) -> None:
        """
        Stop the filesystem observer.
        """

        self.observer.stop()
        self.observer.join(timeout=5)

        LOGGER.info("FIM watcher stopped")

    def run_forever(self) -> None:
        """
        Start and block until interrupted.
        """

        self.start()

        try:
            while self.observer.is_alive():
                time.sleep(1)
        except KeyboardInterrupt:
            LOGGER.info("FIM watcher interrupted")
        finally:
            self.stop()

    def _is_monitored(self, path: str) -> bool:
        """
        Return True when an event path matches one of the configured paths.
        """

        normalized_path = str(
            Path(path).expanduser().resolve()
        )

        for configured in self.paths:
            if os.path.isdir(configured):
                try:
                    common = os.path.commonpath(
                        [normalized_path, configured]
                    )
                except ValueError:
                    continue

                if common == configured:
                    return True

            elif normalized_path == configured:
                return True

        return False

    def _debounced(
        self,
        path: str,
        change_type: str,
    ) -> bool:
        """
        Suppress duplicate filesystem events generated by one operation.
        """

        key = (path, change_type)
        now = time.monotonic()

        with self._event_lock:
            previous = self._last_events.get(key)

            if (
                previous is not None
                and now - previous < self.debounce_seconds
            ):
                return True

            self._last_events[key] = now

        return False

    def _report(
        self,
        *,
        path: str,
        change_type: str,
        old_hash: str | None,
        new_hash: str | None,
        old_size: int | None,
        new_size: int | None,
    ) -> None:
        severity = severity_for_path(
            path,
            change_type,
        )

        self.reporter.report(
            file_path=path,
            change_type=change_type,
            old_hash=old_hash,
            new_hash=new_hash,
            old_size=old_size,
            new_size=new_size,
            severity=severity,
            details=(
                f"Real-time FIM event detected: "
                f"{change_type}"
            ),
        )

    def handle_modified(self, path: str) -> None:
        if not self._is_monitored(path):
            return

        if self._debounced(path, "modified"):
            return

        baseline = self.baseline_cache.get(
            str(Path(path).expanduser().resolve())
        )

        if baseline is None:
            LOGGER.debug(
                "Ignoring modification without baseline: %s",
                path,
            )
            return

        current = snapshot_file(path)

        if current is None:
            return

        if current.sha256 == baseline.sha256:
            return

        LOGGER.warning(
            "FIM modification detected: %s",
            path,
        )

        self._report(
            path=current.path,
            change_type="modified",
            old_hash=baseline.sha256,
            new_hash=current.sha256,
            old_size=baseline.file_size,
            new_size=current.size,
        )

    def handle_created(self, path: str) -> None:
        if not self._is_monitored(path):
            return

        if self._debounced(path, "created"):
            return

        normalized_path = str(
            Path(path).expanduser().resolve()
        )

        if self.baseline_cache.contains(normalized_path):
            self.handle_modified(normalized_path)
            return

        current = snapshot_file(normalized_path)

        if current is None:
            return

        LOGGER.warning(
            "FIM file creation detected: %s",
            normalized_path,
        )

        self._report(
            path=current.path,
            change_type="added",
            old_hash=None,
            new_hash=current.sha256,
            old_size=None,
            new_size=current.size,
        )

    def handle_deleted(self, path: str) -> None:
        if not self._is_monitored(path):
            return

        if self._debounced(path, "deleted"):
            return

        normalized_path = str(
            Path(path).expanduser().resolve()
        )

        baseline = self.baseline_cache.get(
            normalized_path
        )

        if baseline is None:
            LOGGER.debug(
                "Ignoring deletion without baseline: %s",
                normalized_path,
            )
            return

        LOGGER.warning(
            "FIM deletion detected: %s",
            normalized_path,
        )

        self._report(
            path=normalized_path,
            change_type="deleted",
            old_hash=baseline.sha256,
            new_hash=None,
            old_size=baseline.file_size,
            new_size=None,
        )