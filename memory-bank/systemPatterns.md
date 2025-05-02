# systemPatterns.md

## システムアーキテクチャ

- CLI エントリポイントとロジック層を明確に分離（全 tools/\*.py で徹底）
- pydantic 型による厳密なデータ管理
- logger/verbose/標準出力分離
- クロスプラットフォーム（Ubuntu, macOS）対応
- festival/phonemizer の出力を組み合わせて「音素・シラブル・単語・ストレス強弱」を一括抽出（process_syllable.py, 旧 extract_feature.py）
- 音素列のアライメントを行うモジュール（match_phonemes.py）による統合処理

## 主要技術・設計パターン

- festival: シラブル取得可・ストレス強弱不可
- phonemizer+espeak: ストレス強弱取得可・シラブル不可
- process_syllable.py（旧 extract_feature.py）で両者の出力を単語単位でマージし、全情報を統合
- pytest.mark.parametrize によるテストパターン統合（test\_\*.py 全体で assert 順・パターン順序も統一）
- コーディング規約徹底（import 順・関数順・docstring・型ヒント・依存順・テストパターン順序）
- 期待値明示による CI 安定化・再現性最大化

## コンポーネント構成・関係

- tools/process_festival.py: festival 出力の S 式パース・シラブル抽出
- tools/process_phonemizer.py: phonemizer 出力のストレス強弱抽出
- tools/match_phonemes.py: festival と phonemizer の音素列をアライメントするモジュール
- tools/process_syllable.py（旧 tools/extract_feature.py）: 両出力を単語単位でマージし、pydantic 型で返す統合ロジック
- tools/symbol_mapping.json: festival と phonemizer の音素マッピング定義
- tools/test_festival.py, tools/test_phonemizer.py, tools/test_match_phonemes.py, tools/test_process_syllable.py（旧 tools/test_extract_feature.py）: pytest パラメータ化・期待値明示・assert 順統一
- utility/logger_utility.py: logger 生成・設定
- docs/: セットアップ・利用手順
- README.md: 主要ツールの使い方・依存ライブラリの紹介

## 重要な実装パス

- テキスト → 単語・句読点分割 → festival/phonemizer 並列実行 → 出力マージ（process_syllable.py, 旧 extract_feature.py）→ pydantic 型リスト → json 出力
- テスト: 入力・期待値（words, phonemes, stresses, syllables, stress_levels）をパラメータ化し厳密検証

## その他の設計上の考慮点

- コーディング規約徹底・テスト期待値明示により CI の再現性・信頼性を最大化
- OS 差異・パッケージ依存を吸収し保守性・拡張性を確保
- festival/phonemizer の出力仕様変更にも柔軟に追従できる型設計・テスト設計
  - 外部ライブラリのバージョンアップや内部アルゴリズム変更による出力変化に対応
  - テスト期待値は実際の出力に合わせて更新し、CI/テストの安定性を確保
- CLI/ロジック分離・型厳密化・テスト網羅性・ドキュメント即時参照性を重視
