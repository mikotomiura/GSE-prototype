# 意図の監査 round 7（外枠 commit 12e46857）

引き継ぎ 13 件のうち 11 件解消・一部 2 件（3-D・1-A と 3-A〜3-C）。新しい穴で一番重いのは 5 節の換算の段落で、埋めた差と返った量を同じ物差しで並べる（判断 11 で避けると決めた比べ方）。

## 0. 引き継ぎの判定
2-A・2-B 解消（Take-home "what remains in the 15-session panel is about as large as what a less-smoothed version of the shared model gains … and the protocol cannot attribute it to the person"・4.4 "we do not read a direction from either"）／3-D・1-A 一部（Take-home が持ち帰り 2 の検出の下限の報告を落とす・1-a。shrinkage を共通に付ける言い回し・3-a）／2-C 解消／2-D 解消（ただし照らせない: 4.4 "(3 to 6 of 17 positive; 1 to 4 of the 15 with finite values)" は内部で整合。notes の値は候補に入れた行）／1-B 解消／2-E 解消／2-F 解消／2-G 解消／3-A〜3-C 一部（context-B の「どのパネルでも検出できた差より小さく」は k = 30 で裏づけが無い・3-b）／3-E 解消（Status との食い違い・3-d）／3-F 解消。

## 1. 意図にあって対象物に無いもの
- 1-a（中）Take-home が「記録の長さでの検出の下限を合成で報告する」を落とす（推奨は "…and report how much the result depends on the shared model's smoothing and on the symbolization." で終わる・5 節にだけある）。要旨と結論に届かない。
- 1-b（中）30-session の本人 − 共通（+1.1e-3）が C1 にも 4.3 にも無いのに、4.4 は同じパネルの本人 − 最頻値（"+5.4e-4 at k = 30 … (7 of 9; 5 of 7 finite)"）を出す。片側だけの報告。
- 1-c（低）CS1 の合成の持ち込みの文（「CS1 で共通そのものが選ばれたことは、この種の 1e-3 以上の個人差が無いことと合う」）が無い。意図的なら判断の記録に。同じ notes の「拾えた 1e-3 は全員 τ = 10^6 で分けられない領域」と緊張（3-c）。持ち帰り 1 の「CS1 は境界の事例」は Take-home に無い。

## 2. 対象物にあって意図に無いもの
- 2-a（高）5 節 "the smallest planted differences detected correspond to 36 nats at k = 15 and 108 at k = 5; the remainder corresponds to about 1.5 to 2.6 and is not shown to be per-person"。判断 11「埋めた差と返った量を同じ物差しで比べない」。返る割合は 0.10〜0.42（k = 15）・0〜0.19（k = 5）。返った量（例 k = 15 の 1e-2 で +1.9e-3・約 6.8 nat）で書くか、埋めた差の行を外す。
- 2-b（中）C1 "With the structure fixed at ar3 on both sides, per-person minus shared is already +5.5e-4 and +7.6e-4 at k = 5 and 15, so most of the shrinkage comes from the comparison model's structure." 構造を替えたのは両側で、相手の側だけに帰すのは解釈（4.1 "not used to explain the main result"・構造の試験の notes）。言えるのは「両側の構造を ar3 にすると縮む」まで。context-B の持ち帰り 1 も同じ語。
- 2-c（中）5 節の「本研究で評価したもの」に最頻値の診断（"report how much the shared model's smoothing matters, for example with its prior mode, and the writers to whom that mode gives zero probability"）。基の平滑は固定し、最頻値が平滑の効きを測るかは確かめていない（合成の b は全セルで負・実データは +7.4e-4）。当てたことと評価したことを分ける。
- 2-d（低）C1 "is chosen in every cell with tau = 10^6 (3 x 10^5 for 16 of 17 writers at k = 15)" の範囲（CS1 は τ = ∞、30-session の k = 30 は 3×10^4）。15-session に限ると明記。
- 2-e（低）4.3 "(unsmoothed symbols: also below 1e-3; …)" の "also" が指す先が無い。値（+5.8e-4・+8.0e-4）で。

## 3. 矛盾
- 3-a（中）Take-home "a shared model whose structure and shrinkage are chosen on other people"（context-B も）。τ は本人の当てはめの母数で、共通は "a weak base prior (… the strength of this smoothing was fixed, not chosen on other people)"。C1 Protocol は正しい。
- 3-b（中）context-B の「本人 − 最頻値の向きは、どのパネルでも手順が検出できた差より小さく、読まない」: 下限は CoAuthor の k = 5・15 と CS1 の k = 5 だけで、30-session の k = 30 には無い。6 節の下限も k = 30 を覆わない。
- 3-c（低）感度の notes の中の緊張（1-c）。
- 3-d（nit）Status "each later check with its conditions committed before its code (3.4)" と 3.4 "each with conditions committed before its code or, for the reanalysis of stored values, before its computation"。
- 3-e（nit）休止の秒の割合の表記（notes は 0.046・約 4%、外枠は about 0.05・about 5%）。

## 4. 読んだ範囲・注入の疑い
context-A・B・carryover・outline.md・README・requirement.md・判断 10〜24 と 1〜12・notes の指定の節と 20261111 の notes 3 本。summary.json・tables.md・他の記録は読んでいない。注入の疑い: なし。
