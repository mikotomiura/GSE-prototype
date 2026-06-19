# 次セッション開始プロンプト (そのまま貼り付け)

> `feedback_handoff_prompt_in_steering` 方針に従い、次タスクの開始プロンプトを CLAUDE.md 制約込みで固定。
> 本タスク `20260619-participant-id-configurable` の **Part 2 (自動生成 + 永続化)** を実装する。
> Part 1 (env 受け取り) は実装完了・レビュー済み・全テスト緑。
>
> **【2026-06-19 更新】Part 1 はコミット済み**: ブランチ `feature/participant-id-configurable`
> の `4c9cd7b` に foundation commit 済み。次セッションは **このブランチをチェックアウトして
> Part 2 を積む**だけ (下記「着手前に git 整理」の foundation commit 手順は完了済み)。

---

## 次セッションの一手目

タスク: 参加者 ID を **完全自動生成 + ローカル永続化** する (本タスク Part 2、decisions.md D4)。
これは**同一タスクの継続**であり新規 `/start-task` は不要。`.steering/20260619-participant-id-configurable/`
の requirement.md / design.md / decisions.md / tasklist.md を**必ず先に読む**こと。

### 現状 (2026-06-19 セッション終了時点)
- **Part 1 (env 受け取り) 完成・未コミット**。`src-tauri/src/logger.rs` に下記を実装済み:
  - `is_valid_participant_id()` — allowlist `[A-Za-z0-9_-]` 1..=64 + Windows 予約名 (CON/NUL 等) 拒否。
  - `select_participant_id()` — 純粋関数 (優先順選択 + trim)。
  - `resolve_participant_id()` — env 解決 `GSE_PARTICIPANT_ID` → `GSE_PID` → `P000`。
  - `default_log_path()` の `.join("P000")` を解消。単体テスト 10 件。
  - `docs/development-guidelines.md §10.2` に env 手順追記。
- 検証済み: `cargo test --workspace` 緑 (180 lib + 12 bin) / `gse-replay --snapshot` 15/15 byte-equal /
  `emit_schema` drift なし / clippy 新規警告なし。code-reviewer (HIGH なし) + security-checker
  (パストラバーサル問題なし) レビュー済み。`/cross-review` は **jq 不在で Codex 系統 skip → Claude 単独**。
- **未コミット 3 変更**: `src-tauri/src/logger.rs` / `docs/development-guidelines.md` /
  `.steering/20260619-participant-id-configurable/` (untracked)。現在 `main` ブランチ上。

### 承認済み設計 (D4、2026-06-19 にプラン承認済み — 再議不要)
解決順: **永続化値(valid) → `GSE_PARTICIPANT_ID`(valid) → `GSE_PID`(valid) → 自動生成+永続化
→ P000 (生成/書込失敗時の最終 fallback のみ)**。

| 論点 | 採用 |
|---|---|
| ① ID 形式 | `P` + 12桁ランダム hex (例 `Pa3f9c2e1b7d0`)。`is_valid_participant_id` 通過・`P*` glob 互換 |
| ② 永続化先 | `~/.gse/participant_id` (`USERPROFILE`/`HOME` 起点、既存 `fallback_log_dir` と同流儀) |
| ③ env の扱い | override に徹し**永続化しない**。永続ストアは自動生成 ID のみ保持 |
| ④ リセット | `~/.gse/participant_id` 削除で次回再生成 |

- 乱数: `rand = "0.8"` が**既存依存** (新規 crate 追加不要)。
- 既知トレードオフ (D4): D1 (研究者オフライン採番) と衝突。不透明 ID の対応表管理・
  `metrics/P*/` sync 改修は**本タスク外**。実装では触らない。

### スコープ (厳密に限定 — これ以外は実装しない)
- `logger.rs` に: `generate_participant_id()` / `load_persisted_id()` / `persist_id()` /
  純粋関数 `resolve_with_store(persisted, env1, env2, generated)` を追加し、`resolve_participant_id()`
  を新フローへ更新。`is_valid_participant_id` / `select_participant_id` は**再利用**。
- 単体テスト追加 (生成 ID 形式/検証通過/解決順/env を永続化しない こと)。`~/.gse/` 実 I/O は
  純粋関数経由で回避 (HOME を汚さない)。
- docs に自動生成 + リセット手順を追記。
- **スコープ外**: 入力 UI / オンボーディング、ダッシュボード表示、sync・metrics 改修、対応表運用。

### 必須プロトコル (CLAUDE.md 準拠)
1. **コマンド選定**: 継続タスクのため `/add-feature` を起動 (新規 `/start-task` は不要)。
   起動後 agent-shared.md リンクハブから logger 関連 docs を先読み。
2. **Skill 参照**: `data-privacy` (logger.rs 対象・必須) / `rust-standards` / `architecture-rules`。
   ファイル冒頭で Read してから着手。
3. **サブエージェント委譲**: 影響調査が要るなら `impact-analyzer` / `file-finder`。
4. **着手前に git 整理**: `git status`/`git diff` を確認し、**feature ブランチ
   `feature/participant-id-configurable` を作成**してから Part 1 を foundation commit
   (env+検証層)、続いて Part 2 を別コミット。**main へ直コミットしない**。
5. 実装後 **`code-reviewer` + `security-checker` を並列起動** (logger.rs + FS 書込のため
   security-checker 必須、焦点 = 永続化パスの注入・HOME 解決・書込権限)。
6. **`/cross-review`** (jq 不在なら Claude 単独へ縮退し skip 理由を完了報告に明記)。
7. 検証ゲート: `cargo test --workspace` 緑 / `gse-replay --snapshot` byte-equal
   (live パスのみ変更で不変のはず) / `emit_schema` drift なし。
8. 制約: `tracing` のみ (`println!`/`eprintln!` 禁止)、`anyhow::Result`、`any` 不使用、
   unsafe 不要、新規 crate 不要 (rand 既存)。`analysis/` は触らない (logger.rs は src-tauri/src 直下で I/O 可)。
9. `/finish-task`。`.steering/` 記録を省略しない。

### 受け入れ条件 (Part 2)
- env 全未設定 + `~/.gse/participant_id` 不在で初回起動 → `P` + 12桁 hex を生成し永続化、
  以降の起動で同じ ID を再利用 (`$GSE_DATASET/raw/P<hex>/`)。
- 永続化値があれば env より優先。env のみ設定時は env 使用かつ永続化しない。
- 生成/書込失敗時のみ P000。生成 ID は `is_valid_participant_id` を通過。
- `cargo test --workspace` 緑 / snapshot byte-equal / schema drift なし。
- code-reviewer/security-checker の CRITICAL/HIGH 指摘なし (あれば対応)。

---

## Part 3: sync スクリプトを自動生成 ID に追従させる (Part 2 マージ後・別 /start-task 推奨)

> **位置づけ**: scripts ドメイン (bash + PowerShell 5.1) は logger の Rust と別 PR にすべきなので
> **別タスク** (`/start-task` 新規) を推奨。作業の連続性を切らさないため本 handoff に記録する。
> D4 で「本タスク外」とした sync/metrics 追従の実体。

### 解決する問題
Part 2 で `raw/<auto-id>/` への記録は自動になるが、sync スクリプトは `GSE_PID` 単一前提で
`metrics/$PID/` を決めるため、自動生成 ID を知らず **raw と metrics の ID が乖離**する
(`metrics/P000/` に落ちる等)。これを構造的に一致させる。

### スコープ (候補設計 — 着手時に `/reimagine` 不要レベル、承認は次セッションで取る)
- `scripts/sync-session.sh` / `sync-session.ps1`: PID を **セッションパスの親ディレクトリ名
  (`raw/<PID>/gse_*.ndjson`) から導出**。導出不可時のみ `GSE_PID` → `~/.gse/participant_id`
  → `P000` にフォールバック。これで raw と metrics が構造的に同一 ID になる。
- `scripts/sync-all.sh` / `sync-all.ps1`: 単一 `GSE_PID` 前提を廃し、**`raw/*/` を participant
  ごとに反復**して各 `metrics/<PID>/` へ振り分け (現状は全 raw を 1 参加者前提で処理)。
- **ID バリデーション非対称の解消**: スクリプト側にも allowlist (`[A-Za-z0-9_-]`) を入れ、
  logger (`is_valid_participant_id`) と挙動を揃える (code-reviewer MEDIUM 指摘の本対応)。
- `docs/development-guidelines.md §10.2` の手順を per-participant 反復に更新。
- **スコープ外**: ID→被験者 対応表の運用、metrics JSON フォーマット変更、anonymize/package。

### 必須プロトコル / 制約 (CLAUDE.md 準拠)
- `/start-task` で新規タスク作成 → `/add-feature`。`git-workflow` Skill 参照。
- **PowerShell 5.1 footgun に注意** (`docs/development-guidelines.md §10.2.1`):
  `$PSHOME`/`$PSScriptRoot` が null、`Join-Path` 空返し、`LASTEXITCODE` 消費、`>` の UTF-16 BOM。
- bash は `set -euo pipefail` + `bash -n` 構文チェック。
- 実装後 `code-reviewer` + `security-checker` 並列 (パス導出のインジェクション焦点) → `/cross-review`
  (jq 不在なら Claude 単独へ縮退・skip 理由明記)。

### 受け入れ条件 (Part 3)
- `raw/Pabc.../gse_*.ndjson` を sync → `metrics/Pabc.../` に出力 (raw と同一 ID)。
- `sync-all` が複数 `raw/*/` を各々正しい `metrics/<PID>/` へ振り分け。
- 不正なディレクトリ名は allowlist で弾く。
- bash `bash -n` 緑 + 実データ `--no-commit` dry-run 成功 / PowerShell 手動確認 /
  `sync-all` Step0 の schema parity check 緑。

---

## 貼り付け用プロンプト (新セッションで /clear 後に投入)

```
.steering/20260619-participant-id-configurable/ の handoff-next-session.md に従い、本タスク Part 2
(参加者 ID の完全自動生成 + ローカル永続化、decisions.md D4 で承認済み) を実装してください。

着手前に必ず: requirement.md / design.md / decisions.md / tasklist.md を読む。
Part 1 (env 受け取り) は実装完了・未コミット (main 作業ツリー 3 変更) のため、まず feature ブランチ
feature/participant-id-configurable を作成し Part 1 を foundation commit してから Part 2 を実装する。

承認済み設計 (再議不要): 解決順 = 永続化値 → GSE_PARTICIPANT_ID → GSE_PID → 自動生成+永続化 → P000。
ID 形式 = P + 12桁ランダム hex。永続化先 = ~/.gse/participant_id。env は永続化しない。リセットは同ファイル削除。
rand 0.8 は既存依存。スコープ外: 入力UI・ダッシュボード表示・sync/metrics 改修・対応表運用。

CLAUDE.md 準拠で: /add-feature 起動 → data-privacy/rust-standards/architecture-rules を Read →
実装 → code-reviewer + security-checker 並列 (焦点=永続化パス注入/HOME解決) → /cross-review
(jq 不在なら Claude 単独へ縮退し skip 理由明記) → cargo test/snapshot/schema 検証 → /finish-task。
制約: tracing のみ・anyhow・any 不使用・unsafe 不要・新規 crate 不要・analysis/ は触らない。
```
