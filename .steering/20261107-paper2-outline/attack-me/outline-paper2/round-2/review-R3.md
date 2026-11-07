# review-R3（outline round 2）
接地: Hoffmann ら 2021「Ignoring the multiplicity of analysis strategies can therefore lead to an overconfidence in the precision of results and to research findings that do not replicate on independent data.」「In explanatory modelling, confidence intervals and hypothesis tests typically only account for sampling uncertainty, while ignoring measurement and epistemic uncertainty.」「acknowledge the inherent uncertainty in the presented research findings and thereby avoid misleading readers into overinterpretation of the relevance of the results.」「Strictly confirmatory analyses can be realized either through the pre-registration of analysis plans [...] where the analysis strategy is specified in detail before observing the data」「publish all research code, data and material, …」・Kapoor & Narayanan 2023「claims about a model's performance need to be connected to scientific claims using explicit arguments. …」「the claims made in model info sheets cannot be verified in the absence of computational reproducibility.」「… should look beyond headline performance numbers when assessing papers.」
carryover 12 件: 解消 8・一部 4。
評価表: a 3・b 3・c 4・d 4・e 3・f 4。
指摘:
- [major] M1 「逆の結論」が効果量と釣り合わない（l.32・l.8）。n=4,908 で |ρ|≈0.03 でも区間が 0 を外れる（例 W15_q0.95_net_replay は 0.026 [−0.002, 0.053]）。条件 b5687936 の「1 つでもあれば」は甘い。解消: 大きさの帯を書く・読者の結論が変わる場面を具体的に・題を弱める・基準の甘さを 1 文。自信 高
- [major] M2 CS1 の 2 年版の比の逆転は 25% に届かず、ほぼ固定 θ の族だけ（notes.md:68・:74 の 2/53）。解消: いちばん強い主張の根拠から外すか族を明記し 25% に届かないことを 4.1 に。自信 高
- [major] M3 得点の正の 10 通りは W 15 秒・本人の分位に集まり、W の水準が擁護できる理由が無い（l.44・l.100）。解消: 3.3 に W の根拠・無ければ感度の端と明示・入れ替わりは W 15 秒に限られると見出しと同じ段に。自信 中
- [major] M4 取り置きの書き手の扱いが外から再現できない（CoAuthor と CS1 2021 は取り置きを除いた部分集合・ID は出さない）。解消: 取り置きの作り方を seed つきの規則で書く・除いた単位の識別子か照合値を公開・どれもできなければ全員で回した要約を補足に。自信 中
- [minor] m1 課題文の交絡が主の数に入っていない（notes.md:71 課題文ごとの中央値 −0.24〜+0.15）。解消: 課題文ごとの中央値で数えた正負の数を 1 文。自信 中
- [minor] m2 比の逆転の数は基準の比が 1 にどれだけ近いかで決まる（CS1 2019 / KLiCKe の基準 0.86）。解消: 対数の比の範囲を並べ、組の間で数を比べないと 1 文。自信 中
- [minor] m3 [条件] の印が追加の条件（b5687936・主の結果を見た後）まで同じ重み。解消: [条件・主] と [条件・追加] に分けるか 1 度書く。自信 高
- [nit] n1 区間は書き手の再標本だけで定義の揺れは別に数える理由を 3.4 に 1 文。n2 全体の検定をしないなら「数は記述」と 1 文（[V480]）。n3 [V439] の本文が未照合。
総合: major（いちばん強い主張の 2 本の脚が見出しより狭い中身に支えられる。M4 は原稿の前に方針を）。
読めなかった範囲: 接地の参考文献の後半・補足の多く。注入なし。
