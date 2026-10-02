# carryover-audit — round 3 からの引き継ぎ（意図の監査役）

作成: 2026-10-02（メイン）。あなた（監査役）の round 3 の指摘 11 件（1-1・1-2・2-1・3-1〜3-8）と、round 3 であなたが「部分的に解消」と判定した前の指摘 3 件（round 2 の 1-a、round 1 の 1-4・3-8）と nit 1 件（round 2 の 1-b）について、メインの裏取り・研究者の採否・対応・未解決を書く。
⚠️ **再掲を求めない**。各指摘が今の版で**解消したか**を 1 件ずつ判定してから（解消 / 部分的に解消 / 未解消・理由 1 行・今の版の位置）、**今回の直しが作った新しい食い違い**を探してほしい。round 3 で「解消」と判定した指摘は引き継がない。

## 版の変化（round 3 の版 `abc5d7f9` → 今の版 `159a2ec8`）

- 節番号は変わっていない。round 3 の行番号は使えない（本文は 11,217 語から 12,143 語に増えた）。変わった節とコードの関数は context-A の「round 3 から変わった箇所」。
- 意図の資料は、判断 112〜115（`decisions.md` 912〜939 行）が増えた（context-B）。

## A. round 3 の指摘

裏取りの判定は、メインがコード・計画・事前登録で確かめた結果。2-1 の「出どころが判断 108〜111 に無い」の部分だけ偽陽性（下）、ほかは真。

### 1-1 判断 108 の X2 の新しい `long` の定義が、言い方に届いていない
- 対応: §1.2 の問 2（「For the sessions that reach the 20-second cut-off, does the observer write no row, as specified?」）・`l2.py` の docstring（「under_limit, which sets aside the trials whose presses went into a session that the observer is specified to cut off」）。

### 1-2 題が登録の範囲を言っていない（nit）
- 採らなかった: 題は変えていない（任意の nit。メインの選択）。範囲は §1.3 にある。

### 2-1 §3.4 の新しい中止の規則
- 裏取り: 食い違いの 4 点は真。出どころは、round 2 の直す一覧の minor（run の関門）を判断 110 が「直す一覧を全部承認」で承認したもの（あなたは直す一覧を読めない設計なので、確かめられなかったのは当然）。
- 研究者の採否（判断 112 の Y2）: 中止は参照のログが実行器の外からの打鍵を示すときだけ、閉じた規則で決め、「説明」の裁量を無くす。観測の余分な行は観測器の結果として解析し、§6.3 で報告する。検査は `delivery.py` 単体（key 行だけ）で、各 run の直後・§3.2 の次の項目の前に行い、判断と時刻を解析の前に記録する。
- 対応: §3.4（「… or when the reference log shows a key press from outside the executor: … the reference's `excess_rows` over all presses is greater than zero, or its `rows_outside_trials` exceeds the five presses made outside the trials in each block (four marker presses and one kana press). No other reason and no explanation is admitted. The check is made right after the run (section 3.2), and its result and time are recorded in `experiment/data.md` before any analysis of the run. Rows of the observation without a sent press are a result of the observer under test (section 6.3) and never make a run count as aborted.」）・§3.2 の最後の文・§6.3・`data.md`（「Run checks」の表と手順 1）。判断 115 の 2（`delivery.py` の今ある出力で書き、判定の欄は足さない・外からの入力で中止にした run は預けない）。

### 3-1 §7 の「より細かい粒度は評価しない」が §6.8 と合わない
- 対応: §7（「the feature sets that keep times are reported as estimates only, and granularities between milliseconds and one-second bins are not evaluated」）。

### 3-2 §7 の入力モードの文が S14 と合わない
- 対応: §7（「The input mode is switched only by the mode keys (the kana key at the start of each block, and the alphanumeric and kana keys of S14), so a switch made otherwise (from a menu or with a shortcut), which the observer follows by polling the input source, is not exercised.」）。

### 3-3 `kit\e2\README.md` と事前登録が、余裕 2/K とブロック内の依存で食い違う
- 対応: README の 2 か所の余裕の文を「the upper end of the Wilson interval with the margin 2/K, which is a design choice, not derived from the block dependence or from a criterion of privacy」に。依存の理由を「the state of the input method and the block's marker; each trial draws from its own random state, derived from the seed and the trial identifier, so the trials of a block do not share a random state」に。2 つの集合の順序（`counts_only` は `no_time` を粗くしたもの）の文を足した。

### 3-4 `notes.md` の「すべての結果のファイル」が言い過ぎ
- 対応: `notes.md`（「The result files of questions 1 to 3 (`e1_detection.json`, `e1_l1.json` and `e1_l2.json`) name their primary comparison and scope」）・`pipeline.py` の docstring（同じく 3 つのファイルに限った）。

### 3-5 回収の遅れの言い方が §4.4 と合わない（nit）
- 対応: §6.9（「the collection delay of a row (section 4.4) shifts an observation interval by up to about 100 ms」）。

### 3-6 印を oracle が記録するかどうかが §4.5 と §4.2 で食い違う（nit）
- 対応: §4.5（「the keys of the marker presses (the oracle records their times; the keys come from the plan)」）。

### 3-7 断片の行がどの試行に属するかが §6.2 の割り当てと合わない（nit）
- 対応: §6.4 の `over_limit`（「whose row is assigned, like every row, to the trial it overlaps most (usually the trial in which that press falls)」）。

### 3-8 §1.2 と §6.3 で区間の範囲があいまい（nit）
- 対応: §1.2・§6.1 の区間を付けないものを「the delivery figures of section 6.3」に限った。

## B. round 3 で「部分的に解消」と判定した前の指摘

### 1-a パイロットの生ログを預ける基準と、封印した行の扱い
- 研究者の採否（判断 113 の Y4）: 預ける基準と「封印したセッション行は預けるときだけ開け、解析しない」を、凍結の前に測定機で `pilot-macos.md` の Raw logs に書く。あわせて、パイロットの観測の key 行に問 4 の割り当てだけを流し、採点したブロックの割合を §3.1 に書く。
- 対応: §3.1 に「which are written before the freeze」と、割り当てをパイロットの key 行に流す約束の文を足した。
- ⚠️ **未解決（既知）**: どちらも中身はまだ無い（`pilot-macos.md` の Raw logs は "will be written here" のまま・§3.1 に割合は無い）。パイロットのログは測定機にある。round 4 の後に行う。この版で判定するのは、約束の文の書き方（何を・いつ・どこに）だけでよい。

### 1-4 一致の限界の幅を予想しない理由
- 対応: §3.3（「The limits of agreement (the bias plus or minus 1.96 SD) are located to about 1.96 x SD x sqrt(3 x D / n) (Bland & Altman, 1986), about 0.39 x SD with 75 pairs and D = 1. No width is predicted for kappa and the ICC, because it depends on the values estimated」）。

### round 1 の 3-8（問 4 の場面ごと・速さごとの正解率の区間。上の round 3 の 3-8 とは別）
- 研究者の採否: 区間を付けないものの一覧に足す側。
- 対応: §1.2・§6.1 の区間を付けないものに「the per-scenario and per-speed accuracies of question 4」・§6.8 の Reported を「descriptively and without an interval, the accuracy of the feature set alone per scenario and per speed」に。

### 1-b の nit（依存の文）
- 対応: §6.8（「With dependence within a block, the true uncertainty of an accuracy is larger than its Wilson interval shows, so a rule that reads the Wilson upper end is met more easily than it should be」）・§7 の同じ項・README。
