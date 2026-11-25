# タスクリスト —— 背景のステージの机上の検査・6 回のまとめ

## 準備
- [x] `a4_keytar.py` と CI を一次で確かめた（10-17・a4 は走っている → PR は出さない）
- [x] 6 回の requirement・design・notes・decisions と出発点（親タスク・最初の引き継ぎ）を全文で読む
- [x] grill（判断 1〜4）・ブランチ `docs/rhythm-stage-summary`（`docs/rhythm-stage-speed-shape` の上）

## 作る
- [x] `summary.md`（design の節 0〜9）
- [x] `check_summary.py`（bad 0）・変異 11 通りで落ちることを確かめ decisions に書く（判断 5）
- [x] `idea-section12-addendum.md`

## レビュー
- [x] `/cross-review` 1 巡目（自文書と 6 回の記録との矛盾）→ 直す（判断 6）
- [x] `/cross-review` 2 巡目（足した言い方の境目）→ 直す（判断 7）

## 完了処理
- [x] コミット・push（`docs/rhythm-stage-summary`・2026-10-17）
- [ ] PR: `a4_keytar` が終わってから、`docs/rhythm-stage-speed-confound` → `docs/rhythm-stage-speed-shape` → このブランチの順に、前のものが main に入るたびに rebase して出す（台帳の衝突は起点からの差分の和で解く）
- [x] `.idea` §12 に §12.5 として追記した（2026-10-17・研究者の指示で Claude が `C:\GSE-prototype\.idea\` に書いた・§12.4 と §13 の間）
