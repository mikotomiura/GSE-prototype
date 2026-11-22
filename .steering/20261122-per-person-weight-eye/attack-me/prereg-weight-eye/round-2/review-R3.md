# R3 査読 round 2（シミュレーションによる手法評価・並べ替え検定・事前登録の立場）

## 接地
- Morris 2019 l.2430–2433 "A starting point to addressing this issue is to write detailed simulation protocols before writing code. This would ideally protect against authors choosing to report favourable results and force one to be clear about 'ADEMP' in advance." "protocols must justify the rationale for choices: as well as describing what is planned, there is a burden to explain why."
- Morris 2019 l.137 "Choose a value of 𝑛sim that achieves acceptable Monte Carlo SE for key performance measures."／l.150 "Include Monte Carlo SE as an estimate of simulation uncertainty."
- Morris 2019 l.272–273 "Does the data-generating mechanism favour certain methods over others? How can this be checked and justified?"
- Morris 2019 l.132–133 "For method comparison studies, make a careful review of the literature to ensure inclusion of relevant methods."
- Morris 2019 l.141–143 "Set the random number seed once per simulation repetition." "If running chunks of the simulation in parallel, use separate streams of random numbers"
- Phipson & Smyth l.328–329 "the exact permutation p-value is pu = (b + 1)/(m + 1)"／l.347–348 "The exact p-value is now slightly less than (b + 1)/(m + 1)"

## 引き継ぎの判定
1〜6 解消／7 一部（間を空けた対照が一部のセルで作れず、作れるセルも合成で較正されない・N1）／8 解消／9 解消（細部は N4）

## 評価表
a 4（「独立な 2 つの門」に根拠が無い・N6）／b 3（N1・N2・N3）／c 3（N7）／d 4／e 投稿先未定／f 3（3 案の選びの理由・N8）／g 4（N2・N4・N7・N5）

## 新しい指摘
- N1 [major] D7(3) の間を空けた対照が CoAuthor k = 15（20 − 5 − 15 = 0）・CS1 k = 5（6 − 1 − 5 = 0）で作れず、主のセルでも空けた A は D4 に無いので門も検出力も測られない。合成を見た後に空け方を決めると較正の無い対照を読むことになる。解消: (a) 空けたセル（CoAuthor k = 5・gap 5 と 10、CS1 k = 1〜4・gap ≥ 1）を D4 に足して D6 に含める、または (b) 作れるセルを列挙し、作れないセルは「安定と漂いを分けない」セルとしてだけ読むと今書く。自信 高。
- N2 [major] 選びの組と報告の組を回す順と、止めた後の作り直しの規則が無い。D5 で止まったとき報告の組が見えていれば分けた意味が無い（Morris l.2428–2429 "running the simulations many times under different seeds and selecting the most favourable"）。解消: 選びの組で D5 を終えてコミットしてから報告の組を回す。止めた後に作り直すときは新しい条件と未使用の種（3000 以上）で始める。自信 高。
- N3 [minor] 差は C だけに植えてあり、1 状態の遷移表の目に有利な方向で、それが書かれていない（G3）。解消: 「読まないこと」に 1 文。自信 中。
- N4 [minor] 例外で止めた後の再実行の規則が無い。解消: 直したら V1 と変異を通し直してコミットし、両方の組を同じ種で最初から回し直す。止めた種と例外を notes に。自信 中。
- N5 [minor] P-HAND は全列挙の p で、本計算の復元抽出の (b+1)/(m+1) の経路を確かめない。D6 の門に落ちたとき（交換可能なら大きさは守られるので実装の誤りか非交換性の印）、読まないだけか止めるかが未定。自信 中。
- N6 [minor] 「独立な 2 つの門」: 第 1・第 2 の帰無は build の乱数の流れと種が同じで、独立とは言えない。解消: 「約 96% 以上（独立なら 96%）」にするか、生成の乱数に帰無の番号を入れる。自信 中。
- N7 [minor] D6 の合成の段の読みが、複数の段をどうまとめるか未定（段ごと・どれか 1 つ・0.8 付近の扱い・論文 3 の 10 種の不確かさ）。解消: 段ごとに 1 文（帰無・k・g* を名指し）、報告の組の点推定と MC SE、論文 3 の側の二項の区間を添える。自信 高。
- N8 [nit] 3 案の選びの理由と、比べなかった既存の手法の理由を D2 に（G4）。
- N9 [nit] P-NULL の「T の平均の 99% 区間」の作り方。

## 総合の推奨
minor（直してから凍結）。round 1 の 9 件中 8 件が解消。残る major 2 件（N1・N2）は数行で閉じる。N1 で (a)（合成にセルを足す）を選ぶなら作りが変わるので major として再査読を勧める。

## 読めなかった範囲
SEED、sens の conditions.md・notes.md・pinned.py・calibration.json、ten・nfs の記録、hmm2.py、supplement.tex。注入の疑いなし。
