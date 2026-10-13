# 引き継ぎ: 背景のステージの第 2 回 —— 下見 1 → スモーク → 本番

作成 2026-10-13（Windows・G-GEAR・PC の再起動の前）。返答・記録・AskUserQuestion の引数は日本語で。記号（★・⚠️）を多用しない（研究者の指摘）。

## 新しいセッションで最初に打ち込む文

```
.steering/_handoff/next-session-rhythm-stage-round2-pilot.md を読んで、背景のステージの第 2 回の下見 1 から続けて。
```

## 1. ここまでの状態

- worktree は `C:\wt\eh3-windows-device-rest`、ブランチ `docs/rhythm-stage-round2`（push 済み・作業ツリーはきれい）。
- 第 2 回の設計は **固定済み**（`fd2d64d9`・`.steering/20261013-rhythm-stage-round2/design.md`）。固定の時点で下見 1・スモーク・本番は回していない。
- 計器は `experiments/20261013-rhythm-stage-round2/`（第 1 回の写し `65b95fc3` を直したもの）。`config.json` の `pc_stall.lam` は空（下見 1 の後に書く）。
- selftest は gse-replay を使わない分だけ回して 174 項目・0 件の失敗（gse-replay の因果の検査は下見 1 の中で回る）。
- 研究者の決定: `decisions.md` 判断 1（P 240・格子 0.025 刻み 0〜0.30・帯の両条件＋0.055・SEED 20261013・名前）と判断 3（0.055 のまま・2 回の読み方の 4 文）。固定の前の `/cross-review` 2 巡は判断 2・4。

## 2. 読む順（一次）

1. `.steering/20261013-rhythm-stage-round2/design.md` 全文（特に §0 の表・§3.3 への追加・§3.9・§8）
2. 同 `decisions.md` 判断 1〜4、`tasklist.md`
3. 必要に応じて第 1 回: `.steering/20261012-rhythm-stage-desk-check/design.md`（第 2 回 design が参照する節）・`experiments/20261012-rhythm-stage-desk-check/notes.md`

## 3. このセッションでやること

1. **下見 1**（見積もり 2〜3 時間）。先に `gh run list` で G-GEAR の self-hosted CI が走っていないことを確かめる。

   ```
   cd C:/wt/eh3-windows-device-rest/experiments/20261013-rhythm-stage-round2
   PYTHON=C:/wt/portrait-eh1-round3/experiments/20261010-portrait-eh1-round3/.venv/Scripts/python.exe \
   GSE_REPLAY=C:/wt/_target-portrait-eh1/release/gse-replay.exe bash run.sh --pilot --jobs 16
   ```

   - 長いので `run_in_background` で回し、出力はファイルに保存する（Bash の background では cd が効かないことがあるので絶対パスで）。
   - 最後に「PILOT STOPPED」が出たら λ を書かずに研究者に戻す（design §3.9 の止まる条件）。
2. 止まらなければ、同じ入れ物から `$PYTHON scripts/checks.py --apply-pilot config.json results/pilot/pilot.json` で `pc_stall.lam` を書く（出どころを照合して書く・手で書き写さない）。
3. design §8 に下見 1 の行を書く: 計器のコミット・汚れの有無・seed 20261014・所要・AUC(A_speed)・PC1・各候補の `g`・`l`・`ĝ`・帯に入った λ・選んだ λ と規則・λ = 0 の値（上限の最大が 0.03 以上の候補は `stall_baseline` の見込みとして）。`results/pilot/` と config・design をコミットする。
4. **スモーク**（`bash run.sh --smoke --jobs 16`・SEED + 2・P 12・`results/main-smoke/` は git の外）。
5. **本番**（`bash run.sh --main --jobs 16`・約 5 時間・CI が走っていない時）→ `results/main/`・`notes.md`（第 1 回の notes の型。第 1 回と第 2 回の判定を必ず並べる・design §3.3 への追加の 4 文）。
6. notes の `/cross-review`。その後、中間の world を研究者と検討する（判断 16 とぶつかりうる点を先に示す・第 1 回の判断 21）。

## 4. 守ること

- §3.9 の規則と 0.055 は下見 1 を見た後に変えない。直すのは計器の誤りだけで、その場合も §8 に書く。
- 合成の列だけを使う。NDJSON の生ログ（合成も）・キーストロークの内容を外部の LLM（Codex を含む）に送らない。Codex に渡すのは design・notes・集計の要約まで（`scripts/run-codex-review.sh <range> -- <paths>` でパスを限る）。
- `src-tauri/`・EH3 のファイル・第 1 回の入れ物に触れない。
- Codex の台帳（`.codex/budget.json`）は `git checkout --` で戻さない。2026-10-13 の分は 9 回目まで記帳済み（`95fc5024`）。
- `git add -A` を使わない（明示したパスだけ）。worktree のセッションでは、git を含む複合コマンドは分けて叩く。
- 実行の道具: `PYTHON` と `GSE_REPLAY` は上のとおり（gse-replay の SHA-256 `71d09dab…8d78986` を run.sh が確かめる）。

## 5. 未出荷

- `docs/rhythm-stage-desk-check`（第 1 回）: push 済み・PR なし。研究者の確認待ち。
- `docs/rhythm-stage-round2`（第 2 回）: push 済み・PR なし。第 1 回のブランチから切っているので、第 1 回を先にマージしないと差分に第 1 回の分が混ざる。
