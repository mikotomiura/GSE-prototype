# 次のセッション —— 論文 2: 追加の計算 3 つ → 文献 → 原稿の組み直し → attack-me round 2

> 作成: 2026-11-07。このメモを一次資料にしない。一次は `.steering/20261107-paper2-manuscript/decisions.md`（判断 1〜3）・`attack-me/manuscript-paper2/round-1/verdict.md`（直す一覧 A〜U）・`review-*.md`・原稿 `papers/stall-shape-multiverse/manuscript/`。

## §1 どこまで済んだか
- worktree `~/GSE-prototype-paper2`・枝 `docs/gse-paper2-stall-shape`。push・PR はまだ（研究者に確かめる）。
- 原稿の初稿（04519806・英語・JEDM の LaTeX・本文 4,848 語・補足 S1〜S9）。ビルド: `bash build.sh <template-dir> <out-dir>`（テンプレートは scratchpad の `tpl/`。無ければ JEDM の 2024_08_02_jedm-latex.zip）。図の CSV と補足の全表は `.steering/20261107-paper2-manuscript/paper-write/make_figdata.py` が results/ から作る。
- attack-me manuscript round 1 は major。研究者は「全部行う」（判断 3）。

## §2 次にやること（順に）
1. 追加の条件 5 を `experiments/20261107-stall-shape-multiverse/conditions-round5.md` に書き、計算の前にコミット。中身:
   - (a) 休止の系統（第 2 の検出器）: 文字の打鍵の間隔が閾値を超えたら休止。閾値は固定 2・5・10 秒と本人の分位（0.95・0.99・0.995 など・先に決める）。観測区間の切り方は既存の 3 つ。各定義で、率・データの間の順位と比（区間）・KLiCKe の得点との関連（区間）・φ（同じ人の中）。
   - (b) 本人の分位の θ を再標本の中で推定し直した区間（基準・W 15 秒の 10 通り・逆転の境に近い通り、の範囲を先に決める）。
   - (c) 観測の長さ・作文の長さ（文字数）と停滞の率・得点の関係、それらで調整した関連（探索的か条件か、地位を先に書く）。
   - 読み方の文（どの結果で何と書くか）と「看板の形は替えない」を先に書く。
2. 計算（作業場は repo の外・集計値だけ repo へ・selftest と陽性対照・notes.md）。
3. /literature-review（休止の特徴と作文の得点の関連の大きさ。既登録の文献は番号だけ挙げさせる）。Li & An 2026（doi:10.3389/fpsyg.2026.1792834・r = −0.226）を含める。
4. 直す一覧 A〜U と監査役の小さい直しを原稿に当てる（足すより移す）。地位の書き違い（H）を最初に直す。観測区間は推定器なしで読める規則として書く（replay が行を書く条件をコードで確かめる）。S7 は補足から外す。"small-to-moderate" は "small" に。
5. 語数・n-gram・数の照合 → commit → attack-me round 2（同じ立場・同じ文献。接地の本文は round-1/tmp/sources から写すか取り直す。役ごとの carryover。Codex には既知の未決の一覧）。

## §3 気をつけること
- 書き手ごとの値・CS1 のデータ・作文の本文を repo の外・外部の LLM へ出さない。CS1 は集計値だけ。
- 計算の結果を見て看板の形を替えない（判断 15・判断 3）。外枠の round で計算を足すたびに指摘が増えた。
- `.codex/budget.json` はステージしない。本日の Codex は 246,638 / 800,000。
- 公開物（papers/）に GSE・内部の番号・[Vn]・パスを書かない。
