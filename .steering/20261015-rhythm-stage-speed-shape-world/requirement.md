# 背景のステージの机上の検査 —— 揺れの形を分けた world（倍率だけ・漂いだけ）

## 背景

揺れの world `h(c)`（`.steering/20261014-rhythm-stage-speed-confound-world/`）では、L300 の `res=sub` の候補が赤になった。原因の切り分け（`.steering/20261015-rhythm-stage-speed-cause-split/`・`experiments/20261015-rhythm-stage-speed-cause-split/notes.md`）で、次のことが分かった。

- A_speed の特徴を加法の非線形で使う基準（`lrbin`）でも、赤の多くは残る。
- c100 の `lr`・`lrbin` と c200 の `lrbin` では、`raw`・`jitter` の赤の上乗せが `r_absdiff`・`r_sd`（`R2`）に集まっていた。
- 限り: PC-stall は `r` を定数にしているので、`R2` を落とした後に `r` の側に残る手がかりへの感度は示されていない。
- 読み 1（描画が A_speed に無い停滞の手がかりを運ぶ）と読み 2（A_speed の中の手がかりを取り出しやすい形で運び直す）のどちらかには決まっていない。

`h(c)` の速さの揺れは、2 つの成分の和である: `z(τ) = c · δ · (u + d(⌊τ/1000⌋))`。`u` はセッション（か対）ごとの倍率の元、`d` は時定数 300 s の定常な単位 OU の漂いで、秒ごとに変わる。研究者は 2026-10-15 に、この 2 つの成分を分けた world を次のタスクに選んだ（引き継ぎ `.steering/_handoff/next-session-rhythm-stage-speed-shape-world.md`）。

## 問い

赤（とくに `R2` が運ぶ上乗せ）は、倍率の成分から来るのか、漂いの成分から来るのか。

- 倍率だけの world: `z = c · δ · u`。セッションの中では速さが揺れない。
- 漂いだけの world: `z = c · δ · d(k)`。セッションの間で倍率の差が無い。
- 成分を抜くだけで、c は `h(c)` と同じにする（判断 2）。各 world には、`h(c)` の成分が 1 つだけ同じ大きさで入る。全体の標準偏差は `√2 · cδ` から `cδ` に下がる。

見込み（Claude の推論・確かめていない）: 倍率はセッションの中で一定なので、窓ごとの `r` の揺れの量にはほとんど入らない。漂いは秒ごとに変わるので、`r_absdiff`・`r_sd` に入りうる。

## ゴール

1. design を書き、`/cross-review` を 2 巡通してから、計器とともにコミットして固定する。固定は、どの段の下見 0 よりも前に行う。
2. 計器を `experiments/20261015-rhythm-stage-speed-shape-world/` に作る（揺れの world と原因の切り分けの計器を写して直す・前の計器は書き換えない）。
3. 2 つの world × c100・c200 の下見 0 で天井を見て、go の段について、下見 1（λ・PC-stall と PCr）→ スモーク → 本番を回す。
4. 本番の入れ物は、揺れの world と同じもの（項目 1〜6・判定・検査器）に、原因の切り分けの読み（`lrbin` の基準・`R2` などを落とす変種）を最初から加える（判断 4）。
5. `r` の側を通る陽性の対照を 2 本足す（判断 6・判断 7）。
   - PCr-level: 停滞のブロックの値を `r` の水準に入れる。
   - PCr-var: 停滞のブロックの値で `r` の秒ごとの揺れの大きさを変える。
6. notes を書き、`/cross-review` に 2 巡通す。

## スコープ

### 含むもの
- 倍率だけの world と漂いだけの world（c100・c200）。
- 揺れの world の項目 1〜6・判定・検査器と、原因の切り分けの (a)・(b) の読み。
- `r` の側の陽性の対照 PCr-level・PCr-var（λ は下見 1 で較正する）。
- 報告では、`h(c)` の同じ段・原因の切り分けの値を並べる（記述）。

### 含まないもの
- 総量をそろえた world（c × √2）。判断 2 で採らなかった。
- c400 などの段の追加。天井で止まった段も、それを結果として受け入れる（判断 3）。
- L60 の λ の格子を広げること（別のタスク）。
- c100 の hgb を PC-stall の大きさを上げて読めるようにすること（別の候補）。
- 第 1 回・第 2 回・中間の world・揺れの world・原因の切り分けの入れ物・判定・notes を書き換えること。
- `src-tauri/`・EH3 のファイル。
- 実在の人の打鍵。キーストロークの内容・NDJSON の生ログ（合成も）を、外部の LLM（Codex を含む）に送ること。

## 受け入れ条件

- [ ] design が `/cross-review` を 2 巡通り、計器とともにコミットされている（固定のコミットが、どの下見 0 よりも前にある）。
- [ ] 計器の selftest が 0 failed で、変異の検査（world の成分の取り違え・PCr の手がかりの入れ先など）を捕まえることを、固定の前に確かめて `decisions.md` に書いてある。
- [ ] `--world` の新しい 2 つの選択肢は、c = 0 で `--world graded --t 0.5` とバイト単位で一致する。既存の world（v1〜v4・graded・confound）の出力は変わらない。
- [ ] 2 world × 2 段の下見 0 の結果があり、go の段には本番の `summary.json` などがある。天井で止めた段は、そう記録してある。
- [ ] 回す前に `Win32_Process` と `gh run list` を見て、notes に記録してある。
- [ ] notes に `h(c)` の同じ段との比べ（記述）と限りがあり、`/cross-review` を 2 巡通っている。
- [ ] 「GSE が示した」と書いていない。揺れの形は Claude が選んだ一例だと書いてある。

## 関連ドキュメント

- `.steering/_handoff/next-session-rhythm-stage-speed-shape-world.md`
- `.steering/_handoff/next-session-rhythm-stage-after-cause-split.md`
- `.steering/20261014-rhythm-stage-speed-confound-world/design.md`（§1.3 揺れの world）
- `.steering/20261015-rhythm-stage-speed-cause-split/design.md`
- `experiments/20261014-rhythm-stage-speed-confound-world/notes.md`
- `experiments/20261015-rhythm-stage-speed-cause-split/notes.md`
- `docs/experiment-tracking.md`

## 運用メモ
- /reimagine 適用: No
- 理由: 入れ物は揺れの world と原因の切り分けの計器を写して直すもので、新しいのは world の 2 つの選択肢・読みの合体・PCr の 2 本である。大きな設計判断は grill で閉じた。第二の目は `/cross-review` の 2 巡で入れる（研究者 2026-10-15）。
