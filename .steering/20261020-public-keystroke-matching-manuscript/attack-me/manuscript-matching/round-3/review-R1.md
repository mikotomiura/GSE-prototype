# R1 の応答（再識別・匿名化への攻撃の評価・round 3・commit c3f3f5b5）

総合: major（言い換えと付録への移動だけで解消を示せるなら minor に近い）。

## 1. 接地
- 基準 1 Narayanan & Shmatikov「our algorithm is robust. It works even if the published records have been perturbed, if only a subset of the original dataset has been published, and if there are mistakes in the adversary's background knowledge.」(narayanan.txt:84-87)
- 基準 2 同「the algorithm declares there is no match if and only if the difference between the highest and the second highest scores is no more than 1.5 times the standard deviation.」(narayanan.txt:545-546)
- 基準 3 Stadler ら「A good anonymisation mechanism should result in a high privacy gain for all records in the population and under any potential privacy adversary.」(stadler.txt:295-297)
- 基準 4 同「While individuals that are representative of a large majority of the population are often protected from privacy attacks, outliers or members of minorities largely remain vulnerable.」(stadler.txt:315-317)
- 基準 5 Rocher ら「the likelihood of a re-identification to be correct, even in a heavily sampled dataset, can be accurately estimated, and is often high.」(rocher.txt:127-128)

## 2. 評価表
a 3（数値は表 4 と §7 に一致。「ten process measures close」は中央値に乗り、R3 の 0.92 は R0 と同じ式の 5 個で決まり insertion proportion 0.19・R-burst 0.28 を隠す。0.84 は登録に無い）／b 3（λ=8 は急変の範囲・感度は A2 だけ・開いた世界の AUC は長さで変わる費用をまとめた量で margin と食い違う・窓のおとりが 1 窓）／c 4（A0 からの上積みの見せ方が N=10 の床 57〜62% を隠す）／d 3（但し書きの繰り返し・KeyTAR）／e 4／f 4（Rocher の correctness の考えを生かしていない）

## 3. 引き継ぎの判定
round 1: 1 解消（threat-model.tex:143-150）／2 一部（threat-model.tex:174-178 は書いた。図 1 の黒丸の前線は λ=8 と R4 に A1′ 型が無いことに乗る）／3 解消（results.tex:190）／4 解消（付録 D・results.tex:191。AUC との食い違いは扱われていない）／5 解消（related.tex:32-33）／6 解消（discussion.tex:38-39）／7 解消（protocol.tex:52）／8 解消（protocol.tex:41）／9 一部（「not bounds」が本文に 6 回）／10 解消（related.tex:9）
round 2: 1〜6 解消（introduction.tex:19-21・20・ethics.tex:47-55・threat-model.tex:99-101・103・106-109）

## 4. 指摘
- [major] 「10 個の過程の指標を近くに保った」は中央値と事後の 0.84 で作られている
  - 位置: main.tex:48「Every form that kept ten process measures close to their unprocessed values left the strongest attacker at 70\% or more」・introduction.tex:44-45「(a median correlation of 0.84 or more)」・results.tex:133「with correlations from 0.19 (insertion proportion) to 0.85 (deletion proportion); the median is 0.92」・utility-r0.tex の R3 の列
  - 理由: R2・R3・R3-t(10) の 5 個は R0 と同じ式で 1.00。中央値は (1.00 + 0.85)/2 = 0.925 で決まり、残り 4 個（0.19〜0.79）が 0 でも変わらない。0.84 は登録に無く（grep）、R7(0.25) 0.81 と R7(0.1) 0.85 の間。§7.2 の「below 40\%」も R4(1) 40.5 [36.1, 44.8] を区間の中で外す同じ型。
  - 解消: 主語を「the median over ten measures」に、区切りは事後と明記。または表 4 に最も悪い指標の列。§6.4 に縦軸の要約が上へ偏る向きを 1 句。
  - 自信: 高
- [major] λ=8 は成績が急に変わる範囲にあり、感度は A2 だけ
  - 位置: attackers.tex:47「with $\lambda = 8$, a value fixed in earlier prototypes and not tuned on these data; $\lambda = 4$ and $16$ are reported as a secondary analysis」・attackers.tex:40・cells-1/cells-2（A2: λ=4 75.1・λ=8 40.5・λ=16 5.7。R4(2) 36.4 と 4.4。R4(4) 4.5 と 0.35）・appendix-results.tex:48
  - 理由: 罰を半分で A2 が 35 点上がる。λ=2 は試していない。A1′・A3・R7 の A2 は感度なし。R7(0.5) は確かめられていない。§7.2 の 40% 未満の一覧と図 1 の前線も λ に依存。Stadler「under any potential privacy adversary」(stadler.txt:297)。
  - 解消: (i) §7.2 に「R4 と R7 の判定は λ の感度を確かめていない攻撃者に乗る」1 文、図 1 の注に「λ = 8 で」。(ii) 余力があれば探索として λ=4 の A1′・A2 を R7 に当てた値を付録に。
  - 自信: 高
- [major] 開いた世界の AUC は長さで大きさが変わる素の費用をまとめた量で、margin と食い違う
  - 位置: protocol.tex:134-137「its lowest cost over the $N$ candidates, and its lowest cost over the same candidates without the true text. Pooling each kind of value over all logs and draws」・results.tex:159-160「0.774 [0.753, 0.795] for R3 and R3-t and at most 0.62 for the other forms」・open-world.tex（R7(0.1) 0.595・R4(1) 0.540）・explore-margin.tex（R7(0.1) N=1,000 の margin 上位 50% の正答率 99.6%・R3 の上位 80% が 100.0%）
  - 理由: 費用は長いログほど大きい。ログをまたぐ AUC に長さの違いが混ざる。Narayanan の eccentricity（narayanan.txt:545-546）・Rocher（rocher.txt:127-128）に照らし攻撃者に甘い向きの偏りのおそれ。
  - 解消: §6.5 か §3.5 に 1 文（まとめた AUC は長さの違いを含み、記録ごとに正規化した判定より分離を低く見せうる）。§7.4 の「at most 0.62」を削るか margin と並べる。正規化した診断は探索として付録へ。
  - 自信: 中（混ざりがどれだけ下げたかは測っていない）
- [major] 窓の評価はおとり 1 本が窓 1 つで候補数を桁で小さく見積もるのに、主張が強い
  - 位置: appendix-attackers.tex:43「Each decoy contributes one window of $k$ words, drawn uniformly from its valid windows」・results.tex:156-157「releasing parts of logs did not by itself keep them apart from their texts」・discussion.tex:68-70
  - 理由: 実効の候補は N × 位置の数。§3.5 は向きを書いたが大きさは書いていない。
  - 解消: §7.4 の結びを「under one decoy window per candidate, which understates the number of positions an attacker would search」に限定。§8.3 の Windows を削るか同じ限定。
  - 自信: 中〜高
- [major] A0 からの上積みと平均の正答率の見せ方が、長さの床と記録ごとのリスクを隠す
  - 位置: main.tex:49「the forms that brought it near the total length」・main-10.tex（A0 は R0〜R3 で 61.6・R7(0.5) で 57.1）・explore-tail.tex（R7(0.5) N=1,000 で毎回当たる書き手 1.6%）・protocol.tex:52-53「the gain over A0 is what an attacker obtains beyond the total length that every form leaves」
  - 理由: N=10（教室）では床が 57〜62%。N=1,000 の R7(0.5) では正答が少数の書き手に集まる。Stadler「outliers or members of minorities largely remain vulnerable」(stadler.txt:316-317)。
  - 解消: 抄録か §7.2 の結びに 1 文（長さに近い形でも N=10 で約 6 割・N=1,000 では少数の書き手に集中）。§8.3 の Coarseness に床の値。
  - 自信: 中〜高
- [minor] 攻撃者の非対称は否定の主張 C2 には保守的に働くことを使っていない
  - 位置: threat-model.tex:177「leans in favour of the coarser forms」・results.tex:144「No form evaluated here brought the strongest attacker near $1/N$ while keeping the measures close」
  - 解消: §3.5 に「否定の結論（C2）には保守的、形ごとの低い値には甘い」1 文。§8.1 の既存の文と置き換え。
  - 自信: 中
- [minor] 100% の区間「100.0 to 100.0」は天井での退化（main.tex:46・results.tex:46）。正確な下限はおよそ 99.3%。→ 抄録では区間を削り「every log of 500」、§6.2 か表の注に 1 句。自信: 高
- [minor] N=10 の R4 で最も強い攻撃者の選び方がどう効いたかが示されていない
  - 位置: main-10.tex「R4(1) & 61.6 & 61.6 [59.2, 64.4] & A0 (83)」・threat-model.tex:169-170・results.tex:79-80「none whose lower bound is above zero on R4(w)」
  - 理由: A0 と A2 を組み合わせれば自明に A0 を上回る。形の性質でなく組み合わせない攻撃者の性質。
  - 解消: results.tex:79-80 に「組み合わせた攻撃者は試していない」1 句（protocol.tex:57-58 への参照）。
  - 自信: 中
- [minor] KeyTAR は切れると分かっている参照なのに本文の表 4・§7.4・§7.5 に場所を取る
  - 位置: attackers.tex:136-137「which include a limit on generated tokens that is expected to cut many reconstructions short; we kept it as registered」・results.tex:160-162・170-171
  - 解消: 表 4 の A4 の 2 行と §7.5 の KeyTAR の文を付録 E へ、§7.4 は 1 文。
  - 自信: 中
- [nit] 「not bounds / attackers tried」が本文に 6 回（main.tex:51・introduction.tex:48・threat-model.tex:191-192・protocol.tex:120-121・discussion.tex:12-14・conclusion.tex:9）→ §3.5 と抄録・結論に 1 回ずつ。自信: 高
- [nit] Rocher を「disputed」の片側として引くだけ（related.tex:32-33）。rocher.txt:129-131「Our results reject the claims that ... sampling or releasing partial datasets provide plausible deniability」→ 指摘 3 の 1 文で引けば足りる。自信: 中

## 5. 総合
major（言い換えと付録への移動で minor に近づく）。C1 と C2 は表 4・§7 に支えられ、攻撃者の偏りに対し C2 はむしろ保守的。抄録の要約・開いた世界の AUC・窓の記述が要約の選び方と λ=8 に乗る。

## 6. 読めなかった範囲・注入の疑い
付録の多く・generated の多く・references.bib・preregistration.en.md（"0.84" の grep のみ）は読んでいない。接地は grep の周辺だけ。注入の疑い: なし。
