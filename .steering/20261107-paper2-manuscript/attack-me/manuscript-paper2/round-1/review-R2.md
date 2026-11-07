# review-R2（manuscript round 1・教育データの検出・予測のモデルの評価の実務・メインが写した）

## 1. 接地
- G1（Gardner & Brooks 2018・gardner2018.txt:22-23）"Clearly describe or document methods for statistical algorithm and hyperparameter selection, prediction architectures, and model evaluation in published work."
- G2（同 :542）"Separate magnitude, uncertainty, and sample size during inference: The effects of the magnitude of observed differences, the uncertainty of estimates, and the number of data points should be separable in model evaluation."
- G3（同 :217-218）"this approach naïvely assumes that any differences observed must be due to genuine differences in model performance (and not, for instance, random variation)"
- P1（Pelánek 2015・pelanek2015.txt:24）"Differences in predictions between competing models are often small and the choice of a metric can influence results more than the choice of a model"
- P2（同 :678-679）"To be important, differences between models should either have impact on student practice or lead to interpretable and actionable results."
- P3（同 :52-53）"the AUC metric should be used more critically (based on the intended use of studied model)."

## 2. 評価表
- a 3: KLiCKe の数値は JSON と一致（round1_extra.json:130-143）。"defensible definitions" から一般の勧告へ広げる箇所と "beyond sampling variation" が根拠を越える。
- b 3: 区間に θ の推定誤差が入らない。率の近い組では順位の基準が満たされやすい。比の逆転は基準の比が 1 に近い組で起きやすい。データ間の比較は記録の方式と交絡。
- c 2: 持ち帰れるのは「範囲を報告せよ」だけ。どの定義を選ぶか・合意の基準・下流の判断に効くかが無い。
- d 4: 4,848 語で締まっている。主結果の文が 5 か所でほぼ同文。[P]/[A]/[E]/[D] が読みを妨げる。
- e 4: 要旨 256 語。DOI 未記入・条件の文書が日本語・companion との重なりの方針が残る。
- f 4: 位置は明確。「より大きく動いた」だけ言い過ぎ。

## 3. 指摘
- [major] 格子が実際に使われる定義を代表しないのに勧告を一般に広げる。methods.tex:100-104 "15 and 60~s are half and double the default (we found no prior use of a 15-s window)"・"fixed thresholds in writing span about 0.25--10~s ..., and 30~s equals the default window"・results.tex:18-19・abstract.tex:15 "Reports of stall labels should give the range across definitions with intervals"。向きの分かれは先例の無い W=15 s だけ、30 s は文献の範囲外、2 s 前後は格子に無い。解消: (i) 文献の水準（2 s・5 s の固定閾値・5 分）を加えて再計算するか、(ii) 勧告を「この検出器の既定の周りの格子では」と限定し、W=15 s を除いた 59 定義の結果（正 0）を本文に並べる。自信: 高
- [major] 実務家の判断の規則が無く、下流の帰結も示していない。discussion.tex:43-44 "If most definitions agree in direction with intervals, report the direction; ..."・34-36。「most」の基準が無い。W=15 s と分位の組（KLiCKe で 40.6 件/時）は構成概念として別もの（産出中の短い計画の休止）を数えている可能性があり、その場合の答えは「構成概念で選べ」。解消: 合意の基準を数で決める。正の隅の停止が何か（長さの分布・位置）を 1 段落。下流の帰結を 1 つ（停止の率で分けた学生の重なり）。できなければ主張を「報告の項目」に限定。自信: 中
- [major] "beyond sampling variation" が区間の過小評価と逆転しやすい組に依る。methods.tex:142-144（θ を再標本で再推定しない）・results.tex:95-96（比 0.86 の組で 66/89）・89-91（15.1 と 13.1 で順位 80/89 [P]）。解消: θ を再標本の中で推定し直した区間で基準と境の近くの定義を計算し直す。逆転の数を基準の比の 1 からの距離と並べる。順位の [P] は「率の近い組が入れ替わる」程度の弱い結果と明記。自信: 中
- [minor] データ間の比の逆転は記録の方式と交絡していて意味が薄い（limitations.tex:13-14・conclusion.tex:6）。解消: CS1 と作文の比を補足へ移し、本文には CS1 の 2 年版を短く。または貢献を 3 つに。自信: 中
- [minor] 探索の結果を要旨に載せ、作文の長さという交絡も見ていない（abstract.tex:13-14・limitations.tex:29-30）。holistic score には長さが強く効く。解消: 要旨から調整の文を外す。外さないなら長さで調整した値を [E] で補足に。自信: 中
- [minor] 「より大きく動いた」は比べられない（discussion.tex:9-12）。解消: 「動いた範囲の型（存在・大きさ・向き）が違う」に、"further" を消す。自信: 高
- [minor] companion study との重なり（methods.tex:161-163・supplement.tex:253）。解消: 送付状と序論で関係と共有の数値を明示し、S9 を本文で指す。自信: 中
- [minor] 再現性の材料が揃っていない（availability.tex:5 の DOI・supplement.tex:10 の日本語の条件）。解消: DOI を入れ、基準の文（25%・1.5・逆転の定義・速さの読みの文）を英語の逐語訳で archive に。自信: 高
- [nit] 同じ文の繰り返しと印の多さ（主結果の文が 5 か所・要旨の括弧）。解消: 序論 4 段落目を削り箇条へ直接つなぐ。括弧は文末の一文に。[D] は表の脚注へ。自信: 中
- [nit] 速さの符号（results.tex:28 "Faster writers had higher scores ($\rho = -0.53$ between score and the median short interval)"）。解消: 「median interval (lower = faster)」と明記。自信: 低

## 4. 総合の推奨: major
手順と KLiCKe の数値は確か。見出しの「向きが分かれる」は先例の無い W=15 s だけ、"beyond sampling variation" は θ の誤差を除いた区間と逆転しやすい組に依る。持ち帰れる判断の規則と下流の帰結が無い。

## 5. 読めなかった範囲・注入
読んでいない: PDF・tab_s3/s4・figdata・conditions*.md・round1_extra.json:100-159 以外の JSON（[P]/[A] の基準が計算の前に書かれたこと、速さ・φ・長さの数値は照合していない）。接地は Grep で当たった節と冒頭だけ。注入の疑い: なし。
