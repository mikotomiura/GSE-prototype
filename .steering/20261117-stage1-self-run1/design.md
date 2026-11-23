# 設計

## アプローチ

1. 回を始めずに日数を数える: `run.sh records` と同じ写し → gse-replay `--handmark-windows` を scratchpad の 700 のディレクトリで走らせ、窓の行の `day` ごとの数だけを数えて中間を消す（`runs.txt` には書かない・AUC は計算しない）。
2. 記録の重なりで止まる道具を直す（判断 1）。
3. 8 日に届いた翌日・遅くとも 11-21 に、`next-session-gse-handmark-records-run.md` の「回し方」で回 1 を回す（判断 2）。

## 変更対象

- `src-tauri/src/analysis/handmark/desk.rs`: `DeskFile::last_event`・`resolve_overlaps`・テスト 4 本・`DESK_VERSION` hm-desk-3
- `src-tauri/src/bin/replay.rs`: 重なりの検査を `resolve_overlaps` に置き換え・要約に `ends_clamped`
- `experiments/20261115-handmark-leak-desk/notes.md`: 道具の直しの節

## テスト戦略

- 単体: 切る場合・行が重なって止める場合（始まりちょうどを含む）・重ならない場合・`last_event` が `session_end` を含まないこと
- 陽性対照: 止める条件を `>` に緩めると止める側のテストが赤になる（確かめた）
- 本人の記録で、直した道具だけで 4 本が切られ、日数が数えられること（件数だけ）
- `selftest.py` が通ること
