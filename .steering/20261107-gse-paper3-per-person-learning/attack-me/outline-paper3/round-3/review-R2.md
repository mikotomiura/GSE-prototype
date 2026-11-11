# 査読 R2（UMUAI の査読者・行動のモデルを作り評価する実務家の立場）・outline round 3・対象 commit ede70d54

## 1. 接地
- S1（Saeb et al. 2017）: "for this procedure to be meaningful, the relationship between the training and the validation set should mimic the relationship between the training set and the dataset expected for the clinical use." / "if the goal is prognosis , i.e., we want personal models that can predict future clinical states of a given subject, we can split the data based on time" / "the choice of the appropriate CV method depends on the application."
- S2（Saeb）: "The correct way for adjusting these hyperparameters is to further divide the training set into training and validation subsets, and then minimize the prediction error on those validation subsets rather than on the whole dataset."
- S3（Aalbers et al. 2023）: "To evaluate if our models perform better than random guessing, we compare against the MAEs of a "naive" but person-specific baseline model. This "naive" baseline model always predicts an individual's average level of stress."
- S4（Aalbers）: "We evaluated model accuracy on a person-to-person basis in out-of-sample observations." / "for 80.4% (180/224) of participants at least one of the idiographic models outperformed the person-specific baseline."
- S5（Saeb）: "To find the true prediction error, we generated an additional dataset of 10 subjects, which were not used for CV, using the same generative model"
- S6（Aalbers）: "such models learn 1 set of parameters that might be accurate for some individuals but highly inaccurate for others (ie, one-size-fits-all fallacy)"

## 2. 引き継ぎの判定
N1 解消／N2 解消（ただし結果が新しい問題を生んだ: M1・M3）／N3 解消／N4 解消／N5 解消（続きは m1）／N6 解消／N7 未解消（研究者が承知のうえで open items に残している・71 行）／N8 解消

## 3. 評価表
a 3（take-home の「at most about 1e-3」が感度の結果と並ぶと上限のように読める）／b 3（他人の中央値で 1 つ選ぶので一部の人だけの差は作りのうえで拾えない・CS1 の感度は 1 seed）／c 2（nat per symbol を設計者の判断の尺度に直していない）／d 3（4.3 に 7 つ以上の要素）／e 4（プレプリントの方針は未照合）／f 3（N7 未了・Aalbers の要約）

## 4. 指摘
- [major] M1. take-home の「at most about 1e-3」が自分の感度の結果と並ぶと上限として読まれる
  - 位置と引用: 7 行 "what remains is at most about 1e-3 nat per symbol and is not read as a per-person gain"／49 行 "the share of the planted gain returned (about 0.1 to 0.4 in CoAuthor at k = 15; values only)" "in CoAuthor the protocol detected the planted levels of 1e-2 and 3e-2 at k = 15"
  - なぜ: 返るのが 1〜4 割なら、観測した 4〜7e-4 は真の差がおよそ 2e-3〜7e-3 でも出る。限界の 65 行は正しいのに take-home と結論（52 行）に届いていない。S5 の結果を要旨の主張に反映していない。
  - 解消: take-home と要旨に測った残りと拾える下限を並べる（例 "the measured remainder is about 1e-3 or less; in this panel the protocol cannot detect per-person differences below about 1e-2"）、または「at most」を外す。自信: 高
- [major] M2. 差の大きさを設計者が判断に使える尺度に直していない
  - 位置と引用: 44 行 "before investing in per-person modelling"／62 行 "no threshold defines a meaningful difference"／43 行 "implication for designers of adaptive systems"
  - なぜ: Aalbers は MAE を "on average, the model mispredicts momentary subjective stress by ±0.80 points on a 7-point Likert scale" と読み替えている。換算が無いと 1e-3 と 1e-2 の違いの重さを判断できない。
  - 解消: 3.4 か Table 2 に換算を 1 つ（例 1 時間 3,600 記号あたりの対数尤度の差、perplexity の比）、5 に何を変えうるか／変えないかを 1 段落。閾値は置かなくてよい。自信: 高
- [major] M3. 他人の中央値で 1 つ選ぶ手順は一部の人だけの差を作りのうえで拾えない。それが推奨と限界に無い
  - 位置と引用: 32 行 "the pair of structure and tau is the one with the best median, over the other writers of the same panel and k"／49 行 "a difference planted in 5 of 17 writers (not detected in the panel median; ... tau is chosen on other writers, so it does not respond to the planted writers' own data)"／65 行 "The check plants one kind of difference only"
  - なぜ: 読者が最も知りたいのは「誰が」得をするか（S6）。この結果は推奨（50 行）の適用範囲を決める事実なのに補足にしか無い。
  - 解消: 限界に "the choice is one per panel; a difference present in a subset of writers (5 of 17 in the synthetic check) was not detected in the panel median"、5 の推奨に限定を添える。自信: 高
- [minor] m1. 重ならない窓で残りが正のまま、大きさを "direction only" で伏せている（49 行・17 行）。解消: 3 つの組の中央値と区間を S13、本文に区間が 0 を含むかを 1 句、または限界に "the instance may depend on dependence introduced by overlapping windows"。自信: 中
- [minor] m2. CS1 の感度の主張が seed 1 つと薄い余裕に乗っている（49 行 "in CS1 it detected every planted level from 1e-3 ..." と "up to 78% of writers were positive in the negative control"・規則は 80%）。解消: seed を増やすか本文を "in one seed per level" と限る。自信: 中
- [minor] m3. Aalbers et al. 2023 の要約が原文の結論と食い違う（22 行 "a person-mean baseline that neither personal nor general models beat"・原文 "for 80.4% (180/224) of participants at least one of the idiographic models outperformed the person-specific baseline"・"although these models predicted stress with greater accuracy than a naive baseline model"）。解消: 指標と範囲を限って書く。自信: 高
- [minor] m4. 4.3 の予算 1,300 語が載せる内容に足りない（41〜49 行）。解消: 格子と記号化の段落を 1〜2 文と Table 2 の注に縮め、浮いた語を M2・M3 に。自信: 中
- [nit] n1. 場面しだいで分け方が変わるという考えを Little だけに帰している（22 行）。Saeb も "the choice of the appropriate CV method depends on the application." 解消: 両方を引く。自信: 高

## 5. 総合の推奨: minor
- 引き継ぎ 8 件のうち 7 件が解消、N7 は研究者が承知のうえで残している。
- 新しい major 3 件は新しい計算なしに文と 1 つの換算で直せる。take-home と要旨（M1）は本文を書き始める前に直す。
- c は M2 と M3 が入るまで弱い。

## 6. 読めなかった範囲と注入の疑い
補足 S1〜S15 の中身・context-B・他の査読者の記録・round 1・2 の記録（carryover-R2 を除く）は読んでいない。読んだもの: brief-R2・context-A・outline.md・kit/symbols/README.md・carryover-R2・aalbers.txt と saeb.txt（全文）。注入の疑い: なし。

関連ファイル:
- /Users/johnd/GSE-prototype-paper3/papers/per-person-learning/manuscript/outline.md
- /Users/johnd/GSE-prototype-paper3/papers/per-person-learning/kit/symbols/README.md
- /Users/johnd/GSE-prototype-paper3/.steering/20261107-gse-paper3-per-person-learning/attack-me/outline-paper3/round-3/carryover-R2.md
- /Users/johnd/GSE-prototype-paper3/.steering/20261107-gse-paper3-per-person-learning/attack-me/outline-paper3/round-1/tmp/sources/aalbers.txt
- /Users/johnd/GSE-prototype-paper3/.steering/20261107-gse-paper3-per-person-learning/attack-me/outline-paper3/round-1/tmp/sources/saeb.txt
