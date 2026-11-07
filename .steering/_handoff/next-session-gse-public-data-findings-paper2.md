# 次のセッション —— 論文 2（停滞の形）: 濃くする計算で単独にできるかを決める

> 作成: 2026-11-07。始めるのは論文 3（τ・`.steering/_handoff/next-session-gse-tau-trio-pr-then-paper3.md`）の後（判断 43・研究者の選択）。論文 3 の草稿の間に Mac の空きで計算だけ回すのは可（研究者に確かめてから）。このメモを一次資料にしない。

## §1 何を決めるか

- 知見 2（停滞の形）を単独の論文にできるか。判断 4 の文献のラウンド（`docs/literature/20261105-public-data-findings-novelty.md` のカード 1〜2 の 5）では 5 点のうち 3 点が既出、残る 2 点は弱い。
- 先行 0 件の 3 つを公開データで回し、その結果で決める（判断 43）。
  1. 揺れの分解: 打鍵・セッション（または課題）・日・人の 3 水準以上で、停滞の数と長さの揺れがどの水準にあるか。
  2. 数え上げとの比: 停滞の数をポアソンの見込みと比べ、過分散の大きさをデータごとに出す（O1 の「日の揺れ 3 倍」は使わない）。
  3. multiverse: 停滞の定義（C0・C1・C2・θ の分位）・窓の長さ・切り方を振り、停滞の率・長さ・データの間の順位がどれだけ動くか。推定の水準の桁違いが作業の違いか切り方の違いかを、切り方を揃えて確かめる。
- 芯の候補の主張: 「停滞のラベルは分析者の切り方でどれだけ変わるか」（論文 1 と同じ読者・判断 5）。外れたら論文 1 の改訂か論文 3 の補足に回す。

## §2 手順

1. `/start-task` で新しいタスク（worktree を切る・memory の parallel-sessions-share-checkout）。`paper-write` Skill の Step 0（誰に読ませて何を変えるか）を研究者に確かめる。
2. 文献の追いかけ: 判断 4 から日が経っているので、3 つの計算に当たる先行が出ていないかを `/literature-review` で短く（既存の文献は番号だけ挙げさせる）。
3. 条件を先にコミットしてから回す（`experiments/<日付>-stall-shape-*/`・`reproducibility-discipline`）。単独にする判定の基準（例: 揺れのどの水準が支配的か・multiverse で順位が入れ替わるか）も、回す前に条件に書く。事前登録を OSF に出すかは研究者に聞く。
4. 結果で単独にするかを研究者に聞く（AskUserQuestion・推奨は研究として強いか）。単独なら外枠 → /reimagine → attack-me。

## §3 材料

- `experiments/20261102-stall-decomposition/`（O1 の部分は使わない）・`20261104-cs1-landscape/`・`20261102-public-data-landscape/`・`20261101-klicke-early-stall-trigger/`・`20261101-coauthor-pre-stall-signal/`・`20261103-stall-candidates-c1c2c6/`
- データ `~/gse-public-data/`（CoAuthor・KLiCKe・CS1。SWELL-KW を足すかは研究者に聞く）。
- 推定器と replay は公開 repo `~/stall-runup-equivalence` の切り出し版でも動く（論文 1 と同じ版を使うと比べやすい）。

## §4 気をつけること

- O1 は使わない（判断 7）。書き手ごとの値・CS1 のデータを repo の外へ・外部の LLM へ出さない（CS1 は集計値だけの約束・`next-session-gse-public-data-findings-paper-cs1-reply.md`）。
- 論文 1 の取り置き（CS1 2019 の 146 人・KLiCKe の 1,498 人）は確認の検定に使った。開けない小さい取り置き（CoAuthor 18 人・CS1 2021 の 13 人）は開けない。論文 2 で取り置きを使うかは条件の段で研究者に聞く。
- Mac の空きは 6.4 GiB（2026-11-07 の実測・97% 使用）。KLiCKe の全員を回す計算は、職場の PC（HP Z2）に回すかを研究者に聞く（G-GEAR は 11 月ふさがり）。中間は scratchpad か repo の外に置き、空きを見ながら。
- 論文 1 は JEDM で査読中。論文 2 で同じ結果を二重に出さない（論文 1 の停滞の形の短い節と重ならない主張にする）。
- `.codex/budget.json` は未ステージのまま。返答とファイルは日本語、記号を控える。未決は AskUserQuestion で日本語で聞く。
