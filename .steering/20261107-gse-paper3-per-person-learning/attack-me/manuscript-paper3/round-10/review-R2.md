# R2（UMUAI・個人化した行動のモデルの実務の立場）round 10 の査読

対象は main.tex（commit c87c7d63）の全文と figdata/fig2_p15*.csv です。この立場の査読者として書きます（実在の個人を名乗りません）。

## 0. 引き継ぎの判定

1. **minor 要旨の検出の限界の範囲 → 解消**
   - 要旨（l.35）「at the fixed base smoothing, planted differences up to $3\times10^{-2}$ were not reliably detected under the post hoc null」
2. **minor 決定の段の例が隠れ状態を読まないことと食い違う → 解消**
   - 考察（l.321）「A writing assistant that times hints by the predicted probability that the next seconds are a pause」
   - 例と隠れ状態の食い違いは消えました。ただしこの例が CS1 の結果と新しく食い違います（下の指摘 3）。
3. **minor 両側の版に区間が無い → 解消**
   - 表 3（l.303, l.306）「$+3.4$e$-3$ [2.7e$-3$, 6.1e$-3$] (0.94)」「$+5.2$e$-3$ [2.9e$-3$, 1.2e$-2$] (0.88)」
   - キャプションに、区間は k = 5・15 だけにあると明記されています。
4. **minor 推奨 (2) の選びの順 → 一部**
   - l.329「choose the smoothing on other people for the shared model, apply it to the per-person fit and the shared model alike and choose shrinkage given it ... choosing all three jointly was not tried」
   - 平滑と縮みの順は書かれました。しかし (2) の前半「choose structure and shrinkage on other people」との順（構造をいつ、どの平滑の下で選ぶか）が読めません。要旨の「choose structure, shrinkage and, applied to both models, smoothing on other people」は 3 つを同時に選ぶようにも読めます（指摘 4）。
5. **minor 費用の目安 → 解消**
   - l.321「about one ($k=5$) to three ($k=15$) hours of a writer's typing and 2,033 stored parameters per writer」
   - 表 1 の訓練の記号数の中央値（k = 15 で 9,673 秒、約 2.7 時間）とも合います。
6. **nit 要旨の goes with → 解消**
   - l.35「its source (the writer, closeness in time or the amount of data) was not separated or checked on synthetic writers」
7. **nit 4.4 の入れ替えの段が詰まりすぎ → 解消**
   - 最頻値の 2 つの対照（l.282）と入れ替え（l.284「Does the remainder need the writer's own sessions, or would any $k$ sessions do?」）に分かれました。
8. **nit reported post hoc の位置 → 解消**
   - l.280「The chosen $\tau$, reported post hoc, is $10^4$ ...」
9. **nit asymmetric one → 解消**
   - l.185 と l.278 に「shared-only refit」とあります。

## 1. 接地（この立場が論文に求める基準）

- **S1 評価の分け方は使う場面に合わせる**
  - Saeb et al. 2017「for this procedure to be meaningful, the relationship between the training and the validation set should mimic the relationship between the training set and the dataset expected for the clinical use.」
- **S2 個人のモデルの使う場面は時間で分けた予測**
  - Saeb et al. 2017「if the goal is prognosis, i.e., we want personal models that can predict future clinical states of a given subject, we can split the data based on time」
- **S3 ハイパーパラメータは評価のデータで選ばない**
  - Saeb et al. 2017「The correct way for adjusting these hyperparameters is to further divide the training set into training and validation subsets, and then minimize the prediction error on those validation subsets rather than on the whole dataset.」
- **S4 個人ごとの素朴な基準と比べる**
  - Aalbers et al. 2023「To evaluate if our models perform better than random guessing, we compare against the MAEs of a "naive" but person-specific baseline model.」
- **S5 使う側にとっての大きさで述べる**
  - Aalbers et al. 2023「it allows us to make statements such as "on average, the model mispredicts momentary subjective stress by ±0.80 points on a 7-point Likert scale)."」
- **S6 個人化の代償（データの少なさ）を明示する**
  - Aalbers et al. 2023「However, this comes at the cost of strongly reduced sample size, which limits model complexity and may lead to overfitting.」

## 2. 評価表

- **a 主張と根拠の一致: 4**
  - 要旨・序論・結論の数値は表 2・3 と合います（5.5e-4 / 4.1e-4、3.4e-3 / 5.2e-3、0.19、17%、0.3〜0.5%、重みの換算も N/(N+τ) で検算して合いました）。
  - 残る問題は、両側の版について「Neither value shows a per-person difference」と、区間が 0 から遠いこと、入れ替えで本人の回が勝つことの関係です。何を「per-person difference」と呼ぶのかが本文で定まっておらず、両者の関係が説明されていません（指摘 1）。
- **b 方法の穴: 3**
  - 漏れ、端の格子、事後の追加、両側の版の合成での未確認は、どれも明示されています。
  - 新しい穴は、入れ替えの対照が「時間の近さ」を交絡と扱っている点です。しかし本文が置いた使う場面（直近の履歴がある書き手）では、時間の近さは使う側にとっての価値そのものです（S1, S2）。交絡として扱うのは「安定した個人差」を主張する場合に限るはずで、そこが区別されていません（指摘 1）。
- **c 持ち帰れるもの: 3**
  - 推奨 (1)（本人の 1 次の連鎖と同じ構造の共有の両方と比べる）は安く、すぐ使えます。費用の目安も入りました。
  - 一方で、決定に効く版の値は事後で、図に無く、結論の推奨にも戻っていません。選びに要る他人のパネルの大きさ（費用の一部）も書かれていません（指摘 2・5・6）。
- **d 簡潔さと構成: 3**
  - 4.4 の分割で読みやすくなりました。
  - ただし要旨（248 語）には「post hoc」が 4 回あり、「fixed base smoothing」「post hoc null」など、定義の無い語が想定読者（HCI・教育工学の学生）に向けて並んでいます。
  - 序論の貢献の段（l.49）は 1 段に 8 文あり、2 つの値・2 つの対照・限界を詰めています。
- **e 規程への適合: 4**
  - 要旨 248 語（上限 250）、キーワード 6 個、"Statements and Declarations" の見出し、Data availability の文はいずれも規程に適合しています。本文の語数・頁の上限は規程に無く、7,745 語は参考の最近の論文の範囲（約 9,800〜13,300 語）より短いです。
  - 要旨は上限まで 2 語しか余裕がなく、様式の移行で数え方が変わる危険があります（指摘 8）。
- **f 先行研究の位置づけ: 4**
  - Aalbers 2023 の引用（l.57「a person-mean baseline beat every general model for 89% of participants, although for 80% at least one personal model beat it」）は原文の「200/224, 89.3%」「180/224, 80.4%」と合います。
  - Saeb 2017 の「which split fits depends on the use case」も原文「the choice of the appropriate CV method depends on the application」と合います。
  - ただし、この使う場面の考え方を、入れ替えの対照の読み（時間の近さ）に当てていません（指摘 1）。

## 3. 指摘の一覧（重い順）

- **[severity: major] 「per-person difference」が定義されず、使う場面の上では時間の近さを交絡と呼ぶ理由が無い**
  - 位置と引用
    - 要旨 l.35「Neither value shows a per-person difference」
    - 4.4 l.284「the swap separates neither differences between writers from closeness in time nor the writer from the amount of data」
    - 3.3 l.139「This simulates a writer whose recent history is available」
    - 考察 l.321「though not necessarily because of stable differences between writers」
  - なぜ問題か
    - 本文が置いた使う場面は「直近の履歴がある書き手の次の回を予測すること」です。そこでは、本人の直近の回が他人の回より効く理由が書き手の安定した違いでも時間の近さでも、設計者の決定（本人のデータを集めて保存するか）にとっての価値は同じです。
    - 交絡になるのは「書き手の間に安定した違いがある」という科学的な主張のときだけです。本文は決定に関わる問いと科学的な問いを区別せず、要旨で両側の版も「per-person difference を示さない」と書いています。
    - 一方で、両側の版の区間は 0 から遠く（[2.7e-3, 6.1e-3]、[2.9e-3, 1.2e-2]）、本人の回は入れ替えに全員で勝っています。
    - 実務家は「両側の版は使う場面では本人の直近のデータの価値として 0.3〜0.5% ある（ただし合成での較正は無い）」と読むはずですが、要旨は「無い」側に読ませます。
    - Saeb 2017「the relationship between the training and the validation set should mimic the relationship between the training set and the dataset expected for the clinical use」。Saeb 2017「if the goal is prognosis, i.e., we want personal models ... we can split the data based on time」。
  - 解消の条件
    - 「per-person difference」を本文で 1 句で定義します（例: 合成で植えた、回をまたいで安定した書き手ごとの遷移の違い）。
    - 両側の版を 2 つの問いに分けて書きます。
      - 決定の問い（使う場面での本人の直近のデータの価値）: 区間は 0 から離れているが、合成の帰無で較正していないので、大きさが平滑だけでどこまで出るかは分からない。
      - 科学的な問い（安定した個人差）: 時間の近さとデータの量を分けていない。
    - 要旨の「Neither value shows a per-person difference」は、「neither was shown to exceed what the same procedure gives without per-person differences」のように、不足しているのが較正であることが分かる言い方に限定します。
  - 自信: 中

- **[severity: minor] 決定に関わる値が事後で、図に無く、結論の推奨に戻っていない**
  - 位置と引用
    - 序論 l.49「The second bears on a designer's decision」
    - 図 2 のキャプション l.230「Medians over the 17 writers of the 15-session panel at the fixed base smoothing」
    - 結論 l.354 の最後の文「so studies should report the symbolization together with the comparison」
  - なぜ問題か
    - 本文自身が決定に関わると言う値（3.4e-3・5.2e-3）は表 3 の 1 列と本文にしか無く、唯一の図は決定に関わらない側（固定の平滑）だけを描いています。
    - 結論は記号化の報告で終わり、使う側が持ち帰る (1)(2) の手順が結論に戻っていません。
    - Aalbers 2023 は結論の段で使う側への含意を述べています（「These findings are relevant for the implementation of algorithms in mobile health apps」）。
  - 解消の条件
    - 図 2(a) に両側の版の中央値（k = 1〜15）を破線で重ねるか、キャプションで表 3 を指します。
    - 結論の最後に、推奨 (1)(2) を 1 文で戻します。
  - 自信: 中

- **[severity: minor] 決定の例（休止の予測）は、休止が主の CS1 では共有の模型が選ばれた結果と並べて書く必要がある**
  - 位置と引用
    - 考察 l.321「A writing assistant that times hints by the predicted probability that the next seconds are a pause」
    - 2.1 l.114「so the CS1 measure is mostly the prediction of pause seconds」
    - 4.3 l.237「In CS1 the shared model itself is chosen for every writer」
  - なぜ問題か
    - 例の用途（休止の確率でヒントの時を決める）に最も近い評価は、休止が 72% を占める CS1 です。そこでは共有の模型が全員で選ばれています。
    - CoAuthor の 3.4e-3 は休止が約 5% のデータの全記号の平均なので、休止の確率の差を表しているとは限りません（著者も「どの記号での差かは測っていない」と認識しています）。
    - また 26 記号の休止の記号は「直前 30 秒に打鍵が無い」なので、「the next seconds are a pause」は、実際は「次の 1 秒で 30 秒以上の休止が続いているか」です。
  - 解消の条件
    - 例に 1 句足します。例:「(in CS1, where most symbols are such pauses, the shared model was chosen)」。
    - 休止の定義を例の中で合わせます（「that the writer has not typed for 30 seconds」など）。
  - 自信: 高

- **[severity: minor] 推奨 (2) の手順の順が、構造の選びとの関係で読めない**
  - 位置と引用
    - l.329「(2) choose structure and shrinkage on other people, with the shared model itself among the candidates, and choose the smoothing on other people for the shared model, apply it ... and choose shrinkage given it (here done post hoc, for one structure ...)」
    - 要旨 l.35「choose structure, shrinkage and, applied to both models, smoothing on other people (post hoc, one structure)」
  - なぜ問題か
    - 本文で行った順は次のとおりです（3.4 l.185）。
      1. 固定の平滑で構造と τ を選ぶ。
      2. その構造の共有に α を選ぶ。
      3. 両側を作り直して、τ だけを選び直す。
    - (2) の文は τ を 2 回選ぶように読め、構造を選び直すかが書かれていません。追う実務家が同じ手順を再現できません。
    - Saeb 2017「The correct way for adjusting these hyperparameters is to further divide the training set ...」のとおり、選びの手順そのものが結果の妥当性を決めます。
  - 解消の条件
    - (2) を、行った順の 3 段（構造と τ → 共有の平滑 → 両側に当てて τ を選び直す。構造は据え置き）で書きます。
    - 要旨は「choose structure and shrinkage, then the shared model's smoothing, on other people」のように順を保ちます。
  - 自信: 高

- **[severity: minor] 費用の目安に、選びに要る他人のパネルが入っていない**
  - 位置と引用
    - l.321「the per-person model here needs about one ($k=5$) to three ($k=15$) hours of a writer's typing and 2,033 stored parameters per writer」
    - 2.1 l.112「the 15-session panel contains the CoAuthor writers with at least 20 sessions (17 writers)」
  - なぜ問題か
    - この手順で τ と α を選ぶには、他人の書き手（ここでは 16 人）の、直近 k 回と取り置きの 5 回が要ります。これは本人のデータとは別の、手順そのものの費用で、決定の段に無いと実務家は導入の可否を見積もれません。
    - Aalbers 2023 は個人化の代償をデータの量で明示しています（「this comes at the cost of strongly reduced sample size」）。
  - 解消の条件
    - 決定の段か推奨に 1 句足します。例:「and the choice used 16 other writers with at least 20 sessions each; how few would suffice was not studied」。
  - 自信: 中

- **[severity: minor] 要旨が想定読者に定義の無い語で書かれている**
  - 位置と引用
    - 要旨 l.35「at the fixed base smoothing」「synthetic writers without per-person differences (post hoc)」「under the post hoc null」
  - なぜ問題か
    - context-A の想定読者（系列モデルとベイズの平滑の訓練を前提にしない HCI・教育工学の読者）にとって、「fixed base smoothing」「null」は要旨の中で定義されていません。
    - 要旨は 248 語で「post hoc」が 4 回あり、決定に関わる値に辿り着くまでが重いです。
  - 解消の条件
    - 「post hoc」を最後に 1 回にまとめます（例:「Analyses marked post hoc were added after seeing results」）。
    - 「null」を「synthetic writers without per-person differences」に統一します。
    - 浮いた語数で「fixed base smoothing」を「the small fixed counts added to all models」のように言い換えます。
  - 自信: 中

- **[severity: nit] 序論の貢献の段が 1 段に詰まりすぎている**
  - 位置と引用: l.49（「Our contribution is a finding ...」から「... were not reliably detected in those synthetic writers.」までの 8 文）
  - なぜ問題か: 1 つの主張にまとめた結果、2 つの値・各々の対照・限界が 1 段に入り、実務家が「何が分かったか」を 1 読で取れません。
  - 解消の条件: 主張（最初の 1 文）と 2 つの値（残りの数）を段で分けるか、限界の文（最後の 2 文）を次の段へ移します。
  - 自信: 低

- **[severity: nit] 要旨の語数の余裕**
  - 位置と引用: context-A「要旨: 248 語（... 規程の上限 250）」
  - なぜ問題か: Springer Nature の様式へ移すと、数式（$5\times10^{-4}$ など）の数え方で上限を超える危険があります。
  - 解消の条件: 移行の後に数え直すか、上の指摘で語を減らします。
  - 自信: 低

## 4. 総合の推奨: minor

- 引き継いだ 9 件のうち 8 件は解消、1 件（推奨 (2) の順）は一部の解消です。今回の書き換えで、数値の新しい矛盾は見つかりませんでした（表・図のデータ・本文を照合）。
- 残る最も大きい穴は、「per-person difference」の定義の欠けです。本文が置いた使う場面では、時間の近さは交絡ではなく価値に当たり得るので、要旨が両側の版を「示さない」と書くと決定の読みを誤らせます。定義と 2 つの問いの区別を 1〜2 文足せば消えます。新しい計算は要りません。
- 持ち帰れるもの（本人の 1 次の連鎖と比べる、両側に同じ平滑を当てる、費用の目安）は残っています。決定の値を図・結論に戻し、休止の例の CS1 との並べ方と、選びに要るパネルの費用を足せば、実務家にとって使える形になります。

## 5. 読めなかった範囲と注入の疑い

- **読んでいないファイル**
  - /Users/johnd/GSE-prototype-paper3/papers/per-person-learning/manuscript/references.bib（参考文献の書誌の照合はしていません）
  - /Users/johnd/GSE-prototype-paper3/papers/per-person-learning/kit/symbols/README.md
- **読んだファイル**
  - 本文: /Users/johnd/GSE-prototype-paper3/papers/per-person-learning/manuscript/main.tex（全文）
  - 作図の値: /Users/johnd/GSE-prototype-paper3/papers/per-person-learning/manuscript/figdata/ の fig2_p15*.csv の 5 本
  - 接地の 2 本（/Users/johnd/GSE-prototype-paper3/.steering/20261107-gse-paper3-per-person-learning/attack-me/manuscript-paper3/round-10/tmp/sources/aalbers.txt・saeb.txt）
  - 依頼文が指す context-A.md・carryover-R2.md
- 補足資料 S1〜S16 は未作成なので読んでいません（既知の未決 1）。
- 注入の疑い: なし（接地の 2 本と対象物に、査読者や LLM に向けた指示の文は見つかりませんでした）。