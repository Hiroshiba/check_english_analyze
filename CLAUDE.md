# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## 開発コマンド

### パッケージ管理
```bash
uv add ライブラリ名  # 依存関係追加
```

### コード品質
```bash
uv run ruff check --fix && uv run ruff format  # 静的解析・フォーマット
```

### テスト実行
```bash
PYTHONPATH=. uv run pytest -sv                      # 通常のテスト
PYTHONPATH=. uv run pytest -sv --snapshot-update    # スナップショットテスト更新
```

### CI・自動化
```bash
# PRコメントでスナップショット更新（GitHub Actions）
/update-snapshots

# コミットメッセージでスナップショット更新
git commit -m "[update snapshots] テスト仕様変更"
```

### メインツール実行
```bash
PYTHONPATH=. uv run python tools/process_festival.py "text"     # festival音素解析
PYTHONPATH=. uv run python tools/process_phonemizer.py "text"   # phonemizerストレス解析  
PYTHONPATH=. uv run python tools/process_syllable.py "text"     # 統合音素・シラブル解析
PYTHONPATH=. uv run python tools/extract_feature.py --text_glob "*.txt" --wav_glob "*.wav" --output_dir ./output  # 音声アライメント特徴抽出
```

## プロジェクトアーキテクチャ

### コアコンセプト
英語テキストから**音素・シラブル・単語・ストレス強弱**を厳密かつ再現性高く抽出するクロスプラットフォームCLI。festival（シラブル取得）とphonermizer+espeak（ストレス強弱取得）の出力を統合し、pydantic型で厳密管理する。

### 主要コンポーネント構成

#### 統合処理パイプライン
- `tools/process_festival.py`: S式パース・シラブル抽出
- `tools/process_phonemizer.py`: ストレス強弱抽出  
- `tools/match_phonemes.py`: 動的計画法による音素列アライメント
- `tools/process_syllable.py`: 両出力の単語単位マージ・統合ロジック
- `tools/extract_feature.py`: 音声ファイルとテキストからの特徴抽出・アライメント結合

#### 音素マッピング・検証システム
- `tools/symbol_mapping.json`: festival/phonemizer音素対応定義（要素数/記号ごとブロック分割、アルファベット順ソート）
- 音素列アライメント検証: `verify_complete_alignment`関数による完全性保証
- 無音音素の強制追加: `add_silence_phonemes`で先頭・末尾無音区間統一

#### ユーティリティ・設定
- `utility/logger_utility.py`: `logging_setting`関数による一元的ログ管理
- `tools/conftest.py`: pytest設定・ログレベルverbosity連動
- `utility/file_utility.py`, `utility/json_utility.py`: 共通処理

### 重要な設計パターン

#### 厳格なコーディング規約
- **コメント禁止**（docstring必須、意図は関数化で明確化）
  - **例外**: コメントが必要な場合は日本語で記述
- **型ヒント必須**（引数・返り値すべて）
- **依存順記述**（依存多→少の順、main関数最上部、private関数最下部）
- **import順序統一**（最上部配置）
- **Pathlib強制**（os.path禁止、Path.read_text/read_bytes推奨）
- **GitHub Actions命名規約**: stepのnameは`<Setup>`, `<Build>`, `<Test>`, `<Deploy>`等のタグ + 日本語説明

#### テスト・CI戦略
- **pytest.mark.parametrize**による網羅的テストパターン
- **期待値明示**によるCI安定化・再現性最大化
- **syrupy**によるスナップショットテスト（出力仕様変更追従）
- **assert順序・パターン順序統一**（全test_*.pyファイル間で一貫性保持）

#### 例外処理ポリシー
- 通常: 音素不一致時は**raise**でエラー
- `tools/extract_feature.py`のみ例外的に**警告処理で続行**（NOTEコメントで明記）

#### データ構造・型安全
- **pydantic型**による厳密なデータ管理
- **UnifiedPhonemeInfo**等の統一データ構造
- festival/phonemizer出力仕様変更への柔軟な追従性

### 開発時の注意点

#### クロスプラットフォーム対応
- Ubuntu/macOS両対応必須
- festival, espeak-ngは各OSパッケージマネージャで導入
- パッケージ依存・OS差異の吸収

#### ログ・出力分離
- `verbose`フラグによるログレベル制御
- CLI/ロジック層の明確な分離
- 標準出力/ログ出力の責任分離

#### 音素処理の特殊性
- festival音素とphonmizer音素の対応関係理解
- symbol_mapping.jsonによる1:1、1:多、多:1マッピング
- アライメント精度とエラーハンドリングのバランス