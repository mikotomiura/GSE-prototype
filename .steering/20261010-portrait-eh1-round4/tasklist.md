# タスクリスト

## 設計
- [x] 第 3 回の PR #340 が merge 済み・main の CI が緑であることを確かめる
- [x] 研究者に第 4 回の中身を聞く（判断 1・6 問）
- [x] requirement / decisions を書く
- [x] design §3（基準）を書く・Claude が足した細部を判断 2 に書く
- [x] 固定の前の `/cross-review` 1 巡目 → decisions 判断 3
- [x] 固定の前の `/cross-review` 2 巡目（1 巡目で足した規則の境界）→ decisions 判断 4
- [x] design §3 をコミットして固定する（下見・スモークより前）→ `1fa6c833`

## 計器
- [x] `experiments/20261010-portrait-eh1-round4/` を第 3 回から写す
- [x] `portrait.py`: 形の PC（大きさ）・多値の神託（5 本の帯）
- [x] `checks.py`: 形ごとの検査器の条件・`--pilot` で形の PC 4 本の λ の格子・第 3 回との照合
- [x] `selftest.py`: §3.7（`b505ab44`）

## 下見とスモーク
- [x] 下見（SEED + 1・v2・P 40・PC だけ）→ λ を 4 本選ぶ（すべて 0.35）→ `config.json` に固定 → §8（`62b951fe`）
- [x] スモーク → 所要を見積もる（本番の `checks.py` は約 2.8 時間）

## 本番と仕上げ
- [ ] 本番 v2（G-GEAR・計測の run・self-hosted CI と重ならない時間）
- [ ] 判定を JSON の区間から基準の式だけで計算し直して照合する・8 組の値を第 3 回と照合する
- [ ] 結果を読んで解釈する → notes・decisions
- [ ] まとめの `/cross-review` 2 巡
- [ ] 研究者に親の判断 8 の扱いを確かめる
- [ ] 完了時の出荷（push → PR → CI → merge）
