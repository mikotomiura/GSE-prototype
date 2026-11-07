# 引き継ぎ —— 構造の足りなさの仮説を確かめる試験：職場の PC の本計算の結果が戻った後（Mac）

> 作成: 2026-11-07（Mac のセッション）。このメモを一次資料にしない。条件は `experiments/20261107-structure-deficit-test/conditions.md`（末尾の「条件の後の変更」に判断 10〜12）、判断は `.steering/20261107-gse-structure-deficit-test/decisions.md`（判断 1〜12）、職場の PC の手順と実行の記録は `next-session-gse-structure-deficit-run-on-hp-z2.md`（§7 に職場の PC のセッションが追記する）。下敷きは前の試験の `next-session-gse-tau-mode-candidate-after-run.md`。

## 0 入口の文（Mac の Claude Code に打ち込む）

```
.steering/_handoff/next-session-gse-structure-deficit-after-run.md を読み、職場の PC で回した構造の足りなさの試験の結果を確かめて、notes.md を書き、code-reviewer と /cross-review（Codex も加える）を通してください。push と PR は私が確かめてから。
```

作業は worktree `/Users/johnd/GSE-prototype-structure-deficit`（枝 `exp/gse-structure-deficit-test`）。

## 1 取り込み

1. `git -C /Users/johnd/GSE-prototype-structure-deficit fetch origin` の後、`git -C /Users/johnd/GSE-prototype-structure-deficit log --oneline HEAD..origin/exp/gse-structure-deficit-test` で、職場の PC の結果のコミット（`docs(experiments): structure-deficit-test の本計算の結果（HP Z2） [skip ci]` と §7 の追記）が上がっているかを見る。上がっていなければ、研究者に職場の PC の状態を聞いて止まる。
2. Mac に push していないコミットがあれば `git -C /Users/johnd/GSE-prototype-structure-deficit rebase origin/exp/gse-structure-deficit-test` で載せ直す（職場の PC は `results/` と §7 だけを変えるので重ならない）。無ければ `git -C /Users/johnd/GSE-prototype-structure-deficit merge --ff-only origin/exp/gse-structure-deficit-test`。拒否されたら研究者に `!` で頼む。
3. 職場の PC が push できず Drive の `GSE_ML-run_results` に zip を置いた場合は、研究者から受け取り `experiments/20261107-structure-deficit-test/results/` に展開する（改行コードと `results/mutations/` の有無に注意）。
4. 途中で止まった場合（§7 に止まった段と赤の内容）は、notes に進まず、止まった段ごとに §5 を見る。

## 2 結果を読む前の確かめ（1 つでも外れれば notes の結果の節に進まず、研究者に報告）

- `results/summary.json`・`provenance.json`・`selftest.json` の `run_id` が同じ。
- `provenance.json` の `git_head` が §7 の記録と同じで、次が空（`eb8bdfd9` はコードの最後のコミット・HP Z2 の引き継ぎ §6）:
  `git diff eb8bdfd9 <git_head> -- experiments/20261107-structure-deficit-test/scripts experiments/20261107-structure-deficit-test/run.sh experiments/20261107-structure-deficit-test/mutate.sh experiments/20261107-structure-deficit-test/conditions.md experiments/20261107-structure-deficit-test/SEED`
  `git_dirty_paths` が空。`input_manifest_sha256` が `e0163f1b48e94273a9d2e30fe6e6c76de642eae82311a6ca7c125896a3d74406`。
- `provenance.json` の `python` が 3.11.9、`numpy` が 2.4.4、`jobs` が 16。
- `input_manifest_check.json` の `mismatched_or_missing` と `extra` が空。`check_same_coauthor.json`・`check_same_cs1.json` の `mismatched_units` が 0 で `errors` が空。
- `selftest.json` の `all_passed` が true（19 対照）、`mutations` の 16 個すべてが `hit: true`。
- `q_gate.json` の coauthor・cs1 のそれぞれで `mismatched` が 0、`rows` が 0 でない。
- `repro_check.json` の `tau`・`mli` の両方で `mismatched` が 0、`cells` が 0 でない。**ここが外れたら結果の節を書かない**（条件 V1）。外れた数と `mismatched_sections` だけを notes の「実行と門」に書き、Mac で原因を調べる（前の 2 つの summary は repo にある。書き手ごとの値は開かない）。
- `summary.json` の `groups` に 6 組（q5_o・q5_p・q3_o・q3_p・q7_o・q7_p）があり、それぞれに coauthor と cs1 がある。
- `summary.json` を `python3 -I -c` で読み込み、NaN の文字列（"NaN"・"nan"）が無いこと。
- `git show --stat` で、職場の PC のコミットが `experiments/20261107-structure-deficit-test/results/` と HP Z2 の引き継ぎの §7 以外を変えていない。

## 3 notes.md を書く

1. 表を作る前に、`experiments/20261107-structure-deficit-test/notes.md` の骨組み（見出しと、条件 D5 の読みの形をそのまま写した文）を先に書いてコミットする。値はまだ入れない。読みの形は結果の前に決めてある（判断 5・8・9・11）ので、ここで言い換えない。
2. `cd experiments/20261107-structure-deficit-test && python3 -I scripts/report.py results/summary.json tables.md`（引数は 2 つ・手で書き換えない）。
3. 骨組みの「（結果の後）」を埋める。順番:
   1. 実行と門（§2 の値・§7 の時間と見積もりとの比べ）
   2. 表 1 の要約: 主のセル（CoAuthor P15 k = 5・15、P30 k = 30）の hmm3 の 3 列で、G_o・G_p・ΔD・S0・G0r
   3. 部分 1・部分 2・形（表 2）。主のセル 3 つがすべて同じ形のときだけ、その形と書く
   4. hmm6・hmm10・ar1〜ar3 の値（形の判定には使わない）
   5. CS1 C5 k = 5（別に読む・前の試験で hmm3 の G がもともと小さく、力が弱い）
   6. 表 3 の Kendall の τ_b（記述だけ・判定に使わない）
   7. 言えること・言えないこと
4. 部分 2 の G0 は G0r（w の τ = 0 の乱数の開始点の解 − 共通）と読む（判断 11・条件の末尾）。表の列名の「G0」は G0r である。
5. 伏せたセル（人数が 6 未満のパネル）は「伏せ」と書き、形の判定に含めない。表 2 で「未・伏せを含む」になったら、その理由を書く。
6. 読みの形に当てはまらないセルは値だけを書き、末尾の「結果の後に変えたこと」に書く。読みの形・区切り（1/2・1/10）を変えない。

## 4 読みの但し書き（notes に必ず書く）

- 並べ替えは 1 次の依存だけでなく、系列の中のゆっくりした頻度の変化も消す。D_p は 0 にならない。部分 1 の「消える」は「1 次の依存とゆっくりした変化の両方が消えたら上積みも小さくなった」と読む（条件 D5）。
- 部分 2 が「他の人でも勝つ」でも、「共通の EM が悪い局所解にある」という説明が残る。全員の共通の 10 開始点の 1 位と 2 位の差（`pool_full_diag` の `gap12`）を並べて書く。
- S0・G0r は、勝者の解ではなく τ = 0 の乱数の開始点の解で作った（判断 11）。G（τ 他人）や前の試験の G0 とは土台が違う。
- 1/2・1/10 は読みの言い方の区切りで、検定ではない。閾値と検定は置かない。
- 結果は論文 3 に入れない。段 1 の候補の採否や ADR-047 の根拠にしない（条件 D2・D6）。EM の状態に名前を付けない。CS1 を日本語や GSE の参加者へ広げない。
- 前の試験の notes（tau-extend・ml-improve・tau-mode-candidate）は書き換えない。この試験の結果が前の試験の「仮説と同じ向き」の一文をどう狭めるか・広げるかは、この試験の notes の「言えること」に書く。

## 5 止まった場合

- 門（manifest・P-D1・selftest・変異・P-Q）で止まった: 結果は無い。§7 の赤の内容を読み、合成のデータの範囲で原因を調べる。直すなら実データを見る前なので、判断 13 として書き、条件の末尾に足し、門を Mac で通してから、HP Z2 の引き継ぎを直して研究者に回し直しを頼む。
- P-REPRO で止まった（終了コード 3）: 組 q5_o の summary はあるが notes に使わない。外れた節の名前から、乱数の並べ・射影の葉の選び・前の試験との版の違いのどれかを調べる。実データの値の中身を見て直すことになるなら、研究者に聞いてから。
- 本計算の途中で落ちた: 済んだ組は `summary.json` に残る。残りの組だけを回し直す道は今のコードに無い（`run.sh` は最初からやり直す）。回し直すかは研究者に聞く。

## 6 その後

1. `code-reviewer`（notes と集計の読み違い・条件との食い違い・report.py の表と notes の値の一致）と `/cross-review`（Codex も加える）。Codex に渡すのは条件・コード・notes と tables.md の集計値の文だけ。CoAuthor と CS1 の記録も、書き手ごとの値（pkl）も送らない。
2. tasklist（`.steering/20261107-gse-structure-deficit-test/tasklist.md`）の「職場の PC」「結果の後」を閉じる。requirement.md の受け入れ条件を照らす。
3. コミット。push と PR は研究者が確かめてから（`[skip ci]`）。
4. PR の注意: この枝は `exp/gse-tau-mode-candidate` の `05a65021` から切った。その下に `exp/gse-timeseries-tau-extend`・`exp/gse-coauthor-ml-improve` がある。前の試験の枝が main に入っていなければ、PR に一緒に入る（2026-11-07 時点で origin/main から 46 コミット先）。PR の前に研究者に順番を聞く。
5. 次の問い（結果によって）: 形 A なら「本人の上積み」は構造の足りなさの補いとして読み、段 1 の個人化の議論とは切り離す。形 B なら対抗の説明（母数の多い構造は本人の記録で推せない）を詰める試験を考える。形 C なら、どの列・どのセルで割れたかを書き、追加の計算が要るかを研究者に聞く。どれも研究者が決める。

## 7 守ること

- 書き手ごとの値（HP Z2 の `DATA_DIR/landscape/structure_deficit_writer_values.*.pkl`）は人が開いて読まない。Mac に持ち込まない。前の試験の書き手ごとの値・共通の母数も同じ。holdout の一覧を開かない。
- repo に出すのは集計値だけ。書き手・セッション・課題の番号を書かない。
- 返答・問いは日本語で。決めることは AskUserQuestion で 1 問ずつ、推奨と理由を添えて。記号を多用しない。
