# 設計

## 実装アプローチ

既存の `sync-session.ps1` / `sync-session.sh` を内部で呼び出すバッチラッパーを作成する。
ラッパーは以下を行う:

1. **fallback → raw コピー**: fallback ディレクトリの NDJSON のうち、`raw/P000/` に
   存在しないファイルのみをコピー（重複スキップ）
2. **raw 内の未処理ファイル検出**: `raw/P000/` にあるが `metrics/P000/<os>/` に
   対応する `.metrics.json` がないファイルを列挙
3. **既存 sync-session を各ファイルに実行**: `--no-commit` で metrics 生成のみ
4. **まとめて 1 commit + push**: 全ファイル処理後に gse-dataset で git add/commit/push

既存スクリプトの内部ロジックは変更せず、`--no-commit` で呼び出して
git 操作だけバッチ側で制御する。

## 変更対象

### 修正するファイル
- なし

### 新規作成するファイル
- `scripts/sync-all.ps1` — Windows バッチ同期スクリプト
- `scripts/sync-all.sh` — macOS/Linux バッチ同期スクリプト

### 削除するファイル
- なし

## 影響範囲

- 既存の `sync-session.*` は変更なし。影響なし
- gse-dataset の `raw/` と `metrics/` にファイルが追加される（意図通り）

## 既存パターンとの整合性

- `sync-session.ps1` と同じパラメータ命名規則 (`$DatasetRoot`, `$ParticipantId`, `$NoCommit`)
- 同じ exit code 体系 (0=OK, 1=cargo, 2=schema, 3=git)
- PS 5.1 quirk 回避策を踏襲（§10.2.1 記載分）

## テスト戦略

- `--no-commit` (dry-run) で実行し、raw コピー + metrics 生成を確認
- 既に同期済みファイルが重複コピーされないことを確認
- 実際に 5 件の未同期セッションで本番実行して検証

## ロールバック計画

- スクリプト追加のみのため、削除すれば元通り
- gse-dataset 側は `git revert` で戻せる

## 実装時の判明事項

- この環境には `pwsh` (PS 7) がなく `powershell.exe` (PS 5.1) のみ。
  子プロセス起動を `$PSHOME` ベースで検出するよう修正した
- `sync-session.sh` は `GSE_DATASET` / `GSE_PID` を env から読むため、
  `sync-all.sh` 側で明示的に env を渡す必要があった
- dry-run で 7件（既存 raw 2件 + fallback 5件）の metrics 生成を確認後、
  gse-dataset に commit + push 完了
