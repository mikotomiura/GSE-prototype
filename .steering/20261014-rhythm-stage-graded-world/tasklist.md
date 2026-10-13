# タスクリスト

## 設計（固定の前）
- [x] 中間の world の形を研究者と決める（第 2 回の判断 7）
- [ ] `design.md`（第 2 回との違いだけ: 補間の式と 3 段・段ごとの下見 0 と天井の規則・L1800 の専用の対照・seed・費用の見積もり）
- [ ] 固定の前の `/cross-review` 1 巡目 → 対応を `decisions.md` に
- [ ] 第 2 回の計器を写して直す（`gen_sessions.py --world` の段・`stage.py` の L1800 の対照・`checks.py`・`ceiling.py`・selftest・`run.sh`・`config.json`・`SEED`）
- [ ] 固定の前の `/cross-review` 2 巡目（直しの差分・計器を含む）
- [ ] selftest（gse-replay を使わない分）
- [ ] design と計器をコミット（どの下見 0 よりも前）

## 段ごと（固定の後・t = 0.25 / 0.5 / 0.75）
- [ ] 下見 0（天井の測り）→ 天井の段はここで止めて判定不能として記録
- [ ] 下見 1（L300 と L1800 の λ）→ スモーク → 本番（CI と他の重い処理を先に確かめる）

## 完了処理
- [ ] notes（段ごとの判定を第 1 回・第 2 回と並べる）
- [ ] notes の `/cross-review`（2 巡）
