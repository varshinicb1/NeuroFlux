"""
Structured logging for NeuroFlux engines.

Provides a preconfigured logger for engine execution tracking,
performance monitoring, and debugging.
"""

from __future__ import annotations

import logging
import sys
import time
from contextlib import contextmanager
from typing import Generator


def get_logger(name: str, level: int = logging.INFO) -> logging.Logger:
    """Get a configured logger for a NeuroFlux module.

    Args:
        name: Logger name (typically __name__ of the module).
        level: Logging level (default INFO).

    Returns:
        Configured Logger instance.
    """
    logger = logging.getLogger(f"neuroflux.{name}")
    if not logger.handlers:
        handler = logging.StreamHandler(sys.stdout)
        formatter = logging.Formatter(
            fmt="[%(asctime)s] %(levelname)-8s %(name)s — %(message)s",
            datefmt="%H:%M:%S",
        )
        handler.setFormatter(formatter)
        logger.addHandler(handler)
    logger.setLevel(level)
    return logger


@contextmanager
def timed_section(logger: logging.Logger, section_name: str) -> Generator[None, None, None]:
    """Context manager to time a code section and log the duration.

    Args:
        logger: Logger to use.
        section_name: Name of the section being timed.

    Yields:
        None. Logs start and completion with elapsed time.

    Example:
        >>> with timed_section(logger, "MEC solve"):
        ...     solver.solve()
        [12:34:56] INFO neuroflux.analytical — MEC solve completed in 12.3 ms
    """
    logger.info("Starting %s...", section_name)
    start = time.perf_counter()
    try:
        yield
    finally:
        elapsed_ms = (time.perf_counter() - start) * 1000.0
        logger.info("%s completed in %.1f ms", section_name, elapsed_ms)
