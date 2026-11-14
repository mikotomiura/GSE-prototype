# タスクリスト（設計 v2）

## 場面ごとの道具の対応（完了の前に照らす）
- Rust の実装: architecture-rules・rust-standards を読んでから。analysis/ に OS API・IO を置かない
- 描画の切り出し: typescript-standards。画面は実機で見る（ui-changes-need-eyes）
- 依存の追加（@napi-rs/canvas・numpy）: dependency-checker。実験の中に閉じる
- 実験: reproducibility-discipline・docs/experiment-tracking.md
- レビュー: code-reviewer＋security-checker を並列、完了時に /cross-review（Codex 込み・記録の本文と集計は送らない）
- 本人の記録は開かない（このタスクでは使わない）

## 1. Rust: desk.rs と gse-replay --handmark-windows
- [x] desk.rs: 日と区間・t0・種（§1.2）
- [x] desk.rs: 窓と除外の 3 つの理由（§1.3）
- [x] desk.rs: T1・T2（記録の feat）（§1.4）
- [x] desk.rs: A の特徴（§1.5）
- [x] desk.rs: 状態と場の流し・B_state・フレームの列（§1.6）
- [x] replay.rs: モードの引数・排他・usage・ヘッダ・注入（§1.1・§2）
- [x] replay.rs: --labels recomputed（run_replay を分割せずそのまま呼ぶ・既存のモードは変えない）
- [x] テスト（§7 の Rust の一覧）・clippy・cargo test --workspace

## 2. 描画の切り出し
- [ ] handmarkStageDraw.ts（buildWorld・drawFrame）
- [ ] HandmarkStage.tsx を呼ぶだけに
- [ ] scripts/handmark-stage-draw.test.mjs・tsc
- [ ] 実機で前後を見比べる

## 3. 実験 experiments/20261115-handmark-leak-desk/
- [ ] conditions.md（記録を開く前に固定・数値を研究者に確かめる）→ 先にコミット
- [ ] synth.py・pixels.mjs・stats.py・verdict.py・controls.py・timing.py・selftest.py
- [ ] run.sh・SEED・env.md・notes.md・requirements.txt・package.json と lock
- [ ] 段階 S0〜S5 を回す・計算時間を実測（2 時間を超えたら研究者に聞く）
- [ ] mutate.sh（変異がすべて赤）

## 4. 仕上げ
- [ ] code-reviewer＋security-checker・/cross-review
- [ ] 事前登録の改訂へ渡すもの（判断 3 の読み替え・条件）を記録
- [ ] df -h / を見て push・PR は研究者に確かめる
