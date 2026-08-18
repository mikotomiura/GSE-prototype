# タスクリスト — ADR-006 Phase 2a/2b

## 準備

- [x] ADR-006 / ADR-002 / domain-adapter-boundary / research-positioning §8-§9 / notes.md §5 を読む
- [x] engine.rs / task_kind / ゴールデンの現状を実測（subagent）
- [x] Wall の影響範囲を実測（subagent）→ 本タスクでは Out、事実を decisions.md に記録
- [x] grill で判断分岐 10 件を閉じる（decisions.md D-0〜D-10）
- [x] `git checkout -b feature/adr006-head-extraction`
      （★ CI は `push: [main, "feature/*"]` なので `feature/*` にする）

## 2a — 抽出（挙動不変・`HMM_VERSION` 不変）

- [x] `scripts/verify-extraction-parity.sh` を先に作る（変更前の基準出力を取る）
- [x] `analysis/heads/mod.rs` に `DomainInferenceHead` trait を追加
- [x] `analysis/heads/writing.rs` に `WritingHead` を追加
      （`BETA_WRITING_*` / `BETA_WRITING_LATIN_*` = 旧 `BETA_CODING_*` の改名・**値は不変**）
- [x] `analysis/mod.rs` に `pub mod heads;` を追加
- [x] `engine.rs`: `head: Arc<dyn DomainInferenceHead>` フィールド追加、`new()` は `WritingHead`
- [x] `engine.rs`: `calculate_latent_axes` を削除し `self.head.latent_axes()` へ置換
      （★ **式・演算順序・項順・clamp 位置を一切変えない**）
- [x] `engine.rs`: `apply_backspace_penalty` を `self.head.applies_backspace_penalty(ime_open)` へ
- [x] テスト `hmm_version_is_unchanged_by_extraction` を追加
- [x] `cd src-tauri && cargo test --workspace` 緑
- [x] `replay_snapshot_goldens_byte_equal` 緑（ゴールデン 4 本）
- [x] `scripts/verify-extraction-parity.sh` が exit 0（全 10 fixture 差分ゼロ）
- [x] `cargo run --bin emit_schema` → `schema/current.json` と byte-equal（schema 無変更）
- [x] `cargo clippy --workspace` の警告数が変更前と同数
- [x] `docs/glossary.md` に Writing head / β_writing_latin / DomainInferenceHead を追記
- [x] code-reviewer + security-checker を**並列**起動 → HIGH 1 / MEDIUM 8 を反映
- [x] `/cross-review`（Codex 独立レビュー）→ 4 件中 3 件を反映、1 件は D-6c に記録
- [x] コミット: `f31b8fb refactor(engine): β を Writing head へ移送し β_coding を β_writing_latin に改名する`
- [x] `679cbb8 chore(codex): cross-review 実行分の予算計上を反映する`（1 コミット 1 論理単位のため分離）

## 2b — 配線（挙動変更・`HMM_VERSION` → `0.4.0`）

- [x] `analysis/heads/mod.rs` に `TaskDomain` enum と `head_for()` を追加
- [x] `analysis/heads/coding.rs` に `CodingHeadV0` を追加
      （β は β_writing_latin と**同値の別定数**として二重定義・理由をコメントに明記）
- [x] `engine.rs`: `CognitiveStateEngine::new_for_domain(TaskDomain)` を追加（`new()` は Writing 既定を維持）
- [x] `lib.rs`: `logger::TaskKind` → `TaskDomain` 変換を境界に置き、engine 生成へ渡す
- [x] `bin/replay.rs`: `SessionMeta.task_kind` を読んで engine に渡す（`:257` の読み飛ばしを修正）
      / 欠落・未知は `Writing` へフォールバックし `tracing::warn!`
- [x] `logger.rs` + `schema_dto.rs`: `session_meta` に `head_id` を **additive** に追加
      （★ **`FeatSnapshot` には入れない** — ゴールデンが全滅する）
- [x] `engine.rs:45` を `"0.4.0"` へ / `:36-40` の SemVer コメントに MINOR の 1 行を追記
- [x] ゴールデン `tests/fixtures/vibe_coding_ime_mixed.ndjson` + snapshot を新規作成
      （IME on/off 混在 + IME on 区間で backspace streak ≥14）
- [x] `bin/replay.rs:2916` の `cases` に 5 本目を追加
- [x] テスト追加: `vibe_coding_uses_coding_beta_regardless_of_ime` /
      `creative_and_correspondence_route_to_writing_head` /
      `creative_latent_axes_match_writing_head` /
      `unknown_task_kind_falls_back_to_writing` / `hmm_version_is_0_4_0`
- [x] **既存ゴールデン 4 本が byte-equal のまま**であることを確認（★ ここが 2b の肝）
- [x] `cargo test --workspace` 緑 / clippy 新規ゼロ
- [x] schema: `cargo run --bin emit_schema > schema/current.json` →
      `PYTHONUTF8=1 python scripts/check_schema_parity.py --dataset /c/gse-dataset` →
      **gse-dataset 側にも cp してコミット**
- [x] `docs/glossary.md`: Coding head v0 / head_id を追記、`:157` の `hmm_version` を `0.4.0` へ、
      `:120` の「ベースライン (β)」の説明を head 所有の形に更新
- [x] `docs/wbs-verification-halfyear.md:232` の `HMM_VERSION=0.3.0` を更新
- [x] 差分が意図通りかを本ディレクトリに記録（ADR-006 Migration step 4）→ `diff-intent-2b.md`
- [ ] code-reviewer + security-checker を**並列**起動 / `/cross-review`
- [ ] コミット: `feat(engine): task_kind を head 選択へ配線し Coding head v0 を追加する (v0.4.0)`

## 文書

- [x] `docs/adr/ADR-002-domain-local-inference.md` を **Accepted** へ昇格
      （trait 範囲は `DomainInferenceHead` のみ・`infer -> WorkStateEstimate` は ADR-004 と同時＝D-8 を明記）
- [x] `docs/adr/ADR-006-task-kind-beta-wiring.md` に実施記録を追記
      （Creative の扱い D-6 / BS gate D-3 / bump 幅 D-4 / ゴールデン方針 D-5）
- [x] `docs/adr/README.md`: ADR-002 のステータス行を更新 /
      冒頭の凍結注記を「Phase1 は 2026-08-18 に収集打ち切りで終了」へ更新
- [x] `experiments/20260731-phase1-calibration-analysis/notes.md` §5① に
      「2026-08-18 に収集打ち切りで終了」を追記（★ 「収集継続」の記述が現状と食い違うため）
- [ ] コミット: `docs(adr): ADR-002 を Accepted に昇格し ADR-006 に実施記録を追記する`

## 完了処理

- [ ] `/finish-task`
- [ ] PR 作成（★ `git push` / `gh pr merge` は deny → 研究者に `! <command>` で叩いてもらう）
- [ ] CI 全ジョブ緑を確認

## 次タスクの候補（本タスクでは Out）

- T2 観測空間拡張（ポインタ動態 / 編集イベント / アプリ切替回数）— D-7
- `App.tsx` argumentative lock の解除 + Phase2 運用設計 — D-9
- Wall の扱い（PM-Q1〜Q7 の解除とセット）— D-10
