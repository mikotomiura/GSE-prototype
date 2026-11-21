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
- [ ] 今のテストが緑であることを確かめる（基準）
- [ ] `state.rs`: `idle_since` と読み口・テスト（早送りとの一致・打鍵で消える）
- [ ] `stopped.rs`: `StoppedCfg`・`parse_stopped_cfg`・テスト
- [ ] `stopped.rs`: `ambient`（重みの和）・テスト（`grid_start` に依らない・節を共有しない・範囲・種）
- [ ] `stopped.rs`: `stopped_view`・`StoppedFrame`・`gate`・テスト（一定・境界の 4 つ・マウスだけ）
- [ ] `stopped.rs`: `replay_stopped` とライブ版・テスト（呼び方に依らない bits）
- [ ] `handmark_driver.rs`: 一時停止の待ちの列・`Effect::Stopped`・cfg・ライブと再生の一致のテスト（一時停止・日付・時計の飛び・切っているとき出ない）
- [ ] `handmark_stage.rs`・`lib.rs`: 環境変数・`handmark-stopped` の送り・`handmark_guard.rs` の一致の検査
- [ ] `handmarkStoppedDraw.ts`（3 つの形）・`HandmarkStage.tsx`（受けて重ねる）・`node --test`
- [ ] cargo test・clippy・tsc・フロントのテストが緑
- [ ] `docs/functional-design.md`・`docs/glossary.md`
- [ ] code-reviewer ∥ security-checker → 指摘の対応
- [ ] 手動の確かめ（研究者のデバッグ起動）

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
