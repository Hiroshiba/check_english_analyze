"""
英語テキストから音素・シラブル・ストレス情報をjsonで出力するツール。

ストレス情報は同一シラブル内で同じ値となる。

Usage:
    PYTHONPATH=. uv run python tools/process_syllable.py "internationalization"
    PYTHONPATH=. uv run python tools/process_syllable.py "hello, world!" --verbose
"""

import argparse
from collections import defaultdict
from pathlib import Path

from pydantic import BaseModel

from tools.match_phonemes import match_phonemes
from tools.process_festival import PhonemeInfo as FestivalInfo
from tools.process_festival import festival as run_festival
from tools.process_phonemizer import PhonemeInfo as PhonemizerInfo
from tools.process_phonemizer import phonemizer_espeak
from utility.json_utility import print_json_list
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
    result = process_syllables(text, verbose)
    print_json_list(result)


def parse_args(args: list[str] | None = None) -> tuple[str, bool]:
    """コマンドライン引数からテキストとverboseを取得する"""
    parser = argparse.ArgumentParser()
    parser.add_argument("text", type=str, help="解析するテキスト")
    parser.add_argument(
        "--verbose", action="store_true", help="詳細なデバッグ出力をstderrに出す"
    )
    parsed = parser.parse_args(args)
    return parsed.text, parsed.verbose


def process_syllables(text: str, verbose: bool) -> list[UnifiedPhonemeInfo]:
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
    return unify_stress_by_syllable(result)


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


def unify_stress_by_syllable(
    infos: list[UnifiedPhonemeInfo],
) -> list[UnifiedPhonemeInfo]:
    """syllable_indexごとにstressを統一する"""
    grouped: defaultdict[tuple[int, int], list[UnifiedPhonemeInfo]] = defaultdict(list)
    for info in infos:
        grouped[(info.word_index, info.syllable_index)].append(info)

    unified_result: list[UnifiedPhonemeInfo] = []
    for group in grouped.values():
        stresses = [info.stress for info in group]
        try:
            unified_stress_val = get_unified_stress(stresses)
        except ValueError as e:
            raise ValueError(
                f"syllable_index={group[0].syllable_index} (word_index={group[0].word_index}, word='{group[0].word}') のストレス値が不正: {stresses}（許容パターン: 全0, または連続する単一の1か2のみ）"
            ) from e

        for info in group:
            unified_result.append(
                UnifiedPhonemeInfo(
                    word=info.word,
                    word_index=info.word_index,
                    syllable_index=info.syllable_index,
                    phoneme=info.phoneme,
                    phoneme_index=info.phoneme_index,
                    stress=unified_stress_val,
                )
            )
    unified_result.sort(key=lambda x: x.phoneme_index)
    return unified_result


def get_unified_stress(stresses: list[int]) -> int:
    """
    シラブル内のストレス値のリストから統一されたストレス値を取得する。
    有効なパターン:
    1. 全て0。
    2. 0以外の要素が全て1であり、かつ、それらが連続している。
    3. 0以外の要素が全て2であり、かつ、それらが連続している。
    上記以外の場合は ValueError を発生させる。
    """
    if not stresses:
        raise ValueError("ストレス値のリストが空です。")

    if all(s == 0 for s in stresses):
        return 0

    non_zero_stresses = [s for s in stresses if s != 0]
    # non_zero_stresses will not be empty here because all(s == 0) is checked above.

    first_non_zero = non_zero_stresses[0]
    if not all(s == first_non_zero for s in non_zero_stresses):
        raise ValueError(f"0以外のストレス値が混在しています: {non_zero_stresses}")

    if first_non_zero not in [1, 2]:
        raise ValueError(f"不正なストレス値が含まれています: {first_non_zero}")

    start_index = -1
    end_index = -1
    for i, stress_val in enumerate(stresses):
        if stress_val == first_non_zero:
            if start_index == -1:
                start_index = i
            end_index = i

    # 0以外のストレス値が連続しているかチェック
    for i in range(start_index, end_index + 1):
        if stresses[i] == 0:
            raise ValueError(
                f"0以外のストレス値 ({first_non_zero}) のブロック内に0が含まれています: {stresses}"
            )

    return first_non_zero


if __name__ == "__main__":
    main()
