# 設計

## 実装アプローチ

★ **境界は `loop-run.sh` のブランチ検査に置き、`deny` は worktree 限定の多層防御に留める**（判断 1）。
⚠️ 「綴りを網羅する」方向では原理的に閉じないので、**検知できる側**に境界を置く。

3 件はいずれも `scripts/loop-run.sh` への**検査の追加**であり、制御フローは変えない。

### (1) ブランチ検査（起票 10・判断 1 / 2）

★ `ensure_deny` と同じ形の関数を 1 本足す:

```bash
ensure_branch() { # ensure_branch <issue> <phase> <attempt> <worktree>; 0 = 期待どおり
  head="$(git -C "$wt" rev-parse --abbrev-ref HEAD 2>/dev/null || true)"
  case "$head" in "loop/$id"|"loop/$id-"*) return 0 ;; esac
  emit "$id" "$phase" blocked attempt="$attempt" detail="..."
  return 1
}
```

- ★ **前方一致**にする（`loop/<id>-<short>` の `short` は `loop-spawn.sh` の第 2 引数で可変。
  ⚠️ モードC は省略するので常に `issue` だが、厳密一致にすると将来 `short` を渡した瞬間に壊れる）。
- ★ **detached HEAD** は `rev-parse --abbrev-ref HEAD` が `HEAD` を返すので**不一致 = blocked** になる（正しい）。
- **呼ぶ位置は 2 か所**:
  1. attempt 開始時（`ensure_deny` の直後）— ★ 前の attempt が残した逸脱を次の attempt に持ち越さない
  2. `run_verify` の直前 — ★ **worker が動かした**場合を拾う（⚠️ 起票 10 の実測はこの形）
- ★ `emit` の `phase` は呼び出し元に合わせる（`ensure_deny` の先例と同じ作法）。
  ⚠️ `attempt_start` ではないので `execute` 固定にはしない。

### (2) `permission_denials` の内訳（起票 3・判断 3）

- ⚠️★★★ **`WORK_TMP` は使えない** —— `loop-run.sh:298-300` が `trap cleanup_tmp EXIT` で
  run 終了時に `rm -rf` する。→ ★ `$TASK_DIR/_loop-artifacts/` に置く。
- ★ 既存の `if [ "${denials:-0}" -gt 0 ]` ブロック（`:376-379`）を拡張する:
  1. 生の `permission_denials` 配列を `_loop-artifacts/<id>-attempt<N>-denials.json` に書く
  2. events の `detail` に **tool 名ごとの件数**を足す
- ⚠️ **配列要素のスキーマは実測してから jq を書く**（★ 推測で `.tool_name` と決めない）。
  → `measurements.md` の M1 で確かめる。

### (3) Status フィルタ（判断 26 の申し送り・判断 4）

```bash
issue_status() { issue_field "$1" Status 2>/dev/null | grep -m1 -v '^[[:space:]]*$' || true; }
```

- ★ `blocked` で**始まる**ものだけ既定から外す（004 / 006 は `blocked（★ 2026-09-19 更新…` の形）。
- ★ `--issues` を付けたら**フィルタしない**（⚠️ `blocked` を含むなら 1 行警告する）。
- ★ 除外した id は **stdout のログと `_loop-run-report.md`** に出す。
  ⚠️ **events には出さない** —— events 語彙は 10 種で固定であり、
  「実行しなかった」は状態遷移ではない。

#### ⚠️★★★ 本変更が招く回帰の予防（★ これを入れないと静かに壊れる）

★ `preflight_dag`（`:443-456`）は依存の存在確認を **`$ALL` に対して**行っている:

```bash
elif ! printf '%s\n' $ALL | grep -qx "$d"; then
  echo "loop-run: issue $id の依存 $d が issues/ に存在しません" >&2
```

→ ⚠️ `blocked` を `$ALL` から外すと、**`blocked` な issue に依存している issue が
「issues/ に存在しません」で die する**（★ 実際には存在する）。
→ ★ 存在確認だけは**フィルタ前の全 id**（`ALL_FILES`）に対して行う。
⚠️ これは起票 4（merge 済み依存を扱えない）とは**別の話**であり、起票 4 には踏み込まない。

## 変更対象

### 修正するファイル

- `scripts/loop-run.sh` — ★ `ensure_branch` 追加 / denials 内訳 / Status フィルタ / `preflight_dag` の存在確認元
- `scripts/loop-worktree-deny.sh` — `DENY_REQUIRED` を 7 → **9 件**（`Bash(git checkout:*)` / `Bash(git switch:*)`）＋「7 件」の文言
- `.steering/_template/loop-config.README.md` — ⚠️ **契約の二重定義**。逐語リストを 9 件にし、
  「deny の件数を増やす方向で解こうとしないこと」に**境界はブランチ検査である**ことを併記
- `scripts/loop-worktree-deny-test.sh` — 期待件数 7 → 9
- `.claude/commands/loop-issue.md` — ★「worker は commit してから終わる」を契約に明記（判断 5・文章のみ）
- `docs/loop-engineering.md` — ★「7 件は多層防御であって境界ではない」節を**実測結果**で更新
- `.gitignore` — `.steering/**/_loop-artifacts/`

### 新規作成するファイル

- `scripts/loop-run-guard-test.sh` — ★ ブランチ検査と Status フィルタの検査（**3 状態 ＋ 陰性対照**）
- `.steering/20260920-loop-foundation-fixes/measurements.md` — ★ 実測ログ（受け入れ条件 (1) / (3)）

### 削除するファイル

- なし

## 影響範囲

| 何 | 影響 | 対処 |
|---|---|---|
| モードC の実行 | ★ `blocked` の issue が既定で走らなくなる | ⚠️ `--issues` で明示すれば従来どおり |
| モードA（`loop-spawn.sh`） | ★ deny 9 件が注入される | ⚠️ 人が worktree 内で `git checkout` できなくなる（★ 意図どおり） |
| 対話セッション | ★ **影響なし**（判断 1） | 追跡済み `settings.json` を触らない |
| `loop-worktree-deny-test.sh` | ⚠️ 件数が 7 → 9 で赤になる | 同時に更新する |
| `preflight_dag` | ⚠️ `blocked` 依存の誤診 | ★ 存在確認を `ALL_FILES` に対して行う |

## 既存パターンとの整合性

- ★ `ensure_branch` は **`ensure_deny` と同じシグネチャ・同じ `emit` の作法**に揃える。
- ★ 検査スクリプトは `loop-worktree-deny-test.sh` の
  **`setup_loop_repo` ＋ `claude` stub ＋ events を読んで判定**という既存パターンを踏襲する
  （⚠️ 実 repo には 1 バイトも触れない）。
- ★ ファイル書き換えは `Write` / `Edit` のみ（⚠️ python で書き戻さない —— CRLF 混入）。

## テスト戦略

### 単体（機械検査）

- `scripts/loop-worktree-deny-test.sh` — ★ 9 件の契約の二重定義・3 状態・陰性対照（既存を更新）
- `scripts/loop-run-guard-test.sh`（新規）:
  - **B1** stub が `git checkout -q main` する → ★ `blocked` になり `issue_done` が出ない
  - **B2** stub が何もしない → ★ 正常に `issue_done` になる（⚠️ **陰性対照**。検査が空振りでないこと）
  - **B3** stub が detached HEAD にする → ★ `blocked` になる
  - **S1** `blocked` の issue が既定の `--dry-run` 計画に**出ない**
  - **S2** `--issues <blocked-id>` なら計画に**出る**（＋警告）
  - **S3** `## Status` が無い issue は計画に**出る**
  - **S4** ⚠️ `blocked` に依存する issue があっても `preflight_dag` が die しない（★ 回帰の予防）
  - **D1** denials がある stub → `_loop-artifacts/` に生配列が残り、events の detail に内訳が出る

### 実測（受け入れ条件 (1)・⚠️ 機械検査の代替にならない）

★ 権限判定は Claude Code のランタイム内にあるので、**実際にセッションを回さないと確かめられない**。
→ 実 repo に使い捨て worktree（`loop/zzz-issue`）を切り、`claude -p --model haiku` を回す:

- **M1 対照（deny なし = 現状の再現）**: 7 件の deny で `git checkout main` を依頼 → ★ **通る**ことを撮る
- **M2 対策後（deny 9 件）**: 同じ依頼 → ★ **拒否される**ことを撮る（`permission_denials` を採取）
- ★ 終わったら `bash scripts/loop-spawn.sh --cleanup zzz`

⚠️ **この実測が見ていないもの**（★ 検査自身のコメントに書く）:
`git -C <dir> checkout` / `git -c alias.x=checkout x` / `git worktree add` などの**綴り違いの迂回**。
★ それらは deny では閉じない。**閉じるのはブランチ検査（B1〜B3）の側**である。

### 回帰

- `bash scripts/check-tests-are-wired.sh`（★ 新規テストが配線されているか）
- ⚠️ Rust には触らないので `cargo test` は不要。★ ただし `.gitignore` 変更後に
  `git status` が汚れていないことは確認する。

## ロールバック計画

★ すべて単一コミットに収まるスクリプト/文書変更なので `git revert` 1 回で戻る。
⚠️ ただし **deny 9 件は既存 worktree の `settings.local.json` に既に書かれている**ので、
戻すときは `.steering/_template/loop-config.README.md` と
`scripts/loop-worktree-deny-test.sh` の件数も同時に戻さないと検査が赤のままになる。
