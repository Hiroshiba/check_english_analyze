"""
英語テキストから音素・シラブル・ストレス情報をjsonで出力するツール。

Usage:
    PYTHONPATH=. uv run python tools/extract_feature.py "internationalization"
    PYTHONPATH=. uv run python tools/extract_feature.py "hello, world!" --verbose
"""

import argparse
import json
from pathlib import Path

from pydantic import BaseModel

from tools.match_phonemes import match_phonemes
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

    fest_by_word = group_by_word(fest)
    phnm_by_word = group_by_word(phnm)

    result: list[UnifiedPhonemeInfo] = []
    for word in fest_by_word.keys():
        if word not in phnm_by_word:
            raise ValueError(f"単語 '{word}' がphonemizer出力に見つかりません")

        fest_phonemes = [f.phoneme for f in fest_by_word[word]]
        phnm_phonemes = [p.phoneme for p in phnm_by_word[word]]

        try:
            alignments = match_phonemes(fest_phonemes, phnm_phonemes)
        except ValueError as e:
            raise ValueError(
                f"単語 '{word}' の音素アライメントに失敗しました。symbol_mapping.jsonを確認してください。"
            ) from e

        for fest_idx, phnm_idx in alignments:
            f = fest_by_word[word][fest_idx]
            p = phnm_by_word[word][phnm_idx]
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

    result.sort(key=lambda x: x.phoneme_index)
    return result


def group_by_word(
    phoneme_infos: list[FestivalInfo] | list[PhonemizerInfo],
) -> dict[str, list]:
    """音素情報を単語ごとにグループ化する"""
    result: dict[str, list] = {}
    for info in phoneme_infos:
        if info.word not in result:
            result[info.word] = []
        result[info.word].append(info)
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


if __name__ == "__main__":
    main()
