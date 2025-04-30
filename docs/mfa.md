# montreal-forced-aligner

## Ubuntu での Miniconda インストール

### 1. Miniconda インストーラのダウンロード

```sh
wget https://repo.anaconda.com/miniconda/Miniconda3-latest-Linux-x86_64.sh -O ~/miniconda.sh
```

### 2. Miniconda のインストール

```sh
bash ~/miniconda.sh -b -p ~/miniconda
```

### 3. conda コマンドの永続化

```sh
~/miniconda/bin/conda init bash
```

### 4. インストール確認

```sh
conda --version
```

## インストール

```sh
conda create -n mfa -c conda-forge montreal-forced-aligner
```

## 動作確認

```sh
conda run -n mfa mfa version
```
