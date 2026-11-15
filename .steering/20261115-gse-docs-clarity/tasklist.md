# タスクリスト —— gse-docs-clarity

## PR1: research-positioning
- [x] 一次を読む: 現 research-positioning §1・§5・§8・§9、ADR-040〜052、preregistration-stage1
- [x] 旧全文を docs/history/ へ逐語で写し、diff で一致を確かめる
- [x] docs/history/README.md（旧パスの表）
- [x] 新しい本文を書く（章立ては design.md）
- [x] 主張ごとに一次で照合する
- [x] ADR-053 と adr/README.md
- [x] /cross-review（Codex を加える）1 巡目・指摘 8 件を採用（判断 7）
- [ ] コミット（push と PR は研究者に確かめる）

## PR2: 周辺の文書と削除
- [ ] 削除・移動の候補ごとに参照元を grep
- [ ] wbs・eh3-distribution-tag・design-history.ja を削除、design-history・calibration-smoke-runbook・architecture の 3 本を履歴へ
- [ ] 参照元（ADR 以外）を付け替える
- [ ] 節番号の残り: agent-shared:28（§1 冒頭の改訂ブロック）・architecture/personalization-and-online-learning:238,248・gse-v2-overview:55（移すなら不要）・expression-channel:732・intervention-decision-engine:165（移すなら不要）
- [ ] agent-shared・glossary・gse-design-map を現行へ
- [ ] 未踏の不採択コメントの対応表（内部の追跡表）
- [ ] /cross-review・コミット

## PR3: functional-design・architecture
- [ ] 現行とのずれの洗い出し
- [ ] 直す
- [ ] /cross-review・コミット

## 場面ごとの道具（完了前に照合する）
- 文書の差分のレビュー → /cross-review（code-reviewer＋Codex）
- 事実の断定 → verify-before-claiming
- 引用 → citation-ssot（番号は既存のまま・新規は append）
