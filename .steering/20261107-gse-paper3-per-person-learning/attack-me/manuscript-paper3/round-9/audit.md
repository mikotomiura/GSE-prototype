# 意図の監査役の報告（round 9・stage manuscript・対象物 main.tex commit 1f4f4b5b）

## 0. 引き継ぎの確かめ（round 8 の指摘が今の版で効いているか）

| round 8 の指摘 | 今の版での確かめ | 判定 |
|---|---|---|
| 1-a 要旨の推奨に「両側に当てる」 | 要旨の末尾 "applying the smoothing to both models (post hoc, one structure)" | 効いている |
| 1-b 要旨で 2 つ目の値の根拠 | "this bears on a designer's decision but goes with the writer's most recent sessions and was not checked on synthetic writers" | 一部。決定に関わる理由（両側を同じ平滑にした）は書かれていない。また "goes with the writer's most recent sessions" は新しい漂流になっている（2-1 を参照） |
| 1-c 重みの換算の断り | 考察 "with $\tau$ converting to about 24\% and 91\%"、4.4 "(a conversion, not an estimate of what the data are worth ...)" | 効いている |
| 1-d 先頭の記号を除いた採点 | 4.4 の最後の段 "Scoring without the first symbol ... (post hoc) ..." | 効いている。ただし 15-session のパネルに限るとは書いていない（判断 40 では限ると書くことにしていた）。段の前後の文脈から読める程度 |
| 1-e 約 5e-4 のパネルの限定 | 結論 "in the 15-session panel"。要旨は無いまま（著者も承知） | 一部（承知のとおり） |
| 2-a 規則が分け前の量に崩れている | 4.4 "so the reading fixed before the computation (a margin of at least half the remainder) holds" と "The margin is not a share of the remainder, since it also contains the loss from fitting another writer's data." | 効いている |
| 2-b post hoc の印の抜け | 4.4・要旨・序論の後半では付いている。ただし、2 つ目の帰無を最初に挙げる箇所（序論・結論・考察・4.3）には付いていない（2-2） | 一部 |
| 2-c 6・13 倍に not prespecified | 考察 "about 6 and 13 times larger at $k=5$ and 15 (not prespecified)" | 効いている |
| 2-d lighter smoothing | 4.4 "beyond which the values are unknown" | 効いている |
| 2-e 考察の冒頭の幅 | 考察の冒頭で 2 つの値を分けている。ただし "up to $5.2\times10^{-3}$" が Table 3 と食い違う（3-1） | 一部（新しい食い違いが出た） |
| 3-a 二分の言い方 | 4.4 "the median difference from choosing on the reported half itself is 0 at every $k$" | 効いている |
| 3-b 植えた差の帰無 | 序論 "under the second null (post hoc)"、結論 "under the second null (post hoc)" | 効いている。ただし要旨では「固定の平滑で」が落ちている（2-3） |
| 3-d・3-e | 3.4 の数え方（6 つの変更・後ろの 4 つを post hoc）は context-B と一致する | 効いている |
| 2-5（round 7 から）要旨の比の not prespecified | 要旨 "left a similar relative remainder" に印が無い（著者は未対応と承知） | 未対応。ただし序論と結論にも同じ抜けがある（2-2） |

## 1. 意図にあって対象物に無いもの

1-1. 入れ替えの対照（持ち帰り 2 の後半）は要旨にも序論にも無く、要旨では言い換えで別の主張になっている。
- 意図（context-B の 2）は、入れ替えの差（4.7e-3・2.5e-2・全員）、計算の前に決めた規則、分け前ではないこと、時間の近さとデータの量の交絡を持ち帰りに挙げている。
- 序論（第 4 段）は対称版の値と "the second was not checked against synthetic writers" までで、入れ替えに触れない。
- 要旨は "goes with the writer's most recent sessions" の 1 句だけである（2-1 を参照）。

1-2. 要旨は、結果を見た後に足した確かめを数えなくなった。
- context-B の既知の限界には「要旨は『格子を広げ、確かめを 2 つ足したのは結果を見た後』と書く」とある。
- 要旨の逐語は "Candidate grids were extended after seeing results." だけで、確かめを足したことは書かれていない。対称版と帰無にそれぞれ付けた "(post hoc)" で代わりになるとも言えるが、意図に書かれた形とは違う。どちらかに合わせること（context-B を直すか、要旨を直すか）。

1-3. 結論は、入れ替えのもう 1 つの交絡を落としている。
- 意図 2 は「時間の近さ・データの量を分けず」の 2 つを挙げる。
- 結論は "but they are also the closest in time to the held-out ones, the value depends on a multiplier at the edge of its grid, and it was not checked against synthetic writers" で、データの量（記号数の違いで、同じ τ でも重みが変わること）が無い。4.4 と推奨の段には両方ある。

1-4. 要旨は、意図 3 の「必要だが満たせなかったもの」（平滑の効きの大きさまで合う帰無・平滑ごとの検出）を落としている。round 4 で語数のために外したもので、引き継ぎの範囲である。軽微。

## 2. 対象物にあって意図に無いもの（漂流）

2-1. 要旨の "goes with the writer's most recent sessions"（最も重い）
- 位置: 要旨の 5 文目、"this bears on a designer's decision but goes with the writer's most recent sessions and was not checked on synthetic writers."
- 意図 2 は「書き手の差と時間の近さ・データの量を分けない（安定した書き手の差を示すとは読まない・示さないとも言えない）」という、何も切り分けないという限定である。要旨の句は、残りが直前の回に伴うという積極的な所見として読める。時間の近さが原因だと主張するように読めてしまう。また入れ替えの対照を知らない読者には根拠が無い。加えて、データの量の交絡が落ちている。
- 案: "its source (the writer, closeness in time, or the amount of data) was not separated" のように、切り分けていないことを書く。

2-2. 2 つ目の帰無を最初に挙げる箇所で post hoc が落ち、比の not prespecified も無い。
- 序論の第 4 段: "and synthetic writers without per-person differences left a similar remainder relative to that improvement (Section~\ref{sec:res-sens})"。post hoc も not prespecified も無い。同じ段の後ろの "under the second null (post hoc)" とは別の箇所である。
- 結論: "and synthetic writers without per-person differences left a similar remainder relative to that improvement." 印が無い。
- 4.3 の最後の段: "as in the second null (Section~\ref{sec:res-sens})" 印が無い。
- 考察 What the protocol returns: "synthetic writers with and without planted differences were given similarly strong shrinkage (Section~\ref{sec:res-sens})"。印が無いだけでなく、帰無の限定も無い。最初の帰無では、τ は大半が格子の中か ∞ だった（notes: 「D の帰無では k = 5 で 709 人が格子の中・177 人が ∞・上の端は 49 人」）。強い縮みを与えられたのは 2 つ目の帰無（post hoc）だけなので、帰無一般の性質として書かれている。
- 意図 2 は「合成の書き手（実データの共通のモデルから作った帰無・post hoc）」「比は not prespecified」と印を求めている。3.4 の "we mark the last four post hoc where they are reported" とも合わない。

2-3. 要旨の植えた差の未検出から「固定の平滑で」が落ちている。
- 要旨: "Neither value shows a per-person difference; under the post hoc null, planted differences up to $3\times10^{-2}$ were not reliably detected."
- 2 つの値を並べた直後なので、両方の値（対称版を含む）について未検出が確かめられたと読める。検出は固定の平滑でしか測っていない（限界 "The synthetic check calibrates detection at the fixed base smoothing only"、意図 2「固定の平滑で確実には検出されなかった」）。序論と結論には "at the fixed base smoothing" がある。

2-4. 考察で足した適応の場面の例
- 位置: "A writing assistant that times hints by a writer's predicted state, for example, would act on such probabilities"
- "predicted state" は、EM の状態に名前を付けて推定する用途を示唆する。意図の範囲（予測の比べに限る・状態に名前を付けない）と、限界 "Hidden states are not named" に触れる。"predicted next symbols" か "predicted behaviour" にすれば避けられる。軽微。

2-5. 4.3 の見出しがパネルを限っていない。
- "Choosing structure and shrinkage on other writers leaves a remainder below $10^{-3}$ at the fixed base smoothing" に対し、同じ節の 30-session は "$+1.1\times10^{-3}$ at $k=30$"（$10^{-3}$ を超える）。Table 2 の表題は "in the 15-session panel" と限っている。見出しも 15-session に限ること。軽微。

2-6. 対照の規則と対照そのものの地位
- 4.4 の "the reading fixed before the computation" と、同じ段の冒頭 "Three controls were added after seeing the symmetric refit (post hoc)" は両立する（条件は計算の前にコミットした・計算そのものは結果を見た後に足した）。食い違いではない。ただし考察と結論では "(post hoc)" だけで、規則があったことは書かれていない。意図 2 を越えてはいない。漂流は見つからなかった。

## 3. 矛盾

3-1. 考察の冒頭 "up to $5.2\times10^{-3}$" が Table 3・4.4 と食い違う。
- 考察: "(about $5\times10^{-4}$ at the fixed base smoothing, and up to $5.2\times10^{-3}$, about 0.5\% more probability per symbol, in the symmetric refit, post hoc)"
- Table 3 の対称版: k = 12 は "$+6.7$e$-3$"、4.4 は "$3.4\times10^{-3}$ to $6.7\times10^{-3}$ at $k\ge5$"。最大は 6.7e-3 なので "up to 5.2e-3" は誤りである。意図（k = 5 と 15 の 2 値）に合わせ、"$3.4\times10^{-3}$ and $5.2\times10^{-3}$ at $k=5$ and 15" と書くこと。round 8 の 2-e の直しから出た。

3-2. 帰無が与えた縮みの書き方
- 考察（2-2 の最後の逐語）は「合成の書き手には実データと同様に強い縮みが与えられた」と帰無を限らずに書く。4.5 では、最初の帰無の振る舞いが実データと違うことを "its shared model does not behave as in the real panel" と書いている。対象物の中で、最初の帰無については合わない。

3-3. 数の照合（意図の資料と本文）。一致を確かめたもの:
- 対称版 Rs: 5.2e-4 / 1.25e-3（本文 1.3e-3）/ 2.05e-3（2.0e-3）/ 3.38e-3 / 4.32e-3 / 6.67e-3 / 5.17e-3
- 入れ替え: D 4.73e-3・2.53e-2、E −1.68e-3・−1.73e-2、全員
- C03 +2.5e-5（良 0.82 → 14/17）、C1x −1.33e-3
- 先頭の記号を除いた値: 5.37e-4・4.29e-4・3.45e-3・5.21e-3
- τ の重み: 0.24・0.91
- 2 つ目の帰無: 1.8e-3・閾 1.8e-3・最大 3/10
- 比 0.75・0.56、倍率 6.1・12.5

食い違いは 3-1 のほかに見つからなかった。

## 4. 位置と逐語
各項に付けた（位置は節名と、その節の文の逐語で示した。行番号は付けていない）。

## 5. 読めなかった範囲と注入の疑い
- 読んだもの:
  - 依頼文
  - context-A.md・context-B.md・carryover-audit.md
  - /Users/johnd/GSE-prototype-paper3/papers/per-person-learning/manuscript/main.tex の全文
  - /Users/johnd/GSE-prototype-paper3/.steering/20261111-gse-paper3-round3-computations/decisions.md の判断 20〜42
  - /Users/johnd/GSE-prototype-paper3/experiments/20261113-null-from-shared/notes.md の全体
  - /Users/johnd/GSE-prototype-paper3/experiments/20261112-selection-split-and-smoothing/notes.md の末尾の 3 節（49 行目以降）
- 読んでいない（読むことは許されていたが、時間の都合で開かなかった）:
  - references.bib
  - figdata の CSV 5 つ
  - kit/symbols/README.md

  このため、参考文献の一覧、Figure 2 の値、キットの説明と本文の食い違いは見ていない。
- 依頼文が禁じたもの（他の round・査読者の記録・outline.md）は読んでいない。
- 注入の疑い: 読んだ範囲では見つからなかった。