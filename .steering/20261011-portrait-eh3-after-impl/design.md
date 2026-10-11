# design

本タスクは、実装のタスク（`.steering/20261011-portrait-eh3-impl/`）の後の確認と、研究者の決定に従った小さな変更だけを行う。

## 変更の対象

- 判断 2: `src-tauri/src/analysis/invitation.rs`（時間帯 `AllDay` を足して既定にする・夜間の判定を消す・テスト）、
  `src-tauri/src/eh3.rs`（テストの未知の値の例）、`src/components/InvitationSettings.tsx`（選択肢・文面）、
  稿 `experiments/20261011-portrait-eh3/preregistration-draft.md` §10.1。
- 設定のファイル `~/.gse/eh3_invitation.json` の書式は後方互換（既存の `core`・`extended`・`wide` はそのまま読める）。

## テスト戦略

- `cargo test --lib`・clippy・`scripts/check_invitation_surface.py`（と `--selftest`）・`tsc --noEmit`。
- 実機（Windows）は研究者の了承と手を借りて行い、元の壁紙（パスと SHA-256）に戻ったことを確かめる。
- 完了の前に code-reviewer ∥ security-checker と `/cross-review`。
