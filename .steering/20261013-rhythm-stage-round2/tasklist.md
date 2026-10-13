# タスクリスト

## 準備
- [x] 引き継ぎ・第 1 回の notes・design・decisions 判断 16〜21・計器（`select_lambda`・`pilot`・`run.sh`・`config.json`）・下見 1 の値を読む
- [x] 研究者の決定: 下見 P 240・格子 0.025 刻み 0〜0.30・帯の両条件＋中央 0.055・SEED 20261013・名前（判断 1）

## 設計
- [x] `design.md` の案（第 1 回との違いだけ・`b3f3a6ae`）
- [x] 固定の前の `/cross-review` 1 巡目（Codex 中 3・code-reviewer HIGH 1・MEDIUM 5・LOW 7）→ 判断 2・研究者の判断 3
- [x] 第 1 回の計器を写して直す（写し `65b95fc3`・直し `32ba3b48`。`SEED`・`config.json`・`select_lambda`・下見の名前・止まり・`--apply-pilot`・selftest・`run.sh`・`data.md`・`env.md`）
- [x] 固定の前の `/cross-review` 2 巡目（直しの差分・計器を含む。Codex P2 2・P3 1・code-reviewer MEDIUM 3・LOW 7）→ 判断 4・変異で selftest を確かめる
- [x] selftest（gse-replay を使わない分・174 項目・0 件の失敗）
- [x] 固定（どの結果よりも前にコミット）

## 計器と本番（固定の後）
- [x] 下見 1（`--pilot`・P 240）→ `pc_stall.lam`・design §8（止まらず・6034 s）
- [x] スモーク（`--smoke`・581 s・selftest 0 failed）
- [x] 本番（`--main --jobs 16`・CI が走っていない時）→ `results/main/`・`notes.md`（16261 s・selftest 0 failed）
- [x] notes の `/cross-review`（2 巡・判断 5・6）

## 完了処理
- [ ] 中間の world を研究者と検討する（判断 16 とぶつかりうる点を先に示す・第 1 回の判断 21）
