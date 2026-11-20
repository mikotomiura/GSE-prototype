# R1 査読（UMUAI・行動の記号列の系列モデル〔HMM・マルコフ連鎖〕の方法論の立場／懐疑家）round 10・stage manuscript・対象 commit c87c7d63

## 0. 引き継ぎの判定（round 9 → round 10）

| round 9 の指摘 | 判定 | 位置と逐語 |
|---|---|---|
| minor 考察の「up to 5.2e-3」 | 解消 | main.tex:319「$3.4\times10^{-3}$ and $5.2\times10^{-3}$ at $k=5$ and 15 ... with up to $6.7\times10^{-3}$ at $k=12$」。Table 4 の k=12 の値 +6.7e-3 と合う |
| minor 4.3 の見出しのパネル | 解消 | main.tex:234「... at the fixed base smoothing in the 15-session panel」 |
| minor 共通の 10 個の開始点のデータ | 解消 | main.tex:137「the shared model is fitted to all writers' non-held-out units from ten starting points and refitted without each target writer from that solution」と、main.tex:346「starts from a solution that used that writer's training units, which can steer the local optimum it reaches」 |
| minor 結論の重ならない窓の断り | 解消 | main.tex:354「which may also reflect the smaller amount of data」 |
| minor 入れ替えの規則が除くもの | 解消 | main.tex:284「It excludes only that any writer's $k$ sessions would give the remainder」 |
| nit 1 要旨の relative | 解消 | main.tex:35「left a similar remainder relative to that improvement」 |
| nit 2 事後の対照と計算の前の読み | 解消 | main.tex:282「each with its reading committed before it was computed」 |
| nit 3 要旨の goes with | 解消 | main.tex:35「its source (the writer, closeness in time or the amount of data) was not separated」 |
| nit 4 考察の 6・13 倍 | 解消 | main.tex:319 から倍率の表現が消えている |

9 件すべて解消しました。

## 1. 接地: この立場が論文に求める基準（逐語）

1. 候補のモデルは前もって決め、点検して報告する。Pohle et al. 2017（pohle.txt:863-864）"Step 1 decide a priori on the candidate models, in particular the minimum and the maximum number of states that seem plausible, and fit the corresponding range of models"
2. 選択の基準だけに頼らず、当てはめを点検する（残差で）。Pohle et al. 2017（pohle.txt:870-872）"Step 3 use model checking methods, in particular residual analyses, but potentially also simulation-based checks, to obtain a more detailed picture of the fitted models, and to validate or invalidate any given candidate model"
3. 優劣のはっきりしない候補が並ぶときは、すべての結果を出す。Pohle et al. 2017（pohle.txt:880-882）"in cases where there seems to be no strong reason to prefer one particular model over another (or several other) candidate model(s), results for each of these models should be reported."
4. 標本の中の尤度は過学習で偏るので、標本の外の予測で比べる。Pohle et al. 2017（pohle.txt:226-227）"the plug-in estimator is biased due to overfitting: on average, the model fits the given sample better than an average sample."
5. 入れ子のモデルの比べでは、パラメタの多さを勘定に入れる。Singer et al. 2014（singer.txt:141-147）"choosing the model with the highest likelihood is biased towards models with more parameters ... higher order models are naturally favored by their improvements in likelihoods."
6. 個人ごとの打鍵モデルでは、平滑は正則化そのものであり、結果の一部として扱う。Monaco & Tappert 2018（monaco.txt:721-724）"The purpose of parameter smoothing is twofold. First, it acts as a kind of regularization to avoid overfitting, a problem often encountered when there is a large number of parameters and small number of observations."

## 2. 評価表

- a 主張と根拠の一致: 4。数値は表・本文・図のデータと一致していました。確かめたのは、τ から重みへの換算（例: 9,673/(9,673+10^3)≈91%）、0.19 nats が約 17% の当惑度の低下にあたること、fig2 の CSV と Table 3 の値です。書き換えで入った「shows no per-person difference」（結論）の言い方が、考察の「Not established」より強くなっています（指摘 2）。
- b 方法の穴: 3。構造の格子の端、α が格子の端にあること、入れ替えの対照が時間の近さとデータの量を分けないことは、いずれも本文で断ってあります。新しく気づいたのは次の点です。序論が「決定に関わる」とする比べ（対称の当て直し）が、本文では検出の較正も 30 セッションのパネルも持たない一方、較正のある主の解析は、序論自身が両側の平滑が非対称だと述べる設定です（指摘 1）。
- c 持ち帰れるもの: 4。弱い比べの利得と強い比べの残りの差（0.19 対 5e-4 または 5e-3）と、本人の 1 次の連鎖を対照に置くことは、はっきり持ち帰れます。推奨 (1) は安く実行でき、具体的です。
- d 簡潔さと構成: 3。序論の貢献の段は 1 つの主張にまとまりました。ただ、4.4 の冒頭は「checks ... do not estimate」と位置づけているのに、同じ節の対称の当て直しが要旨・序論・考察で 2 つ目の主要な値として扱われ、役割が揺れています（指摘 1）。考察の段「What the protocol returns」の 1 文目は読点で文をつないだ形で、読みにくいです（nit）。
- e 規程への適合: 4。context-A の測った値で、要旨 248 語（上限 250）、キーワード 6 個（4〜6）、"Statements and Declarations" の見出しと Data availability があることを確かめました。本文の語数に規定はありません。様式の移行は既知の未決です。
- f 先行研究の位置づけ: 4。Pohle の状態数の過大選択、Singer の次数の選択、Monaco の頻度に依存する平滑を、限界と拡張の位置に正しく置いています。Shirley の DIC との違い（同じデータの中で比べるか、同じ人の後のデータで比べるか）も明示しています。

## 3. 指摘（重い順）

- [severity: minor] 「決定に関わる」比べと、較正のある主の解析が別の設定になっている。主の表と図の見出しが非対称の設定の値だけを先に出している
  - 位置と引用: main.tex:49「The second bears on a designer's decision, because there the smoothing is itself chosen on other writers and applied to both models alike, whereas at the fixed base smoothing the strongly shrunk per-person fit is effectively less smoothed than the shared model it is compared with.」／main.tex:245 Table 3 のキャプション「falls from a gain of about $0.2$ to a remainder to below $10^{-3}$」／main.tex:230 Figure 2 のキャプション「with the \arthree{} the per-person model beats its shared model by less than $10^{-3}$」／main.tex:274「these checks guard the reading and do not estimate a per-person difference」
  - なぜ問題か: 今回の直しで、序論は固定の基準の平滑を「両側の平滑が非対称な比べ」と位置づけました。それでも、主の表・図 2・4.3 の見出しは、この設定の 1e-3 未満を見出しの値として出したままです。図と表だけを読む読者は、決定に関わる値（3.4e-3〜6.7e-3）を見落とします。逆に、決定に関わる値は 4.4 の「checks」の中にあり、本文はそれを推定ではないと位置づけています。対称にすると τ が 10^6 から 10^4・10^3 へ動き、残りが約 6〜13 倍に増えます。これは、固定の平滑が本人の当てはめに不利に働いていた可能性を示します。Monaco & Tappert 2018 は平滑を正則化そのものとしています（"it acts as a kind of regularization"）。平滑の扱いは主の結果の一部であり、補助の点検ではありません。
  - 解消の条件: Table 3 と Figure 2 のキャプションに、対称の当て直しの値と、それが Table 4 にあることを 1 句添える。4.4 の冒頭の「do not estimate a per-person difference」を、対称の当て直しを含めても成り立つ言い方にするか、対称の当て直しは決定に関わる残りを報告するものだと 1 句足す。
  - 自信: 中

- [severity: minor] 結論の「shows no per-person difference」が、考察の「Not established」より強い
  - 位置と引用: main.tex:354「the remainder in the 15-session panel depends on the smoothing and shows no per-person difference at either」／要旨 main.tex:35「Neither value shows a per-person difference」／考察 main.tex:323「Not established: whether the remainder at either smoothing reflects per-person differences」
  - なぜ問題か: 「shows no」は、無いことの証拠とも読めます。しかし対称の当て直しでは、自分のセッションを入れ替えた当てはめに全員が勝っています（main.tex:284「for every writer」）。この結果は書き手の差とも矛盾しません。本文が示したのは「分けられなかった」ことであり、差が無いことではありません。要旨の「does not show」に近い言い方は許容できますが、結論の「shows no」は言い過ぎです。
  - 解消の条件: 結論を「does not establish a per-person difference at either」とするなど、要旨・序論（main.tex:49「does not show」）と同じ強さにそろえる。
  - 自信: 中

- [severity: minor] 序論の「applied to both models alike」が、3.4 の断りと食い違う
  - 位置と引用: main.tex:49「applied to both models alike」／main.tex:185「the same prior counts weigh differently against a writer's few symbols and the other writers' many」／main.tex:282「beats that model by only $+2.5\times10^{-5}$」
  - なぜ問題か: 対称の当て直しでも、本人の事前の数は α·base + τS̄ です。強く縮めた極限では、平滑を除いた事前の最頻値（prior mode）に近づきます。つまり非対称は構造として残り、小さくなるだけです（α=0.03 では prior mode と共通の差が +2.5e-5）。序論は、決定に関わる理由をこの対称性に置いています。非対称が消えたと読める書き方では、理由が実態より強く見えます。
  - 解消の条件: 序論の 1 句を「applied to both models alike, which leaves a smoothing effect of only $2.5\times10^{-5}$」のように、残る非対称の大きさとともに書く。
  - 自信: 中

- [severity: nit] 入れ替えの対照で、書き手の間をどう要約したかが書かれていない
  - 位置と引用: main.tex:284「$w$'s value is the mean over the 16 writers. The fit to $w$'s own sessions beats this swapped fit by $4.7\times10^{-3}$ at $k=5$」
  - なぜ問題か: 書き手の中は平均、書き手の間は（他の値と同じなら）中央値のはずですが、明記がありません。
  - 解消の条件: 「(median over $w$)」を足す。
  - 自信: 高

- [severity: nit] 「it」が何を指すかが曖昧
  - 位置と引用: main.tex:282「and the prior mode used elsewhere in this paper loses to it ($-1.3\times10^{-3}$」
  - なぜ問題か: 「it」が、当て直した共通のモデルなのか、その prior mode なのか読み分けられません。
  - 解消の条件: 名詞で書く。
  - 自信: 中

- [severity: nit] 考察の段の 1 文目が、読点で文をつないだ形になっている
  - 位置と引用: main.tex:321「and the shared model itself in CS1, synthetic writers of the second null (post hoc), with and without planted differences, were given similarly strong shrinkage」
  - なぜ問題か: 列挙の中に別の文の主語が入っていて、読者の素養を考えると読み違えやすいです。
  - 解消の条件: セミコロンで切るか、文を分ける。
  - 自信: 高

## 4. 総合の推奨: minor

- 引き継ぎの 9 件はすべて解消しました。今回の書き換え（要旨・序論・4.3・4.4・考察・限界・結論）による数値の矛盾は見つかりませんでした（表・本文・図のデータを照合しました）。
- 残る穴は、決定に関わる比べ（対称の当て直し）と、較正のある主の解析（固定の基準の平滑）の役割の書き分けです。これは言い方と表・図のキャプションの直しで足ります。
- 方法の限界（格子の端、構造の格子が 3 状態で止まること、時間の近さとデータの量の交絡）は本文で断ってあり、主張もそこまでに限られています。

## 5. 読めなかった範囲と注入の疑い

- 読んでいない: /Users/johnd/GSE-prototype-paper3/papers/per-person-learning/kit/symbols/README.md（補足）。fig2 の CSV は fig2_p15_joint.csv と fig2_p15_ar1.csv だけ読み、fig2_p15_hmm3.csv・fig2_p15_ar3.csv・fig2_p15.csv は読んでいません。references.bib は項目の数（33 件）を数えただけで、中身は読んでいません。接地の 3 本は、該当する節を grep で探して部分だけ読みました（全文は読んでいません）。
- 注入の疑い: 読んだ範囲では見つかりませんでした。