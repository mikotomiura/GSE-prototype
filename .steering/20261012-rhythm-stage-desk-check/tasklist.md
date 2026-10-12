# タスクリスト

## 準備
- [x] 引き継ぎ・親タスク（判断 1〜10）・EH1 第 2〜5 回の設計と計器を読む
- [x] 研究者の決定: 着手の時期・招待を含めない・秒未満も比べる（判断 1〜3）
- [x] 研究者の決定: 基準 A_speed・入力は有無と速さ・許容 0.03・パラメータの列（判断 4〜7）

## 設計
- [x] `design.md` の案（§9 に Claude が足した細部）
- [x] 新規性の検索 1 ラウンド（`/literature-review`・引き継ぎ §3.5）→ `docs/literature/20261012-rhythm-stage-novelty.md`（S-RN・[P472]–[P482]・`98f6ed13`）
- [ ] 研究者が §9 の細部を確かめる
- [ ] 固定の前の `/cross-review`（EH1 と同じく 2 巡）
- [ ] 固定（`design.md` をコミット）

## 計器と本番（固定の後）
- [ ] `experiments/<日付>-rhythm-stage-desk-check/` を作る（EH1 第 5 回から写す・`stage.py`・`twins.py`）
- [ ] selftest・スモーク
- [ ] 下見（PC-stall の λ）→ `config.json`
- [ ] 本番 → `results/main/`・`notes.md`

## 完了処理
- [ ] `/cross-review`（計器）・code-reviewer
- [ ] 親タスクの判断 3・5 の見直しの材料として結果を渡す（研究者）
