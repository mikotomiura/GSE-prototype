# main へのマージで CI が発火しない事象（★ 観測記録・⚠️ 未解決）

> ⚠️★★★ **本ディレクトリは「起票と観測台帳」であって、修正記録ではない。**
> ★ 対処方針は **A（次のマージで再現を見る）＋ B（`/finish-task` で毎回確認する）**（研究者決定・2026-08-27）。

## 事象

**2026-08-26T15:04:42Z（JST 2026-08-27 00:04）、PR #118 を merge commit でマージしたところ、
`main` に対する workflow run が 1 件も作られなかった。**

- マージコミット: `f90c90e7bfcb678933c627fa5a530793d755c271`
- PR: #118（`docs/o1-researcher-decisions` → `main`）

## ★ 決定的な証拠 — **`PushEvent` が配信されていない**

| API | 記録 |
|---|---|
| `repos/{o}/{r}/activity` | ✅ `2026-08-26T15:04:42Z pr_merge refs/heads/main f90c90e7` — ★ **ref は更新された** |
| `repos/{o}/{r}/events` | ❌ 同時刻に `PullRequestEvent` **のみ**。⚠️ **`PushEvent refs/heads/main` が無い** |
| `repos/{o}/{r}/actions/runs?head_sha=f90c90e…` | ❌ **`total_count = 0`**（★ 10 分後も 0） |

★ 直前 2 回との対比（★ どちらも `PushEvent` があり run が作られている）:

```
2026-08-24T18:05:19Z pr_merge → 18:05:21Z PushEvent refs/heads/main 90df0499 → run 32760388787 ✅
2026-08-24T13:59:26Z pr_merge → 13:59:27Z PushEvent refs/heads/main 95e39d71 → run 32735932837 ✅
2026-08-26T15:04:42Z pr_merge →         （PushEvent なし）                  → run 0 件         ❌
```

→ ★★★ **トリガが発火しなかったのではなく、発火する材料が届かなかった。**

## ★ 潰した仮説（★ すべて 2026-08-27 に API / ファイルで確認）

| # | 仮説 | 判定 | 根拠 |
|---|---|---|---|
| 1 | Actions が無効 | ❌ | `actions/permissions` → `{"enabled": true}` |
| 2 | ワークフローが無効化 | ❌ | `actions/workflows` → `258808332 **active**` |
| 3 | トリガ条件の不一致 | ❌ | `ci.yml` `on.push.branches: [main, "feature/*"]`。⚠️ **paths フィルタは無い** |
| 4 | `[skip ci]` 等の指令 | ❌ | マージコミットのメッセージを grep → **ヒット 0** |
| 5 | `concurrency` によるキャンセル | ❌ | group は `workflow-{ref}` で PR (`refs/pull/118/merge`) と main (`refs/heads/main`) は別。⚠️ **キャンセルされた run も残る**が run 自体が 0 件 |
| 6 | merge commit だと発火しない | ❌ | ★ **過去 10 件の merge commit（#106〜#114）はすべて run あり**。#118 だけが 0 |
| 7 | GitHub の障害 | ❌ | `githubstatus.com` → Actions / Webhooks / API すべて `operational` |
| 8 | ⚠️ 支出上限（quota）超過 | ⚠️ **弱い** | ★ 上限超過なら **run が作られないだけで `PushEvent` は出る**はず。⚠️ 今回は `PushEvent` 自体が無い。※ 課金 API は `user` scope が無く未確認（`gh auth refresh -h github.com -s user` で読める） |

→ ★ **残る候補は「GitHub 側の一過性のイベント取りこぼし」。⚠️ 単発 1 件なので断定しない。**

## ⚠️ このときの検証ギャップ

★ **無かった。** マージコミットと PR ブランチ head の **tree ハッシュが完全一致**しており
（どちらも `be4d30f0c66509b5c251ced78e2e361b806eeb94`）、その tree に対する PR 側 CI
（run `32982437780`）は **Windows / macOS self-hosted ＋ frontend-check すべて success で完走**していた。

## ★ 対処（研究者決定・2026-08-27）

| 案 | 内容 | 状態 |
|---|---|---|
| **A** | **次のマージで再現するか観測する** | ⚠️ **継続中**。★ 下の台帳に追記する |
| **B** | **`/finish-task` に「マージ後の CI 発火確認」を入れる** | ✅ **実施済み**（`.claude/commands/finish-task.md` **Step 5**） |
| C | `workflow_dispatch` で手動発火 | ❌ **採らない** —— ⚠️ 現行の `if:` では `check` も `frontend-check` も skip され `build-windows` だけ走るので**確認にならない**（`ci.yml:66,116,161`） |
| D | main へ空コミットを push して確かめる | ❌ **採らない**（★ main を汚す） |

⚠️★★★ **2 回以上続けて run = 0 になったら一過性ではない。** ★ 下の台帳に 2 件目が入った時点で、
原因調査（quota の確認 ＋ GitHub Support への照会）へ切り替える。

## ★ 観測台帳（★ マージのたびに 1 行追記する）

| # | 日時 (UTC) | マージ sha | main の run | 判定 |
|---|---|---|---|---|
| 1 | 2026-08-26T15:04:42Z | `f90c90e` | **0 件** | ❌ 発火せず（★ tree 一致で検証は代替） |

## 受け入れ条件（★ この起票を閉じてよい条件）

- [ ] ★ **その後 3 回のマージで連続して run ≥ 1** → 一過性と結論して閉じる
- [ ] または ⚠️ **2 件目が出た** → 原因調査タスクへ昇格させる（★ この起票は閉じない）
