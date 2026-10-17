# 引き継ぎ: 背景のステージ —— 揺れの形を分けた world の後

作成 2026-10-17（Windows・G-GEAR）。返答・記録・AskUserQuestion の引数は日本語で書く。記号（★・⚠️）は多用しない。AskUserQuestion には推奨と理由を添える。

前の引き継ぎ: `.steering/_handoff/next-session-rhythm-stage-speed-shape-world.md`（このタスクの中身）と `.steering/_handoff/next-session-rhythm-stage-after-cause-split.md`（その前の状態）。

## 0. 最初にやること

1. `Get-CimInstance Win32_Process` と `gh run list` を一次で見る。
   - 2026-10-17 の時点で `a4_keytar.py` は走っていた（python 2 本・10-14 01:45 開始）。走っている間は PR を出さない（memory の「計測の run 中は PR を出さない」）。
2. `a4_keytar.py` が終わっていれば、出荷を 2 段で行う。
   - まず `docs/rhythm-stage-speed-confound`（揺れの world と原因の切り分けの 2 タスク・`3c66a290` まで）の PR を出し、CI が緑なら merge する。
   - 次に `docs/rhythm-stage-speed-shape`（このタスク・`3c66a290` の上に積んだ）を merge 後の main に載せ直し（rebase）、PR を出す。
   - rebase で `.codex/budget.json` が衝突したら、memory の「台帳はブランチごと」の規則（起点からの差分の和）で解く。`git checkout --` で戻さない。
3. 次のタスクは決まっている（§3・まとめ）。

## 1. 状態

- worktree `C:\wt\rhythm-stage-speed-confound`、ブランチ `docs/rhythm-stage-speed-shape`（push 済み・最後は `5fdbbd4c`）。PR は未作成。
- タスクの記録: `.steering/20261015-rhythm-stage-speed-shape-world/`（requirement・design（固定 `74754d26`・§8 は値の追記だけ）・decisions 判断 1〜16・tasklist）。
- 入れ物: `experiments/20261015-rhythm-stage-speed-shape-world/`（`notes.md`・`results/{ceiling,d100,d200,f200,compare}/`・`check_notes.py`）。
- `/cross-review` は固定の前に 2 巡（判断 12〜14）、notes に 2 巡（判断 15・16）を通した。tasklist の残りは「引き継ぎ・PR」だけ。

## 2. 結果（notes.md の要約・詳しくは notes）

- 段: f100 は下見 0 で天井（回していない）。d100・d200・f200 を本番まで回した（どれも読みの門 866 値・最大の差 0）。
- 成分の読み（固定の表）: c = 1 は `not_run`（`f(1)` が天井）、c = 2 は `unsettled`（`f(2)` は 24 本のうち 16 本が判定不能）。主な問い「`h(c)` の赤は倍率 `u` と漂い `d` のどちらから来るか」に、この試行は答えていない。
- 漂いだけの world `d(c)` では、c = 1・2 とも L300 に赤が出て、`R2` を落とすと「残る」が 0 になった（「決まらない」が 1 本ずつ残る）。`r` の側の対照 PCr-level は、`R2` を落としても働いた。
- `f(2)` が判定できなかったのは、16 本で停滞の陽性対照 PC-stall が働かなかったため（`weak_stall_pc`）。理由は分けていない（推論の候補: `A_speed` の強さ・λ の格子の上端（8 本について）・PC-stall の形）。
- 所要は 1 段で約 14〜15.4 時間（下見 1 約 5.9 h・本番 約 5 h・読み 約 2.6〜3.8 h）。rank の候補が遅い（下見 1 の時間の 6 割強）。研究者は 10-16 に「下見長くない？」と聞いた。縮める案は固定の後の変更になるので採らなかった。

## 3. 次の候補（2026-10-17 に研究者が候補 2 を選んだ → `next-session-rhythm-stage-summary.md`）

1. 倍率の world を読めるようにする: PC-stall の λ の格子を延ばす（PCr で行ったように 1.0 まで）か、`A_speed` を弱める作り（c を上げる・別の要約）で `f(c)` を作り直す。新しい計器なので、design → `/cross-review` 2 巡 → 固定 → 下見 0 から。rank の遅さを先に直すと、1 段の所要が縮む見込み（直すなら計器の固定の前に、出力が変わらないことを確かめて）。
2. 背景のステージの机上の検査をここで区切り、第 1 回からの 6 回（第 1 回・第 2 回・中間の world・揺れの world・原因の切り分け・揺れの形）をまとめる。
3. ほかの研究者の案。

## 4. 守ること

- 第 1 回・第 2 回・中間の world・揺れの world・原因の切り分け・揺れの形の入れ物と判定を書き換えない。
- 合成の列だけを使う。NDJSON の生ログ（合成のものも）とキーストロークの内容を、外部の LLM（Codex を含む）に送らない。
- `src-tauri/` と EH3 のファイルに触れない。
- `.codex/budget.json` を `git checkout --` で戻さない。回す前に、worktree の台帳と origin/main の台帳を見る（予算ガードの hook は `C:\GSE-prototype` の台帳を読む）。
- `git add -A` を使わない。
- バックグラウンドの実行の「completed」の通知は、終わりより早く届くことがある。結果のファイルとログを一次で確かめてから報告する。
- 「GSE が示した」と書かない。揺れの形（倍率・OU の漂い）は Claude が選んだ一例で、人の打鍵の速さの揺れを写したものではない。
- notes の表を直したら `python check_notes.py .`（experiment の dir で）を回す。
