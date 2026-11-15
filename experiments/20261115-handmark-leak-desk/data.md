# 入力

- このタスク（2026-11-15）: 合成の入力だけ（`scripts/synth.py`・種は `SEED` から）。人の記録（公開データを含む）は使わない（判断 4）。
- 割付の表: 合成の対照では `gse-handmark-table --seed <SEED> --s1-start-day 20400 --early-min 30 --early-max 30 --late-days 10` で作る（日はすべて前期の扱い・種は `draw_seed(表の SHA-256, 日)`）。
- 次のタスク（本人の前期の記録）: 記録は repo にも gse-dataset にも置かない。場所・日の範囲・ファイルの SHA-256 の一覧は、回すときにこのファイルへ追記する（ファイル名は日付の形で、個人に結びつく名を書かない）。

## 本人の記録（2026-11-16 時点・まだ回していない）

- 置き場: GSE の既定のセッションのディレクトリ。段 1 の記録は `prepare_records.py` が最初の `meta` の `s1_mode` で選ぶ（O1 の記録は選ばない）。区間指定削除の台帳が同じ場所にあれば渡す。
- 割付の表（2026-11-16 に作った・判断 20）: 段 1 の配布のフォルダ（`s1.mode` の隣）の `handmark_assignment.json` と `.sha256`。
  - SHA-256: `e19e51c94f979c4c129bb998cc39ad42ee1f85e681fb205f4d71a8a9639e20da`
  - `gse-handmark-table --seed <研究者が保管> --s1-start-day 20764 --early-min 17 --early-max 17 --late-days 15`
  - `s1_start_day` 20764（2026-11-07・段 1 の開始 11-08 0:56 JST は 4:00 区切りでこの日）・`early_days` 17・`late_start_day` 20781（2026-11-24）・後期は 15 日（20781〜20795 = 12-08）。割付は 14 日のうち 7 日が「あり」。
  - 種は OS の乱数（64 ビット）で、repo の外に研究者が保管する。
- 回したら、`results/records/inputs_<回>.json`（写しの番号と SHA-256。元の名前は残さない）と `runs.txt` の行をここから指し、日の範囲（最初と最後の日付）だけをここに書く。
