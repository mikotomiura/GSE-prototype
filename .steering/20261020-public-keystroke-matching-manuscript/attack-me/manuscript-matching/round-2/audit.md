# audit（意図の監査役・stage: manuscript・round 2・変更箇所だけ）

読んだもの: brief-audit.md、context-B.md、context-A.md、carryover-audit.md、introduction.tex（全文）、threat-model.tex（全文）、ethics.tex（全文）、discussion.tex（全文）、outline.md の 95〜149 行。data.tex・open-science.tex・事前登録は grep で関連語だけ見た。

## 1. 意図にあって対象物に無いもの

1-1. 持ち帰り 1 が一般化した形でどこにも書かれていない。
- 意図（B「持ち帰ってほしいこと」1）: 「加工が本文を守るかは、その後に何が公開されるかに左右される」
- 対象物で近いのは threat-model.tex 108〜110 の "for those essays the masking no longer keeps the log apart from its text, since the text was released later with another log of the same writing." だけ。個々の作文についての条件つきの帰結に限られ、一般の持ち帰りは §3.3・序論・議論（§8.1）のどこにも 1 文として無い。

1-2. 序論の 1 文に持ち帰り 2（確かめていない）が付いていない。
- introduction.tex 19〜20: "The essays of the competition, according to the authors of the KLiCKe corpus, were drawn from that corpus before it was released with its texts (Section~\ref{sec:threat-model:settings})."
- 最初のページだけを読む読者は、確定した事実と受け取りうる。

1-3. 既知の限界「どの作文がどれだけ重なるかは分からない」が、序論と倫理の節で逆向きに読める。
- introduction.tex 19 "The essays of the competition ... were drawn from that corpus"、ethics.tex 26 "the competition data were drawn from it"、44 "the competition data were drawn from KLiCKe"。
- 部分の重なりの可能性は threat-model.tex 107 の "If the hidden essays are among the public KLiCKe essays" の条件だけ。

## 2. 対象物にあって意図に無いもの

2-1. 「同じ書きの別の記録」は聞いた事実を越えている。threat-model.tex 109〜110 "since the text was released later with another log of the same writing."（別の記録か、同じ記録の加工前の版かは聞いていない）

2-2. 「得点も公開されている」は聞いた事実を越えている。threat-model.tex 107〜108 "their texts, logs and scores are already public"（コンペの得点が KLiCKe の得点と同じかは資料に無い）

2-3. 「取った」の限定が節によって落ちている。threat-model.tex 105 "drawn from the KLiCKe corpus before it was released" に対し、ethics.tex 26 "drawn from it"・44 "drawn from KLiCKe"。公開の KLiCKe は選別を経た集合（discussion.tex 21 "logs that did not pass the selection of the KLiCKe release"）。

## 3. 矛盾

3-1.（重要）threat-model.tex 95 "We do not know who held the texts of the competition data." と 同 104〜105 の新しい文が同じ段落で食い違う。

3-2.（重要）ethics.tex 27 "Doing so would test a real release whose participants did not agree to that use"・48〜49 "does not use the release whose participants did not agree to an evaluation of this kind (the competition data)"・33〜34 "the writers of other released logs (including the competition data)" と、8〜11 の KLiCKe の参加者の同意（"used for research purposes by the broader research community"）が、同じ人について並ぶ。照合しない理由を同意の範囲として言い直さないと成り立たない。

3-3. threat-model.tex 108 "matching would show only which records of the two releases correspond" の "only" と、ethics.tex 37〜38 の害の言い方・害 (a) の定義（threat-model.tex 144）の重みがそろわない。

3-4. ethics.tex 41〜44 で、論文が対応を公にすること自体を害として量っていない。35〜37 "If no one misuses the paper, the writers of the two corpora lose nothing new" と言い切っている。

3-5.（軽微）序論の例の置き方が §3.3 の結論（同じ作文の場合は対応だけ）とずれ、照合が新しい害を生む例として読まれうる。

3-6. 事前登録との食い違いは見つからない（事前登録 58 行目・274 行目、outline.md 109・132〜134 行目）。

## 4. 意図の資料だけに関わる注意

- ethics.tex 17〜18 "The corpus authors will receive the paper when it is complete." と、完成の前に原稿を読んでもらう予定とで時期が合わない。
- KLiCKe の著者とコンペの公開者の関係を書かないことで足りるかは、資料からは判断できない。

## 5. 読めなかった範囲と注入の疑い

- 読んでいない: main.tex、references.bib、data.tex と open-science.tex の本文（grep のみ）、outline.md の 1〜94 行と 149 行より後、事前登録の本文（grep のみ）。
- 注入の疑い: なし。
