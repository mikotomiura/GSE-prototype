# review-R2（outline round 4）
接地: Gardner & Brooks 2018 "Little attention has been paid to hyperparameter tuning in prior work, despite the fact that tuning each additional hyperparameter setting adds an additional hypothesis test or pairwise comparison to an experiment."・"hyperparameter tuning is frequently not described in published research ... with no reproducible procedure offered."・"the impact of these methods is compounded by large numbers of hypotheses being tested ..."・Pelánek 2015 "To be important, differences between models should either have impact on student practice or lead to interpretable and actionable results."・"The choice of suitable metric depends on the intended use of a student model. …"・"the use of the AUC metric may be justifiable, but the justification needs to be explicitly discussed (which is not a current practice)."
carryover: 押下の率・止まりの条件・4 倍・縮む・[V439]・推奨 3 は解消。機構は一部（考察の −0.93）。一般化の橋は一部。
評価表: a 2・b 3・c 2・d 4・e 4・f 3。
指摘:
- [major] いちばん強い主張が結果を見て選び直した 2 つ目の共変量に乗るのに「確立」（l.48・l.19・conditions-round3.md）。共変量の選び直しは比べの 1 回。解消: 強さを「探索的（共変量は 2 つ目の選択）」に・「揃った（探索的）」と書く・または生の値の幅を中心にし速さの固定を副に・3.5 に共変量を選んだ回数。自信 高
- [major] 「速さを固定した値を並べよ」が何の推定量で、どの使い道に効くかを書かない（l.70・l.38・l.82）。解消: 「両方を並べ、目的で選ぶ」に弱め考察に 2〜3 文（予測・検出なら生の値、構成概念として読むなら固定した値）・または説明力の増分を 1 つ。自信 高
- [major] 固定に使う量の 2 秒が振られていない（l.28）。解消: 「停滞の定義によらない（速さの閾値は 2 秒に固定）」・1・2・3 秒の感度を S3 に・または限界 6 に。自信 中
- [major] 考察の −0.93 は 0.93 と同じ型（l.66）。解消: 外すか同じ文に「代数でほぼ出る」と。自信 中
- [minor] 正の 10 のうち |ρ| ≥ 0.1 の数と、偏相関の |·| < 0.1 の 16 を書く（l.48・l.108・l.34）。自信 中
- [minor] 入れ替わりは W 15 秒だけで、その水準の根拠がいちばん弱い。解消: 「W 15 秒を除くと生の値の正は 0」を 4.1 に。自信 中
- [minor] 題と主張が KLiCKe の 1 つの得点に限っていない（l.8・l.38）。自信 中
- [nit] 抑制を統計の文献に位置づけていない。自信 低
総合: major。
読めなかった範囲: 補足の大半・カード 3 枚。注入なし。
