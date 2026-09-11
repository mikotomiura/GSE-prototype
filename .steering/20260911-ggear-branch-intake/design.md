# 設計 — G-GEAR ブランチ取り込み

## アプローチ

⚠️ 引き継ぎメモの「5 本の PR に割る」は **`main..branch` の二点差分 (246 ファイル)** を
前提にしていた。実測 (`merge-base..branch` = 199 ファイル) と **衝突の実数 6 件** を踏まえ、
**2 本**に集約する (研究者承認済み)。

| PR | 内容 | 関門 (exit code で言える形) |
|---|---|---|
| **PR-A** `feat/ggear-intake-rust` | Rust 5 ＋ 下流の消費者 ＋ `docs/architecture.md` の改名追随 | `cargo test --workspace` / `gse-replay --snapshot` × 6 / `test_build_analysis_db` (skip=0) |
| **PR-B** `docs/ggear-intake-records` | steering 101 / experiments 36 / docs 30 / ADR 7 / scripts 7 / `.claude` 5 / `.github` / `.codex` / `.gitignore` | `secrets-filter-test.sh` / schema parity / 衝突 6 件の解決 |

★ 2 本は **ファイル集合が交差しない**ので、独立に merge できる。

## 変更対象 (PR-A)

- `src-tauri/src/analysis/{metrics,intervention,intervention_eval,probe_scheduler}.rs`
- `src-tauri/src/bin/replay.rs`
- `scripts/build_analysis_db.py` / `scripts/tests/test_build_analysis_db.py`
- `scripts/fixtures/analysis_join/metrics/{P101/windows/sess_a,P101/windows/sess_b,P102/macos/sess_c}.metrics.json`
- `docs/architecture.md` (★ branch が追随していなかった 2 行)

## 改名の実体 (ADR-024 D2)

`--metrics` 経路の outcome 構造体のみ:

| 旧 | 新 |
|---|---|
| `compute_recovered_at` | `compute_pflow_exit_at` |
| `DEFAULT_RECOVERY_WINDOW_MS` | `DEFAULT_PFLOW_EXIT_WINDOW_MS` |
| `recovered_episode_count` | `pflow_exit_episode_count` |
| `productive_manual_recovery_rate` | `pflow_exit_manual_gain_rate` |
| `self_recovery_without_paste` | `pflow_exit_without_receipt` |

★ 併せて `AWAY_IDLE_MS` (180_000) を `intervention.rs` の `pub const` に一本化し、
`probe_scheduler.rs` の 2 箇所の再定義を参照に置換 (ADR-024 D3)。

## テスト戦略と実測結果 (2026-09-11・macOS)

| 関門 | 結果 |
|---|---|
| `cargo build --bin gse-replay` | ✅ (`was_active` 警告は **main 由来**・本 PR は `lib.rs` を触っていない) |
| `cargo fmt --check` | ✅ |
| `cargo clippy --workspace --all-targets` | ✅ error 0 |
| `cargo test --workspace` | ✅ **599 passed / 0 failed** |
| `gse-replay --snapshot` × **6 本** | ✅ 全て exit 0 = byte-equal |
| ⚠️ **陽性対照** (snapshot を 1 バイト改変) | ✅ **exit 1** — 検査は空振りしていない |
| `test_build_analysis_db` (duckdb 有り) | ✅ **19/19・skip=0** |

⚠️ duckdb 無しだと **18/19 が skip** して「ほぼ何も検査しない緑」になる
(実測)。★ venv に入れて skip=0 で走らせた。

## `HMM_VERSION` bump は不要 — 根拠

★ 見立てではなく実測:

- `schema_dto.rs` / `analysis/engine.rs` / `analysis/features.rs` / `schema/current.json`
  の差分は **0 行**、`HMM_VERSION` の差分も **0 行**。
- ゴールデン **6 本すべて** で `--snapshot` が byte-equal (上表)。
- 改名は `--metrics` の outcome 構造体に閉じており、`FeatSnapshot` 経路に触れない。

## 下流の消費者 — 旧名 metrics.json は壊れない

★ branch の `build_analysis_db.py` は `LEGACY_FIELD_ALIASES` を持ち、旧名の
`metrics.json` も読める。⚠️ fixture `P104/windows/sess_d.metrics.json` は **main 側で
後から追加され旧名のまま**だが、実測で `(1, 0.0, 0.0)` と **生の値に一致**して入り、
黙って NULL にはならなかった。→ ★ sess_d の書き換えは不要。
