# decisions.md — calibration-blind-dashboard

## CD-1 frontend のみで完結 (backend/schema 不変)
- **判断**: blind 化は `App.calibrationMode` (frontend state) と `Dashboard` の条件表示のみで実現し、
  `record_session_meta`・schema・backend は変更しない。
- **根拠**: blind は「被験者に何を見せるか」という UI 表示の制約。track="main" / interventionEnabled は
  既に session_meta に記録済みで、calibrationMode を NDJSON に永続化する必要がない。A schema 凍結・
  スコープ「schema 変更しない」を守れ、回帰面が最小。

## CD-2 新規コンポーネントを作らず Dashboard に prop を追加 (ユーザー承認済み)
- **判断**: `BlindDashboard.tsx` を新設せず、`Dashboard` に `calibrationMode?: boolean` を足して
  モデル出力セクションを条件表示。
- **根拠**: blind 表示も Dashboard 既存の「セッションバー + 権限バナー + Monk Mode + 終了」を流用する。
  権限バナー (macOS/Windows 約 180 行) を別コンポーネントへ複製すると二重保守。単一コンポーネントの
  条件表示が最小差分・最低リスク。設計承認で v2(別コンポーネント)案より本案を選択。

## CD-3 calibrationMode 既定 ON
- **判断**: 既定 true (v0.3 較正の既定画面 = blind)。Start 画面トグルでデバッグ/通常用途は OFF にできる。
- **根拠**: v0.3 は較正フェーズであり、測定独立性が既定要件。要件「v0.3 較正セッションの既定画面を blind」準拠。

## CD-4 間接漏れ (状態色) も遮断
- **判断**: コンテナの `state-${dominant}` クラス (背景/アクセント色が推定状態を暗示) を較正時は中立
  `state-calibration` に置換。`.state-calibration` は状態色を持たない。
- **根拠**: テキスト/数値だけでなく色によるアンカリングも測定独立性を壊すため (data-privacy)。

## 受容 / 申し送り
- **独立レビューが infra 都合で未実施**: code-reviewer / security-checker サブエージェントが
  **529 Overloaded で複数回失敗**、かつ Codex 側は **jq 不在**で /cross-review がゲートされた。
  → インライン自己レビュー (typescript-standards / data-privacy 基準) を実施し HIGH なし・`npm run build`
  (tsc) 緑を確認。API 復旧後に /cross-review を再試行することを推奨 (品質ゲートの失敗ではなく基盤不在)。
- **cargo 検証省略**: Rust 無変更のため回帰なし (frontend のみ)。
- **GUI 手動確認は実機**: blind 表示・ProbeCard 回答・VignetteTest・nudge/wall 非表示 (interventionEnabled=false)
  は headless 不可のため実機手動。design.md テスト戦略に明記。
