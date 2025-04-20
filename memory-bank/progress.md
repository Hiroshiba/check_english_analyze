# progress.md

## 現状動作していること

- tools/festival.py で英語テキストから音素・シラブル・ストレス情報を Festival 経由で抽出し、S 式出力・sexpdata パース・PhonemeInfo(pydantic)リスト変換・json 出力まで厳密な型安全・コーディング規約・例外処理・フォーマットを徹底
- 記号や空白も word として出力されるが、phoneme=None, syllable_index=None, stress=None で表現される
- "hello", "Yes, It's ok! I see. Good!", "internationalization" など多様なテストケースで安定動作を確認

## 残タスク

- verbose 出力（詳細なデバッグ/中間情報出力）対応
- 必要に応じてファイル出力機能や記号フィルタ機能の追加

## 現在のステータス

- festival.py の型安全・json 出力・コーディング規約・例外処理・フォーマットまで安定動作
- 記号や空白の扱いも明確化されている

## 既知の課題

- Festival の No default voice found ワーニングは依然出力される（機能自体には影響なし）
- 記号や空白を用途に応じてフィルタする必要がある

## 意思決定の経緯・履歴

- print や json.dumps による見やすいデバッグ出力を重視
- コードフォーマット・型厳密化・例外処理（raise ... from e）を徹底
- pydantic 導入により PhonemeInfo 型で全出力を厳密に管理
