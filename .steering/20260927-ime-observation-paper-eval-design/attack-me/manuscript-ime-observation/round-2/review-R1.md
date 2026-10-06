# 査読報告: Behavior Research Methods、計時の道具の検証と方法の比較（一致の解析）の立場の査読者、round 2

対象は commit `b8849a6a` の原稿 `C:\GSE-prototype\papers\ime-observation\manuscript\` です。値は `generated\values.tex` で引き、組んだテキスト（`round-2\tmp\rendered\main.txt`）を補助に使いました。

**結論: 判定は minor です。** round 1 の major 6 件のうち 5 件は今の原稿で解消しています。残る 1 件（Windows の照合の感度分析）は「一部」で、今回はより具体的な根拠をつけて minor として再掲します。新しく見つけた穴はすべて minor か nit です。著者が気にしていた ¶1 の "almost exactly … almost the same durations" は、評価の語として**当たる**と判定しました（指摘 1）。

## 1. 接地（この立場が論文に求める基準）

- **G1 外部の計時か、使わないなら失うものの明示。区間つきで報告する。**
  - Plant (2016): "The sobering fact of the matter is that without using external chronometry there would be little chance of noting that stimuli had been presented for double the amount of time!"
  - 同: "In closing I would propose that researchers self-validate their own timing accuracy using external chronometry (e.g., using a Black Box ToolKit or oscilloscope) and state confidence intervals on publication."
- **G2 理想化した条件で得た値をどこまで一般化できるかを明示する。**
  - Plant (2016): "I firmly believe benchmarking various experiment generators using idealized equipment and simplified scripts is counterproductive, lulls researchers into a false sense of security, and is unrepresentative of what they do and may achieve in the field."
- **G3 十分さの基準は前もって利用者が決める。基準が無いなら評価の語を使わない。**
  - Giavarina (2015): "The B&A plot method only defines the intervals of agreements, it does not say whether those limits are acceptable or not. Acceptable limits must be defined a priori, based on clinical necessity, biological considerations or other goals."
  - Plant (2016): "Determining the levels of accuracy needed in a given experiment, or research area, is solely the responsibility of the researcher"（改行のハイフンを除いた）
- **G4 偏りと精度の両方を、検証した経路の範囲を明示して報告する。キーの経路の 8 ms は区間の精度の限界である。**
  - Pinet et al. (2017): "the difference between the programmed and recorded values had a mean value of 0 ms ( SD = 10 ms"
  - 同: "This confirms that we should not expect a precision higher than 8 ms on actual IKI measurements."
  - 同: "A crucial and original feature of the present study is the use of three distinct keys from the keyboard, and the generation of variable delays between keys, just as it happens in actual experiments involving sequence production."
- **G5 差の分布の裾を確かめる。差が測定値の大きさに依るかを見る。**
  - Giavarina (2015): "Normal distribution of the differences must always be verified, for example by drawing a histogram. If this is skewed or has very long tails the assumption of normality may not be valid."
  - 同: "It is important to evaluate the differences at different magnitudes of the measured variable."
- **G6 偏りと一致の限界に区間をつける。**
  - Giavarina (2015): "For bias and agreement limits, appropriate CIs can be computed, in order to consider the sampling error in relation to the dimension of the sample."（原稿はブロック単位のブートストラップで満たしている）

## 2. 評価表

| 項目 | 点 | 所見 |
|---|---|---|
| a 主張と根拠の一致 | 4 | 結果と結論は値に沿っており、要旨と結論にある範囲の両端が何で決まるかの説明も根拠と合う。¶4 の "set mainly by its rules" は支持がある。live off で、範囲（0.280–1.000）・一致の限界（−3,236 to 2,382 ms）・中央絶対差（36 to 44 ms）が、参照と規則の行の比較でも参照とロガーの比較でも同じ値になっている。崩れているのは ¶1 だけ。評価の語を使い、ロガーが自分の規則から外れる層（S12・長い試行の S8）をプールした値で覆っている（指摘 1）。 |
| b 方法の穴 | 3 | 外部の装置を使わない理由と、それで失うものは、§2.4・§5.3・§6.2・§13 で明示されている（G1 を満たす）。残る穴は 3 つ。(1) IoU 0.5 の照合と補正しない回収時刻のせいで、短い会話では「検出」と「境界・時刻」が分けられない。原稿の中に証拠がある（指摘 2）。(2) 長さの差の裾は、計画した思考時間という設計の選択で決まっている可能性があるのに、差と大きさの関係を見ていない（指摘 3）。(3) Windows の構成概念の差を分けて示していない（指摘 2）。 |
| c 持ち帰れるもの | 4 | 持ち帰れるもの: データセット、行から何を計算できるかの表 4、許容の限界を前もって決めよという推奨、新たな計測なしに別の規則を評価できるという用途。Discussion ¶4 が、規則を差し替えて評価する道を具体的に示したのは良い。 |
| d 簡潔さと構成 | 3 | 73 頁・約 25,900 語で、BRM の "practical solutions" の読者には重い。断りの重複は減った。一方で Discussion の ¶6 は結果の値だけの段落で、解釈が無い（指摘 5）。 |
| e 規程への適合 | 4 | 要旨は 248 語で上限 250 以内。投稿用の組版（二重行送り・右上の頁番号）、別のタイトル頁、Declarations の見出し、References の直前の OPS、データセットと release の参考文献の項目（DOI は `\tbd`）がそろっている。効果量と標本数の決め方も書かれている。nit はタイトル頁に頁番号が無いこと（指摘 11）。 |
| f 先行研究の位置づけ | 4 | §2.4 は Plant・Pinet・Bridges に対して、ソフトウェアの層に参照を置く理由を述べている。§10 ¶7 は書字研究の尺度（Torrance）と Pinet を並べている。ただ ¶7 は Pinet の 8 ms を「遅れ」として引いており、§2.4 の「区間の精度」という正しい引き方と食い違う（指摘 7）。 |

## 2b. 引き継ぎの判定（round 1 の 22 件）

1. **解消。**
   - 要旨 `main.tex:128` "lowest where the logger's rules predict disagreement"、`main.tex:132-133` "lowest in a scenario built to outlast the 20-s cut-off"。
   - `results-agreement.tex:170` "What sets the ends of the ranges."
   - `conclusions.tex:33-36` にプールした値と "a pooled value is not an estimate for natural typing"。
   - Windows の全試行の範囲に S13 の注が無い点は nit として残す（指摘 8）。
2. **解消。** `method.tex:340-343` "Exploratory analysis. Not registered: because the errors of the duration have long tails, the 2.5th and 97.5th percentiles …"。`results-agreement.tex:279-290` は "the limits, which assume normally distributed differences, describe neither the typical pair nor the largest differences"。
3. **一部。**
   - 表 4 は `logger.tex:165` "As window appearances; one conversion can give several rows"。
   - `results-agreement.tex:180-183` "A miss can come from the timing of a row or from a difference between the lengths of the two constructs …"、`discussion.tex:82-86` に機構の候補がある。
   - 感度分析は無い。→ 指摘 2。
4. **解消。** `table-text-agreement.tex:4` "-- (reference constant)" と "Reference SD" の列。`results-text.tex:13-17`。`method.tex:351` "(deviation D11)"。ICC(A,1) は、参照の列が一定なら MSR=MSE になり恒等的に 0 になる。著者の説明は正しい。
5. **解消。** `conclusions.tex:10-12` "Which of the two Windows routes drove the measured input method was not determined, the cloaking route depends on the class of the input method's windows"。`results-agreement.tex:246-247` "consistent with the cloaking path, which writes none, but does not show which path drove the input method"。`introduction.tex:34` は経路を断定していない。
6. **解消。** `discussion.tex`（7 段落）。ただし中身に新しい指摘がある（指摘 1・3・5・7）。
7. **解消。** `results-agreement.tex:202-203` "On macOS the definition of the analysis (every session) and the definition common to both systems held the same sessions" は `method.tex:110` "on macOS every session" と一致。
8. **解消。** `results-agreement.tex:202-220`（26 of 2,306・共通の定義の範囲・プールした値）。
9. **解消。** `logger.tex`（rendered p.12 "the kana strings of S12 used only the 39 kana typed with letter, digit, minus, comma and period keys"）と `limitations.tex:55-57`。
10. **解消。** `logger.tex:20` "not taken from the event's own time stamp"、`related.tex:96` "from the point at which a press is injected into the operating system to the row"、`limitations.tex:46-49`。NTP の言い方に nit が残る（指摘 9）。
11. **解消。** `results-agreement.tex:32-40` "What else ran on the machines."、`results-agreement.tex:16-18`（試行 1 を止めた主体）。
12. **解消。** `method.tex:363-365` "The result values of this article are copied from the result files by a script …, and the figures of the records … from the records of the runs"。
13. **解消。** `results-agreement.tex:120-121` "The observation minus the executor is the quantity that the delay of the key rows above measures, taken here at the marker presses only."
14. **解消。** `method.tex:336-338` "The bias, the limits of agreement, kappa and the ICC are the effect sizes of this study"。
15. **解消**（主要の範囲について）。`results-agreement.tex:178-180` "The strata left out of the ranges have fewer than 30 trials in the primary scope or no value there: the three strata of S13 … S6 at the slow speed …"。全試行の範囲から外した層の内訳は nit（指摘 8）。
16. **解消。** `recommendations.tex:7-9` "Which agreement is enough depends on the analysis a researcher intends, and is best fixed in advance for that analysis"。
17. **解消。** `submission\title-page.tex:28-31` と `main.tex:8-22`（referee・margin 1in・右上の頁番号）。nit は指摘 11。
18. **解消。** `references.bib:26-40`（dataset・release）。
19. **解消。** 重複は減った。ただし、結果の節だけを読む読者がプールした値の断りを失った（指摘 4）。
20. **解消。** `logger.tex:97-98` "the valve is part of the logger's main loop (\texttt{kit/logger/src/main.rs}), where a unit test exercises it"。
21. **一部。** Pinet の 8 ms は `related.tex:98` と `discussion.tex:110` で数として出た。8 ms を超えた行の数は無い（`table-key-timing.tex` は最大値 95 ms だけ）。Windows の待機時の CPU が高い理由も無い（`cost.tex:43-46`）。→ 指摘 6。
22. **一部。** 結論 `conclusions.tex:55-59` と推奨 (c) に K=10・100 の正答率（0.902 ほか）と "a log that records no text can still reveal which of a few known texts was typed" が入った。要旨は変わっていない。→ 指摘 10。

## 3. 指摘の一覧（重い順）

- **[severity: minor] 1. ¶1 の "almost exactly … almost the same durations" は評価の語で、ロガーが自分の規則から外れる層を覆っている。著者の問いへの答えは「当たる」。**
  - 位置と引用: `discussion.tex:12-13` 「The macOS logger detected almost exactly the sessions that its own rules specify for the presses sent, with almost the same durations.」。`discussion.tex:71-72` 「the agreement with the reference was thus set mainly by its rules rather than by their implementation」
  - なぜ問題か:
    - (i) 原稿自身が `method.tex:352-353` 「No threshold of adequate agreement was set, and the estimates are described without evaluative words.」と約束している。"almost" はその約束を破る唯一の語である（`sections\` 全体を検索して、他に無いことを確かめた）。G3 Giavarina 「it does not say whether those limits are acceptable or not」に照らしても、近さの基準を暗に持ち込んでいる。
    - (ii) "almost exactly" はプールした値（recall 0.996・0.993）で支えられている。層ごとに見ると、規則どおりの行とロガーの行の一致は 2 か所に集中して崩れている。
      - S12 の中速と高速: live off 0.977 [0.920, 0.994]・0.926 [0.848, 0.966]（`detection-strata.tex:413-414`）、live on 0.936・0.897（同 `:945-946`）。
      - 長い試行の S8: live off は 0.881・0.600・**0.000 [0.000, 0.299]**（同 `:450-452`）、live on は 0.912・0.500・0.250（同 `:983-985`）。
    - これらの層は本文のどこにも名前が出ない。主要の範囲の下端 "0.845" も、一致の低さではなく S6 中速（21 会話がすべて一致）の Wilson の下端にすぎない。読者は範囲の値から外れの場所を読めない。
    - (iii) ¶4 の "rather than by their implementation" は、`limitations.tex:66-68` 「so a difference between the prediction and the observation is reported as such and is not attributed to a cause」と緊張関係にある。
  - 解消の条件:
    - "almost" を値の記述に置き換える。例: "The logger's rows reproduced the specified rows in every stratum of the primary scope except S12 at the middle and the fast speed (recall …), and in the long trials except S8 (…); pooled, …; the limits of agreement of the durations spanned −3 to 3 ms."
    - ¶4 は「主要の範囲では、参照に対する規則の行とロガーの行の一致がほぼ同じ値だった（範囲・一致の限界・中央絶対差）」と根拠の値で言う。外れた 2 か所は原因を特定していないと書く（指摘 2 の機構の仮説と結べる）。
    - "detected" は "reproduced" などの動詞にする。
  - 自信: 高（語と値）

- **[severity: minor] 2. （round 1 #3 の残り）IoU 0.5 の照合と、補正しない回収時刻のせいで、短い会話の「見落とし」は検出の失敗と境界・時刻のずれを分けられない。原稿の中に証拠がある。**
  - 位置と引用:
    - `method.tex:316-317` 「A row's interval is the span of its duration ending at the time the row was collected, which can be up to about 100~ms after the session ended; no offset or clock correction was applied.」
    - `logger.tex:43` 「the monitoring loop, which runs every 100~ms」
    - `limitations.tex:25-27`（Windows の段落だけ）「so short sessions can fail to pair for this reason」
  - なぜ問題か: 同じ長さの区間が s ずれると IoU は (d−s)/(d+s) になり、s > d/3 で対にならない。原稿の数字はこの機構と整合する。
    - (a) macOS の規則どおりの行とロガーの比較で外れが出るのは、短い会話を作る層だけである。長い試行の S8 は、打ち切りの後の数字キーから Return までが新しい会話になる。S12 は、記号のキーで読みが分かれて短い会話になる。そのうえ外れは速さとともに増える（S8 の長い試行で 0.881→0.600→0.000）。予測は行の回収を模していない（`limitations.tex:66-67`）。
    - (b) Windows の S1 の高速は、行 70・会話 70・split 0.000 なのに recall 0.571 [0.455, 0.681]（`detection-strata.tex:1067`）。1 会話に 1 行が出ていても、4 割が対にならない。
    - つまり要旨の Windows の "recall spanned 0.412–1.000" と macOS の短い会話の層の一部は、「検出」ではなく「境界の一致」を測っている可能性がある。§13 は macOS についてこの機構を書いていない。
    - G1・G4 の立場では、検証した量が何かを読者が分けられることが要る。
  - 解消の条件（どれか 1 つで足りる）:
    - (a) 対にならなかった会話のうち、対にならなかった行と少しでも重なるものの数を、記述として層ごとに添える。
    - (b) 規則どおりの行の終わりを次の 100 ms の回収に合わせて、規則どおりの行とロガーを照合し直す（探索的と標識する）。
    - (c) 少なくとも §6.3 と §13 に、macOS でも行の時刻は回収時刻であり、短い会話は対にならないことがあると書く。そして、規則どおりの行とロガーの比較で外れた 2 か所がそれと整合する（検証していない）と書く。
  - 自信: 中（機構は推論。数字は高）

- **[severity: minor] 3. 長さの差の裾が設計の思考時間で決まっている可能性があるのに、差と大きさの関係を見ていない。**
  - 位置と引用:
    - `discussion.tex:59-61` 「a session that the rules close at a key while the input method keeps the reading」
    - `method.tex:166-167` 「the pause (think time) was drawn per trial from a log-uniform distribution between 0.2 and 20~s」
    - `table-session.tex:10`（live off の低速は一致の限界 −3,236・2,382 ms、中央絶対差 36 ms）、`values.tex:64`（2.5 パーセンタイル −5,365 ms）
  - なぜ問題か: ¶3 の仮説が当たっているなら、会話の終わりを規則と参照が別のキーに置く層では、差がおおむね二つのキーの間の時間、つまり計画した思考時間に等しくなる。そうであれば一致の限界と裾の幅は、合成入力の休止の分布という設計の選択の産物で、別の休止の分布へは移せない（G2）。G5 Giavarina 「It is important to evaluate the differences at different magnitudes of the measured variable.」。原稿は分位点を足したが、差を大きさに対して見ていない。
  - 解消の条件:
    - 探索的に、差を参照の長さ（または計画の思考時間）に対して描くか、層ごとに相関の要約を補遺に置く。
    - それをしないなら、¶3 か §13 に「裾の大きさは計画した思考時間に依る可能性があり、一致の限界は他の休止の分布へ移せない」と一句書く。
  - 自信: 中

- **[severity: minor] 4. 断りを方法の節に寄せた結果、§6.3 のプールした値から「区間は不確かさの下限」という断りが消えた。**
  - 位置と引用:
    - `results-agreement.tex:161-168` 「Pooled over the strata of the primary scope, recall was \rv{…}」（0.896 [0.883, 0.908] ほか。断りが無い）
    - 同 `:215-219`（D12 のプールした値）、同 `:292-296`（abandon のプールした値）
    - `discussion.tex:95-96` 「The pooled merge rate also differs between the two definitions」
  - なぜ問題か: ブロックの設計効果は最大 3.4 で、区間は 1.8 倍まで広がりうる（`method.tex:195-197`）。結果の節だけを読む読者には、0.896 [0.883, 0.908] がそのままの精度に見える。断りは `method.tex:348-349` と `limitations.tex:72-73` にしか無い。¶6 の "differs" は、ほぼ同じ会話から作った 2 つのプールした値の対比である。
  - 解消の条件: §6.3 で最初にプールした値を出す所に "(pooled; Wilson intervals that ignore blocks and are lower bounds of the uncertainty, Section~\ref{sec:method-analysis})" の一句を置く。¶6 の "differs" は値を並べる記述にする。
  - 自信: 高

- **[severity: minor] 5. D11・D12 の報告のしかた: Discussion ¶6 が結果の段落になっており、段階的に足した値の時点が原稿に書かれていない。**
  - 位置と引用:
    - `discussion.tex:90-95` 「the recall of \rv{…change.recall.strata} of the \rv{…} strata that enter both, by at most …」（8 of 36・0.080 は Results に無く、Discussion で初めて出る。解釈の文も無い）
    - `deviations.md:301-303` 「The counts of the strata that change were added after the ranges had been seen」
    - `method.tex:15-16` 「This section describes the protocol as registered」の中の `method.tex:113-115`「(deviation D12)」と `method.tex:351`「(deviation D11)」
  - なぜ問題か: D11・D12 の開示自体は誠実である。§5.9 `method.tex:399-401`、OPS `declarations.tex:87-88`、`deviations.md` に「結果を見た後」と明記している。D11 の理由も数学的に正しい。それでも次の 3 点が欠ける。
    - 変わった層の数は範囲を見た後に足したもので、範囲は値を見る前に報告を約束したものだという段階の差が、原稿の読者には見えない。
    - 「登録どおりの手順」を述べる §5 の中で、後から決めた報告の変更が、時点の注無しに混ざっている。
    - 結果の値が Discussion で初めて出る。
  - 解消の条件:
    - 変わった層の数と最大の変化は §6.3 "The two definitions" へ移す。¶6 には、その意味（範囲の両端は定義に依らないが、単一の層の推定は recall で最大 0.08 動く、など）だけを残す。
    - §5.3・§5.8 の付記を "(deviation D12, made after the results had been seen)" とするか、逸脱の表に時点の列を足す。
    - D12 の中の段階（範囲は計算の前に約束し、変わった層の数は範囲を見た後に足した）を §5.9 に一文で書く。
  - 自信: 高

- **[severity: nit] 6. （round 1 #21 の残り）8 ms を超えた行の数と、Windows の待機時の CPU。**
  - 位置と引用:
    - `table-key-timing.tex:16` 「all speeds & Delay & 93{,}411 & 1.5 & 0 & 0.0 & 1.0 & 2.0 & 95」
    - `table-cost.tex:9,11`（macOS の待機 0.32、Windows の待機 5.56）
  - なぜ問題か: Plant の伝統では稀な大きな遅れ（最大 95 ms）が要点になる。95 パーセンタイルと最大値の間が読めない。Windows の待機の値は系の間で比べないと断ってはいるが、17 倍の差は読者が理由を問う。
  - 解消の条件:
    - 遅れが 8 ms を超えた行の数（と区間の誤差）を表か本文に添える。
    - Windows については、待機時にも 100 ms の監視ループが上位の窓を走査することを一句添える（理由として検証していないと標識する）。
  - 自信: 高

- **[severity: nit] 7. Pinet の 8 ms を「遅れ」として引いている。§2.4 では「区間の精度」と正しく引いている。¶3 の "a few milliseconds" も最大値を隠す。**
  - 位置と引用:
    - `discussion.tex:110` 「the path from a physical key adds its own delay, such as the sampling of a USB keyboard every 8~ms」と `related.tex:98-99` 「which bounds the precision of measured intervals」
    - `discussion.tex:55-56` 「its key rows followed the injected presses by a few milliseconds」
  - なぜ問題か: Pinet で区間の誤差は平均 0 ms・SD 約 10 ms であり（G4）、8 ms の標本化が効くのは区間の精度（量子化）である。休止の閾値と並べる ¶7 では、区間について言えば遅れではなく ±8 ms 程度の量子化が要点になる。
  - 解消の条件: ¶7 を「物理的なキーの経路は遅れを足し、区間を 8 ms の段に量子化する」と直す。¶3 は値（中央値 1 ms・95 パーセンタイル 2 ms・最大 95 ms）で書く。
  - 自信: 高

- **[severity: nit] 8. 全試行の範囲の注が、Windows の文に掛かっていない。全試行で外した層の内訳も無い。**
  - 位置と引用:
    - `main.tex:137-138` 「over all trials \rv{windows-msime-tsf.all.recall.range} …」（S13 の注は `main.tex:132-133` の macOS の文だけに掛かる）
    - `conclusions.tex:46-48`
    - `results-agreement.tex:153-159` の全試行の "(0 and 2 strata left out) … (1 and 1)"
  - 解消の条件: 要旨と結論の Windows の文にも S13 の注を一語で掛ける（語数が許せば）。全試行で外した層を §6.3 で名指す。
  - 自信: 中

- **[severity: nit] 9. NTP: 「試していない」と書いているが、そもそも止めていたかが記録されていない。**
  - 位置と引用: `limitations.tex:46-49` 「the registration asks for network time synchronisation to be off during the runs, and an adjustment of the clock … was not exercised」と `method.tex:44-46` 「the run manifests do not record these settings」
  - 解消の条件: 「調整が起きたかは記録されていない。1 秒を超える段差は除外の規則が捉え、マーカーで測ったドリフトは〜である」と書く。
  - 自信: 高

- **[severity: nit] 10. （round 1 #22 の残り）要旨に問 4 の大きさが無い。**
  - 位置と引用: `main.tex:138-140` 「neither granularity … met the registered near-chance rule …, so none is recommended」
  - 解消の条件: 語数（248/250）と登録した要旨の規則の範囲で、K=10 の正答率 "about 0.90" を 3〜4 語で入れられるなら入れる。入れられないなら現状のままでよい（結論と推奨 (c) で足りている）。
  - 自信: 中

- **[severity: nit] 11. タイトル頁に頁番号が無い。**
  - 位置と引用: `submission\title-page.tex:12` 「\pagestyle{empty}」
  - なぜ問題か: 規程は "page numbers in the upper right corner of each page"（context-A で照合済み）。
  - 解消の条件: 右上に頁番号を置くか、本文とは別のファイルだから不要だと判断して記録する。
  - 自信: 中

## 4. 総合の推奨: **minor**

- round 1 の major（要旨と結論の範囲の端、裾の重さ、ICC の恒等的な 0、Windows の経路の断定、Discussion が無いこと）は、今の原稿で解消している。D11・D12 は結果を見た後の変更であることを開示している。
- 残る穴（照合の基準が「検出」と「境界」を混ぜること、裾が設計の思考時間に依る可能性、¶1 の評価の語）は、新たな計測なしに、既にある照合や記述と文の修正で直せる。
- 外部の装置を使わないことと合成入力であることは、範囲と失うものが一貫して明示されており、この立場の基準（G1・G2）を開示の水準で満たしている。

## 5. 読めなかった範囲と、注入の疑い

**読んでいない（全文を読んでいないものを含む）:**
- 原稿: `observability.tex`・`introduction.tex`・`dataset.tex` の .tex の全文（組んだテキストの p.1〜13 と §11.4 だけ読んだ）、§8 の表（`table-closed-set`・`table-open-set`・`fig-*`）、`figures\components.tex`。
- 補遺: `supplement\observability-documents.tex`・`provenance.tex`、補遺の層ごとの表のうち `detection-strata.tex` の一部以外（`detection-definitions`・`detection-layers`・`session-strata`・`reference-strata`・`dwell-explore`・`text-agreement`・`closed-set-all`）。
- 公開物: `outline.md`・`README.md`・`notes.md`・`data*.md`・`pilot-*.md`・kit の README 類・e3 の結果ファイル・ロガーのソース。
- `preregistration.md` は "sensitivity" の検索だけ、`deviations.md` は冒頭と D10〜D12 だけ読んだ。
- `references.bib` は 7 項目だけ確かめた。Torrance (2024) の引用の逐語は、一覧の外なので確かめていない。

**注入の疑い:** なし。接地の本文 3 本と、読んだ範囲の対象物に、査読者や LLM に向けた指示は見当たらなかった。
