# Festival

## macOS でのインストール手順

### 1. 必要ツールのインストール

```sh
brew install make
```

※ Homebrew でインストールされる GNU make は`gmake`として利用可能。

### 2. 作業ディレクトリの作成

```sh
mkdir -p ~/speech_processing/tools
cd ~/speech_processing/tools
```

### 3. speech_tools の取得・展開・削除

```sh
wget http://www.cstr.ed.ac.uk/downloads/festival/2.4/speech_tools-2.4-release.tar.gz
tar xvf speech_tools-2.4-release.tar.gz
rm speech_tools-2.4-release.tar.gz
```

### 4. speech_tools のビルド

```sh
cd speech_tools
./configure
gmake
cd ..
```

- Apple Silicon の場合、`CFLAGS="-std=gnu89"`を指定して`./configure`を実行するとよい。
- `make`ではなく`gmake`を必ず使うこと。

### 5. Apple Silicon (arm64) 対応 Makefile の作成

```sh
cp speech_tools/config/systems/x86_64_Darwin.mak speech_tools/config/systems/arm64_Darwin.mak
```

### 6. festival 本体の取得・展開・削除

```sh
wget http://www.cstr.ed.ac.uk/downloads/festival/2.4/festival-2.4-release.tar.gz
tar xvf festival-2.4-release.tar.gz
rm festival-2.4-release.tar.gz
```

### 7. festival ビルド前の Apple Silicon 対応パッチ

```sh
sed -i '' 's/finite/isfinite/g' festival/src/modules/clunits/acost.cc
```

### 8. festival 本体のビルド

```sh
cd festival
./configure
make
cd ..
```

- Apple Silicon の場合、`CFLAGS="-std=gnu89"`を指定して`./configure`を実行するとよい。

### 9. 動作確認

```sh
./festival/bin/festival --version
```
