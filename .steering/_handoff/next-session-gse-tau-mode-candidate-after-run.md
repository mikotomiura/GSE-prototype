# 引き継ぎ —— τ の候補に最頻値を足す試験：職場の PC の本計算の結果が戻った後（Mac）

> 作成: 2026-11-06（Mac のセッション）。このメモを一次資料にしない。条件は `experiments/20261106-tau-mode-candidate/conditions.md`（末尾に判断 10 の「条件の後の変更」）、判断は `.steering/20261106-gse-tau-mode-candidate/decisions.md`（判断 1〜11）、職場の PC の手順と実行の記録は `next-session-gse-tau-mode-candidate-run-on-hp-z2.md`（§7 に職場の PC のセッションが追記する）。notes の骨組み（値なし・読みの形は結果の前に決めた）は `experiments/20261106-tau-mode-candidate/notes.md`。

## 0 入口の文（Mac の Claude Code に打ち込む）

```
.steering/_handoff/next-session-gse-tau-mode-candidate-after-run.md を読み、職場の PC で回した τ の候補に最頻値を足す試験の結果を確かめて、notes.md の骨組みを埋め、code-reviewer と /cross-review（Codex も加える）を通してください。push と PR は私が確かめてから。
```

作業は worktree `/Users/johnd/GSE-prototype-tau-mode`（枝 `exp/gse-tau-mode-candidate`）。

## 1 取り込み

1. `git -C /Users/johnd/GSE-prototype-tau-mode fetch origin` の後、`git -C /Users/johnd/GSE-prototype-tau-mode log --oneline HEAD..origin/exp/gse-tau-mode-candidate` で、職場の PC の結果のコミット（`docs(experiments): tau-mode-candidate の本計算の結果（HP Z2） [skip ci]` と §7 の追記）が上がっているかを見る。上がっていなければ、研究者に職場の PC の状態を聞いて止まる。
2. Mac に push していないコミットがあれば、`git -C /Users/johnd/GSE-prototype-tau-mode rebase origin/exp/gse-tau-mode-candidate` で載せ直す（職場の PC は `results/` と §7 だけを変えるので重ならない）。拒否されたら研究者に `! git -C /Users/johnd/GSE-prototype-tau-mode rebase origin/exp/gse-tau-mode-candidate` を頼む。
3. 職場の PC が push できず Drive の `GSE_ML-run_results` に zip を置いた場合は、研究者から受け取り `experiments/20261106-tau-mode-candidate/results/` に展開する（改行コードと `results/mutations/` の有無に注意）。

## 2 結果を読む前の確かめ（1 つでも外れれば notes に進まず、研究者に報告）

- `results/summary.json`・`provenance.json`・`selftest.json` の `run_id` が同じ。
- `provenance.json` の `git_head` が §7 の記録と同じで、`git diff 18792a84 <git_head> -- experiments/20261106-tau-mode-candidate/scripts experiments/20261106-tau-mode-candidate/run.sh experiments/20261106-tau-mode-candidate/mutate.sh` が空（`18792a84` はコードのコミット・HP Z2 の引き継ぎ §6）。`git_dirty_paths` が空。`input_manifest_sha256` が `e0163f1b48e94273a9d2e30fe6e6c76de642eae82311a6ca7c125896a3d74406`。
- Python 3.11.9・numpy 2.4.4。
- `input_manifest_check.json` の食い違い・欠け・余りが 0。`check_same_coauthor.json`・`check_same_cs1.json` の不一致が 0。
- `selftest.json` の `all_passed` が true（26 対照）、`mutations` の 23 個すべて `hit: true`。
- `provenance.json` の `pool_params_file_sha256` に coauthor・cs1 の値があり、`summary.json` に `pool_params_content_sha256` がある（npz の中身は開かない）。
- `repro_check.json` の `passed` が true・`mismatched` が 0・`cells` が 0 でない（前の試験の summary の葉をすべて照らす。Mac で前の試験どうしを照らすと 72,332）。**ここが外れたら結果の節を書かない**（条件 V1）。外れた数と `mismatched_sections` だけを notes の「実行と門」に書き、Mac で原因を調べる。
- `summary.json` を `python3 -I -c` で読み込み、NaN の文字列（"NaN"・"nan"）が無いこと（±∞ は "+inf" / "-inf" で書かれる）。
- `git status` で、職場の PC のコミットが `experiments/20261106-tau-mode-candidate/results/` と §7 以外を変えていない。

## 3 notes.md を埋める

- `experiments/20261106-tau-mode-candidate/` で `python3 -I scripts/report.py results/summary.json > tables.md`（手で書き換えない）。
- `notes.md` の「（結果の後）」の欄を、骨組みの読みの形のとおりに埋める。順番: 実行と門 → 4 つ組 → −∞ の人数 → 結果 1（a と b）→ 結果 2（2 段）→ 主と副の違い → 言えること・言えないこと。
- 読みの形（判断 5・10）を変えない。当てはまらないセルは値だけを書き、末尾の「結果の後に変えたこと」に書く。
- 前の試験の notes の結果 2 の但し書き（大きい τ での差を本人の寄与と分けられない）を、この試験の結果でどう狭められるかを「言えること」に書く。前の試験の notes は書き換えない（書き換えるなら研究者に聞く）。

## 4 読みの但し書き（notes に必ず書く）

- 前の試験の「読まないこと」と ADR-047 との関係の段落をそのまま守る。
- 副（最頻値が有限の書き手だけ）は、−∞ の書き手を除いた残りで、偏りうる。値には必ず人数を添える。
- −∞ が多いことそのものは、「共通に一度も出ない記号の組か頭の記号を評価に持つ書き手が多い」という記述にとどめる。どちらが多いかは summary では分からない（書き手ごとの値を開かない）。

## 5 その後

1. `code-reviewer`（notes と集計の読み違い・条件との食い違い）と `/cross-review`（Codex も加える。Codex には条件・コード・notes の集計値の文だけ。CoAuthor と CS1 の記録も書き手ごとの値も npz も送らない）。
2. tasklist（`.steering/20261106-gse-tau-mode-candidate/tasklist.md`）の「本計算の後」を閉じ、道具の対応を照らす。
3. コミット。push と PR は研究者が確かめてから（`[skip ci]`）。
4. PR の注意: この枝は前の試験の枝 `exp/gse-timeseries-tau-extend`（その下に `exp/gse-coauthor-ml-improve`）の上に立っている。前の 2 つが main に入っていなければ、PR に一緒に入る。PR の前に研究者に順番を聞く。`.codex/budget.json` が差分に入っていれば、main と食い違わないかを確かめる。
5. 論文 3（1 人ごとの学習の効き）へ: 判断 6 のとおり、主の表は変えず、a・b の表を補足資料に、限界の節の一文を形 1〜3（主が形 5 なら副）に合わせて書き換える。論文 3 は別の worktree・別のセッションで、公開 repo は GSE-prototype とは別にする（`next-session-gse-timeseries-after-tau-extend.md` §3）。
6. 共通の母数の npz（職場の PC の `DATA_DIR/landscape/tau_mode_candidate_pool_params.*.npz`）は、次の試験で使うときに、その試験の条件で照らし方（中身のハッシュ）を決める。Mac には持ち込まない。

## 6 守ること

- 書き手ごとの値（`tau_mode_candidate_writer_values.*.json`・`.pkl`）と共通の母数の npz は人が開いて読まない（職場の PC の分も Mac に持ち込まない）。holdout の一覧を開かない。O1 の 11-01 08:30 以降の記録を開かない。
- repo に出すのは集計値だけ。
- 結果を段 1 の候補の採否の根拠にしない（ADR-047 D2・D6）。
- 返答・問いは日本語で。決めることは AskUserQuestion で 1 問ずつ、推奨と理由を添えて。記号を多用しない。
