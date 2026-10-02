# carryover-R2 — round 3 からの引き継ぎ（R2: 打鍵記録を使う書字研究の利用者・公開の安全の立場）

作成: 2026-10-02（メイン）。あなた（R2 の立場）の round 3 の新しい指摘 9 件（major A・B、minor 1〜6、nit 1）と、round 3 であなたが「部分的に解消／未解消」と判定した前の指摘 9 件について、メインの裏取り・研究者の採否・対応・未解決を書く。
⚠️ **再掲を求めない**。各指摘が今の版で**解消したか**を 1 件ずつ判定してから（解消 / 部分的に解消 / 未解消・理由 1 行・今の版の位置）、**今回の直しが作った新しい穴**を探してほしい。round 3 で「解消」と判定した指摘は引き継がない（変わっていない節は round 3 の判定のまま）。
「採らなかった」部分は研究者の選択（またはメインの選択）で、理由を添えた。その理由が成り立たないと考えるなら、新しい指摘として根拠つきで書いてよい。

## 版の変化（round 3 の版 `abc5d7f9` → 今の版 `159a2ec8`）

- 節番号は変わっていない。round 3 の行番号は使えない（本文は 11,217 語から 12,143 語に増えた）。変わった節とコードの関数は context-A の「round 3 から変わった箇所」。
- 読んでよいファイルの一覧は round 3 と同じ（増減なし）。

## A. round 3 の新しい指摘

裏取りの判定は、メインがコード・計画・事前登録で確かめた結果。9 件すべて「真」（major A の「大きさ」はメインが計算していない）。

### A [major] 問 3 の主（`under_limit`）は、テキストを残して long の試行だけを抜くので、件数と時間の割合が設計の long の割合に依存する
- 裏取り: 真（`l2.py` の旧 docstring と `aggregate`: `n_conversions` は範囲に残った試行のセッションの和、`dwell_fraction` の分母はテキスト全体の時間のまま）。
- 研究者の採否: あなたの解消の条件 (a)（範囲の上で定義し直す）。採らなかった: (b) long の試行を含まないテキストに限る（slow ではほとんど残らない）・(c) 定義はそのまま限界に書く。
- 対応（文）: §4.6（「The four measures are computed for every text on both sides, over the trials of the text that are in the scope of the analysis (section 6.4): the conversions per trial (sessions or rows over the number of those trials), … and the fraction of time spent converting (total duration over the summed duration of those trials, each from its begin to its end). A text with no trial in the scope has no value (section 6.11).」）・§6.4 の問 3 の文・§6.7（「The number of a text's trials in the scope is reported per speed, and the texts with none are counted (section 6.11).」）・§6.11・§1.2 の問 3 の量の名前。
- 対応（コード）: `l2.py` の `MEASURES`（`n_conversions` を `conversions_per_trial` に改名）・`text_layout`（`out_of_scope`）・`aggregate`・`evaluate`（`texts.trials_in_scope_by_speed`＝テキストごとの範囲の試行の数の分布を速さごとに）。
- メインの実装上の選択: 定義は**すべての範囲で同じ**（範囲が変えるのは、どの試行を数えるかだけ）。`dwell_fraction` の分母は「範囲の中の試行の窓（oracle の begin〜end）の和」で、`all_trials` でも試行の間の待ちを含まない（テキストの端から端までの時間より短い）。範囲の中に試行が 1 つも無いテキストは 4 つの量とも null で、速さごとに数える。試行ごとの量（`per_trial` の `n_conversions` ほか）は名前も定義も変えない。

### B [major] 推奨の単位は「句 1 つを K 個から当てる」なのに、推奨は公開するログの粒度として書かれている
- 裏取り: 真。
- 研究者の採否: 範囲を書く（あなたの解消の条件の前半）。採らなかった: テキスト（8 試行）を単位に K 個の候補テキストへ距離を足し合わせる記述の解析を足すこと（新しい推定の対象とコード。今後の課題）。
- 対応: §6.8 の推奨の段落（「The rule judges the identification of one phrase among K candidates in one trial; combining several trials of one writer, or matching a log against known final texts, is not evaluated, and the recommendation makes no claim about the safety of a whole log (section 7).」）・§1.2 の問 4（下の minor 4）・§7 の新しい項「**The text-recoverability study judges one phrase at a time.**」・`kit\e2\README.md` の Scope of the claim。

### minor 1. 公開物の `kit\e2\README.md` が、セッション行と余裕の幅について事前登録と逆のことを言う
- 対応: README の What the attacker sees（「The attacker sees the key rows of a log: the category and the time of each key row. … The rows of type `ime_shadow` (the session rows) are in the log but are not given to the attack; the recommendation below concerns the key rows of a log published without its session rows.」）・Scope of the claim の `dwell_ms` の理由を事前登録 §6.8 の文に置き換え・余裕の 2 か所を「the upper end of the Wilson interval with the margin 2/K, which is a design choice, not derived from the block dependence or from a criterion of privacy」に。

### minor 2. 層 none の試行ごとの差で重み付けし直すと一致の方向に偏る
- 研究者の採否: あなたの解消の条件の前半（汚染の層だけを除いた版を足し、重み付けし直しにはそれを使う）。
- 対応: §6.7（「they are reported over every trial of the scope and over the trials of the scope that are in neither the carried-out nor the received-carry layer of section 6.4, for which reweighting to another mix of scenarios is meant; the trials that send a closing key in their reading stay in that view, because their disagreement is their own. As a diagnostic, they are also reported over the trials in none of the four layers.」）。コード: `match.py` の出力の `scope.uncontaminated_trials`・`l2.py` の `per_trial_uncontaminated`。層 none の版（`per_trial_layer_none`）は診断として残した。

### minor 3. 「読者は自分のデータに打ち切りの規則を当てられる」は、観測器のログだけでは成り立たない
- 対応: §6.4 の最後（「The effect of the cut-off on a researcher's aggregates follows from the rule stated in section 1.1. An observer's log does not show which sessions were cut off, because they have no row, so a reader who wants to apply the rule to their own data has to estimate from another source how often a conversion lasts 20 seconds or more; these are the longest conversions.」）。
- ⚠️ **入れ漏れ**: 直す一覧では「§7 にも 1 文」としたが、§7 の打ち切りの項には足していない（メインの漏れ）。

### minor 4. §1.2 の問 4 が §6.8 の範囲より広い
- 対応: §1.2 の問 4（「Given only the key rows of a published log, how accurately can an attacker identify which of K candidate phrases was typed in a trial, and how far can an attacker with a language model reconstruct the typed reading? Which of two granularities of the key rows that keep no time keeps the identification of a phrase near chance?」）。

### minor 5. 中止に数える「説明できない余分な行」の基準が事前に決まっていない
- 研究者の採否: 中止は参照のログが実行器の外からの打鍵を示すときだけ、閉じた規則で決め、「説明」の裁量を無くす。観測の余分な行は観測器の結果として解析する。
- 対応: §3.4（「… the reference's `excess_rows` over all presses is greater than zero, or its `rows_outside_trials` exceeds the five presses made outside the trials in each block (four marker presses and one kana press). No other reason and no explanation is admitted. The check is made right after the run (section 3.2), and its result and time are recorded in `experiment/data.md` before any analysis of the run.」）・`data.md` の「Run checks」の表（セル・試みの番号・検査の時刻・2 つの数・中止か）と手順 1。外からの入力で中止にした run は預けない。
- 採らなかった: 判断した人の名前を記録すること（規則が閉じていて、判断の余地が無いため）。

### minor 6. ブロックの合わせ直しは実ログで一度も試していない
- 研究者の採否: 凍結の前に、パイロットの観測の key 行に `align_plan` だけを流し（攻撃はしない・セッション行に触れない）、採点されたブロックの割合を §3.1 に書く。
- 対応: §3.1 に約束の文（「Before the freeze, the assignment of observed key presses to trials that both attacks of question 4 use (section 6.8) is run, without any attack, on the key rows of the pilot's observation logs, and the fraction of blocks it scores is reported here.」）。
- ⚠️ **未解決（既知）**: 中身（割合）はまだ無い。パイロットのログは測定機にある。round 4 の後に行う。この版で判定するのは、約束の文の書き方だけでよい。
- 別に、合わせ直しのコードに 1 つ欠陥が見つかり直した（試行の中にできた矢印 4 つちょうどの並びに錨が移ると、以後のブロックが全部採点されなかった）。§6.8 の第 2 段落と README の Usage を、足された・重複した打鍵も 1 ブロックだけを失う、と書き直した。

### nit 1. 依存の文が自己矛盾に読める
- 対応: §6.8（「With dependence within a block, the true uncertainty of an accuracy is larger than its Wilson interval shows, so a rule that reads the Wilson upper end is met more easily than it should be」）・§7 の同じ項・README。

## B. round 3 で「部分的に解消／未解消」と判定した前の指摘

### 新 3（問 3 の主）→ 上の A で対応。
### 新 4（推奨とセッション行・README）→ 上の minor 1 で対応。
### 新 6（重み付けし直し）→ 上の minor 2 で対応。

### nit 3（冗長さ）
- 対応（一部）: 設計効果の数は §3.3 の 1 か所に置き、§6.1 は参照に。打ち切りの規則は §1.1 の 1 か所に置き、§6.4 は参照に。
- 採らなかった: `all_trials` の依存の文は §6.4・§7・`notes.md`・`PRIMARY_NOTE`（`pipeline.py`）に残した（読む場所が違うため。メインの選択）。本文は 12,143 語（round 3 の版から +8%）。

### major-3（セッション行の公開の形）
- round 3 から変わらない。セッション行を公開する形（丸める・削る）を決めることは round 1 から採っていない。今の版は §6.8・§7・README で「セッション行の公開は評価していない」と書く。

### major-4
- 採らなかった（round 1 から）: (iii) L2 の偏りを「打ち切りの分」と「それ以外」に分けること・中央値か対数の平均の変換時間を足すこと。

### major-5 → 上の minor 2 で対応。

### minor-5（中間の粒度と、粒度ごとに計算できる書字の指標）
- 採らなかった（round 1 から・研究者の承知のうえ）。§7 の文を「the feature sets that keep times are reported as estimates only, and granularities between milliseconds and one-second bins are not evaluated」に直した。

### minor-7（パイロットの生ログを預ける基準）
- 対応: §3.1 に「which are written before the freeze」を足した。
- ⚠️ **未解決（既知）**: 基準そのものと「封印したセッション行は預けるときだけ開け、解析しない」は、まだ `pilot-macos.md` の Raw logs に無い。round 4 の後に測定機で書く。
