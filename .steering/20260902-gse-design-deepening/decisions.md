# 設計判断の記録 — 20260902-gse-design-deepening

## 判断 1: `.idea` §15 の層番号 `L1〜L4` を採らない

- **日付 / 決定者**: 2026-09-02・研究者
- **決定**: `.idea` §15.2 が提案する「Mh-D 内部を L1〜L4 と呼ぶ」案を**採用しない**。
  既存の **7 層アーキテクチャ `Layer 0`–`Layer 7`**（`docs/architecture/gse-v2-overview.md` §2）のまま説明する。
  新規の長期プロファイルには**層番号を与えず、別トラック名で置く**。
- **理由**:
  1. ★ **既存の層番号が 3 系統あり、いずれも L1/L2 を別の意味で使っている**（実測・`conflict-audit.md` F1）
     —— ① 7 層アーキ（L1=Domain Event Adapter / L2=Privacy Boundary）、
     ② glossary 逐語「`p_stuck` は **MhD（L1）**が計算する」「**Need 層（L2）**が消費する」、
     ③ 表現層の「層 0–3」（glossary に 18 箇所）。
  2. ★ **新設すると 4 系統目になり、`docs/` 全体で `L2` が 3 通りの意味を持つ。**
  3. ★ **`.idea` の L1〜L3 は既存 Layer 1–4 の別名にすぎず、新規性は L4 のみ**（同 F1 の対応表）。
  4. ★ 採らないことで `docs/` 側の改修がゼロで済む。
- **却下案**:
  | 案 | 却下理由 |
  |---|---|
  | L1〜L4 を既存 Layer 0–7 と併存させる | ⚠️ `L2` が 3 通りの意味を持ち、docs の可読性が落ちる |
  | 既存 7 層を L1〜L4 へ全面改番 | ⚠️ **確定済み ADR（001–018）の本文に触れる**ことになり、本タスクの禁止事項に抵触する |

## 判断 2: 「認知体力」という語を新設しない

- **日付 / 決定者**: 2026-09-02・研究者
- **決定**: **「認知体力」を新設しない。内部の長期構成概念としても置かない。**
  長期の量は**既存の行動指標の時系列**として扱い、**固有名を与えない**
  （`self_recovery_without_paste` / `paste_after_stuck_rate` / `manual_contribution_ratio`）。
- **理由**:
  1. ⚠️★★★ **「体力」は貯蔵量メタファそのもの**（減る・尽きる・回復する）であり、
     `docs/glossary.md` 禁止用語表が明示的に禁じた「**消耗 / 回復 / リソースの補充**」と**同じ枠組みの語**である。
     ★ 限定資源モデル（ego depletion）は死亡が確認済み（[P199] d=0.04 / [P200] d=0.06 / [P201] b=0.003）、
     **ART は限定資源モデルそのもので事前登録された検定 5 本すべて null**（[P193]–[P197]）。
     ★ **2026-09-01 に落としたばかりの枠組みへの逆戻りになる。**
  2. ⚠️ `.idea` §11.3 が提案する代替語「**負荷応答と回復のプロファイル**」は、
     **それ自体が禁止語「回復」を含む**。glossary の例外は既存指標名だけである。
  3. ⚠️ **`.idea` 自身が語の危険を自認している** —— §15.5 逐語
     「介入に反応しなかった人を『**認知体力が低い**』と誤って学習しない」。
     ★ **人物評価（trait）に読める語は、内部にすら置かない方が安全**。
  4. ★ 実測: **`認知体力` は repo に 1 件も存在しない**（まだ入っていない＝取り除くコストがゼロ）。
- **却下案**:
  | 案 | 却下理由 |
  |---|---|
  | 内部限定で「認知体力」を使う（表示しない） | ⚠️ 内部語も設計判断に影響する。★ [P77] 型（測ること自体の害）と同じで、「持つだけ」でも機序は残る |
  | 「回復」を含まない別の語を新設する | ★ 恒久否決ではない。⚠️ ただし**現時点では名前を要する対象が確定していない**（判断 3 が未確定）ので、先に名前を作らない |

## 判断 3: 長期プロファイル層を **置かない**（★ 確定・2026-09-02）

- **日付 / 決定者**: 2026-09-02・研究者（★ Stage 4 サーヴェイの結果を見たうえで）
- **決定**: **Phase1 では長期プロファイル層を置かない。** ADR に決定として明記して閉じる。
  ★ 将来やるなら**別 ADR で開き直す**。
- **理由**（★ すべて `stage4-survey.md` 系統 2 の一次確認による）:
  1. ⚠️★★★ **置ける形が、新しい層を要さない。** 成立するのは「各被験者に閉じた個人内の記述」だけであり
     （個人間パラメータを含む形は N=数名では文献上まったく支持されない）、★ それは
     **既存の行動指標（`self_recovery_without_paste` / `paste_after_stuck_rate` / `manual_contribution_ratio`）の
     時系列そのもの**である。→ ★ **層を新設する必要が無い。**
  2. ⚠️★★★ **GSE の設計は、基準論文が「悪い方」と名指しした象限である。**
     **Schultzberg & Muthén (2018)** 逐語 *"Samples with **many subjects and few time points** are shown to perform
     **substantially better** than samples with **few subjects and many time points**."*
  3. ⚠️★★★ **5 量のうち 1 つは、この時点で推定できない。**
     「同じ負荷に対するセッション間の変動」は **1 セッション = 1 時点 → T = 数十**で、
     **Mansueto (2023)** の *"sensitivity is low with ... **75 and 100 time points**"* に届かない。
  4. ⚠️★★★ **「個人差を層として明示化すれば解決する」は未検証の救済案である。**
     **GLOBEM (Xu 2022)** は **500 名超 / 2 機関 / 2 年**で先行 9 手法 ＋ domain generalization 8 手法を再評価し
     *"barely any advantage over the naive baseline of guessing the majority"*、★ **原因の診断が
     *"individual differences ... may play the most important role"***。→ ★ **GSE の発想はこの論文で否定も検証もされていない。**
  5. ★ **人物評価への滑落の危険が、規模で担保できない。**
     **Jussim & Harber (2005)**: 自己成就は平均では小さいが *"**selectively occur among students from stigmatized
     social groups**"* → ⚠️ **数名では選択的な害を検出できない。**
     かつ *"expectations may predict outcomes **more because these expectations are accurate than because they are
     self-fulfilling**"* → ★★★ **「予測が当たった」ことは自己成就の否定にならず、RCT でしか分離できない。**
- **却下案**:
  | 案 | 却下理由 |
  |---|---|
  | ADR-012 の先例に倣い、3 条件付きの**探索トラック**として置く（★ 当初の推奨案） | ★ 上記 1 —— **置ける形が既存指標の時系列であり、層を要さない**。⚠️ 層を作ると「人を比較する層」への滑落経路を自分で作ることになる |
  | 提出資料に将来構想としてだけ書く | ⚠️ 設計判断が SSOT に残らず、次セッションで再燃する |
- ★ **将来開き直すときの必要条件**（★ ADR に残す）:
  1. ★ **個人間パラメータを推定しないことを、実装で構造的に禁止する**（★ 宣言ではなく型と境界で）
  2. ★ **method-specific であることをモデルに書き込む**（**Steyer (2015)** LST-R 逐語 *"states and traits are **method specific**"*
     → ★ 単一の観測方法から出た量は **state であって trait ではない**）
  3. ★ **事後区間を必須にし、広いときはプロファイルを出さない**（★ ADR-010 の abstention と同型。
     **McNeish (2019)**: 壊すのは小 N ではなく**既定の diffuse prior**）
  4. ★ **欠測を第一級の量として扱う**（**Kiang (2021)**: 非収集は**週 0.5〜0.9% ずつ増える**
     → ⚠️ **脱落しがちな被験者ほど「持続しない人」に見える**）
  5. ★ **本人への提示を既定で行わない。返す/返さないを無作為化して害を測る**
  6. ★ **測定のみの対照群を置く**（⚠️ **「Nudge を出さない群」は「測定していない群」ではない** — [P77]）

## 判断 4: 未踏提出資料の Stage 表は **維持し、「降ろした理由」に一次証拠を足す**（★ 確定・2026-09-02）

- **日付 / 決定者**: 2026-09-02・研究者
- **決定**: 現行の Stage 1–4 表（3/4 は「主目標から外す」）を**維持する**。
  ★ ただし「Stage 3/4 を主目標から外した理由」に、**今回の一次証拠を足す**。
- **理由**: ★ 現行の判断は文献と一致していた。★ かつ言い方を強められる ——
  「**データが無いから段を上げない**」だけでなく「★ **この領域では複雑化して性能が下がった記録がある**」と言える。
- ★ **足す一次証拠**（判断 5 と共通）。

## 判断 5: `.idea` の ML の形を採るが、6 点を修正する（★ 確定・2026-09-02）

- **日付 / 決定者**: 2026-09-02・研究者（★「この方針で行きましょう」）
- **決定**: `.idea` §14.5 / §15.3 の **「モデルの複雑さの梯子」から「何をどの根拠で推定できるかの梯子」へ**という
  再定義を**採る**。⚠️ ただし下記 6 点を修正する。
- **なぜ `.idea` の形が有利か**:
  - ⚠️★★★ **旧 4 段（ルール+HMM → ロジスティック → 勾配ブースティング → 1D-CNN/TCN）が乗る「複雑さ」の軸には、
    負の記録がある**:
    - **Freihaut & Göritz (2024)** 本文逐語（N=179 × 14 日 × 10,760 instances）:
      *"The inclusion of mouse usage features in the ML models **did not enhance affect prediction, but decreased
      prediction performance as compared to the null model.** This decrease is likely due to **overfitting on random
      noise** arising from the inclusion of additional, non-informative input features."*
    - **Freihaut & Göritz (2021)** 本文逐語（N=994）: *"**All condition classifications were close to random guessing**"*、
      ★ **マウス軌跡を画像化した CNN 回帰は R² −5.22 〜 −1.10**（＝ 平均値予測より大幅に悪い）
    - **Kuvar (2023)** PRISMA 42 研究: *"**multimodal models do not present a clear edge over their unimodal counterparts**"*
    - **Koldijk (2018)**: ★ アルゴリズム間の幅 **最大 12 ポイント**（実用域の SVM↔RF は **3 ポイント**）に対し、
      ★★★ **評価法を 10-fold から LOSO に変えると 31 ポイント落ちる**（＝ **複雑化で得る幅より、正直に評価して失う幅が約 3 倍大きい**）
  - ★ **対して `.idea` の各段は、証拠のある軸に乗っている**:
    - Stage 2（criterion 直結）は **ADR-009 D2 で既決**の competing-risks / 離散時間ハザードと同じ形
    - Stage 3（個人・タスク適応）は ★ **今回唯一一貫して正の証拠が出た軸** ——
      **Naegelin (2025)** ρ **0.078 → 0.296**（⚠️preprint）/ **Ghosh (2017)** LOPO 71%(SD19%) → 個人化 **84%(SD6%)** /
      **Koldijk (2018)** mental effort 回帰に participant ID を足すと r **0.8221 → 0.9410**
      （⚠️ ただし **working condition 分類では ID は効かない** —— ★ **課題によって効き方が逆転する**）
    - Stage 4（policy を MRT で検証）は ★ **横断サーヴェイ 4 主張中いちばん裏付けが強かった**もの

### ★ 修正 6 点

| # | 修正 | 根拠 |
|---|---|---|
| **M-1** | ⚠️★★★ **「4 段」を提出資料の売りにしない。** ★ M（モデル成熟）だけを残し、**段の呼称を落とす** | ★ 名前を変えた 4 段の再導入は、スライドが 1 枚を割いて説明した「**降ろした理由**」と衝突して読まれる（`conflict-audit.md` F5）。★ `.idea` §15.1 自身が Stage（工程）と M（モデル）を分けろと書いている |
| **M-2** | ★ **Stage 3 から「長期系列化」を切り離す**（★ 個人・タスク適応だけにする） | ★ **判断 3**。長期プロファイルは置かない |
| **M-3** | ⚠️★★★ **昇格ゲートの「+X%」をやめる。** ★ 代わりに **(a) subject / session holdout での calibration** と **(b) 上下界が介入判断を反転させないか**（★ ADR-009 の反証ゲート G2 と同型）に置き換える | ★★★ **Varoquaux (2018)** 逐語 *"sample sizes ... inherently lead to **large error bars, eg ±10% for 100 samples**. The standard error across folds **strongly underestimates** them."* ⚠️ GSE の較正スモークは prereg で **n=3–5** → ★ **+3% / +5% は原理的に測れない** |
| **M-4** | ★ **有効標本数の単位を `Decision Episode` にする**（⚠️ セッション数 × 窓数で数えない） | ★★★ **Hammerla & Plötz (2015)** 逐語 *"**adjacent segments are not statistically independent**"* / *"a **significant drop in performance** ... if this bias is removed"*。★ GSE は 30 秒窓を 1Hz で出す＝**隣接窓は 29/30 が重複**。⚠️ **正しい DOI は `10.1145/2750858.2807551`**（広く引かれる `…2805940` は Crossref で 404） |
| **M-5** | ★ **M4 の最終候補を TCN / GRU から **ROCKET / MultiROCKET+Hydra**（非学習のランダム畳み込み特徴 ＋ 線形分類器）へ差し替える** | ★ **Middlehurst (2024)**（UCR 112 ＋ 新規 30）で **有意に最良の 2 手法の一方**。★ **Dempster (2020)** 逐語 *"simple linear classifiers using **random convolutional kernels** achieve state-of-the-art accuracy"* ＝ **カーネルを学習しなくても畳み込みの利得が取れる** → ★ data hungriness（**van der Ploeg 2014**: 複雑モデルは **>200 EPV でも不安定**）と被験者間分散（**Hefron 2018**: **時間文脈を伸ばすと被験者間分散が有意に増える**）の**両方を回避**。★ かつ **分類器が線形のままなので Stage 2 と地続き** |
| **M-6** | ★★★ **段を上げる前に、観測空間の穴を埋める**（★ 語・文境界のリズム特徴） | ★ **メインが一次検算（2026-09-02）**: `anonymize.rs` は `KeyCategory::SentencePunctuation`（0xBE / 0xBC）を「⚠️ **収集後は取り返せない**」と書いてまで保持し、[P121]（N=475・2 独立文脈）を根拠に **boundary keys を「採用（弁別の前提条件）」に格上げ**している。⚠️ ところが `features.rs` の `InputEvent` は **`is_backspace` しか持たず**、現行 5 特徴量（`f1_flight_time_median` / `f3_correction_rate` / `f4_burst_length` / `f5_pause_count` / `f6_pause_after_del_rate`）は**すべて境界非依存**。★ **`Kuvar (2022)` の κ=0.363 を出したモデルは、その境界特徴を含む** → ★★★ **記録側は残していて推論側が使っていない。モデルの段より先に特徴の段。** |

- ⚠️ **M-6 はコード変更であり、本タスクのスコープ外**（★ 別タスク・別ブランチ）。
- ★ **既に落としてあるもの**: 「認知体力」（判断 2）/ `L1〜L4`（判断 1）/
  `.idea` §14.4 の改善案 7 件のうち 6 件（★ 既決 ADR の言い換え・`conflict-audit.md`）。

## 判断 6: `md2pptx.py` を手組み OOXML から `python-pptx` へ移す（★ 2026-09-02）

- **決定**: `.pptx` の生成を **`python-pptx` 1.0.2** に委ねる。
- **理由**: ⚠️★★★ **手組み版は Google Slides で 2 回続けて開けなかった**（1 回目 = 必須パートと XML 妥当性のみ検査／
  2 回目 = 標準パート 5 本を追加し継承チェーンを繋いだ）。★ **「PowerPoint が出す形」を推定し続けるのをやめた。**
  ★ 前提が変わった —— **2026-09-01 に「入っていない」と実測された `python-pptx` が、2026-09-02 に `pip install` で入った。**
- ⚠️ **代償**: 依存が 1 つ増える（★ `md2docx.py` は標準ライブラリのまま）。
- ★ **併せて検査の偽陽性を 1 件潰した**: `layout → master` の継承照合を **idx でやっていたのが誤り**。
  実物では `dt` / `ftr` / `sldNum` は **layout と master で idx が違うのが正常**
  （★ 既定テンプレートで実測: master `dt:2 / ftr:3 / sldNum:4` vs layout `dt:10 / ftr:11 / sldNum:12`）。
  → ★ **`layout → master` は type で照合し、`slide → layout` は idx まで一致を要求する。**
- ⚠️★★★ **未検証**: **Google Slides で実際に開けるかは未確認**（★ 前回も機械検査は全部緑だった）。
