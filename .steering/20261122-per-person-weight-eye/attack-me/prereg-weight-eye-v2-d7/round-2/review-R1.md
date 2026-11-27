# R1 の査読（round 2・paper-reviewer の応答の写し）

## 1. 接地

- G1（Teh 2013・4.6 Sample Collection Interval）: "keystroke dynamics are to behavioral biometrics where variability of typing is expected appear across different sittings [ 95 ]. Therefore, several sessions of data collection would ideally leverage one's typing evolution."
- G2（Teh 2013・同節）: "the greater number of samples collected the more accurate and conclusive a test result can be from statistical point of view."
- G3（Shadman 2025・限界の節）: "various factors such as noise, different keyboards, typing on unfamiliar devices, physical condition, or urgency can affect a user's typing pattern or speed. Therefore, these factors need to be considered seriously when designing keystroke dynamics-based systems."／1025 行 "enrolling and testing with different keyboards affect keystroke dynamics performance"
- G4（Shadman 2025・847–848 行）: "the consequences of some other factors like differing amounts of samples needed to develop the model, individual or global threshold, the database size, etc."
- G5（Shadman 2025・399–403 行）: "Identification seeks to determine the identity of an unknown user from a pool of candidates based on their typing patterns."
- G6（Teh 2013・3.2 節）: "there may be a concern that the result obtained under such control setting may not reflect real world scenario."

## 2. 引き継ぎの判定

1. 量の規則 → 一部解消。(i) 最大を上回った場合の枝が無い。(ii) 範囲は第 1 の帰無だけで数えたが CoAuthor の c は第 2 の帰無で決まる（m1）。
2. 代わりの説明 → 一部解消。s0 の使い方に読みの文が固定されていない。頻度を超えた分は止まりの続き方（止まり→止まりの遷移）でも生じる（M2）。
3. 書き手の並べ順 → 解消（data.py 139・184 行と一致）。
4. 「示した」の強さと r → 解消。
5. g の並び → 解消。表の「拾う」が r = 0 の p ≤ 0.05 を指すことは明記されていない（nit）。
6. 閉じた集合 → 解消。
7. (4) の分岐 → 解消。k = 5 と k = 15 で割れた場合は新しい穴（m2）。

## 2b. 評価表

- a 4: 文は探索・補正なし・揃えの 1 回の引きに限られる。例外は CS1 で拾わなかったときの文（M1）。CoAuthor の値は notes と一致。CS1 の k = 1 の値は notes に無く、d6.json は一覧の外なので確かめていない。
- b 3: CS1 の揃えは実データでは合成 wide より強く間引く見込みが高く、拾わなかったときの文がそれを考えていない（M1）。s0 は止まりの続き方の違いを分けない（M2）。
- c 3: 主のセルを 1 つに決めたので持ち帰りは明確。s0 との比べが何を言えるかは決まっていない。
- d 3: 同じ限定が冒頭・(3)・(4)・読まないことで 3〜4 回繰り返される。
- e 投稿先未定。
- f 3: 機器・キーボード（G3）は「機器・環境」として読まないことに入っているが、CoAuthor で書き手ごとに機器が一定である見込みを頻度だけの基準線では分けられないと 1 文あると系譜に沿う。
- g 3: 残る余地は 5 箇所: 量の規則の最大の側（m1）、s0 の読みの文（M2）、k = 5 と k = 15 が割れたとき（m2）、止めた後の手順（m3）、E2・E3 の出力の扱い（m4）。

## 3. 指摘

- [major] M1. CS1 で拾わなかったときの文が、実データの揃えの強さに条件づけられていない
  - 位置と引用: 123 行「CS1 で拾わなかったときは「量の散らばりを寄せた合成で E1 が 0.8 に届かなかった大きさ（k = 1 で 3e-3 以下）の差か、差が無いことと食い違わない」と書く。」と同じ行の「実データの CS1 の量の散らばりが wide の作りに合っているとは書かない」。
  - なぜ問題か: 根拠は wide の合成の検出力で、揃えた後の量の比は nA/中央 0.13〜0.34・nB/中央 0.15〜0.28。実データの CS1 の held-out は補足 S2 の表（136 行）で「10,635 [2,965, 16,640]」。第 1 四分位でも中央の約 0.28 で、23 人の最小はそれよりかなり低い見込みが高い。(2) は中央に対する比を出すと決めているが、その値で文を変える規則が無い（G2・G6）。
  - 解消の条件: (a) wide の合成で揃えた後の n_A・n_B の範囲（または中央に対する比の範囲）を書く。(b) 実データの値がその最小を下回ったセルでは、拾わなかったときの文を「wide の合成の検出力の較正の範囲外。大きさの上限は言わない」に替える。k = 5 のセルでは上限が「1e-3 以下」になるので、セルごとの文も書く。
  - 自信: 中
- [major] M2. s0 の比べの読みの文が固定されておらず、止まりの続き方を分けない
  - 位置と引用: 67 行「E1 の T と並べ、E1 が頻度を超えて遷移で近さを拾っているかを見る記述に使う」。(3) の文の末尾「頻度だけの基準線は T = t0・p = p0」。127 行「頻度だけの基準線は止まりの割合のような周辺の頻度の差を映すが、それ以外の書き手の中で一定の条件は分けない」。
  - なぜ問題か: T_E1 と t0 の大小からどの文を書くかが無い（g）。T_E1 − t0 の帰無の分布は合成で計算していない。CS1 では止まりの秒が 0.082〜0.900（補足 S6・246 行）で、頻度を超えた分のかなりが止まりの続き方で生じうる。これは作業のしかたで、打鍵の遷移の差ではない（G3）。
  - 解消の条件: (a)「E1 と s0 の T と p を並べるだけで、両者の差についての文は書かない」と固定するか、(b) 差について書くなら文の型と止まりの続き方を含むことを固定し、読まないことに「E1 が s0 を超えた分は止まり→止まりの続き方の書き手の差を含み、打鍵の遷移の差とは読まない」と足す。
  - 自信: 高
- [minor] m1. 量の規則に最大の側の枝が無く、CoAuthor の c を決めた帰無の量が数えられていない
  - 位置と引用: 117 行・115 行・119 行
  - なぜ問題か: 最大を上回った場合が決まっていない。CS1 k = 5 の n_A は実データの中央 70,395（補足 S2）が合成の最大 63,338 を超えているので起こりうる。CoAuthor では c を決めた帰無と範囲を数えた帰無が違う。
  - 解消の条件: (a) 最大を上回ったときの枝を 1 つに決める（例: 範囲内と同じ報告をし「量が c の較正より多い」と添える）。(b) CoAuthor の範囲は第 2 の帰無の量で数えるか、第 1 の帰無だけで数えたことを限界として書く。
  - 自信: 高
- [minor] m2. (4) で k = 5 と k = 15 が割れたときの文が無い
  - 解消の条件: 「セルごとにどちらかの文を書き、セルをまとめた文は書かない」と足す。
  - 自信: 高
- [minor] m3. 止めた後の手順が決まっていない
  - 位置と引用: 71 行
  - 解消の条件: 「総数 0 のセルは「計算できない」と書いて残りのセルは進める。例外はコードを直して同じ鍵ですべてを回し直し、止めた時点で出ていた量と直した差分を記録する」のように固定する。
  - 自信: 中
- [minor] m4. 「E2・E3 は計算しない」と「合成と同じ作り」がぶつかる
  - 位置と引用: 59 行・63 行。eye.py の eval_cell は 3 案すべてを計算して返す（321–332 行）。
  - 解消の条件: 「同じ関数で計算されても E2・E3 の値は出力に書かない（または書いても読まず報告しない）」と決める。
  - 自信: 高
- [nit] g の並びの表の「拾う」の定義 — 「拾う = r = 0 の p ≤ 0.05」と足す。
- [nit] 多重性の脚注の「最大」 — 「約 0.37」とする。

## 4. 総合の推奨

minor（直してから凍結）。2 つの major は文の固定と枝の追加で消え、新しい計算はほぼ要らない（wide の n の範囲を数え直す程度）。止まりを除いた基準線を新しく足す道を選ぶなら作りが変わるので再査読を勧める。

## 5. 読めなかった範囲と注入の疑い

- 一覧の外で読んでいない: gen.py、selftest.py、d6.json、eq_amounts.json の本体、context-B.md。
- 一覧の中で読んでいない: v1 の conditions.md と notes.md、ml.py、run_eye.py の 130 行より後、supplement.tex の該当行より外、接地の 2 本の全文（grep の節だけ）。
- 注入の疑い: なし。
