# R2 査読（本人ごとのモデル・個人差の立場・round 1・prereg）

依頼文に評価表の見出しの定義が無かったため、a = 問いの意義・c = 主張と証拠の釣り合い・d = 明瞭さ・f = 再現性と来歴を査読者が補った（b・e・g は依頼文どおり）。

## 1. 接地

- G1 Fisher 2018 "Researchers should explicitly test for equivalence of processes at the individual and group level across the social and medical sciences."
- G2 Fisher 2018 "both the within- and between-subject variation should be explicitly modeled in any approach, and all models should be evaluated in terms of how well they represent individual-level processes before making generalizations from aggregate estimates."
- G3 Fisher 2018 "the variance around the expected value was two to four times larger within individuals than within groups."
- G4 Fisher 2018 "the data sampled within an individual in time must be representative of that individual generally (i.e., stationary)."
- G5 Adolf & Fried 2019 "Heterogeneity between individuals ... is one important complication for inferences across levels. But instability over time can also produce ambiguous effects and promote interpretational fallacies." / "Empirical quests into nonergodicity therefore need to incorporate variance sources at both levels."
- G6 Adolf & Fried 2019 "Which and how many sources of heterogeneity will have to be conditioned on, and whether the resulting conditional inferences remain meaningful, will depend on the phenomenon, population, and time span studied"

## 2. 評価表

a 4（G1 に沿う。重みの採否への接続は D7 に送られている）／b 2（指摘 1・2）／c 4／d 3（指摘 3・4）／e 投稿先未定／f 4（指摘 5・9）／g 3（指摘 3・6・7）

## 3. 指摘

1. [major] w を除く共有の表を書き手ごとに作るので、帰無の下で本人の対と他人の対が交換可能でなく、置換の p が正しくならないおそれ（E2・E3 で特に）。D1「B も同じ作りで p_v^B（共有は S_{-v}）」・D2 E2「δ_v^B = log p_v^B − log S_{-v}」・D3「s の行列は並べ替えの前に 1 回だけ作る」。pool_units(exclude=v) は w の A の単位も含む（ml.py 78 行）ので、他人の対では S_{-v} に w の A が入り E2 の相関を負に押す。本人の対では A と B が同じ S_{-v} に縮み、共有の推定誤差が同じ符号で入る（正に偏る）。E3 では数の少ない行で本人の対の JS が系統的に小さくなりうる。置換は名札だけを入れ替えるので、このずれを帰無に再現しない。解消: (i) 対ごとに S_{-w,-v} で A と B を作る、または (ii) すべての対で共通の 1 つの表を使い、理由を D1 に書く。V1 に帰無で T の平均が 0.5 から外れない門を置き、今の作りを変異として入れる。自信 中（E1 は帰無の下でほぼ無害と読む）。
2. [major] 合成の書き手は単位の間で定常で、個人内のばらつきが標本の揺らぎだけ。選びと止めが実データより甘い条件で決まる。A は B の直前なので、安定した差が無くても時間の近さで本人の対が近くなりうるが、その帰無が無い（G3・G5）。解消: (a) 単位ごとに行を揺らす筋と、安定した差は無く漂うだけの帰無を記述として足す（可能なら漂いの帰無の偽陽性を許しに加える）、または (b) 最低でも「読まないこと」に定常であることと時間の近さを区別しないことを書き、D7 で時間の近さの対照を必ず置くと約束する。自信 中。
3. [minor] D5.3 の止めが案ごとの除外か全体の判定か 1 通りに読めない。解消:「第 2 の帰無の 3e-2 の検出力が 0.8 以上の案だけを選びの候補に残す。候補が 0 なら止める」。自信 高。
4. [minor] π_j の定義が D1（w ごとに S_{-w}）と D2（全員の S）で食い違う。自信 高。
5. [minor] v2 の名指しの対照 P-HAND が置換の p を見ないので赤にならない。v2 の意味も 1 通りでない。解消: 3 人の 6 通りの置換で正確な p と一致させる。自信 高。
6. [minor] 選んだ案の検出力を選びに使った同じ複製で報告する（勝者の呪い）。解消: 選びと報告の種を分けるか、同じであることを明記。自信 中。
7. [minor] 複製の数・許しの閾値・同率の幅の根拠が無い。真の偽陽性 0.05 の案でも 2 つの帰無を両方通る確率は約 0.95。0.065 前後なら半々。500 複製の検出力の標準誤差は 0.5 付近で約 0.022。自信 中。
8. [minor] 見分けと本人ごとの重みの得の対応を、この段の複製に記録していない。各複製・各案で AUC_v と本人の表の予測の得（E1 の s(v→v) − 共有の表での同じ量）を記述として残す。自信 中。
9. [nit] 乱数の鍵の筋・形の番号が未定義、帰無の番号が鍵に無い。自信 高。
10. [nit] m = 26 の根拠が対象物に無い。自信 高。
11. [nit] 同率の解消の段で比べの基準が書かれていない（循環しうる）。自信 中。

## 4. 総合の推奨

major（直して再査読）。指摘 1 は主の統計量の作りに関わり、置換の p と許しの門の意味が変わりうる。指摘 2 は選びと止めが個人内のばらつきと時間の不安定さを持たない合成で決まる。他は文の直しで消える。

## 5. 読めなかった範囲と注入の疑い

読んでいない: sens の notes.md・pinned.py・calibration.json、ten の notes.md、nfs の notes.md、hmm2.py、data.py と ml.py の該当以外、supplement.tex の S2〜S5。ハッシュの値は照合していない。論文 3 の数は supplement.tex 395・425〜426 行と一致。注入の疑いなし。
