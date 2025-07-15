# check_english_analyze

英語を前処理する方法を検討する。

## 使い方

tools ディレクトリ配下の主要スクリプトは以下の通りです。

- `process_festival.py`  
  英語テキストから音素・シラブル・ストレス情報を抽出

  ```
  PYTHONPATH=. uv run python tools/process_festival.py "hello, world!"
  ```

- `process_phonemizer.py`  
  英語テキストから音素・ストレス情報を抽出

  ```
  PYTHONPATH=. uv run python tools/process_phonemizer.py "hello, world!"
  ```

- `process_syllable.py`  
  festival/phonemizer 両方の出力を統合し、音素・シラブル・単語・ストレス強弱を一括抽出

  ```
  PYTHONPATH=. uv run python tools/process_syllable.py "hello, world!"
  ```

- `process_alignment.py`  
  英語音声ファイルとテキストファイルを元に音素アライメントの lab ファイルを出力

  ```
  PYTHONPATH=. uv run python tools/process_alignment.py --text-glob "tools/data/*.txt" --wav-glob "tools/data/*.wav" --output-dir ./hiho_aligned_output
  ```

- `extract_feature.py`  
  テキストと wav ファイルから、音素・シラブル・ストレス・アライメント情報を結合した json ファイルを出力

  ```
  PYTHONPATH=. uv run python tools/extract_feature.py --text-glob "tools/data/*.txt" --wav-glob "tools/data/*.wav" --output-dir ./hiho_aligned_output
  ```

## 環境構築

uv を使う。

### ライブラリの追加方法

```sh
uv add ライブラリ名
```

### 静的解析・コードフォーマット

```sh
uv run ruff check --fix && uv run ruff format
```

### テスト

#### 通常のテスト実行

```sh
PYTHONPATH=. uv run pytest -sv
```

#### スナップショットテスト

syrupy を使ったスナップショットテストを導入しています。  
初回または出力仕様変更時は以下のコマンドでスナップショットを更新してください：

```sh
PYTHONPATH=. uv run pytest -sv --snapshot-update
```

## 依存ライブラリの紹介

### festival

festival のインストール方法については[docs/festival.md](docs/festival.md)を参照。\
コマンドは以下の場所にある。

- macOS: `./festival/bin/festival`

### phonemizer

phonemizer のインストール・利用方法については[docs/phonemizer.md](docs/phonemizer.md)を参照。

```sh
# macOS
echo hello | uv run phonemize -b espeak -l en --espeak-library /opt/homebrew/Cellar/espeak/*/lib/libespeak.dylib # hələʊ
```

### g2p_en の利用

`g2p_en`は英語の綴りから発音記号（音素列）を推定する Python ライブラリ。

#### nltk リソースの前準備

初回利用時は下記コマンドで nltk リソースをダウンロードする。

```sh
uv run python -c "import nltk; nltk.download('averaged_perceptron_tagger_eng', quiet=True)"
```

#### 使い方例

上記を実行する場合は:

```sh
uv run python -c "from g2p_en import G2p; g2p = G2p(); print(g2p('hello'))" # ['HH', 'AH0', 'L', 'OW1']
```

### MFA (Montreal Forced Aligner)

MFA（Montreal Forced Aligner）のインストール・利用方法については[docs/mfa.md](docs/mfa.md)を参照。
