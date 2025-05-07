"""TextGridファイルのパースおよびlabファイル形式での出力に関連する関数群"""

import shutil
from pathlib import Path

from pydantic import BaseModel

from utility.logger_utility import get_logger

logger = get_logger(Path(__file__))


class LabEntry(BaseModel):
    """lab形式のエントリ情報（開始時間、終了時間、音素）"""

    start: float
    end: float
    phoneme: str


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
