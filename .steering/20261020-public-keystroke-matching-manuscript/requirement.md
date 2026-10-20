# 公開データでの照合の論文 —— 結果に依存しない節を書く

## 背景

照合の論文（事前登録は OSF 10.17605/OSF.IO/Y5R7N・2026-10-13 に凍結）の本計算は G-GEAR で進んでいる（11/9 ごろの見込み）。
投稿の目標は PoPETs 2027 Issue 3（2026-11-30 AoE）。判断 59（`.steering/20261012-public-keystroke-matching-prereg/decisions.md`）で、
結果に依存しない節を結果の前に Mac で書くと決めた。引き継ぎは `.steering/_handoff/next-session-public-keystroke-matching-manuscript-pre-results.md`。

## ゴール

結果に依存しない節（脅威モデルの動機・序論・関連研究・方法・必須の 3 節）の草稿を、PoPETs 2027 のテンプレートで書き、MacTeX でビルドが通る状態にする。
このセッションでは、原稿の置き場と骨組み、脅威モデルの節（動機を含む）から始める。

## スコープ

### 含むもの
- 原稿の置き場 `papers/keystroke-log-release-matching/manuscript/`（研究者の選択・2026-10-20）と骨組み（main.tex・outline.md・BUILD.md・build.sh）
- 脅威モデルの節（現実に誰が・どの公開物と・どの候補の本文で照合できるか）
- 序論・関連研究・方法・倫理・open science・AI の利用（順に）
- 書誌の追加（citation-ssot・append-only）

### 含まないもの
- 本計算の結果を見る・書く（G-GEAR の作業）
- 事前登録の脅威モデル・攻撃者・手順の変更（凍結済み。変える場合は notes.md の逸脱）
- 投稿・PR の作成（研究者に確かめてから）

## 受け入れ条件

- [ ] 原稿が PoPETs 2027 のテンプレートで、build.sh によりエラーなくビルドできる
- [ ] 脅威モデルの節の主張が、outline.md の対応表で一次の出典か事前登録の節に接地している
- [ ] 公開物の文体の規則（papers/README.md: 英語・GSE と内部番号への言及なし）を _style_check.py で確かめた
- [ ] 脅威モデルの節を attack-me（stage: 原稿の外枠）にかけ、指摘を動機の書き方と限界の節に返した

## 関連ドキュメント

- `experiments/20261012-public-keystroke-matching/preregistration.en.md`（正の版）
- `docs/literature/20261012-public-keystroke-matching-novelty.md`・`20261012-public-keystroke-matching-prereg-search.md`・`20261013-length-unicity-and-dp-release.md`・`20261009-keystroke-release-reidentification.md`
- `papers/README.md`（公開物の規則）

## 運用メモ
- /reimagine 適用: No
- 理由: 原稿の執筆で、設計の判断は凍結済みの事前登録にある。章立ての選択は outline.md で研究者に見せる
