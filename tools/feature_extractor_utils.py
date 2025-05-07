"""特徴抽出処理に関連するユーティリティ関数群"""

from pathlib import Path

from tools.process_syllable import UnifiedPhonemeInfo
from utility.logger_utility import get_logger

logger = get_logger(Path(__file__))


def add_silence_phonemes(
    unified_infos: list[UnifiedPhonemeInfo],
) -> list[UnifiedPhonemeInfo]:
    """unified_infosの先頭・末尾に無音要素を追加する"""
    result = []

    result.append(
        UnifiedPhonemeInfo(
            word="",
            word_index=0,
            syllable_index=0,
            phoneme="",
            phoneme_index=0,
            stress=0,
        )
    )

    for info in unified_infos:
        result.append(
            UnifiedPhonemeInfo(
                word=info.word,
                word_index=info.word_index + 1,
                syllable_index=info.syllable_index + 1,
                phoneme=info.phoneme,
                phoneme_index=info.phoneme_index + 1,
                stress=info.stress,
            )
        )

    result.append(
        UnifiedPhonemeInfo(
            word="",
            word_index=result[-1].word_index + 1,
            syllable_index=result[-1].syllable_index + 1,
            phoneme="",
            phoneme_index=result[-1].phoneme_index + 1,
            stress=0,
        )
    )
    return result
