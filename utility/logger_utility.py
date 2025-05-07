import logging
import sys
from pathlib import Path


def logging_setting(verbose: bool) -> None:
    """loggingの設定（レベルを明示指定）"""
    level = logging.DEBUG if verbose else logging.INFO
    handler = logging.StreamHandler(sys.stderr)
    handler.setFormatter(logging.Formatter("%(name)s - %(levelname)s :%(message)s"))
    root = logging.getLogger()
    root.handlers.clear()
    root.addHandler(handler)
    root.setLevel(level)


def get_logger(path: Path) -> logging.Logger:
    logger = logging.getLogger(path.name)
    return logger
