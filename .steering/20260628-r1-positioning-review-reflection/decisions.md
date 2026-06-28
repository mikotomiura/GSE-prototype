# 重要な設計判断

## 判断 1: 売りの headline は B「Stuck 検出 × 介入タイミング」を主役、A/C を入れ子

- **判断日時**: 2026-06-28（ユーザー選択）
- **背景**: 研究の貢献を 1 つ headline に立てる必要。資産が多い（測定/思想/学習科学/身体性/方法論）。
- **選択肢**: A 不便益の計算機実装 / B 行動的弁別（測定）/ C AI 時代の認知的自立 / D 不便の処方の因果同定
- **採用**: **B 主役 + A(System)/C(Vision) 入れ子**
- **理由**: 現フェーズ（較正）で実際に賭けているのが B の反証可能な測定主張。X1 Kill でも「測定法の破綻検出」が貢献として残り、Go なら H-Y/H-X2 が開く（守攻両対応）。
- **トレードオフ**: Codex は「停滞検出単体は既知」と指摘 → §4 で「本文非保存制約下の統合プロトタイプ＋前向き較正」を新規性核に立てて吸収（指摘 E）。headline 全面差し替えはしない。

## 判断 2: 非 overclaim の精密化（F/I/S 分類は claim しない）

- **判断日時**: 2026-06-28（ユーザー指摘で2段階是正）
- **確定事項**:
  - GSE は F/I/S を 3 値で実用精度分類**しない**。
  - **Need 層 = p_stuck（stuck_likelihood）= 「介入を要するほど Stuck か」の 1 次元検出**（ユーザー補足: Need 層は Stuck か否かは測る）。
  - **Opportunity 層 = 介入タイミング**（高 Stuck × 小休止で発火、能動タイプ <2s は defer）。
  - 「守る苦闘 vs 断つ停滞」の区別は**分類器出力ではなく Need×Opportunity ゲートの組合せから創発**。
  - MhD = 検出モデル総称、Stage1 = ルールベース HMM が現在地、Stage2 = ロジスティック回帰。
- **見直しタイミング**: Stage2 昇格時、または F/I/S を実分類する設計に変えたとき。

## 判断 3: references.md は P/V 名前空間で 2 書誌を統合（renumber 禁止）

- **判断日時**: 2026-06-28
- **背景**: 理論書誌（提案・[1..15]）と方法論書誌（v0.4・[1..17]）が独立番号で既出。1 本に振り直すと既存 docs の inline がずれる。
- **採用**: 名前空間保持（`[Pn]`/`[Vn]`）＋重複 6 件は「重複」列で相互リンク（一意 26 本）。
- **トレードオフ**: 論文用に統一番号が要れば後で振り直し可。当面は traceability と無破壊を優先。

## 判断 4: Physical Anchor の縮退（指摘 C）は採用しない

- **判断日時**: 2026-06-28（ユーザー明言）
- **背景**: レビュー（Codex/Claude）は PA を feasibility 限定へ縮退すべきと指摘。
- **採用**: **不採用**。PA は実装予定の第一級構成要素として扱う（§9 等の PA 記述は本タスクで変更しない）。
- **影響**: 本タスクのスコープから指摘 C を除外。将来 PA 実装時に受容/効果/安全の検証設計を別途詰める。

## 判断 5: 検証は「層別 GT/判断性能ラダー」として docs に明示（A-1/A-2 の決着）

- **判断日時**: 2026-06-28（ユーザーとの対話で確定）
- **背景（層モデルの訂正）**: 当初「Need 層が焚く p_stuck」と書いたのは誤り。正しくは:
  - **機能3（MhD/HMM）= Stuck の計算**: 特徴量 → X(Cognitive Friction)/Y(Engagement) → HMM Forward → `p_stuck`。**p_stuck は MhD の出力**。
  - **機能4（Need）= 別計算**: `p_stuck` に閾値（nudge_need 0.60 / wall_need 0.70 累積30s）＋抑制を当てる介入要否判定。`intervention.rs:335` で現状 `need_score = p_stuck` だが判定ロジックは別層。
- **核心の指摘（ユーザー）**: 現状 GATE3 の検証は「**システム自体の GT**」＝ MhD 内部軸（L0）の収束的妥当性しか確立しない。Stuck(L1)・Need(L2) には独立 GT/判断性能の定義が要る。
- **重要な発見（既実装・収集不変）**: Need 層の**判断性能は既に評価器がある**（`intervention_eval.rs`）。混同行列（PROTECT={Flow,Inc}/STALL={Stuck}）＋**HIR(有害介入率)**/Precision/STALL-recall＋`nudge_need` 閾値 sweep・reason 層別。GT は UserLabel 3 値(hotkey)。
- **確定した 3 層ラダー（docs に明示する構造）**:

  | 層 | 検証対象 | 評価方法（実装） | GT | GT クラス | 客観アンカー |
  |---|---|---|---|---|---|
  | L0 軸 | MhD X/Y | 順序 C-index, GATE3 (`calibration_eval.rs`) | probe Q1/Q2 | 主観 | — |
  | L1 Stuck | `p_stuck` | L0 継承＋self-marker 照合 | self-marker(疎)・派生 high-Q1×low-Q2 | 主観(疎) | `external_paste` 等で間接 |
  | L2 Need | 介入決定 ACT/HOLD | 混同行列＋HIR/Precision/STALL-recall＋閾値 sweep (`intervention_eval.rs`) | UserLabel 3 値{F/I/S}(hotkey) | 主観(別計器) | `paste_after_stuck`/`self_recovery` |

- **採用方針**:
  - **A-1**: L1 Stuck GT = **self-marker（独立主観 Stuck）主＋派生 high-Q1×low-Q2 補**、直接プローブ項目は**将来課題**（収集変更のため本タスク外）。X1 確証主張は L0 二軸に限定し、p_stuck は「X/Y から導く Need 信号、独立妥当性は L1 として別建て」と橋渡し。
  - **L2 Need**: 判断性能（HIR/Precision/STALL-recall/閾値 sweep）を §5 に明示。GT = UserLabel(主観) ＋ dismiss_reason 負例 ＋ 行動アウトカム（paste/recovery）で三角測量。
  - **A-2**: 全 GT が主観自己申告（反応性・観察者効果）と明記。**唯一の客観 content-free アンカー = 行動アウトカム**。**客観的脳内 GT は不在**と §8「方法論的限界」に明記。
- **重要制約**: **コードは Edit しない**。既実装の評価器・GT 信号（全て収集不変・既ログ）を **docs に明示するだけ**。
- **見直しタイミング**: Stage2 昇格時、または直接 Stuck プローブ項目を追加する収集変更を行うとき。
