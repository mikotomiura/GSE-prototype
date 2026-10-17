# 引き継ぎ: /literature-review の 3 票の規約を直す（Mac）

作成 2026-10-17（Mac）。返答・記録・AskUserQuestion の引数は日本語で。記号（★・⚠️）を多用しない。AskUserQuestion には推奨と理由を添える。

## 0. 新しいセッションで最初に打ち込む文

```
.steering/_handoff/next-session-literature-review-vote-rule.md を読んで、/start-task から始めて。直し方は §3 の案を研究者に確かめてから。
```

## 1. 背景

- 2026-10-17 の `/cross-review`（S-TN2・S-CO の文書の差分・`docs/tangibility-design` 枝 `c44e0d7d..6beecc86`）で、Codex が次を指摘した（`.steering/20261015-tangibility-design/` 判断 35 に記録）。
  - 「内的妥当性・外挿・頑健性は独立した検証者ではなく、同一評価者による異なる必要条件です。2 対 1 では、内的妥当性に問題があっても残り 2 軸で『確定』になり得ます。逐語の照合と結論の妥当性を分け、各軸の判定を残してください。」
- 研究者は、その差分では扱わず、規約を変える別タスクを起こすと決めた（2026-10-17・AskUserQuestion）。

## 2. いまの規約（一次）

- `.claude/commands/literature-review.md` の Step 4「敵対的検証（3 票パネル・対称フィルタ）」。票は視点を変える（例: 内的妥当性 / 外的妥当性・外挿 / 効果量の頑健性）。`3-0` = confirmed、`2-1` = confirmed（留保をカード §5 に明記）、`1-2` / `0-3` = 否決。
- 同じ「3 票」に触れる文書: `.claude/skills/literature-card/SKILL.md`・`docs/literature/_index.md`（51 枚のカードの多くが見出しに `[検証済 3-0 / 2-1]` を持つ）。最初に `grep -rn '3 票\|3-0\|2-1' .claude/ docs/literature/` で全体を数えること。
- 実際の運用（S-TN・S-TN2・S-CO）では、3 票はメインが 1 人で付けている。サブエージェントは探索だけで、票は付けていない。

## 3. 直し方の案（研究者に確かめる）

- (a) 内的妥当性の軸が落ちたら、2-1 でも「確定」にしない（PLAUSIBLE BUT UNPROVEN か否決）。軸を対等に数えない。
- (b) 軸ごとの判定（○/留保/×）を台帳の列に残す。「2-1」の合計だけを書かない。
- (c) 「逐語の照合（引用が一次に有るか）」と「結論の妥当性（その引用から言えるか）」を別の段にする。前者は機械的な照合、後者が票。
- (d) 票を本当に独立にする（軸ごとに別のサブエージェントに付けさせる）。費用がかかり、入れ子禁止と並列数の規約（`subagent-delegation` ルール 4）に触れる。
- 過去のカード（51 枚）を遡って付け直すかは別に決める。遡らないなら、規約を変えた日を `_index.md` に書き、それより前のカードの票は旧い規約によると読めるようにする。

## 4. 守ること

- 規約の文書（`.claude/commands/literature-review.md`・`.claude/skills/literature-card/SKILL.md`）を変えたら、`empirical-prompt-tuning` で検証する（CLAUDE.md の研究トラック Skill の表）。
- 過去のカードの票の書き換えは、研究者が決めるまでしない。
- `docs/references.md` の番号は触らない。
