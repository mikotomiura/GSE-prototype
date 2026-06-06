---
name: "source-command-finish-task"
description: "タスクの完了処理を行う。steering 最終化・テスト実行・コミット提案までを実行する。 Step 3 で schema parity check (tier-3 workflow guard) が走り、 src-tauri/src/schema_dto.rs または src-tauri/schema/current.json に変更がある場合は gse-dataset 側との JSON 意味同値を検証する。drift 検出時は Step 4 に進まず停止する。 /implement の完了後に必ず実行する。"
---

# source-command-finish-task

Use this skill when the user asks to run the migrated source command `finish-task`.

## Command Template

# /finish-task

## Step 1: tasklist 確認

`.steering/[現在のタスク]/tasklist.md` を Read で確認する。

未完了タスクがあればユーザーに確認:
> 「未完了: [タスク名] — 完了させますか? 次タスクに繰り越しますか?」

---

## Step 2: steering の最終化

実装中に変わった設計判断や判明した事実を `design.md` に追記する。
重要な設計判断があれば `decisions.md` を作成する（任意）。

---

## Step 3: レビューとテスト + schema parity check（並列）

以下を並列で起動する:

- **`/review-changes`** を実行 (code-reviewer + security-checker 統合レビュー)
- **`test-runner`** を起動 (cargo test / frontend test の回帰検証)
- **schema parity check** (下記のサブブロックを Bash ツールで実行)

### Schema parity check (tier-3 workflow guard)

タスク中に `src-tauri/src/schema_dto.rs` または `src-tauri/schema/current.json`
を touch した場合のみ、gse-dataset 側の `schema/current.json` との
JSON 意味同値を検証する。drift 検出時は Step 4 に進まず停止する。

以下を 1 つの Bash 呼び出しで実行:

```bash
set +e
SCHEMA_PATHS="src-tauri/src/schema_dto.rs src-tauri/schema/current.json"

# 1) 検出: 3 つの範囲 (merge-base 以降 / unstaged / staged) の union を取る。
#    /finish-task は commit 直前に走るため「未 stage 編集」ケースも拾う必要あり。
#    下記 3 行はそれぞれ独立した statement (インデントは可読性のみ、継続行ではない)。
BASE=$(git merge-base HEAD origin/main 2>/dev/null || true)
SKIP=1
[ -n "$BASE" ] && [ -n "$(git diff "$BASE"  --name-only -- $SCHEMA_PATHS)" ] && SKIP=0
[ -n "$(git diff          --name-only -- $SCHEMA_PATHS)" ] && SKIP=0
[ -n "$(git diff --cached --name-only -- $SCHEMA_PATHS)" ] && SKIP=0
# shallow clone / offline / origin 不在: drift 見逃し回避のため unconditional 呼出しに縮退
[ -z "$BASE" ] && SKIP=0

rc=0
if [ "$SKIP" = 1 ]; then
    echo "[finish-task] schema parity check: skip (no schema changes in this task)"
else
    # 2) DATASET 解決: GSE_DATASET → DATASET_ROOT → platform 既定
    DATASET="${GSE_DATASET:-${DATASET_ROOT:-}}"
    if [ -z "$DATASET" ]; then
        case "$(uname -s)" in
            MINGW*|CYGWIN*|MSYS*) DATASET="C:/gse-dataset" ;;
            *)                     DATASET="$HOME/gse-dataset" ;;
        esac
        if [ ! -d "$DATASET" ]; then
            echo "[finish-task] WARN: GSE_DATASET / DATASET_ROOT 未設定かつ既定 '$DATASET' が存在しません (helper は exit 3 で停止します)"
        fi
    fi

    # 3) helper 呼出し (python3 → python fallback, sync-all.sh:68-84 と同流儀)
    echo "[finish-task] schema parity check: verifying (dataset=$DATASET)"
    parity_rc=0
    if command -v python3 >/dev/null 2>&1; then
        python3 scripts/check_schema_parity.py --dataset "$DATASET" || parity_rc=$?
    else
        python scripts/check_schema_parity.py --dataset "$DATASET" || parity_rc=$?
    fi

    if [ "$parity_rc" -eq 0 ]; then
        echo "[finish-task] schema parity check: OK"
    else
        echo "[finish-task] schema parity check: FAILED (exit $parity_rc) — DO NOT proceed to Step 4."
        rc=$parity_rc
    fi
fi
exit "$rc"
```

**結果判定:**

| helper の挙動 | アクション |
|---|---|
| skip (schema 非 touch) / exit 0 | 他 2 検査の結果待ち → 全緑で Step 4 へ |
| exit 1 (drift) / 2 (proto 不在) / 3 (dataset 不在) / 4 (usage) | **Step 4 に進まない**。helper の生出力をユーザーに見せ、修復コマンドに従って対応を促す |

CRITICAL/HIGH 指摘 / テスト失敗 / parity check 失敗 のいずれかがあれば
対応してから次へ。

---

## Step 4: コミットメッセージ提案

```
[type]([scope]): [短い説明]

- 変更内容 1
- 変更内容 2

Refs: .steering/[YYYYMMDD]-[task-name]/
```

type: `feat` / `fix` / `refactor` / `docs` / `test` / `chore`

ユーザー承認後に `git commit` を実行する。

---

## Step 5: 完了通知

```
完了しました。
次タスクを始める前に `/clear` でセッションをリセットしてください。
```

## 制約

- テスト失敗・CRITICAL/HIGH 指摘を残したまま完了しない
- **Step 3 の schema parity check が失敗した状態で Step 4 に進まない**
  (helper の出力に従って修復 → 再度 /finish-task を実走する)
- ユーザー承認なしで commit しない
- steering の記録を省略しない
