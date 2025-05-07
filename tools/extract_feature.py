"""
テキストとwavファイルから、音素・シラブル・ストレス・アライメント情報を結合したjsonファイルを出力するツール。

Usage:
    PYTHONPATH=. uv run python tools/extract_feature.py --text_glob "tools/data/*.txt" --wav_glob "tools/data/*.wav" --output_dir ./hiho_aligned_output
    PYTHONPATH=. uv run python tools/extract_feature.py --text_glob "tools/data/*.txt" --wav_glob "tools/data/*.wav" --output_dir ./hiho_aligned_output --verbose
"""

from pathlib import Path
from typing import Annotated

import typer
from pydantic import BaseModel

from tools.feature_extractor_utils import add_silence_phonemes
from tools.process_alignment import LabEntry, alignment
from tools.process_syllable import UnifiedPhonemeInfo, process_syllables
from utility.file_utility import expand_glob_pattern
from utility.json_utility import write_json_list
from utility.logger_utility import get_logger, logging_setting

logger = get_logger(Path(__file__))


class AlignedPhonemeInfo(BaseModel):
    """音素・シラブル・ストレス・アライメント情報"""

    word: str
    word_index: int
    syllable_index: int
    phoneme: str
    phoneme_index: int
    stress: int
    start: float
    end: float


def main(
    text_glob: Annotated[
        str,
        typer.Argument(help="テキストファイルのglobパターン（例: tools/data/*.txt）"),
    ],
    wav_glob: Annotated[
        str, typer.Argument(help="音声ファイルのglobパターン（例: tools/data/*.wav）")
    ],
    output_dir: Annotated[Path, typer.Argument(help="出力先ディレクトリ")],
    output_textgrid_dir: Annotated[
        Path | None,
        typer.Option(
            help="TextGridファイルの出力先ディレクトリ。指定しない場合は出力しない。"
        ),
    ] = None,
    verbose: Annotated[
        bool, typer.Option(help="詳細なデバッグ出力をstderrに出す")
    ] = False,
) -> None:
    """コマンドライン引数から実行するエントリポイント"""
    logging_setting(verbose)
    phoneme_dict = extract_aligned_feature(text_glob, wav_glob, output_textgrid_dir)
    for stem, infos in phoneme_dict.items():
        json_path = Path(output_dir) / f"{stem}.json"
        write_json_list(infos, json_path)
        logger.info(f"jsonファイル出力: {json_path}")


def extract_aligned_feature(
    text_glob: str,
    wav_glob: str,
    output_textgrid_dir: Path | None = None,
) -> dict[str, list[AlignedPhonemeInfo]]:
    """音素・シラブル・ストレス・アライメント情報を抽出しファイル名ごとに返す"""
    logger.debug("verboseモード: ON")
    logger.debug(f"text_glob: {text_glob}")
    logger.debug(f"wav_glob: {wav_glob}")

    text_paths = expand_glob_pattern(text_glob, "テキストファイル")
    wav_paths = expand_glob_pattern(wav_glob, "音声ファイル")
    if len(text_paths) != len(wav_paths):
        raise ValueError(
            f"テキストファイルと音声ファイルの数が一致しません: text_paths={len(text_paths)}, wav_paths={len(wav_paths)}"
        )

    lab_dict = alignment(text_glob, wav_glob, output_textgrid_dir)
    phoneme_dict: dict[str, list[AlignedPhonemeInfo]] = {}

    for text_path in text_paths:
        stem = text_path.stem
        txt = text_path.read_text(encoding="utf-8").strip()
        unified_infos = process_syllables(txt)
        lab_entries = lab_dict.get(stem)
        if lab_entries is None:
            raise ValueError(f"lab情報が見つかりません: {stem}")
        phoneme_dict[stem] = combine_phoneme_with_lab(unified_infos, lab_entries, stem)
    return phoneme_dict


def combine_phoneme_with_lab(
    unified_infos: list[UnifiedPhonemeInfo], lab_entries: list[LabEntry], stem: str
) -> list[AlignedPhonemeInfo]:
    """音素情報とlabアライメント情報を結合する

    NOTE: extract_feature.pyのみ例外的に、音素不一致はエラーにせず警告として処理し続行する。
    """
    unified_infos = add_silence_phonemes(unified_infos)

    result = []
    n = min(len(unified_infos), len(lab_entries))
    if len(unified_infos) != len(lab_entries):
        logger.warning(
            f"音素数不一致: {stem}, lab_entries数={len(lab_entries)}, unified_infos数={len(unified_infos)}"
        )
    for i in range(n):
        info = unified_infos[i]
        lab = lab_entries[i]
        if info.phoneme != lab.phoneme:
            logger.warning(
                f"音素不一致: {stem}, phoneme_index={info.phoneme_index}, info={info.phoneme}, lab={lab.phoneme}"
            )
        result.append(
            AlignedPhonemeInfo(
                word=info.word,
                word_index=info.word_index,
                syllable_index=info.syllable_index,
                phoneme=lab.phoneme,
                phoneme_index=info.phoneme_index,
                stress=info.stress,
                start=lab.start,
                end=lab.end,
            )
        )
    return result


if __name__ == "__main__":
    typer.run(main)
