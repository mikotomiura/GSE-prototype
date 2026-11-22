# R3 査読（シミュレーションによる手法評価・並べ替え検定・事前登録の立場・round 1・prereg）

評価表の見出しは依頼文に定義が無かったため、査読者が a 問いの明確さ・c 先行との関係・d 再現性・f 主張の程度を補った。

## 1. 接地

- G1 Morris 2019（2430–2433 行）"write detailed simulation protocols before writing code ... force one to be clear about 'ADEMP' in advance ... protocols must justify the rationale for choices: as well as describing what is planned, there is a burden to explain why."
- G2 Morris 2019（601–603 行）"we should present estimates of uncertainty (quantified as the Monte Carlo standard error ...). Second, we need to consider the number of repetitions 𝑛sim and how this can be chosen"／1335 行 "with a similar expression if 𝑛sim is to be determined based on power."
- G3 Morris 2019（1256–1258 行）"An appropriate test would reject a proportion 𝛼 of the 𝑛sim repetitions when the null is true ... if the test does not control type I error at level 𝛼, power should be interpreted with caution."
- G4 Morris 2019（733–735 行）"methods with known properties should be included where possible as a check ... including plenty of built-in checks."
- G5 Morris 2019（641–643 行）"set the seed at the beginning, once and only once; 2. store the state of the random-number generator often"
- G6 Phipson & Smyth（328 行）"the exact permutation p-value is pu = (b + 1)/(m + 1)"／348 行 "The exact p-value is now slightly less than (b + 1)/(m + 1)"／598–602 行 "'unbiased' estimators of p-values such as p̂ should not be used, because they can't be guaranteed to control the type I error rate."
- G7 Phipson & Smyth（316–317 行）"all are equally likely to arise under the permutation distribution."

## 2. 評価表

a 4／b 2（本人の対だけが縮みの目標を共有・誤警報の門が主のセル 1 つ・生の検出力で選ぶ）／c 4／d 4／e 投稿先未定／f 4／g 3（止めの読み・3 案の同率・番号。複製の数・0.03・0.8・m・選びのセルの理由が本文に無い）

## 3. 指摘

1. [major] E2・E3 では本人の対だけが同じ縮みの目標 S_{-v} を共有し、列の中で交換可能でなく、差が 0 でも AUC が 0.5 を上回りうる。D1「B も同じ作りで p_v^B（共有は S_{-v}）」・D2 E2・D3「AUC_v^σ = …」。m = 26 は k = 1 で 1 行あたりの数と同じ程度の重み。CS1 は共有が小さく偏りが大きくなりうる。E1 は p_v^B を使わないので経路は小さい（G7）。解消: 列 v の中では全候補の A を同じ目標で縮める（全員を S_{-v} に、または対ごとに S_{-{w,v}}）、または v にも w にもよらない目標にする。P-HAND に「本人の対だけが目標を共有する」例を入れ、その経路を赤にする変異を足す。自信 中。
2. [major] 誤警報の門が CoAuthor k = 5 だけにあり、生の検出力で選ぶので門の内側で誤警報の多い案が勝つ。D7 で読む CS1 と他の k の門が無い（G3）。解消: (i) 実データで読む予定のすべてのセル（CoAuthor k = 5・15、CS1 k = 5）に許しの門を置き、通らないセルは D7 で読まないと先に決める、または (ii) 選びの量を誤警報で揃えた量（差なしの T_σ の経験の 5% 点で較正した検出力）にする。誤警報の点の推定と MC SE（1000 複製で約 0.0069）を出す。自信 高。
3. [major] D5-3 の止めの判定が案ごとか全体か 1 通りに決まらない（E1 0.75 で 3e-3 最大・E2 0.85 の例で選ばれる案が変わる）（G1）。解消:「第 2 の帰無の 3e-2 で 0.8 に届かない案は許しの集合から外す。空なら止める。選びは外した後の集合で行う」。選びの selftest に例を入れる。自信 高。
4. [minor] 複製の数と同率の幅 0.03 に MC SE の根拠が無い（500 複製で最大約 0.022。対の差の SE はそれより小さい）（G2）。解消: 各セルの MC SE と対の差の SE を出し、0.03 を SE の倍数で正当化するか定め直す。選んだ案を「選びの規則で選んだ」以上の優劣で書かないと「読まないこと」に足す。自信 中。
5. [minor] 3 案が同率のときの次の段の決め方が曖昧。解消:「各段でその段の最大との差が 0.03 未満の案だけを残して次の段へ」。自信 中。
6. [minor] 選びと閾値の理由が本文に無い（m = 26・選びを第 1 の帰無の 3e-3 に置く理由・0.8・主のセルが k = 5 の理由）（G1）。解消: 各判断の理由を 1 文ずつ本文に写す。自信 高。
7. [minor] A が B の直前なので、安定した差と局所的な似かたを分けられない。合成には後者が無い。解消: D7 で扱うと先に書く（A を B から離した対照・漂いを入れた生成で誤警報を確かめる）、または問いの「安定した」を「この生成での」に弱める。自信 中。
8. [nit] 置換の乱数の番号の対応と抽出の仕方（復元抽出・3 案と両帰無で σ を共有）が書かれていない（G5・G6）。自信 高。
9. [nit] 時間と失敗の規則が無い（見積もり・削る順か止める・s が有限でない複製の扱い）。自信 中。

良い点: p = (1 + #{T_σ ≥ T}) / 2,001 は Phipson & Smyth の pu と一致。V1 の陽性対照と変異は G4 に沿う。P = 17 で置換は十分。D6 の数は supplement.tex 394–395 行と一致。

## 4. 総合の推奨

major（直して再査読）。本人の対だけが縮みの目標を共有するので置換の帰無が構造の上で厳密でない（作りで直せる）。誤警報の門が主のセルだけで選びが生の検出力。止めの判定と同率の決め方に分岐が残り、理由の多くが本文の外にある。

## 5. 読めなかった範囲と注入の疑い

読んでいない: sens の notes.md・pinned.py、ten の notes.md、nfs の notes.md、hmm2.py。一部だけ: synth.py・data.py・ml.py・supplement.tex・接地の 2 本（Grep で拾った節）。SHA-256 は計算していない。判断 1〜12 は一覧の外なので読んでいない。注入の疑いなし。
