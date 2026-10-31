# 公開データの当てはめ 項目 1: AI を求める手前に停滞の信号が出るか

## 背景

- 少人数（n=3〜5）の設計（`.steering/20261031-gse-small-n-research-design/decisions.md` 判断 1〜18）で、人数の少なさで弱い箇所を公開データで補えるかを 1 つずつ確かめる（判断 18・研究者が 1 → 2 → 3 の順を選んだ）。
- 本タスクは項目 1。「詰まる前」の招待の契機は `friction_rising`（ADR-021 D4 の `level`）で定義する方針だが、値は未決（判断 13・ADR-040）。その根拠を、AI に助けを求めた時刻の手前の打鍵の振る舞いから探る。
- 引き継ぎ: `.steering/_handoff/next-session-gse-public-data-fit.md`（branch `docs/gse-small-n-research-design`）。
- worktree: `/Users/johnd/GSE-prototype-pdfit`・branch `docs/gse-public-data-fit-ai-request`。引き継ぎは origin/main から切るとしていたが、判断 1〜18 と文献カードが未マージのため `docs/gse-small-n-research-design` から切った。

## ゴール

CoAuthor・RealHumanEval・CS1（[V243]）について、
1. 利用条件と記録される出来事の種類を一次で確かめ、使えるか・どう使うかを決める。
2. 解析の条件（何を「AI を求めた」とするか・手前とは何秒前か・何なら成り立つと読むか）を計算の前にコミットする。
3. 本文を捨てて時刻とキーの種類だけにする変換をかけ、計算する。
4. 言える範囲を限って結果を書く（英語の作業・その課題での推定の振る舞い）。

## スコープ

### 含むもの
- 3 データの利用条件・出来事の種類の確認（サブエージェントの並列）
- 解析の条件の事前のコミット
- 変換と計算（`experiments/` の規約に従う）
- 結果の記録と言える範囲

### 含まないもの
- `friction_rising` の値の確定（事前登録の前に研究者が決める・判断 13）
- 招待の実装・ADR-040 Migration（別トラック）
- 項目 2〜7
- IME 論文 2 のブランチ・成果物の変更

## 受け入れ条件

- [ ] 3 データの利用条件と出来事の種類が、URL と逐語つきで記録されている
- [ ] 解析の条件が計算より前のコミットにある
- [ ] 計算は本文を含まない変換後のデータだけで行われている
- [ ] 結果に言える範囲と言えない範囲が書かれている

## 関連ドキュメント

- `docs/adr/ADR-040-*.md`・ADR-021 D4・ADR-024・ADR-030（stall onset）
- `docs/literature/20261031-non-human-substitutes-small-n.md`
- `docs/experiment-tracking.md`

## 運用メモ
- /reimagine 適用: No
- 理由: 実装の設計判断ではなく公開データの解析。解析の条件は研究者に AskUserQuestion で確かめる。
