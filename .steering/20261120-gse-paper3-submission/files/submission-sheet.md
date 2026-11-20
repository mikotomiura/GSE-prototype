# 論文 3 の投稿画面に貼る文（UMUAI・Editorial Manager）

- 記事の種類: Original research（画面の選択肢の名に合わせる）
- 題: Per-person sequence models of keystroke behaviour: what remains of the gain against stronger comparisons
- 短い題（running title）: Per-person sequence models of keystroke behaviour
- 著者: Mikoto Miura（責任著者・単著）
- 所属: Independent Researcher, Hiroshima, Japan（規程: 所属のない著者は市と国だけを載せる）
- ORCID: 0009-0000-4196-0508
- メール: 登録のアカウントのまま
- キーワード（6）: personalization; user modelling; keystroke logs; hidden Markov models; evaluation protocol; baselines

## 要旨（248 語・空白区切り・数式は空白なしで 1 語）

Whether a per-person model looks worthwhile depends on the comparison. Exploring public co-writing (CoAuthor) and programming (CS1) keystroke data, coded per second over overlapping 30-second windows, we scored models on each writer's later symbols. In CoAuthor, a per-writer three-state hidden Markov model beats a shared model of the same structure by up to 0.19 nats per symbol but loses to the writer's own first-order Markov chain. With a stronger structure and shrinkage chosen on other writers, about 5×10^-4 remains at five and fifteen training sessions in the 15-session panel at the fixed base smoothing, no more than the shared model improves when its smoothing is removed; synthetic writers without per-person differences left a similar remainder relative to that improvement (ratio not prespecified). When the shared model's chosen smoothing is applied to both models with the structure fixed, 3.4×10^-3 and 5.2×10^-3 remain; this bears on a designer's decision but was not separated from closeness in time or the amount of data, nor checked synthetically. Neither value shows stable per-person differences; under the post hoc null at the fixed base smoothing, planted differences up to 3×10^-2 were not reliably detected. The synthetic writers, both-sides smoothing and wider grids came after seeing results. In CS1, mostly pauses, the shared model is chosen at the fixed base smoothing. For overlapping-window symbols, group-level decisions on per-person modelling should compare with both baselines, choose structure and shrinkage on other people, and apply the shared model's chosen smoothing to both models (tried for one structure).

## 宣言の欄（規程: Author Contribution と Competing Interest は画面から入れたものだけが使われる）

- Funding: No funding was received for conducting this study.
- Competing interests: The author declares no competing interests.
- Author contributions: Mikoto Miura is the sole author and carried out the conception, analysis and writing, and approved the final manuscript.
- Ethics: Not applicable (secondary analysis of public, de-identified datasets; no new data were collected from people).
- Data availability: 原稿の Declarations の文をそのまま貼る（CS1 の扱いの判断待ち）。
- Code availability: https://github.com/mikotomiura/per-person-keystroke-models ・ https://doi.org/10.5281/zenodo.24395569
- 推薦・除外する査読者: 任意（研究者が決める）

## 上げるファイル

| 種類（画面の名に合わせる） | ファイル |
|---|---|
| Cover letter | cover-letter.pdf |
| Manuscript（PDF） | manuscript.pdf |
| LaTeX source files | manuscript-source.zip（main.tex・main.bbl・references.bib・sn-jnl.cls・sn-basic.bst・figdata/。zip だけから組めることを確かめた） |
| Supplementary material（Online Resource 1） | ESM_1.pdf |

CSV などの機械向けのファイルは単独で上げない（DOI で示す）。Submit の前に、合成された校正刷りの全頁（特に ESM_1 の部分）を研究者が見る。
