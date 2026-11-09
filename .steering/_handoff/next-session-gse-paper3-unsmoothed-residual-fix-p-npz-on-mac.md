# 引き継ぎ —— HP Z2 の 1 回目が P-NPZ の後片付けで止まった所見と、Mac で直して回し直すまで

> 作成: 2026-11-09（HP Z2 のセッション）。このメモを一次資料にしない。実行の記録は `next-session-gse-paper3-unsmoothed-residual-run-on-hp-z2.md` の §7、条件は `experiments/20261107-unsmoothed-residual-check/conditions.md`、判断は `.steering/20261107-gse-paper3-unsmoothed-residual-check/decisions.md`。

## 0 入口の文（Mac の新しいセッションで打ち込む）

```
.steering/_handoff/next-session-gse-paper3-unsmoothed-residual-fix-p-npz-on-mac.md を読み、§3 のとおり selftest.py の P-NPZ の npz を閉じる直しを入れ、§4 の確かめをしてからコミット・push してください。直すのは後片付けだけで、条件・数式・対照の判定・変異は変えないでください。
```

## 1 何が起きたか（見えたこと）

- 2026-11-09 12:55:06 に HP Z2 で run.sh を開始した（別の worktree `C:/Users/SDS02/GSE-prototype-paper3`・先端 `a599378c`・Python 3.11.9・numpy 2.4.4・JOBS=16）。
- 緑で通った段: P-PIN → manifest 2 つの照合（3 ファイルの SHA-256 も一致）→ [12:55:09] 門の単体と P-D1 → [12:55:21] 引き継ぐ陽性対照（tau-extend の `ml.py --selftest`・約 9.5 分）。
- 赤: [13:04:49] 「足す陽性対照と変異」の最初の `selftest.py`（全対照）が、約 30 秒後に例外で落ち、run.sh は終了コード 1 で止まった。`selftest.json` は書かれていない（どの対照が値で通ったかは分からない）。
- ログの末尾（要点）:

```
File ".../scripts/selftest.py", line 368, in main
    Rr["P-NPZ"] = p_npz(seed)
File ".../scripts/selftest.py", line 264, in p_npz
    with tempfile.TemporaryDirectory() as td:
File ".../Lib/tempfile.py", line 943, in __exit__
    self.cleanup()
PermissionError: [WinError 32] プロセスはファイルにアクセスできません。別のプロセスが使用中です。: '...\\Temp\\tmpkuyt74xv\\p.npz'
```

- 変異 11 個・配管の合成の通し・本計算（n・o・u）・P-REPRO には進んでいない。実データの値は 1 つも作られていない。

## 2 原因（コードで確かめたこと）

- `scripts/selftest.py:272` の `z = np.load(p)` は `NpzFile` を返し、中のファイルを開いたまま持つ（読みは遅延）。`with tempfile.TemporaryDirectory()`（264 行）を抜けるときにも `z` が生きているので、Windows では開いている `p.npz` を消せず `PermissionError` になる。Mac・Linux は開いたままでも消せるので、Mac の合成では通っていた。
- **値の比べで落ちたのではない**（例外は `with` を抜けるところ・P-NPZ の比べの後）。
- 同じ型の危険がほかにないかを見た（直す必要は無いと判断）:
  - `scripts/residual.py:218` の `np.load(...)`: 別のプロセス（`subprocess.run`）の中で、プロセスが終われば閉じる。e2e_synth.py の一時フォルダの後片付けより前に終わる。
  - `selftest.py` の `pickle.load(open(...))`・`json.load(open(...))`・`open(...).write(...)`: 戻った直後に参照が無くなり CPython が閉じる。
  - `selftest.py:54`・`297`・`333`・`e2e_synth.py:88` の一時フォルダ: 中のファイルを開いたまま抜ける所は無い。
- 変異への波及: m49（`fit.py` が npz の τ の鍵を 1 つずらして書く）は `--only P-NPZ` で同じ `p_npz` を通る。直さないと、m49 も値で赤（終了コード 3）になる前に例外（終了コード 1）で落ち、`check_mutations.py` の「当たり」（`code == 3`）を満たさない。直せば両方が解ける。

## 3 直し（Mac）

`scripts/selftest.py` の `p_npz` だけを、npz を閉じる形にする。例:

```python
        np.savez_compressed(p, **flat)
        with np.load(p) as z:
            for w, units in enumerate(writers):
                ...（今の 273〜287 行をそのまま 1 段下げる）
```

- 比べの中身・セル数の数え方・`passed` の判定は変えない。`TemporaryDirectory(ignore_cleanup_errors=True)` で例外を飲む形は使わない（開いたままを隠すだけになる）。
- **P-PIN は変わらない**: P-PIN（`scripts/pinned.py` の `PIN`・conditions D3）が照らすのは tau-extend の `hmm2.py`・`data.py`・`ml.py` の 3 つだけで、この実験の `selftest.py` は入っていない。条件・SEED・門の SHA-256 の書き直しは要らない。この実験のファイルの SHA-256 は provenance の `files_sha256` に実行の時点の値として記録されるだけ。
- 条件の後の変更として扱うか: 数式・対照の判定・格子は変えない後片付けの直しなので、decisions.md に判断 11（Windows で npz を閉じずに一時フォルダを消せなかった・後片付けだけを直した・値の門は変えない）として 1 項足すのを勧める（採否は研究者）。

## 4 直した後の確かめ（Mac）

1. `python3 -I -X utf8 scripts/selftest.py "$(cat SEED)" /tmp/st.json --only P-NPZ --run-id check` が 0 で、`P-NPZ` が true。
2. `--mutate m49 --only P-NPZ` が終了コード 3（値で赤）。
3. できれば全対照（`--only` なし）を一度。Windows だけの事象なので Mac では元から通るが、直しで壊していないことの確かめになる。
4. コミット（例: `fix(experiments): unsmoothed-residual-check の P-NPZ で npz を閉じてから一時フォルダを消す（Windows） [skip ci]`・本文に `Refs: .steering/20261107-gse-paper3-unsmoothed-residual-check/`）して push。

## 5 HP Z2 での回し直し

- 前のメモ（`next-session-gse-paper3-unsmoothed-residual-run-on-hp-z2.md`）の §3 のコマンドをそのまま、worktree `C:/Users/SDS02/GSE-prototype-paper3/experiments/20261107-unsmoothed-residual-check` で回す（`git pull` で直しを取り込んでから）。データの 3 ファイルは `C:/Users/SDS02/gse-public-data/landscape/` に置いてあり、SHA-256 も照らし済み（`d9526ea7…`・`d4edd002…`・manifest `370c1d59…`）。
- worktree の `results/` に 1 回目の門のファイル 6 つ（`check_same_coauthor.json`・`check_same_cs1.json`・`input_manifest_check.json`・`pin_check.json`・`selftest_inherited.json`・`variant_manifest_check.json`）がコミットせずに残っている。回し直しで書き直されるが、混ざらないよう回す前に消してよい（1 回目の run_id のものなので使わない）。
- 1 回目は元の作業ツリーで構造の足りなさの試験（`exp/gse-structure-deficit-test`）と並走した。引き継ぐ陽性対照までで約 9.5 分。並走が続くなら本計算の見込み（約 3.5〜4 時間）より長くなる。
- 済んだ後は前のメモの §4〜§7 のとおり（値は開かない）。

## 6 次から気をつけること（Windows で回すコード）

- 一時フォルダの中で `np.load` した npz・`open` したファイルは、`with` で閉じてからフォルダを抜ける。Mac の合成の門では見えないので、HP Z2 で初めて赤になる。
