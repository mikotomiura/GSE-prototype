# 設計

## アプローチ

- IME 論文（`papers/ime-observation/manuscript/`）と同じ形: `main.tex` が `sections/*.tex` を読む。主張と根拠の対応は `outline.md`。
  テンプレート（PoPETs 2027 の submission-template-2027.zip・SHA-256 b1abbcc0…ea7d7・2026-10-20 取得）は置かず、BUILD.md に入手先と SHA-256 を書く。
- 章立て（12 頁の本文。倫理・open science・AI の利用は頁数に数えない）:
  1 Introduction / 2 Background and related work / 3 Threat model / 4 Data and release forms / 5 Attackers /
  6 Evaluation protocol / 7 Results（後で）/ 8 Discussion and limitations（一部は後で）/ 9 Conclusion。
- テンプレートの範囲の要件: 「first page must clearly state how the work is relevant to real-world privacy applications」→ 序論の最初の段落で公開の実例を示す。
- 引用: 公開物では `[Pn]`/`[Vn]` を使わず BibTeX の普通の引用。内部の番号との対応は outline.md（公開しない側に置くかは要確認 → outline.md は IME 論文と同じく papers/ にあり、内部番号を書かない）。

## 変更対象

- `papers/keystroke-log-release-matching/manuscript/` 新規
- `docs/references.md` に [V326] [V327] 追記（[V299]–[V325] は別の枝 docs/ai-fatigue-core2-discriminant が使っているので避けた）

## テスト戦略

- build.sh で pdflatex + bibtex を通し、エラー・未定義参照・overfull を数える
- `_style_check.py` で公開物の文体を確かめる
