# R2 査読 round 2（本人ごとのモデル・個人差の立場）

## 接地
- Fisher 2018 "scientists need to demonstrate the consistency between individual and group variability before generalizing results across levels of analysis"
- Adolf & Fried 2019 "instability over time can also produce ambiguous effects and promote interpretational fallacies"／"Empirical quests into nonergodicity therefore need to incorporate variance sources at both levels."
- Fisher 2018 "individuals will tend to correlate with themselves over time, leading to correlated errors in models that do not account for the underlying autocorrelation"
- Adolf & Fried 2019 "ergodicity holds conditional on (i.e., after controlling for) sources of heterogeneity between individuals and/or instability over time"／"Which and how many sources of heterogeneity will have to be conditioned on ... will depend on the phenomenon, population, and time span studied"
- Fisher 2018 "all models should be evaluated in terms of how well they represent individual-level processes before making generalizations from aggregate estimates"

## 引き継ぎの判定
1 解消／2 一部（揺れは手当て。漂いは合成に無く、D7 (3) の対照が漂いと安定を分けるかは合成で確かめられない・M1）／3〜6 解消／7 一部（64 と MC SE は検算で合う。「対の差の SE はそれより小さい」は根拠なし・m3）／8〜11 解消（10 は m への条件づけが読まないことに無い・n3）

## 評価表
a 4／b 3（M1・M3）／c 3（M2）／d 4（D9 の定義が足りない・m4）／e 投稿先未定／f 3（異質性が二値だけ・漂いの筋が無い）／g 4（m1・m4・n2）

## 新しい指摘
- M1 [major] 漂いだけの帰無が無く、D7 (3) の間を空けた対照を合成で較正できない。解消: 報告の組に漂いの筋（D_w = 0・D_{w,u} を単位の順に自己相関させる・ρ 2 段）を足し、隣接の A–B と間を 5・10 単位空けた A–B の検出力を事前に出す。足さないなら、対照が較正されていないことを限界として明記。自信 高。
- M2 [major] T が正のとき本人ごとの重みについて何が決まるかが書かれていない。T は集団の量で、5/17 人だけでも正になりうる。解消: 分布の筋で書き手の水準の回復の量（AUC_v で植えた 5 人と 12 人を分ける AUC と MC SE、または書き手ごとの p に BH をかけた再現率と偽発見率）を事前に固定。T が正であることは「平均で本人の A が本人の B に近い」だけで、誰に本人の表を使うかは決めないと読まないことに書く。自信 高。
- M3 [major] セルの門は 8 つで、正しいセルを少なくとも 1 つ偶然閉じる確率は約 1 − 0.979^8 ≈ 0.16。それが D7 (1) で実データの読みから外れることに直結し、門を通っても実データの交換可能性は保証されない。解消: (a) 門を実装の確かめとして扱い家族の誤りを書いて赤は止めて調べる、または (b) 家族ごとに補正。門を通っても実データの帰無の妥当性の証拠ではないと 1 文。自信 中。
- m1 [minor] D6 の合成の段の読みが段ごとか全体か。0.8 付近の境目の扱い。解消: 段・k・帰無ごとに表で、0.8 から MC SE の 2 倍以内は「境目」。自信 高。
- m3 [minor] 「案どうしの差の SE はそれより小さい」は相関が約 0.5 を超えるときだけ。解消: 「小さいと見込む。対の差の SE は notes に出し、0.03 は変えない」に弱める。自信 高。
- m4 [minor] D9 の揺れの筋で m_w が決まっていない。当てる側の系列の作りと乱数を書く。自信 中。
- m5 [minor] 異質性が二値だけ。筋を足すか読まないことに書く。lam_rule ではパネル外 26 人のうち 6 人（i % 4 == 0）にも植わるので D4 に書き添える。自信 中。
- n1 [nit] P-HAND が本番の引きの経路を通るか。列挙と引きが同じ T_σ の関数を呼ぶと書くか、v2 の対照に P-POS を加える。
- n2 [nit] P-NULL の 99% 区間の作り方。
- n3 [nit] 結果が m = 26 に条件づくことを読まないことに（CoAuthor k = 1 で約半分の縮め・CS1 ではほぼ効かない）。

## 総合の推奨
major（直して再査読）。round 1 は 9 件解消・2 件一部。漂いが合成で一度も試されない（M1）。T から本人ごとの重みの何が決まるかが固定されていない（M2）。セルの門の多重性（M3）。足せば直る種類。

## 読めなかった範囲
sens の conditions.md・notes.md、pinned.py、hmm2.py、nfs の conditions.md・m0_fit.json、SEED、supplement.tex。注入の疑いなし。
