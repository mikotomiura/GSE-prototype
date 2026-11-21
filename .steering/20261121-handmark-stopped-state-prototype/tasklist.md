# タスクリスト

## 準備
- [x] 始める条件（回 1 が終わった・研究者が始めると決めた・判断 1）
- [x] ADR-056・設計案 §0.1・§4.4・判断 6〜10 を読む
- [x] 分かれ目を研究者に確かめる（判断 2〜5）
- [x] 実装を読む（`state.rs`・`handmark_driver.rs` の一時停止と刻み・`lib.rs` の打鍵と一時停止の経路）
- [x] architecture-rules・rust-standards・typescript-standards の要点
- [x] 既存パターンと影響範囲（file-finder ∥ impact-analyzer）
- [x] design.md → 承認（判断 6〜9）→ /reimagine → ハイブリッド（判断 10）

## PR-a: 状態・層・駆動役・窓・切り替え
- [x] 今のテストが緑であることを確かめる（基準）—— 回している途中で state.rs を変えたので、素の基準は取れていない。既存の手跡のテストは変更の上で全部通った（下の注）
- [x] `state.rs`: `idle_since` と読み口・テスト（早送りとの一致・打鍵で消える）
- [x] `stopped.rs`: `StoppedCfg`・`parse_stopped_cfg`・テスト
- [x] `stopped.rs`: `ambient`（重みの和）・テスト（`grid_start` に依らない・節を共有しない・範囲・種）
- [x] `stopped.rs`: `stopped_view`・`StoppedFrame`・`gate`・テスト（一定・境界の 4 つ・マウスだけ）
- [x] `stopped.rs`: `replay_stopped` とライブ版・テスト（呼び方に依らない bits）
- [x] `handmark_driver.rs`: 一時停止の待ちの列・`Effect::Stopped`・cfg・ライブと再生の一致のテスト（一時停止・日付・時計の飛び・切っているとき出ない）
- [x] `handmark_stage.rs`・`lib.rs`: 環境変数・`handmark-stopped` の送り・`handmark_guard.rs` の一致の検査
- [x] `handmarkStoppedDraw.ts`（3 つの形）・`HandmarkStage.tsx`（受けて重ねる）・`node --test`
- [x] cargo test・clippy・tsc・フロントのテストが緑
- [x] `docs/functional-design.md`・`docs/glossary.md`
- [x] code-reviewer ∥ security-checker → 指摘の対応（判断 11・HIGH 0・MEDIUM 5 と LOW 8 を直した）
- [x] 手動の確かめ（研究者のデバッグ起動）→ 試しのタスクへ回した（判断 12・段 1 の期間の外）

## PR-b: 机上の確かめ
- [ ] `desk.rs`・`bin/replay.rs`: `--stopped <cfg>` の出力の口（切っているときは今と同じ）
- [ ] `experiments/20261121-handmark-stopped-desk/`: 重ね描き（`drawFrame` → `drawStopped`）
- [ ] (i)〜(iii)（片側 5%・判断 9）を形 × W で回し、結果を decisions.md に（推測で書かない）
- [ ] 漏れの検査（ADR-051 D3・B′ と A）
- [ ] 今ある基層（`drift`）の扱いを (iii) の結果で研究者に確かめる

## 完了処理
- [ ] /cross-review 2 巡
- [ ] 次のタスク（研究者自身の試し・値の確定・ADR-056 の「決めずに残すもの」1）の引き継ぎ
- [ ] /finish-task

## 注

- 基準（2026-11-21）: 基準の `cargo test --lib handmark` を裏で回している途中に `state.rs` を変えたので、その回には変更が入っていた（280 件中 279 件が通り、落ちた 1 件は足したばかりのテストの算数の誤り）。手を入れる前の素の基準は取れていない。既存のテストは変更の上で全部通り、`StageState` と `bits()` は変えていない。
- 実装後（`1bfe092e`）: `cargo test --workspace` 1392 passed・2 ignored、clippy `-D warnings` 緑、`cargo fmt --check` 緑、tsc 緑、`npm run test:handmark` 54 passed。
