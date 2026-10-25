# 引き継ぎ: EH3 の凍結の前の準備を閉じる —— drift を決め、G-GEAR の後で PR（Mac）

作成 2026-10-26（Mac）。返答・記録・AskUserQuestion の引数は日本語で。記号（★・⚠️）を多用しない。研究者に決めてほしいことは、報告の文章に並べず AskUserQuestion で、推奨と理由を添えて聞く（F-1 のように研究者が選ぶものは推奨を付けない）。

## 0. 新しいセッションで最初に打ち込む文

```
worktree /Users/johnd/GSE-prototype-eh3-pre-freeze の .steering/_handoff/next-session-eh3-pre-freeze-close.md を読んで、§2 の残りを進めて。PR は G-GEAR の処理が終わったと研究者が言うまで出さない。
```

## 1. 今の位置

- タスク: `.steering/20261016-eh3-pre-freeze/`（worktree `/Users/johnd/GSE-prototype-eh3-pre-freeze`・ブランチ `chore/eh3-pre-freeze`・push 済み `259b349f`・PR なし）。
- 段 1（F-1 の見比べ）: 2026-10-18〜10-25 の 8 日を見比べ、研究者が文法を `lattice` に決めた（判断 9）。記録は `f1-viewing-notes.md`（日 1・4 は基準 2 つが未回答で自由記述だけ）。壁紙は元に戻し、launchd（`com.johnd.gse-f1-viewing`）は外した。画とスクリプトは `~/Pictures/gse-f1-viewing/` に残っている（repo の外・コミットしない）。
- 段 2（肖像と招待の分け方の検査）: 実装・陽性対照・code-reviewer ∥ security-checker・/cross-review まで済み（判断 5〜7）。手元で fmt・clippy・test・replay は緑。Windows の CI はまだ通していない（PR を出していないため）。

## 2. 残り（tasklist.md）

1. **F-1 の理由**: 研究者が「後で書く」とした。書いてもらったら `f1-viewing-notes.md` の「終えたあと」と判断 9 に写す。催促はしない。
2. **drift の決定**（研究者が決める・「後で決める」）。材料は判断 4: 配る物の経路では更新が約 2 割（4 時間で 10 回）しか起きず、`diffuse` は `none` との差が画素の値で最大 4/255 で目では見分けられない。選択肢は `none` のまま／`diffuse` を見える形で別に試す。どちらにも推奨を付けず、材料だけ添えて聞く。
3. **PR・CI（Windows・macOS）**: G-GEAR 側の処理が終わってから（研究者の指示 2026-10-26）。それまでは push だけ。G-GEAR で長い計算が走っている間は self-hosted CI と重なるので PR を出さない。研究者が「終わった」と言ったら、PR を出す前に一度確かめてから `gh pr create`。CI が赤なら直す（分け方の検査は CRLF でも通ることを手元で確かめてある）。
4. **/finish-task**。

## 3. 閉じた後（このタスクの外）

- 割り当ての表（参加者ごとの `order`・`a_first`）を `SEED` から作り、`eh3.mode` を `grammar=lattice;drift=<決めた値>` で書く（`docs/eh3-distribution-tag.md` §2）。`grammar` はコードに既定の無い必須のキーなので、コードの変更は要らない。drift が決まるまで作れない。
- そのあとが EH3 の配布物の固定（タグ）。固定から先の段取りは tangibility-design 側の計画（ブランチ `docs/tangibility-design`）を読み直して決める。
- 判断 4 の「更新が約 2 割しか起きない」ことを F-2（予定の値）として凍結の前に見直すかは、研究者が決める（このタスクでは変えていない）。

## 4. 守ること

- 合成の打鍵だけを使う。キーストロークの内容・NDJSON を外部の LLM（Codex を含む）に送らない。
- `git add -A` を使わない。`.codex/budget.json` は codex のスクリプトの記帳で、コミットも巻き戻しもしない。
- 並行のセッションとは worktree を分ける。コミットの前に `git branch --show-current`。
- G-GEAR の作業（相対のタイミングの机上の検査など）は G-GEAR に任せ、このタスクに混ぜない。
