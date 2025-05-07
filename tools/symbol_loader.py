"""symbol_mapping.jsonの読み込みと解釈を行う関数群"""

import json
from pathlib import Path
from typing import Any

from utility.logger_utility import get_logger

logger = get_logger(Path(__file__))


def load_symbol_mapping() -> dict[str, Any]:
    """symbol_mapping.jsonを読み込み、マッピング辞書を構築する"""
    mapping_path = Path(__file__).parent / "symbol_mapping.json"
    with mapping_path.open("r", encoding="utf-8") as f:
        mapping_data = json.load(f)

    single_mapping: dict[str, set[str]] = {}
    compound_mapping: dict[str, dict[str, Any]] = {}
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
