# 設計

## アプローチ

sync スクリプトを「単一 `GSE_PID` 前提」から「raw ディレクトリ構造を真実とする per-participant
処理」へ移行する。logger (Part 2) が `raw/<PID>/` に自動生成 ID で書く以上、**PID の真実源は
raw のディレクトリ構造**である。スクリプトはそれを読み取って `metrics/<PID>/` に対応付ける。

3 つの純粋ロジックを bash と PowerShell で**対称に**実装する:

1. **`is_valid_participant_id` 相当の allowlist** — logger と同基準。`^[A-Za-z0-9_-]{1,64}$`
   かつ Windows 予約名 (CON/PRN/AUX/NUL/COM1-9/LPT1-9, 大小無視) を拒否。
   logger の `is_valid_participant_id` (logger.rs:930) と挙動を一致させる
   (Part 1 code-reviewer MEDIUM「バリデーション非対称」の本対応)。
2. **パスからの PID 導出** — セッションパスが `.../raw/<PID>/gse_*.ndjson` の形のとき、
   親ディレクトリ名を PID とする。**祖父ディレクトリ名が `raw` であること**を確認して
   初めて導出成立 (fallback dir `~/Documents/GSE-sessions/gse_*.ndjson` を誤って
   "GSE-sessions" と導出しないため。"GSE-sessions" は allowlist は通るので構造ガードが必須)。
3. **ローカル PID 解決** — 導出不可時 / fallback コピー先決定用。
   `GSE_PID` → `~/.gse/participant_id` (logger の永続化先) → `P000` の順、各段で allowlist 検証。

### sync-session の PID 解決順 (新)

1. パス導出 (`.../raw/<valid-PID>/`)  ← raw と metrics を構造的に一致させる主経路
2. 明示 `GSE_PID` / `-ParticipantId` (valid)  ← 後方互換 (fallback dir のファイル等、導出不可時)
3. `~/.gse/participant_id` (valid)  ← 自動生成 ID で記録した端末の fallback dir ファイル対応
4. `P000`  ← 最終 fallback (既定挙動不変)

→ `OUTPUT_DIR` 既定は従来どおり `metrics/<解決PID>/<os>/`。raw 配下のファイルは必ず (1) で
解決され、`raw/<PID>/` と `metrics/<PID>/` が一致する。

### sync-all の per-participant 反復 (新)

- **Step 1 (fallback→raw コピー)**: ローカル PID 解決 (`GSE_PID`→永続化→P000) で対象 `raw/<local>/`
  を決め、フラットな fallback `gse_*.ndjson` をそこへコピー (fallback dir は端末ローカル・PID 無し
  のため、この端末の永続化 ID が正しい帰属先)。
- **Step 2 (metrics 生成)**: `raw/*/` を**全 participant 反復**。各ディレクトリ名を allowlist 検証
  (不正名は warn してスキップ)。未生成 `gse_*.ndjson` ごとに sync-session を `--no-commit` で実行
  (PID はパス導出に委ね、明示渡ししない)。出力は `metrics/<PID>/<os>/`。
- **Step 3 (commit)**: `git add raw/ metrics/` で全 participant をまとめて 1 commit。
  commit scope は触れた PID が 1 件なら `data(<pid>-<os>)`、複数なら `data(multi-<os>)`。
- **Step 0 (schema parity)**: 変更なし。

## 変更対象ファイル

- `scripts/sync-session.sh` — allowlist 関数 + パス導出 + ローカル PID 解決を追加し、
  `PID="${GSE_PID:-P000}"` を解決ロジックへ置換。
- `scripts/sync-session.ps1` — 同上 (PowerShell 5.1)。`-ParticipantId` 既定を `P000` から
  「`GSE_PID` or 空」に変更し、本体で解決 (空のまま P000 即決を避け永続化 fallback を通す)。
- `scripts/sync-all.sh` — 単一 `PID`/`RAW_DIR`/`METRICS_DIR` 前提を撤廃し per-participant 反復へ。
- `scripts/sync-all.ps1` — 同上 (PowerShell 5.1)。子 PS 起動時の `-ParticipantId` 明示渡しを削除
  (パス導出に委ねる)。
- `docs/development-guidelines.md §10.2` — 「sync は未追従」注記を「追従済み」に更新し、
  per-participant 反復の手順を反映。

## 既存パターンとの整合

- allowlist は logger `is_valid_participant_id` (logger.rs:930) を bash/ps1 へ移植。Windows 予約名
  リストも含めて完全一致させる (logger.rs:918-921)。
- 永続化先 `~/.gse/participant_id` は logger `participant_id_store_path()` (USERPROFILE→HOME) と同じ。
- PowerShell 5.1 footgun (§10.2.1): `$PSHOME`/`$PSScriptRoot` null・`LASTEXITCODE` 消費・
  `Join-Path` 空返し・`>` の UTF-16 BOM・変数 interpolation の遅延 null。既存 ps1 の回避策
  (param 化・pre-access・`[regex]::IsMatch`・文字列結合) を踏襲。
- bash と ps1 の I/O 契約 (位置引数 / `--output-dir` / `--no-commit` / exit 0-3) を維持。

## テスト戦略

スクリプトのみの変更 (Rust 非変更) のため Rust 回帰 (`cargo test`/`--snapshot`/`emit_schema`) は非影響
だが、検証ゲートとして:

- **bash**: `bash -n` 構文チェック (sync-session.sh / sync-all.sh)。allowlist/導出ロジックの
  単体スモーク (一時 `raw/<id>/` ツリーを作り `--no-commit` dry-run で `metrics/<id>/` 生成を確認)。
- **PowerShell**: 構文 parse 確認 (AST parse / `[scriptblock]::Create`)。実行は手動確認
  (ブリッジ経由 quirk のため自動化困難 — §10.2.1)。
- **allowlist 単体**: bash 関数を直接呼び、logger テスト (logger.rs:1719-1772) と同じケース群
  (P000/pilot_01/a-b_C9 OK、空/`..`/`a/b`/`a\b`/空白/null/改行/`:`/`~`/`$`/65文字/CON/NUL NG、
  CONSOLE/COM10/P_CON OK) で一致を確認。
- **sync-all Step 0**: `check_schema_parity.py` 緑 (gse-dataset 存在時)。
- 手動確認: 実 `C:\gse-dataset` で `raw/Pxxxx/` を sync → `metrics/Pxxxx/` 出力 (dry-run)。

## ロールバック計画

スクリプト 4 本 + docs の局所変更。問題時は各スクリプトの PID 解決を `${GSE_PID:-P000}` に戻す。
データ破壊リスクなし (書き込み先ディレクトリ選択と git add 範囲のみ)。

## 実装完了メモ (2026-06-19)

- 変更: `scripts/sync-session.{sh,ps1}` / `scripts/sync-all.{sh,ps1}` / `docs/development-guidelines.md`
  (§10.2 + §10.2.1) / 新規 `scripts/tests/test_participant_id_parity.sh`。`src-tauri/**/*.rs` 不変。
- 実装中に発覚した追加判断は decisions.md D5 (`.ps1` の UTF-8 BOM 必須 = PS 5.1 CP932 誤読対策)。
- 検証 (全緑): `bash -n` ×2 / allowlist 単体 35/35 / derive 単体 6/6 / dry-run E2E
  (`raw/<id>/` → `metrics/<id>/`、`GSE_PID=P003` でも path 勝利) / sync-all E2E
  (Paaa111・Pbbb222 振り分け、CON 不正名 skip、fallback→raw/P000) / 実 commit test
  (M6: 触れた PID のみ stage、CON 非 commit) / PS `ParseFile` errors 0 (BOM 後) /
  parity test 緑 / schema parity tier-3 = skip (schema 非 touch)。
- レビュー: Step G で code-reviewer + security-checker を並列実行。CRITICAL/HIGH = 0 (security)、
  HIGH ×2 (code-review: 予約名パリティ test 不在 / sync-all.ps1 の LASTEXITCODE 依存) は両方対応。
  採用 MEDIUM = M3/M5/M6 + SEC-MEDIUM。見送りは tasklist.md「レビュー」節に理由付きで記録。
- `/cross-review` の Codex 系統は **jq 未導入 (本機既知制約) によりブロック → Claude 単独へ縮退**。
  Claude の独立 2 観点 (code-reviewer + security-checker) は Step G で実施済み。
