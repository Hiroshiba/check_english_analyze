# activeContext.md

## 現在の作業フォーカス

- festival/phonemizer の出力を組み合わせて「音素・シラブル・単語・ストレス強弱」をすべて得る統合ロジックの設計・実装
- 両ツールの長所短所（festival: シラブル可/ストレス不可、phonemizer: ストレス可/シラブル不可）を補完するアルゴリズム検討
- 統合出力のための pydantic 型設計・テストケース設計
- pytest.mark.parametrize によるテスト統合・期待値明示
- festival/phonemizer のセットアップ・利用手順のドキュメント整備

## 直近の変更・決定事項

- projectbrief.md, productContext.md を現状目的（音素・シラブル・単語・ストレス強弱の一括抽出）に合わせて整理
- コーディング規約・型ヒント・docstring・依存順の徹底
- pytest.mark.parametrize でテストを 1 関数に統合し、入力・期待値（words, phonemes, stresses, syllables, stress_levels）を明示
- festival/phonemizer の Ubuntu/macOS セットアップ手順を docs/ に反映
- .gitignore に GitHub 公式 Python テンプレートを反映
- pytest による自動テストが全てパス
- festival/phonemizer ともに Ubuntu/macOS で動作確認済み

## 次のステップ

- festival/phonemizer の出力をマージし、全情報（音素・シラブル・単語・ストレス強弱）を一括で返す統合関数の実装
- 統合出力のための pydantic 型・テストケース拡充
- 必要に応じてファイル出力機能や記号フィルタ機能の追加
- phonemizer の高度な利用例やバックエンド切替の検証

## 重要なパターン・好み

- print や json.dumps による見やすいデバッグ出力
- logger/verbose/出力分離
- pytest による自動テスト
- コードフォーマット・型厳密化・例外処理の徹底
- OS 差異を吸収する実装
- CLI/ロジック分離・pydantic 型による厳密なデータ管理
- テスト期待値の明示・CI 安定化

## 学び・インサイト

- festival/phonemizer の出力を組み合わせることで「音素・シラブル・単語・ストレス強弱」を一括で得ることが可能
- OS 差異を吸収することでクロスプラットフォームな CLI ツールが実現できる
- ドキュメント・.gitignore・テストの整備が保守性・信頼性向上に直結する
- コーディング規約徹底・テスト期待値明示により CI の再現性・信頼性が大幅向上
