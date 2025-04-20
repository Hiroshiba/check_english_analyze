# activeContext.md

## 現在の作業フォーカス

- festival/phonemizer の出力を組み合わせて「音素・シラブル・単語・ストレス強弱」をすべて得る統合ロジックの設計・実装（extract_feature.py）
- 統合出力のための pydantic 型設計・pytest.mark.parametrize によるテストケース設計・期待値明示（test_extract_feature.py）
- コーディング規約・テスト・ドキュメント（README.md）整備・主要ツールの CLI/ロジック分離
- テスト網羅性・assert 内容・パターン順序の統一

## 直近の変更・決定事項

- extract_feature.py で festival/phonemizer 両方の出力を統合し、全情報（音素・シラブル・単語・ストレス強弱・各種インデックス）を一括で返す関数を実装
- test_extract_feature.py で pytest.mark.parametrize による厳密なテストを追加し、期待値を実装出力に完全同期
- コーディング規約（引数順・関数順・docstring・型ヒント・依存順・テストパターン順序）を全ファイルで統一
- README.md に主要ツールの使い方・依存ライブラリの紹介を明記し、ドキュメントの即時参照性を向上
- festival/phonemizer の個別出力・統合出力ともに Ubuntu/macOS で安定動作・CI 再現性を確保

## 次のステップ

- ファイル出力機能や記号フィルタ機能など extract_feature.py の拡張
- phonemizer の高度な利用例やバックエンド切替の検証
- CI/CD 強化や他言語対応の検討
- ドキュメント・テストケースのさらなる拡充

## 重要なパターン・好み

- print や json.dumps による見やすいデバッグ出力
- logger/verbose/出力分離
- pytest による自動テスト
- コードフォーマット・型厳密化・例外処理の徹底
- OS 差異を吸収する実装
- CLI/ロジック分離・pydantic 型による厳密なデータ管理
- テスト期待値の明示・CI 安定化
- テスト・ドキュメント・コーディング規約の一貫性

## 学び・インサイト

- festival/phonemizer の出力を組み合わせることで「音素・シラブル・単語・ストレス強弱」を一括で得ることが可能
- OS 差異を吸収することでクロスプラットフォームな CLI ツールが実現できる
- ドキュメント・.gitignore・テストの整備が保守性・信頼性向上に直結する
- コーディング規約徹底・テスト期待値明示により CI の再現性・信頼性が大幅向上
