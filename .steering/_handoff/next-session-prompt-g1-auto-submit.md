# 次セッション開始プロンプト — G1 自動提出の**残務**（第 4 版）

このファイルの「===」以下をコピペして開始する。

**前提**: 2026-08-07 に **`/cross-review` まで完了**した。
★ 残っているのは **push / PR**、**研究者の手作業 3 件**、**未実測 3 件**である。
⚠️ ★ 第 3 版（cross-review 未実施の版）は**もう有効ではない**。git 履歴に残っている。

---

===

## §0 このセッションでやること

`.steering/20260806-g1-auto-submit-on-block-end/` の **残務**を片付ける。
⚠️ ★ **実装・テスト・レビュー・cross-review はすべて終わっている。作り直さない。**

★ **最初に読むもの（この順）**:

1. `.steering/20260806-g1-auto-submit-on-block-end/tasklist.md` — ★ **§7 の push/PR だけが残る**
2. `decisions.md` — D-1〜**D-21**（★ **D-17 / D-21 が 2026-08-07 の追加**）
3. `experiments/20260801-controlled-friction-task/notes.md` **§8-3f / §8-4**

## §1 いまの状態（★ 2026-08-07 実測）

- ブランチ **`feature/g1-auto-submit-on-block-end`**（`origin/main` から **23 コミット** /
  43 files / 7,400 insertions）
- ⚠️★★ **未 push**。⚠️ **`git push` が 2 セッション連続で権限チェックに拒否されている**
  （★ これは環境の問題であって設計の問題ではない。ユーザーが手で push するか、
  権限を通す必要がある）
- ⚠️ ★ PR の base は **`main`** にする。`docs/win-g1-measured-tests` は**リモートに無い**
  （ローカルのみ）ので base に指定できない。
- 検証はすべて緑（★ 2026-08-07 実測）:
  - `bash experiments/20260801-controlled-friction-task/run.sh` → **GREEN**
    （★ cargo ゲートが "2 / 2 本" で実走・受け口ガード **33 ケース**）
  - `cargo test --workspace` **289** / `--features package` **311** + bin 23/7/2
  - golden 4 本 byte-equal / `emit_schema` byte-equal / `npx tsc --noEmit` 緑
  - `bash scripts/secrets-filter-test.sh` **17** / `bash scripts/run-codex-review-test.sh` **7**

## §2 ✅ タスク A — `/cross-review`（★ **完了。もう走らせなくてよい**）

★ 2 周回した。結果は `tasklist.md §5` と `decisions.md` D-17〜D-21 にある。要点だけ:

- ⚠️★ **Codex だけが見つけた実在の穴が 1 件**（D-17）: 同秒ローテートで生まれる
  `gse_..._2.ndjson` 由来の `.age` を、受け口の名前検査が**永久に弾いていた**。修正済み。
- ⚠️★★ **2 周目でレビュー基盤そのものの穴が出た**（D-21）: `secrets-filter` は
  「大文字小文字無視」と**書いてあるだけ**で、`"secret": "…"`（`g1-submit.json` の形）が
  素通りしていた。wrapper の引数も素通しで `--no-index` が書けた。両方塞いで検査を置いた。
- ★ 予算: 2 回で **66,876 / 200,000 tokens**（`.codex/budget.json` に反映済み）。

⚠️ ★ 次に cross-review を使うときの作法（**罠が 2 つある**）:

```bash
# ★ 引数なしだと「未ステージ変更」しか見ない = コミット済みは対象ゼロで rc=0
scripts/run-codex-review.sh <base>..<head> -- <path> ...
# ⚠️ secrets-filter が誤検知で止めたら、★ 該当行を目で見てから ack を付ける
scripts/run-codex-review.sh --ack-filtered <base>..<head> -- <path> ...
```

## §3 ★ タスク B — 研究者の手作業 3 件（⚠️ **自動化しない**）

⚠️★★ **Apps Script の関数セレクタは自動操作を受け付けない**（4 回試して 4 回とも失敗・実測）。
★ これで **同意フォームの全設問を消す事故**を起こしている
（`incident-20260807-g1c-rebuild.md`）。⚠️ **自動で実行しようとしない。人に依頼する。**

| # | 何 | 手順 |
|---|---|---|
| **B-1** | ⚠️★★ **配布済み G1-C の同意 8 項目目を更新** | D-14 で文言を「自動送信」→「毎回の送信確認」に変えた。★ **`migrateConsentForm()`**（回答を消さない・idempotent）を実行 → **`checkConsentFormParity()`** で一致を確認。⚠️ ★ **`setupG1Forms()` を実行しない**（`clearForm()` が同意記録を壊す） |
| **B-2** | 受け口 (GAS `doPost`) の**配備** | `Form_G1/README.md` の手順。★ **新規プロジェクト**に `GSE_G1_Submit.gs` を貼る（⚠️ フォームビルダーと**混ぜない**）→ スクリプト プロパティに `FOLDER_ID` / `SHARED_SECRET` → `checkSubmitConfig()` で ✅ → ウェブアプリとしてデプロイ（実行=自分 / アクセス=全員）→ `/exec` を控える |
| **B-3** | ⚠️ **未実測の GAS 所要時間を埋める** | `measureSaveTiming()` をエディタで 1 回実行し、出力を `gas-measurements.md §3` に貼って「未実測」を消す |

⚠️★★ **B-2 は 2026-08-07 に `GSE_G1_Submit.gs` が変わった**（D-17 / D-18）。
★ **必ず最新のファイルを貼ること。** 古い版を貼ると、同秒ローテートしたブロックが
永久に届かない（`bad name`）。

★ B-2 のあと、配布フォルダ（`g1.mode` と同じ場所）に `g1-submit.json` を置く:

```json
{ "endpoint": "https://script.google.com/macros/s/…/exec", "secret": "<B-2 と同じ>" }
```

⚠️ ★ **これが無ければアプリは送信しない**（`.age` はローカルに貯まり、画面に
「この端末は自動送信の設定がされていません」が出る）。★ `.gitignore` 済み。**コミットしない。**

## §4 ⚠️ タスク C — まだ実測していないこと（★ 実施前に埋める）

1. ⚠️★ **端末 → 実エンドポイントの通し確認**（`.age` が 1 本実際に届くこと）。★ **未実施**
   （B-2 の配備が前提）
2. ⚠️★ **Windows 実機での動作確認**。★ 未実施（macOS のみ）
3. ⚠️★ **`cargo audit` / `cargo deny`**。★ 未実行（環境に未インストール）。
   `.age` 送信のため `rustls` / `aws-lc-rs` / `ring` 等 **40 パッケージが lockfile に増えている**
   （⚠️ ただし **配布アプリ本体には載らない**ことは実測済み・`notes.md §8-3d`）

★ 1 が済むまで `consent.md` の**実施前の停止条件**ブロックを消さない。

## §5 ★ 終わり方

- ⚠️★★ **push と PR**（★ **2 セッション連続で権限拒否**。base は `main`）
- ★ それ以外の完了処理（`/finish-task`・検証・記録）は**済んでいる**

## §6 ⚠️ 環境の罠（★ 先に読む）

| 罠 | 中身 |
|---|---|
| ⚠️★★ `~/.cargo/bin/cargo` が壊れている | rustup shim が dangling。実体は **`~/.rustup/toolchains/stable-aarch64-apple-darwin/bin/cargo`**（1.97.1）。★ **PATH に足さないと `run.sh` の cargo ゲートが「飛ばした」と言って素通りする** |
| repo 直下の `cargo test` は空振り | `Cargo.toml` は `src-tauri/`。`cd src-tauri` か `--manifest-path` |
| ⚠️ **Bash の cwd が持ち越される** | ★ 2026-08-07 にも踏んだ（`cd src-tauri` のまま相対パスを叩いて「ファイルが無い」）。**絶対パスで書く** |
| `run.sh` は未コミット変更で RED | 仕様どおり。コミットしてから走らせる |
| ⚠️★★ Apps Script の関数セレクタ | **自動操作を受け付けない**（§3 参照）。⚠️ 保存も「変更が保存されていません」表示のまま通っていないことがある → ★ **リロードして実体で確かめる** |
| ⚠️ `git push` が拒否される | ★ 2 セッション連続。回避せずユーザーに伝える |

## §7 ⚠️★ やらないこと

- ★ **実装を作り直さない**（`/reimagine` は適用済み・v2 採用）
- ★ **`/cross-review` をもう一度回さない**（2 周済み・D-17〜D-21）
- ★ **D-14 を蒸し返さない**（送信前の確認は研究者判断）
- ⚠️ ★ `preregistration.md §3.1/§3.2/§3.4/§3.5/§3.6` を変更しない
- ⚠️ ★ `ime_state` の session ゲート（`20260805` R-9）を蒸し返さない
- ⚠️ ★ `schema_dto.rs` を変えない
