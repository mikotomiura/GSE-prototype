# 設計 — intervention-ux-clarity

## 実装アプローチ

### (1) Monk Mode UX 整理 — 表示条件のみ変更 (ロジック不変)
`interventionEnabled` を App→Dashboard に渡し、**interventionEnabled=true のときだけ** Monk Mode トグルを
描画する。interventionEnabled=false (較正既定) では `lib.rs:135` で全介入が gate されるため Monk Mode は
no-op → 非表示にして「効かないのに見える」不整合を解消。介入有効時は従来どおり Wall mute 操作として機能。
Monk Mode のトグル/broadcast/Wall 無効化ロジックは**一切変更しない** (intervention-design ルール5 準拠)。

> Step C 選択肢: A=「interventionEnabled で表示条件化」(推奨・機能温存) / B=「Monk Mode を廃し介入トグルに一本化」
> (機能削減・Wall 単独 mute ができなくなる)。推奨は A。

### (2) 介入仕様の明文化 — docs
`docs/functional-design.md` の介入セクションに「発火/非発火条件」を明記:
- Need=p_stuck。Nudge: Need≥0.60。Wall: Need≥0.70 が累積30秒。
- Opportunity ゲート: 2〜30秒の小休止が好機 (短2-8s=+0.45/中8-30s=+0.35)、能動タイプ中(<2s)は減点で defer、
  **idle≥3分は `away_idle` で介入停止** (席を離れたら黙る=不便益)。
- **idle≠Stuck**: 放置すると p_stuck は低下する (無打鍵=idle 観測)。「放置で介入」は設計外。
- interventionEnabled (セッションのマスタ ON/OFF) と Monk Mode (実行中・Wall のみ無効) の役割差を明記。
- glossary に Monk Mode / away_idle 等の用語を必要に応じ追加。

### (3) opportunity ゲート検討 — 調査記録 (コード変更なし)
dogfood セッションの `gse-replay --intervention`: 1111 decision = none1082 / defer29 / nudge0 / wall0、
**DC=1.000** (defer した苦闘は全て自己回復)、Burden 0。能動タイプ中に p_stuck 0.65〜0.92 を検知するも
好機 (小休止) と重ならず nudge 未発火。**n=1・DC=1.0 では閾値変更を正当化できない** (介入しなかったのは妥当)。
→ decisions.md に記録 + 「ラベル付き複数セッションで `gse-replay --intervention` の HIR/Precision を見て再評価。
将来の調整候補: `NUDGE_OPPORTUNITY_THRESHOLD=0.35` / pause 窓 / away_idle 閾値」を申し送り。`intervention.rs` は無変更。

## 変更対象

### 修正
- `src/App.tsx` — `<Dashboard interventionEnabled={interventionEnabled} ... />` を渡す。
- `src/components/Dashboard.tsx` — `interventionEnabled?: boolean` prop 追加。Monk Mode トグルを
  `{interventionEnabled && (...)}` で条件表示。
- `docs/functional-design.md` — 介入の発火/非発火条件・interventionEnabled vs Monk Mode を明記。
- (必要なら) `docs/glossary.md` — away_idle / Monk Mode。
- `.steering/.../decisions.md` — opportunity ゲート調査結果と推奨。

### 触らない
- `src-tauri/src/analysis/intervention.rs` (閾値・ロジック)・`engine.rs`・`features.rs`・`lib.rs`・`wall_server.rs`。
- Monk Mode の機能実体 (broadcast / Wall 無効化)。Overlay / ProbeCard / VignetteTest。

## 影響範囲
- frontend 表示条件のみ。backend / schema / 介入ロジック不変 → snapshot / intervention テスト回帰なし。
- calibrationMode と独立: interventionEnabled=true & calibrationMode=true なら blind 画面でも Monk Mode 表示
  (介入が起こりうるため正しい)。gate 信号は interventionEnabled (Monk Mode が意味を持つ条件) で適切。

## 既存パターンとの整合性
- `calibrationMode` prop と同型の条件表示 (typescript-standards: any 不使用・builtin hooks)。
- intervention-design ルール5 (Monk Mode は Wall のみ無効・Nudge 不変) を維持。

## テスト戦略
- `npm run build` (tsc+vite) 緑。
- 手動: interventionEnabled OFF で開始→ Monk Mode 非表示 / ON で開始→ 表示・トグル動作。
- `intervention.rs` 無変更ゆえ `cargo test --workspace` / `gse-replay --snapshot` は不変 (確認のみ・省略可)。

## ロールバック計画
- frontend prop 追加 + docs のみ。revert で従来表示に即復帰。介入ロジック不変ゆえ副作用なし。
