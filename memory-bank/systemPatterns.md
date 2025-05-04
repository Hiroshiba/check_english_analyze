# systemPatterns.md

## システムアーキテクチャ

- CLI エントリポイントとロジック層を明確に分離（全 tools/\*.py で徹底）
- pydantic 型による厳密なデータ管理
- logger/verbose/標準出力分離
- クロスプラットフォーム（Ubuntu, macOS）対応
- festival/phonemizer の出力を組み合わせて「音素・シラブル・単語・ストレス強弱」を一括抽出（process_syllable.py, 旧 extract_feature.py）
- 音素列のアライメントを行うモジュール（match_phonemes.py）による統合処理
- アライメント検証を独立関数として実装し、単一責任の原則を適用

## 主要技術・設計パターン

- 無音音素の必ず追加
  - 音声認識結果（lab_entries）には先頭・末尾に無音区間が存在するが、テキスト解析結果にはない
  - add_silence_phonemes 関数で UnifiedPhonemeInfo リストの先頭・末尾に必ず無音要素を追加し、データ構造を揃える
  - これによりアライメント時の index 対応が単純化され、例外的な分岐や特別扱いを排除できる
- 例外的エラー処理
  - 通常は音素不一致はエラーとして raise するが、tools/extract_feature.py のみ例外的に警告として処理し続行する
  - NOTE コメントで例外的措置であることを明記し、他ファイルとの設計意図の違いを明確化
- 関数責任の明確化
  - match_phonemes.py での検証ロジックを verify_complete_alignment として切り出し
  - より堅牢なアライメント処理と明確なエラーメッセージを実現
  - 最上位関数(match_phonemes)内で検証を呼び出し、アライメント結果の整合性を保証
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
  - align_phonemes: 動的計画法を使用して最適なアライメントを計算
  - verify_complete_alignment: アライメントが両方の音素列を完全にカバーしているか検証
  - match_phonemes: メイン関数として処理と検証を統括
- tools/process_syllable.py（旧 tools/extract_feature.py）: 両出力を単語単位でマージし、pydantic 型で返す統合ロジック
- tools/symbol_mapping.json: festival と phonemizer の音素マッピング定義
- tools/test_festival.py, tools/test_phonemizer.py, tools/test_match_phonemes.py, tools/test_process_syllable.py（旧 tools/test_extract_feature.py）: pytest パラメータ化・期待値明示・assert 順統一
- utility/logger_utility.py: logger 生成・設定
- docs/: セットアップ・利用手順
- README.md: 主要ツールの使い方・依存ライブラリの紹介

## 重要な実装パス

- テキスト → 単語・句読点分割 → festival/phonemizer 並列実行 → 出力マージ（process_syllable.py, 旧 extract_feature.py）→ pydantic 型リスト → json 出力
- 音素列アライメント: festival 音素列と phonemizer 音素列 → symbol_mapping.json に基づくマッピング → 動的計画法によるアライメント計算 → アライメント結果の検証 → 整合性の取れた音素マッピング
- テスト: 入力・期待値（words, phonemes, stresses, syllables, stress_levels）をパラメータ化し厳密検証

## その他の設計上の考慮点

- コーディング規約徹底・テスト期待値明示により CI の再現性・信頼性を最大化
- OS 差異・パッケージ依存を吸収し保守性・拡張性を確保
- festival/phonemizer の出力仕様変更にも柔軟に追従できる型設計・テスト設計
  - 外部ライブラリのバージョンアップや内部アルゴリズム変更による出力変化に対応
  - テスト期待値は実際の出力に合わせて更新し、CI/テストの安定性を確保
- CLI/ロジック分離・型厳密化・テスト網羅性・ドキュメント即時参照性を重視
- 単一責任の原則に基づく関数設計
  - 1 つの関数は 1 つの責任のみを持つように設計
  - 検証ロジックの関数化による再利用性と可読性の向上
  - エラーメッセージの明確化による開発者体験の向上
