"""
2種類の音素列を受け取り、それらの対応関係を示すインデックスペアのリストを返すモジュール。
"""

from pathlib import Path

from tools.phoneme_matcher import align_phonemes, verify_complete_alignment
from tools.symbol_loader import load_symbol_mapping
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
