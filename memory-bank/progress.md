# progress.md

## 現状動作していること

- tools/process_festival.py で英語テキストから音素・シラブル・ストレス情報を Festival 経由で抽出し、word_index, phoneme_index, syllable_index を全体通し番号で付与し、pydantic 型・json 出力・logger/verbose 分離・pytest テストまで徹底
- tools/process_phonemizer.py で英語テキストから音素・ストレス強弱情報を phonemizer+espeak 経由で抽出し、word_index, phoneme_index を全体通し番号で付与し、pydantic 型・logger・CLI/ロジック分離・pytest テストまで徹底
- tools/extract_feature.py で festival/phonemizer 両方の出力を統合し、音素・シラブル・単語・ストレス強弱・各種インデックスを一括で返す関数を実装
- tools/test_extract_feature.py で pytest.mark.parametrize による厳密なテストを追加し、期待値を実装出力に完全同期
- OS 自動判別（macOS: ./festival/bin/festival, Linux: festival）でクロスプラットフォーム対応
- festival/phonemizer の Ubuntu/macOS セットアップ手順を docs/ に反映
- .gitignore に Python 公式テンプレートを反映
- 多様なテストケースで安定動作を確認
- pytest.mark.parametrize で全テストを厳密にパターン化し、全プロパティの期待値を assert
- テスト期待値は実装出力に完全同期
- pytest による自動テストが全ての test\_\*.py で常時検証可能
- README.md に主要ツールの使い方・依存ライブラリの紹介・テスト方法を明記

## 残タスク

- extract_feature.py の拡張（ファイル出力機能や記号フィルタ機能など）
- phonemizer の高度な利用例やバックエンド切替の検証
- CI/CD 強化や他言語対応の検討
- ドキュメント・テストケースのさらなる拡充

## 現在のステータス

- festival/phonemizer の個別出力・統合出力ともに型安全・json 出力・コーディング規約・例外処理・フォーマット・logger/verbose 分離・pytest テスト・README 整備まで安定動作
- word_index, phoneme_index, syllable_index を含む全プロパティが厳密にテスト・CI で検証されている
- festival/phonemizer ともに Ubuntu/macOS で公式パッケージ・PyPI で安定運用可能
- 記号や空白の扱いも明確化されている

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
- festival/phonemizer の出力統合・型設計・テスト設計を最優先
