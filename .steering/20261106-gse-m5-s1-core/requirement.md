# gse-m5-s1-core —— M5 の 1 本目: 段 1 の層・調停器・行種と schema

## 背景

- プローブの配線 M5（ADR-031・design-map §4・R2）の計画は `.steering/20261105-gse-m5-probe-wiring-plan/` にある（design.md v2 ハイブリッド・decisions 判断 0〜10・tasklist の B1〜B7）。
- 前提の R1（`feature/nudge-default-off`）は 2026-11-06 に main に入った（PR #388・`8edc2d4b`）。
- B1〜B7 は 20 ファイル近くに及ぶため、研究者の判断（2026-11-06・本タスクの decisions 判断 1）で 3 本の PR に分けた。本タスクはその 1 本目。

## ゴール

段 1 の層（`s1.rs`）・純粋な調停器（`analysis/probe_arbiter.rs`）・新しい行種と schema を、cargo test で閉じる形で main に入れる。画面と駆動スレッドは持たないので、本タスクの後も配布物の挙動は変わらない（印 `s1.mode` を置いたときに `meta` に `s1_mode` が出るだけ）。

## スコープ

### 含むもの（計画の tasklist の B1〜B3）

- B1: `s1.rs`（印 `s1.mode`・env `GSE_S1_MODE=1`・`resolve`・`OnceLock`・`is_s1()`）、起動時の `s1::set_mode`、`meta` の `s1_mode`、`o1::activity_label_allowed` の読み替え、`submission` の段 1 の同意の印の読み書き（関数まで）。
- B2: `analysis/probe_arbiter.rs`（`RandomFrame`・`StrataDetector`・`NoAskPlan`・`DayQuestion`・`Arbiter::tick`・仮の定数）とその検査。
- B3: `LogEntry::{ProbeFrame, ProbeSuppressed, DayQuestion}`・整形の純粋関数・`SkipReason::Superseded`・`probe_suppressed.reason` の値・`redaction.rs`（`probe_frame` を消さない）・`schema_dto.rs` → `emit_schema` → `schema/current.json`・capabilities の宣言（送出元が無い間は `emitterless`）。

### 含まないもの

- 2 本目（B4・B5）: 駆動スレッド・`s1_day_state.rs`・IPC コマンド・overlay の表示・トレイの終了の補助・`ProbeCard.tsx`・`DayQuestionCard.tsx`・登録の画面の同意の項目・実機での画面の確かめ。capabilities の `config_gated` への移しも送出元と一緒にこちら。
- 3 本目（B6・B7）: `gse-replay --probes`・`--day-questions`・段 1 の配布の門と launcher・文書・R3（gse-dataset の同期）。
- 仮の定数の確定（R6′）・同意文書（R4）。

## 受け入れ条件

- [ ] 計画の tasklist の B1〜B3 の検査（2 本目に回すと decisions に書いたものを除く）が名前どおりにあり、緑
- [ ] `cargo test --workspace`・`cargo clippy`・`cargo fmt --check` が緑
- [ ] 印の無い O1 の `meta` が byte-equal（`o1_meta_unchanged_without_s1_marker`）
- [ ] 既存のゴールデンの `gse-replay --snapshot` が byte-equal
- [ ] `emit_schema` の出力が `schema/current.json` と byte-equal
- [ ] `analysis/` に OS API と IO が無い
- [ ] 削除の台帳と data-privacy の文言が `probe_frame` を残すことと合うか確かめた（合わなければ止めて相談）

## 関連ドキュメント

- `.steering/20261105-gse-m5-probe-wiring-plan/`（design.md・decisions.md・tasklist.md の B）
- `docs/architecture/gse-design-map.md` §4、ADR-031・ADR-043・ADR-048・ADR-013

## 運用メモ

- /reimagine 適用: No
- 理由: 計画の段（2026-11-05）で /reimagine を済ませ、v2 ハイブリッドを研究者が選んだ（計画の decisions 判断 3）。本タスクはその設計の実装。
