---
name: codex-rescue
description: >
  Claude が同じバグで複数回失敗した、または重い refactor で進捗が止まった時、
  OpenAI Codex CLI に修正を委譲する。git worktree で隔離した別ディレクトリで実行し、
  完了後の diff をメイン worktree の Claude が review してから merge する。
  workspace-write 権限が必要。明示的なユーザー承認なしに起動しない。
  proprietary plugin 出力 / 機密情報を含むタスクは対象外。
allowed-tools: Bash(codex *), Bash(git worktree *), Bash(git *), Bash(jq *), Bash(scripts/secrets-filter.sh), Read
---

# Codex Rescue Skill

## 起動条件 (すべて満たす必要)

1. ユーザーが明示的に「Codex に rescue させて」と指示した、または `/cross-review`
   からの提案にユーザーが承認した
2. Claude が同じ問題で 2 回以上失敗している
3. 対象タスクに proprietary 出力 / 機密情報を含まない
4. `.codex/budget.json` の予算余裕が `per_invocation_max * 2` 以上
5. メイン worktree が clean state である (uncommitted changes が無い、または stash 済み)

## 実行フロー

### Step 0: Pre-flight スナップショット取得

```bash
TIMESTAMP=$(date +%s)
{
  echo "## git status"
  git status --porcelain=v1
  echo
  echo "## submodule status"
  git submodule status 2>/dev/null || echo "(none)"
} > "/tmp/codex-rescue-precheck-${TIMESTAMP}.txt"
```

### Step 1: 隔離 worktree の作成

```bash
WORKTREE_DIR=".worktrees/codex-rescue-${TIMESTAMP}"
mkdir -p .worktrees
git worktree add "$WORKTREE_DIR" HEAD
```

### Step 2: タスク記述の準備 + 機密フィルタ

以下の形式で `/tmp/codex-rescue-task.txt` を作成し `secrets-filter.sh` を通す:

```text
## 失敗していたタスク
[1 行サマリ]

## エラー / 失敗内容
[stack trace, テスト失敗ログ等]

## Claude が試したアプローチ
1. [アプローチ A] — 失敗理由: ...
2. [アプローチ B] — 失敗理由: ...

## 関連ファイル (proprietary 除外、最大 5 件)
- src-tauri/src/...

## 受け入れ条件
- [ ] cargo test --workspace が通る
- [ ] ...
```

### Step 3: Codex 実行 (worktree 内、要承認モード)

```bash
cd "$WORKTREE_DIR"
codex exec --sandbox workspace-write --ask-for-approval \
  --skip-git-repo-check \
  -m gpt-5.5 -c model_reasoning_effort=high \
  - < /tmp/codex-rescue-task-filtered.txt
```

### Step 4: 結果 diff 取得 + Claude レビュー

```bash
cd "$WORKTREE_DIR"
git diff > /tmp/codex-rescue-result.diff
git status > /tmp/codex-rescue-status.txt
cd -  # メイン worktree に戻る
```

Claude が `/tmp/codex-rescue-result.diff` を読み、受け入れ条件の充足・副作用・
Pre-flight 状態との一致を確認する。`test-runner` で実走推奨。

### Step 5: Merge または破棄

ユーザー承認後:

```bash
git apply /tmp/codex-rescue-result.diff
git worktree remove "$WORKTREE_DIR" --force
rm -f /tmp/codex-rescue-*.{diff,txt}
```

破棄の場合: `git worktree remove "$WORKTREE_DIR" --force` のみ。

## 適用しないケース

- proprietary plugin 出力の編集
- 機密情報を含む可能性のあるファイル
- Claude が 1 回しか試していないタスク
- ユーザー承認なしの自発的起動
- uncommitted changes があるメイン worktree (stash 必須)

## アンチパターン

- ❌ メイン worktree で直接 `workspace-write` で動かす
- ❌ `--ask-for-approval` を外す
- ❌ rescue 結果を Claude review なしに自動 merge する
- ❌ Claude が初回失敗した時点で Codex に切り替える
- ❌ 同時に複数の codex rescue セッションを起動する
