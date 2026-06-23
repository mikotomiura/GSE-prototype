# タスクリスト

## 準備
- [x] HCI 査読研究を調査 (research agent) → 方向性をユーザー承認
- [x] 既存 self_marker/realtime_label/hotkey 配線・Overlay box-mode を調査

## 実装
- [x] Nudge: nudgeVisible 保持 + 60s silent タイムアウト + 非ブロック box (widgetOnly) + 穏やかフェード CSS
- [x] Wall: wall-dim-in でゆっくり減光フェードイン (QR/早期解除維持)
- [x] 自己ラベル: record_self_marker_inner 集約 + コマンド + D ホットキー + Dashboard ボタン + CSS

## テスト
- [x] tsc + vite build 緑
- [x] cargo test --workspace 緑 (210)
- [x] --snapshot byte-equal (HMM 不変)
- [ ] 実機 GUI: nudge 保持/非ブロック/右上・wall 減光・ボタン/ホットキーで self_marker 記録 (手元)

## レビュー
- [x] code-reviewer + security-checker (CRITICAL/HIGH なし; HIGH-1 debounce 集約・MEDIUM 対応済)
- [ ] /cross-review (Claude ∥ Codex)
- [ ] CRITICAL/HIGH 対応

## 完了処理
- [x] design.md / decisions.md
- [ ] git commit + PR (別 PR・main 基点)
