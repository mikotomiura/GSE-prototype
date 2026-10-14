# タスクリスト

## 設計（固定の前）
- [x] world の形を研究者と決める（判断 1）
- [x] `design.md`（中間の world との違いだけ: 揺れの式と 3 段・段の名前・seed）
- [x] 固定の前の `/cross-review` 1 巡目（design）→ 判断 2
- [x] 中間の world の計器を写して直す（`gen_sessions.py --world confound`・段の名前と値・`config.json`・`SEED`・selftest）
- [x] 固定の前の `/cross-review` 2 巡目（計器を含む）→ 判断 3・直しの Codex の確かめ → 判断 4
- [x] selftest（gse-replay を使わない分・343 項目・0 件の失敗・変異 17 通り）
- [x] design と計器をコミット（どの下見 0 よりも前・固定 → 判断 5）

## 段ごと（固定の後・c = 0.5 / 1 / 2）
- [ ] 下見 0（天井の測り）
- [ ] `go` の段: 下見 1 → スモーク → 本番

## 完了処理
- [ ] notes（段ごとの判定を前の 3 回と並べる）
- [ ] notes の `/cross-review`（2 巡）
