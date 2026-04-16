# sync-batch-sessions

## 背景

現在の `sync-session.ps1` / `sync-session.sh` は 1 ファイルずつ手動指定する設計。
fallback ディレクトリ (`~/Documents/GSE-sessions/`) に溜まった未同期 NDJSON を
gse-dataset に一括同期する手段がなく、セッション数が増えると運用が煩雑になる。

## ゴール

fallback → raw コピー → metrics 生成 → git commit/push を 1 コマンドで
バッチ実行できるスクリプトを作成する（Windows .ps1 + macOS .sh）。

## スコープ

### 含むもの
- fallback ディレクトリから未同期 NDJSON を `raw/P000/` にコピー
- 各ファイルに gse-replay → metrics JSON 生成
- まとめて 1 commit + push
- Windows (ps1) と macOS (sh) の両対応

### 含まないもの
- 既存 `sync-session.ps1` / `sync-session.sh` の内部ロジック変更
- validate_schema.py の修正
- gse-replay バイナリの変更
- 参加者 ID の自動検出（P000 固定 or env 指定のまま）

## 受け入れ条件

- [ ] fallback の未同期ファイルのみがコピーされる（既存 raw と重複しない）
- [ ] 全ファイルの metrics JSON が生成される
- [ ] 1 commit にまとめて push される
- [ ] --no-commit (dry-run) オプションが動作する
- [ ] Windows / macOS 両方のスクリプトが存在する

## 関連ドキュメント

- docs/development-guidelines.md §10（データ repo 連携）
- scripts/sync-session.ps1（既存の単一ファイル同期）
- scripts/sync-session.sh（既存の単一ファイル同期）

## 運用メモ
- /reimagine 適用: No
- 理由: 既存スクリプトのバッチ化ラッパーであり、設計判断は自明
