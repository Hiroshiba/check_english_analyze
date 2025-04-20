# phonemizer

## Ubuntu でのインストール・利用

### 1. インストール

```sh
sudo apt update
sudo apt install espeak
```

### 2. 動作確認

```sh
echo hello | uv run phonemize -b espeak -l en # hələʊ
```

## macOS でのインストール・利用

### 1. インストール

```sh
brew install espeak
```

### 2. 動作確認

espeak の dylib パスを明示指定する。

```sh
echo hello | uv run phonemize -b espeak -l en --espeak-library /opt/homebrew/Cellar/espeak/*/lib/libespeak.dylib # hələʊ
```
