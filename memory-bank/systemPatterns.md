# systemPatterns.md

## システムアーキテクチャ

- CLI エントリポイントとロジック層を明確に分離
- pydantic 型による厳密なデータ管理
- logger/verbose/標準出力分離
- クロスプラットフォーム（Ubuntu, macOS）対応
- festival/phonemizer の出力を組み合わせて「音素・シラブル・単語・ストレス強弱」を一括抽出

## 主要技術・設計パターン

- festival: シラブル取得可・ストレス強弱不可
- phonemizer+espeak: ストレス強弱取得可・シラブル不可
- 両者の出力を単語単位でマージし、全情報を統合
- pytest.mark.parametrize によるテストパターン統合
- コーディング規約徹底（import 順・関数順・docstring・型ヒント・依存順）
- 期待値明示による CI 安定化

## コンポーネント構成・関係

- tools/process_festival.py: festival 出力の S 式パース・シラブル抽出
- tools/process_phonemizer.py: phonemizer 出力のストレス強弱抽出
- 統合ロジック: 両出力を単語単位でマージし、pydantic 型で返す
- tools/test_festival.py, tools/test_phonemizer.py: pytest パラメータ化・期待値明示
- utility/logger_utility.py: logger 生成・設定
- docs/: セットアップ・利用手順

## 重要な実装パス

- テキスト → 単語・句読点分割 → festival/phonemizer 並列実行 → 出力マージ → pydantic 型リスト → json 出力
- テスト: 入力・期待値（words, phonemes, stresses, syllables, stress_levels）をパラメータ化し厳密検証

## その他の設計上の考慮点

- コーディング規約徹底・テスト期待値明示により CI の再現性・信頼性を最大化
- OS 差異・パッケージ依存を吸収し保守性・拡張性を確保
- festival/phonemizer の出力仕様変更にも柔軟に追従できる型設計・テスト設計
