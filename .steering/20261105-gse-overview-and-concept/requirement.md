# gse-overview-and-concept —— 公開データの分析の俯瞰・GSE の文書の整理・コンセプトの問い直し

## 背景

2026-10-31 から 11-04 にかけて、公開データ（CoAuthor・KLiCKe・CS1 2019/2021）と O1 の記録で 13 本の分析を行い、ADR-040〜046 を決めた。結果は「停滞の手前で推定が上がる」前提を支持せず（AUC 約 0.5）、1 人ごとの学習の効きは構造を良くするとほぼ消え、停滞の中身・受領はデータで大きく違った。一方で上流の文書（research-positioning §1 の headline・wbs・functional-design）は古い前提のまま残っている（`docs/architecture/gse-design-map.md` §0）。研究者の依頼（2026-11-05）: 分析を絡めた俯瞰の整理、文書の整理、それに基づく GSE のコンセプトと内容の議論。

## ゴール

1. 俯瞰: 分析ごとの問い・結果・言えないことと、分析をまたぐ結論・食い違いを 1 つの文書にまとめる。
2. 文書のずれの一覧: 上流の文書と ADR-040〜046・分析の結果の食い違いを、ファイル・箇所ごとに挙げる。
3. コンセプトの議論: 問い・対象・推定の役割・介入（招待）・検証の形を全面に問い直し（ADR-040〜046 も見直しの対象）、案を並べ、codex-consult の第二意見を経て、研究者の決定を decisions.md に記す。
4. 決定に沿って上流の文書を直す（議論の後）。

## スコープ

### 含むもの
- docs/ と .steering/ の文書の作成・修正。ADR の起票（決定が ADR に当たる場合）。

### 含まないもの
- コードの変更・新しい計算（必要になったものは次のタスクの候補として書く）。
- ~/gse-public-data の中（実データ・書き手ごとの値）を開くこと。Codex に渡すのは俯瞰の文（集計値だけ）と案だけ。
- O1 の収集アプリに触れること。τ の格子の試験（`exp/gse-timeseries-tau-extend`・HP Z2 で計算中）の結果を議論の根拠にすること（結果が戻るまでは未了として扱う）。

## 受け入れ条件

- [ ] 俯瞰の文書（overview.md）がある
- [ ] 文書のずれの一覧（doc-drift.md）がある
- [ ] コンセプトの案と codex-consult の結果と研究者の決定が decisions.md にある
- [ ] 決定に沿って上流の文書が直り、code-reviewer と /cross-review を通っている

## 関連ドキュメント

- docs/architecture/gse-design-map.md（11-03 時点の状態の地図）
- docs/adr/ADR-040〜046
- docs/research-positioning.md §1・docs/wbs-verification-halfyear.md・docs/functional-design.md

## 運用メモ
- /reimagine 適用: No
- 理由: コードの設計ではなく議論のタスクで、案の比較は議論の中で複数案を並べて行う（第二意見は codex-consult・研究者の選択 2026-11-05）
