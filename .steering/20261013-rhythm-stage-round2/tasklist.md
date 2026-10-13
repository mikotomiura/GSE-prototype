# タスクリスト

## 準備
- [x] 引き継ぎ・第 1 回の notes・design・decisions 判断 16〜21・計器（`select_lambda`・`pilot`・`run.sh`・`config.json`）・下見 1 の値を読む
- [x] 研究者の決定: 下見 P 240・格子 0.025 刻み 0〜0.30・帯の両条件＋中央 0.055・SEED 20261013・名前（判断 1）

## 設計
- [ ] `design.md` の案（第 1 回との違いだけ）
- [ ] 固定の前の `/cross-review`（design の差分）→ 対応を `decisions.md` に
- [ ] 固定（どの結果よりも前にコミット）

## 計器と本番（固定の後）
- [ ] 第 1 回の計器を写して直す（`SEED`・`config.json`・`select_lambda`・下見の名前・selftest・`run.sh`・`data.md`・`env.md`）
- [ ] 計器の差分の `/cross-review`
- [ ] 下見 1（`--pilot`・P 240）→ `pc_stall.lam`・design §8
- [ ] スモーク（`--smoke`）
- [ ] 本番（`--main --jobs 16`・CI が走っていない時）→ `results/main/`・`notes.md`
- [ ] notes の `/cross-review`

## 完了処理
- [ ] 中間の world を研究者と検討する（判断 16 とぶつかりうる点を先に示す・第 1 回の判断 21）
