# HP Z2 での作業: 窓の歩みの用量反応の本計算を全部回し直す（D6）

> 作成: 2026-11-28（Mac のセッション）。一次は `experiments/20261127-window-overlap-dose/conditions.md`（第 7 版・D6・V1・末尾の判断 10〜12）と `decisions.md`（判断 13）。この手順は回すだけで、コードは直さない。赤・例外が出たらそこで止めて、出力をそのまま研究者に返す。

## 入口の文（HP Z2 の Claude Code に）

```
GSE-prototype の枝 exp/gse-per-person-window-overlap の .steering/20261127-gse-paper3-window-overlap/handoff-hpz2-run.md を読んで、その手順だけを行って。
```

## なぜ HP Z2 で回すか

Mac の本計算は、端の再現の門（列 A1 と S13 の u、列 A30 と S13 の n の一致・相対 1e-9）で外れた（A30: 6,816 中 116、A1: 6,815 中 144）。同じ Mac で S13 の fit.py・residual.py を列 n にそのまま回すと、HP Z2 の S13 の結果と同じ 116 か所で外れ、この試験の列 A30 とは 6,816 中 0 の差で一致した。外れは機械（BLAS: Mac は Accelerate・HP Z2 は OpenBLAS）の違いで、コードの違いではない。D6 のとおり、許容を変えずに HP Z2 で合成の門から全部を回し直す。Mac の結果は notes に使わない。

## 前提

- 機械は S13 の試験と同じ HP Z2・git-bash。Python 3.11.9・numpy 2.4.4（S13 の provenance と同じ版）。`JOBS = 16`。
- 入力は S13 の試験で HP Z2 が使ったものと同じ（SHA-256 は手順 2 で照らす）。`$DATA_DIR` の既定は `$HOME/gse-public-data`。
- 書き手ごとの値と母数は `$DATA_DIR/landscape/window_overlap_raw/` に書かれる（repo の外）。開かない。
- 時間の見込み: 合成の門が 1〜2 時間（tau-extend の selftest がいちばん長い）、本計算が約 3 時間（Mac の見積もり 5.8 時間 ÷ 約 2.04）。

## 手順

1. 枝を取り出す（worktree が無ければ作る）:
   ```bash
   cd <GSE-prototype の本線のチェックアウト> && git fetch origin
   git worktree add ~/GSE-prototype-window-overlap exp/gse-per-person-window-overlap   # 既にあれば cd して git pull --ff-only
   cd ~/GSE-prototype-window-overlap && git config core.autocrlf false && git status --short   # 何も出ないこと
   git log --oneline -1   # 判断 13 の commit（「HP Z2 の引き継ぎ」）であること
   cd experiments/20261127-window-overlap-dose
   PY=<Python 3.11.9 のパス>
   "$PY" -I -X utf8 -c "import sys, numpy; print(sys.version.split()[0], numpy.__version__)"   # 3.11.9 2.4.4
   ```
2. 入力を照らす（3 つとも一致すること。違えば止める）:
   ```bash
   D=$HOME/gse-public-data
   sha256sum $D/landscape/unsmoothed_residual_coauthor.json.gz $D/landscape/unsmoothed_residual_manifest.json $D/transfer_coauthor_ml/input_manifest.json
   # d9526ea7731706e7c1920a84a19dd873fa7d2414270f634af427cddc0ef0926d  unsmoothed_residual_coauthor.json.gz
   # 370c1d599c59f3d7bb77bc4e0d5c79e7b1b65ae4980fa091f96fa0fdfa62d494  unsmoothed_residual_manifest.json
   # e0163f1b48e94273a9d2e30fe6e6c76de642eae82311a6ca7c125896a3d74406  input_manifest.json
   ```
3. 合成の門（実データを読まない）:
   ```bash
   PYTHON="$PY" JOBS=16 bash run_synth.sh 2>&1 | tee ../../../window-overlap-synth.log
   ```
   最後が「済んだ（合成）」で、途中の JSON がすべて true であること（S13 の 10 本・tau-extend の 15 本・足す対照 10 本・変異 21 本）。e2e は `{"passed": true, ...}`。外れたら止めて返す。
4. 本計算:
   ```bash
   PYTHON="$PY" JOBS=16 \
   INPUT_MANIFEST=$D/transfer_coauthor_ml/input_manifest.json INPUT_MANIFEST_SHA256=e0163f1b48e94273a9d2e30fe6e6c76de642eae82311a6ca7c125896a3d74406 \
   VARIANT_MANIFEST=$D/landscape/unsmoothed_residual_manifest.json VARIANT_MANIFEST_SHA256=370c1d599c59f3d7bb77bc4e0d5c79e7b1b65ae4980fa091f96fa0fdfa62d494 \
   bash run.sh 2>&1 | tee ../../../window-overlap-run.log
   ```
   最後が「済んだ」であること。
   - 「端の再現の門が外れた」（終了コード 3）で止まったら、許容を変えずにそこで止め、`results/repro_check.json` の `leaves`・`mismatched`・`max_rel_diff`・`mismatched_sections` だけを研究者に返す（HP Z2 は S13 と同じ機械なので、外れはコードか入力の違いを指す）。
   - 他の所で止まったら、出力の最後の 30 行をそのまま返す。
5. コミットして push（集計値だけ。`results/` の下の出したものと 2 つの log は入れない）:
   ```bash
   cd ~/GSE-prototype-window-overlap && git branch --show-current   # exp/gse-per-person-window-overlap
   git status --short   # results/ の下だけが変わっていること（window_overlap_raw は repo の外）
   git add experiments/20261127-window-overlap-dose/results
   git commit -m "docs(experiments): 窓の歩みの用量反応の本計算を HP Z2 で回した（D6） [skip ci]"
   git pull --rebase && git push
   ```
   push の後、commit の番号と `results/provenance.json` の `run_id`・`git_head`・`git_dirty_paths` を研究者に返す。

## してはいけないこと

- コードと条件を直さない。許容（相対 1e-9）を変えない。`DROP_B` を使わない（判断 11）。
- 出た値（summary・readings・tables）を読んで解釈しない。notes・論文の文は Mac のセッションが書く。
- 書き手ごとの値・母数（`window_overlap_raw`）を開かない・repo に入れない・外部の LLM に送らない。
