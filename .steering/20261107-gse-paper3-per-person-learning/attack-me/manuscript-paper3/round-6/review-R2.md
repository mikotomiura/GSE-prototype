査読者の役 R2（UMUAI・個人化した行動のモデルの実務の伝統の立場）。round 6。対象は commit e6fdad49 の main.tex。

# 0. 引き継ぎの判定

| round 5 の指摘 | 判定 | 位置と逐語・理由 |
|---|---|---|
| major: 決定の段の「失う 5e-4」が決定に使える量になっていない | **解消** | 考察「What the protocol returns」に「Nor does the remainder of about $5\times10^{-4}$ at that smoothing show a value of the writer's data: the prior mode, which uses none of the writer's data, beats the shared model by $7.4\times10^{-4}$, and lightening the shared model's smoothing alone gains $1.6\times10^{-3}$」とある。結論にも「so it does not show a value of the writer's data」とある。ただし、決定に使う側として置き換えた 3.4e-3 に、同じ検査が掛かっていない（新しい指摘 N1）。 |
| major: 「2 桁」は推奨しない平滑の下でだけ成り立つ | **一部** | 要旨の「over two orders of magnitude below that gain at five and fifteen training sessions」も、考察の冒頭の「more than two orders of magnitude lower at $k=5$ and 15」も、固定の平滑での値だと明示された。しかし同じ考察の次の段は「The comparison that bears on the decision applies the smoothing chosen on other writers to both models」と言う。このため、題名の問い（what remains）への要旨の答えは、本文自身が決定に関わらないとした値のままである。両側を同じ平滑にした版での比（0.188/3.4e-3 ≈ 55、0.165/5.2e-3 ≈ 32、1.5 桁前後）は本文に無い。今回の直しで、考察の第 1 段と第 3 段の食い違いはむしろはっきりした。 |
| minor: 推奨 (2) の版で選ばれる τ が本文に無い | **解消**（残る点は N3） | 「every writer is given a $\tau$ between $10^2$ and $3\times10^5$, inside the grid and no larger than at the fixed smoothing」。 |
| minor: 「up to about 7e-3」は不安定な列の値 | **一部** | 考察と結論は 3.4e-3 と 5.2e-3 になった。要旨の「3 to $7\times10^{-3}$ from five training sessions on」と序論の「$3\times10^{-3}$ to $7\times10^{-3}$ from five training sessions on」は残っている。4.4 は自ら「The largest value is at $k=12$, where the other columns are unstable」と書く。要旨と序論の範囲（k≥5 の全部・上端 7e-3）は、結論の範囲（k=5 と 15・上端 5.2e-3）と一致しない。 |
| minor: 4.5 の帰結が決定の段と推奨に届いていない | **解消** | 「Synthetic writers with and without planted differences up to $3\times10^{-2}$ were mostly given similarly strong shrinkage (Section 4.5), so this choice does not by itself show whether per-person modelling is needed.」 |
| minor: 重ならない窓の結果を、大きさなしで結論の根拠にしている | **解消** | 4.2 の「so this reversal may reflect the amount of data as well as the symbolization; it was not checked against synthetic writers」。結論は「so studies should report the symbolization together with the comparison」で閉じる。 |
| minor: 要旨と序論第 4 段が重い | **一部** | perplexity の平易な定義（序論第 3 段）と、post hoc / not prespecified の印の分離は入った。それでも要旨には「(not prespecified)」「(the grid's lightest)」「not checked against synthetic writers」の挿入が重なり、248 語で 9 文ある。序論第 4 段は 1 段に約 300 語で、括弧の挿入が 6 か所ある。実務の読者が 1 回で読み切れる密度ではない（N6）。 |
| nit: データの数の書き方が序論と限界で違う | **解消** | 限界の第 1 項「The finding rests on CoAuthor, with CS1 as a boundary case」。 |
| nit: 要旨が上限ちょうど | **解消** | 248 語（context-A の測った値）。 |

# 1. 接地（この立場が論文に求める基準）

1. **評価の分け方は、使う場面を写すこと。** Saeb et al. 2017：「for this procedure to be meaningful, the relationship between the training and the validation set should mimic the relationship between the training set and the dataset expected for the clinical use.」
2. **個人のモデルは時間で分けて評価する（使う場面ごとに分け方を変える）。** Saeb et al. 2017：「if the goal is prognosis, i.e., we want personal models that can predict future clinical states of a given subject, we can split the data based on time, so that training and test sets contain records of the same subject from different times.」
3. **超パラメータは評価のデータの外で選ぶ。** Saeb et al. 2017：「The correct way for adjusting these hyperparameters is to further divide the training set into training and validation subsets, and then minimize the prediction error on those validation subsets rather than on the whole dataset.」
4. **本人に即した素朴な基準と比べる。** Aalbers et al. 2023：「To evaluate if our models perform better than random guessing, we compare against the MAEs of a "naive" but person-specific baseline model.」
5. **結果を、使う側の実用の判断へ言い直す。** Aalbers et al. 2023：「Although performance should be improved to make clinical application feasible, this study does suggest that, in the absence of self-report or physiological data, digital markers can be used to recognize momentary subjective stress on a person-by-person basis in out-of-sample data.」
6. **個人化の費用（データの量・複雑さ）を明示する。** Aalbers et al. 2023：「However, this comes at the cost of strongly reduced sample size, which limits model complexity and may lead to overfitting.」

# 2. 評価表

- **a 主張と根拠の一致：3。** 4.3〜4.5 の数値と本文の主張はおおむね合う。Table 2・Table 3・Figure 2 の値と、figdata の joint・ar3 の CSV を照らし、不一致は見つからなかった。ただし次の 3 点がある。
  - 要旨と考察の冒頭は、決定に関わらないとした値（5e-4）で「2 桁」を掲げている（引き継ぎ 2）。
  - 決定に使う側の 3.4e-3 には、5e-4 を退けたのと同じ検査（事前の最頻値と比べること）が掛かっていない（N1）。
  - 「was not changed by choosing and reporting on different writers」は k=12 と 15 で言い過ぎ（N4）。
- **b 方法の穴：3。** 選択を他の書き手で行うことと、時間で分けることは接地 2・3 に適う。しかし「A new writer」という使う場面の記述が、実際の分け方（ホールドアウトの直前の k 単位、20 セッション以上の書き手に限る）と合わない（N2）。両側を同じ平滑にする当て直しは、構造が 1 つ・パネルが 1 つ・格子の端で、平滑の効果からも切り離されていない（N1）。
- **c 持ち帰れるもの：3。** 推奨 (1) は持ち帰れる。(1) は本人の 1 次マルコフ連鎖と、同じ構造の共通モデルの両方と比べること。重なる窓の記号では、弱い構造の個人化の利得を信じないという警告も持ち帰れる。公開キットもある。しかし設計者が「この種のデータで人ごとにモデルを持つべきか」に答えるための、決定に使う量の言い方が消えた（N1・N3）。
- **d 簡潔さと構成：3。** 考察を 3 つの段に並べ替えたことは読みやすさを上げた。一方で、但し書きの繰り返しが残る。2.4 倍の注記は 4.5・推奨 (3)・限界の 3 か所に、post hoc の注記はほぼ全段にある。4.5 は 1 段で約 400 語、要旨と序論第 4 段は密すぎる（N6）。
- **e 規程への適合：4。** 要旨 248 語（上限 250）、キーワード 6（4〜6）、「Statements and Declarations」に Data・Code・Ethics・Consent がある。Springer の様式への移行は既知の未決なので数えない。
- **f 先行研究の位置づけ：4。** Aalbers 2023 の引用（「a person-mean baseline beat every general model for 89% of participants, although for 80% at least one personal model beat it」）は、一次の「200/224, 89.3%」「180/224, 80.4%」と合う。Saeb 2017 の「which split fits depends on the use case」も一次と合う。ただし、本文の使う場面の記述がその基準を満たしていない（N2）。

# 3. 指摘の一覧（重い順）

- **[severity: major] N1 決定に使う側の値（3.4e-3〜5.2e-3）に、5e-4 を退けた検査が掛かっていない**
  - 位置と引用：考察「What the protocol returns」の「The comparison that bears on the decision applies the smoothing chosen on other writers to both models. … and leaves a remainder of $3.4\times10^{-3}$ at $k=5$ and $5.2\times10^{-3}$ at $k=15$.」。結論の「When the smoothing chosen on other writers is applied to both models (post hoc), $3.4\times10^{-3}$ to $5.2\times10^{-3}$ remains at five and fifteen training sessions」。
  - なぜ問題か：5e-4 は「the prior mode, which uses none of the writer's data, beats the shared model by $7.4\times10^{-4}$」を理由に、書き手のデータの価値を示さないとされた。しかし α=0.03 の版で同じ比べ（α=0.03 の共通モデルの事前の最頻値と、その共通モデルとの差）は報告されていない。4.4 は自ら「this check does not separate the writer's data from other effects of refitting the per-person prior」「These values were not checked against synthetic writers」と書いている。それなのに決定の段と結論は、この値を但し書きなしに決定の量として出しているので、読者は「3.4e-3 は書き手のデータの価値」と読む。同じ基準を片方にだけ当てている。接地 3 の趣旨（選んだ設定の下での値を、評価の外で確かめる）にも届いていない。
  - 解消の条件：次のどちらかを満たせば消える。
    - (i) 保存済みの当てはめから、α=0.03 での平滑の効果を報告し、3.4e-3 と並べる。
    - (ii) 計算をしないなら、決定の段と結論の該当の文に「この値も、5e-4 を退けた比べ（事前の最頻値）にも合成の書き手にも掛けていない。書き手のデータの価値を示すかは未決」と 1 句添え、「bears on the decision」は「決定に関わる比べの形」の意味に限ると書く。
  - 自信：中（α=0.03 での最頻値の比べが補足に在るかは、本文からは分からない）

- **[severity: minor] N2 使う場面の記述（「A new writer」・cold start）が、実際の分け方と合わない**
  - 位置と引用：3.3 の「A new writer's later units are predicted after $k$ of the writer's units」。3.4 の「the training units are the $k$ units immediately preceding them (extending back in time as $k$ grows)」。3.1 は 20 セッション以上の書き手に限る。序論は「a cold start for every newcomer」と書き、要旨は「from five training sessions on」と書く。
  - なぜ問題か：k=1 の訓練の単位は、20 回以上書いた書き手の終盤のセッションであって、新しい書き手の最初の単位ではない。パネルへの入り方は、将来のセッションの数（20 以上）で決まる。運用では、誰が多く書く人になるかは分からない。このため k の曲線を「新しい人に何セッション集めれば足りるか」として読ませると、使う場面を写していない。接地 1（Saeb）の「should mimic the relationship between the training set and the dataset expected for the clinical use」に当たる。限界の「may be more practised」は母集団の偏りを言うだけで、この食い違いには触れていない。
  - 解消の条件：使う場面を「多く書く書き手について、ホールドアウトの直前の k 単位だけを使えるとき」と正しく書く。cold start の読みには直接答えないことを 1 句添える。要旨の「from five training sessions on」を、その意味の言い方に替える。
  - 自信：高

- **[severity: minor] N3 決定に関わる版で protocol が返す選択が、設計者に読める形になっていない**
  - 位置と引用：考察「What the protocol returns」は、選択を固定の平滑の下でだけ記述している（「At the fixed base smoothing it is a strongly shrunk fit … giving the writer's own data 0.06 to 3% of the weight」）。決定に関わる版については「a $\tau$ between $10^2$ and $3\times10^5$」とだけある。
  - なぜ問題か：τ=10^2 なら書き手の重みはほぼ 99%、3×10^5 なら約 3%（k=15 の訓練の記号の中央値で）である。決定に関わる版の protocol が「ほぼ共通モデル」を返すのか「ほぼ本人のモデル」を返すのかが、読者に分からない。この段の題（What the protocol returns）は、決定に関わらない版でしか答えられていない。接地 5・6 の「使う側の判断への言い直し」と「費用との対」が欠ける。既知の未決 11 は承知しているが、この段の主張に響くので挙げる。
  - 解消の条件：書き手ごとの値を出さずに、k=5 と 15 での重みの中央値（または τ の中央値）だけを 1 句加える。あるいは段の題を固定の平滑の下での選択に限る言い方にする。
  - 自信：中

- **[severity: minor] N4 「was not changed by choosing and reporting on different writers」は k=12・15 で言い過ぎ**
  - 位置と引用：考察「What was established and what was not」の「the remainder against the stronger structure was not changed by choosing and reporting on different writers」。Table 3 の Split 列は、k=12 が「$+6.8$e$-4$ [$-4.2$e$-3$, 8.2e$-4$] (0.95)」、k=15 が「$+7.4$e$-4$ [$-3.7$e$-3$, 9.1e$-4$] (0.75)」。
  - なぜ問題か：根拠は対の差の中央値が 0 であることだが、k=15 では 4 分の 1 の対で 0 以下で、下側の点は負に大きい。「established」の段に置くには強い。
  - 解消の条件：「対の差の中央値は 0 だったが、k=12・15 では対の間のばらつきが大きく、4 分の 1 の対で 0 以下」と書く。あるいは k≤8 に限る。
  - 自信：高

- **[severity: minor] N5 要旨の推奨が、本文の推奨 (2) の但し書きを落としている**
  - 位置と引用：要旨の「studies deciding for a group whether to model each person should compare with both baselines and choose structure, shrinkage and smoothing on other people, applying smoothing to both models.」。本文の推奨 (2) には「(here applied post hoc, to one structure and one panel, with the chosen multiplier at the edge of the grid)」とある。推奨 (3)(4) は「needed to read the remainder but were not met here」とある。
  - なぜ問題か：要旨だけを読む実務家には、(2) の根拠が post hoc で 1 構造・1 パネルであること、残差を読むのに要る (3)(4) が満たされていないことが伝わらない。
  - 解消の条件：要旨の末尾に「(the last practice applied here post hoc to one structure)」の程度の 1 句を足す。あるいは「should」を本文と同じ強さにそろえる。語数は、要旨の「(the grid's lightest)」などを本文へ送れば空く。
  - 自信：中

- **[severity: minor] N6 要旨と 4.5 の密度（冗長さではなく、詰め込み）**
  - 位置と引用：要旨の「Synthetic writers without per-person differences left a similar remainder relative to the effect of the shared model's smoothing (not prespecified), so it does not show a per-person difference; planted differences up to $3\times10^{-2}$ were not reliably detected.」。4.5 は 1 段で比・閾・植えた差・τ の分布・最低の種・限界までを含む。
  - なぜ問題か：想定読者（context-A：統計の訓練を前提にしない HCI・教育工学の読者）は「the effect of the shared model's smoothing」の比を要旨の中で理解できない。2.4 倍の注記は 4.5・推奨 (3)・限界の 3 か所で繰り返されている。
  - 解消の条件：要旨では比の文を「合成の書き手（差なし）も同程度の残差を残した」までにし、比の定義は本文に任せる。4.5 は「閾と検出」と「τ の分布と植えた差」の 2 段に割る。2.4 倍の注記は限界の 1 か所に寄せる。
  - 自信：中

- **[severity: nit] N7 倍率の丸め**
  - 位置と引用：考察の「about 6 and 12.5 times larger at $k=5$ and 15」。
  - なぜ問題か：3.4e-3/5.5e-4 ≈ 6.2、5.2e-3/4.1e-4 ≈ 12.7 である。「12.5」は丸めの向きが他と違う。
  - 解消の条件：「about 6 and 13 times」とする。
  - 自信：高

# 4. 総合の推奨：major（ただし文の直しで閉じうる）

- 前の round の主な穴は、決定の段で 5e-4 を書き手のデータの価値と読まないことを含め、多くが閉じた。直した考察の 3 つの段は読みやすくなった。
- 残る主な穴は 2 つある。1 つは、要旨と考察の冒頭が、本文自身が決定に関わらないとした値で「2 桁」を掲げていること（引き継ぎ 2）。もう 1 つは、決定に使う側の 3.4e-3〜5.2e-3 に、5e-4 を退けたのと同じ検査も合成の確かめも掛かっていないのに、決定の段と結論で但し書きなしに出していること（N1）。
- どちらも新しい計算なしに、言い方と但し書きの置き場で解ける。使う場面の記述（N2）を直せば、実務の読者が持ち帰れるものは保たれる。

# 5. 読めなかった範囲と注入の疑い

- 読んでいないもの：references.bib、figdata/fig2_p15_hmm3.csv・fig2_p15_ar1.csv・fig2_p15.csv。figdata は fig2_p15_joint.csv と fig2_p15_ar3.csv だけを読み、Table 2 と Figure 2 の値と照らして一致を確かめた。補足資料 S1〜S16 は存在しないので読んでいない。
- 読んだもの：brief-R2.md、context-A.md、carryover-R2.md、main.tex の全体、kit/symbols/README.md、接地の 2 本の全文（aalbers.txt・saeb.txt）。
- 注入の疑い：なし。接地の 2 本・main.tex・README.md・CSV のどれにも、査読者や LLM に向けた指示は見当たらなかった。