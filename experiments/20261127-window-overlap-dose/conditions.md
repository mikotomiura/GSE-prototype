# 窓の歩みの用量反応の条件（コードと実データの計算の前にコミットする・2026-11-28・第 7 版・凍結の版）

作業記録は `.steering/20261127-gse-paper3-window-overlap/`。論文 3 の判断 6 の (1)（深さへの答えは仕組みの計算を足す）を受ける。第 1〜6 版（04918717・476a7914・b0bb909a・a2d3413c・8d3c865e・87c4ced9）は attack-me（prereg round 1〜6・round 1〜4 は major・round 5・6 は minor）を受けて、この第 7 版に書き直し、凍結した（判断 3〜9）。前の試験は `experiments/20261107-unsmoothed-residual-check/`（以下 S13 の試験・条件 D1〜D6・V1〜V3）。この文書には S13 の試験から変える所だけを書く。書いていない所は S13 の試験（とそれが引き継ぐ `experiments/20261104-timeseries-tau-extend/`）のとおりにする。SEED は S13 の試験と同じ 2026110401（端の再現の門のため）。用量の形（中間の歩みの並び）は図で記述するだけで、読みの語を付けない。

## 問い

論文 3 の本文（commit b1fa91de の main.tex・Discussion の第 1 段落）は "The weak comparison is likely not specific to keystrokes: features computed over overlapping windows make consecutive inputs dependent, and a shared model whose structure misses that dependence makes a per-person fit look good. We have not checked this in other domains." と書き、確かめていない。S13 の試験は両端だけを見た。平滑を外し窓が 29/30 重なる列 u と、重ならない窓の列 n である。n では得（本人 hmm3 − 共有 hmm3）が縮んだ。ただし n は記号の数が約 1/30 で、縮みが歩みによるのか記号の数によるのかを分けられない（補足 S13）。

この試験は、窓の歩みを 1・5・10・15・30 秒と変え、同じ記号の数で歩みが違う比べを作って、次を問う。

- (a) 重ならない窓での得の縮みに対して、記号の数をそろえた歩み 1 の連続した区間ではどれだけの差が残るか（主の問い・型を決める）。
- (b) 本人 hmm3 が本人の連鎖に負けるか勝つかは、どの歩みで入れ替わるか（論文 3 の勧め (1) がどの記号化で効くか）。
- (c) 構造を ar3 に固定した比べ（本人 ar3 − 共有 ar3）の値（記述だけ・型を決めない）。仕組みの後半（従属を運べる構造の共有を相手にすると差が消える）は、歩み 30 の列の記号の数では本人 ar3 のデータの重みが小さくなりうるので、この試験では判定しない（判断 7）。

## 言い方の限り（どの結果でも守る）

句（日本語と英訳。英訳は本文にそのまま使う）:

- 句 (1)「平滑を外した記号（S13 の u）で」／ "in unsmoothed symbols"。この試験の記号はすべて u から作る。主の記号化（平滑あり）へは広げない。新しい節の、この試験を述べる最初の段落に「平滑した主の記号化では確かめていない」／ "this was not checked in the smoothed symbols of the main analysis" も入れる。
- 句 (2)「歩み（窓の重なり・予測の先の長さ・同じ記号の数で覆う時間の長さ。この試験は分けない）」／ "with the step (window overlap, prediction horizon and time covered by the same number of symbols, not separated)"。短い形「歩みの成分は分けない」／ "with the step's components not separated"。列 A（歩み s）と列 C（歩み 1 の連続した区間）は、同じ記号の数で、この 3 つが同時に違う。この試験は 3 つを分けない（窓の長さの列も、散らした短い束の列も作らない・判断 4・6）。「重なりが効いた」「重なりが従属を生む」と書かない。打鍵そのものが 1 秒先では続き 30 秒先では続かないことでも、連続した短い区間の中身がそろうことでも、同じ形は出うる。
- 句 (3)「記号の数はそろえたが独立な情報はそろわない」／ "the same number of symbols did not carry the same independent information"。列 C は歩み 1 の連続した区間なので、続く記号はほぼ写しで、独立に近い観測は列 A より少ない。列 C30 は約 22 行（約 22 秒）で、1 つの窓（30 秒）より短い。φ ≈ 0 は「記号の数だけが効く」だけでなく、「列 C の短い区間からは本人の当てはめが学べない」でも出る。
- 句 (4)「手順の全体の差」: 列 A と列 C の比べは、記号の作り・当てはめ・評価を含む手順の全体の差である。学習と評価のどちらが効いたかは分けない（判断 5）。限界に書き、本文の句には入れない。

句の置き方:

- 列 A と列 C の比べの結果を述べる文（型 1〜3 の新しい節の結果の文・Discussion の置き換えの文・main.tex 223 行に足す文・貢献の句と、境の文の列 C の部分）には、句 (1)・(2)（または (2) の短い形）・(3) を、その文そのものに入れる。比べを読まない文（型なし・外れの文）には句 (1)・(2)（または短い形）だけを入れる（比べを読まないので句 (3) は要らない）。下の英文はすべてそうしてある（P-READ が文ごとに照らす）。
- 列 A と列 C の比べを述べない差し込み（main.tex 136 行・337 行への句・勧め (1) の境の文の列 A の部分）には句 (1) だけを入れる。境の文は句 (2) の代わりに固定の括弧「（記号の数も歩みとともに減る）」を持つ。
- 新しい節の最初の段落は S12 と S13 の結論（平滑した主の記号化を含む）だけにし、この試験の句は次の段落の最初の文から入れる。

ほかの限り:

- 列 C は比べを作るための作りで、使う場面（新しいセッションの全体を予測する）の推定ではない。勧め (1) の境は列 A だけで述べ、列 C の句は「記号の数をそろえた比べでは」と限る。英訳で「列 C」の語を使わず "the same number of symbols from a contiguous stretch at the 1-second step" と書く。
- 「構造を ar3 に固定した比べ」は、論文 3 の主の強い比べ（構造と縮みを他人で選ぶジョイント）とは違う。この語を「強い比べ」と略さない。
- 型の名と文に「仕組みと合う」「仕組みを測った」「仕組みが確かめられた」と書かない。型 1 は「記号の数をそろえても差が残る形」、型 2・3 は「その予測を支えない形」と書き、支える側と支えない側の範囲をそろえる（どちらも「この比べでは」に限る）。読みの規則が仕組みを当てられるかは、合成のデータで確かめていない（判断 4）。新しい節に "The reading rules were not checked on synthetic data." を入れる。
- 中間の歩み（5・10・15）の並びには語を付けない。図で記述するだけで、文に「歩みが短いほど」のような勾配を書かない。例外は 2 つで、どちらも格子の歩みごとの符号を数えるだけである: 勧め (1) の境の文と、型 1 の条件「4 つの s のうち 3 つ以上で stay_G(s) > 0」。型 1 にだけ格子の条件を課すのは、支える側の読みを厳しくするためである。
- 型 1〜3 の文に因果の語（does not account for・because・drives を事実として）を使わない。対応のある差の中央値の記述（"the median paired difference …"）で書き、中央値どうしの「縮み」を量として比べる書き方をしない（中央値は加法でない）。
- 作りの確かめ（M − M_shuf）は、歩みで隣の記号の従属が変わったことの配管の確かめで、列 C の独立な情報の確かめではない。型の支えに数えない。
- 量は 1 記号あたりの対数尤度の差に固定する。予測の先が違う列の差を同じ尺度で引くので、S13 の「大きさを比べない」（notes の「読まないこと」）を、この試験の φ と stay の比べの範囲でだけ外す。記録の 1 秒あたりの値は出さない。
- 2 つのセル（k = 5・15）は同じ 17 人で学習のセッションも重なるので、独立の再現ではない。「両セルで」を再現の意味に使わない。
- 境の文と C2a の文は中央値の符号で書く。「中央値で」／ "the median" を入れ、良い側の割合を添える（本文の "for every writer" と粒度を分ける）。
- 1 人抜きと区間は、固定した書き手ごとの得点の集約の感度で、選びと当てはめを繰り返した頑健さでも、母集団の不確かさでもない。
- この試験は、既知の端（S13）に条件づけた追加の分析で、独立の確かめではない（独立の確かめには取り置いた 30% の書き手が要る・研究者は選んでいない）。
- 仮説の文: 仕組みの推測を残すときは、「〜と推測したが、確かめていない」か「〜と推測したが、この比べは支えなかった」の形でだけ書く。
- 結果を CS1・ほかの記号化・ほかの分野へ広げない。Uto2020 の作り（30 秒の枠・10 秒の歩み）は歩み 10 に当たるが、「Uto2020 の記号化でも成り立つ」と書かない。

## 結果を見る前に知っていること（開示）

条件を書いた者は、次を見たうえで歩みの段・量・読みの区切りを置いた。区切りが既知の端を見てから置かれたことは限界に書く。値は CoAuthor P15 の k = 5 / k = 15 の中央値（S13 の notes と補足 S13）。

| 量 | 歩み 1（列 A = S13 の u） | 歩み 30（列 A = S13 の n） |
|---|---|---|
| G = 本人 hmm3 − 共有 hmm3 | 0.140 / 0.155 | 0.043 / 0.096 |
| C2a = 本人 hmm3 − r1 | −0.558 / −0.566 | +0.298 / +0.140 |
| C2b = ジョイント − r1 | 0.049 / 0.012 | 0.351 / 0.140 |
| ジョイントの残り（ジョイント − 同じ構造の共有） | 5.8e-4 / 8.0e-4（補足 S13） | ジョイントが全員 hmm3 を選ぶので G と同じ（導ける） |
| r1 − 共有 hmm3（書き手ごとに G − C2a・中央値は近似） | 約 +0.70 / +0.72（導ける） | 約 −0.26 / −0.04（導ける） |
| ジョイントで選ばれた構造 | ar3 が 16 / 13 人（残りは ar2） | hmm3 が全員 |
| 共有 hmm3 の擬似残差の遅れ 1 の自己相関（x / y の軸・k = 5 と 15 をまとめた値） | 0.315 / 0.525 | 0.037 / 0.012 |
| 本人 hmm3（τ 他人）の同じ量 | 共有と同じ程度（u の範囲 0.24〜0.63） | 未見 |

- k = 1 の値（G は u で 0.087・n で 0.0008、C2a も）も見ている（S13 の notes の結果の節）。
- CS1 の値も見ている（C5 k = 5 の G は o 0.028・u 0.010・n −0.003、k = 1 も）。CS1 を作らないと決めたのは第 1 版（round 1 の前）で、理由は、引き継ぎが CoAuthor を勧めたこと・CS1 は休止の秒が約 72% であること・u で既に G が縮み n で符号が逆になり、φ の分母（約 0.02）が小さく定まらないこと。データの選びが既知の端を見た後であることは限界に書く。
- 列 C の G について数の見込みは持たなかったが、u では続く記号の持続が強い（r1 − 共有 hmm3 が約 +0.70）ことを知っていた。
- u の共有 hmm3 の遅れ 10 の自己相関（0.146〜0.457）も見ている。補足 S12（構造の埋め合わせの確かめ）の結果も見ている。
- CoAuthor の分析の単位は 875 で行は 588,227（S13 の notes の門の表）なので、1 セッションは平均約 672 行で、列 C30・A30 は 1 系列あたり約 22 行と見込める。
- 共有の構造の足りなさ D_s と、共有 hmm3 の残差の自己相関 ρ_h（下の D4）は、列 C（どの歩みでも 1 秒先）と列 A の比べで「列 C の側で大きい」になることが、作りと既知の値から見込める。D_s と ρ_h は型を決めず、作りの確かめとして扱う。
- 歩み 1 ではジョイントが ar3 を 16 / 13 人に選び、その書き手ではジョイントの残りが R_ar3（本人 ar3 − 共有 ar3）にほぼ重なるので、R_ar3 の列 A1 の値は 1e-3 程度以下と導ける。歩み 30 の列では学習の記号が 1 セッションあたり約 22 で、ar3（2,033 の母数）の本人のデータの重み N / (N + τ) は小さくなりうると見込める。R_ar3 は型を決めず記述にとどめる（判断 7）。R_ar3 の値そのものと共有 ar1 − 共有 hmm3 の値は、S13 の summary から導けるが、条件を書いた者は見ていない。
- 区切りを G の単位に直すと、φ(30) ≥ 1/2 は stay_G(30) が k = 5 で約 0.049、k = 15 で約 0.030 以上（開示の中央値から粗く計算した目安・実際の判定は対応のある差で取る）。
- 勧め (1) の境の端（歩み 1 で C2a が負・歩み 30 で正）は既知で、境を決めるのは中間の歩みだけである。
- 列 A の中間の歩み（5・10・15）・列 C と列 C′（下）のすべて・列 B（下）は未見である。主の読みは、既知の列 A の端と、未見の列 C の値を組み合わせる。

## D1 データ（変える所）

- データ: CoAuthor だけ。CS1 は作らない。
- 入力: S13 の試験の新しい中間（`$DATA_DIR/landscape/unsmoothed_residual_coauthor.json.gz`・manifest で照らす）の u の記号と、tau-extend の `data.py` の単位の pflag。行の時刻は、`data.py` が読む今の中間（`coauthor_work_obs`）の feat 行の第 1 列を、`data.py` と同じ選び・同じ並べで読む。読んだ単位の obs が `data.py` の系列と 1 つでも違えば、時刻の数が系列の長さと違えば、または系列の中で隣の行の時刻の差が 1,000 ms でない所があれば止める（記号化は t0 から最後の打鍵まで 1 秒ごとに 1 行を出す・kit の README）。
- 歩み s ∈ {1, 5, 10, 15, 30}（秒）。
- 列 A（歩み s・位相 1 つ）:
  - s = 1: u の全行（S13 の u そのもの）。
  - s ≥ 2: 系列ごとに、最初の行の時刻を t0 とし、時刻がちょうど t0 + 1,000 · s · j（j = 1, 2, …）の行だけを採る（kit の `thinned_mask(times, step_ms = 1,000 · s)`）。s = 30 は S13 の n そのもの。
  - s = 1 だけ規則が違う（kit の規則を s = 1 に当てると各系列の最初の行が落ちる）のは、端を S13 の u と一致させるためである。
- 列 C（歩み 1 のまま・記号の数を列 A の s に合わせる）: s ≥ 2 で、系列ごとに、列 A の s がその系列で採る行の数を n_A とし、u の連続した n_A 行を採る。始まりの行の番号は floor((L − n_A) / 2)（L はその系列の行の数）。乱数は使わない。
- 列 C′（区間の位置の感度）: 列 C と同じで、始まりだけを floor((L − n_A) / 4)（列 C′1）と floor(3 · (L − n_A) / 4)（列 C′3）にした 2 版。
- 列 B（記述だけ・位相 s 個）: s ≥ 2 で、系列ごとに位相 r = 0, 1, …, s − 1 の部分系列を作る。位相 r は、時刻 t − t0 = 1,000 · (r + s · j)（j = 1, 2, …）の行。位相 0 は列 A と同じ。各位相は独立の系列として当てはめと評価に入る。読みに使わず値を補足に並べる。
- 行が 1 つも残らない部分系列は落とす。単位とパネルの顔ぶれは全部の列で同じにする。学習か評価の記号が 0 の書き手はそのセルで欠けとし、人数を出す。pflag は行といっしょに採る。

## D2 単位と分け方・列の番号（変える所）

- パネル: CoAuthor P15（≥ 20 セッション・17 人）。k ∈ {1, 5, 15}。主のセルは k = 5 と k = 15。k = 1 は値だけを出す（S13 の端の再現の門のために作る）。
- 列の番号 c（乱数の流れと出力の名に使う）:

| 列 | A1 | A30 | A5 | A10 | A15 | C5 | C10 | C15 | C30 | B5 | B10 | B15 | B30 | C′1-5 | C′1-10 | C′1-15 | C′1-30 | C′3-5 | C′3-10 | C′3-15 | C′3-30 |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| c | 1 | 2 | 3 | 4 | 5 | 6 | 7 | 8 | 9 | 10 | 11 | 12 | 13 | 14 | 15 | 16 | 17 | 18 | 19 | 20 | 21 |

- A1 の c = 1 と A30 の c = 2 は、S13 の残差の v の流れの列の番号（u 1・n 2）と同じにする（端の再現の門のため）。合わせて 21 組。

## D3 EM（変える所）

- 構造・τ の格子・開始点・収束・切れ端（900 記号）・束・r1・事前分布・行（τ 固定の 9 行・τ 他人・ジョイント（他人））・相手（r1・同じ構造の共有）は S13 の試験と同じ。
- 乱数の流れ: EM は S13 の試験と同じ流れを全部の列で使う（データが違うので値は違う）。残差の v は `default_rng([SEED + 51, 0, 書き手の通し番号, c])`（S13 と同じ形・データの番号は CoAuthor 0）。
- 数式と駆動のコード: S13 の試験の `scripts/fit.py`・`scripts/residual.py`・`scripts/pinned.py`（とそれが読む tau-extend の `hmm2.py`・`data.py`・`ml.py`）を写さずに読み込み、列の読み込み（`load.py` の `load_column` に当たる所）だけを、この試験の読み込みに差し替える。読み込むファイルの SHA-256 は次の値で、run.sh の頭と provenance で照らす（外れれば止める）。
  - S13 `fit.py` 1a385200648e494edaaf0faf455f9b459a8a3aa454a3fac6fe37ec26e37c4a0c
  - S13 `residual.py` fe805fbbd504a2d204e50c39b29171340dc08087a459f7709844d029665b1017
  - S13 `load.py` d1daf1532caff1a192ac10d8e5e14caa41cde5587f386638e6cacf236573f092
  - S13 `pinned.py` 60dcf6b0b6519208421eab087d14903e84b908e148460e29f1c3df0d86bcb5fb
  - tau-extend `hmm2.py` d71f4c206789b2dd33e2acc1569ac69a75006be2d33de227f7f094456a3966bc
  - tau-extend `data.py` dd93d58b5f942e72a89c77023237eb22f9e6cfa5849aa4e318b74990f6d182e5
  - tau-extend `ml.py` 93a3935cef367f1702d2aa4d51715b428945be3dd29a1962aa7aaecaaf64701c
  - kit `variants.py` 8910312a2c9b067490ac1d746495feccc4b3b74688fc00a46456660130437807
- τ は列ごとに他人で選ぶ。データの重み N / (N + τ) は列と構造でそろわない。
- 母数と書き手ごとの値は repo の外（`$DATA_DIR/landscape/window_overlap_*`）。書き手の ID は書かず通し番号だけ。人は開かない。

## D4 量（書き手ごと・1 記号あたりの対数尤度の差）

書き手の集合: 各セル（k = 5・15）で、列 A1・A5・A10・A15・A30・C5・C10・C15・C30 のすべてに G の値のある書き手を共通の集合とし、φ・stay・shrink・C2a の比べはこの集合で取る（人数 m を出す）。M・D_s・ρ_h は k に依らないので、列 A と列 C のすべてに値のある書き手の集合で取る。m が 12 未満なら、その量は「欠けがある」とする。列どうしの比べは、同じ書き手の対応のある差の中央値で取る。

主の量（型を決める）:

- G（得）= 本人 hmm3（τ 他人）− 共有 hmm3。

主の量（型を決めない・勧め (1) の境）:

- C2a = 本人 hmm3（τ 他人）− r1。と、同じ歩みの r1 − 共有 hmm3。

作りの確かめの量（型の前に当てる・見込みどおりかを書く）:

- M: パネルの書き手の評価の単位の記号で、系列（部分系列）の中の隣り合う組だけから数えた遅れ 1 の相互情報量（Miller–Madow の補正: (使われた組の数 − 使われた左の記号の数 − 使われた右の記号の数 + 1) / (2 · 組の数) を引く）。M_shuf は、同じ記号を各系列の中で並べ替えた同じ量の、20 回の並べ替え（乱数 [SEED + 61, c, 書き手の通し番号, r]・r = 0〜19）の平均で、セッションの混ぜ合わせと表の疎さから出る分を表す。判定には M − M_shuf を使い、20 回の M_shuf の標準偏差も並べる。一定の系列（同じ記号だけの系列・並べ替えても変わらない）の割合と、記号のエントロピーの中央値も列ごとに並べる（記述・判定に使わない）。書き手ごとに求め中央値を取る。組が 0 か値が有限でない書き手はその列で欠けとする。組の数・使われたセルの数・plug-in の値を並べる。
- D_s（共有の構造の足りなさ）= 共有 ar1 − 共有 hmm3（どちらも w を除く共有を w の評価の単位で採点・本人のデータを含まない）。列ごとに 1 つ。
- ρ_h: 共有 hmm3 の擬似残差の遅れ 1 の自己相関（S13 の D4 と同じ作り）。x 軸と y 軸を別々に、書き手ごとに求め中央値を取る。有効な組の割合を並べる。列ごとに 1 つ。

記述の量（値を並べる・型に使わない）:

- R_ar3 = 本人 ar3（τ 他人）− 共有 ar3 と、τ = 10,000 の固定の行の同じ量。列 A1・A30・C30 の値と、stay_R(30) = 中央値_w(R_ar3,C30 − R_ar3,A30)。
- 構造（hmm3・ar3）・列・セルごとの、選ばれた τ と τ = 10,000 でのデータの重み N / (N + τ) の中央値（N は学習の記号の数の中央値）。
- ジョイントの残りと、ジョイントで選ばれた構造の人数。C2b。
- 本人 hmm3 の ρ_h と、本人 hmm3 と共有 hmm3 の ρ_h の差（軸ごと・列 A1 と列 C30）。
- 副の採点: 各系列（部分系列）の最初の記号を除いた差（G・C2a）。
- τ = 10,000 の固定の行の G。選ばれた τ の人数。
- 列 C の区間の秒の長さの中央値（列ごと）。
- セルごとの G_C30 > G_A30 の書き手の数と、G_A1 > G_A30 の書き手の数（どちらも / m）。
- 列ごとの、900 記号の切れ端が掛かった系列の数。
- 区間: stay_G(30) の、書き手の値を固定した百分位ブートストラップ（セルごと・2,000 回・乱数 [SEED + 4, 9, k]・9 は列 C30 の番号）。固定した得点の集約の感度。
- 語の揺れ: セルごとに、そのセルの G の語を、書き手を 1 人ずつ抜いた m 通りで当て直し、同じ語が出た数。固定した得点の集約の感度。

## D5 読みの形（結果を見る前に決めた・閾値と検定は置かない）

1/2・1/4・1.5・「3 つ以上」・12・ceil(12m/17)・30 秒は言い方の区切りで、検定ではない。

### G の語（主・セルごと）

各セル（k = 5・15）で、共通の書き手の集合の上で、s ∈ {5, 10, 15, 30} について次を取る。

- shrink_G(s) = 中央値_w(G_A1 − G_As)（列 A の歩み 1 から歩み s への縮み）
- stay_G(s) = 中央値_w(G_Cs − G_As)（記号の数をそろえた歩み 1 の区間との差）
- φ(s) = stay_G(s) / shrink_G(s)（shrink_G(s) > 0 のときだけ）

φ は 2 つの中央値の差の比である。歩み（句 (2) の 3 つ）だけが効けば φ ≈ 1、記号の数（ただし句 (3) のとおり独立な情報はそろわない）だけが効けば φ ≈ 0 になるが、書き手ごとの分解・寄与の割合・書き手の順位ではないので、「割合」「寄与」「越える」と書かない。分母に下限は置かない（下限は結果を見る前に決めても別の区切りを 1 つ足すことになり、k = 15 で分母が小さく比が揺れやすいことは限界と 1 人抜きの句で示す）。判定の順（最初に当たった語を採る）:

1. m < 12 → 「欠けがある」。
2. shrink_G(30) ≤ 0 → 「列 A で縮まない」。
3. φ(30) > 1.5 → 「比が 1.5 を超える」。
4. 「列 C では縮みが小さい」: φ(30) ≥ 1/2、かつ 4 つの s のうち 3 つ以上で stay_G(s) > 0。
5. 「列 C でも同じ程度に縮む」: |φ(30)| < 1/4。
6. 「列 C でかえって大きく縮む」: φ(30) ≤ −1/4。
7. どれでもない → 「形が定まらない」。

2 セルとも同じ語ならその語、どちらかが「欠けがある」なら「欠けがある」、それ以外で違えば「割れる」。

### 作りの確かめ（型の前に当てる）

- (i) 列 A の M − M_shuf の中央値が、歩み 1 で正で、歩み 1 から 30 へ下がる（値(1) > 0、値(1) − 値(30) ≥ 値(1) / 2、かつ隣の 4 組のうち 3 つ以上で値(短い歩み) ≥ 値(長い歩み)）。
- (ii) 4 つの s のうち 3 つ以上で、列 C の M − M_shuf の中央値が正で、かつ列 A より大きい（組の数は同じ）。
- どれかの列の M が「欠けがある」、または (i) か (ii) が成り立たなければ、型を付けない（型「外れ」）。
- D_s と ρ_h（x・y の両方）が、4 つの s のうち 3 つ以上で列 C − 列 A > 0、かつ s = 30 で > 0 なら「見込みどおり」、そうでなければ「見込みと違った」と書く。型は変えないが、「見込みと違った」なら補足の注に「共有の構造の足りなさか残差の自己相関が見込みと違った」と書く。

### 型（決定表）

| 作りの確かめ | G の語 | 型 | 名 |
|---|---|---|---|
| 通る | 列 C では縮みが小さい | 1 | この比べでは、記号の数をそろえても差が残る形 |
| 通る | 列 C でも同じ程度に縮む | 2 | この比べでは、記号の数をそろえると同じ程度に縮み、差が残るという予測を支えない形 |
| 通る | 列 C でかえって大きく縮む | 3 | この比べでは、記号の数をそろえるとかえって大きく縮み、差が残るという予測を支えない形 |
| 通る | 比が 1.5 を超える・形が定まらない・割れる・欠けがある・列 A で縮まない | なし | 形が定まらない |
| 外れる | どれでも | 外れ | 作りの確かめが外れた |

### 本文の文（英文で固定・<> は数を入れる所・k = 5 と 15 の値は「k = 5 / k = 15」の順で並べる）

語の英訳（本文と補足の英文はこの表の語だけを使う）:

| 語 | 英訳 |
|---|---|
| 列 C では縮みが小さい | the gap stayed at an equal number of symbols |
| 列 C でも同じ程度に縮む | the gap shrank about as much at an equal number of symbols |
| 列 C でかえって大きく縮む | the gap shrank more at an equal number of symbols |
| 比が 1.5 を超える | the ratio exceeded 1.5 |
| 形が定まらない | no pattern by the prespecified cut points |
| 割れる | the two cells disagreed |
| 欠けがある | fewer than 12 writers with all values |
| 列 A で縮まない | no shrinkage between the 1-second and 30-second steps |

新しい節の、この試験を述べる最初の段落の最初の 2 文（どの型でも）: "In unsmoothed symbols, we compared the same number of symbols taken either at a coarser step or from a contiguous stretch at the 1-second step, with the step (window overlap, prediction horizon and time covered by the same number of symbols, not separated); this was not checked in the smoothed symbols of the main analysis, and the construction check (lag-1 mutual information minus that of shuffled symbols) only checks that the step changed the dependence of consecutive symbols, not that the independent information was matched. The reading rules were not checked on synthetic data."

結果の文（新しい節）:

- 型 1: "In unsmoothed symbols, against the median shrinkage of the gain between the 1-second step and non-overlapping windows (<shrink_G(30)>), the median paired difference between the same number of symbols from a contiguous stretch at the 1-second step and the non-overlapping windows was <stay_G(30)> (ratio <φ(30)>), with the step's components not separated; the same number of symbols did not carry the same independent information."
- 型 2: "In unsmoothed symbols, the median paired difference between the same number of symbols from a contiguous stretch at the 1-second step and the non-overlapping windows was <stay_G(30)>, small against the median shrinkage of <shrink_G(30)> (ratio <φ(30)>), with the step's components not separated; the same number of symbols did not carry the same independent information, and a per-person fit may learn little from such a short stretch."
- 型 3: "In unsmoothed symbols, the median paired difference between the same number of symbols from a contiguous stretch at the 1-second step and the non-overlapping windows was <stay_G(30)>, below zero (ratio <φ(30)> to the median shrinkage of <shrink_G(30)>), with the step's components not separated; the same number of symbols did not carry the same independent information, and a per-person fit may learn little from such a short stretch."
- 型なし: "In unsmoothed symbols, the comparison at an equal number of symbols, with the step's components not separated, did not settle (<語の英訳>)."
- 外れ: "In unsmoothed symbols, changing the step (window overlap, prediction horizon and time covered by the same number of symbols, not separated) did not meet the prespecified construction check (lag-1 mutual information minus that of shuffled symbols), so no type is assigned (values in Supplement S<n>)."

留保の句（本文・型 1〜3 では新しい節の結果の文、223 行に足す文、貢献の句の 3 か所すべての直後に同じ条件で付ける。型なしでは新しい節の結果の文の直後だけ。外れでは付けない）:

- "(Same word in <n_5> of <m_5> and <n_15> of <m_15> leave-one-writer-out medians, k = 5 / k = 15; the scores were not refitted.)" どちらかのセルで n が ceil(12m/17) 未満なら "(The word is unstable when one writer is left out.)" を足す。
- どちらかのセルで stay_G(30) の区間が 0 をまたげば "(The interval spans zero in at least one cell.)"。
- 頭を外した採点で G の語が違えば "(Without the first symbol of each sequence the word is: <語の英訳>.)"。
- τ = 10,000 の固定の行で G の語が違えば "(With τ fixed at 10,000 the word is: <語の英訳>.)"。

結果の文の直後に付ける句（本文・新しい節だけ・外れを除く）:

- "(The contiguous stretch at the 30-second step lasts <秒> s in the median.)"（どの型でも付ける）
- "With the structure fixed at the three-state AR-HMM, the per-person data carried a median weight of <w_A30> and <w_C30> in the 30-second columns with τ chosen on others (<w'_A30> and <w'_C30> at τ = 10,000), and for the three-state HMM that decides the type <h_A30> and <h_C30> (k = 5 / k = 15); because a small weight can make the comparison with the fixed AR-HMM uninformative at so few symbols, this study does not judge whether the gap vanishes against a shared structure that can carry the dependence (values in Supplement S<n>)."
- 型 1 のときだけ: "Values only, not read: the lag-1 autocorrelation of residuals, per-person HMM minus shared HMM (median), was x <値> and y <値> at the 1-second step and x <値> and y <値> at the 30-second contiguous stretch." S13 の「読まないこと」（hmm3 の残差の自己相関を、本人の当てはめが足りなさを補ったかの確かめに使わない）はこの試験でも外さない。

補足の注（同じ節の表の注・英文）:

- 列 C′1 か列 C′3 で G の語が列 C と違えば "The word changes with the position of the stretch: <C′1 の語の英訳> (first quarter) and <C′3 の語の英訳> (third quarter)."。
- 作りの確かめで D_s か ρ_h が見込みと違えば "The shared-structure deficit or the residual autocorrelation did not follow the expected direction."。
- 一定の系列（同じ記号だけの系列）の割合と記号のエントロピーの中央値を列ごとに並べる（作りの確かめの記述・判定に使わない）。

Discussion の第 1 段落の置き換え: "The weak comparison is likely not specific to keystrokes: features computed over overlapping windows make consecutive inputs dependent, and a shared model whose structure misses that dependence makes a per-person fit look good. We have not checked this in other domains." の 2 文を、次の文に置き換える。

- 型 1: "In unsmoothed symbols and in this comparison, a median paired difference in the same-structure gain remained at an equal number of symbols when the step differed (window overlap, prediction horizon and time covered by the same number of symbols, not separated), although the same number of symbols did not carry the same independent information; the step boundary for recommendation (1) is given in Section X. We have not checked this pattern in other domains."
- 型 2: "In unsmoothed symbols, at an equal number of symbols, the median paired difference in the same-structure gain between the 1-second step and non-overlapping windows was small against their shrinkage, with the step's components not separated and the same number of symbols not carrying the same independent information. We had guessed that the step, rather than the number of symbols, drives this shrinkage; in this comparison, the prediction that a gap remains at an equal number of symbols was not supported."
- 型 3: "In unsmoothed symbols, at an equal number of symbols, the median paired difference in the same-structure gain between the 1-second step and non-overlapping windows was below zero, with the step's components not separated and the same number of symbols not carrying the same independent information. We had guessed that the step, rather than the number of symbols, drives this shrinkage; in this comparison, the prediction that a gap remains at an equal number of symbols was not supported."
- 型なし: "In unsmoothed symbols, the comparison at an equal number of symbols, with the step's components not separated, did not settle. We had guessed that the step, rather than the number of symbols, drives this shrinkage, and have not checked it."
- 外れ: "In unsmoothed symbols, changing the step did not meet the prespecified construction check, so the comparison at an equal number of symbols, with the step's components not separated, was not read. We had guessed that the step, rather than the number of symbols, drives this shrinkage, and have not checked it."

main.tex の結果の文（"…with non-overlapping windows, which give about one-thirtieth of the symbols, the \hmmthree{} beats the own chain in CoAuthor and its per-person fit beats the shared \hmmthree{} at $k=5$ and 15, which may also reflect the smaller amount of data (\Sref{13}).")は、", which may also reflect the smaller amount of data" を削り、"(\Sref{13})." の後に次の 1 文を足す（C2a の向きはこの文で述べず、勧め (1) の境の文で述べる）。

- 型 1: "In unsmoothed symbols and in this comparison, with the step's components not separated, the median paired difference in the per-person gain over the shared HMM between the same number of symbols from a contiguous stretch at the 1-second step and the non-overlapping windows was <stay_G(30)> (ratio <φ(30)> to the shrinkage), although the same number of symbols did not carry the same independent information (Section X)."
- 型 2: "In unsmoothed symbols and in this comparison, with the step's components not separated, the median paired difference in the per-person gain over the shared HMM between the same number of symbols from a contiguous stretch at the 1-second step and the non-overlapping windows was small against the shrinkage (ratio <φ(30)>), and the same number of symbols did not carry the same independent information (Section X)."
- 型 3: "In unsmoothed symbols and in this comparison, with the step's components not separated, the median paired difference in the per-person gain over the shared HMM between the same number of symbols from a contiguous stretch at the 1-second step and the non-overlapping windows was below zero (ratio <φ(30)>), and the same number of symbols did not carry the same independent information (Section X)."
- 型なし・外れ: "In unsmoothed symbols, a comparison of the per-person gain at an equal number of symbols, with the step's components not separated, did not settle whether the smaller number of symbols goes with that shrinkage (Section X)."

main.tex の記号化の段落の "our results concern this overlapping, smoothed form" の後に、どの型でも ", except the comparison of steps in Section X, which uses unsmoothed symbols" を足す。

main.tex の Discussion の "Relation to earlier findings" の段落の "so whether it holds for symbolizations like theirs is open" の後に、どの型でも "; a 10-second step was among those we varied in unsmoothed symbols (Section X), but other parts of their symbolization differ" を足す。

main.tex の要旨の "the second smoothing variant, these synthetic writers and wider candidate grids were added after seeing results" を、どの型でも "the second smoothing variant, these synthetic writers, wider candidate grids and a comparison of steps in unsmoothed symbols were added after seeing results" に替える。

勧め (1)（main.tex の "(1) compare per-person sequence models with at least the person's own first-order Markov chain …"）の文の後に、どの型でも境の文（下）を足す。

貢献 (1)（main.tex の "A finding: …"・平滑した主の記号化の発見）: どの型でも発見の文は書き換えず、文の末尾（"(Sections~\ref{sec:res-hmm} and~\ref{sec:res-protocol}; …)" の後）に次の 1 句だけ足す。

- 型 1: "An added comparison in unsmoothed symbols, conditioned on the known ends and with the step's components not separated, found in this comparison a median paired difference in the same-structure gain between steps at an equal number of symbols, which did not carry the same independent information (Section X)."
- 型 2・3: "In an added comparison in unsmoothed symbols, conditioned on the known ends and with the step's components not separated, the prediction that a difference in the same-structure gain between steps remains at an equal number of symbols was not supported; the same number of symbols did not carry the same independent information (Section X)."
- 型なし・外れ: "An added comparison in unsmoothed symbols, with the step's components not separated, did not settle this (Section X)."

序論（main.tex の "the natural comparison, a shared model of the same structure, is weak whenever that structure misses the dependence between consecutive symbols"）はどの型でも変えない。この命題は平滑した主の記号化での ar3 の比べが支え、この試験が問うのは、縮みが歩みと記号の数のどちらに沿うかだけだからである。

S12 と S13 の結論（数 1 つと読み 1 文）は、新しい節の最初の段落（この試験の句の前）に上げる。足す分は本文の他の所を移す・まとめるで埋め合わせる。どの型でも同じ基本の図 1 つを載せる（横軸 = 歩み。上の枠に G の中央値を列 A は実線・列 C は破線・列 C′ は細線で。下の小さな枠に D_s・ρ_h・M − M_shuf と、R_ar3（灰色の線・型を決めない量と注に書く）。2 セル）。

### 勧め (1) の境（列 A の C2a）

- 歩みごと（s ∈ {1, 5, 10, 15, 30}）に、2 セルの C2a の中央値の符号を「両方正」「両方正でない」「混ざる」「欠け」の 4 つのどれかに分ける。同じ歩みの r1 − 共有 hmm3 の中央値の符号も同じ 4 つに分ける。良い側の割合は、セルごとの、C2a > 0 の書き手の割合。
- 境の歩み s* = 「両方正」の歩みのうち最も短いもので、かつ s* 以上の格子の歩みがすべて「両方正」、s* より短い格子の歩みがすべて「両方正でない」か「混ざる」であるもの。
- s* があれば、本文の英文: "In unsmoothed symbols, when symbols were made from the same recording time at a grid step of <s*> s or longer (fewer symbols at longer steps), the median difference favoured the per-person HMM over the person's own first-order chain in both cells (share of writers favouring the per-person HMM at <s*> s: <p_5> and <p_15>, k = 5 / k = 15); at every shorter grid step it did not favour the per-person HMM in both cells at once, and both ends of this grid (1 s and 30 s) were known before the check." s* より短い格子の歩みに「混ざる」があれば続けて "(At <s の並び> s it favoured the per-person HMM in one cell only.)"。続けて、s* の r1 − 共有 hmm3 の分類が「両方正でない」なら "At that step the median difference also favoured the shared HMM over the own chain in both cells."、「両方正」なら "At that step the median difference still favoured the own chain over the shared HMM in both cells."、「混ざる」か「欠け」なら "At that step the own chain against the shared HMM differed between cells."。さらに列 C の s* の C2a の分類が「両方正」なら "In unsmoothed symbols, in the comparison at an equal number of symbols from a contiguous stretch at the 1-second step, with the step's components not separated and the same number of symbols not carrying the same independent information, the median difference also favoured the per-person HMM in both cells."、「両方正でない」なら同じ前置きで "the median difference did not favour the per-person HMM in both cells at once."、「混ざる」か「欠け」なら同じ前置きで "the two cells disagreed."。
- s* = 1 は起きない（歩み 1 は既知で負）。s* が無いか s* = 1 になったときは、歩みごとの分類を補足に並べ、本文には "In unsmoothed symbols, no grid step separated the steps at which the median difference favoured the per-person HMM over the own chain in both cells (Supplement S<n>)." を足す。

### 構造の選び（記述）

ジョイントで ar の構造を選ばれた書き手の割合を列ごとに表に並べるだけで、文の語を付けない。Pohle 2017 [V508] は、モデルの硬さで運べない構造を余分な状態が埋め合わせ、状態の数が多く選ばれすぎると述べた。ここで ar が選ばれるのは指定が 1 次の従属に合う向きで、その埋め合わせとは別の現象だと推測したが、確かめていない。G5 との関係は検定しない。

## D6 計算の量と場所

- 場所: Mac（研究者が決めた）。repo の外の仮想環境で、S13 と同じ Python 3.11 と numpy 2.4.4 を使う（uv で作る）。線形代数のライブラリは S13 の HP Z2（Windows）と違う。版と機械は provenance に書く。
- 実行の順: 列 A30 → 列 A1 → 端の再現の門 → 列 A5・A10・A15 → 列 C → 列 C′ → 列 B。
- 端の再現の門が外れたら、許容（相対 1e-9）を変えずに、HP Z2 で全部を回し直す（引き継ぎの文書を書く）。Mac の結果は notes に使わない。HP Z2 でも外れれば計算を止め、notes に外れた節と最大の差だけを書き、結果を論文に持ち込まない。
- 見積もり（コードを書く前の粗い値）: S13 の試験の HP Z2 で CoAuthor の 1 列が約 22 分。列 A1 と列 B の 4 組が記号の数で u とほぼ同じ、列 A・C・C′ の s ≥ 5 は合わせて 2 列ぶんより少ない。Mac の合成で時間を測ってから「条件の後の変更（実データを見る前）」として見積もりを書き足す。見積もりが 10 時間を超えれば列 B を外す（主の読みに使わないため・既定）。
- 本計算が見積もりを超えても、途中で歩み・格子・範囲を変えない。

## V1 門（実データ）

- P-PIN: D3 の SHA-256。
- 入力の照合: S13 の試験の manifest と同じ照合（食い違い・欠け 0）。時刻を読んだ単位の obs と `data.py` の系列の一致・時刻の数と系列の長さの一致・系列の中の時刻の差がすべて 1,000 ms。
- P-REPRO-U: 列 A1 の集計のうち、S13 の試験の `results/summary.json` の u・CoAuthor の葉（P15 の k = 1・5・15 × 4 構造 × τ 固定の 9 行・τ 他人・ジョイント（他人）× 相手 r1・同じ構造の共有 × 全記号・押下のある記号の中央値・四分位・良い側の割合・人数、共有 − r1、選ばれた τ・構造の人数、診断、残差の集計）を辿り、数は相対 1e-9、文字列・真偽・None は一致で照らす。区間・時間・run_id は照らさない。
- P-REPRO-N: 列 A30 を S13 の n・CoAuthor の葉と同じ規則で照らす。
- P-ROWS: 実データで、列 A の行の数が kit の `thinned_mask` の真の数と、列 C・C′ の系列ごとの行の数が列 A と、列 B の位相の行の数の和が t − t0 ≥ 1,000 · s の行の数と、すべての系列で一致する。外れた系列の数だけを出す。
- P-REPRO-U・P-REPRO-N が外れたら D6 のとおり。ほかの門が外れたら計算を止め、notes に外れた門と数だけを書き、結果を論文に持ち込まない。出すのは照らした数・外れた数・最大の差・外れた節の名前だけ。

## V2 陽性対照と変異（合成のデータだけ・実データの前に通す）

S13 の試験の selftest と、それが引き継ぐ tau-extend の対照は、読み込んだコードの selftest をそのまま回して通す。足す対照:

| 対照 | 通る条件 | 名指しの変異 |
|---|---|---|
| P-STRIDE | 列 A の印が、s ≥ 2 で kit の `thinned_mask(times, 1,000 · s)` とすべての系列で一致し、s = 1 で全行 | m61: s = 1 にも `thinned_mask` を当てる／m62: 行の番号（s 行ごと）で間引く |
| P-BLOCK | 列 C・C′ の系列ごとの行の数が列 A と一致し、行が連続し、始まりが D1 の式どおりで、系列をまたがない | m70: 列 C の始まりを 0 にする／m71: 行の数を列 A より 1 つ多くする |
| P-PHASE | 列 B の位相が互いに行を共有せず、合わせて t − t0 ≥ 1,000 · s の行の全部になり、位相 0 が列 A と一致し、系列をまたがない | m63: 位相 r（r ≥ 1）の頭に t0 + 1,000 · r の行を入れる／m64: 系列をつないで位相を切る |
| P-TIME | 系列の中に時刻の差が 1,000 ms でない所がある合成の入力で、読み込みが止まる | m76: 時刻の連続の検査を外す |
| P-MI | 既知の 1 次マルコフの合成の列（26 記号）で、(a) 20,000 組で Miller–Madow の M が真の相互情報量（0.5 nats 以上）の ±3% 以内、(b) 約 22 組の短い系列を 1 書き手あたり 30 本・20 書き手で、M − M_shuf（20 回の平均）の中央値が、独立の列では 0 の ±0.02 nats に、1 次マルコフの列では正に出る。系列の境目をまたぐ組を数えない。記号の分布が違う系列を混ぜた独立の列（系列の中は独立）で、M は正でも M − M_shuf は 0 の ±0.02 nats に落ちる | m65: 系列の境目をまたいで組を数える／m66: 周辺を全記号の頻度で取る／m77: M_shuf を系列をまたいで並べ替える／m80: M_shuf を 1 回の並べ替えにする |
| P-DS | 合成の書き手で、D_s が「w を除く共有 ar1 − w を除く共有 hmm3」の評価の対数尤度の差にちょうど一致する（出力の葉から作った値と、npz から読み戻して採点した値が一致） | m72: 全員の共有（w を含む）を使う |
| P-FIRST | 合成の書き手で、頭を除いた採点の対数尤度の和が、全記号の和から各系列の頭の記号の対数尤度を引いた値とちょうど一致し、記号の数が系列の数だけ少ない | m67: 頭の記号を除かずに分母だけ減らす |
| P-PAIR | 列どうしの差が、同じ書き手の対応のある差の中央値で、共通の書き手の集合（D4）だけで取られる。共通の集合が 12 人未満なら「欠けがある」になる | m74: 中央値どうしの差にする／m81: 共通の集合を列ごとの集合にする |
| P-SWAP | 列の読み込みを差し替えた駆動で、列 A1 の当てはめが、S13 の `fit.py` を u の列で直接回した結果と、合成の書き手 3 人で本人（全 τ）・共有・r1・診断までちょうど一致する | m68: 差し替えた読み込みで pflag を採らない |
| P-READ | D5 の語の関数と決定表と本文の英文の組み立てが、手で作った書き手の値の組で期待の語・型・英文を返す。組には次を含む: 開示の端の値（k = 5 で G_A1 0.140・G_A30 0.043、k = 15 で 0.155・0.096）に「歩みだけが効く」（全部の s で G_Cs = G_A1）を置いた組で G が「列 C では縮みが小さい」、「記号の数だけが効く」（全部の s で G_Cs = G_As）を置いた組で「列 C でも同じ程度に縮む」、G_C30 が G_A1 を大きく越える組で「比が 1.5 を超える」になること。作りの確かめで M − M_shuf が全部の列で負の組が「外れ」になること。型 1 と列 C の C2a が「両方正でない」の組で、223 行の差し替えの文と境の文が互いに食い違わないこと（223 行の文が C2a に触れない）。ほかに、各語・φ の境（1.5・1/2・1/4・−1/4）・shrink ≤ 0・m < 12・片方欠けの合わせ・2 セルの割れ・3 つ以上の境・決定表の 5 行・本文の句の 6 つ・1 人抜きの境 ceil(12m/17)（m = 17 と m = 15）・境の歩みの分類 4 つと単調でない並び（例 両方正でない・両方正・両方正でない・両方正・両方正）・s* の r1 − 共有 hmm3 の分類 3 つ・英文ごとに句の期待（型 1〜3 の比べの結果の文と境の文の列 C の部分は句 (1)・(2)・(3)、型なし・外れの文は句 (1)・(2)、比べを述べない差し込みは句 (1)）どおりに入っていること・語の英訳の表の語だけが使われていること・留保の句が型 1〜3 で 3 か所に同じ条件で付くこと・型 1 の残差の文に結論の語（supported など）が無いこと | m69: 「3 つ以上」を「2 つ以上」にする／m75: φ の分母を shrink_G(30) から G_A1 にする／m79: 作りの確かめの正の条件を外す／m82: 型 1 の結果の文から句 (3) を落とす／m83: 留保の句を新しい節だけに付ける |

- 変異の門は S13 の試験と同じ（出力先を空にし、実行の識別子・`mutate` 欄・終了コード 3・名指しの対照の `passed = false`）。
- P-MI の ±3%・±0.02 は配管の対照の通る条件で、実データの読みの区切りではない。

## V3 出力

`results/summary.json`（列ごとの節: 尤度の差の集計・R_ar3・D_s・ρ_h・M と M_shuf・構造と τ の人数・データの重み・区間の秒の長さ・書き手の数・切れ端の数・残差の集計・副の採点・対応のある差・φ・区間・語の揺れ）・`selftest.json`・`repro_check.json`・`rows_check.json`・`timing.json`・`provenance.json`・`tables.md`・`readings.json`（D5 の語と型と本文の英文を機械で組み立てた結果）・図の元の CSV（中央値だけ）。集計値だけで、書き手・セッションの番号を書かない。

## 限界（結果の前に書く）

- 歩みは、窓の重なり・予測の先の長さ・同じ記号の数で覆う時間の長さを同時に変える（句 (2)）。窓の長さを変えて歩みを固定する列と、歩み 1 の短い束を全体に散らす列は、次の試験の候補である（窓を変えると特徴の意味も変わる。休止の数などの基準値は 30 秒の窓のもの）。
- 列 C は列 A と記号の数がそろうが、独立な情報はそろわない（句 (3)）。列 C30 は約 22 行で 1 つの窓より短い。φ ≈ 0 は、記号の数が効くことのほかに、列 C の短い区間からは本人の当てはめが学べないことでも出る。この試験はこの 2 つを分けない。
- 列 A と列 C の差は手順の全体の差で、学習と評価のどちらが効いたかは分けない（句 (4)）。列 C は評価でもセッションの頭を外す。区間の位置は列 C′ の 2 版で感度を見るが、連続した区間と散った行の違いそのものは残る。列 C は使う場面の推定ではない。
- 仕組みの後半（従属を運べる構造の共有を相手にすると差が消える）は、この試験では判定しない（R_ar3 は記述だけ・判断 7）。仕組みの環のうち「本人の当てはめが共有の運べない従属を運ぶ」は副の量で、歩み 1 では本人と共有の残差の自己相関が同じ程度と既に分かっている。
- D_s と ρ_h の向きは作りと既知の値から見込めるので、型の支えに数えない。
- φ は中央値の差の比で、書き手ごとの分解ではない。k = 15 では分母（約 0.06）が小さく、比が揺れやすい（分母の下限は置かない）。
- 2 つのセルは独立の再現ではない。1 人抜きと区間は固定した得点の集約の感度である。
- この試験は既知の端に条件づけた追加の分析で、独立の確かめではない。勧め (1) の境の端 2 つも既知である。
- 列 B は記号の数をそろえるが情報はそろえず、学習の系列の頭の数と履歴の長さも変える。値は記述にとどめる。
- 切れ端（900 記号）は s = 1 の長い系列にしか掛からないと見込む（列ごとに掛かった系列の数を出し、s ≥ 2 で 0 でなければこの文を直す）。
- 区切り（1/2・1/4・1.5・3 つ以上・12・ceil(12m/17)）は既知の端を見てから置いた。データを CoAuthor に絞ったのも、CS1 の既知の端を見た後である。φ(30) > 1.5 を型なしにするのは、列 C の得が列 A1 を大きく越える形は歩みの効きとしても説明しにくく、列 C の短い区間が別のものを測っている徴候かもしれないからである。φ の定義は、round 2 の査読で、開示の値から第 2 版の区切りでは k = 15 で歩みだけが効いても語が付かないと分かった後に置いた。
- 読みの規則が仕組みを当てられるかを、書き手の差と従属を別々に置いた合成のデータで確かめていない（P-READ の手で作った組は規則の配管の確かめ）。
- 作りの確かめ M − M_shuf はほぼ必ず通り、型の支えに数えない。強い持続で並べ替えても変わらない系列（一定の系列）があると 0 に近づきうる（一定の系列の割合を並べる）。
- 17 人の中央値で語が決まる（1 人抜きの一致の数を文に添える）。

## 計算の前に決めたことから外れるときの扱い

S13 の試験と同じ。実データを見る前なら `decisions.md` に判断として書き、この文書の末尾に「条件の後の変更（実データを見る前）」として足す。凍結（attack-me を閉じた後の commit・この第 7 版）の後は、歩み・列・量・読みの語・型・本文の英文を変えない（英文の文法の直しは、意味と語の強さを変えないものだけを、逸脱として notes に書いて行う）。変えるなら新しい版として凍結し直す。実データを見た後は変えず、止めて研究者に聞き、逸脱として notes に書く。

## 条件の後の変更（実データを見る前）

（まだ無い）
