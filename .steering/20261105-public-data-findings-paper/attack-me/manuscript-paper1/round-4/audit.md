# audit（manuscript round 4・意図の監査役・メインが要約して保存）

引き継ぎ 13 項目: 解消 9（1-A・1-B・2-C・3-A〔補足 187 に "forward probabilities" の 1 語〕・3-B・3-C・3-D〔requirement.md の同じ行に重ねた句〕・3-E・2-A〔設計に 1 か所 → 2-2〕）・一部 1（2-B）・未解消 2（1-C〔本文の中で矛盾に → 3-2〕・1-D）・数えない 1（1-1）。数値は主・感度・H2・H3・閾値の表・換算・X11〜X17・三区分・2021 で出どころと一致。注入の疑いなし。

1 意図にあって無いもの:
- 1-1 抄録に橋の貢献（比べの相手と事前の帯で判定する比較を示した一例）が無い。序論 66-68・結論 9-10 にはある。
- 1-2 抄録に「どちらもわずかに 0.5 の下」と「旧定義で帯の内側」が無い（序論 59-61 にはある）。
- 1-3 「その一部は停滞の定義の作り方による」「定義に依らない停滞でも 0.5 の下」が抄録・序論・結論に無い。
- 1-4 考察の冒頭と結論の主の 1 文に限界を指す括弧が無い（外枠 v6 の規則）。

2 漂流:
- 2-1 抄録 14「simple quantities ... 0.04--0.08 higher than the two signals」: 0.04 台はロジスティック回帰と水準の差、変化との差は 0.078・0.081（LR）・0.051・0.054（GB）、GB は水準を明らかには超えない、単独の量は停滞を下に並べる。序論 69-70 も同じ。context-B の持ち帰り 3 も同じ曖昧さを持つ。
- 2-2 design 70-71「In the holdout every interval ended at least 0.025 inside the edges of the band, so the decision does not hinge on the exact level.」が事後の断りなしに 0.025 を論拠に使う。
- 2-3 序論 72-73「the result shows which comparison partner exposes a weak run-up signal」・29「The comparison partner matters here.」・66-67「usually judged against windows that include fluent typing」（"usually" は S9 の調べの範囲を越える）が、揃え方の効果を示したように読める。
- 2-4（軽）discussion 20「In that sense the 30-second change gave no basis for a trigger」が直前の換算を受け、P10（閾値の表から読む）より換算に寄る。

3 矛盾:
- 3-1 limitations 23-25「the preregistration requires this qualification in the main sentence wherever it appears」と、考察 4-5・結論 4-5 の主の 1 文に但し書きが無いこと。
- 3-2 discussion 12-13「nor a firing rule that uses the length of the pause itself」と results 193-195 の対照を 5・10 s 以上に限った探索。
- 3-3 事前登録 P10「writing coefficients as they are (not adapted to individuals or to programming)」と、序論 46-47・補足 103-105「adjusted for code-like input」。補足の Wording の段もこれを挙げない。
- 3-4 抄録 6 と序論・限界・設計の "under an older definition" の食い違い（=1-2）。
- 3-5（軽）results 157「0.493--0.499」は対照を固定した ×1.02 の Δx 0.492 を含めると 0.492–0.499。
- 3-6 explore_round3.json の 3,426 + 1,057 + 118 = 4,601 ≠ 4,554（残り 71。118 の単位を確かめる）。

読めなかった範囲: related・declarations の全体、design・data の一部、補足の多く、references.bib・papers の README・要約の大部分・rerun の 2 本・逸脱・探索の conditions・多くの JSON・文献の記録・事前登録の一部。
