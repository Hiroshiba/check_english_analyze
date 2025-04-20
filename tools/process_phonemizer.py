"""
英語テキストから音素・ストレス情報をjsonで出力するツール。

Usage:
    PYTHONPATH=. uv run python tools/process_phonemizer.py "internationalization"
    PYTHONPATH=. uv run python tools/process_phonemizer.py "hello, world!" --verbose
"""

import argparse
import json
import re
from pathlib import Path

from phonemizer import phonemize
from phonemizer.separator import Separator
from pydantic import BaseModel

from utility.logger_utility import get_logger, logging_setting

logger = get_logger(Path(__file__))


class PhonemeInfo(BaseModel):
    """単語・音素・ストレス情報"""

    word: str
    phoneme: str
    stress: int


def main() -> None:
    """コマンドライン引数から実行するエントリポイント"""
    text, verbose = parse_args()
    infos = phonemizer_espeak(text, verbose)
    print_phoneme_info(infos)


def parse_args(args: list[str] | None = None) -> tuple[str, bool]:
    """コマンドライン引数からテキストとverboseを取得する"""
    parser = argparse.ArgumentParser()
    parser.add_argument("text", type=str, help="解析するテキスト")
    parser.add_argument(
        "--verbose", action="store_true", help="詳細なデバッグ出力をstderrに出す"
    )
    parsed = parser.parse_args(args)
    return parsed.text, parsed.verbose


def phonemizer_espeak(text: str, verbose: bool) -> list[PhonemeInfo]:
    """英語テキストから音素・ストレス情報を抽出しPhonemeInfoリストで返す"""
    logging_setting(level=10 if verbose else 20, to_stderr=True)
    logger.debug("verboseモード: ON")
    logger.debug(f"text: {text}")

    words = split_words(text)
    logger.debug(f"words: {words}")

    phones = phonemize(
        words,
        language="en-us",
        backend="espeak",
        separator=Separator(phone=" ", word=""),
        strip=True,
        with_stress=True,
        njobs=1,
        preserve_punctuation=True,
    )
    logger.debug(f"phones: {phones}")

    infos: list[PhonemeInfo] = []
    for word, phone_str in zip(words, phones, strict=False):
        if not isinstance(phone_str, str):
            raise RuntimeError("phonemize()の戻り値がstr型でない")
        for ph, st, w in parse_phoneme(phone_str, word):
            if not ph or not w:
                continue
            infos.append(
                PhonemeInfo(
                    word=w,
                    phoneme=ph,
                    stress=st,
                )
            )
    return infos


def split_words(text: str) -> list[str]:
    """テキストを単語・句読点ごとに分割する"""
    return re.findall(r"[A-Za-z0-9]+|[.,!?]", text)


def parse_phoneme(p: str, orig_word: str) -> list[tuple[str, int, str]]:
    """phonemizer出力を(phoneme, stress, word)に分解する"""
    result: list[tuple[str, int, str]] = []
    for token in p.split():
        stress = 0
        base = token
        if "ˈ" in base:
            base = base.replace("ˈ", "")
            stress = 1
        elif "ˌ" in base:
            base = base.replace("ˌ", "")
            stress = 2
        m = re.match(r"^(.+?)([.,!?])$", base)
        if m:
            ph, punct = m.group(1), m.group(2)
            if ph:
                result.append((ph, stress, orig_word))
            result.append((punct, 0, punct))
        else:
            result.append((base, stress, orig_word))
    return result


def print_phoneme_info(infos: list[PhonemeInfo]) -> None:
    """PhonemeInfoリストを見やすいJSONで標準出力する"""
    print(
        json.dumps(
            [info.model_dump() for info in infos],
            ensure_ascii=False,
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
