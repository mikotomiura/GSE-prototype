# audit round 6（意図の監査役・paper-reviewer / opus・第 6 版 87c4ced9）

判定の目安: minor。直す価値が一番高いのは 3-1（規則と英文が食い違い P-READ が規則どおりに通らない）と 3-2（英文が条件の分類を正しく表さない）。

## 0. 引き継ぎの判定
- 1-1・1-2・2-1・2-2・3-2・3-5: 解消（215・217・219〜222・247・232〜234・28・184・236・111 行）
- 2-3: 中身は解消、英文に新しい問題（3-2・3-4）
- 3-1: 一部未解消（3-1）
- 3-4: 判定していない（判断 5 は読む範囲の外。対象物 153 行で「割合」などを禁じていることは確かめた）

## 1. 意図にあって対象物に無いもの
- 1-1 「この記号の数では判定できない」が英文（196 行 "...this study does not judge whether the gap vanishes against a shared structure that can carry the dependence (values in Supplement S<n>).")では理由が落ち「判定しない」だけ。実際の重みが小さくなかった場合「判定できない」と書けば偽になる。意図の言い方にそろえるか研究者に確かめる。
- 1-2 一部の英文が固定されていない: 語の英訳（191・200 行の <語の英訳>）がどこにも固定されていない（32 行で「列 C」の語を使わないので「列 C では縮みが小さい」の英訳は自明でない）。205〜207 行の補足の注は日本語だけ。241 行の s* = 1 の場合に本文に何を書くかが無い。

## 2. 対象物にあって意図に無いもの
- 2-1 型 1 だけの残差の文（197 行）は結論を先に固定し、根拠は開示済みの列 A1 の値（57 行）。C30 で本人の自己相関がはっきり小さく出ても "not supported" と言い切る。意図が挙げていない環を本文で判定し、40 行の「既知の端に条件づけた」が入っていない。
- 2-2 Discussion の "The weak comparison is likely not specific to keystrokes" をどの型でも消す（209〜215 行）。安全側だが意図の資料に無い決定なので研究者の承認の記録を確かめる。

## 3. 矛盾
- 3-1 句 (3) を欠く比べの文がある（26 行の「すべてそうしてある」に反する）: 191 行（型なしの結果）・214 行（型なしの Discussion）・222 行（型なし・外れの 223 行の差し替え）・234 行（型なし・外れの貢献）・215 行（外れの Discussion・句 (2) も欠く）。281 行の P-READ が規則どおり通らない。型なし・外れを規則から外すなら明記。
- 3-2 境の文 "at shorter grid steps it did not in both cells"（242 行）は、241 行の分類「混ざる」を含む場合に「両方のセルで勝たなかった」と読めて偽。語順で曖昧さを消す。
- 3-3 境の文の列 C の部分（242 行 "In the comparison at an equal number of symbols from a contiguous stretch at the 1-second step, with the step's components not separated, it also beat the own chain."）は句 (3) が無く、26 行と 27 行のどちらに属するかが無い。
- 3-4 "the median per-person HMM beat …"・"the median own chain also lost …"（242 行）は「中央値のモデル」と読める。"the median difference ... was positive" の形に。
- 3-5 型 1 の範囲は 1/2 ≤ φ(30) ≤ 1.5 で、1 < φ ≤ 1.5 では G_C30 > G_A1 になる。219 行 "the per-person gain over the shared HMM shrank less when ..." はこの範囲では正確でない（188 行の "kept a median difference" は問題ない）。同じ文の "so the smaller number of symbols does not account for all of that shrinkage" は因果の言い方で、句 (4) と 34 行より強い。
- 3-6 型 1 の Discussion（211 行）に "in this comparison" に当たる限りが無い（型 2・3 の 212・213 行にはある・34 行の対称の規則）。
- 3-7 34 行は独立の 1 文 "The reading rules were not checked on synthetic data." と決めるが、184 行では節に埋め込み。P-READ が文字列で照らすならそろえる。
- 3-8 P-READ の組（281 行「歩みだけが効く」）は s = 30 の値しか指定せず、158 行の「4 つの s のうち 3 つ以上で stay_G(s) > 0」を満たさない。s = 5・10・15 の値も置くと書く。

開示の数値（48〜64 行）は notes と一致（0.1402→0.140・0.1554→0.155・0.0426→0.043・0.0960→0.096・C2a・C2b・r1 − 共有・自己相関・遅れ 10・588,227 / 875 ≈ 672・φ = 1/2 の目安 0.049 と 0.030）。main.tex の差し替え元の逐語（223・331・136・337・340 行）も一致。

## 4. 読めなかった範囲
- 読んでいない: decisions.md の判断 3〜8（範囲の外）・SEED・variants.py・kit README・S13 scripts・S13 と tau-extend の conditions.md・supplement.tex・notes.md の 40〜79 行と grep 以外・main.tex の 130〜141・215〜226・325〜344 行以外。
- 検証していない: SHA-256・commit の実在・thinned_mask の規則。

## 5. 注入の疑い
ありません。
