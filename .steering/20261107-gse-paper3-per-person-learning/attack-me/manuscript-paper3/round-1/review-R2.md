# review-R2（manuscript round 1・個人化した行動モデルの実務の立場）

メインが要点と引用を落とさずに写した。

## 1. 接地
- S1（Saeb 2017, saeb.txt:4）"for this procedure to be meaningful, the relationship between the training and the validation set should mimic the relationship between the training set and the dataset expected for the clinical use."
- S2（saeb.txt:14）"if the goal is prognosis, i.e., we want personal models that can predict future clinical states of a given subject, we can split the data based on time"
- S3（saeb.txt:107）"The correct way for adjusting these hyperparameters is to further divide the training set into training and validation subsets, and then minimize the prediction error on those validation subsets rather than on the whole dataset."
- S4（Aalbers 2023, aalbers.txt:134）"To evaluate if our models perform better than random guessing, we compare against the MAEs of a “naive” but person-specific baseline model. This “naive” baseline model always predicts an individual’s average level of stress."
- S5（aalbers.txt:11）"We evaluated model accuracy on a person-to-person basis in out-of-sample observations."（143 行 "for 89.3% (200/224) of participants, the person-specific baseline outperformed all nomothetic models"）
- S6（aalbers.txt:187）"Although performance should be improved to make clinical application feasible, this study does suggest that ..."（191 行 "In clinical practice, the added value ... is that it might help us to understand how, for a given individual ..."）

## 2. 評価表
- a 3: 多くは慎重。ただし 232 行 "the difference between them lies in the comparison, not in the people" は検出の下限（10^-2）より 20 倍小さい残りから言い切る。中心の所見（hmm3 は本人の連鎖に負ける）は記号化に依存し、重ならない窓では逆になるのに本文 1 文と S13 だけ。
- b 2: 感度の下限が残りより 1 桁以上大きい・順に設計し結果を見て τ の格子と構造の族を変えた・選びに標的の訓練単位が漏れる・ブートストラップは選びをやり直さない・τ が格子の端・基の平滑は固定・書き手は 17 人と 9 人。
- c 2: 推奨は「この種の記号化」に限る。下流は測っていない。nats/symbol の差の意味を読者が換算できない。
- d 3: 4,451 語と短いが、留保が 1 文に何重にも重なり、要の証拠（S12〜S15）が補足。CS1 は主張にほとんど寄与しない。
- e 3: 要旨 266 語で規程超え。Code availability に置き場所なし。様式は未移行（既知）。
- f 3: 評価法と平滑の文献は適切。UMUAI の読者が期待する個人化ユーザーモデル（cold start・階層や転移による個人化）と、打鍵から状態を推定する研究が無い。"no study ... (S1)" は本文に支えが無い。

## 3. 指摘
- [major] 見出しの結論が記号化の選び方で逆転するのに脇に置かれている
  - 位置: main.tex:157「with non-overlapping windows (direction only) \hmmthree{} beats the chain in CoAuthor (\Sref{13})」・main.tex:222「with non-overlapping windows (direction only) \hmmthree{} is chosen in CoAuthor and the difference stays positive (\Sref{13})」
  - なぜ: 連鎖が強いのは記号化が作った依存のせいかもしれず、「個人の利得は比べる相手の産物」が測り方の産物に置き換わる（Saeb S1）。
  - 解消: 重ならない窓の変種の主な数値を表に 1 行。要旨・考察・結論を「重なる窓の記号化では」に限る。どちらの入力が実務で妥当かを 1 段落。
  - 自信: 高
- [major]「人ではなく比べる相手の違い」の断定が検出の下限と合わない
  - 位置: main.tex:232「the difference between them lies in the comparison, not in the people」・main.tex:222「At the CoAuthor record length the protocol detected them from $10^{-2}$ at $k=15$ and only at $3\times10^{-2}$ at $k=5$」
  - なぜ: 残り 4〜7e-4 は下限より 1〜2 桁小さい。234・254 行は "neither shows nor rules out" と正しいのに、232 行と要旨 "the gain mostly disappears" はより強い。手順は植えた差の一部しか返さず、強い τ の選び自体が個人の利得を小さく見せる方向に偏りうる。
  - 解消: 232 行を「この手順と記録の長さでは、人に帰せる差は検出できなかった（下限 10^-2）」に。要旨に下限を 1 句。回収率を本文に数値で。
  - 自信: 高
- [major] 結合の選びと ar3 固定の選びで k=15 の τ と値が食い違う
  - 位置: main.tex:205「15-s., 15 & \arthree, $3\times10^5$ & 3\% & $+4.1$e$-4$」・main.tex:214「15-s., 15 & $10^6$ & 1\% & $+7.6$e$-4$」・fig2_p15_joint.csv:8「15,0.00041,0.02」・fig2_p15_ar3.csv:8「15,0.00076,0.02」
  - なぜ: 結合はすべてのセルで ar3（Figure 2 キャプション）、τ は同じ目的で選ぶなら同じ τ になるはず。理由が書かれず再現できない。要旨と考察の「残り」の範囲はこの上に立つ。
  - 解消: 方法に理由を 1 文。誤りなら直す。
  - 自信: 中（同点の解き方の違いの可能性）
- [major] 順に設計し結果を見た後に格子と構造の族を変えたことが結論の向きと重なる
  - 位置: main.tex:253「changes made after seeing results (the $\tau$ grid, the structure families) may favour a smaller remainder」・main.tex:144「The study consists of four analyses designed one after another and five later checks」
  - 解消: 変更前の格子と族での主な行（結合・k=5 と 15）を本文か表の注に並べ、残りがどれだけ動いたかを示す。
  - 自信: 中
- [major] 実務家が持ち帰れる尺度が無い
  - 位置: main.tex:236「the comparison concerns predictive accuracy, and downstream benefit and cost were not measured」・main.tex:251「Hidden states are not named and are not read as cognitive or affective states」
  - なぜ: Aalbers は MAE を評定尺度の点数に直す（aalbers.txt:134 "on average, the model mispredicts momentary subjective stress by ±0.80 points on a 7-point Likert scale"）。236 行の換算は著者自身が証拠にならないと書く。
  - 解消: 判断の側の量を 1 つ（休止の予測・次の秒の打鍵の予測の一致率など）。しないなら題・要旨・推奨の適用を「予測の対数尤度での比べ」に明示的に限り、何を言わないかを考察に 1 段落。
  - 自信: 中
- [major] 選びに標的の書き手の訓練単位が漏れ、使う場面を近似していない
  - 位置: main.tex:105「This simulates the use case for the fit and the evaluation, but not for the choice: ...」・main.tex:256「a nested design was not run」
  - なぜ: 17 人のパネルで 1 人の寄与は無視できず、残り（1e-4 の桁）と同じ桁の偏りを生みうる（Saeb S1）。
  - 解消: 入れ子を主な行（15-session・k=5 と 15）で回す。回さないなら漏れの向きを論じる。
  - 自信: 中
- [minor] ブートストラップが選びのばらつきを含まない（main.tex:142「... without refitting or re-choosing」）。表の注に「選びを固定した条件付きの区間」、または主な行で選び直したブートストラップ。自信: 中
- [minor] τ が格子の端・基の平滑が固定（main.tex:255）。10^7 へ 1 段伸ばした結果を 1 文。基の平滑を 2 水準で。自信: 中
- [minor] 30-session の結果が要旨で弱められている（要旨 "at most about 1% ... (about 3% ...)"・main.tex:206「30-s., 30 & \arthree, $3\times10^4$ & 39\%」）。要旨に「k=30 で重み 39%・9 人で区間は 0 をまたぐ」の 1 句。"at most" の言い方を直す。自信: 高
- [minor] 要旨の語数が規程超え（266 語・"Please provide an abstract of 150 to 250 words."）。自信: 高
- [minor] Code availability に置き場所が無い（main.tex:269）。kit README（75–80 行）が認めるとおり元データとの一致は確かめられない（既知 4）。リポジトリと DOI か「査読者へ提供」。自信: 高
- [minor] 新しさの主張の支えが本文に無い（main.tex:44「we found in our search (\Sref{1}) no study that compared ...」）。検索の範囲を 1 文。関連研究に「打鍵による状態推定」と「適応システムの個人化」を各 2〜3 文。自信: 中
- [minor] CS1 の役割が薄い（main.tex:80「We use CS1 as a boundary case ...」・222「so we do not use the CS1 sensitivity to read the real CS1 panel」）。何を言うかを 1 文、無ければ補足へ。自信: 中
- [nit] 222 行の 1 文に留保 4 つ。結論の文と CS1 の注を分ける。自信: 高
- [nit] 選びの目的の説明（main.tex:115「This objective was fixed in the first analysis; it is not the target writer's predictive accuracy.」）。本人の連鎖は候補によらず一定なので、書き手ごとには対数尤度の順位と同じ。「対数尤度を本人の連鎖で中心化し、その中央値で選ぶ」と言い換える。自信: 中

## 4. 総合: major
- 評価の作り（時間で分ける・本人の素朴な基準・他人で選ぶ）は Saeb・Aalbers の基準に沿う。限定の多くも適切。
- ただし見出しの結論は記号化の変種で逆転し、下限より 1〜2 桁小さい残りから「人ではない」と読む。結合と ar3 固定の値が食い違い、選びに漏れがある。
- nats/symbol を適応の判断に結ぶ道筋が無い。範囲を限るか判断の側の量を 1 つ。

## 5. 読めなかった範囲・注入の疑い
- 読んでいない: S1〜S15（未作成）・figdata/fig2_p15.csv・規程の原文（context-A の抜粋のみ）・被引用文献の本文。
- 注入の疑い: 無し（main.tex:60 のコメントは著者のメモ）。
- 接地に使った本文と対象は brief の一覧の範囲（tmp/sources/aalbers.txt・saeb.txt、main.tex・references.bib・figdata・kit README）。
