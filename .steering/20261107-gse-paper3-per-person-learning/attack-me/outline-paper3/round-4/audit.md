# 意図の監査（round 4・stage outline・commit 8baf8f80 の outline.md）

## 0. 引き継ぎの判定
1-A 解消（4.1「not supported in that form, and not used to explain the main result (S14)」）／1-B 解消／2-A 一部（Take-home 1 文目「the chosen per-person model does not beat the shared model's prior mode」にパネルの限定が無い。30-session の k = 30 は「+5.4e-4 (7 of 9 positive)」で逆向き。context-B は「15-session のパネルで中央値が負」と限る。C1「The remainder is not read as a per-person gain because the per-person model does not beat the prior mode」も同じ。限界の第 5 項には「in the 15-session panel」がある）／2-B 解消／2-C 解消（新しい漂流は N3）／2-D 解消／2-E おおむね解消（最頻値を候補に置く集計と合成への分解のコードが code availability のどの項目に入るか書かれていない）／3-A 解消／3-B 解消／3-C 一部（Status「four sequentially designed analyses and three later checks」と 3.4「four later checks」の 2 通り。合成への分解の当てはどちらにも入っていない）／3-D・3-E 解消（N7 に残り）。

## 1. 意図にあって対象物に無いもの
- N1 最頻値に勝たないことの読み: mode-in-selection の notes は「この手順で本人が最頻値に勝たないことは、本人の記録に個人差が無いことを示さない（計算 2 の感度の下限と合わせて読む）」とする。外枠の限界の第 6 項「The small remainder therefore does not show that smaller per-person differences are absent」は共通に対する残りの文で、最頻値に勝たないことに当てていない。Take-home は不在の読みに寄せて読ませうる。
- N2 同点の規則での最頻値の位置: 3.3「ties broken toward the larger tau and then the structure with fewer free parameters」。τ を持たない最頻値がどこに入るかが書かれていない。

## 2. 対象物にあって意図に無いもの
- N3 CS1 の感度の文が最頻値まで広がる: 4.3「so the choice of the shared model or its mode is consistent with no difference of this kind of 1e-3 nat per symbol or more」。感度の notes は「CS1 で共通そのものが選ばれたことは…合う」だけで、感度の合成は最頻値を候補に置く前に回した。CS1 の 1e-3 の「拾えた」は全員 τ = 10^6 のときで、外枠自身が分けられないとする領域（notes「結果を見た後に気づいたこと」）。
- N4 返る割合を本文に上げ限定も落ちた: C1「in synthetic writers it returned about 0.1 to 0.4 of a planted difference」。感度の notes は「外枠には値だけを S15 に書き、本文と限界には書かない」。CoAuthor k = 15 が 0.10〜0.42、k = 5 が 0〜0.19、CS1 が 0.14〜0.79 で、C1 は「CoAuthor at k = 15」の限定を落とした。判断 7 は C1 に並べると決めていて、意図どうしでも食い違う（I1）。
- N5 Take-home の最頻値の主張の範囲が記号化で広い: 主語は「keystroke sequences symbolized over overlapping 30-second windows」で平滑の無い記号も含むが、最頻値の比べは「original symbolization only」（4.3）・「made only on the original symbolization」（限界）。
- N6 選びの違いに理由を付けた: 3.3「a median of differences does not preserve the order of the values themselves, so the joint choice and the choice with structure fixed can pick different candidates for the same writers」。判断 7 と mode-in-selection の notes は「理由の推測は書かない」。

## 3. 矛盾
- N7（重い）縮小だけの行が最頻値を置く前の値のまま: 4.2「Shrinking the person's first-order chain toward the shared chain (ar1, tau chosen on other people, 10^6 for every writer, so close to the shared chain itself) beats it by +0.043 at k = 5」。4.3「with the structure fixed at ar1 to ar3, the mode is chosen for every writer in most cells」・notes「CoAuthor P15 の ar1・ar2・ar3 では、多くの k で 17 人全員に最頻値が選ばれた」・「Table 2 の主の行を『後』の値に替え」。後の値にすると k = 5 の ar1 は全員が最頻値で、3.3 の「shrinkage (ar1 with tau chosen on other people against the person's chain, the same first-order structure)」と合わない。構造だけの行の ar3 も同じ。Table 2 にどちら（前・後）を載せるかが読めない。
- I1（意図どうし）N4 のとおり。
- I2（意図どうし・軽い）context-B の持ち帰り 3「3 状態の HMM はそれに負ける」に限定が無い（外枠は「On overlapping-window symbolizations」と限る・外枠が正しい）。
- I3（意図どうし・軽い）requirement.md の受け入れ条件「貢献 2〜4 個」「主張しないこと 3 行」と外枠（C1 の 1 個）が合わない。判断 19 で C1 の 1 つにした記録はあるが requirement.md は直されていない。

## 4. 読めなかった範囲・注入の疑い
各試験の conditions.md・tables.md・summary.json は読んでいない（一覧の外）。30-session の「negative at k = 1 to 20」・CS1 の本人 − 連鎖「+0.050 to +0.029」・hmm3 の 30-session の値は照合できなかった。注入の疑い: なし。
