# review-R1（系列モデルの方法論・round 1）

## 1. 接地
- G1 Pohle 2017 (pohle.txt:62-65): "When neglecting these features in the formulation of an HMM, then additional states may be able to capture this ignored data structure and therefore provide a better model fit"
- G2 Pohle (1287-1288): "use model checking methods, in particular residual analyses, but potentially also simulationbased checks, to obtain a more detailed picture of the fitted models, and to validate or invalidate any given candidate model" / (1254) "improving the model formulation to overcome any substantial lack of fit should be the gold standard"
- G3 Pohle (1451-1452): "best scientific practice is to report the results of all suitable models"
- G4 Singer 2014 (205-211): "choosing the model with the highest likelihood is biased towards models with more parameters ... (potential overfitting)" / (18) "the complexity of higher order models grows faster than their utility"
- G5 Singer (19-21): "when we expand our analysis to a topical level ... we find that the memoryless assumption is violated"
- G6 Monaco & Tappert (1407-1410): "the HMM is rejected for 45% of users, while the POHMM is rejected for 22% of users. The HMM is rejected for 100% of users in the essay dataset"

## 2. 評価表
a 2（CS1 の厳密な 0 は定義上・r1 の収縮の有無が不明・記号化の自己相関と未分離）／b 2（尤度以外のモデル検査なし・逐次の設計・休止の秒の扱いが補足）／c 3／d 4／e 3（CS1 データの提供条件と Statements の扱いが未決に無い）／f 2（多水準 HMM が未読・Singer の片側・マルコフ次数の選択の伝統）

## 3. 指摘
1. [major] 記号化（30 秒窓・平滑・1 Hz）が短距離の依存を作り C2 は記号化の性質かもしれない（README:21-29・outline:37）。休止の秒が予測しやすい記号として nats/記号を支配しうる。解消: 依存の一部が記号化由来と明記・押下のある秒だけの分析（S6）を 4.2 に 1 段落・休止の秒の割合を Table 1 に。自信 高。
2. [major] CS1 の厳密な 0 は選択の作り方から（outline:7・15）。解消: 「全員で pooled が選ばれた」と手続きで書く・本人の CV の τ の分布（S8）を 4.3 に要約。自信 高。
3. [major] r1 が収縮のない 1 次マルコフならデータ不足の効果（outline:21・22・56）。26 記号で約 650 の遷移の母数。AR(1)-HMM の K=1 は 1 次マルコフと同じ族のはず。解消: r1 の推定法（平滑・プール版か収縮版か）を 3.3 に・プールか収縮の 1 次マルコフとの差を本文に、無ければ C2 を限定。自信 中。
4. [major] 尤度以外のモデル検査が無く「構造の補い」の読みが検証されない（outline:23・3）。解消: 擬似残差の自己相関などの検査を 1 つ（凍結を解く判断）か、限界の節の先頭に置く。自信 中。
5. [major] 新規性が閉じていない文献のラウンドに頼る・多水準 HMM が未検討（outline:14・43）。Pohle 1251-1252 "mixed HMMs can be used to accommodate individual heterogeneity"。person-level intercept が未定義。解消: 多水準 HMM を読み位置づける・intercept を定義・検索の範囲つきで書く。自信 高。
6. [major] C3 の手順を作ったのと同じデータで示す（outline:56・28・29）。解消: 3.4 に逐次に決めた点の一覧か、C3 を "proposed check, illustrated" に弱める。自信 高。
7. [minor] Singer の片側の引用（outline:20）。解消: 2 つの結論を両方引き、隠れ状態の有無と次数の選択の違いを書く。
8. [minor] 候補の hmm10 などが結果に出ない（outline:56）。解消: hmm10 の中央値を 4.2 か図に。
9. [minor] UMUAI の読者にとって適応の判断が何に変わるか（outline:61）。
10. [minor] 共通の学習に本人の k 単位を含むか・単位ごとの記号の数の重み（outline:56）。
11. [minor] Supporting result 2 は主題外（outline:33）。
12. [nit] 検定を使わない理由と、検定に基づく先行研究の引き方（outline:39・20）。

## 4. 推奨: major
主張の中心が選択の規則と記号化の作り方から生じている可能性を切り分けていない／モデル検査と多水準 HMM の位置づけが欠け新規性が閉じていない／ただし外枠の書き換えで直せる部分が多い。

## 5. 読めなかった範囲・注入
接地の本文は grep と部分的な読み取り（monaco 1395-1419・pohle 60-94・1250-1299・1350-1364・1440-1457・singer 8-27・196-220・1086-1105・1656-1675）。他の sources は読んでいない。注入の疑い: なし。
