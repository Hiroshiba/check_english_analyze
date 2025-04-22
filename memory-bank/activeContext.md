# activeContext.md

## 現在の作業フォーカス

- Montreal Forced Aligner（MFA）ラッパー（tools/process_mfa.py）の設計・実装・コーディング規約統一
- validate_mfa_command による conda/mfa 環境/コマンドの事前検証・明確なエラー案内
- CLI/ロジック分離・型安全・docstring・logger 設計・例外処理の徹底
- ドキュメント（docs/mfa.md）最小化・案内文の統一
- 既存 tools/process\_\*.py との完全な書式・動作・エラー挙動の統一
- KPT による振り返り・徹底比較・能動的な統一の重要性の学び

## 直近の変更・決定事項

- tools/process*mfa.py を他の tools/process*\*.py と完全に同じ設計・書式・例外伝播に統一
- validate_mfa_command で conda コマンド・mfa 環境・mfa コマンドの存在を事前検証し、エラー時は docs/mfa.md 参照を案内
- argparse の nargs, help, description, print_help, sys.exit 等の細部まで統一
- ドキュメント（docs/mfa.md）は最小限のインストール・動作確認のみ記載
- KPT で「徹底比較・一括設計・能動的な統一」の重要性を明文化

## 次のステップ

- 他の CLI 追加時も既存 tools/process\_\*.py と一行単位で徹底比較し、完全統一を最初から実現
- validate 系の設計・案内文も最初に方針を決めて実装
- ドキュメント・エラー案内も最小限・統一化を徹底
- CI/CD 強化や他言語対応の検討

## 重要なパターン・好み

- CLI/ロジック分離・型安全・docstring・logger 設計・例外処理の徹底
- validate_mfa_command 等による事前検証・明確なエラー案内
- ドキュメント・案内文の最小化・統一
- 既存実装との徹底比較・一括設計
- pytest による自動テスト
- コードフォーマット・型厳密化・例外処理の徹底
- OS 差異を吸収する実装
- テスト・ドキュメント・コーディング規約の一貫性

## 学び・インサイト

- 「他の process\_\*.py と合わせる」指示は表層だけでなく、動作・出力・エラー時の挙動・引数パース・例外処理まで一行単位で厳密に一致させる必要がある
- 既存実装の全文比較・徹底模倣が修正サイクル短縮・品質向上に直結する
- validate 系の設計・案内文も最初に統一方針を決めておくと効率的
- ドキュメント・案内文も最小限・統一化がユーザー体験向上に寄与する
