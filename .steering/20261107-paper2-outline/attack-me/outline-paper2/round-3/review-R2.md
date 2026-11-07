# review-R2（outline round 3）
接地: Gardner & Brooks 2018 "Clearly describe or document methods for statistical algorithm and hyperparameter selection, prediction architectures, and model evaluation in published work."・"provides no robustness against spurious results, no measure of confidence in the conclusion given the observed data, and little basis for comparison across studies"・"[i]f the results on different data sets are not comparable, their averages are meaningless"・Pelánek 2015 "The choice of suitable metric depends on the intended use of a student model."・"To be important, differences between models should either have impact on student practice or lead to interpretable and actionable results."・"metrics can indicate good performance even through good results are achieved mainly due to the variability in data, …"
注: 依頼文は Gardner, Brooks & Baker 2018 と書くが本文の著者欄は 2 名。
carryover 8 件: すべて解消（[V439] の照合は解消・位置づけは下の M3）。不採用 2 件は釣り合っている。
評価表: a 2・b 3・c 3・d 4・e 4・f 3。
指摘:
- [major] M1 「流暢さを固定するとどの定義でも関連は縮む」は集計と合わない（l.34・notes l.88）。偏相関の絶対値が元より大きい通りが約 16（例 W15_q0.95_ins_g5 は −0.087 → +0.106）。解消: 「|0.11| 以下に収まる（大きくなる通りもある）」に。自信 高
- [major] M2 先に置いた機構の予測が外れたことが外枠に無く、事後の 0.93 が中心に。0.93 は偏相関が小さいことの言い換え（ρ ≈ 0.62×P1）。解消: 3.5 の表と限界 5 に「支持されなかった（P1 中央値 −0.16 < +0.3）」・後半を算術の分解として書く・「機構」「動かす量を名指す」を弱める。自信 高
- [major] M3 [V439] は打鍵の速さを調整しても負が残った（抄録 "even after accounting for their typing speed and general pausing"）のに位置づけに使っていない。解消: C1 の比べと考察に、[V439] は調整後も負・論文 2 は調整後 |0.11| 以下で符号が割れる、と対比・新しさは「定義の空間の上で調整前後の関連がどう分布するか」に。自信 高
- [major] M5 「流暢さ」は停滞の時間を分母に含み、固定は停滞の一部の固定を含む。解消: 1 文・名を「押下の率（休止を含む時間あたり）」に・主張を「押下の率を固定すると」に限る。自信 中
- [major] M6 推奨 1 の固定後の値の符号は止まりの条件でほぼ決まり（正 48 は文字だけの 45 と W15_fix30s_net の 3）、実務家はどちらを使えばよいか分からない。流暢さは得点の構成概念の一部かもしれない。解消: 4.1 と図 2 の色分けで軸を示す・推奨 1 に固定前と固定後が答える問いを添える。自信 高
- [minor] M4 「4 倍」は基準に錨を下ろした比。解消: ρ の幅（−0.25〜+0.14）か ρ² で。自信 中
- [minor] M7 推奨 3「1 つの定義で報告してよい」は CS1 の 2 年版からの許可。解消: 観察の形か範囲を限る。自信 中
- [nit] N1 「1 つの定義では、関連の大きさが 4 倍まで変わり」は「どの定義を選ぶかで」に。自信 高
総合: major（どれも新しいデータを要しない。止まりの条件で符号が分かれることは実務家が持ち帰れる新しい事実）。
読めなかった範囲: gardner2018 の後半・条件 3 つ・results の多く・カード 2 枚。注入なし。
