# R3（UMUAI・方法論と再現性）round 7・commit 12e46857

## 1. 接地
- 基準 1 Varma & Simon 2006「Proper use of CV for estimating true error of a classifier developed using a well defined algorithm requires that all steps of the algorithm, including classifier parameter tuning, be repeated in each CV loop.」
- 基準 2 同「The parameter selection bias, on the other hand, is always negative.」・「for large K , there is a high probability that choosing the minimum resampled error will give a biased estimate of the true error.」
- 基準 3 同「Using these "null" datasets, we selected classifier parameter values that minimized the CV error estimate.」・「With "null" and "non null" ... data, we also tested a nested CV procedure」
- 基準 4 Liu & Meng（arXiv 1510.08539v1）「we predict each individual's response using the remaining n − 1 individuals ... The downside is that we base our accuracy assessment on observed prediction errors for individuals who do not necessarily match the target's background ... our inference will be less relevant.」
- 基準 5 同「our inferences can be hurt either by too much matching (not robust) or too little matching (not relevant).」

## 2. 引き継ぎの判定
M1 一部（7・13・47・64 行は直った。49 行「the smallest planted differences detected correspond to 36 nats at k = 15 and 108 at k = 5; the remainder corresponds to about 1.5 to 2.6」が埋めた量と返った量を並べ直す。解消: 検出された水準で返った量を nats で、それができなければ対の比べを外す）／M2 解消（12・49 行）／m1 解消（README 75〜80 行）／m2 解消（30 行「Within the final protocol」・63 行「may favour a smaller remainder」）／m3 解消（44 行・73 行）／m4 解消／n1〜n3 解消。

## 3. 評価表
a 3（選ばれた tau = 10^6 では per-person fit はほぼ prior mode で、4.4 の「残り ≈ 平滑の差」は構成上ほぼ自明・M-A。5 節に M1 の残り）／b 3（合成の検査が本物の選ばれ方を再現しているかが無い・CS1 は本物で共通、合成で tau = 10^6・M-B）／c 3（選ばれた tau の下で本人のデータが事後の擬似カウントに占める重みが本文に無い）／d 4（49 行の 5 節が過密）／e 4（照合のハッシュが投稿までに出ないとデータの可用性の声明が記号の段で閉じない）／f 4（Liu & Meng の版）。

## 4. 指摘
- [major] M-A 選ばれた tau = 10^6 では per-person fit がほぼ prior mode なので、4.4 の「残り ≈ 平滑の差」は構成から出る帰結に近い
  - 位置と引用: 13 行「ar3 ... is chosen in every cell with tau = 10^6 ... the remainder ... about the prior mode's gain over the shared model (4.4)」・65 行「At large shrinkage, a finite tau of 10^5 or more cannot be separated from the shared model or its prior mode.」・48 行「The remainder is of the size of the shared model's smoothing gap」・28 行「As tau grows the fit approaches the prior mode」
  - なぜ問題か: 選ばれた tau で fit が prior mode と区別できないなら per-person − shared ≈ mode − shared は等式に近く、4.4 は出どころの証拠にならない。一方 48 行の per-person − mode（−3.5e-4〜−1.6e-4）は残りと同じ桁で、65 行の「区別できない」と数の上で食い違う。格子の端（最大構造・最大有限 tau）が全セルで選ばれることも報告すべき（基準 2）。
  - 解消の条件: 選ばれた tau の下で本人の訓練記号が事後の擬似カウントに占める割合（例 n_person / (tau·Σshared + n_person) の中央値・k ごと）を数値で。65 行の「cannot be separated」を何を基準に区別できないかで書き直し、48 行との関係を 1 文で解く。4.4 の見出しを構成からの帰結を含む形に。tau 側の端も 6 節に。
  - 自信: 中（擬似カウントの正規化の単位が読み切れない）
- [major] M-B 合成の検査が本物のパネルの選ばれ方を再現しているかが示されていない（とくに CS1）
  - 位置と引用: 47 行「from 1e-3 in CS1 (where tau = 10^6 was chosen for every writer)」・14 行「under the protocol the shared model itself is chosen for every writer」・47 行「the real remainder exceeds the largest negative-control median」
  - なぜ問題か: 本物の CS1 は共通（tau = ∞）、合成の CS1 は tau = 10^6。生成器が本物の選択を再現していないので、「CS1 では 1e-3 から検出」を本物に移せない。移せるなら 14 行より強い読みが成り立つ。CoAuthor でも陰性対照で選ばれる構造と tau が本物と一致するかが無い（基準 3）。
  - 解消の条件: S15 と 4.3 に陰性対照で選ばれた構造と tau を本物と並べる。CS1 で一致しないなら合成の CS1 の感度を本物の解釈に使わないと明記するか較正し直す。一致するなら本物の CS1 の読みを 1 文。
  - 自信: 中
- [minor] 5 節の尺度の段落で埋めた量と返った量を並べる（49 行・M1 の残り）。解消: 返った量を nats で、または対を外す。自信: 高
- [minor] 選択の目的は chain に対する差で、主表の主な列は shared に対する差（30 行「the best median ... of their own per-person minus chain difference ... it is not the target writer's predictive accuracy」）。chain の列（4.3「against the chain +0.220 ... every writer」）に選択の楽観が乗りうる。解消: 3.3 か 6 節に「chain の列は選択の目的と同じ量・残りの列は目的ではない」と、偏りは他の人の値の側から来ることを 1 文。自信: 中
- [minor] 記号の列の照合ハッシュが投稿までに出ないとデータの可用性の声明が閉じない（75 行・README 79〜80 行・規程「explain how to access data supporting the results」）。解消: 投稿前にハッシュを公開して声明に載せるか、照合できない範囲を声明に明記。自信: 中
- [nit] Liu & Meng の版（74 行）。手元の本文は arXiv 1510.08539v1 だけで、15 行の言い換えは 1724〜1732 行と合う。解消: arXiv 版を引くか 2016 年版で照合。自信: 高

## 5. 総合の推奨: minor
引き継ぎ 7 件のうち 6 件解消・M1 は 5 節の 1 行だけ。新しい major 2 件は主張の立て直しでなく、計算済みの量を書き足し 4.4 の見出しを言い直せば消える。ただし合成の CS1 が本物の選ばれ方を再現していないと分かれば、CS1 の感度の文は取り下げか較正のし直しが要る（major 相当）。

## 6. 読めなかった範囲・注入の疑い
S1〜S15・Liu & Meng の 2016 年版・Varma & Simon の図表の画像は読んでいない。Liu & Meng の 122〜1656 行は grep だけ。注入の疑い: なし。
