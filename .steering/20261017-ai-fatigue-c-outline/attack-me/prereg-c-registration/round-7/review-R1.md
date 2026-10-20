# R1（心理測定と構成概念の妥当性の立場）round 7 の査読：登録版 0.19 の全文

総合: major（直して再査読）。

## 1. 接地
- Elson 2023「Determine procedural and scoring details ahead of time, reporting all deviations as they potentially weaken the strength of conclusions.」
- Elson 2023「Report all of the items, stimuli, instructions, procedural parameters or other measurement characteristics used in a study」
- Elson 2023「They involve a nominal fallacy: that a measure's name tells you about its contents or what it measures」
- Elson 2023「Dropping, adding, and altering items in self-report scales ... occur while researchers not only refer to the same construct, but actually to the same nominal instrument」
- Lintner 2024「COSMIN requires that both experts and target population are involved in content validation for content validity to be considered adequate.」
- Lintner 2024「It was performed by a single author, which might have caused some bias in the scales' quality assessment」
- Lintner 2024「Most studies did not report percentages of missing data and strategies they employed to address missing data, which puts their credibility into question.」

## 2. 評価表
- a 4: C2b を COSMIN の内容的妥当性ではないと明記（GSRR-10・55）。C6a と C7 (iii) は名前の比較と明記。ただし C5 の「signs present but not confirmed」が、報告そのものが同じ標本だと書いた場合にも付く（N2）。
- b 3: 80% の門は prevalence に鈍い（N1）。中心の不一致だけで記録が本体の外へ（N3）。C2b の対象の規則が stem を見ない（N4）。
- c 4: 監査・網・合意できない記録を分けて公開する設計は再利用しやすい。
- d 3: GSRR-33 の 1 項に詰まっている。同じ規則が GSRR-4・33・43・44・46 に重ねて書かれ食い違いが生まれる（N6・N8）。
- e 4: 逐語 1・2 は満たす。逐語 3 の contingency plan が符号化者間の一致が低い場合に無い（N7）。
- f 4: Elson・Lintner・Perrig・Jonaid への位置づけは適切。
- g 3: 感度分析に著者 2 の値が無い（N5）。モデルの指定が別名（N9）。閉じる日が条件つき（N10）。C4f の下書きを開く時点が 3 か所で食い違う（N6）。

## 3. 引き継ぎの判定
1 E5 消えた（ただし付ける値が N2）／2 感度分析 5 前提が無くなった（GSRR-62 は 1〜4・GSRR-10 に外したこと）／3 n < 5 消えた（GSRR-44 の 2・GSRR-65・tables.tex:115）／4 段 1 の入力 消えた（GSRR-34 の書き方と両立・nit）／5 2 度目の改訂 消えた／6 束と取り直し 消えた（call.md:24「up to nine」）／7 GSRR-46 一部（GSRR-4 の表と main.tex に古い言い方・N6）／8 束をまたぐ学び 前提が無くなった（GSRR-65「Author 1 can open the net's answers ...」）／9 2 回目の順 消えた／10 "or boundary" 消えた。

## 4. 新しい指摘
- [major] N1 段 1 の 80% の門は含める記録が少ないと効かない。確かめの標本と合わせて計算する
  - 位置と引用: GSRR-33「Agreement on these 113 records together is computed on the decision (include or exclude, not the code); if it is below 80% ..., author 2 also judges every remaining record」
  - なぜ問題か: 割合の一致は含める記録が少ないほど除外どうしの一致で膨らむ。確かめの標本 60 件は GSRR-39 が適格 1% 前後と見込む。113 件のうち含めるべき 15 件を著者 1 が 10 件落としても一致は約 91% で通る。唯一の分岐なので、効かなければ一人の判断の偏りが残る（Lintner「performed by a single author, which might have caused some bias」）。代価は GSRR-65 に無い。
  - 解消の条件: (a) 53 件だけで計算、(b) どちらかが含めた記録の中での一致も条件に、(c) どちらも採らないなら GSRR-65 に書き kappa とどちらかが含めた件数を並べて報告。
  - 自信: 高
- [major] N2 報告が同じ標本だと書いていても C5 が「not confirmed」になり、報告の問題に数えられる
  - 位置と引用: GSRR-33「If the other record is not among the candidates, is excluded or pending, or belongs to the exploration set, no E5 link is made: the record is coded, and its C5 value is "signs present but not confirmed"」。GSRR-57 の Reporting に「C5 "signs present but not confirmed"」。
  - なぜ問題か: 重なりを正直に書いた研究が「確かめられない」研究と同じ値になり、報告の問題の側に数えられる。感度分析 2 は区別しない。
  - 解消の条件: C5 に「stated by the report, not linked」を足し Reporting から外す、またはその記録を問題の型の分母から外すと書く。
  - 自信: 高
- [major] N3 中心が一致しないだけで、含めると合意した記録が本体の外へ出る
  - 位置と引用: GSRR-33「A record on which they cannot agree is left pending as unresolved: it is not coded, is outside the main set ... Unresolved applies only to whether the record is included and to its centre」
  - なぜ問題か: 中心は SQ1 の分け方にしか使わないのに、RQ1〜RQ5 からも消える。中心で揉めるのは帰属があいまいな研究で、C1・C6c・C7 (ii) に最も関わる記録が選ばれて抜ける。代価は GSRR-65 にも main.tex の限界にも無い。tables.tex:75「records judged boundary ... all of which were assigned to centre A or B」とも合わない。
  - 解消の条件: (a) 中心だけ合意できない記録は本体に入れ、中心を unresolved として SQ1 の表の外に数える、(b) 今の規則なら偏りの向きを GSRR-65 に書き、分けて数え、tables.tex の注を直す。
  - 自信: 高
- [major] N4 C2b の対象は stem を見ないので、L1b の尺度で AI に向いた項目が TASK や OTHER になる
  - 位置と引用: codebook-c2b-en.md Principles「Instructions or stems ... They are not used to decide the type or the target.」、優先の規則「(3) a task or activity, named or not: `TASK`」
  - なぜ問題か: 「After using ChatGPT ...」の stem の下の「I want to avoid it」は、指す先が stem にしか無い。RQ2 の対象で系統的に AI が少なく出る。本符号化の間の改訂は禁じられている。反例集にこの例があるかは確かめていない。
  - 解消の条件: 代名詞や省略で stem の対象を指す項目の規則を書く、またはその代価を codebook と GSRR-65 に書く。
  - 自信: 中
- [minor] N5 感度分析に著者 2 の値が無い。位置: GSRR-62「4. Each of author 1's two passes in place of the reconciled values.」、GSRR-48「the agreed value is the data for those records」。解消: 「5. Author 2's codes in place of the agreed values」を足すか、足さない理由。自信 中。
- [minor] N6 C4f の AI の下書きを開く時点が 3 か所で食い違う。GSRR-4 の表「In each pass, author 1 makes the recalculations or records the signs before opening a draft, and then checks every drafted value」、GSRR-43「opened only after the values of both passes and of the third pass (GSRR-48) are fixed」、main.tex:248–249「opened only after the values of both coding passes are fixed」。協議の前か後かも無い。解消: 揃え、「著者 2 との協議の後に開く」。自信 高。
- [minor] N7 符号化者間の一致が低いときの手当てが無い。GSRR-47「a point of reference, not a stopping rule」。著者 2 は較正に加わらず、練習の準備の基準も無い（逐語 3）。解消: 80% を下回った単位の問題の記述に印、置かないなら明記。自信 中。
- [minor] N8 確かめの標本の E5 記録が本体の RQ4 の件数に入る。GSRR-33「A record of the coverage sample whose full text says it reports the same sample as an additional candidate that is included is excluded with E5」、GSRR-35「An uncoded E5 record is counted in the RQ4 record counts with the set ... of its group's coded record」と GSRR-39「Its records are never part of the main set」。解消: 例外として書く。自信 中。
- [minor] N9 モデルを別名で呼び出す。call.md:8「subagent type `general-purpose`, model `opus`」と GSRR-33「One model identifier is used throughout (`claude-opus-5-5` ...)」。解消: 各回で返った識別子を残し、違えば後継の規則。自信 中。
- [nit] N10 閉じる日: GSRR-33「... waits until the full-text decisions on these records are made」と outline.md:90「included by 31 December 2026」。
- [nit] N11 架空の例のキーを AI で下書きしたことが登録版に無い。findings.md:5「The cases and the key were drafted with an AI assistant (Claude).」、main.tex:255。GSRR-4 は AI の補助を C4f と C5 だけとする。
- [nit] 語の揃え: GSRR-46「Author 1 wrote the earlier narrative review」と GSRR-19・65「Both authors」。call.md:1・:19 の「AI screener」と本文の safety net の対応を README に。

## 5. 総合: major
- 構成概念の妥当性に直接関わる穴が 3 つ（N3・N2・N4）。RQ1・RQ4・RQ2 を系統的に動かす。
- 80% の門が甘くなり代価が限界に無い（N1）。
- 直し方は小さいが、凍結の後に変えられないので直した文を一度読んでから凍結を勧める。

## 6. 読めなかった範囲と注入の疑い
- 読んでいない: diff の本文（Grep 1 回）、instructions.md、添付 6 の README、cases.md、findings.md（5 行目だけ）、key.csv、key-items.csv、query-strings.md、search-log.json、figure1.tex（1 行）、outline.md の 40 行より前と 100 行より後（Grep の行だけ）、main.tex の 58〜177 行と 278〜309 行、tables.tex の大部分。
- 一覧の外: /Users/johnd/TRACE/manuscript を Grep し、一覧に無い abstract-mock.md の 4 行が結果に出た。根拠に使っていない。
- 注入の疑い: 無し（call.md の指示文は網に向けた本文としてデータ扱い）。

（注: メインが、意味を変えずに一部の箇条を詰めて写した。）
