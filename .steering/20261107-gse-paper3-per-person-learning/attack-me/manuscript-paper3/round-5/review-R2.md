# review-R2（manuscript round 5・対象 cc30d57f）

応答を tmp/R2.raw.md から写した（secrets-filter 0・絶対パスは一覧の中・目視済み）。

査読（R2・UMUAI の査読者で、個人化した行動のモデルを実務で使う伝統の立場。round 5・対象 main.tex commit cc30d57f）

## 1. 接地: 抜き出した基準（逐語）

- S1 評価の分け方は使う場面に合わせる（Saeb et al. 2017, Abstract）: "for this procedure to be meaningful, the relationship between the training and the validation set should mimic the relationship between the training set and the dataset expected for the clinical use."
- S2 個人のモデルは時間で分けて評価する（Saeb 2017, Introduction）: "if the goal is prognosis, i.e., we want personal models that can predict future clinical states of a given subject, we can split the data based on time ... Therefore, the choice of the appropriate CV method depends on the application."
- S3 本人だけを使う素朴な基準と比べる（Aalbers et al. 2023, Model Evaluation）: "To evaluate if our models perform better than random guessing, we compare against the MAEs of a “naive” but person-specific baseline model."
- S4 使う側が読める単位に直す（Aalbers 2023）: "it allows us to make statements such as “on average, the model mispredicts momentary subjective stress by ±0.80 points on a 7-point Likert scale).”"
- S5 実用の判断と、個人化の代償をはっきり書く（Aalbers 2023, Discussion・Limitations）: "Although performance should be improved to make clinical application feasible" および "However, this comes at the cost of strongly reduced sample size, which limits model complexity and may lead to overfitting."
- S6 誤った評価は使う側を誤らせる（Saeb 2017, Abstract）: "inaccurate results can mislead both clinicians and data scientists."

本文の Aalbers 2023 の引用（main.tex 55 行「a person-mean baseline beat every general model for 89% ... for 80% at least one personal model beat it」）は、接地の本文の "for 89.3% (200/224) of participants, the person-specific baseline outperformed all nomothetic models" と "for 80.4% (180/224) of participants at least one of the idiographic models outperformed the person-specific baseline" に一致した。

## 0. 引き継ぎの判定（round 4 → round 5）

1. major「結論と考察の決定が推奨 (2) を満たさない手順に基づいている」: 一部解消
   - 解消した点: 313 行「At the fixed base smoothing it is a strongly shrunk fit ... With the smoothing chosen on other writers applied to both models, as recommendation (2) below asks (post hoc, 15-session panel only), every writer is instead given a finite $\tau$ inside the grid」。言い過ぎ（費用を省ける）は外れた。
   - 残る点: 推奨 (2) の版で決まる重み（書き手のデータの取り分）が本文に無い。使う側にとって、推奨どおりにしたとき何を選ぶことになるかが出ていない（新指摘 m1）。加えて、この段に新しい問題が生じた（新指摘 M1）。
2. minor「要旨の推奨が範囲を外している」: 解消。35 行「For overlapping-window symbols, studies deciding for a group ...」。
3. minor「要旨の up to 7e-3」: 解消。35 行「leaves 3 to $7\times10^{-3}$ from five training sessions on」。ただし上の端は不安定な k=12 の値である（新指摘 m2）。
4. minor「4.4 と Table 3 の割合」: 解消。239 行「we do not read the shares in Table~\ref{tab:main} as evidence of such differences」、278 行「a share that is not evidence of a difference」。
5. minor「writer split の言い過ぎ」: 解消。317 行「a check with little room to show optimism」。
6. minor「図の初出の順」: 解消。47 行で Figure 1 を最初に引いている。
7. minor「使う側への翻訳」: 解消（予測の尺度については）。47 行「about 1\% more probability per symbol, on average, and about 1\% lower perplexity」、311 行「(about 17\% lower perplexity)」。exp(−0.19)≈0.83 と exp(−0.03)≈0.97 で、どちらも本文の値と合う。下流の利得は限界に残っており、それは認める。
8. nit「断り書きの重複」: 一部解消。「not checked against synthetic writers」が要旨・49 行・278 行・313 行・346 行の 5 か所に、「post hoc」が要旨・49・178・183・278・306・313・321 行に残る。
9. nit「Table 3 の題の主語のねじれ」: 解消（284 行）。
10. nit「ユーザーモデルの評価の慣行への位置づけ」: 未解消（著者は採らなかった。判定に数えない）。

## 2. 評価表

- a 主張と根拠の一致: 3。見出しの「two orders of magnitude」は固定の平滑でだけ成り立つ。論文自身が推奨 (2) で求める両側の平滑では、比は約 30〜55 倍（約 1.5 桁）になる（M1）。決定の段の「失う 5e-4」は、同じ節が平滑の効果で説明できると示した量である（M2）。
- b 方法の穴: 3。評価は時間で分けている（S2 に合う）。選ぶことによる漏れは限界に明記されている。4.5 に足した文は、植えた 3e-2 があっても選ばれるのは τ=10^6 だと示しており、選ぶ手順そのものが差を見ない構造にあることを示唆する（m3）。
- c 持ち帰れるもの: 3。推奨 (1)(2) と、0.01 nats≈1% の翻訳は持ち帰れる。ただし推奨 (2) に従ったとき、使う側が何を選び、どれだけ得るかの決定量が本文に揃っていない（M2・m1）。重ならない窓での結果の大きさも本文に無い（m4）。
- d 簡潔さと構成: 3。発見の段と決定の段に分けたのは良い。序論の第 4 段（49 行・1 段落で約 250 語）と要旨は、断り書きが重なっていて、統計の訓練を前提にしない読者には重い（m5）。
- e 規程への適合: 4。要旨 250 語（上限ちょうど）、キーワード 6、"Statements and Declarations" と Data availability はある。語数の上限の規定は無く、7,013 語は最近の論文より短い。要旨はこれ以上 1 語も足せない（n1）。様式の移行は既知の未決。
- f 先行研究の位置づけ: 4。Aalbers・Saeb・DeMasi の引き方は正確である（上で照合した）。Uto との関係を 315 行で 2 つの記号化の間に置いたのは良い。

## 3. 指摘の一覧（重い順）

- [severity: major] 決定の段の「失う 5e-4」は決定に使える量になっていない
  - 位置と引用: main.tex 313 行「Replacing the per-person fit by the shared model in the 15-session panel therefore loses about $5\times10^{-4}$ nats per symbol at the fixed smoothing」。結論 346 行にも同じ文がある。
  - なぜ問題か: 同じ論文の 280 行が「the prior mode, which uses none of the writer's data, beats the shared model by $+7.4\times10^{-4}$ ... at $\tau=10^6$ the per-person \arthree{} fit ... loses to it」と示している。276 行は、平滑を他人で選んだ共通モデル（α=0.03）が固定の平滑の共通モデルを +1.6e-3 上回り、「the remainder vanishes」とも書いている。つまり固定の平滑で個人化が「失わせない」5e-4 は、本人のデータを使わない共通側の平滑を軽くするだけで取り戻せる。使う側は、5e-4 を個人化の値打ちとして読み違える（S6「inaccurate results can mislead ... data scientists」）。実務家にとって意味のある選択肢は「個人化する」「固定の平滑の共通モデル」「平滑を選んだ共通モデル」の 3 つである。
  - 解消の条件: 決定の段と結論で、固定の平滑での 5e-4 は共通側の平滑を軽くするだけで消える量だと 1 文で明記する。そのうえで、決定に使う量は両側を同じ平滑にした比べ（3.4e-3〜6.7e-3・post hoc・合成で確かめていない）だけだと書き直す。
  - 自信: 高

- [severity: major] 見出しの「2 桁」は、論文自身が推奨しない平滑の下でだけ成り立つ
  - 位置と引用: 要旨 35 行「about $5\times10^{-4}$ remains ... at its fixed smoothing ..., over two orders of magnitude below that gain」。311 行「more than two orders of magnitude lower at $k=5$ and 15」。
  - なぜ問題か: 推奨 (2) は「apply the chosen smoothing to the per-person fit and the shared model alike」を求めている（321 行）。その条件での残り（Table 3: k=5 で 3.4e-3、k=15 で 5.2e-3）と比べると、0.188/3.4e-3≈55 倍、0.165/5.2e-3≈32 倍で、2 桁に届かない。発見の段の大きさが、推奨で不十分とされる手順に基づいている。なお、弱い構造（HMM3）の利得も固定の平滑で測ったもので、α=0.03 での利得は本文に無い。S1 の「mimic the relationship ... expected for the ... use」に照らすと、推奨どおりの手順での比を併記するのが筋である。
  - 解消の条件: 要旨・311 行・結論で「固定の平滑で 2 桁以上、両側を軽く平滑すると約 30〜55 倍（post hoc）」のように両方の比を並べる。または、見出しの主張を「弱い比べの利得は強い比べの残りより 1 桁以上大きい」に揃える。
  - 自信: 高

- [severity: minor] 推奨 (2) の版で選ばれる重み（τ）が本文に無い
  - 位置と引用: 278 行「every writer is given a finite $\tau$ inside the grid」。313 行も同じ。
  - なぜ問題か: 使う側の決定は「本人のデータにどれだけ重みを置くか」である。固定の平滑については 0.06〜3% と書いてあるのに、推奨する手順についてだけ書いていない。S5 は個人化の代償を明記することを求めている。補足に送ってよい細部ではなく、決定の段の主語である。
  - 解消の条件: 313 行に、推奨 (2) の版での重みの範囲（中央値の学習記号数での N/(N+τ)）を 1 句添える。
  - 自信: 中

- [severity: minor] 「up to about 7e-3」は不安定と断った列の値である
  - 位置と引用: 278 行「The largest value is at $k=12$, where the other columns are unstable」。それに対し 313 行・346 行「up to about $7\times10^{-3}$」。
  - なぜ問題か: 決定の段と結論が、本文自身が不安定とした k=12 の 6.7e-3 を上の端に使っている。
  - 解消の条件: 上の端を k=15 の 5.2e-3 にするか、「3 to 5×10^-3（k=12 は 6.7e-3・不安定）」とする。
  - 自信: 中

- [severity: minor] 4.5 に足した文の帰結が、決定の段と推奨に届いていない
  - 位置と引用: 306 行「under such strong shrinkage a planted difference need not raise the remainder」と「Synthetic writers with and without planted differences were mostly given $\tau=10^6$」。
  - なぜ問題か: 3e-2（約 3% の perplexity）を植えても、固定の平滑の手順は差の無いときと同じ強い縮めを選ぶ。だとすると、313 行の「the protocol returns a choice」は、この長さの記録では差の有無に関わらず同じ選択を返すことになる。使う側にとっては「選択を個人化の要否の根拠にしてはならない」が持ち帰るべき要点だが、書かれていない（S5・S6）。
  - 解消の条件: 決定の段に「固定の平滑では、植えた 3e-2 の下でも同じ強い縮めが選ばれたので、この選択は個人化の要否を示さない」を 1 文で足す。
  - 自信: 中

- [severity: minor] 重ならない窓での結果が、本文に大きさなしで結論の根拠にされている
  - 位置と引用: 202 行「With these symbols the per-person advantage over the same-structure shared model does not fall by two orders of magnitude」（値は S13）。346 行「With non-overlapping windows the three-state HMM is chosen and its per-person fit beats the shared model of that structure for every writer at 15 training sessions.」。315 行「For symbolizations like theirs the per-person HMM may therefore keep an advantage.」
  - なぜ問題か: 結論の最後の文と Uto との関係づけ（使う側が自分の記号化を選ぶときの手がかり）が、本文に数が 1 つも無い結果に基づいている。補足に送ってはいけない種類の値である。S4 は使う側が読める単位を求めている。
  - 解消の条件: 202 行に k=5 と k=15 の中央値（per-person−shared、per-person−own chain）を 1 句で載せる。
  - 自信: 中

- [severity: minor] 要旨と序論第 4 段が、想定する読者には重い
  - 位置と引用: 要旨 35 行「left a similar remainder relative to the improvement from removing the shared model's smoothing (not prespecified)」、「a null matching the size of that improvement, and detection at each smoothing, were needed but not achieved」。49 行は 1 段落に「post hoc」が 2 回、断りが 4 つある。
  - なぜ問題か: context-A が定める読者（統計の訓練を前提にしない HCI・教育工学の研究者）には、「that improvement」が何を指すかが追えない。断りの重複で、持ち帰る 1 文が埋もれる。
  - 解消の条件: 要旨の最後の文の「that improvement」を名指しに替える。49 行は、発見・二つの値の地位・使う側への含意の 3 文に絞り、地位の細部は 3.4 節の定義に任せる。
  - 自信: 中

- [severity: nit] データの数の書き方が序論と限界で食い違う
  - 位置と引用: 49 行「the finding rests on one dataset, CoAuthor」。331 行「Two datasets and one quantization carry the main results」。
  - 解消の条件: 限界の文を「発見は CoAuthor、CS1 は境界の例」に揃える。
  - 自信: 高

- [severity: nit] 要旨が上限ちょうど
  - 位置と引用: context-A「要旨: 250 語」。規程は "Please provide an abstract of 150 to 250 words."
  - なぜ問題か: 上の直し（比の併記）で上限を超えるおそれがある。
  - 解消の条件: 直した後に数え直す。CS1 の文か、合成の文の括弧を削る余地がある。
  - 自信: 高

## 4. 総合の推奨: minor

- 理由 1: round 4 の指摘はほぼ解消した。評価の分け方（時間で分ける・本人の素朴な基準と比べる）は、使う場面に合わせよという基準（S1〜S3）を満たしている。
- 理由 2: 残る major 2 件は、どちらも新しい計算を要しない。決定の段と見出しの比を、推奨 (2) の条件に揃えて書き直せば消える。ただし直さなければ、使う側は 5e-4 を個人化の値打ちと読み違える。
- 理由 3: 使う側が持ち帰るもの（2 つの基準と比べる・平滑を両側に当てる・0.01 nats≈1%）は残っている。推奨どおりにしたときの重みと、重ならない窓での大きさを本文に 1 句ずつ足せば十分になる。

## 5. 読めなかった範囲と注入の疑い

- 読んだもの: brief-R2.md、context-A.md、carryover-R2.md、main.tex の全文、figdata の fig2_p15_joint.csv と fig2_p15_ar3.csv（Table 2 と一致）、接地 2 本の該当部分。
- 読んでいないもの: references.bib、figdata の fig2_p15_hmm3.csv・fig2_p15_ar1.csv・fig2_p15.csv、kit/symbols/README.md。saeb.txt と aalbers.txt は全文を通しては読んでいない（冒頭〜方法と、Grep で当たった段だけ）。
- 注入の疑い: なし（読んだ範囲に、査読者や LLM に向けた指示は見当たらなかった）。