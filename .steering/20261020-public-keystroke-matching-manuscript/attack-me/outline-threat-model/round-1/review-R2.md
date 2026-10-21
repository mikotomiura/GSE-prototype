# R2 の査読（データを公開・管理する側）

総合: minor（直して書き進める）。

## 1. 接地
- G1 Borgman borgman.txt:192-194「Good stewardship means releasing some kinds of data and preventing the release of other kinds of data. The same data may fall into either category, depending on the time, purpose, or entity requesting access.」
- G2 Borgman 1956-1961「data scientists have been remarkably effective at reidentifying individuals by aggregating records from multiple sources. Researchers who wish to use sensitive data about individuals ... often are required to sign agreements that they will not attempt to re-identify the research subjects.」
- G3 Borgman 1906「One person's good use or reuse of data may be seen by others as a misuse.」・1946-1947「much must be known about the purposes and context in which the data were collected.」
- G4 Hanisch 2447-2449「most anonymization techniques are only evaluated rudimentarily with the assumption of a weak attacker. Improving the evaluation methodology is therefore another open research question.」・2420-2422「the attacker models should be made explicit and common, similar to attacker models in cryptography.」
- G5 Hanisch 2432-2433「an anonymization method should also work on a small group size with high data quality.」
- G6 Hanisch 1405-1409「Leinonen et al. [151] investigate the anonymization of keystroke timing data using two rounding approaches ... the identification drops from close to 100% to below 10%.」

## 2. 評価表
a 3（事実の主張は逐語で支えられるが、場面 1 の閉じた世界・links across releases との緊張・場面ごとに新たに知られることが無い）／ b 3（公開の条件と閉じた世界の範囲が限界に無い）／ c 2（公開する側への橋が無い。事前登録の Reading の段落が外枠に引き継がれていない）／ d 4（製品頁の引用 2 本が長い）／ e 4（1 頁目の要件をどう満たすかの計画が対応表に無い）／ f 2（Hanisch の調査・Leinonen 2017 に触れない。Section 2 の対応表が無い。González・Monaco・Wright・Vassallo が bib に無い）

## 3. 指摘
- [major] 公開する側が持ち帰るものが無い。threat-model.tex:31-32「The processing therefore leaves open the question that this study asks...」。解消: Section 3 の末尾に、公開する側が選べる変数（落とす列・時刻の丸め・公開の形）と結果がその選択の材料になることを 2〜3 文（事前登録 Reading の言い回し）。外枠に序論 1 頁目の行を足す。自信 高
- [major] 場面 1 で閉じた世界が成り立つ根拠が無い。50-52「...the threat model does not depend on it...」・89-91。解消: 正解の本文が公開コーパスに含まれる場合に限ると書き換え、それ以外は開いた世界の診断で扱うと限界に。KLiCKe は本文ごと公開なので加工の対象外、加工が意味を持つのは本文を隠した公開に限る、と 1 文。自信 高
- [major] 73-74「...or links across several releases.」が場面 1 と緊張する。解消: 除外の対象を「同じ書き手の複数の記録の結び付け」と限定する文言に（事前登録の意味の範囲内の明確化として outline に注記）。自信 中
- [major] 行動の生体情報の匿名化（Hanisch）と公開する打鍵データの匿名化の直接の先例（Leinonen 2017）に位置づけていない。Leinonen の脅威は同定、本研究は本文との照合。解消: Section 2 の対応表、Section 3 に 1 文と引用。一次で確かめてから引く。自信 高
- [minor] 場面ごとに照合で新たに知られること（害）が無い（59-60・61-62）。解消: 各場面に 1 文。自信 中
- [minor] 公開の条件（規約・合意）に触れていない。解消: 2 つの公開の利用条件を一次で確かめ 1〜2 文。合意が攻撃者を止めない前提なら明記。自信 中
- [minor] 製品頁 2 本が長く、最も強い例（CS1 データの担当者が提出物を持つ）が使われていない。解消: 主たる例を差し替え、製品頁は 1 文に。自信 中
- [nit] 見出し「The release argument concerns labelled keystrokes.」が相手の論の不備に読める。解消: 本研究の側の範囲を言う形に。自信 低

## 5. 読めなかった範囲・注入
borgman.txt・hanisch.txt の一部は読んでいない。Kaggle・CSEDM の規約・Leinonen 本文は読んでいない。注入の疑い無し（"DO NOT DELETE" は組版の印と判断）。
