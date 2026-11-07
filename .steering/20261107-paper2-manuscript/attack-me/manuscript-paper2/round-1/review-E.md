# review-E（manuscript round 1・編集者の役 E の応答・メインが写した）

## 1. 接地
- C1（JEDM）: "Accepted submissions should extend beyond mere application and must include elements that contribute to broader knowledge, such as generalizable methodologies or comparative analyses." / "Submissions must emphasize the novelty and impact of the research."
- C2（JEDM）: "All submissions should present their methodologies and findings in a way that ensures replicability by other researchers. This includes clear descriptions of the data, tools, and procedures used."
- C3（JEDM）: "It is the policy of the journal that no submission, or substantially overlapping submission, be published or be under review elsewhere." / "Upon submission, the editor will verify that the article can be read and is within the scope of the journal." / "Are the presentation, organization and length satisfactory?" / "Are the key words and abstracts/summary informative?"
- C4（Mensh Rule 1）: "Focus on a single message; papers that simultaneously focus on multiple contributions tend to be less convincing about each and are therefore less memorable."
- C5（Mensh Rule 4・8・5）: "Only the central idea of the paper should be touched upon multiple times. Otherwise, each subject should be covered in only one place" / "The discussion section explains how the results have filled the gap that was identified in the introduction, provides caveats to the interpretation, and describes how the paper advances the field" / "the most common mistake with the abstract, which is to talk about results before the reader is ready to understand them."

## 2. 最初の 2 頁から言える 1 文
言える（迷いが 1 つ）。「停滞の検出器の 4 つの選択を 89 通りに変えて 4 つの公開データに当てると、作文の得点との相関の強さ（ある一角では向きも）とデータセット間の率の比は動き、停滞の長さの分散構造は動かなかった。停滞・休止のラベルを使う EDM の研究者が、1 つの定義での点の値ではなく、定義をまたぐ幅を区間つきで報告する手続きを示した。」
迷い: 何が新しいのかを序論 3 段落目の "the diagnostic adds three things" だけで読み取ることになり、3 つのうち 2 つ（区間・θ の 2 系統）は手続きの新しさとして弱い。抄録では読者が何を変えるのかが最後の一文まで出ない。

## 3. 指摘
- [major] 見出しの結果（向きが割れる）が、著者が置いた水準（W=15 s）と自分の検出器だけに依る。results.tex l.19-20 "The 10 positive definitions all had the shortest window, $W = 15$~s, the level we set at half the default; among the 59 definitions without it, none was positive."・表 2 "(we found no prior use of a 15-s window)"・抄録 "across defensible definitions"。解消: 看板を強さの動きに置き、向きの割れは先例の無い窓に限ると抄録で一度限定するか、W=15 s を defensible と呼ぶ根拠を示す。自信: 高
- [major] 扱う範囲の言い方が検出器の範囲より広い。抄録 "Pauses, stalls and inactivity in keystroke logs are widely used process measures"・序論 "fixed pause thresholds in writing ... between about 250~ms and 10~s"・表 2 "fixed 10, 30~s"。変えたのは窓にもとづく 1 つの検出器の族だけで、固定の閾値も作文の普通の範囲をほぼ外れる。解消: 抄録と序論 1 段落目で対象を「窓にもとづく停滞の検出器」と限定するか、普通の IKI の閾値を含めない理由を 1 文。自信: 高
- [major] companion study との重複と依存が本文で説明されていない。methods.tex l.161-163 "The baseline definition, the conversion, the estimator and the opened holdouts are shared with the companion study ... (S9)."。観測区間の定義（"the spans in which the estimator, re-run on the recorded stream, wrote its per-second rows"）が companion の推定器に依り、この原稿だけでは再現できない。二重盲検なら自己引用の扱いも。解消: 共有するもの・しないもの・問いの違いを本文の短い 1 段落に移す。送付状で提示。観測区間を推定器なしで読める形で書く。自信: 高
- [major] 新しさの主張が弱く、EDM の何が変わるかが示されていない。序論 "it varies the way keystroke events are cut into stalls ...; it attaches a writer-level interval ...; and it separates two families of thresholds"・考察 "That such definitional spread would corrupt the decision of when to intervene ... are possibilities we did not test."。解消: 新しさを 1 つに絞る（候補: 事象の切り方そのものを変える）。結論が逆になる具体例（CS1 とエッセイの率の比較の逆転）を序論の看板の近くに。自信: 中
- [major] 抄録が読者の準備の前に結果を出す。未定義の語・文の途中の括弧の但し書き・4 つの結論と探索がすべて入る。解消: 看板の結論 1 つと「動いたもの／動かなかったもの」を 1 文ずつ。過分散・長さ・速度は名前だけか外す。但し書きを文の途中から外す。自信: 高
- [minor] 地位の印 [P][A][E][D] と §3.5 の「三つの変更」が流れを止める。解消: 地位の一覧は表にして補足へ。本文では結論ごとに 1 回。三つの変更は限界の節へ。自信: 中
- [minor] 繰り返し: 「割合は 89 定義について」4 回（抄録・序論・方法・限界）／速度の調整が探索 7 回（抄録・方法 2・結果の見出し・図のキャプション・考察 2）／抑制を検定していない 4 回（関連研究・結果・考察 2）／原因を特定しない 2 回／詰まりの判定ではない 2 回／W=15 s に先例なし 3 回／CS1 2021 の 31 人 3 回／提言 4 か所／序論の得点の段落と直後の箇条 1 つ目が同じ。解消: 但し書きは限界に 1 回、他は参照。序論の段落は箇条にまとめる。自信: 高
- [minor] 本文に置かなくてよい細部: 観測区間の手順・参照実装の再現・REML の 3 つの最適化と件数の分解・θ の推定誤差・床効果と課題文の中央値・速度の調整（2 文と図に絞れる）・考察の 63 組のうち 11（考察に新しい結果）。分量 4,848 語は JEDM として短めで問題は長さではない。自信: 中
- [minor] 過分散と長さの分解が「誰の何を変えるか」に結びついていない。φ の 1.5 は著者の規則で重みが分からない。解消: 序論で 1 文ずつ動機を書くか、「動かない側の対照」として 1 節にまとめる。自信: 中
- [minor] 考察の「より大きく動いた」は違う量・違う格子の比べで言いすぎ。解消: 「向きまで変わった点が違う」という質の比較に。自信: 中
- [nit] JEDM の方針では研究での AI の使用は Methodology に書く（"this will typically be described in a section called Methodology"）。分析のスクリプトを書かせたことを方法にも 1 文。DOI を入れる。自信: 中

## 4. 判定
直してから回す。範囲内で方法と結果の段落は査読に耐える。ただし看板の「向きが割れる」が先例の無い W=15 s だけから出ることと、範囲の言い方が検出器より広いことが最初の 2 頁で信頼を落とす。companion との重複の説明が補足にしか無く、本文だけで再現できない。

## 5. 読めなかった範囲・注入
読んでいない: jedm_submissions.txt（抜粋で代えた）・references.bib・PDF 4〜15 頁の画像・補足の印のファイル。注入の疑い: なし。
