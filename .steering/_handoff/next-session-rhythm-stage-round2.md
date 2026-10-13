# 引き継ぎ: 背景のステージの机上の検査 —— 再実行（第 2 回）

作成 2026-10-13（Windows・G-GEAR）。返答・記録・AskUserQuestion の引数は日本語で。記号（★・⚠️）を多用しない（研究者の指摘）。

## 新しいセッションで最初に打ち込む文

```
.steering/_handoff/next-session-rhythm-stage-round2.md を読んで、背景のステージの再実行の固定を作って。
```

## 1. ここまでの状態

- 第 1 回の本番は済んだ（`2f60ea33`・world v4・SEED 20261009・P 240・`experiments/20261012-rhythm-stage-desk-check/results/main/`）。L300 は緑 14・赤 0・判定不能 10、L60 は緑 16・判定不能 8、L1800 は 24 本とも判定不能。第 1 回の判定は書き換えない。
- notes は `/cross-review`（Codex と code-reviewer）で直した（`experiments/20261012-rhythm-stage-desk-check/notes.md`・判断 21）。下見と本番の PC-stall の対照表は notes の「逸脱・気づいたこと」にある。
- 研究者の判断 21（`.steering/20261012-rhythm-stage-desk-check/decisions.md`）: 再実行は別の固定で、**λ の選び方を直す**と**新しい seed で回す**の 2 つを入れる。端から端までの赤の検査と中間の world は今回の固定に入れない。順番は「再実行（v4）→ その結果を見て中間の world を改めて検討 → 実施」。

## 2. 読む順（一次）

1. `experiments/20261012-rhythm-stage-desk-check/notes.md`（全文。特に判定不能 10 本・下見と本番の対照表・L1800）
2. `.steering/20261012-rhythm-stage-desk-check/design.md` §3.2・§3.3・§3.8・§3.9・§8 と `decisions.md` 判断 16〜21
3. `experiments/20261012-rhythm-stage-desk-check/scripts/checks.py` の `select_lambda`・`pilot`・`judge`、`run.sh`、`config.json` の `pc_stall`
4. EH1 の回の分け方の型（`experiments/20261010-portrait-eh1-round5/` と `.steering/20261010-portrait-eh1-round5/`）

## 3. このセッションでやること

1. `/start-task` で `.steering/20261013-rhythm-stage-round2/` を作る（タスク名は研究者に確かめる）。入れ物は `experiments/<固定の日付>-rhythm-stage-round2/` に新しく作り、第 1 回の計器を写す（第 1 回の入れ物は変えない）。
2. design を書く。第 1 回の design を土台にし、変えるのは λ の選び方と seed だけにする。論点（研究者に推奨つきで問う）:
   - λ の選び方: 下限 > 0.03 も条件にするか（今は点推定だけを狙う）・λ = 0 の上乗せ（下見の P 40 で +0.001〜+0.016）を差し引くか・格子を細かくするか（0.025 刻みなど）・下見を本番と同じ P 240 で回すか（所要は 1 本の本番に近くなる）。下見の点推定は写像ごとに P で向きが分かれた（raw は下がり、smooth・rank・jitter は上がった）ので、P 40 の下見では選べない見込みが強い（推論）。
   - seed: 本番・下見・スモークの seed を第 1 回と重ならない値にする（第 1 回の本番を見た後に λ を選ぶので、同じ列を使うと選び方に自由度が入る）。
   - 第 1 回の notes で見つかった計器以外の弱さ（L1800 の PC の範囲がラベルと合わない・変異を最後の判定まで通していない）は、今回の固定に入れない（判断 21）。入れたくなったら研究者に戻す。
3. 固定の前に `/cross-review`（design の差分）を回す。固定 → 下見 → スモーク → 本番 → notes の型は第 1 回と同じ。
4. 再実行の結果が出たら、中間の world（停滞が打鍵の時刻に弱く出る世界。強さを段にした系列を結果の前に固定する案）を研究者と検討する。判断 16（天井に合わせて世界を調整しない）とぶつかりうる点を先に示す。

## 4. 守ること

- 合成の列だけを使う。キーストロークの内容・NDJSON の生ログ（合成も）を外部の LLM（Codex を含む）に送らない。Codex に渡すのは design・notes・集計の要約まで。
- 結果を見てから主のラベル・基準・world・式を選び直さない。λ は直した選び方で下見から選ぶ（第 1 回の本番の値から λ を直接決めない）。
- `src-tauri/`・EH3 のファイルに触れない（第 1 回の判断 1）。
- 本番は G-GEAR の self-hosted CI が走っていない時に回す（`gh run list`）。第 1 回の本番は `--jobs 16` でメモリ 32 GB 中 15 GB 前後が空いたまま、判定と記述で 16676 s。
- Codex の台帳（`.codex/budget.json`）は `git checkout --` で戻さない。ブランチごとに記帳されるので、回す前に origin/main の台帳も見る。
- `git add -A` を使わない（明示したパスだけ）。worktree のセッションでは、git を含む複合コマンドは分けて叩く。
- 実行の道具: `PYTHON=C:/wt/portrait-eh1-round3/experiments/20261010-portrait-eh1-round3/.venv/Scripts/python.exe`・`GSE_REPLAY=C:/wt/_target-portrait-eh1/release/gse-replay.exe`（SHA-256 `71d09dab…8d78986`）。

## 5. 未出荷

- ブランチ `docs/rhythm-stage-desk-check` は push 済みで PR は出していない（第 1 回の本番と notes の修正・判断 21 を含む）。PR は研究者の確認の後（第 1 回のタスクの最後の項「親タスクの判断 3・5 の見直しの材料として結果を渡す」が残っている）。
