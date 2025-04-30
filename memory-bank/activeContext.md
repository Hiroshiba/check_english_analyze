# activeContext.md

## 現在の作業フォーカス

- Montreal Forced Aligner（MFA）ラッパー（tools/process_mfa.py）の設計・実装・コーディング規約統一
- validate_mfa_command による conda/mfa 環境/コマンドの事前検証・明確なエラー案内
- festival/phonemizer の出力を組み合わせて「音素・シラブル・単語・ストレス強弱」をすべて得る統合ロジックの設計・実装（extract_feature.py）
- 統合出力のための pydantic 型設計・pytest.mark.parametrize によるテストケース設計・期待値明示（test_extract_feature.py）
- dict.json（festival/phonemizer 音素対応辞書）の拡充・難単語解析・未登録音素ペアの追加運用

## 直近の変更・決定事項

- tools/process_alignment.py を大幅に改良
  - TextGrid 形式から lab 形式への出力形式変更
  - 一時ディレクトリの自動削除機能追加
  - glob パターンによるファイル指定対応
  - MFA の align コマンドに`--clean`と`--overwrite`オプション追加
  - TextGrid ファイルの空のテキスト区間（ポーズ）を"(.)"として出力するように修正
- tools/process*mfa.py を他の tools/process*\*.py と完全に同じ設計・書式・例外伝播に統一
- validate_mfa_command で conda コマンド・mfa 環境・mfa コマンドの存在を事前検証
- extract_feature.py で festival/phonemizer 両方の出力を統合する機能実装

## 次のステップ

- 他の CLI 追加時も既存 tools/process\_\*.py と一行単位で徹底比較し、完全統一を最初から実現
- validate 系の設計・案内文も最初に方針を決めて実装
- ドキュメント・エラー案内も最小限・統一化を徹底
- dict.json を活用した音素名寄せ・バリアント吸収ロジックの設計・実装

## 重要なパターン・好み

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
