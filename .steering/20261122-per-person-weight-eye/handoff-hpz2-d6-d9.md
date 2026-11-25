# HP Z2 での作業: D6 の書き手の水準の量（第 2 の帰無）と D9（第 2 の帰無の用量）

> 作成: 2026-11-25（Mac のセッション）。一次は `experiments/20261122-per-person-weight-eye/conditions.md`（D6・D9）と `decisions.md`（判断 42・43）。この手順は回すだけで、コードは直さない。赤・例外が出たらそこで止めて、出力をそのまま研究者に返す。

## 入口の文（HP Z2 の Claude Code に）

```
GSE-prototype の枝 exp/gse-per-person-weight-eye の .steering/20261122-per-person-weight-eye/handoff-hpz2-d6-d9.md を読んで、その手順だけを行って。
```

## 前提

- 前回の report2（a15d76e0）の複製の jsonl が `results/hpz2/report/` に残っていること（`.gitignore` で repo には無い。D6 の書き手の水準の規則はこの jsonl の G_v を使う）。消えていたら止める。
- Mac の 95% 点（`results/report/d6_local_null1.json`）は、Mac の報告の組が終わってから push される（手順 3 で待つ）。
- code_hash は `e38db3af7cfe…`。Python 3.11.9・numpy 2.4.4。npz は前回と同じ置き場。worktree は前回のもの（`core.autocrlf=false`）。git-bash で回す。

## 手順

1. 最新にする:
   ```bash
   cd ~/GSE-prototype-weight-eye && git status --short   # 何も出ないこと
   git pull --ff-only
   cd experiments/20261122-per-person-weight-eye
   PY=<Python 3.11.9 のパス>
   "$PY" -I -X utf8 -c "import sys; sys.path.insert(0, 'scripts'); import run_eye; print(run_eye.code_hash())"   # 先頭が e38db3af7cfe
   ```
2. D9（第 2 の帰無の用量・4 段 × 40 人・数分。Mac の 95% 点は要らない）:
   ```bash
   "$PY" -I -X utf8 scripts/d9.py results/hpz2/d9_null2.json --null 2 --npz <npz のパス> --jobs 16
   ```
   「書いた: results/hpz2/d9_null2.json」で終わること。
3. Mac の 95% 点を待つ。`git pull --ff-only` の後に `ls results/report/d6_local_null1.json` で在るか確かめる。無ければ、5 分おきに pull して確かめる（Mac の報告の組が終わってから Mac が push する。2026-11-25 の夕方の見込み）。1 時間たっても無ければ、2 の結果だけを 5 でコミットして push し、止まって研究者に返す。
4. D6 の書き手の水準の量（自機の 95% 点・Mac の 95% 点と合わせた c・第 2 の帰無の率）:
   ```bash
   "$PY" -I -X utf8 scripts/d6_local.py results/hpz2 --null 2 --peer results/report/d6_local_null1.json
   ```
   「書いた: …d6_local_null2.json（5 群・c と率あり）」で終わること。「複製が計画と合わない」「群の jsonl が無い」で止まったら、そのまま返す。
5. コミットして push（出したものだけ）:
   ```bash
   git branch --show-current   # exp/gse-per-person-weight-eye
   git add results/hpz2/d9_null2.json results/hpz2/report/d6_local_null2.json
   git commit -m "docs(experiments): 重みを見る目の D6 の書き手の水準の量と D9 を HP Z2 で出した（第 2 の帰無）"
   git pull --rebase && git push
   ```

## してはいけないこと

- コードを直さない。報告の組・選びの組を回し直さない。
- 出した json の値を読んで解釈しない（D6 の判定は Mac の d6_report.py が機械的に行う）。
- npz を repo に入れない・値を出さない。
