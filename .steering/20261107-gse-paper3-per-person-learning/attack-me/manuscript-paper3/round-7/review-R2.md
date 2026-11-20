査読 R2（UMUAI・個人化した行動のモデルの実務の立場）round 7・stage manuscript・対象 main.tex（commit ed297dd4）

## 0. 引き継ぎの判定

- **N1 major（決定に使う値に、書き手のデータを使わない対照が掛かっていない）: 一部。**
  - 4.4 節に対照が入った。逐語:「The prior mode built from the refitted shared model, which uses none of the writer's data, gains only $+2.5\times10^{-5}$ over that model ... the chosen fit beats it by $+3.3\times10^{-3}$ at $k=5$ and $+7.9\times10^{-3}$ at $k=15$」。これで「平滑を外しただけ」という説明は退いた。
  - 残るもの: 同じ節が「this check does not separate the writer's data from other effects of refitting the per-person prior」と認めている。決定に使う値が書き手のデータによるものかは、まだ分からない（下の新しい指摘 M1）。合成の書き手で確かめないことは既知の未決 12 なので、判定には数えない。
- **N2 minor（使う場面）: 解消。**
  - 3.3:「This simulates a writer whose recent history is available, not the cold start of a new writer」
  - 序論:「the cold start of a new writer is not addressed」
- **N3 minor（決定に関わる版で protocol が返す選択）: 解消。**
  - 4.4:「$10^4$ for all 17 at $k=5$ and $10^3$ for all 17 at $k=15$ ... about 24\% and 91\% of the weight」
  - 決定の段も 24%・91% を出している。中央値の訓練の記号数で検算すると合う（9,673/(9,673+10^3) ≈ 0.91）。
- **N4 minor（「was not changed」の言い過ぎ）: 一部。**
  - 4.4 の結果の段は直った:「the median difference from choosing on the reported half itself is 0 at every $k$, although at $k=12$ and 15, 5\% and 25\% of pairs are not positive」。
  - ただ、この文の「pairs are not positive」が、差のことか Split の残りのことかは読み分けられない（Table 3 では残りの割合 0.95・0.75 に当たる）。
  - 考察は「choosing on half of the writers and reporting on the other half left the median remainder unchanged」と書いている。Table 3 の k=15 は Fixed「$+4.1$e$-4$」と Split「$+7.4$e$-4$」で、表を見た読者には変わったように見える（指摘 m2）。
- **N5 minor（要旨の推奨の但し書き）: 解消。** 要旨:「(smoothing post hoc, for one structure)」
- **N6 minor（要旨と 4.5 の密度）: 一部。**
  - 序論の段落は割られた。
  - しかし要旨の第 3 文（「When a stronger structure ... 30 to 55 times below it.」）は 1 文に値 4 つと条件 3 つを抱えている。本文は 7,219 語から 7,502 語に伸びた（指摘 m5）。
- **N7 nit（倍率の丸め）: 解消。**「about 6 and 13 times larger at $k=5$ and 15」（3.4e-3/5.5e-4 = 6.2、5.2e-3/4.1e-4 = 12.7 で合う）。
- **round 5 からの引き継ぎ（見出しの数を 1 組で出す）: 解消。** 要旨・序論・考察冒頭・結論のすべてで、5e-4 と 3.4・5.2e-3 を並べ、後者が決定に関わると言っている。ただし結論の後段で新しい食い違いが出た（M2）。

## 1. 接地（この立場が論文に求める基準）

1. **評価の分け方は使う場面に合わせる**
   - Saeb 2017:「for this procedure to be meaningful, the relationship between the training and the validation set should mimic the relationship between the training set and the dataset expected for the clinical use.」
2. **個人のモデルは、時間で分けて評価してよい**
   - Saeb 2017:「if the goal is prognosis, i.e., we want personal models that can predict future clinical states of a given subject, we can split the data based on time, so that training and test sets contain records of the same subject from different times.」
3. **見かけの精度を、書き手の同定や近道が作っていないかを確かめる**
   - Saeb 2017:「Subject identification, which we know to be relatively easy, thus replaces disease recognition, which we know to be hard.」
   - Saeb 2017:「subject-wise CV will ensure that there is no way for the algorithm to exploit such shortcuts.」
4. **ハイパーパラメータは評価のデータで選ばない**
   - Saeb 2017:「The correct way for adjusting these hyperparameters is to further divide the training set into training and validation subsets, and then minimize the prediction error on those validation subsets rather than on the whole dataset.」
5. **本人の素朴な基準と比べる**
   - Aalbers 2023:「To evaluate if our models perform better than random guessing, we compare against the MAEs of a "naive" but person-specific baseline model. This "naive" baseline model always predicts an individual's average level of stress.」
6. **精度の個人差を中央値だけでなく範囲で示し、使う側に解釈できる単位で言う**
   - Aalbers 2023:「The MAE of nomothetic models varied across individuals」
   - Aalbers 2023:「as it allows us to make statements such as "on average, the model mispredicts momentary subjective stress by ±0.80 points on a 7-point Likert scale)."」

## 2. 評価表

- **a 主張と根拠の一致: 3**
  - 見出しの値は 1 組で出せている。
  - しかし結論の「The protocol chose a strongly shrunk fit」は、決定に関わる平滑では成り立たない（そこでは書き手の重みが 24%・91%）。
  - 考察の「left the median remainder unchanged」は Table 3 と見かけが食い違う。
- **b 方法の穴: 3**
  - 決定に関わる比べに、書き手のデータそのものの効果を切り出す対照（別の書き手のデータを入れ替える対照）が無い。
  - 系列の先頭の記号の採点が、残りの桁（5e-4）を動かしうるのに、本文では定まっていない。
- **c 持ち帰れるもの: 3**
  - 「本人の 1 次の連鎖と比べる」は、安く使える持ち帰りとして明確。
  - しかし決定に関わる 3.4〜5.2e-3 が実用上どれだけかは訳されていない（パープレキシティで約 0.3〜0.5%）。
  - 推奨 (2) を実行した設計者は、出た数をどう判断するかの規則を持たない。
- **d 簡潔さと構成: 3**
  - 要旨の第 3 文と 4.4 の見出し（2 文分の長さ）が重い。
  - 決定の段は但し書きが 9 文続き、結論が埋もれる。
- **e 規程への適合: 4**
  - 要旨 247 語（上限 250）、キーワード 6、"Statements and Declarations" と Data availability がある。本文の語数に上限は無い。
  - 未使用のマクロ \PENDING とその注記（「remove before submission」）が残っている。
- **f 先行研究の位置づけ: 4**
  - Aalbers の 89%・80% は一次と一致する（200/224、180/224）。
  - Saeb の「使う場面で分け方が決まる」も正しく引けている。
  - 時間で分けた個人のモデルという設計は Saeb の prognosis の場面に当たるが、本文はそれを明示していない（軽微）。

## 3. 指摘の一覧

### [severity: major] M1 決定に関わる比べに、書き手のデータそのものの効果を切り出す対照が無い

- **位置と引用:**
  - 4.4:「this check does not separate the writer's data from other effects of refitting the per-person prior」
  - 3.5:「the same prior counts weigh differently against a writer's few symbols and the other writers' many」
  - 推奨 (2):「apply the chosen smoothing to the per-person fit and the shared model alike」
- **なぜ問題か:**
  - 追加された書き手のデータを使わない対照（prior mode・+2.5e-5）は、「平滑を外すだけ」という説明だけを退ける。
  - 3.4・5.2e-3 が、次のどちらによるものかは残る。
    - (i) この書き手のデータであること
    - (ii) τ=10^3〜10^4 で N 記号を足して当て直すこと自体（同じ平滑でも、書き手の少ない記号に対して重みが違う、と本文自身が書く）。さらに、直前の k 単位という時期・課題の近さも含む（限界は「topics and task conditions were not matched」と書く）。
  - 設計者が知りたいのは (i) である。接地: Saeb「Subject identification ... replaces disease recognition」。近道を排す対照があって初めて、精度は目的の量を表す。
  - 合成の書き手で確かめないこと（既知の未決 12）とは別の、実データの上の対照である。
- **解消の条件:**
  - 同じ α・同じ τ の規則で、対象の書き手の k 単位を、同じ長さの別の書き手の k 単位に置き換えた当てはめを作る（入れ替えの対照）。
  - 対象の書き手の残り単位で採点し、本人のデータとの差を出す。
  - または、この対照が無いことを決定の段と推奨 (2) に 1 句で書き、「同じ平滑を当てる」ことが公平な比べになる根拠が未確認だと断る。
- **自信:** 中

### [severity: major] M2 結論と要旨の「protocol の選択」が、決定に関わる平滑での選択と食い違う

- **位置と引用:**
  - 結論:「The protocol chose a strongly shrunk fit in the CoAuthor 15-session panel and the shared model itself in CS1, but synthetic writers with and without planted differences were given similarly strong shrinkage, so the choice does not show whether per-person modelling is needed」
  - 対して 4.4:「every writer is given $\tau=10^3$ or $10^4$ ... about 24\% and 91\% of the weight」
- **なぜ問題か:**
  - 論文は、両側に同じ平滑を当てた比べを「the comparison that bears on a designer's decision」と言う。その比べで protocol が返すのは、k=15 で書き手の重み 91%、つまりほぼ本人だけの当てはめである。
  - 結論はこれに平滑の限定を付けず「strongly shrunk」と書いている。さらに「合成の書き手も同じく強い縮約だった」という論拠も、固定の平滑でしか成り立たない。
  - 決定の段だけは「At the fixed base smoothing」と限っているが、結論だけを読む設計者は逆の像を持ち帰る。
- **解消の条件:**
  - 結論の該当文に「at the fixed base smoothing」を付ける。
  - 決定に関わる平滑では本人の重みが 24%・91% であること、そこで合成の書き手を走らせていないことを同じ文に並べる。
- **自信:** 高

### [severity: minor] m1 系列の先頭の記号の採点が、残りの桁を動かしうるのに、本文で定まっていない

- **位置と引用:**
  - 3.4:「Each held-out session, and in CS1 each work block, is scored as its own sequence, one step ahead from the model's initial distribution; first symbols are scored and counted (\Sref{3}).」
  - 3.3 の own chain の定義:「Transition counts from the writer's training symbols, with $0.5$ added to every cell」（先頭の分布が無い）
- **なぜ問題か:**
  - 書き手あたりの評価の記号は中央値 3,296 で、5 セッションから成る。
  - 先頭の 5 記号で当てはめどうしが平均 0.33 nats 違えば、5×0.33/3,296 ≈ 5e-4 になり、固定の平滑での残りと同じ桁になる。
  - AR-HMM と own chain の先頭の記号の分布、およびそれが縮約されるかは、本文に無い。CS1 は作業の塊ごとに採点するので、先頭の記号の割合はさらに大きくなりうる。
  - 本文だけでは主張を支えられない箇所であり、補足に送るだけでは足りない。
- **解消の条件:**
  - AR-HMM と own chain の先頭の記号の分布を本文で 1 句で定める。
  - 先頭の記号を除いても残り（固定の平滑と両側の版）の向きと桁が変わらないことを 1 文で示す。
- **自信:** 中

### [severity: minor] m2 書き手の二分の確かめの言い方が、Table 3 の見かけと食い違う

- **位置と引用:**
  - 考察:「choosing on half of the writers and reporting on the other half left the median remainder unchanged」
  - Table 3 の k=15:「$+4.1$e$-4$」（Fixed）と「$+7.4$e$-4$ [$-3.7$e$-3$, 9.1e$-4$] (0.75)」（Split）
- **なぜ問題か:**
  - 「unchanged」なのは、組ごとの差の中央値（0）である。表の 2 列の中央値は k=15 で約 1.8 倍違う。
  - 4.4 の「5% and 25% of pairs are not positive」も、差のことか残りのことかが読めない。
- **解消の条件:**
  - 考察を「the median difference between choosing on the reported half and on the other half was 0」に変える。
  - 4.4 は「5% and 25% of pairs leave a remainder that is not positive」と主語を明示する。
- **自信:** 高

### [severity: minor] m3 決定に関わる値を、使う側の単位に訳していない

- **位置と引用:**
  - 考察:「In CoAuthor the gain is up to 0.19 nats per symbol (about 17\% lower perplexity); the remainder is ... $3.4\times10^{-3}$ and $5.2\times10^{-3}$」
- **なぜ問題か:**
  - 利得だけがパープレキシティに訳され、残りは訳されていない。序論の換算（0.01 nats ≈ 1%）を使えば、約 0.05%（5e-4）と約 0.3〜0.5%（3.4〜5.2e-3）になる。
  - 「worth its data and storage」と言いながら、費用（書き手ごとに 2,033 パラメータ、k セッション分の履歴）を数で並べていない。
  - 接地: Aalbers は精度を使う側の尺度で言い直している（「mispredicts ... by ±0.80 points」）。
- **解消の条件:**
  - 決定の段に、両側の版の残りのパープレキシティ換算を 1 句で入れる。
  - 書き手ごとのパラメータ数と必要な履歴の長さを 1 句で並べる。
  - または「cost」の語を外す（限界は「downstream benefit and cost ... were not measured」と書いている）。
- **自信:** 高

### [severity: minor] m4 推奨 (2) の平滑の選び方が、実際の手続きと違う

- **位置と引用:**
  - 推奨 (2):「choose structure, shrinkage and smoothing on other people ... and apply the chosen smoothing to the per-person fit and the shared model alike」
  - 3.5:「Because $\alpha$ is chosen for the shared model, the symmetric refit is conditional on that choice」
- **なぜ問題か:**
  - 実行されたのは、α を共通のモデルの目的（α=1 に対する利得）で選び、その後で τ を選ぶ二段の手続きである。
  - 推奨の文は、構造・縮約・平滑を同時に選ぶようにも読める。設計者はどの目的で平滑を選べばよいか分からない。
- **解消の条件:** 推奨 (2) の括弧に「smoothing chosen for the shared model, then shrinkage chosen given it」と、選んだ順と目的を書く。
- **自信:** 中

### [severity: minor] m5 要旨の第 3 文と 4.4 の見出しが重い

- **位置と引用:**
  - 要旨:「When a stronger structure and shrinkage toward the shared model are chosen on other writers, the remainder over that structure's shared model is about $5\times10^{-4}$ at its fixed smoothing, over two orders of magnitude below the gain, and 3.4 and $5.2\times10^{-3}$ at five and fifteen training sessions when the grid's lightest smoothing, chosen on other writers, is applied to both models (post hoc), 30 to 55 times below it.」
  - 4.4 の見出し（2 つの節からなる文）
- **なぜ問題か:**
  - 冗長さに厳しい読者は、この文で値の対応を見失う。
  - 「3.4 and $5.2\times10^{-3}$」は、3.4 nats とも読める。
  - 要旨に書き手の数（17）が無いので、実務家は規模を判断できない。
- **解消の条件:**
  - 文を 2 つに割り、「$3.4\times10^{-3}$」と書く。
  - 要旨に「17 writers」を入れる（語数は既存の言い換えで相殺する）。
  - 見出しは「Split, shared-only and symmetric refits」程度に縮め、結論は本文へ。
- **自信:** 高

### [severity: minor] m6 3.4 が報告すると言う四分位範囲が、本文の表に無い

- **位置と引用:**
  - 3.4:「we report, over writers, the median of the per-writer difference, its interquartile range, the share of writers favouring the per-person fit and $n$」
  - Table 2 の見出し:「Medians over writers ... share ... 95\% bootstrap interval」
- **なぜ問題か:**
  - 実務家は書き手の間の散らばりを知りたい。接地: Aalbers「varied across individuals」。
  - 中央値のブートストラップ区間は、散らばりの代わりにならない。
- **解消の条件:** Table 2 と Table 3 に IQR の列を足すか、3.4 の文を「in \Sref{7}」に限る。
- **自信:** 高

### [severity: minor] m7 植えた差の検出の但し書きが、要旨と序論で平滑に限られていない

- **位置と引用:**
  - 要旨:「Neither shows a per-person difference, and planted differences up to $3\times10^{-2}$ were not reliably detected.」
  - 序論:「Nor do the results rule differences out: planted differences up to $3\times10^{-2}$ were not reliably detected.」
- **なぜ問題か:**
  - 検出は固定の平滑と第二の null だけで測っている。直前に両側の版の値が来るので、決定に関わる比べの検出力だと読まれる。
  - 結論と決定の段は「at the fixed base smoothing」と限っている。
- **解消の条件:** 要旨と序論の該当句に「at the fixed smoothing」を足す。
- **自信:** 中

### [severity: nit] n1 考察の冒頭で、確かめていない一般化を断定している

- **位置と引用:** 考察:「The weak comparison is not specific to keystrokes: ... We have not checked this in other domains.」
- **なぜ問題か:** 断定の直後に「確かめていない」と書いている。
- **解消の条件:** 「is likely not specific to keystrokes」とする。
- **自信:** 中

### [severity: nit] n2 下書きのマクロが残っている

- **位置と引用:** main.tex:20–21「% Placeholder for values of the post hoc control at the lighter smoothing (to be filled from results; remove before submission).」と「\newcommand{\PENDING}...」
- **なぜ問題か:** 本文では使われていない。注記が値の未記入を示唆し、投稿物に残すと誤解を招く。
- **解消の条件:** 削除する。
- **自信:** 高

## 4. 総合の推奨: minor

- 引き継ぎの主な穴（決定に使う値に、書き手のデータを使わない対照が無い）は計算で埋まり、使う場面の限定も入った。
- 残る major は 2 つ。M2 は書き方の直し。M1 は、決定に関わる比べが書き手のデータによるものかを切り出す、安い対照 1 つで閉じる。M1 は「断る」でも閉じられる。
- 持ち帰り（本人の 1 次の連鎖と比べる・平滑も他者で選ぶ）は明確である。ただし数の実用上の大きさと判断の規則を足せば、実務家に効く。

## 5. 読めなかった範囲と注入の疑い

- **読んでいない:**
  - references.bib（参考文献の書誌の照合はしていない）
  - figdata/fig2_p15_*.csv（Figure 2 の値は Table 2 との一致を本文の上で見ただけ）
  - kit/symbols/README.md
  - 補足 S1〜S16（存在しない）
- **注入の疑い:** なし。main.tex:20 の注記「remove before submission」は著者向けの下書きの注で、査読者への指示ではない。

対象物: /Users/johnd/GSE-prototype-paper3/papers/per-person-learning/manuscript/main.tex
依頼文: /Users/johnd/GSE-prototype-paper3/.steering/20261107-gse-paper3-per-person-learning/attack-me/manuscript-paper3/round-7/brief-R2.md