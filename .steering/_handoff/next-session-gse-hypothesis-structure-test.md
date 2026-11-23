# 引き継ぎ —— 仮説を確かめる試験（構造の族と量子化の列を増やす）の条件とコード（Mac）

> 作成: 2026-11-07（Mac）。このメモを一次資料にしない。研究者が 2026-11-07 に「論文 3 と並行して回す・結果は論文 3 に入れない」を選んだ。論文 3 は `next-session-gse-paper3-per-person-learning.md`。

## 0 入口の文（Mac の Claude Code に打ち込む）

```
.steering/_handoff/next-session-gse-hypothesis-structure-test.md を読み、構造の族と量子化の列を増やして「本人の上積みは構造の足りなさの補い」という仮説を確かめる試験を /start-task から始めてください。grill で問いと範囲を決め、条件と SEED をコードより前にコミットし、本計算は職場の PC に渡す形にしてください。push と PR は私が確かめてから。
```

## 1 問いの出どころ

- 仮説（`experiments/20261104-coauthor-ml-improve/notes.md` 185 行）: B で本人の EM が共通に勝っていたのは、3 状態の HMM が前の記号への強い依存を運べず、その不足を本人の当てはめが一部埋めていたためかもしれない（人ごとの違いではなく、構造の足りなさを人ごとに補っていた）。
- ここまでの材料（`experiments/20261104-timeseries-tau-extend/notes.md` 170・208・220 行）: hmm3 で本人の上積みが大きく（CoAuthor で最大 +0.19）、ar1〜ar3 で小さい（約 1e-3 以下）。「仮説と同じ向き」とだけ書き、確かめたとは書いていない。理由は構造の族が 2 つ（hmm と AR(1)-HMM）、量子化の列が 1 つ（26 記号）だけだから。
- `experiments/20261106-tau-mode-candidate/notes.md`: CoAuthor の ar の大きい τ の差は、中央値の比べでは主に最頻値と共通の違い（形 1）。hmm3 は形 2（本人の寄与が主）。
- 確かめる形の候補（grill で決める・決めるのは研究者）: 構造を強めるにつれて本人の上積みが小さくなるか。例として、状態の数（K）、AR の次数（AR(2) など）、量子化の列の粗さ・細かさ（26 記号の他の列）。

## 2 始める前に

- 新しい worktree・新しいセッションで行う。論文 3 のセッションとチェックアウトを共有しない。τ の 3 本の枝が main に入っていれば main から切る。入っていなければ `exp/gse-tau-mode-candidate` から切るかを研究者に聞く。
- 実装系なので `/start-task` が先。設計判断があるので `/reimagine` で初回案と比べる。条件は reproducibility-discipline に従う（条件と SEED をコードより前にコミット・provenance・前の試験との P-REPRO・合成の陽性対照と変異の門）。
- 前の試験のコード（`experiments/20261106-tau-mode-candidate/scripts/`）と職場の PC の手順（`next-session-gse-tau-mode-candidate-run-on-hp-z2.md`）を写して変える形が近い。前の試験の P-REPRO は 72,332 セルで照らせた。
- 新しい量子化の列を作るなら、入力の作り直し（P-D1 にあたる門）が要る。入力は職場の PC の `C:/Users/SDS02/gse-public-data`（manifest の SHA-256 `e0163f1b…3d74406`）で、Mac には記録が無い。Mac の合成で門を通してから職場の PC に渡す。
- 計算の量: 前の試験は約 1.9 時間（共通の当てはめが大半・CS1 の共通 4,084 秒）。構造を増やすと共通の当てはめが比例して増える。Mac の合成で時間を測ってから、条件に見積もりを書く。G-GEAR は 11 月ふさがり。職場の PC（HP Z2・JOBS = 16・Python 3.11.9・numpy 2.4.4）で回す。

## 3 守ること

- 結果は論文 3 に入れない（論文 3 の範囲は凍結）。次の論文か改訂の材料にする。
- 読まないこと（前の試験の notes）を引き継ぐ: EM の状態に名前を付けない・閾値と検定を置かない・CS1 を日本語や GSE の参加者へ広げない・26 記号の列を予測できることは作業上の認知状態の構造ではない。
- 書き手ごとの値と共通の母数は repo の外（職場の PC の `DATA_DIR/landscape/`）に置き、人が開かない。repo に出すのは集計値だけ。holdout の一覧を開かない。
- 結果を段 1 の候補の採否や ADR-047 の根拠にしない（D2・D6）。
- 計算の前に code-reviewer、結果の後に code-reviewer と /cross-review（Codex を加える・Codex には条件・コード・集計値の文だけ）。
- 返答・問いは日本語で。決めることは AskUserQuestion で 1 問ずつ、推奨と理由を添えて。記号を多用しない。
