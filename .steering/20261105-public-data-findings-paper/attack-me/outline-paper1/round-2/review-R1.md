# review-R1（outline round 2・paper-reviewer・打鍵の記録と作文の過程の測定の伝統）

推奨: minor。引き継ぎ 10 件のうち 8 件が解消、F1 と m1 が一部。新しい穴は major 2・minor 4・nit 1。

## 1. 接地
- G1 Roeser et al. 2025（roeser2025.txt:162-163）"\"Pause\" in the written-production literature is used to refer to a break in output with duration that exceeds an a priori threshold."
- G2 Roeser 2025（:414-416）"interkey intervals are not directly and sufficiently determined by transition location ... but are also associated with different probabilities that a hesitation occurs."（Table 2 :527-539 の Within word / Before word / Before sentence）
- G3 Roeser 2025（:383-387）"an interkey interval at a specific linguistic edge-type can result from one of two entirely separate data generating process"
- G4 Roeser 2025（:608-610）"planning may not be reflected in sentence or word-initial hesitations when planning occurs concurrently to the execution of previous language units."
- G5 Guo et al. 2020（guo2020.txt:281-284）"A personalized threshold was necessary, rather than a single fixed threshold for all students, because students vary widely in their typing facility."
- G6 Guo 2020（:1049）"we used relatively simple heuristics to define our writing states"／（:1058-1059）"results may not necessarily generalize to a broader population or to different conditions so replication with other conditions and participant samples is typically recommended."

## 2. 引き継ぎの判定
- F1 陽性対照 → 一部。限界（:64）に入ったが、代わりに並べた水準 0.524（0.510〜0.537）自体が幅 [0.45, 0.55] の内側で、計器が幅の外の差を拾えることは示せない（N1 と連動）。
- M1・M2・M3・M4 → 解消（:55・:58／:25／:65／:82・:33）。
- m1 公開の形 → 一部（:60・場所は未決）。
- m2・m3・m4・n1 → 解消（:29・:68・:57・:69）。

## 3. 評価表
a 3（N1・N2）／b 3（47% の混入の含意が 1 句だけ・合成の離し）／c 3（手順の実演は較正と逸脱の事例に限られる・:46 が認める）／d 4／e 4（公開の場所が未決・テンプレートの説明は未照合）／f 4（並列の説の精度・N7）

## 4. 指摘
- [major] N1 持ち帰りの「水準は 0.5 から離れたが、手前の上がりは離れなかった」は同じ物差しで読むと成り立たない
  - 位置: :13・:28「`d_ewma_x` 0.487（0.476〜0.497）」・:29「区間の上限も 0.5 未満」・:30「`p_stuck` 0.524（0.510〜0.537）…下限が 0.5 を超える」
  - なぜ: 「離れた」を 0.5 との差（区間が 0.5 を含まない）で言うなら `d_ewma_x` の上がりも下向きに離れている。同等の基準なら水準 0.524 も幅の内側。2 つの物差しを取り替えている。水準は幅の内側の差しか示さず、力量の証拠にならない。
  - 解消: 2 文目を削るか、同じ物差しで「水準と上がりはどちらも幅の内側で、水準だけが 0.5 を上回り、上がりは 0.5 をわずかに下回った」。限界に「水準の分離は幅の内側の差で、幅の外の差を拾える証拠ではない」。自信 高
- [major] N2 抄録の主張が床と H3 を落とし「打鍵は停滞を予告しない」と読まれうる
  - 位置: :19「床と信号の名前の但し書きは 5.2 節と限界の節にだけ置く」・:32「床…停滞の 61%・対照の 65%」・:37「ロジスティック回帰 0.567（0.5497〜0.578）…点推定が幅の外」
  - なぜ: `d_p_stuck` はほとんど動けない信号なのに 2 本分の証拠に見える。H3 は陰性が推定器の性質か現象の不在かを分ける手がかりなのに 5.4 の 1 段落だけ（G6）。
  - 解消: 抄録に「打鍵の標準の量では幅の上側を否定できなかった」、主張の直後に「`p_stuck` の信号は床が多く、主張は主に `ewma_x` による」。自信 中
- [minor] N3 停滞の 47% が実行の待ちで対照（6%）と非対称に混ざる含意が無い（:34・:68）。G3。混入は AUC を 0.5 へ寄せる向きに働く。解消: 限界と 5.2 に 1 文ずつ（混入の無い停滞だけの値は求めていない・事前登録に無い）。自信 中
- [minor] N4 合成の離しが推定器のどの入力を一定にするかが無い（:38・:64）。解消: データの節に、合成の離しで一定になる入力の名前と係数の扱いを 1〜2 文（無ければ「該当なし」）。自信 中
- [minor] N5 位置の bullet に確認と探索が同じ行（:33「[確認・感度＋探索]」）。X8 は取り置きを見た後の探索（exploration/notes.md:22-26）。解消: 表 1 と 5.2 は事前登録の感度だけ、3 区分の値は 5.5・表 3（か S3・S7）へ、5.2 には参照だけ。自信 高
- [minor] N6 3 区分の比べで対が約半分（explore_position.json:98 "pairs": 394394・主は 709,352）に減ったことを報告していない。解消: S3 か S7 に対の数・実効の書き手・区間の幅を主と並べて 1 行。自信 高
- [nit] N7 並列の説の使い方（:82）。Roeser 2025（:373-377）"The only situation in which preparation of the next text unit affects an interkey interval is if for some reason it cannot be completed in its entirety in parallel ... there is an effect ... on the interval immediately preceding production of the next text unit."。解消:「並列の説では、並行で済まなかった計画は休止そのものに現れ、手前の打鍵には現れにくい（散文の言語の境界の主張で、コードの長い停滞への外挿）」。自信 中

## 5. 総合: minor
- H1 の数値・範囲・限界の 1 か所化・位置で揃えた比べは整い、引き継ぎ 8 件が解消・2 件が一部。
- N1 は物差しの取り違えで 1 文で閉じる。N2 も数文で閉じる。
- N3・N4 は新しい計算をせず書き方で境界を示せば足りる。

## 6. 読めなかった範囲・注入
全文を読んだ: brief・context-A・carryover-R1・outline・explore_position.json・exploration/notes.md。一部だけ: prereg-draft.en.md（grep）・prereg-draft.md（3 行）・prefreeze/notes.md（grep）・roeser2025.txt・guo2020.txt（範囲と grep）。読んでいない: confirm_holdout.json・conditions.md・explore_*.json の残り・seed_spread.json・文献の記録 2 つ・20261101 の notes 2 つ（[V440] などの要約が原典に忠実かは照合していない）。注入の疑いなし。
