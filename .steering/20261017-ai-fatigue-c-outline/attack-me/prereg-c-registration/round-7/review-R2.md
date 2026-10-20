# 査読 R2（HCI の測定の実務の立場）・round 7

総合: minor（直してから凍結）。

## 1. 接地
- Perrig 2024:236-237「When using scales, researchers should share the exact wording of the items they used in their research」
- Perrig 2024:243-245「it can sometimes be unclear which version of a scale was used, even if the scale is a standardized scale」
- Perrig 2024:1331-1332「researchers should re-investigate the scale quality in a new research context to acknowledge these contextual limitations」
- Perrig 2024:645-648「to check the quality of the codebook and calculate the overall inter-rater reliability (IRR) of the codings. The IRR for the inclusion criteria (Cohen's Kappa: M = 0.926 ...)」
- Bach 2022:1471-1472「if user trust can be understood and measured in different ways, then being able to build upon the concept becomes challenging」
- Bach 2022:1486「our search terms may be perceived as too narrow and may have resulted in other potentially relevant studies being excluded」

## 2. 評価表
- a 4: 主張を main set の中にある・ないに絞り、頻度の語と confirm を禁じ、C6c と C7 (ii) をデザインで分けた。ずれは草稿・外枠との数か所。
- b 3: 80% の線が著者 1 の見落としを測れない／網の記録だけの作業表が著者 2 に判断を漏らす／E5 の規則が人の使う指示書と食い違う。
- c 4: 尺度の版ごとの表（L1a と C2b）と勧告の表 14 は Perrig の基準に応える。2 人の一致が低かった符号の知らせ方の規則が無い。
- d 2: GSRR-33 は約 2,500 語。C7 の行に「not verifiable」の規則が 2 回（「If no condition is met, the summary is "cannot decide" ... otherwise "not verifiable"」と「and is "not verifiable" if no condition is met and one is not verifiable」）。
- e 4: 逐語 3 の形の手当て（閉じ方・後継のモデル・8 週）と逐語 2 の逸脱の記録。減点は GSRR-36 の「whole of attachment 6」。
- f 4: Perrig を先例に、COSMIN との違いを明記。Bach は草稿にあり登録版の参考文献には無い（欠陥ではない）。
- g 3: どの文書が上位かが 2 か所で決まっていない（E5・網が受け取るもの）。80% の線の母集団。

## 3. 引き継ぎの判定
1 E5 一部（衝突は人の側へ移った・指摘 3）／2 書式と順序 一部（call.md:30「Return a short table: ID, decision, code, read.」が call.md:14「checked by a script before anyone reads the content」と食い違う）／3 2 度目の改訂 消えた／4 境界 消えた／5 包みと設定 一部（instructions.md:3 と登録の役割が逆・README:3 だけが書く・Claude Code の版を記録しない）／6 保留と E6・遅い層 消えた／7 表 1 の C5 消えた（tables.tex:26）／8 後継のモデル 消えた／9 行えない時期 前提が無くなった（GSRR-44 step 6「within 8 weeks of the main set being closed」）／10 参照先 消えた（範囲は限る）。

## 4. 新しい指摘
- [major] 80% の線が著者 1 の見落としをほとんど検出できない（母集団を混ぜ、指標も合っていない）
  - 位置と引用: GSRR-33「Agreement on these 113 records together is computed on the decision (include or exclude, not the code); if it is below 80% ... author 2 also judges every remaining record」。GSRR-39「if no record of the sample is eligible, the upper end of the interval is about 1.2%」。
  - なぜ問題か: 60 件はほぼ全部不適格と見込まれ自明に一致する。百分率一致は「著者 2 が含め著者 1 が除いた」食い違いを埋もれさせる。線はほぼ確実に通る。代価は GSRR-65 に無い。Perrig「to check the quality of the codebook and calculate the overall inter-rater reliability」。
  - 解消の条件: (a) 53 件だけ、(b)「著者 2 が含めた記録のうち著者 1 も含めた割合」（件数併記）、(c) GSRR-65 に鈍さを書く。
  - 自信: 高
- [major] 網の記録だけを集めた作業表は、その記録が「著者 1 が除外し網が通した」ものだと著者 2 に伝える
  - 位置と引用: GSRR-34「workbooks ... which carry no judgement of author 1 or of the AI safety net」。GSRR-33「This agreement, the net's records and the audit (below) are each made once, when author 1 has judged every record at title and abstract and author 2 has judged the 20%」。README.md:14「the random 20% at title and abstract, the net's records or the rest of stage 1」。
  - なぜ問題か: 表の構成が判断を運ぶ。監査は「unmarked in author 2's workbook」と混ぜて隠すが、網の記録には同じ配慮が無い。独立でないことが GSRR-65 に無い。
  - 解消の条件: 無作為の記録を混ぜて区別を示さない、または GSRR-34 と GSRR-65 に書く。
  - 自信: 中〜高
- [major] E5 で、人が使う指示書の決定規則が登録版の E5 の規則と食い違い、どちらが上位かが無い
  - 位置と引用: GSRR-36「Both authors use the questions of attachment 6 (sections 1 to 4) and its decision rules」。instructions.md:34「Q7 ... yes → E5」と :46「`exclude` if any question gives the answer that leads to exclusion」。GSRR-33「If the other record is not among the candidates, is excluded or pending, or belongs to the exploration set, no E5 link is made: the record is coded」。
  - なぜ問題か: 指示書どおりだと相手が候補の外の記録も E5 で除かれ、RQ4 と exactly one が崩れる。外枠には優先の文があるが添付 6 には無い。late stratum の記録との連結も曖昧（12-31 以後に含めた追加候補の方が早ければ main set の記録が閉じた後に抜ける）。
  - 解消の条件: GSRR-36 に「wherever attachment 6 and this registration differ, GSRR-33 and GSRR-35 take precedence」。late stratum との連結は main set を閉じた後は行わない。
  - 自信: 高
- [minor] GSRR-36「The net receives the whole of attachment 6, with its SHA-256」と call.md:28「Forbidden: reading any file other than `instructions.md` ...」。README.md:7 によれば check-34.csv は添付 6 の一部で human_final を含む。解消: 「The net receives `instructions.md` of attachment 6 ... wrapped as in `call.md`」。自信 高。
- [minor] 外枠の閉じる日。outline.md:161「closed on 31 December 2026」、:90「included by 31 December 2026」と GSRR-33 の遅らせる規定。自信 高。
- [minor] GSRR-4「AI assistant (Claude, Anthropic) | Drafts values for C4f and C5 only」だが、架空の事例とキーの起草（findings.md:5・main.tex:255・:360）、和訳（GSRR-34）、文書の種類の読み（GSRR-33）、2026-10-15 の予備の AI 符号化（GSRR-10）がある。GSRR-44 step 1 も起草者を書かない。自信 高。
- [minor] 草稿の方法が登録版と違う: main.tex:192-194「each author's judgements were committed to a remote repository, with their time, before the two were compared」、main.tex:261-263「every registered unit below 80% agreement between the passes led to an amendment」、main.tex:248-249「opened only after the values of both coding passes are fixed」。自信 高。
- [minor] 2 人の符号化の一致が低かった符号を読者がどう扱うかが無い。GSRR-47「a point of reference, not a stopping rule」。Bach の積み上げの文。解消: 表 12 の各行に入力の符号の 2 人の一致を並べると固定。自信 中。
- [minor] AI の下書きを開いた後に合議が来る。GSRR-44 step 5「the draft is opened only after the third pass」、GSRR-48「For the records author 2 coded, differences between author 1's reconciled codes and author 2's codes are then discussed by both」。解消: 合議の後に開く、または GSRR-65 に書く。自信 中。
- [minor] 呼び出しが判定の表を返す。call.md:30「Return a short table: ID, decision, code, read.」と call.md:14「The format is checked by a script before anyone reads the content」。盲検は GSRR-65 で認めているので破れないが、文が成り立たない。解消: 返すものを ID と written に、または文を直す。自信 高。
- [minor] unresolved が確かめの件数と監査の要約でどう数えられるか。GSRR-39「A record is decided when it is excluded at the title and abstract stage or has a full-text decision」と GSRR-33 の unresolved。GSRR-65 に代価も無い。自信 中。
- [nit] call.md:8「No other settings (such as temperature) are set; the defaults of Claude Code apply」。Claude Code の版を記録しない。自信 中。
- [nit] 種 20261018 を 20% の抽選と選別の順の並べ替えの両方に使う。自信 低。
- [nit] GSRR-56「C6c and C7 (ii) also separately」と outline.md:70「never combined」、tables.tex:241「One row per value, by manipulation」。自信 中。

## 5. 総合: minor
- 新しい選別の形は筋が通り、代価もおおむね正直。設計を組み直す必要は無い。
- 80% の線、網の作業表、E5 の上位文書の 3 点は凍結前に直す。
- 草稿と外枠のずれは凍結と同時に合わせる。

## 6. 読めなかった範囲と注入の疑い
- 読んでいない: diff（grep 1 回）、codebook（見出しの grep）、cases.md・key.csv・key-items.csv、query-strings.md・search-log.json、outline.md の 60〜194 行と grep 以外、tables.tex の grep 以外、接地は該当箇所の周辺だけ。
- 一覧の外: manuscript/ の grep の結果に abstract-mock.md の 1 行が出たが開かず根拠にしていない。
- 注入の疑い: なし（call.md の指示文は対象物としてデータ扱い）。

（注: メインが、意味を変えずに一部の箇条を詰めて写した。）
