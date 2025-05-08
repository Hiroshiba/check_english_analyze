"""MFAの実行に関連する関数群"""

import shutil
import subprocess
from pathlib import Path

from utility.logger_utility import get_logger

logger = get_logger(Path(__file__))


def validate_mfa_command() -> None:
    """condaコマンド・mfa環境・mfaコマンドの存在を事前検証し、なければ例外を投げる"""
    logger.debug("condaコマンドの存在を確認")
    if shutil.which("conda") is None:
        raise RuntimeError(
            "condaコマンドが見つかりません。詳細はdocs/mfa.mdを参照してください。"
        )

    logger.debug("conda環境の一覧を取得")
    try:
        envs = subprocess.check_output(["conda", "env", "list"], text=True)
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
        result = subprocess.check_output(
            ["conda", "run", "-n", "mfa", "which", "mfa"], text=True
        )
    except Exception as e:
        raise RuntimeError(
            "mfa環境の起動に失敗しました。詳細はdocs/mfa.mdを参照してください。"
        ) from e

    if not result.strip():
        raise RuntimeError(
            "mfa環境にmfaコマンドがインストールされていません。詳細はdocs/mfa.mdを参照してください。"
        )


def ensure_model_exists(model_type: str, model_name: str) -> None:
    """モデル・辞書が存在しなければダウンロードする"""
    result = subprocess.check_output(
        ["conda", "run", "-n", "mfa", "mfa", "model", "list", model_type], text=True
    )
    logger.debug(f"{model_type}モデル一覧: {result}")

    if model_name not in result:
        logger.info(f"{model_type}モデル {model_name} をダウンロードします")
        try:
            subprocess.check_call(
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
        result = subprocess.check_output(cmd, text=True)
        logger.debug(f"コマンド実行結果: {result}")
        return result.strip()
    except subprocess.CalledProcessError as e:
        raise RuntimeError("mfa alignコマンドの実行に失敗") from e
