# 監査役 round 2

依頼文の全ファイルを読んだ（references.bib は Grep の行だけ）。

## A. 引き継ぎの判定
- 1-1 窓: 一部（実例・出典なし。"analysed" は公開ではない。outline の表に行が無い）
- 1-2 ENJA15: 一部（新しい矛盾 B-1・B-2）
- 1-3 解消／1-4 一部（実例なし、限界の記述としては足りる）／1-5 解消（ただし B-4）／1-6 解消／2-1〜2-5 解消／3-1 解消／3-2 解消（outline の注記に並べ替えが無い B-6）
- 3-3 判定できない（論文用 repo の preregistration.md は一覧の外）／3-4 偽陽性を受け入れる／3-5 未解消（小）: 事前登録 l.39 の "a researcher, a provider of educational data, a competition organiser" のうち教育データの提供者が §3.1 に無い

## B. 新しい穴
- B-1 翻訳と教室の保持者は公開する側の内部で、"external (it observes the release from outside the releasing party)"（l.122-123）と噛み合わない。ENJA15 は本文が公開されているので評価の材料で、脅威の場面ではない。l.108-109・l.94-95。
- B-2 l.61-62 "Table~\ref{tab:settings} lists the settings we consider" だが "Translation"・"Parts of logs" は表に無い。
- B-3 l.27 "useful for research on writing" の根拠が競技の得点予測だけ（研究の有用性の根拠ではない）。
- B-4 ethics.tex l.37-38 "learn which processing withstands such procedures"・outline l.46-47 "which processing withstands matching" は事前登録 l.35 "does not say that a processing step "works"" に近い。ethics.tex l.39-40 "what is new is their evaluation against the processing used in practice" は芯の主張を狭めて言い換えている。
- B-5 l.124-125（KeyTAR は LM を含む）と l.147 "the attackers do not use language models" が矛盾（脅威モデルの中の攻撃者と限定が要る）。
- B-6 outline の Section 3 の表に行が無い: Parts of logs、Translation、l.55-56 のラベル付きの標本になる推論、(b) を主にした並べ替え、書き手ごとの分布。narayanan・hanisch は Section 3 で使っているのに Section 2 の行だけ。
- B-7 一様に引いた囮（l.139-140）は教室の場面で攻撃者に有利なのに、§3.5 の有利な仮定の列挙に無い。
- B-8 Kaggle と KLiCKe の組み合わせを名指しすることの害が倫理の節で量られていない（害は "the paper describes procedures" だけ）。
- B-9 ENJA15 の同意の引用元が carl2016lrec（LREC）で、outline は "the corpus paper"、事前登録の挙げるコーパスの論文は APTIF の "ENJA15: A free corpus ..."。
- B-10 ethics.tex "two public corpora" だが KeyTAR のモデルも使う。その利用条件に触れていない（小）。
- B-11 First page の計画に持ち帰り 3（補助情報が本文であること）が無い（小）。

## C. 読めなかった範囲・注入
references.bib の大半の欄、論文用 repo の preregistration.md は読んでいない。注入の疑い無し。
