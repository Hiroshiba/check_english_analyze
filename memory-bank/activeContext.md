# activeContext.md

## 現在の作業フォーカス

- festival/phonemizer の Ubuntu セットアップ手順をドキュメントに反映
- tools/festival.py の OS 自動判別・コーディング規約準拠リファクタ
- .gitignore の Python 公式テンプレート反映
- テスト・CI の安定化

## 直近の変更・決定事項

- docs/festival.md, docs/phonemizer.md に Ubuntu 手順を macOS と同じ粒度で追記
- tools/festival.py で OS 自動判別（macOS: ./festival/bin/festival, Linux: festival）を実装し、import 順・関数順・docstring 等も規約に完全準拠
- .gitignore に GitHub 公式 Python テンプレートを追記
- pytest による自動テストが全てパス
- festival/phonemizer ともに Ubuntu で動作確認済み

## 次のステップ

- 必要に応じてファイル出力機能や記号フィルタ機能の追加
- phonemizer の高度な利用例やバックエンド切替の検証

## 重要なパターン・好み

- print や json.dumps による見やすいデバッグ出力
- logger/verbose/出力分離
- pytest による自動テスト
- コードフォーマット・型厳密化・例外処理の徹底
- OS 差異を吸収する実装

## 学び・インサイト

- festival/phonemizer ともに Ubuntu で公式パッケージ・PyPI で安定運用可能
- OS 差異を吸収することでクロスプラットフォームな CLI ツールが実現できる
- ドキュメント・.gitignore・テストの整備が保守性・信頼性向上に直結する
