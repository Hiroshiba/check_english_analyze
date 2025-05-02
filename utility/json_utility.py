import json
from pathlib import Path
from typing import TypeVar

from pydantic import BaseModel

T = TypeVar("T", bound=BaseModel)


def write_json_list(items: list[T], output_path: Path, indent: int = 2) -> None:
    """BaseModelのリストをJSON形式でファイルに書き込む"""
    output_path.parent.mkdir(exist_ok=True, parents=True)
    output_path.write_text(
        json.dumps(
            [item.model_dump() for item in items],
            ensure_ascii=False,
            indent=indent,
        ),
        encoding="utf-8",
    )


def print_json_list(items: list[T], indent: int = 2) -> None:
    """BaseModelのリストを標準出力にJSONとして出力する"""
    print(
        json.dumps(
            [item.model_dump() for item in items],
            ensure_ascii=False,
            indent=indent,
        )
    )
