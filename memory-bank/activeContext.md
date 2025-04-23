# activeContext.md

## 現在の作業フォーカス

- Montreal Forced Aligner（MFA）ラッパー（tools/process_mfa.py）の設計・実装・コーディング規約統一
- validate_mfa_command による conda/mfa 環境/コマンドの事前検証・明確なエラー案内
- CLI/ロジック分離・型安全・docstring・logger 設計・例外処理の徹底
- ドキュメント（docs/mfa.md）最小化・案内文の統一
- 既存 tools/process\_\*.py との完全な書式・動作・エラー挙動の統一
- KPT による振り返り・徹底比較・能動的な統一の重要性の学び
- dict.json（festival/phonemizer 音素対応辞書）の拡充・難単語解析・未登録音素ペアの追加運用
- festival/phonemizer の出力を組み合わせて「音素・シラブル・単語・ストレス強弱」をすべて得る統合ロジックの設計・実装（extract_feature.py）
- 統合出力のための pydantic 型設計・pytest.mark.parametrize によるテストケース設計・期待値明示（test_extract_feature.py）
- コーディング規約・テスト・ドキュメント（README.md）整備・主要ツールの CLI/ロジック分離
- テスト網羅性・assert 内容・パターン順序の統一

## 直近の変更・決定事項

- tools/process*mfa.py を他の tools/process*\*.py と完全に同じ設計・書式・例外伝播に統一
- validate_mfa_command で conda コマンド・mfa 環境・mfa コマンドの存在を事前検証し、エラー時は docs/mfa.md 参照を案内
- argparse の nargs, help, description, print_help, sys.exit 等の細部まで統一
- ドキュメント（docs/mfa.md）は最小限のインストール・動作確認のみ記載
- KPT で「徹底比較・一括設計・能動的な統一」の重要性を明文化
- dict.json の運用ルールを厳格化し、未登録音素ペアの推定・難単語（20 語以上）を解析・追加
- extract_feature.py で festival/phonemizer 両方の出力を統合し、全情報（音素・シラブル・単語・ストレス強弱・各種インデックス）を一括で返す関数を実装
- test_extract_feature.py で pytest.mark.parametrize による厳密なテストを追加し、期待値を実装出力に完全同期
- コーディング規約（引数順・関数順・docstring・型ヒント・依存順・テストパターン順序）を全ファイルで統一
- README.md に主要ツールの使い方・依存ライブラリの紹介を明記し、ドキュメントの即時参照性を向上
- festival/phonemizer の個別出力・統合出力ともに Ubuntu/macOS で安定動作・CI 再現性を確保

## 次のステップ

- 他の CLI 追加時も既存 tools/process\_\*.py と一行単位で徹底比較し、完全統一を最初から実現
- validate 系の設計・案内文も最初に方針を決めて実装
- ドキュメント・エラー案内も最小限・統一化を徹底
- dict.json を活用した音素名寄せ・バリアント吸収ロジックの設計・実装
- シラブル・音素・ストレス・単語情報を 1 コマンドで抽出する CLI/API の実装
- ファイル出力機能や記号フィルタ機能など extract_feature.py の拡張
- phonemizer の高度な利用例やバックエンド切替の検証
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

- 「他の process\_\*.py と合わせる」指示は表層だけでなく、動作・出力・エラー時の挙動・引数パース・例外処理まで一行単位で厳密に一致させる必要がある
- 既存実装の全文比較・徹底模倣が修正サイクル短縮・品質向上に直結する
- validate 系の設計・案内文も最初に統一方針を決めておくと効率的
- ドキュメント・案内文も最小限・統一化がユーザー体験向上に寄与する
- festival/phonemizer の出力を組み合わせることで「音素・シラブル・単語・ストレス強弱」を一括で得ることが可能
- OS 差異を吸収することでクロスプラットフォームな CLI ツールが実現できる
- ドキュメント・.gitignore・テストの整備が保守性・信頼性向上に直結する
- コーディング規約徹底・テスト期待値明示により CI の再現性・信頼性が大幅向上
- 辞書運用・難単語解析・未登録音素ペアの追加運用により網羅性・拡張性が向上
