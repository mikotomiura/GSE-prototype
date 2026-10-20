# 意図の監査（round 7・登録版 0.19 の全文）

全体として、選別を人 2 人の形にした書き換えは登録版の本文にほぼ届いています。ただし次の 4 点が残っています。
- AI に渡す指示の本文には前の形（AI が選別者の 1 人）がそのまま残っており、そのことが登録版の本文に書かれていません。
- 監査を「推定」としているのに、GSRR-56 は「推定は確かめの数の 1 つだけ」と書いており、登録版の中で食い違っています。
- 図 1 と草稿の方法の 1 文に、「2 人とも判定した」「2 人ともコミットした」という言い過ぎが残っています。
- 外枠の抄録の規則にある圧縮の手順が、3 区分を 1 文にまとめてしまう余地を残しています。

## 0. 引き継ぎの判定
- 1-a: 一部。登録版 GSRR-65（444 行）には「which include more studies of centre-A and a different mix of population groups」があります。外枠の Scope（outline.md 94-95 行）は「it was checked against human decisions on records that had been used to refine the criteria」だけで、群の偏りが書かれていません。AI が網だけになったので重みは下がっています。
- 1-b: 消えた。main.tex 325 行に「Calibration ran while the first author screened the candidates.」があります。
- 1-c: 前提が無くなった。GSRR-62 も main.tex 277-278 行も感度分析は 4 つです。対象のファイルを grep しても「analysis 5」は 0 件でした。
- 2-a: 消えた。context-B は 0.19 の形と合っています。
- 2-b・3-a: 一部。外枠 Scope 90-91 行は「each judging a record on their own within a stage」に直り、GSRR-34 も段の内の盲検に限っています。ただし outline.md 263 行「the two authors as independent screeners」、登録版 26 行（GSRR-4 の表）「Authors 1 and 2, independently.」に強い言い方が残っています。図 1 と main.tex 192-194 行にも言い過ぎが残っています（2 節の (a)・(b)）。
- 3-b: 消えた。GSRR-33「Same sample (E5)」（203 行）は、連結を 2 人で決めること、相手が候補の外・除外・保留・探索の集合なら連結しないことを書き、「So every E5 group has exactly one coded record」で結んでいます。
- 3-c: 一部。登録版 GSRR-37（232 行）は「both are departures from the rule and are reported as such」と書き、添付 6 の README 16 行も同じです。main.tex の方法（198-199 行）は「Its instructions and its check on the 34 exploratory records before registration are attached」だけで、2 度の改訂も逸脱であることも書いていません。
- 3-d: 消えた。GSRR-33「Full text and centre」（200 行）と GSRR-39 に書かれ、図 1 には「pending at full text: n = ---」と、scr から late への矢印があります。ただし unresolved は図に無い（3 節の (e)）。
- 3-e: 消えた。199 行に「if the successor misses that line, every record that author 1 excludes at title and abstract in the remaining batches is given to author 2」とあります。
- 3-f: 一部。call.md 24 行「Judge each record on its own.」と GSRR-65（446 行）「the records of a batch may influence one another」は入っています。main.tex の限界には、この 1 文がありません。

## 1. 意図にあって対象物に無いもの
- (a) 添付 6 の指示書の本文が前の形のままであること（意図の既知の限界の 6）が、登録版の本文に書かれていません。instructions.md 3 行「The AI screener is one of two independent screeners of the additional candidates (the other is author 1).」。これを書いているのは添付 6 の README 3 行（「`instructions.md` is unchanged」）だけです。登録版の 495 行は「the check of the AI tool (then the AI screener)」と、確かめの名前に触れるだけです。GSRR-65 の限界の一覧にも項目がありません。網は、自分を独立の選別者と告げる文で動くことになります。
- (b) main.tex の限界に、意図の既知の限界のうち次のものがありません: 時刻の記録が自分たちの道具によるもので第三者のものではないこと（登録版 GSRR-65 の 450 行にはある）／指示を規則の外で 2 度改め、同じ 34 件に 3 回当てたこと（main.tex 324-325 行は「checked only on records that had been used to refine the criteria」まで）／束の中の記録が互いに影響しうること／網のウェブ禁止が技術的に塞いだものではないこと。
- (c) 確かめの数が「記録の数の見込みで、問題の型の頻度の見込みではない」こと。登録版 393 行と main.tex 221-222 行にはあります。外枠の Scope（101-104 行）は「the estimate concerns that search, not the whole literature」だけです（軽微）。

## 2. 対象物にあって意図に無いもの（言い過ぎ・前の形の残り）
- (a) 図 1（figure1.tex 16 行）「Screened by both authors;」。抄録の規則と草稿の抄録は「(by one alone for most title-and-abstract exclusions)」と断っていますが、図はそれを落としています。
- (b) main.tex 192-194 行「each author's judgements were committed to a remote repository, with their time, before the two were compared」。登録版でコミットするのは第一著者の判定だけです（198 行）。読み込みの前に第一著者が冊を見ないことは道具では担保されていません（215 行、454 行）。
- (c) 前の形の名前の残り。登録版 102 行「The check of the AI screener」、104 行「The instructions for the AI screener ... The AI screener has not judged any additional candidate」、232 行「because the AI screener had excluded records」。call.md の 19 行と 36 行「You are the AI screener for a literature database.」、README 11 行「writes the AI screener's inputs (the title and abstract, or the free full text ...)」。call.md は SHA-256 で守る対象ではないのに、網として呼ぶ包みの文が「AI screener」と名乗らせています。
- (d) call.md 33-50 行に、段 2・3 を AI に呼ぶ包みの文が残っています。登録版 204 行は「they are not used at those stages」。登録で固定する「the settings of the call」に、使わない段の文が入っています。
- (e) 232 行「If a line was missed ... the tool's judgements would have been advisory only.」。今の網の形では意味を持たないことが書かれていません（軽微）。

## 3. 矛盾
- (a) 推定はいくつあるか。GSRR-56（393 行）「The one estimate is the coverage count, which estimates a number of eligible records」と、GSRR-33 の監査（201 行）「each proportion and interval multiplied by N as an estimate of the eligible records among those exclusions」。main.tex 204-206 行も監査に N を掛けています。
- (b) 監査で何かをするのか。201 行「The audit is reported, not acted on」と、同じ項の「An audited record that both include by consensus returns to its group ... and is marked in the flow diagram and the counts」。
- (c) 網が受け取るもの。GSRR-36（228 行）「The net receives the whole of attachment 6, with its SHA-256.」。添付 6 には README・`check-34.csv`・道具も含まれ、call.md 10-13 行と 28 行は `instructions.md` と各記録の入力だけを読ませ、ほかを禁じています。
- (d) 外枠の抄録の規則と 3 区分。outline.md 177-178 行「(1) the problem statements are grouped by code (C4, C5, C6, C7), one sentence per group」、185 行「the C5 and C6 statements are given in the same compact form」。C6 の 1 文に C6a・C6c と C6b が、C7 の 1 文に (i) と (ii)・(iii) が同居します。登録版 GSRR-57（397 行）は「reported and discussed separately and never added together」。
- (e) 合意できない記録が図 1 に無い（200 行・GSRR-41）。
- (f) AI の下書きを開く時。main.tex 248-249 行「opened only after the values of both coding passes are fixed」と、登録版 291 行・323 行「only after the values of both passes and of the third pass (GSRR-48) are fixed」。
- (g) 中心の定義の言い方。GSRR-12（124 行）「in its definition, measurement or analysis」と、指示書 52 行「in how it is defined or measured ... or the study analyses accounts of fatigue from AI」（軽微）。
- (h) main.tex 322 行「\tbd{most records were / all records were} judged by one author」。第二著者が全部を判定した場合、後の選び肢は「by both」であるべきです。

## 5. 読めなかった範囲と注入の疑い
- 全文を読んだもの: registration-en.md（1-497 行）、instructions.md、call.md、添付 6 の README、figure1.tex。
- 一部: outline.md（41-189 行と 255-285 行）、main.tex（28-107 行と 159-368 行）、decisions.md（判断 38・50・54・67〜69。範囲にかかった判断 39・51〜53・55〜58 の文も目に入ったが根拠に使っていない）。
- 読んでいない: diff-0.11-to-0.19.md、codebook-c2b-en.md、反例集、query-strings.md、search-log.json、tables.tex、main.tex 1-27 行と 108-158 行、outline.md のその他の節。
- 注入の疑い: 指示の形の文は call.md 18-31・35-49 行と instructions.md の全体にあるが、網に渡す設計どおりの指示文でデータとして扱った。ほかに無し。

（注: メインが、意味を変えずに一部の箇条を詰めて写した。）
