# 重要な設計判断

## 判断 1: 未マージの事前登録の枝 2 本を先に取り込む

- **判断日時**: 2026-11-21（研究者が AskUserQuestion で選んだ）
- **背景**: `docs/preregistration-stage1.md` を直した枝が 2 本、main に入っていなかった。`docs/gse-stage1-prereg-revision`（11-05・ADR-047・048 の項目を足す・値は空欄）と `exp/gse-stage1-penalty-synthetic`（11-04・S1-E8 の罰の強さを τ = 0.25 に埋めた合成の実験）。どちらも PR が無く、main とぶつかる。ADR-052 D4 の関門 4 は §2 がすべて埋まることなので、入れないと値の表に穴が残る。
- **選択肢**:
  - A: 先に 2 本を取り込む（改訂の枝の S1-F5〜F10 は付け替え、文献は空いた番号で採り直す）
  - B: 罰の値だけ取り込み、改訂の枝は別のタスク
  - C: main の版だけで進める
- **採用**: A
- **理由**: ADR-047・048 は Accepted で、日の終わりの問いは実装済み（`src/components/DayQuestionCard.tsx`）。入れないまま値を埋めると凍結の前に抜けが出る。
- **トレードオフ**: 取り込みの作業（番号の付け替え・文献の番号）がこのタスクに乗る。
- **影響範囲**: 事前登録の §2 の項目の数、このタスクの PR の大きさ（罰の実験の結果の表を含む）。
- **見直しタイミング**: なし。

## 判断 2: 罰の枝の 1-SE 規則の出典に番号を付けない

- **判断日時**: 2026-11-21（研究者が AskUserQuestion で選んだ）
- **背景**: 罰の枝は Hastie・Tibshirani・Friedman『The Elements of Statistical Learning』（doi:10.1007/978-0-387-84858-7）を [V370] で登録していたが、main の [V370] は CENT 2015（ADR-047 が引く）。ほかの未マージの枝が V399〜553 を使っているので、空いているのは V554 から。V554 を main に入れると、間の枝が入るまで `scripts/check_citations.py` の欠番で main の CI が赤になる。
- **選択肢**:
  - A: 番号を付けずに名だけ書き、登録は後のタスクに回す
  - B: V554 で登録し、PR は間の枝の後まで待つ
  - C: 出典を落とす
- **採用**: A
- **理由**: 1-SE 規則は比べた CV の版の 1 つで採らなかったもので、定義は `experiments/20261104-stage1-penalty-synthetic/conditions.md` C2 に自分で書いてある（出典は本文未読・provisional だった）。PR を待たせる重さに見合わない。
- **やったこと**: 罰の枝の [V370] の 5 か所（事前登録 S1-E8・実験の notes 2 本・steering 2 本）を「出典は未登録」の注に替え、references.md の行は入れなかった。
- **トレードオフ**: 手法の名の出どころが一時的に references.md に無い。
- **見直しタイミング**: V413〜553 を使う枝が main に入った後に、末尾の番号で登録する。

## 判断 3: 改訂の枝は事前登録の本文と steering だけ取り込み、S-DQ の文献は枝に残す

- **判断日時**: 2026-11-21（研究者が AskUserQuestion で選んだ）
- **背景**: 改訂の枝 `docs/gse-stage1-prereg-revision` は、日の終わりの問いの尺度の文献のラウンド S-DQ（枝 `docs/gse-daily-item-scale-literature`・カード `docs/literature/20261105-daily-end-of-day-items.md` と文献 27 件）の上に積んであった。27 件は V386〜412 で振られているが、main の V386〜398 は後から入った別の 13 件で、番号がまるごとかぶる。main の後ろで空いているのは V399〜412 の 14 件分だけで、残りは V413 以降（論文の枝が使用中）か V554 以降（欠番で main の CI が赤）になる。事前登録の本文が S-DQ から引くのは 5 件。
- **選択肢**:
  - A: 事前登録の本文と steering だけ取り込み、S-DQ は枝に残す
  - B: 全部取り込み V554 から振る（PR は待ち）
  - C: 空きの 14 件分だけ取り込む
- **採用**: A
- **やったこと**:
  - 改訂の枝の `docs/preregistration-stage1.md` の差分を 3-way で当て、`.steering/20261105-gse-stage1-prereg-revision/` を写した。`docs/research-positioning.md` の 1 行の追記（S-DQ の結果を引く）は入れていない。
  - 改訂の枝の S1-F5〜F10 は S1-F6〜F11 に付け替えた（main の S1-F5 は手跡の漏れの確かめで、ADR-051 と conditions.md が指す）。本文の中の参照（§1・S1-F3・S1-F7 の中・§4 の表）もずらした。`.steering/20261105-gse-stage1-prereg-revision/` の中の番号は当時の記録として直していない（そこでの S1-F5〜F10 は今の S1-F6〜F11）。
  - S-DQ の文献 5 件（[V405]〜[V408]・[V411]）は、番号を付けずに著者・年・DOI で書いた。[V27] は main にあるのでそのまま。
- **残したこと**:
  - S-DQ の枝を main へ入れるときに、27 件を空いた番号で振り直し、事前登録の S1-F8・F9・F10 の 5 件に番号を付ける。
  - 改訂の枝は [V27] の著者の表記を直していた（"Lafit, G. et al." は誤りで Yang, L.-Q. ら・全文 PDF と Crossref で確認したとある）。main の [V27] はまだ旧表記。S-DQ を入れるときに一緒に直す。
- **見直しタイミング**: S-DQ の枝を main へ入れるとき。
