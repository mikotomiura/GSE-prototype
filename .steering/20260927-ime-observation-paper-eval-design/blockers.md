# blockers — IME 論文の評価一式（ループの実行）

## B1（2026-09-28・W1）spawn が main checkout の未追跡ディレクトリで止まった

- 事象: `bash scripts/loop-run.sh <task> --issues 001` の 1 回目が `loop-spawn: 作業ツリーに未コミット変更があります … 中断 (LOOP_FORCE=1 で強行可)` で止まり、events に `blocked`（`worktree 生成に失敗`）が 1 行残った。
- 原因: main checkout に**別トラックの未追跡ディレクトリ** `.steering/20260921-media-expression-theory-audit/` がある（`loop-spawn.sh:958` の `git status --porcelain` が未追跡も数える）。
- 対応: そのディレクトリには触れず（別セッションの作業の可能性がある）、`LOOP_FORCE=1` を付けて再実行した。
  ★ `LOOP_FORCE` が外すのは dirty 検査（`loop-spawn.sh:958-962`）だけで、base の解決（`--task` 指定・provenance の出力）は別経路であることを一次で確認した。再実行の provenance は `base = feature/ime-eval-kit` / `start-choice = equal` / 乖離 0。
- ★ 次の波も同じ状態なら `LOOP_FORCE=1` を付ける。

## B2（2026-09-28・W1）`loop-run.sh` の RETURN trap が呼び出し元に漏れる（既存の欠陥・未修正）

- 事象: 1 回目の run の stderr に `scripts/loop-run.sh: line 661: spawn_err: unbound variable`。
- 原因: `run_issue_body` の中の `trap 'rm -f "$spawn_err"' RETURN`（`loop-run.sh:693`）が関数の戻りで解除されず、呼び出し元 `run_issue` の `return`（`:661`）でも発火する。そこでは `local spawn_err` が既に無いので `set -u`（`:14`）で落ちる。
- 影響: `run_issue` は `&` のサブシェルで走り、戻り値は `wait "$p" || true`（`:1150`）で捨てられ、合否は events で決まる。→ ★ **判定には影響しない**（stderr の雑音とサブシェルの非 0 終了だけ）。
- 直し方の候補: trap の中で自分を外す（`trap 'rm -f "$spawn_err"; trap - RETURN' RETURN`）。
- ⚠️ 本タスクでは直さない（`scripts/` は本タスクの範囲外・全 issue の acceptance が `forbid_gse_changes` で `scripts/` の差分を禁じている）。Loop 基盤の別タスクで扱う。

## B3（2026-09-28・W1）`recheck` の watchdog は、このタスクでは何も再実行できない（読んで判断しているだけ）

- 事象: 001 の watchdog は try 1 で「ユーザーに確認してから実行します。acceptance script を走ら…」と返して解釈不能になり、try 2 で `OK` を返して `issue_done` になった。
- 原因: watchdog の許可ツール `WD_TOOLS`（`loop-run.sh:363`）は cargo / npm / git diff / cat 等だけで、**`python` も `bash` も入っていない**。本タスクの verify と acceptance はすべて `bash` / `python` なので、watchdog は **verify も acceptance も再実行できない**。→ `OK` は**読んだうえでの判断**であって、独立の再実行ではない。
- 影響: ★ `verify_level: recheck`（19 / 27 本）の「独立の再検証」は、このタスクでは実質的に効いていない。
- 対応: ★ merge ゲートの合否は、**メインが clean な checkout で回す acceptance** で決める（`docs/loop-engineering.md` P1-B の「合否を最終的に決めるのは merge 前にメインが clean な checkout で回す acceptance」のとおり）。W1 では clean な checkout（`loop/001-issue` を detached で）で `001-acceptance.sh` 失敗 0 件・verify 3 本と `check.sh --self-test` が exit 0・変異（未知キーの拒否を殺す）で selftest / `check.sh` / acceptance がすべて赤になることを確認した。
- 直し方の候補（Loop 基盤の別タスク）: `_loop-config.json` から watchdog の許可ツールを足せるようにする（例 `headless.watchdog_allowed_tools`）。⚠️ 本タスクでは `scripts/` を変えない。

## B4（2026-09-28・W2 の前）予算の積算は run ごと・G-GEAR には flock が無い

- `token_ceiling` は**1 回の `loop-run.sh` ごと**の上限（`loop-run.sh:574` で run のたびに `mktemp` で 0 から数え直す）。タスク累計ではない。
- W1 の実測: issue 001 の 1 attempt（worker ＋ watchdog 2 回）で **6,172,416 トークン**（キャッシュ込み）・**$2.68**。→ W2（G-GEAR 7 本）を 1 run に入れると、1 attempt ずつでも約 4,300 万 ＞ 4,000 万で**途中で止まりうる**。
- G-GEAR に `flock` が無い（`command -v flock` が空）。`add_usage`（`loop-run.sh:617-624`）は flock が無いとロックなしで読み書きするので、`parallel` ≥ 2 では積算が**競合で少なく数えられ**、`token_ceiling` の停止が遅れうる（判定の合否には影響しない）。
- 対応案: W2 を 2〜3 回の run に分ける（同じ波の issue どうしは独立なので分けてよい）・`parallel` は 1 のまま、または積算の不正確さを承知で上げる。
- ★ 研究者の判断（2026-09-28）: W2 の G-GEAR 分は 2 run（002,003,010,016 → 008,011,015）・`parallel=1` で回す。

## B5（2026-09-28・W2）010 は成果物が合格なのに、watchdog の空応答で `blocked` になった

- 事象: 010 の attempt 1 で verify が緑になった後、watchdog が 2 回とも**空の応答**を返し、`loop-run.sh` が fail-closed で `blocked`（`watchdog の verdict を解釈できず`）にした。`issue_done` は出ていない。
- 確認: worktree はクリーン・コミット 2 件。clean な checkout（`loop/010-issue` を detached）で `010-acceptance.sh` 失敗 0 件（✅ 14 件）・`check.sh` 緑。→ ★ **成果物は合格**。B3 のとおり watchdog はもともと何も再実行できないので、判定の材料は失われていない。
- 影響: ⚠️ `deps_met` は events の `issue_done` だけを見るので、**010 に依存する 020（W5）は「依存 issue が未完」で起動しない**。⚠️ `issue_done` を手で書かない（events の writer は `loop-run.sh` だけ）。
- 対応: 010 はメインの merge ゲート（clean な checkout の acceptance ＋ レビュー）を通して base へ merge する。W5 の前に、020 の起動の扱い（依存の書き方を変えるか、010 を `parse` に落として再実行するか）を研究者に問う。
- ★ 研究者の判断 34（2026-09-28）: 未実行の `recheck` 14 本を `parse` に落とし、`blocked` のまま merge した 008 / 010 / 011 を後続の依存から外した。
- ⚠️ **同じ形が W2b でも 2 本続いた**: 008（03:34）・011（03:46）も attempt 1 の verify の後に watchdog が空応答で `blocked`。→ W2 の `recheck` 5 本のうち 3 本（010 / 008 / 011）が watchdog で止まった。★ watchdog は B3 のとおり何も再実行できないので、止まるたびにメインの独立検証で置き換えている。残りの `recheck` の issue の `verify_level` をどうするかは研究者に問う。

## B6（2026-09-28・W2 の直し）作業用エージェントが main checkout の issue ファイルを一度書き換えた

- 事象: 015 の直しを渡した作業用エージェント（general-purpose・Sonnet）が、worktree ではなく main checkout（`C:/GSE-prototype`）側の `issues/015.md` を誤って編集し、自分で `git checkout --` で戻したと報告した。
- 確認: メインが直後に `git status` と `git diff HEAD` を見て、main checkout が HEAD（`da69335e`）と一致し、別トラックの未追跡物も残っていることを確かめた（失われたものは無い）。
- ⚠️ 危うさ: main checkout に未コミットの変更があった場合、`git checkout --` はそれを消す。今回は main 側の 015.md に未コミットの変更が無かったので無害だった。
- 次から: 作業用エージェントへの指示に「main checkout（`C:/GSE-prototype`）のファイルを編集しない・`git checkout -- <path>` で戻さない（間違えたら報告して止まる）」を明記する。

## B7（2026-09-28）Rust のビルド生成物を含む clean な checkout は `git worktree remove` で消せない

- 事象: `target/` の中のパスが長すぎ（Filename too long）、`git worktree remove --force` が失敗する。git 側の登録は外れ、ディレクトリが scratchpad に残る。
- 対応: bash の `rm -rf` で消してから `git worktree prune`。

## B8（2026-09-28・W3 の直し）`closed_set.py` の selftest が 22 秒になった（入口の警告の目安 30 秒に近い）

- 事象: 021 の直し（判断 39 の位相の探索・シナリオ別の囮）で、`kit/check.sh` の `e2/closed_set.py` の selftest が約 22 秒（G-GEAR）。入口は 1 本 30 秒を超えると警告を出す（止めない）。
- 影響: 遅い機械（Mac）では警告が出うる。verify と各 acceptance で毎回回るので、W4 以降の所要時間が延びる。
- 対応の候補: 重い検査を `--selftest --full` に分けて既定を速くする（入口の規則どおり）。★ 判断 36 の整理の issue で一緒に行う。

## B9（2026-09-28・W3）作業用エージェントが「自分のバックグラウンドの処理が残ったまま止まった」と通知された

- 事象: 013 / 009 の直しのエージェントが、完了報告の後に「background work of its own still running」と通知された（cargo の実行が残っていた可能性）。
- 対応: merge の前に、worktree の `git status` が空で HEAD が報告のコミットのままであることを確かめてから merge した（どちらも一致）。★ 次からも、報告の後で worktree が動いていないことを merge の直前に確かめる。

## B10（2026-09-29・Mac の W2 の前）Mac の base で verify がベースラインから赤・この checkout は別セッションが使っている

- 事象 1: `kit/check.sh` が `analysis/gt_sessions.py` の 1 ケースで赤（深い入れ子が拒否されない）。Python 3.14.4 の `json` は 3000 段で `RecursionError` を出さない。→ 判断 47 で selftest の深さを上げた。
- 事象 2: main checkout（`/Users/johnd/GSE-prototype`）は別の対話セッションが別ブランチ（`docs/g1-o1-collection-readiness`）で未コミットの作業中だった。→ ★ ブランチを切り替えず、base を別 worktree（`/Users/johnd/GSE-ime-base`）に出し、`loop-run.sh` には **その worktree の task ディレクトリを絶対パスで渡す**（`TASK_DIR` は絶対パスならそのまま使われ、config・issue・acceptance はそこから読まれる）。events は §7 のとおり main checkout の絶対パス。spawn の dirty 検査は main checkout を見るので `LOOP_FORCE=1`（B1 と同じ）。
- 事象 3: 004 / 007 の依存 `001` が Mac の events で満たされない → 判断 47。

## B11（2026-09-29・G-GEAR で Mac の W2 / W3 を取り込んだとき）Windows で `kit/check.sh` がベースラインから赤

- 事象: G-GEAR で base（`91289c09`）の clean な checkout に全 acceptance を回すと、全 17 本（Windows で回るもの）が `kit/check.sh` の 1 件で赤。落ちていたのは 004 の `emit/emit.py` の selftest の時間の 3 ケース（遅れの 95 パーセンタイル・試行間の待ち・マーカーの間隔）。
- 原因 1: Python 3.11 の Windows では `time.monotonic()` が 16 ms 刻み（`GetTickCount64`）、`time.time()` の宣言上の分解能が 15.6 ms。oracle の時刻がこれで取られていた。→ 判断 52。
- 原因 2: 同じ機械で別プロジェクト（`C:\ERRE-Sand_Box`）の計算が CPU を 82% 使っていて、送出の遅れの 95 パーセンタイルが 20 ms を超えた（高い優先度では 0.04 ms）。→ 判断 53。★ そのプロセスには触れていない。
- 影響: 直すまでは 005 / 006 のループの verify がベースラインから赤になる（`docs/loop-engineering.md` のモード C の条件 ③）。
- ★ 教訓: 004 の acceptance は `require_os macos` なので、`emit.py` の selftest は Windows では一度も回っていなかった。**「どちらの OS でも走る selftest」（`check.sh` が拾うもの）を片方の機械だけで merge したら、もう片方の機械で全 acceptance を回すまで完了としない。**

## B12（2026-09-29・W3 の残りの merge の後）`emit.py` の既定の selftest が間欠的に赤（約 1%）

- 事象: 005 / 006 を merge した後の base（`5668dccd`）の clean な checkout で全 acceptance を回すと、005 の AC5（`emit.py --selftest`）だけが 1 回赤になった（同じ acceptance の中の `kit/check.sh` と、回し直しは緑）。既定の selftest を 200 回回すと 2 回、どちらも「no key is sent before its planned time」で落ちた。
- 原因: `run_trial` が送出の基準 `start = time.perf_counter()` を、`trial_begin` 行の刻印（`_emit` の中の `_stamp()`）より**先に**取っていた。その 2 つの文の間でプロセスが止められると、oracle 上の `trial_begin` が実際の基準より遅れ、鍵が「計画より早く送られた」ように見える。★ 実データでも oracle の試行の窓が実際の基準からずれる。
- 再現の試み: 16 コアを埋めた負荷・低い優先度では再現しなかった（止められる位置が 2 文の間に当たる確率が低い）。200 回の繰り返しで捕捉した。
- 対応: 判断 59（基準を刻印そのものにする・004 の追補）。★ 退行を決定的に捕まえるケースを selftest に足した（`trial_begin` の刻印だけを 5 ms 遅らせても早く送らない）。
- ⚠️ `emit.py` を変えたので、Mac で `004-acceptance.sh` を回し直す（B11 の教訓）。

## B13（2026-09-30・Mac で W6 の 024 を確かめたとき）書き出しの一覧の SHA-256 が Mac と G-GEAR で合わない —— 測定器の改行

- 事象: 同じ `papers/`（`c6305340`）の書き出しについて、`024-acceptance.sh` が出す「書き出しの一覧の SHA-256」が Mac `577caaff…`・G-GEAR `9e586e52…` と違った（どちらも 91 ファイル・失敗 0 件）。
- 原因: 書き出しの中身ではなく測定器。一覧を作る Python が `sys.stdout.write`（テキスト）で書いていて、Windows の Python が改行を CRLF に変えていた。bash の `$( )` は末尾の改行だけを落とし、`printf '%s\n'` が最後に LF を足すので、Windows の値は「行の区切り CRLF・末尾 LF」の一覧のハッシュになる。★ Mac の一覧をその形にすると `9e586e52…` と完全一致した → 91 ファイルはバイト一致しており、判断 68 は成り立っている。
- 対応: 一覧を `sys.stdout.buffer` にバイトで書く。一覧そのものに CR があれば ❌ にする検査を足した（陰性対照: CRLF で書く写しで ❌ を確認）。直した版の Mac の値は `577caafffe2c0aa743f34ae1491cdaa8297d119296e72f03a42d29200936f34a`。
- ⚠️ 残り: G-GEAR で直した版を回し、同じ値になるかを確かめる（tasklist）。
  → ✅ 2026-09-30: G-GEAR（`b2e284e2` の clean な checkout）で失敗 0 件・`577caaff…`（91 ファイル）で Mac と一致した。
- ★ 教訓: 「機械によらず同じ」を確かめる値は、値を作る道具そのものが機械によらないことを先に確かめる。不一致を見たら、まず測定器を対照で検算する。

## B14（2026-09-30・main への merge の前の /cross-review 1 巡目）機密フィルタが受け入れ検査の架空の値に当たって Codex の呼び出しの前に止まった

- 事象: 範囲 `c11b8b80..3ba24091` の 6 ファイル（判断 72）でラッパーを回すと `BLOCKED: secrets-filter detected sensitive content`（exit 2・Codex は呼ばれていない・トークン消費 0）。
- 当たった行（フィルタの報告は差分の 220 行目の 1 件だけ）: `issues/024-acceptance.sh` の陰性対照 `newf 2 secret "experiment/.env" "API_KEY=placeholder" "判断 70: …"`。判断 70 の「秘密の名前の型（`.env`）のファイルがあれば exit 2」を確かめるための**架空の中身**で、実在の鍵ではない（値は `placeholder`）。
- 対応: メインが差分の該当行を目で見て確かめ、研究者に示して承認を得た（AskUserQuestion「`--ack-filtered` で通す」）。→ ラッパーの `--ack-filtered` で回す（フィルタの置換は適用されたまま＝この行は `[REDACTED]` で送られる）。範囲は変えない。

## B15（2026-09-30・main への merge の後に Mac で全 acceptance を回したとき）main の上ではすべての acceptance の SCOPE が赤

- 事象: main（`6bf24b59`）の clean な worktree で回すと、各 acceptance の `only_allowed`（SCOPE）が「Allowed Files の外を変えている」で ❌（1 本あたり 1 件）。SCOPE 以外は全件 ✅。
- 測った原因: `_acceptance-lib.sh` の `_base` はローカルの `feature/ime-eval-kit` を先に見る。この Mac のローカル枝は `b2e284e2`（origin より 137 commit 古い・別の worktree が checkout したまま）→ merge-base からの差分 266 件。★ 最新の `origin/feature/ime-eval-kit`（`57210663`）を base にしても、main には #277 などの別トラックの 34 件が入っているので赤のまま（`papers/` の差分は 0 件）。
- 判定: 測定器の適用範囲の外。`_acceptance-lib.sh` 自身が「issue ブランチの上で回すと意味を持つ。merge 後の枝では差分が空になり素通りする」と書く検査で、main の上では base が定まらない。→ 失敗は SCOPE を除いて数える（Mac の確認の結果は tasklist）。道具は変えない（worker は `_acceptance-lib.sh` を変えない・判断の対象外）。
- ★ 教訓: main へ merge した後は、「枝の上の検査」と「中身の検査」を分けて読む。赤を見たら、まず何と比べた差分かを測る（B13 と同じく、測定器の検算が先）。
