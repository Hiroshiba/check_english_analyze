# progress.md

## 現状動作していること

- tools/process_alignment.py を大幅に改良
  - TextGrid 形式から lab 形式（開始秒・終了秒・音素記号のスペース区切り）に出力形式を変更
  - TextGrid は一時ディレクトリに出力し、lab 形式に変換して最終出力
  - lab 形式の各行情報を pydantic.BaseModel（LabEntry）で管理
  - 関数順序を process_phonemizer.py や process_festival.py と完全に統一（main→parse_args→ ロジック本体 → サブロジック → 出力関数）
  - glob パターンによるファイル指定に対応（`--text_glob`、`--wav_glob`）
  - glob パターンを展開する処理を`expand_glob_pattern`関数として切り出し
  - 出力先ディレクトリを必須パラメータに変更（`--output_dir`に`required=True`を追加）
  - 一時ディレクトリを`tempfile.TemporaryDirectory`で自動削除するように変更
  - ログ出力を他の process\_\*.py ファイルと細部まで統一（詳細なデバッグログ、エラーロギング、コマンド実行ログなど）
  - テキストファイルと音声ファイルの数が一致しない場合のエラーハンドリングを追加
  - MFA の align コマンドに`--clean`と`--overwrite`オプションを追加
  - prepare_corpus_dir 関数で既存のディレクトリを削除してから新規作成するように修正
  - run_mfa_align 関数で出力ディレクトリが存在する場合は事前に削除するように修正
  - TextGrid ファイルの空のテキスト区間（ポーズ）を"(.)"として出力するように修正
- tools/process_festival.py, tools/process_phonemizer.py, tools/extract_feature.py で英語テキストの音素・シラブル・ストレス強弱等を抽出し、pydantic 型・logger・CLI/ロジック分離・pytest テスト・コーディング規約統一を徹底
- tools/process*mfa.py を新規実装し、他の tools/process*\*.py と完全に同じ設計・書式・例外伝播に統一
- validate_mfa_command で conda コマンド・mfa 環境・mfa コマンドの存在を事前検証し、エラー時は docs/mfa.md 参照を案内
- argparse の nargs, help, description, print_help, sys.exit 等の細部まで統一
- ドキュメント（docs/mfa.md）は最小限のインストール・動作確認のみ記載
- KPT で「徹底比較・一括設計・能動的な統一」の重要性を明文化
- 既存 tools/process\_\*.py との一行単位の徹底比較・統一を実践
- tools/process_festival.py で英語テキストから音素・シラブル・ストレス情報を Festival 経由で抽出し、word_index, phoneme_index, syllable_index を全体通し番号で付与し、pydantic 型・json 出力・logger/verbose 分離・pytest テストまで徹底
- tools/process_phonemizer.py で英語テキストから音素・ストレス強弱情報を phonemizer+espeak 経由で抽出し、word_index, phoneme_index を全体通し番号で付与し、pydantic 型・logger・CLI/ロジック分離・pytest テストまで徹底
- tools/extract_feature.py で festival/phonemizer 両方の出力を統合し、音素・シラブル・単語・ストレス強弱・各種インデックスを一括で返す関数を実装
- tools/test_extract_feature.py で pytest.mark.parametrize による厳密なテストを追加し、期待値を実装出力に完全同期
- dict.json（festival/phonemizer 音素対応辞書）の運用ルールを厳格化し、未登録音素ペアの推定・難単語（20 語以上）を解析・追加
- OS 自動判別（macOS: ./festival/bin/festival, Linux: festival）でクロスプラットフォーム対応
- festival/phonemizer の Ubuntu/macOS セットアップ手順を docs/ に反映
- .gitignore に Python 公式テンプレートを反映
- 多様なテストケースで安定動作を確認
- pytest.mark.parametrize で全テストを厳密にパターン化し、全プロパティの期待値を assert
- テスト期待値は実装出力に完全同期
- pytest による自動テストが全ての test\_\*.py で常時検証可能
- README.md に主要ツールの使い方・依存ライブラリの紹介・テスト方法を明記

## 残タスク

- シラブル・音素・ストレス・単語情報を 1 コマンドで抽出する CLI/API の実装
- ファイル出力機能や記号フィルタ機能など extract_feature.py の拡張
- phonemizer の高度な利用例やバックエンド切替の検証
- CI/CD 強化や他言語対応の検討

## 現在のステータス

- festival/phonemizer/mfa の個別出力・統合出力ともに型安全・json 出力・コーディング規約・例外処理・フォーマット・logger/verbose 分離・pytest テスト・README/ドキュメント整備まで安定動作
- validate_mfa_command で MFA 環境の事前検証・明確なエラー案内が可能
- word_index, phoneme_index, syllable_index を含む全プロパティが厳密にテスト・CI で検証されている
- festival/phonemizer ともに Ubuntu/macOS で公式パッケージ・PyPI で安定運用可能
- 記号や空白の扱いも明確化されている
- 辞書運用・難単語解析・未登録音素ペアの追加運用により網羅性・拡張性が向上
- process_alignment.py が複数ファイル対応・一時ディレクトリ自動削除・出力先必須化・詳細ログ出力により使いやすさと安定性が向上
- 共通処理を関数として切り出し、コードの再利用性と可読性を向上（例：`expand_glob_pattern`関数）

## 既知の課題

- festival: シラブル取得可・ストレス強弱不可
- phonemizer: ストレス強弱取得可・シラブル不可
- Festival の No default voice found ワーニングは依然出力される（機能自体には影響なし）
- 記号や空白を用途に応じてフィルタする必要がある
- MFA のデフォルト動作（`--clean`と`--overwrite`が False）により、明示的にオプション指定しないと以前の実行結果が残る可能性がある

## 意思決定の経緯・履歴

- print や json.dumps による見やすいデバッグ出力を重視
- logger/verbose/出力分離・pytest による自動テスト・README への手順明記
- コードフォーマット・型厳密化・例外処理（raise ... from e）を徹底
- pydantic 導入により PhonemeInfo 型で全出力を厳密に管理
- OS 差異を吸収する実装・ドキュメント・.gitignore・テストの整備を重視
- festival/phonemizer/mfa の出力統合・型設計・テスト設計を最優先
- KPT で「徹底比較・一括設計・能動的な統一」の重要性を明文化
- 外部ツール（MFA）のデフォルト動作を理解し、必要なオプションを明示的に指定することの重要性を確認
- 詳細なログ出力による処理フローの可視化を全ファイルで統一し、デバッグ・問題解決を容易に
- 一時ファイル・ディレクトリの自動削除によるクリーンな実行環境の維持を徹底
- 共通処理は関数として切り出し、コードの再利用性と可読性を向上させる方針を採用
