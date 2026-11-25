# タスクリスト

## 準備
- [x] 引き継ぎを読む・worktree を切る（`~/GSE-prototype-weight-eye`・枝 `exp/gse-per-person-weight-eye`）
- [x] /start-task の問い（decisions 判断 1〜7）
- [x] 論文 3 の S2〜S5・S10・S13 と、`synth.py`・`run_synth.py`・`pinned.py`・`data.split`・`ml.pool_units` を一次で読む
- [x] PoPETs の論文の特徴量と記号化を読み、論文 3 との異同を decisions に書く（判断 7: 照合の論文は書き手を見分けていなかった）

## 設計（合成の前）
- [x] design.md: 1 状態の遷移表での表と縮みの定義（細部は conditions.md が一次）
- [x] design.md: 目の候補 3 案と帰無（入れ替え）
- [x] 実験のディレクトリ `experiments/20261122-per-person-weight-eye/` と conditions.md（候補・選びの基準・偽陽性と検出力・門・止め）
- [x] attack-me（prereg・Codex を加える）round 1〜5（major → major → major → minor → minor で閉じた・判断 13〜36）→ conditions をコミット（合成の前）

## 合成の較正
- [x] 目のコードと selftest・変異（陽性対照が赤になる）— Mac の V1 は c7645298 で緑（判断 37・38）
- [x] HP Z2 の 1 回目は手順 2 で code_hash の食い違いで止まった → パスの区切りを直し、Mac の V1 を回し直した（code_hash e38db3af・判断 40）
- [x] HP Z2: 第 2 の帰無の P-HASH・P-XMACH・第 2 の帰無の選びの組（0b3e7cef・P-XMACH 緑）
- [x] Mac: 第 1 の帰無の選びの組 → summarize → choose.py（D5）→ E3 を選んだ（判断 41）
- [ ] 報告の組（Mac: report・HP Z2: report2）→ D6 の集計（門 55・間のセル・書き手の水準・論文 3 との並べ）と D9
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
