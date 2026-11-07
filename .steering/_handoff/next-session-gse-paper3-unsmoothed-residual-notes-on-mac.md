# 引き継ぎ —— HP Z2 の本計算（平滑の無い記号 u・n と擬似残差）が済んだ後、Mac で notes.md を書き、論文 3 の外枠を直す

> 作成: 2026-11-07（Mac のセッション・本計算の前）。このメモを一次資料にしない。条件は `experiments/20261107-unsmoothed-residual-check/conditions.md`（D5 が読みの形・末尾に判断 7〜10 の「条件の後の変更」）、判断は `.steering/20261107-gse-paper3-unsmoothed-residual-check/decisions.md`（判断 1〜10）。HP Z2 の手順と実行の記録は `next-session-gse-paper3-unsmoothed-residual-run-on-hp-z2.md`（§4 の確かめ・§7 の記録）。notes の形の手本は `experiments/20261104-timeseries-tau-extend/notes.md`。

## 0 入口の文（Mac の新しいセッションで打ち込む）

```
/Users/johnd/GSE-prototype-paper3/.steering/_handoff/next-session-gse-paper3-unsmoothed-residual-notes-on-mac.md を読み、§2 の確かめをしてから §3 のとおり notes.md を書き、§4 のとおり論文 3 の外枠を直してください（worktree /Users/johnd/GSE-prototype-paper3）。読みの形は条件 D5 のまま使い、結果を見た後に変えた所は notes の末尾に書いてください。決めることは AskUserQuestion で聞き、push と PR は私が確かめてから。
```

## 1 守ること

- 書き手ごとの値（`~/gse-public-data/landscape/unsmoothed_residual_writer_values.*.json`）と母数（`unsmoothed_residual_params.*.npz`）を開かない。Mac には来ない見込みだが、来ても開かない。notes には `results/summary.json`・`tables.md` の集計値だけを書く。書き手・セッション・課題の番号を書かない。
- 読みの形（条件 D5・判断 7・10）を結果を見た後に変えない。当てはまらない所が出たら、変えずに止めて研究者に聞き、notes の「結果の後に変えたこと」に書く。
- `tables.md` の「列の比べ」「残差の遅れ 1」の語（残る・縮む・逆・同じ向き・0・割れる・欠けがある・比べない（o = 0）・ar で運べる・ar でも残る・どちらでもない）は `report.py` が機械で当てたもの。notes ではその語をそのまま使い、言い換えない。
- 条件の「読まないこと」を守る: n を「依存の出どころをすべて外した列」と書かない。n の大きさを o・u と比べない（向きだけ）。残差の自己相関が 0 に近いことを「モデルが正しい」と書かない（この軸の周辺のこの遅れでは運べていない依存が小さい、と書く）。CS1 を日本語・IME・GSE の参加者へ広げない。セッション・課題は日ではない。
- 結果を段 1 の候補の採否や ADR-047 の根拠にしない（ADR-047 D2・D6）。結果は論文 3 の外枠の直し（C2 の限定・限界の節）にだけ使う（論文 3 の判断 11）。
- tau-extend と構造の足りなさの試験（`/Users/johnd/GSE-prototype-structure-deficit`・枝 `exp/gse-structure-deficit-test`）のディレクトリ・条件・コードを変えない。
- 公開物（`papers/`）に GSE の名前・内部のパス・番号（ADR・判断・条件の記号）を書かない（`papers/README.md`）。
- キーストロークの内容・NDJSON・書き手ごとの値を外部の LLM（Codex を含む）に送らない。/cross-review に渡すのは notes と外枠の diff だけ（集計値だけなので送ってよい）。

## 2 入口の確かめ（値を読む前）

1. `git -C /Users/johnd/GSE-prototype-paper3 pull`（研究者が push 済みのとき）。HP Z2 の結果のコミット `docs(experiments): unsmoothed-residual-check の本計算の結果（HP Z2） [skip ci]` と、HP Z2 の引き継ぎ §7 の記録のコミットが入っていること。
   - HP Z2 から push できなかった場合は、Drive の `GSE_ML-run_results` に `results/` の zip がある。研究者に場所を聞き、展開して `experiments/20261107-unsmoothed-residual-check/results/` に置く（`u_gate.json`・`timing.json` は Mac のものを残す・上書きしない）。zip の中に `unsmoothed_residual_writer_values` や `.npz` が入っていたら開かずに止めて研究者に言う。
2. HP Z2 の引き継ぎ §4 の 1〜4 を Mac でもう一度照らす（値は読まない・件数と真偽だけ）。
   - 終了コード 0 の記録が §7 にある。§4 の 1 のファイルがそろい、`summary.json`・`provenance.json`・`selftest.json` の `run_id` が同じ（`e2e_synth.json` は run_id を持たない）。
   - `repro_check.json` の `passed` が true・`mismatched` が 0。
   - `summary.json` の各列・各データの `npz_check.mismatched` が 0。
   - `provenance.json` の `pin_ok` が true・`git_dirty_paths` が空。`git_head` の時点で `git diff 88ff16a8 <git_head> -- experiments/20261107-unsmoothed-residual-check/scripts experiments/20261107-unsmoothed-residual-check/run.sh experiments/20261107-unsmoothed-residual-check/mutate.sh papers/per-person-learning/kit/symbols` が空（Mac で門を通したコードと同じか）。`files_sha256` の `conditions.md` が今の repo のものと同じ。
   - `provenance.json` の `python` が 3.11.9・`numpy` が 2.4.4。
3. どれかが外れたら notes を書かずに止め、何が外れたかだけを研究者に報告する。とくに P-REPRO が外れて止まった（終了コード 3）場合、`results/` に残る n・o の値は notes に使わない。
4. `tables.md` は `report.py` が `summary.json` から作ったもの。Mac で `python3 -I scripts/report.py` を回し直して作り直さない（HP Z2 の版を使う）。手で直さない。

## 3 notes.md を書く（`experiments/20261107-unsmoothed-residual-check/notes.md`）

形は tau-extend の notes に合わせる。値は `summary.json`・`tables.md` からだけ取る。

1. 冒頭: 条件のコミット（`efa38fbf`・末尾の判断 7〜10）、コード（`d0c41fe9`・`762e6b01`）、作業記録、値の置き場所。
2. 読まないこと（条件の再掲）。
3. 実行と門: 機械と版・`run_id`・`git_head`・時間（§7 の各段の時刻と、見積もり 3.5〜4 時間（判断 9・`results/timing.json`）との比べ）。門と対照の表（P-PIN・manifest 2 つ・P-D1 2 つ・selftest 2 本の件数・変異 11 個の当たり・配管の合成の通し・P-U（Mac・`u_gate.json`: CoAuthor 588,227 行・CS1 2,794,277 行・外れ 0）・P-REPRO の照らした葉の数と最大の差・npz の照合）。
4. 結果 1 —— 問い (a) 依存の出どころ: `tables.md` の「列の比べ」をそのまま写し、主のセル 3 つ（CoAuthor P15 k = 5・15、CS1 C5 k = 5）で G・C2a・C2b ごとに u と n の語を書く。3 セルで語がそろったときだけその語で 1 文にし、割れたら値を並べて「割れる」と書く。k = 1 は値だけ。n は向きだけ（大きさを比べない理由: 記号が o の約 1/30）。CS1 の 2 段で o = 0 のセルは「比べない（o = 0）」と u の値と向きだけ。
5. 結果 2 —— 問い (b) モデル検査: `tables.md` の「残差の遅れ 1 の自己相関」をそのまま写し、主のセル・列ごとに「ar で運べる」「ar でも残る」「どちらでもない」を書く。遅れ 2〜10・較正・副（押下のある時刻）は値を並べるだけで読みの語に使わない。
6. 副の結果: 尤度の差の表（列ごと）で、主の読みを変えるものがあるかだけを見る。
7. 伏せた箇所（6 人未満）・欠け（n の学習か評価の記号が 0 の書き手の人数）。
8. 計算の前に決めた条件から外れたこと・条件の後の変更（判断 7〜10 の要約。HP Z2 で逸脱があれば §7 から）。
9. 言えること・言えないこと: D5 の「論文への持ち込みの書き方」をそのまま当てる。
   - G・C2a・C2b が u・n で「残る」「同じ向き」なら、C2 を「この記号化の上で」に限る必要は小さくなる（ただし休止の秒の特徴が窓をまたぐ記憶を持つことは残る）。
   - u で「縮む」「逆」なら、C2 は平滑の作りに依る分があり、C2 を元の記号化の上の測定に限る。
   - 割れたら、どのセル・どの量で割れたかを書き、限定の強い方（元の記号化の上の測定）を採る。
10. 結果の後に変えたこと（無ければ「無い」と書く）。

書いたら `tasklist.md` の「P-REPRO が通る」「notes.md」に印を付け、`decisions.md` に notes の読みで判断したこと（あれば）を判断 11 以降として足す。

## 4 論文 3 の外枠を直す（`papers/per-person-learning/manuscript/outline.md`）

- 対象: C2 の Strength の行（いまは "two structure families, one quantization" と書いている）と、Out of scope / 限界の節。ほかに C1 の Strength に依存の出どころの一文が要るかを見る。
- 書き方は §3 の 9 の結論に従う。値は集計の中央値だけを、英語で、論文の語（unsmoothed symbols・non-overlapping windows・randomized quantile pseudo-residuals）で書く。GSE の名前・内部のパス・ADR や判断の番号を書かない。
- 残差の置き場所（本文か補足か）はこの試験では決めていない（条件 D5）。AskUserQuestion で研究者に聞く。推奨は、読みの語が「ar で運べる」なら補足の表 1 つと本文 1 文、「ar でも残る」「どちらでもない」なら限界の節に 1 段落、を添える。
- 構造の足りなさの試験の結果がまだなら、C2 の Strength の「確かめていない」の一文はそのまま残す（あちらの結果で直す）。こちらの結果で直すのは「平滑と窓の重なり」と「モデル検査」の 2 点だけ。
- 引用を足すとき（擬似残差の原典 Dunn and Smyth 1996 は 2026-11-07 の時点で `docs/references.md` に未登録）は grep で確かめ、無ければ citation-ssot の手順で登録する。
- 直した後、`attack-me` を回すかを研究者に聞く（判定の推移を数えてから・Codex を加える）。

## 5 完了処理

- 場面ごとの道具: notes と外枠の diff → code-reviewer と /cross-review（Codex・集計値だけ）。決めること → AskUserQuestion。
- `design.md`・`decisions.md` を最終化し、`tasklist.md` の完了処理に印を付ける。
- コミット: `docs(experiments): unsmoothed-residual-check の notes と論文 3 の外枠の直し [skip ci]`（本文に `Refs: .steering/20261107-gse-paper3-unsmoothed-residual-check/`）。push と PR は研究者が確かめてから。`.codex/budget.json` の変更はコミットしない。

## 6 この時点の状態（Mac・2026-11-07）

- 枝 `docs/gse-paper3-per-person-learning`。条件 `efa38fbf`、コード `d0c41fe9`、レビューへの対応と HP Z2 の引き継ぎ `762e6b01`・`5ee2ffc8`、文献の取り直し `88ff16a8`。このメモはその次のコミット。
- HP Z2 の引き継ぎは Drive の handoff フォルダにも置いた（ファイル ID `16nqnqbXEg40r17xMP2O-N5n0WdPqbNqq`）。
- 新しい中間 3 ファイル（manifest の SHA-256 `370c1d599c59f3d7bb77bc4e0d5c79e7b1b65ae4980fa091f96fa0fdfa62d494`）は研究者が Drive 経由で HP Z2 へ写す。
- 文献: 論文 3 のカードで未読だった本文 7 件は `88ff16a8` で照合済み。次に読む候補は Interspeech 2012 の relevance factor・Kuhn and De Mori 1990・Bellegarda 2004 の 3 つ（未着手）。
