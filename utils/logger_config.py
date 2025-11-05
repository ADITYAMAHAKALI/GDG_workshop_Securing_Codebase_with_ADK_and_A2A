# utils/logger_config.py
import logging
import sys


def setup_logger(name: str) -> logging.Logger:
    """Create a color-coded, timestamped logger for agents."""
    logger = logging.getLogger(name)
    logger.setLevel(logging.INFO)
    if not logger.handlers:
        handler = logging.StreamHandler(sys.stdout)
        formatter = logging.Formatter(
            fmt="%(asctime)s | %(name)-15s | %(levelname)-8s | %(message)s",
            datefmt="%H:%M:%S"
        )
        handler.setFormatter(formatter)
        logger.addHandler(handler)
    return logger
