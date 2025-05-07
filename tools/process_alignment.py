"""
英語音声ファイルとテキストファイルを元に音素アライメントのlabファイルを出力するツール。

Usage:
    PYTHONPATH=. uv run python tools/process_alignment.py --text_glob "tools/data/*.txt" --wav_glob "tools/data/*.wav" --output_dir ./hiho_aligned_output
    PYTHONPATH=. uv run python tools/process_alignment.py --text_glob "tools/data/*.txt" --wav_glob "tools/data/*.wav" --output_dir ./hiho_aligned_output --output_textgrid --verbose
"""

import argparse
import shutil
import subprocess
import tempfile
from pathlib import Path

from pydantic import BaseModel

from utility.file_utility import expand_glob_pattern
from utility.logger_utility import get_logger, logging_setting

logger = get_logger(Path(__file__))


class LabEntry(BaseModel):
    """lab形式のエントリ情報（開始時間、終了時間、音素）"""

    start: float
    end: float
    phoneme: str


def main() -> None:
    """コマンドライン引数から実行するエントリポイント"""
    text_glob, wav_glob, output_dir, verbose, output_textgrid = parse_args()
    lab_dict = alignment(text_glob, wav_glob, output_dir, verbose, output_textgrid)
    write_lab_files(lab_dict, output_dir)


def parse_args() -> tuple[str, str, Path, bool, bool]:
    """コマンドライン引数からtext_glob, wav_glob, output_dir, verbose, output_textgridを取得する"""
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--text_glob",
        required=True,
        help="テキストファイルのglobパターン（例: tools/data/*.txt）",
    )
    parser.add_argument(
        "--wav_glob",
        required=True,
        help="音声ファイルのglobパターン（例: tools/data/*.wav）",
    )
    parser.add_argument(
        "--output_dir",
        type=Path,
        required=True,
        help="出力先ディレクトリ",
    )
    parser.add_argument(
        "--verbose", action="store_true", help="詳細なデバッグ出力をstderrに出す"
    )
    parser.add_argument(
        "--output_textgrid",
        action="store_true",
        help="TextGridファイルを出力ディレクトリにコピーする",
    )
    parsed = parser.parse_args()
    return (
        parsed.text_glob,
        parsed.wav_glob,
        parsed.output_dir,
        parsed.verbose,
        parsed.output_textgrid,
    )


def alignment(
    text_glob: str,
    wav_glob: str,
    output_dir: Path,
    verbose: bool,
    output_textgrid: bool,
) -> dict[str, list[LabEntry]]:
    """アライメント処理本体。各ファイル名ごとにLabEntryリストを返す"""
    logging_setting(level=10 if verbose else 20, to_stderr=True)
    logger.debug("verboseモード: ON")
    logger.debug(f"text_glob: {text_glob}")
    logger.debug(f"wav_glob: {wav_glob}")

    text_paths = expand_glob_pattern(text_glob, "テキストファイル")
    wav_paths = expand_glob_pattern(wav_glob, "音声ファイル")

    validate_mfa_command()
    validate_file_counts(text_paths, wav_paths)

    model_name = "english_mfa"
    dict_name = "english_mfa"
    ensure_model_exists("acoustic", model_name)
    ensure_model_exists("dictionary", dict_name)

    logger.debug("一時ディレクトリを作成")
    with tempfile.TemporaryDirectory() as temp_dir:
        temp_path = Path(temp_dir)
        corpus_dir = temp_path / "mfa_corpus"
        textgrid_dir = temp_path / "textgrid_output"
        logger.debug(f"コーパスディレクトリ: {corpus_dir}")
        logger.debug(f"TextGrid出力ディレクトリ: {textgrid_dir}")
        prepare_corpus_dir(text_paths, wav_paths, corpus_dir)
        align_result = run_mfa_align(corpus_dir, model_name, dict_name, textgrid_dir)
        logger.debug("MFAアライメント完了")
        logger.debug(f"MFA出力: {align_result}")
        lab_dict: dict[str, list[LabEntry]] = {}
        for textgrid_file in textgrid_dir.glob("*.TextGrid"):
            logger.debug(f"TextGridファイル変換: {textgrid_file}")
            lab_entries = parse_textgrid_file(textgrid_file)
            lab_dict[textgrid_file.stem] = lab_entries
            logger.debug(f"phones: {[entry.phoneme for entry in lab_entries]}")
        if output_textgrid:
            copy_textgrid_files(textgrid_dir, output_dir)
        return lab_dict


def write_lab_files(lab_dict: dict[str, list[LabEntry]], output_dir: Path) -> None:
    """LabEntryリストのdictをlabファイルとして出力する"""
    output_dir.mkdir(exist_ok=True)
    for stem, entries in lab_dict.items():
        lab_path = output_dir / f"{stem}.lab"
        write_lab_file(entries, lab_path)
        logger.debug(f"labファイル出力: {lab_path}")


def copy_textgrid_files(textgrid_dir: Path, output_dir: Path) -> None:
    """TextGridファイルをコピーする"""
    output_dir.mkdir(exist_ok=True)
    for textgrid_file in textgrid_dir.glob("*.TextGrid"):
        dst = output_dir / textgrid_file.name
        try:
            shutil.copy2(textgrid_file, dst)
        except Exception as e:
            raise RuntimeError(
                f"TextGridファイルのコピーに失敗: {textgrid_file}"
            ) from e


def validate_file_counts(text_paths: list[Path], wav_paths: list[Path]) -> None:
    """テキストファイルと音声ファイルの数が一致するか検証し、不一致なら例外を投げる"""
    if len(text_paths) != len(wav_paths):
        raise ValueError(
            f"テキストファイルと音声ファイルの数が一致しません: text_paths={len(text_paths)}, wav_paths={len(wav_paths)}"
        )


def validate_mfa_command() -> None:
    """condaコマンド・mfa環境・mfaコマンドの存在を事前検証し、なければ例外を投げる"""
    logger.debug("condaコマンドの存在を確認")
    if shutil.which("conda") is None:
        raise RuntimeError(
            "condaコマンドが見つかりません。詳細はdocs/mfa.mdを参照してください。"
        )

    logger.debug("conda環境の一覧を取得")
    try:
        envs = subprocess.run(
            ["conda", "env", "list"],
            capture_output=True,
            text=True,
            check=True,
        ).stdout
    except Exception as e:
        raise RuntimeError(
            "conda環境一覧の取得に失敗しました。詳細はdocs/mfa.mdを参照してください。"
        ) from e

    logger.debug("mfa環境の存在を確認")
    if not any(line.split() and line.split()[0] == "mfa" for line in envs.splitlines()):
        raise RuntimeError(
            "conda環境「mfa」が存在しません。詳細はdocs/mfa.mdを参照してください。"
        )

    logger.debug("mfaコマンドの存在を確認")
    try:
        result = subprocess.run(
            ["conda", "run", "-n", "mfa", "which", "mfa"],
            capture_output=True,
            text=True,
            check=True,
        )
    except Exception as e:
        raise RuntimeError(
            "mfa環境の起動に失敗しました。詳細はdocs/mfa.mdを参照してください。"
        ) from e

    if result.returncode != 0 or not result.stdout.strip():
        raise RuntimeError(
            "mfa環境にmfaコマンドがインストールされていません。詳細はdocs/mfa.mdを参照してください。"
        )


def ensure_model_exists(model_type: str, model_name: str) -> None:
    """モデル・辞書が存在しなければダウンロードする"""
    result = subprocess.run(
        ["conda", "run", "-n", "mfa", "mfa", "model", "list", model_type],
        capture_output=True,
        text=True,
        check=True,
    )
    logger.debug(f"{model_type}モデル一覧: {result.stdout}")

    if model_name not in result.stdout:
        logger.info(f"{model_type}モデル {model_name} をダウンロードします")
        try:
            subprocess.run(
                [
                    "conda",
                    "run",
                    "-n",
                    "mfa",
                    "mfa",
                    "model",
                    "download",
                    model_type,
                    model_name,
                ],
                check=True,
            )
        except Exception as e:
            raise RuntimeError(
                f"{model_type}モデル {model_name} のダウンロードに失敗"
            ) from e
    else:
        logger.debug(f"{model_type}モデル {model_name} は既に存在します")


def prepare_corpus_dir(
    text_paths: list[Path], wav_paths: list[Path], corpus_dir: Path
) -> None:
    """MFA用コーパスディレクトリを作成し、ファイルをコピーする"""
    logger.debug(f"コーパスディレクトリを作成: {corpus_dir}")
    corpus_dir.mkdir(exist_ok=True)

    for text_path, wav_path in zip(text_paths, wav_paths, strict=False):
        logger.debug(f"ファイルの存在確認: {text_path}, {wav_path}")
        if not text_path.exists():
            raise FileNotFoundError(f"テキストファイルが見つかりません: {text_path}")
        if not wav_path.exists():
            raise FileNotFoundError(f"音声ファイルが見つかりません: {wav_path}")

        wav_dst = corpus_dir / wav_path.name
        txt_dst = corpus_dir / text_path.name
        logger.debug(f"ファイルをコピー: {text_path} -> {txt_dst}")
        shutil.copy2(text_path, txt_dst)
        logger.debug(f"ファイルをコピー: {wav_path} -> {wav_dst}")
        shutil.copy2(wav_path, wav_dst)


def run_mfa_align(
    corpus_dir: Path, model_name: str, dict_name: str, output_dir: Path
) -> str:
    """mfa alignコマンドを実行し、出力を返す"""
    if output_dir.exists():
        logger.debug(f"既存の出力ディレクトリを削除: {output_dir}")
        shutil.rmtree(output_dir)

    cmd = [
        "conda",
        "run",
        "-n",
        "mfa",
        "mfa",
        "align",
        "--clean",
        "--overwrite",
        str(corpus_dir),
        dict_name,
        model_name,
        str(output_dir),
        "--beam=100",
        "--retry_beams=400",
    ]
    logger.debug(f"実行コマンド: {' '.join(cmd)}")

    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            check=True,
        )
        logger.debug(f"コマンド実行結果: {result.stdout}")
        if result.stderr:
            logger.debug(f"コマンドエラー出力: {result.stderr}")
        return result.stdout.strip()
    except subprocess.CalledProcessError as e:
        raise RuntimeError("mfa alignコマンドの実行に失敗") from e


def parse_textgrid_file(textgrid_path: Path) -> list[LabEntry]:
    """TextGridファイルを読み込んでLabEntryのリストに変換する"""
    lines = textgrid_path.read_text(encoding="utf-8").splitlines()
    entries: list[LabEntry] = []
    in_phones = False
    interval_count = 0
    i = 0
    while i < len(lines):
        line = lines[i].strip()
        if line == 'name = "phones"':
            in_phones = True
        elif in_phones and line.startswith("intervals: size ="):
            interval_count = int(line.split("=")[1].strip())
            i += 1
            for _ in range(interval_count):
                while i < len(lines) and not lines[i].strip().startswith("xmin"):
                    i += 1
                if i >= len(lines):
                    break
                xmin = float(lines[i].split("=")[1].strip())
                i += 1
                xmax = float(lines[i].split("=")[1].strip())
                i += 1
                text = lines[i].split("=")[1].strip().strip('"')
                i += 1
                if text:
                    entries.append(LabEntry(start=xmin, end=xmax, phoneme=text))
                else:
                    entries.append(LabEntry(start=xmin, end=xmax, phoneme="(.)"))
            break
        i += 1
    return entries


def write_lab_file(entries: list[LabEntry], output_path: Path) -> None:
    """LabEntryリストをlab形式でファイルに書き込む"""
    output = "\n".join(f"{e.start} {e.end} {e.phoneme}" for e in entries)
    output_path.write_text(output, encoding="utf-8")


if __name__ == "__main__":
    main()
