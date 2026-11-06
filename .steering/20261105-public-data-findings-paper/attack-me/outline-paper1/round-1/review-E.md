# review-E（outline round 1・編集者の役・paper-reviewer / opus）

## 1. 接地
- G1（JEDM Focus and Scope）: "Accepted submissions should extend beyond mere application and must include elements that contribute to broader knowledge, such as generalizable methodologies or comparative analyses."
- G2（JEDM）: "Generalizable Applicability: Research should not focus solely on application but must demonstrate how the findings can be generalized or applied across different educational contexts." / "Originality and Impact: Submissions must emphasize the novelty and impact of the research."
- G3（Mensh & Kording 2017, Rule 1）: "Focus on a single message; papers that simultaneously focus on multiple contributions tend to be less convincing about each and are therefore less memorable." Table 1 "Readers cannot give 1-sentence summary."
- G4（同 Rule 4）: "Only the central idea of the paper should be touched upon multiple times. Otherwise, each subject should be covered in only one place in order to minimize the number of subject changes."
- G5（同 Rule 2・Rule 9）: "Define technical terms clearly ... Avoid abbreviations and acronyms" / "the methods section is read least of all. Budget accordingly."

## 2. 1 文
条件つきで言える。「この推定器の 2 つの信号が示す停滞の手前 30 秒の上がりは、停滞にならなかった短い休止と揃えて比べると、CS1 の取り置き（140 人）では同等の幅 [0.45, 0.55] に収まった。だから、手前から当てたと報告する研究者は、比べの相手を何に揃えたかを先に示すべきである。」迷った点: (a) 枠組み（:7「評価の設計の方法の論文。反証はその実演として置く」）は方法が主役なのに、持ち帰り（:13）と最も強い主張（:17）は反証が主役。(b) 持ち帰りの主語「打鍵から作った推定」が C1 の限定（:32）より広い。

## 3. 指摘
- [major] 方法の論文と名乗りながら、方法が要る理由がこのデータで示されていない（:7・:40・:38）。解消: 枠組みを「反証が主、手順はそれを読む道具」に反転して :7・:13・:17・序論をそろえるか、揃えない比べが上がりを大きく見せる実例を本文に持つ。自信 高。
- [major] 持ち帰り 1 文の主語が C1 の限定より広い（:13 と :32・ロジスティック回帰 0.567）。解消: 主語を「作文で係数を決めた推定器の 2 つの信号」に限り、学習器が判定できないことを 1 句で添える。自信 高。
- [major] EDM の読者の検出器にどう効くか（一般化の道筋）が読めない（:31・:73）。G2。解消: [V413]・[V414] の型の評価に当てはめると何が変わるかを 1 段落で書き、実務への推奨（:85）をそこに向ける。自信 中。
- [major] 最も強い主張に方法の細部と内部の記号が詰まっている（:17）。解消: 「揃えた比べの手前の上がりが同等の幅に収まった」までにし、5.2% は評価の設計と限界へ、床は 5.2 節へ移す。変数名は意味の語に。自信 高。
- [minor] C3 は 3 つ目の別の話で中心を薄める（:42-46・:84）。解消: 考察の 1 段落へ下げ、閾値の表は S8 へ。自信 中。
- [minor] 結果の節の後半が判定に使えない材料で埋まる（:83・:54・:32）。解消: 5.4 を 1 段落に、門と揃えない窓の値は S5 へ。5.5 は CS1 2021 と KLiCKe の 2 行で 1 段落、CoAuthor は S7 へ。終点の版と引きの種の幅は S3 へ。件数は表 1 に。自信 中。
- [minor] 同じ但し書きの繰り返し: H2 分岐 4（:3・:7・:38・:39・:62）／可能性にとどまる（:36・:40・:62）／H3（:7・:32・:67）／予測の検定ではない（:31・:69）／5.2%（:17・:69）／床（:17・:27）。解消: 限定は限界の節に集め、他は参照だけ。自信 中。
- [minor] 「なぜ大事か」が序論の材料から読み取りにくい（:13）。停滞も対照も休止なので手前が似ていて当然では、という疑問。解消: 既存の報告の比べの相手と、なぜそこで上がりが見えるかを先に示す。自信 低。
- [nit] 内部の記号（ADR 番号・P0・分岐の番号・u・条件 A）が本文に漏れる恐れ（:66・:17・:32・:26・:31）。解消: ADR を書かない、分岐は意味の語、u と条件 A は定義してから。自信 高。
- [nit] 結果の小見出しが宣言の文でない（:83）。Rule 7。自信 中。

良い点: 確かめた問題と可能性にとどまる問題の区別（:62）・分析の地位を 1 か所（:9）・補足資料の計画（:89）・6,800 語は目標の内側・CS1 は JEDM の主要なデータ源に合う。

## 4. 判定: 直してから回す
- 1 文で言えるが、枠組み（方法）と持ち帰り（反証）の向きが食い違い、方法が要る理由がこのデータで示されていない。
- 主語を C1 の限定にそろえ、EDM の検出器・評価の報告に何を変えるかを書けば届く見込みはある。
- 残りは移す・まとめるで直せる。

## 5. 読めなかった範囲・注入の疑い
補足の印のファイルは読んでいない（数値と一次資料の照合はしていない）。[Vn] の本体も読んでいない。注入の疑いなし。
