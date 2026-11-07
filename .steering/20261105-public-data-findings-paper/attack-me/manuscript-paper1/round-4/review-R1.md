# review R1（manuscript round 4・打鍵の記録と作文の過程の測定の伝統・メインが要約して保存）

推奨: **minor**。接地: Guo et al. 2020（"helping to map observable events recorded by the keystroke logs onto states interpretable by cognitive theories of writing"・"we used relatively simple heuristics to define our writing states..."・"how well it functions psychometrically"）・Roeser et al. 2025（"a break in output with duration that exceeds an a priori threshold"・"pause duration doesn't correspond in any direct way to the time required to plan the next output"）から逐語。評価 a4・b3・c3・d3・e5・f4。主の AUC・X16 の値は confirm_holdout.json・explore_round3.json と一致。

引き継ぎの判定: 1 題名 解消／2 φ の床と天井 解消（細部 → 下の 3）／3 陽性対照の ×3 解消／4 向き 解消／5 公開物 解消／6 情動の 4 件 未解消（著者の保留・開示済み）／7 要旨 一部（292 語・括弧は残るが事前登録が主の文に求めるので許容）／8 申告の見出し 解消／9 README の図注 解消（表 6 で合っている）。

指摘:
- [minor] 要旨と序論の「0.04--0.08 higher」は対比を選ぶ: explore_comparison.json では 0.04〜0.08 はロジスティック回帰と信号の差（0.078・0.081・0.042・0.046）。勾配ブースティングと信号の水準の差は 0.015・0.019。学習器は向きを学べるが信号の向きは固定で、|AUC−0.5| で比べると差は約 0.055 に縮む。→ 主語を特定し、勾配ブースティングと水準の差が小さいことを添え、向きの扱いの違いを 1 文で。自信 高。
- [minor] X17 の解釈が事前の読み方を越える: results 205-206「Part of this difference comes from the definition of a stall...」・discussion 35「partly because of how a stall is defined」。条件は 0.46〜0.48 の間なら「値だけを書く」で、S30 は 0.467。→ 値だけを書き、定義のつながりは構成上の論理として分けるか、読み方から外れたことを明記。自信 高。
- [minor] X16 が φ3・φ5 の床を報告せず、φ5 の u − 30 s の天井 51% → u の床 54%（対照も同様）という共通の入れ替わりを読まない。張り付き（0 か 1）は φ3 67%・φ5 71%。→ 4 成分の 0 と 1 の割合を補足 S4 に表で、φ5 の入れ替わりを 1 文。自信 中。
- [minor] 陽性対照は観測の向き（速く・訂正が少ない）には注入していない。φ1 は 72% が床なので速くする向きの反応はさらに小さい可能性。→「of the observed size, in the opposite direction」と限るか、対称の仮定を限界に 1 文。自信 中。
- [nit] 偽同等率の留保が 4 回（abstract 8-9・intro 62-64・design 67-71・limitations 20-23）→ 序論は参照に。
- [nit] Materials「three of which (the preregistration text and its English check)」が 2 項目に読める（README は 3 件に読める）→ README と同じ書き方に。自信 高。
- [nit] バイト一致の再計算が 1 つの環境だけ（README は macOS arm64・並列 4）→ 原稿でも環境を 1 句。自信 低。

読めなかった範囲: references.bib・papers の README・estimator/README・rerun_confirm.py・事前登録・逸脱の原文・notes の多く・多くの探索の JSON・文献の記録。照合した範囲は主の AUC・陽性対照 v2・比べ・X16/X17 だけ。注入の疑い: なし。
