# 一次資料メモ (2) モデルの更新・昇格の実施手段 / 各モデルの選定理由

> 出典は ADR / docs / コード実測 (2026-09-04)。

## ⚠️ 呼称が 2 段階で変わっている（スライドで最も間違えやすい）

| 時期 | 呼称 | 出典 |
|---|---|---|
| 〜2026-09-01 | `Stage 1〜4`（モデルの複雑さの梯子） | ADR-019:37-38 が旧スライドの実測を引用 |
| 2026-09-02 ADR-019 D1 | `M1〜M4` | ADR-019:100-108 |
| 2026-09-02 ADR-021 D11（**現行**） | **実体名**: 固定 baseline / criterion 直結 / 個人・タスク適応 / 時系列 | ADR-021:400-421 |

`M1〜M4` は **26 週 WBS の `M0〜M5` と記号衝突**したため撤回 (ADR-021:412-415)。
⚠️ **ADR-019 だけ読むと古い呼称を掴む** (ADR-021:420)。順序は名前ではなく昇格ゲートが担う。

## 段の定義 (ADR-019:100-105 + ADR-021:402-407)

| 段 | 何を推定するか | 主な候補 | 出力 |
|---|---|---|---|
| 固定 baseline | 観測パイプラインと時間的 proxy を確立 | ルール + Writing HMM (ADR-001 のまま) | `p_stuck` / friction / engagement / `uncertainty` |
| criterion 直結 | 状態名でなく**観測可能な自力前進の帰結**を予測 | 正則化ロジスティック / 離散時間ハザード / stateless baseline (ADR-009 D3 が「正」) | `self_directed_recovery_risk` の**上下界** |
| 個人・タスク適応 | 個人差・タスク差を吸収 | partial pooling / 階層ロジスティック / domain-local head | 個人・タスク別 risk / `scope_fit` / `evidence_quality` |
| 時系列 | 時間的な競合と系列構造 | 離散時間の競合リスク / 固定構造の状態空間 / **ROCKET 系** | 同上 |

処理層は既存の 7 層 `Layer 0`–`Layer 7` で呼び、段と混ぜない (ADR-019:107-108)。

### 軸を変えた理由 — 負の記録 7 本 (ADR-019:41-50)

| # | 一次 | 内容 |
|---|---|---|
| a | [P227] | PRISMA 42 研究「multimodal models do not present a clear edge over their unimodal counterparts」 |
| b | [P219] | アルゴリズム間 最大 12pt (実用域 SVM↔RF は **3pt**) / モダリティ間 18pt / **評価法 10-fold→LOSO 31pt** |
| c | [P161] | 同一論文内で深層 (TypeNet 転移) AUC 72.1% に対し **RF 77.8% / SVM 74.4%** |
| d | [P223] | N=994「All condition classifications were close to random guessing」/ マウス軌跡 CNN 回帰 **R² −5.22〜−1.10** |
| e | [P224] | N=179 x 14 日 = 10,760 事例。特徴を足すと**帰無モデルより下がった**「overfitting on random noise」 |
| f | [V89] | 71 研究 282 比較。**低バイアス 145 比較で logit(AUC) の差は 0.00** |
| g | [V92] | UCR 112 + 新規 30 で有意に最良は MultiROCKET+Hydra と HIVE-COTEv2 —— **深層は上位に入っていない** |

⚠️ **逆側も同じ基準で探して見つからなかったことを明記している** (ADR-019:51-54)。
「これは存在しないことの証明ではない」(self-supervised pre-training による小標本 HAR は未探索)。

## 昇格ゲートの判定量

### ⚠️★★★ 「Stage N 比 +X%」は外された (ADR-019 D3 / :123-136)

- **効果量の差を昇格の判定量にしない**。代わりに 2 つ:
  1. **subject / session holdout での calibration**（点推定の accuracy でなく**確率が当たっているか**）
  2. **上下界が介入判断を反転させないか**（ADR-009 の反証ゲート G2 と同型）
- 理由: [V95] 逐語「sample sizes … inherently lead to **large error bars, eg ±10% for 100 samples**」
  ＋ 較正スモークは **n=3–5** → 「+3%」「+5%」は**原理的に測れない**。
  [V96]「K-fold CV produces strongly biased performance estimates with small sample sizes,
  and the bias is still evident with sample size of 1000」
- 併記する量: subject / task / session holdout・**Brier score**・calibration・欠測時の挙動・
  baseline との差・介入負担
- ★ **「約 50 セッション」というデータ量の条件は残す**（外すのは +3% という判定量）

未踏技術設計書:320-328 の表がそのまま使える:
| | 内容 |
|---|---|
| データ量 | 約 50 セッション（不変） |
| 判定量 (a) | 被験者およびセッションを分けた holdout での **calibration** |
| 判定量 (b) | 推定の**上下界が介入判断を反転させないこと** |
未達なら **固定 baseline を正とする**（オッカムの剃刀）。

### 有効標本数の単位 (ADR-019 D4 / :138-146)

- **セッション数 × 窓数で標本を数えない。単位は `Decision Episode`**
- 根拠 [V100]「adjacent segments are not statistically independent」。GSE は 30 秒窓を 1Hz で出す
  ＝ **隣接窓の 29/30 が重複**
- 実環境の参照点 [P225]: 7 週で 1 人あたり平均 **26.13 recordings**
- 定義は `docs/architecture/personalization-and-online-learning.md:330-337`

### 潜在状態モデル（時系列段）の採用ゲート (ADR-009 D4 / :169-217)

**両方**満たしたときにだけ stateless baseline を置き換えられる。

(i) **勝ち幅** — held-out（**subject / task / session split の 3 つとも必須。1 つでも欠けたら失格**）
(ii) **退化検出（2026-08-21 に数値を凍結）**

| 条件 | 数値 |
|---|---|
| 状態占有エントロピー | **H(occupancy) ≥ 0.5 · log K** |
| 各状態の最小占有率 | **≥ 5%** |
| seed 間のラベル安定性 | **≥ 5 seed で Hungarian 対応づけ後の一致率 ≥ 0.90** |

⚠️ **勝ち幅の数値は今入れない。「決め方」だけを凍結** (ADR-009:204-208):
逐語「勝ち幅は、P1 で得た `stateless baseline` の held-out 成績の**「fold 間標準偏差」を単位として、
P2 開始前に宣言する**。宣言するのは **P1（baseline のみ）を見た時点**であり、
**候補 A / B の成績は 1 つも見ていない**状態で固定する。**データを見てから幅を緩めることはしない。**」

指標: 離散時間 x 競合事象向けの**時間依存 AUC / Brier**、複数の H での `CIF_rec(H)` の較正。
⚠️ **単一の二値 C-index を主指標にしない —— 旧定式化の遺物**。

### 反証ゲート G1〜G4 (personalization-and-online-learning.md:1169-1180)

| ID | 何を判定するか | 失敗したら |
|---|---|---|
| G1 | 統制タスク実験。低/高摩擦条件が content-free 打鍵で分離できるか | 自然ログで粘る前に**軸そのものを疑う** |
| G2 | ラベルの成立。`left_observation` の**上下界の幅が介入判断を反転させないか** | `self_directed_recovery` は目的変数として使えない |
| G3 | 勝ち幅と退化 (= ADR-009 D4) | stateless baseline のまま。online EM は Phase 4 にも進まない |
| G4 | replay parity | オンライン更新を本番経路に載せない |

⚠️★★★ **G1 は 2026-09-04 時点で `n = 0/3`（1 回も走っていない）**。
これが ADR-009 が Proposed に留まる最大の理由 (ADR-009:5-6, 350)。

### 降格

- ⚠️ **モデル成熟の段について「昇格後に降格する」手続きは一次資料に無い。**
  明文は「**昇格しない / 採用しない**」側だけ。
- **計器の段 T0–T3 には降格先が宣言されている**（別軸・混同注意）—— research-positioning.md:1185-1190:
  T1 / T2 の降格先 = 「`Need` 推定から外し、`evidence_quality` の減衰 ＝ 介入を*抑制*する側にのみ使う」
- 過去の「降格」は**位置づけの降格**: ADR-001（HMM を ontology → Writing head の baseline へ）、
  ADR-009 D1b（旧 X 軸を確証の核 → 比較用 baseline へ。「降格は不可逆な棄却ではない」）、
  ADR-009 D6（online EM を Phase 4 へ）、ADR-019 D5（1D-CNN/TCN を主役から降ろす・恒久否決ではない）。

## 誰が / いつ / どう実施するか

### 誰が
**研究者判断がゲート**。ADR のステータス自体がこの形式 (ADR-019:3 / ADR-006:3, 211-214 /
ADR-009:234-235「今は載せない。採択は P2 開始時。」)。

### いつ (personalization-and-online-learning.md:1221-1230、すべて Phase1 完了・凍結解除後)

| Phase | 内容 | 完了条件 |
|---|---|---|
| G1 | 統制タスク実験（**P1 より前・凍結解除後の最初のタスク**） | 条件が分離できるか |
| P1 | episode 化、`user × task_kind × phase` baseline のみローカル更新。**現行 X を置換せず並走** | ラベルが取れる (**G2**) |
| P2 | stateless baseline を実装。partial pooling。cold-start / past-session / within-session を分離評価 | **G4** |
| P3 | 介入効用と MRT。`no_action/defer/light_nudge` を小さくランダム化 | propensity ログと proximal outcome |
| P4 | 潜在構造の再評価。候補 A/B を採用ゲートへ | **G3** |

★ 唯一の例外（実施済み）: **Tier 0 配線**（`keys`/`bs_keys` の additive 追加のみ）を G1 前に先行実施。
理由「**Tier 0 配線はパイプラインを作らない —— 記録するだけで HMM にも X/Y 合成式にも 1 バイトも流さない**」。

### どう (オフライン学習 → 評価 → デプロイ)

ADR-008 D1 の逐語: **オフライン検証 → model version bump → golden 再生成 (ADR-009)**

`HMM_VERSION` bump の手順 (development-guidelines.md:156-161):
1. `analysis::engine::HMM_VERSION` を SemVer で bump
2. `gse-replay` でゴールデンスナップショットを再生成
3. 差分が**意図通り**であることを `.steering/` に記録
4. **無関係な差分が出たら変更を見直す**

SemVer の定義 (engine.rs:27-58):
- bump 対象: `INITIAL_PROBS` / `INITIAL_AXES_EWMA` / `BACKSPACE_PENALTY_THRESHOLD`、遷移・放出・初期確率、
  `update()` / `update_silence()` の α とヒステリシス α、`features.rs` の `phi` /
  `make_silence_observation` / `calculate_features` の数値挙動、`loop_step.rs` の摩擦フロア
- MAJOR = 既存ログの確率列が大幅に変わる / MINOR = 確率列は動くが同じラベル付け / PATCH = ログ形式のみ
- 追加 MINOR (2026-08-18): **既存ログの確率列は 1 ビットも変わらないが、新しい入力クラスに対して分岐が増える場合**
- 履歴: `0.3.0` Phase1 → `0.4.0` (ADR-006 2b・task_kind→head 配線) → `0.5.0` (2026-08-23・IME 停止をやめた)

**実施の型（抽出と配線を 2 コミットに割る）** —— ADR-006 の実施記録 (:168-186):
| サブフェーズ | HMM_VERSION | ゴールデン |
|---|---|---|
| 2a 抽出（挙動非変更） | `0.3.0` 不変 | 4 本 byte-equal（＋全 10 fixture が対 main で byte-equal） |
| 2b 配線（挙動変更） | `0.3.0` → `0.4.0` | 既存 4 本 byte-equal のまま・新規 1 本を追加して 5 本 |
★ 既存 4 本は「無関係な副作用が無いこと」の証明、**新規 1 本が「意図した差分」を担う**。

**学習状態の pinning (ADR-008 D5 / :98-106)**: replay で pin できることを**設計の必須条件**とする。
`model_version, profile_version, initial_profile_state, update_rule_version, random_seed`。
★ ADR-009 D2 改訂に伴い **期の幅 Δ・baseline hazard の形・person-period 展開の順序**も pin 対象に追加。

### オンライン学習の境界 (ADR-008 D1 / :36-45)

| 層 | オンライン更新 | 方針 |
|---|---|---|
| 瞬間状態 | **必須** | 固定構造上の Bayesian filtering。**構造は動かさない** |
| 個人・タスク基準（正規化） | 採用 | EWMA / robust quantile (P² 系) / decayed counts。O(1) メモリ |
| 個人・タスク**写像係数** | 採用 | 低次元の階層ロジスティック。`δ_user_task` は L2 縮約 |
| 介入の効用 | 採用 | 二値フィードバック＋近接行動アウトカムによる保守的更新 |
| **潜在状態の意味・構造** | **原則固定** | オフライン検証 → version bump → golden 再生成 |
| 特徴表現・大規模モデル | **採用しない** | Deep model / embedding / **online ONNX training は初期スコープ外** |

**D4 (:66-78) —— PreReg-5 との両立基準は「情報の出所」**:
逐語「**評価期間のデータが 1 バイトも推定に入らないなら PreReg-5 と両立する。入るなら破る。**」
| Replay モード | PreReg-5 |
|---|---|
| `cold_start` (global prior のみ) | 両立 |
| `past_session_adapted` (評価開始**前**に凍結した profile を固定) | 両立 |
| `within_session_adaptive` | **破る** → 探索的結果としてのみ報告 |

その他の禁止:
- **D7**: 個人化は「**抑制方向にのみ**」使う。提示形式・文面・強度を個人化して説得力を上げる方向は採らない。
  bandit のアームも `no_action / defer / light_nudge / strong_intervention` に限り、
  **提示バリエーションをアームにしない**。
- **D8**: 個人の癖は 3 種（水準 / 写像 / どの信号が効くか）。**③ には専用の特徴選択機構を作らない**
  （1 人あたりラベル 20〜100 件では確実に過学習）。`λ_user_task` と `δ_user_task` の 2 つに集約。
- **profile をクラウド同期しない**（ローカル保持のみ）。

## 各モデルの選定理由とアーキ

### HMM（固定 baseline）
- ADR-001: HMM を **GSE 全体の ontology でなく「Writing Head の baseline」**に位置づける。**廃棄しない**。
  **HMM の内部挙動・`HMM_VERSION` は変えない**（降格は「位置づけ」と「表示」の話）。
- アーキ: **3 状態 x 26 ビン放出 = 78 ＋ 遷移 9 = 87 パラメータ（全て手書き定数）**。
  ADR-008:22-23 逐語「**現行は学習が一箇所も無い** … ＝**「HMM の形をしたルールベース」**」。
- 資産の理由: 開発初日から動作し他の全モデルの比較基準になる／較正前でも「画面に何も出ない」を避けられる。

### 正則化ロジスティック / 離散時間ハザード（criterion 直結）
- 選定の核: **criterion が主観プローブでなく行動になるので、プローブを 1 件も撃たずに教師信号が生成される**
  (ADR-009:55-58)。「Phase1 で死んだ label supply の構造問題への直接の答え」。
- **二値でなく離散時間 time-to-event にした理由**: [V59] Allison 1982 pp.64-65 逐語
  「the dichotomization of the dependent variable is both **arbitrary and wasteful of information**」。
  ★ **H を事前凍結しても恣意性は消えない**。
- **アーキ (personalization…:611-616)**:
```
η_j(k) = α_j(k) + bias_{j,user,task,phase} + ( w_{j,head} + δ_{j,user_task} ) · context_k
h_j(k) = exp(η_j(k)) / ( 1 + Σ_l exp(η_l(k)) )   j,l ∈ {recovery, externalized, left_observation}
h_stall(k) = 1 / ( 1 + Σ_l exp(η_l(k)) )         ← 参照カテゴリ
S(k)       = Π_{l≤k} ( 1 − Σ_j h_j(l) )
CIF_rec(H) = Σ_{k ≤ H/Δ}  h_recovery(k) · S(k−1)
self_directed_recovery_risk(H) = 1 − CIF_rec(H)
```
  - `α_j(k)` は baseline hazard。**期ごとのダミーにせず** `α_{j0} + α_{j1}·log k` のような低次関数に制約。
  - ★ **推定器は H に依存しない。H は意思決定層が読み出すときに与えるパラメータ**。
    「これが定式化を変えた最大の実利」。
  - 実装上の帰結: **依然として GLM**。sigmoid が softmax (3+1) になっただけで逐次更新は O(d·m), m=3。
    量子化を経由しない（連続値 `context_k` を直接受ける）。

### 競合リスク
- [V61]「ある事象の発生が目的事象の発生を排除するとき、それは打ち切りではなく競合イベント」。
- 3 分類: `externalized`(paste) = 競合イベント / `left_observation` = **競合と真の打ち切りの混合。
  潰さずに両方の極端で上下界を取る** / セッション終了 = 管理的打ち切り。
- ⚠️ **上下界のために推定器を 2 本学習しない**。3 カテゴリ多項モデルを **1 本だけ**学習し、
  読み出し段階で `left_observation` の扱いを切り替える（2 本学習すると係数まで変わる）。
- ⚠️ `self_directed_recovery_risk` は**点推定として測れると主張しない**。測れると主張するのは**上下界**。

### partial pooling / 階層ロジスティック（個人・タスク適応）
★ **今回唯一一貫して正の証拠が出た軸** (ADR-019:83-91)。
| 一次 | 数値 |
|---|---|
| [P221]（⚠️ 査読前） | LOSO ρ 0.078 → 個人化 **0.296** |
| [P228] | LOPO 集約 71%（**SD 19%**「for most of the participants it performs poorly」）→ 個人化 **84%（SD 6%）** |
| [P219] | mental effort 回帰に participant ID を足すと r 0.8221 → **0.9410**。⚠️ ただし working condition 分類では効かない |
| [P231] | 「ensembles of individually-trained models is statistically indistinguishable from group-trained methods」 |

実測動機 (ADR-008:15-18): **個人差は平均水準でなく写像係数に出る**。ICC(1) は概ね 0.05–0.30 と小さい一方、
`keys→Q2` の個人内 C-index は 4 名で 0.60–0.68 に対し **P014 だけ 0.368 と符号が反転**。
→「**個人適応すべきは β（切片）ではなく写像の係数**」。縮約強度は ICC でなく交差検証で選ぶ。

### 状態空間モデル（時系列・候補 A）
- 候補 A =「相互排他な作業モードの状態フィルタ（例 Progressing / Stalled / Externalizing）」。
- ⚠️ **正は stateless baseline**。候補 A は昇格候補にすぎない。
- **なぜ 3 モードを今確定しないか**: 破綻点 1〜4 は解けるが「**破綻点 5（状態数を手で選ぶこと自体）を
  4→3 の向きで繰り返す**」。
- 本質的難所: 教師なしオンライン学習は**クラスタ**を作るが「Stuck」は作らない。online EM を回すと恐らく
  「速く打つ / 遅く打つ / 打っていない」に収束し、**label switching** と **semantic drift** が起きる。

### ROCKET 系（時系列・第一候補）／1D-CNN・TCN を降ろした理由 (ADR-019 D5 / :148-161)
- **決定**: 時系列段の第一候補を **MultiROCKET(+Hydra) / ROCKET 系**
  （**非学習のランダム畳み込み特徴 ＋ 線形分類器**）とする。深層系列モデルは
  **恒久否決ではないが、主役から降ろす**。
- 根拠 4 本:
  1. [V92] UCR 112 + 新規 30 で**有意に最良の 2 手法の一方**
  2. [V91] 逐語「simple linear classifiers using random convolutional kernels achieve
     state-of-the-art accuracy」→ **学習パラメータが実質不要**
  3. したがって [V94]（複雑モデルは >200 EPV でも不安定）と [P231]（時間文脈を伸ばすと
     被験者間分散が有意に増える）の**両方を回避できる**
  4. **分類器が線形のままなので criterion 直結（ロジスティック回帰）と地続き**であり、
     **同一の推定枠組みで D3 のゲートを比較できる**
- ⚠️ **これは文献上の整合性であって、GSE データでの実証ではない**。
- ★ **「MultiROCKET + Hydra は最終段の第一候補であって、次にやることではない」**
  (GSE_proposal.docx.md:107)

### ★ 到達点の目安（期待値を上げないための記録・ADR-019:231-245）
逐語「content-free 打鍵単独の到達点は、**被験者内なら AUC 0.7 台、被験者を跨ぐと chance 付近**である。」
| 標的 | 設計 | 数値 | 一次 |
|---|---|---|---|
| 疲労（断眠） | 単発 / 累積 | AUC 72.1% → 80% | [P161] |
| mind wandering | 10 分統制・LOPO | κ 0.363 / ROC-AUC 0.692 | [P226] |
| stress | 実フィールド 8 週・LOSO | ρ 0.078（個人化 0.296） | [P221]（査読前） |
| stress | 統制 N=977・content-free 打鍵 | ⚠️ **chance を超えず** | [P222] |
| 作業条件 | SWELL・computer 18 特徴単独 | 65.51%（baseline 61.76%） | [P219] |
| 同上 | SWELL・**LOSO** | ⚠️ **58.89%（baseline を下回る）** | [P219] |

⚠️ **Flow / Incubation / Stuck そのものを content-free 打鍵から推定した研究は発見できなかった**。

### 昇格の前に埋めるべき観測空間の穴 (ADR-019 D6 / :163-170)
- **criterion 直結へ進む前に、`features.rs` に語・文境界に基づくリズム特徴を入れる検討を先に置く**。
- 理由 (2026-09-02 実測): `anonymize.rs` は `KeyCategory::SentencePunctuation`
  (`VK_OEM_PERIOD` 0xBE / `VK_OEM_COMMA` 0xBC) を**独立カテゴリとして保持**し doc に
  「収集後は取り返せない」とまで書いてあるのに、`features.rs` の `InputEvent` は
  **`is_backspace` しか持たず**、現行 5 特徴量は**すべて境界非依存**。
  [P226] の κ 0.363 を出したモデルは境界特徴を含む。
- ⚠️ **ADR-019 ではコードを変更しない**（別タスク・別ブランチ）。

## 評価の契約

### GATE ↔ PreReg (SSOT = docs/preregistration-v0.3.md)

| GATE | PreReg | 何を判定するか | 合否 |
|---|---|---|---|
| GATE1 尺度理解 | PreReg-1 | Q1/Q2 の尺度を理解しているか | 8 ビネット中 **6 問以上**が想定象限、被験者の **80% 以上**が通過 |
| GATE2 測定法 | PreReg-2/-3 | ラベルが**供給されるか** | 回答率 **≥80%** / 回答時間中央値 **≤10 秒** / 有効プローブ **≥20 件/人**。**Kill**: 全体 <80% または **2 人以上で <70%** |
| GATE3 モデル | PreReg-4 | **L0（X/Y 二軸）が主観プローブと個人内で順序一致するか** | **Go**: 各人の C-index 中央値 **≥0.65**、全員で **>0.55**。**Kill**: 中央値 ≤0.55 または 2 人以上で ≤0.50 |

⚠️ 現行スモークは GATE1 を延期し GATE2 起点。
⚠️ Phase1 は **verdict = `inconclusive` / GATE3 = `DataInsufficient`** で終了 (ADR-006:170)。
原因は probe 枯渇と P013 の straight-lining。

### C-index
**方向付き順序 C-index**（`|r|≥0.30` は逆相関でも通る穴があるため廃止）。
`calibration_eval.rs:12` 逐語「**0.5=偶然 / 1.0=完全 / <0.5=逆**」。
★ **新軸（criterion 直結）では C-index を主指標にしない**（旧定式化の遺物）。

### HIR / Precision / STALL-recall (intervention_eval.rs)
- **PROTECT = {flow, incubation}** / **STALL = {stuck}** / **ACT = {nudge}** / **HOLD = {none, defer}**
  （⚠️ 2026-09-01 訂正で ACT から `wall` を削除・ADR-015）

| 指標 | 式 | 位置 |
|---|---|---|
| **HIR (有害介入率)** | **ACT∩PROTECT / labeled-ACT** = fp/(fp+tp)。**最重要・安全性指標** | :11, :435-439 |
| Precision | ACT∩STALL / labeled-ACT = tp/(tp+fp)。★ **labeled-ACT 上で HIR + Precision = 1** | :12, :440-444 |
| STALL recall | tp/(tp+fn)（STALL labeled が 0 なら None） | :445-448 |
| Burden | ACT 回数 / セッション分（過介入代理） | glossary.md:194 |

### 層別の評価指標 (personalization…:1156-1167)
| 層 | 指標 |
|---|---|
| 観測 | event capture 率、**dead field 率**、privacy audit |
| 状態推定 | calibration、Brier、state stability、**占有エントロピー / 最小占有率 / seed 間ラベル安定性** |
| 個人適応 | cold-start からの改善、係数の過学習、task transfer、**個人ごとの符号安定性** |
| Recovery | **時間依存 AUC / Brier**、複数 H での `CIF_rec(H)` の較正、`left_observation` の**上下界の幅** |
| 介入 | proximal causal effect、**HIR**、dismiss 率 |
| システム | CPU、メモリ、更新時間、**replay parity** |

### その他の凍結条項 (prereg:78-92)
- **PreReg-6**: 独立した陽性エピソードが **30 件未満**なら Recall の点推定を出さない。
- **PreReg-7 MNAR**: 未回答を「全て高摩擦」「全て低摩擦」と置いた**上下限を併報**。
  無回答率 >20% で注意、**>30% で主分析不成立**。**被験者は除外しない**。
- **PreReg-8 二軸性**: 非対角象限（特にインキュベーション）の出現が **<10%** なら
  「**二軸性は検証不能**」と報告。単軸とも二軸とも結論しない。

## ⚠️★★★ 個人化 —— 「凍結」の実装上の実体

**★ 重要: ランタイムで per-user β を較正・凍結する実装は存在しない。**

| 何 | 実体 | 位置 |
|---|---|---|
| β | **母集団定数のハードコード** | heads/writing.rs:22-37 |
| 正規化関数 | `φ(x, β) = clamp((x−β)/(κ·β), 0, 1)`（コメント名は「個人ベースライン正規化関数」だが β は個人値ではない） | features.rs:60 |
| EWMA | **セッション内の平滑化**。個人プロファイルではない | engine.rs:482, 486-492 |
| 実装されている「凍結」 | **オフライン評価の前向き固定 holdout のみ**。`HOLDOUT_CALIBRATION_SESSIONS = 2`／`prospective_holdout()` | calibration_eval.rs:344-355（契約は :11） |
| 個人化部品 | **`PersonalizationStore` / `OnlineUpdater` / `ContextBuilder` は `src-tauri/src/` に 0 件 = 未実装** | — |

→ ★ スライドで「個人ベースラインを凍結」と書く場合、それは (i) PreReg-5 の評価設計上の契約、
および (ii) オフライン解析での holdout 分割であって、**アプリ実行時に個人 β を学習・凍結する機構ではない**。
⚠️ **「実装済み」と読める書き方をしないこと。**

較正前 / 較正後の契約（現行スライド :96-104 の表がそのまま正）:
| 較正の状態 | 推定 | 介入 | 妥当性の主張 |
|---|---|---|---|
| 較正前（母集団ベースライン） | 動く（固定 baseline はゼロデータで走る） | **強い介入を出さない**（可視化と `defer` の記録に留める） | **しない** |
| 較正後（個人ベースラインを凍結） | 動く | Need × Opportunity に従って発火 | **GATE3 を通った範囲でのみ** |
機構としては新設せず、**`evidence_quality` 低下 → `none` / `defer`** という既存原則がそのまま発火する形。

個人化に付く制約: **抑制方向にのみ使う** (D7) / **人格を推定しない** / **長期プロファイル層は置かない**
(ADR-020 D1。根拠 [V103]「Samples with **many subjects and few time points** are shown to perform
substantially better than samples with few subjects and many time points」→ GSE の設計は
この論文が「悪い方」と名指しした象限そのもの) / **固有名を与えない** (ADR-020 D2 / ADR-019 D7 ——
「認知体力」「作業持続プロファイル」を新設しない。ego depletion は [P199] d=0.04 / [P200] d=0.06 で死亡)。

## ONNX 移行 —— **未実装**（実測）

| 確認 | 結果 |
|---|---|
| `src-tauri/src/` の `onnx` grep | **0 件** |
| `Cargo.toml` の `ort`/`tract`/`onnxruntime`/`candle`/`burn`/`tch` | **0 件** |
| Python 学習スクリプト (train.py / export_onnx.py) | **存在しない** |
| `src-tauri/models/*.onnx` | ディレクトリ自体が無い |

⚠️ 文書が食い違っている:
- `.claude/skills/ml-workflow/SKILL.md:73-124` は「Python 学習 → ONNX 推論」を前提
- ★ `personalization-and-online-learning.md:684-687` 逐語「**深層学習は不要** … **ONNX すら不要**で
  **Rust 内完結**にできる」
- ★ `ADR-008:158-162`「ONNX / PyTorch の常時実行は不要（Rust 内完結）」
- ⚠️ 未踏技術設計書:656 の技術スタック表は「PyTorch → ONNX Runtime | **昇格判定を通った場合のみ**」

→ ★ **現時点の設計の正は「Rust 内完結・ONNX 不要」**。スライドでは
「**未実装。昇格判定を通った場合にのみ検討する経路**」と書く。
軽量性は制約でなく**帰結**: 「『軽いから選んだ』のではなく、**観測空間が小さくラベルが疎なので、
線形・低次元しか正当化できない**」(personalization…:689-692)。

## ⚠️ スライド執筆時の落とし穴（一次資料が明示的に警告）

1. **`Stage` / `M1〜M4` と書かない。実体名で書く** (ADR-021:400-421)。
2. **「段を売りにしない」** (ADR-019:197)。逐語「**データが無いのに段を上げることは、
   この分野で最も再現性を壊す行為である**」。名前を変えた 4 段の再導入は**この説明と正面から衝突**する。
3. **`L1〜L4` という層番号を新設しない** (ADR-019 D2)。既に 3 系統ある。
4. **代償を隠さない**: D3 により「昇格した / しなかった」を**1 つの数字で言えなくなる**。
   D5 は文献上の整合性であって GSE データでの実証ではない。
5. **ROCKET 系は「最終段の第一候補であって、次にやることではない」**。
