# activeContext.md

## 現在の作業フォーカス

- tools/festival.py の厳密な型安全・コーディング規約・verbose/logger 対応・pytest テスト・README 整備

## 直近の変更・決定事項

- pydantic による PhonemeInfo 型で厳密な型安全を実現
- S 式出力 →sexpdata パース →PhonemeInfo リスト変換 →json 出力まで一貫して型安全
- verbose 時のみ logger で stderr に詳細出力、通常は json のみ標準出力
- pytest による自動テストを tools/test_festival.py で導入
- コーディング規約・ruff/フォーマッター・例外処理（raise ... from e）を徹底
- README.md にテスト方法（PYTHONPATH=. pytest）を明記

## 次のステップ

- 必要に応じてファイル出力機能や記号フィルタ機能の追加

## 重要なパターン・好み

- print や json.dumps による見やすいデバッグ出力
- logger/verbose/出力分離
- pytest による自動テスト
- コードフォーマット・型厳密化・例外処理の徹底

## 学び・インサイト

- Festival は記号や空白も word として出力するため、用途に応じたフィルタが必要
- 長い単語や複雑な文でもシラブル・ストレス・音素が正確に抽出できる
- コードフォーマット・型厳密化・例外処理・テスト自動化を徹底することで保守性・信頼性が大幅に向上する
