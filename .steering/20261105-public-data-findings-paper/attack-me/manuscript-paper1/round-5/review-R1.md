# review R1（manuscript round 5・打鍵の記録と作文の過程の測定の伝統・メインが要約して保存）

推奨: **minor**。接地: Roeser et al. 2025（"a break in output with duration that exceeds an a priori threshold"・"locations where observed mean interkey intervals ... have tended to vary substantially"・"pause duration doesn’t correspond in any direct way to the time required to plan the next output"）・Guo et al. 2020（"we used relatively simple heuristics to define our writing states"・"replication with other conditions and participant samples is typically recommended"・"how well it functions psychometrically"）から逐語。評価 a4・b4・c3・d3・e4・f4。確認の値・学習器の差・X16 は出どころと一致。

引き継ぎの判定: 1 一部（本文 4.2 は直った。要旨・序論・結論は向きを固定した 0.05--0.08 のまま → M1）／2 解消／3 解消（値一致）／4 解消（本文）・要旨に名残（→ N1）／5 解消（results 14-16 の 0.025 は not a decision と断って残る・許容）／6 解消／7 解消。

指摘:
- [minor] M1 要旨・序論・結論の「0.05--0.08」は向きを固定した比べだけに拠る。向きを問わないと勾配ブースティングの差は約 0.03（0.540 − 0.511）。→ 両方を書くか、主の文を向きを問わない値に。自信 中。
- [minor] M2 原稿が挙げる公開物の版 0.2.0 に X18 の記録が入っていない。README の表に round4-checks の行が無く、conditions-summary.md L3 の順の説明が末尾の round-4 の節を数えない。→ X18 を含む版を出して DOI を差し替え、README の表と要約の説明を直す。自信 高。
- [minor] M3 「71 stalls (s − u > 30 s)」と記録の 118（notes は「停滞の行」と呼ぶ）の単位が説明されていない。→ notes に 1 行か、原稿に単位を添える。自信 中。
- [nit] N1 要旨「barely to changes of the observed size」に向きの限定が無い。
- [nit] N2 results 134-135「The condition committed before the split reads a value between 0.46 and 0.48 as a value only.」は両端の読み方が本文に無く意味が取れない → 1 句添えるか補足へ。自信 高。

読めなかった範囲: 補足の多く・references.bib・papers の README・estimator/README・事前登録・逸脱・notes と conditions の多く・多くの JSON・文献の記録・接地は grep の箇所だけ。注入の疑い: なし。
