# HP Z2 での作業: 第 2 の帰無の報告の組（report2）

> 作成: 2026-11-25（Mac のセッション）。一次は `experiments/20261122-per-person-weight-eye/conditions.md`（追記 3 まで）と `decisions.md`（判断 1〜41）。この手順は回すだけで、コードは直さない。赤・例外・見積もり超過が出たらそこで止めて、出力をそのまま研究者に返す。

## 入口の文（HP Z2 の Claude Code に）

```
GSE-prototype の枝 exp/gse-per-person-weight-eye の .steering/20261122-per-person-weight-eye/handoff-hpz2-report2.md を読んで、その手順だけを行って。
```

## 前提

- D5 は commit 13ed2543 でコミット済み（E3 を選んだ・判断 41）。報告の組はこの後でだけ回してよい（D8）。
- code_hash は `e38db3af7cfe…`（前回の HP Z2 の V1 と同じ）。Python 3.11.9・numpy 2.4.4。npz は前回と同じ置き場。
- worktree は前回の `C:\Users\SDS02\GSE-prototype-weight-eye`（`core.autocrlf=false` で作ったもの）を使う。git-bash で回す。

## 手順

1. 最新にする:
   ```bash
   cd ~/GSE-prototype-weight-eye && git status --short   # 何も出ないこと（results/hpz2 の jsonl は .gitignore で出ない）
   git pull --ff-only
   git log --oneline -1   # 13ed2543 かそれより新しいこと
   cd experiments/20261122-per-person-weight-eye
   ```
2. code_hash を確かめる:
   ```bash
   PY=<Python 3.11.9 のパス>
   "$PY" -I -X utf8 -c "import sys; sys.path.insert(0, 'scripts'); import run_eye; print(run_eye.code_hash())"
   ```
   先頭が `e38db3af7cfe` でなければ止める。
3. 第 2 の帰無の報告の組（最初に見積もりを出し、24 時間を超えるなら自分で止まる）:
   ```bash
   NPZ=<npz のパス> PYTHON="$PY" JOBS=16 OUT=results/hpz2 bash run.sh report2
   "$PY" -I -X utf8 scripts/summarize.py report results/hpz2 --null 2
   ```
   最後が「終わり: report2 …」で、終了コードが 0 であること。
4. コミットして push（複製の `*.jsonl` は入らない）:
   ```bash
   git branch --show-current   # exp/gse-per-person-weight-eye であること
   git add results/hpz2
   git commit -m "docs(experiments): 重みを見る目の第 2 の帰無の報告の組を HP Z2 で回した"
   git pull --rebase && git push   # Mac が同時に push していることがある
   ```

## してはいけないこと

- コードを直さない。`results/hpz2/select` を回し直さない。
- `summary_null2.json`（report）の値を読んで解釈しない（D6 は Mac で集計する）。
- npz を repo に入れない・値を出さない。
