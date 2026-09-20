---
description: >
  1 個の issue を worktree 内で実装しきる薄い executor。issue の Acceptance Criteria に
  対応する test が緑、かつ typecheck/lint 緑になるまで /goal を有界ループさせ、各 attempt を
  test-runner→loop-watchdog で客観検証する。done は watchdog の再検証が gate する。
argument-hint: <issue-id-or-path>
allowed-tools: Read, Write, Edit, MultiEdit, Glob, Grep, Task, TodoWrite, Bash(git status:*), Bash(git diff:*), Bash(git log:*), Bash(git show:*), Bash(git rev-parse:*), Bash(git branch:*), Bash(git ls-files:*), Bash(git add:*), Bash(git commit:*), Bash(cargo test:*), Bash(cargo build:*), Bash(cargo check:*), Bash(cargo clippy:*), Bash(cargo run:*), Bash(cargo fmt:*), Bash(npm test:*), Bash(npm run:*), Bash(npx tsc:*), Bash(echo:*), Bash(printf:*), Bash(ls:*), Bash(cat:*), Bash(head:*), Bash(tail:*), Bash(wc:*), Bash(grep:*), Bash(rg:*), Bash(sort:*), Bash(uniq:*), Bash(cut:*), Bash(jq:*), Bash(test:*), Bash(mkdir:*), Bash(touch:*), Bash(diff:*), Bash(basename:*), Bash(dirname:*), Bash(pwd:*), Bash(date:*), Bash(true:*), Bash(cd:*)
---

# /loop-issue — 1 issue を実装しきる (worker session)

引数: issue id (例 `002`) または issue ファイルのパス。

> `allowed-tools` を縮めてはならない / `Bash(git *)` に戻してはならない。理由は
> `docs/loop-engineering.md` §実行モードとセッション境界・`.steering/_template/loop-config.README.md`
> の「⚠ `allowed_tools` を `null` にしない」節を参照。worker が打つ検証コマンドは
> `cargo test --workspace ; echo "EXIT:$?"` のような複合コマンドで、`;`/`&&` で分割された
> **各部分が個別に許可判定される**。`echo`/`ls`/`cat`/`wc`/`test` が無いと検証コマンドの
> 組み立て自体が拒否される。`Bash(git *)` は `git push`/`git reset --hard`/`git rebase` まで
> 許可してしまうため、読み取り系 + `add`/`commit` に限定している。
> `python`/`python3`/`find`/`sed`/`awk`/`git push`/`git reset --hard`/`git rebase` は意図的に
> 入れていない (allowlist 迂回・worktree 外書き換え・リモート破壊のリスク)。
> allowlist は完全な境界ではない — 実質的な境界は worktree 隔離と人間の merge ゲート
> (`.claude/settings.json` の `permissions.deny` を併用)。

## 前提の確認 (worktree ガード)
```bash
git rev-parse --abbrev-ref HEAD          # loop/<id>-<short> であること
git rev-parse --show-toplevel            # ../wt/<repo>-<id>-<short> であること
```
- **現在ブランチが `loop/*` でない、または worktree 内でない場合は警告し確認を求める**
  ("main checkout で直接実行しようとしています。続行しますか?")。ユーザーが No なら
  `scripts/loop-spawn.sh <id>` の実行を案内して停止する。

### ⚠★★★ セッションを終える前に必ず commit する (2026-09-20 追加)

**実装・停止記録・起票のいずれであっても、worktree を離れる前に `git add <path>` + `git commit` する。**
未コミットのまま終わらない。

- **なぜ**: 2026-09-15 に worker が `git checkout main` を打って worktree 隔離を外した (起票 10)。
  このとき作業が失われなかったのは **commit の後に checkout したからで、偶然である**。
  ⚠️ 001 / 002 / 003 の worker は**いずれも未コミットのまま終わっており**、
  同じことが起きていれば作業は消えていた。
- ⚠ **`git checkout` / `git switch` は打たない。** worktree のブランチを変えない。
  `permissions.deny` に入っている (綴りを変えて迂回しようとしないこと) うえ、
  `loop-run.sh` の `ensure_branch` が逸脱を検出して **その attempt を `blocked` にする**
  (`docs/loop-engineering.md` §worktree ブランチ検査)。
- ⚠ これは**文章の契約であって機械強制ではない**。守られなかったことは
  ブランチ検査が結果として拾うが、「未コミットで終わった」こと自体は記録されない。

## 入力の読み込み (SSOT)
1. `docs/loop-engineering.md` — 用語・Done/Stop・budget 方針 (この command の唯一の真実源)。
2. タスクの `_loop-config.json` — `verify.*` / `ci_command` / `budget.max_attempts` /
   `resource_isolation` / `events_path`(絶対パス)。
3. issue ファイル本体 — `verify_level` (parse|recheck) / `## Acceptance Criteria` (AC↔test マッピング)
   / `## Allowed Files` / `## Stop Conditions`。

## verify コマンドの pin (推測禁止)
`_loop-config.json.verify` から test / typecheck / lint を **そのまま採用**する。
config に無い項目のみ `Cargo.toml` / `package.json` / `docs/agent-shared.md` §テスト方針 等から
検出して config に追補する (GSE の既定は `cargo test --workspace` / `cargo clippy --workspace
--all-targets -- -D warnings` / `npx tsc --noEmit`。回帰段は
`cargo run --bin gse-replay -- tests/fixtures/<name>.ndjson --snapshot tests/snapshots/<name>.json`)。
AC 直結の絞り込みは `scope_test_template` (例 `cargo test --workspace {paths}`) を使う。

## 実行ループ (/goal を有界起動)
```
/goal 「この issue の Acceptance Criteria に対応する test が緑、かつ typecheck/lint が緑になったら完了。
       ただし budget.max_attempts 回の attempt を超えたら停止 (= or stop after N turns)。
       変更は ## Allowed Files の範囲のみ。」
```
`/goal` の各 attempt (実装→自己テスト) の**直後に**、この command が客観検証を挿入する:

1. `attempt_start` を events に append。
2. `Task(subagent_type="test-runner")` (Haiku) に pin 済み verify を実行させ、exit code を回収。
3. `Task(subagent_type="loop-watchdog")` (Haiku) を呼ぶ。watchdog は:
   - test-runner の結果を parse し fingerprint 化 (README 2.4)。
   - `verify_level: recheck` の issue、または `/goal` が「done」を主張した時は **独立に verify を再実行**
     して緑を客観確認する。
   - 同一 fingerprint の連続 / 前進の有無 / AC を本当に満たすかを判断して verdict を返す。
4. verdict で分岐:
   - 緑かつ watchdog が AC 充足を確認 → `issue_done` を append し `/goal` を終了。
   - 赤 → `test_fail`/`typecheck_fail`/`lint_fail` を append し次 attempt へ。
   - Stop 条件 (下記) → 対応イベントを append し停止。

> **重要**: `/goal` 自身の「done」宣言は信用しない。`issue_done` は必ず watchdog の客観再検証
> (`verify_level` に応じた独立再実行または parse 確定) を通してから確定する。

## Stop Conditions (docs/loop-engineering.md をミラー)
- `no_progress_stop`: 同一 fingerprint が連続 N 回 (loop-guard.sh の閾値) → 停止。
- attempt が `budget.max_attempts` に到達 → 停止。
- `scope_violation`: `## Allowed Files` 外を変更 → 停止。
- `blocked`: 依存 issue 未完 / 外部要因 → 停止。
- token が `budget.token_ceiling` 超過 (loop-guard.sh が Stop hook で検出) → 停止。
どの停止も **理由イベントを events に append**してから止まる (静かに死なない)。

## 記録 (single writer, 絶対パス)

> ### ⚠ まず `_loop-config.json.mode` を読むこと。events の writer はモードで変わる。
>
> - **`mode` が `"C"` の場合は events に append してはならない。**
>   モードC では `scripts/loop-run.sh` が **events の唯一の writer** であり、
>   verify の exit code から機械的に書く。worker が書くと `issue_done` が
>   **自己申告に戻り、モードC の存在意義が消える**。
>   モードC では events パスが worktree の cwd 境界の外にあり、append しようとすると拒否される。
>   **これは正常な挙動である。`--add-dir` で通そうとしないこと** (拒否は非致命として扱われる)。
> - **`mode` が `"A"` / `"B"` の場合のみ**、下記のとおり append する。

- **events (モードA / B のみ)**: `_loop-config.json.events_path` の**絶対パス**に append のみ。board は書かない
  (board はダッシュボード端末 `/loop-status` の専任)。1 状態遷移 = 1 行 (README 2.4)。
- **issue `## Status`**: この worktree のループが**唯一の書き手**として更新 (running/verifying/done/blocked)。
- **issue `## Execution Result`**: 完了/停止時に一度だけ記入。**この節が PR 本文になる**
  (何を実装し・どの test が緑・残課題・attempt 数)。

## worktree ポリシー
`.claude/skills/git-workflow/SKILL.md` の "Loop worktree policy" (`<!-- loop:begin -->` 節) を参照する。
1 issue = 1 branch = 1 worktree = 1 PR / base 解決 / dirty tree / stale cleanup / resource_isolation の
3 分岐 (per-worktree / serialize / 隔離不能) はそちらが SSOT。ここには再掲しない。

## 実装/テスト/レビューの骨格
実装・テスト・レビューの骨格は `implementation-workflow` skill に従う。
この command 自身は「issue を読む → verify を pin → 有界ループ → 記録」の薄い制御だけを持つ。

<!-- loop:codex:begin -->
## (任意) TASK-POST: 統合 diff の cross-review
この issue の merge で**タスクの全 issue が緑**になった場合のみ、最終 merge の前に
ダッシュボード端末 (端末0) で 1 回だけ実行する。issue 毎には走らせない。

1. 統合ブランチで**フル CI** (`ci_command`) が緑であることを先に確認する。
2. 既存 `/cross-review` を**統合 diff** に対して起動する
   (= code-reviewer(Opus) ∥ codex-review(gpt-5.5) の並行レビュー)。
   - Codex には `scripts/secrets-filter.sh` を通した**フィルタ済み diff のみ**が渡り、
     `.codex/budget.json` の予算ガードを尊重する (超過時は codex-review 側が中止)。read-only。
   - `/cross-review` が無い環境では `codex-review` skill を直呼びし、code-reviewer の
     指摘と**手動で突き合わせる** (degrade)。
3. 結果を retrospective に**一致点 / 相違点**として記録し、要修正は最終 merge 前に解消する。
<!-- loop:codex:end -->
