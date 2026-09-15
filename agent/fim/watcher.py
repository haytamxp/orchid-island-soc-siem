"""
Real-time Windows FIM watcher.
"""

from __future__ import annotations

import logging
import os
import threading
import time
from pathlib import Path
from typing import Any

from watchdog.events import (
    FileSystemEventHandler,
)
from watchdog.observers import Observer

from agent.fim.config import FIMConfig
from agent.fim.hashing import (
    FileSnapshot,
    snapshot_file,
)
from agent.fim.reporter import FIMReporter


logger = logging.getLogger(
    "orchid.fim.watcher"
)


class FIMEventHandler(
    FileSystemEventHandler
):
    """
    Convert filesystem events into FIM telemetry.
    """

    def __init__(
        self,
        config: FIMConfig,
        reporter: FIMReporter,
        baseline_map: dict[str, dict[str, Any]],
    ) -> None:
        super().__init__()

        self.config = config
        self.reporter = reporter
        self.baseline_map = baseline_map

        self._last_events: dict[
            tuple[str, str],
            float,
        ] = {}

        self._lock = threading.Lock()

    def _normalize(self, path: str) -> str:
        return os.path.normcase(
            os.path.abspath(path)
        )

    def _is_monitored(self, path: str) -> bool:
        return self._normalize(path) in {
            self._normalize(monitored)
            for monitored in self.config.paths
        }

    def _should_process(
        self,
        path: str,
        change_type: str,
    ) -> bool:
        now = time.monotonic()

        key = (
            self._normalize(path),
            change_type,
        )

        with self._lock:
            previous = self._last_events.get(key)

            if (
                previous is not None
                and now - previous
                < self.config.debounce_seconds
            ):
                return False

            self._last_events[key] = now

        return True

    def _baseline_for(
        self,
        path: str,
    ) -> dict[str, Any] | None:
        return self.baseline_map.get(
            self._normalize(path)
        )

    def _reload_baseline(
        self,
        path: str,
    ) -> dict[str, Any] | None:
        try:
            baselines = self.reporter.get_baselines()

            for baseline in baselines:
                baseline_path = baseline.get(
                    "file_path"
                )

                if (
                    isinstance(baseline_path, str)
                    and self._normalize(
                        baseline_path
                    )
                    == self._normalize(path)
                ):
                    self.baseline_map[
                        self._normalize(path)
                    ] = baseline

                    return baseline

        except Exception:
            logger.exception(
                "Failed to refresh baseline for %s",
                path,
            )

        return None

    def _ensure_baseline(
        self,
        path: str,
    ) -> dict[str, Any] | None:
        existing = self._baseline_for(path)

        if existing is not None:
            return existing

        try:
            snapshot = snapshot_file(path)

            response = (
                self.reporter.register_baseline(
                    snapshot
                )
            )

            baseline = response.get(
                "baseline"
            )

            if isinstance(baseline, dict):
                self.baseline_map[
                    self._normalize(path)
                ] = baseline

                logger.info(
                    "Registered baseline: %s",
                    path,
                )

                return baseline

        except Exception:
            logger.exception(
                "Failed to register baseline: %s",
                path,
            )

        return None

    def handle_path(
        self,
        path: str,
        change_type: str,
    ) -> None:
        normalized_path = self._normalize(
            path
        )

        if not self._is_monitored(path):
            return

        if not self._should_process(
            path,
            change_type,
        ):
            return

        baseline = (
            self._baseline_for(path)
            or self._reload_baseline(path)
        )

        if baseline is None:
            baseline = self._ensure_baseline(path)

        if baseline is None:
            logger.error(
                "Ignoring event because no trusted baseline exists: %s",
                path,
            )
            return

        old_hash = baseline.get(
            "sha256"
        )

        old_size = baseline.get(
            "file_size"
        )

        snapshot: FileSnapshot | None

        try:
            snapshot = snapshot_file(path)
        except FileNotFoundError:
            snapshot = None
        except PermissionError:
            logger.exception(
                "Permission denied while reading %s",
                path,
            )
            return

        if change_type == "modified":
            if (
                snapshot is not None
                and old_hash == snapshot.sha256
            ):
                logger.debug(
                    "Ignored unchanged event: %s",
                    path,
                )
                return

        details = (
            "collector=watchdog; "
            f"hostname={self.config.hostname}; "
            f"agent_id={self.config.agent_id}; "
            "actor/process attribution is not "
            "claimed without Windows audit telemetry"
        )

        try:
            response = self.reporter.report_event(
                snapshot=snapshot,
                old_hash=old_hash,
                old_size=old_size,
                file_path=normalized_path,
                change_type=change_type,
                details=details,
            )

            logger.info(
                "FIM event stored: path=%s type=%s response=%s",
                path,
                change_type,
                response,
            )

        except Exception:
            logger.exception(
                "Failed to report FIM event: %s",
                path,
            )

    def on_modified(self, event):
        if event.is_directory:
            return

        self.handle_path(
            event.src_path,
            "modified",
        )

    def on_created(self, event):
        if event.is_directory:
            return

        self.handle_path(
            event.src_path,
            "added",
        )

    def on_deleted(self, event):
        if event.is_directory:
            return

        self.handle_path(
            event.src_path,
            "deleted",
        )


class FIMWatcher:
    """Manage the watchdog observer."""

    def __init__(
        self,
        config: FIMConfig,
        reporter: FIMReporter,
    ) -> None:
        self.config = config
        self.reporter = reporter

        self.observer = Observer()

        self.baseline_map: dict[
            str,
            dict[str, Any],
        ] = {}

    def _load_existing_baselines(
        self,
    ) -> None:
        existing = self.reporter.get_baselines()

        for baseline in existing:
            path = baseline.get(
                "file_path"
            )

            if isinstance(path, str):
                self.baseline_map[
                    os.path.normcase(
                        os.path.abspath(path)
                    )
                ] = baseline

    def register_missing_baselines(
        self,
    ) -> None:
        for path in self.config.paths:
            if not os.path.isfile(path):
                logger.warning(
                    "Configured FIM path does not exist: %s",
                    path,
                )
                continue

            normalized = os.path.normcase(
                os.path.abspath(path)
            )

            if normalized in self.baseline_map:
                logger.info(
                    "Baseline already exists: %s",
                    path,
                )
                continue

            if not self.config.register_baselines:
                logger.warning(
                    "No baseline for %s and automatic registration disabled.",
                    path,
                )
                continue

            snapshot = snapshot_file(path)

            response = (
                self.reporter.register_baseline(
                    snapshot
                )
            )

            baseline = response.get(
                "baseline"
            )

            if isinstance(baseline, dict):
                self.baseline_map[
                    normalized
                ] = baseline

                logger.info(
                    "Registered baseline: %s",
                    path,
                )

    def start(self) -> None:
        self._load_existing_baselines()

        self.register_missing_baselines()

        handler = FIMEventHandler(
            config=self.config,
            reporter=self.reporter,
            baseline_map=self.baseline_map,
        )

        watched_directories: set[str] = set()

        for path in self.config.paths:
            directory = str(
                Path(path).parent
            )

            watched_directories.add(
                directory
            )

        for directory in watched_directories:
            if not os.path.isdir(directory):
                logger.warning(
                    "Directory does not exist: %s",
                    directory,
                )
                continue

            self.observer.schedule(
                handler,
                directory,
                recursive=False,
            )

            logger.info(
                "Watching: %s",
                directory,
            )

        self.observer.start()

    def stop(self) -> None:
        self.observer.stop()
        self.observer.join(
            timeout=5
        )