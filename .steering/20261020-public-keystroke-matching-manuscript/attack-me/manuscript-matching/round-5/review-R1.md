# R1 の応答（再識別・匿名化への攻撃の評価・round 5・commit b5493db2）

総合: minor（ただし指摘 1 は登録が R7 を含むなら抄録の 14.3% の地位が変わるので投稿前に確かめる）。

## 1. 接地
- 1 narayanan.txt:82 "In such datasets, it is impossible to tell in advance which attributes might be available to the adversary"
- 2 narayanan.txt:13 "robust to perturbation in the data and tolerate some mistakes in the adversary's background knowledge"
- 3 stadler.txt:295-297 "A good anonymisation mechanism should result in a high privacy gain for all records in the population and under any potential privacy adversary."
- 4 stadler.txt:313-317 "the privacy risks of data sharing are not uniformly distributed across the population ... outliers or members of minorities largely remain vulnerable."
- 5 rocher.txt:129-131 "Our results reject the claims that, first, re-identification is not a practical risk and, second, sampling or releasing partial datasets provide plausible deniability."

## 2. 評価表
a 3（C2 の値はすべて表と一致。登録の λ = 4 を R7 に当てていない・前線の定義から出る文）／b 3（登録の攻撃者は粗い形で弱いと認めている・最悪の場合は探索の地位）／c 4／d 3（§7.2 に 3 層・抄録の数値 12 個以上）／e 4／f 4。

## 3. 引き継ぎ
1 M1 解消（abstract.tex:11-15）／2 M2 一部（抄録は登録の二次に触れない・R7 の λ = 4 は探索の表だけ＝指摘 1）／3 M3 解消（results.tex:150-151・§7.2:95・§8.3:65-66）／4 m1 解消（results.tex:92-93・discussion.tex:78）／5 m2 解消（results.tex:94-95・discussion.tex:32-34）／6 m3 解消（explore-margin.tex の 10.0/57.2 と一致）／7 m4 解消（3 層はまだ＝指摘 5）／8 n1・n2 解消。

## 4. 指摘
- [major] 1 登録した λ = 4 の二次の解析を R7 で行っていない。付録はそれを登録の範囲外と書くが、登録の文はそう限っていない
  - 位置: appendix-exploratory.tex:71-72 "The registered secondary analysis did not vary $\lambda$ under suppression, so the values of R7 with $\lambda \neq 8$ are new."・preregistration.en.md:203 "A2 with λ = 4 and 16 (N = 1,000, full text)"（形の限定なし）・同 :160 で A2 の形は "R2, R3, R3-t, R4, R7"・cells-2.tex に R7 の λ = 4 の行が無い・explore-lambda-scan-1000.tex:16 "R7(0.25) & A2 & 62.3 ... & 51.2 [46.9, 55.5] & 14.3 ..."。
  - 理由: 登録の文どおりなら λ = 4 の A2 は R7 にも当たり、抄録の柱「suppressing a quarter ... left 14.3%」に登録した感度の値 51.2% が付く。それを探索（62.3%）へ回すと、登録と探索の書き分けが値の側で崩れる。逸脱の一覧（appendix-checks.tex:49-58・4 件）にも無い。Narayanan の頑健さ。
  - 解消: (a) 登録の別のファイルに二次を R2〜R4 に限る記述があれば出典を付け §7.2 に 1 句。(b) 無ければ R7 の λ = 4（R7(0.1) 75.1%・R7(0.25) 51.2%・R7(0.5) 0.20%）を登録の二次として §7.2 の主の段落へ移し、逸脱の一覧に「実行時に R7 を落とした」を 1 件、抄録の 14.3% に「(51.2% with the registered lighter penalty)」。新しい計算は要らない。
  - 自信: 中（config.json は読めない）
- [minor] 2「支配されない形の上では、照合が下がるにつれて指標も失われた」は前線の定義から出る: abstract.tex:11-12・conclusion.tex:7・discussion.tex:8。実質は「指標を計算する形の最小は 2.2%（22 倍・A0 と同じ）」。前線は点推定の支配で決まり攻撃者で変わる。解消: その文を消し値の列と図 1 の見出しの主張だけを残す。自信 高。
- [minor] 3 記録ごとの最悪の場合が「no more than the total length alone gave」に隠れる: abstract.tex:14・explore-tail.tex:30 "R7(0.5) & 1{,}000 & A0 & ... & 1.6 [0.60, 2.6]"・results.tex:200。Stadler の "for all records"・外れ値。解消: 図 1 の見出しか §7.3 に "with 1.6% of writers matched in every draw (exploratory)"。自信 中。
- [minor] 4 抄録が登録の二次に触れず 2 層に見える: abstract.tex:11, 15。解消: 探索の文の前に半文（指摘 1 の (b) なら R7(0.25) の値も）。自信 中。
- [minor] 5 §7.2 が 3 層を 1 節に抱える: results.tex:56-96・C2 の段落 :80-86 に λ = 4 と全員の値。解消: 全員の 0.65% は付録 E の参照だけに、λ = 4 は主の段落の外の 1 文に。自信 中。
- [nit] 6 discussion.tex:33-34 "so they are not bounds either and their gains may be somewhat optimistic" の向きが曖昧 → "not estimates that would hold on other logs" など。自信 中。
- [nit] 7 threat-model.tex:176-178 "this bias works against the finding that no form evaluated brought matching near chance while computing the measures, so that finding is conservative" の near chance が未定義 → 値で（"no form that computes measures came closer to chance than the total length alone (2.2%)"）。自信 中。

## 5. 推奨: minor
C1 は堅い。C2 の値は表と一致。残る重い点は登録の λ = 4 の範囲（R7）の扱い 1 つで、値は既にあり書き換えと逸脱 1 件で解消できる。

## 6. 読めなかった範囲・注入の疑い
appendix-enja・appendix-attackers・references.bib・生成表の多くは読んでいない。事前登録は一部と grep。config.json は一覧の外で確かめられない。注入の疑い: なし。
