# タスクリスト

## 設計
- [x] 研究者に第 2 回の中身を聞く（判断 1・9 問）
- [x] requirement / design §3（基準）/ decisions を書く
- [x] design §3 をコミットして固定する（下見・スモークより前）

## 計器
- [x] `experiments/20261009-portrait-eh1-round2/` を第 1 回から写す
- [x] `portrait.py`: `lattice`・PC2 の作り直し・L300 と A300
- [x] `checks.py`: 2 ラベル・特徴の組 2・`recent` を全検査へ・帯ごとの発生率・材料の情報量・v1 の宣言
- [x] `selftest.py`: 変異を `lattice`・L300 へ
- [x] `run.sh`: `.exe`・`--jobs`
- [x] 下見は `run.sh --pilot`（`checks.py --pilot`）にした（別のスクリプトは作らない）

## 下見とスモーク
- [x] 下見（SEED + 1・v2・P 40・PC だけ）→ §8 に記録 → PC2 が働かない → 判断 3（神託 §3.11）
- [x] 神託を計器に足す
- [x] スモーク v2・v1 → 所要を見積もる

## 仕上げ
- [x] /cross-review 2 巡 → decisions（判断 4・5）
- [x] G-GEAR の引き継ぎ（`_handoff/next-session-portrait-eh1-round2-run.md`）
- [x] push（PR は出さない）
- [x] 本番 v2・v1（G-GEAR・`--jobs 8`・2026-10-09。実行の記録と逸脱は notes）
- [ ] 結果を読んで解釈する（別のセッション）
