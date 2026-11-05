# 引き継ぎ —— τ の格子を広げる試験：職場の PC の本計算の結果が戻った後（Mac）

> 作成: 2026-11-05（Mac のセッション）。このメモを一次資料にしない。条件は `experiments/20261104-timeseries-tau-extend/conditions.md`（末尾に判断 6 の「条件の後の変更」）、判断は `.steering/20261104-gse-timeseries-tau-extend/decisions.md`（判断 1〜6）、職場の PC の手順と実行の記録は `next-session-gse-timeseries-tau-extend-run-on-hp-z2.md`（§7 に職場の PC のセッションが追記する）。

## 0 入口の文（Mac の Claude Code に打ち込む）

```
.steering/_handoff/next-session-gse-timeseries-tau-extend-after-run.md を読み、職場の PC で回した τ の格子を広げる試験の結果を確かめて、notes.md の骨組みを埋め、code-reviewer と /cross-review を通してください。push と PR は私が確かめてから。
```

作業は worktree `/Users/johnd/GSE-prototype-tau-extend`（枝 `exp/gse-timeseries-tau-extend`）。

## 1 取り込み

1. `git -C /Users/johnd/GSE-prototype-tau-extend fetch origin` の後、`git -C /Users/johnd/GSE-prototype-tau-extend log --oneline HEAD..origin/exp/gse-timeseries-tau-extend` で、職場の PC の結果のコミット（`docs(experiments): timeseries-tau-extend の本計算の結果（HP Z2） [skip ci]` と、引き継ぎ §7 の追記）が上がっているかを見る。上がっていなければ、研究者に職場の PC の状態を聞いて止まる（推測で進めない）。
2. Mac にはまだ push していないコミットが 2 つある（`f15d4b2b`・notes.md の骨組み・結果の前に書いた／このメモの追加）。職場の PC のコミットは `results/` と引き継ぎの §7 だけを変えるので、重ならない。`git -C /Users/johnd/GSE-prototype-tau-extend rebase origin/exp/gse-timeseries-tau-extend` で載せ直す。私から rebase が拒否されたら、研究者に `! git -C /Users/johnd/GSE-prototype-tau-extend rebase origin/exp/gse-timeseries-tau-extend` を頼む。
3. 職場の PC が push できず、Drive の `GSE_ML_run` に results の zip を置いた場合は、研究者から受け取り、`experiments/20261104-timeseries-tau-extend/results/` に展開する（改行コードの違いと `results/mutations/` の有無に注意）。

## 2 結果を読む前の確かめ（1 つでも外れれば notes に進まず、研究者に報告）

- `results/summary.json` と `results/provenance.json`（と `selftest.json`）の `run_id` が同じ。
- `provenance.json` の `git_head` が、職場の PC で回したコミット（引き継ぎ §7 の記録）と同じで、`scripts/` が `e2ac9d74` と同じ（`git diff e2ac9d74 <git_head> -- experiments/20261104-timeseries-tau-extend/scripts experiments/20261104-timeseries-tau-extend/run.sh experiments/20261104-timeseries-tau-extend/mutate.sh` が空）。`git_dirty_paths` が空。`input_manifest_sha256` が `e0163f1b48e94273a9d2e30fe6e6c76de642eae82311a6ca7c125896a3d74406`。
- Python 3.11.9・numpy 2.4.4（前回と同じ版。違えば P-REPRO は照らせない）。
- `input_manifest_check.json` の食い違い・欠け・余りが 0。`check_same_coauthor.json`・`check_same_cs1.json` の不一致が 0。
- `selftest.json` の `all_passed` が true（17 対照）、`mutations` の 11 個すべて名指しの対照が赤（`hit: true`）。
- `repro_check.json` の `passed` が true・`mismatched` が 0・`cells` が 0 でない。**ここが外れたら結果の節を書かない**（条件 V1。同じ機械・同じ版なので、外れはコードの変更の誤りを示す）。外れたセルの数と最大の差だけを notes の「実行と門」に書き、原因を Mac で調べる。
- `git status` で、職場の PC のコミットが `experiments/20261104-timeseries-tau-extend/results/` と引き継ぎの §7 以外を変えていない。

## 3 notes.md を埋める

- `python3 -I scripts/report.py results/summary.json > tables.md` で全表を作る（`experiments/20261104-timeseries-tau-extend/` で。手で書き換えない）。
- `notes.md` の骨組み（`f15d4b2b`）の「（結果の後）」の欄を埋める。読みの形は結果を見る前に決めてあるので、そのとおりに書く。結果を見た後に読みの形を変えたら、末尾の「結果の後に変えたこと」に書く。
- 結果 1〜3 は、それぞれ問い (a)（上の端への張り付きは解けたか）・(b)（本人が共通に届かないのは格子の端のせいか）・(c)（2 段の組み方で本人の上積みは k とともにどう変わるか）に答える形で書く。
- 前回の notes（`experiments/20261104-coauthor-ml-improve/notes.md`）の「読みの仮説」（B で本人が勝っていたのは構造の足りなさの補い）への材料は、「仮説と同じ向き」とまでで止め、確かめられたとは書かない。

## 4 読みの但し書き（notes に必ず書く）

- 条件の「読まないこと」をそのまま守る（EM の状態に名前を付けない・閾値と検定を置かない・セッションと課題は日ではない・CS1 を日本語や GSE の参加者へ広げない・ラベルを使わない）。
- 2026-11-05 に main に入った ADR-047 との関係を 1 段落書く。この試験は D2（推定は契機を作らない・改良は段 1 の後の候補の準備として続ける）と D6（公開データは推定の改良と方法の知見に限る）の範囲の仕事である。結果を段 1 の候補の採否の根拠にせず、主張（観測で見分けられる所と保留すべき所）の根拠にもしない。

## 5 その後

1. `code-reviewer`（notes と集計の読み違い・条件との食い違い）と `/cross-review`（Codex には条件・コード・notes の集計値の文だけ。CoAuthor と CS1 の記録も書き手ごとの値も送らない）。
2. tasklist の残り（P-REPRO の確かめ・notes・レビュー）を閉じる。
3. コミット。push と PR は研究者が確かめてから（`[skip ci]`）。
4. PR の注意: この枝は前回の試験の枝 `exp/gse-coauthor-ml-improve`（main に未マージ・PR 無し）の上に立っているので、PR を出すと前回の試験も一緒に main に入る。ADR-047 Context 3 は前回の notes を引いているので、入るのは望ましい。ただし枝の差分に `.codex/budget.json` が含まれる（前回の枝のコミット由来）。PR の前に、main の `.codex/budget.json` と食い違わないかを確かめ、食い違えば研究者に扱いを聞く。
5. 次の問いにつなぐ引き継ぎを書く（時系列の段の組み方の材料・ADR-046 D3・ADR-047 D2）。

## 6 守ること

- `~/gse-public-data/landscape/timeseries_tau_extend_writer_values.*.json`（書き手ごとの値）は人が開いて読まない（職場の PC の分も Mac に持ち込まない）。holdout の一覧を開かない。O1 の 11-01 08:30 以降の記録を開かない。
- repo に出すのは集計値だけ（書き手・セッション・課題の番号と範囲の端を出さない）。
- 返答・問いは日本語で。決めることは AskUserQuestion で 1 問ずつ、推奨と理由を添えて。記号を多用しない。
