# R3 の査読（round 2・paper-reviewer の応答の写し）

推奨は minor（直してから凍結）。round 1 の 9 件は 8 件が解消・1 件が一部。新しい指摘は major 2・minor 3・nit 3 で、どれも追記の中で閉じる直し。

## 1. 接地

- G1（Morris 2019, Table 1）: "Set the random number seed once per simulation repetition." / "Store the random number states at the start of each repetition." / "If running chunks of the simulation in parallel, use separate streams of random numbers"
- G2（Morris 2019）: "Include Monte Carlo SE as an estimate of simulation uncertainty." / "failing to report measures of uncertainty would be unacceptable in medical research."
- G3（Morris 2019 §3）: "Simulation studies provide us with empirical results for specific scenarios." / "it is very common to vary the sample size of simulated datasets because performance often varies over 𝑛obs"
- G4（Morris 2019, Table 1）: "For less-used performance measures, give explicit formulae for the avoidance of ambiguity."
- G5（Phipson & Smyth 2010）: "the exact permutation p-value is pu = (b + 1)/(m + 1)" / "The moral is that p-values must be directly evaluated as probabilities, not treated as if they were unknown parameters to be estimated in a statistical model."
- G6（Phipson & Smyth 2010）: "Permutation assumes that the items being permuted are statistically independent"

## 2. 引き継ぎの判定

1. CS1 の読みが E3 に依っていた → 解消（:123 の値は cs1_spread_summary.txt の wide の E1 と一致）。拾わなかったときの文の大きさに新しい穴（m1）。
2. 実データの量と c の較正の量のずれ → 一部（:115 と :119。CoAuthor では c を決めた帰無の量の範囲が表に無い・M1）。
3. パネル外の構成 → 解消（:70・:128）。
4. 文の型の穴 2 つ → 解消（:81〜86・:118）。
5. r の鍵・置換の SE → 解消（:68・:69・:66）。SE の書き方に nit（n1）。
6. 課題の組み合わせ・判定の名 → 解消（:127・:100）。
7. 補正しない文の強さと 0.37 → 解消（:76）。
8. 30% の取り置き → 解消（:63）。特定のしかたに nit（n2）。
9. 論文 3 の数の出どころ → 解消（supplement.tex 262・263・356・359 行と一致）。

## 2b. 評価表

- a 4: CoAuthor の値は notes.md:36・51 と一致。CS1 の値は一覧の中に出どころが無く照合していない。CS1 の拾わなかったときの文は上限を言い過ぎ（m1）。
- b 3: 代替説明は限界として書かれたが、基準線を判断に使う道に検定も文の型も無い（M2）。量の範囲の帰無の取り違え（M1）。
- c 3: 主のセルの 1 文に絞ってあり範囲は明確。推奨は探索の版なので薄い。
- d 3: 約 6,300 字。読まないことが 5 か所に散る。CS1 の節が (3) から離れている。
- e 投稿先未定。
- f 4: 置換の p は Phipson & Smyth の pu の形。[V562] にも触れている。交換可能性の前提を実データの書き手の不均一のもとで明示することが抜けている（:117）。
- g 4: 残る余地は M1・M2・m2。

## 3. 指摘

- [major] M1. CoAuthor の c の較正の範囲を、c を決めていない帰無で測っている
  - 位置と引用: :115「11 群 × 1,000 複製（種 12000〜12999）。第 2 の帰無（HP Z2）の分は数えていない。」と :119「合成の CoAuthor の c は第 2 の帰無の 95% 点で決まり」。notes.md:49 も同じ。
  - なぜ問題か: 「c の較正の範囲外」の規則（:117）は c を較正した合成の量の範囲に入るかを問うが、CoAuthor で c を決めたのは第 2 の帰無で、表は第 1 の帰無だけ（G3）。
  - 解消の条件: (i) 凍結の前に第 2 の帰無の差なしの筋の範囲を数えて表に足し、CoAuthor では c を決めた帰無か両方の和の範囲を規則にする。(ii) 数えないなら「CoAuthor の範囲の判定は c を決めた帰無の範囲ではない」と限界に書き、範囲内でも「c の較正の範囲内」とは書かない。
  - 自信: 高
- [major] M2. 頻度だけの基準線の読みが固定されていない
  - 位置と引用: :67「E1 の T と並べ、E1 が頻度を超えて遷移で近さを拾っているかを見る記述に使う」。:75。:59「門をかけていない」。
  - なぜ問題か: T − t0 に帰無の分布は無く、基準線は較正されていない。E1 と基準線の拾う・拾わないの 4 通りに書く文が無い（G4）。
  - 解消の条件: (i) :67 の目的の文を消し、基準線は値を並べるだけで解釈には使わないと固定する。(ii) 使うなら 4 通りと T・t0 の大小の文を表で固定し、どの文も「遷移で拾った」と言わない。
  - 自信: 中
- [minor] m1. CS1 の拾わなかったときの文の大きさがセルによって合わず、上限も言い過ぎ
  - 位置と引用: :123
  - なぜ問題か: (a) k = 5 では 3e-3 で 0.91 なので k = 5 の大きさ（1e-3 以下）が決まっていない。(b) 格子は 3e-3 の次が 1e-2 で、「3e-3 以下」と書くと 3e-3〜1e-2 の差と食い違うかのように読める（G3）。
  - 解消の条件: セルごとに書き分け、「調べた格子で 0.8 に届かなかった最大の段（k = 1 は 3e-3・k = 5 は 1e-3）。次の段との間は調べていない」と書く。
  - 自信: 高
- [minor] m2. 量の規則に上限を超えたときが無い
  - 位置と引用: :117
  - 解消の条件: 「最小を下回るか最大を上回ったら範囲外」とするか、上側は範囲内として扱う理由を付けて 1 通りに書く。
  - 自信: 中
- [minor] m3. 「実データを読む前の凍結」を第三者が確かめる手段が無い
  - 位置と引用: :55「これを凍結するコミットが実データを読む前の凍結になる」
  - 解消の条件: 凍結のコミットのハッシュを外の時刻の付く場所に置くことを書くか、「凍結の時点は repo の履歴でだけ示す」と限界に書く。
  - 自信: 中
- [nit] n1. 「p = x ± SE」は推定量の誤差の幅に見える（G5）
  - 解消の条件: 「p = x（置換の引きの揺れの目安 SE = y・判定は x で行う）」の形に。
  - 自信: 中
- [nit] n2. 30% の取り置きを特定する手段が無い（data.py の load_* は work の下の全ファイルを読み、取り置きを外す処理を持たない）
  - 解消の条件: 取り置きの一覧（または取り置いた後のデータの置き場）と、その SHA-256 を出力に書く。
  - 自信: 中
- [nit] n3. 合成の値に MC SE が無い（:88・:123）（G2）
  - 解消の条件: 括弧で MC SE を添える。
  - 自信: 高

## 4. 総合の推奨: minor（直してから凍結）

- round 1 の 9 件のうち 8 件が解消。
- M1 は第 2 の帰無の量を数えて足すか限界として書くことで、M2 は基準線の読みの文を固定するか解釈に使わないと書くことで閉じる。
- m1〜m3 は文の書き分けと手当てで、新しい本計算を要しない。メインが照合できれば再査読なしで凍結してよい。

## 5. 読めなかった範囲と注入の疑い

- 読んでいない: run_eye.py・explore_eq_amounts.py・ml.py・SEED・v1 の notes.md。eye.py は乱数の鍵（121〜139 行）だけ。supplement.tex は該当の行だけ。Morris 2019 は Table 1 と §3 の一部。v1 の conditions.md は D3・D6・D7 の周り。
- 照合できなかった値: :88 の CS1 の合成の値と D9 の KL の ρ ごとの値（d6.json が一覧に無い）。
- 注入の疑い: なし。
