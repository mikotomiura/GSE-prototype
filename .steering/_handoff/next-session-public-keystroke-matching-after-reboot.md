# 次のセッション: 公開データでの照合の論文 —— 再起動の後、A4 の生成を再開して本計算を回す

作成 2026-10-13（G-GEAR）。前の引き継ぎ `next-session-public-keystroke-matching-enja15-a4-impl.md` の実装は済んだ。GPU が TDR のような落ち方をしたので（下）、研究者が PC を再起動する。投稿の目標は PoPETs 2027 Issue 3（締切 2026-11-30 AoE）。

## 新しいセッションで最初に打ち込む文

```
.steering/_handoff/next-session-public-keystroke-matching-after-reboot.md を読んで、A4 の生成を再開し、CPU の本計算・ENJA15・探索的な分析を回して。
```

## 今の状態

- worktree `C:\GSE-wt-matching-prereg`・ブランチ `docs/public-keystroke-matching-freeze`（push 済み）。このセッションのコミット: `1eb10cf3`（判断 56・探索的な分析の手順の固定）→ `b798b75c`（A4 の生成）→ `4d6bb503`（ENJA15）→ `2434390b`（読み込み・A4 の照合・探索的な分析）→ `f16e9460`（レビューの直し）→ `110e3dec`（Codex の台帳）→ `d61bf234`（Codex 2 巡目の直し）→ 引き継ぎのコミット。
- 研究者の判断 56（4 つとも推奨）: A4 は 500 人・`max_new_tokens` 50 のまま。unicity は k = 1〜50・N = 10・100・1,000。R-DP は ε = 0.5・1・2・4・間隔の上限 2,000 ms。手順は `notes.md` の「探索的な分析の手順」と `exploratory.json`。
- レビュー: code-reviewer（HIGH なし）・security-checker（CRITICAL・HIGH なし）・Codex 2 巡（`notes.md` の「実装のレビュー」）。直しはすべて済み。自己検査は `selftest_main`・`selftest_enja15`・`selftest_exploratory`・`selftest_a4` が PASS で、変異はどれも落ちる（`selftest_main` は `d61bf234` の後に回し直していない。`run_main.py` の変更は `--a4-dir` の検査と出力の `mutate` だけ）。
- 実データの照合と有用性の値は **まだ 1 つも計算していない**。ENJA15 も回していない。

## GPU の落ち方（2026-10-13）

- A4 の生成（`scripts/a4_keytar.py`）を 16:15 に始め、3 人を終えた後（約 34 分）に `RuntimeError: CUDA error: unknown error`。直後の `nvidia-smi` は「GPU is lost. Reboot the system to recover this GPU」。1 人あたり約 9〜10 分（500 人で約 80 時間）。
- 最初の 3 人ぶんのファイルは生成の指紋が無いので `raw/derived/a4_before_fingerprint/` に退けた（使わない。消してよい）。`raw/derived/a4/` は空。
- 再起動の後にまた落ちるなら、GPU の電力の上限を下げる（例 `nvidia-smi -pl <W>`・管理者）か、ドライバを確かめる。どうするかは研究者に聞く。

## やること（順に）

1. GPU が見えることを確かめる（`nvidia-smi`）。
2. A4 の生成を再開する（バックグラウンドで約 80 時間・止まっても GPU が見えるまで待って続きから再開・やり直しても治らない止まり方は終了コード 3 で止まる）:
   ```bash
   bash /c/GSE-wt-matching-prereg/experiments/20261012-public-keystroke-matching/scripts/a4_run_resumable.sh
   ```
   進み具合は `raw/derived_a4_progress.log`（行は「writer n/500 done」と試行の時刻だけ）。`a4_keytar.py` と指紋に入るコード（`FINGERPRINT_FILES`）は、生成を再開した後は変えない（変えると全ファイルが「別の生成」になり止まる）。
3. CPU の本計算（GPU と並行・約 22 時間・12 並列。同じ PC の Windows の CI のため 16 にしない）:
   ```bash
   cd /c/GSE-wt-matching-prereg/experiments/20261012-public-keystroke-matching
   ~/.venvs/pkm-main/Scripts/python -I scripts/run_main.py --source klicke --root raw/klicke/extracted/WritingTask --out results/main.json --workers 12 --all
   ```
   その前に、一度だけ小さく通して落ちないかを確かめるとよい（例: `--per-prompt-sample 2` で `results/.tmp/` に出し、値は見ない。`--per-prompt-sample` は 500 人の標本の大きさを変えるので本番には使わない）。
4. ENJA15（数分）: `~/.venvs/pkm-main/Scripts/python -I scripts/enja15_main.py --root raw/enja15 --out results/enja15_main.json`
5. 探索的な分析: `scripts/exploratory_unicity.py --source klicke --root ... --out results/exploratory_unicity.json --workers 12`・`scripts/run_main.py --source klicke --root ... --forms dp --out results/exploratory_dp.json --workers 12`（`run.sh` の data の段と同じ）。
6. A4 の生成が終わったら: `run_main.py --source klicke --root ... --a4-dir raw/derived/a4 --out results/main_a4.json --workers 12`（500 人だけ・A4 以外のセルが `main.json` の 500 人と同じことを確かめる）。
7. 結果を `notes.md` に書く（「結果」の節を作る）。集計だけ。逸脱があれば「逸脱」に。

## 守ること

- 記録・本文・A4 の復元の中身を Claude 自身も読まない（数・ハッシュ・分布だけ）。外部 LLM（Codex を含む）に送らない。Codex にはコードと文書の差分だけ（`raw/` と結果の JSON を範囲に入れない）。
- 凍結の後の変更は `notes.md` の「逸脱」に（変える前の結果も残す）。
- 応答は日本語。★・⚠️ を多用しない。`git add -A`・`git add <dir>` を使わない。バックスラッシュを含む置換は Write か Edit で（heredoc は壊す）。
- 状態を変える操作（push・PR・merge）は出力をファイルに保存して 1 回だけ。
- Windows では `ProcessPoolExecutor` の作業のプロセスがスクリプトを読み直すので、本計算を回している間はスクリプトを編集しない（編集するなら別の場所に `git archive` で書き出したコードで回す）。
- Codex の予算: このブランチの台帳は 2026-10-13 に 2 巡ぶん使った（上限 600,000）。
