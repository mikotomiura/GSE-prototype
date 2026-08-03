---
description: >
  1 タスクの issue 群を 1 セッションで回す orchestrator (モードB)。issue の依存 DAG を
  topological order で解決し、loop-worker subagent を起動し、events を集約して board を
  再描画し、全緑後に review ゲートへ渡す。分解セッションとは別の新セッションで起動すること。
argument-hint: <task-dir-or-name>
allowed-tools: Read, Edit, Glob, Grep, Bash(git *), Bash(jq *), Bash(date *), Task
---

# /loop-orchestrate — issue 群を 1 セッションで回す (モードB)

引数: task ディレクトリ (`.steering/[YYYYMMDD]-[task]`) または task 名。

## 前提の確認 (セッション境界ガード・最初に必ず実行)

このコマンドは **issue 分解とは別のセッション**で起動しなければならない (docs/loop-engineering.md
§実行モードとセッション境界)。次を確認し、1 つでも該当したら**停止して `/clear` を促す**:

- このセッションで grill / to-prd / to-issues を実行した (= 分解セッションのまま)
- このセッションで issue ファイルを新規作成・編集した
- `/context` が既に 50% を超えている

> **なぜか**: 分解セッションには却下案・議論・暗黙の前提が残っており、そのまま実行すると
> 「issue に書いていない前提」を持ち込んで issue = SSOT の契約が壊れる。
> **issue ファイルだけを読んで実行が成立しないなら、分解が失敗している。**
> このガードはその契約の検査装置でもある。

モデルは **Sonnet** であること (`/model sonnet`)。判断は gate (watchdog / code-reviewer) に
委譲するため、orchestrator 自身に Opus は要らない。

## 入力の読み込み

1. `docs/loop-engineering.md` — Done/Stop・budget・モデル割当 (唯一の真実源)。
2. `_loop-config.json` — `mode` が `"B"` であることを確認 (`"A"` なら loop-spawn.sh を、
   `"C"` なら scripts/loop-run.sh を案内して停止)。`verify.*` / `budget.*` / `events_path` を読む。
3. `issues/*.md` 全件 — `## Dependencies` / `## Allowed Files` / `verify_level` を抽出。
4. `_issue-plan.md` (あれば) — issue-slicing が出力した依存 DAG と Allowed Files 交差表。
   **あればこれを一次情報として採用**し、issue ファイルとの不一致は停止して差し戻す
   (実行側で辻褄を合わせない)。無ければ 3 から自分で構築する。

## 実行計画の構築 (DAG)

1. `## Dependencies` から依存 DAG を構築する (`_issue-plan.md` があればそれと突き合わせる)。
   **循環があれば停止**し、該当 issue を提示する
   (issue-slicing の失敗であり、実行では直せない)。
2. topological order で実行順を決める。
3. **並列度の決定**: 既定は 1 (直列)。`budget.parallel > 1` にできるのは、同時に走らせる issue の
   `## Allowed Files` 集合が**互いに交差しない**ことを確認できた場合のみ。
   交差する組は必ず直列化する。判定根拠 (交差表) をユーザーに提示してから開始する。
4. 実行計画 (順序・並列組・総 attempt 見積り = 最長 chain × max_attempts) を提示し承認を得る。

## 実行ループ

実行可能 (依存が全て done) な issue から順に:

```
Task(subagent_type="loop-worker", prompt=<task dir, issue id, config path>)   [Sonnet]
  └ worker 内で attempt ごとに test-runner[Haiku] → loop-watchdog[Haiku]
```

worker が返した要約を受け取ったら、**自己申告を信用せず events を独立に読む**:

- `events_path` を読み、その issue の最終 event と attempt 数を確認する。
- `issue_done` が無いのに worker が done と主張していたら **done として扱わない** (blocked 扱い)。
- `attempt` 数が `budget.max_attempts` を超えていれば budget 逸脱として記録する。

依存先が blocked / stopped になった issue は起動せず `blocked` を append して skip する
(依存の失敗を握りつぶして先に進まない)。

## 進捗の可視化 (board の single-writer 契約は変えない)

`_loop-board.md` を書くのは **`/loop-status` だけ** (single-writer 契約)。
**orchestrator は board を書かない。** events を読み、issue の状態変化をセッション内に表示する。

board を人が眺めたい場合は**別端末**で `/loop 30s /loop-status` を常駐させる (読み取り側は自由)。
別端末を立てたくない場合に限り、orchestrator が `/loop-status` と同じ描画契約で再描画してよいが、
**その場合は別端末の `/loop-status` を同時に走らせない** — writer は常に 1 つ。
描画ロジックは重複させず `/loop-status` を参照する (DRY)。

## 全 issue 完了後の review ゲート

```
Task(subagent_type="code-reviewer")            [Opus]  統合 diff のレビュー
Task(subagent_type="security-checker")         [Opus]  security 面 (該当時)
/cross-review                                  [gpt-5.5] Codex 第二意見 (L6 enabled 時・人が起動)
統合フル CI (_loop-config.json.ci_command。GSE 既定は cargo test --workspace / gse-replay --snapshot / emit_schema diff)
retrospective.md を .steering/_template/loop-retrospective.md から作成
```

review は **Opus**。見逃しのコストが高く、実装 (Sonnet) と同じ高度に置かない。

## 停止 (orchestrator 自身)

> **モードB では `loop-guard.sh` が発火しない** (`loop/*` ブランチが無いため素通り)。
> したがって budget の強制はこのコマンドと `loop-worker` の二段が**唯一のガード**になる。
> 検出したら必ず止めること — ここを緩めるとモードB には停止機構が残らない。

次のいずれかで停止し、理由を events に残してユーザーにエスカレートする:
DAG に循環 / `budget.token_ceiling` 超過 / いずれかの issue が `budget.max_attempts` を超過 /
blocked が滞留 / 同一 issue が 2 回連続で worker から blocked 返却。
