# progress.md

## 現状動作していること

- tools/process_festival.py, tools/process_phonemizer.py, tools/extract_feature.py で英語テキストの音素・シラブル・ストレス強弱等を抽出し、pydantic 型・logger・CLI/ロジック分離・pytest テスト・コーディング規約統一を徹底
- tools/process*mfa.py を新規実装し、他の tools/process*\*.py と完全に同じ設計・書式・例外伝播に統一
- validate_mfa_command で conda コマンド・mfa 環境・mfa コマンドの存在を事前検証し、エラー時は docs/mfa.md 参照を案内
- argparse の nargs, help, description, print_help, sys.exit 等の細部まで統一
- ドキュメント（docs/mfa.md）は最小限のインストール・動作確認のみ記載
- KPT で「徹底比較・一括設計・能動的な統一」の重要性を明文化
- 既存 tools/process\_\*.py との一行単位の徹底比較・統一を実践

## 残タスク

- 他の CLI 追加時も既存 tools/process\_\*.py と一行単位で徹底比較し、完全統一を最初から実現
- validate 系の設計・案内文も最初に方針を決めて実装
- ドキュメント・エラー案内も最小限・統一化を徹底
- CI/CD 強化や他言語対応の検討

## 現在のステータス

- festival/phonemizer/mfa の個別出力・統合出力ともに型安全・json 出力・コーディング規約・例外処理・フォーマット・logger/verbose 分離・pytest テスト・README/ドキュメント整備まで安定動作
- validate_mfa_command で MFA 環境の事前検証・明確なエラー案内が可能
- 既存実装との徹底比較・一括設計・能動的な統一の重要性を KPT で明文化

## 既知の課題

- festival: シラブル取得可・ストレス強弱不可
- phonemizer: ストレス強弱取得可・シラブル不可
- Festival の No default voice found ワーニングは依然出力される（機能自体には影響なし）
- 記号や空白を用途に応じてフィルタする必要がある

## 意思決定の経緯・履歴

- print や json.dumps による見やすいデバッグ出力を重視
- logger/verbose/出力分離・pytest による自動テスト・README への手順明記
- コードフォーマット・型厳密化・例外処理（raise ... from e）を徹底
- pydantic 導入により PhonemeInfo 型で全出力を厳密に管理
- OS 差異を吸収する実装・ドキュメント・.gitignore・テストの整備を重視
- festival/phonemizer/mfa の出力統合・型設計・テスト設計を最優先
- KPT で「徹底比較・一括設計・能動的な統一」の重要性を明文化
