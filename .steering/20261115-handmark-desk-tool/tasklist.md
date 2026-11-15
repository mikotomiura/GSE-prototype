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
- [x] handmarkStageDraw.ts（buildWorld・drawFrame）
- [x] HandmarkStage.tsx を呼ぶだけに（切り出す前のコードと 12 組で命令の列が一致・対照で 0/12）
- [x] scripts/handmark-stage-draw.test.mjs・tsc
- [ ] 実機で前後を見比べる

## 3. 実験 experiments/20261115-handmark-leak-desk/
- [x] conditions.md（記録を開く前に固定・研究者が確認・固定の印を付けた）
- [x] synth.py・pixels.mjs・stats.py・verdict.py・controls.py・selftest.py・report.py・check_mutations.py（timing は controls.py の timing に入れた）
- [x] run.sh・SEED・env.md・notes.md・requirements.txt・package.json と lock
- [x] 段階 S0〜S5 を回す・計算時間を実測（JOBS=2 で約 4 時間・入れ子は回さない＝判断 13）
- [x] 変異（check_mutations.py・名指しした対照が赤）

## 4. 仕上げ
- [x] code-reviewer＋security-checker・/cross-review（Rust・描画・実験。実験の指摘は対照の後に直した）
- [x] 事前登録の改訂へ渡すもの: 回す回数と止める条件を S1-F5 に書いた（判断 14）。判断 3 の読み替え（T2）は conditions.md C1 にある
- [ ] df -h / を見て push・PR は研究者に確かめる

## 5. 本人の記録に回す（2026-11-16・引き継ぎ next-session-gse-handmark-records-run.md）
- [x] desk.rs: handmark_day の割付・量・toggles を読む・感度分析の日の印（C7・判断 15）・テスト
- [x] gse-replay --handmark-redactions（台帳）・テスト
- [x] stats.py: 主と感度分析を合わせる（combined）・selftest に配線の検査（変異で赤を確認）
- [x] prepare_records.py（meta.s1_mode で選ぶ・切れた最後の行を除く・名前は番号）
- [x] run.sh records（中間は終わったら・失敗しても消す・回の記録・同じ回の回し直しを止める）
- [x] 合成の記録で通し（9 本・切れた行 1・段 1 でない 1 本を除く・回し直しで exit 7・失敗の経路で中間が消える）
- [x] 事前登録 S1-F5（判断 14）
- [x] cargo test --workspace・clippy・fmt・emit_schema（差なし）
- [ ] code-reviewer＋security-checker・/cross-review（Codex 込み・記録の本文と集計は送らない）
- [ ] 回 1 を回す: 割付の表ができ、前期の記録が 8 日に届く見込みが立ってから（判断 16）
