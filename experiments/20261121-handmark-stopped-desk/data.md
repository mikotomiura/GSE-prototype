# 入力

- 合成の対照（`run.sh controls`）: 人の記録を使わない。止まりの多い合成（`scripts/synth_stops.py`・12 日・3 時間）と、漏れの机上の道具の合成（`../20261115-handmark-leak-desk/scripts/synth.py`・20 日・1.5 時間）。種は `SEED`。割付の表は `gse-handmark-table --seed <SEED> --s1-start-day 20400 --early-min 30 --early-max 30 --late-days 10`。
- 本人の段 1 の記録（`run.sh records`）: 漏れの机上の道具と同じ場所と表（`../20261115-handmark-leak-desk/data.md` の「本人の記録」・表の SHA-256 `e19e51c94f979c4c129bb998cc39ad42ee1f85e681fb205f4d71a8a9639e20da`）。記録は repo にも gse-dataset にも置かない。
- 回したら、`results/records/<回>/inputs.json`（写しの番号と SHA-256。元の名前は残さない）と `results/records/runs.txt` の行をここから指し、日の範囲（最初と最後の日付）だけをここに書く。

## 本人の記録（2026-11-22 に回した）

- 回: `20261122T133821Z_33994`（`results/records/runs.txt`・入力は `results/records/20261122T133821Z_33994/inputs.json`）。
- 日の範囲: 段 1 の記録の始まりで 2026-11-08 〜 2026-11-22（28 本）。解析に入った日は 11。
- 除いた入力: 起動直後に時計が 1976 年だった 2 本（SHA-256 `d132b307…abc7`・`df08a7ec…d2fa`）。理由と経緯は `.steering/20261121-handmark-stopped-state-prototype/decisions.md` 判断 15。止まった回 `20261122T131407Z_30794` は `runs.txt` に `aborted` として残す。
