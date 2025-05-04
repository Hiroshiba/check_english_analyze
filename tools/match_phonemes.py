"""
2種類の音素列を受け取り、それらの対応関係を示すインデックスペアのリストを返すモジュール。
"""

import json
from pathlib import Path
from typing import Any

from utility.logger_utility import get_logger

logger = get_logger(Path(__file__))


def match_phonemes(
    festival_phonemes: list[str], phonemizer_phonemes: list[str]
) -> list[tuple[int, int]]:
    """2種類の音素列を受け取り、それらの対応関係を示すインデックスペアのリストを返す"""
    if not festival_phonemes or not phonemizer_phonemes:
        return []

    mapping_dict = load_symbol_mapping()
    alignment = align_phonemes(festival_phonemes, phonemizer_phonemes, mapping_dict)
    verify_complete_alignment(alignment, festival_phonemes, phonemizer_phonemes)
    return alignment


def load_symbol_mapping() -> dict[str, Any]:
    """symbol_mapping.jsonを読み込み、マッピング辞書を構築する"""
    mapping_path = Path(__file__).parent / "symbol_mapping.json"
    with mapping_path.open("r", encoding="utf-8") as f:
        mapping_data = json.load(f)

    single_mapping: dict[str, set[str]] = {}
    compound_mapping: dict[str, dict[str, set[str]]] = {}
    reverse_compound_mapping: dict[str, set[tuple[str, ...]]] = {}

    for entry in mapping_data:
        festival_phonemes = entry["festival"]
        phonemizer_phonemes = entry["phonemizer"]

        if len(festival_phonemes) == 1 and len(phonemizer_phonemes) == 1:
            f_ph = festival_phonemes[0]
            p_ph = phonemizer_phonemes[0]
            if f_ph not in single_mapping:
                single_mapping[f_ph] = set()
            single_mapping[f_ph].add(p_ph)

        elif len(festival_phonemes) > 1:
            f_key = "_".join(festival_phonemes)
            if f_key not in compound_mapping:
                compound_mapping[f_key] = {
                    "phonemes": set(),
                    "original": festival_phonemes,
                }

            if len(phonemizer_phonemes) == 1:
                compound_mapping[f_key]["phonemes"].add(phonemizer_phonemes[0])
            else:
                compound_mapping[f_key]["phonemes"].add("_".join(phonemizer_phonemes))

        elif len(phonemizer_phonemes) > 1:
            p_phs = tuple(phonemizer_phonemes)
            f_ph = festival_phonemes[0]

            if f_ph not in reverse_compound_mapping:
                reverse_compound_mapping[f_ph] = set()
            reverse_compound_mapping[f_ph].add(p_phs)

    return {
        "single": single_mapping,
        "compound": compound_mapping,
        "reverse_compound": reverse_compound_mapping,
    }


def align_phonemes(
    festival_phonemes: list[str],
    phonemizer_phonemes: list[str],
    mapping_dict: dict[str, Any],
) -> list[tuple[int, int]]:
    """動的計画法を使用して2つの音素列の最適なアライメントを見つける"""
    single_mapping = mapping_dict["single"]
    compound_mapping = mapping_dict["compound"]
    reverse_compound_mapping = mapping_dict["reverse_compound"]

    # DPテーブルの初期化
    # dp[i][j] = (festival_phonemes[:i]とphonemizer_phonemes[:j]の最適アライメントスコア, 前のセルへのポインタ, マッチしたインデックスペア)
    dp = []
    for _ in range(len(festival_phonemes) + 1):
        row = []
        for _ in range(len(phonemizer_phonemes) + 1):
            row.append((0, None, []))
        dp.append(row)

    # ベースケース: 空列同士のアライメント
    dp[0][0] = (0, None, [])
    for i in range(len(festival_phonemes) + 1):
        for j in range(len(phonemizer_phonemes) + 1):
            if i == 0 and j == 0:
                continue

            best_score = -float("inf")
            best_prev = None
            best_pairs = []

            # 1. 単一音素マッチング (1:1)
            if i > 0 and j > 0:
                f_ph = festival_phonemes[i - 1]
                p_ph = phonemizer_phonemes[j - 1]

                if f_ph in single_mapping and p_ph in single_mapping[f_ph]:
                    score = dp[i - 1][j - 1][0] + 1
                    if score > best_score:
                        best_score = score
                        best_prev = (i - 1, j - 1)
                        best_pairs = dp[i - 1][j - 1][2] + [(i - 1, j - 1)]

            # 2. festival側の複合音素マッチング (n:1)
            for compound_len in range(2, min(i + 1, 4)):  # 最大3音素まで考慮
                if i >= compound_len:
                    f_slice = festival_phonemes[i - compound_len : i]
                    f_key = "_".join(f_slice)

                    if j > 0 and f_key in compound_mapping:
                        p_ph = phonemizer_phonemes[j - 1]
                        if p_ph in compound_mapping[f_key]["phonemes"]:
                            score = dp[i - compound_len][j - 1][0] + compound_len
                            if score > best_score:
                                best_score = score
                                best_prev = (i - compound_len, j - 1)
                                new_pairs = [
                                    (i - compound_len + k, j - 1)
                                    for k in range(compound_len)
                                ]
                                best_pairs = dp[i - compound_len][j - 1][2] + new_pairs

            # 3. phonemizer側の複合音素マッチング (1:n)
            if i > 0:
                f_ph = festival_phonemes[i - 1]
                if f_ph in reverse_compound_mapping:
                    for p_compound in reverse_compound_mapping[f_ph]:
                        compound_len = len(p_compound)
                        if j >= compound_len:
                            p_slice = phonemizer_phonemes[j - compound_len : j]
                            if tuple(p_slice) == p_compound:
                                score = dp[i - 1][j - compound_len][0] + compound_len
                                if score > best_score:
                                    best_score = score
                                    best_prev = (i - 1, j - compound_len)
                                    new_pairs = [
                                        (i - 1, j - compound_len + k)
                                        for k in range(compound_len)
                                    ]
                                    best_pairs = (
                                        dp[i - 1][j - compound_len][2] + new_pairs
                                    )

            # 最適な選択がなければスキップ操作（ペナルティあり）
            if best_score == -float("inf"):
                if i > 0:
                    score = dp[i - 1][j][0] - 0.5  # festival側のスキップ
                    if (j == 0) or (score > best_score):
                        best_score = score
                        best_prev = (i - 1, j)
                        best_pairs = dp[i - 1][j][2]

                if j > 0:
                    score = dp[i][j - 1][0] - 0.5  # phonemizer側のスキップ
                    if (i == 0) or (score > best_score):
                        best_score = score
                        best_prev = (i, j - 1)
                        best_pairs = dp[i][j - 1][2]

            dp[i][j] = (best_score, best_prev, best_pairs)

    alignment = dp[len(festival_phonemes)][len(phonemizer_phonemes)][2]
    final_score = dp[len(festival_phonemes)][len(phonemizer_phonemes)][0]

    # 有効なマッピングが不十分な場合（スコアが0以下）はエラーを発生させる
    if not alignment or final_score <= 0:
        raise ValueError(
            f"アライメント失敗: festival={festival_phonemes}, phonemizer={phonemizer_phonemes}"
        )

    return alignment


def verify_complete_alignment(
    alignment: list[tuple[int, int]],
    festival_phonemes: list[str],
    phonemizer_phonemes: list[str],
) -> None:
    """アライメントが両方の音素列を完全にカバーしているか検証する"""
    aligned_fest_indices = {pair[0] for pair in alignment}
    aligned_phnm_indices = {pair[1] for pair in alignment}

    if len(aligned_fest_indices) != len(festival_phonemes) or len(
        aligned_phnm_indices
    ) != len(phonemizer_phonemes):
        raise ValueError(
            f"アライメント失敗: 不完全なアライメント。 "
            f"Festival: {len(aligned_fest_indices)}/{len(festival_phonemes)}, "
            f"Phonemizer: {len(aligned_phnm_indices)}/{len(phonemizer_phonemes)}"
        )
