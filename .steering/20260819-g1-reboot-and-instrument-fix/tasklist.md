# タスクリスト

⚠️ 順序は handoff §9: **ADR-013 実装 → G-1 修正 → 検証 → 事前登録の凍結 → (募集 → 収集開始)**

## Phase 1 — ADR-013 (計器)

- [x] T1-1 `src-tauri/src/capabilities.rs` 新規 (`KNOWN_LINE_TYPES` / `unconditional()` / `THRESHOLD_GATED` / `app_version()`)
- [x] T1-2 `lib.rs` に `mod capabilities;`
- [x] T1-3 `logger.rs::write_meta_start` に `app_version` / `capabilities` を**末尾に**追記 (2 経路とも)
- [x] T1-4 `logger.rs` に `LogEntry::StarveWindow` + 整形
- [x] T1-5 `logger.rs::LogEntry::HookHealth` に `dropped_delta`
- [x] T1-6 `input/liveness.rs` に micro 帯の窓集計 (純関数)
- [x] T1-7 `lib.rs` 監視スレッドで窓集計を回して送出 (⚠️ `continue` より**前**)
- [x] T1-8 `lib.rs` に `dropped_at_last_line` を追加し `dropped_delta` を渡す
- [x] T1-9 `schema_dto.rs` 同期 → `emit_schema` 再生成

## Phase 2 — G-1 (運用)

- [x] T2-1 `decide_start_action` (純関数) + `StartAction`
- [x] T2-2 容量ガード (何も触る前に弾く)
- [x] T2-3 `start_session` を `StartAction` で分岐させる (⚠️ `RotateForRestart` はカウンタを増やさない)

## Phase 3 — テスト (= ADR-013 D3 acceptance)

- [x] T3-1 `capabilities_covers_every_line_type` (網羅)
- [x] T3-2 `ime_shadow_declared_on_windows` / `ime_shadow_not_declared_on_macos` (OS 対)
- [x] T3-3 `every_capability_has_a_reachable_emitter` (過大申告の逆アサート)
- [x] T3-4 `starve_window_omits_empty_windows` / `starve_window_counts_only_micro_episodes`
- [x] T3-5 `hook_health_semantics_unchanged`
- [x] T3-6 `dropped_delta_is_per_line_difference`
- [x] T3-7 `decide_start_action_*` (4 ケース)
- [x] T3-8 `double_start_rotates_and_closes_previous` (ロガー結合)
- [x] T3-9 `log_capacity_guard_rejects_when_full`

## Phase 4 — 検証 (Done 条件)

- [x] T4-1 `cargo test --workspace` exit 0
- [x] T4-2 ゴールデン 6 本 byte-equal
- [x] T4-3 `HMM_VERSION` が `0.4.0` のまま (⚠️ 動いたら Stop)
- [x] T4-4 `emit_schema` == `schema/current.json`
- [x] T4-5 `check_schema_parity.py --dataset <gse-dataset>` exit 0 (⚠️ `--dataset` 必須)
- [x] T4-6 `validate_blocks.py --selftest` 緑 (解析側の独立ゲート)
- [x] T4-7 `analyze.py --selftest` 緑

## Phase 5 — 事前登録とリブートの記録

- [x] T5-1 `preregistration.md` 第 17 版 (P010 をパイロットへ格下げ・凍結の言い方は「パイロットを参照したうえで新コホートのデータ前に凍結」)
- [x] T5-2 `config.json` + `analyze.py PREREG_REVISION` を 17 に
- [x] T5-3 `data.md` (確証標本 1/3 → **0/3**・P010 はパイロット)
- [x] T5-4 `protocol.md` / `data.md` に「提出番号は**試行の連番**」を明記 (判断 4)
- [x] T5-5 `consent.md` 記録項目表 + `participant-guide.md` に `starve_window` / `app_version`

## Phase 6 — 「G1 は実施中」記述の修正 (handoff §6 の 8 件)

- [x] T6-1 `ADR-011:69` / `:104`
- [x] T6-2 `ADR-012:83` / `:235` / `:282`
- [x] T6-3 `ADR-013:51,53,225,259` + **D5 ゲートを「G1 完了後」→「リブート前の停止期間」へ**
- [x] T6-4 `docs/architecture/domain-adapter-boundary.md:94`
- [x] T6-5 `docs/repository-structure.md` に `capabilities.rs` を 1 行
- [x] T6-6 `docs/architecture/task-adaptation-and-scope-gating.md §2.8` に判断 3 (相乗りさせない) を記録

## Phase 7 — 完了処理

- [ ] T7-1 `/review-changes` (code-reviewer + security-checker 並列)
- [ ] T7-2 `/cross-review` (⚠️ パス限定で回す)
- [ ] T7-3 `/finish-task`

## Phase 8 — レビュー指摘の反映 (2026-08-19・code-reviewer + security-checker)

- [x] T8-1 ⚠️★★★ **HIGH**: `capabilities` に第 3 群 `config_gated` を新設 (判断 11)
      — G1 では probe 系、盲検較正では intervention 系が**設定で 0 行**になり、
      `unconditional` のままだと「信号が無かった」という**偽の結論**が出る
- [x] T8-2 ⚠️★★★ **HIGH**: `record_session_meta` 失敗後の再押下で**ログを 1 行も書かない** (判断 12)
      — ⚠️ `has_any_data_row` は孤児を止めない (`session_start` 行があるファイルは通る) と実測
- [x] T8-3 **MEDIUM**: 窓集計を**ブロックに閉じる** (偽エピソード計上 / 窓のまたぎを解消)
- [x] T8-4 **MEDIUM**: `dropped_delta` の基準を**ブロック開始で引き直す** (ファイル境界をまたがせない)
- [x] T8-5 **MEDIUM**: `win_ms` に**実測の窓長**を載せる (公称 60_000 は分母の嘘になる)
- [x] T8-6 **MEDIUM**: `SessionStart` の送信失敗を**黙らせない**
- [x] T8-7 **MEDIUM**: 送信失敗時は `peak_starved_ms` / `prev_health` も**進めない**
- [x] T8-8 **MEDIUM**: `sum_lt30_ms` の意味を正す (⚠️ **静止した思考時間は含まれない**)
- [x] T8-9 **MEDIUM**: 「空窓を出さない」を*プライバシー統制として*数えない — 実際に効く統制へ書き直し
- [x] T8-10 **MEDIUM**: 在席判定に**マウス等が効く**ことを 3 文書に開示
- [x] T8-11 **HIGH(sec)**: 同意の**正本ソース** `Form_G1/GSE_G1_Form_Builder.gs` を更新
      (⚠️ 実フォームへの反映と突合は次セッション = 収集開始前ゲート)
- [x] T8-12 **LOW**: 「NDJSON を書くのは logger.rs だけ」を**テストで固定**
- [x] T8-13 **LOW**: Tauri の `capabilities/` との名前衝突を doc で明示
- [x] T8-14 ⚠️ **自己レビュー**: 同時押下の交錯を閉じる (`swap` をログロック内へ・判断 10)
- [x] T8-15 ⚠️ **自己レビュー**: 容量ガードを G1 限定に (通常運用の挙動を変えない・判断 9)
- [ ] T8-16 ⚠️ **D-1 (自動終了 × 押下の競合)** — ★ 本タスクでは直さない (`blockers.md`)

## Phase 9 — 最終検証 (全部緑)

- [x] `cargo test --workspace` **422 passed / 0 failed**
- [x] ゴールデン **6 本 byte-equal**
- [x] `HMM_VERSION` = **`0.4.0` 据え置き** (additive の裏付け)
- [x] `emit_schema` == `schema/current.json` (**削除・変更行 0 = 厳密に additive**)
- [x] `check_schema_parity.py --dataset` **exit 0**
- [x] `validate_blocks.py --selftest` / `analyze.py --selftest` **exit 0**
- [x] clippy: **新規コードに警告 0**
