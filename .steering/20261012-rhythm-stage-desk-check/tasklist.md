# タスクリスト

## 準備
- [x] 引き継ぎ・親タスク（判断 1〜10）・EH1 第 2〜5 回の設計と計器を読む
- [x] 研究者の決定: 着手の時期・招待を含めない・秒未満も比べる（判断 1〜3）
- [x] 研究者の決定: 基準 A_speed・入力は有無と速さ・許容 0.03・パラメータの列（判断 4〜7）

## 設計
- [x] `design.md` の案（§9 に Claude が足した細部）
- [x] 新規性の検索 1 ラウンド（`/literature-review`・引き継ぎ §3.5）→ `docs/literature/20261012-rhythm-stage-novelty.md`（S-RN・[P472]–[P482]・`98f6ed13`）
- [x] 固定の前の `/cross-review` 2 巡（判断 8・11）→ 天井の下見 0・world v3・候補ごとの PC（判断 9・10）
- [x] 研究者が判断 7・9 の理由の訂正を了承（判断 12）
- [x] 研究者が §9 の細部を確かめる（判断 14・変更なし）
- [x] 下見 0 の計器（`experiments/20261012-rhythm-stage-desk-check/`・world v3・A・A_speed・`ceiling.py`・selftest）→ `4f50b7ed`
- [x] 計器の code-reviewer・`/cross-review` 2 巡（下見 0 を回す前・判断 15）
- [x] 下見 0 の 1 回目（v2 0.997・v3 0.884 で使える world なし → 研究者に戻す・`32acef1f`）
- [x] 研究者が world v4 を選ぶ（判断 16）→ v4 を足す（`5fcda976`）
- [x] 下見 0 の 2 回目（v4 0.705 で使える）→ §3.0 に追記して固定
- [x] world v4 の追加の差分の `/cross-review`（固定の後・判断 17・selftest に実測の項・§8 の 2 行目）
- [ ] 次の段: 下見 1（PC-stall 24 本の λ・design §3.9）→ `stage.py`・`twins.py`・`checks.py`・selftest の残り → スモーク → 本番（world v4）

## 計器と本番（固定の後）
- [ ] `experiments/<日付>-rhythm-stage-desk-check/` を作る（EH1 第 5 回から写す・`stage.py`・`twins.py`）
- [ ] selftest・スモーク
- [ ] 下見（PC-stall の λ）→ `config.json`
- [ ] 本番 → `results/main/`・`notes.md`

## 完了処理
- [ ] `/cross-review`（計器）・code-reviewer
- [ ] 親タスクの判断 3・5 の見直しの材料として結果を渡す（研究者）
