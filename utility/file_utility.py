import glob
from pathlib import Path


def expand_glob_pattern(pattern: str, file_type: str) -> list[Path]:
    """globパターンを展開してPathオブジェクトのリストを返す"""
    paths = [Path(p) for p in sorted(glob.glob(pattern))]
    if not paths:
        raise ValueError(f"{file_type}が見つかりません: {pattern}")
    return paths
