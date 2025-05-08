# activeContext.md

## 現在の作業フォーカス

- `tools`ディレクトリ以下のモジュール構成の改善
  - 各ファイルの行数を 150 行程度に抑え、可読性とメンテナンス性を向上
  - `process_alignment.py` と `match_phonemes.py` を中心に機能分割
  - 新規モジュールとして `mfa_runner.py`, `textgrid_parser.py`, `phoneme_matcher.py`, `symbol_loader.py`, `feature_extractor_utils.py` を作成
- 音素マッピングの追加検討
  - `symbol_mapping.json` にさらに必要なマッピングがないか網羅的に確認
  - 特殊な音素や記号のマッピングを強化
- アライメントロジックの継続的改善
  - `verify_complete_alignment` による検証を活かした堅牢性向上
  - エラーメッセージの改善でデバッグ容易性を向上
- CI の安定化と拡張
  - テストカバレッジの追加
  - コードフォーマットチェックの追加
  - 型チェックの追加
- Linux と macOS の環境差異を吸収するテスト設計の改善

## 直近の変更・決定事項

- `tools`ディレクトリ以下のモジュールを分割・整理
  - `process_alignment.py` から MFA 実行関連の関数を `mfa_runner.py` に移動
  - `process_alignment.py` から TextGrid パース・lab ファイル出力関連の関数を `textgrid_parser.py` に移動
  - `match_phonemes.py` から音素マッチングロジックを `phoneme_matcher.py` に移動
  - `match_phonemes.py` から `symbol_mapping.json` 読み込みロジックを `symbol_loader.py` に移動
  - `extract_feature.py` からユーティリティ関数 `add_silence_phonemes` を `feature_extractor_utils.py` に移動
  - 各メイン処理ファイル (`process_alignment.py`, `match_phonemes.py`, `extract_feature.py`) の import 文を修正
- symbol_mapping.json の大規模拡充・ソート（festival 要素数/記号ごとにブロック分割しアルファベット順に整理）
- process_syllable.py のストレス検証ロジックを「全て 0 か、連続する 1 もしくは 2 が 1 度のみ現れてそれ以外が 0 か」を許容する仕様に修正
- match_phonemes.py のバグ修正を実施
  - 音素マッピングが存在しない（または不十分な）場合でもエラーを発生させない問題を修正
  - 最終アライメントのスコア（`final_score`）を評価し、スコアが 0 以下の場合は ValueError を発生させるように変更
  - アライメント検証ロジックを `verify_complete_alignment` 関数として切り出し、単一責任の原則を適用
  - `match_phonemes` 関数内でアライメント検証を行うよう変更し、責任範囲を明確化
  - `test_match_phonemes_invalid_mapping`テストが正常に通るようになった
  - 存在しないマッピングに対して確実にエラーが発生するようになり、システムの堅牢性が向上
- GitHub Actions のワークフローファイル（.github/workflows/test.yml）を作成
  - すべてのブランチを対象に、push するたびにテストを実行するよう設定
  - リント・フォーマットのチェックを実行
  - VOICEVOX_engine のワークフローを参考に命名規則を統一
- Linux 環境でのテスト実行に対応するため、テストコードを修正
  - tools/test_festival.py のシラブルインデックスを修正
  - tools/test_phonemizer.py の音素表現を修正（`'aɪ'`を`'ᵻ'`に変更）
  - tools/test_syllable.py の音素表現とシラブルインデックスを修正
  - tools/**snapshots**/test_extract_feature/test_extract_aligned_feature_with_real_data.json のスナップショットを更新
- tools/extract_feature.py を新規実装
  - テキストと wav ファイルから音素・シラブル・ストレス・アライメント情報を結合した JSON を出力
  - tools/process_syllable.py と tools/process_alignment.py の関数を統合活用
  - 必ず先頭・末尾に無音要素を追加する設計に統一
  - 音素不一致時は例外的にエラーではなく警告として処理し続行する仕様（NOTE コメントで明記）
  - コーディングスタイルは process_alignment.py に合わせて実装
- syrupy を dev 依存として導入し、スナップショットテストを実装
- tools/conftest.py で JSON スナップショット用 fixture を定義
- tools/test_process_alignment.py で alignment 関数のスナップショットテストを実装
- tools/test_extract_feature.py で extract_aligned_feature 関数の JSON スナップショットテストを実装
- 実際のデータ（tools/data/_.txt, _.wav）を使用した統合テストを重視
- 命名規則統一のため、tools/extract_feature.py を tools/process_syllable.py にリネーム
  - テストファイルも tools/test_extract_feature.py から tools/test_process_syllable.py に変更
  - README も更新し、他の process\_\* 系ツールと命名を統一
- テストの期待値を実際の出力に合わせて修正
  - phonemizer 出力の音素変更（「ᵻ」→「aɪ」）に対応
  - festival 出力のストレス値変更に対応
  - シラブルインデックスの変更に対応
- tools/process_alignment.py を大幅に改良
  - TextGrid 形式から lab 形式への出力形式変更
  - 一時ディレクトリの自動削除機能追加
  - glob パターンによるファイル指定対応
  - MFA の align コマンドに`--clean`と`--overwrite`オプション追加
  - TextGrid ファイルの空のテキスト区間（ポーズ）を"(.)"として出力するように修正
- tools/process*mfa.py を他の tools/process*\*.py と完全に同じ設計・書式・例外伝播に統一
- validate_mfa_command で conda コマンド・mfa 環境・mfa コマンドの存在を事前検証
- process_syllable.py（旧 extract_feature.py）で festival/phonemizer 両方の出力を統合する機能実装
  - ストレス情報（stress）は同一シラブル内で必ず同じ値となる仕様を明文化・実装・テスト・ドキュメントで統一
- `utility/logger_utility.py`の`logging_setting`関数を変更し、引数を`verbose`フラグのみに統一。ログレベルは`verbose`フラグに基づいて決定し、出力先は常に`sys.stderr`に固定。
- 各`process_*.py`および`extract_feature.py`スクリプトの`main`関数および主要ロジック関数で`logging_setting`の呼び出し方を変更し、`verbose`フラグを直接渡すように修正。
- `tools/conftest.py`に`pytest_configure`フックを追加し、pytest の verbosity（`-v`オプションの有無）に応じてログレベルを設定するように変更。
- `tools/extract_feature.py`と`tools/process_alignment.py`のコマンドライン引数に`--output_textgrid_dir`を追加し、TextGrid ファイルの出力先を任意で指定できるように変更。
- `tools`ディレクトリ以下の CLI ツール（`extract_feature.py`, `process_alignment.py`, `process_festival.py`, `process_phonemizer.py`, `process_syllable.py`）に`typer`を導入し、`argparse`を置き換え。
- 上記 CLI ツールのうち、`process_festival.py`, `process_phonemizer.py`, `process_syllable.py` の `text` 引数を `typer.Argument` に修正し、Usage 通りの動作を保証。`process_alignment.py`, `extract_feature.py` は `typer.Option` のまま変更なし。
- GitHub Actions のワークフローファイル（.github/workflows/test.yml）を修正し、MFA インストール時に `joblib<1.4` を指定することで CI エラーを解消。
- MFA アライメント処理の未知語対応
  - `tools/mfa_runner.py` に `run_mfa_g2p` 関数を追加し、MFA の G2P コマンドを実行可能にした。
  - `tools/mfa_runner.py` の `run_mfa_align` が辞書ファイルパスを受け取れるように変更。
  - `tools/process_alignment.py` で `run_mfa_g2p` を呼び出し、生成された辞書を `run_mfa_align` に渡すように変更。これにより、未知語を含むテキストでもアライメントが可能になった。
  - `tools/mfa_runner.py` の `run_mfa_g2p` から不要な引数 `existing_dictionary_path_or_name` を削除。
  - `tools/process_alignment.py` から不要なコメントを削除。

## 次のステップ

- 音素マッピングの追加検討
  - `symbol_mapping.json` にさらに必要なマッピングがないか網羅的に確認
  - 特殊な音素や記号のマッピングを強化
- アライメントロジックの継続的改善
  - `verify_complete_alignment` による検証を活かした堅牢性向上
  - エラーメッセージの改善でデバッグ容易性を向上
- CI の安定化と拡張
  - テストカバレッジの追加
  - コードフォーマットチェックの追加
  - 型チェックの追加
- Linux と macOS の環境差異を吸収するテスト設計の改善

- 音素マッピングの追加検討
  - `symbol_mapping.json` にさらに必要なマッピングがないか網羅的に確認
  - 特殊な音素や記号のマッピングを強化
- アライメントロジックの継続的改善
  - `verify_complete_alignment` による検証を活かした堅牢性向上
  - エラーメッセージの改善でデバッグ容易性を向上
- CI の安定化と拡張
  - テストカバレッジの追加
  - コードフォーマットチェックの追加
  - 型チェックの追加
- Linux と macOS の環境差異を吸収するテスト設計の改善
- 他の CLI 追加時も既存 tools/process\_\*.py と一行単位で徹底比較し、完全統一を最初から実現
- validate 系の設計・案内文も最初に方針を決めて実装
- ドキュメント・エラー案内も最小限・統一化を徹底
- dict.json を活用した音素名寄せ・バリアント吸収ロジックの設計・実装

## 重要なパターン・好み

- 関数責任の明確化と単一責任の原則の適用
  - `match_phonemes.py`での`verify_complete_alignment`関数の切り出しによる責任領域の明確化
  - 検証ロジックを独立させることによる再利用性の向上
- 外部ライブラリの出力変更に柔軟に対応するテスト設計
- テスト期待値は実際の出力に合わせて更新し、CI/テストの安定性を確保
- OS 間の差異（Linux/macOS）を吸収するテスト設計

- CLI/ロジック分離・型安全・docstring・logger 設計・例外処理の徹底
- validate_mfa_command 等による事前検証・明確なエラー案内
- ドキュメント・案内文の最小化・統一
- 既存実装との徹底比較・一括設計
- pytest による自動テスト
- コードフォーマット・型厳密化・例外処理の徹底
- OS 差異を吸収する実装
- テスト・ドキュメント・コーディング規約の一貫性
- 外部ツールのデフォルト動作を理解し、必要なオプションを明示的に指定する
- 詳細なログ出力による処理フローの可視化
- 一時ファイル・ディレクトリの自動削除によるクリーンな実行環境の維持
- 共通処理は関数として切り出し、再利用性と可読性を向上
- ロギング設定の一元管理（`utility/logger_utility.py`の`logging_setting`）と、pytest の verbosity との連携（`tools/conftest.py`の`pytest_configure`）。

- 「他の process\_\*.py と合わせる」指示は表層だけでなく、動作・出力・エラー時の挙動・引数パース・例外処理・ログ出力まで一行単位で厳密に一致させる必要がある
- 既存実装の全文比較・徹底模倣が修正サイクル短縮・品質向上に直結する
- validate 系の設計・案内文も最初に統一方針を決めておくと効率的
- ドキュメント・案内文も最小限・統一化がユーザー体験向上に寄与する
