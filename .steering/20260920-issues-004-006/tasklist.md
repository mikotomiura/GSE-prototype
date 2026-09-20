# タスクリスト

## Phase 0: 裁定（★ 着手条件・判断 26）

- [x] 一次資料を読む（issues/004.md・006.md 本文 / decisions.md 判断 25 #9 #10・判断 26 / `definitions-restop-t1d-t1c.md` / `feat_offline/`）
- [x] baseline の赤を実測（004 / 006 とも「必須フィールドが揃っていない」）
- [x] U1〜U4 を裁定（判断 1）
- [x] V1〜V5 を裁定（判断 2）・実装中に見つかった V6 を裁定（判断 3）
- [x] 配線の裁定（判断 4: `restart` は `stall_onset` の列を入力にする）
- [x] issues/004.md・006.md へ反映し `grep -c 未裁定` = 0 を実測
- [x] issue 006 の Allowed Files に `stall_onset.rs` を追加（V2）

## Phase 1: issue 004（`revision.rs`）

- [x] `revision.rs` を書く（純関数 ＋ tick 帰属 ＋ 単体テスト）
- [x] `mod.rs` へ `pub mod revision;` と `FeatureRow.revision` を足し配線する
- [x] `004-acceptance.sh` が OK

## Phase 2: issue 006（`restart.rs`）

- [x] `stall_onset.rs` に `condition_a_timeline`（`pub(super)`）を足す（⚠️ 検出は変えない）
- [x] `restart.rs` を書く（純関数 ＋ 単体テスト）
- [x] `mod.rs` へ `pub mod restart;` と `FeatureRow.restart` を足し配線する
- [x] `006-acceptance.sh` の fixture を差し替え（V3）・AC6 の注記を外す
- [x] `006-acceptance.sh` が OK

## Phase 3: 全体の検証

- [x] `001-acceptance.sh` の最上位キー集合を更新し OK
- [x] 002 / 003 / 005 / 007 / 008 / envelope の acceptance が OK のまま
- [x] `cargo test --workspace` / ゴールデン replay / `clippy -D warnings` / `fmt --check`
- [x] `blockers.md` 起票 20（V4 の追跡時間・E2 の過剰分割）

## Phase 4: レビュー

- [ ] `code-reviewer` ＋ `security-checker`（並列・opus・範囲/禁止/締切を明記）
- [ ] `/cross-review` 2 巡（⚠️ 予算ガードの状態を先に確認。止まったら skip 理由を明記）
- [ ] 指摘の是正と `decisions.md` への記録
- [ ] `/finish-task`
