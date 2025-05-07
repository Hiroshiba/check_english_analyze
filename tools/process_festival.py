"""
英語テキストから音素・シラブル・ストレス情報をjsonで出力するツール。

Usage:
    PYTHONPATH=. uv run python tools/process_festival.py "internationalization"
    PYTHONPATH=. uv run python tools/process_festival.py "hello, world!" --verbose
"""

import platform
import subprocess
from pathlib import Path
from typing import Annotated

import sexpdata
import typer
from pydantic import BaseModel

from utility.json_utility import print_json_list
from utility.logger_utility import get_logger, logging_setting

logger = get_logger(Path(__file__))


class PhonemeInfo(BaseModel):
    """単語・シラブル・音素・ストレス・インデックス情報"""

    word: str
    word_index: int
    syllable_index: int
    phoneme: str
    phoneme_index: int
    stress: int


def main(
    text: Annotated[str, typer.Argument(help="解析するテキスト")],
    verbose: Annotated[
        bool, typer.Option(help="詳細なデバッグ出力をstderrに出す")
    ] = False,
) -> None:
    """コマンドライン引数から実行するエントリポイント"""
    logging_setting(verbose)
    infos = festival(text)
    print_json_list(infos)


def festival(text: str) -> list[PhonemeInfo]:
    """英語テキストから音素・シラブル・ストレス情報を抽出しPhonemeInfoリストで返す"""
    logger.debug("verboseモード: ON")
    script = build_festival_script(text)
    output = run_festival(script)
    infos = extract_sexp(output)
    return infos


def build_festival_script(text: str) -> str:
    """Festival用Schemeスクリプトを生成する"""
    return f"""(voice_cmu_us_slt_arctic_clunits)
(lex.select "cmu")

(define (phonemize line)
  (set! utterance (eval (list 'Utterance 'Text line)))
  (utt.synth utterance)
  (print (utt.relation_tree utterance "SylStructure")))

(set! lines (list "{text}"))
(mapcar (lambda (line) (phonemize line)) lines)
"""


def run_festival(script: str) -> str:
    """Festivalを実行し出力を得る"""
    system = platform.system()
    if system == "Darwin":
        cmd = ["./festival/bin/festival", "-i", "--pipe"]
    elif system == "Linux":
        cmd = ["festival", "-i", "--pipe"]
    else:
        raise RuntimeError(f"未対応OS: {system}")
    logger.debug(f"script: {script}")
    try:
        output = subprocess.check_output(
            cmd,
            input=script.encode(),
            stderr=subprocess.STDOUT,
        ).decode()
    except subprocess.CalledProcessError as e:
        raise RuntimeError("festival実行エラー") from e
    logger.debug("=== festival出力 ===\n" + output)
    return output


def extract_sexp(output: str) -> list[PhonemeInfo]:
    """Festival出力からS式部分を抽出し、PhonemeInfoリストに変換する"""
    logger.debug("=== S式抽出 ===")
    start = output.find('((("')
    if start == -1:
        raise RuntimeError("S式部分が見つかりません")
    paren = 0
    end = None
    for i, c in enumerate(output[start:], start=start):
        if c == "(":
            paren += 1
        elif c == ")":
            paren -= 1
            if paren == 0:
                end = i + 1
                break
    if end is None:
        raise RuntimeError("S式の括弧が閉じていません")
    sexp_text = output[start:end]
    logger.debug("S式: " + sexp_text)
    logger.debug("=== S式パース ===")
    try:
        sexp = sexpdata.loads(sexp_text)
    except Exception as e:
        raise RuntimeError("sexpdata.loads失敗") from e

    infos: list[PhonemeInfo] = []
    phoneme_index = 0
    syllable_index = 0
    for word_index, word_entry in enumerate(sexp):
        witem = word_entry[0][0]
        word = witem.value() if isinstance(witem, sexpdata.Symbol) else str(witem)
        has_syl = False
        for syl_entry in word_entry[1:]:
            if not (
                isinstance(syl_entry, list)
                and syl_entry
                and isinstance(syl_entry[0], list)
            ):
                continue
            key = syl_entry[0][0]
            if not (
                (isinstance(key, str) and key == "syl")
                or (isinstance(key, sexpdata.Symbol) and key.value() == "syl")
            ):
                continue
            has_syl = True
            syl_props = syl_entry[0][1]
            stress = next(
                (
                    p[1]
                    for p in syl_props
                    if isinstance(p, list)
                    and (
                        (isinstance(p[0], str) and p[0] == "stress")
                        or (
                            isinstance(p[0], sexpdata.Symbol)
                            and p[0].value() == "stress"
                        )
                    )
                ),
                None,
            )
            for ph_container in syl_entry[1:]:
                if not (
                    isinstance(ph_container, list)
                    and ph_container
                    and isinstance(ph_container[0], list)
                ):
                    continue
                psym = ph_container[0][0]
                phoneme = (
                    psym.value() if isinstance(psym, sexpdata.Symbol) else str(psym)
                )
                infos.append(
                    PhonemeInfo(
                        word=word,
                        word_index=word_index,
                        syllable_index=syllable_index,
                        phoneme=phoneme,
                        phoneme_index=phoneme_index,
                        stress=int(stress) if stress is not None else 0,
                    )
                )
                phoneme_index += 1
            syllable_index += 1
        if not has_syl:
            infos.append(
                PhonemeInfo(
                    word=word,
                    word_index=word_index,
                    syllable_index=syllable_index,
                    phoneme=word,
                    phoneme_index=phoneme_index,
                    stress=0,
                )
            )
            phoneme_index += 1
            syllable_index += 1
    return infos


if __name__ == "__main__":
    typer.run(main)
