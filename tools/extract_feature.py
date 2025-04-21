"""
英語テキストから音素・シラブル・ストレス情報をjsonで出力するツール。

Usage:
    PYTHONPATH=. uv run python tools/extract_feature.py "internationalization"
    PYTHONPATH=. uv run python tools/extract_feature.py "hello, world!" --verbose
"""

import json
from pathlib import Path

from pydantic import BaseModel

from tools.process_festival import PhonemeInfo as FestivalInfo
from tools.process_festival import festival as run_festival
from tools.process_phonemizer import PhonemeInfo as PhonemizerInfo
from tools.process_phonemizer import phonemizer_espeak
from utility.logger_utility import get_logger, logging_setting

logger = get_logger(Path(__file__))


class UnifiedPhonemeInfo(BaseModel):
    """単語・シラブル・音素・ストレス・インデックス情報"""

    word: str
    word_index: int
    syllable_index: int
    phoneme: str
    phoneme_index: int
    stress: int


def main() -> None:
    """コマンドライン引数から実行するエントリポイント"""
    text, verbose = parse_args()
    result = extract_feature(text, verbose)
    print_phoneme_info(result)


def parse_args(args: list[str] | None = None) -> tuple[str, bool]:
    """コマンドライン引数からテキストとverboseを取得する"""
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument("text", type=str, help="解析するテキスト")
    parser.add_argument(
        "--verbose", action="store_true", help="詳細なデバッグ出力をstderrに出す"
    )
    parsed = parser.parse_args(args)
    return parsed.text, parsed.verbose


def extract_feature(text: str, verbose: bool) -> list[UnifiedPhonemeInfo]:
    """英語テキストから音素・シラブル・ストレス情報を抽出しUnifiedPhonemeInfoリストで返す"""
    logging_setting(level=10 if verbose else 20, to_stderr=True)
    fest = run_festival(text, verbose)
    phnm = phonemizer_espeak(text, verbose)

    validate(fest, phnm, verbose)

    result: list[UnifiedPhonemeInfo] = []
    for f, p in zip(fest, phnm, strict=False):
        result.append(
            UnifiedPhonemeInfo(
                word=f.word,
                word_index=f.word_index,
                syllable_index=f.syllable_index,
                phoneme=p.phoneme,
                phoneme_index=f.phoneme_index,
                stress=p.stress,
            )
        )
    return result


def print_phoneme_info(infos: list[UnifiedPhonemeInfo]) -> None:
    """UnifiedPhonemeInfoリストを見やすいJSONで標準出力する"""
    print(
        json.dumps(
            [info.model_dump() for info in infos],
            ensure_ascii=False,
            indent=2,
        )
    )


def validate(
    fest: list[FestivalInfo], phnm: list[PhonemizerInfo], verbose: bool
) -> None:
    """festival/phonemizerの単語・インデックス情報が一致しているか検証し、不一致なら詳細な例外を投げる"""
    if len(fest) != len(phnm):
        if verbose:
            logger.debug(f"要素数不一致: festival={len(fest)}, phonemizer={len(phnm)}")
            logger.debug("festival側: " + str([(f.word, f.phoneme) for f in fest]))
            logger.debug("phonemizer側: " + str([(p.word, p.phoneme) for p in phnm]))
        raise ValueError(
            f"festival/phonemizerの要素数が一致しません: festival={len(fest)}, phonemizer={len(phnm)}"
        )
    for i, (f, p) in enumerate(zip(fest, phnm, strict=False)):
        if f.word != p.word:
            if verbose:
                logger.debug(
                    f"word不一致 at index {i}: festival='{f.word}', phonemizer='{p.word}'"
                )
            raise ValueError(
                f"word不一致 at index {i}: festival='{f.word}', phonemizer='{p.word}'"
            )
        if f.word_index != p.word_index:
            if verbose:
                logger.debug(
                    f"word_index不一致 at index {i}: festival={f.word_index}, phonemizer={p.word_index}"
                )
            raise ValueError(
                f"word_index不一致 at index {i}: festival={f.word_index}, phonemizer={p.word_index}"
            )
        if f.phoneme_index != p.phoneme_index:
            if verbose:
                logger.debug(
                    f"phoneme_index不一致 at index {i}: festival={f.phoneme_index}, phonemizer={p.phoneme_index}"
                )
            raise ValueError(
                f"phoneme_index不一致 at index {i}: festival={f.phoneme_index}, phonemizer={p.phoneme_index}"
            )


if __name__ == "__main__":
    main()
