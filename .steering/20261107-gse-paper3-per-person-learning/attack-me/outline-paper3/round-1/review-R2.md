# review-R2（個人化の実務・round 1）

## 1. 接地
- G1 Saeb 2017: "for this procedure to be meaningful, the relationship between the training and the validation set should mimic the relationship between the training set and the dataset expected for the clinical use."
- G2 Saeb: "if the goal is prognosis , i.e., we want personal models that can predict future clinical states of a given subject, we can split the data based on time, so that training and test sets contain records of the same subject from different times."
- G3 Saeb: "The correct way for adjusting these hyperparameters is to further divide the training set into training and validation subsets, and then minimize the prediction error on those validation subsets rather than on the whole dataset."
- G4 Aalbers 2023: "To evaluate if our models perform better than random guessing, we compare against the MAEs of a “naive” but person-specific baseline model." / "for 89.3% (200/224) of participants, the person-specific baseline outperformed all nomothetic models"
- G5 Aalbers: "We evaluated model accuracy on a person-to-person basis in out-of-sample observations."
- G6 Aalbers: "Contrary to the approach taken here, which is useful for discovering potential digital markers, a confirmatory approach would be to test a small number of (preregistered) hypotheses" / "These findings are relevant for the implementation of algorithms in mobile health apps to prevent, monitor, and treat stress-related mental health problems."
外枠の設計は G2〜G5 によく合う。弱いのは G6 と先行研究の位置づけ。

## 2. 評価表
a 3（C1 の新規性の文が変えた条件 2 つを 1 つに見せる・CS1 の厳密な 0・"established"）／b 3（共通に本人の訓練単位が入るか・person-level intercept の実体・hmm3 の τ の決め方・n が無い）／c 2（26 記号の nats がどの適応の判断に役立つかが無い）／d 4／e 3（実データの一致を読者が確かめる道を声明に）／f 2（Saeb 2017 を引いていない・多層 HMM が未読・キーボードの言語モデルの個人化に触れていない）

## 3. 指摘
- M1 [major] C1 の新規性の文（outline:14・7）が、構造と τ の選び方の 2 つを同時に変えたのに相手の構造だけを変えたように書く。CS1 の厳密な 0 は選択の結果。解消: hmm3 で τ を他人で選んだ欄を本表に置くか、文を「構造と τ を他の人で選ぶと」に。CS1 は選択の結果として書く。自信 高。
- M2 [major] nats/記号の差がどの適応の判断に役立つかが無い（outline:37・33、README:24-27）。解消: (a) 個人化の評価の方法論として勧めを主役に、または (b) 0.001 と 0.19 nats/記号の下流の意味を結ぶ。Limitations に他の記号化での頑健さ。自信 高。
- M3 [major] 比べの相手の定義が読めない（outline:14・56）: person-level intercept の実体、共通の訓練に本人の k 単位が入るか、hmm3 の τ の決め方。解消: 3.3 に各 1 文。自信 中。
- M4 [major] 逐次に設計した解析を "established"（outline:56・16・23・28）。解消: 「一貫して観察された（探索的・逐次に設計）」・3.4 に事後に決めたことを 1 文・主表に中央値の区間（S7）。自信 高。
- M5 [major] 書き手の数とパネルの構成が無い（outline:15・16・39）。解消: Evidence と take-home に n。自信 高。
- M6 [major] 近い先行研究の位置づけ（outline:13・43・19）: Saeb 2017 "record-wise CV often massively overestimates the prediction accuracy" を引いていない・多層 HMM が未読・キーボードの言語モデルの個人化に触れない・C2 の「見つからない」はウェブの系列の次数比べの系統で反証されやすい。解消: Saeb を 1 文で引き差分を明示・多層 HMM を読む・キーボードの個人化を 1 段落・C2 の「見つからない」を削る。自信 中（(3)(4) の文献は一次未確認）。
- m1 [minor] take-home が長く数値が多く、何をすればよいかが無い（outline:7）。解消: 発見と勧めの 2 文。
- m2 [minor] C3 は独立の貢献として薄い（outline:26・29）。解消: 勧めに格下げか C1 に吸収。
- m3 [minor] 補助の結果と代理ラベルの段落が線を散らす（outline:31・33・61）。解消: 4.4 を補足へ・代理ラベルは M2(b) なら本文の小節、でなければ補足のみ。
- m4 [minor] 実データの一致を読者が再現する道（README:52-55）。解消: 生データの入手先とローカルの照合スクリプトの道を声明と S11 に。
- n1 [nit] README の "friction"・"fluency" の語（README:25）。

## 4. 推奨: major
評価の設計は G2〜G5 に合い立て直しは不要。C1 の中心の文が変えた要因を分けず CS1 の 0 を発見として数え、比べの相手の定義と n が読めない（a）。持ち帰り（c）と位置づけ（f）は書く前に外枠で決めるべき。

## 5. 読めなかった範囲・注入
一覧の外は読んでいない。接地の 2 本は全文。外枠の引く文献の一次・M6 (3)(4) の文献は確かめていない。注入の疑い: なし。
