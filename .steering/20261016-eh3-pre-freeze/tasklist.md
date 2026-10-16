# tasklist

## 段 1: F-1 の見比べの画
- [x] grill（判断 1〜3）
- [x] design.md 段 1
- [x] `render_f1_viewing_days`（`PortraitLayer` の経路・`write_png` 2560×1664）
- [x] day 1 の試し（2・3・4 時間）を見て組み直す（判断 4）
- [x] 8 日ぶんの画を `~/Pictures/gse-f1-viewing/` に書き出し、目で確かめる
- [x] `f1-viewing-notes.md`
- [ ] cargo test / clippy / fmt
- [ ] コミット（段 1）
- [ ] 研究者が 8 日見比べる → F-1 の選択と drift の扱いを decisions.md に

## 段 2: 分け方の検査（見比べの間に）
- [ ] design.md 段 2
- [ ] `PortraitRunner` の画を出す処理を戻り値にする（振る舞いは変えない）
- [ ] 振る舞いの検査（推定の値だけを変えても画と時刻が同じ）
- [ ] 参照の検査（`analysis/portrait/` の全 .rs・ファイル数の照合）
- [ ] 陽性対照（参照を 1 行・`p_stuck` で止める分岐を 1 つ → 赤）
- [ ] cargo test / clippy / fmt
- [ ] code-reviewer ∥ security-checker
- [ ] /finish-task（/cross-review・CI の Windows・macOS）
