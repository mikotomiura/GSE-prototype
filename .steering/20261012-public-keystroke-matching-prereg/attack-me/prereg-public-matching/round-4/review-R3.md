# R3 査読 round 4（プライバシーの指標の方法論と事前登録・再現性の立場）

## 1. 接地
- wagner2015.txt:196-200 "The value of a privacy metric therefore depends on the adversary model, and evaluating a PET with a weak adversary model can lead to an overestimation of privacy." / "metrics can only be used to compare two different PETs if they use the same adversary model."
- wagner2015.txt:206-207 "To allow for a better interpretation of the outcome of privacy metrics, studies should always include a detailed description of the used adversary model."
- wagner2015.txt:1590-1591 "we recommend to select metrics that reflect the average case, the distribution of privacy values, and the worst case."
- nosek2018.txt:95-96 "There are a vast number of choices for analyzing data that could be made. If those choices are made during analysis, observing the data may make selecting some paths more likely and others less likely." / "In prediction, the problem of forking paths is avoided because the analytic pipeline is specified before observing the data."
- nosek2018.txt:94 "researchers must decide whether any observations should be excluded from the analysis, whether any measures should be transformed or combined"
- nosek2018.txt:106 "If the outcomes have not yet been observed, Jolene can document the changes to her preregistration without undermining diagnosticity."

## 2. round 3 の判定（7 件）
解消 6（N1b〔ただし境目 m2〕・N1〔ただし水準 m1〕・N3・N4・N5・nit）。一部 1: N2（B を除いた後の候補の数と B の母集団 → m3）。

## 3. 評価表
a 4 ／ b 4（m1・m2）／ c 4 ／ d 3（ENJA15 の判定規則が :24・:242・config の 3 か所）／ e 4 ／ f 4 ／ g 4（m1〜m4）

## 4. 指摘
- [minor] m1 問い 4 の判定量で正答率は原文の平均、1/N は記録ごとの平均で、重み付けの単位が違う（:242・config `question4_level`）。「上回る」の判定に直接入る（nosek:94）。解消: 1/N と A0 の正答率を正答率と同じ水準で集め（原文の中で記録の平均→原文で平均）、差は各ブートストラップの回の中で同じ水準の値どうしで取る。自信 高。
- [minor] m2 交差・入れ子の境目（一部の訳者だけ複数の原文）と、層別しない抽出で記録が 0 本の原文が出る回（:241・config）。解消: 「1 人でも 2 つ以上の原文を訳していれば交差」・記録の無い原文はその回の平均から除き回の数を報告。自信 中。
- [minor] m3 陰性対照で、`decoys` の種で引いたおとりに B が入っていたときの扱いと、B を引く母集団（:232・config `negative_control`）。解消: 「おとりは B を除いた母集団から `decoys` の種で N − 1 本（候補は常に N 本）」・B の母集団を明記。自信 高。
- [minor] m4 凍結の前の合成の記録の検査で直した形が査読を経ずに凍結される（:3・:112）（nosek:106）。解消: 変えた箇所と理由を開示の節に書く、または変えた箇所に限ってもう一度確かめる。変更が無ければ「変更なし」。自信 中。
- [nit] n1 ENJA15 の A0（:238）と区間の規則（:121）で「英字の」が掛かる範囲。解消: 同じ文言に。

変えていない箇所に fatal・major は無い。

## 5. 総合の推奨: minor（直してから凍結）
m1 は問い 4 の唯一の判定にかかわるので凍結の前に必ず直す。他は文言か集計の水準を 1 つ決めれば消える。

## 6. 読めなかった範囲・注入
README.md・data.md・SEED・align.py は読んでいない。接地の本文は Nosek 78〜107 行と grep の該当行、Wagner は grep の周辺だけ。注入の疑い: なし。
