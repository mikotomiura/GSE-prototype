# 引き継ぎ — 肖像の EH1 第 2 回の本番（G-GEAR）

> 作成: 2026-10-09（設計と計器のセッション）。設計は `.steering/20261009-portrait-eh1-round2/design.md`（§3 の基準は `ea02e557`、§3.11 の神託は `6b8ef7de` で固定）、判断は同 `decisions.md` 判断 1〜5。
> ⚠️ このメモを一次資料にしない。基準は design §3・§3.11、計器は `experiments/20261009-portrait-eh1-round2/`。

## §0 次のセッションの最初に貼るプロンプト

```
.steering/_handoff/next-session-portrait-eh1-round2-run.md を読んで、肖像の EH1 第 2 回の本番を G-GEAR で回してください。
worktree は C:\wt\portrait-eh1-round2（ブランチ docs/portrait-eh1-round2）。結果を読んで解釈するのは本番の後の別のセッションです。
```

## §1 どこまで済んでいるか

- 基準の固定 → 下見（PC だけ・SEED 20261010）→ PC2 が働かず、研究者の決定で神託（§3.11）を足した → 計器 → スモーク（v2・v1）→ `/cross-review` 2 巡（判断 4・5）。
- 計器の最後のコミット: `eb5034a3`。selftest は 0 failed（スモーク v2）。

## §2 回す前に確かめること

1. **計測の run と self-hosted CI が走っていないこと**（本番は 16 コアを数時間使い切る）。`gh run list --limit 5` で `in_progress` が無いか・G-GEAR の `gse-win` の job が無いかを見る。計測の run は研究者に聞く（推測しない）。
2. worktree が clean で、HEAD が `eb5034a3` 以降であること（`git status --short` が空）。
3. `.venv/` が無ければ作る: `python -m venv .venv` → `.venv/Scripts/python -m pip install -r requirements.txt`（Python 3.11.9）。
4. `gse-replay`: 第 1 回と同じビルド `C:/wt/_target-portrait-eh1/release/gse-replay.exe`（SHA-256 `71d09dab…986`）を `GSE_REPLAY` で渡す。無ければ `run.sh` が `cargo build` する（target は worktree の外）。

## §3 回し方

```bash
cd /c/wt/portrait-eh1-round2/experiments/20261009-portrait-eh1-round2
export GSE_REPLAY=/c/wt/_target-portrait-eh1/release/gse-replay.exe
bash run.sh --world v2 --jobs 16 2>&1 | tee ../../../_eh1r2-v2.log   # 主
bash run.sh --world v1 --jobs 16 2>&1 | tee ../../../_eh1r2-v1.log   # 副（E1-3 は not_applicable と宣言済み）
```

- ⚠️ v2 と v1 を**同時に回さない**（どちらも 16 コアを使い切る）。同じ world を 2 本並行に回さない（`run.sh` の結果の置き換えが互いを壊す）。
- 所要の見積もり（確かめていない）: スモーク（P 12・ブートストラップ 200・並べ替え 2）が約 2 分。本番は行が 20 倍・当てはめが 7 倍なので、**1 world で 2〜4 時間**と見込む。最初の `E1-3 L300 done at … s` の行で見積もりを直す。
- ログは worktree の外（`C:/wt/_eh1r2-*.log`）に置く。⚠️ ログに絶対パスが出るので、notes に貼るときは取る。
- 一時ファイル: 特徴の行列を `work-<world>/e13-*/` に書く（ラベルごとに消す・1 ラベルで数 GB）。C: の空きを確かめる。

## §4 回した後

1. `results/<world>/provenance.json` の `git_commit`・`experiment_dir_dirty`（false であること）・`seed`（20261009）・`jobs` を見る。
2. selftest の行（`0 failed`・変異 4 本とも PASS・`lattice` の揺らしの INFO）をログから notes の「実行の記録」に写す。
3. コミットするのは `results/v2/`・`results/v1/` の JSON と `samples/*.png` だけ（`work-*/`・`.partial-*`・`.old-*` はコミットしない・NDJSON は外部に送らない）。`git add` はファイルを名指しする。
4. ⚠️ **結果の解釈は書かない**（本番の後の別のセッション）。notes の「実行の記録」と「逸脱・気づいたこと」だけを書く。
5. push だけ（PR は出さない・merge の順は S-MR → 親 → `docs/portrait-eh1-eh2` → このブランチ）。

## §5 止まる条件

- selftest が 1 つでも FAIL → 本番に進まず止めて報告する。
- `MemoryError`・ディスク不足 → `--jobs` を下げて回し直す（結果は並列の数に依らない設計・design §3.9）。下げたことを notes に書く。
- それ以外の例外 → 計器を直さずに止めて報告する（固定の後の変更は design §8 に書く必要がある）。

## §6 守ること

- 応答は日本語。AskUserQuestion には推奨と理由を添える。
- main checkout（`C:\GSE-prototype`）の git には触らない。
- 結果の PNG・NDJSON・`work-*/` を Codex や外部の LLM に送らない。
- 「検査した範囲で見つからなかった」より強く書かない。主張の格は EH0。神託が「狭い」でも実際の組を緑と呼ばない（design §3.11）。
