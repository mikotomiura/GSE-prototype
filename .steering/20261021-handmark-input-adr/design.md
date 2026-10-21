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

## /cross-review 1 巡目（`81e79f94..01d6f050`）と直し

- Codex は exit 0 で完走（指摘 3 件）。Claude 側は cross-reviewer の中でサブエージェントを起動できず、cross-reviewer 自身が code-reviewer の観点で一次資料を読んだ（code-reviewer を別に起動した独立のレビューではない）。
- 両者一致（HIGH）: D2 が禁じる行き先を D3 の検査が覆っていない（`analysis`・`fs`・ネットワーク・`packaging.rs`・payload）。→ D3 に「D2 の行き先 → 止め方 → 止められないもの」の表を置いた。窓への配信を `emit_to` に限ることも足した。Tauri の `emit` が `Serialize` を要ることは tauri 2.10.2 の `lib.rs:952` で確かめた。
- Codex だけ:
  - D3 の「列を持たない」と D4 の「固定数の枠」が衝突する。見本の波紋は `{x, y, t0}` の 6 枠のリングバッファ（`handmark-nature-multi.html:282-303`）。→ D4 に許す描画の状態（固定の少ない数・寿命は数秒まで・寿命を過ぎた枠は描かず読む口もない）を定め、D3 の列の検査はこの区別で見るとした。
  - 切った後に遅れて届いた値で跡が戻りうる。→ D4 に、取得を止めて配送待ちと切る前の値を捨てること、テストで固定することを足した。
- Claude だけ:
  - E-11 の書き方が `expression-channel.md:957` の追記（5 つのうち PC 側 UI と通知を足した）を落としていた。→ D5 を「E-11 のうち PC 側 UI の手跡の背景の層の入力だけを閉じる提案」とし、Migration に E-11 の行への追記を足した。
  - 描画の回数のような、入力で動く値の経路。→ D2 に入力の代わりの値として足した（spike の冒頭のコメントが根拠）。
  - OS の API の置き場所。→ 技術的制約 11 が許す `input/` に、O1 の `observe*.rs` とは別のファイルとして置くとした。
  - 窓の capability で返送を塞ぐ案。→ 採らなかった。spike の `capabilities/handmark-stage.json` 自身が「AppManifest がないので窓ごとにアプリのコマンドを止められない」と書いている。止められないものとして表に書き、窓ごとに止めるかは実物のタスクに残した。
  - LOW: 型に `Display` を足し、エラーの文の経路を「止められないもの」に書いた／判断の範囲を 1〜6 に直した／「逐語」を「逐語・記号と太字を除く」に直した／README に 3 つ目の見直しのきっかけを足した／判断 4 で実物のタスクに残すものを明記した。
