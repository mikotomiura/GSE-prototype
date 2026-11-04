# タスクリスト

## 場面ごとの道具（完了前に照合する）
- 設計の判断 → grill（AskUserQuestion・1 問ずつ）・/reimagine（済み）
- 実験 → reproducibility-discipline（conditions を計算の前にコミット・seed・provenance）
- コード → 計算の前に code-reviewer、完了時に code-reviewer ＋ /cross-review（Codex には条件・コード・集計値だけ）
- サブエージェントに渡す前 → subagent-delegation
- 外部の文献に新しく依拠する（1-SE 規則）→ citation-ssot

## 準備
- [x] grill（寄せる先・決め方・格子・枝・タスク名）→ decisions 判断 1〜4
- [x] requirement.md
- [x] design.md（/reimagine 1 回・ハイブリッド）

## 条件と作り
- [x] reproducibility-discipline を読む
- [x] README.md・conditions.md・SEED・env.md・run.sh・mutate.sh
- [x] scripts/sim.py・selftest.py・check_mutations.py・report.py
- [x] selftest 緑（G6 を判断 5 で直した）・変異 5 つが赤・20 反復の通し（判断 6）
- [x] conditions とコードをコミット（計算の前・1dd2d082）
- [x] 計算の前の code-reviewer・指摘の直し・再コミット（判断 7）

## 計算
- [ ] 本計算（run.sh・主 72 セル ＋ 感度 s1・s2 ＋ cons）・provenance
- [ ] report（表・C4 の規則を当てた案の値・G7・G8）

## 記録
- [ ] notes.md（結果・案の文・読まないこと）
- [ ] 1-SE 規則の出典を references に（citation-ssot）
- [ ] 完了時の code-reviewer ＋ /cross-review・指摘の直し
- [ ] tasklist を閉じる・push（PR は研究者に確かめてから）
