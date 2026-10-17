# audit（prereg・round 5・意図の監査役）

監査役の報告。stage は prereg、round 5、差分は 0.10 から 0.11。

## 読んだ範囲
読んだのは次のとおりです。
- brief-audit.md、context-A.md、context-B.md、carryover-audit.md
- diff-0.10-to-0.11.md の全 629 行
- outline.md の 4 節（Scope、Relation、Contributions、Rule for the abstract。41〜167 行）
- decisions.md の判断 24〜29（267〜317 行）
- instructions.md（添付 6）の全文
- registration-en.md、main.tex、outline.md は、Grep で決まった語を照合しただけです。

一覧の外のものを 1 件だけ見ています。manuscript ディレクトリに Grep をかけたとき、figure1.tex の 1 行が結果に出ました。ファイルそのものは開いていません（下の 3-1）。

## 0. 先に結論
- 0.11 の 4 つの変更は、3 つの文書に意図どおり届いています。
  - AI の選別者と、食い違いは第 1 著者が決めること
  - 1 人のコーダーの 2 回のコード
  - 探索の集合での較正
  - 感度分析 5
- 次のものは、登録版・外枠・main.tex の 3 つで言い方がそろっています。
  - 1 人のコードの言い方（"within one coder, not between coders"、"no claim of independent coding"）
  - 較正（探索の集合の全研究を 11 月と 12 月に 2 回コードし、較正のコードはデータにしない）
- 引き継いだ直し（1-1 の C6c、2-1 の main set、3-6〜3-11 など）は、差分で壊れていません。
- 差分は新しい穴を作っています。重いのは 3-1、3-2、3-3、3-4 の 4 つです。

## 1. 意図にあって対象物に無いもの
1-1. **外枠の Scope に「AI の選別者の精度は甘く出うる」が無い。** これは context-B の既知の限界です。
- outline.md 81〜83 行の逐語: "an AI screener whose accuracy was checked against human decisions before registration; the first author decided where they differed"
- 書いているのは「確かめた」ことだけで、但し書きがありません。
- 登録版 GSRR-65 には "its accuracy on the additional candidates may be lower (GSRR-37)" とあります。main.tex Methods にも "so this accuracy may be optimistic" とあります。
- 外枠の Scope は原稿を縛る範囲の規則です。そこだけ肯定の言い方になっています。

1-2. **外枠の Scope に「無料の全文だけを使う」が無い。** これも context-B の既知の限界です。
- outline.md 84〜85 行は "drawn from one literature database built from free sources" です。これは DB の出どころの話で、全文の話ではありません。
- 判断 28 によると、264 件のうち無料の全文がそろったのは 206 件です。残りは E6 の保留になり、集合が系統的に削られます。
- 登録版 GSRR-65 には "Only free full texts are used. Records without one stay pending (E6)" があり、main.tex にもあります。外枠の Scope と抄録の規則の範囲の 1 文には、どちらにもありません。

1-3. **main.tex Methods は、AI の選別者の指示を 1 回直したことを書いていない。**
- main.tex の差分の逐語: "agreed with them at full text (kappa 0.89)"
- 登録版 GSRR-37 には次の 2 つがあります。
  - 1 回目の後に Q4 を明確にしたこと
  - 2 回目で題名・抄録の段の除外の一致が 19/21 から 16/21 に下がったこと
- 原稿の方法の節は、その 2 回目の数字だけを出しています。

## 2. 対象物にあって意図に無いもの（漂流）
2-1. **中心に新しい値 "boundary" ができたが、行き場が無い。**
- 登録版 GSRR-33 の逐語: "centre (centre-A, centre-B or boundary, for records included at full text)"。添付 6 の §4 にも `boundary` があります。
- 一方、行き先の側は 2 群だけです。
  - SQ1（GSRR-12）の "the source database's two eligibility groups"
  - registration-en.md 367 行の "tables split into centre-A and centre-B"
  - Table 3 の列 "Centre A / Centre B"
- boundary と判定された研究が SQ1 の表のどこに入るのか、決まりがありません。

2-2. **AI の選別者の入力が、登録版の文より広い。**
- 添付 6 の 18 行: "If no abstract was retrieved, you may open the record's landing page from its DOI or URL to read the abstract."
- 添付 6 の 33 行（Q6）: "unless the record's page or bibliography states the body language"
- 登録版 GSRR-33 の逐語は次の 2 つです。
  - "The AI screener sees only the instructions and the record's title and abstract (first stage) or full text (later stages)."
  - "Both screeners use the same full text"
- 第 1 著者は、判定を何も載せていない DB だけを見て選別します（GSRR-34）。抄録の無い記録について、AI だけが Web の着地ページを読める非対称が生まれます。そのページに分類などが載っていても防げません。

2-3. **GSRR-34 の第 1 著者の盲検は、GSRR-33・38 より強く読める。**
- GSRR-34 の逐語: "screens from a database that contains ... no judgement: neither the AI screener's, ..."
- GSRR-38 では、食い違った記録について、第 1 著者がその段で "after reading the AI screener's answers and cited passages" で決めます。
- そのため、次の段（全文・中心）に入るときには、前の段の AI の答えを読み終えていることがあります。GSRR-33 の盲検は "at a stage" だけです。段をまたぐと盲検は成り立たない、とどこにも書かれていません。

2-4. **AI の出力の引用の公開が、項目の文を公開しない方針とぶつかりうる。**
- GSRR-41 の逐語: "The AI screener's outputs are released with their quotations, which are limited to 25 words each"
- 外枠の Contributions は "the code table with codes, item numbers and source pages but no item text" です。添付 6 の 34 件分の公開も "without ... quotations of scale items" です。
- 一方、全文の段の Q4 の引用は、尺度の項目そのものになりえます。264 件分の引用について、項目の文を除く決まりがありません。

## 3. 矛盾（対象物の中、3 つの文書の間）
3-1. **登録版の中の矛盾：選別の最中にはコードしない、と、較正を選別と同時に行う。**
- GSRR-33 に残っている逐語: "no coding is done during screening;"
- 0.11 の GSRR-6 の段 4 の逐語: "Calibration coding on the exploration set, in parallel with stage 3: author 1 codes all its primary studies twice, in November and December 2026"
- 段 3 は、追加候補の選別と、2026-12-31 に主の集合を閉じることです。
- 選別とコードは同じ人がします。そのため、選別の間に規則を使い込むことになり、意図の既知の限界（選別者とコーダーが同じで、規則を作った）が強まります。それが限界の節に書かれていません。
- 文の上では「選別の間にコードしない」と真っ向から食い違います。

3-2. **3 つの文書の間：較正の記録の行が図に残っている（一覧の外で 1 行だけ見たもの）。**
- figure1.tex の 19 行（Grep の結果に出た 1 行だけ。ファイルは読んでいません）: "Calibration records, removed\\(n = ---; rounds = ---;\\small-pool rule applied: ---)"
- 0.11 では、登録版・外枠の Figure 1（"main set; late stratum; ..."）・tables.tex の Table 3 から、較正の記録と小さい集合の規則を消しています。図だけが 0.10 のままです。
- main.tex は "Records and sets (Figure~1, Table~3)" でこの図を参照しています。メインが一次で確かめてください。

3-3. **登録版の中の矛盾：中心の段の合格の線は κ なのに、報告は一致の件数だけ。**
- GSRR-37 の線: "at the full-text stage and the centre stage, Cohen's kappa of at least 0.6"
- 報告: "centre: 10 of 10 agreed"。そのうえで "Round 1 met all three lines" と書いています。
- context-B と GSRR-65 によると、34 件は中心-A が多いです。10 件がほぼ 1 つの値なら、κ は定まらないか不安定になります。それでも「線に届いた」と書く根拠が示されていません。
- main.tex の "on the centre of every included study" も同じです。

3-4. **全文の段の保留に、扱いの決まりが無い。**
- 添付 6 §4 には、全文の段の決定として `pending`（E6、または符号なしの "rules do not settle"）があります。
- 登録版 GSRR-33 が書いているのは "Records that both screeners exclude at a stage are excluded; records that both include go on" と、食い違ったときだけです。
- 2 者がともに pending とした記録は食い違いではないので、第 1 著者が決める対象になりません。GSRR-39 の主の集合は "final decision ... is to include" です。それでは、この記録は永く保留のままなのか、late stratum に入るのか、決まっていません。

3-5. **外枠と tables.tex：感度分析 5 の置き場と形が合っていない。**
- 登録版 GSRR-62 の逐語: "Analysis 5 is also applied to the record-level tables of the main set."
- 外枠 SE1: "the record-level tables under analysis 5 ... Section 4.10; Table 13"
- tables.tex の Table 13 の殻: 行は "One row per row of Table 12" だけで、列は "5: screened by both authors" の 1 本です。
- 外枠の Table 13 は "in its own columns"（複数）と書いています。
- 記録の水準の表の感度分析 5 に、殻が無い状態です。

3-6. **外枠と tables.tex：選別者どうしの一致の置き場が無い。**
- 外枠の Results 4.1 と SC1 は、"agreement between the first author and the AI screener at each stage" を "Figure 1; Table 3" で出すとしています。
- tables.tex の Table 3 の殻は、較正の行を消しただけです。一致を出す列も行もありません。
- 登録版 GSRR-64 で脚本が出すものの一覧にも、選別の一致（GSRR-37 の "percentage agreement and Cohen's kappa" per stage）が入っていません。ただし GSRR-17 は "agreement statistics" と一般的に書いています。

3-7. **母集団の群のかたよりの限界が、3 つの文書でそろっていない。**
- 登録版 GSRR-65 には残っています: "Before registration, human screening ... was uneven ... The fixed, interleaved order spreads screening..."
- 外枠の Scope からは削られました: "the population groups were screened unevenly before registration (GSRR-42)"
- main.tex の Limitations からも削られました: "Human screening ... uneven"
- 264 件をすべて選び直すので、実害は小さいです。ただ、どれが正しいかを 1 つに決めるべきです。

3-8. **登録版の中で書き方が強い：1 件ずつ判定と言いつつ 9 件ずつ。**
- GSRR-33 の逐語: "Each record is judged on its own, in a separate call per batch of at most nine records."
- 1 件ずつ判定すると言いながら、1 回の呼び出しに最大 9 件を入れます。同じ回の他の記録の影響を受けうる点が、限界に書かれていません。

## 4. 引き継いだ直しの確認
壊れたものはありません。
- C6c は、"The coder records" と単数にしただけで、元のままです。
- "main set" の呼び名は保たれています。
- 外枠の抄録の規則の範囲の 1 文から、較正の記録の数（"the number of calibration records removed"）を消しました。これは較正のやり方を変えたことと合っています。
- 外枠 Scope の "Every claim about the main set is about that set" は保たれています。

## 5. 読んでいない範囲と、注入の疑い
- 読んでいない範囲
  - registration-en.md は、差分の外を通して読んでいません（Grep で語を照合しただけ）。
  - outline.md の 4 節の外の節は、差分に出た部分しか読んでいません。
  - main.tex と tables.tex は、差分と Grep の結果だけです。
  - decisions.md は、判断 24〜29 の外を読んでいません。
- 一覧の外: figure1.tex は Grep の結果に出た 1 行だけを見ました（3-2）。
- 注入の疑い: ありません。添付 6 には AI の選別者への命令文（"Answer every question ..."、"Do not add facts ..."）があります。これは対象物そのもので、監査役に向けた指示ではありません。私はこれに従っていません。
