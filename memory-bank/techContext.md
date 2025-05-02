# techContext.md

## 採用技術・ライブラリ

- festival（TTS エンジン, apt/brew）
- phonemizer（PyPI, uv/pip）
- espeak（apt/brew, phonemizer バックエンド用）
- pytest（自動テスト、parametrize によるパターン網羅）
- ruff（静的解析・フォーマット）
- pydantic（型安全、データ構造厳密化）
- sexpdata（S 式パース）
- uv（Python パッケージ管理）
- 独自 logger（utility/logger_utility.py）

## 開発環境・セットアップ

- Ubuntu, macOS 両対応
- festival, espeak は各 OS のパッケージマネージャで導入
- phonemizer は uv add phonemizer で導入
- .gitignore は GitHub 公式 Python テンプレートを採用
- テストは PYTHONPATH=. uv run pytest で実行

## 技術的制約・設計方針

### festival/phonemizer 統合

- festival: シラブル取得可・ストレス強弱不可
- phonemizer+espeak: ストレス強弱取得可・シラブル不可
- match_phonemes.py で両者の音素列を適切にアライメント
- extract_feature.py で両者の出力を単語単位でマージし、「音素・シラブル・単語・ストレス強弱」を一括抽出
- symbol_mapping.json で音素マッピングを定義し、1:1、1:多、多:1 の対応関係を管理
- 統合出力は pydantic 型で厳密に管理し、テスト期待値も明示

### コーディング規約

#### 共通

- 想定外の挙動は例外を投げる
- コメント禁止（docstring 必須、意図は関数化で明確化）
- 不要な引数・変数は削除
- 命名・docstring・型ヒント・依存順の統一
- 依存が多いものを上に、依存が少ないものを下に書く
- main 関数は最上部、プライベート関数は最下部
- import 文は最上部
- API keys や credentials は扱わない

#### Python のコーディング規約

- os.path 禁止、Pathlib 推奨
- with Path.open 禁止、Path.read_text/read_bytes 推奨
- 関数の引数・返り値に型ヒント必須
- コード自動整形（ruff 等）
- pytest.mark.parametrize によるテスト網羅
- festival/phonemizer の出力仕様変更に追従できる型設計・テスト設計
- テスト・assert・パターン順序・docstring・引数順も全ファイルで統一

#### HTML のコーディング規約

- z-index はなるべく使わない
- 不要な CSS 要素は追加しない

## 依存関係

- festival, espeak, phonemizer, pytest, ruff, pydantic, sexpdata, uv

## ツール利用方針

- OS 差異を吸収しクロスプラットフォームで動作する CLI・テスト・ドキュメントを徹底
- .gitignore, テスト, フォーマット, 型安全, 例外処理を重視
- pydantic 型・logger 設計・CLI/ロジック分離・テスト期待値明示で CI の再現性・信頼性を最大化
- extract_feature.py/test_extract_feature.py による統合ロジック・テスト網羅性・コーディング規約徹底
- festival/phonemizer の出力統合・型設計・テスト設計を最優先
