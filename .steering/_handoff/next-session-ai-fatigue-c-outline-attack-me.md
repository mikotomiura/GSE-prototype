# 引き継ぎ: C の原稿の外枠のプレ査読（attack-me・stage outline）

作成 2026-10-17（Mac）。返答・記録・AskUserQuestion の引数は日本語で。記号を多用しない。決めてほしいことは AskUserQuestion で、推奨と理由を添えて聞く。

## 始め方

worktree `/Users/johnd/GSE-prototype-af-c`（ブランチ `docs/ai-fatigue-c-outline`・push 済み・PR なし）で新しいセッションを開き、次を打ち込む。

```
.steering/_handoff/next-session-ai-fatigue-c-outline-attack-me.md を読んで、attack-me（stage outline）で papers/ai-fatigue-measurement/manuscript/outline.md をプレ査読して。
```

タスクは `.steering/20261017-ai-fatigue-c-manuscript/` を続ける（tasklist の残り: プレ査読・コミット）。査読の記録は `.steering/20261017-ai-fatigue-c-manuscript/attack-me/outline-c-manuscript/` に置く（公開物の `papers/` に置かない）。

## ここまでで決まったこと（一次は同タスクの `decisions.md` 判断 1〜4）

- 実現性の見積もり（`feasibility.md`・脚本と出力は `scripts/`）: 264 件をすべて審査すれば含めるのは約 30〜90 件（中央で約 60 件）。候補の集合が 25 件以上になるには、中央の想定で審査の順の先頭から 120〜150 件（2 人で 85〜105 時間ほど）。この数は登録にも原稿にも書かない。
- 論文の形: C を単独の論文にする（判断 2）。narrative review は待たずに投稿でき、C はそれを引く。
- 投稿先: まだ決めない（判断 3）。外枠は APA 7 版・抄録 250 語以内を仮置き。プレ査読では規程への適合（観点 5）は「投稿先が未定」として評価から外すよう依頼文に書く。
- 外枠: `papers/ai-fatigue-measurement/manuscript/outline.md`（英語・公開物の作法・`_style_check.py` で違反 0 件）。

## プレ査読で意図の監査役に渡すもの（B の候補）

- 登録版 `.steering/20261017-ai-fatigue-c-outline/registration-en.md`（外枠より優先される）
- `.steering/20261017-ai-fatigue-c-outline/overlap-narrative-review.md`（narrative review と何が違うか）
- 同タスクの `decisions.md`（判断 2〜4）
- narrative review の草稿そのものは渡すかを研究者に確かめる（git の外・共著の未公開の原稿）。

## 見積もりで気づいた、登録の前に研究者が決めること（`feasibility.md` §4）

- レビューを狙った検索の 43 件に付ける群の名（GSRR-16 の 6 群に無い。審査の順の一覧を作るときに要る）。
- 無料の版が無い 48 件の本文を、共著者が組織の購読で入手できるか。
- 登録が遅れるほど審査の窓（登録から 12 月 31 日）が縮む。

## 守ること

- 結果を先取りしない。予想を原稿にも登録にも書かない（GSRR-13）。
- 尺度の項目を逐語で公開物に載せない。GSE の話を混ぜない。
- 出典は `citation-ssot`（P524 から）。PR は研究者が確かめてから（push で止める）。`git add -A` を使わない。
