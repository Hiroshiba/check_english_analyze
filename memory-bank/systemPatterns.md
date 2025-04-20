# systemPatterns.md

## システムアーキテクチャ

- CLI エントリポイントとロジック層を明確に分離
- pydantic 型による厳密なデータ管理
- logger/verbose/標準出力分離
- クロスプラットフォーム（Ubuntu, macOS）対応

## 主要技術・設計パターン

- phonemizer+espeak による音素・ストレス抽出
- pytest.mark.parametrize によるテストパターン統合
- コーディング規約徹底（import 順・関数順・docstring・型ヒント・依存順）
- 期待値明示による CI 安定化

## コンポーネント構成・関係

- tools/process_phonemizer.py: CLI/ロジック分離・pydantic 型・logger 設計
- tools/test_phonemizer.py: pytest パラメータ化・期待値明示
- utility/logger_utility.py: logger 生成・設定
- docs/: セットアップ・利用手順

## 重要な実装パス

- テキスト → 単語・句読点分割 →phonemizer→ 音素・ストレス抽出 →pydantic 型リスト →json 出力
- テスト: 入力・期待値（words, phonemes, stresses）をパラメータ化し厳密検証

## その他の設計上の考慮点

- コーディング規約徹底・テスト期待値明示により CI の再現性・信頼性を最大化
- OS 差異・パッケージ依存を吸収し保守性・拡張性を確保
