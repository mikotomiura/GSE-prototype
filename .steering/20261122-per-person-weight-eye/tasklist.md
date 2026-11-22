# タスクリスト

## 準備
- [x] 引き継ぎを読む・worktree を切る（`~/GSE-prototype-weight-eye`・枝 `exp/gse-per-person-weight-eye`）
- [x] /start-task の問い（decisions 判断 1〜7）
- [ ] 論文 3 の S10・S13・S15 と、`synth.py`・`run_synth.py`・`pinned.py` を一次で読む（記号化・前半と後半に分けられる長さ・書き手の数）
- [ ] PoPETs の論文の特徴量と記号化を読み、論文 3 との異同を decisions に書く（判断 7）

## 設計（合成の前）
- [ ] design.md: 1 状態の遷移表での「共有モデルからのずれ」の定義（共有の当て方・縮み・行の重み）
- [ ] design.md: 目の候補 2〜3 案と、それぞれの統計量・帰無（入れ替え）
- [ ] 実験のディレクトリ `experiments/20261122-per-person-weight-eye/` と conditions.md（候補・選びの基準・偽陽性と検出力の数え方・「確実に拾う」の定義・Stop）
- [ ] attack-me 1 回目（prereg・Codex を加える）→ 直し → conditions をコミット（合成の前）

## 合成の較正
- [ ] 目のコードと selftest・変異（陽性対照が赤になる）
- [ ] 合成を回す（差なし・1e-3〜3e-2・5 人だけ）。seed と run_id を記録
- [ ] notes.md に候補ごとの偽陽性と検出力。選びの基準どおりに 1 案を選ぶ
- [ ] Stop の判定: 3e-2 を確実に拾えないなら、ここで止めて報告

## 凍結
- [ ] 実データの判定の基準を書く（何を「本人の中で安定した差がある」と読むか）
- [ ] attack-me 2 回目（Codex を加える）→ 直し
- [ ] 凍結のコミット（実データの読み込みより前）

## 完了処理
- [ ] /cross-review
- [ ] design.md の最終化・glossary
- [ ] 次のタスク（実データへの適用）の引き継ぎ
- [ ] push・PR は研究者に確かめる（docs だけなら [skip ci]）
