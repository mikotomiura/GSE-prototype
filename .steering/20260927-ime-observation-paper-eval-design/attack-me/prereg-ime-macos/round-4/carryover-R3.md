# carryover-R3 — round 3 からの引き継ぎ（R3: 投稿先の方法論と再現性の番人の立場）

作成: 2026-10-02（メイン）。あなた（R3 の立場）の round 3 の新しい指摘 6 件（下で 1〜4・nit a・nit b と呼ぶ。あなたの round 3 の応答の §4 の順）と、round 3 であなたが「部分的に解消」と判定した前の指摘 3 件（N6・M2・M3）について、メインの裏取り・研究者の採否・対応・未解決を書く。
⚠️ **再掲を求めない**。各指摘が今の版で**解消したか**を 1 件ずつ判定してから（解消 / 部分的に解消 / 未解消・理由 1 行・今の版の位置）、**今回の直しが作った新しい穴**を探してほしい。round 3 で「解消」と判定した指摘は引き継がない（変わっていない節は round 3 の判定のまま）。
「採らなかった」部分は研究者の選択（またはメインの選択）で、理由を添えた。その理由が成り立たないと考えるなら、新しい指摘として根拠つきで書いてよい。

## 版の変化（round 3 の版 `abc5d7f9` → 今の版 `159a2ec8`）

- 節番号は変わっていない。round 3 の行番号は使えない（本文は 11,217 語から 12,143 語に増えた）。変わった節とコードの関数は context-A の「round 3 から変わった箇所」。
- 読んでよいファイルの一覧は round 3 と同じ（増減なし）。

## A. round 3 の新しい指摘

裏取りの判定は、メインがコード・計画・事前登録で確かめた結果。6 件すべて「真」（1 の「大きさ」はメインが計算していない）。

### 1 [major] 問 3 の主（`under_limit`）は、テキストを残したまま長い試行を抜くので、テキストごとの量と ICC に抜いた試行の数のばらつきが混ざる
- 裏取り: 真（`l2.py` の旧 docstring と `aggregate`）。
- 研究者の採否: あなたの解消の条件 (a) の前半（残った試行の上で定義し直す）。採らなかった: (a) の後半（ブロックの中で残った試行を 8 つずつ束ね直してテキストにする）・(b) の「速さのあいだで ICC を比べない」と書く道（定義を直したので）。
- 対応（文）: §4.6（「The four measures are computed for every text on both sides, over the trials of the text that are in the scope of the analysis (section 6.4): the conversions per trial (sessions or rows over the number of those trials), … and the fraction of time spent converting (total duration over the summed duration of those trials, each from its begin to its end). A text with no trial in the scope has no value (section 6.11).」）・§6.4 の問 3 の文・§6.7（「The number of a text's trials in the scope is reported per speed, and the texts with none are counted (section 6.11).」）・§6.11。
- 対応（コード）: `l2.py` の `MEASURES`（`n_conversions` を `conversions_per_trial` に改名）・`text_layout`（`out_of_scope`）・`aggregate`・`evaluate`（`texts.trials_in_scope_by_speed`）。
- メインの実装上の選択: 定義は**すべての範囲で同じ**（範囲が変えるのは、どの試行を数えるかだけ）。`dwell_fraction` の分母は「範囲の中の試行の窓（oracle の begin〜end）の和」で、`all_trials` でも試行の間の待ちを含まない。範囲の中に試行が 1 つも無いテキストは 4 つの量とも null で、速さごとに数える。試行ごとの量（`per_trial` の `n_conversions` ほか）は名前も定義も変えない。

### 2 [minor] 設計効果の上限の計算が、層ごとの試行の割り付けと合わない
- 裏取り: 真（メインが 2 つの計画〔SHA-256 は登録の値と一致〕から計算: 1 つの層の Σm²/Σm は ON 2.36〜3.13・OFF 2.47〜3.43、層の 75 試行が入るブロックは ON 33〜39・OFF 30〜37、区間の幅の倍率は最大 1.77 倍・1.85 倍。round 3 の版の「約 42 ブロック」は速さあたりのブロックの数だった）。
- 対応: §3.3 の「Precision of continuous measures and the design effect」に式と計画から計算した値を 1 か所に置き（「D is therefore at most about 3.4 and usually near 1 … and at most about 1.8 times that」）、§6.1 は §3.3 を参照する形にした。
- 採らなかった: 式の出典を添えること（新しい書誌の確認が要る。メインの選択）。

### 3 [minor] run 単位の関門の「説明できる」に基準が無く、解析の結果を見てから判断できる
- 研究者の採否: 中止は参照のログが実行器の外からの打鍵を示すときだけ、閉じた規則で決め、「説明」の裁量を無くす。検査は `delivery.py` 単体（key 行だけ）で、各 run の直後・§3.2 の次の項目の前に行い、判断と時刻を解析の前に記録する。
- 対応: §3.4（「A completed run counts as aborted when its plan has another SHA-256 than the plan of section 2.4, or when the reference log shows a key press from outside the executor: in the delivery report of `kit/analysis/delivery.py`, run on the run directory alone (it reads the key rows of the logs, not the session rows), the reference's `excess_rows` over all presses is greater than zero, or its `rows_outside_trials` exceeds the five presses made outside the trials in each block (four marker presses and one kana press). No other reason and no explanation is admitted. The check is made right after the run (section 3.2), and its result and time are recorded in `experiment/data.md` before any analysis of the run. Rows of the observation without a sent press are a result of the observer under test (section 6.3) and never make a run count as aborted.」）・§3.2 の最後の文・§6.3・`data.md`（「Run checks」の表を新設し、検査を「run の直後・解析の前」の手順 1 に移した。検査の元として `results/e1_delivery.json` を挙げる文は消した）。
- メインの実装上の選択: 閉じた規則は `delivery.py` の今ある出力で書いた（判定の欄は足していない）。外からの入力で中止にした run は預けない（参照のログに人の打鍵が入りうる）。

### 4 [minor] 速さごとの偏りに、作り方の違う区間が 2 つ出る
- 対応（コード）: `l2.py` の `mixture_bias.by_stratum` から区間を外した（混合の計算に使う点だけを持つ）。登録の区間は `agreement_by_stratum` の 1 つ。混合の区間は変えていない。
- 対応（文）: §6.7（「… to show whether the aggregate's bias moves with the mix; the interval of a single speed's bias is the one reported with that speed's agreement.」）。

### nit a. 問 4 の場面ごと・速さごとの正解率に区間が無く、§1.2 と食い違う
- 研究者の採否: 区間を付けないものの一覧に足す側。
- 対応: §1.2 と §6.1 の区間を付けないものに「the per-scenario and per-speed accuracies of question 4」を足し、§6.8 の Reported を「and, descriptively and without an interval, the accuracy of the feature set alone per scenario and per speed」にした。

### nit b. §3.3 の「打ち切りの下に残る試行」は除外の前の数
- 対応: §3.3（「the trials that remain per scenario and speed (slow / mid / fast), before the exclusions of section 6.2, which can only reduce them, are:」）。

## B. round 3 で「部分的に解消」と判定した前の指摘

### N6（run の関門）→ 上の 3 で対応。

### M2（2/K と K の根拠）
- round 3 から変わらない（設計の選択として §7 に開示。あなたは round 3 で「これ以上は求めない」とした）。公開物の `kit\e2\README.md` の余裕の文を、事前登録と同じ言い方（2/K は設計の選択で、ブロックの依存やプライバシーの基準から導いていない）に揃えた。

### M3（一致の限界の幅を予想しない理由）
- 対応: §3.3（「The limits of agreement (the bias plus or minus 1.96 SD) are located to about 1.96 x SD x sqrt(3 x D / n) (Bland & Altman, 1986), about 0.39 x SD with 75 pairs and D = 1. No width is predicted for kappa and the ICC, because it depends on the values estimated; they are read through the intervals reported with them.」）。
