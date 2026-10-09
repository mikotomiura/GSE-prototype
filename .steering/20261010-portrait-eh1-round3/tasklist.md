# タスクリスト

## 設計
- [x] 4 本のブランチを merge する（PR #338・研究者の決定: 先端の PR 1 本）
- [x] 研究者に第 3 回の中身を聞く（判断 1・9 問）
- [x] requirement / design §3（基準）/ decisions を書く
- [x] 固定の前の `/cross-review` 2 巡（基準の穴を探す）→ decisions 判断 3・4
- [x] design §3 をコミットして固定する（下見・スモークより前）

## 計器
- [ ] `experiments/20261010-portrait-eh1-round3/` を第 2 回から写す
- [ ] `portrait.py`: `clock60`・PC-cal・`ORCgap`・`ORCcum`・L1800 の特徴
- [ ] `checks.py`: E1-3 だけ・3 ラベル・判定不能の条件の置き換え・神託 6 本・`--pilot` で λ の格子
- [ ] `selftest.py`: §3.7

## 下見とスモーク
- [ ] 下見（SEED + 1・v2・P 40・PC だけ）→ λ を選ぶ → `config.json` に固定 → §8
- [ ] スモーク → 所要を見積もる

## 本番と仕上げ
- [ ] 本番 v2（G-GEAR）
- [ ] 結果を読んで解釈する → notes・decisions・親の判断
- [ ] まとめの `/cross-review` → decisions
- [ ] 完了時の出荷（push → PR → CI → merge）
