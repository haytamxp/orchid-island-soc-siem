"""
Entry point for the real-time FIM agent.

Run:

    python -m agent.fim.main
"""

from __future__ import annotations

import logging
import sys

from agent.fim.baseline import BaselineCache
from agent.fim.config import FIMConfig
from agent.fim.reporter import FIMReporter
from agent.fim.watcher import FIMWatcher


def configure_logging() -> None:
    """
    Configure console logging suitable for an endpoint agent.
    """

    logging.basicConfig(
        level=logging.INFO,
        format=(
            "%(asctime)s "
            "%(levelname)s "
            "[%(name)s] "
            "%(message)s"
        ),
    )


def main() -> int:
    configure_logging()

    logger = logging.getLogger("fim.main")

    try:
        config = FIMConfig.from_environment()

        if not config.monitored_paths:
            logger.error(
                "No FIM paths configured. "
                "Set FIM_PATHS using ';' as separator."
            )
            return 2

        baseline_cache = BaselineCache(
            server_url=config.server_url,
            hostname=config.hostname,
            timeout=config.request_timeout_seconds,
        )

        try:
            baseline_cache.load()
        except Exception as exc:
            logger.error(
                "Unable to load FIM baselines: %s",
                exc,
            )
            return 3

        reporter = FIMReporter(
            server_url=config.server_url,
            hostname=config.hostname,
            agent_id=config.agent_id,
            timeout=config.request_timeout_seconds,
        )

        watcher = FIMWatcher(
            paths=config.monitored_paths,
            baseline_cache=baseline_cache,
            reporter=reporter,
            debounce_seconds=config.debounce_seconds,
        )

        logger.info(
            "Starting FIM agent '%s' on host '%s'",
            config.agent_id,
            config.hostname,
        )

        watcher.run_forever()

        return 0

    except Exception as exc:
        logging.getLogger("fim.main").exception(
            "FIM agent failed: %s",
            exc,
        )
        return 1


if __name__ == "__main__":
    sys.exit(main())