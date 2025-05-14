"""
英語音声ファイルとテキストファイルを元に音素アライメントのlabファイルを出力するツール。

Usage:
    PYTHONPATH=. uv run python tools/process_alignment.py --text-glob "tools/data/*.txt" --wav-glob "tools/data/*.wav" --output-dir ./hiho_aligned_output
    PYTHONPATH=. uv run python tools/process_alignment.py --text-glob "tools/data/*.txt" --wav-glob "tools/data/*.wav" --output-dir ./hiho_aligned_output --output-textgrid-dir ./hiho_aligned_output --verbose
"""

import tempfile
from pathlib import Path
from typing import Annotated

import typer

from tools.mfa_runner import (
    ensure_model_exists,
    prepare_corpus_dir,
    run_mfa_align,
    run_mfa_g2p,
    validate_mfa_command,
)
from tools.textgrid_parser import (
    LabEntry,
    copy_textgrid_files,
    parse_textgrid_file,
    write_lab_file,
)
from utility.file_utility import expand_glob_pattern
from utility.logger_utility import get_logger, logging_setting

logger = get_logger(Path(__file__))


def main(
    text_glob: Annotated[
        str,
        typer.Option(
            ...,
            help="テキストファイルのglobパターン（例: tools/data/*.txt）",
        ),
    ],
    wav_glob: Annotated[
        str,
        typer.Option(
            ...,
            help="音声ファイルのglobパターン（例: tools/data/*.wav）",
        ),
    ],
    output_dir: Annotated[
        Path,
        typer.Option(..., help="出力先ディレクトリ"),
    ],
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
    lab_dict = alignment(text_glob, wav_glob, output_textgrid_dir)
    write_lab_files(lab_dict, output_dir)


def alignment(
    text_glob: str,
    wav_glob: str,
    output_textgrid_dir: Path | None = None,
) -> dict[str, list[LabEntry]]:
    """アライメント処理本体。各ファイル名ごとにLabEntryリストを返す"""
    logger.debug(f"text_glob: {text_glob}")
    logger.debug(f"wav_glob: {wav_glob}")

    text_paths = expand_glob_pattern(text_glob, "テキストファイル")
    wav_paths = expand_glob_pattern(wav_glob, "音声ファイル")

    validate_mfa_command()
    validate_file_counts(text_paths, wav_paths)

    acoustic_model_name = "english_us_arpa"
    existing_dictionary_name = "english_us_arpa"
    g2p_model_name = "english_us_arpa"

    ensure_model_exists("acoustic", acoustic_model_name)
    ensure_model_exists("dictionary", existing_dictionary_name)
    ensure_model_exists("g2p", g2p_model_name)

    logger.debug("一時ディレクトリを作成")
    with tempfile.TemporaryDirectory() as temp_dir:
        temp_path = Path(temp_dir)
        corpus_dir = temp_path / "mfa_corpus"
        g2p_output_dictionary_path = temp_path / "g2p_dictionary.txt"
        textgrid_dir = temp_path / "textgrid_output"

        logger.debug(f"コーパスディレクトリ: {corpus_dir}")
        logger.debug(f"G2P辞書出力パス: {g2p_output_dictionary_path}")
        logger.debug(f"TextGrid出力ディレクトリ: {textgrid_dir}")

        prepare_corpus_dir(text_paths, wav_paths, corpus_dir)

        logger.info("G2P辞書を生成中...")
        g2p_result = run_mfa_g2p(
            corpus_dir,
            g2p_model_name,
            g2p_output_dictionary_path,
        )
        logger.debug(f"G2P処理完了: {g2p_result}")

        align_result = run_mfa_align(
            corpus_dir,
            str(g2p_output_dictionary_path),
            acoustic_model_name,
            textgrid_dir,
        )
        logger.debug("MFAアライメント完了")
        logger.debug(f"MFA出力: {align_result}")

        lab_dict: dict[str, list[LabEntry]] = {}
        for textgrid_file in textgrid_dir.glob("*.TextGrid"):
            logger.debug(f"TextGridファイル変換: {textgrid_file}")
            lab_entries = parse_textgrid_file(textgrid_file)
            lab_dict[textgrid_file.stem] = lab_entries
            logger.debug(f"phones: {[entry.phoneme for entry in lab_entries]}")

        if output_textgrid_dir is not None:
            copy_textgrid_files(textgrid_dir, output_textgrid_dir)

        return lab_dict


def write_lab_files(lab_dict: dict[str, list[LabEntry]], output_dir: Path) -> None:
    """LabEntryリストのdictをlabファイルとして出力する"""
    output_dir.mkdir(exist_ok=True)
    for stem, entries in lab_dict.items():
        lab_path = output_dir / f"{stem}.lab"
        write_lab_file(entries, lab_path)
        logger.debug(f"labファイル出力: {lab_path}")


def validate_file_counts(text_paths: list[Path], wav_paths: list[Path]) -> None:
    """テキストファイルと音声ファイルの数が一致するか検証し、不一致なら例外を投げる"""
    if len(text_paths) != len(wav_paths):
        raise ValueError(
            f"テキストファイルと音声ファイルの数が一致しません: text_paths={len(text_paths)}, wav_paths={len(wav_paths)}"
        )


if __name__ == "__main__":
    typer.run(main)
