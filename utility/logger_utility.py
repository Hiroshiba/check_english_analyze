import logging
from pathlib import Path


def logging_setting() -> None:
    logging.basicConfig(
        level=logging.INFO,
        format="%(name)s - %(levelname)s :%(message)s",
    )


def get_logger(path: Path) -> logging.Logger:
    logger = logging.getLogger(path.name)
    return logger
