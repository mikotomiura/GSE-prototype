# Stage 4 サーヴェイ（2026-09-02・研究者指示「具体的なサーヴェイの後に議論する」）

## 系統 1: 深層系列モデル vs 単純ベースライン（★ 完了）

★ 13 件すべて Crossref raw JSON で DOI 検算済み。**全件が `docs/references.md` に未登録**（grep 0 ヒット）。

### Q1. 深層はこの規模で単純なベースラインに勝つか → ★ **勝つという前提は支持されない**

| 文献 | 逐語の要点 |
|---|---|
| **Christodoulou (2019)** J Clin Epidemiol 110:12-22 | ★★★ **低バイアス 145 比較で logit(AUC) の差は 0.00 [-0.18, 0.18]**。高バイアス 137 比較でのみ ML が +0.34 → ⚠️ **報告された ML 優位はバイアスとほぼ同義**。逐語 *"We found no evidence of superior performance of ML over LR."* ⚠️ ただし**対象 ML に系列深層モデルは含まれない**（tree/RF/ANN/SVM） |
| **Grinsztajn (2022)** NeurIPS 35（★ Datasets & Benchmarks Track・査読済） | ★ 45 データセット × **2 万計算時間**の探索予算を揃えて、逐語 *"tree-based models remain state-of-the-art on medium-sized data (∼10K samples)"* |
| **Middlehurst (2024)** DMKD 38:1958-2031 | ★★★ UCR 112 ＋ 新規 30。**有意に最良は MultiROCKET+Hydra と HIVE-COTEv2** —— ⚠️ **深層は上位に入っていない** |
| **Dempster (2020)** DMKD 34:1454-1495（ROCKET） | ★★★ **Stage 4 への最も直接的な反証**。逐語 *"simple linear classifiers using random convolutional kernels achieve state-of-the-art accuracy"* → ★ **畳み込みの利得はカーネルを学習しなくても取れる**＝深層の学習容量が利得の源泉ではない |

### Q2. どれだけのデータを要するか → ⚠️ **「200–500 セッション」に文献的根拠は無い**

- ★ **直接検算できる learning curve 研究を発見できず。** 周辺証拠はすべて**楽観側**を指す:
  - **van der Ploeg (2014)** BMC Med Res Methodol 14:137 —— 逐語 *"LR ... approximately 20 to 50 events per variable"* に対し
    **SVM/NN/RF は >200 EPV でも不安定**。逐語 *"may need over 10 times as many events per variable"*
  - **Sun (2017)** ICCV pp.843-852 —— 逐語 *"performance ... increases **logarithmically** based on volume of training data"*
    → ★ **200 → 500 は 2.5 倍＝0.4 桁**。対数線形なら**桁を上げないと利得が出ない**
    ⚠️ ただし画像 3 億枚であり、GSE への外挿は正当化できない
- ⚠️★★★ **Varoquaux (2018)** NeuroImage 180:68-77 —— 逐語 **"sample sizes ... inherently lead to large error bars, eg ±10% for 100 samples.
  The standard error across folds strongly underestimates them."**
  → ★★★ **GSE の昇格ゲート「Stage 3 比 +5%」は、この標本規模では測定できない**（★ 較正スモークは prereg で **n=3–5**）
- **Vabalas (2019)** PLOS ONE 14:e0224365 —— 逐語 **"K-fold CV produces strongly biased performance estimates with small sample sizes,
  and the bias is still evident with sample size of 1000."** ★ nested CV / train-test split なら不偏

### Q3. 行動・生理センシングでの汎化失敗 → ★ **強い**（⚠️ ただし領域が 1 段ずれる）

| 文献 | 逐語の要点 |
|---|---|
| ⚠️★★★ **Hammerla & Plötz (2015)** UbiComp '15 pp.1041-1051 | ★★★ **GSE に構造的に直撃する唯一の論文**。逐語 *"adjacent segments are not statistically independent"* / *"a significant drop in performance ... if this bias is removed"* → ★ **GSE は 30 秒窓を 1Hz で出す＝隣接窓は 29/30 が重複**。「500 セッション × 数千窓 ＝ 数十万サンプル」という数え方が成立しない。★ **これは類推ではなくデータ構造の議論** ⚠️ **DOI 訂正: 広く引かれる `10.1145/2750858.2805940` は Crossref で 404。正しくは `10.1145/2750858.2807551`** |
| **Hefron (2018)** Sensors 18:1339 | ★★★ Stage 4 の中核前提を直撃。逐語 *"While increasing temporal sequence length improves mean accuracy, it is not sufficient to overcome distributional dissimilarities between individuals' EEG data, as it results in statistically significant increases in cross-participant variance."* → ★ **時間文脈を伸ばしても被験者間分散はむしろ増える**。★ 併せて *"ensembles of individually-trained models is statistically indistinguishable from group-trained methods"*（★ ADR-008 の個人化路線と整合） |
| **Bühler (2025)** Int J AI in Education 35:823-857 | ★★★ **GSE と最も近い課題設定**（content-free 行動から注意状態を連続推定・LSTM/BiLSTM）。**within F1 0.44–0.459 (AUC-PR 0.39–0.40) → lab→wild 転移で F1 0.352 (AUC-PR 0.26)** ⚠️ **著者自身は肯定的に書いている**（*"comparably to the state-of-the-art"*） |
| **Saeb (2017)** GigaScience 6:1-9 | 逐語 *"record-wise CV often massively overestimates"* / **該当文献のほぼ半数が record-wise を使用** ⚠️ 深層を対象にしていない（CV 手続きの問題） |
| 参考 **D'Mello & Kory (2015)** ACM Comput Surv 47(3) | ★ **自然データでは多モーダルの利得が 1/3 に縮む**（acted 12.7% → natural **4.59%**）。GSE は自然作業データ |

### Q4. ★ 逆側の証拠（★ 公平のため同じ基準で探した） → ⚠️ **弱い**

- ⚠️★★★ **「深層系列モデルが小標本の行動時系列で *単純ベースラインに* 明確に勝った」査読済み一次証拠は発見できず。**
- **Ismail Fawaz (2020) InceptionTime** DMKD 34:1936-1962 —— ⚠️ **"on par"（HIVE-COTE と同等）であって上回るではない**。
  ★ かつ比較相手 HIVE-COTE は単純ベースラインではなく、⚠️ **Middlehurst (2024) で順位が下がっている**
- ★ **Ordóñez & Roggen (2016)** Sensors 16:115 —— ★★★ **GSE に有利な唯一の実証**。
  **本文より**（PMC4732148 全文 XML）: 逐語 *"recordings of **four subjects**"* / *"about **6 hours** of recordings in total"* /
  評価は **session-wise hold-out（テスト被験者は訓練にも登場）**
  → ★ **「被験者は少ないがセッションは多い」という GSE の形に protocol が一致する**
  ⚠️ ただし比較相手は *"competing deep non-recurrent networks"* ＝ **深層同士**であり、
  **ROCKET / GBDT / ロジスティック回帰と一度も比較していない**。⚠️ subject-wise 汎化の証拠には一切ならない

### ★ 天井の問題（★ repo の既存 SSOT と整合）

★ 同じ帯域の報告が **5 本目**になった:
`[P117]` precision **0.57**（base rate ≈0.5）/ `[V86]` AUC **0.62** / `[V84]` F1 が無作為基線 **+15%** /
`[V83]` 逐語 *"We cannot replicate models that significantly improve over the baseline of a majority classifier."* /
★ **＋ Bühler (2025) within F1 0.44 / 転移 0.352**
→ ⚠️★★★ **天井が偶然のすぐ上にある領域で「Stage 3 比 +5%」を積む余地があるという証拠は 1 本も無い。**

### ★ 文献が最も強く支持する置き換え先

> **Stage 4 を「1D-CNN / TCN」から「MultiROCKET(+Hydra) / ROCKET 系の非学習ランダム畳み込み特徴 ＋ 線形分類器」へ**

- Middlehurst (2024) で **有意に最良の 2 手法の一方**
- Dempster (2020) で **学習パラメータが実質不要** → ★ Q2 の data hungriness と Q3 の被験者間分散の**両方を回避**
- ★ **分類器が線形のまま**なので **Stage 2（L2 ロジスティック回帰）と地続き**＝同一の推定枠組みで昇格ゲートを比較できる
- ⚠️ **これは文献上の整合性であって GSE データでの実証ではない。**
  ★ 「データが無い以上 Stage 1 が正」という現在の判断**自体は文献と一致している**。

### ⚠️ 検証者自身が申告した限界

1. ⚠️★★★ **Q4 の探索が不十分**（クエリ 6 本程度）。★ **self-supervised pre-training / transfer learning による小標本 HAR
   （Haresamudram 系など）は未探索** → ★ **Stage 4 を最終決定する前に、この方向を独立に 1 ラウンド回すべき**
2. ⚠️ Q2 の 4 本は**すべて単位が GSE と違う**（EPV / 画像枚数 / 脳画像スキャン / シミュレーション）。
   ★ **「方向」の証拠であって「量」の証拠ではない**
3. ⚠️★★★ **キーストローク動態からの認知状態推定で LOSO / セッション間崩壊を示した査読済み一次証拠は発見できず**
   （★ 本系統と §9.1 の検証者が**独立にこの空白を報告**した）
4. ⚠️ abstract の取得元が Crossref 直だったのは Hefron のみ。
   ★ **Hammerla / Killourhy / Zeng は OpenAlex の inverted index 再構成**であり、**逐語性が 1 段弱い**

---

## 系統 2: 長期プロファイル層（★ 完了）

★ 全件 Crossref raw JSON で検算。★ **Etkin (2016) は既登録の [P77]**（ADR-017 D10 根拠 2 が既に逐語引用している）。他は未登録。

### Q1. 個人内の縦断データの方法論と必要規模 → ⚠️ **GSE の規模は検討範囲の外**

| 文献 | 逐語の要点 |
|---|---|
| ⚠️★★★ **Schultzberg & Muthén (2018)** SEM 25(4):495-515 | ★ 「何人 × 何時点」を正面から扱った基準論文。逐語 *"Samples with **many subjects and few time points** are shown to perform **substantially better** than samples with **few subjects and many time points**."* → ⚠️★★★ **GSE の設計（被験者数名 × 1 人数十セッション）は、この論文が「悪い方」と名指しした象限そのもの**。★ 二次（Fang & Wang 本文より）: *"N = 100 with T = 50 or N = 200 with T = 25 are needed"* ⚠️ **本文未到達（有料・PMC 非収載）＝二次引用である** |
| **McNeish (2019)** SEM 26(6):948-966 | ★ GSE に最も近い人数域（N = 10〜50）を扱った唯一の論文。本文より逐語 *"random effect variances with diffuse priors and small samples exhibit large positive relative bias, especially with **N < 30**. At **N = 40**, ... relative biases exceeding 1.10."* / 複雑モデルでは **N = 100 でも問題が残った** ⚠️ **検討した最小が N = 10。GSE の数名は範囲外** ★ ただし結論は条件付き肯定 —— **壊すのは小 N ではなく既定の diffuse prior** |
| ★★★ **Mansueto (2023)** Psychological Methods 28(5):1052-1068 | ★ N-of-1（1 人ずつ推定）路線に「何時点要るか」を直接答える唯一の一次証拠。逐語 *"sensitivity is low with sample sizes feasible for clinical practice (**75 and 100 time points**)"* / *"with 75 and 100 observations, it is advisable to **reduce the number of nodes to around six variables**"* / ⚠️ *"Estimating **temporal** networks appears particularly challenging"* → ★ 設計メモの 5 量は**まさに時間方向の関係**であり、最も推定しにくいクラス |
| **Asparouhov (2018)** SEM 25(3):359-388 | DSEM の枠組み原典。⚠️ abstract の *"any number of observations across time"* は**枠組みが定義できるという意味であり、任意の N・T で推定が正しいという意味ではない**（★ 同じ著者陣が同年に Schultzberg を出して N/T を別途調べていることが裏づけ）→ ⚠️ **この一文を「数十セッションでもよい」の根拠に使ってはならない** |

### Q2. 人物特性への取り違え → ★ **確立している。ただし引き方を誤ると弱くなる**

- **Molenaar (2004)** Measurement 2(4):201-218 —— ★ 「個人間データから個人内の法則は導けない」の原典（古典的エルゴード定理）。
  ⚠️★★★ **逆向きにも効く** —— **GSE が数名分のプロファイルを束ねて「傾向」を語ることも、同じ定理で禁止される。**
- **Fisher (2018)** PNAS 115(27):E6106-E6115 —— 6 標本・各 87〜94 名（★ **1 人あたり約 90 時点**）。
  逐語 *"the variance around the expected value was **two to four times larger within individuals than within groups**"*
  ⚠️★★★ **同誌で 2 本の Letter による批判を受けている**:
  - **Hamaker & Ryan (2019)** PNAS 116(14):6544-6545（★ **Letter**）—— 逐語 *"this comparison is **fundamentally flawed**, because the two variances they compare are designed to represent inherently different phenomena"*
  - **Adolf & Fried (2019)** PNAS 116(14):6540-6541（★ **Letter**）—— ★ 表題そのものが *"**Ergodicity is sufficient but not necessary** for group-to-individual generalizability"*
  - ★ Fisher らの reply は *"it may be fair to argue that comparisons between idiographic and nomothetic data structures offer limited value"* と**部分的に譲歩**
  → ⚠️★★★ **「非エルゴードだから群→個人は不可」という強い形で引いてはならない。**
- ★★★ **Steyer (2015)** Annu Rev Clin Psychol 11:71-98（LST-R）—— ★ **これが GSE に効く安全な定式化**。
  逐語 *"they are always made using a specific method of observations"* / *"**states and traits are method specific**"*
  → ★★★ **GSE の観測は単一方法（PC 上の content-free 行動）に固定されている＝定義上、出力は state であって trait ではない。**
  ⚠️ **ただし宣言では足りない。method-specific であることを *モデルに書き込まないと* trait として読まれる。**

### Q3. 行動センシングでの長期プロファイルの先行例 → ⚠️★★★ **GSE と同じ設定の先行例は存在しない**

| 文献 | 逐語の要点 |
|---|---|
| ⚠️★★★ **Xu (2022) GLOBEM** IMWUT 6(4):1-34 | ★★★ **最も重い。500 名超 / 2 機関 / 2 年 / 4 institute-year データセット。** 先行 9 アルゴリズムを忠実に再実装 ＋ domain generalization 手法 8 個。逐語 *"Our experiment reveals the **lack of model generalizability** of these methods"* / *"these methods also do not generalize well ..., with **barely any advantage over the naive baseline of guessing the majority**"* ⚠️★★★ **原因の診断が GSE に最も不利** —— 逐語 *"**individual differences** (both within and between populations) **may play the most important role** in the cross-dataset generalization challenge"* → ★ 「個人差を長期プロファイルとして明示的にモデル化すればよい」という発想は、この論文では **検証されていない救済案**であって実証された解決ではない。著者らの最良手法でも *"the overall advantage is **incremental**"* |
| **Wang (2014) StudentLife** UbiComp '14 pp.3-14 | 48 名 × 10 週。⚠️ 出しているのは**群レベルの相関と学期のライフサイクル**であって、**個人ごとのプロファイル層ではない** |
| **Kiang (2021)** Sci Rep 11:15408 | 211 名 / 6 研究 / **29,500 人日**。逐語 *"non-collection **increased by 0.5% to 0.9% per week**"*、加速度計では属性による差もあり → ★★★ **脱落しがちな被験者ほど「持続しない人」に見える**＝**人物評価への最短経路** ⚠️ **著者ら自身は楽観的な結論を書いている**（*"demonstrate the **feasibility**"*）→ ★ 「欠測は深刻」の根拠に引くのは**著者の結論と逆向き**であり、そう明記しないと誤引用になる |
| ★★★ **Fang & Wang (2024)** SEM 31(5):891-908 | ★ 欠測込みで「何人 × 何時点」を唯一直接に答える。本文より逐語 *"**N = 100 generally was not enough** to provide accurate inference about between-person variations"* / *"As N increased to **200**, relative biases decreased substantially"* / *"estimating between-person variances ... usually **demands more on N than T**"* ⚠️ **検討した最小の N が 100** |
| 参考 **Hamaker (2018)** Multivar Behav Res 53(6):820-841 | ★ DSEM の実適用が想定する規模の基準点 —— 逐語 *"two samples of **over 100 individuals each** who were measured for **about 100 days**"* |

### Q4. 本人に返すことの帰結 → ★ **強い（ただし全部が類推）**

- ★★★ **Turnwald (2019)** Nat Hum Behav 3:48-56 —— ★ 「系が返したラベルがラベル通りの結果を作る」の最強の因果証拠。
  **無作為割付**（実験1 N=116 / 実験2 N=107）で、告げるリスクを**実際の遺伝型と独立に割り付けた**。
  逐語 *"Merely receiving genetic risk information changed individuals' cardiorespiratory physiology, perceived exertion and running endurance ... **in a self-fulfilling manner**"* /
  *"Effects of perceived genetic risk on outcomes were **sometimes greater than the effects associated with actual genetic risk**."*
  → ⚠️★★★ **プロファイルが自分自身の予言を実現し、GSE はそれを「予測が当たった」と読む**（＝交絡）
- ★★★ **Kluger & DeNisi (1996)** Psychol Bull 119(2):254-284 —— **607 効果量 / 23,663 観測**。
  逐語 *"FIs improved performance on average (d = .41) but that **over 1/3 of the FIs decreased performance**"* /
  ★★★ *"FI effectiveness **decreases as attention moves up the hierarchy closer to the self and away from the task**"*
  → ★★★ **人物プロファイルの提示は、定義上、注意を自己へ向ける操作である。**
- ★★★ **Etkin (2016)** = **既登録 [P77]** —— ★ 「返す」以前に「測る」こと自体の害。6 実験。
  逐語 *"measurement can **decrease continued engagement** in the activity and subjective well-being.
  **Even in the absence of explicit external incentives**, measurement itself can thus have similar effects."*
  → ⚠️★★★ **「Nudge を出さなければ安全」ではない。**
- **Jussim & Harber (2005)** Pers Soc Psychol Rev 9(2):131-155 —— ★ **擁護側でもある**（自己成就は *"typically small"* / *"may be more likely to dissipate than accumulate"*）。
  ⚠️ ただし**二重に不利**: (1) *"powerful self-fulfilling prophecies may **selectively occur among students from stigmatized social groups**"*
  ＝ **害は平均では小さいが不利な立場の人に集中し、数名では検出できない**。
  (2) ★★★ *"teacher expectations may predict student outcomes **more because these expectations are accurate than because they are self-fulfilling**"*
  → ★★★ **「予測が当たった」ことは自己成就の否定にならない。RCT でしか分離できない。**

---

## ★★★ 結論（系統 2）

### 成立する範囲

★ **各被験者に閉じた、個人内の記述と個人内予測**としてなら成立しうる（他者データを 1 バイトも使わないので Molenaar / Fisher を回避できる）。
⚠️ ただし **Mansueto が上限を切る**: **75〜100 時点でなお sensitivity 不足・変数は約 6 個まで・時間方向がとりわけ難しい**。

⚠️★★★ **設計メモの 5 量のうち 1 つは、この時点で落ちる**:

| 量 | 1 時点の数え方 | 判定 |
|---|---|---|
| 摩擦が高まり始めるまでの傾向 | セッション内の事象 | ★ 桁は足りうる |
| 摩擦が高まった後に自力で前進へ戻るまでの傾向 | 同上 | ★ 桁は足りうる |
| 短い中断の後に作業へ再接続できる傾向 | 同上 | ★ 桁は足りうる |
| 高摩擦状態で外部出力へ依存せずに前進する傾向 | 同上 | ★ 桁は足りうる |
| ⚠️★★★ **同じ負荷に対するセッション間の変動** | ★ **1 セッション = 1 時点** → **T = 数十** | ⚠️★★★ **Mansueto の 75〜100 に届かない。文献上、推定できると言えない** |

### 成立しない範囲（★ 明確に）

1. ⚠️★★★ **個人間の差を含む定式化**（多水準 VAR / DSEM の random effects / cohort 横断の判定）。
   逐語の下限は **N = 10（McNeish の最小）/ N = 100 が「不十分」（Fang & Wang）/ N = 100×T=50 または N = 200×T=25（二次）**。
   ★ **GSE の被験者数名は、いずれの検討範囲にも入っていない。**
2. ⚠️★★★ **「この被験者は他の被験者と比べて〜な傾向」という形の出力は、規模の点で文献上まったく支持されない。**
   ★ **数名分のプロファイルを束ねて集団的傾向を語ることも同様**（Molenaar の定理は両方向に効く）。
3. ⚠️ **外部妥当性の主張**（他コホート・他年度・他被験者への一般化）—— GLOBEM が 500 名超 × 2 年で失敗している。

> ★★★ **要するに**: 「**各被験者に閉じた個人内の記述**」なら置ける。「**人を比較する層**」としては置けない。
> ⚠️★★★ 設計メモの文言（「個人内の時系列的な作業状態の変化として分析する」）は正しい方向を向いているが、
> **正しさは文言でなく、「個人間パラメータを一切推定しない」という実装上の制約でしか担保できない。**

### ★ 置くなら方法論上どうしても要るもの（6 件）

1. ★★★ **個人間パラメータを推定しない、という構造的な禁止**（★ 宣言でなく実装で）。
   ★ 既存の `cohort.rs` 系の横断判定とプロファイル層の間に、**越えられない境界**を置く。
2. ★★★ **method-specific であることをモデルに書き込む**（Steyer LST-R）。★ 出力に観測方法を型として付随させ、
   **方法をまたいだ解釈を型で禁じる**。
3. ★★★ **不確実性を必ず伴わせ、事前分布を明示的に制限する**（McNeish: **壊すのは小 N ではなく既定の diffuse prior**）。
   ★ **事後区間を必須フィールドにし、区間が広いときはプロファイルを出さない（`none` を返す）** ← ★ ADR-010 の abstention と同じ形。
4. ★★★ **欠測を第一級の量として扱う**（Kiang: 週 0.5〜0.9% ずつ増え、属性にも依存）。
   ⚠️ **脱落しがちな被験者ほど「持続しない人」に見える** —— ★ 欠測率・時間パターンを共変量として記録し、**MNAR 仮定の感度分析を事前登録**する。
5. ★★★ **本人への提示を既定で行わない。行うなら人物述語を出力語彙から外す。**
   ★ 「あなたは〜な人」ではなく**日時付きの事象列**として返し、**返す/返さないを無作為化して害を測る**
   （★ Jussim & Harber の (d) により、**予測の当たりは自己成就の否定にならない**＝ RCT でしか分離できない）。
6. ★★★ **測定それ自体の害を測る対照群** —— ⚠️ **「Nudge を出さない群」は「測定していない群」ではない**（[P77]）。
   ★ **測定のみの群を置かないと、プロファイル層の害は原理的に検出できない。**

### ⚠️ 検証者自身が申告した限界

1. ⚠️★★★ **最も弱いのは Q3** —— GSE と同じ設定（PC 上の content-free 行動から個人の縦断プロファイル）の先行例は**発見できず**。
   ★ **支持する先行例も、直接反証する先行例も、文献上まだ存在しない**（＝置くなら GSE 自身が先行例を作る立場になる）。
2. ⚠️ **次に弱いのが Q4** —— 「作業状態の長期プロファイルを本人に返した無作為化試験」は**発見できず**。全部が類推。
3. ⚠️ **Q1 の Schultzberg & Muthén の N/T 数値は二次引用**（★ 本文未到達）。★ 文書に書くなら二次性を明記するか原本を入手する。

---

## 系統 3: 打鍵 ML の到達点（★ 追補のみ到着・本体は再送依頼中）

★ **統合版が再送で到着し、本体が揃った。**（★ 旧注記: 追補だけが先に届いていた） 検証者が参照する「先の報告」（到達点の表の本体 / モデル複雑化の証拠 (a)〜(d) /
Koldijk・Naegelin・Freihaut 4 連続 null・Bixler & D'Mello・Vizer・Kuvar 42 研究レビューの各エントリ）は**未着**。
★ 統合版を再送依頼済み。⚠️ **未着分を推測で埋めないこと。**

### ★★★ 最重要の追加: Banholzer (2021) は独立再解析で予測に転化しなかった

**Freihaut & Göritz (2024)** `10.1109/TAFFC.2024.3357733`
（★ **本文を一次取得** —— Augsburg OPUS の OA PDF・13 ページ・pypdf 抽出。⚠️ **abstract には無い記述**）:

> 本文逐語（Discussion）:
> *"Note that Banholzer and colleagues [26] drew a more positive conclusion from their longitudinal study data,
> which showed a significant relationship between everyday mouse usage and self-reported stress. However, although
> the authors suggested that their results indicate that the mouse could be used to predict the stress level of
> computer users, **they did not specifically test such a prediction in their analysis. We bridged this gap by
> reanalyzing their data [54], which failed to provide reliable stress prediction on new data** (see Supplement 6).
> Thus, the results of both studies might be more similar than their diverging interpretations suggest."*

⚠️★★★ **訂正**: **Banholzer (2021)** `10.2196/27121`（N=70・7 週・1 人 26 recordings・stress と speed-accuracy trade-off の関連 mean −0.32）は、
★ **規模の参照点としては引けるが、「マウス/打鍵から stress が読める根拠」としては引けない。**

### ★★★ モデル複雑化が性能を「下げた」という一次記述

同じ Discussion 節の本文逐語:

> *"the incremental explanatory power across all non-null models over the null model was minimal, indicating a
> practically negligible correlation between mouse usage and affect. The machine learning results underscore this
> observation. **The inclusion of mouse usage features in the ML models did not enhance affect prediction, but
> decreased prediction performance as compared to the null model. This decrease is likely due to overfitting on
> random noise arising from the inclusion of additional, non-informative input features.**"*

> *"**Promising results from laboratory settings do not necessarily translate into real-life settings.**"*

★ **N=179 × 14 日 × 10,760 instances** —— ⚠️ **GSE より大きなデータでの結果である。**

→ ★★★ **GSE の勾配ブースティング / 1D-CNN / TCN ロードマップは、この領域では
「上がる証拠が無い」ではなく「*下がった記録がある*」段階に置くのが正確。**

### ★★★ 盲検独立評価では state 検出が実質ゼロ

**D'Mello (2023)** `10.1109/MIS.2022.3221854` *IEEE Intelligent Systems* 38(1):76-84
（★ **本文を NSF PAR の PDF から一次取得**。Crossref の abstract は null）:

- IARPA MOSAIC。★ **参加者の 20–40% の ground truth を盲検化**。本文逐語
  *"Teams could use any modeling approach but could only rely on automatically sensed information...
  These criteria, along with the blinding, were established to assess generalizability to new (unseen) participants."*
  / *"**all code and data were independently verified by the testing and evaluation team.**"*
- Tesserae = **757 名・1 年** / TILES = **212 名・10 週**。目標は trait r ≥ 0.5 / state R² ≥ 0.25
- ★★★ 本文逐語: *"**neither team met the program metrics** for either trait (r of 0.5) or state (R² of 0.25) affect
  detection... **state detection accuracies were essentially zero** with the exception of stress, where automated
  methods explained **1%–3% of the variance** in self-reported daily stress."*
- 集計: Tesserae は 14 traits で mean r = 0.14 (SD 0.12)、17 states で **mean R² = 1% (SD 3%)**。
  TILES は r = .10 (SD .17)、**R² = 1% (SD 4%)**
- ★ 導入部の対比: *"Literature surveys suggest impressive accuracies, such as **78%–97%** for stress detection"*
- ⚠️★★★ **重大な限界（★ 検証者が本文で確認した）**: **MOSAIC のセンサに打鍵もマウスも含まれていない**
  （Tesserae = Garmin + 通信メタデータ + Bluetooth ビーコン + Facebook / TILES = Fitbit + OMSignal シャツ + 音声トラッカー + Bluetooth + SNS）
  → ★ **「打鍵の証拠」としては引けない。「実環境の受動行動センシング全般への批判」として引く。**
  ★ それでも「**文献の 78–97% と、盲検独立評価の R² 1–3%**」という落差は GSE の評価設計に直接効く。

### ★★ 外部データで検証した研究がほぼ皆無

**Vos (2023)** `10.1016/j.ijmedinf.2023.105026` *Int J Med Inform* 173:105026（★ 本文は arXiv:2209.15137 全文より）:

> *"**In virtually all the reviewed studies the number of subjects were less than 30. None of these studies apart
> from Mishra et al. [41] and Liapis et al. [47], tested generalization of the resulting models on a totally unseen,
> new dataset**, to further validate the reported accuracy achieved"*
> *"**No definitive improvement in reported accuracy rates were noted when using LOSO cross-validation compared to
> K-fold cross-validation**"*

⚠️ wearable が対象で打鍵/マウスではない（隣接領域）。
★ 2 つ目の引用は逆説的に重要 —— **「LOSO にしても数字が落ちない論文群」自体が疑わしい**という指摘。

### ★★ record-wise 分割による過大評価の一次数値

**Saeb (2017)** `10.1093/gigascience/gix019`（★ 系統 1 とも重複）—— **本文数値**:
HAR 実験で record-wise CV 誤差は *"started at a value of 2%"* に対し subject-wise は 27% から始まり 9% まで。
文献調査 62 本のうち *"**28 used record-wise while 34 used subject-wise CV… for subject-wise CV papers, the median
classification error was 13.00%, more than twice that of record-wise CV papers, which was 5.60% (P < 0.01)**"*

⚠️ **訂正**: 一部で流通している「**record-wise で 0.99**」という数字は**この論文に存在しない**。
★ **反論も併記すべき**: **Little (2017)** `10.1093/gigascience/gix020` —— 差の一部は identity leakage ではなく
**異質データへの underfitting** だと主張。

### 補助

- **Kapoor (2023)** `10.1016/j.patter.2023.100804` *Patterns* 4(9):100804 —— *"**17 fields** where leakage has been
  found, collectively affecting **294 papers**"*
- **Xu (2022) GLOBEM** `10.1145/3569485` —— ★ 系統 2 と同一。先行 depression 検出を 4 データセットで再評価し
  **Δ = 18.9 ± 9.7%** の性能低下、最良モデルでも **ROC AUC 54.1% vs majority baseline 50.0%**
- ⚠️ どちらも**打鍵ではない隣接領域**

### ★ 個人化 vs LOSO の差が打鍵で直接出ている

**Ghosh (2017) TapSense** `10.1145/3098279.3098564` MobileHCI '17 pp.1-12
（★ Crossref の abstract は null → **abstract 未取得**。本文数値は公開 PDF より）:

- ★ **content を使わない**（typing characteristics = 打鍵特性）。22 名・3 週間・4 情動状態
- **個人化モデル**: *"average AUCROC of close to **84% (standard deviation 6%)**"*
- ★ **打鍵特徴のみの個人化モデル: 71% (SD 11%)**
- ⚠️ **集約モデル・leave-one-participant-out**: *"we attain an average AUCROC of **71% (standard deviation 19%)**…
  **for most of the participants it performs poorly**, resulting in such high standard deviation"*
- ⚠️ **手法推進側の論文であり批判論文ではない。** それでも **SD 19%** が「平均 71%」の内実を露呈している
  （★ 著者自身が「多くの被験者では機能していない」と書いている）。⚠️ スマホのタッチ入力であり PC 物理キーボードではない

### ★ 検証者が「採らなかった / 条件付きにした」もの（★ 引かないこと）

| 文献 | 理由 |
|---|---|
| **Maalej & Kallel (2020)** `10.1109/IE49459.2020.9155004` | ★ キーストローク×情動の唯一の正式 SLR だが、⚠️ **risk-of-bias appraisal をしていない**。abstract のみ取得。批判論文としては弱い |
| **Yang & Qin (2021)** IEEE Access | ⚠️ **全文未取得**。★ **未見のまま批判の根拠に引かないこと** |
| **Kołakowska (2013)** / **Alberdi (2016)** | ⚠️ **abstract も全文も取得できず** → ★ **引用しない** |
| preprint 群（arXiv:2508.02417 / arXiv:2505.18175） | ⚠️ 査読前。参考にとどめる |
| 「Pepa mouse stress」 | ⚠️ **存在が確認できなかった** |

### ★★★ GSE が自分で埋められる空白（★ ポジショニング上の資産）

1. ⚠️★★★ **キーストローク／マウスによる情動・認知状態検出について、
   PRISMA + QUADAS 相当の正式なリスク評価を伴う系統的レビューは存在しない。**
2. ⚠️★★★ **打鍵に特化した cross-dataset failure 研究も発見できず**
   —— ★ cross-dataset の証拠は生理・EEG・音声・モバイルセンシング側にあり、
   **打鍵側は「null 結果」と「再解析失敗」という形をとっている**。
3. ★ **GSE が `gse-replay` の byte-equal 回帰と被験者横断評価を最初から持っていることは、この空白に対する資産である。**

### ⚠️ 検証者自身が申告した裏付けの弱さ（順位が更新された）

- ⚠️ **Q1 が最も弱い** —— **Flow / Incubation / Stuck を直接扱った研究を発見できず**。
  Bixler & D'Mello (2013) は**本文入手不能で二次情報が矛盾**、Vizer (2009) は**出版社が abstract を伏せている**、
  Kuvar の「タイミングのみ κ=0.018–0.050」は**本系統では未検証**（★ 確実なのは headline κ=0.363 自体が content-free であること）
- ★ **Q2 は大幅に強化された** —— Koldijk の LOSO 崩壊 ＋ Naegelin のラボ→フィールド崩壊 ＋ Freihaut 4 連続 null
  ＋ **Banholzer の再解析失敗** ＋ **MOSAIC の盲検 R² 1–3%** ＋ Kuvar の 42 研究レビュー
- ★ **Q3 は中程度** —— ⚠️ ただし **Banholzer は「規模の参照点」としてのみ使い、「陽性所見」としては使わない**

### ★ 統合版の本体（★ 再送で到着）

#### Q1. content-free 打鍵単独の到達点 → ★ **上限は AUC 0.72–0.80 / κ 0.36 / F1 0.63。すべて被験者内か統制条件下**

| 標的 | 設計 | 数値 | 出典 |
|---|---|---|---|
| **疲労**（★ 断眠という極端な対比） | 単発 150 キー / 5 分 / 4 セッション累積 | **AUC 72.1% / RF 77.8% / SVM 74.4% / 累積 80%**、F1 49.1–72.2% | **Acien (2022)** JMIR Biomed Eng 7(2):e41003 |
| **mind wandering** | 10 分統制チャット・**LOPO** | **κ 0.363** / ROC-AUC **0.692** / F1 0.508 / MCC 0.372 | **Kuvar (2022)** UMUAI 33(3):617-641 |
| **stress** | 模擬オフィス N=90・**10-fold CV** | mouse+keyboard GBM **F1 0.625** / 0.631 / 0.775 | **Naegelin (2023)** J Biomed Inform 139:104299 |
| **stress** | ★ **実フィールド 8 週 N=36・LOSO** | ⚠️★★★ **Spearman ρ 0.078**（時系列 0.096）／個人化 **0.188 → 0.296** | **Naegelin (2025)** ⚠️ **medRxiv preprint・査読前** |
| **stress** | 統制・**N=977**・content-free 打鍵 | ⚠️★★★ **chance を超えず / R² > 0 に届かず**。11 特徴中 1 つのみ有意（**d=0.18**） | **Freihaut & Göritz (2021)** Z Psychol 229(4):245-250 |
| **作業条件** | SWELL・**computer 18 特徴単独**・10-fold | **65.51%**（majority baseline **61.76%**）＝ ★ **+3.75 ポイントのみ** | **Koldijk (2018)** IEEE TAFFC 9(2):227-239 |
| 同上 | SWELL・4 モダリティ・**LOSO** | ⚠️★★★ **58.89%** ← ★ **baseline 61.76% を下回る** | 同上 |
| **mental effort**（回帰） | SWELL・10-fold → **LOSO** | ⚠️★★★ **r 0.8221 → 0.0343**（baseline r = −0.0703） | 同上 |
| **情動 4 状態**（スマホ打鍵） | 個人化 / **LOPO 集約** | **71% (SD 11%)** / 71% だが **SD 19%** | **Ghosh (2017)** MobileHCI '17 |
| 参考: 情動（wearable） | ★ **盲検独立評価** | state **R² 1–3%** / trait mean r 0.14 | **D'Mello (2023)** ⚠️ 打鍵は非対象 |

★ **de Jong (2020)**（既登録 [P218]・N=22・6 週）は ⚠️ **分類器を作っていない**。AUC も精度も存在せず、群平均の時刻・曜日効果のみ
（効果量は **2 時間で 11.6 ms**・backspace は **8.6% vs 8.4%**）。
⚠️★★★ **かつ逐語 "we excluded interkey intervals that were longer than 5 seconds"** ＝ ★ **GSE が特徴量として拾いたい「沈黙」を、この研究は捨てている。**
⚠️ abstract 末尾の *"office workers are able to **recover** from work-related demands"* は**限定資源型の枠組み**なので、★ **GSE はこの解釈を引き継がない。**

⚠️★★★ **Flow / Incubation / Stuck そのものを content-free 打鍵から推定した研究は発見できず。**
★ 最も近い **Bixler & D'Mello (2013)** IUI 2013 pp.225-234 は ⚠️ **本文入手不能で二次情報が矛盾**
（87% / 82% / 56.3% / κ 0.612 が並立）→ ⚠️ **引かないこと。**
⚠️ **Vizer (2009)** は **content（linguistic 特徴）を使う**ので転用不可。★ かつ後続論文が publication bias を名指ししている ——
逐語 *"Vizer et al. (2009) additionally let participants write standardized texts but **only published the results about the free text writing**."*
⚠️★★★ **`.idea` §9.1 検証で報告された「Kuvar のタイミングのみ特徴群は κ=0.018–0.050」は、本系統では検証できなかった**
（出版版本文が入手不能）。★ **確実なのは headline κ=0.363 自体が content-free だということ。**
→ ⚠️ **2 つの系統で食い違っているので、出版版 UMUAI 33(3):617-641 の本文入手が要る。**

#### Q2. 再現性・外的妥当性 → ★★★ **一貫して弱い**

- ★★★ **Koldijk (2018)**: **10-fold 90.03% → LOSO 58.89%**（★ **31 ポイント崩壊**、majority baseline 61.76% を下回る）。
  mental effort 回帰は **r 0.8221 → 0.0343**。被験者間 SD 11.64 ポイント、最悪 37.5%。
  著者逐語 *"**Computer interactions and physiology, however, showed no gains**, which was unexpected given the presented related work"* /
  *"**Predicting the mental effort of an unseen user is thus difficult.**"*
- ★★★ **Naegelin 2023 → 2025**: **同一グループ**が模擬オフィス 10-fold で F1 0.63 → **実フィールド 8 週 LOSO で ρ 0.078**。
  ★ **GSE の設計（実作業・数週間・PC 入力・自己申告ラベル）にほぼ完全に一致する条件**。
  ⚠️ **訂正**: web 検索が伝える「person-dependent 78% / LOSO 46%」という数値は **Crossref raw の abstract に存在しない**。
- ★★★ **Freihaut & Göritz の 4 連続 null**（★ 規模も設計も変えて出なかった）:

  | # | 誌 | 対象 | N | 結果 |
  |---|---|---|---|---|
  | 1 | Int J Hum-Comput Stud 145:102520 (2021) | マウス | 53・ラボ | *"failed to find clear differences"* |
  | 2 | Behav Res Methods 53(6):2281-2301 (2021) | マウス | **994**・フィールド | *"did not reveal a clear and systematic relationship"* |
  | 3 | Z Psychol 229(4):245-250 (2021) | **打鍵** | **977** | ★ **ML 分類は chance 超えず・回帰は R² > 0 に届かず** |
  | 4 | IEEE TAFFC 15(3):1490-1501 (2024) | マウス | **179 × 14 日 / 10,760 instances** | *"weak and sporadic ... at best"* ＋ **null model より性能低下** ＋ **Banholzer の再解析失敗** |

- ★★ **Kuvar (2023) ICMI** pp.163-173（**PRISMA・42 研究**）: 逐語 *"models built on **gaze** typically outperform other modalities"* /
  ★★★ *"**multimodal models do not present a clear edge over their unimodal counterparts**"* / 障壁は **generalizability**。
  ⚠️ **メタ分析の pooled 推定はしていない**（モダリティ間の相対比較のみ）。
- ⚠️ **Alfalahi (2022)** Sci Rep 12:7690（**41 研究・25 研究をメタ分析・QUADAS-2**）は **pooled sensitivity 0.86 / specificity 0.83** だが、
  ⚠️★★★ **標的は fine motor decline（運動機能低下）の診断であって認知状態ではない**。**PD 患者 3,791 名 vs 健常者の群間判別**であり、
  GSE の「同一人物の中で今 Flow か Stuck か」という群内問題とは別。★ **I² が 79–88% と極めて高い。**
  → ⚠️★★★ **この 0.86 / 0.83 を GSE の根拠に転用してはならない。**

#### ★★★ Q2 の核心 — モデル複雑化の証拠 (a)〜(e)

| # | 証拠 |
|---|---|
| **(a)** | ★ **系統的レビューが否定** —— Kuvar (2023) 逐語 *"multimodal models do not present a clear edge over their unimodal counterparts"* |
| **(b)** | ★★★ **アルゴリズムの差より評価法の差が約 3 倍大きい**（Koldijk の内部比較）—— アルゴリズム間の幅 **最大 12 ポイント**（実用域の SVM↔RF は **3 ポイント**）/ モダリティ間 **18 ポイント** / ★ **評価法（10-fold → LOSO）31 ポイント** |
| **(c)** | ★ **DNN が古典手法を明確に上回っていない** —— Acien (2022) の深層ネット（TypeNet 転移）が AUC 72.1%、★ **同一論文内の RF 77.8% / SVM 74.4%** で、**5 分条件では RF の方が高い** |
| **(d)** | ★★ **CNN / RNN を試して chance 相当** —— Freihaut & Göritz (2021, N=994) 本文逐語 *"**All condition classifications were close to random guessing** (a maximum accuracy of 59% is not reliable for stress detection)"*。回帰は全 R² が **−0.12〜0.00**、⚠️★★★ **マウス軌跡を画像化した CNN 回帰は R² −5.22〜−1.10**（＝ **平均値予測より大幅に悪い**） |
| **(e)** | ★★★ Freihaut & Göritz (2024) 本文逐語 —— **特徴を足すと null model より性能が下がった**（*"overfitting on random noise"*）。**N=179 × 14 日 × 10,760 instances** |

★ **一方、個人化には一貫した証拠がある**（★ 複雑化とは別軸）:
Naegelin 2025 で **ρ 0.078 → 0.296**（約 4 倍・⚠️preprint）/ Ghosh 2017 で **LOPO 71%(SD19%) → 個人化 84%(SD6%)** /
Koldijk 2018 で mental effort 回帰に participant ID を足すと **r 0.8221 → 0.9410**
（⚠️ ただし **working condition 分類では ID は効かない** —— ★ **課題によって効き方が逆転する**）。

#### Q3. 実環境の収集規模と離脱率

| 研究 | 信号 | 募集 → 解析 | 期間 | 量 | **離脱・欠測** |
|---|---|---|---|---|---|
| **Smeaton (2021)** LNCS/MMM pp.183-195 | PC 打鍵 timing | 4 → 4 | ★ **6 か月超** | 記載なし | ⚠️ **報告なし** |
| **Zulueta (2018)** JMIR 20(7):e241 | スマホ打鍵 metadata | ⚠️ **19 → 9** | 8 週 | 626,641 keystrokes | ⚠️★★★ **53% 脱落**。全 16 名の平均参加 **4.69 週 (SD 3.05)** |
| **Banholzer (2021)** JMIR 23(4):e27121 | PC マウス | 71 → 70 | **7 週** | 2029 → **1829** / ★ **1 人平均 26.13 (SD 14.33)** | recording 単位で **14.6% 除外** |
| **Acien (2022)** の nQCS | PC 打鍵 timing | 251 | ★ **9 か月** | 約 1,000 セッション | ⚠️ **報告なし** |
| **Huang (2025)** PLOS Digit Health 4(7):e0000883 | スマホ受動＋能動 | 48 完了 | **18 か月** | passive 25,029 日 / survey 10,448 回 | ★★★ **受動 89% vs 能動アンケート 47%** / 完走 81% |
| **Matcham (2022)** BMC Psychiatry 22:136 | スマホ＋wearable | 623 | 11–24 か月 | — | ⚠️★★★ **全データ種で 50% 以上あるのは 623 名中 110 名 = 17.7%**（参加率は 79.8%） |

★ **判定**: GSE の想定（数名 × 数十セッション × 数か月）には**前例がある**（Smeaton N=4 × 6 か月・査読通過 / Banholzer 1 人 26 recordings × 7 週）。
⚠️ ただし **解析に載る人数は募集の 5〜8 割に落ち**、★★★ **自己申告ラベルの回収率は受動データの約半分**（Huang 89% vs 47%）
→ ★★★ **律速はセンサではなくラベルである。**
⚠️ **Banholzer の「7 週で 1 人 26 セッション」から見て、GSE の「1 人あたり数十セッション」は数週間ではなく数か月を要する。**
⚠️ **PC デスクトップ打鍵の長期研究は 2 件のみで、どちらも離脱率を報告していない。**
★ **PC 特有の離脱要因（常駐アプリの停止・OS 更新・業務 PC への導入拒否）を報告した研究は発見できず。**
⚠️ Huang（受動 89% / 能動 47%）と Matcham（*"comparable levels of data availability in active and passive"*）は**食い違う**
→ ★ **GSE は自分のコホートで実測するしかない。**

---

## ★★★ 実装に直接効く発見（★ メインが一次検算した）

> 検証者の指摘: **Kuvar の κ 0.363 を出したモデルは "message features"（語・文・メッセージの境界に基づくリズム特徴）を含み、
> それは GSE の匿名化下でそのまま計算できる。**

★ **メインによる実測（2026-09-02）**:

| 確認先 | 結果 |
|---|---|
| `src-tauri/src/analysis/anonymize.rs` | ★ **`KeyCategory` に `SentencePunctuation`（0xBE / 0xBC）が独立して存在する。** doc コメント逐語: 「`personalization-and-online-learning.md §5.2` は **boundary keys を『採用 (弁別の前提条件)』に格上げ**しており ([P121] N=475・2 独立文脈)、その接地は散文の階層 **語内 < 語間 < 文間 < 段落間**」「`Punctuation` へ一括で畳むと **『文間』の段だけが失われる**」「⚠️ **収集後は取り返せない**」 |
| `src-tauri/src/analysis/features.rs` | ⚠️★★★ **`InputEvent` は `is_backspace` しか持たない。文・語境界の特徴は 1 つも無い。** （★ `sentence|word_|space` の 16 ヒットは**全部 `backspace` の部分一致**だった） |
| 現行 5 特徴量 | `f1_flight_time_median` / `f3_correction_rate` / `f4_burst_length` / `f5_pause_count` / `f6_pause_after_del_rate` ★ **すべて境界非依存** |

→ ★★★ **記録側は境界キーを保持していて、推論側がそれを使っていない。**
★ **[P121] は既に「弁別の前提条件」として採用と判定されており、`anonymize.rs` は「収集後は取り返せない」と書いてまで残している。**
→ ★★★ **モデルを複雑にするより先に、ここを埋める方が証拠に沿っている。**
⚠️ **ただしこれはコード変更であり、本タスクのスコープ外**（★ 別タスク・別ブランチ）。
