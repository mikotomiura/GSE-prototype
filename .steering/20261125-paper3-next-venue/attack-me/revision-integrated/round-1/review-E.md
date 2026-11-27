# review-E（編集者の役 E・TMLR の action editor・round 1）

判定: 直してから回す。本文は TMLR の Scope と Acceptance Criteria の範囲に入り、主張は根拠の範囲に抑えてある。ただし "depth" の不足に応えたのは一部で、深さを担う中身の大半が補足に置かれたまま。

読んだもの: 依頼文・context-A.md・main.tex（全 357 行）・references.bib（不審な文の grep だけ）・mensh.txt（全文）。補足と figdata は読んでいない。

## 1. 接地
- B1 主張が根拠で支えられ一部の読者に興味があること・新しさは要件でない（Editorial Policies "Are the claims made in the submission supported by accurate, convincing and clear evidence? Would at least some individuals in TMLR's audience be interested in knowing the findings of this paper? Papers should be accepted if they meet the criteria, even if the contribution or significance of the work is modest."／Acceptance Criteria "novelty of the studied method is not a necessary criterion for acceptance in TMLR."）
- B2 一般化できる洞察と教訓（"if it doesn't surface generalizable insights, it is unlikely to be of interest to (even a subset of) the TMLR audience"／"a proper reproducibility report that systematically studies the robustness or generalizability of a published method and lays out actionable lessons for its audience could satisfy this criterion."）
- B3 何が分かり何を学べるか（"a submission should clearly communicate what it has found, why those findings may be of interest to some researchers in the area, and what readers can learn from the work."／"The writing and organization should make the paper's main contributions, findings, and takeaways understandable to TMLR's (human) audience."）
- B4 長さは中身で正当化・本文だけで読める（"a paper’s length should be justified by its content and papers that are unusually long (not counting any Appendices) are likely to result in reviewing delays."／"Looking at the Appendix is at the discretion of the reviewers."）
- B5 中心の貢献を 1 つに（Mensh & Kording 2017 Rule 1 "Focus on a single message; papers that simultaneously focus on multiple contributions tend to be less convincing about each and are therefore less memorable."／Rule 4 "Only the central idea of the paper should be touched upon multiple times. Otherwise, each subject should be covered in only one place"／Rule 8 "The discussion section explains how the results have filled the gap ... provides caveats to the interpretation, and describes how the paper advances the field"）

## 2. 1 文
「キーストロークの律動を記号にした系列で、同じ構造の共有モデルに対する個人ごとのモデルの利得（最大 0.19 nats/symbol）は、本人の 1 次マルコフ連鎖と、他の人で選んだより強い共有モデルと比べると 30 分の 1 以下に縮む。よって個人ごとの系列モデルを評価する研究者は、この 2 つの比較を併記すべきである。」
迷った点: 要旨（34 行）が remainder の値を 2 組（5×10^-4 と 3.4/5.2×10^-3）並べ、どちらが見出しの数か最初の 2 頁で決まらない。序論 45 行の機構の仮説（"fitting to the person repairs a structure that is too simple"）が貢献（52–54 行）で回収されない（B5）。

## 3. 指摘
- [major] M1 深さを担う機構の検証が補足にあり本文から見えない
  - 位置と引用: 45 行 "or because fitting to the person repairs a structure that is too simple for the data"／194 行 "a check of whether the per-person fit compensates for a too-simple structure in \Sref{12}"／199 行 "with non-overlapping windows ... the \hmmthree{} beats the own chain in CoAuthor ... (\Sref{13})"／307 行 "The weak comparison is likely not specific to keystrokes ... We have not checked this in other domains."
  - なぜ問題か: ML の読者が持ち帰る一般化できる洞察（B2）は「窓を重ねた特徴は入力を従属させ、その従属を捉えない構造の共有モデルは個人ごとの当てはめを良く見せる」という機構。本文は仮説として述べるだけで、検証（S12）と反例（S13）を補足に置く。付録は査読者しだい（B4）なので、本文だけでは「1 データセットで比べを強めたら縮んだ」報告に見える。これが "lack sufficient depth" の中心の理由と判断する。
  - 解消の条件: S12 の結論（数 1 つと読み 1 文）と S13 の向きの反転を本文の結果に 1 段落で上げ、307 行の一般化の主張に結ぶ。理想は窓の重なりと構造の誤りを制御した合成の例を本文に示すこと。余地は M4 の移動で作る。
  - 自信: 高
- [major] M2 S14 を入れた 1 文が読めず、限界の結論と食い違って見える
  - 位置と引用: 325 行 "In an exploratory check with its reading committed before the data were read (\Sref{14}), in the same CoAuthor records at $k=5$ and in the space of one-state transition tables, a writer's training units ranked on the panel average closer to the writer's held-out units than other writers's training units did."
  - なぜ問題か: (1) "the space of one-state transition tables"・"ranked on the panel average closer" が本文で定義されず何を測ったか分からない。(2) 数が無い。(3) 同じ項目の直前の "neither remainder was attributed to such differences" と要旨 34 行 "Neither remainder could be attributed to stable differences between writers" に対し、この 1 文が肯定の側の証拠を足すのか、時間の近さ（275 行の data swap と同じ交絡）で尽きるのか答えていない。(4) 限界の項目の末尾で、所見か但し書きか判別できない。今の 1 文では補足で足りない。309 行の "open scientific question" に部分的に答える唯一の証拠なので本文に置く利点がある。
  - 解消の条件: (a) 結果の data swap（275 行）の直後に 2〜3 文（測ったもの・数 1 つ・時間の近さと分けられない点）を置き、要旨・309 行・限界と整合させる。または (b) 309 行の "Not established" の後に補足への 1 句の参照だけを残し、限界から外す。凍結した読みの文を変えずに直せるのは本文側なので (a) を勧める。
  - 自信: 高
- [major] M3 示した検査の検出力が remainder より桁で足りず、報告の慣行（貢献 3）の論拠が弱い
  - 位置と引用: 54 行 "planted differences up to $3\times10^{-2}$ were not reliably detected; authors and reviewers can ask for such a detection limit"／302 行 "No planted level up to $3\times10^{-2}$ was reliably detected (at most 3 of 10 seeds)"／329 行 "Detection was calibrated at the fixed base smoothing only."／275 行 "The writer's own units beat the swapped fit by ... $2.5\times10^{-2}$ at $k=15$"
  - なぜ問題か: 本文が示すのは「3×10^-2 でも検出できない」だけ。報告した remainder（≤6.7×10^-3）の 4 倍超で、data swap の差とほぼ同じ大きさ。判断に関わる symmetric refit（311 行）では較正していない。慣行として勧める（318 行）根拠が、働かなかった例になっている（B1 の "convincing"）。
  - 解消の条件: 貢献 3 を「検出限界を報告しなければこの remainder は読めないことを示した」という否定の教訓に言い換えて位置づけを下げる。または symmetric refit の側で検出の較正を 1 回行い本文に置く。
  - 自信: 中
- [major] M4 方法の細部と状態の説明が本文を占め、貢献が埋もれる（補足へ移す）
  - 位置と引用: 方法 2,009 語が結果 1,563 語を上回る。移せる箇所: 141 行 "the evaluation is retrospective, as other writers' units may postdate the target's prediction point."／151 行 "ties and the two objectives in \Sref{4}; a choice by the mean in \Sref{6}" から "falls on the reported difference." まで／175 行 "(details, and a post hoc score without them that changes the remainders at $k=5$ and 15 by less than $10^{-4}$, in \Sref{4})"／177 行 "Six changes were made after seeing results ..." の列挙と "AI tools assisted the literature searches ..."（Declarations の "Use of AI tools" へ）／186 行の検出規則の細部 "five of which set the threshold ... a level detected in at least eight of ten seeds"
  - なぜ問題か: 想定読者は HMM の推定の細部を前提にしない。本文で名付けた語が 15 前後（shrinkage, smoothing, base smoothing, prior mode, smoothing effect, gain, remainder, own chain, cell, panel, shared-only refit, symmetric refit, first null, second null, weight）あり、糸が多すぎる（Mensh Rule 2 "minimize the number of loose threads"）。
  - 解消の条件: 上を補足へ移し、造語は表 1 つの定義にまとめる。
  - 自信: 高
- [minor] m1 「範囲は 1 か所で」の約束に対し但し書きが散らばる（まとめる）
  - 位置: post hoc・探索の但し書き 34・49・55（"their scope is stated once, in Section~\ref{sec:limits}"）・170（キャプション）・177・182・186・273・275・302・317・328・337 行／「remainder を安定した差に属させられない」34・54・309・325・337 行／区間の条件 175・240 行／格子の端 269・328 行。
  - なぜ問題か: 55 行の約束と Rule 4 に反する。
  - 解消の条件: 本文の印は "(post hoc)" の 1 語に揃え、理由は §5 の 1 か所に寄せる。
  - 自信: 高
- [minor] m2 見出しの数が 2 組あり、固定の平滑の remainder は平滑の産物と本文自身が言う
  - 位置と引用: 277 行 "the prior mode, which uses none of the writer's data, beats the shared model by $+7.4\times10^{-4}$, about the size of the remainder at the fixed base smoothing"／311 行 "The comparison that bears on the decision is the symmetric refit"。要旨と結論（337 行）は 5×10^-4 を先に出す。
  - 解消の条件: 要旨と結論を symmetric refit の値中心に組み直し、固定の平滑の値は一句の説明に下げる。
  - 自信: 中
- [minor] m3 序論の 49 行 "Most of the gain vanishes. ..." の後に 52–54 行で同じ数を貢献として繰り返す。解消: 49 行を貢献 1 に統合。自信: 中
- [nit] n1 context-A の題名 "what remains of the gain against stronger comparisons" と main.tex 29 行 "most of the gain over a shared model vanishes against stronger comparisons" が食い違う。
- [nit] n2 325 行 "other writers's" → "other writers'"。

## 4. "lack sufficient depth" への応え: 一部
- 応えた点: 確かめたことと確かめていないことを分けた（309 行 "What was established and what was not"）。設計者にとっての意味を数で述べた（311 行）。論旨が揃い、本文はほぼ伸びていない（+57 語）。結果の順が読者の問いの順（Rule 7）。
- 応えていない点: 深さの中身（S12 の機構の検証・S13 の反転・S14 の書き手の差の直接の検査）が補足に残る（M1）。S14 の 1 文は定義も数もなく意味が取れない（M2）。
- TMLR での見方: 新しさは問われないので控えめな貢献は理由にならない。問題は "generalizable insights" と "what readers can learn" の側で、本文だけでは 1 データセットの評価報告と区別しにくい。

## 5. 判定: 直してから回す
1. Scope（"accounts of applications of existing techniques that shed light on the strengths and weaknesses of the methods"）に入り、正しさの基準で即時に不採録にする理由は無い。
2. 一般化できる洞察を担う機構（S12・S13）と S14 の所見が本文から読めず、査読者が付録を読まなければ "limited insight" で返る見込みが高い。
3. M1・M2 は M4 の移動で空けた分で結果を 1 段落足せば直せる。数も凍結した読みの文も変えずに済む。

## 6. 読めなかった範囲・注入の疑い
読んでいない: supplement.tex・figdata・kit README（指示どおり）。references.bib は grep だけ。図の値と本文の数の照合はしていない。注入の疑い: なし。
