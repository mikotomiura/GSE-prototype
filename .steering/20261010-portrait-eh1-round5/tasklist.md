# タスクリスト

## 設計
- [x] 第 4 回の PR #343 が merge 済み・main の CI が緑であることを確かめる
- [x] 研究者に第 5 回の中身を聞く（判断 1・7 問）
- [x] requirement / decisions を書く
- [x] design §3（基準）を書く・Claude が足した細部を判断 2 に書く
- [x] 固定の前の `/cross-review` 1 巡目 → decisions 判断 3（研究者の決定 1 問）
- [x] 固定の前の `/cross-review` 2 巡目（1 巡目で足した規則の境界）→ decisions 判断 4
- [x] design §3 をコミットして固定する（下見・スモークより前）→ このコミット（ハッシュは次のコミットで書く）

## 計器
- [x] `experiments/20261010-portrait-eh1-round5/` を第 4 回から写す
- [x] `portrait.py`: 先読みの PC（`ahead_values`）
- [x] `checks.py`: 組ごとの検査器の条件・`--pilot`（先読みの PC・目標 0.05）・`--pilot-replicate`（反復の対照 12 本・目標 0.035・P 240・L300）・`--replicate`・第 4 回との照合
- [x] `selftest.py`: §3.7
- [x] `run.sh`: `--replicate`
- [x] 照合のスクリプト（`verify_verdicts.py`・`verify_round4.py`・反復の数え直し）を写して直し、変異で失敗することを確かめる

## 下見とスモーク
- [x] 本番用の下見（SEED + 1・v2・P 40・3 ラベル）→ 先読みの PC 8 本の λ（目標 0.05）
- [x] 反復用の下見（SEED + 2・v2・P 240・L300）→ 対照 12 本の λ（目標 0.035）
- [x] 選んだ λ を `config.json` に固定してコミット → §8
- [x] スモーク（本番と反復 1 回分）→ 所要を見積もる

## 本番・反復と仕上げ
- [x] 本番 v2（G-GEAR）→ design §8
- [x] 反復 20 回（G-GEAR・本番と別の時間）→ design §8
- [x] 判定を JSON の区間から基準の式だけで計算し直して照合する・第 4 回と照合する・反復を数え直す
- [x] 結果を読んで解釈する → notes・decisions
- [x] まとめの `/cross-review` 2 巡（判断 7・8）
- [x] 研究者に親の判断 8 を聞く（判断 9・親の判断 15）
- [ ] 完了時の出荷（push → PR → CI → merge）
