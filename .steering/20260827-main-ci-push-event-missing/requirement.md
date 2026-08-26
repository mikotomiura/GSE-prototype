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

→ ★ 初報の結論は「GitHub 側の一過性のイベント取りこぼし」だった。
⚠️★★★ **この結論は 2026-08-27 に取り下げた（下記「訂正」）。**

---

## ⚠️★★★ 訂正（2026-08-27）— **一過性の取りこぼしではない。Actions が run を作れない状態である**

★ **2 件目と 3 件目の観測が出たので、初報の結論を取り下げる。**

### ★ 観測 2 — **PR #119 でも run が作られない**

- `2026-08-26T15:29:06Z` に PR #119（`chore/main-ci-firing-guard`）を作成。
- ⚠️ **2 分経っても `actions/runs?head_sha=cb656316` は `total_count = 0`。**
- ★ `events` API には `CreateEvent` / `PullRequestEvent` が**記録されている**。

→ ★★★ **`push` だけでなく `pull_request` でも run が作られない。**
⚠️ **14:47:05 の run 32982437780 を最後に、イベント起因の run 作成が 1 件も起きていない。**

### ★★★ 観測 3 — **手動再実行が `startup_failure` で落ちた**（★ これが決定的）

★ 診断のため、**同一コミット・同一ワークフローの完了済み run を手動で再実行**した:

```
gh run rerun 32982437780     # 14:47 に success で完走した run
  → 15:31:40 queued → 15:35:05 completed
  → conclusion = startup_failure
  → ⚠️ jobs が 1 件も作られていない（jobs API が空）
```

| ★ 意味 |
|---|
| ★ **ワークフローファイルは変わっていない**（★ 同じ commit・同じ `ci.yml`）。**45 分前は success で完走している。** |
| ⚠️★★★ `startup_failure` ＋ **job 0 件**は、**run を開始する前段で止まっている**ことを示す。 |
| ⚠️ **ランナーの問題ではない**（★ job が作られていないので、ランナーに渡る前の段階である）。 |

### ★ 更新した仮説の順位

| # | 仮説 | 判定 |
|---|---|---|
| 8 | ⚠️★★★ **支出上限 / 含有分数の枯渇（アカウント単位）** | ★★★ **最有力**。⚠️ private repo で枠が尽きると Actions は動かなくなる。★ `startup_failure` ＋ job 0 件は典型的な現れ方 |
| 9 | 支払い方法の失敗（カード期限切れ等） | ★ 8 と同じ症状を出す。⚠️ 同時に疑う |
| — | 一過性のイベント取りこぼし（**初報の結論**） | ❌ **取り下げ**。⚠️ 3 件連続かつ手動再実行も落ちるので「取りこぼし」では説明できない |

⚠️★★★ **課金枠の直接確認には `user` scope が要る**（★ 現行トークンは `gist, read:org, repo, workflow`）。
→ ★ `gh auth refresh -h github.com -s user` のうえで
`gh api users/<owner>/settings/billing/actions` を読むか、**GitHub の Settings → Billing を目視する**。

### ⚠️★★★ 副作用の記録 — **診断のための再実行が、緑の記録を上書きした**

⚠️ `gh run rerun 32982437780` を実行した結果、**その run の conclusion が `success` → `startup_failure` に変わった**
（★ `run_attempt` は 1 のまま。⚠️ 起動前に落ちたため attempt が増えていない）。
→ ★ **PR #118 の tree に対する「CI 緑」の記録は、API 上では失われている。**
★ 14:47 の完走時に各 job が SUCCESS だった事実は本セッションの記録に残っているが、
⚠️ **API から再取得はできない。**→ ★ **診断のための再実行は、緑の記録を壊しうる**（★ 次に同じ状況で繰り返さないこと）。

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

| # | 日時 (UTC) | 対象 | run | 判定 |
|---|---|---|---|---|
| 1 | 2026-08-26T15:04:42Z | main へのマージ `f90c90e` | **0 件** | ❌ 発火せず（★ tree 一致で検証は代替） |
| 2 | 2026-08-26T15:29:06Z | PR #119 作成 `cb65631` | **0 件** | ❌ 発火せず（⚠️ `pull_request` でも起きる） |
| 3 | 2026-08-26T15:31:40Z | run 32982437780 の**手動再実行** | 1 件 | ❌ **`startup_failure`・job 0 件**（★ 決定的） |
| 4 | 2026-08-26T17:47:38Z | PR #119 `a6583e5`（**自然発火の `pull_request` イベント**） | 1 件 (`32996144273`) | ✅ **success**（18:03:00Z 完走。`decide-win-runner`/`frontend-check`/`check(win-selfhosted)`/`check(mac-selfhosted)` すべて success）。★ **障害復旧後、イベント起因の run が作られることを確認** |

★ 18:01:30Z 時点で `githubstatus.com` incidents API は `"incidents": []`、Actions コンポーネントは `operational` — ★ **インシデント解消を確認**（開始 15:11:58Z → 解消 18:01:30Z より前、実測 ~2h50min）。
→ ★ 手動再実行 (`gh run rerun`) は行わなかった（「緑の記録を壊しうる」教訓 #3 を踏まえ、自然発火の run が既に success だったため不要と判断）。

| 5 | 2026-08-26T18:25:54Z | `decide-win-runner` self-hosted 化 (`adbf178`) push（**自然発火の `pull_request`**） | 1 件 (`32999649870`) | ✅ **success**（18:32:41Z 完走）。`decide-win-runner` は `gse-mac`(`macbook-air-m-arm64`)上で 2 秒で `gse-win` online を検知し正しく self-hosted へ解決。`check(win)`=`g-gear-win-x64` success / `check(mac)`=`macbook-air-m-arm64` success。★ **self-hosted 化の実 run 検証完了** |

---

## ✅★★★ 決着（2026-08-27）— **GitHub Actions の major outage だった**

★ **17:07Z 時点の `githubstatus.com`**:

```
overall : Partial System Outage
Actions : major_outage
active incidents: 1  — "Incident with Actions" (investigating)
```

⚠️★★★ **15:14Z に同じ API を見たときは `operational` だった。** ★ 後からインシデントが立った
（もしくは反映が遅れた）。→ ⚠️ **「1 回見て障害ではないと確定させた」のが誤りだった。**

### ★ すべての症状がこれで説明できる

| 観測 | ★ 説明 |
|---|---|
| main マージ `f90c90e` で run 0 件 | ★ 障害によるイベント処理の取りこぼし |
| PR #119 の 1 コミット目で run 0 件、2 コミット目 (`e5cb04f`) では run あり | ★ **断続的**に落ちていた |
| hosted 2 ジョブが 15 分キューで `cancelled`（`runner_name` 空） | ★ hosted の割り当てが機能していない |
| 再実行しても 17 分間 `queued` のまま job が 1 件も作られない | ★ 現在進行形（★ 17:07Z 時点） |
| self-hosted 2 台は `online / busy=false` | ★ **self-hosted は無事**。⚠️ ただし `check` は hosted の `decide-win-runner` に依存し道連れ |

### ⚠️ 前の節「観測 3」の解釈も差し替える

★ PR #118 の run を再実行して `startup_failure` になった件は、**PR がマージ済みで
`refs/pull/118/merge` が解決できなかった**ためと読むほうが自然である。
⚠️ **「Actions 全体が壊れている証拠」としては使えない。**

### ⚠️★★★ 診断の過程で犯した誤り（★ 記録して繰り返さない）

| # | 誤り | ★ 教訓 |
|---|---|---|
| 1 | ⚠️ **古い `head_sha`（`cb65631`）を照会し続け、実際には作られていた run を「作られていない」と誤認した** | ★ **push のたびに `head_sha` は変わる。必ず現在の HEAD で引き直す** |
| 2 | ⚠️ **`githubstatus` を早い時刻に 1 回見て「障害ではない」と潰した** | ★ **症状が続く限り、障害の有無は何度でも引き直す** |
| 3 | ⚠️★★★ **診断のための `gh run rerun` が、success だった run の記録を `startup_failure` に上書きした** | ★ **緑の記録が残っている run を診断目的で再実行しない**（⚠️ しかもマージ済み PR では情報も得られない） |
| 4 | ⚠️ 結論を 3 回出し直した（枠 → run 作成不能 → hosted 不調 → 障害） | ★ **単発の観測で原因を確定させない**。⚠️ 2 件目・3 件目を取ってから言う |

### ★ 残る作業（★ 障害とは独立）

- ⚠️★★★ **`decide-win-runner` を self-hosted へ移す** —— ★ `runs-on: ubuntu-latest`（`ci.yml:67`）であり、
  ⚠️ **hosted が死ぬと self-hosted の `check` まで skip される**。★ しかも fallback 先が
  `windows-latest`（hosted）なので **hosted 障害時に二重で効く**。
  → ★★★ **復旧後に、下の残作業とまとめて扱う**（★ 研究者決定・2026-08-27）。⚠️ **単独では起票しない。**
- ★ 復旧後に PR #119 を `gh run rerun` して緑を取り、マージする。

---

## ⚠️ 参考: 障害前に検討していた次手（★ 決着したので実行不要）

1. ⚠️★★★ **GitHub の Settings → Billing で Actions の残枠と支払い状態を確認する**（★ dev には見えない）。
2. ★ または `gh auth refresh -h github.com -s user` で `user` scope を付け、
   `gh api users/<owner>/settings/billing/actions` を読む。
3. ★ 枠が原因なら **上限の引き上げ / 翌サイクルまで待つ / self-hosted のみで回る形へ `ci.yml` を組み替える**
   のいずれかを選ぶ。⚠️ 3 つ目は **`decide-win-runner` と `frontend-check` が `ubuntu-latest`（hosted）**
   である点が効く（`ci.yml:67,162`）。

## 受け入れ条件（★ この起票を閉じてよい条件）

- [x] ⚠️ **原因が特定されたこと** → ✅ **GitHub Actions の major outage**（2026-08-27・`githubstatus.com`）
- [x] ★ **障害の復旧後、イベント起因の run が作られること**を 1 回以上確認する → ✅ 観測台帳 #4
- [x] ★ PR #119 を緑にしてマージする → ✅ 観測台帳 #4 の自然発火 run が success（`gh run rerun` 不要と判断）。マージは本節末尾で実施
- [x] ★ `/finish-task` Step 5 の検査が、復旧後に `OK` を返すこと → ✅ `[finish-task] OK: main (d6ff124) の run = 1 件`（PR #119 マージ後、run `33000927868` success）
- [x] ⚠️ **`decide-win-runner` の self-hosted 化** —— ✅ **実施・実 run 検証済み**（観測台帳 #5、`adbf178`）。
      design.md / tasklist.md 参照。code-reviewer + security-checker + `/cross-review` 済み
