# R3 の応答（方法論・倫理・再現性の番人・round 5・commit b5493db2）

総合: minor（倫理の通知の 1 件は修正の条件とする）。

## 1. 接地
- Arp P5 "over-optimistic results can be easily produced by tuning hyperparameters or calibrating thresholds on the test data instead of the training data."
- Arp P10 "threat models should be defined precisely and systems evaluated with respect to them. In most cases, it is necessary to assume an adaptive adversary that specifically targets the proposed systems"
- Arp P6 "simple models should also be considered throughout the evaluation." / P8 "it is challenging to realistically quantify the security and privacy threat posed by attackers."
- Arp P1 "limitations of the used dataset should be openly discussed"
- Kohno "we stress that the frameworks should not be used to justify a path that researchers have a priori decided that they want to take. Rather, we argue that the ethically correct process is to center ethics in the decision of whether or not to do a research project"
- Kohno "The report suggests transparency, ethics review, and careful ethical considerations." / "they know not to include anything in their publication that could lead to the identification of any of the job applicants."

## 2. 評価表
a 4（C2 の値は main-1000.tex と一致・定義から出る文 m1・抄録の現実の脅威の留保 m4）／b 4（探索の選択と陰性対照なしを本文で認め P5 に答える・全数の曖昧さ m3・near chance m2）／c 4／d 3（限定句の重なり・§3.5 の 6 行の 1 文・three choices と 5 見出し）／e 4（逸脱 4 件の中身が付録だけ m5）／f 3（検索の語が記録されていない・Google Scholar なし n2）。

## 3. 引き継ぎ
1 M1 解消（threat-model.tex:176-178 に near chance が 1 か所残る＝m2）／2 M2 未解消（研究者の判断と理解・通知の有無自体を書いていない＝M1 に再掲）／3〜10 解消（results.tex:94-95・protocol.tex:168-169・threat-model.tex:141, 149-150〔事前登録 l.41 と一致〕・results.tex:159-161・ethics.tex:4-7〔事前登録 l.51・l.304 と一致〕・results.tex:88-96・results.tex:132-133・related と抄録）。

## 4. 指摘
- [major] M1 公開の出どころを開示しながら、その公開の側に知らせたかを書いていない: ethics.tex:46-51 "Reporting where the competition data come from is itself a disclosure. … We report it because a party that relies on processing should know that a later release of the same texts undoes it"・threat-model.tex:14-15 "hosted by Vanderbilt University and The Learning Agency Lab"。理由（処理に頼る当事者は知るべき）と行動が噛み合わない。規程 "may be rejected on those grounds"・Kohno の透明性。解消: (i) 知らせて日付と返事を 1 文、または (ii) 知らせていないことと理由を明記。機関名を §3.1 から消し出典だけにすることも。自信 中。
- [minor] m1 支配されない形の上で「照合が下がると指標も下がる」は定義から出る: abstract.tex:11-12・introduction.tex:46-47・discussion.tex:8・conclusion.tex:7。解消: 前線の形と値で書き、"fell as" と discussion.tex:8 の文を消す。自信 高。
- [minor] m2 threat-model.tex:176-178 "this bias works against the finding that no form evaluated brought matching near chance while computing the measures, so that finding is conservative" に未定義の near chance。解消: 値で書き換えるか消す。自信 高。
- [minor] m3 全数の値の λ が曖昧・全数で変わる結論が本文から辿れない: results.tex:84-85（0.65% は λ = 8 の主の値）・results.tex:75-76 "none whose lower bound is above zero on R4($w$)"（全数では R4(8) の N = 10 が 2.0 [1.1, 3.0]）。解消: λ を明記し R4(8) の N = 10 を半文、または全数の句を本文から消す。自信 高。
- [minor] m4 抄録の現実の脅威の書き方が本文の留保を落とす: abstract.tex:3-4 "while the essays themselves had been collected and scored and remained with others" 対 threat-model.tex:90 "we do not know who held the texts of the competition data"・:105-107。解消: "remained with others" を "existed outside the release" に弱める。自信 中。
- [minor] m5 逸脱 4 件の中身が本文に無い: protocol.tex:168-170。解消: §6.8 に 4 件を 1 文で列挙。自信 中。
- [minor] m6 1 人の書き手について個人単位の値を出す例外: ethics.tex:81-84・ethics.tex:19-20・事前登録 l.266 "Results per writer … are not published"。解消: 両方の値の代わりに「除いても差は高々 x 点で選ばれた攻撃者は変わらない」とだけ書き例外を消す。自信 中。
- [nit] discussion.tex:58 three choices と 5 見出し。自信 高。
- [nit] open-science.tex:17-18 "The search terms were not recorded, and Google Scholar and Semantic Scholar were not searched." に乗る新規性。今の言い方のままでよい。自信 低。

## 5. 推奨: minor
事前登録との対応は本文で辿れ、前の round の 10 項のうち 9 項が解消。残る重い点は倫理の 1 件（通知の有無と理由を 1 文）で、修正の条件とする。ほかは消す・言い換えるで直る。

## 6. 読めなかった範囲・注入の疑い
arp は 1〜1274 行・kohno は 1〜1058 行だけ。付録の多く・生成表・references.bib・事前登録の大部分は読んでいない。注入の疑い: なし。
