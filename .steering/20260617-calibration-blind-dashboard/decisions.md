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

## CD-5 review LOW 対応: 較正中の打鍵状態色を中立化
- **判断**: security-checker LOW 指摘 (kbd-active=flow緑 / kbd-idle=incubation黄 が状態パレットと同一で
  色による状態アンカリングを誘発しうる) に対応し、較正中は `kbd-neutral` (--color-text) を適用。
- **根拠**: CD-4 (コンテナ状態色の中立化) と同じ「間接的な色アンカリング防止」方針の一貫適用。値自体は
  keyboardIdleMs でモデル出力ではないが、色記号の誤連想を断つ。

## 受容 / 申し送り
- **独立レビュー実施済 (API 復旧後に再試行して成功)**: 初回は code-reviewer/security-checker が
  **529 Overloaded で複数回失敗**・Codex 側は **jq 不在**でゲートされたため一旦インライン自己レビューで
  コミットしたが、API 復旧後に **code-reviewer + security-checker を再実行**。
  - code-reviewer: HIGH/MEDIUM なし。LOW 2 件 (dominant 計算・inline style) は任意・現状維持。
  - security-checker: PASS。HIGH/MEDIUM なし。LOW 1 件 (打鍵状態色) → CD-5 で対応済。
  - Codex (/cross-review) は引き続き jq 不在でスキップ ([[project-codex-review-needs-jq]])。
- **cargo 検証省略**: Rust 無変更のため回帰なし (frontend のみ)。
- **GUI 手動確認は実機**: blind 表示・ProbeCard 回答・VignetteTest・nudge/wall 非表示 (interventionEnabled=false)
  は headless 不可のため実機手動。design.md テスト戦略に明記。
