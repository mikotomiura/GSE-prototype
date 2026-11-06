# タスクリスト —— M5 の 1 本目（B1〜B3）

場面ごとに使うもの（完了の前に照合する）: `*.rs` → `rust-standards`・`architecture-rules`／logger・redaction・自己申告 → `data-privacy`／区切りの点検 → `code-reviewer` ＋ `security-checker` を並列／完了 → `/finish-task`（`/cross-review` を含む・Codex に記録の本文を送らない）。

## 準備
- [x] 計画の requirement・design・decisions・tasklist を読む
- [x] file-finder と impact-analyzer を並列で（R1 の後の main で行番号を引き直す）
- [x] 指摘の一次の確かめ（`SkipReasonKind`・replay の未知のキー・削除の台帳の約束と `invitation_condition` の先例）
- [x] design.md・研究者の承認

## B1 段 1 の層
- [ ] `s1.rs` と検査（`s1_requires_o1`・`s1_and_eh3_both_dropped`・`s1_marker_beats_env`・`env_value_exactly_1`）
- [ ] `lib.rs` の起動時の判定（判断 7）と `mod s1;`
- [ ] `meta` の `s1_mode`（`o1_meta_unchanged_without_s1_marker`・`s1_meta_fragment_order`）
- [ ] `o1::activity_label_allowed` の読み替え（`activity_label_none_for_o1_even_with_consent`・`activity_label_some_only_for_s1_with_ack`）
- [ ] `submission` の段 1 の同意の印の読み書きと検査

## B2 調停器
- [ ] `SplitMix64`・`sample_interval_ms` の公開範囲
- [ ] 定数と `ArbiterConfig`・`RandomFrame`
- [ ] `StrataDetector`・`NoAskPlan`
- [ ] `DayQuestion`・`DayState`
- [ ] `Arbiter::tick` と検査一式

## B3 行種と記録
- [ ] `SkipReason::Superseded`・`SkipReasonKind::Superseded`・`record_realtime_skip` で拒む
- [ ] `LogEntry` の 3 行種・整形・書き出し・`line_type`・検査
- [ ] `capabilities.rs`（`KNOWN_LINE_TYPES`・`emitterless` の両 OS）
- [ ] `redaction.rs`（`probe_frame` を外す・他は `"t"` で消える・検査）
- [ ] `schema_dto.rs` → `emit_schema` → `schema/current.json`

## 検証
- [ ] `cargo test --workspace`（test-runner）
- [ ] `cargo clippy --all-targets -- -D warnings`・`cargo fmt --check`
- [ ] ゴールデンの `gse-replay --snapshot`
- [ ] `emit_schema` の byte-equal
- [ ] code-reviewer ＋ security-checker を並列・HIGH に対応

## 完了
- [ ] `docs/functional-design.md` の追記（Step H）と glossary の要否
- [ ] 2 本目の引き継ぎ（`config_gated` への移し・登録の画面・JST と UTC の検査・駆動役）
- [ ] `/finish-task`（`/cross-review`）・push と PR は研究者に確かめる
