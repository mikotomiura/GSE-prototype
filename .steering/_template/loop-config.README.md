# loop-config.json の落とし穴（実測ベース・JSON にコメントを書けないため分離）

SSOT は `docs/loop-engineering.md`。canonical spec は
`.claude/commands/commands_setup_research_inloop/README-loop-engineering.md` §2.3。
ここはテンプレを実タスクへ写す時に**必ず読む** ⚠ 集。

## 検出して pin する（推測しない）

- `verify.test` / `verify.typecheck` / `verify.lint` / `ci_command` は
  package.json / pyproject / Makefile / Cargo.toml 等から**検出して pin** する。
  テンプレの値 (`pytest -q` 等) は spec 逐語の例であり、そのまま使わない。
- `mode` は `"A"` (手動 worktree 並列) / `"B"` (orchestrator ＋ subagent) /
  `"C"` (script ＋ headless・無人) を pin する。
- モードB では `budget.parallel` の既定は **1**、`resource_isolation` に
  `per-worktree` を選べない (subagent は親と同じチェックアウトを共有する)。
- `headless` は**モードC のときのみ必須**。他モードでは無視される。
- CLI フラグと JSON スキーマは**実測してから**使う (`verify.*` と同じ原則)。

## ⚠ `allowed_tools` を `null` にしない

`--permission-mode acceptEdits` は **Edit/Write を通すだけで Bash は通さない**。
worker が実際に打つのは `uv run ruff check . ; echo "EXIT:$?"` のような**複合コマンド**で、
`;` / `&&` で分割された**各部分が個別に許可判定される**。`echo` / `ls` / `cat` / `wc` / `test` に
許可が無いと、検証コマンドを組み立てた瞬間に落ちる。

実測 (claude 2.1.220) では最初の 2 回の無人実行が**コード 0 行のまま終了**した (約 $11 を消費)。
対話セッション (モードA/B) では人間が承認するので顕在化せず、**無人のモードC で初めて即死する**。
→ テンプレの既定リストをそのまま使い、`null` に戻さないこと。

### 意図的に入れないもの

| 除外 | 理由 |
|---|---|
| `python` / `python3` / `uv` 全体 | `python3 -c "import os;os.system(...)"` で allowlist を丸ごと迂回できる |
| `find` | ホームディレクトリ全体を走査できる |
| `sed` / `awk` | `sed -i` で **worktree の外**を書き換えられる |
| `git push` / `git reset --hard` / `git rebase` | 無人ループからリモートを壊せる。git は読み取り系 + `add` / `commit` に限定 |
| `cat` の無制限許可 | `.env` を読める。テンプレでは含めているが、機密を置くリポジトリでは外す |

### allowlist は「完全な境界」ではない

許可を 1 つ間違えるだけで全体が迂回できる。**実質的な境界は worktree 隔離と人間の merge ゲート**。
`.claude/settings.json` の `permissions.deny` を必ず併用する (`deny` は allow と frontmatter の両方に優先):

```json
"permissions": {
  "deny": ["Bash(git push:*)", "Bash(gh pr merge:*)", "Bash(git reset --hard:*)",
           "Bash(git rebase:*)", "Bash(sudo:*)", "Bash(rm -rf:*)", "Bash(chmod -R:*)"]
}
```

## ⚠ `token_ceiling` を 2,000,000 にしない

実測で **1 attempt × 3 並列 ≒ 7.09M tokens** (cache 込み)。2M は 1 ラウンドで必ず超過し、
attempt 2 の開始時点で全 issue が `abandoned` になる。`token_ceiling` は attempt の
**開始時にしか判定されない**ため、並列実行では 1 ラウンド分の超過を見込んだ値にする
(テンプレの 40M は `parallel=3` × `max_attempts=6` 想定)。
**実質的な費用ガードは `headless.max_budget_usd`** (claude 呼び出し 1 回あたり) の方。

目安 (実測): 1 issue あたり $1〜12 / 5 issue を緑にするまで総額 約 $40。

## ⚠ `base_branch` は未 merge の作業ブランチなら必ず pin

`null` なら `origin/HEAD` → `main` → `master` の順に解決する。
pin し忘れると main から worktree が切られ、実装が存在しないため**全 issue が即死する**。

## ⚠ `acceptance_template` — AC が gate に載っていない issue は素通りする

`verify` の `test` / `typecheck` / `lint` は、docs 同期・設定変更のみの issue では
**無条件に緑になる**。実測で「grep が 0 件」という AC が 22 件残ったまま `issue_done` になった。

`acceptance_template` で issue ごとの AC 検査コマンドを回す (`{issue_dir}` は issue の置き場に解決)。
`acceptance.sh` が無い issue はこの段を skip する。
**AC が test で表せない issue には必ず `acceptance.sh` を書く。**

## ⚠ verify はベースラインで緑か

pin 済み verify がベースラインで赤い (既存の lint 負債等) と、worktree は互いに独立なので
**それを直す issue の修正が他 worktree に存在せず、実装が完璧でも落ちる**。
分解時に `verify.*` を 1 回実行して**ベースラインの exit code を記録**し、
前提を変える issue は並列ウェーブに混ぜず**最初の単独ウェーブ**に置く。

## claude 2.1.220 の実測メモ (モードC)

- `--help` は**存在しないフラグも素通り**させる。「通ったから存在する」は成立しない。
- `--max-turns` は help 非掲載だが機能する。上限到達時は `subtype: "error_max_turns"` /
  `is_error: true` になるが、これは **attempt の終了であって run の失敗ではない** (verify に進む)。
- `usage.input_tokens` は**キャッシュ分を含まない**。`cache_read` / `cache_creation` を足すか
  `total_cost_usd` を使う。足さないと 500 倍規模で過小計上し `token_ceiling` が永久に発火しない。
- `permission_denials` は必ず見る (無人実行では権限拒否が「静かな停滞」になる)。
- `--disable-slash-commands` が存在する = **`-p` でスラッシュコマンドは既定で有効**
  (モードC の前提の裏取り)。

## GSE 固有の申し送り

テンプレ値は spec 逐語の Python 例。GSE で実タスクを切る際は最低限これを置換する:

- `verify.test` → `cargo test --workspace`
- `verify` の回帰段 → `cargo run --bin gse-replay -- tests/fixtures/minimal.ndjson --snapshot tests/snapshots/minimal.json`
- `verify.lint` → `cargo clippy --workspace --all-targets -- -D warnings` (typecheck は `cargo check` / `tsc --noEmit`)
- `allowed_tools` の `Bash(uv run …)` / `Bash(pytest:*)` 系 → `Bash(cargo test:*)` / `Bash(cargo clippy:*)` /
  `Bash(cargo run:*)` / `Bash(cargo check:*)` / `Bash(npm run:*)` 等
- HMM 挙動を変える issue は `HMM_VERSION` bump とゴールデン再生成が伴うため、
  ベースライン緑の前提を壊す。**最初の単独ウェーブ**に置く。
