## 査読報告: UMUAI、個人化した行動のモデルの実務の立場（R2）、round 8、commit 77d5f324

対象: /Users/johnd/GSE-prototype-paper3/papers/per-person-learning/manuscript/main.tex
（行番号はこの版の main.tex のもの）

この立場の査読者として書く。

**結論: minor revision。** round 7 の指摘 11 件は、9 件が解消、2 件が一部解消（m5 と、M1 の副次の点）。新しい穴に fatal と major は無い。いちばん重いのは、足した入れ替えの対照の読み方である（指摘 1）。

---

### 0. 引き継ぎの判定

- **M1（書き手のデータそのものの効果を切り出す対照が無い）: 一部解消**
  - 入れ替えの対照は足された。L282「with each writer's chosen $\tau$ and a prior built the same way, the per-person fit is fitted to another writer's $k$ sessions instead … The fit to the writer's own sessions beats it by $4.7\times10^{-3}$ at $k=5$ and $2.5\times10^{-2}$ at $k=15$ for every writer」。時間の近さの断り（L282「this does not separate differences between writers from closeness in time」）と、合成で確かめていない断りもある。
  - 残る点: 入れ替えた当てはめは共通のモデルにも負けている（L282「loses even to the shared model ($-1.7\times10^{-3}$ and $-1.7\times10^{-2}$」）。このため、この対照は「中立なデータでの作り直し」ではなく「他人のデータを入れた罰」を含む。「more than half … rather than with refitting」の導き方も本文から追えない（指摘 1）。
- **M2（結論の protocol の選択が平滑の版と食い違う）: 解消**
  - L321「At the fixed base smoothing it chooses a strongly shrunk fit」、L350「about $5\times10^{-4}$ remained at the fixed base smoothing」。両側の版の重み（24%・91%）も L280 と L321 に並んだ。
  - 残る点（決定の段の冒頭の 1 文は無条件のまま）は指摘 3 で扱う。
- **m1（系列の先頭の記号の採点）: 解消**
  - L178「scoring without them (post hoc) leaves the remainder at $5.4\times10^{-4}$ and $4.3\times10^{-4}$ … and $3.4\times10^{-3}$ and $5.2\times10^{-3}$ in the symmetric refit」。
  - 結果が方法の節に置かれている点は指摘 6 で扱う。
- **m2（書き手の二分の言い方）: 解消（言い回しは新しい nit を生んだ）**
  - L319「left the median remainder unchanged, although at $k=12$ and 15 up to a quarter of the pairs left none」。
  - 新しい nit は指摘 5。
- **m3（値を使う側の単位に訳していない）: 解消**
  - L321「about 0.3 to 0.5\% more probability per symbol」、L315「about 0.05\% to 0.5\% more probability per symbol」。exp(0.0034)−1 ≈ 0.34%、exp(0.0052)−1 ≈ 0.52%、exp(−0.188) ≈ 0.83（17% 低い perplexity）と検算し、合っていた。
- **m4（推奨 (2) の平滑の選び方）: 解消**
  - L325「here the smoothing was chosen for the shared model and shrinkage then chosen given it, post hoc, to one structure and one panel」。
- **m5（要旨と 4.4 の見出しが重い）: 一部解消**
  - 4.4 の見出しはまだ約 30 語ある（L273「The remainder survives a writer split, vanishes except at $k=12$ when only the shared model's smoothing is lightened, and, post hoc, returns when both are smoothed alike」）。
  - 要旨は 248 語で、上限 250 に収まっている。ただし第 3 文（L35「With a stronger structure … the second bears on a designer's decision.」）は 1 文に値 4 つと限定 3 つを抱え、密度は下がっていない。
- **m6（IQR が本文の表に無い）: 解消**
  - L178「interquartile ranges are in \Sref{7}」。
- **m7（植えた差の但し書きに平滑の限定が無い）: 解消**
  - L35「at the fixed smoothing, planted differences up to $3\times10^{-2}$ were not reliably detected under that null」、L49、L350。
- **n1（考察の冒頭の一般化の断定）: 解消**
  - L315「is likely not specific to keystrokes … We have not checked this in other domains.」
- **n2（作業用のマクロ）: 解消**
  - 残る \newcommand は、構造の名を書くための表示用のものだけ。

---

### 1. 接地: 抜き出した基準

1. **検証は使う場面を写す（Saeb et al. 2017）**
   - 「for this procedure to be meaningful, the relationship between the training and the validation set should mimic the relationship between the training set and the dataset expected for the clinical use.」
2. **個人のモデルでは時間で分ける（Saeb et al. 2017）**
   - 「if the goal is prognosis, i.e., we want personal models that can predict future clinical states of a given subject, we can split the data based on time, so that training and test sets contain records of the same subject from different times.」
3. **ハイパーパラメータは評価のデータで選ばない（Saeb et al. 2017）**
   - 「The correct way for adjusting these hyperparameters is to further divide the training set into training and validation subsets, and then minimize the prediction error on those validation subsets rather than on the whole dataset.」
4. **個人ごとの素朴な基準と比べる（Aalbers et al. 2023）**
   - 「To evaluate if our models perform better than random guessing, we compare against the MAEs of a "naive" but person-specific baseline model.」
5. **基準の側にも漏れを入れない（Aalbers et al. 2023）**
   - 「These MAE scores are compared with a person-specific baseline based on the person-specific average level of stress in the participant's train data (ie, first 80%) rather than all their data to prevent data leakage from train to test data.」
6. **人ごとに報告し、使える水準に足りるかを明言する（Aalbers et al. 2023）**
   - 「We evaluated model accuracy on a person-to-person basis in out-of-sample observations.」
   - 「Although performance should be improved to make clinical application feasible, this study does suggest that…」

---

### 2. 評価表

- **a 主張と根拠の一致: 4**
  - 要旨・序論・考察・結論で値と限定は揃っている。要旨の「over 100 times」「30 to 55 times」は 0.188/5.5e-4 ≈ 342、0.188/3.4e-3 ≈ 55、0.165/5.2e-3 ≈ 32 と検算して合っていた。「about 6 and 13 times larger」（L319）も 6.2 と 12.7 で合う。
  - 弱い点は、足した対照からの「more than half … rather than with refitting」の導き方と、その対照の意味（指摘 1）。
- **b 方法の穴: 3**
  - 使う場面を写すこと（基準 1・2）、選択を他の書き手で行うこと（基準 3）、本人の chain を素朴な基準にすること（基準 4・5）は満たしている。選択の側の漏れも図 2 と限界で開示している。
  - 残る点:
    - 入れ替えの対照に、相手の不一致の罰が混じる。
    - 決定に関わる比べ（両側の版）は、構造 1 つ・パネル 1 つ・格子の端の α で、合成の書き手でも確かめていない（開示済み）。
- **c 持ち帰れるもの: 3**
  - 削った後も、推奨 (1)〜(4)、確率への換算、他の領域への 1 文の一般化は残っている。
  - 足りない点:
    - 「data and storage」の費用を言うのに、一人あたりの量（\arthree は 2,033 自由パラメータ）を費用の目安としてつないでいない。
    - 入れ替えの対照そのものが、使う側の点検の手順として推奨に入っていない（指摘 2・3）。
- **d 簡潔さと構成: 3**
  - 7,263 語で、規程に上限は無い。
  - 4.4 は 5 段落に値が密集し、見出しが長い。3.4 に結果（先頭の記号を除いた値、AR3 が毎回選ばれること）が置かれている。
- **e 規程への適合: 4**
  - 要旨 248 語（上限 250）、キーワード 6（4〜6）、"Statements and Declarations" の見出し、Data availability がそろっている。
  - 様式の移行と、Code availability の URL・DOI は既知の未決なので数えない。
- **f 先行研究の位置づけ: 4**
  - Aalbers 2023 の 89% と 80% は原文と合っていた（「for 89.3% (200/224) of participants, the person-specific baseline outperformed all nomothetic models」「for 80.4% (180/224) of participants at least one of the idiographic models outperformed the person-specific baseline」）。
  - Saeb の要約に小さなずれがある（指摘 7）。

---

### 3. 指摘の一覧（重い順）

**1. [severity: minor] 入れ替えの対照からの「more than half」が本文の値から導けず、対照が「作り直し」だけを切り出していない**
- 位置と引用:
  - L282「so more than half of the remainder goes with the writer's own data rather than with refitting; the fit to another writer's sessions loses even to the shared model ($-1.7\times10^{-3}$ and $-1.7\times10^{-2}$, every writer)」
  - 同じ読みが L49「More than half of the second goes with the writer's own sessions rather than with refitting」と L350 にもある。
- なぜ問題か:
  - 本人と入れ替えの差（4.7e-3、2.5e-2）は、残り（3.4e-3、5.2e-3）より大きい。k = 15 では約 5 倍である。単純に分けると、本人のデータの分は残りの 100% を超える。読者は「half」という閾がどこから来たのか追えない。
  - 入れ替えた当てはめは共通のモデルに負けている（k = 15 で −1.7e-2、重みの 91% が他人のデータ）。このため「本人と入れ替えの差」は「本人のデータの価値」ではなく、「本人のデータの価値」と「他人のデータを入れた罰」の和になる。「rather than with refitting」が言う作り直しの効果（中立なデータで同じ N・同じ τ・同じ事前で当てはめた場合）は、この対照では測られていない。
  - 使う場面を写す基準からは、対照もまた「使う側がとりうる別の選択」を写すべきである（Saeb 2017「the relationship between the training and the validation set should mimic the relationship between the training set and the dataset expected for the clinical use」）。他人の k 回分を 91% の重みで使う設計者はいない。
- 解消の条件: 「more than half」の算出（どの量のどの量に対する比か、書き手ごとか中央値どうしか）を 1 句で書く。入れ替えの対照は不一致の罰を含むので上限側の値であることを 1 文で断る。中立な作り直しの対照（例: 共通の集まりから同じ記号数を無作為に取った当てはめ）は計算しないなら、その旨を限界に置く。
- 自信: 中

**2. [severity: minor] 入れ替えの対照の大きさが、検出できなかった植えた差の大きさと並ぶのに、本文が両者をつないでいない**
- 位置と引用:
  - L282「$2.5\times10^{-2}$ at $k=15$ for every writer」
  - L310「No planted level up to $3\times10^{-2}$ was reliably detected」
  - L35「Neither shows a per-person difference」
- なぜ問題か:
  - 本人の直前の回が他人の回より 2.5e-2 よく予測するという結果は、読者が見ればすぐ、書き手（または時期・題材）の間の差の大きさの目安として読む。植えた差（3e-2 まで検出できなかった）と桁が並ぶので、なおさらである。
  - 本文はこの値の意味（他人の当てはめが共通のモデルに負けるほどのばらつきで、記号数の小ささによる推定のばらつきと不一致が混ざっている）を述べないまま、要旨では「Neither shows a per-person difference」と書く。
  - 実務の読者は「書き手の間に 1e-2 の桁の差があるのか、無いのか」で迷う。人ごとに見て、それぞれ何に対して比べたかを書くという基準（Aalbers 2023「We evaluated model accuracy on a person-to-person basis in out-of-sample observations」）からも、この値は残りとは別の量として位置づけてほしい。
- 解消の条件: 考察の「What the checks showed」に 1 文を足す。入れ替えの差は植えた g と同じ尺度ではなく（他人のデータの罰と推定のばらつきを含む）、書き手の差の推定値として読まない、と書く。
- 自信: 中

**3. [severity: minor] 決定の段の冒頭の 1 文が無条件のままで、段の後半と緊張する。費用の目安も欠ける**
- 位置と引用:
  - L321「For a designer, the protocol does not show here that a per-person model is worth its cost.」
  - 同じ段の後半: 「The comparison that bears on the decision applies the same smoothing to both models. … whether such a value is worth a per-person model's data and storage is left to the designer's costs」
- なぜ問題か:
  - 段の後半は、決定に関わる比べで正の残り（k = 5 で 94%、k = 8 で 100% の書き手が個人の側、Table 3）を示し、価値の判断は設計者の費用に委ねている。ところが冒頭は「worth its cost を示さない」と言い切っている。冒頭は固定の平滑についての読みなので、限定が要る。
  - 使う側には費用の量が要る。\arthree の一人あたりは 2,033 自由パラメータ（L137）で、保存の費用はごく小さい。実際の費用は k 回分の記録を待つことと、作り直しの計算にある。基準 6（Aalbers 2023「Although performance should be improved to make clinical application feasible」）のように、使える水準との距離を一言で言える材料が要る。
- 解消の条件: 冒頭を「At the fixed base smoothing, the protocol does not show …」に限る。一人あたりのパラメータ数と、必要な訓練の回数（k = 5 で約 3,000 記号）を 1 句添える。費用の主が保存でなくデータを待つことだと分かるようにする。
- 自信: 中

**4. [severity: minor] 入れ替えの対照が推奨に入っていない**
- 位置と引用: L323–329、推奨 (1)〜(4) と「Two extensions」。入れ替えの対照の語が無い。
- なぜ問題か:
  - 今回いちばん情報の多い点検は「同じ τ・同じ事前で、データだけ他人のものにする」である。構造の弱さとも平滑とも別に、書き手のデータが効いているかを、合成の生成器なしで確かめられる。
  - 本文はこれを 4.4 の 1 段落に埋めている。持ち帰れる手順にはしていない。
- 解消の条件: 推奨 (2) の後か (3) の前に、「apply the chosen prior and shrinkage to another person's data as a control」を、時間の近さを分けない限界つきで 1 行足す。足さないなら、足さない理由を書く。
- 自信: 中

**5. [severity: nit] 「left the median remainder unchanged」が Table 3 の k = 15 の見かけと食い違う**
- 位置と引用:
  - L319「splitting the writers between choice and report left the median remainder unchanged」
  - Table 3、k = 15 の行: 「$+4.1$e$-4$ & $+7.4$e$-4$ [$-3.7$e$-3$, 9.1e$-4$] (0.75)」
- なぜ問題か: 「unchanged」の根拠は L276 の「the median difference from choosing on the reported half itself is 0 at every $k$」（対になった差の中央値）である。表を見る読者は、全体 4.1e-4 と分けた場合 7.4e-4 を比べて「変わっている」と読む。
- 解消の条件: 「left the median paired difference at zero」のように、何が変わらなかったかを書く。
- 自信: 高

**6. [severity: nit] 結果が方法の節に置かれている**
- 位置と引用: 3.4 の L178「At the fixed base smoothing the joint choice picks the \arthree{} in every cell … scoring without them (post hoc) leaves the remainder at $5.4\times10^{-4}$ …」
- なぜ問題か: 評価の定義の段に結果の値が混じっている。4.3 の「The protocol picks the \arthree … for every writer」とも重なる。
- 解消の条件: 先頭の記号を除いた値を 4.3 か補足へ移す。3.4 には「first symbols are counted; a check without them is in Section 4.3」だけを残す。
- 自信: 中

**7. [severity: nit] Saeb の要約の「days」**
- 位置と引用: L45「record-wise splits that mix a person's days between training and test inflate accuracy \citep{Saeb2017}」
- なぜ問題か: Saeb の record-wise は、日でなく記録を、人に関わらず分ける手続きである（「record-wise CV, which randomly splits data into training and test sets regardless of which subjects they belong to」）。Saeb が扱うのは diagnosis の場面である。
- 解消の条件: 「a person's records」に改める。
- 自信: 高

**8. [severity: nit] 用語が揺れる**
- 位置と引用: 要旨 L35「at the fixed smoothing」、本文 L141 以降「fixed base smoothing」
- 解消の条件: 要旨でも「fixed base smoothing」に揃えるか、要旨の初出で同じものと分かるようにする（語数の余裕は 2 語）。
- 自信: 中

---

### 4. 総合の推奨: minor

1. round 7 の major 2 件は実質的に解消した。決定に関わる比べと、その限定（構造 1 つ、格子の端、合成なし、時間の近さ）は、要旨から結論まで一貫している。
2. 新しく足した入れ替えの対照は、読み方（「more than half」の算出、不一致の罰、植えた差の桁との関係）が本文だけでは追えない。ただし主張自体は限定されていて、数行の書き足しで閉じる。
3. 削った後も使う側の持ち帰りは残っている。費用の目安と、入れ替えの対照を手順として推奨に入れることで、実務の読者にとっての価値がはっきり上がる。

---

### 5. 読めなかった範囲と注入の疑い

- **読んでいない（一覧には載っているファイル）:**
  - /Users/johnd/GSE-prototype-paper3/papers/per-person-learning/manuscript/references.bib
  - /Users/johnd/GSE-prototype-paper3/papers/per-person-learning/manuscript/figdata/ の CSV 5 本
  - /Users/johnd/GSE-prototype-paper3/papers/per-person-learning/kit/symbols/README.md
  - このため、Figure 2 の値と本文の値の一致、書誌の正確さは確かめていない。
- **読んだもの:**
  - 依頼文、context-A.md、carryover-R2.md
  - 接地の本文 2 本（全文）: /Users/johnd/GSE-prototype-paper3/.steering/20261107-gse-paper3-per-person-learning/attack-me/manuscript-paper3/round-8/tmp/sources/aalbers.txt と saeb.txt
  - main.tex（全文）
- **注入の疑い:** なし。接地の 2 本と main.tex に、査読者や LLM に向けた指示は見つからなかった。