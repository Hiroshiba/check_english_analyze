import logging
import sys
from pathlib import Path


def logging_setting(level: int, to_stderr: bool) -> None:
    """loggingの設定（レベル・出力先を明示指定）"""
    handler = logging.StreamHandler(sys.stderr if to_stderr else sys.stdout)
    handler.setFormatter(logging.Formatter("%(name)s - %(levelname)s :%(message)s"))
    root = logging.getLogger()
    root.handlers.clear()
    root.addHandler(handler)
    root.setLevel(level)


def get_logger(path: Path) -> logging.Logger:
    logger = logging.getLogger(path.name)
    return logger
