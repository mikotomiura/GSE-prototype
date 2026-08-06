# 次セッション開始プロンプト — G1 自動提出の**残務**（第 3 版）

このファイルの「===」以下をコピペして開始する。

**前提**: 2026-08-08 に **実装・テスト・Claude 側レビュー・文書改訂まで完了**した。
★ 残っているのは **`/cross-review`** と **研究者の手作業 3 件**、および**未実測 3 件**である。
⚠️ ★ 第 2 版（実装待ちの版）は**もう有効ではない**。git 履歴に残っている。

---

===

## §0 このセッションでやること

`.steering/20260806-g1-auto-submit-on-block-end/` の **残務**を片付ける。
⚠️ ★ **実装は終わっている。作り直さない。**

★ **最初に読むもの（この順）**:

1. `.steering/20260806-g1-auto-submit-on-block-end/tasklist.md` — ★ **§5 と §7 だけが残っている**
2. `decisions.md` — D-1〜**D-16**（★ **D-14 が最新の方針転換**: 送信前の確認）
3. `experiments/20260801-controlled-friction-task/notes.md` **§8**（★ 実測したことと、していないこと）

## §1 いまの状態（★ 実測済み）

- ブランチ **`feature/g1-auto-submit-on-block-end`**（`docs/win-g1-measured-tests` から 7 コミット）
- ⚠️ ★ **未 push**。PR は出ていない（前セッションで `git push` が権限で拒否された）
- 検証はすべて緑（★ 2026-08-08 実測）:
  - `bash experiments/20260801-controlled-friction-task/run.sh` → **GREEN**
    （★ cargo ゲートが "2 / 2 本" で**実走**・受け口ガード **20 / 20**）
  - `cargo test --workspace` **287** / `--features package` **309** + bin 23/7/2
  - golden 4 本 byte-equal / `emit_schema` byte-equal / `npx tsc --noEmit` 緑

## §2 ★ タスク A — `/cross-review`（★ ユーザー承認済み）

⚠️★★ **踏む罠が 1 つある。先に読むこと。**

`scripts/run-codex-review.sh` は **`git diff`（＝ 未ステージの変更）だけ**をレビュー対象にする。
★ 今回の作業は **全部コミット済み**なので、そのまま実行すると:

```
[run-codex-review] no unstaged changes to review (skipped, no budget consumed)
```

を出して ★ **exit 0** で返る。⚠️ **rc=0 なので「走った」と誤読しやすい**
（`silent-failure-in-guard-scripts` の型そのもの）。
→ ★ **出力に Codex のレビュー本文が入っていることを目で確かめる**まで「実施した」と書かない。

### ★ 予算（⚠️ **その場で計算し直すこと**。以下は 2026-08-08 時点の値）

| 何 | 値 |
|---|---|
| 全体差分 | 25 files / **4,395 insertions / 181 deletions = 4,576 行** |
| `.codex/budget.json` `manual_approval_threshold_lines` | **2,000** → ★ **超過**（⚠️ ユーザーが 2026-08-08 に**明示承認済み**） |
| `per_invocation_max` | **30,000 tokens** → ★ 全体を送ると超える見込み |
| `daily_token_budget` | 200,000（`today.date` が古ければ日次はリセット扱い） |

→ ★ **新規コードの中核 3 ファイルだけに絞る**（**1,890 insertions** = 閾値内）:

```bash
git diff docs/win-g1-measured-tests..HEAD -- \
  src-tauri/src/reconcile.rs src-tauri/src/submission.rs Form_G1/GSE_G1_Submit.gs
```

⚠️ ★ `Cargo.lock` / `docs/` / `.steering/` / `experiments/` は **送らない**。
⚠️ ★ `scripts/secrets-filter.sh` を必ず通す。

### ★ レビューで見てほしいこと

1. **収束の穴** — 何度走らせても収束するか。並行実行・途中終了で**ブロック番号の重複**や
   取りこぼしが起きないか（`ReconcileLock` の stale 判定・Drop 漏れを含む）。
2. **黙って壊れる経路** — 「送ったつもり」になる経路。とくに **`.sent` を書く条件**と
   `append_manifest` 失敗時の扱い。
3. **GAS 受け口** — 匿名アクセス可の Web App である点、`saveWithoutOverwriting_` が
   上書き・握り潰しをしないか、`decodedLength_` の境界。
4. **「自分の分だけ」判定** — `parse_block_number` / `owned_age_files` / `age_for_stem` の抜け。

⚠️ ★ **以下は Claude 側で既に潰してある。重複報告は要らない**
（★ **両者が見落とした穴**を探してほしい）:
G1 スコープの絞り漏れ / 送信先未設定が画面に出ない / ブロック終了の合図の残留 /
ロック作成失敗と busy の混同 / 子プロセス stderr の PII / GAS シークレットの置き場所 /
GAS の「同名同サイズなら保存しない」が提出を握り潰す。

### ⚠️ 前セッションで起きたこと（★ 環境の問題であって設計の問題ではない）

★ セッション後半、`Bash` / `Agent` / `Skill` の多くが **権限チェックで拒否**された。
`codex` / `jq` は `/opt/homebrew/bin` に**存在する**ので不在ではない。
→ ★ 新セッションなら通る見込み。⚠️ また拒否されたら**無理に回避せず**ユーザーに伝える。

## §3 ★ タスク B — 研究者の手作業 3 件（⚠️ **自動化しない**）

⚠️★★ **Apps Script の関数セレクタは自動操作を受け付けない**（4 回試して 4 回とも失敗・実測）。
★ これで **同意フォームの全設問を消す事故**を起こしている
（`incident-20260807-g1c-rebuild.md`）。⚠️ **自動で実行しようとしない。人に依頼する。**

| # | 何 | 手順 |
|---|---|---|
| **B-1** | ⚠️★★ **配布済み G1-C の同意 8 項目目を更新** | D-14 で文言を「自動送信」→「毎回の送信確認」に変えた。★ **`migrateConsentForm()`**（回答を消さない・idempotent）を実行 → **`checkConsentFormParity()`** で一致を確認。⚠️ ★ **`setupG1Forms()` を実行しない**（`clearForm()` が同意記録を壊す） |
| **B-2** | 受け口 (GAS `doPost`) の**配備** | `Form_G1/README.md` の手順。★ **新規プロジェクト**に `GSE_G1_Submit.gs` を貼る（⚠️ フォームビルダーと**混ぜない**）→ スクリプト プロパティに `FOLDER_ID` / `SHARED_SECRET` → `checkSubmitConfig()` で ✅ → ウェブアプリとしてデプロイ（実行=自分 / アクセス=全員）→ `/exec` を控える |
| **B-3** | ⚠️ **未実測の GAS 所要時間を埋める** | `measureSaveTiming()` をエディタで 1 回実行し、出力を `gas-measurements.md §3` に貼って「未実測」を消す |

★ B-2 のあと、配布フォルダ（`g1.mode` と同じ場所）に `g1-submit.json` を置く:

```json
{ "endpoint": "https://script.google.com/macros/s/…/exec", "secret": "<B-2 と同じ>" }
```

⚠️ ★ **これが無ければアプリは送信しない**（`.age` はローカルに貯まり、画面に
「この端末は自動送信の設定がされていません」が出る）。★ `.gitignore` 済み。**コミットしない。**

## §4 ⚠️ タスク C — まだ実測していないこと（★ 実施前に埋める）

1. ⚠️★ **端末 → 実エンドポイントの通し確認**（`.age` が 1 本実際に届くこと）。★ **未実施**
2. ⚠️★ **Windows 実機での動作確認**。★ 未実施（前セッションは macOS のみ）
3. ⚠️★ **`cargo audit` / `cargo deny`**。★ 未実行（環境に未インストール）。
   `.age` 送信のため `rustls` / `aws-lc-rs` / `ring` 等 **40 パッケージが lockfile に増えている**
   （⚠️ ただし **配布アプリ本体には載らない**ことは実測済み・`notes.md §8-3d`）

★ 1 が済むまで `consent.md` の**実施前の停止条件**ブロックを消さない。

## §5 ★ 終わり方

- `bash run.sh` **GREEN**（★ cargo ゲートが "N / N 本" で**実際に走った**ことを確認）
- `/finish-task`
- ⚠️ ★ **push と PR**（前セッションで拒否されたまま）

## §6 ⚠️ 環境の罠（★ 先に読む）

| 罠 | 中身 |
|---|---|
| ⚠️★★ `~/.cargo/bin/cargo` が壊れている | rustup shim が dangling。実体は **`~/.rustup/toolchains/stable-aarch64-apple-darwin/bin/cargo`**（1.97.1）。★ **PATH に足さないと `run.sh` の cargo ゲートが「飛ばした」と言って素通りする** |
| repo 直下の `cargo test` は空振り | `Cargo.toml` は `src-tauri/`。`cd src-tauri` か `--manifest-path` |
| ⚠️ **Bash の cwd が持ち越される** | 前セッションで `cd src-tauri` のまま `.codex/` を探して「無い」と誤読した。★ **`pwd` を確かめる** |
| `run.sh` は未コミット変更で RED | 仕様どおり。コミットしてから走らせる |
| ⚠️★★ Apps Script の関数セレクタ | **自動操作を受け付けない**（§3 参照）。⚠️ 保存も「変更が保存されていません」表示のまま通っていないことがある → ★ **リロードして実体で確かめる** |

## §7 ⚠️★ やらないこと

- ★ **実装を作り直さない**（`/reimagine` は適用済み・v2 採用）
- ★ **D-14 を蒸し返さない**（送信前の確認は研究者判断。⚠️ D-4 が却下した失敗様式が戻ることは
  `decisions.md` D-14 と `notes.md §8-3e` に**明記済み**）
- ⚠️ ★ `preregistration.md §3.1/§3.2/§3.4/§3.5/§3.6` を変更しない
- ⚠️ ★ `ime_state` の session ゲート（`20260805` R-9）を蒸し返さない
- ⚠️ ★ `schema_dto.rs` を変えない
