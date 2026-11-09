# 引き継ぎ —— 平滑の無い記号（u・n）と擬似残差の試験の本計算を、職場の HP Z2 で回す

> 作成: 2026-11-07（Mac のセッション）。このメモを一次資料にしない。条件は `experiments/20261107-unsmoothed-residual-check/conditions.md`（末尾に判断 7〜10 の「条件の後の変更」）、判断は `.steering/20261107-gse-paper3-unsmoothed-residual-check/decisions.md`（判断 1〜10）。下敷きは `next-session-gse-tau-mode-candidate-run-on-hp-z2.md`（§7 に前の試験の HP Z2 での実行の記録）。

## 0 入口の文（HP Z2 の新しいセッションで打ち込む）

```
HP Z2 の repo の .steering/_handoff/next-session-gse-paper3-unsmoothed-residual-run-on-hp-z2.md を読み、§2 の準備を確かめてから §3 のとおり run.sh を回してください。条件・コードは変えず、門が赤なら直さずに止めて、何が赤かだけを報告してください。結果の値は開かず、§4 の確かめだけをしてください。
```

## 1 守ること

- 条件・コード・格子を変えない。門（P-PIN・manifest 2 つ・P-D1・selftest 2 本・変異 11 個・配管の合成の通し・P-U の記録・P-REPRO）が赤なら、直さずに止めて、どの門が赤かだけを報告する。
- 書き手ごとの値（`DATA_DIR/landscape/unsmoothed_residual_writer_values.*.json`）と母数（`unsmoothed_residual_params.*.npz`）を開かない。repo に入れない。
- P-REPRO が外れたら run.sh は u に進まず終了コード 3 で止まる。そのとき `results/` に残る n・o の `summary.json`・`tables.md` は notes に使わず、コミットもしない（止まったことだけを報告する）。
- 結果を段 1 の候補の採否や ADR-047 の根拠にしない。

## 2 準備（研究者が Mac で行い、HP Z2 で確かめる）

1. 枝 `docs/gse-paper3-per-person-learning` を研究者が push する（このメモを書いた時点では未 push）。HP Z2 で取り出し、`git log --oneline -3` に §5 のコミットが含まれることを確かめる。
2. Mac の `~/gse-public-data/landscape/` から次の 3 ファイルを HP Z2 の `C:/Users/SDS02/gse-public-data/landscape/` へ写す（前の試験と同じく Drive 経由・研究者が手で）。
   - `unsmoothed_residual_coauthor.json.gz`（約 170 KB）
   - `unsmoothed_residual_cs1.json.gz`（約 480 KB）
   - `unsmoothed_residual_manifest.json`（SHA-256 `370c1d599c59f3d7bb77bc4e0d5c79e7b1b65ae4980fa091f96fa0fdfa62d494`）
   - 新しい中間は書き手の ID を持たない（書き手 → 単位 → 系列の並べと、記号の列だけ）。gzip が作成時刻を持つので、Mac で作り直すと SHA-256 が変わる。作り直したら manifest の SHA-256 をこのメモに書き直す。
3. 版: Python 3.11.9（`python`）・numpy 2.4.4（前の試験と同じ・P-REPRO はこの版でしか照らさない）。AC のスリープと休止を 0 にする。空き容量: npz は 6 つで合わせて数百 MB 以下の見込み（書き手 40 人 × 4 構造 × τ 8 値 × k 2〜3 の母数）。`DATA_DIR` のドライブに 2 GB 以上の空きがあることを確かめる。
4. 前の試験と同じ manifest `C:/Users/SDS02/Desktop/GSE_ML_run/input_manifest.json`（SHA-256 `e0163f1b48e94273a9d2e30fe6e6c76de642eae82311a6ca7c125896a3d74406`）がそのままあること。

## 3 回す（git-bash・repo の `experiments/20261107-unsmoothed-residual-check/` で）

```bash
cd experiments/20261107-unsmoothed-residual-check
PYTHON=python DATA_DIR="C:/Users/SDS02/gse-public-data" \
INPUT_MANIFEST="C:/Users/SDS02/Desktop/GSE_ML_run/input_manifest.json" \
INPUT_MANIFEST_SHA256=e0163f1b48e94273a9d2e30fe6e6c76de642eae82311a6ca7c125896a3d74406 \
VARIANT_MANIFEST="C:/Users/SDS02/gse-public-data/landscape/unsmoothed_residual_manifest.json" \
VARIANT_MANIFEST_SHA256=370c1d599c59f3d7bb77bc4e0d5c79e7b1b65ae4980fa091f96fa0fdfa62d494 \
JOBS=16 bash run.sh 2>&1 | tee "C:/Users/SDS02/gse-public-data/unsmoothed_residual_run.log"; echo "exit=${PIPESTATUS[0]}"
```

- `PYTHON` と `JOBS` は必ず渡す（既定は `python3`・6）。run.sh は Python を `-I -X utf8` で呼び、各段の頭に時刻を出す。
- 中身: P-PIN → manifest 2 つの照合 → 門の単体（tau-extend の 2 本・repro_check の測定器）→ P-D1 の門 2 つ → 引き継ぐ対照（tau-extend の `ml.py --selftest` の 15 対照）→ 足す対照 10 個 → 変異 11 個 → 配管の合成の通し → 本計算 n（CoAuthor → CS1・当てはめ → 残差）→ o → P-REPRO → u → provenance。
- 見込み（Mac の合成で測った・`results/timing.json`・判断 9）: 門は約 30〜40 分（Mac で selftest 約 7 分・変異約 4 分・配管の通し約 9 分・引き継ぐ対照は前の試験で約 8 分）。本計算は o・u が 1 列あたり約 1.6 時間（共通の当てはめが大半・CS1 が長い）、n は数分。合わせて約 3.5〜4 時間。8 時間を大きく超えても途中で止めて格子を変えない（止めるかは研究者が決める）。

## 4 済んだ後の確かめ（値は読まない）

1. 終了コード 0。`results/` に `summary.json`・`tables.md`・`selftest.json`（`mutations` 欄つき）・`selftest_inherited.json`・`e2e_synth.json`・`check_same_coauthor.json`・`check_same_cs1.json`・`input_manifest_check.json`・`variant_manifest_check.json`・`pin_check.json`・`repro_check.json`・`provenance.json`・`u_gate.json`（Mac・元からある）・`timing.json`（Mac・元からある）・`parts/`（6 つ × 2）があり、`summary.json` と `provenance.json` の `run_id` が同じこと。
2. `repro_check.json` の `passed` が true、`mismatched` が 0（照らした葉の数・最大の差だけを報告する）。
3. `summary.json` の各列・各データの `npz_check.mismatched` が 0。
4. `provenance.json` の `pin_ok` が true、`git_dirty_paths` が空。
5. コミット（`docs(experiments): unsmoothed-residual-check の本計算の結果（HP Z2） [skip ci]`・本文に `Refs: .steering/20261107-gse-paper3-unsmoothed-residual-check/`）して push。PR は出さない。push できなければ `results/` を zip にして Drive の `GSE_ML-run_results` に置く（研究者が手で）。
6. 回した時間（各段の時刻）・JOBS・Python と numpy の版・P-REPRO の照らした葉の数と最大の差・止まった場合の段と赤の内容を、このメモの末尾（§7）に追記してコミットする。

## 5 Mac での状態（このメモを書いた時点）

- 枝 `docs/gse-paper3-per-person-learning`。条件と SEED は `efa38fbf`（コードより前）、コードと合成の門は `d0c41fe9`、レビューへの対応とこのメモは `762e6b01`（この §5 の書き直しはその次のコミット）。HP Z2 では、取り出した枝の先端が `762e6b01` かその後であることを確かめる。
- Mac（Python 3.14・numpy 2.x）で、足す対照 10 個はすべて緑、変異 11 個はすべて当たり（終了コード 3・名指しの対照が赤・値で落ちた）、配管の合成の通しは緑。P-U は全行一致（CoAuthor 588,227 行・CS1 2,794,277 行・alpha を含む・外れ 0・data.py の並べとの照合 0）。Mac の selftest の結果のファイルは repo に入れていない（HP Z2 の run.sh が同じものを `results/` に書く）。
- 引き継ぐ対照（tau-extend の `ml.py --selftest`）は Mac では回していない（tau-extend で通ったコードをそのまま読み込み、SHA-256 で固定している）。HP Z2 の run.sh が回す。

## 6 その後（Mac）

- notes.md を読みの形（条件 D5・判断 7・10）のとおりに書く。`tables.md` の「列の比べ」「残差の遅れ 1」の語をそのまま使い、集計値だけを書く。
- 論文 3 の外枠の直し（C2 の限定・限界の節）に使う。

## 7 HP Z2 での実行の記録（職場の PC のセッションが追記）

### 1 回目（2026-11-09）—— 足す陽性対照で門が赤・止まった

- 場所: 別の worktree `C:/Users/SDS02/GSE-prototype-paper3`（同じ時刻に元の作業ツリーで構造の足りなさの試験が走っていたため）。先端 `a599378c`。
- 版: Python 3.11.9・numpy 2.4.4。JOBS=16（32 論理コア・構造の足りなさの試験と並走）。
- 準備: 3 ファイルの SHA-256 は manifest と一致（`d9526ea7…`・`d4edd002…`・manifest `370c1d59…`）。
- 段の時刻: 開始 12:55:06 → P-PIN・manifest 2 つ 緑 → [12:55:09] 門の単体と P-D1 緑 → [12:55:21] 引き継ぐ陽性対照 緑 → [13:04:49] 足す陽性対照と変異 → 赤で終了（run.sh の終了コード 1）。
- 赤の内容: `scripts/selftest.py` の `p_npz`（P-NPZ）が値ではなく後片付けで例外。`np.load(p)` で開いた npz を閉じないまま `tempfile.TemporaryDirectory()` を抜けるため、Windows で `p.npz` が消せず `PermissionError: [WinError 32]`（別のプロセスが使用中）。Mac では起きない Windows だけの事象と見られる。直していない。
- 本計算（n・o・u）・変異 11 個・配管の合成の通し・P-REPRO には進んでいない。`results/` に残った門のファイル（pin_check・manifest の照合 2 つ・check_same 2 つ・selftest_inherited）はコミットしていない。
- 次: Mac で直す（例: `with np.load(p) as z:`）かは研究者が決める。P-PIN が照らすのは tau-extend の 3 ファイルだけなので、selftest.py を直しても P-PIN は変わらない（上の記録の後で確かめた）。所見と直し方は `next-session-gse-paper3-unsmoothed-residual-fix-p-npz-on-mac.md`。
