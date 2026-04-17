# 設計 (v1)

## 実装アプローチ

`scripts/sync-all.ps1` と `scripts/sync-all.sh` の両方に **Step 0: schema
parity pre-flight** を追加し、`src-tauri/schema/current.json`
(gse-prototype 側) と `$DATASET_ROOT/schema/current.json` (gse-dataset 側)
の内容同値を検証する。

比較は **SHA-256 ハッシュ同値チェック**で行う。これは impact-analyzer が
指摘した BOM / CRLF / trailing newline などのバイト差異問題を、テキスト
比較ではなく「ハッシュが一致すれば実用上等価とみなす」方針で避ける…
のではなく、逆に「ハッシュが完全一致するまで許さない」厳格な byte-equal
を採用する。理由:

- schema ファイルは機械生成であり、人間がエディタで書くことがない
- BOM / CRLF 差異が発生している時点で環境差由来のバグなので検出すべき
- ハッシュ不一致時のメッセージに `diff` 出力を含めれば人間判断に委ねられる

### Step 0 のフローチャート

```
[Start]
  │
  ├─ (a) src-tauri/schema/current.json 存在確認
  │     不在 → FAIL: "run: cd src-tauri && cargo run --bin emit_schema > schema/current.json"
  │
  ├─ (b) $DATASET_ROOT/schema/current.json 存在確認
  │     不在 → FAIL: "copy src-tauri/schema/current.json → $DATASET_ROOT/schema/current.json"
  │
  ├─ (c) SHA-256 ハッシュ算出
  │     prototypeHash = sha256(src-tauri/schema/current.json)
  │     datasetHash   = sha256($DATASET_ROOT/schema/current.json)
  │
  └─ (d) prototypeHash != datasetHash
        → FAIL: diff 先頭 20 行 + 修復コマンド + exit $EXIT_SCHEMA_DRIFT (new=5)
        prototypeHash == datasetHash
        → OK: "[sync-all] Step 0/4 OK (schema in sync: <hash 先頭12桁>)"
```

### 比較方式の詳細

| 環境 | 比較手段 |
|---|---|
| PowerShell | `Get-FileHash -Algorithm SHA256` を両ファイルに実行し `.Hash` 比較 |
| bash | `shasum -a 256` (macOS) / `sha256sum` (Linux) + `awk '{print $1}'` |

bash 側は macOS / Linux で利用可能なコマンドが異なるため、どちらも
試して存在する方を使う ( `command -v sha256sum || command -v shasum` )。

### ドリフト検出時の出力メッセージ

```
[sync-all] Step 0/4 FAIL: schema drift detected
  src-tauri/schema/current.json  : a1b2c3d4...
  $DATASET_ROOT/schema/current.json: e5f6g7h8...

To fix:
  1. Ensure src-tauri schema is current:
       cd src-tauri && cargo run --bin emit_schema > schema/current.json
  2. Copy to gse-dataset:
       cp src-tauri/schema/current.json $DATASET_ROOT/schema/current.json
  3. Commit both changes, then re-run sync-all.

Diff (first 20 lines):
  <diff output>

Aborting before any file copy. Exit code: 5 (SCHEMA_DRIFT)
```

## 変更対象

### 修正するファイル

- `scripts/sync-all.ps1` — Step 0 追加 (現行 Step 1/2/3 を Step 1/2/3 の
  まま維持し、Step 0 を冒頭に差し込む。番号表記は 4 ステップ化)
- `scripts/sync-all.sh` — 同等の Step 0 追加
- `docs/development-guidelines.md` §10.2 — バッチ同期フローの Step 0 説明追加
- `docs/development-guidelines.md` §10.3 — pre-flight check が存在する旨を追記

### 新規作成するファイル

- なし (sync-all の既存スクリプトに Step を追加するのみ)

### 削除するファイル

- なし

## 影響範囲

1. **通常ケース (schema が一致)**:
   ハッシュ算出 < 50ms の追加オーバーヘッドのみ。ユーザー体験は変化なし。
2. **初回クローン直後 ($DATASET_ROOT/schema/ 不在)**:
   明示的に FAIL し、コピー手順を案内。以前は `validate_schema.py` が
   走り始めてからしか気付けなかった欠陥を早期検出に昇格。
3. **ドリフト発生時**:
   5 ファイル full run を完走する前に停止。診断時間が 10 分 → 30 秒に短縮見込み。
4. **既存ドキュメント**:
   §10.2 / §10.3 の運用記述を更新し、pre-flight が公式フローであると記載。

## 既存パターンとの整合性

- Exit code 体系に `$EXIT_SCHEMA_DRIFT = 5` を追加
  (既存: 0=OK, 1=cargo, 3=git, 4=precondition → 5 を新設)
- ログ出力は既存の `Write-Step` / `[sync-all]` prefix パターンを踏襲
- PS 5.1 quirk (§10.2.1) に既に記載された教訓を適用:
  - `Test-Path -LiteralPath` 使用
  - 文字列連結は `"$a\$b"` 形式
  - 変数 pre-access (`Write-Host "[sync-all] ..."`) を追加

## テスト戦略

自動テストは現状 `scripts/` 向けに存在しない (impact-analyzer 確認済み)。
**手動回帰テストを tasklist.md の最初に明記する** 方針:

### 回帰テスト (TDD: 先に失敗させる)

1. **ドリフト再現**:
   - src-tauri/schema/current.json の末尾に空白 1 文字追加 (ハッシュ変化)
   - sync-all.ps1 -NoCommit 実行 → Step 0 FAIL (exit 5) を確認
   - sync-all.sh --no-commit 実行 → 同様に FAIL
   - 末尾空白を戻す

2. **不在ケース**:
   - $DATASET_ROOT/schema/current.json を一時退避 (mv)
   - sync-all 実行 → FAIL メッセージでコピー手順を表示
   - 退避を戻す

3. **正常ケース**:
   - 現在の sync 済み状態で sync-all -NoCommit 実行
   - Step 0 OK + Step 1/2/3 がこれまで通り動作することを確認

4. **5 ファイル同期 regression**:
   - (今回の sync 対象は既に commit 済みなので新規データ作成不可)
   - 代替: dry-run で Step 0/1/2 すべてが "OK" と表示されることを確認

## ロールバック計画

スクリプト編集のみなので、commit を revert すれば完全に戻せる。
docs 側も同一 commit に含めるため巻き戻しは 1 コマンド。

## 実装時の注意

1. **ps1 → sh の順で実装** (impact-analyzer 指摘: ps1 master / sh mirror)
2. **tasklist.md で両方を独立チェック項目に分離**し、片側だけの commit を防ぐ
3. **SHA-256 出力文字列の大小文字正規化**: PowerShell は大文字 HEX、
   bash `sha256sum` は小文字 HEX を返す。同一 OS 内比較なので問題ないが、
   ログ出力は小文字に揃える (ps1 側で `.ToLower()`)

## 将来の拡張余地 (本タスク対象外)

- `sync-session.*` にも同等 check を入れる (単一ファイル同期でのガード)
- `/finish-task` workflow に `schema_dto.rs` 変更時の §10.3 reminder を組み込む
- gse-dataset 側 pre-push hook で repo 間 schema 一致を強制
