"""
Entry point for the Windows FIM agent.
"""

from __future__ import annotations

import logging
import signal
import sys
import time

from agent.fim.config import load_config
from agent.fim.reporter import FIMReporter
from agent.fim.watcher import FIMWatcher


logging.basicConfig(
    level=logging.INFO,
    format=(
        "%(asctime)s "
        "%(levelname)s "
        "%(name)s "
        "%(message)s"
    ),
)


logger = logging.getLogger(
    "orchid.fim"
)


def main() -> int:
    config = load_config()

    logger.info(
        "Starting FIM agent: %s",
        config.agent_id,
    )

    logger.info(
        "Hostname: %s",
        config.hostname,
    )

    logger.info(
        "Server: %s",
        config.server_url,
    )

    logger.info(
        "Paths: %s",
        ", ".join(config.paths),
    )

    reporter = FIMReporter(
        config
    )

    watcher = FIMWatcher(
        config,
        reporter,
    )

    stopping = False

    def stop_handler(
        signum,
        frame,
    ):
        nonlocal stopping

        if stopping:
            return

        stopping = True

        logger.info(
            "Stopping FIM agent..."
        )

        watcher.stop()

    signal.signal(
        signal.SIGINT,
        stop_handler,
    )

    if hasattr(
        signal,
        "SIGTERM",
    ):
        signal.signal(
            signal.SIGTERM,
            stop_handler,
        )

    try:
        watcher.start()

        logger.info(
            "FIM agent is monitoring."
        )

        while not stopping:
            time.sleep(1)

    except KeyboardInterrupt:
        stop_handler(
            signal.SIGINT,
            None,
        )

    except Exception:
        logger.exception(
            "FIM agent stopped because of an error."
        )

        try:
            watcher.stop()
        except Exception:
            pass

        return 1

    return 0


if __name__ == "__main__":
    sys.exit(
        main()
    )