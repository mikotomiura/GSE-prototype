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

（段 1 の後に書く。方針は decisions.md 判断 3）
