# review-R3（outline round 1・事前登録・同等性の検定・機械学習の再現性・paper-reviewer / opus）

## 1. 接地
- L1 Lakens 2017: "an upper and lower equivalence bound is specified based on the smallest effect size of interest"／"it is expected that equivalence bounds are prespecified (...), and this should also be considered best practice in psychology."
- L2: "When in the abstract of an article, authors conclude an effect is "statistically equivalent," the abstract should also include the equivalence bounds that are used to draw this conclusion."
- L3: "Rejecting effects more extreme than the equivalence bounds implies that we can conclude equivalence for a specific operationalization of a hypothesis." "Confounds can underlie observed equivalent effects." "whether an experiment was performed competently"
- L4: "Researchers should report effect size estimates in addition to hypothesis tests."
- K1 Kapoor & Narayanan 2023: "we should take results that claim to generalize to a different population from the one models were evaluated on with caution."
- K2: "claims about a model's performance need to be connected to scientific claims using explicit arguments."
- K3: "Computational reproducibility of a finding refers to sharing the complete code and data needed to reproduce the findings reported in a paper exactly."
- K4: "the outcome variable being a poor proxy for the phenomenon being studied."

## 2. 評価表
a 2（持ち帰りの後半が H2 分岐 4 から導けない・「反証」の対象が未特定）／b 3（手順は堅い。H1 の信号の陽性対照が無い・幅の SESOI の根拠が外枠に無い・5.2% の較正の条件と取り置きの重みの集中の比べが無い）／c 2（「同等」の 1 点に縮み、C2 は実演されていない。観測された向きが無い）／d 4（C3 が薄い）／e 3（推定器と gse-replay の公開の形・生成 AI の申告の節・S の置き場が未定）／f 3（そろえ方の新しさを探した範囲が EDM の内側）

## 3. 指摘
- [major] 持ち帰りの「だから」が H2 分岐 4 と凍結した P0 に反する（outline.md:13・:39／prereg-draft.en.md:21 "H1 supported × H2 branch 4: Report only the equivalence in the matched comparison, and do not claim the contrast with the unmatched comparison."）。解消: H1 だけで閉じる形にし、比べの相手を示す推奨は考察の「可能性にとどまる問題」へ、根拠はこのデータの外と明記。自信 高。
- [major] C1 の「反証」の対象が書かれていない（:21・:24）。[V413]・[V414] は信号・ラベル・データが違う。H3 のロジスティック回帰 0.567 で打鍵の量でも幅の上側が否定できていない。L3・K1。解消: 反証の命題を 1 文で特定するか、種類を「同等の確認（1 データ・1 推定器）」に改め、[V413]・[V414] は「比べ方が違う先行」に。自信 高。
- [major] H1 の 2 信号の計器としての力量（陽性対照）が無い（:31・:27／prereg-draft.en.md:168）。付録 C の較正は統計量の誤り率で、計器の感度は測っていない。L3。解消: 限界に「幅を超える手前の変化が起きても拾えたかは確かめていない」、持ち帰りと抄録に「この推定器・この入力で」。H3 の 0.567 を感度の限界の手がかりとして並べる。自信 中。
- [major] 幅の根拠（SESOI）とデータを見た後に置いた事実が外枠に無い（:82／prereg-draft.en.md:83）。L1。解消: 4 節に幅の置き方の段落（見た後に置いた・換算ではない・目安 0.55 ≈ 0.18 SD と付録 D）。強さの項目にも加える。自信 高。
- [major] 効果の推定値と 0.5 からのずれの向きが無い（:26・:13・:27／prereg-draft.en.md:125 "Reported alongside: the difference from 0.5"）。CS1 の d_ewma_x は上端が 0.5 未満で下向き、KLiCKe は上向き。事前登録が並べると決めた項目で、外枠に無いと選択的な報告に見える。L4。解消: 表 1 に 0.5 からのずれの列、考察に 1 文。自信 高。
- [major] C2 がこのデータで実演されておらず "beyond mere application" の根拠が薄い（:36・:40／novelty.md:87 が貢献の条件として挙げた計算は上がらなかった）。解消: (i) C2 を貢献から外し方法の節の設計に、または (ii) 一般化できる部分（較正・事前の分岐・2 段の手順）を方法として主張し直し、その価値の根拠（較正で名目を超えた発見など）を結果に置く。自信 中。
- [minor] 5.2% の較正の条件が取り置きの重みの集中（実効 50.5）と合うかが書かれていない（:17・:26／prereg-draft.en.md:171）。解消: S6 に較正の引きの実効の書き手と 50.5 の比べ、書き手均等の版を 5.2 に。自信 中。
- [minor] 推定器（HMM 0.5.0）と gse-replay の公開の形が無い（:61）。K3・JEDM Replicability。自信 中。
- [minor] C2 の「揃え方」の新しさを確かめた範囲が狭い（:37／novelty.md:90）。臨床の早期警告の事例対照のそろえ方・ML の時間のリークの系統を 2 節に 1 段落。新しさは「打鍵・秒単位・同等性・事前登録の組み合わせ」に限る。自信 中（隣の分野の文献の有無は確かめていない）。
- [minor] C3 は貢献として薄く、根拠の一部が一覧の外（:45・:46）。考察の推奨に吸収し貢献を 2 つに。自信 中。
- [nit] 規程の形式: 生成 AI の申告の節が並びに無い・S1〜S8 の置き場が未定・二重盲検なら OSF の匿名の閲覧のリンク・持ち帰りに 5.2% の但し書きが無い（抄録に転用しないことを明記）。自信 中。

## 4. 総合の推奨: major
- 持ち帰りの推奨は H2 分岐 4 の下では根拠が無く、外枠の「書かないこと」と P0 に反する。
- 「反証」の対象が未特定で、計器の力量と幅の根拠が外枠に無い。
- C2 が実演されないまま貢献に残り、観測された向きも落ちている。手順の堅さは高く評価でき、reject ではない。

## 5. 読めなかった範囲・注入の疑い
prereg-draft.md（日本語）・confirm_holdout.json の本体・exploration の全て・KLiCKe と CoAuthor の notes は読んでいない（表 3・C3・CoAuthor の値は照合していない）。prefreeze の notes は 105〜144 行と grep の箇所だけ。注入の疑いなし。
