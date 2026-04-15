# タスクリスト — Phase 1 Task 3: Counter Widget + 実機手動検証

## 準備
- [x] Task 1 (phase1-ground-truth) + Task 2 (phase1-metrics) が commit 済みであることを確認
- [x] `Dashboard.tsx` の既存構造・CSS・listen パターンを把握
- [x] Skill: `typescript-standards` 参照

## 実装
- [x] C3-1: `src/components/Dashboard.tsx` に counter state 追加
- [x] C3-2: `useEffect` で `listen("user_label_recorded", ...)` 購読 + cleanup
- [x] C3-3: 読み取り専用 counter widget UI（Flow / Inc / Stuck + ショートカット hint）
- [x] C3-4: 既存 Dashboard レイアウトに干渉しないスタイル調整

## テスト（ビルド + 回帰）
- [x] T-C1: `npx tsc --noEmit` エラー 0
- [x] T-C2: `cargo test --workspace` 全 PASS
- [x] T-C3: `cargo build --target aarch64-apple-darwin` warning 0
- [x] T-C4: `cargo run --bin gse-replay -- src-tauri/tests/fixtures/minimal.ndjson --snapshot src-tauri/tests/snapshots/minimal.json` byte-equal

## 実機手動検証
- [x] V3-1: `verification_log.md` 雛形を作成
- [x] V3-2: `~/.cargo/bin/cargo tauri dev` で起動、Input Monitoring 権限確認
- [x] V3-3: Dashboard で counter `Flow 0 / Inc 0 / Stuck 0` 表示確認
- [x] V3-4: `⌘⇧⌥F` 押下 → Flow counter が 1 に
- [x] V3-5: 2 秒以内に再押下 → デバウンスで 1 のまま
- [x] V3-6: 2 秒以上空けて再押下 → 2 に
- [x] V3-7: `⌘⇧⌥I` × 1 / `⌘⇧⌥S` × 1 で Inc=1 / Stuck=1
- [x] V3-8: セッション終了 → NDJSON 目視で meta 行 `hmm_version` + user_label 4 行確認（Phase 0 条件 5 消化も兼ねる）
- [x] V3-9: `gse-replay --metrics` で pretty-print 出力確認
- [x] V3-10: `gse-replay --metrics --json` で JSON 出力確認
- [x] V3-11: `verification_log.md` に各ステップの実測結果を記録

## レビュー
- [x] R-C1: `code-reviewer` 起動（Frontend + Phase 1 全体スコープ）
- [x] R-C2: `security-checker` 起動（外部入力経路を含むため必須）
- [x] R-C3: HIGH 指摘全対応、MEDIUM はユーザー判断

## ドキュメント
- [ ] D-C1: `docs/functional-design.md` に GT Counter Widget セクション追加（低優先、Phase 2 前に対応可）
- [ ] D-C2: `docs/glossary.md` に「Ground Truth / UserLabel」用語追加（用語は README.md / development-guidelines.md で既に言及済み、必要性要確認）
- [x] D-C3: Phase 1 全体の retrospective（`phase1-ground-truth/retrospective.md`）作成

## 完了処理
- [x] `phase1-ground-truth/requirement.md` の全受け入れ条件を `[x]` にクローズ
- [x] `phase1-ground-truth/decisions.md` に Phase 1 全体の主要決定（/reimagine v2 採用、3 分割 workflow 等）を記録
- [x] git commit: `feat(gt): dashboard counter widget + Phase 1 manual verification (Phase 1 task 3/3)`
- [ ] Phase 2a (Synthetic Friction 再設計) の着手可否判断（Go/No-Go: GT 付きセッション 10 件以上 + ベースライン記録） — **運用フェーズで継続、Phase 1 クローズ条件外**
