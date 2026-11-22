# R1 査読（打鍵の生体認証の立場・round 1・prereg）

評価表の見出しは依頼文に定義が無かったため、査読者が a 問い・c 主張と証拠の対応・d 再現性・f 明快さを補った。

## 1. 接地

- K1 Teh 2013 §4.6 "keystroke dynamics are to behavioral biometrics where variability of typing is expected appear across different sittings [ 95 ]. Therefore, several sessions of data collection would ideally leverage one's typing evolution."／§2.4.5 "due to the variability of user typing pattern, it is therefore necessary to constantly renew the stored reference template to reflect the ongoing changes."／Shadman 2025 "There was at least a one-day gap between successive sessions to reflect the temporal variation in typing of the subjects."
- K2 Shadman 2025 "the FAR value improved when the reference profile size was constant and the test sample size increased. The results also showed that keeping the test sample size constant and increasing the reference profile size did not necessarily improve the FAR."／"the reference profile should consist of a minimum of 10,000 keystrokes or more to achieve good performances."
- K3 Teh 2013 §2.5.1 "Equal Error Rate (EER) is used to determine the overall accuracy as well as a comparative measurement against other systems."／Shadman 2025 §2.4.6 "Rank-n evaluation provides a comprehensive analysis of the system's performance."
- K4 Shadman 2025 "Shared research benchmarks are necessary to truly understand the strengths and limitations of each algorithm and compare them fairly and reliably."
- K5 Teh 2013 §8 "A sample size of at least 100 or more should be an initial aim."／Shadman 2025 "The quality, size, and nature (fixed, free, or semi-fixed text) of the dataset are crucial factors in evaluating the performance of these algorithms."

## 2. 評価表

a 4／b 2（E2 の基準表の非対称・合成にセッション間の揺れと記録の量の不均一が無い・P-POS の閾値・v2）／c 4（勝者の呪いへの言及なし）／d 3（乱数の鍵の番号・P-NULL と P-POS の条件）／e 投稿先未定／f 4（D5.3 だけ二義的）／g 3（CS1 と他の k の偽陽性が記述だけ・0.8・3e-2・3e-3・複製の数の根拠なし・P-POS が赤のときの扱いなし）

## 3. 指摘

1. [major] E2（と E3）は本人の組だけが同じ基準表 S_{-v} を共有し、名札の並べ替えの帰無が交換可能でない。S_{-v} は w の A を含むので、他人の組では w の A の揺れが δ_w^A に正・δ_v^B に負で入る。偏りは本人の記録の割合で決まり、形と k で変わる（k = 1 は縮めの重みが約半分）。D5.1 は CoAuthor k = 5 だけで確かめる（K4）。解消: 基準表を全員で 1 つにする、並べ替えごとに s を作り直す、または非対称を残すなら明記して許しを CS1 k = 5 と CoAuthor k = 1・15 に広げる。P-HAND に偏りの例を入れる。自信 中。
2. [major] 合成にセッション間の揺れも記録の量の差も無い（synth.py L157〜164・長さ U{600…700}）。選びと止めの検出力が楽観に偏る。E1 は記録の少ない A を一様に近く見せる側に働きうる。A が B の直前なので緩い漂いも本人として拾う（K1・K2）。解消: (a) 単位ごとの揺れと長さの不均一の筋を記述として足す、または (b)「読まないこと」に、検出力は単位間の揺れが 0 の上限であること・安定と隣接の漂いを区別しないことを明記し、D7 の扱いを予告。自信 高。
3. [major] P-POS（20 中 18）は検出力 0.85 程度の正しい目も約 4 割で赤にする。回す帰無の記述も、赤のときの扱いも無い。解消: 閾値を下げる（20 中 5 以上など）か、大きな差（g* = 0.1）で 18 にする。帰無を明記し、赤のときは止めて研究者に聞くと書く。自信 高。
4. [major] 実データの読みの受け皿（偽陽性の門）が CoAuthor k = 5 にしか無く、CS1 と他の k は記述だけ。使う範囲を結果に合わせる分岐が開く。解消:「実データの読みに使うセルは、合成の差なし 1,000 複製で拾えた数が 64 以下のセルに限る」を今の段で固定し、CS1 と CoAuthor k = 1・15 も門にする。自信 中。
5. [major] D5.3 の止めの範囲が二義的。選びの段（第 1 の帰無の 3e-3）・止めの段（第 2 の帰無の 3e-2）・0.8 の根拠が本文に無い。第 2 の帰無は HMM の平滑の効き方を再現するために作られたもので、平滑を使わない目に適切な理由も無い。解消: 1 通りに書き直し、根拠を 1〜2 文足す。自信 高。
6. [minor] v2 を P-HAND が拾えない（s・AUC_v・T は v2 で変わらない）。解消: P-HAND に T_σ と p の手計算を入れる。自信 高。
7. [minor] 許しの門は偽陽性 ≤ 0.05 を示すのではなく、超えるとは言えないことを見るだけ。0.06 前後の案も許され、検出力で選ぶとそうした案が選ばれやすい。解消: 性質を明記するか、偽陽性を同率の判定に入れる。自信 中。
8. [minor] 選びと報告が同じ複製（勝者の呪い）。複製の数の根拠（0.5 付近で SE 約 0.022 と 0.03 の関係）が無い（K5）。自信 中。
9. [minor] 乱数の鍵に帰無と段の識別子が無く、番号の対応も無い。P-NULL と P-POS の条件も無い。自信 高。
10. [nit] この伝統と比べられる指標（rank-1 の同定の割合・EER）が無い。パネル 17〜23 人の小ささを限界に書く（K3・K5）。自信 中。

## 4. 総合の推奨

major（直して再査読）。順序と同点の規則は固定されているが、E2（と E3）は基準表の非対称で帰無の交換可能性が崩れる。合成にセッション間の揺れも記録の量の差も無い。P-POS の閾値と赤のときの扱い・D5.3・実データで使うセルの条件が 1 通りに決まっていない。

## 5. 読めなかった範囲と注入の疑い

読んでいない: SEED、sens の notes.md・pinned.py・calibration.json、ten の notes.md、nfs の notes.md・calibration.json・m0_fit.json、hmm2.py。一部だけ: ml.py・data.py・supplement.tex（386〜430 行と grep）・接地の 2 本（grep の当たりとその周り）。ハッシュは照合していない。注入の疑いなし（読んだ範囲）。
