# review-R2（manuscript round 3・個人化した行動のモデルの実務の立場・対象 c68dfc30）

## 0. 引き継ぎの判定
- M1 一部: 要旨 34・考察 274・結論 307 は範囲で並べた。ただし「up to $7\times10^{-3}$」は上限に読めるが α は格子の最下端（246「the multiplier is the lowest value of its grid」）で、平滑を軽くするほど残りは大きい。「格子の端での値」と書く必要。序論 48 は 7e-3 を出さない。
- M2 解消（235「Applied to the real 15-session panel, this rule returns a detection at $k=5$ and 15」・推奨 (3) の条件 283）。新しい穴は major 1・2。
- M3 解消（274 のパープレキシティ。exp(−0.19) ≈ 0.83 で正しい）。
- M4 一部: 165「With these symbols the gain over the same-structure shared model does not fall by two orders of magnitude」は入ったが要旨と結論に無い（major 3）。
- m1 解消（151）・m2 解消（242・278）・m3 一部（244 に 8 to 17、表は 0 (0.00) のまま）・m4 一部（結論 307 が要旨 34 をほぼ逐語でなぞる・+535 語）・m5 解消・m6 未解消（既知の未決 8）・n1 解消・n2 未解消（求めない）。

## 1. 接地
- Saeb 2017: "for this procedure to be meaningful, the relationship between the training and the validation set should mimic the relationship between the training set and the dataset expected for the clinical use."・"if the goal is prognosis, i.e., we want personal models that can predict future clinical states of a given subject, we can split the data based on time"・"The correct way for adjusting these hyperparameters is to further divide the training set into training and validation subsets, and then minimize the prediction error on those validation subsets rather than on the whole dataset."・"inaccurate results can mislead both clinicians and data scientists."
- Aalbers 2023: "To evaluate if our models perform better than random guessing, we compare against the MAEs of a "naive" but person-specific baseline model."・"We evaluated model accuracy on a person-to-person basis in out-of-sample observations."・"Although performance should be improved to make clinical application feasible"・"These findings are relevant for the implementation of algorithms in mobile health apps"

## 2. 評価表
a 3 / b 3（帰無は 1 つの作り・α は格子の端・軽い平滑での検出は未評価・合う帰無の下で 3e-2 まで何も確実に検出できない＝出力が強く縮められている）/ c 2（設計者が結局どちらを配るかが書かれない・重ならない窓で逆になることが要旨に無い・100% 本人側は差が無くても出る）/ d 3（4.4 第 1 段落は較正されていない帰無に 1 段落・考察で検出率を再掲・結論は要旨の再掲）/ e 4（要旨 249 語で直すと超える。削る当てが要る）/ f 4（Aalbers の 89%・80% は原文の 89.3% (200/224)・80.4% (180/224) と合う）

## 3. 指摘
- [major] 要旨・結論の「Neither value shows a per-person difference」は 7e-3 について根拠がない。34・307。陰性対照の残り 1.1e-3〜1.8e-3（237・固定の平滑）に対し、軽い平滑の実データは最大 6.7e-3（246・Table 3）。297「Detection at the lighter smoothing was not evaluated」・278「Not established: ... at the lighter smoothing」。Table 3 は k とともに 5.2e-4 → 6.7e-3・本人側 0.71 → 0.88〜1.00 で、本人の差があるときの形と食い違わない。Saeb「inaccurate results can mislead ...」。解消: 2 つの値を分ける（5e-4 は合う帰無の下で差の無い残りより小さい／7e-3 は帰無で評価していないので示すとも示さないとも言えない・k とともに増える）。自信 高
- [major] 新しい帰無の「2〜4 倍」は 2.4 倍の行き過ぎを割り引くとほぼ消える。237「two to four times the real remainder」「about 2.4 times the real one」・234 見出し。負の対照の残りは真のモデル（α = 0.03）とプロトコルの固定の平滑（α = 1）のずれから出るので、平滑の効きに比例して膨らむと考えるのが自然。2.4 で割ると約 4.6e-4〜7.5e-4 で実データの 4.1e-4〜7.6e-4 と重なる。「示さない」の方向は保たれるが「実データより大きい」「2〜4 倍」を根拠にする書き方（見出し・237・307）は成り立たない。237 の注意は閾と検出率のことで、この比べには触れない。4.4 と限界 297 では足りない。解消: 見出しと本文を「同じ程度の残りが差なしに生じる」に替え割り引いた幅を 1 文、または α = 0.1・0.3 の種での最頻値の利得と陰性対照の残りの関係で比例を示す。自信 中（比例は推論）
- [major] 重ならない窓では結論の向きが逆になるが要旨と結論に無い。165「with non-overlapping windows ... the joint choice picks \hmmthree{}, and the per-person \hmmthree{} ... beats the shared \hmmthree{} by $+0.043$ at $k=5$ and $+0.096$ at $k=15$ (17 of 17 writers at $k=15$) ... the findings of this and the next section hold for overlapping, smoothed symbols.」。Uto 型（57「10-second step」）は重ならない枠に近い。Saeb「the choice of the appropriate CV method depends on the application.」。解消: 要旨と結論に 1 文（重ならない窓では hmm3 を選び 0.04〜0.10 が残る・帰無で較正していない）。考察で Uto 型との関係。自信 高
- [major]「2 桁落ちる」は縮める前の量と縮めた後の量の比べ。276・34・237「no level was reliably detected」・235「3 to 16\%」。0.19 は τ = 0（158）、5e-4 は重み 0.06〜3% の出力。データと合う本人の差は 3e-2 まで否定されない（0.19 の約 1/6）。gain falls は本人の利得そのものが 2 桁小さいと読ませる。0.19 自体も主に構造の補修（163）。解消: 「プロトコルの出力（残り）が 2 桁小さい」とし、同じ段落で植えた差を強く縮めて返すので 3e-2 までは否定されないと書く。自信 高
- [major] 使う側の決定が書かれていない。34「Studies deciding for a whole panel whether to model each person」・274「whether the writers differ in ways this protocol cannot detect remains open.」。CoAuthor は ar3・τ = 1e6・重み 0.06〜3%、CS1 は共通そのもの＝実務上ほぼ「共通を配る」。費用（42）を払う理由が無いこと、検出できない差（3e-2 未満）を捨てる危険が書かれない。Aalbers「Although performance should be improved to make clinical application feasible」「These findings are relevant for the implementation of algorithms in mobile health apps」。解消: 考察の冒頭か推奨の前に 2〜3 文（返した決定と費用の帰結・捨てる差の大きさ＝パープレキシティで約 3% まで）。自信 高
- [major]「書き手の 100% が本人側」は差が無くても出るのに根拠のように並べる。237「with every writer favouring the per-person fit」・Table 2 の (1.00)・198「(16 or 17 of 17 writers)」・144 の 80% の規則。Aalbers「we compare against the MAEs of a "naive" but person-specific baseline model」。解消: 4.4 と Table 2 の注に「平滑のずれがあると本人側の割合は差なしでも 1 に近づくので証拠として読まない」、推奨 (3) の規則にも注意。自信 高
- [minor] 最初の帰無の検出率を 2 度（235 段落・278「Under the first null, planted differences below $10^{-2}$ were detected in at most 6 of 10 seeds, and the real panel passes the detection rule only there」）。解消: 2 文に縮め数値は S15 へ。自信 中
- [minor] 縮約だけの行の残り 2e-3（229「$+0.002$ (0.82)」・重み 24%）が見出しの 5e-4 と新しい閾 1.8e-3 を上回るのに論じない。解消: 4.2 か 4.3 に、この行に帰無の閾は当てられないと 1 文。自信 中
- [minor] 新しい帰無の作り方の 2 点: 146「only the true model and the calibration of the planted size differ」（g の較正が本文に無い）・237「the two seeds with a finite median」（−∞ の説明が無い）・目標値 +7.4e-4 がどの k か無い。解消: 各 1 句。自信 中
- [nit] 結論が要旨の再掲（307 と 34）。結論は実務の決定と記号化の条件に絞り 200 語未満に。自信 中

## 4. 総合: major
新しい帰無で固定の平滑での「示さない」は方向として保たれたが、2.4 倍を割り引くと「2〜4 倍大きい」は「同じ程度」になる。要旨と結論は 7e-3 も「示さない」とし、重ならない窓での逆転も要旨から読めない。実務家に向けて、返した決定と捨てる大きさが書かれず、「2 桁落ちる」は縮める前後の比べとして直す必要がある。

## 5. 読めなかった範囲と注入の疑い
- 読んでいない: kit README・references.bib（書誌は照合していない）・figdata の fig2_p15.csv。hmm3/ar1/ar3/joint の CSV と Table 2・Figure 2 は一致。
- 注入の疑い: なし。
