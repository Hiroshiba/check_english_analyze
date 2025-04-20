import argparse
import json
import subprocess
from pathlib import Path

import sexpdata
from pydantic import BaseModel

from utility.logger_utility import get_logger, logging_setting

logging_setting()
logger = get_logger(Path(__file__))


class PhonemeInfo(BaseModel):
    """単語・シラブル・音素・ストレス情報"""

    word: str
    syllable_index: int | None
    phoneme: str | None
    stress: int | None


def main():
    """英語テキストから音素・シラブル・ストレス有無を抽出しprintする"""
    text = parse_args()
    script = build_festival_script(text)
    output = run_festival(script)
    infos = extract_sexp(output)
    print_phoneme_info(infos)


def parse_args() -> str:
    """コマンドライン引数からテキストを取得する"""
    parser = argparse.ArgumentParser()
    parser.add_argument("text", type=str, help="解析するテキスト")
    args = parser.parse_args()
    return args.text


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
    print(f"script: {script}")
    try:
        output = subprocess.check_output(
            ["./festival/bin/festival", "-i", "--pipe"],
            input=script.encode(),
            stderr=subprocess.STDOUT,
        ).decode()
    except subprocess.CalledProcessError as e:
        raise RuntimeError("festival実行エラー") from e
    print("=== festival出力 ===")
    print(output)
    return output


def extract_sexp(output: str) -> list[PhonemeInfo]:
    """Festival出力からS式部分を抽出し、PhonemeInfoリストに変換する"""
    print("=== S式抽出 ===")
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
    print(sexp_text)
    print("=== S式パース ===")
    try:
        sexp = sexpdata.loads(sexp_text)
    except Exception as e:
        raise RuntimeError("sexpdata.loads失敗") from e

    infos: list[PhonemeInfo] = []
    for word_entry in sexp:
        witem = word_entry[0][0]
        word = witem.value() if isinstance(witem, sexpdata.Symbol) else str(witem)
        has_syl = False
        for syl_idx, syl_entry in enumerate(word_entry[1:], 1):
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
                        syllable_index=syl_idx,
                        phoneme=phoneme,
                        stress=int(stress) if stress is not None else None,
                    )
                )
        if not has_syl:
            infos.append(
                PhonemeInfo(
                    word=word,
                    syllable_index=None,
                    phoneme=None,
                    stress=None,
                )
            )
    return infos


def print_phoneme_info(infos: list[PhonemeInfo]) -> None:
    """PhonemeInfoリストを見やすいJSONでprintする"""
    print(
        json.dumps([info.model_dump() for info in infos], ensure_ascii=False, indent=2)
    )


if __name__ == "__main__":
    main()
