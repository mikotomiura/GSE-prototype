# 設計 —— gse-docs-clarity

## アプローチ

1. 現行の主張の一次は ADR-040〜052 と `docs/preregistration-stage1.md`。新しい本文は、それらにある決定だけを要約し、各段落に根拠の ADR・実験のパスを付ける。新しい決定を docs で下さない。
2. 旧全文は `git mv` ではなく、`docs/history/research-positioning-2026-11-15.md` へ逐語で写し（先頭に「履歴である」の 3 行の頭書きだけ足す）、`diff` で本文の一致を確かめる。
3. ADR-053 で「現行版と履歴を分ける」作法を決め、ADR-047 Migration 1 を改める。ADR の本文は書き換えない。
4. 削除・移動は判断 6 の表のとおり。各ファイルの参照元を `git grep` で数え、ADR 以外は付け替え、ADR からの参照は `docs/history/README.md` の旧パスの表で辿る。

## 新しい research-positioning の章立て（案）

0. この文書について（現行版である・食い違えば ADR が優先・履歴の場所）
1. 位置づけ・headline・一言
2. 問いと主張（観測と申告の対応・乖離の条件、保留）
3. 対象と単位（停滞・中身・C4・日）
4. 研究の設計（段 1・段 2・手跡）
5. 推定の役（契機を作らない・HMM 0.5.0 の固定）
6. 人数と主張の上限（N-of-1・3 名の確認・採択後の再現）
7. 公開データの位置と、そこで分かったこと
8. 新規性として書ける範囲と数えないもの
9. 反証条件と、主張しないこと
10. 目指す世界（短く）
11. 証拠の今の状態（投稿した論文・実験のパス）
参照した書誌（[Pn]/[Vn]・references.md の番号のまま）

## 変更対象

- PR1: docs/research-positioning.md（書き直し）・docs/history/（新設）・docs/adr/ADR-053-*.md・docs/adr/README.md
- PR2: docs/agent-shared.md・docs/glossary.md・docs/architecture/gse-design-map.md・docs/mitou_submission/review-response-2026.md（新設）・削除と移動・参照元の付け替え・CLAUDE.md のリンク表
- PR3: docs/functional-design.md・docs/architecture.md・docs/repository-structure.md

## テスト戦略

- 逐語の写しは `diff`（頭書きを除いて一致）。
- リンク切れは、削除・移動したパスを `git grep` して ADR と history 以外で 0 件。
- 同じパスで書き直した文書は、節番号の参照（`research-positioning.*§`）も grep する。手順書・テンプレート・Skill とミラー（`.agents/`）は付け替え、過去の記録は §0 の規則で受ける（/cross-review 1 巡目の指摘）。
- 禁止用語（glossary）を新本文で grep。
- 新本文の各主張の根拠を一次（ADR 本文）で照合する（verify-before-claiming ルール 7・8）。
- /cross-review（Claude＋Codex）を各 PR で。
