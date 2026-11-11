# 意図の監査役（round 5・outline.md commit afc96bfa）

一番大きな問題（新 1）: 「残りは検出の下限より下」は、実データで返した量（+4.1e-4〜+7.2e-4）を合成で埋めた差の大きさ（1e-2・3e-2）と比べる、尺度の違う比べ。手順自身の検出の規則を実データの残りに当てると「拾える」側に入る。

## 0. 引き継ぎの判定
2-A 解消（1 文目の前半は 3-6）／2-E 解消／3-C 解消／N1 解消（4.4 "it does not show that per-person differences are absent (Section 6)"）／N2 解消（設計の変更で不要）／N3 解消／N4 解消／N5 解消／N6 解消／N7 解消（Main-table rows の節）／I1 一部（質的な文が限界と 5 節に残る・3-1）／I2 解消／I3 未解消（論文の外として保留）。

## 1. 意図にあって対象物に届いていないもの
- 1-1 記号化しだいが推奨の文に無い（context-B の持ち帰り 2・判断 7 の T3）。Take-home の 2 文目と 5 節の推奨に記号化の限定が無く、4.3 と限界「the size of what remains depends on the symbolization (4.3)」にだけある。
- 1-2 最頻値が −∞ を割り当てうる注意が推奨から消えた（判断 7・判断 10 で狭めたのは候補の方だけ）。5 節の推奨「compare with … its prior mode」に注意が無く、限界「The prior mode can give zero probability to a held-out symbol pair (one or two writers per cell in CoAuthor)」だけ。本人 − 最頻値に +∞ を生む（mode-in-selection notes「本人 − 最頻値の +∞ は 1〜2 人」）。
- 1-3（軽い）CS1 の感度の結論の形（sensitivity notes の「CS1 で共通そのものが選ばれたことは、この種の 1e-3 以上の個人差が無いことと合う」）が無い。弱い側に書いているので未着。

## 2. 対象物にあって意図に無いもの
- 2-1（重大）Take-home「what remains in the 15-session panel is below what the protocol can detect」・C1「below the smallest difference the protocol detected in synthetic writers of that record length」・4.3 の見出し「leaves a remainder below the protocol's detection limit」。1e-2・3e-2 は埋めた差 g、+4e-4 は返した量。g = 1e-2 で返る中央値は +1.9e-3（k = 15）、回収の比 0.10〜0.42。規則「median above the largest negative-control median and at least 80% of writers positive」を実データに当てると、中央値 +4e-4 は U = 8.4e-5（k = 15）・1.4e-5（k = 5）を超え、正は 16〜17/17。sensitivity notes の持ち込みは「手順はそれ未満の個人差を拾えない。実データの小さな残りは、それより小さい個人差が無いことを示さない」で、「残りが下限より下」とは言っていない。「未満」は回した段に限る。下限は k = 5 と 15 だけで測った。案: 「手順は 1e-2 未満（k = 15）の埋めた差を拾えなかったので、この大きさの残りは個人差の有無を示さない」。
- 2-2（重大）4.4「This shows that the shared model's smoothing, not the person's data, accounts for most of the remainder」は資料より強い（objective-and-pause notes「…と合う。これは中央値どうしの比べで、書き手ごとの分解ではない」・tau-mode notes「中央値の絶対値の大小と符号で読んだもの…配分した量ではない」・context-B「最頻値の分解は…根拠に使わない」）。限界「Comparisons of medians are not per-writer decompositions」とも食い違う。context-B の持ち帰り 1 も同じ強さ（3-2）。
- 2-3 C1 の見出し「the gain that a weak comparison shows disappears against a stronger one」は、判断 20・23 と外枠の 4.3・4.4 より強い（残りは 16〜17/17 で正）。
- 2-4 4.4「Placing the prior mode among the candidates changes little」は CoAuthor だけ。CS1 では候補に置くと 23 人全員が共通そのものから最頻値に替わり、本人 − 共通は 0 から +2.0e-4。
- 2-5 4.2「0.02 or less for ar3 and the chain」: unsmoothed notes は「r1 は 0.0287 以下（u の CoAuthor k = 5 の zy・遅れ 6）」。記号化と遅れの範囲がそろっていない。
- 2-6 限界「better prediction of the 26-symbol sequence is short-range sequential dependence」は肯定の断定。unsmoothed notes の言えないこと（正しいモデルとして読まない）より強い。否定の形に。
- 2-7 5 節の尺度の段落（「a likelihood ratio of about 4 to 13 over an hour」）: 計算は合うが、4.4 は残りの大部分を平滑の差とするので、本人を使う利得と読まれうる。最頻値が本人のデータ無しで同じだけを得ると同じ段落で。
- 2-8 データの声明「every reported value can be recomputed from the public data with the code listed」と Open items「until then the paper does not claim it」の調子がそろっていない。

## 3. 矛盾
- 3-1（I1 の残り）返る割合: sensitivity notes「本文と限界には書かない」と、context-B の持ち帰り 2・5 節「because it returns only a fraction of a planted gain」・限界「The protocol returns only part of a planted per-person difference」。どちらに寄せたかの記録が無い。
- 3-2 context-B の持ち帰り 1「残りの大部分は共通の平滑と最頻値の差である」が、同じ context-B の限界と notes に支えられない。
- 3-3 同じ量に 3 つの範囲: mode-in-selection notes +4.1e-4〜+7.2e-4・tau-mode notes +4.1e-4〜+7.5e-4・objective-and-pause notes「結果を見た後に気づいたこと」+4.8e-4〜+7.6e-4（取り違えの疑い）。
- 3-4 4.4「−3.5e-4 to −1.6e-4 … (3 to 6 of 17 positive)」の出どころが定まらない（mode-in-selection の値は良い側 0.12〜0.35 = 2〜6/17、objective-and-pause は 0.18〜0.35 で値は −3.5e-4〜−1.2e-4）。主の行（最頻値を候補に置かない）の本人 − 最頻値は読んでよい notes に無い。+∞ を positive に数えたかが無い。「the same in direction on pressed symbols」も notes に無い。
- 3-5 3.4「each with conditions committed before its code」: mode-in-selection notes は「実データの計算より前」（同じ commit を decomposition notes は「コードより前」）。小さい。
- 3-6 Take-home の 1 文目の前半「a per-person sequence model gains a lot over a shared model of the same weak structure」にデータの限定が無い（CS1 では勝たない）。context-B の持ち帰り 1 の前半も同じ。

## 4. 読めなかった範囲・逸脱・注入の疑い
summary.json と tables.md は読んでいない（3-4 と CS1 の +0.050〜+0.029 は確かめていない）。per-person-sensitivity notes の「結果の後の確かめ」の節（61〜65 行）を指定の外として読んだ（根拠に使っていない）。注入の疑い: なし。
