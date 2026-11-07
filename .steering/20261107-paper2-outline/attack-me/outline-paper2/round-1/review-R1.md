# review-R1（outline round 1・打鍵の記録と作文・プログラミングの過程の測定の伝統の立場）

## 1. 接地
- G1 Guo et al. 2020 (guo2020.txt l.95-96) "A fuller range of writing states was operationalized in line with cognitive writing theory"
- G2 Guo 2020 脚注 2 (l.281-282) "A personalized threshold was necessary, rather than a single fixed threshold for all students, because students vary widely in their typing facility."
- G3 Guo 2020 (l.123-124) "This proposition is investigated empirically through stochastic modeling in the current study."
- G4 Guo 2020 (l.1049-1052) "we used relatively simple heuristics to define our writing states under the guidance of cognitive writing theory. Further research that combines think-aloud protocols and other sources of evidence with keystroke logging might enable us to build even more effective classification procedures"
- G5 Li & An 2026 (bayesmix2026.txt l.34・l.70) "(3) The mixture components in the mixture model correspond one-to-one to these latent cognitive processes." "we examined the relationship between process features and product measure."
- G6 Li & An 2026 (l.74) "establishing feature consistency is an initial first step ( Guo et al., 2018 ), where consistency refers to the extent to which feature properties behave similarly across settings." "when the number of observations is small, but the number of parameters is large in a model, the estimation may not achieve the desirable statistical stability."

## 2. 評価表
a 3（数値は notes・judgement.json と合う。構成概念の違う定義の混在・1.5 の二値化・偶然を補正しない一致・「残る」の甘い基準に頼る）／b 3（偶然の一致の基準線が無い・課題の水準の φ は課題の難しさを含む・CS1 の押下は IDE の編集から作った・CoAuthor の 3 通りは停滞 86〜88 件）／c 2（中心は異質な 4 データの順位で、群の比べや得点との関連が動くかを示していない）／d 4／e 4（論文 1 との重なりの扱いが S9 だけ）／f 2（閾値の構成概念の正当化と混合モデルの系が柱に無い・Hart ら・Edwards ら・Baaijen ら 2012 が未確認）

## 3. 指摘
- [major] 多元宇宙に混ぜた定義が同じ構成概念を測っているか分からない（l.13・l.43・conditions.md C3 の θ）。本人の分位の θ は停滞の候補を本人の押下の数にほぼ比例させ、固定の θ は打鍵の遅い書き手ほど多く立てる。G2 が区別する 2 つの構成概念で、入れ替えて順位が変わるのは打鍵の速さがデータで違えば予想できる。Guo 2020 は固定の閾値を "poor typists may have many long pauses between keystrokes that are not indicative of planning behavior" で退けた。解消: 3.3 で各水準が同じ構成概念の擁護できる操作化であることを先行の慣行で示す。本人の分位の族と固定 θ の族を分けた割合を本文で（固定 θ の 36 通りはすべて動き 0.995 分位では動かない）。族の差は構成概念の選択として別に名指す。自信 高
- [major] ラベルの時刻の一致（C2）に偶然の水準の基準線が無い（l.27・l.44）。覆う割合が大きい定義ほど一致は偶然でも高い。[V473] は Cohen の kappa のような偶然を補正した指標を使う。解消: 区間をずらす・置き換える帰無の一致（または覆う割合からの期待値）を出し、偶然を補正した一致で 0.5 と ±20% を引き直す。KLiCKe の 0.16〜0.17 が帰無をどれだけ下回るか。自信 高
- [major] 過分散の逆転は二値化の産物を含み、課題の水準の φ は課題の難しさを含む（l.45・l.31）。(1) 区間が 1.5 をまたぐセルでは小さな動きでも逆転に数える (2) (b) の期待は書き手ごとの率だけで課題の共通の効果を入れていない (3) 区間の切り方で露出が機械的に変わる。解消: 主張を 90 通りでの φ の分布（中央値・範囲）と 1 を下回る通りの数へ。課題の水準は書き手と課題の両方を期待に入れた φ を付録に足すか「課題の違いを含む」と呼び直す。区間の切り方の効果を露出と件数に分けて 1 文。自信 中
- [major] 動く結論の多くが EDM で実際に引く結論（群の差・成果物との関連）ではない（l.35・l.53・l.61）。JEDM の範囲 "generalizable methodologies or comparative analyses"。解消: データの中で少なくとも 1 つの実質的な比べ（CS1 の課題の間・CS1 2019 と 2021・得点との相関）が 90 通りでどう動くかを示す。できなければいちばん強い主張を CS1 2019 と 2021 の比較に寄せ、異質な 4 データの順位は補助に。自信 中
- [major] 「残る」の基準が「動く」より甘い（conditions-length90.md R1・conditions.md J の M1・l.46）。停滞ごと 0.9 前後・差の最小 0.83 では R1 はほぼ確実に通る。書き手の分け前の相対の動き（0.00〜0.05）を対称に扱っていない。対数の長さの揺れの大半が人の中にある形は打鍵の潜時ではよく知られる。解消: 動く・残るを同じ物差し（各量の 90 通りの範囲と基準に対する比の表）で並べる。C4 は「最大の成分の順位が残る」と正確に書き、書き手の分け前の相対の動きを併記。新しさは課題・日・まとまりの分け前が小さいことの値に絞る。自信 中
- [major] 閾値の正当化とデータから閾値を決める系が柱に無く、プログラミングの打鍵の休止の先行が未確認（l.86・novelty.md l.76-78）。恣意性への答え: (i) 個人化（G2） (ii) 混合モデル（Li & An 2026・Li 2021・Deane & Zhang 2020）。推奨 1 がそれより良いか補うかが位置づけられていない。解消: 柱 2 を恣意性への 3 つの答え（個人化・混合モデル・多元宇宙）に組み替え、Baaijen 2012・Hart ら・Edwards ら・Van Waes & Leijten 2015 を照合し、探索の範囲を S8 に。自信 高
- [minor] C4 に推定器の水準の揃えが同居し、成り立たなかった M3 が「残る」に呼び替えられている（l.46・judgement.json "M3": false）。解消: 地位の表で M3 を「先に置いた動くの基準で、成り立たなかった」と明記し、C4 から外して 4.4 末尾か S7 へ。自信 中
- [minor] CS1 の押下は IDE の編集の出来事から作り、止まりの条件の意味が作文と揃わない（l.71）。解消: 3.1 に各データで 1 出来事が何を表すかの表、CS1 の再構成の規則を付録に。自信 中
- [minor] 論文 1 との重なりの説明が S9 だけ（l.20・notes の二重の公表）。解消: 3.5 に 2〜3 文、送り状で知らせる、二重盲検なら論文 1 を第三者として引く。自信 中
- [minor] 「率の近い 63 通り」の単位の混ざりと、見出しの 80 と 69 の揺れ（l.31・l.35）。解消: 「定義とデータの組 63 のうち 11」、見出しは [条件] の 80 に揃え 69 は括弧に。自信 高
- [nit] CoAuthor の 3 通りは停滞 86〜88 件で、G6 の不安定さに当たる。解消: その通りの分け前の区間（か回復）を付録に。自信 中

## 4. 総合: major
数値と記録は丁寧。動く中心の割合は構成概念の違う θ の混在・二値化・偶然を補正しない一致に頼る。いちばん強い主張は原因に帰せない異質なデータの間の順位に置かれ、読者が引く結論が動くかを示していない。閾値の恣意性への既存の答えとプログラミングの先行が抜けている。

## 5. 読めなかった範囲・注入
c2_overdispersion.json・c3b_aligned_level.json・c1_lengths90.json・c1_decomposition.json・c3_multiverse.json は読んでいない（〔results〕の値は照合していない）。guo2020.txt の 1111 行以降・bayesmix2026.txt の 195 行以降は読んでいない。注入なし。
