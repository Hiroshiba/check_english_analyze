# check_english_analyze

英語を前処理する方法を検討する。

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

## festival

festival のインストール方法については[docs/festival.md](docs/festival.md)を参照。\
コマンドは以下の場所にある。

- macOS: `./festival/bin/festival`

## phonemizer

phonemizer のインストール・利用方法については[docs/phonemizer.md](docs/phonemizer.md)を参照。

```sh
# macOS
echo hello | uv run phonemize -b espeak -l en --espeak-library /opt/homebrew/Cellar/espeak/*/lib/libespeak.dylib # hələʊ
```

## g2p_en の利用

`g2p_en`は英語の綴りから発音記号（音素列）を推定する Python ライブラリ。

### nltk リソースの前準備

初回利用時は下記コマンドで nltk リソースをダウンロードする。

```sh
uv run python -c "import nltk; nltk.download('averaged_perceptron_tagger_eng', quiet=True)"
```

### 使い方例

上記を実行する場合は:

```sh
uv run python -c "from g2p_en import G2p; g2p = G2p(); print(g2p('hello'))" # ['HH', 'AH0', 'L', 'OW1']
```
