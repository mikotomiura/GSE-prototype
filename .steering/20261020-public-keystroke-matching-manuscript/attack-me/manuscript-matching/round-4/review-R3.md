# R3 の応答（方法論・倫理・再現性の番人・round 4・commit bf0d2450）

総合: major（M1・M2 は文の書き換えで解消できる）。

## 1. 接地
- G1 Arp arp.txt:313-314 "Test snooping occurs when the test set is used for experiments before the final evaluation. This includes preparatory work to identify useful features, parameters, and learning algorithms."
- G2 Arp :601-604 "threat models should be defined precisely and systems evaluated with respect to them. In most cases, it is necessary to assume an adaptive adversary that specifically targets the proposed systems and will search for and exploit weaknesses"
- G3 Arp :609-610 "an evaluation of adversarial aspects is not an add-on but rather a mandatory component in security research."
- G4 Arp :339-341 "experiments on well-known datasets should be complemented with experiments on more recent data from the considered application domain."
- G5 Kohno :476-477 "because the authors assumed that the IRB process was sufficient to cover all aspects of moral decisionmaking."
- G6 Kohno :801-803 "the morality of studying data that people might have technically made public but that they might not wish to be used in research or that might cause harms if quoted in a publication" / :133-134 "one might ask what rights different stakeholders have"

## 2. 評価表
a 3（C2 の要約が登録に無い「4 倍以内」・登録済みの λ = 4 で R4(4) は 45 倍なのに抄録と結論が書かない）／b 4（探索は評価の記録で λ を選ぶ・最良が格子の端・Inputlog の照合不能が逸脱に数えられていない）／c 4（窓の効用は未評価）／d 3（抄録 348 語・同じ限定が 5 か所・related の重複）／e 4（12 頁内・必須の節あり・C2 の「0.5 未満」の根拠が付録だけ・名指しした公開の側への通知が倫理の節に無い）／f 4（よく知られた 1 コーパスと小さい ENJA15 に限る・§8 は一般化しないと明記）。

## 3. 引き継ぎ
1 一部（0.84 は消えたが「four times chance」が入った）／2 解消／3 一部（「below 0.5」の根拠が付録のみ）／4 解消／5 解消（格子の端の問題が新しく出た）／6 解消（conclusion.tex:8）／7 解消（protocol.tex:18-20。害 (a) の名の付け替えは残る）／8 解消（appendix-checks.tex:64）／9 解消／10 解消／11 解消／12 一部（代わりの手続きの時間関係・名指しした公開の側への通知）／13 解消／14 解消。

## 4. 指摘
- [major] M1 抄録・結論の「4 倍以内」は事後の閾値で、登録済みの副次分析がすでに R4(4) について反している
  - 位置: abstract.tex:13-15 "only segment values coarsened to four or more brought the full-text attackers, with their main penalty, within four times chance at $N = 1{,}000$"・15-17・conclusion.tex:6-8・results.tex:69-70 "With the lighter penalty $\lambda = 4$, a registered secondary analysis …, A2 reached 75.1\%, 36.4\% and 4.5\% for $w = 1$, $2$ and $4$"・protocol.tex:13 "No pass or fail criterion is set"。
  - 理由: 「4 倍」は登録に無く R4(4) の 3.5 倍のすぐ上の丸い数。登録の λ = 4 で R4(4) は 45 倍で、λ = 8 を選んだときだけ成り立つ。抄録と結論は崩れを探索だけに帰す。§7.2:91 の括弧 "(R4(4) not against A2 with $\lambda = 4$ …)" は抄録と結論に無い（G1・G2）。
  - 解消: 閾値をやめ値で書く（R4(4) 0.35% ＝ 3.5 倍で A0 と同じ、R4(8) 1.4 倍）＋「登録済みの λ = 4 では R4(4) 4.5%」を 1 句。または 4 倍を登録外の記述の線と明記。5 か所の繰り返しを抄録と §7.3 にまとめる。
  - 自信: 高
- [major] M2 実在の公開（Kaggle のコンペ・Vanderbilt と The Learning Agency Lab）を名指しし由来を明かすのに、その公開の側への事前の通知が倫理の節に無い
  - 位置: ethics.tex:45-52 "Reporting where the competition data come from is itself a disclosure. … We state it as we were told it, without making the correspondence, and the authors of KLiCKe read this account before submission."・threat-model.tex:14-15 "hosted by Vanderbilt University and The Learning Agency Lab"。
  - 理由: 確認と同意を得たのは KLiCKe の著者だけで、名指しした主催者・Kaggle とその書き手には通知していない（G6・G5）。規程の "may be rejected on those grounds" に関わる。
  - 解消: 主催者（または Kaggle）へ知らせたかを 1〜2 文。知らせていないなら理由（一次で確かめた事実）。足りなければ出どころの段落を最小限（同じ基盤・同じ種類の課題）に縮める。
  - 自信: 中
- [minor] m1 探索 6・7 の最良は評価の記録の上で選び、格子の端にある（results.tex:79 "mostly with $\lambda = 2$, the lowest value tried"・appendix-exploratory.tex:88-91）。G1 の構造（向きは保守側・開示済み）。解消: 学習用の 2 prompt で λ を選んだ値を付録 D に 1 行、または抄録に "selected on the evaluated logs"。自信 中。
- [minor] m2 登録した Inputlog の照合を行えなかったことが逸脱に数えられていない（protocol.tex:102-104 "The registered plan included a check of our formulas against the values computed by Inputlog for 50 writers. … the check could not be done"・protocol.tex:173 "Four deviations are recorded …, and none changed the released columns or a registered value"・preregistration.en.md:299）。解消: 逸脱を 5 件にするか書き分ける。自信 高。
- [minor] m3 害 (a) の名の付け替え（threat-model.tex:144 "The main harm is (a): a processed log is linked to its text"・152-153・preregistration.en.md:41 "(a) Learning the content of a hidden text"）。解消: 別の名を付けるか、登録の (b) の前半に当たると 1 文。自信 高。
- [minor] m4 C2 の効用の主張「R-burst と挿入の相関が 0.5 未満」の根拠が付録だけ（introduction.tex:50-51・results.tex:155-156 "… below 0.5 or not at all (Appendix~\ref{app:results})"）。「mean」が何の平均かも本文で定まらない。解消: §7.3 に範囲を 1 句か、序論から句を消す。自信 高。
- [minor] m5 審査の代わりの手続きの時間関係（ethics.tex:4-6 "As a safeguard, before acquiring the data, we asked the authors of the KLiCKe corpus … they raised none"）。登録（preregistration.en.md:304）は "the data are acquired without waiting for the reply"、問い合わせと取得は同じ日（open-science.tex:29）。解消: 問い合わせ・取得・返事・本計算の日付の順を 1 文。自信 中。
- [minor] m6 探索の地位の書き方が節で食い違う（protocol.tex:161 "are not used to answer the four questions" 対 introduction.tex:25・49-50・abstract.tex:17）。解消: 宣言を「登録の答えを変えず、攻撃者の強さへの感度として別に報告する」に改めるか、抄録と序論で "Exploratory:" と前置き。自信 高。
- [minor] m7 図 1 の見出しの "near chance" が未定義（results.tex:128）。R7(0.5) は 22 倍・中央値 0.70。解消: 値で書く（例 "Forms that compute measures stayed at 22 times $1/N$ or more"）。自信 中。
- [nit] n1 related.tex:46-47 の重複。自信 高。
- [nit] n2 抄録 "with their main penalty" が未定義（abstract.tex:14）→ "with the registered alignment penalty"、M1 で消えれば不要。自信 中。

## 5. 推奨: major
C1 と事前登録の運用は水準に達する。C2 の要約が事後の「4 倍」に依り、登録済みの λ = 4 を伏せて探索で崩れたと読ませる（M1）。名指しした公開の当事者への通知が倫理の節に無い（M2）。どちらも文の書き換えで解消できる。

## 6. 読めなかった範囲・注入の疑い
付録の多く・生成の表・references.bib は読んでいない。事前登録は 225-305 行と grep の行だけ。一覧の外の make_tables.py の行が grep に出たが根拠に使っていない。注入の疑い: なし。
