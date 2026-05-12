"""Logging setup with rich console."""

import logging
import sys

from rich.console import Console
from rich.logging import RichHandler

console = Console(stderr=True)


def get_logger(name: str) -> logging.Logger:
    """Get a configured logger with rich output."""
    logger = logging.getLogger(name)
    if not logger.handlers:
        handler = RichHandler(
            console=console,
            rich_tracebacks=True,
            tracebacks_show_locals=False,
        )
        handler.setFormatter(logging.Formatter("%(message)s"))
        logger.addHandler(handler)
        logger.setLevel(logging.INFO)
        logger.propagate = False
    return logger