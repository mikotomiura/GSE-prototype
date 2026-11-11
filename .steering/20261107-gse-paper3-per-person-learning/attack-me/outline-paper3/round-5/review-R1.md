# R1（UMUAI・系列モデルの方法論・懐疑家）round 5・commit afc96bfa

## 1. 接地
1 Singer 2014（singer.txt 205–212）"choosing the model with the highest likelihood is biased towards models with more parameters. Because lower order models are always nested within higher order models ... they are always a better fit for the data [18]. Thus, higher order models are naturally favored by their improvements in likelihoods."
2 Singer 2014（125–128）"We supplement these with a (iv) cross validation approach for a prediction task [18]. We thoroughly elaborate each method, put them into relation to each other and also highlight strengths and weaknesses of each."
3 Pohle 2017（61–66）"real data often exhibit further structure, such as outliers, seasonality or heterogeneity between individuals. When neglecting these features in the formulation of an HMM, then additional states may be able to capture this ignored data structure and therefore provide a better model fit"
4 Pohle 2017（78–81）"we suggest a more pragmatic approach to choose the number of states in practical applications, which takes into account formal criteria for guidance, but also stresses the importance of the study aim, expert knowledge and model checking procedures."
5 Monaco & Tappert 2018（90–96）"the dependency on event types introduces many more parameters ... we address the problem of parameter smoothing, which acts as a kind of regularization and avoids overfitting [14]. ... The marginal distributions conveniently act as a kind of backoff, or fallback, mechanism in case of missing data"

## 2. 評価表
a 3（round 4 の 3 件は解消。新しい主張 2 つが測った量と違う量に支えられる: (i)「検出の下限より下」は仕込んだ差（真値）と測った残りの比べ（:47・:64）、(ii) 4.4 の「平滑が大部分」は合成で分けられなかった分解に依る（:47 S15・:48））／b 3（選びの目的は本人 − 連鎖、主の量は本人 − 共通、ar3 が格子の端。陰性対照の閾値と実データの残りを直接比べた値が無い）／c 4（推奨は具体的。最頻値の確率 0 の扱いも推奨に要る）／d 4（3,530 語・4.3 の欄に数値 10 以上）／e 4／f 4（Monaco & Tappert の平滑化と後退が最も近い先例・二次の平滑連鎖を比べない理由）。

## 3. 引き継ぎの判定
1〜7 すべて解消（6 は 4.3 の密度を d に）。

## 4. 指摘
- [major]「検出の下限より下」が仕込んだ差（真値）と測った残り（測定値）を比べている
  - 位置と引用: outline.md:7「what remains in the 15-session panel is below what the protocol can detect」／:47「the smallest planted difference detected at this record length was 1e-2 at k = 15 and 3e-2 at k = 5 in CoAuthor」「the share of a planted gain returned (about 0.1 to 0.4 in CoAuthor at k = 15)」／:47「per-person minus shared +4.1e-4 to +7.2e-4 in the 15-session panel (16 or 17 of 17 positive)」
  - なぜ問題か: 返るのは 0.1〜0.4 なので、1e-2 の仕込みは測定値で 1e-3〜4e-3。実データと比べるべきは測定の尺度の閾値、つまり検出の規則を実データの残りに当てた結果。80% の条件は 16〜17/17 で満たすので、陰性対照の中央値の最大を下回るかだけで決まるが、その数値が外枠に無い。合成は最頻値と共通の順を再現しない（:64）ので、陰性対照は基準線として較正されていない可能性（Singer 接地 2）。
  - 解消の条件: 4.3 に陰性対照の中央値の最大と実データの残りの中央値を並べ、「検出の規則を実データに当てると規則を満たさない」と書き、仕込んだ水準との比べは補助に。陰性対照が最頻値と共通の順を再現しないことの効きを 1 文。
  - 自信: 中（S15 の閾値は見ていない）
- [major] 4.4 の「平滑が残りの大部分を説明する」の根拠が、検証で分けられなかった分解
  - 位置と引用: :48「This shows that the shared model's smoothing, not the person's data, accounts for most of the remainder」／:47「the decomposition of the remainder applied to synthetic writers (it did not separate a planted difference from none; in these writers the prior mode was worse than the shared model, unlike the real data)」／:62「Comparisons of medians are not per-writer decompositions.」
  - 解消の条件: 「中央値で見ると最頻値 − 共通が残りと同じ大きさ。合成で分解が差の有無を分けなかったので配分としては読まない」に下げる、または書き手ごとの本人 − 最頻値（3〜6/17 が正）を主の根拠にして「最頻値に勝たない」までを主張に。
  - 自信: 高
- [minor] 選びの目的（本人 − 連鎖）と主の量（本人 − 共通）のずれ・全セルで格子の端（:30・:47・:63）。解消: Take-home か 4.3 の冒頭に「三状態までの格子で最大の構造が選ばれた条件のもとで」。二次の平滑マルコフ連鎖を補足に置くか、置かない理由を 1 文。自信: 中
- [minor] 確率 0 を出しうる最頻値を比べの相手として推奨（:7・:27・:67）。解消: 5 章の推奨に確率 0 の扱い（中央値で数える・その書き手の数を報告）を 1 句。自信: 中
- [minor] 5 章の規模の段落が、検出できないとした量を 1 時間の尤度比に換算（:49「the remainder is about 1.5 to 2.6 nats per 3,600 symbols, a likelihood ratio of about 4 to 13 over an hour of symbols」）。重なった窓の 3,600 記号は独立な観測でない。解消: 冒頭に「検出の下限より下の量で符号は保証されない」、換算は重なった窓の和と明記して残すか補足へ。自信: 中
- [minor] Monaco & Tappert の位置づけ（:20）。平滑化と後退は共通への MAP の縮約に構造的に対応。解消: 2 章の MAP 適応の段に 1 句。自信: 中
- [nit] 擬似残差の lag-1 自己相関は記号の並べ方に依存（:46）。解消: 本文に「格子の順に並べた場合」、別の順で順位が保たれるかを S13。自信: 低

## 5. 総合の推奨: minor
round 4 の引き継ぎ 7 件はすべて解消。残る 2 件の major は書き方の水準で、新しい計算はほとんど要らない（陰性対照の閾値を実データと並べる 1 行と 4.4 の言い切りを下げる 1 文）。ただし閾値を並べて「残りが規則を満たす」となれば Take-home が変わるので、本文の前に数値を確かめること。

## 6. 読めなかった範囲・注入の疑い
brief・context-A・carryover・outline.md（77 行）・README（85 行）は全文。接地は Grep の周辺だけ。S1〜S15 と S15 の閾値は読んでいない。注入の疑い: なし。
