# 引き継ぎ —— CoAuthor と CS1 の改善の試験：本計算の結果が戻った後（Mac）

> 作成: 2026-11-04（Mac のセッション）。このメモを一次資料にしない。条件は `experiments/20261104-coauthor-ml-improve/conditions.md`、判断は `.steering/20261104-gse-coauthor-ml-improve/decisions.md`（判断 1〜13）、設計は同じディレクトリの `design.md`（判断 3〜13 が優先）。

## 0 入口の文（Mac の Claude Code に打ち込む）

```
.steering/_handoff/next-session-gse-coauthor-ml-after-run.md を読み、職場の PC で回した CoAuthor と CS1 の改善の試験の結果を確かめて、notes.md を書き、code-reviewer と /cross-review を通して push してください（PR は私が確かめてから）。
```

作業は worktree `/Users/johnd/GSE-prototype-coauthor-ml`（枝 `exp/gse-coauthor-ml-improve`）。最初に `git -C /Users/johnd/GSE-prototype-coauthor-ml fetch origin && git -C /Users/johnd/GSE-prototype-coauthor-ml merge --ff-only origin/exp/gse-coauthor-ml-improve` で職場の PC の結果のコミットを取り込む（push できなかった場合は、Drive の `GSE/GSE_ML_run` に置かれた results の zip を研究者から受け取り、`results/` に展開する）。

## 1 結果を読む前の確かめ（1 つでも外れれば notes に進まず、研究者に報告）

- `results/summary.json` と `results/provenance.json` の `run_id` が同じ。
- `provenance.json` の `git_head` が、職場の PC で回したときのコミット（引き継ぎ `next-session-gse-coauthor-ml-run-on-hp-z2.md` の末尾の追記）と一致し、`git_dirty_paths` が空。`input_manifest_sha256` が `e0163f1b48e94273a9d2e30fe6e6c76de642eae82311a6ca7c125896a3d74406`。
- `results/input_manifest_check.json` の `mismatched_or_missing` と `extra` が 0。`check_same_coauthor.json`・`check_same_cs1.json` の不一致が 0。
- `results/selftest.json` の `all_passed` が true、`mutations` の 10 個すべて `hit: true`、`run_id` が同じ。
- 職場の PC の Python・numpy の版（provenance）を notes に書く。Mac の合成の selftest（Python 3.14.4・numpy 2.5.2）と値が小数の末尾で違いうるのは、版の違いとして扱う。

## 2 notes.md に書くこと（`experiments/20261104-coauthor-ml-improve/notes.md`）

1. 4 つ組（ADR-042 D4）: データ組ごとに `four_tuple`（人数・人ごとの単位の数・評価の問いの数と陽性の数・停滞のエピソード「使わない（0）」）。
2. EM（`datasets.<組>.em`）: パネル × k で、構造ごとの「τ 他人（主）」の Δ（本人 − r1・本人 − 同じ構造の共通・本人 − K = 3 の共通・本人 − F-b）の中央値 [四分位]・良い側の割合・区間。τ 固定 4 行と τ 本人 CV（副）は表にまとめる。K 本人 CV（族ごと）と選ばれた構造の人数。窓に押下のある記号だけの平均（`pressed`）を全記号（`all`）と並べる（CS1 の長い空白が平均を決めていないか）。B の問い「r1 に勝てるか」に答える形で書く。
3. ロジスティック（`datasets.<組>.lg`）: パネル × k × 問いの組（CS1 は `main` と `all`）× 版（`tab` 主・`recal` 副）で、書き手の中の一致度 C（と C − 0.5・区間・組のある人数）と、Brier の 本人 − B0-self。行は 本人（λ 主）・本人（λ 副）・λ 固定 5・共通（1 つの切片）・B0-self・B0-pool。選ばれた λ の人数と、λ の主が本人の CV で決まった数と他人に落ちた数。CS1 の書き手ごとの AUC の四分位。
4. 共通の逆向きの分け: (a) 共通（1 つの切片）の合わせた AUC と C、(b) `coef_split` の 1 つの切片の版と書き手の切片の版の係数の符号、w を除く版で符号が変わる割合。B の課題 4 に答える形で書く。
5. 診断: 共通・本人の EM の収束しなかった開始点・目的が減った回・勝った開始点の種類・1 位と 2 位の差。ロジスティックの 1 類だけ・|β − β_共通| > 10・収束しなかった数。`probe_stats`（捨てた問いの数）。`seconds`。
6. 伏せた箇所: 人数 6 未満で伏せたもの（`suppressed`）を数え、どこで伏せたかを書く（条件 D5）。

## 3 読みの但し書き（notes に必ず書く）

- 代理ラベル（CoAuthor の提案の要求・CS1 の補完の受け入れ）は道具の使用の出来事で、詰まりでも作業上の認知状態でもない。結果を段 1 の候補の根拠にせず、MhD が学習できた根拠にもしない。EM の状態に Flow / Incubation / Stuck の名前を付けない（ADR-046 D1）。閾値・検定を置かない。
- r1 に追いついても、26 記号の量子化の列を予測できることで、作業上の認知状態の構造ではない。CS1 の結果を日本語・IME・文章を書く作業・GSE の参加者へ広げない。
- CoAuthor の λ の主（本人の CV）は、折り目の問いが 1 人 6 問ほどしかなく雑音で決まる。合成の P-LAM の 3 問の版（`selftest.json` の `P-LAM.not_gate_3_per_unit`）で、β が違っても同じでも 17 人中 9 人が λ = 0.1 を選んだ（判断 10）。CoAuthor の λ 主の行はこの但し書きと並べて読む。
- 全員の共通の開始点を 10 にしたが（判断 9）、本人の当てはめの開始点は 2 つのまま。AR の本人の当てはめが局所解に落ちる割合は実データでは測っていない（合成では共通の解から始めると P-AR が通った）。
- CS1 の feat 行の `obs` は replay が出した値で、独立の参照とは照らしていない（参照の中間に obs が無い・判断 12）。
- B の共通（他人の評価の本を含む）・標準化・r1 の頭と定義が違うので、B の値との比べは目安。
- 逸脱と条件の後の変更（判断 7〜13）を列挙する。結果を見た後に条件を変えたら逸脱として書く。

## 4 その後

1. `code-reviewer`（notes と集計の読み違い・条件との食い違い）と `/cross-review`（Codex には条件・コード・notes の集計値の文だけ。CoAuthor と CS1 の記録も書き手ごとの値も送らない）。
2. tasklist の残りを閉じる（本計算・notes・レビュー・引き継ぎ）。
3. コミット・push。PR は研究者が確かめてから（`[skip ci]`）。
4. B の続きの次の問い（改善の 1・3 は段 1 の 1 人ごとのロジスティックの材料、2 は時系列の段の候補の材料・ADR-046 D3）につなぐ引き継ぎを書く。

## 5 守ること

- `~/gse-public-data/landscape/coauthor_ml_improve_writer_values.*.json`（書き手ごとの値）は人が開いて読まない（職場の PC の分も Mac に持ち込まない）。`~/gse-public-data/landscape/holdout.json`・`~/gse-public-data/cs1/holdout.json` の一覧を開かない。O1 の 11-01 08:30 以降の記録を開かない。
- repo に出すのは集計値だけ（書き手・セッション・課題の番号と範囲の端を出さない）。
- 返答・問いは日本語で。決めることは AskUserQuestion で 1 問ずつ、推奨と理由を添えて。記号を多用しない。
