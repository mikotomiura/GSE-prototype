# R2 査読 round 2（作文の過程の研究の立場・記録を公開する側と使う側）

総合の推奨: minor（直してから凍結）。14 件は解消 10・一部 4（#1・#2・#4・#10）・未解消 0。

## 1. 接地
- S1 KLiCKe §4.1 "We then analyzed the truncated logfiles (in .idfx formats) using Inputlog 9.0 to generate a set of keystroke indices"
- S2 KLiCKe Table 5 R-burst "The mean length of the string of actions delineated by an insertion or deletion exceeding 2 seconds and is measured in characters." ／ interval variance "The standard deviation of the production rates for the 10 intervals in each writing process in relation to a task maximum."
- S3 KLiCKe §2.1.5 "• Pause Time. Represents the time between two consecutive key presses (i.e. Press downy - Press downx)."
- S4 KLiCKe §2.2 "instances where substantial text appeared to have been pasted from external sources were detected ... Any files that were deemed flawed based on these criteria were excluded from the dataset." ／ 限界 "it does not fully capture the range of writing practices"
- S5 KLiCKe "researchers using the KLiCKe corpus for writing quality studies should consider potential prompt effects."
- S6 Conijn 2019 "it is important to be mindful when deriving conclusions from individual keystroke features, because they are already sensitive to small differences in writing tasks." ／ "caution should be taken when generalizing the effect of these features across tasks"

## 2. 引き継ぎの判定
一部: #1（最終稿と配布の本文が一致しない書き手で語への写し方が無い）・#2（検査の 4 の「真の対応から数えた値」の定義と誤差が大きいときの分岐が無い）・#4（操作の定義と基準の値が未固定・可否の表と近似の規則の食い違い）・#10（おとりが学習用の本文を含む）。他は解消（#3・#5・#6・#7〔KLiCKe §3.3 の "from the first keystroke to the last change made to the text before submission" と一致〕・#8・#9・#11・#12〔正義の項に中身が無い nit〕・#13・#14）。

## 3. 評価表
a 4（KLiCKe の選別と課題の形の限定が欠ける）／ b 3（Pause Time・有用性の基準・おとり）／ c 3（順位相関だけ・形の選び方が未定）／ d 3（A3 の行・区間の記録の行が長い 1 セル）／ e 4 ／ f 4 ／ g 3（有用性の式・基準・不確かさ・標本・検査の 3・4 の分岐）

## 4. 指摘
- [major] M1 表に無い列（Pause Time など）の既定の扱いが無い（prereg:81・:90）。Pause Time が丸めずに残ると R3-t は時刻を丸めた形にならず R3 − R3-t の対比が意味を失う。解消: 「表に無い列は R0 以外の全形で削除」を既定に・時刻から派生する列は丸めた down から計算し直すか削除。自信 中（配布の CSV にあるかは未確認）。
- [major] M2 有用性の 10 指標の操作の定義と基準の値（R0）の出どころが未固定（:166・config の名前だけ）。KLiCKe は Inputlog 9.0 で出した。解消: (i) 計算式を config に書き、R0 の自前の値と Inputlog の値の一致を取得の後の検査に（例 50 人・順位相関と絶対差）(ii) R0 の基準を Inputlog の出力そのものとし加工した形は自前の近似。自信 高。
- [minor] m1 可否の表の「○」（R3・R3-u の P-burst など）と近似の規則（字の数は字の押下の数）が食い違う（:172・:180）。解消: R0 と同じ入力で計算できるときだけ「○」と定義し直す。自信 中。
- [minor] m2 おとりに学習用の本文が入る（:145）。(a) 攻撃者は除ける (b) A3・A2-b の推定に含まれる。解消: 使わないと明記し評価用だけのおとりを副次に、またはおとりを評価用に限る。自信 中。
- [minor] m3 KLiCKe の選別（貼り付けの多い記録の除外）と課題の形（30 分・議論文）の限定が「結論に使わないこと」に無い（:233-240・:195）。解消: 1 項を足す。自信 高。
- [minor] m4 有用性の一致を順位相関だけで測る（:182）。解消: R0 に対する比の中央値（または平均の差）と範囲を加える。自信 中。
- [minor] m5 形の選び方の図が前もって決まっていない（:186）。解消: 横軸 = 最も強い攻撃者の倍率、縦軸 = 順位相関の中央値、Pareto の前線にある形を記述する図を固定。自信 中。
- [minor] m6 有用性の標本と不確かさが未固定（:182・:154）。解消: 除外の後の全員・書き手単位で課題で層別した 2,000 回のブートストラップ。自信 高。
- [minor] m7 検査の 3・4 の結果による分岐が無い（:72・:73・:77）。解消: 窓の正解は最終稿と配布の本文の語を空白の正規化の後に揃えて写す・写せない窓は使わず数を報告・一致の割合は表に添えるだけ。自信 中。
- [nit] n1 Menlo の「正義」が名前だけ（:224）。
- [nit] n2 carryover-R2.md の「d00cf09e」と context-A.md の「f118a7e2」が違う。

## 6. 読めなかった範囲・注入
klicke2025.txt の 1–339 行は grep の該当行だけ・945 行以降はほぼ読んでいない。conijn2019.txt は 332–361・780–849 と grep。書誌の本体と context-B.md は読んでいない。配布の CSV に Pause Time があるかは確かめていない。注入の疑い: 無し。
