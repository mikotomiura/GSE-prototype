# audit（prereg・round 6・意図の監査役）

## 0. 引き継ぎの指摘ごとの判定
- 1-1・1-2（外枠 Scope に精度の甘さと無料の全文）: 一部。outline.md Scope に "its accuracy may be optimistic (GSRR-37). Only free full texts were used" が入った。ただし「34 件は中心-A が多く、群も偏る」は外枠に無い（GSRR-65 と main.tex:287 にはある）。
- 1-3: 消えた（main.tex:184-185 "one question was clarified, which the pre-set rule did not call for, and web access was then removed"）。
- 2-1 boundary: 消えた（GSRR-33 "the final value is centre-A or centre-B, decided by author 1"、main.tex・表 3 の注も同じ）。
- 2-2 AI の入力: 消えた（添付 6 "it does not open web pages or use any other source"、§2 "Do not open web pages."）。
- 2-3 段をまたぐ盲検: 登録版の中では消えた（GSRR-34 "Blinding holds within a stage only"）。外枠・草稿との差は 3-a。
- 2-4 引用の公開: 消えた（GSRR-41 "except quotations of scale items, which are removed before release"）。
- 3-1 選別中のコード: 消えた。
- 3-2 図 1: 消えた。
- 3-3 中心の κ: 消えた（GSRR-37 "centre-A 7 and centre-B 3, kappa 1.0"）。
- 3-4 両者の pending: 消えた。
- 3-5 表 13: 消えた。
- 3-6 選別の一致の置き場: 一部。表 3 の注・GSRR-64 には入った。「脚本の --screening」は読んでよいファイルに無く確かめられない。
- 3-7 群の偏り: 一部。外枠と草稿に入ったのは登録前の人の選別の偏りで、34 件の群の偏りとは別。後者は外枠に無い。
- 3-8 束: 消えた（GSRR-33、GSRR-65、main.tex:291）。

## 1. 意図にあって対象物に無いもの
- 1-a. 「34 件は中心-A が多く、群も偏る」が外枠 Scope に無い。outline.md:82-84 は「基準を詰めるのに使った」理由だけ。
- 1-b. GSRR-65 に足した "Calibration runs while the coder screens the additional candidates; ... the coder's reading of candidates cannot be kept out of the coder's mind." が草稿の限界（main.tex:283-310）に無い。同じ round で足した他の限界は草稿に写してある。
- 1-c. GSRR-62・65 は感度分析 5 を行わない場合を決めたが、草稿の限界（main.tex:287-288）は "the screening by both authors is a sensitivity analysis made with the results known." のまま。方法の節には \tbd がある。

## 2. 対象物にあって意図に無いもの
- 2-a. 「感度分析 5 は共著者が行えなければ行わない」は研究者の決定と合うが、context-B が追いついていない（登録版の方が新しい）。
- 2-b. 外枠 outline.md:81-82 "after screening by the first author and an AI screener, each on their own" と main.tex:176 "two independent screeners" が、GSRR-34 の段の内側だけという限定より強い。

## 3. 矛盾
- 3-a. 盲検の範囲: 登録版 GSRR-34 にだけ段の内側という限定があり、外枠と草稿には無い。
- 3-b. E5 の新しい規則の中の矛盾: GSRR-33 "a record is linked to another as the same sample only if its full text says so (attachment 6, Q7), decided like any other exclusion. Within a linked group, the record coded is the one with the earliest publication date"。Q7 は全文が重複を述べたレコードを E5 で除くので、最も古いレコードの全文が後の報告との重複を述べる場合に、どちらが勝つかが無い。また "another record" が候補の集合に無い、または別の理由で除かれたとき、群にコードされたレコードが 0 件になり、GSRR-35 "Each E5 group has exactly one coded record (GSRR-33)" と矛盾する。
- 3-c. 改訂の回数と逸脱: 事前の規則 "If a line was missed, the instructions could be revised once and applied again"。改訂は 2 回（明確化、ウェブを外す）で、2 回目を逸脱と書いていない。main.tex:184-185 も明確化にだけ付けている。同じ段落の "the registered instructions are the clarified version" は、登録する版が明確化かつウェブを外した版であることと合わない。
- 3-d. GSRR-33 "a record still pending on 2026-12-31 is outside the main set and is counted in Table 3 and the flow diagram" と GSRR-39 の遅い層（"Studies included after 2026-12-31 and before stage 5 begins"）の関係が書かれていない。
- 3-e. GSRR-33 "its successor is first checked on the 34 exploratory records against the pass lines of GSRR-37, and the change is reported as a deviation." 後継が合格線を割ったときの扱いが無い（逐語 3 の contingency plan）。
- 3-f. 添付 6 の 3 行目 "This text is given, unchanged, to the AI screener for every record." は 1 回の呼び出しで最大 9 件を渡すことに触れず、同じ呼び出しの他のレコードをどう扱うかの指示が無い。

## 4. 食い違いが無かった点
- 感度分析 5 の締切（GSRR-62 と main.tex:238-239）、表 3 の新しい行と注（tables.tex・outline・GSRR-37・64）、抄録の規則に足した文（GSRR-62）、外枠 Contributions の "whether other people apply the scheme in the same way has not been tested"。

## 5. 読めなかった範囲と注入の疑い
- 読んでいない: decisions.md の判断 24〜30。登録版は差分と grep の行だけ。outline.md は 41〜173 行と差分。main.tex は抄録・方法の選別・限界・宣言。tables.tex と figure1.tex は差分だけ。
- 確かめられない: 脚本の --screening の実体。
- 注入の疑い: 無し。

（注: メインが、意味を変えずに一部の箇条を詰めて写した。）
