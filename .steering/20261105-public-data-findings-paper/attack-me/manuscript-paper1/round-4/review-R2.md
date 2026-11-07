# review R2（manuscript round 4・教育データの予測・検出の評価の実務・メインが要約して保存）

推奨: **minor**。接地: Pelánek 2015（"The choice of suitable metric depends on the intended use of a student model."・"To be important, differences between models should either have impact on student practice or lead to interpretable and actionable results."・"it is useful to analyze correlations of model predictions"）・Gardner & Brooks 2018（"this approach naïvely assumes that any differences observed must be due to genuine differences"・"we use ROPE = 0.01"）から逐語。評価 a3・b3・c3・d3・e4・f4。主の値・閾値の表（0.1030/0.0927/0.0958）・X17 は出どころと一致。

引き継ぎの判定: 1 題名 解消／2 停滞の定義と打鍵の量 解消（S9 は supplement 383-386 に直った・nit N2 が残る）／3 基準率 解消（5 s・10 s の基準率は数値なし → 下の 4）／4 要旨の比べの相手 一部（→ 下の 2）／5 版の DOI 解消／6 英語の要約と manifest 解消（nit N3）／7 但し書きの繰り返し 一部（5.2% と漏れがそれぞれ 4 か所）／8 要旨の語数 解消／9 一部（S10 と 247/428 は直った・予測の相関は無い）。

指摘:
- [major] 貢献を「比べの相手の選び方」に置くがデータは示していない: intro 72-73「the result shows which comparison partner exposes a weak run-up signal」・conclusion 9-10「...is how we would check another.」対 discussion 43-45（揃えない比べでも上がらず判定できない）・59「our data do not show an effect of the way of matching」。揃えない比べ 0.497/0.494 も帯の中、学習器では揃えた方が高い（0.567 対 0.529）。JEDM の "generalizable methodologies or comparative analyses" の柱にあたる。→ 序論の文を「この比べの相手で 1 つの推定器を判定した例で、比べの相手が結論を変えるかは示していない」に、結論の最後の文を手順を公開した事実の言い方に。新しい解析は要らない。自信 高。
- [minor] 「simple quantities ... 0.04--0.08 higher」は比べの相手（変化か水準か）と主体（学習器か単一の量か）が混ざる: 0.04 は水準との差・0.08 は変化との差、勾配ブースティングは水準を明確に上回らない、単一の量（押下の数 0.446）は 0.5 の下。→ 主体と相手を分けて書く。自信 高。
- [minor] discussion 41-42「What the registration establishes ... including after removing stalls that contain events inside the pause」が [C-D] の感度を登録の確立に含める（design 100-101「do not enter the decision」）。→ 分けて書く。自信 中。
- [minor] discussion 19-20「a trigger that waits longer in the pause meets a higher base rate」が数値なし。→ 2・5・10 s 以上の間のうち停滞になった割合を 1 文で足すか「(not computed)」に下げる。自信 中。
- [minor] X17 の解釈の文（results 205-206「Part of this difference comes from the definition of a stall」）が事前の読み方（中間は値だけ・reading_rule "between"）を越える。→ consistent with に下げ、s − u = 30 s でも 0.467 と並べるか、読み方を明記。自信 中。
- [minor] 但し書きの 4 重の繰り返しと序論の推定器の記述（intro 41-48）が data 46-52・S3 と重なる。→ 設計は値と出どころだけ、限界は新しい情報だけ、序論の第 4 段は型と手で決めた係数に絞る。300〜400 語減の見込み。自信 中。
- [nit] N2 X17 の 2 群の和 3,426 + 1,057 = 4,483 が 4,554 に 71 足りない（JSON は s − u > 30 s の行 118）。→ 残りの 71 をどちらにも入れないと 1 句。自信 高。
- [nit] N3 manifest の 3 件の括弧が 2 件に読める（README と同じ書き方に）。自信 高。
- [nit] 学習器と信号の予測の相関が無い（Pelánek）。自信 低。
- [nit] 陽性対照の表が ×1.05・×1.2・r = 0.02・0.1 を載せない（記録にあり同じ区分）。→ 行を足すかキャプションに。自信 中。

読めなかった範囲: references.bib・papers の README・estimator/README・rerun_confirm.py・事前登録・逸脱・prefreeze の notes・探索の conditions の原文・多くの JSON・round3-checks の conditions・文献の記録。照合は該当の値だけ。注入の疑い: なし。
