# タスクリスト

## 準備
- [x] 実機セッション (gse_20260623_055742) で原因特定 (全画面オーバーレイがクリック奪取)
- [x] Skill 参照 (typescript-standards / intervention-design)・Overlay/ProbeCard/App.css 調査
- [x] 非ブロック方針をユーザー承認 (AskUserQuestion)

## 実装
- [x] ProbeCard を右上配置 + probe-card-pop スライドイン
- [x] App.css に @keyframes probe-pop-in
- [x] Overlay 統合表示モード effect (Wall=全画面 / probe単独=box非ブロック / nudge=現状 / なし=hide)
- [x] cross-review CRITICAL/HIGH 対応 (明示 fullscreen 復元・cancelled ゲート・physical 座標・高さ clamp)

## テスト
- [x] tsc + vite build 緑
- [x] cargo test --workspace 緑 (Rust 不変 = main)
- [ ] 実機 (Win) で右上スライドイン・クリック透過・Wall 全画面維持を確認 (GUI 手元検証)

## レビュー
- [x] code-reviewer (CRITICAL/HIGH 対応済)
- [ ] /cross-review (Claude ∥ Codex)
- [ ] CRITICAL/HIGH 対応

## 完了処理
- [x] design.md / decisions.md 作成
- [ ] git commit + PR (別 PR・main 基点)
