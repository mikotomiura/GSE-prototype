# 背景のステージの机上の検査 —— 再実行（第 2 回）

## 背景

第 1 回（`.steering/20261012-rhythm-stage-desk-check/`・`experiments/20261012-rhythm-stage-desk-check/`・world v4・SEED 20261009・P 240）の本番で、主のラベル L300 は緑 14・赤 0・判定不能 10 だった。判定不能 10 本の理由はすべて PC-stall（候補ごとの陽性対照）が帯（下限 > 0.03・点推定 ≤ 0.08）に入らなかったことで、`raw` の 6 本は弱く、`smooth-hold`・`smooth-decay` の 4 本は強すぎた。主因は λ の選び方（P 40 の下見の点推定だけを目標 0.05 に合わせ、下限と小標本の上乗せを見ない）と読める（第 1 回 notes「逸脱・気づいたこと」）。

研究者の判断 21（第 1 回 `decisions.md`）: 再実行は別の固定で、「λ の選び方を直す」と「新しい seed で回す」の 2 つを入れる。端から端までの赤の検査と中間の world は入れない。順番は「再実行（v4）→ その結果を見て中間の world を改めて検討 → 実施」。

引き継ぎ: `.steering/_handoff/next-session-rhythm-stage-round2.md`。

## ゴール

1. 第 2 回の設計（`design.md`）を、第 1 回の design から変えるのは λ の選び方と seed だけにして書き、`/cross-review` を通してから、どの結果（下見を含む）よりも前にコミットして固定する。
2. 計器を `experiments/20261013-rhythm-stage-round2/` に写して直し、下見 1 → スモーク → 本番 → notes を第 1 回と同じ型で回す（固定の後の段）。
3. 結果が出たら、中間の world を研究者と検討する（判断 16 とぶつかりうる点を先に示す）。

## スコープ

### 含むもの
- λ の選び方: 下見 1 を本番と同じ P 240 で回す・格子 0.025 刻み 0〜0.30・帯の両条件を満たす λ のうち点推定が 0.055 に最も近いもの（研究者・判断 1）。
- 新しい seed: `SEED` = 20261013（下見 1 は +1・スモークは +2）。

### 含まないもの
- 端から端までの赤の検査（変異を候補として最後の判定まで通す）・L1800 の PC の範囲の直し・中間の world（判断 21）。入れたくなったら研究者に戻す。
- 第 1 回の入れ物・判定・notes を変えること（第 1 回の判定は書き換えない）。
- `src-tauri/`・EH3 のファイル（第 1 回の判断 1）。
- 実在の人の打鍵。キーストロークの内容・NDJSON の生ログ（合成も）を外部の LLM（Codex を含む）に送ること。

## 受け入れ条件

- [ ] `design.md` が、第 1 回の design との違い（λ の選び方・seed・それに伴う計器の細部）を明示し、研究者の決定が `decisions.md` にある
- [ ] 固定の前の `/cross-review` の結果と対応が `decisions.md` にある
- [ ] `design.md` が、計器のどの結果（下見 1 を含む）よりも前にコミットされている
- [ ] 本番の結果が `experiments/20261013-rhythm-stage-round2/results/` と `notes.md` にあり、読み方が「検査した範囲で見つからなかった／見つかった」までに限られている

## 関連ドキュメント

- `.steering/20261012-rhythm-stage-desk-check/`（design・decisions 判断 1〜21・tasklist）
- `experiments/20261012-rhythm-stage-desk-check/notes.md`（第 1 回の結果・下見と本番の PC-stall の対照表）
- `experiments/20261010-portrait-eh1-round5/`・`.steering/20261010-portrait-eh1-round5/`（回の分け方の型）
- `docs/experiment-tracking.md`

## 運用メモ
- /reimagine 適用: No
- 理由: 第 1 回の検査の設計を土台に、λ の選び方と seed だけを変える再実行で、選び方の案は研究者が 3 案から選んだ（判断 1）。研究者が求めれば適用する。
