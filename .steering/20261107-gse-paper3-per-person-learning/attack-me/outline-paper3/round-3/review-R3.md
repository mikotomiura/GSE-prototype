# round 3 の査読（UMUAI・方法論と再現性を見る立場・stage outline）

対象: /Users/johnd/GSE-prototype-paper3/papers/per-person-learning/manuscript/outline.md（commit ede70d54）。補足: /Users/johnd/GSE-prototype-paper3/papers/per-person-learning/kit/symbols/README.md

## 1. 接地
- 基準 1（Varma & Simon 2006・varma.txt 3 行）: "Proper use of CV for estimating true error of a classifier developed using a well defined algorithm requires that all steps of the algorithm, including classifier parameter tuning, be repeated in each CV loop."
- 基準 2（同）: "The CV error estimate for the classifier with the optimal parameters was found to be a substantially biased estimate of the true error that the classifier would incur on independent data."
- 基準 3（同）: "Even though there is no real difference between the two classes for the "null" datasets, the CV error estimate ... was less than 30% on 18.5% of simulated training data-sets."
- 基準 4（同）: "Since selection of classifier parameters that minimize CV error estimates is a kind of training, it should be included as part of the classifier training algorithm."
- 基準 5（Liu & Meng 2016・liumeng.txt 1726–1732 行）: "we predict each individual's response using the remaining n − 1 individuals ... our inference will be more robust. The downside is that we base our accuracy assessment on observed prediction errors for individuals who do not necessarily match the target's background ~x0 —our inference will be less relevant."
- 基準 6（同・19–20 行）: "how to make the right relevance robustness trade-off: if we exercise too much judgement in determining which controls are relevant, our inferences will not be robust."

## 2. 引き継ぎの判定
N1 解消／N2 解消／N3 解消／N4 解消（"disappear" 0 件・"consistent in sign" 0 件・ただし C を参照）／N5 解消／N6 解消（3.2 の 5 特徴と 2 合成値が README 21–25 行と一致）／N7 一部（README 78 行 "That comparison used the raw datasets and is not part of this kit"・検証の経路が無い・研究者が未対応として残した）／N8 解消

## 3. 評価表
a 3（合成の検出規則を実データに当てると「検出」・要点は「読まない」・関係が書かれていない）／b 3（構造の格子が上端で止まる・CS1 の感度は seed 1 本）／c 3（「at most about 1e-3」は構造の格子の端に依存）／d 3（4.3 の過密）／e 4（「every reported value can be recomputed」が公開コードの範囲と合わない・プレプリントは未照合）／f 3（打鍵のユーザーモデリング・cold-start が未検索）

## 4. 指摘
- [major] A. 自分の検出規則を実データに当てると残りは「検出」になる。それでも「読まない」とする理由が外枠に無い
  - 位置と引用: 49 行 "the detection rule (every seed's median above the largest negative-control median and at least 80% of writers positive)"、"negative control (... largest seed median 1.4e-5 and 8.4e-5 at k = 5 and 15 in CoAuthor, below the CoAuthor remainder ...)"、"the share of the planted gain returned (about 0.1 to 0.4 in CoAuthor at k = 15 ...)"／13 行 "+4.1e-4 to +7.2e-4 for k = 1 to 15 (positive for 16 or 17 of 17 writers). This remainder is not read as a per-person gain"
  - なぜ: 実データは陰性対照の最大の 5 倍以上・94% 以上が正で、規則の 2 条件を満たす。割り戻すと 1e-3〜7e-3 の世界と両立。外の構造を真にしても "below the real remainder"。読まない根拠は S9 の中央値どうしの比べだけで、その分解が合成で個人差を埋めたとき正の寄与を返すかは示されていない。陰性対照で陽性に出た量を別の基準で読み替えるには理由が要る（基準 3）。
  - 解消: (1) 検出規則を実データの各セルに当てた結果を 4.3 に書く。(2) S9 と同じ分解を合成の陽性と陰性対照に当て、分けるかを S15 に値で。(3) 分けられなければ「小さな個人差と prior mode の差とを、この手順では分けられない」へ書き換える。自信: 中（実データの誤指定が大きいという議論で基準を上げる道はあるが外枠に無い）
- [major] B. 構造の格子が上端（ar3）で止まり、tau の端に与えた配慮が構造に無い
  - 位置と引用: 12 行 "with the shared model itself (no per-person deviation, tau = infinity) among the candidates so that a choice at the edge of the grid can be read"／63 行 "The structure grid stops at three states ... ar3 was chosen in every cell, at the upper end."／要点 "what remains is at most about 1e-3"
  - なぜ: 要点の数は「3 状態まで」という止め方の関数。選んだ構造は「候補の中の最良」にとどまる（基準 4）。
  - 解消: (a) 1 セルで ar を K = 4 まで延ばすか平滑した 2 次の連鎖を加え、選択と残りが動くかを S8 か S9 に、または (b) 要点と 4.3 の見出しの文そのものに「3 状態までの候補の中で選んだ」と入れる。自信: 中
- [minor] C. 「閾値を置かない」としながら「at most about 1e-3」を境目に使う（62 行・4.3 の見出し・13 行 "+0.001"）。30-session の値を 2 桁で、「at most」がどのセルの上限かを 1 句で、重ならない窓の値を S13 に。自信: 中
- [minor] C2. novelty の文が投稿先の中心の文献を検索する前に置かれている（16 行・71 行）。検索を S1 に加えてから確定し、Related work に 1 項。自信: 高
- [minor] D. CS1 の感度の推論を seed 1 本と閾値すれすれの陰性対照（78% 対 80%）から引いている（49 行）。seed を増やすか "one seed per level; the negative control was close to the 80% rule" と限定し "consistent with" より弱く。自信: 中
- [minor] E. データ可用性の "every reported value can be recomputed" が公開するコードの範囲と合わない（53 行・S13・S14 のコードが列挙に無い・README 78 行）。列挙に S13〜S15 を入れるか範囲を限る。自信: 中
- [minor] F. 4.3 の 1,300 語に載せる内容が予算を超える見込み（49 行）。記号化の段落を 1 文と S13 の参照に、または 4.3 を 2 節に。自信: 中
- [nit] G. 分析の数え方が冒頭と 3.4 で合成の確かめを含まない（3 行・46 行）。3.4 に S15 を加える（条件はコードより前に固定と明記）。自信: 高
- [nit] H. 4.1 の hmm3 の本人のモデルで tau をどう決めたかが書かれていない（13 行・33 行）。1 句を足す。自信: 低

## 5. 総合の推奨: minor
- 引き継ぎ 8 件のうち 7 件は解消、N7 は研究者が残した一部のみ。
- 新しく加えた合成の検査が要点の「読まない」と緊張関係にある（A）。構造の格子の端（B）と合わせ要点の 1 文は書き換えが要る。
- どちらも既にある計算の当てはめか要点の限定の文で直せる見込み。本文を書く前に要点と 4.3 の見出しを直すことを条件に書き進めてよい。

## 6. 読めなかった範囲と注入の疑い
読んだもの: brief-R3・context-A・carryover-R3・outline.md 全 74 行・README 全 85 行。varma.txt は 3 行目だけ、liumeng.txt は 14–25・1712–1741 行と grep の行だけ。補足 S1〜S15 は読んでいない。注入の疑い: なし。
