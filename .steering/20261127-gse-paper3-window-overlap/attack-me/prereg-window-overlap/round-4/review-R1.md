# 査読 R1 round 4（行動の記号列の系列モデルの方法論・paper-reviewer / opus）

## 1. 接地
- 基準 1 Pohle 2017（991）"it may just as well be an indication that the additional states merely mop up some structure missing in the model, but have no clear (biological) meaning"
- 基準 2 Pohle 2017（949-952）"the residuals obtained for the two-state model exhibit much stronger autocorrelation than those for the three-state model. This could be an indication of a violation of the dependence assumptions"
- 基準 3 Pohle 2017（993-997）"a large difference in AIC, BIC, ICL or any other information criterion alone does not prove that the model with the higher (or lower) number of states is most suitable ... What exactly these problems may be then needs to be investigated further."
- 基準 4 Singer 2014（140-147）"choosing the model with the highest likelihood is biased towards models with more parameters ... higher order models are naturally favored by their improvements in likelihoods."
- 基準 5 Singer 2014（20-23）"the memoryless model represents a quite practical model for human navigation on a page level. However, when we expand our analysis to a topical level ... we find that the memoryless assumption is violated"
- 基準 6 Monaco 2018（163-168）"Typing behavior generally evolves over time ... A user's keystroke dynamics is also generally dependent on the typing task."

## 2. 評価表
- a 3: 型 1 の R_ar3 の条件は s = 30 の縮みの床で機械的に満たされうる（指摘 1）。型 3 は仕組みが予測しない形なのに「支えない」と書かない（指摘 3）。
- b 3: τ = 10,000 の行が s = 30 で床の対照として効かない。R_A30 について仕組みが何を予測するかを導いていない（指摘 2）。
- c 4: 境の歩み s* と列 C はどの結果でも持ち込める。
- d 3: 句の置き方が Discussion の第 1 段落と食い違う（指摘 4）。型 1 の置き換え文が内部の語「列 C」に依る。
- e 5: 1 通りに決まっている。
- f 4: Pohle の埋め合わせと ar が選ばれる現象を区別。Uto2020 に広げていない。
- g 4: 残る自由は R_ar3 の合わせ方の順と 1 人抜きの分母（指摘 5・6）。

## 3. carryover の判定
- major 1（覆う時間）: 解消（20・114・253 行）
- major 2（R_ar3 の床）: 一部だけ解消。s = 30 では τ = 10,000 自体が床で対照として効かない（新しい指摘 1）
- minor 3〜8・nit 2 件: すべて解消（175・134・150・103・237・159・179・19・205 行）

## 4. 指摘
- [major] 1 τ = 10,000 の固定の行は s = 30 で縮みの床の対照にならない。stay_Rfix を τ 他人の stay_G と比べていて非対称
  - 位置: 153・144・148・255 行
  - 理由: S13 notes 13 行によると n の評価の記号の中央値は 107。学習の記号は k = 5 で数百、k = 15 でも千台と見込まれ、τ = 10,000 での重みは数 % から十数 %。A30 と C30 は同じ記号の数で、両方で本人 ar3 は共有 ar3 にほぼ縮み、stay_Rfix ≈ 0 で「小さい」がほぼ構造から出る。相手の stay_G は τ 他人の hmm3 で床に張りつかない（G_A30 = 0.043 / 0.096 が既知）。基準 4 の非対称。重みの表は読みに入っていない。
  - 解消: (a) R^fix の語を同じ τ = 10,000 の G^fix から取った stay_Gfix(30) を基準に判定、(b) 型 1 に「C30・A30 の本人 ar3 の重みの中央値が同じ列の本人 hmm3 の重みの 1/2 以上」を足し外れれば型 2′（重みで比べられない）、(c) 重みをそろえた τ の行を足す、のどれか。
  - 自信: 中（N は評価の記号の中央値からの推定）
- [major] 2 R_A30 について仕組みが何を予測するかを導いていない。仕組みと合う結果が「逆」になって型 2′ に落ちうる
  - 位置: 12・144・150・168 行
  - 理由: 仕組みの直接の予測は、列 C の中で G_C30 が大きく R_C30 が小さいこと（A1 で G 0.140 に対して R 約 1e-3 と同じ形）。読みは差の差 R_C30 − R_A30。A30 では従属が小さく（ρ_h 0.037 / 0.012）hmm3 と ar3 の違いは効かないはずで、仕組みの外の得（G_A30 = 0.043 / 0.096）が R_A30 にもそのまま出ると見込める。すると R_C30 が小さくても stay_R ≈ −G_A30 となり「逆」になる。基準 3。
  - 解消: 仕組みが R_A30 に予測する値（≈ G_A30 か ≈ 0 か）を書き、それに合う量を選ぶ。例 R の語を列 C の中の対比 (G_C30 − R_C30) / stay_G(30) で取る、または型 1 に「逆」でも |R_C30| < stay_G(30)/4 なら型 1 の分岐。P-READ に「仕組みどおり（R_A30 = G_A30・R_C30 ≈ 0）」の組。
  - 自信: 中
- [major] 3 型 3 は仕組みの予測に反する形なのに「支えない」と書かず推測の形で仕組みを残す。型 1 と非対称（169・201・198・170 行）
  - 理由: 作りの確かめ (ii) で C30 の従属が A30 より大きいと確かめたうえで、得が A30 と同じ程度まで縮むなら、得は記号の数に従う。仕組みの特定の予測（φ ≈ 1）が外れた形。それなのに型なしと同じ書き方。
  - 解消: 型 3 の名と置き換え文を「記号の数で同じ程度に縮み、仕組みの予測（記号の数をそろえても差が残る）を支えない形」に。推測の文は「〜と推測したが、この試験は支えなかった」に。
  - 自信: 高
- [minor] 4 句の置き方の規則が Discussion の第 1 段落の最初の文（平滑した主の結果）と食い違う（17・197 行・main.tex 331 行の最初の文）。解消: Discussion では句を置き換える文そのものの頭に入れる例外を明記。自信: 高
- [minor] 5 "We have not checked this in other domains." の "this" が指すものを失う（197 行）。解消: 残す文を型ごとに決めるか削ると決める。自信: 中
- [minor] 6 1 人抜きの分母 17 と φ の書き手の集合が合わない（93・180 行）。解消: 分母をその量の書き手の数 m とし、境を ceil(12m/17) などで。自信: 中
- [nit] R_ar3 の語をまとめる順（τ が先かセルが先か）が無い（153 行）。解消: 「セルごとに τ を合わせ、次に 2 セルを合わせる」。P-READ に。自信: 高
- [nit] 型 1 の英訳の置き換え文が内部の語「列 C」に依る（198 行）。解消: 英訳では「記号の数をそろえた 1 秒の歩みの連続した区間」と書く。自信: 中

## 特に見てほしいことへの答え
- (1) どの型でも言えるのは、平滑を外した記号の上での、歩み（3 成分の束）と構造の比べの間の形だけ。「重なり」の部分は言い方の限り (2) によりどの結果からも言えない。後半の「本人の当てはめが運ぶ」は既に支えられないと分かっている（175 行）。型 1 でも Discussion の文は「形が合う」以上にならず妥当。ただし指摘 1・2 で型 1 は偽陽性にも偽陰性にもなりうる。
- (2) 型ごとの文はほぼ固定。残るのは指摘 3・5・4。
- (3) s = 30 の記号の数が既知なので τ = 10,000 での床も見込めたが、その見込みは開示されておらず、型 1 の R の条件が通りやすい向きに働く（指摘 1）。

## 5. 総合: major
- 型 1 の R の条件は s = 30 の記号の数では τ = 10,000 でも床に張りつき、比べも G と非対称。
- 仕組みが R_A30 に何を予測するかが導かれず、仕組みどおりの結果が「逆」として型 2′ に落ちうる。
- 型 3 の書き方が型 1 と非対称。どれも文の直しで閉じられ、計画の立て直しは要らない。

## 6. 読めなかった範囲と注入の疑い
- 読んでいない: SEED・variants.py・kit README・S13 scripts・S13 と tau-extend の conditions.md・supplement.tex・main.tex 325〜342 行以外（136・223 行は grep で場所だけ）・notes.md の grep 以外・接地の文献の一部。N は推定。
- 注入の疑い: 無い。tmp/sources/ に依頼文が挙げていない aalbers.txt があることが grep に出た（中身は読んでいない）。
