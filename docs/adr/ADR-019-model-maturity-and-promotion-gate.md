# ADR-019: ML の段を「モデルの複雑さ」から「推定対象と根拠」へ改め、昇格ゲートを効果量差から置き換える

- **ステータス**: **Accepted**（2026-09-02・研究者判断）
- **日付**: 2026-09-02
- **関連**: **ADR-001**（HMM を Writing baseline へ降格）/ **ADR-006**（`task_kind` → head）/
  **ADR-008 D1 / D4**（オンライン学習の境界・PreReg-5 との両立基準）/
  **ADR-009 D2 / D3**（`self_directed_recovery_risk`・競合リスク・stateless baseline を正とする）/
  **ADR-010 D1**（`scope_fit` / `evidence_quality` / abstention）/ **ADR-011 §5** / **ADR-012**（superset の決め方）
- **作業記録**: `.steering/20260902-gse-design-deepening/`
- **入力**: `.idea/20260901-smartphone-state-externalization-and-physical-return.md` §11–15
  （⚠️ **追跡外＝ SSOT ではない**。本 ADR が裁く）
- **一次証拠**: [P219]–[P233] / [V89]–[V102]（★ 全件 Crossref raw JSON で検算済み）
- **コード変更**: **ゼロ**（★ 本 ADR は段の定義と昇格ゲートだけを動かす。D6 の実装は別タスク）

---

## Context

### 1. `.idea` §14 の「改善案」7 件のうち 6 件は既に決まっていた

2026-09-02 に `.idea` §12–15 を既存 ADR と逐条照合した（`.steering/20260902-gse-design-deepening/conflict-audit.md`）。

| `.idea` §14.4 | 既決か | 出所 |
|---|---|---|
| ① 時間スケールの分離 | **一部既決** | `Decision Episode`（`personalization-and-online-learning.md §3.1` / ADR-008 D2）。★ `profile` のみ新規 |
| ② recovery を競合リスクに | **既決** | **ADR-009 D2**（`recovery` / `externalized` / `left_observation` / `still_stalled` の 4 カテゴリが逐語一致・2026-08-01） |
| ③ 不確実性と観測可能性を分ける | **既決** | **ADR-010 D1**（`uncertainty`＝ambiguity / `evidence_quality`＝novelty） |
| ④ 観測特徴と推論特徴の分離 | **既決** | **ADR-008 D1** ＋ **ADR-012**（限界寄与 ≥ δ かつ null 超過） |
| ⑤ 予測・介入・長期評価の学習分離 | **既決** | **ADR-008 D1 / D4** |
| ⑥ abstention を出力契約に | **既決** | **ADR-010 D1**（conformal outlier testing [V66] に接地） |
| ⑦ 評価指標を accuracy 中心から変える | **部分既決** | ADR-009 の反証ゲート G2 等。⚠️ **calibration / Brier / 時間依存 AUC の明示は薄い** |

→ ★ **新規に裁くべきは ⑦ と、段そのものの定義である。**（★ ① の `profile` は **ADR-020** で別に裁く）

### 2. ⚠️★★★ 旧 4 段が乗る「複雑さ」の軸には、負の記録がある

`docs/mitou_submission/mitou_pptx/…設計スライド.pptx.md` の現行 Stage 表は
**1 = ルール＋HMM / 2 = ロジスティック回帰 / 3 = 勾配ブースティング / 4 = 1D-CNN・TCN** であり、
段の軸は **モデルの複雑さ**である。2026-09-02 のサーヴェイは、この軸に**負の記録**を見つけた。

| # | 一次 | 内容 |
|---|---|---|
| (a) | [P227] | **PRISMA・42 研究**。逐語 *"**multimodal models do not present a clear edge over their unimodal counterparts**"* |
| (b) | [P219] | ★★★ **アルゴリズムの差より評価法の差が約 3 倍大きい** —— アルゴリズム間の幅 最大 12 ポイント（実用域の SVM↔RF は **3 ポイント**）/ モダリティ間 18 ポイント / **評価法（10-fold → LOSO）31 ポイント** |
| (c) | [P161] | **同一論文内で深層ネット（TypeNet 転移）AUC 72.1% に対し RF 77.8% / SVM 74.4%**。★ 5 分条件では **RF の方が高い** |
| (d) | [P223] | **N=994**。逐語 *"**All condition classifications were close to random guessing**"*。回帰は全 R² が −0.12〜0.00、⚠️★★★ **マウス軌跡を画像化した CNN 回帰は R² −5.22〜−1.10**（＝ 平均値予測より大幅に悪い） |
| (e) | [P224] | ★★★ **N=179 × 14 日 × 10,760 instances**。逐語 *"The inclusion of mouse usage features in the ML models **did not enhance affect prediction, but decreased prediction performance as compared to the null model.** This decrease is likely due to **overfitting on random noise**"* |
| (f) | [V89] | 71 研究 / 282 比較。**低バイアス 145 比較で logit(AUC) の差は 0.00**。高バイアス側でのみ ML が +0.34 |
| (g) | [V92] | UCR 112 ＋ 新規 30 で **有意に最良は MultiROCKET+Hydra と HIVE-COTEv2** —— ⚠️ **深層は上位に入っていない** |

⚠️ **公平のため逆側も同じ基準で探した。** 得られたのは [V93]（InceptionTime = HIVE-COTE と **"on par"**。★ かつ [V92] で順位が下がっている）と
[P238]（**深層同士の比較**で +4%）の 2 種のみで、
★ **「深層系列モデルが小標本の行動時系列で *単純ベースラインに* 明確に勝った」査読済み一次証拠は発見できなかった。**
⚠️ **これは「存在しない」ことの証明ではない** —— 探索は限定的で、self-supervised pre-training による小標本 HAR は未探索である。

### 3. ⚠️★★★ 昇格ゲートの「+X%」は、この標本規模では測れない

- [V95] 逐語: *"sample sizes ... inherently lead to **large error bars, eg ±10% for 100 samples.
  The standard error across folds strongly underestimates them.**"*
- ★ `docs/preregistration-v0.3.md` の較正スモークは **n=3–5**。
- → ★★★ **「Stage 1 比 +3%」「Stage 3 比 +5%」は誤差棒の中に完全に埋まる。**
- ★ 併せて [V96]: *"**K-fold CV produces strongly biased performance estimates with small sample sizes,
  and the bias is still evident with sample size of 1000.**"*

### 4. ⚠️★★★ 有効標本数の数え方が、GSE のデータ構造で成立しない

[V100] 逐語: *"**adjacent segments are not statistically independent**"* /
*"a **significant drop in performance** ... **if this bias is removed**"* /
*"**prolonged, repetitive activities are particularly affected**"*。

★ GSE は **30 秒ローリングウィンドウを 1Hz で出す**（`docs/agent-shared.md` アーキテクチャ要約）
＝ **隣接窓は 29/30 が重複している**。→ ★★★ **「N セッション × 数千窓 ＝ 数十万サンプル」という数え方は成立しない。**

### 5. ★ 記録側は境界キーを保持していて、推論側が使っていない（2026-09-02 実測）

| 確認先 | 実測 |
|---|---|
| `src-tauri/src/analysis/anonymize.rs` | ★ `KeyCategory::SentencePunctuation`（`VK_OEM_PERIOD` 0xBE / `VK_OEM_COMMA` 0xBC）が**独立カテゴリとして存在する**。doc コメント逐語:「`personalization-and-online-learning.md §5.2` は **boundary keys を『採用 (弁別の前提条件)』に格上げ**しており ([P121] N=475・2 独立文脈)」「`Punctuation` へ一括で畳むと **『文間』の段だけが失われる**」「⚠️ **収集後は取り返せない**」 |
| `src-tauri/src/analysis/features.rs` | ⚠️★★★ `InputEvent` は **`is_backspace` しか持たない**。現行 5 特徴量（`f1_flight_time_median` / `f3_correction_rate` / `f4_burst_length` / `f5_pause_count` / `f6_pause_after_del_rate`）は**すべて境界非依存** |

★ そして [P226]（**content-free 打鍵で κ 0.363**）の主要特徴は **語・文・メッセージの境界**に基づく。

### 6. ★ 個人化には一貫した正の証拠がある（★ 複雑化とは別軸）

| 一次 | 数値 |
|---|---|
| [P221]（⚠️ **査読前**） | LOSO ρ **0.078** → 個人化 **0.296** |
| [P228] | LOPO 集約 71%（**SD 19%**・*"for most of the participants it performs poorly"*）→ 個人化 **84%（SD 6%）** |
| [P219] | mental effort 回帰に participant ID を足すと r **0.8221 → 0.9410**。⚠️ **ただし working condition 分類では効かない**（★ **課題によって効き方が逆転する**） |
| [P231] | *"**ensembles of individually-trained models is statistically indistinguishable from group-trained methods**"* |

---

## Decision

### D1. ★★★ 段の軸を「モデルの複雑さ」から「**何をどの根拠で推定できるか**」へ改める

`.idea` §14.5 / §15.3 の再定義を**採る**。

| 段 | 役割 | 主なモデル候補 | 出力 |
|---|---|---|---|
| **M1 固定 baseline** | 観測パイプラインと時間的 proxy を確立する | 現行ルール ＋ Writing HMM（**ADR-001** のまま） | `p_stuck` / friction / engagement / `uncertainty` |
| **M2 criterion 直結** | 状態名ではなく**観測可能な自力前進の帰結**を予測する | 正則化ロジスティック / **離散時間ハザード** / stateless baseline（**ADR-009 D3 が「正」と定めたもの**） | `self_directed_recovery_risk` の**上下界**（**ADR-009 D2 の主張範囲**） |
| **M3 個人・タスク適応** | 個人差とタスク差を吸収する | partial pooling / 階層ロジスティック / domain-local head（**ADR-002 / ADR-006**） | 個人・タスク別 risk / `uncertainty` / `scope_fit` / `evidence_quality`（**ADR-010**） |
| **M4 時系列モデル** | 時間的な競合と系列構造を扱う | 離散時間の競合リスク／固定構造の状態空間／**ROCKET 系**（→ **D5**） | 同上 |

⚠️★★★ **「Stage」と呼ばない。** ★ 呼称は **M1〜M4**（モデル成熟）に限定し、
**処理は既存の 7 層 `Layer 0`–`Layer 7`（`docs/architecture/gse-v2-overview.md` §2）で呼ぶ。**

### D2. ★★★ `.idea` §15 の `L1〜L4` を**採らない**

⚠️ repo には **既に L1/L2 を別の意味で使う層番号が 3 系統ある**（2026-09-02 実測）:

| # | 体系 | L1 / L2 の意味 |
|---|---|---|
| ① | **7 層アーキテクチャ `[0]`–`[7]`**（`gse-v2-overview.md §2`。`domain-adapter-boundary.md` / `intervention-decision-engine.md` / `personalization-and-online-learning.md` / ADR-009 が全部この番号で書かれている） | L1 = Domain Event Adapter / L2 = Privacy Boundary + Event Envelope |
| ② | **`docs/glossary.md`** 逐語「`p_stuck` は **MhD（L1）が計算する**」「**Need 層（L2）**が `stuck_likelihood` として閾値消費する」 | L1 = MhD 全体 / L2 = Need 層 |
| ③ | **表現層の「層 0–3」**（`glossary.md` に 18 箇所 / `expression-channel.md` に 9 箇所） | 層 0 = 状態に応答しない常在の基層 |

★ かつ `.idea` の **L1〜L3 は既存 Layer 1–4 の別名にすぎず、新規性は L4 だけ**である（L4 は **ADR-020** で裁く）。
→ ★★★ **番号を新設すると 4 系統目になり、`docs/` 全体で `L2` が 3 通りの意味を持つ。採らない。**

### D3. ★★★ 昇格ゲートから「**Stage N 比 +X%**」を外す

- **決定**: **効果量の差を昇格の判定量にしない。** 代わりに次の 2 つを置く。
  1. ★ **subject / session holdout での calibration**（★ 点推定の accuracy ではなく、**確率が当たっているか**）
  2. ★ **上下界が介入判断を反転させないか** —— **ADR-009 の反証ゲート G2 と同型**
     （`personalization-and-online-learning.md §3.4 / §8.2`）
- **理由**: [V95]（**n=100 で ±10%・fold 間標準誤差は過小評価**）＋ 較正スモークが **n=3–5**
  → ★★★ **「+3%」「+5%」は原理的に測れない。**
- ★ **併せて併記する量**: subject / task / session holdout・Brier score・calibration・欠測時の挙動・
  baseline との差・介入負担（`.idea` §14.4 ⑦）。
- ⚠️★★★ **これは `docs/glossary.md` の MhD 項と未踏提出資料が書いている
  「約 50 セッション ＋ Stage 1 比 +3% の Go/No-Go」を改訂する。**
  ★ **「約 50 セッション」という *データ量* の条件は残す**（★ 外すのは **+3%** という *判定量* である）。
- ⚠️ **`docs/preregistration-v0.3.md` は凍結文書であり書き換えない。** ★ ずれは本 ADR に記録として残す。

### D4. ★★★ 有効標本数の単位を `Decision Episode` に固定する

- **決定**: 昇格判定・検出力の議論で、**セッション数 × 窓数で標本を数えない。**
  ★ 単位は **`Decision Episode`**（`personalization-and-online-learning.md §3.1` の既存概念。
  読み出し粒度は `task-adaptation-and-scope-gating.md §3.4` 逐語「**推定は streaming・読み出しは Decision Episode**」）。
- **理由**: [V100]（**隣接する重複セグメントは統計的に独立でない**／バイアスを除くと**有意に性能が落ちる**）。
  ★ GSE の 30 秒窓 1Hz は **29/30 が重複**する。
- ★ **実環境の参照点**: [P225] は **7 週で 1 人あたり平均 26.13 recordings**。
  → ⚠️ **GSE の「1 人あたり数十セッション」は、数週間ではなく数か月を要する。**

### D5. ★★ M4 の候補から **1D-CNN / TCN を主役から降ろし、ROCKET 系を第一候補にする**

- **決定**: M4 の第一候補を **MultiROCKET(+Hydra) / ROCKET 系**（**非学習のランダム畳み込み特徴 ＋ 線形分類器**）とする。
  ★ 深層系列モデル（TCN / GRU）は**恒久否決ではないが、主役から降ろす**。
- **根拠 4 本**:
  1. [V92] —— UCR 112 ＋ 新規 30 で **有意に最良の 2 手法の一方**。
  2. [V91] 逐語 *"**simple linear classifiers using random convolutional kernels achieve state-of-the-art accuracy**"*
     → ★ **学習パラメータが実質不要。**
  3. ★ したがって [V94]（**複雑モデルは >200 EPV でも不安定**）と
     [P231]（**時間文脈を伸ばすと被験者間分散が有意に増える**）の**両方を回避できる**。
  4. ★ **分類器が線形のままなので M2（L2 ロジスティック回帰）と地続き**であり、
     **同一の推定枠組みで D3 のゲートを比較できる。**
- ⚠️★★★ **これは文献上の整合性であって、GSE データでの実証ではない。**
  ★ **「データが無い以上 M1 が正」という現在の判断自体は文献と一致している**（オッカムの剃刀の規約は不変）。

### D6. ★★★ 段を上げる前に、**観測空間の穴を埋める**（★ 語・文境界のリズム特徴）

- **決定**: **M2 以降へ進む前に、`features.rs` に語・文境界に基づくリズム特徴を入れる検討を先に置く。**
- **理由**: Context-5 のとおり **記録側（`anonymize.rs`）は境界キーを「収集後は取り返せない」と書いてまで保持しているのに、
  推論側（`features.rs`）が使っていない**。★ [P121] は既に **「弁別の前提条件」として採用**と判定済みであり、
  [P226] の **κ 0.363 を出したモデルはその境界特徴を含む**。
- ⚠️ **本 ADR ではコードを変更しない**（★ 別タスク・別ブランチ）。
  ★ ADR-012 の手続き（**限界寄与 ≥ δ かつ null 超過**）に従って採否を決めること。

### D7. ★★★ 「**認知体力**」という語を新設しない

- **決定**: `.idea` §11.3 の「認知体力」を、**表示にも内部構成概念にも置かない。**
- **理由 3 本**:
  1. ⚠️★★★ **「体力」は貯蔵量メタファ**（減る・尽きる・回復する）であり、
     `docs/glossary.md` 禁止用語表が明示的に禁じた「**消耗 / 回復 / リソースの補充**」と**同じ枠組みの語**である。
     ★ 限定資源モデル（ego depletion）は死亡が確認済み（[P199] d=0.04 / [P200] d=0.06 / [P201] b=0.003）、
     **ART は限定資源モデルそのもので事前登録された検定 5 本すべて null**（[P193]–[P197]）。
     → ★ **2026-09-01 に落としたばかりの枠組みへの逆戻りになる。**
  2. ⚠️ `.idea` が提案する代替語「**負荷応答と回復のプロファイル**」は、**それ自体が禁止語「回復」を含む**。
     ★ glossary の例外は既存指標名（`自力回復率` / `productive_manual_recovery_rate` / `打鍵再開`）**だけ**である。
  3. ⚠️ **`.idea` 自身が語の危険を自認している** —— §15.5 逐語
     「介入に反応しなかった人を『**認知体力が低い**』と誤って学習しない」。
- ★ **実測**: 2026-09-02 時点で `認知体力` は `docs/` / `.claude/` / `src-tauri/src` / `src` に **1 件も存在しない**
  （＝ 取り除くコストがゼロ）。
- ★ **長期の量が要るときは、既存の行動指標の時系列として扱い、固有名を与えない**
  （`self_recovery_without_paste` / `paste_after_stuck_rate` / `manual_contribution_ratio`）。→ **ADR-020**。

---

## Alternatives

| 却下案 | 却下理由 |
|---|---|
| ★ **旧 4 段（複雑さの梯子）をそのまま維持する** | ⚠️ Context-2 の (a)–(g)。★ 特に [P224] は **特徴を足すと null model を下回った**という一次記述であり、「上がる証拠が無い」ではなく **「下がった記録がある」** |
| ★ **`.idea` の新 4 段を「Stage 1〜4」として提出資料に出す** | ⚠️★★★ **未踏スライドは「Stage 3/4 を主目標から外した理由」に 1 枚を割いている**（逐語「**データが無いのに段を上げることは、この分野で最も再現性を壊す行為である**」）。★ 名前を変えた 4 段の再導入は、**この説明と正面から衝突し、審査側に後退と読まれる**。→ ★ **D1 で呼称を M に限定し、段を売りにしない** |
| ★ **`L1〜L4` を既存 Layer 0–7 と併存させる** | ⚠️ **`L2` が 3 通りの意味を持ち、docs の可読性が落ちる**（D2） |
| ★ **既存 7 層を `L1〜L4` へ全面改番する** | ⚠️ **確定済み ADR（001–018）の本文に触れる**ことになり、本リポジトリの規約（改名は追補と用語表で受ける・ADR-012 / ADR-018 D7 の先例）に反する |
| ★ **昇格ゲートの「+X%」を残したまま n を増やす** | ★ **原理的には正しい**（[V95] の著者もそう言っている）。⚠️ ただし **n=3–5 の較正スモークは prereg で凍結されており、本 ADR では動かせない**。→ ★ **恒久否決ではない。n が増えたら再検討可** |
| ★ **M4 に TCN / GRU を第一候補として残す** | ⚠️ [V92]（**2024 年時点で深層は上位に入っていない**）＋ [V91]（**カーネルを学習しなくても利得が取れる**）＋ [V94] ＋ [P231]。⚠️ **恒久否決ではない** —— ★ 逆側の探索が不十分（[V93] / [P238] しか見つかっていない）であり、**self-supervised pre-training による小標本 HAR は未探索**である |
| ★ **「認知体力」を内部限定で使う（表示しない）** | ⚠️ **内部語も設計判断に影響する。** ★ [P77] 型（**測ること自体の害**）と同じで、**「持つだけ」でも機序は残る** |

---

## Consequences

### 良くなること

- ★ **段の軸が、証拠のある方向を向く** —— M2 は **ADR-009 D2** の competing risks と同じ形、
  M3 は**今回唯一一貫して正の証拠が出た軸**（Context-6）。
- ★ **昇格ゲートが「測れる量」になる**（D3）—— ★ 誤差棒に埋まる差を判定量にしない。
- ★ **有効標本数の議論が構造に合う**（D4）。
- ★ **禁止用語との衝突が起きない**（D7）。
- ★ **`docs/` の層番号が 1 系統増えない**（D2）—— ★ 既存 docs の改修がゼロ。

### 代償（★ 隠さない）

- ⚠️★★★ **D3 により「昇格した / しなかった」を 1 つの数字で言えなくなる。**
  ★ 受け方は **calibration ＋ 上下界が判断を反転させないか**の 2 本立てであり、**説明が長くなる。**
- ⚠️ **D5 は文献上の整合性であって GSE データでの実証ではない。** ★ ROCKET 系が GSE で効く保証は無い。
- ⚠️★★★ **逆側の探索が不十分である。** ★ 「深層が小標本の行動時系列で単純ベースラインに勝った」証拠を
  **発見できなかった**が、これは**存在しないことの証明ではない**
  （★ self-supervised pre-training による小標本 HAR は未探索）。→ ★ **D5 を恒久否決にしていない理由。**
- ⚠️ **D6 はコード変更を要するが、本 ADR では着手しない。** ★ 別タスクへ送る。
- ⚠️★★★ **打鍵動態からの認知状態推定で LOSO / セッション間崩壊を示した査読済み一次証拠は、
  2 系統の独立探索でも発見できなかった。** ★ 本 ADR の根拠は EEG（[P231]）/ 顔動画（[P230]）/
  加速度（[V100]）/ スマホ（[V98] [P232]）からの類推を含む。
  ⚠️ **ただし [V100] だけは領域ではなくデータ構造の議論**であり、GSE の 30 秒 1Hz 窓に直接適用できる。

### ★ 到達点の目安（★ 期待値を上げないために記録する）

★ content-free 打鍵単独の到達点は、**被験者内なら AUC 0.7 台、被験者を跨ぐと chance 付近**である。

| 標的 | 設計 | 数値 | 一次 |
|---|---|---|---|
| 疲労（★ 断眠という極端な対比） | 単発 / 累積 | AUC **72.1% → 80%** | [P161] |
| mind wandering | 10 分統制チャット・LOPO | **κ 0.363** / ROC-AUC 0.692 | [P226] |
| stress | 実フィールド 8 週・LOSO | **ρ 0.078**（個人化 0.296） | [P221]（⚠️ **査読前**） |
| stress | 統制 **N=977**・content-free 打鍵 | ⚠️ **chance を超えず / R² > 0 に届かず** | [P222] |
| 作業条件 | SWELL・computer 18 特徴単独 | **65.51%**（baseline **61.76%**） | [P219] |
| 同上 | SWELL・**LOSO** | ⚠️ **58.89%**（★ **baseline を下回る**） | [P219] |

⚠️★★★ **Flow / Incubation / Stuck そのものを content-free 打鍵から推定した研究は発見できなかった。**
★ 最も近い Bixler & D'Mello (2013, IUI) は **本文入手不能で二次情報が矛盾**しており、★ **引かない。**

---

## Migration

1. ✅ `docs/references.md` に [P219]–[P238] / [V89]–[V111] を append（★ 併せて [V84] の書誌を補完）。
2. `docs/glossary.md` の **MhD 項**を改訂 —— 「Stage 2 昇格は約 50 セッション ＋ 3% 改善」の
   **「3% 改善」を D3 のゲートへ差し替える**（★ **「約 50 セッション」は残す**）。
3. `docs/architecture/gse-v2-overview.md` に **M1〜M4 の呼称**と、
   **`L1〜L4` を採らない**（D2）ことを注記する。
4. `docs/adr/README.md` の一覧に本 ADR を追加する。
5. ✅ **未踏提出資料**（技術設計書 §4.4 / §4.5・設計スライド・参考文献）に D1 / D3 / D5 を反映した。
   ⚠️★★★ **研究者判断（2026-09-02）の「Stage 表を維持する」は、*段を降ろした説明を残す* という意味であって、
   *`Stage` という呼称を残す* 意味ではない。** ★ D1 が呼称を M1〜M4 に限定するため、
   **表そのものは M 表へ置換し、「降ろした理由」のスライドに本 ADR の一次証拠を足した。**
   ★ 実測（2026-09-02・`/cross-review` 指摘を受けて確認）: 設計スライドに `Stage` の残存は **0 件**、
   技術設計書に残るのは **旧基準への回顧的言及 1 箇所のみ**（§4.4 冒頭）。
6. ⚠️ **`docs/preregistration-v0.3.md` は触らない**（★ 凍結文書。ずれは本 ADR の記録として残す）。
7. ⚠️ **D6（境界特徴の実装）は別タスク・別ブランチ。**
