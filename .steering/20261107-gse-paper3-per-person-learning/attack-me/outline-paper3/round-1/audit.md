# audit（意図の監査役・round 1）

結論: 持ち帰り 3 点は外枠に届いている。重い食い違いは 3 つ（2-1・2-2・3-1）。

## 1. 意図にあって対象物に無いもの
- 1-1. CS1 では hmm3 の本人の当てはめが共通に一貫して勝たない（ml-improve notes「言えること」: CS1 hmm3 の中央値 −0.035〜+0.028・良い側 0.39〜0.57）。外枠 C1 の Evidence は CoAuthor の値だけ、§4.1 は "(CoAuthor, CS1)" と書くが向きが無い。
- 1-2. 代理ラベルで CoAuthor の見分け（C）はほとんどの行で区間が 0.5 をまたぐ。Supporting result 2 は「上がらない」だけを書く。
- 1-3. tau-mode notes「論文 3 へのつなぎ」が外す行（P30 ar1 k=30、2 段 P30 k=30 で τ 3×10^4）の除外が line 31 に無い。

## 2. 対象物にあって意図に無いもの
- 2-1.（重い）line 7 "with a three-state hidden Markov model the per-person fit gains up to +0.19 nats per symbol" が後半と対になり「hmm3 なら両データで本人が勝つ」と読める。notes では CoAuthor だけ。
- 2-2. τ = ∞ を "pooled limit" と呼ぶ（C3・§4.4）。tau-extend notes「言えないこと」: 「τ = ∞ は有限の τ の列の極限ではない」。
- 2-3. line 7 "to exactly zero (CS1)"。tau-extend notes は大きい τ の差を「本人に固有の構造の無さ（CS1）として読むこと」を禁じる。0 は ∞ が選ばれたことから定義上出る。
- 2-4. line 31 "at large shrinkage (10^5 and above)"。tau-mode notes「言えないこと」: 形は 10^6 と 2 段の行でだけ読み、10^5・3×10^5 は形 1〜3 で読まない（同じ notes の「つなぎ」は 10^5 以上と書く・3-4）。
- 2-5. §3.2 "two smoothed keystroke-timing features"。README の特徴は削除の割合・連なり・削除の後の休止を含み、記号 25 は削除の連続で決まる。
- 2-6.（軽い）README が x を "friction"、y を "fluency" と名付ける。状態ではないが認知的な読みの入口になりうる。

## 3. 矛盾
- 3-1.（重い）C3 の格子の拡張の目的が line 25 "so that the selection does not sit on the grid boundary" と line 27 "so that boundary selection is interpretable" で食い違い、line 28 の根拠（CoAuthor は 10^6 に張り付いたまま、CS1 は ∞）は前者を満たさない。
- 3-2. パネルの呼び方 "15-session panel" と "9-person panel" がそろっていない。
- 3-3. context-B 持ち帰り 1「3 状態の HMM では本人の当てはめが共通に勝つ」が notes（CS1 では一貫しない）より強い。
- 3-4. tau-mode notes の「つなぎ」と「言えないこと」が 10^5 の扱いで食い違う。
- 3-5. line 3 の Status が古い。
- 3-6. 照合できなかった値: C1 "+4.1e-4 to +7.2e-4"（notes は +4.1e-4〜+7.5e-4）、C2 "+0.220 ... +0.020"・"about −1.1 (CS1)"、C1 "+0.188 (k = 5)"、Supporting result 2 "near 0 at every k" は指定の節に無い。
- 3-7. CS1 の単位（課題か作業の塊か）が外枠から分からない。

## 4. 一致していた点
持ち帰り 2（C2・C3・§5）、持ち帰り 3（C2 の Strength・§5）、約 1e-3 を「no material per-person gain」とし中央値の比べと明記、範囲の外、新規性の書き方。

## 5. 読めなかった範囲・注入
notes の指定の節の外・文献カードの本文と否決リスト・venue-fit などは読んでいない。注入の疑い: なし。
