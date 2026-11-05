# データ

- 停滞の分解（`../20261102-stall-decomposition/data.md`）の O1 と同じ 18 本（名前の日付 20261018〜20261101・書き込み中だった 1 本を除く）。フォーカスの行が 0 の 4 本を除いた 14 本を使う。
- 読むのは同実験の中間（`~/gse-o1-derived/20261102-stall-decomposition/`・repo の外）だけ。NDJSON（`~/Documents/GSE-sessions/`）は SHA-256 の照合にだけ使う。入力の SHA-256 の連結の digest は `../20261102-stall-decomposition/o1/results/provenance.json` と同じでなければ止める。
- 11-01 08:30 開始の本とそれ以降は開けない（H4a・H5 の確認に残す）。
- repo に入れるのは集計値だけ（時刻・ファイル名・日付・本文なし）。
