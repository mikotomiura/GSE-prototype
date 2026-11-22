# HP Z2 での作業: V1（第 2 の帰無の P-HASH・P-XMACH）と、第 2 の帰無の選びの組

> 作成: 2026-11-23（Mac のセッション）。一次は `experiments/20261122-per-person-weight-eye/conditions.md`（追記 2 まで）と `decisions.md`（判断 1〜38）。この手順は収集だけで、コードは直さない。赤が出たらそこで止めて、出力をそのまま研究者に返す。

## 入口の文（HP Z2 の Claude Code に）

```
GSE-prototype の枝 exp/gse-per-person-weight-eye の .steering/20261122-per-person-weight-eye/handoff-hpz2-v1-select2.md を読んで、その手順だけを行って。
```

## 前提

- 枝 `exp/gse-per-person-weight-eye`（Mac が push 済み）。Mac の V1 は commit c7645298 で緑、code_hash は `646328e370c9…`（`results/v1/selftest.json` の `code_hash`）。
- Python 3.11.9・numpy 2.4.4（nfs と同じ版）。`run.sh` は版が違うと止まる。
- 第 2 の帰無の m0 の npz は repo の外（nfs と同じ置き場。既定は `$HOME/gse-public-data/landscape/null_from_shared_m0.npz`）。値も要約も見ない・出さない。
- git-bash で回す。

## 手順

1. 枝を取り出す（既存のチェックアウトを汚さないよう worktree で）:
   ```bash
   git fetch origin
   git worktree add ../GSE-prototype-weight-eye exp/gse-per-person-weight-eye
   cd ../GSE-prototype-weight-eye/experiments/20261122-per-person-weight-eye
   ```
2. 改行の変換でハッシュが変わっていないか（変わっていれば止める）:
   ```bash
   PY=<Python 3.11.9 のパス>
   "$PY" -I -X utf8 -c "import sys; sys.path.insert(0, 'scripts'); import run_eye; print(run_eye.code_hash())"
   ```
   先頭が `646328e370c9` でなければ止めて研究者に返す（`git config core.autocrlf` の値も添える）。
3. V1（第 2 の帰無の P-HASH を含む）:
   ```bash
   NPZ=<npz のパス> PYTHON="$PY" JOBS=16 OUT=results/hpz2 bash run.sh v1
   ```
   最後が「変異 6 個: 名指しの対照がすべて赤・変異なしは緑」と「終わり: v1 …」で終わること。終了コードが 0 でなければ止める。
4. P-XMACH（Mac の selftest と照らす）:
   ```bash
   PYTHON="$PY" OUT=results/hpz2 bash run.sh xmach results/v1/selftest.json
   ```
   「P-XMACH 緑: 68b8da877869…（Python 3.11.9・numpy 2.4.4）」が出ること。赤なら止める（決定的な検査。D8）。
5. 3 と 4 が緑なら、第 2 の帰無の選びの組（2,000 複製の見込み。最初に見積もりを出し、24 時間を超えるなら自分で止まる）:
   ```bash
   NPZ=<npz のパス> PYTHON="$PY" JOBS=16 OUT=results/hpz2 bash run.sh select2
   "$PY" -I -X utf8 scripts/summarize.py select results/hpz2 --null 2
   ```
6. コミットして push（複製の `*.jsonl` は `.gitignore` で入らない）:
   ```bash
   git branch --show-current   # exp/gse-per-person-weight-eye であること
   git add results/hpz2
   git commit -m "docs(experiments): 重みを見る目の V1 と第 2 の帰無の選びの組を HP Z2 で回した"
   git push
   ```

## してはいけないこと

- 報告の組（`report2`）は回さない（D5 をコミットする前は禁止・D8）。
- コードを直さない。赤・例外・見積もり超過は、出力をそのまま研究者に返す。
- `summary_null2.json` の値を読んで解釈しない（D5 は Mac が choose.py で機械的に行う）。
- npz を repo に入れない・値を出さない。
