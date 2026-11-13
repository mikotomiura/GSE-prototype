# review-R2（manuscript round 2・個人化した行動モデルの実務の立場・対象 9a4c1d34）

## 0. 引き継ぎの判定
記号化で逆転: 一部（163 に重ならない窓の文。重ならない窓での本人 − 共通の値が本文に無い。限界 1 項目の参照 "depends on the symbolization (Section~\ref{sec:res-protocol})" が 4.3 を指すが 4.3 は記号化を扱わない）。「人ではなく比べる相手」: 解消（270）。k=15 の食い違い: 解消（112・200）。結果を見た後の変更: 解消（141・292）。実務の尺度: 未解消（著者が採らなかった）。訓練単位の漏れ: 一部（二分は足された・入れ子なし・281）。minor 群: ブートストラップ・30-session・要旨・CS1 の役割は解消、τ の端・Code・新しさの支えは一部。nit: 解消。

## 1. 接地
Saeb「for this procedure to be meaningful, the relationship between the training and the validation set should mimic the relationship between the training set and the dataset expected for the clinical use.」「The correct way for adjusting these hyperparameters is to further divide the training set into training and validation subsets」「subject-wise CV had a significantly closer estimate of the true performance of the algorithm.」。Aalbers「To evaluate if our models perform better than random guessing, we compare against the MAEs of a 'naive' but person-specific baseline model.」「on average, the model mispredicts momentary subjective stress by ±0.80 points on a 7-point Likert scale」「for 89.3% (200/224) of participants, the person-specific baseline outperformed all nomothetic models」

## 2. 評価表
a 2・b 3・c 2・d 3・e 4・f 4

## 3. 指摘
- [major] M1 見出しの数値は選ばれていない平滑での値で、選ばれた平滑で残りが約 10 倍になることが要旨と結論に出ていない。要旨・Table 3 Both refitted・242「we do not read the values at the lighter smoothing as the size of a per-person gain, because the multiplier sits at the edge of its grid and was chosen for the shared model」。読まない理由の「格子の端」は τ=10^6 にも当てはまる（294）のに τ の値は見出しに使う。非対称。解消: (i) 残りを「固定の平滑で約 5e-4、両側を軽い平滑で最大約 7e-3」の範囲で、「2 桁以上」を条件つきに、(ii) α の格子を下へ広げ両側の系で選び直す、(iii) α=1 を主に据える理由を τ と同じ基準で。自信 高
- [major] M2 実際のパネルは著者自身の検出の規則を満たすのに「示さない」と読み、推奨 (3) が自分の事例で使えない。144・233・279。感度の検査の α が 3.5 に無い。解消: 実データは規則を満たすが生成器が再現しないので検出とは読まない、と率直に。推奨 (3) に陰性対照が実データの性質を再現する条件。3.5 に α を書く。自信 中
- [major] M3 nats per symbol が設計の判断の尺度に換わっていない（引き継ぎ 5）。270。perplexity の比やセッションあたりの対数尤度比に換えて並べる。自信 中
- [major] M4 重ならない窓で見出しの主張が成り立つかが本文に無い。163。重ならない窓での結合の選びの本人 − 共通の中央値を本文か Table 2 に。限界 1 項目の参照を 4.2 に。自信 中
- [minor] m1 要旨の「両側を他人で選んだ平滑」は言い過ぎ（294 "The symmetric refit chose the multiplier for the shared model and applied it to the per-person fit"）。自信 高
- [minor] m2 二分は選びが格子の端に張り付くと楽観を検べられない。k=15 で Fixed +4.1e-4 と Split +7.4e-4 の食い違いの理由が無い。自信 中
- [minor] m3 Table 3 Only shared refitted の 0 と「8 to 17 writers」の対応。k ごとの人数の列。自信 低
- [minor] m4 同じ要約の反復（34・48・235・270・274・303）と限界の再掲（293・295）。自信 高
- [minor] m5 「one decision per panel」と標的ごとの選び（112・200）。自信 中
- [minor] m6 Data availability が書き手ごとの値を出さない理由を書かない（307）。自信 中
- [nit] n1 「2 桁以上」は k=1 では約 25 倍。自信 高
- [nit] n2 他の書き手の単位が暦の上で標的の評価より後を含みうる（102・104）。自信 低

## 4. 総合: major
対称の再当てはめで他人で選んだ平滑のもとでは残りが約 10 倍になると分かったが、要旨と結論は非対称な理由で読んでいない。実データは検出の規則を満たすことが率直に書かれず推奨 (3) は自分の事例で使えない。重ならない窓と実務の尺度が無い。

## 5. 読めなかった範囲
references.bib・fig2_p15.csv は読んでいない。注入の疑い: なし。
