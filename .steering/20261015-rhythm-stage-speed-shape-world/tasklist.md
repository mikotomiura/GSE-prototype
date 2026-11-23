# タスクリスト —— 揺れの形を分けた world

## 準備
- [x] `a4_keytar.py` と CI を一次で確かめた（10-15・a4 は走っている → 前の PR は出さない）
- [x] grill（判断 1〜8）・新ブランチ `docs/rhythm-stage-speed-shape`
- [ ] 前の PR: a4 が終わったら、`docs/rhythm-stage-speed-confound` の PR を出す（2 タスク）→ merge の後にこのブランチを main に載せ直す

## 設計と固定
- [x] design.md（world の式・PCr-level / PCr-var の写像と λ の較正・読みの合体・判定と読み方・自己検査と変異・所要の見積もり・`git_state` から results を外す）
- [x] 計器を `experiments/20261015-rhythm-stage-speed-shape-world/` に写して直す
- [x] selftest 0 failed・変異の結果を decisions に書く（536 / 128・変異 19 通り・試作で端から端まで通した・判断 9〜11）
- [x] `/cross-review` 1 巡目 → 直す（判断 12）
- [x] `/cross-review` 2 巡目 → 直す（判断 13・Codex の確かめ 判断 14）
- [x] 固定のコミット（どの下見 0 よりも前）

## 実行（回す前に Win32_Process・gh run list を notes に）
- [x] 下見 0（2 world × c100・c200）（f100 は天井）
- [x] go の段: 下見 1（λ: PC-stall・PCr-level・PCr-var）
- [x] go の段: スモーク
- [x] go の段: 本番（項目 1〜6 と読み）・`--compare`

## 報告
- [x] notes.md（`h(c)` の同じ段と並べる・限り）
- [x] `/cross-review` 2 巡（判断 15・16）
- [x] 引き継ぎ（`_handoff/next-session-rhythm-stage-after-shape-world.md`）
- [ ] PR（`a4_keytar` が終わってから・前のブランチの PR の merge の後に rebase）
