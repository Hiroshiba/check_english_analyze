"""
Montreal Forced Aligner (MFA) をconda環境「mfa」から呼び出すラッパーツール。

Usage:
    PYTHONPATH=. uv run python tools/process_mfa.py version
    PYTHONPATH=. uv run python tools/process_mfa.py align ...
"""

import argparse
import shutil
import subprocess
from pathlib import Path

from utility.logger_utility import get_logger, logging_setting

logger = get_logger(Path(__file__))


def main() -> None:
    """コマンドライン引数をそのままmfaコマンドに渡して実行するエントリポイント"""
    logging_setting(level=20, to_stderr=True)
    args = parse_args()
    validate_mfa_command()
    output = run_mfa(args)
    print(output)


def parse_args() -> list[str]:
    """コマンドライン引数をすべて取得する"""
    parser = argparse.ArgumentParser()
    parser.add_argument("mfa_args", nargs="+", help="MFAコマンド引数")
    args = parser.parse_args()
    return args.mfa_args


def validate_mfa_command() -> None:
    """condaコマンド・mfa環境・mfaコマンドの存在を事前検証し、なければ例外を投げる"""
    if shutil.which("conda") is None:
        raise RuntimeError(
            "condaコマンドが見つかりません。詳細はdocs/mfa.mdを参照してください。"
        )
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
    if not any(line.split() and line.split()[0] == "mfa" for line in envs.splitlines()):
        raise RuntimeError(
            "conda環境「mfa」が存在しません。詳細はdocs/mfa.mdを参照してください。"
        )
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


def run_mfa(args: list[str]) -> str:
    """conda環境「mfa」からmfaコマンドを引数付きで実行し出力を返す"""
    result = subprocess.run(
        ["conda", "run", "-n", "mfa", "mfa"] + args,
        capture_output=True,
        text=True,
        check=True,
    )
    return result.stdout.strip()


if __name__ == "__main__":
    main()
