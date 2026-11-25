# HP Z2 での作業（v2）: 第 2 の帰無の報告の組と、D6 の書き手の水準の量

> 作成: 2026-11-26（Mac のセッション）。v2 の実験は `experiments/20261126-per-person-weight-eye-v2/`。一次は v2 の `conditions.md`・`notes.md` と `decisions.md`（判断 47〜49）。この手順は回すだけで、コードは直さない。赤・例外・見積もり超過が出たらそこで止めて、出力をそのまま研究者に返す。
>
> 2 回に分けて頼む。**今回は「前半」だけ**を行う。後半は、Mac が自分の 95% 点を push した後に、研究者が後半の入口の文で頼む。

## 入口の文（HP Z2 の Claude Code に）

前半:
```
GSE-prototype の枝 exp/gse-per-person-weight-eye の .steering/20261122-per-person-weight-eye/handoff-hpz2-v2-report2.md を読んで、前半の手順だけを行って。
```

後半（Mac から合図があってから）:
```
GSE-prototype の枝 exp/gse-per-person-weight-eye の .steering/20261122-per-person-weight-eye/handoff-hpz2-v2-report2.md を読んで、後半の手順だけを行って。
```

## 前提

- D5 は commit 8c21235d でコミット済み（E1 を選んだ）。報告の組はこの後でだけ回してよい。
- code_hash は `1665a0b2f83f…`（前回の HP Z2 の V1 と同じ）。Python 3.11.9・numpy 2.4.4。npz は前回と同じ置き場。
- 前回と同じ worktree（`core.autocrlf=false` で作ったもの）を git-bash で使う。

## 前半

1. 最新にする:
   ```bash
   cd <GSE-prototype-weight-eye の worktree> && git status --short   # 何も出ないこと
   git pull --ff-only
   git log --oneline -1   # 8c21235d かそれより新しいこと
   cd experiments/20261126-per-person-weight-eye-v2
   ```
2. code_hash を確かめる（先頭が `1665a0b2f83f` でなければ止める）:
   ```bash
   PY=<Python 3.11.9 のパス>
   "$PY" -I -X utf8 -c "import sys; sys.path.insert(0, 'scripts'); import run_eye; print(run_eye.code_hash())"
   ```
3. 第 2 の帰無の報告の組（3,000 複製。最初に見積もりを出し、24 時間を超えるなら自分で止まる）と集計:
   ```bash
   NPZ=<npz のパス> PYTHON="$PY" JOBS=16 OUT=results/hpz2 bash run.sh report2
   "$PY" -I -X utf8 scripts/summarize.py report results/hpz2 --null 2
   ```
   `run.sh` の最後が「終わり: report2 …」で、終了コードが 0 であること。
4. D6 の書き手の水準の量（この機械の 95% 点だけ・`--peer` は付けない）:
   ```bash
   "$PY" -I -X utf8 scripts/d6_local.py results/hpz2 --null 2
   ```
   「書いた: results/hpz2/report/d6_local_null2.json（5 群・95% 点だけ）」で終わること。
5. コミットして push（複製の `*.jsonl` は `.gitignore` で入らない）:
   ```bash
   git branch --show-current   # exp/gse-per-person-weight-eye であること
   git add results/hpz2
   git commit -m "docs(experiments): 重みを見る目 v2 の第 2 の帰無の報告の組と 95% 点を HP Z2 で回した"
   git pull --rebase && git push
   ```
   ここで止める。

## 後半（Mac の `results/report/d6_local_null1.json` が push されてから）

1. 最新にして、Mac の 95% 点があるかを確かめる（無ければ止めて研究者に返す。待たない）:
   ```bash
   cd <worktree> && git pull --ff-only && cd experiments/20261126-per-person-weight-eye-v2
   ls results/report/d6_local_null1.json
   ```
2. 両機の 95% 点から閾値 c と率を出す:
   ```bash
   "$PY" -I -X utf8 scripts/d6_local.py results/hpz2 --null 2 --peer results/report/d6_local_null1.json
   ```
   「書いた: results/hpz2/report/d6_local_null2.json（5 群・c と率あり）」で終わること。
3. コミットして push:
   ```bash
   git add results/hpz2/report/d6_local_null2.json
   git commit -m "docs(experiments): 重みを見る目 v2 の第 2 の帰無の書き手の水準の率（c と率あり）"
   git pull --rebase && git push
   ```

## してはいけないこと

- コードを直さない。`results/hpz2/select` を回し直さない。
- `summary_null2.json`（report）と `d6_local_null2.json` の値を読んで解釈しない（D6 は Mac で集計する）。
- npz を repo に入れない・値を出さない。
- v1 のディレクトリ（`experiments/20261122-per-person-weight-eye/`）に書き込まない。
