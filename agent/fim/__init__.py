"""
Real-time File Integrity Monitoring agent package.
"""

from agent.fim.config import FIMConfig
from agent.fim.watcher import FIMWatcher

__all__ = [
    "FIMConfig",
    "FIMWatcher",
]