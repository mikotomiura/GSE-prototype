# Decisions

## D-1: RQ1–RQ4 の設計反映は Phase1 終了後に議論し、Phase2 以降で反映する (2026-07-03、同日訂正)

**決定**: サーヴェイ (20260703-intervention-content-and-ml-grounding.md) の改善提案は
Phase1 中には実装せず、**Phase1 終了後の議論で採否を決め、Phase2 以降に反映**する。

**⚠️ 訂正 (研究者指摘)**: 初版は「Phase1 は介入 OFF のため乗らない」を根拠にしたが誤り。
**Phase1 は 2 相プロトコル** (.steering/20260624-phase1-form-survey-design/decisions.md FD2):
- **Week1** = `intervention_enabled=false` + blind 較正 (`calibration_blind`)
- **Week2** = `intervention_enabled=true` で Nudge / Wall+2分Timer が**実発火** (`post_intervention`)

**訂正後の根拠**:
1. Week2 の `post_intervention` データは X1 確証 (Week1 の `calibration_blind` のみ) には
   使われず、受容性・介入応答・dismiss の観測とモデル監視用。**Week2 は「現行介入デザインの
   ベースライン受容性測定」と位置づける** — 現行版の受容性ベースラインが先にあることで、
   Phase2 AB/BA でのコンテンツ改善 (サーヴェイ反映版) の効果を相対化して語れる。
2. RQ2 (ポーズ位置・個人化閾値) は NDJSON が生 key (VK)・IME イベントを記録済みのため、
   Phase1 収集ログに gse-replay で遡及評価可能 = 延期でデータを失わない。Phase1 中の
   HMM 特徴変更は HMM_VERSION bump を強い較正の一貫性を壊すため不可 (M0 凍結維持)。
3. RQ3 (Stage2 = logistic+RF 2アーム) の判断時期はもともと M5。

**不変の制約 (どの案でも)**:
- **Phase1 開始後の介入内容の途中変更は不可** — 被験者間で介入体験が割れ Week2 観測が汚染される。
- 採用した介入内容は**使用するフェーズの開始前に PreReg 追補 (WBS 0.16) へ凍結**。

**検討した代替案**: 文言のみの軽量改善 (#1 メタ認知質問形 / #2 二人称形 / #4 Wall 自然画像) を
Phase1 開始前に入れて凍結し、Week2 受容性データを最初からサーヴェイ反映版で測る案。
Phase1 開始が迫る中での実装・検証時間リスクと、「現行版ベースライン→Phase2 改善版」という
比較構造の明快さを優先し、**採らない** (研究者が開始前に余裕ありと判断すれば再考可)。

**境界 (Phase1→Phase2) で必ず拾う 3 項目**:
- dismiss 理由 4択 UI (WBS 0.8、未実装確認済) + Nudge 選択肢化 (提案 #3) の統合設計・実装
- 採用介入内容 (文言・選択肢・if-then 意図設定) の PreReg 追補 (WBS 0.16) への凍結 — Phase2 開始前必須
- セッション開始 UI の if-then 意図設定 (提案 #7) の実装判断

**追加の含意**: Week2 で現行コンテンツの dismiss・受容性・介入応答 (A2 capture) が集まるため、
Phase1 終了後の採否議論は**サーヴェイ知見 × Week2 実測**の突合で行える (例: Nudge 無視率が
文献の 92% に近ければ選択肢化 #3 の優先度を上げる)。
