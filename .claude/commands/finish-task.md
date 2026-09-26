---
description: >
  タスクの完了処理を行う。steering 最終化・テスト実行・コミット・★ 出荷フロー
  （push → PR → CI 緑なら merge。git-workflow ルール 6）までを実行する。
  Step 5 で main へマージした場合の CI 発火確認を行う (2026-08-27 の取りこぼし事象への対処)。
  Step 3 で schema parity check (tier-3 workflow guard) が走り、
  src-tauri/src/schema_dto.rs または src-tauri/schema/current.json に変更がある場合は
  gse-dataset 側との JSON 意味同値を検証する。drift 検出時は Step 4 に進まず停止する。
  /add-feature, /fix-bug, /refactor の完了後に必ず実行する。
allowed-tools: Read, Write, Edit, Bash(git *), Bash(gh api*), Bash(gh run*), Bash(gh pr *), Bash(python scripts/check_schema_parity.py*), Bash(python3 scripts/check_schema_parity.py*), Task
---

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

- **`/cross-review`** を実行 (**必須**): code-reviewer (Claude) ∥ codex-review (Codex) の独立 2 系統を
  並列起動し、一致/乖離を分類した統合レポートを返す。**codex review はタスク完了ごとに必須**
  (ユーザー方針 2026-06-16)。proprietary/機密混入・予算超過・codex/jq 不在で Codex が使えない場合のみ
  code-reviewer 単独へ自動フォールバックし、**skip 理由を完了報告に明記**する (gate は /cross-review 内で fail-closed)。
- **`security-checker`** を起動 (外部入力・認証・データ保存に関わる変更時。/cross-review に含まれないため別途)
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

★ **2026-09-26 から都度の承認は求めない**（研究者の既定指示「push、PR、CI 緑なら merge。今後 Git 関連はこの形で動く」）。
Step 3 が全部通ったら、そのまま `git commit` し、**Step 4.5 へ進む**。
⚠️ 研究者が「コミットしないで」「PR まで」などと明示したときは、その指示が優先する。

---

## Step 4.5: ★★★ 出荷フロー（push → PR → CI 緑なら merge）

★ **`git-workflow` Skill のルール 6 を Read して、その手順どおりに最後まで実行する**（手順と「止まる条件」の SSOT はそちら。ここに写さない）。
⚠️ 止まる条件（CI 赤・未対応の HIGH・force や `--admin` が要る・機密の混入など）に当たったら merge せずに報告する。
★ merge したら、そのまま Step 5（main の CI 発火確認）へ進む。

---

## Step 5: ⚠️★★★ main へマージした場合の **CI 発火確認**

> ★ **本タスクで PR を main へマージした場合だけ実行する**（★ コミットしただけなら不要）。
> ⚠️ 出所: 2026-08-27 に **マージしたのに `main` の workflow run が 1 件も作られない**事象が起きた
> （`.steering/20260827-main-ci-push-event-missing/`）。★ ref は更新され、PR 側の CI は緑だったが、
> ⚠️ **`PushEvent` が配信されず Actions のトリガが発火しなかった**。
> → ★★★ **CI が回らないまま main が進むのに、誰も気づかない**という失敗様式である。

```bash
# ⚠️ マージ直後は run の作成に数十秒かかる。1 度 0 件でも、30 秒待って再実行してから判断する。
git fetch -q origin main
head="$(git rev-parse origin/main)"
short="$(git rev-parse --short origin/main)"
runs="$(gh api "repos/{owner}/{repo}/actions/runs?head_sha=$head" --jq '.total_count' 2>/dev/null)"
if [ "${runs:-0}" -eq 0 ]; then
  echo "[finish-task] WARN: main ($short) に対する workflow run が 0 件 — CI が発火していない"
else
  echo "[finish-task] OK: main ($short) の run = ${runs} 件"
fi
```

| 結果 | ★ やること |
|---|---|
| run ≥ 1 | ★ そのまま Step 6 へ |
| ⚠️ **run = 0**（30 秒後も） | ★ **完了報告に明記する**。⚠️ **「CI は緑」と書かない** —— ★ 代わりに **PR 側の run と `main` の tree ハッシュが一致するか**を確認し、一致するなら「同一 tree で検証済み」と書く。⚠️ 一致しないなら **main は未検証である** |

```bash
# ★ tree 一致の確認（run が 0 件だったときだけ）
git rev-parse origin/main^{tree} <PR ブランチ head>^{tree}
```

⚠️★★★ **2 回以上続けて run = 0 になったら、一過性ではない。**
★ `.steering/20260827-main-ci-push-event-missing/` に日時と sha を追記し、原因調査へ回すこと。

---

## Step 6: 完了通知

```
完了しました。
次タスクを始める前に `/clear` でセッションをリセットしてください。
```

## 制約

- テスト失敗・CRITICAL/HIGH 指摘 (code-reviewer / security-checker / **codex のいずれか**。
  特に **両者一致の指摘**) を残したまま完了しない
- **codex review (`/cross-review`) を省略しない**。安全ゲート (proprietary/機密/予算/jq・codex 不在) で
  ブロックされた場合のみ Claude 単独へ縮退し、**理由を完了報告に明記**する
- **Step 3 の schema parity check が失敗した状態で Step 4 に進まない**
- ⚠️★★★ **main へマージしたなら Step 5 の CI 発火確認を省略しない**。★ run = 0 のまま「CI は緑」と報告しない
  (helper の出力に従って修復 → 再度 /finish-task を実走する)
- ★ commit / push / PR / merge は `git-workflow` ルール 6 に従って自動で行う（2026-09-26 研究者の既定指示）。
    ⚠️ ただし**止まる条件**に当たったら merge しない。⚠️ `--force` / `--admin`
  を使わない。研究者の明示の指示が常に優先
  - ⚠️ CI が赤のまま merge しない
- steering の記録を省略しない
