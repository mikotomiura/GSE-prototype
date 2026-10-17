# 引き継ぎ: 背景のステージの机上の検査 —— 6 回のまとめ

作成 2026-10-17（Windows・G-GEAR）。返答・記録・AskUserQuestion の引数は日本語で書く。記号（★・⚠️）は多用しない。AskUserQuestion には推奨と理由を添える。

研究者は 2026-10-17 に、倍率の world を作り直さず、ここで区切って 6 回をまとめることを選んだ（`next-session-rhythm-stage-after-shape-world.md` §3 の候補 2）。理由（Claude の勧め・研究者が了承）:

- 倍率の world は、作りからして `A_speed` が強い（f100 は天井、f200 の hgb は 0.979）。格子を延ばしても天井は直らない。
- 作り直して増えるのは「倍率だけでも赤が出るか」の 1 つの seed の記述だけで、残っている読み 1・読み 2 の別に届かない。
- 1 段 約 15 時間・設計を含めて 2〜3 日かかる。

## 0. 最初にやること

1. 出荷の状態を一次で確かめる（`next-session-rhythm-stage-after-shape-world.md` §0）。
   - `Get-CimInstance Win32_Process` と `gh run list`。`a4_keytar.py` が走っていれば PR は出さない。
   - 終わっていれば、`docs/rhythm-stage-speed-confound` の PR → merge → `docs/rhythm-stage-speed-shape` を rebase して PR → merge。まとめは、2 本が main に入った後の main から切るのが素直（まだなら `docs/rhythm-stage-speed-shape` の上に積む・研究者に聞く）。
2. `/start-task` を起動し、grill でまとめの形を確定する（§2）。`/reimagine` を使うかも grill の中で聞く。

## 1. まとめる対象（一次資料）

| 回 | 記録 | 入れ物（notes・results） |
|---|---|---|
| 第 1 回 | `.steering/20261012-rhythm-stage-desk-check/` | `experiments/20261012-rhythm-stage-desk-check/` |
| 第 2 回 | `.steering/20261013-rhythm-stage-round2/` | `experiments/20261013-rhythm-stage-round2/` |
| 中間の world | `.steering/20261014-rhythm-stage-graded-world/` | `experiments/20261014-rhythm-stage-graded-world/` |
| 揺れの world | `.steering/20261014-rhythm-stage-speed-confound-world/` | `experiments/20261014-rhythm-stage-speed-confound-world/` |
| 原因の切り分け | `.steering/20261015-rhythm-stage-speed-cause-split/` | `experiments/20261015-rhythm-stage-speed-cause-split/` |
| 揺れの形 | `.steering/20261015-rhythm-stage-speed-shape-world/` | `experiments/20261015-rhythm-stage-speed-shape-world/` |

- 出発点: 背景のステージ（描画のリズム）の案の記録 `.steering/20261012-portrait-rhythm-motion/` と、ブランチ `origin/docs/handoff-rhythm-stage-novelty` の引き継ぎ。まとめは、もともと何を確かめたかったか（描画が停滞の手がかりを運ぶか・運び直すだけか）から書き起こす。
- 第 1 回〜中間の world は main に入っている（#367 まで）。揺れの world 以降は §0 の 2 本のブランチにある。
- 各回の design の「固定する節」と notes の「読み」「逸脱」を、1 節だけでなく全文で読む（memory: 長い一次資料を 1 節で代表させない）。

## 2. grill で決めること（案）

- 誰に・何のために書くか（研究者の判断の材料か、論文の一部か、docs/ の文書か）。置き場所（`docs/` か `.steering/` か `experiments/` の索引か）。
- 中身の骨（案）:
  - 問いと、6 回の world・段・結果（天井・赤・判定不能）を 1 つの表に。
  - 分かったこと: `res=sub` の赤、`R2`（`r_absdiff`・`r_sd`）に上乗せが集まる型、漂いだけでも同じ型の赤が出ること。
  - 分からないこと: 読み 1（`A_speed` に無い停滞の手がかりを運ぶ）と読み 2（`A_speed` の中の手がかりを運び直すだけ）の別。倍率の成分の効き。
  - 計器の限り: 天井、PC-stall が帯に届かない条件、1 つの seed・列が world の間で対にならないこと、所要（rank の遅さ）。
  - 次に問うなら、読み 1・2 をどう分けるか（案を並べるだけ・採るかは研究者）。
- 判定を作り直さない。各回の判定と読みを写し、言い方は各回の固定した読み方の範囲に留める。

## 3. 守ること

- 6 回の入れ物・判定・notes・design を書き換えない（まとめは新しいファイルに書く）。
- 合成の列だけを使う。NDJSON の生ログ（合成のものも）とキーストロークの内容を、外部の LLM（Codex を含む）に送らない。
- `src-tauri/` と EH3 のファイルに触れない。
- `.codex/budget.json` を `git checkout --` で戻さない。回す前に、worktree の台帳と origin/main の台帳を見る。
- `git add -A` を使わない。
- 「GSE が示した」と書かない。合成の world の結果を、人の打鍵や描画の効果の主張にしない。揺れの形は Claude が選んだ一例。
- 理論・手法・先行研究に依拠する記述を書くなら `citation-ssot` に従う。
- 完了時は `/cross-review` 2 巡（1 巡目: 自文書と 6 回の記録との矛盾、2 巡目: 足した言い方の境目）。数は一次の JSON と notes から写す。
