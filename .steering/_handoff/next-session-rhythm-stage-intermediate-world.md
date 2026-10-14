# 引き継ぎ: 背景のステージ —— 中間の world の検討（第 2 回の後）

作成 2026-10-14（Windows・G-GEAR）。返答・記録・AskUserQuestion の引数は日本語で。記号（★・⚠️）を多用しない（研究者の指摘）。AskUserQuestion には推奨と理由を添える。

## 新しいセッションで最初に打ち込む文

```
.steering/_handoff/next-session-rhythm-stage-intermediate-world.md を読んで、背景のステージの中間の world の検討から始めて。
```

## 1. ここまでの状態

- worktree は `C:\wt\eh3-windows-device-rest`、ブランチ `docs/rhythm-stage-round2`（`d98103a0` まで push 済み・作業ツリーはきれい・PR なし）。
- 第 2 回（λ の選び方を直した再実行）は、下見 1・スモーク・本番・notes・notes の `/cross-review` 2 巡まで終わった。残りは tasklist の最後の 1 項目「中間の world を研究者と検討する」だけ。
- 項目 1 の判定（赤は 2 回とも 0）:

| ラベル | 第 1 回（SEED 20261009） | 第 2 回（SEED 20261013） |
|---|---|---|
| L300（主） | 緑 14・判定不能 10 | 緑 24 |
| L60 | 緑 16・判定不能 8 | 緑 20・判定不能 4（`jitter-hold`・`jitter-ground`・PC-stall が弱い） |
| L1800 | 判定不能 24 | 判定不能 24（PC1 が働かない・下限 +0.072） |

- 第 2 回の規則は第 1 回の本番を見て決めた（探索的）。2 回の判定は並べて扱い、併せた 1 つの判定は作らない（第 2 回 design §3.3 への追加 (a)〜(d)）。(c) により λ のための第 3 回は行わない。

## 2. 読む順（一次）

1. 第 1 回の `decisions.md` 判断 16（world v4 を選んだ理由・「天井の値に合わせて世界を調整しない」）と判断 21（再実行の後に中間の world を検討する・強さを段にした系列を結果の前に固定する案）: `.steering/20261012-rhythm-stage-desk-check/decisions.md`
2. 第 2 回の notes 全文: `experiments/20261013-rhythm-stage-round2/notes.md`（特に「読み方」と「親タスクへの材料」）
3. 第 1 回 design §3.0（下見 0・天井の測り・v2 と v3 の値）と §1.6（world の作り）: `.steering/20261012-rhythm-stage-desk-check/design.md`
4. 第 2 回 `design.md` §3.9（λ の選び方）・`decisions.md` 判断 1〜6・`tasklist.md`
5. 必要なら生成器 `experiments/20261013-rhythm-stage-round2/scripts/gen_sessions.py`（world v2〜v4 の作り分け）

## 3. このセッションでやること

研究者と中間の world を検討する。最初に、判断 16 とぶつかりうる点を示す（第 1 回の判断 21 の指示）。前のセッションで研究者に示した 4 点:

1. **段の強さの決め方**: 中間の world は、v4（打鍵の時刻に停滞が無い）と v2・v3（天井に当たる）の間を段で埋めるもの。段を天井の値（AUC(A_speed) ≤ 0.85）を見て決めると判断 16 に反するので、強さの系列は天井を測る前に固定する必要がある。
2. **天井に当たる段が出る**: v3 ではモデル A だけで 0.86〜0.90 に届いた（第 1 回 design §3.0）。強い段は `ceiling` で判定不能になる見込みで、それを結果として受け入れる形にする必要がある。
3. **L1800 は中間の world では動かない見込み**: 2 回とも PC1 が働かない。原因は対照の手がかりの範囲（直前 60 s・攻撃者は約 180 s）がラベルの範囲（1800 s）に合わないことと読んでいる（推論）。世界とは別の論点として扱うかを決める。
4. **段ごとの費用**: 第 2 回の規則で λ を選ぶと、段ごとに下見 1（今回 6034 s・CPU の取り合いが無ければ約 75 分の見込み・rank の 6 本が約 470 s ずつで重い）と本番（判定と記述で 16261 s）が要る。段の数が費用を決める。

ほかに決めること（推論・研究者に問う）: 段の軸（打鍵の間隔の差か、訂正の後の間か、両方か）・段の数・下見 0（天井の測り）を段ごとに回すか・入れ物（第 3 回の入れ物ではなく、新しいタスク名にするか）・seed。決まったら `/start-task` で新しいタスクを作り、design を固定の前の `/cross-review` に通す（第 1 回・第 2 回の型）。

## 4. 守ること

- 第 1 回・第 2 回の判定と入れ物（`experiments/20261012-rhythm-stage-desk-check/`・`experiments/20261013-rhythm-stage-round2/`）を書き換えない。
- 合成の列だけを使う。NDJSON の生ログ（合成も）・キーストロークの内容を外部の LLM（Codex を含む）に送らない。Codex に渡すのは design・notes・集計の要約まで（`scripts/run-codex-review.sh <range> -- <paths>` でパスを限る）。
- `src-tauri/`・EH3 のファイルに触れない。
- Codex の台帳（`.codex/budget.json`）は `git checkout --` で戻さない。2026-10-14 は 2 回まで記帳済み（`d98103a0`）。
- `git add -A` を使わない（明示したパスだけ）。worktree のセッションでは、git を含む複合コマンドは分けて叩く。
- 計器を回すときは、先に `gh run list` で CI を、`Get-CimInstance Win32_Process` で他の重い処理（同じ機械の別の実験）を確かめる。2026-10-13 の下見 1 では別の実験と重なり、1 候補あたり約 110 s が約 300 s に延びた。
- 実行の道具: `PYTHON=C:/wt/portrait-eh1-round3/experiments/20261010-portrait-eh1-round3/.venv/Scripts/python.exe`・`GSE_REPLAY=C:/wt/_target-portrait-eh1/release/gse-replay.exe`（SHA-256 `71d09dab…8d78986`）。長い実行は `run_in_background` で、出力はファイルに保存し、パスは絶対パスで書く。

## 5. 未出荷

- `docs/rhythm-stage-desk-check`（第 1 回）: push 済み・PR なし。研究者の確認待ち。
- `docs/rhythm-stage-round2`（第 2 回）: push 済み・PR なし。第 1 回のブランチから切っているので、第 1 回を先にマージしないと差分に第 1 回の分が混ざる。
