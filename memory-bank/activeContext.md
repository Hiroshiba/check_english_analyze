# activeContext.md

## 現在の作業フォーカス

- match_phonemes.py のバグ修正および音素アライメントロジックの堅牢化
  - アライメント検証ロジックの関数切り出しによるコード品質向上
  - コーディング規約に準拠した関数責任の明確化
- GitHub Actions のワークフローファイル（.github/workflows/test.yml）の作成・設定
- Linux 環境でのテスト実行の安定化
- テストコードを Linux 環境に合わせて修正
- スナップショットテストの更新
- festival と phonemizer の音素列を適切にアライメントするモジュール（tools/match_phonemes.py）の設計・実装
- 音素列のアライメントに基づいて情報を統合するロジックの改善（tools/process_syllable.py）
- symbol_mapping.json の拡充・音素マッピングの追加
- コーディング規約・スタイルの徹底（不要なコメント削除、docstring 簡素化、例外処理の統一）
- 不整合があった場合のエラー処理の改善（警告からエラーへの変更）
- tools/process_alignment.py, tools/extract_feature.py に対する syrupy スナップショットテストの実装・運用
- 実データ（tools/data/_.txt, _.wav）を使った統合的な出力検証

## 直近の変更・決定事項

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

- 「他の process\_\*.py と合わせる」指示は表層だけでなく、動作・出力・エラー時の挙動・引数パース・例外処理・ログ出力まで一行単位で厳密に一致させる必要がある
- 既存実装の全文比較・徹底模倣が修正サイクル短縮・品質向上に直結する
- validate 系の設計・案内文も最初に統一方針を決めておくと効率的
- ドキュメント・案内文も最小限・統一化がユーザー体験向上に寄与する
