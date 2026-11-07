# 設計の地図の古い行を直す

## 背景

ADR-049 のタスク（`.steering/20261107-gse-eh3-withdrawal/decisions.md` の「気づいたこと」）で、設計の地図 `docs/architecture/gse-design-map.md` の「介入（招待）」行と「O1 の見ていない期間」行が古いと分かった。地図は段 1 の作業の入口なので、古いままだと次のセッションが誤った状態を掴む。研究者が 2026-11-07 にこの作業を選んだ。

## ゴール

地図の状態の列を main（8d2357e2）に合わせる。

## スコープ

### 含むもの
- 「介入（招待）」行: 通常のモードの第 2 週の招待・Nudge の既定の無効化が main に入ったこと・EH3 の取り下げ。
- 「O1 の見ていない期間」行: PR #394 の結果。
- 「観測と記録」行の O1 の状態（同じ事実で古かった・O1 は 11-07 に終えた）。
- 冒頭の「確かめた main」の印。

### 含まないもの
- ほかの行の見直し・決定の列の書き換え。

## 受け入れ条件

- [ ] 3 行の状態が一次（architecture.md・pilot-runbook.md・main の log・unseen-confirm の notes.md）と合う。
- [ ] `python3 scripts/check_doc_lexicon.py` が違反なし。
- [ ] /cross-review を通す。

## 運用メモ
- /reimagine 適用: No
- 理由: 状態の記述を一次に合わせるだけ。
