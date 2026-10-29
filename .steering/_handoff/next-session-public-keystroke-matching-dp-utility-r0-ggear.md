# 次のセッション（G-GEAR）: 照合の論文 —— R-DP の有用性を R0 に比べて集計し直す（notes.md D5）

> **使用済み（2026-10-29）。** G-GEAR で済んだ（コミット `84527b7a`・`9463d81b`・`520e6be5`・notes.md D5）。Mac で陽性対照 3 つを独立に照らし直して一致した。続きは段 3 の引き継ぎ。

作成 2026-10-29（Mac・判断 81 の後）。**この作業は G-GEAR で行う。Mac では行わない。** 手順は Mac で書き、ブランチ `docs/public-keystroke-matching-manuscript` に push 済み。G-GEAR では、まずこのブランチを pull してから始める。

## 新しいセッションで最初に打ち込む文（G-GEAR で）

```
.steering/_handoff/next-session-public-keystroke-matching-dp-utility-r0-ggear.md を読んで、R-DP の有用性を R0 に比べて集計し直して。
```

## なぜ要るか

`results/exploratory_dp.json`（dp の段・2026-10-28 終了）は、有用性のうち R0 との Spearman の相関と R0 との比（中央値・10 と 90 百分位）が全部空だった。`--forms dp` の形の組（`forms.DP`）に R0 が無く、`aggregate.utility_summary` が各書き手の R0 の値を引けなかったため（notes.md D5）。研究者は 2026-10-29 に、キャッシュから集計だけをやり直すと決めた（判断 81）。照合の値は影響を受けていない。

## 0. 始める条件

1. `git fetch origin && git checkout docs/public-keystroke-matching-manuscript && git pull`（G-GEAR の worktree で）。
2. チェーンの `all` の段（全員の付録・2026-10-28 18:12 UTC 開始）が走っていても、この作業はできる。次の「やってはいけないこと」を守る。

## やってはいけないこと（キャッシュの指紋）

A4 の 499 人の版（`next-session-public-keystroke-matching-a4-499-ggear.md` の同じ節）と同じ。

- `run_main.py`・`evaluate.py`・`matching.py` など、走行が読み込むファイルを変えない（`all` の段が 500 人の段のキャッシュ `33fa95833296d7a5` を使えなくなる）。走っているチェーンの台本も書き換えない。
- `aggregate.py` は既存の関数の振る舞いを変えない。新しい台本は別のファイル（例 `scripts/dp_utility_r0.py`）にし、その中で `cache_fingerprint` を呼ばない。キャッシュの場所は引数で渡す。
- キャッシュは読むだけにする（書かない・消さない）。

## 1. 何を出すか

- 出力: `results/exploratory_dp_utility_r0.json`（集計だけ・書き手ごとの値と ID を書かない）。
- 中身: `exploratory_dp.json` の `main500.utility` と `utility_figure` と同じ鍵と同じ量を、R0 の値を入れて計算したもの（形は R3・R-DP(0.5)・(1)・(2)・(4)）。

## 2. 実装案（Mac でコードを読んだ範囲・G-GEAR で実物を読んで確かめてから決める）

- 書き手ごとの有用性の値は、2 つのキャッシュにある: 本計算の 500 人の段（指紋の頭 `33fa95833296d7a5`・R0 を含む全ての主の形）と dp の段（`1383e6ee6aca2c58`・R3 と R-DP）。どちらも `raw/derived/main_cache/` の下。標本の 500 人の件（窓を評価する件）を読み、`(課題, 書き手)` の順に並べる（`run_main.run` の `sorted(sample_set)` と同じ）。
- 各書き手の `utility` の辞書に、本計算の件の R0 の値を足す（R3 と R-DP は dp の件のまま）。得点・抽出（`aggregate.resamples` の名前 `main500`・課題の層別の列）は `run_main.run` と同じものを作る。その上で `aggregate.utility_summary(res, scores, forms.DP, R, cols)` を呼ぶ（関数を写さず同じ関数を呼ぶ）。`--forms dp` の実行が渡した引数を `run_main.py` の 466 行目の前後で確かめる。
- 確かめること（陽性対照）:
  - 2 つのキャッシュで、R3 の書き手ごとの有用性の値が全員で一致すること（R3 は両方の段で計算された）。
  - 出力の R3 の有用性が、`main.json` の `main500.utility` の R3 と全部の葉で一致すること。`utility_figure` の R3 も一致すること。
  - 出力の `spearman_score`・`cell` が `exploratory_dp.json` と全部の形で一致すること（R0 は得点との相関に関わらない）。
  - 書き手の数が 500 で、R0 を落とした数（`ratio_dropped_r0`）が `main.json` の R3 と同じであること。
- 自己検査と変異（`selftest_main.py` の作法）: 合成の結果で、(a) R0 を足さないと比が空になる（今の出力の再現）(b) 足すと全部の形で埋まる (c) 2 つのキャッシュで書き手の組が違えば止まる。変異ごとに赤を見る。
- レビュー: code-reviewer・security-checker・Codex（Codex には台本の diff だけ。記録・本文・書き手ごとの値・ID を送らない）。

## 3. 終わったら

- notes.md の D5 に、回した日時・コミット・出力の SHA-256・陽性対照の結果を追記する。
- 出力を `results(experiment): ...` のコミットで freeze の枝に入れ、原稿の枝へ merge する（これまでと同じ形）。
- push だけ。PR は出さない（G-GEAR の計算中は出さない）。
- Mac の段 3 で表 8 に R0 との相関と比の列を足す（`next-session-public-keystroke-matching-manuscript-stage-3.md`）。

## 守ること

- キャッシュの中の書き手ごとの値・ID・本文を印字しない。打鍵の記録・本文を外部 LLM（Codex を含む）に送らない。
