# 設計（Claude の作業）

研究者の判断は decisions.md にある。

## 草稿

- ファイル: `docs/adr/ADR-040-handmark-input-not-recorded.md`（Proposed）。決定は D1〜D8。
- 構成: Context（何を決めるか・なぜ要るか・確かめたこと）/ Decision / Alternatives / Consequences / Migration / 見直しのきっかけ。ADR-038 の形に倣った。
- 引用: 外部の理論・文献には依拠しない（ADR-038 と同じ書き方）。OS の API の挙動は実測（20261020 design.md §1・§2）と survey-input-channels.md §6.5 の逐語に依る。

## 一次で確かめたこと

- ADR の番号: `git fetch` の後、origin の全枝とローカルの全枝に ADR-040 以降は無い。
- ADR-014 D4 の 2 行は 199・200 行（逐語を ADR の Context 2 に写した）。
- `POINTER_TX` は `input/observe.rs:59` にある。
- `LogEntry` は `#[derive(Debug)]` だけで、`Serialize` は derive していない（`logger.rs:818`）。行は `format!` と `json!` で組み立てる。`Serialize` を derive しているのは `schema_dto.rs` の `LogEntryDto`。
  - `20261020-handmark-multi-input` design.md §3 の「`LogEntry` は `Serialize` を derive しているので」は誤り。ADR には実物に合わせて書いた（型に `Debug` を付けないことで `LogEntry` に入らない）。前タスクの design.md は書き換えず、ここに記録する。
- 背景の層の窓がマウスを受けないことは `spike/handmark-stage` の `handmark_stage_spike.rs` 冒頭のコメントで確かめた。
- `20261015-tangibility-design` 判断 16 は小面の規則で、背景の層の打鍵の扱いではない。草稿の初版で打鍵の扱いの出典に挙げていたので外した。
