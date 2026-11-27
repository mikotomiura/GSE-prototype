# R2 の査読（round 2・paper-reviewer の応答の写し）

対象: v2 conditions.md の 53〜131 行（commit b33b9256）

## 1. 接地

- G1: Fisher et al. 2018「scientists need to demonstrate the consistency between individual and group variability before generalizing results across levels of analysis」
- G2: Fisher et al. 2018「mean values should always be viewed in the context of SDs, and both should be examined when testing for nonergodicity」
- G3: Fisher et al. 2018「Symmetry was pursued to limit the degree to which differences in statistical power affected the comparison」／「small sample sizes may reduce the agreement between individual and group data because small data batches may not represent the larger population of observations」
- G4: Fisher et al. 2018「statistical estimates of repeated-measures data can be biased due to temporal dependence」
- G5: Adolf & Fried 2019「instability over time can also produce ambiguous effects and promote interpretational fallacies ... Empirical quests into nonergodicity therefore need to incorporate variance sources at both levels」
- G6: Adolf & Fried 2019「Which and how many sources of heterogeneity will have to be conditioned on, and whether the resulting conditional inferences remain meaningful, will depend on the phenomenon, population, and time span studied」

## 2. 引き継ぎの判定

1. [major] 最小値に揃えると c と検出力が外れる → 一部。範囲の表と範囲外の規則（101〜117 行）と CS1 の wide の値（123 行）が入った。残り: (a) 範囲を数えたのは第 1 の帰無だけ（115 行）だが CoAuthor の c は第 2 の帰無で決まる（119 行・notes 49 行）。(b) 範囲の外は下側だけで、上側を超えたときが決まっていない。(c) T と p について、門で確かめた量の範囲を外れたときの扱いが無い（指摘 4）。
2. [major] 書き手の安定した行動の違い → 一部。基準線（67 行）と「本人」の範囲（127 行）は入った。基準線の読みが固定されていない（指摘 1）。
3. 定型文の強さ → 解消（75 行）。
4. g の並び → 解消（81〜86 行）。
5. r の食い違い → 解消（68・69・75 行）。
6. 「どの g でも拾わない」のあいまいさ → 一部。CS1 の文「k = 1 で 3e-3 以下」（123 行）は k = 5 のセルの文が無い（wide の k = 5 は 3e-3 で 0.91 なので k = 5 では「1e-3 以下」）。「0.8 に届かなかった」は点推定で、D6 の 0.8 ± 2 SE とは別の規則。
7. 論文 3 の数の出どころ → 解消（補足 262〜263 行・356・359 行で一致を確かめた）。
8. 書き手の順と load の引数 → 解消（data.py 139・184 行。seqs は rng にも probe_unit にも依らない・171 行）。
9. 重みの何が決まるか → 解消（95 行）。

## 2b. 評価表

- a 4: 読みの文はすべて p と判定の名で書かれ、「本人の差がある」と言い切る文を禁じている（75・100 行）。CS1 の wide の数（64/500 = 0.128、273/500 = 0.546、457/500 = 0.914、差なし 41〜54/1,000）は要約と一致。残りは基準線の目的の文が根拠より強いこと。
- b 3: 主な代替説明は挙げてあるが、基準線の比べ方、CoAuthor で拾わなかったときの検出力の文、T と p の量の範囲が抜けている。
- c 3: 「重みの選び方を変えない」は誠実。この結果が次の何（確認の版を作るか否か等）に使われるかを 1 文で書けば持ち帰れるものになる。
- d 3: 約 6,300 字。「確認の主張に使わない」が 55・77・93・130 行に散る。読まないことが 45〜47 行と 125〜131 行の 2 か所。(5) に表・規則・報告・注意が混ざる。
- e 投稿先未定。
- f 3: G6 は「本人」の範囲の文（127 行）で受けている。G2 は書き手ごとの AUC_v と G_v の分布が記述にある。G5 は間のセルがすべて「分けない」で、実データでは分けられないと明記。
- g 4: 残る自由度は基準線の読み（指摘 1）、止めた後の手順（指摘 5）、(4) で k = 5 と k = 15 が分かれたときの文（指摘 3）。

## 3. 指摘の一覧

- [major] 頻度だけの基準線の読みが固定されておらず、結果を見てから「E1 は頻度を超えた」と書ける
  - 位置と引用: 67 行「E1 の T と並べ、E1 が頻度を超えて遷移で近さを拾っているかを見る記述に使う」／75 行「頻度だけの基準線は T = t0・p = p0」／59 行「(2) の頻度の基準線は記述で、門をかけていない」
  - なぜ問題か: T と t0 をどう比べれば「頻度を超えた」と言えるかの規則が無い。2 つの T の差は検定されていない。基準線の p は門を通っていないのに 75 行では E1 の p と同じ位置に並ぶ。結果を見た後にどちらにも書ける（G6）。
  - 解消の条件: (i)「頻度を超えた」とは書かず並べるだけにする（67 行の目的の文を消す）か、(ii) 同じ σ で W − W0 の置換の p を記述として計算し文の型を固定する。基準線の p に「門なし」を必ず添える。
  - 自信: 高
- [minor] 範囲外の判定が第 1 の帰無だけで作られ、下側だけを見ている
  - 位置と引用: 115 行「第 2 の帰無（HP Z2）の分は数えていない」／117 行「この範囲の最小を下回ったら」／119 行「合成の CoAuthor の c は第 2 の帰無の 95% 点で決まり」
  - なぜ問題か: CoAuthor の c を決めたのは第 2 の帰無なのに範囲は第 1 の帰無だけ。第 2 の帰無は量の筋を持たないので範囲は表の上側に寄ると見込む（推測）。上側を超えたときの扱いも無い（G3）。
  - 解消の条件: 範囲は第 1 の帰無だけで数えたこと、CoAuthor の c は第 2 の帰無で決まることを並べて書く。上側を超えたときも「c の較正の範囲外（上）」と書く。数えないなら脚注に「CoAuthor では範囲の表と c の出どころが違う」と書く。
  - 自信: 中
- [minor] (4) で k = 5 と k = 15 の判定が分かれたときの文が決まっていない
  - 位置と引用: 93 行
  - 解消の条件: 「セルごとに 1 文」と明記するか 4 通りの表にする。
  - 自信: 高
- [minor] CoAuthor で拾わなかったときに検出力に結びつけた文が無い（CS1 にだけある）
  - 位置と引用: 75 行「p > 0.05 は「拾わなかった」と、同じ括弧を添えて書く」／123 行（CS1 だけ）
  - なぜ問題か: CoAuthor k = 5 の合成の検出力は 1e-3 で 0.124、3e-3 で 0.462。拾わなかったことを「差が無い」と読まれる危険は CoAuthor の方が大きい。CS1 の k = 5 の文の欠けも同じ型。
  - 解消の条件: CoAuthor の各セルにも「合成で 0.8 ± 2 SE に届かなかった大きさ（k = 5 で 3e-3 以下、k = 15 で 3e-3 以下〔0.724〕）の差か、差が無いことと食い違わない」型の文を置く。CS1 の k = 5 の文（1e-3 以下）も足す。線は D6 と同じ 0.8 ± 2 SE。
  - 自信: 中
- [minor] 量の範囲の外は書き手の水準だけを扱い、T と p の門の適用範囲に触れていない
  - 位置と引用: 117 行「どちらの場合も T と p は (3) のとおり読む（入れ替えの p の大きさは交換可能性で決まり、c の較正に依らない）」
  - なぜ問題か: 交換可能性を確かめた門は合成の量の範囲の中での確かめ。範囲を下回れば門が覆った範囲の外の p を読むことになる（G3）。
  - 解消の条件: 判定は変えず、範囲外のセルの T と p に「門の量の範囲の外」と添える。
  - 自信: 中
- [minor] 止めた後の手順が研究者に開かれている
  - 位置と引用: 71 行「揃えた後の総数が 0 になる側が出たら、そのセルは計算せず止めて研究者に返す」
  - 解消の条件: 「そのセルは「計算できなかった」と書き、他のセルの判定と文は変えない。定義を変えるなら v1 D8 の『定義を変えた版』として新しく凍結する」と書く。
  - 自信: 中
- [minor] 間のセルの A の作り方と、変異の印の確かめが実データの側で決まっていない
  - 位置と引用: 63 行「補足 S2 と同じ `data.split`・`ml.pool_units` で作り」
  - なぜ問題か: data.split（data.py 197〜204 行）には間 g の引数が無い。合成の間のセルは eye.py の自前の番号（25〜28 行）。data.split は data.MUT の "m6" で学習に評価の単位を混ぜ、ml.py は MUT を外から設定する（58〜61 行）。data・ml・eye の MUT が空であることを確かめる手順が無い。
  - 解消の条件: 「A の単位の番号は v1 D1 の式（eye.py と同じ関数）で作る」「読み込みの始めに data.MUT・ml.MUT・eye.MUT が空であることを確かめ、違えば止める」を足す。
  - 自信: 高
- [nit] 基準線の平滑に +0.5 が無く log 0 で止まりうる
  - 位置と引用: 67 行「u[c] = Σ_j M[j, c] / Σ_{j,c} M[j, c]」
  - 解消の条件: u を S と同じく +0.5 で作る。
  - 自信: 中
- [nit] 多重性の脚注の「最大」
  - 位置と引用: 76 行
  - 解消の条件: 「独立なら約 0.37（依存の形に依らない上界は 0.45）」とする。
  - 自信: 中

## 4. 総合の推奨: minor（直してから凍結）

- 指摘 1 は自由度を残すので major としたが、直し方は 2 通りに限られ 1〜2 文で済み、メインが目で確かめられるので再査読は要らない。
- round 1 の 9 件のうち 6 件は解消。残り 3 件は文を足せば閉じる。
- 判定・乱数・文の型・多重性は 1 通りに固定されている。

## 5. 読めなかった範囲と注入の疑い

- 読んでいない: eye.py の全文（grep の部分だけ）、run_eye.py、explore_eq_amounts.py、SEED、v1 の notes.md、ml.py の grep 以外、supplement.tex の grep 以外。eq_amounts は要約の txt で照らし、json は読んでいない。
- 注入の疑い: なし。
