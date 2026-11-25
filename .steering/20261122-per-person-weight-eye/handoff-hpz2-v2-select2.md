# HP Z2 での作業（v2）: V1・P-XMACH・第 2 の帰無の選びの組・D9

> 作成: 2026-11-26（Mac のセッション）。v2 は量を揃えた目の版で、新しい実験のディレクトリ `experiments/20261126-per-person-weight-eye-v2/` で回す（v1 の `experiments/20261122-per-person-weight-eye/` は触らない）。一次は v2 の `conditions.md` と `decisions.md`（判断 47〜49）。この手順は収集だけで、コードは直さない。赤が出たらそこで止めて、出力をそのまま研究者に返す。

## 入口の文（HP Z2 の Claude Code に）

```
GSE-prototype の枝 exp/gse-per-person-weight-eye の .steering/20261122-per-person-weight-eye/handoff-hpz2-v2-select2.md を読んで、その手順だけを行って。
```

## 前提

- 枝 `exp/gse-per-person-weight-eye`（Mac が push 済み）。Mac の v2 の V1 は緑で、code_hash は `1665a0b2f83f…`（`experiments/20261126-per-person-weight-eye-v2/results/v1/selftest.json`）。
- Python 3.11.9・numpy 2.4.4。`run.sh` は版が違うと止まる。
- 第 2 の帰無の m0 の npz は repo の外（v1 と同じ置き場）。値も要約も見ない・出さない。
- git-bash で回す。v1 で使った worktree（`core.autocrlf=false` で作ったもの）をそのまま使う。

## 手順

1. worktree を最新にする:
   ```bash
   cd <v1 で使った GSE-prototype-weight-eye の worktree>
   git status --short   # 何も出ないこと
   git pull --ff-only
   cd experiments/20261126-per-person-weight-eye-v2
   ```
2. ハッシュを確かめる（違えば止めて、`git config core.autocrlf` の値も添えて研究者に返す）:
   ```bash
   PY=<Python 3.11.9 のパス>
   "$PY" -I -X utf8 -c "import sys; sys.path.insert(0, 'scripts'); import run_eye; print(run_eye.code_hash())"
   ```
   先頭が `1665a0b2f83f` であること。
3. V1（第 2 の帰無の P-HASH を含む）:
   ```bash
   NPZ=<npz のパス> PYTHON="$PY" JOBS=16 OUT=results/hpz2 bash run.sh v1
   ```
   最後が「変異 7 個: 名指しの対照がすべて赤・変異なしは緑」と「終わり: v1 …」で終わること。終了コードが 0 でなければ止める。
4. P-XMACH（Mac の selftest と照らす）:
   ```bash
   PYTHON="$PY" OUT=results/hpz2 bash run.sh xmach results/v1/selftest.json
   ```
   「P-XMACH 緑: e598e872545f…（Python 3.11.9・numpy 2.4.4）」が出ること。赤なら止める。
5. 3 と 4 が緑なら、第 2 の帰無の選びの組（2,000 複製の見込み。最初に見積もりを出し、24 時間を超えるなら自分で止まる）:
   ```bash
   NPZ=<npz のパス> PYTHON="$PY" JOBS=16 OUT=results/hpz2 bash run.sh select2
   "$PY" -I -X utf8 scripts/summarize.py select results/hpz2 --null 2
   ```
6. D9（第 2 の帰無。目を使わないので D5 を待たなくてよい）:
   ```bash
   "$PY" -I -X utf8 scripts/d9.py results/hpz2/d9_null2.json --null 2 --npz <npz のパス> --jobs 16
   ```
   「書いた: results/hpz2/d9_null2.json」で終わること。
7. コミットして push（複製の `*.jsonl` は `.gitignore` で入らない）:
   ```bash
   git branch --show-current   # exp/gse-per-person-weight-eye であること
   git add results/hpz2
   git commit -m "docs(experiments): 重みを見る目 v2 の V1・第 2 の帰無の選びの組・D9 を HP Z2 で回した"
   git pull --rebase && git push
   ```
   Mac も同じ枝に push するので、push が弾かれたら `git pull --rebase` してからもう一度 push する。

## してはいけないこと

- 報告の組（`report2`）は回さない（D5 をコミットする前は禁止）。報告の組は、Mac が D5 をコミットした後に別の引き継ぎで頼む。
- コードを直さない。赤・例外・見積もり超過は、出力をそのまま研究者に返す。
- `summary_null2.json` の値を読んで解釈しない（D5 は Mac が choose.py で機械的に行う）。
- npz を repo に入れない・値を出さない。
- v1 のディレクトリ（`experiments/20261122-per-person-weight-eye/`）に書き込まない。
