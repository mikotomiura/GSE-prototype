# /literature-review の 3 票の規約を直す（literature-review-vote-rule）

## 背景

- 2026-10-17 の `/cross-review`（S-TN2・S-CO の文書の差分・`docs/tangibility-design` 枝 `c44e0d7d..6beecc86`）で、Codex が次を指摘した（同枝 `.steering/20261015-tangibility-design/decisions.md` 判断 35）。逐語:
  「内的妥当性・外挿・頑健性は独立した検証者ではなく、同一評価者による異なる必要条件です。2 対 1 では、内的妥当性に問題があっても残り 2 軸で『確定』になり得ます。逐語の照合と結論の妥当性を分け、各軸の判定を残してください。」
- 研究者は、その差分では扱わず、規約を変える別タスクを起こすと決めた（同 判断 37）。引き継ぎは同枝の `.steering/_handoff/next-session-literature-review-vote-rule.md`（コミット `a6db6cdb`・main には未合流）。
- いまの規約（`.claude/commands/literature-review.md` Step 4）: 票は視点を変える（例: 内的妥当性 / 外的妥当性・外挿 / 効果量の頑健性）。`3-0` = confirmed、`2-1` = confirmed（留保を §5 に）、`1-2` / `0-3` = 否決。票とエビデンス温度の間に対応の規則が無い。
- 実際の運用では、3 票はメインが 1 人で付けている。直近の S-TN2 では confirmed の 11 件がすべて `2-1` だった（同枝 `docs/literature/20261017-tangibility-recognition-leak-followup.md` の claim 台帳）。

## ゴール

`/literature-review` の Step 4 を、研究者が 2026-10-17 に選んだ (a)(b)(d) の形に改める（`decisions.md` 判断 1〜3）。

- (a) 内的妥当性の軸が ○ でなければ、他の軸に関係なく温度の上限を PLAUSIBLE BUT UNPROVEN にする。
- (b) 軸ごとの判定（○ / 留保 / ×）を台帳の列に残す。合計の「2-1」だけを書かない。見出しも軸ごとの表記にし、「票」の語をやめる。
- (d) 軸ごとに別のサブエージェント（新しい定義済み agent・Opus・道具は Read / Grep / Glob）に判定させる。1 ラウンドにつき軸ごとに 1 本、計 3 本を並列に起動する。

## スコープ

### 含むもの
- `.claude/commands/literature-review.md` の Step 4・Step 5・Step 9・アンチパターン・冒頭の description
- 新しい agent の定義 `.claude/agents/evidence-axis-judge.md`
- `docs/loop-engineering.md` のモデル割当表に 1 行・`CLAUDE.md` のサブエージェント一覧に 1 語
- `.claude/skills/literature-card/SKILL.md` の「3 票」の言及
- `.claude/skills/subagent-delegation/SKILL.md` の、この起動に関わる箇所（ルール 4 の並列数・ルール 5 の一次の代行）
- `docs/literature/_index.md` に規約を変えた日付を書く
- 変えた規約を `empirical-prompt-tuning` で検証する

### 含まないもの
- (c) 逐語の照合を別の段にすること（研究者が採らなかった）
- 過去のカード（36 本・約 420 か所の「3 票 / 3-0 / 2-1」）の票の付け直し（研究者が遡らないと決めた）
- `docs/references.md` の番号
- `/attack-me` や `paper-reviewer` の変更

## 受け入れ条件

- [ ] `literature-review.md` の Step 4 に、軸の定義・判定の 3 値・温度の上限の対応表・独立判定の起動手順・メインの異議の扱いが書かれている
- [ ] 対応表は、内的妥当性が ○ でない claim を「確定」にできない（どの組み合わせにも行が当たる）
- [ ] `evidence-axis-judge` の `model:` と `docs/loop-engineering.md` の表が一致している
- [ ] 「票」の語が新しい規約の本文から消え、`_index.md` と規約に変更日（2026-10-17）が書かれている
- [ ] `empirical-prompt-tuning` で、新しい Step 4 を白紙の実行者に読ませ、対応表の当てはめと起動手順が一意に読めることを確かめた
- [ ] `/cross-review` を通した

## 関連ドキュメント

- `.claude/commands/literature-review.md`（規約の一次）
- `.claude/skills/subagent-delegation/SKILL.md`（ルール 1・4・5・6）
- `docs/loop-engineering.md` モデル割当ポリシー
- `.claude/agents/paper-reviewer.md`（道具を絞った判定役の先例）

## 運用メモ
- /reimagine 適用: No
- 理由: 直し方の案は引き継ぎで 4 つに絞られ、研究者が AskUserQuestion で選んだ。残る設計の細部（対応表の穴・該当しない軸の扱い）は design.md の承認で研究者に確かめる。
