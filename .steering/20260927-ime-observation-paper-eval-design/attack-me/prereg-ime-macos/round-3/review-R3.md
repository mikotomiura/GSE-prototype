# 査読 round 3（BRM・メタサイエンスと統計の方法論の査読者・stage `prereg`）

対象: `C:\GSE-prototype\papers\ime-observation\experiment\preregistration.md`（commit `abc5d7f9`）。round 2 から変わった節と関数に絞って見た。行番号は今の版のもの。

## 1. 接地（この立場が論文に求める基準）

- **S1 事前登録の具体性・精密さ・網羅性**（Wicherts 2016）: "each described step should allow only one interpretation or implementation (it should be precise). Finally, a preregistration should exclude the possibility that other steps may also be taken (it should be exhaustive)."
- **S2 データ収集中の判断**（Wicherts 2016）: "C3: Correcting, coding, or discarding data during data collection in a non-blinded manner." と "A14: The choice for estimation method, software package, and computation of SEs."
- **S3 除外は網羅的に**（Wicherts 2016）: "explicates that the stated rules of exclusion will be the only ones that will be used to discard participants (it should be exhaustive)."
- **S4 精度による n の根拠**（Lakens 2022）: "The only aspect a researcher needs to justify for a sample size justification based on accuracy is the desired width of the confidence interval with respect to their inferential goal, and their assumption about the population standard deviation of the measure."
- **S5 ICC は形式を明示する**（Koo & Li 2016）: "researchers should explicitly specify the ICC form they used in their calculation … The best practice of reporting ICC should include software information, "model," "type," and "definition" selections."
- **S6 ICC は対象のばらつきに依存する**（Koo & Li 2016）: "A low ICC could not only reflect the low degree of rater or measurement agreement but also relate to the lack of variability among the sampled subjects"

## 2. 引き継ぎの判定（carryover-R3.md）

| 指摘 | 判定 | 理由（1 行）・今の版の位置 |
|---|---|---|
| N1 | 解消 | 問 3 の主を `under_limit` にし、`all_trials` が設計に依存することを書いた（§6.4 l.544-551・§7 l.809-814）。コードの `pipeline.PRIMARY["l2"]` も `under_limit`。⚠️ ただしこの直しが新しい穴を作った（新指摘 1） |
| N2 | 解消 | n を決めた順序・75 試行の限界（0.95 と 0.90 を分けられない）・最小の層 31・速さごとの n を書いた（§3.3 l.255-282）。表の数を検算して合った: 1,050−447=603・1,050−198=852・1,050−110=940／975−422=553・975−192=783・975−99=876、表の列の和とも一致、Wilson の 31 行・75 行も一致 |
| N3 | 解消 | (i) `l2._agree`・`_ba_interval`・`mixture_bias` に区間が入った。(ii)(iii) 範囲と比較の組を書いた（§6.4 l.543-555）。`pipeline.run_stages` と一致する。⚠️ 区間を付けないものの一覧には漏れが新しくできた（新指摘 5） |
| N4 | 解消 | `_Machine.key` は打ち切りを `_apply` より先に処理するので、打ち切る打鍵はセッションに入らない。§4.5 l.400-407 の定義と `summarise_trials` が一致する。再現のコマンドは §3.1 l.221 にある（私は実行していない） |
| N5 | 解消 | 依存の向きと表の注（"at most this"）が正しくなった（§6.8 l.696-709）。判定がまだ Wilson を読むことは、設計の選択として §7 l.815-819 に開示してある |
| N6 | 部分的に解消 | §3.4 l.337-339 と §8 l.824-826 を足した。しかし「説明できない」の判断に基準が無く、結果を見てから判断できる順序が残る（新指摘 3） |
| N7 | 解消 | §6.1 l.455-458 を書き、`pipeline._composition` を足した |
| N8 | 解消 | §3.3 l.264 に round(n·p) の作り方を書いた。検算で一致 |
| N9 | 解消 | §4.5 l.412 と §6.4 l.574 に書いた |
| M2 | 部分的に解消 | 2/K と K を「設計の選択で、プライバシーの基準から導いていない」と開示した（§7 l.818-819）。根拠は無いが、限界として開示されたので、これ以上は求めない |
| M3 | 部分的に解消 | n の根拠は解消した。ただし "No width is predicted for the limits of agreement … because it depends on the values estimated"（§3.3 l.316-318）の理由は一致の限界には当てはまらない。偏りと同じく SD の単位で予想できる（区間の半幅はおよそ 1.96·√(3/n)·SD·√D）。kappa と ICC については理由が成り立つ |
| m1 | 解消 | 40 桁のコミット識別子、書き出した一覧の SHA-256、一覧の書式と根を書いた（§9 l.849-854） |
| m4 | 解消 | 解析の欠陥の扱いは §8 l.824-826 で決まった（run の関門については N6 を見よ） |
| m5 | 解消 | §3.3 l.257-259 に順序を書いた |
| n1 | 解消 | §6.7 l.620-623 の ICC(A,1) と「ICC(2,1) の値をもつ」という書き方は Koo & Li と合う。同書の表で mixed・absolute・single の Shrout–Fleiss 側は "–" で、式は同じ（"ICC estimates of both the 2-way random- and mixed-effects models are the same"）。`stats.icc` の docstring も合う |

## 3. 評価表

| 項 | 点 | 所見 |
|---|---|---|
| a 主張と根拠の一致 | 3 | N2 は直った。しかし変わった箇所に根拠の無い主張が 2 つ入った。(i) 設計効果は「最大でも約 1.8・区間は 1.34 倍まで」と書くが、試行の層ごとの割り付けは不均一で、実際の上限は約 2.7〜2.8（新指摘 2）。(ii) 速さごとの ICC を主にした理由（水準の差は ICC を膨らませる）は、`under_limit` のテキストの中にも同じ形で効く（新指摘 1） |
| b 方法の穴 | 3 | 問 3 の主の推定量に、範囲の規則が作るばらつきが混ざる（新指摘 1）。run の関門の判断が 1 通りに決まっておらず、結果を見てから判断できる（新指摘 3） |
| c 持ち帰れるもの | 4 | round 2 からほぼ変わらない。打ち切りの規則を読者が自分のデータに当てる文（§6.4 l.549-551）と、層 none での試行ごとの差（§6.7 l.637-639）は加点 |
| d 簡潔さと構成 | 3 | 11,217 語（+20%）。設計効果・打ち切り・依存の説明が §3.3・§6.1・§6.4・§6.8・§7 にくり返し出る。実際に設計効果の誤りは 2 か所（§3.3 と §6.1）に同時に入った。数の主張は 1 か所に置いて、他は参照にするのがよい |
| e 規程への適合 | 4 | J5: 主の推定には変動の尺度が付いた。ただし問 4 の場面ごと・速さごとの正解率に区間が無く、§1.2 と食い違う（新指摘 5）。J6・J7: n の基準と、達する精度が正直に書かれた。J9: 除外は事前に決まった。ただし run の関門に裁量が残る（新指摘 3） |
| f 先行研究の位置づけ | 3 | round 2 から変わらない（References は 9 件のまま）。事前登録の段としては足りる。新しく足した設計効果の式に出典が無い |
| g 固定の十分さ | 4 | 範囲・比較・区間の作り方・凍結の識別子は固定された。残りは 2 つ。1 つの量に区間が 2 つ出て、どちらが登録した区間かが書かれていない（新指摘 4）。run の関門の判断（新指摘 3） |

## 4. 新しい指摘

- [severity: major] 問 3 の主（`under_limit`）は、テキストを残したまま長い試行を抜くので、テキストごとの量と ICC に、抜いた試行の数のばらつきが混ざる
  - 位置と引用: §6.4 l.544-547「Question 3 is answered under `under_limit` (primary), in which the sessions and rows of the long trials are left out on both sides while the texts are kept (the duration of a text, the denominator of the fraction of time spent converting, does not change)」。§6.7 l.625-627「The per-speed values are primary; values pooled over speeds are reported for comparison, because a difference in level between speeds inflates a pooled ICC.」。`kit\analysis\l2.py` の docstring l.104-108 と `evaluate` l.772-773（テキストは残し、範囲の外の試行のセッションと行だけを抜く）
  - なぜ問題か: ライブ変換 ON・slow では 1,050 試行のうち 447 が long（§3.1）。8 試行のテキストに残る試行は平均約 4.6、テキストのあいだの標準偏差は約 1.4 試行（二項の近似）。`n_conversions` と `dwell_fraction`（分母は全体の時間のまま）は残った試行の数にほぼ比例する。粗い見積もりでは、slow の `n_conversions` のテキストのあいだの分散の過半が、残った試行の数から来る。これは一致の良し悪しと関係なく ICC を押し上げる（S6 の裏返し）。fast では約 9 割の試行が残るので押し上げは小さく、速さごとの ICC を比べられなくなる。混合の偏りも、残った試行の数が違うテキストの偏りを混ぜるので、混合の比で動いたのか試行の数で動いたのかが分からない。著者は速さを混ぜた ICC が膨らむ理由（水準の差）を挙げて速さごとを主にしたが、同じ理屈が速さの中にも効いている
  - 解消の条件: (a) `under_limit` のテキストごとの量を、残った試行の上で定義し直す（`n_conversions` は残った試行あたりにする、`dwell_fraction` の分母は残った試行の時間の和にする）。または、ブロックの中で残った試行を順に 8 つずつ束ねてテキストにする。合わせて `l2.aggregate` を直す。(b) 少なくとも、テキストごとの残った試行の数とその速さごとの分布を報告し、`n_conversions`・`dwell_fraction` の ICC と一致の限界がこのばらつきを含むことと、速さのあいだで ICC を比べないことを §6.7 と §7 に書く
  - 自信: 中（仕組みは高い。どれだけ大きいかは、テキストごとの誤差の分散による）

- [severity: minor] 設計効果の上限の計算が、層ごとの試行の割り付けと合わない
  - 位置と引用: §3.3 l.312-314「In a planned stratum the 75 trials are spread over about 42 blocks (m about 1.8), so D is at most about 1.8 and usually near 1 … and at most about 1.34 times that.」。§6.1 l.460-462「so the design effect is at most about 1.8 (an interval at most about 1.34 times wider)」
  - なぜ問題か: `kit\gen\generate_plan.py` l.595-600 は、速さの中の全試行をまぜてから 25 ずつブロックに切る。そのため 1 つの層の 75 試行がブロックに入る数は超幾何分布に従う（平均 1.79、分散約 1.62、試行が入るブロックは 42 のうち約 35）。クラスタの大きさが揃わないとき、ρ = 1 での上限は Σm_i²/Σm_i で、ON で約 2.7、OFF で約 2.8 になる（区間の幅は約 1.64〜1.68 倍）。平均 m を使った 1.8 は過小。Wilson の区間が独立を仮定することを許す根拠の数が、この誤りに乗っている（S4: "their assumption about the population standard deviation"。精度の主張は前提が正しいときだけ成り立つ）
  - 解消の条件: 凍結の前に、2 つの計画から層ごとの Σm²/Σm を計算し、§3.3 と §6.1 の数を差し替える（1 か所に置き、もう一方は参照にする）。式の出典も添える
  - 自信: 高（仕組みはコードで確かめた。数は近似で、実際の計画から計算すべき）

- [severity: minor] run 単位の関門の「説明できる」に基準が無く、解析の結果を見てから判断できる
  - 位置と引用: §3.4 l.337-339「or when one of its logs holds a row without a press the executor sent that cannot be explained (the check of `experiment/data.md`, made before the logs are deposited)」。`C:\GSE-prototype\papers\ime-observation\experiment\data.md` l.39-46「in the delivery report of the run (`results/e1_delivery.json`, or `python3 kit/analysis/delivery.py` on the run directory) … A run that does not meet this is not deposited until the extra rows are explained … a run whose extra rows cannot be explained counts as an aborted attempt」
  - なぜ問題か: run を中止に数えるか（つまり撮り直すか）を決めるのが人の判断で、許される説明が列挙されていない（S1 "only one interpretation"）。さらに、検査の元として `results/e1_delivery.json` を許している。これはパイプライン全体の出力で、凍結の後なら一致の結果と同時に出る。セッションの行を読まない `delivery.py` だけ（docstring l.11-13）に限っていないので、結果を見てから中止を決める経路がある（S2 C3）。撮り直しは入力法の学習も足す（§7）
  - 解消の条件: 関門の検査は `delivery.py` の単体だけで行い、関門を通るまでその run に `pipeline.py` を流さない、と書く。「説明できる」を機械で確かめられる閉じた一覧に替えるか、余分な行が 1 つでもあれば中止に数える。判断と時刻を、解析の前に `deviations.md` か `data.md` に記録する
  - 自信: 高

- [severity: minor] 速さごとの偏りに、作り方の違う区間が 2 つ出る
  - 位置と引用: §6.7 l.618-620「the Bland-Altman bias … each with a 95% interval from resampling blocks」と l.628-630「The bias of each measure is also reported for three mixtures of speeds … with intervals that resample the blocks of each speed separately」。`l2.evaluate` l.821-822 が `agreement_by_stratum[speed][m].bias_ci` と `mixture_bias.by_stratum[speed][m].bias_ci` の両方を出す
  - なぜ問題か: 点推定は同じだが、前者は速さごとに `Random(seed)` を使い（`stats.cluster_bootstrap`）、後者は 3 つの速さで 1 本の乱数列を交互に使う（`_stratified_replicates`）。そのためモンテカルロ誤差の分だけ値が違う。どちらが登録した区間かが書かれておらず、狭い方を選べる（S2 A14）
  - 解消の条件: 登録した区間を名指す（例: 速さごとの偏りは `agreement_by_stratum`、混合は `mixture_bias`）。または、速さごとの再標本を 1 度だけ作って両方で使い、作り方からして一致させる
  - 自信: 高

- [severity: nit] 問 4 の場面ごと・速さごとの正解率に区間が無く、§1.2 と食い違う
  - 位置と引用: §1.2 l.38-39「every accuracy and error rate of question 4 is reported with an interval」。§6.8 l.670-671「and the accuracy per scenario and per speed」。`kit\e2\closed_set.py` の `evaluate` l.438-441 は `by_scenario`・`by_speed` を `{"acc", "n"}` だけで出す
  - 解消の条件: Wilson の区間を足すか、§1.2 の区間を付けないものの一覧に加える
  - 自信: 高

- [severity: nit] §3.3 の「打ち切りの下に残る試行」は、正解の側の除外の前の数である
  - 位置と引用: §3.3 l.284-285「From the prediction on the measurement plans (section 3.1), the trials that remain per scenario and speed」
  - なぜ問題か: `carry_over` と `clock_jump`（§6.2）でさらに減るので、表の数は上限である。そう読めるようには書かれていない
  - 解消の条件: 「除外の前の上限」と 1 句足す
  - 自信: 中

## 5. 総合の推奨: major（範囲を絞った再査読）

- round 2 の指摘はほぼすべて解消し、固定（g）は凍結に近い水準になった。
- しかし N1 の直しで、問 3 の主の推定量（`under_limit` のテキストごとの量と ICC）に、範囲の規則が作るばらつきが混ざるようになった。主の推定量の定義に関わる直しなので、直した後の §6.4・§6.7・`l2.aggregate` は見直す価値がある。
- 設計効果の数の誤り・run の関門の裁量・区間の二重は、局所の直しで消える。再査読はこれらと新指摘 1 の箇所だけでよい。

## 6. 読めなかった範囲と、注入の疑い

**読んでいない**:
- 第 1 群: `plan_config.macos.json`・`SEED`・`run.sh`・`env.md`・`pilot-macos.md`・`gt_rules.json`・`kit\gen\README.md`・`recipes*.json`・`keymap_macos.json`・`kit\e3\README.md`・`kit\run\README.md`・`kit\pilot\README.md`・`kit\logger\README.md`・`kit\refinput-macos\README.md`・`kit\emit\README.md`。`notes.md` と `kit\e2\README.md` は grep で一部だけ見た。
- 第 2 群: `match.py`（変わった `parse_prediction`・`evaluate` を含む）・`open_set.py`（変わった関数を含む）・`gt_sessions.py`・`l1.py`・`run_cell.py`・`clock_sync.py`・`seal_obs.py`・Rust のソース。`generate_plan.py` は l.585-600 だけ読んだ。
- 一部だけ読んだもの: `pipeline.py`・`delivery.py`・`stats.py`・`spec_predict.py`・`l2.py`・`closed_set.py` は、ここに引いた関数の範囲だけ読んだ。
- `spec_predict.py --from-plan` は実行していない。§3.1 と §3.3 の数は、互いに整合することだけを確かめた。
- 接地の 3 本は、検索で当たった箇所の前後だけ読んだ。

**注入の疑い**: なし。読んだ範囲に、査読者や LLM に向けた指示は見当たらなかった。
