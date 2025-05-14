# Flite

## Linux/macOS でのインストール手順

### 1. 必要ツールのインストール

**macOS の場合：**

```sh
brew install make
```

※ Homebrew でインストールされる GNU make は`gmake`として利用可能。

**Linux の場合：**

```sh
sudo apt update
sudo apt install build-essential git
```

### 2. ソースコードの取得

```sh
git clone https://github.com/festvox/flite.git
cd flite
```

### 3. ビルド

```sh
./configure --with-audio=none
```

**macOS の場合：**

```sh
gmake
```

**Linux の場合：**

```sh
make
```

### 4. 動作確認

```sh
./flite/bin/t2p "hello, world" # pau hh ax l ow1 pau w er1 l d pau
```
