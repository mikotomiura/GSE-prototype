# タスクリスト

## 準備
- [x] 調査でトリガー条件を特定 ([[project-wall-not-idle-trigger]])
- [x] Skill 参照 (intervention-design / rust-standards / typescript-standards)

## 実装
- [ ] intervention.rs: force_wall_decision() + 単体テスト
- [ ] lib.rs: FORCE_WALL + force_wall コマンド + get_intervention_decision 消費 + handler 登録
- [ ] Dashboard.tsx: 較正モード時のデバッグボタン → invoke force_wall

## テスト
- [ ] cargo test --workspace 緑
- [ ] --snapshot byte-equal (HMM 不変)
- [ ] tsc + vite build 緑
- [ ] 実機: ボタン→Wall→QR→解除→A2 捕捉 (手元検証)

## レビュー
- [ ] code-reviewer
- [ ] /cross-review (Claude ∥ Codex)
- [ ] CRITICAL/HIGH 対応

## 完了処理
- [x] design.md
- [ ] decisions.md (必要なら)
- [ ] git commit + PR (別 PR・main 基点)
