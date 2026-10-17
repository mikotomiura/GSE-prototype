# 引き継ぎ: 背景のステージの次の段を決める（試作・机上でもう一段・保留）

作成 2026-10-17（Windows・G-GEAR）。返答・記録・AskUserQuestion の引数は日本語で書く。記号（★・⚠️）は多用しない。AskUserQuestion には推奨と理由を添える。

研究者が 2026-10-17 に、次のセッションの主題としてこれを選んだ（候補は、公開データでの照合の論文・相対のタイミングの机上の検査・Mac の作業の続き）。決めるだけのセッションで、実装や計算はしない。

## 0. 新しいセッションで最初に打ち込む文

```
.steering/_handoff/next-session-rhythm-stage-next-step.md を読んで、背景のステージの次の段を決める議論をして。
```

このメモはブランチ `docs/rhythm-stage-summary`（worktree `C:\wt\rhythm-stage-speed-confound`）にある。main にはまだ無い。

## 1. 材料（一次）

- まとめ: `.steering/20261017-rhythm-stage-summary/summary.md`。とくに §7（親タスクの判断 3・4・5 への材料）と §8（次の案・Claude の見立て）。各回の一次は同 §9 の表。
- 出発点: `.steering/20261012-portrait-rhythm-motion/decisions.md` 判断 1（EH3 の後に回す）・判断 3（ステージは壁紙とは別の面の候補）・判断 4（最初の段は机上の検査・試作は作らない）・判断 5（背景での招待も候補に残す）。
- `.idea/20261005-motivation-fatigue-reentry-surface.md` §12（§12.5 に机上の検査の要約を 2026-10-17 に足した）と §13（打鍵からの手応え）。`.idea` は main のチェックアウト `C:\GSE-prototype` にだけある（git の外）。

## 2. 重なりを先に確かめるもの（Mac で進んだ作業・一次で読む）

背景の層の試作は、Mac で「手跡」の案として既に一部進んでいる。ステージの「試作へ進む」を選ぶ前に、重なりと違いを一次で確かめる。どれも push 済みで、`git show origin/<ブランチ>:<パス>` で読める（G-GEAR では `MSYS_NO_PATHCONV=1` を付ける）。

- `origin/spike/handmark-stage`: `.steering/20261016-handmark-stage-spike/`（背景の層の試作・判断 1〜5）と `.steering/_handoff/next-session-handmark-stage-followups.md`（残りの計測）。
- `origin/docs/tangibility-design`: `.steering/20261015-tangibility-design/`（判断 1〜37）と `.steering/_handoff/README.md`（いま有効なメモの索引）。案 D の机上の検査 `next-session-tangibility-relative-timing-desk-check.md`、「なぜ面白いか」の議論 `next-session-handmark-why-interesting.md`。
- 確かめたいこと: 手跡の背景の層は、ステージ（打鍵のリズムで滑らかに動く背景）と同じ面か。入力は何か（`res=sec` の作りか、打鍵 1 つずつの時刻か）。机上の検査の材料（`res=sub` は停滞の手がかりを残しうる・訂正を写すと停滞が写る）が当たるか。

## 3. 決めること（案・研究者が選ぶ）

1. 次の段: 試作へ進む／机上でもう一段（summary §8.1 のどれか・倍率の world）／保留。手跡の試作と合わせるか分けるか。
2. 試作へ進むなら、描画の入力をどこまでに限るか（`res=sec` の作りと訂正を読まない、が机上の材料。秒未満の時刻を使うかは `data-privacy` と合わせて決める・親タスクの判断 3）。速さを本人に返すこと（ADR-025・`PS-Q8`）をどう扱うか。
3. 時期: 親タスクの判断 1 は「EH3 の後」。EH3 の凍結の前の準備（Mac・`next-session-eh3-pre-freeze-f1-and-separation.md`）との順。
4. 決めたことの記録先（新しいタスクの `.steering/` か、`.steering/20261017-rhythm-stage-summary/decisions.md` に判断を足すか）と、`.idea` §12 への追記を Claude が行うか。

## 4. 出荷の状態（このセッションの終わり・2026-10-17 21 時ごろ）

- G-GEAR で公開データでの照合の A4 の生成（`a4_keytar.py`・python 2 本）が走っている。見張りのログ（`C:\GSE-wt-matching-prereg\experiments\20261012-public-keystroke-matching\raw\a4_watch\a4_watch.log`）では 500 本のうち 314 本、終わりは 10-20 の朝〜昼の見込み。走っている間は PR を出さない（memory: 計測の run 中は PR を出さない）。
- 背景のステージの 3 本は push 済み・PR なし。A4 が終わったら `docs/rhythm-stage-speed-confound` → `docs/rhythm-stage-speed-shape` → `docs/rhythm-stage-summary` の順に、前のものが main に入るたびに rebase して出す（`.codex/budget.json` の衝突は起点からの差分の和で解く）。
- Mac の作業のブランチ（PR なし・2026-10-17 に origin で中身が読めることを確かめた）: `docs/ai-fatigue-c-outline`・`docs/tangibility-design`・`spike/handmark-stage`・`spike/handmark-a-surface`・`docs/literature-review-vote-rule`・`chore/eh3-pre-freeze`・`docs/ai-fatigue-core1-item-analysis`・`docs/ai-fatigue-core2-discriminant`・`docs/ai-fatigue-motivation-claims`・`docs/handoff-tangibility-ai-fatigue`。研究者はこれらの PR も A4 が終わってから出す考え。

## 5. 守ること

- 6 回の入れ物・判定・notes・design と、まとめ（summary.md）の判定の写しを書き換えない。
- 「GSE が示した」と書かない。合成の world の結果を、人の打鍵や描画の効果の主張にしない。
- 決めるだけのセッションでは `src-tauri/`・EH3 のファイルに触れない。
- Mac のブランチを G-GEAR で書き換えない（読むだけ）。
- `git add -A`・`git add <dir>` を使わない。`.codex/budget.json` を `git checkout --` で戻さない。
- 長い一次資料を 1 節で代表させない（memory）。

## 6. タンジビリティの机上の検査の時期（研究者・2026-10-17）

- タンジビリティ関連の機械検査（主に案 D「相対のタイミングの写像は停滞と速さを写すか」・`origin/docs/tangibility-design` の `next-session-tangibility-relative-timing-desk-check.md`）は、公開データでの照合の論文の重い処理（A4 の GPU の生成と CPU の本計算）が終わってから、価値があれば G-GEAR で行う。CPU を本計算と取り合わないため（机上の検査は 1 段 約 15 時間・照合の論文の締切 11-30 が先）。
- 価値の見立て（Claude・決定ではない）: 背景のステージの検査で、打鍵 1 つずつの時刻から作ったテンポの秒ごとの揺れ（`r_absdiff`・`r_sd`）に停滞の手がかりが残った（summary.md §4）。相対のタイミングはこの種の量なので、案 D の前提（全体の速さを割り引けば状態を写さない）は検査する価値がある。問いは A_speed を基準にすると天井に当たるので、その引き継ぎの §3 の 1 のとおり立て直す。始めるときの引き継ぎは `next-session-tangibility-relative-timing-desk-check-ggear.md`（このブランチ）。
- このセッションで背景のステージの次の段を決めるとき、案 D の検査と計器や問いを共有できるか（同じ world・同じ攻撃者で両方を測るか）も併せて考える。
