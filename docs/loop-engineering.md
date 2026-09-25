# Loop Engineering — 単一 SSOT

## 目的
短い・検証可能・記録可能な issue 単位ループで、有界自律実行 (/goal) を
worktree 隔離のもと安全に回す。人が目視できる監視ファイルを中核に置く。

## 基本単位
- task        : 1 つのまとまった開発目標 (例: add-user-auth)。1 retrospective に対応。
- issue       : task を割った vertical slice。1 issue = 1 worktree = 1 PR 候補。
- loop        : 1 issue に対する attempt の列 (execute → verify → done/stop)。
- goal        : /goal による 1 セッションの有界自律実行 (executor)。
- checkpoint  : events.jsonl の 1 状態遷移行 (attempt_start / test_fail / issue_done 等)。
- retrospective: task 完了時の学習記録 (次ループへの入力)。
- **worktree 逸脱**: worktree の HEAD が、その issue のために切られた `loop/<id>-*` から
  外れている状態 (別ブランチ / detached HEAD)。⚠️ このまま verify すると**別ブランチを測る**。
- **ブランチ検査**: 逸脱を検出して `blocked` にする `loop-run.sh` の検査 (`ensure_branch`)。
  ★ **worktree 隔離の境界はここに置く** (⚠️ `permissions.deny` は多層防御であって境界ではない)。

## 原則
1. **1 issue = 1 worktree = 1 PR 候補**。issue は vertical slice で切る (縦に薄く貫く)。
2. **/goal は executor でありセッションにつき 1 回**。完了判定は fast model が
   トランスクリプト基準で行い、テストを独立実行しない → 「done」は自己申告。
   だから **客観検証 (exit code) を events.jsonl に別記録**し、重要 issue は
   watchdog が独立再実行する。
3. **grill を goal の前段に置く**。要件を adaptive に詰めてから issue 化・実行する。
4. **worktree 隔離**。共有する監視ファイルは main checkout の絶対パス 1 か所に集約。
   worktree 内 `.steering` に書くと他端末から見えない。

## Done Condition (issue 完了の条件・すべて満たす)
- [ ] Acceptance Criteria を全項目充足 (AC↔test マッピングで対応 test が緑)
- [ ] test / typecheck / lint がすべて緑 (pin 済み verify コマンドの exit 0)
- [ ] Execution Result に summary を記載 (PR 本文になる)
- [ ] 未解決事項・既知の制約を明記
- [ ] PR 説明 (背景・変更点・検証方法) を用意

## Stop Condition (即時停止し人にエスカレートする条件・いずれか)
- 要件が曖昧 (AC を確定できない)
- scope 外の変更が必要になった (Allowed Files を超える)
- 同一 failure が連続 (同一 fingerprint の反復)
- 原因不明 (前進の見込みが立たない)
- security に関わる判断が必要
- 新規依存の追加が必要

## Budget 方針
- `max_attempts`           : 1 issue あたりの attempt 上限 (既定 6)。
- `no_progress_threshold`  : 同一 fingerprint がこの回数連続したら停止 (既定 4)。
- `token_ceiling`          : task 全体の token 上限 (既定 40,000,000)。
- `parallel`               : 同時 worktree 数 (既定 3)。
- **no-progress fingerprint**: `sha1(失敗test id + error種別 + file:line)`。
  同一 fingerprint が連続すると loop-guard.sh が数え、budget 内でも停止する。

## Events 語彙 (events.jsonl の event 値・全 12 種)
`attempt_start` | `test_pass` | `test_fail` | `typecheck_fail` | `lint_fail` |
`acceptance_fail` | `uncommitted` |
`no_progress_stop` | `scope_violation` | `blocked` | `issue_done` | `abandoned`

- `acceptance_fail`: `<id>-acceptance.sh` が非 0。⚠️ `loop-run.sh` は以前から出していたが、この表に載っていなかった (2026-09-26 に追記)。
- `uncommitted` (2026-09-26・起票 P1-I): worker の attempt の後、**verify を回す前**に見て、worktree に**未コミットの変更がある**か、
  **worktree 生成時点からのコミットが 0 件**。⚠️ verify も watchdog も回さず `issue_done` にしない (未コミットの緑をそのまま merge すると空の merge になる)。
  ★ verify より前に見るので「verify が測った内容 ＝ コミット済みの内容」になり、verify が作る生成物で誤検知しない。
  ★ `test_fail` と同じく**失敗 attempt**として次の attempt へ進む (max_turns で切れた worker が次の attempt でコミットできる)。
  同じ未コミット状態が続けば同じ fingerprint になり `no_progress_stop` で止まる。モードC では `loop-run.sh` が機械検査する。

1 状態遷移 = 1 行 append (main checkout の絶対パスへ)。board は書かない。
**writer はモードで変わる**: モードA/B = 各 worker セッション (LLM の申告) /
モードC = `scripts/loop-run.sh` **だけ** (worker に書かせるとモードC の存在意義が消える)。

## Board 状態機械
`queued(⏳) → running(🔄) → verifying → review → done(✅)` / 逸脱 `blocked(⛔)` / 断念 `abandoned`。
board は events を issue ごとに畳んだ (最終 event 優先) 表示。単一書き手 (dashboard 端末) のみ再描画。

## モデル割当ポリシー
**やり直しが効かない判断は Opus / やり直しが効く作業は Sonnet / 判断を含まない実行は Haiku。**
誤りのコストで選ぶ。issue の切り方を誤ると全ループが正しい方向に無駄に回るので Opus。
実装は verify で機械的に検出・再試行できるので Sonnet。verify 実行や parse は判断を含まないので Haiku。

| 役割 | model | 根拠 |
|---|---|---|
| 設計判断・SSOT 設計・grill | Opus | 判断分岐を閉じる作業。やり直しが効かない |
| issue-slicing (縦切り分解) | Opus | 切り方の誤りが最も高価 |
| オーケストレーション (/loop-orchestrate) | Sonnet | 定型の制御。判断は gate に委譲 |
| オーケストレーション (無人・loop-run.sh) | script (無料) | 簿記であり推論ではない。LLM に渡さない |
| survey (探索・影響調査) | Sonnet | read-only・再実行可能 |
| issue 実装 (worker / loop-worker) | Sonnet | verify が誤りを機械的に検出する |
| verify 実行 (test-runner) | Haiku | exit code 回収のみ |
| 監視 (loop-watchdog) | Haiku | parse ＋ 条件付き再実行 |
| ガード (loop-guard.sh) | script | 無料・機械的 |
| 統合レビュー (code-reviewer / security-checker) | Opus | 見逃しコストが高い |
| 第二意見 (codex-consult / cross-review) | gpt-6-astra（★ 2026-09-25 に gpt-5.5〔Legacy〕から更新） | 別 LLM の独立性が価値・見逃しコストが高い |

この表は `.claude/agents/*.md` の frontmatter `model:` と一致させる (L7 が drift を検出する)。

## issue-slicing の基準 (7 条件)
1. **縦切り**: 1 issue = 層を貫いて価値を 1 本通す。層別の横切り分割は禁止。
2. **粒度**: `budget.max_attempts` (既定 6) 以内に緑にできる大きさ。目安 変更 ≤ 5 ファイル / ≤ 300 行 / AC 3〜7 項目。
3. **独立性**: `## Allowed Files` 集合が交差しない issue だけが並列可能。交差するなら `## Dependencies` で直列化。
4. **検証可能性**: AC は exit code か test 名で言える。AC↔test マッピングが空の issue は issue ではない。
   さらに **その exit code を script が実際に回収できるか** (= `verify` / `acceptance` に載っているか) まで確認する。
5. **verify_level**: AC 直結 / security / 公開 API / データ移行 / 課金 に触れるなら `recheck`。それ以外は `parse`。
6. **DAG**: 依存は DAG。循環禁止。orchestrator は topological order で実行する。
7. **単独 merge 可能性**: 単体 merge しても main が壊れない。1 issue = 1 PR 候補。

分解の締めに slicer 自身が検査する: 単独 merge 可否 / 各 AC の test 名を今書けるか /
Allowed Files 交差表を作ったか / DAG に循環がないか (最長 chain 何段か) /
recheck を基準 5 で選別したか (全部 parse にしていないか) /
**pin 済み verify の前提を変える issue を最初の単独ウェーブに置いたか** /
**test/lint が無条件に緑になる issue に `acceptance.sh` を書いたか**。

## 実行モードとセッション境界
**分解セッションと実行セッションは必ず分ける。** `to-issues` 後に `/clear` し、新セッションで実行を始める。

- 分解セッションには却下案・議論・暗黙の前提が残っており、そのまま実行すると
  「issue に書いていない前提」を持ち込む。**issue ファイルだけを読んで実行が成立しないなら
  issue-slicing が失敗している** — 新セッションはこの契約の検査装置。
- モデルを Opus (分解) → Sonnet (実行制御) に切り替える自然な境界。
- 分解セッションは既に context を消費しており、実行は長時間・多 subagent で context を食う。
- `/goal` はセッションにつき 1 ゴール (モードA)。分解で消費していると起動できない。

| | A: 手動 worktree 並列 | B: orchestrator ＋ subagent | C: script ＋ headless (無人) |
|---|---|---|---|
| 起動 | `loop-spawn.sh --task <task> <id>` → `/loop-issue` | `/loop-orchestrate` (新セッション) | `bash scripts/loop-run.sh <task>` |
| 制御の主体 | 人 | LLM (Sonnet) | **script (決定論)** |
| 隔離 | worktree で完全隔離 | 親と同一チェックアウト | worktree で完全隔離 |
| 並列度 | `budget.parallel` (既定 3) | 既定 1 (直列) | `budget.parallel` (semaphore) |
| スラッシュコマンド | ✅ | ❌ | ✅ (`claude -p "/loop-issue 001"`) |
| loop-guard.sh | ✅ 発火 | ❌ 素通り | ✅ 発火 |
| 有界化 | `/goal … or stop after N turns` | プロンプト内蔵ループ | `--max-turns` ＋ script の attempt ループ |
| events の writer | 各セッション (LLM の申告) | worker subagent (LLM の申告) | **script (verify の exit code)** |
| 停止手段 | guard ＋ watchdog ＋ 人 | LLM 二段 (弱い) | **script が数えて停止・kill 可** |
| 向く場面 | 対話しながら進めたい | 手軽に試したい | **本命の自動化**・夜間・CI |

⚠️★★★ **モードA は `--task` を名指しする** (2026-09-21・起票 23)。
★ `loop-spawn.sh` は旧実装で `.steering/*/_loop-config.json` を `tail -1` で
**タスクと無関係に 1 つ拾っていた** ため、⚠️ **完了済みタスクの枝から worktree が切られ、
main より 38 コミット前になる**事故が実測された。
→ ★ **config が 1 件以上あるのに `--task` / `LOOP_TASK` / `LOOP_BASE_BRANCH` のいずれもなければ
  `loop-spawn.sh` は止まる** (fail-closed)。⚠️ **1 件だけでも黙って選ばない。**
★ モードC (`loop-run.sh`) は `$TASK_DIR` を自動で渡すので、人が書く必要はない。
★ 解決した base は **provenance と「既定ブランチからの乖離コミット数」とともに stderr へ出る**
  (★ モードC では run ログに残る)。→ 詳細は `.steering/_template/loop-config.README.md`。

**なぜ C が本命か**: オーケストレーションは「何回試したか / 同じ失敗か / 予算を超えたか」という
**簿記**であって推論ではない。LLM に持たせると止める役がループの当事者になる (B の弱点)。
C では制御がループの**外**にあり、events も自己申告ではなく exit code から作られるため、
「done は自己申告」問題が構造的に消える。

**ただし C の客観性は自動的には成立しない。次の 3 条件を満たした結果として出てくる**:
①events を書くのは `loop-run.sh` だけ ②AC の検証コマンドが `verify` / `acceptance` に載っている
③verify がベースラインで緑。どれかが崩れると「客観に見えて無意味な緑/赤」を量産する。

**C の危険と既定**: 非対話で書き込みを許すので次を守る。
worktree 隔離を必須 (main checkout で走らせない) / `headless.permission_mode` の既定は
`acceptEdits` (全許可は worktree 隔離下で明示合意時のみ) / `budget.token_ceiling` を必ず設定し
script が usage を積算して超過停止 / 各 `claude -p` は `--max-turns` で有界化 /
**worktree には必須 `permissions.deny` 9 件が自動注入される** (`loop-spawn.sh` → `loop-worktree-deny.sh`。
書いたあと読み直して検査し、失敗したら worktree のパスを返さない = fail-closed。
`loop-run.sh` は **attempt ごとに再注入・再検査**する — worker は `acceptEdits` で
`.claude/settings.local.json` を書き換えられるため、作成時 1 回では閉じない)。
⚠ `ask` は**承認する人が居ない無人実行では前提を満たさない**ので、止めたいものは `deny` に置く。

⚠ **この 9 件は「多層防御」であって境界ではない**:
- **綴りを網羅できない**。⚠️★★★ **2026-09-20 に実測した** (`.steering/20260920-loop-foundation-fixes/measurements.md` M3)。
  `Bash(git checkout:*)` を deny に入れた worktree で **`git -C . checkout main` は拒否 0 件で通り、
  ブランチが `main` へ動いた**。`Bash(git push:*)` も前置一致なので `git -C <dir> push …` は当たらず、
  追跡済み `.claude/settings.json` の `allow: ["Bash(git *)","Bash(gh *)"]` に拾われる。
  `gh pr merge` を塞いでも `gh api --method PUT …/merges` は残り、`git -c alias.x=push x` も通る。
  → **deny の件数を増やす方向で解こうとしないこと。**
  → **実効的な境界は (a) 下記の worktree ブランチ検査、(b) リモート側** (`main` の branch protection)、
    **(c) 人間の merge ゲート**に置く。
- ⚠️★★★ **`allow` は worktree 側で狭められない**。`<worktree>/.claude/settings.local.json` の
  `allow` は追跡済み `.claude/settings.json` と **union** される (★ 2026-09-20 に一次で確認)。
  → worktree 限定で効かせられるのは **`deny` 側だけ**。`allow` を絞るには追跡ファイルを変えるしかなく、
    それは**対話セッションの権限も同時に変える**。
- **注入されていること ≠ 発効していること**。`headless.permission_mode` を
  `LOOP_ALLOW_FULL_ACCESS=1` で `auto` / `bypassPermissions` へ昇格させたとき deny が
  どう評価されるかは**実測していない** (⚠️ 2026-09-20 の実測は既定 `acceptEdits` だけ)。
  昇格モードを使うなら、そこは未検証のまま使うことになる。

### ⚠★★★ worktree ブランチ検査 —— **これが隔離の境界である** (2026-09-20)

`loop-run.sh` は worktree の `git rev-parse --abbrev-ref HEAD` が `loop/<id>-*` であることを
確かめる (`ensure_branch`)。外れていたら events に `blocked` を 1 行残して
**その issue を落とす (fail-closed)**。**自動では戻さない。**

★ **検出力を持つのは 2 か所**:

1. **`run_verify` の直前** — worker のセッション中の逸脱を拾う (⚠️ 起票 10 の実測はこの形)。
2. **`issue_done` を出す直前** — `verify_level: recheck` の `run_watchdog` は worktree 内で
   **もう 1 回フルセッション**を起動するので、ここを見ないと
   ⚠️ **「別ブランチを見て出した done」**が成立する (★ 2026-09-20 に両レビューが HIGH で指摘)。

⚠ attempt 開始時にも呼んでいるが、**現在のモードC では到達しない**
(逸脱は必ず先に 1. が拾って issue を落とすため)。将来 worktree を再利用する経路のための保険であり、
**「3 か所で検査している」と数えないこと。**

★ 名前だけでなく **`merge-base --is-ancestor` で履歴の子孫性**も見る。
⚠ `git reset --soft|--mixed <other>` / `git branch -f loop/<id>-issue <other>` は
**HEAD の名前を保ったまま中身を差し替える** (deny に在るのは `git reset --hard:*` だけ)。
⚠ **境界の限界は 2 つある** (★ どちらも 2026-09-20 に実測した):

1. `git restore --source=<other> -- .` / `git read-tree -u` のような
   **HEAD を動かさない内容の差し替えは拾えない**。
2. **同じブランチ内の巻き戻し** (`git reset --soft|--mixed <アンカー>`) は
   `--is-ancestor` が TRUE を返すので **検出しない**。
   ★ これは**許容と裁定した仕様**である —— `--soft` / `--mixed` は作業ツリーを保つので、
   verify が測る内容は worker の成果物のまま。害は「コミットが捨てられる」であって
   「別の内容を測る」ではなく、**「未コミットで終わる」を失敗にしない**のと同じ型。
   ⚠ `git reset --hard` は deny に在る (作業ツリーも消すため)。

⚠ deny で塞ぐ方向に戻さないこと。

- **なぜ要るか**: 2026-09-15 に worker が `git checkout main` を打ち、worktree が `main` を
  掴んだまま attempt が終わった (起票 10)。⚠️ このとき `run_verify` は
  **別ブランチの内容を検査して緑/赤を出す** — 何を測ったのか分からない数字になる。
- **なぜ deny ではなくこれが境界か**: ⚠️ deny は**到達の綴り**を塞ぐが網羅できない (上記 M3)。
  ブランチ検査は**結果 (HEAD) だけ**を見るので、どの綴りで到達しても同じく拾う。
- ⚠ **自動で戻さない**。`ensure_deny` は「検知して再注入」する型だが、ブランチは違う:
  未コミットの変更を抱えたまま `git checkout` で戻すと、変更が別ブランチへ持ち越されるか
  checkout 自体が失敗する。→ **記録して止める。** worktree は撤去せず人に渡す。
- ⚠ **worker は commit してから終わること** (`.claude/commands/loop-issue.md` の契約)。
  未コミットのまま逸脱すると作業が失われうる。

### ⚠ `## Status` が `blocked` の issue は既定の選択から外れる (2026-09-20)

`loop-run.sh` は issue の `## Status` 節の最初の非空行を読み、`blocked` で始まるものを
**既定の実行対象から外す**。`--issues 004,006` と明示すれば回せる (警告を 1 行出す)。

- **なぜ**: ⚠️ 以前は `issues/*.md` を無条件に列挙していたため、`blocked` の issue も走った。
  実績として issue 004 は blocked のまま回されて **attempt 1〜3 を失った**。
- ⚠ **`done` は外さない**。外すと `deps_met()` が永久に false になり、その issue に依存する
  後続が「依存 issue が未完のため未実行」で落ちる。完了の復元は events からの seed が担う。
- ⚠ **`## Status` が無い issue は回す**。テンプレの Status 節は見出しだけで値が空なので、
  外すと新規に切った issue が黙って走らなくなる。
- ⚠ 判定の前に **先頭の記号・絵文字・`**` を剥がして小文字化する**。
  実在する書式 (`✅ **done**（…）` / `⚠️★★★ **不要（not needed）**`) と同じ形で `blocked` を
  書かれると、素の前方一致は **fail-open する**。
- 除外は **ログと `_loop-run-report.md`** に出す。⚠ events には出さない
  (events 語彙は上の語彙表の種類で固定であり、「実行しなかった」は状態遷移ではない)。
  ★ ただし **`--issues` で `blocked` を承知で回したとき**は、その attempt の
  `attempt_start` に `detail` を 1 行足す (⚠ 迂回が端末のスクロールバックにしか残らないのを避ける)。

**追補 (2026-09-25): attempt 中に worker が worktree 側で `blocked` にしたら、その attempt の
verify 失敗で打ち切る。** 上の除外判定は main checkout 側の `## Status` を**起動前**に 1 回読むだけ
なので、worker が「Allowed Files の外の変更が必要」と判断して**worktree 側**のコピーの
`## Status` を `blocked` に書き換えて止まっても、`loop-run.sh` は気づかず同じ worker を
`max_attempts` まで再起動していた (issue 001 の実測で 5 attempt の空回り)。
→ worktree 生成直後の `## Status` を記録しておき、verify 失敗のたびに worktree 側を読み直して
「開始時は `blocked` でなかったのに今 `blocked`」という**遷移**だけを検知したら、その場で打ち切る
(`--issues` で最初から `blocked` な issue を明示実行する経路は遷移が起きないため対象外のまま)。

### ⚠ `permission_denials` を残すときは、先に伏せる (2026-09-20)

`loop-run.sh` は拒否の内訳を events の `detail` (集計) と
`<task>/_loop-artifacts/<id>-attempt<N>-denials.json` (生配列) に残す。

- ⚠ `.tool_input.command` は worker が組み立てた**自由文字列**で、資格情報が混ざりうる。
  → **`KEY=VALUE` の値・秘密らしいキーの直後の値を伏せ、1 件 200 字で切ってから**保存する。
  ⚠ 伏せる前に集計キーを作らないこと (★ 「先頭 2 語」は `KEY=secret cmd` を狙い撃ちで拾う)。
- ⚠ 集計キーは **`tool_name` ではなくコマンドの先頭 2 語**。拒否はほぼすべて `tool_name == "Bash"`
  になるため、`tool_name` を数えても「何が拒否されたか」は分からない (★ 2026-09-20 に実測)。
- 成果物は 14 日で prune する。`.gitignore` は **`**/_loop-artifacts/`**
  (⚠ `.steering/**` に限定すると、外に置いた task-dir で ignore が外れる)。

**`claude -p` は完全なセッション**であり、機能が削られた実行ではない。だからカスタムスラッシュ
コマンド・hook・settings.json・権限設定がすべて効き、worktree 内で `loop-guard.sh` が発火する。
C は「script が外から数える」「hook が内から止める」の**二重の停止機構**を持つ唯一のモード。
また 1 attempt = 1 新セッションなので、**セッション境界が構造的に保証される**。

**新しい実行モードを初めて使う時は、最も安い issue 1 本を `parallel=1` で回して基盤を検証する。**
`--dry-run` では権限・cwd 境界・hook 発火・契約の二重定義が観測できない (実測で 2 回空振り)。

`_loop-config.json.mode` に `"A"` / `"B"` / `"C"` を pin する。
**全モードで events / board / watchdog gate / Stop 条件の契約は同一**。変わるのは制御の主体だけ。

### ⚠ 2026-09-26 の是正 (P1 前タスクの起票 P1-I / J / K / B / D ・ `.steering/20260926-loop-foundation-p1-fixes/`)

- **P1-I — 未コミットの attempt は verify を回さず失敗にする (done にしない)。** 上の語彙表 `uncommitted` を参照。
- **P1-J — 切り元はローカルと `origin/<base>` の祖先関係で決まる。**
  `loop-spawn.sh` は fetch 後に比べ、一致 → origin ／ **ローカル先行 → ローカル** (⚠️ 未 push のコミットを含む) ／
  ローカル遅れ → origin ／ **分岐 → fail-closed で止まる** (worktree も branch も作らない)。
  選んだ理由は provenance ブロックの `start-choice = <equal|local-ahead|local-behind|no-local|fetch-failed>` 行に出る。
  ★ モードC ではローカル先行を attempt 1 の `attempt_start` の `detail` (WARN) にも残す。
  ⚠️ 旧実装は fetch に成功すると**無条件に origin から切った** (push 前にローカルで merge した 005 を含まない枝から 006 が切られた)。
- **P1-K — spawn は直列化される。** `git worktree add` は upstream 設定で `.git/config` を書くので、
  同時に 2 本走ると片方がロックで落ちていた。`loop-spawn.sh` は `<git-common-dir>/loop-spawn.lock` (mkdir ロック) を取って
  worktree を作る。⚠️ `worktree add` が失敗して**ブランチだけ残った**ときは、作成時から動いていなければ消してから止まる。
- **P1-D — `## Dependencies` の装飾は剥がしてから拾う。** `- **001**` も依存として拾う。
  箇条書きの先頭にない 3 桁数字 (散文中の「issue 004 の merge 後に」など) は依存にしないが、**WARN を出す** (黙って落とさない・止めもしない)。
- **P1-B — worker は acceptance を自分で回せる。** テンプレの `allowed_tools` に `Bash(bash .steering/**/*-acceptance.sh)` を入れた。
  ⚠️★★★ **これは境界ではない** —— worker は `Write` で任意の `*-acceptance.sh` を作れ、`.steering/../` でも外へ出られる
  (★ 2026-09-26 に `claude 2.1.282` で実測。権限上は `Bash(bash:*)` と同等)。境界は従来どおり
  worktree ブランチ検査・必須 deny・人の merge ゲートである。
  ⚠️★★★ **Loop の verify の合否は worker の影響を受けうる。** verify は main checkout 側の acceptance を走らせるが、
  任意のコードを実行できる worker はそのファイルも書き換えうる (★ `cargo run` / `cargo test` の build.rs 経由でも元から可能。
  test / typecheck / lint も worktree の中で走る)。→ ★ **合否を最終的に決めるのは、merge 前にメインが clean な checkout で回す acceptance**
  (★ 前タスク判断 21 / 22 の運用。`security-checker` MEDIUM・2026-09-26 で旧文「書き換えても合否は動かない」を訂正)。
  ⚠️ 途中に `*` を置く形 (`Bash(bash .steering/*/issues/*-acceptance.sh:*)` / `… *)`) と前方一致 `Bash(bash .steering/:*)` は**効かなかった** (同実測)。
- ⚠️ **P1-H (verify が他の issue の門を回さない) は未是正**。メインが merge 前に全 acceptance を正しい終了コードで回す運用で補う。

<!-- loop:codex:begin -->
## Codex ゲート (任意・タスク境界のみ)

Codex はタスク境界の 2 点にだけ配置する。issue ループの内側 (毎 attempt・毎 issue) には
入れない。マルチエージェント構成はトークンを ~15x 消費しうるため、coarse・低頻度・
コスト有界に固定する。issue 内の意味判断は Haiku watchdog (安価) が担う。

| 高度 | 担当 | model | 頻度 | 権限 |
|---|---|---|---|---|
| issue ループ内 (毎 attempt) | `loop-guard.sh` / `loop-watchdog` | script / Haiku | 高頻度・安価 | 監視・停止のみ |
| **タスク境界 (前)** | `codex-consult` | gpt-6-astra | task 毎 1 回 | read-only |
| **タスク境界 (後)** | `/cross-review` (codex-review ∥ code-reviewer) | gpt-6-astra ∥ Opus | task 毎 1 回 | read-only |

### TASK-PRE: issue 独立性の第二意見 (codex-consult, read-only)
grill → /start-task → /to-prd → /to-issues で issue が確定した**直後**、
実行 (loop-issue) を始める**前**に、1 回だけ実行する:

1. issue 一覧の公開可能な最小抜粋 (各 issue の Goal / Scope In-Out / Allowed Files /
   Dependencies / AC↔test) を整形する。internal 名称は仮名化。
2. 既存 `codex-consult` skill を起動 (内部で `scripts/run-codex-consult.sh` が
   secrets-filter + budget チェックを実施。read-only)。設問を固定する:
   - これらの issue は**本当に独立/並列化可能**か。隠れた共有状態・暗黙の順序依存は無いか。
   - 抜けている**エッジケース**は何か。
   - **順序ハザード** (先行 merge が後続の前提を壊す、schema/API の破壊的変更順) は無いか。
   - vertical slice の切り方に、後で衝突する分割はないか。
3. Codex の応答を `.steering/[YYYYMMDD]-[task]/_codex-preplan.md` に保存する。
4. **これは助言**。採否は人が決める。盲点は issue/Dependencies に反映し、
   誤検知 (Codex は文脈の半分しか持たない) は却下理由を preplan に併記する。

### 日常運用との対応 (README §3・再掲のみ・新規手順は作らない)
- 端末0 の計画時: `/to-issues` 直後に「必要なら TASK-PRE (codex-consult) で issue 独立性を第二意見」。
- 全 issue 緑: 「TASK-POST (/cross-review) → 統合フル CI 確認 → merge → retrospective」
  (TASK-POST の手順は `.claude/commands/loop-issue.md` ＜loop:codex＞ 節を参照)。
<!-- loop:codex:end -->
