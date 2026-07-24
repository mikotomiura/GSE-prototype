# tasklist

## ③ RQ-2 gate 成果の SSOT 化 (additive doc)
- [x] 落合カード `docs/literature/20260724-agentic-coding-overreliance-detection.md` (9 カード)
- [x] `docs/references.md` に [V45]-[V53] append (dedup 済・renumber なし)
- [x] `docs/literature/_index.md` に行追加

## A Epic2 安全網: snapshot 回帰の cargo test 化
- [x] `snapshot_path()` helper 追加
- [x] `replay_snapshot_goldens_byte_equal` test 追加 (minimal + phase1_ime_heavy + category_coverage)
- [x] `cargo test --bin gse-replay` 全パス確認 (23 passed)

## B golden 追加 (現行挙動の記録)
- [x] `tests/snapshots/phase1_ime_heavy.json` 生成 (6 snaps・round-trip exit 0・決定論)
- [x] `tests/snapshots/category_coverage.json` 生成 (2 snaps・round-trip exit 0・決定論)

## D scripts/repro.sh (再現性)
- [x] `scripts/repro.sh` 作成 (来歴固定 + run-calibration-cohort.sh 委譲)
- [x] dry-run / 実走 smoke (合成 dataset・verdict=data_insufficient・provenance 生成)

## 完了処理
- [x] 凍結対象の変更ゼロ検証
- [ ] 論理単位でコミット → PR (③ doc / A+B test+golden / D script)
- [ ] cross-review (code-reviewer + codex) は PR 前にメインで判断
