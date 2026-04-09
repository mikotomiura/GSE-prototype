# gse-dataset-setup

## 背景

ML移行（HMM → ONNX）に向けてセッションログを体系的に蓄積する基盤が必要。
現在 `~/Documents/GSE-sessions/` に NDJSON が保存されているが、
分析・匿名化・ラベリングのパイプラインが未整備。
まずは自分1人のデータで Phase 1 を開始し、
将来的に5名規模のデータ収集（IRB取得後）に拡張できる設計にする。

## ゴール

`gse-dataset` リポジトリ（private）の雛形を作成し、
匿名化スクリプト・スキーマ定義・ディレクトリ構造を整備する。

## スコープ

### 含むもの
- gse-dataset リポジトリのディレクトリ構造作成
- NDJSON スキーマ定義
- 匿名化スクリプト（anonymize.py）
- スキーマ検証スクリプト（validate_schema.py）
- README（データ管理計画）

### 含まないもの
- 5名分のデータ収集の実施（Phase 2 以降）
- IRB 申請・同意書の正式作成
- ONNX 移行の実装自体
- behavioral_gt.py の本格実装（スタブのみ）

## 受け入れ条件

- [ ] gse-dataset リポジトリの雛形が作成されている
- [ ] NDJSON スキーマ定義が存在する
- [ ] anonymize.py が raw → anonymized 変換を実行できる
- [ ] validate_schema.py でログのスキーマ準拠をチェックできる
- [ ] 将来の複数被験者対応を想定した構造になっている

## 関連ドキュメント

- docs/functional-design.md の機能5（セッションロギング）
- .claude/skills/data-privacy — プライバシー規約
- .claude/skills/ml-workflow — ML移行ワークフロー
