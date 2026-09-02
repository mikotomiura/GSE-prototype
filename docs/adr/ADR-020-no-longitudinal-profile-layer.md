# ADR-020: 長期プロファイル層を Phase1 では置かない

- **ステータス**: **Accepted**（2026-09-02・研究者判断）
- **日付**: 2026-09-02
- **関連**: **ADR-019**（ML の段の再定義。★ 本 ADR は ADR-019 D1 の M3 から「長期系列化」を切り離す）/
  **ADR-008 D1**（オンライン更新の対象を層で限定）/ **ADR-009 D2**（主張範囲を上下界に縮める先例）/
  **ADR-010 D1**（`evidence_quality` 低下 → `none` / `defer`）/ **ADR-012 D7**（★ 計測器を本体の外に置く先例）/
  **ADR-017 D10** / **ADR-018 D5**（評価量を機会保存の行動指標に置く）
- **作業記録**: `.steering/20260902-gse-design-deepening/`
- **入力**: `.idea/20260901-smartphone-state-externalization-and-physical-return.md` §11.3 / §15.2
  （⚠️ **追跡外＝ SSOT ではない**）
- **一次証拠**: [P77] / [P232] / [P234]–[P237] / [V103]–[V111]（★ 全件 Crossref raw JSON で検算済み）
- **コード変更**: **ゼロ**

---

## Context

### 1. これが `.idea` §12–15 で**唯一の新規要素**だった

2026-09-02 に `.idea` を既存 ADR と逐条照合した結果、§14.4 の「改善案」7 件のうち 6 件は
**ADR-008 / 009 / 010 / 012 で既に決まっていた**（`ADR-019` Context-1）。
★ **既存の 7 層に対応が無いのは「複数セッションにまたがる長期プロファイル層」だけ**である。

`.idea` §11.3 逐語（★ 扱いたい 5 つの量）:

> 摩擦が高まり始めるまでの傾向 / 摩擦が高まった後に自力で戻るまでの傾向 /
> 離席や小休止の後に作業へ再接続できる傾向 / 高摩擦状態で外部出力へ依存せずに前進する傾向 /
> 同じ負荷に対するセッション間の変動
> …これらは「認知体力が高い／低い」という**人物評価ではなく**、個人内の時系列的な作業状態の変化として分析する。

### 2. ⚠️★★★ GSE の規模は、この領域の検討範囲の外にある

| 一次 | 逐語 |
|---|---|
| ★★★ [V103] | *"**Samples with many subjects and few time points are shown to perform substantially better than samples with few subjects and many time points.**"* → ⚠️★★★ **GSE の設計（被験者数名 × 1 人数十セッション）は、この論文が「悪い方」と名指しした象限そのもの** |
| [V104] | 検討した Level-2 の**最小が N = 10**。*"large positive relative bias, especially with **N < 30**. At **N = 40** ... relative biases exceeding 1.10"*。複雑モデルでは **N = 100 でも問題が残った** |
| ★★★ [V106] | *"**N = 100 generally was not enough** to provide accurate inference about between-person variations"* / *"As N increased to **200**, relative biases decreased substantially"* / *"usually **demands more on N than T**"* |

→ ★ **個人間パラメータを含む定式化（多水準 VAR / DSEM の random effects / cohort 横断の判定）は、
GSE の被験者数ではどの検討範囲にも入っていない。**

### 3. ★ 個人ごとに独立に推定する N-of-1 路線にも上限がある

[V105] 逐語: *"**sensitivity is low with sample sizes feasible for clinical practice (75 and 100 time points)**"* /
*"with 75 and 100 observations, it is advisable to **reduce the number of nodes to around six variables**"* /
⚠️ *"**Estimating temporal networks appears particularly challenging**"*。

⚠️★★★ **この基準で、5 量のうち 1 つが落ちる**:

| 量 | 1 時点の数え方 | 判定 |
|---|---|---|
| 摩擦が高まり始めるまでの傾向 | セッション内の事象 | ★ 桁は足りうる |
| 摩擦が高まった後に自力で前進へ戻るまでの傾向 | 同上 | ★ 桁は足りうる |
| 短い中断の後に作業へ再接続できる傾向 | 同上 | ★ 桁は足りうる |
| 高摩擦状態で外部出力へ依存せずに前進する傾向 | 同上 | ★ 桁は足りうる |
| ⚠️★★★ **同じ負荷に対するセッション間の変動** | ★ **1 セッション = 1 時点** → **T = 数十** | ⚠️★★★ **[V105] の 75〜100 に届かない。文献上、推定できると言えない** |

★ かつ 5 量はいずれも**時間方向の関係**であり、[V105] が *"particularly challenging"* と名指ししたクラスに当たる。

### 4. ⚠️★★★ 「個人差を層として明示化すれば解決する」は、未検証の救済案である

[P232]（GLOBEM）は **500 名超 / 2 機関 / 2 年 / 4 institute-year データセット**で、
先行 9 アルゴリズムを忠実に再実装し、domain generalization 手法 8 個を加えて評価した。

- 逐語 *"Our experiment reveals the **lack of model generalizability** of these methods"*
- 逐語 *"these methods also do not generalize well ..., with **barely any advantage over the naive baseline of
  guessing the majority**"*
- ★★★ **原因の診断**: *"**individual differences** (both within and between populations)
  **may play the most important role** in the cross-dataset generalization challenge"*
- ★ 著者らの最良手法でも *"the overall advantage is **incremental**"*

→ ⚠️★★★ **GSE の発想（個人差を層として明示化する）は、この論文で否定も検証もされていない。**

### 5. ★ 人物評価への滑落は、規模では防げない

| 一次 | 逐語 |
|---|---|
| ★★★ [P236] | ★ **無作為割付**（N=116 / N=107）で、告げるリスクを**実際の遺伝型と独立に**割り付けた。*"changed individuals' cardiorespiratory physiology, perceived exertion and running endurance ... **in a self-fulfilling manner**"* / *"Effects of perceived genetic risk on outcomes were **sometimes greater than the effects associated with actual genetic risk**."* |
| ★★★ [P235] | **607 効果量 / 23,663 観測**。*"**over 1/3 of the FIs decreased performance**"* / ★★★ *"FI effectiveness **decreases as attention moves up the hierarchy closer to the self and away from the task**"* → ★ **プロファイルの提示は、定義上、注意を自己へ向ける操作である** |
| ★★ [P237] | *"powerful self-fulfilling prophecies **may selectively occur among students from stigmatized social groups**"* ＝ ⚠️ **害は平均では小さいが不利な立場の人に集中し、数名では検出できない**。★★★ かつ *"expectations may predict student outcomes **more because these expectations are accurate than because they are self-fulfilling**"* → **「予測が当たった」ことは自己成就の否定にならず、RCT でしか分離できない** |
| ★★★ [P234] | *"non-collection **increased by 0.5% to 0.9% per week**"*、属性による差もあり → ★★★ **脱落しがちな被験者ほど「持続しない人」に見える＝人物評価への最短経路** ⚠️ **著者ら自身は楽観的に結論している**（*"demonstrate the **feasibility**"*）ので、逆向きに引くことを明記する必要がある |
| ★★★ [P77]（既登録） | *"**Even in the absence of explicit external incentives**, measurement itself can thus have similar effects."* → ⚠️ **「Nudge を出さなければ安全」ではない** |

### 6. ⚠️ エルゴード性の議論は、**両方向に効き、かつ決着していない**

- [V107]（原典）: *"only under very strict conditions ... can a generalization be made from a structure of
  interindividual variation to the analogous structure of intraindividual variation"*
  → ⚠️★★★ **逆向きにも効く** —— **GSE が数名分のプロファイルを束ねて「傾向」を語ることも、同じ定理で禁止される。**
- [V108] は同誌で **2 本の Letter による批判**を受けている: [V109]（*"this comparison is **fundamentally flawed**"*）/
  [V110]（**表題が "Ergodicity is sufficient but not necessary"**）。★ 著者らの reply も部分的に譲歩している。
  → ⚠️★★★ **「非エルゴードだから群 → 個人は不可」という強い形で引いてはならない。**
- ★ **GSE に効く安全な定式化は [V111]（LST-R）側**である: *"**states and traits are method specific**"*
  → ★ **単一の観測方法から出た量は state であって trait ではない。**

---

## Decision

### D1. ★★★ **Phase1 では長期プロファイル層を置かない**

- **決定**: 複数セッションにまたがる負荷応答・持続の**推論層を新設しない。**
  ★ **ADR-019 D1 の M3 は「個人・タスク適応」だけを担い、「長期系列化」を含まない。**
- ⚠️★★★ **これは「将来もやらない」ではない。** ★ 将来やるなら **別 ADR で開き直す**（→ D3）。

**根拠 4 本**:

1. ★★★ **置ける形が、新しい層を要さない。** Context-2 / 3 より、成立するのは
   **「各被験者に閉じた個人内の記述」**だけであり、★ それは **ADR-018 D5 が既に主要アウトカムに置いた行動指標
   （`paste_after_stuck_rate` / `self_recovery_without_paste` / `manual_contribution_ratio`）の時系列そのもの**である。
   → ★ **層を新設せずに同じものが得られる。**
2. ⚠️★★★ **GSE の規模が検討範囲の外にある**（Context-2）。★ **[V103] が名指しした「悪い方」の象限**である。
3. ⚠️★★★ **5 量のうち 1 つは、この時点で推定できない**（Context-3）。
4. ⚠️★★★ **主因の診断が GSE の発想を支持していない**（Context-4）。

### D2. ★★★ 長期の量が要るときは、**既存の行動指標の時系列**として扱い、**固有名を与えない**

- **決定**: 「作業持続プロファイル」「負荷応答プロファイル」等の**新しい名前を作らない。**
  ★ **ADR-019 D7**（「認知体力」を新設しない）と一体で読むこと。
- **理由**: ★ **名前を与えた瞬間に、それは「人が持つ何か」として読まれる。**
  [V111] の逐語（*"states and traits are **method specific**"*）が守れるのは、
  **量が観測方法に紐づいた指標のままである間だけ**である。
- ⚠️ `.idea` §11.3 の代替語案「**負荷応答と回復のプロファイル**」は、
  **それ自体が `docs/glossary.md` の禁止語「回復」を含む**（★ 例外は既存指標名だけ）。

### D3. ★★★ 将来この層を開き直すときの**必要条件 6 件**（★ ADR に残す）

⚠️ **下記が揃わないうちは開かない。** ★ 開くときは新規 ADR でこの 6 件への充足を示すこと。

| # | 必要条件 | 根拠 |
|---|---|---|
| 1 | ★★★ **個人間パラメータを推定しないことを、実装で構造的に禁止する**（★ 宣言ではなく型と境界で）。★ 既存の `cohort.rs` 系の横断判定とプロファイルの間に**越えられない境界**を置く | [V107]（★ **両方向に効く**）/ Context-2 |
| 2 | ★★★ **method-specific であることをモデルに書き込む** —— 出力に観測方法を型として付随させ、**方法をまたいだ解釈を型で禁じる** | [V111] 逐語 *"states and traits are method specific"*。⚠️ **宣言では足りない** |
| 3 | ★★★ **事後区間を必須フィールドにし、区間が広いときはプロファイルを出さない**（`none` を返す）。★ **事前分布を明示的に制限する** | [V104]（★ **壊すのは小 N ではなく既定の diffuse prior**）。★ **ADR-010 の abstention と同型** |
| 4 | ★★★ **欠測を第一級の量として扱う** —— 欠測率・時間パターンを共変量として記録し、**MNAR 仮定の感度分析を事前登録**する | [P234]（**週 0.5〜0.9% ずつ増える**・属性差あり）/ [V106]（*"heterogeneity in missingness distributions"*） |
| 5 | ★★★ **本人への提示を既定で行わない。行うなら人物述語を出力語彙から外し、「日時付きの事象列」として返す。★ 返す / 返さないを無作為化して害を測る** | [P236] / [P235] / ★ [P237] の *"more because ... accurate than ... self-fulfilling"* により **RCT でしか分離できない** |
| 6 | ★★★ **測定それ自体の害を測る対照群を置く** —— ⚠️ **「Nudge を出さない群」は「測定していない群」ではない** | [P77] 逐語 *"Even in the absence of explicit external incentives, measurement itself can thus have similar effects."* |

---

## Alternatives

| 却下案 | 却下理由 |
|---|---|
| ★ **ADR-012 の先例に倣い、3 条件付き（本体の判定に使わない / 利得を主張しない / 別プロセス）の探索トラックとして置く** | ★ **当初の推奨案だったが、サーヴェイの結果で落とした。** ⚠️ **置ける形が既存指標の時系列であり、層を要さない**（D1 根拠 1）。★ かつ **層を作ると「人を比較する層」への滑落経路を自分で作ることになる** |
| ★ **提出資料に将来構想としてだけ書き、ADR を起票しない** | ⚠️ **設計判断が SSOT に残らず、次セッションで再燃する**（★ `.idea` §12–15 の 6 件が「既決の再発見」だったのと同じ形） |
| ★ **N-of-1 路線に限定して置く**（★ 各被験者に閉じる） | ⚠️ [V105] が **75〜100 時点でなお sensitivity 不足**とし、**5 量のうち「セッション間の変動」は T=数十で届かない**（Context-3）。⚠️ **恒久否決ではない** —— ★ **D3 の 6 件が揃い、かつ時点数が足りれば再検討可** |
| ★ **「作業持続プロファイル」等の中立的な名前を新設する** | ⚠️ **名前を与えた瞬間に「人が持つ何か」として読まれる**（D2）。★ **現時点では名前を要する対象が確定していない** |

---

## Consequences

### 良くなること

- ★ **主張範囲と観測が一致する** —— 測るのは **ADR-018 D5 が既に定めた機会保存の行動指標**だけになる。
- ★ **人物評価への経路を、実装として持たない**（★ 規約ではなく構造で防ぐ）。
- ★ **ADR-019 D1 の M3 が「個人・タスク適応」に絞られ、証拠のある軸だけを残す。**
- ★ **`.idea` §12–15 の全項目に裁定が付いた**（★ 6 件は既決の再発見・1 件は本 ADR・残りは ADR-019）。

### 代償（★ 隠さない）

- ⚠️★★★ **「同じ負荷に対するセッション間の変動」を系として扱う手段が無くなる。**
  ★ 記述統計として見ることは妨げないが、**推論層としては持たない。**
- ⚠️★★★ **GSE と同じ設定（PC 上の content-free 行動から個人の縦断プロファイルを構成し、
  それが再現された / 崩れた）の先行例は、探索で発見できなかった。**
  ★ **支持する先行例も、直接反証する先行例も、文献上まだ存在しない**
  → ⚠️ **本 ADR は「文献が否定したから置かない」ではなく、「規模と害の非対称から置かない」という設計判断である。★ そう書くこと。**
- ⚠️ **「作業状態の長期プロファイルを本人に返した無作為化試験」も発見できなかった。**
  ★ D3-5 / D3-6 の根拠（[P236] / [P235] / [P77]）は**いずれも類推**である。
- ⚠️ **[V103] の具体的な N/T 数値は本文未到達であり、[V106] 本文からの二次引用である。**
  ★ 提出資料で数値を出すなら、二次性を明記するか原本を入手すること。

---

## Migration

1. ✅ `docs/references.md` に [P232] [P234]–[P237] / [V103]–[V111] を append（ADR-019 と同時）。
2. `docs/glossary.md` に **「長期プロファイル層は置かない」**を追記し、
   ★ **「作業持続プロファイル」「負荷応答プロファイル」「認知体力」を禁止用語側へ入れる**（D2 / ADR-019 D7）。
3. `docs/architecture/gse-v2-overview.md` に、**7 層の外に長期層を足さない**ことを注記する。
4. `docs/adr/README.md` の一覧に本 ADR を追加する。
5. ⚠️ **`docs/preregistration-v0.3.md` は触らない**（★ 凍結文書）。
6. ⚠️ **コード変更は無い。**
