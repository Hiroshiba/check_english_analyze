# projectbrief.md

## プロジェクト概要

英語テキストから「音素・シラブル・単語・ストレス強弱」を厳密かつ再現性高く抽出・分析できるクロスプラットフォーム CLI/ライブラリを開発する。  
機械学習・音声/NLP 前処理のための高信頼な特徴量生成を目指す。  
コーディング規約徹底・型安全・pydantic 型・logger 設計・pytest パラメータ化・期待値明示による CI 安定化を重視。

## コア要件

- 英語テキストから音素・シラブル・単語・ストレス強弱を抽出し、pydantic 型で厳密に管理
- festival/phonemizer 等の出力を組み合わせ、全情報を一括で得る
- CLI/ライブラリ両対応・クロスプラットフォーム（Ubuntu, macOS）
- コーディング規約・型ヒント・docstring・依存順の徹底
- pytest.mark.parametrize によるテスト網羅・期待値明示
- CI での再現性・信頼性の最大化

## スコープ

- festival/phonemizer+espeak による音素・シラブル・ストレス強弱抽出
- 両者の出力を組み合わせる統合ロジック
- logger/verbose/標準出力分離
- セットアップ・テスト・利用手順のドキュメント整備

## 非スコープ

- 日本語・多言語対応
- Web UI や API サーバ
- 音声合成そのもの

## 参考情報

- https://bootphon.github.io/phonemizer/python_examples.html
- https://bootphon.github.io/phonemizer/api_reference.html
- GitHub 公式 Python.gitignore
- pytest/ruff/pydantic 公式
