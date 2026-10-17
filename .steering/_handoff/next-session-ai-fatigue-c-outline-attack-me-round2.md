# 引き継ぎ: C の外枠のプレ査読 round 2（attack-me・stage outline）

作成 2026-10-17（Mac）。返答・記録・AskUserQuestion の引数は日本語で。記号を多用しない。決めてほしいことは AskUserQuestion で、推奨と理由を添えて聞く。

## 始め方

worktree `/Users/johnd/GSE-prototype-af-c`（ブランチ `docs/ai-fatigue-c-outline`・push 済み・PR なし）で新しいセッションを開き、次を打ち込む。

```
.steering/_handoff/next-session-ai-fatigue-c-outline-attack-me-round2.md を読んで、attack-me（stage outline）round 2 で papers/ai-fatigue-measurement/manuscript/outline.md を再査読して。
```

## round 1 で決まったこと（一次は `.steering/20261017-ai-fatigue-c-manuscript/decisions.md` 判断 5・`attack-me/outline-c-manuscript/round-1/verdict.md` §7）

- 判定 major。指摘 F1〜F26 のうち、F15・F17・F26 以外を直した。題は TRACE（符号化の手順の名）。焦点は「測ったものから結論がどこまで行けるか」。
- 登録版は 0.7（題・C4f・GSRR-56 の表 3 つ・添付 5 に外枠）。合成の脚本に出力 3 つと検査を足した。
- narrative review の著者・引き方は、研究者が草稿の完成後に共著者と直接相談する（外枠の未決）。

## round 2 でやること

- 置き場: `.steering/20261017-ai-fatigue-c-manuscript/attack-me/outline-c-manuscript/round-2/`。同じ立場・同じ文献（`round-1/panel.md`。本文は round-1/tmp/sources/ にある。消えていたら panel の DOI と SHA-256 で取り直す）。
- 役ごとの引き継ぎ（carryover-R1〜R3・carryover-audit）を、round 1 の verdict の各役の指摘と §7 の対応から書く。他の役の指摘は渡さない。
- context-B を直す（F15: C4 の新しさは「再計算と整合の規則を全件に当てる」・F26: 探索の集合は 10 研究と 4 尺度）。
- 研究者に確かめていない既定 2 つを査読で見てもらう: C4f で表の値を含む／C7 を条件ごとに報告し (iii) と C6a は名前の比較と書く。
- Codex は既定では加えない（加えるなら preview を見せて研究者の OK を取る）。

## 守ること

- 結果を先取りしない。尺度の項目を逐語で公開物に載せない。GSE の話を混ぜない。
- 原稿の草稿を組む段階では、必要に応じて MacTeX を使う。.docx などオフィス系の出力は LibreOffice（`soffice`）を使う（研究者の指示・2026-10-17）。
- 出典は `citation-ssot`（次は P526）。PR は研究者が確かめてから（push で止める）。`git add -A` を使わない。
- TRACE の展開と同名の有無は、投稿の前に調べ直す。
