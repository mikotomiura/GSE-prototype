# タスクリスト（手跡の PR 3・v2 格子の場）

## 場面ごとに使うもの（完了前に照らす）

| 場面 | 使うもの |
|---|---|
| 実装 | 実装役（Sonnet・general-purpose・model を明示）。報告はコードと照らしてから事実として扱う（PR 1 判断 10） |
| 守りの確かめ | 自分で変異を入れて赤を見る（memory: guard-test-must-stub-guarded-action） |
| 区切りの点検 | code-reviewer ＋ security-checker を並列 |
| 完了時 | /finish-task の中で code-reviewer・security-checker・/cross-review（Codex を加える） |
| 画面 | PR 1 判断 11 の段取り（研究者が gse-next を止める・一時の HOME）。AX で押さない |
| schema | emit_schema の一致・gse-dataset の同期の PR（origin/main から切る・memory: schema-parity-stale-local-dataset） |
| 容量 | ビルドの前に `df -h /`。足りなければマージ済みの worktree の `cargo clean` |

## 準備
- [x] 関連する docs・ADR-050／051・PR 1 の判断を読む
- [x] file-finder・impact-analyzer で既存の実装と影響範囲を調べる
- [x] design.md（v1 → /reimagine → v2 を採用）

## 実装 A（OS 非依存・1 コミットずつ）
- [x] A1 `analysis/handmark/trace.rs`: `TraceField`（16 × 10 × 3・f32・16ms の格子・半減・上限・世代・押下の始まり）と単体テスト（決定性・まとめて進めても同じ・陰性の対照・戻る・8 秒で 0・上限）
- [x] A2 `analysis/handmark/trace_replay.rs`: `pointer_bin` → 合成の一点（種・バケットの代表の距離・縁で跳ね返る・等間隔の押下）と `replay_trace`・テスト
- [x] A3 `input/handmark_pointer.rs`: `PointerSample`（`Debug`・`Display`・`Serialize` なし）・正準の箱への写し
- [x] A4 `handmark_pointer_thread.rs`: スレッドの純粋な部分（読む口・送る口・時計を引数）。Atomic の門（開閉・入れ切り・世代）・一時停止で読まない・閉じている間は待ちを延ばす・33ms の写し・全部 0 なら 1 回で止める・波紋の種。ライブの経路と `replay_trace` の一致のテスト
- [x] A5 入力ごとの入れ切りの記録: `day.rs`（`input_toggles`・上限・区間の削除）・`handmark_store.rs`（状態ファイルの `cursor_off`・`click_off`・起動での復元・書けなければ切った側・scrub）・`logger.rs`（行と固定のテスト）・`schema_dto.rs`・`schema/current.json`・`redaction.rs`
- [x] A6 `handmark_driver.rs`: 入力ごとの入れ切りの口・`Effect::PointerGate` と行き先（記録へは向かわない）・テスト
- [x] A7 `handmark_guard.rs`: ポインタのファイルを走査の一覧の末尾に足す・型／ソース／記録の側の逆向き／macOS の読み／列／振る舞いの検査・陽性対照

## 実装 B（macOS の配線と窓）
- [x] B1 `input/handmark_pointer_macos.rs`（cfg）と `input/mod.rs`
- [x] B2 `lib.rs`: ポインタのスレッドの起動（macOS だけ・cfg）・Atomic の受け渡し・`handmark_stage::emit_trace`／`emit_ripple`・トレイの押下
- [x] B3 `tray.rs`: 「カーソル」「クリック」のチェックの項目（「やめる」の上・窓が出ている日だけ）・純関数の plan／after のテスト
- [x] B4 `src/components/handmarkStageTrace.ts`（波紋の枠・受け取りの判定・場の補間）と `HandmarkStage.tsx`（場を草と粒に当てる・波紋）
- [x] B5 `scripts/handmark-stage-trace.test.mjs`（試作の件の写し・ホイールは PR 5 へ・補間の件）・`package.json` の `test`・`ci.yml` の frontend-check に step

## テスト・確かめ
- [x] fmt・clippy（`-D warnings`）・`cargo test --workspace`・`emit_schema` の一致・`tsc --noEmit`・`node --test` を自分で走らせ直す
- [x] 変異で赤を見る（読みの後に `tracing` を足す・`PointerSample` に `Debug`・世代が進んでも場を消さない・一時停止を見ない・区間の削除で `input_toggles` を消さない・格子の進め方を描画の回数に依らせる）
- [ ] gse-replay の snapshot（HMM は変えないので一致を見るだけ）
- [x] 区切りの点検: code-reviewer ＋ security-checker
- [x] 画面の確かめ（研究者と・格子の粗さを判定）

## ドキュメント
- [x] `docs/functional-design.md` に手跡のポインタの入力を足す
- [x] glossary（新しい語があれば）

## 完了処理
- [ ] /finish-task（/cross-review を含む）
- [ ] gse-dataset の同期の PR
- [ ] push・PR は研究者に確かめてから
