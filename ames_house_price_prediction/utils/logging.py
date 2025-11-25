"""Logging configuration utilities."""

import sys

from loguru import logger

from ames_house_price_prediction.config.settings import LOG_FORMAT, LOG_LEVEL


def setup_logger(level: str = LOG_LEVEL, format_string: str = LOG_FORMAT) -> None:
    """Configure the logger with specified level and format.

    Args:
        level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        format_string: Format string for log messages
    """
    # Remove default logger
    logger.remove()

    # Add new logger with custom configuration
    logger.add(
        sys.stderr,
        format=format_string,
        level=level,
        colorize=True,
    )

    # Configure tqdm compatibility if available
    try:
        from tqdm import tqdm

        logger.remove()
        logger.add(
            lambda msg: tqdm.write(msg, end=""),
            format=format_string,
            level=level,
            colorize=True,
        )
    except ImportError:
        pass


# Auto-configure logger when module is imported
setup_logger()
