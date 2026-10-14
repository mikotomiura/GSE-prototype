# タスクリスト

## 設計（固定の前）
- [x] 中間の world の形を研究者と決める（第 2 回の判断 7）
- [x] `design.md`（第 2 回との違いだけ: 補間の式と 3 段・段ごとの下見 0 と天井の規則・L1800 の専用の対照・seed・費用の見積もり）
- [x] 固定の前の `/cross-review` 1 巡目 → 判断 2
- [x] 第 2 回の計器を写して直す（写し `2adf0fc3`・直し `c61f2bce`・`gen_sessions.py --world` の段・`stage.py` の L1800 の対照・`checks.py`・`ceiling.py`・selftest・`run.sh`・`config.json`・`SEED`）
- [x] 固定の前の `/cross-review` 2 巡目（直しの差分・計器を含む）→ 判断 4
- [x] selftest（gse-replay を使わない分・264 項目・0 件の失敗・変異 19 通りを捕まえた）
- [x] design と計器をコミット（どの下見 0 よりも前・固定・2 巡目の直しの Codex の確かめ → 判断 5）

## 段ごと（固定の後・t = 0.25 / 0.5 / 0.75）
- [x] 下見 0（天井の測り）→ 3 段とも `ceiling`（L300 の AUC(A_speed) 0.995〜0.999・design §8）。3 段とも判定不能
- [x] 下見 1・スモーク・本番 → `go` の段が無いので回さない（§3.0 の規則）

## 完了処理
- [x] notes（段ごとの判定を第 1 回・第 2 回と並べる・判断 6）
- [ ] notes の `/cross-review`（2 巡）
