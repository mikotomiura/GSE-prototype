# 設計

## 段 1: F-1 の見比べの画

### アプローチ

`analysis/portrait/mod.rs` の手で回すテストに、`render_f1_viewing_days` を 1 本足す（`#[ignore]`・環境変数 `GSE_F1_VIEWING=<dir>` があるときだけ書く。既存の `render_portrait_samples` と同じ形）。

- 経路は配る物と同じにする: `PortraitLayer`（`start` → 毎秒 `second` → `end`）に、印 `eh3.mode` を `parse_assignment` で読んだ `Assignment`（`grammar`・`drift` だけ候補ごとに替える）と条件 `PortraitSeed` を与える。予定（5 分ごと・打鍵の最中と 60 秒以上の不在は飛ばす）・`active` の秒だけを貯めること・終わりの seed まで、実物の層を通る。既存の見本は生成器に 300 秒ずつ直接渡していて、この経路を通らない。
- 合成の列: 既存の見本と同じ形（書く区間 60〜300 秒・止まる区間 10〜120 秒・区間ごとに f1/f3/f4/f6 を変える）に、打鍵の時刻（書く区間の `active` の秒に 1 つ）を足す。長さは 1 日 1 セッション・4 時間（day 1 で 2・3・4 時間を出して見て決めた・判断 4）。日ごとに合成の列と生成器の seed を変える（day d の列の seed = 1000 + d、生成器の seed = 2000 + d）。
- 書き出し: `wallpaper::write_png` で 2560×1664（この Mac の画面）。実物も画面の大きさで書くので、16:9 の画布が縦に少し伸びる見え方まで同じになる。
- 出力: `day{1..8}-{候補}-day.png`（日中＝その日の最後に出た画）と `day{1..8}-{候補}-seed.png`（終わりの seed）。候補は `raw` / `lattice`（drift `none`）を raw → lattice → lattice → raw の各 2 日（判断 4）。`GSE_F1_HOURS` に複数の値を書くと、day 1 だけを 4 候補 × 各時間で書く（試し）。1 日ごとの更新の回数を `updates.tsv` に書く。
- 置き場所: repo の外（`~/Pictures/gse-f1-viewing/` を想定。合成の画なので個人の情報は含まない）。PNG はコミットしない。
- `f1-viewing-notes.md`: 日ごとの表（日付・候補・画のファイル名・「予想しない形が返るか」・「良し悪しに見えないか」・自由記述）と、置き替えの手順（システム設定 > 壁紙）。

### 変更対象ファイル

- `src-tauri/src/analysis/portrait/mod.rs` — テスト `render_f1_viewing_days` を足す（`#[cfg(test)]` の中だけ。配る物の振る舞いは変えない）
- `.steering/20261016-eh3-pre-freeze/f1-viewing-notes.md` — 新規

### 既存パターンとの整合

`render_portrait_samples`（同じファイル）と同じく、`#[ignore]` ＋ 環境変数で手で回す。合成の列の作り方も同じ。違いは、生成器ではなく `PortraitLayer` を通すことと、`write_png` で画面の大きさに書くこと。

### テスト戦略

- `cargo test --lib render_f1_viewing_days -- --ignored`（`GSE_F1_VIEWING` あり）で 16 枚が出ること、seed が空でないことを確かめる。環境変数なしでは何もしない（既存の見本と同じ）。
- 画は目で見る（Read で開いて、候補ごとに違う形が出ているか・真っ白でないか）。
- `cargo test --workspace`・`clippy`・`fmt --check`。

## 段 2: 分け方の検査

方針は decisions.md 判断 3、細部は判断 5。

### アプローチ

1. `PortraitRunner`（`lib.rs`）の出口を差し替えられるようにする（振る舞いは変えない）。
   - 壁紙のスレッドへの指示（`Show`・`Finish`・`Ack`）を、大域の `send_wall` を直接呼ぶ代わりに、持たせた受け口 `wall: Box<dyn FnMut(WallCmd)>` へ渡す。本番の受け口は `send_wall`。順序（終わりの `Show` の後に `Ack`）はそのまま保たれる。
   - セッションの種（`rand::random`）も持たせた関数から取る（本番は `rand::random`）。
   - `tick` が中で読んでいた `crate::recording::is_paused()` を引数にする（呼び出し側が渡す）。大域の一時停止は他のテストが並行して切り替えるので、検査の中で読まない。
2. 振る舞いの検査（`lib.rs` のテストのモジュール `portrait_separation_tests`）
   - 分析のループと同じ順で、合成の列（2 時間・書く区間と止まる区間・1 秒に 1 回）を `DayTracker`・`PortraitRunner` に通す（打鍵 → `on_press`・`assigned`・`presses`、`feat`、`tick`、最後に `end`）。受け口に届いた指示を `(時刻, 中身)` の列として集める。
   - 推定の欄（`p_flow`・`p_inc`・`p_stuck`・`raw_x`・`raw_y`・`ewma_x`・`ewma_y`・`obs`・`alpha`）だけを変えた 3 通り（停滞が高いまま・低いまま・秒ごとに乱れる）で、集めた列が完全に一致することを確かめる。
   - 空回りの防止: 画（`Show::Image`）が 3 回以上出ていること。対照として、f1 の値だけを変えると列が変わることも確かめる（比べ方が鈍くない）。
3. 参照の検査（同じモジュール）
   - 対象: `analysis/portrait/` の全 `.rs` と `src/wallpaper*.rs`（引き継ぎ §3 の「肖像」の範囲）。`include_str!` で読み、`#[cfg(test)]` より前・コメント行を除いた本文を、識別子に切って調べる。
   - 禁止: `engine`・`intervention`・`invitation`・`stuck`・`featsnapshot`・`loop_step` を含む識別子（大文字小文字を問わない）と、`p_flow`・`p_inc`・`raw_x`・`raw_y`・`ewma_x`・`ewma_y`・`level` に一致する識別子。
   - 許可リスト: `crate::` の参照は `crate::eh3`・`crate::analysis::portrait`・`crate::wallpaper`・`crate::submission::home_dir` で始まるものだけ。
   - ファイルの数の照合: ディレクトリを実際に読み、`.rs` の集合が検査の対象の一覧と一致しなければ赤（足したファイルの漏れを防ぐ）。
   - 対照: 同じ切り方で `lib.rs` を調べると `p_stuck` が見つかる（探し方が空回りしていない）。
   - 生成器の内部の関数 `level`（正規化した平均）は、禁止の語と同じ名なので `normalized_mean` に改名する（振る舞いは変えない）。
4. 陽性対照（コミットしない）: `analysis/portrait/mod.rs` に `use crate::analysis::invitation;` を 1 行足す → 参照の検査が赤。`PortraitRunner::feat` に `p_stuck` で材料を捨てる分岐を 1 つ足す → 振る舞いの検査が赤。結果を tasklist と decisions に書く。

### 変更対象ファイル

- `src-tauri/src/lib.rs` — `PortraitRunner` の受け口・種・`tick` の引数、呼び出し側、テストのモジュール `portrait_separation_tests`
- `src-tauri/src/analysis/portrait/generator.rs` — `level` → `normalized_mean`（改名だけ）

### テスト戦略

- 新しい 2 本と既存の肖像のテストが緑。`cargo test --workspace`・`clippy -D warnings`・`fmt --check`。
- 陽性対照で 2 本がそれぞれ赤になるのを見る。
- CI の Windows・macOS の両方で緑（`wallpaper_windows.rs` も `include_str!` の対象なので、macOS でも中身は読まれる）。
