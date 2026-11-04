# 引き継ぎ —— CoAuthor と CS1 の 1 人ごとの学習の改善の試験の本計算を、職場の HP Z2 で回す

> 作成: 2026-11-04（Mac のセッション）。このメモを一次資料にしない。条件は `experiments/20261104-coauthor-ml-improve/conditions.md`、判断は `.steering/20261104-gse-coauthor-ml-improve/decisions.md`（判断 1〜13）。

## 0 入口の文（職場の PC の Claude Code に最初に打ち込む）

```
GSE-prototype の枝 exp/gse-coauthor-ml-improve を取り出し、.steering/_handoff/next-session-gse-coauthor-ml-run-on-hp-z2.md を読んで、CoAuthor と CS1 の改善の試験の run.sh をこの PC で回し、結果を枝に push してください。条件とコードは変えず、門が赤なら直さずに止めて報告してください。データは Drive の GSE/GSE_ML_run にあります。
```

repo がまだこの PC に無ければ、先に `git clone git@github.com:mikotomiura/GSE-prototype.git`（または HTTPS）。

## 1 やること（これだけ）

この PC では `run.sh` を回して結果を持ち帰るだけにする。notes・読み・レビューは Mac のセッションが行う。

- 条件・コード・格子を変えない。門（P-D1・manifest・selftest・変異）が赤なら、直さずに止めて、何が赤かだけを報告する。
- 結果の値を読んで解釈しない（`results/summary.json` を開くのは、ファイルができたかと `run_id` の確かめまで）。
- `~/gse-public-data/landscape/coauthor_ml_improve_writer_values.*.json`（書き手ごとの値）を開かない。repo に入れない。
- CoAuthor・CS1 の記録も値も、Codex を含む外部の LLM に送らない。

## 2 準備

1. Git for Windows（git-bash）・Python 3（3.11 以上）と numpy が要る。Mac は Python 3.14.4・numpy 2.5.2。版が違っても回してよい（provenance に残る）。`python --version`・`python -c "import numpy;print(numpy.__version__)"` で確かめ、Python のコマンド名（`python` か `python3` か `py`）を控える。
2. コード: `git fetch origin && git checkout exp/gse-coauthor-ml-improve`（Mac が push した先頭のコミットは §6）。worktree を切るなら `git worktree add ../GSE-prototype-coauthor-ml exp/gse-coauthor-ml-improve`。取り出した `run.sh` が LF であること（`file experiments/20261104-coauthor-ml-improve/run.sh` が CRLF と言わない）。ディレクトリの `.gitattributes` で LF に固定してある。
3. データ: Drive のフォルダ `GSE/GSE_ML_run`（ID `1fAx-J4WUJX9tdgat-gRaqaBwooo6StrC`）に研究者が Mac から上げた 2 つを、研究者が手で（またはこの PC の Drive for desktop で）ダウンロードする。Mac の元は `/Users/johnd/gse-public-data/transfer_coauthor_ml/`。
   - `coauthor_ml_inputs.tar.gz`（195,075,078 バイト・SHA-256 `6efc58db0ab8f2ce616b8e55a26529a73cd7834000389d5d0b0b8607fa7272f2`）
   - `input_manifest.json`（SHA-256 `e0163f1b48e94273a9d2e30fe6e6c76de642eae82311a6ca7c125896a3d74406`）
   - 2 つとも SHA-256 を確かめる（`sha256sum <ファイル>`）。違えば止める。
4. 展開: データの置き場所を決める（例 `C:/Users/<名前>/gse-public-data`。以下 `DATA_DIR`）。`mkdir -p "$DATA_DIR" && tar -xzf coauthor_ml_inputs.tar.gz -C "$DATA_DIR"`。`$DATA_DIR/landscape/coauthor_work`・`coauthor_work_obs`・`$DATA_DIR/cs1/work2021_obs`・`work2021_ref` ができる。manifest は `$DATA_DIR` の外でも中でもよい。
5. スリープを切る（研究者の操作）: 電源につなぎ、`powercfg /change standby-timeout-ac 0` と `powercfg /change hibernate-timeout-ac 0`（終わったら元に戻す）。

## 3 回す

git-bash で:

```bash
cd <repo>/experiments/20261104-coauthor-ml-improve
PYTHON=python DATA_DIR="C:/Users/<名前>/gse-public-data" \
INPUT_MANIFEST="<manifest の場所>/input_manifest.json" \
INPUT_MANIFEST_SHA256=e0163f1b48e94273a9d2e30fe6e6c76de642eae82311a6ca7c125896a3d74406 \
JOBS=16 bash run.sh 2>&1 | tee "$DATA_DIR/coauthor_ml_run.log"
```

- `PYTHON` は §2-1 で控えた名前。run.sh・mutate.sh は Python を `-I -X utf8` で呼ぶ（Windows の既定の cp932 で JSON が化けないように）。`JOBS=16`（24 コアのうち 16・各プロセス 1 スレッド）。
- 中身: manifest の照合（`results/input_manifest_check.json`）→ 変換と門の selftest → P-D1 の門 2 つ → selftest（合成・約 5 分）→ 変異 10 個（合成・約 40 分）→ 本計算（CoAuthor → CS1）→ provenance。
- 見込み: 本計算は Mac の 6 プロセスで約 9〜10 時間の見積もり（合成による・`results/timing.json`）。16 プロセスで約 4 時間前後と推すが、実測ではない。
- `set -euo pipefail` なので、どこかで赤なら止まる。`tee` を使うと終了コードが見えにくいので、最後に `echo ${PIPESTATUS[0]}` で 0 を確かめる。

## 4 終わったら

1. `results/` に `summary.json`・`selftest.json`（`mutations` 欄つき）・`check_same_coauthor.json`・`check_same_cs1.json`・`input_manifest_check.json`・`provenance.json` があり、`summary.json` と `provenance.json` の `run_id` が同じこと。`results/mutations/` は変異のログで、repo に入れてよい（合成だけ）。
2. `git status` で、変わったのが `experiments/20261104-coauthor-ml-improve/results/` の下だけであること。それ以外が変わっていれば止めて報告する。
3. コミット（`docs(experiments): CoAuthor と CS1 の改善の試験の本計算の結果（HP Z2） [skip ci]`・本文に `Refs: .steering/20261104-gse-coauthor-ml-improve/`）して push。PR は出さない。push できなければ `results/` を zip にして Drive の `GSE_ML_run` に置く（研究者が手で）。
4. 回した時間（各段の時刻）・JOBS・Python と numpy の版・止まった場合の段と赤の内容を、このメモの末尾に追記してコミットする。

## 5 止まったとき

- manifest・P-D1 が赤: データの展開の誤りか取り違え。展開をやり直す。直らなければ止めて報告。
- selftest・変異が赤: Windows で値が変わる箇所の可能性。直さずに、`results/selftest.json` の赤の対照と値を報告する（Mac で原因を見る）。
- 本計算が例外: 例外のメッセージに番号や値が出うるので、メッセージは研究者と Mac のセッションの間だけで扱い、外に出さない。直さずに報告する。

## 6 Mac 側の状態（2026-11-04）

- 枝 `exp/gse-coauthor-ml-improve`（origin に push 済み。条件・コード・門の最後のコミットは `bef80020`。その後はこのメモの直しだけ）。門（P-D1・manifest）は Mac で通した。合成の selftest は 18 対照すべて緑。変異の門の Mac での結果は decisions の判断 13。
- このメモの後の作業（Mac）: 結果が戻ったら notes.md（4 つ組・各表・言える範囲・逸脱）→ code-reviewer・/cross-review → push（PR は研究者が確かめてから）。
