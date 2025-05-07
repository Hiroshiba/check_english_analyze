"""
英語テキストから音素・ストレス情報をjsonで出力するツール。

Usage:
    PYTHONPATH=. uv run python tools/process_phonemizer.py "internationalization"
    PYTHONPATH=. uv run python tools/process_phonemizer.py "hello, world!" --verbose
"""

import glob
import os
import platform
import re
from pathlib import Path
from typing import Annotated

import typer
from phonemizer import phonemize
from phonemizer.separator import Separator
from pydantic import BaseModel

from utility.json_utility import print_json_list
from utility.logger_utility import get_logger, logging_setting

logger = get_logger(Path(__file__))


class PhonemeInfo(BaseModel):
    """単語・音素・ストレス・インデックス情報"""

    word: str
    word_index: int
    phoneme: str
    phoneme_index: int
    stress: int


def main(
    text: Annotated[str, typer.Argument(help="解析するテキスト")],
    verbose: Annotated[
        bool, typer.Option(help="詳細なデバッグ出力をstderrに出す")
    ] = False,
) -> None:
    """コマンドライン引数から実行するエントリポイント"""
    logging_setting(verbose)
    infos = phonemizer_espeak(text)
    print_json_list(infos)


def phonemizer_espeak(text: str) -> list[PhonemeInfo]:
    """英語テキストから音素・ストレス情報を抽出しPhonemeInfoリストで返す"""
    logger.debug("verboseモード: ON")
    logger.debug(f"text: {text}")

    words = split_words(text)
    logger.debug(f"words: {words}")

    set_espeak_library_for_macos()

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
    phoneme_index = 0
    for word_index, (word, phone_str) in enumerate(zip(words, phones, strict=False)):
        if not isinstance(phone_str, str):
            raise RuntimeError("phonemize()の戻り値がstr型でない")
        for ph, st, w in parse_phoneme(phone_str, word):
            if not ph or not w:
                continue
            infos.append(
                PhonemeInfo(
                    word=w,
                    word_index=word_index,
                    phoneme=ph,
                    phoneme_index=phoneme_index,
                    stress=st,
                )
            )
            phoneme_index += 1
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


def set_espeak_library_for_macos() -> None:
    """macOS用にespeak dylibパスを環境変数にセット。なければwarning出力"""
    if platform.system() != "Darwin":
        return
    dylib_paths = glob.glob("/opt/homebrew/Cellar/espeak/*/lib/libespeak.dylib")
    if dylib_paths:
        os.environ["PHONEMIZER_ESPEAK_LIBRARY"] = dylib_paths[0]
    else:
        logger.warning(
            "espeak dylibが見つかりません: /opt/homebrew/Cellar/espeak/*/lib/libespeak.dylib"
        )


if __name__ == "__main__":
    typer.run(main)
