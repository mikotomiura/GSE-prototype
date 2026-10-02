# carryover-R3 — round 2 からの引き継ぎ（R3: 事前登録・統計・再現性の方法論の立場）

作成: 2026-10-02（メイン）。あなた（R3 の立場）の round 2 の新しい指摘 9 件（N1〜N9）と、round 2 であなたが「部分的に解消」と判定した round 1 の指摘 6 件について、メインの裏取り・研究者の採否・対応・未解決を書く。
⚠️ **再掲を求めない**。各指摘が今の版で**解消したか**を 1 件ずつ判定してから（解消 / 部分的に解消 / 未解消・理由 1 行・今の版の位置）、**今回の直しが作った新しい穴**を探してほしい。round 2 で「解消」と判定した指摘は引き継がない（変わっていない節は round 2 の判定のまま）。
「採らなかった」部分は研究者の選択（またはメインの選択）で、理由を添えた。その理由が成り立たないと考えるなら、新しい指摘として根拠つきで書いてよい。

## 版の変化（round 2 の版 `384712ee` → 今の版 `abc5d7f9`）

- 節番号は変わっていない。round 2 の行番号は使えない（本文は 9,326 語から 11,217 語に増えた）。変わった節とコードの関数は context-A の「round 2 から変わった箇所」。
- 読んでよいファイルの一覧は round 2 と同じ（増減なし）。

## A. round 2 の新しい指摘

裏取りの判定は、メインがコード・計画・事前登録で確かめた結果。9 件すべて「真」。

### N1 [major] 問 3 の主を `all_trials` にした理由が §7 と矛盾し、主の値が設計の打ち切り率で決まる
- 裏取り: 真（§6.4 と §7 の文。ライブ変換 ON の slow で、打ち切られるセッションに打鍵が入る試行は、下の N4 の新しい定義で 447 / 1,050）。
- 研究者の採否: 解消の条件 (a) を採る。問 3 の主を `under_limit` にし、`all_trials` は設計に依存する副として示す。
- 対応: §6.4 の Scopes の最後の段落（「Question 3 is answered under `under_limit` (primary) … and under `all_trials` (secondary). The values under `all_trials` depend on this design's fraction of long trials (section 3.1) …」）・§6.7 の冒頭・§1.2 の最後の段落・§7 の打ち切りの範囲の項（「Values under `all_trials`, those of question 3 in particular, hold for this design's fraction of long trials only.」）。コード: `pipeline.py` の `PRIMARY`（L2 の主を `under_limit` に）・`L2_SCOPES`（主から並べた）・`PRIMARY_NOTE`。

### N2 [major] n の根拠の推論が誤っており、主の範囲ではさらに目標に届かない
- 裏取り: 真（メインが `stats.wilson` で再計算: 71/75 → [0.871, 0.979]・68/75 → [0.820, 0.954]・34/34 の下端 0.8985・p = 0.95・n = 75 の正確な p では半幅 5.29、x = 71 では 5.4。真の recall 0.95 で 73/75 以上が出る確率 0.27）。
- 研究者の採否: n は変えない。言えることを設計に合わせて書き直す（あなたの解消の条件の 4 点）。
- 対応: §3.3 の Trials（「It was chosen before the key intervals of the measurement were set (below), and it was not revised when the prediction later showed how many trials the cut-off sets aside (section 3.1) … That a run fits in one night is a secondary justification」）・精度の表（最小の行を、S6・S13 以外で主の範囲の最小の層 31 に）・表の後の段落（「this does not guarantee that 0.95 and 0.90 are told apart」・31 試行で約 9 点・主の範囲の速さごとの n: ON 603 / 852 / 940・OFF 553 / 783 / 876、半幅 1.4〜1.8 点）・打ち切りの下に残る試行の表の後（S6・S13 以外で各セル 6 層〔すべて slow〕が 50 試行未満）。
- ⚠️ 主の範囲の数は、下の N4 の新しい `long` の定義で計算し直した値（round 2 であなたが引いた slow 627 / 577 は旧定義の値）。

### N3 [minor] 登録の文と、凍結するコードが計算するものが食い違う
- 裏取り: 真（(i) 旧 `l2.py` の `_agree` は偏りと一致の限界の点だけ・`mixture_bias` も点だけ／(ii)(iii) `pipeline.py` の範囲と比較の組）。
- 研究者の採否: (i) は `l2.py` に区間を足す。理由: 主の推定に変動の尺度が無いのは規程 J5 に反し、凍結の後に足すと作り方を結果の後に選ぶことになる。
- 対応: (i) §6.7（偏りと一致の限界のそれぞれに、ブロックで再標本した 95% 区間・混合の偏りは速さごとに独立にブロックを再標本した区間）・§6.1 の区間の段落。コード: `l2.py` の `_agree`・`_ba_stat`・`_ba_interval`（状態は偏りと一致の限界で別に持つ。偏りは 1 テキストでも定義されるため）・`mixture_bias`・`_stratified_replicates`（層化したブロックのブートストラップ。重み 1 を 1 つの速さに置いた混合はその速さの区間と一致）・`_ci_status`。(ii)(iii) §6.4 の Scopes の最後の段落（問 1 は 3 範囲・問 2 は `under_limit` と `all_trials`・`over_limit` は §6.6 Cut-off だけ）と Comparisons（問 3 は `gt_obs` だけ）。(iv) §1.2 と §6.1 で区間を付けないものを列挙（F1・数・問 4 の平均順位・§6.3・§6.9・§6.10 の記述の値）。

### N4 [minor] `long` は打ち切られたセッションが始まった試行で決まる
- 裏取り: 真。
- 研究者の採否: 解消の条件の 2 つ目（定義とコードと表を変える）を採る。`long` を「打ち切られたセッションに打鍵が 1 つでも入った試行」に、持ち越しを受けた層（`received carry`）を「前の試行で始まったセッションに打鍵が入った試行」に定義し直す（予測から決定的）。
- 対応: §4.5（各セッションが「打鍵が入った試行」を持ち、「the press that cuts a session off does not enter it」）・§6.4 の Scopes（`over_limit` の文: 打ち切りの後に開く新しいセッションの行は、その打鍵が落ちる試行の行）・§3.1・§3.3 の数を計算し直した（`long` は ON 755・OFF 713。S13 は全試行が `long`）・§1.2。コード: `spec_predict.py` の `_Machine`・`summarise_trials`（出力の形式を `spec_predict/2` に上げた）・`match.py` の `parse_prediction`（`received_carry` を必須にし、古い形式を拒む）。
- 表の値を再現する手順: §3.1 に `python3 kit/analysis/spec_predict.py --from-plan --plan <plan> --out <file>` を書いた（計画の時刻から送出の記録を組む `oracle_from_plan`: 印は `marker_gap_ms` 間隔・試行は `gap_before_ms` の後・打鍵は `at_ms`・ブロックの間 2 秒）。メインは、前の版の値（旧定義）をこの手順で**すべて再現**したことを確かめてから、新しい定義の値を書いた。

### N5 [minor] §6.8 の依存の理由づけが成り立たず、表は「最大値」に当てる規則を表していない
- 裏取り: 真。
- 研究者の採否: 解消の条件 (a) を採る（規則は変えない）。
- 対応: §6.8 の最後の段落（「Dependence within a block would widen the interval and make the rule easier to meet; it is expected to be small, because the key rows of a trial follow from its own phrase and procedure, and the phrase, intervals and decoys of each trial are drawn independently, but it is not ruled out, and the block-resampled interval is reported next to the Wilson interval for this reason」）・表の注（「for a set whose reported accuracy is the maximum over coarser sets as well, the probability is at most this」）・§7 の新しい項「Intervals that treat trials as independent」。コード: `closed_set.py` の `evaluate`（`--bootstrap`、既定 2,000・ブロックで再標本した正解率の区間・最大は再標本ごとに取り直す）。§6.8 のコマンドに `--bootstrap 2000` を足した。
- 採らなかった: (b) 設計効果を数で置いた余裕。

### N6 [minor] 登録の外に run 単位の関門があり、その後の分岐が決まっていない
- 裏取り: 真。
- 対応: §3.4（「A completed run counts as aborted when its plan has another SHA-256 than the plan of section 2.4, or when one of its logs holds a row without a press the executor sent that cannot be explained (the check of `experiment/data.md`, made before the logs are deposited).」）・`data.md` の手順 4（同じ）・§8（「The results of the analysis run from the freezing tag are always reported as the registered results; if a defect of the frozen code is found after the analysis, a corrected analysis is reported next to them as a deviation, not in their place.」）。

### N7 [minor] 主の範囲での速さ別の pooled は、速さごとに組成が違う
- 裏取り: 真。
- 対応: §6.1 第 1 段落の後半（「In the primary scope the trials that remain differ between speeds in composition … so a difference between speeds is not an effect of speed alone. The number of letter keys and the think time of the trials in each scope are reported per stratum, from the plan.」）・§7 の打ち切りの範囲の項（読みの長さを足した）。コード: `pipeline.py` の `_composition`（層 × 範囲ごとの英字のキー数と思考時間の n・中央値・最小・最大を計画から）。
- 採らなかった: シナリオに等しい重みを付けた平均を副として足すこと。

### N8 [nit] §3.3 の Wilson の表の作り方
- 対応: §3.3 の Precision of proportions（「half-width … of the 95% Wilson interval for round(n x p) successes in n trials」）。

### N9 [nit] 「4 つの層」は分割ではない
- 対応: §4.5（「A trial can carry several of these marks.」）・§6.4 の Layers（「A trial with several marks is counted in each of its layers.」）。層は carried out・received carry・closing key in reading・どれでもない、の 4 つ（`started none` を `received carry` に置き換えた）。

## B. round 2 で「部分的に解消」と判定した round 1 の指摘

### M2（部分的に解消と判定）E2 の判定規則
- 依存の扱い → 上の N5。
- 余裕 2/K の根拠: §7 の新しい項に「The margin of the rule (2/K) and the values of K are design choices, not derived from a criterion of privacy.」と書いた。プライバシーの基準から導いた余裕には替えていない（round 1 からの研究者の選択）。

### M3（部分的に解消と判定）n の根拠・一致の限界・kappa・ICC の予想幅
- n の根拠 → 上の N2。
- 一致の限界・kappa・ICC: §3.3 の連続量の精度の最後を「No width is predicted for the limits of agreement, kappa and the ICC, because it depends on the values estimated; they are read through the intervals reported with them.」に書き直した。予想の幅は書いていない。

### m1（部分的に解消と判定）凍結のハッシュ
- 対応: §9（「registered on OSF Registries with the two marks, the 40-digit identifier of the freezing commit and the SHA-256 of the list of files exported from it … The export root is the top directory of the published materials (the directory that holds `experiment/` and `kit/`); the list holds one line per exported file … so that the SHA-256 of the list can be computed again from the published materials」）。
- 採らなかった: 一覧を作るコマンドを名指すこと（書き出しの道具は公開物の外にある。一覧の書式と根を書いた）。

### m4（部分的に解消と判定）完走した後に欠陥が見つかった run の扱い → 上の N6。

### m5（部分的に解消と判定）n = 75 を決めた順序 → 上の N2（§3.3 の Trials）。

### n1（部分的に解消と判定）ICC の model の名前
- 対応: §6.7（「the intraclass correlation for absolute agreement of a single measurement, with the two methods as the only raters of interest (a two-way mixed model): ICC(A,1) in the notation of McGraw and Wong (1996), which has the value of ICC(2,1) of Shrout and Fleiss (1979).」）・`stats.py` の `icc` の docstring（random でも mixed でも値は同じ・この比較は 2 つの方法だけが関心の評定者）・`notes.md` の統計の表。
