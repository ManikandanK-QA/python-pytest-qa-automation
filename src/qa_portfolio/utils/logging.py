"""Structured, dependency-free logging.

One line per event with timestamp, level, logger name and message. The format
is deliberately greppable so a failing CI job can be diagnosed from the raw job
log without downloading artefacts.
"""

from __future__ import annotations

import logging
from typing import Final

_LOG_FORMAT: Final = "%(asctime)s %(levelname)-8s [%(name)s] %(message)s"
_DATE_FORMAT: Final = "%Y-%m-%dT%H:%M:%S%z"

_configured = False


def configure_logging(level: str = "INFO") -> None:
    """Configure the root logger once per process."""

    global _configured
    if _configured:
        return

    handler = logging.StreamHandler()
    handler.setFormatter(logging.Formatter(fmt=_LOG_FORMAT, datefmt=_DATE_FORMAT))

    root = logging.getLogger()
    root.handlers.clear()
    root.addHandler(handler)
    root.setLevel(level.upper())

    # httpx logs every request at INFO; our client already logs the summary.
    logging.getLogger("httpx").setLevel(logging.WARNING)
    _configured = True


def get_logger(name: str) -> logging.Logger:
    """Return a namespaced logger, e.g. `get_logger("qa.api")`."""

    return logging.getLogger(name)
