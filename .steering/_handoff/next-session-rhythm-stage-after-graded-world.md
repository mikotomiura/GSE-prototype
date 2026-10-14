# 引き継ぎ: 背景のステージ —— 中間の world の後（3 段とも天井で閉じた）

作成 2026-10-14（Windows・G-GEAR）。返答・記録・AskUserQuestion の引数は日本語で。記号（★・⚠️）を多用しない。AskUserQuestion には推奨と理由を添える。

## 1. ここまでの状態

- worktree `C:\wt\eh3-windows-device-rest`、ブランチ `docs/rhythm-stage-graded-world`（`424d9500` まで push 済み・PR なし）。第 2 回のブランチ `docs/rhythm-stage-round2`（判断 7 の `2ca01de5` まで push 済み）から切った。
- タスク `.steering/20261014-rhythm-stage-graded-world/` は完了した（tasklist すべて済み）。
  - 中間の world: v4（t = 0）と v2（t = 1）の間を STRUGGLE の打鍵の間隔で補間した 3 段（t = 0.25・0.5・0.75）。L1800 の専用の陽性対照（直前 1800 s）。設計と計器は `a6747868` で固定（固定の前の `/cross-review` 2 巡と直しの Codex の確かめ）。
  - 下見 0 で 3 段とも天井（L300 の AUC(A_speed) の小さいほう 0.995・0.997・0.997）。固定した規則どおり、どの段も下見 1・本番を回さず、項目 1 は 3 段とも判定不能（`ceiling`）。研究者はここで閉じると決めた（判断 6）。
  - notes: `experiments/20261014-rhythm-stage-graded-world/notes.md`（`/cross-review` 2 巡・判断 7・8）。
- 「停滞が打鍵の時刻に出るときに、ステージが A_speed の要約を超えて停滞を写すか」は未検証のまま。L1800 の専用の対照は一度も使われていない。

## 2. 未出荷（研究者の確認待ち）

- `docs/rhythm-stage-desk-check`（第 1 回）→ `docs/rhythm-stage-round2`（第 2 回）→ `docs/rhythm-stage-graded-world`（このタスク）の順に積み重なっている。どれも push 済み・PR なし。前のブランチを先にマージしないと、後のブランチの差分に前の回の分が混ざる。
- マージの順と PR を出すかは研究者が決める（計測の run の最中は PR を出さない・CI が self-hosted で測定と重なる）。

## 3. 次に考えること（研究者が決める）

- 研究者に示して採らなかった案（判断 6）: t < 0.25 や段と段の間の探索的な系列、窓の速さの要約が STRUGGLE を分けない世界の作り（セッションごとの速さのばらつきなど）。どちらも結果を見た後に決めるので探索的。
- 親タスク（判断 3・5 の見直し）への材料は、各回の notes の「親タスクへの材料」。

## 4. 守ること

- 第 1 回・第 2 回・このタスクの入れ物と判定を書き換えない。
- 合成の列だけを使う。NDJSON の生ログ（合成も）・キーストロークの内容を外部の LLM（Codex を含む）に送らない。
- `src-tauri/`・EH3 のファイルに触れない。`.codex/budget.json` を `git checkout --` で戻さない（2026-10-14 は 8 回・251,688 を記帳済み）。`git add -A` を使わない。
- バックグラウンドの実行の「completed」の通知は、終わりより早く届くことがある。結果のファイルとログを一次で確かめてから報告する（memory の reference_bash_background_absolute_paths）。
