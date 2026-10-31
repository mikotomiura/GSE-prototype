# 設計

## 変更
- `src/components/RecordingControls.tsx`
  - 宣言の行の文字を `paused ? "止めています" : "記録中"` にする。
  - 「選ぶ・変える」を `paused` のとき押せなくし、下に「作業の種類は、記録を再開してから選べます。」を出す。
  - 種類の欄は `pickingTaskKind && !paused` のときだけ描く。止めたら `setPickingTaskKind(false)`（useEffect）。
- `src-tauri/src/logger.rs`: `RecordingPause` の腕のコメントを実装に合わせる。

## 確かめ方
- 開発版を `GSE_O1_MODE=1`・識別子 `com.johnd.gse-next-pause-row`・HOME と GSE_DATASET を一時フォルダにして起動（`probe/run-dev-o1.sh`）。研究者の O1（`~/.gse`・`~/Documents/GSE-submissions`）と分ける。`GSE_O1_MODE` は自動起動を登録しない（`autostart.rs`）。
- `probe/axclick.swift`（前のタスクの写しに `texts` を足した）で、pid から文字とボタンを読み、押す。押す直前にその座標の一番上の窓が同じ pid かを確かめる。
- 記録は一時フォルダの NDJSON の行の種類と時刻だけを数える。
