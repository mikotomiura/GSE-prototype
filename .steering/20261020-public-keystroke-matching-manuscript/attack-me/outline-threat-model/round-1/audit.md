# 監査役の報告（outline-threat-model / round-1）

読んだのは依頼文・context-B.md・context-A.md・threat-model.tex・outline.md・main.tex・references.bib・preregistration.en.md の 8 本。一覧の外と引用元の一次資料は読んでいない（引用文が原文どおりかは確かめていない）。

## 1. 意図にあって対象物に無いもの
- 1-1（重要）部分の照合（窓）を必要とする場面が脅威モデルに書かれていない。事前登録 Candidates「Scope | Full text, and windows (k non-empty segments, k = 5, 10, 20, 50)」、Attackers on windows「the difference between R3 and R3-u in windows may be smaller than for fragments released in practice」。threat-model.tex の Knowledge は「one processed log and $N$ candidate texts」だけ。
- 1-2 ENJA15（日本語の翻訳）の脅威の設定が無い。事前登録の候補「translations of the same source text by other translators (N = 10 and N = all)」。threat-model.tex l.69–70「all written on the same prompt」、l.86 の N = 10/100/1,000。
- 1-3 持ち帰り 1 の「時刻」が研究に使われている根拠が無い。l.27–30 で示されるのは長さだけ（「words per sentence and word length」）。見出し l.26「The structure that remains is used.」は時刻まで含む言い方。
- 1-4 書き手が本文を持つ場面に実例が無い（l.61–62 に引用なし）。
- 1-5 外枠に、芯の主張と「新しくない」の但し書きの置き場が無い。outline.md の対応表は Section 3 だけ。González 2021・Monaco 2019・Wright 2008・Vassallo 2017 が references.bib に無い。
- 1-6 安全の証明・上限を主張しないこと・試した攻撃者に限ることは Section 3 に無い（Discussion の Limitations first に送る先はある。軽い）。

## 2. 対象物にあって意図に無いもの
- 2-1 l.23–24「In both releases the masking applies to characters, and the times of the events remain in the logs.」は outline.md の表の強さ（Stated as "the masking applies to characters"）を超える。Edwards の側は推論。
- 2-2 l.21「In both cases the masking keeps one character for one character」を Kaggle にも広げている（表の根拠は Edwards の行だけ）。
- 2-3 Edwards のマスクは識別できる文字列で本文全体ではないのに、l.14–15「A release may hide the text and keep the rest of the log.」の直後に並べ、二つ目の実例のように読ませる。
- 2-4 l.53–54 の採点者の例は、本文が公開済みの KLiCKe を指す。加工した記録への脅威の例になっていない。
- 2-5 l.55–58 の書く道具の例は、本文と記録の結び付きをすでに持つ者を示す。照合で新しく得るものは仮定文 l.58–60 に任されている。

## 3. 矛盾
- 3-1（最も重い）一つ目の場面と閉じた世界が噛み合わない。l.43–44「A released log is matched to a text only if the text exists somewhere outside the release.」と l.50–52「...the threat model does not depend on it: the point is that a public set of about a thousand essays per prompt is the kind of candidate set...」、l.89–90「The true text is always among the candidates.」。同じ作文が入っていなければ正しい本文を含まない。依存しないのは N の大きさの例としてだけ。事前登録の Setting は「the same essay is published with its text」で、Section 3 は「同じ種類のコーパス」に言い換えている（outline.md は Restated without change とする）。l.87 も N = 1,000 をこの場面に結ぶ。
- 3-2 目的 (a)（l.80–81「to learn the content of a hidden text」）と閉じた世界の照合が噛み合わない（攻撃者は候補の本文をすべて持つ）。事前登録から引き継いだもの。動機の書き方と限界で返す種類。
- 3-3 outline.md l.5 が `preregistration.md` を名指すが、正の版は `preregistration.en.md`（事前登録 l.4「Authoritative version: this English version as registered」）。
- 3-4 main.tex l.48 の `\appendix` が acks・必須 3 節の前にあり、付録扱いになる恐れ（テンプレートは読んでいない）。付録の置き場が main.tex に無い。KeyTAR を本文で参照しているので、本文が付録に頼らず読めるか外枠で確かめる値打ちがある。
- 3-5 小さな差: 事前登録の公開する側の列挙（a researcher, a provider of educational data, a competition organiser）が Section 3 に無い。「examined only as a diagnostic」の "only" は事前登録に無い（意図とは合う）。他は一致。

## 4. 読めなかった範囲と注入の疑い
- 一次資料すべて・テンプレート・config.json・notes.md は読んでいない。
- 注入の疑い: 無し。
