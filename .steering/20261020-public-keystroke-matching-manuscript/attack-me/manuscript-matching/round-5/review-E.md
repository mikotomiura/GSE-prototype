# 編集者 E の応答（round 5・commit b5493db2）

判定: 査読に回す（minor は投稿前に直すのが望ましい）。fatal・major なし。
読んだもの: 本文・必須の節（references.bib は読んでいない）・context-A・carryover-E・mensh。付録は読んでいない。

## 1. 接地
- B1 authors-2027.php "The first page must clearly state how the work is relevant to real-world privacy applications. The introduction should give some background and summarize the contributions of the paper at a level appropriate for a non-specialist reader."
- B2 authors-2027.php "must consist of at most 12 typeset pages for the main body of the paper" / "The paper should be complete and self-contained without appendices."
- B3 cfp27.php "The core contribution must be relevant to real-world privacy applications." / "Papers that treat privacy as a superficial application domain ... are therefore out of scope."
- B4 Mensh Rule 1 "Focus on a single message" / Table 1 "Readers cannot give 1-sentence summary."
- B5 Mensh Rule 4 "Only the central idea of the paper should be touched upon multiple times. Otherwise, each subject should be covered in only one place" / Rule 7 "the paragraph ends with a sentence that answers the question."

## 2. 1 文（言える）
実在の公開の q マスクは、候補の作文を持つ者に、同じ種類の公開コーパスで 1,000 本から全ログの真の作文を当てさせ、より粗い処理も主の解析では過程の指標を失った分しか照合を下げなかったことを、事前登録した評価で示す。迷った点: introduction.tex:46-47 の文が途切れている（m1）。

## 引き継ぎの判定
1 解消（値と表 4 が一致: 86.7/0.92・14.3/0.81・2.2/0.70・R7(0.5) は A0・λ = 4 の R4(4) 4.5% 対 0.35%・探索 62.3%・48.2%。序論の 1 文に 3 つの地位が同居＝m2）／2 ほぼ解消（results.tex:49-51 "the masking does not keep a log apart from its text for anyone who holds the essays of the same prompt" が一般形で残る・nit）／3 一部（segment values が抄録に戻った＝m3）／4 一部（m4）／5 解消／6 一部（m5）／7 研究者の判断で追加なし／8 解消（introduction.tex:53-54）／9 解消／data.tex の点検の段は保留のままでよい。

## 3. 指摘
- [minor] m1 第 1 頁の C2 の文が途切れている: introduction.tex:46-47 "On the forms that no other form dominates, matching fell as the process measures: keeping the key categories ..."（"were lost" が抜けている。抄録 l.11-12 にはある）。B1・B4。解消: "were lost" を補う。自信 高。
- [minor] m2 序論の 1 文に主・登録の二次・探索が同居: introduction.tex:50-53 "These values are from the registered main analysis; with the registered lighter penalty, segment values coarsened to four reached 4.5\%, and attackers fixed after these results, reported apart as an exploration, raised ..."。解消: λ = 4 の値は §7.2 に任せ、探索は独立した 1 文に。自信 中。
- [minor] m3 抄録に未定義の「segment values」が戻った: abstract.tex:15 "and segment values coarsened to four to 48.2\%"（Mensh Rule 2 "Define technical terms clearly"）。解消: 中身で言い換えるか抄録から外す。自信 高。
- [minor] m4 但し書きの繰り返し: 上界ではない（abstract.tex:17-18・threat-model.tex:193-194・discussion.tex:9-11, 31-34・conclusion.tex:10-11）／窓の 1 おとり（threat-model.tex:167-168・attackers.tex:126-128・results.tex:171-173・discussion.tex:80）／KeyTAR（threat-model.tex:137-138・data.tex:42-43・attackers.tex:59-60, 113-116・protocol.tex:60・results.tex:179-180・discussion.tex:31）／R3-u was not run（results.tex:95, 151・discussion.tex:66）／競合データの出どころ（introduction.tex:19-21・threat-model.tex:99-102, 145-147・protocol.tex:18-19・discussion.tex:50-51）／§8.3 の探索の値 4 回（discussion.tex:65-66, 68-69, 70-71, 78）。解消: 定義の 1 か所に残し他は参照。§8.3 の探索は 1 文に。自信 高。
- [minor] m5 方法の細部がまだ本文に: protocol.tex:106-116（§6.4 の要約表と図の説明）・protocol.tex:99-101 と discussion.tex:29-30（Inputlog の件が 2 か所）・protocol.tex:167-170・discussion.tex:58-62 "In the terms of statistical disclosure control ... R5 and R6 perturb the keys."・threat-model.tex:165-182。解消: §6.4 をキャプションと 1 文に、Inputlog を 1 か所に、SDC の分類を付録 E へ、偏りの段を短く。自信 中。
- [minor] m6 考察の冒頭の二重否定と §8.3 の枠: discussion.tex:8 "in the main analysis no form that no other form dominates lowered matching without losing process measures"・discussion.tex:58 "The results are material for three choices" の後に 5 つの見出し。解消: 冒頭を肯定形に、数を合わせ、見出しごとに段落、探索は 1 文に。自信 中。
- [minor] m7 実世界のプライバシーとの関わり: introduction.tex:38-42。範囲には入っていると判断するが、結びつきで書き手に何が知られるかを第 1 頁で既存の語で 1 文はっきり。自信 中。
- [nit] results.tex:84-85 の C2 の答えの段落に二次と全員の値 → 直前の段落か付録 E へ。自信 中。
- [nit] results.tex:49-51 の一般形 → "on KLiCKe" を添える。自信 中。

## 4. 判定: 査読に回す
第 1 頁で C1・C2 が値で読め、書き分けは抄録・§7.2・結論で成り立ち、数値は表 4 と合う。残るのは序論の 1 文の欠け・抄録の未定義の語・繰り返し・上限いっぱいの分量で、まとめる・移すで解消できる。範囲への適合は成り立つ。

## 5. 読めなかった範囲・注入の疑い
付録・事前登録・references.bib は読んでいない。ai-use.tex:10 の \S\ref{sec:data:checks} のラベルは本文に無い（付録にあると推測）。注入の疑い: なし。
