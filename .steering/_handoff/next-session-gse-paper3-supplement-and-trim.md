# 引き継ぎ —— 論文 3 の補足資料（Online Resource S1〜S16）を作り、本文を予算に寄せる

> 作成: 2026-11-20（Mac のセッション）。このメモを一次資料にしない。採否は `.steering/20261111-gse-paper3-round3-computations/decisions.md` 判断 37〜44、attack-me の記録は `.steering/20261107-gse-paper3-per-person-learning/attack-me/manuscript-paper3/round-7`〜`round-10/verdict.md`、分量は `.steering/20261107-gse-paper3-per-person-learning/paper-write/length-log.md`。

## 0. 入口の文

```
worktree /Users/johnd/GSE-prototype-paper3（枝 docs/gse-paper3-per-person-learning）で、.steering/_handoff/next-session-gse-paper3-supplement-and-trim.md を読んで、論文 3 の補足資料 S1〜S16 を作り、本文の細部を補足へ移して分量を予算に寄せてください。
```

## 1. 今の状態（2026-11-20）

- 本文は `papers/per-person-learning/manuscript/main.tex`（ed99b8ac）。attack-me は round 10（minor・R1〜R3 は 3 回続けて全員 minor・E「査読に回す」）で閉じた。
  - 閉じるときは、直す一覧をメインが確かめ、数値の照合（Opus・読むだけ）で誤りが無いことも確かめた（round-10/verdict.md §9）。
  - tmp/ は消した。
- 分量: 本文（序論〜結論・`texcount -inc -sub=section` の text+headers+captions の和）は 8,059 語、要旨 249 語、19 頁、警告 0。予算 6,800 語を 1,259 語超えている（投稿先に上限の規定は無い。E は長さそのものを欠陥にしていない）。
- 補足資料はまだ無い。本文は `\Sref{n}` で S1〜S16 を指す（S6・S10・S11 は欠番。振り直す）。
  - 補足へ移すと決めた文は `papers/per-person-learning/manuscript/outline.md` の末尾にある。節は「Round 6 fixes」「Round 7 fixes」「Round 8 preparation」の 3 つ。
  - S12（後の確かめの一覧・12 件）と S16 の対照の値の置き場も、そこに書いてある。
- 実データの計算は終わっている（round 7 の A・B を含む）。新しい計算の予定は無い。

## 2. やること

1. 補足資料を別のファイルで作る（paper-write Step 2。置き場と形は投稿先 UMUAI の Supplementary Information の規程に合わせる。規程の文 "Supplementary Information (SI) will be published as received from the author without any conversion, editing, or reformatting." は照合済み）。
   - 中身は outline.md の末尾の 3 節、本文の `\Sref` の参照先、各 experiments/ の notes と results の集計値。
   - 書き手ごとの値は出さない（Data availability の方針）。
2. 本文の細部を補足へ移し、予算に寄せる。足すより移す。
   - 移す候補（round 9・10 の E の指摘）: 4.4 の 7 段（2 つの最頻値の対照・先頭の記号を除いた段・own chain の平滑の選び）、3.4 の結果を見た後の変更の 1 文の一覧（S12 へ）、方法の細部（ただし EM の初期化・収束の 1 文と、先頭の記号の採点の規則は本文に残すと決めた。判断 37 C と round 7 の Y5）、限界の細部。
   - 決定に関わる値・個人差の定義・決定の問いと科学の問いの区別・入れ替えの対照の結論の範囲は、本文に残す（判断 43・44）。
3. 表 3 の区間が四分位と同じ値になる（n = 17 では両方とも 5 番目と 13 番目の順序統計量）。脚注にするか S7 で断るかを決める。
4. 移した後に、数値の照合（Opus・読むだけ）をもう一度通す。length-log に語数を書く。
5. 投稿の前に残る既知の未決（round-10/context-A.md の 1〜16）を確かめる。とくに次の 3 つ。
   - Springer Nature の様式への移行。移行で要旨の語数が変わりうる（今 249 語・上限 250）。
   - Code availability の URL と DOI。
   - 元の記号列の記録ごとのハッシュ。

## 3. 守ること

- `papers/` に GSE の名前・内部のパス・判断の番号を書かない。投稿先や状態を公開物に書かない。
- 実データ・書き手ごとの値は開かない。CoAuthor の記録も値も Codex に送らない。
- push は枝だけ・PR は出さない（[skip ci]）。worktree の `.codex/budget.json` はコミットしない（台帳は本線。11-20 は 15 回・約 60 万 tokens）。
- 文献を足すときは citation-ssot（枝をまたぐ採番に注意）。
