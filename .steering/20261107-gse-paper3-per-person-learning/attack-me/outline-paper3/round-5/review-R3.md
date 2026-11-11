# R3（UMUAI・方法論と再現性）round 5・commit afc96bfa

## 1. 接地
- G1 Varma & Simon 2006 "Since selection of classifier parameters that minimize CV error estimates is a kind of training, it should be included as part of the classifier training algorithm."
- G2 同 "requires that all steps of the algorithm, including classifier parameter tuning, be repeated in each CV loop. A nested CV procedure provides an almost unbiased estimate of the true error."
- G3 同 "Over-optimistic estimates of error close to zero are obtained, even for data where there is no real difference between the two classes."・"Assume that classifier parameter α can only take discrete values ... and that the true prediction error E is independent of the value of the parameter."
- G4 同 "the generalization error for the resulting classifier should be estimated correctly. This can be accomplished by a large validation set that is independent of data used for parameter tuning."
- G5 Liu & Meng 2016（liumeng.txt 1724–1732）"we predict each individual's response using the remaining n − 1 individuals ... our inference will be more robust. The downside is that we base our accuracy assessment on observed prediction errors for individuals who do not necessarily match the target's background —our inference will be less relevant."
- G6 同（89–92）"our inferences can be hurt either by too much matching (not robust) or too little matching (not relevant)."

## 2. 引き継ぎの判定
A 解消（3.3 30 行・4.4 48 行。主の目的の理由は N5）／B 解消（読み方の非対称は N2）／C 一部（64 行は入ったが 48 行 "This shows that the shared model's smoothing, not the person's data, accounts for most of the remainder" が残る・N1）／D 解消（書き方のずれは N11）／E 解消／F 解消（合計のずれは N10）／G 一部（52 行に再現の文・N4）／H 解消／I 一部（Open items）。

## 3. 評価表
a 3（4.4 の "accounts for" が限界の事実と矛盾。最頻値に勝たないは下限より 1 桁以上小さい差の符号から）／b 3（入れ子でない・合成の水準が粗い・主の目的の理由が無い）／c 4（尤度比の段落が読み違いを誘う）／d 4（予算の合計 6,800 と "Total 7,000"）／e 4（データの声明にリンクか引用が無い）／f 4（5 節の Liu & Meng の帰属）。

## 4. 指摘
- [major] N1 4.4 が残りの由来を分解したと主張するが、その手法は合成で効かないと限界に書いてある（48 行・47 行 S15 "the decomposition of the remainder applied to synthetic writers (it did not separate a planted difference from none ...)"・62 行 "Comparisons of medians are not per-writer decompositions."）。解消: "is of the same size as the prior mode's advantage over the shared model, which is consistent with smoothing rather than per-person data accounting for the remainder; the decomposition did not separate planted differences in synthetic writers (S15)" のような一致の記述に。自信: 高
- [major] N2 検出の下限より 1〜2 桁小さい差の符号を見出しの結論にし、読み方が非対称（7 行 "does not beat the shared model's prior mode"・48 行 "per-person minus mode is −3.5e-4 to −1.6e-4 ... +5.4e-4 at k = 30 (7 of 9 positive)"・13 行 "with 9 writers we do not read this as a crossover"・64 行 "did not detect differences below 1e-2 (k = 15)"）。4.3 は残りを下限より下として読まないのに、4.4 は同じ桁の符号を「勝たない」と読み、30-session の逆の符号は人数で退ける（G3）。解消: 4.4 の見出しと Take-home を「最頻値との差も検出の下限より下で、15-session では向きが負・30-session の最大の k では正」と同じ物差しで。または最頻値を相手にしたときの陰性対照の幅を示してから符号を読む。自信: 高
- [minor] N3 規模の段落が個人の利得でない残りを尤度比で示す（49 行 "the remainder is about 1.5 to 2.6 nats per 3,600 symbols, a likelihood ratio of about 4 to 13 over an hour of symbols"）。解消: 「検出の下限より下で個人の利得とは示されていない」を 1 文、または尤度比は hmm3 の利得と ar3 対 chain だけに。自信: 中
- [minor] N4 データの声明に再現の主張が残る（52 行 "every reported value can be recomputed from the public data with the code listed under code availability"・75 行・README 75–78 行 "That comparison used the raw datasets and is not part of this kit."）。解消: "the code that produced every reported value is provided" に下げるか、ハッシュを入れてから残す。自信: 高
- [minor] N5 主の目的（他の人の本人 − chain の中央値）の理由が無い（30 行）。use case は予測で、平均の対数尤度が確かめの側にある。解消: 3.3 に理由を 1 文（事前の条件で固めていた等）、または平均の目的で ar3 以外が選ばれたセルがあるかを 4.3 か S9 に。自信: 中
- [minor] N6 推奨する手順は入れ子が前提なのに著者は入れ子にしていない（66 行・49 行 "choose structure and shrinkage on other people"）。解消: 5 節の推奨に「他の書き手の共通モデルからも対象の書き手を外す（入れ子）。本研究では評価単位だけ外した（6 節）」。自信: 中
- [minor] N7 合成の検出の下限の水準が本文から分からない（47 行 "the smallest planted difference detected at this record length was 1e-2 at k = 15 and 3e-2 at k = 5 in CoAuthor, and 1e-3 in CS1 (two seeds per level)"）。解消: 試した水準の並び（1e-3, 3e-3, 1e-2, 3e-2）と、検出した最小と検出しなかった最大の両方。自信: 中
- [minor] N8 データの声明にリンクか引用が無い（52 行 "CoAuthor and CS1 from their public sources"・規程 "including links/citations to publicly archived datasets analysed"）。解消: 引用・URL か DOI・版（CS1 2021 release）を書くと明記。自信: 中
- [nit] N9 5 節の Liu & Meng の帰属（49 行 "a per-person model can be no better than the comparison model allows it to be shown (Liu and Meng 2016)"）が出典の言い方と合わない可能性。解消: 著者自身の主張とし、Liu & Meng は関連性と頑健さの交換として引く。自信: 中
- [nit] N10 予算の合計 6,800 と "Total 7,000"。自信: 高
- [nit] N11 「候補」の書き方（67 行 "it is used as a comparison model, not as a candidate (4.4)"・44 行 "the prior mode as a comparison model and a candidate"・48 行 "Placing the prior mode among the candidates changes little"）。解消: 67 行を「主の選びでは候補に置かず、候補に置いた確かめは S9」。自信: 高

## 5. 総合の推奨: minor
round 4 の major 3 件のうち 2 件は解消、C は一部。残る major 2 件は言い方の問題で新しい計算は要らない（N1・N2）。宣言の再現の文（N4）と推奨の入れ子（N6）は本文の前に直す。

## 6. 読めなかった範囲・注入の疑い
brief・context-A・carryover・outline.md（76 行）・README（85 行）。varma.txt は grep の抜粋、liumeng.txt は 80–119 行と 1710–1740 行。S1〜S15 と規程の原文は読んでいない。注入の疑い: なし。
