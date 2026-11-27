# 設計

## アプローチ

- S13 の試験（`experiments/20261107-unsmoothed-residual-check/`）の当てはめと残差のコードを SHA-256 で固定して読み込み、列の読み込みだけを差し替える。数式のコードは書かない。
- 用量: 窓の歩み s ∈ {1, 5, 10, 15, 30} 秒。平滑は全部の歩みで外す（u の記号）。
- 量の交絡: 列 A（位相 1 つ・量は約 1/s）と列 B（位相 s 個を別の系列として全部使う・量はほぼ一定）で逆の側から挟む。読みの主は列 B。
- 端の再現: 列 A の s = 1 は S13 の u、s = 30 は S13 の n と同じになるように定義し、S13 の summary と相対 1e-9 で照らす（配管の門）。
- 量: G・R・C2a・C2b・D（= r1 − 共有 hmm3）・M（遅れ 1 の相互情報量＝操作の確かめ）・構造の選び・残差（値だけ）・頭を除く採点。
- 読みの型 1〜4 と論文への持ち込みの文は conditions.md D5 に凍結する。

## 変更対象

- 新: `experiments/20261127-window-overlap-dose/`（conditions.md・SEED・scripts/・run.sh・mutate.sh・results/・notes.md）
- 後で論文の枝: `papers/per-person-learning/manuscript/main.tex`・`supplement.tex`（結果の要約だけ）

## テスト戦略

- conditions.md V2 の陽性対照（P-STRIDE・P-PHASE・P-MI・P-FIRST・P-SWAP・P-READ）と名指しの変異 m61〜m69、S13 の selftest の引き継ぎ。
- 実データの門: P-PIN・入力の照合・P-REPRO-U・P-REPRO-N。
