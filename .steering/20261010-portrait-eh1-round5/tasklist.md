# タスクリスト

## 設計
- [x] 第 4 回の PR #343 が merge 済みであることを確かめる（main の CI は確認中）
- [x] 研究者に第 5 回の中身を聞く（判断 1・7 問）
- [x] requirement / decisions を書く
- [x] design §3（基準）を書く・Claude が足した細部を判断 2 に書く
- [ ] 固定の前の `/cross-review` 1 巡目 → decisions 判断 3
- [ ] 固定の前の `/cross-review` 2 巡目（1 巡目で足した規則の境界）→ decisions 判断 4
- [ ] design §3 をコミットして固定する（下見・スモークより前）

## 計器
- [ ] `experiments/20261010-portrait-eh1-round5/` を第 4 回から写す
- [ ] `portrait.py`: 先読みの PC（`ahead_values`）
- [ ] `checks.py`: 組ごとの検査器の条件・`--pilot` の格子（目標 0.05 と 0.035）・`--replicate`・第 4 回との照合
- [ ] `selftest.py`: §3.7
- [ ] `run.sh`: `--replicate`
- [ ] 照合のスクリプト（`verify_verdicts.py`・`verify_round4.py`・反復の数え直し）を写して直し、変異で失敗することを確かめる

## 下見とスモーク
- [ ] 下見（SEED + 1・v2・P 40）→ λ を選ぶ（先読みの PC 8 × 2 目標・形の PC 4）→ `config.json` に固定 → §8
- [ ] スモーク（本番と反復 1 回分）→ 所要を見積もる

## 本番・反復と仕上げ
- [ ] 本番 v2（G-GEAR）→ design §8
- [ ] 反復 20 回（G-GEAR・本番と別の時間）→ design §8
- [ ] 判定を JSON の区間から基準の式だけで計算し直して照合する・第 4 回と照合する・反復を数え直す
- [ ] 結果を読んで解釈する → notes・decisions
- [ ] まとめの `/cross-review` 2 巡
- [ ] 研究者に親の判断 8 を聞く
- [ ] 完了時の出荷（push → PR → CI → merge）
