# R2 の応答（データを公開・管理する側・round 5・commit b5493db2）

総合: minor。

## 1. 接地
- B1 borgman.txt:1645-1650 "Determining who has access to what data, by what criteria, when, and under what conditions is an overarching problem of data governance and stewardship. Competing values are often at stake. Openness promotes transparency and accountability, but can undermine privacy, confidentiality, and anonymity."
- B2 borgman.txt:1688-1690 "Conversely, highly processed data might be released, with or without sufficient documentation, software, and code to make them useful to others."
- B3 borgman.txt:1956-1958 "data scientists have been remarkably effective at reidentifying individuals by aggregating records from multiple sources."
- H1 hanisch.txt:177-179 "any PET poses a trade-off between privacy and functionality. The optimization of the privacy-functionality (or privacy-utility) tradeoff will refer to the design and tuning of PETs in order to maximize privacy for a desired functionality, or vice versa."
- H2 hanisch.txt:2230-2235 "We find this methodology too simple as the underlying assumption is that the attacker is not aware of the anonymization. … should also consider an attacker that actively tries to reverse the anonymization and knows the anonymization technique and its parameters."
- H3 hanisch.txt:2447-2448 "most anonymization techniques are only evaluated rudimentarily with the assumption of a weak attacker."

## 2. 評価表
a 4（要約の値は main-1000.tex と一致・探索の値の選び方に偏り）／b 3（主の攻撃者は粗い形で弱い・探索は評価の記録で選び陰性対照なし。どちらも本文が認めるが前線は攻撃者に依存）／c 3（探索の後の前線を本文から組み立てられない・得点との関係の変化が 2 例だけ）／d 3（値の組が 6 か所以上・図 1 の見出しと §7.3 末がほぼ同文・抄録 324 語に 3 層・three choices と 5 観点）／e 4（12 頁内・1 頁目にプライバシー・必須の節あり・付録なしで完結）／f 4。

## 3. 引き継ぎ
1 解消（abstract.tex:11-15・introduction.tex:46-53・results.tex:84-85）／2 解消（探索の下で R7(0.25) が R3-u を支配しなくなることを書いた文は無い＝指摘 2）／3 一部（指摘 3）／4 研究者の判断で見送り・欠陥に数えない／5 一部・研究者の判断で欠陥に数えない／6 解消（別の重複＝指摘 5）／7 一部（指摘 6）／8 解消（discussion.tex:66・results.tex:95）／9 解消／10 解消。

## 4. 指摘
- [minor] 1 本文で報告する探索の値の選び方が偏る（R3 と R4(1) の 98.5% が本文に無い）: results.tex:88-93 の列挙・explore-strongest.tex:2-3 "98.5 [97.4, 99.4] & A2-scan ($\lambda{=}2$)"（R4(1) は 40.5 → 98.5）。protocol.tex:116 "no cell is selected for being favourable"。解消: 列挙に "R3 and R4(1) to 98.5%" を 1 句か、挙げる基準を 1 文。自信 高。
- [minor] 2 公開する側が探索の後の前線を本文から組み立てられない: results.tex:148-151・図 1 の見出し。探索では R7(0.25) は R3-u を支配しなくなり、前線で変わらないのは R7(0.5)（A0 と同じ 2.2%・ρ 0.70）と R4(8) だけ。解消: §7.3 か §8.3 に 1 文（探索の下でも前線に残るのは R7(0.5) と R4(8) だけ・ほかの点は攻撃者に依存）。自信 中。
- [minor] 3 得点との関係の変化が 2 例だけ: results.tex:152-154・discussion.tex:72-73・utility-score.tex:2-10（insertion length 0.20 → 0.33 など・R7(0.5) で within-word −0.30 → −0.45・between-word −0.08 → −0.33）。解消: 2 例を「得点との相関が R0 から 0.1 以上ずれた指標の数」の 1 文に置き換え、§8.3 を「近似した指標と、ずれる向きを明記」に。自信 中。
- [minor] 4 値の組と「2.2%」の文の繰り返し: 図 1 の見出し "the lowest matching on a form that computes process measures was 2.2\% (R7(0.5), 22 times $1/N$, no more than A0)" と results.tex:158-159 がほぼ同文。86.7/0.92・14.3/0.81・2.2/0.70 が 6 か所以上。解消: 図の見出しを読み方だけに、§7.3 の C2 の段落は図の塗りつぶした点を指すだけに。自信 中。
- [minor] 5 抄録の 3 層の数: abstract.tex:11-15。解消: 前線は R7(0.5) の 1 組、探索は値を出さず「粗い形の照合を大きく上げた」、約 250 語。自信 中。
- [nit] 6 discussion.tex:58 "The results are material for three choices" の後に観点 5 つ → 数を書かないか five。SDC の対応づけを別の段落に。自信 高。
- [nit] 7 threat-model.tex:168 "like the better of the two versions of A3 on R3-u" が未定義の R3-u・A3 を参照 → 参照を添えるか例を消す。自信 高。
- [nit] 8 discussion.tex:31 "KeyTAR, run with the defaults of its artifact (\S\ref{sec:attackers:list})" の参照先に既定値の記述が無い → 付録 C へ。自信 中。

## 5. 推奨: minor
前の round の major 3 件は表の値と合う形で直った。残るのは持ち帰りの質（探索の値の範囲・探索の後の前線・得点との関係のずれの広がり）と冗長さで、1〜2 文の置き換えと削除で直る。

## 6. 読めなかった範囲・注入の疑い
接地は grep の周辺。付録は一部（appendix-exploratory 60-104・いくつかの生成表）。references.bib・appendix-checks・enja・attackers・事前登録は読んでいない。注入の疑い: なし。
