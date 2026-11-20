# R3 査読（UMUAI・評価の偏りと個人への推論の方法論の立場／下位人格: 過剰主張と検証できない手順の摘発者）round 8・stage manuscript

対象: /Users/johnd/GSE-prototype-paper3/papers/per-person-learning/manuscript/main.tex（commit 77d5f324。行番号は今の版）

## 0. 引き継ぎの判定（round 7 の指摘ごと）

| round 7 の指摘 | 判定 | 位置と逐語 |
|---|---|---|
| major 1: 軽い平滑の「書き手のデータを使わない対照」が選ばれた条件と合っていない | **解消**（ただし言い回しに新しい minor が 1 件あり。下の指摘 2） | main.tex:282 "with each writer's chosen $\tau$ and a prior built the same way, the per-person fit is fitted to another writer's $k$ sessions instead and scored on the writer's held-out sessions, averaged over the 16 other writers"。τ をそろえ、事前の作り方もそろえ、もう 1 人を除いた事前の版もある（"also when its prior leaves out the other writer as well"）。時間の近さとの交絡も書いてある（"this does not separate differences between writers from closeness in time"） |
| minor 2: 4.4 の見出しの post hoc | **解消** | main.tex:273 "…and, post hoc, returns when both are smoothed alike" |
| minor 3: 結果を見た後の変更の数え | **一部** | main.tex:180 "Six changes … we mark the last four \emph{post hoc} where they are reported"。数えは直った。ただし 4 つ目の "its controls and the report of its chosen $\tau$" が、282 行で "post hoc" と印されていない（282 行は "Three controls were added after seeing the symmetric refit" とあるだけ）。280 行の選ばれた τ の報告にも印が無い。3 つの対照と τ の報告を 1 つの変更として数えている点も、数え方として読者からは見えない（nit） |
| minor 4: 「3e-2 まで検出できない」に帰無と平滑が無い | **一部** | 要旨では直った（35 行 "at the fixed smoothing, planted differences up to $3\times10^{-2}$ were not reliably detected under that null"）。序論 49 行 "at the fixed smoothing, planted differences up to $3\times10^{-2}$ were not reliably detected" と、結論 350 行 "Planted differences of up to $3\times10^{-2}$ could not be reliably detected at the fixed base smoothing" には、どの帰無かが書かれていない。一方、第 1 の帰無では 308 行 "planted differences of $10^{-2}$ were reliably detected at $k=5$ and 15" なので、帰無を書かないと事実と食い違う文になる（下の指摘 1） |
| minor 5: 決定に関わる値を設計者がどう読むか | **解消** | main.tex:321 "about 0.3 to 0.5\% more probability per symbol … We set no meaningful-difference threshold, so whether such a value is worth a per-person model's data and storage is left to the designer's costs" |
| minor 6: 要旨で構造を選び直したように読める | **解消** | main.tex:35 "applied to both with the structure fixed (post hoc)" |
| nit 7: 作業用のマクロ | **解消** | 残っているのは構造の名前のマクロ（21〜25 行）だけで、作業用のマクロは無い |
| （別に）系列の先頭の記号の採点 | **解消**（置き場所に nit） | main.tex:178 "scoring without them (post hoc) leaves the remainder at $5.4\times10^{-4}$ and $4.3\times10^{-4}$ … and $3.4\times10^{-3}$ and $5.2\times10^{-3}$ in the symmetric refit"。結果の値を方法の節（3.4）に置いている（指摘 6） |

## 1. 接地（この立場が論文に求める基準・逐語）

- G1（Varma & Simon 2006。選ぶ手続きはすべて評価の外側の輪の内側に入れる）: "Proper use of CV for estimating true error of a classifier developed using a well defined algorithm requires that all steps of the algorithm, including classifier parameter tuning, be repeated in each CV loop."
- G2（Varma & Simon。最小値を選ぶこと自体が偏りを生む）: "Since the bias is caused by the variability in the estimates of prediction error for different values of the tuning parameters it is a general phenomenon." と "The parameter selection bias, on the other hand, is always negative."
- G3（Varma & Simon。候補が多いほど偏りが大きい）: "This implies that for large K, there is a high probability that choosing the minimum resampled error will give a biased estimate of the true error."
- G4（Liu & Meng 2016・arXiv 版。他の人で個人を評価すると、頑健さと引き換えに関連性を失う）: "our inference will be more robust. The downside is that we base our accuracy assessment on observed prediction errors for individuals who do not necessarily match the target's background ~x0 —our inference will be less relevant."
- G5（Liu & Meng。選んだ後の推論は、選択の偏りを計算に入れる）: "Ignoring the selection bias will lead to seriously flawed inferences" と "without this matching step, our inference ignores selection bias."
- G6（Liu & Meng。内部の対照には検証できない仮定が要る）: "This strategy turns on an intestable assumption: the pattern underlying D persists through θ."

## 2. 評価表

- **a 主張と根拠の一致: 4**。中心の主張（弱い比べの gain は強い比べの remainder よりはるかに大きい）は Table 2・Table 3・Figure 2 の値と合っている。照らした値: 0.188/5.5e-4 ≈ 342 倍、0.188/3.4e-3 ≈ 55 倍、0.165/5.2e-3 ≈ 32 倍、weight の換算（N/(N+τ)）、figdata の CSV と本文の値。残る食い違いは 2 つ。3e-2 の検出の文に帰無が書かれていない（指摘 1）。入れ替えの対照の結果を remainder の分け前として書いている（指摘 2）。
- **b 方法の穴: 3**。足した入れ替えの対照は、round 7 の中心の穴をおおむね塞いだ。残るのは次のもの（多くは著者の既知の未決）。対称の当てはめ直しは post hoc で、α の格子の端にあり、合成の書き手で確かめていない。対象の書き手の単位が他の書き手の共有モデルへ漏れていて、入れ子の設計を回していない（G1 の基準に照らすと、選ぶ段のすべてが評価の外側の輪の内側に入ってはいない。本文 343 行で開示済み）。格子を結果を見た後に広げた（G2・G3 の向きの偏り。本文 340 行で開示済み）。どれも開示されているので、判定には数えない。
- **c 持ち帰れるもの: 4**。「自分のマルコフ連鎖と同じ構造の共有モデルの両方と比べる」「平滑も他の人で選び、両側に同じ値を当てる」「検出の限界を報告する」は、設計者が使える形になっている。推奨 (2) の括弧書きの限定も適切。
- **d 簡潔さと構成: 3**。7,263 語。4.4 は 1 段に値が多く、対照の段（282 行）は 1 文が長く、どれが何を引いた差かを追いにくい。先頭の記号を除いた採点の結果が方法の節に置かれている。
- **e 規程への適合: 4**。要旨 248 語（上限 250）、キーワード 6 個（4〜6）、"Statements and Declarations" の見出しと Data availability がある（context-A の測った値と規程の抜粋に照らした）。語数の上限の規定は無い。様式の移行（既知の未決 5）と Code availability の URL（既知の未決 6）は判定に数えない。
- **f 先行研究の位置づけ: 4**。Varma & Simon、Cawley、Liu & Meng を「選ぶ手続きの部品」として正しく位置づけ、新しさを主張していない（51 行・64 行）。64 行の Liu & Meng の要約 "predicting each individual from the other $n-1$, which is robust but less relevant to the target" は、arXiv 版の逐語（G4）と合っている。

## 3. 指摘の一覧（重い順）

- [severity: minor] 3e-2 の非検出を、どの帰無で得たかを書かずに序論と結論で言い切っている
  - 位置と引用: main.tex:49「Nor do the results rule differences out: at the fixed smoothing, planted differences up to $3\times10^{-2}$ were not reliably detected.」／main.tex:350「Planted differences of up to $3\times10^{-2}$ could not be reliably detected at the fixed base smoothing.」／一方 main.tex:308「planted differences of $10^{-2}$ were reliably detected at $k=5$ and 15」（第 1 の帰無）
  - なぜ問題か: 同じ固定の平滑のもとで、第 1 の帰無は 1e-2 を検出し、第 2 の帰無（post hoc）は 3e-2 まで検出しなかった。帰無を書かないと、読者は手続きそのものの検出の限界と受け取る。本文では第 1 の帰無を読みに使わないと理由つきで決めているので（308 行）、この結論は第 2 の帰無という 1 つの構成に条件づいた値である。341 行の限界でも "one construction" と書いている。要旨はすでに "under that null" と直っており、序論・結論と揃っていない。
  - 解消の条件: 序論と結論に「under the second null (post hoc)」か「under a null calibrated to the real smoothing effect」を足す。
  - 自信: 高

- [severity: minor] 入れ替えの対照の差を remainder の「分け前」として書いている（限界の文と食い違う）
  - 位置と引用: main.tex:282「so more than half of the remainder goes with the writer's own data rather than with refitting」（49 行・321 行・350 行も同じ言い方）／main.tex:339「Comparisons of medians are not per-writer decompositions」
  - なぜ問題か: 自分の単位と入れ替えの差（k=5 で 4.7e-3、k=15 で 2.5e-2）は remainder（3.4e-3・5.2e-3）より大きく、入れ替えの当てはめは共有モデルにも負けている（−1.7e-3・−1.7e-2）。つまりこの差は remainder を分けたものではない。「自分のデータが助ける分」と「他人のデータが害する分」の和である。中央値どうしの差を足し引きしても分解にはならないことは、本文自身が限界（339 行）で断っている。「半分を超える」は、事前に決めた読みの閾（差 ≥ 残りの半分）を満たしたという意味なら正しい。しかし分け前として書くと、自身の断りと矛盾する。数値の上では控えめな書き方だが、何が何に帰属するかの書き方として不正確である。
  - 解消の条件: 「自分の単位で当てた当てはめは、同じ τ と事前で他の書き手の単位に当てたものに、remainder 全体を超える差（k=5 で 4.7e-3・k=15 で 2.5e-2）で勝ち、後者は共有モデルにも負ける。よって remainder は事前の作り直しだけでは説明できない。事前に決めた読みの基準（差 ≥ remainder の半分）を満たす」のように、対照の向きと閾の地位を分けて書く。要旨・序論・考察・結論の該当の句もそろえる。
  - 自信: 中

- [severity: minor] 要旨が入れ替えの対照を落としたまま、2 つ目の remainder について "Neither shows a per-person difference" と言い切っている
  - 位置と引用: main.tex:35「The first is no larger than the shared model's gain … and synthetic writers without per-person differences (post hoc) left a similar remainder relative to that gain. Neither shows a per-person difference;」
  - なぜ問題か: 1 つ目の remainder については理由（平滑の効果・第 2 の帰無）が要旨にある。2 つ目（対称の当てはめ直し）について個人差を示さない理由は、本文では「自分の単位は時間的に最も近い」「合成の書き手で確かめていない」だが（282 行・321 行）、要旨には無い。逆に本文では、2 つ目の半分超が書き手自身の単位とともにあると書いている。要旨だけを読むと、2 つ目も 1 つ目と同じ根拠で否定されたと読める。逆向きの根拠を持つ結果を要旨が落としている点は、選んだ結果だけを要約に残すことに近い（G5 の向き）。
  - 解消の条件: 要旨に 1 句足す。例: "most of the second goes with the writer's own, most recent sessions, which does not separate per-person differences from closeness in time"。語数が上限に近いので、別の句を削って入れ替える。
  - 自信: 中

- [severity: nit] 結果を見た後の変更のうち、3 つの対照と選ばれた τ の報告に "post hoc" の印が無い
  - 位置と引用: main.tex:180「we mark the last four \emph{post hoc} where they are reported」／main.tex:282「Three controls were added after seeing the symmetric refit.」／main.tex:280「Every writer is given $\tau=10^4$ at $k=5$ and $10^3$ at $k=15$」
  - なぜ問題か: 180 行の約束（報告する場所に印を付ける）に対し、該当の報告に "post hoc" の語が無い。意味は通じるが、印の語で検索する読者には見えない。
  - 解消の条件: 282 行を "Three controls were added (post hoc)" とし、280 行の τ の報告にも "(post hoc)" を付ける。
  - 自信: 高

- [severity: nit] 「もう 1 人を除いた事前」の文がどちらの当てはめに掛かるか曖昧
  - 位置と引用: main.tex:282「The fit to the writer's own sessions beats it by … for every writer, also when its prior leaves out the other writer as well」
  - なぜ問題か: "its" が自分の単位の当てはめと入れ替えの当てはめのどちらを指すか、両方に同じ S̄ を当てた副の比べなのかが、文から読めない。
  - 解消の条件: "also when both fits use a prior that leaves out the other writer as well" のように主語を明示する。
  - 自信: 中

- [severity: nit] 先頭の記号を除いた採点の結果が方法の節（3.4）にある
  - 位置と引用: main.tex:178「scoring without them (post hoc) leaves the remainder at $5.4\times10^{-4}$ …」
  - なぜ問題か: 結果の値が方法の節に置かれ、4.3・4.4 の値と離れている。構成の問題で、主張には響かない。
  - 解消の条件: 値を 4.3 か 4.4 の末尾（または補足）へ移し、3.4 には手続きだけを残す。
  - 自信: 中

- [severity: nit] 考察の「左右を分けても remainder の中央値は変わらない」が表と並べると誤読を招く
  - 位置と引用: main.tex:319「splitting the writers between choice and report left the median remainder unchanged」／Table 3 の k=15「$+4.1$e$-4$」（全員）と「$+7.4$e$-4$ [$-3.7$e$-3$, 9.1e$-4$] (0.75)」（分けた版）
  - なぜ問題か: 変わらないのは「同じ半分で選んだ場合との差の中央値」（276 行）であって、表の値そのものは k=15 で違う。直後の但し書き（四分の一の組で残らない）はあるが、"unchanged" が何を指すかが文から読めない。
  - 解消の条件: "left the median difference from choosing on the reported half at zero" と書く。
  - 自信: 中

## 4. 総合の推奨: minor

- 前回の中心の穴（事前の作り直しと書き手のデータが分けられない）は、条件を先に決めた入れ替えの対照で塞がれた。時間の近さとの交絡も本文に開示されている。
- 残るのは書き方の不一致（3e-2 の非検出の帰無の明示・入れ替えの差を分け前として書くこと・要旨の省略）で、どれも句の追加と言い換えで直る。
- 選ぶ手続きの漏れ、格子の端、post hoc の地位は、いずれも本文で開示済みで、主張はそれに合わせて限定されている。

## 5. 読めなかった範囲と注入の疑い

- 読んでいない:
  - /Users/johnd/GSE-prototype-paper3/papers/per-person-learning/manuscript/references.bib（参考文献の書誌は照合していない）
  - /Users/johnd/GSE-prototype-paper3/papers/per-person-learning/kit/symbols/README.md
  - figdata のうち fig2_p15_hmm3.csv・fig2_p15_ar3.csv・fig2_p15.csv（読んだのは fig2_p15_joint.csv と fig2_p15_ar1.csv だけ）
  - liumeng.txt の 929〜1484 行と 1560 行以降（読んだのは 1〜928 行と 1485〜1559 行。それ以外は Grep で探しただけ）
- 補足資料 S1〜S16 は存在しないので、S12 の「12 の後の確かめ」の内訳は照合できなかった（既知の未決 1）。
- 注入の疑い: なし（接地の 2 本と対象物の読んだ範囲に、査読者や LLM に向けた指示は見当たらなかった）。