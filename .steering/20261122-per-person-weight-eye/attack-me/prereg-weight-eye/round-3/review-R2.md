# R2 査読 round 3（本人ごとのモデル・個人差の立場）

## 接地
- Fisher 2018 "Researchers should explicitly test for equivalence of processes at the individual and group level"／"all models should be evaluated in terms of how well they represent individual-level processes before making generalizations from aggregate estimates"
- Fisher 2018 "the data sampled within an individual in time must be representative of that individual generally (i.e., stationary)"
- Fisher 2018 "statistical estimates of repeated-measures data can be biased due to temporal dependence"／"nonergodicity in the natural sciences may also be driven by variation in temporal dependencies across individuals"
- Adolf & Fried 2019 "Empirical quests into nonergodicity therefore need to incorporate variance sources at both levels."／"failure to distinguish them will mischaracterize both processes"
- Adolf & Fried 2019 "ergodicity holds conditional on (i.e., after controlling for) sources of heterogeneity between individuals and/or instability over time"／"whether the resulting conditional inferences remain meaningful, will depend on the phenomenon, population, and time span studied"

## 引き継ぎの判定
M1 一部（漂いの筋は CoAuthor だけで CS1 の間のセルに較正が無い・漂いの筋が非定常・N1）／M2・M3・m1・m3・m4・m5・n1・n2・n3 解消（29 の門の内訳を検算）

## 評価表
a 4（L19「目に有利な方向」に根拠なし）／b 2（N1・N2・N3）／c 3／d 3（判断の番号と括弧書きが多い・λ の出どころが表と箇条書きで重複）／e 投稿先未定／f 3（定常性と時間依存・ρ の個人差）／g 3（N2 の選び直しの分岐）

## 新しい指摘
- N1 [major] 漂いの筋が定常でなく、書き手ごとの初期の差が残る。D4「E_{w,1} = draw_D、E_{w,u} = ρ · E_{w,u−1} + (1 − ρ) · draw_D」。単位 u での E_{w,1} の重みは ρ^{u−1}（ρ = 0.9 で単位 11 に約 0.35、単位 20 に約 0.14）。書き手の間のずれの分散は ρ^{2(u−1)} + (1−ρ)²(1−ρ^{2(u−1)})/(1−ρ²) で、単位 1 の 1 から単位 16〜20 の約 0.07〜0.09 へ縮む。減衰する本人固有の成分と、後ろの単位ほど似る非定常を持ち、間を空けたセルが拾っても漂いか初期の成分かを区別できない。解消: 定常から始める（ρ = 0.9 なら 50 単位以上の空回し）、定常でのずれの大きさを用量の 3e-2 と比べる記述、「安定した差は 0」を V1 か D9 で確かめる。自信 高。
- N2 [major] 量と長さの交換可能性の確かめが、案を選んだ後にしかない。量の筋では本人の A と B が同じ長さの尺度を共有し、m = 26 の縮めの効き方が行の数に依るので、差なしでも偽の近さが案ごとに違う強さで出うる（E2・E3）。門が赤なら止め、選び直しの規則が無い。解消: 量の筋と揺れの段 0 の差なしを選びの組に加えて許しの門に入れる、または選び直しの規則を今書く。自信 中。
- N3 [major] CS1 のセルは第 1 の用量の差なしでしか門を通らないまま実データで読む。CS1 は単位の構造が CoAuthor と違い、門の結果を移す根拠が無い。解消: CS1 にも量・揺れの段 0（と漂い）を足して門に入れる、または D7 を限定する。自信 高。
- N4 [minor] 漂いの ρ が全員に同じ。ρ_w を書き手ごとに引くか、読まないことに明記。自信 中。
- N5 [minor] 量の筋の幅（0.5〜2 倍）の根拠が無く、読まないことにも入っていない。自信 中。
- N6 [nit] D9 の乱数の段の番号と、種 7000〜7039 の m_w の作り方が未定義。自信 高。
- N7 [nit] L19「目に有利な方向」の理由を 1 文か「有利と見込む」に。自信 中。

## 総合の推奨
major（直して再査読）。引き継ぎ 9 件中 8 件解消。新しく入れた漂いの筋が非定常で、この版の中心の確かめ（間を空けた対照が漂いを切り分けるか）が解釈できない。長さと量の交換可能性の確かめが選びの後で選び直しの規則が無い。CS1 は均質な帰無でしか門を通らない。

## 読めなかった範囲
SEED、sens・nfs・ten の記録と calibration.json・m0_fit.json、pinned.py、hmm2.py、supplement.tex、synth.py の大半。論文 3 の値・ハッシュ・λ = 0.191・2.4 倍は照合していない。注入の疑いなし。
