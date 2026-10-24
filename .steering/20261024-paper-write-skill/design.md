# 設計

- paper-write は「書く手順」、attack-me は「攻撃させる手順」と分ける。paper-write の最後の段が attack-me を呼ぶ。
- 分量の目安は投稿先の規程が先。規程が無いときの目安を本文 5,000〜7,000 語・図表込みで 20 頁台前半までとする（編集者の 1 例と研究者の希望。固定の規則ではない）。
- 編集者の役 E は 4 本目の査読として並列に起動する（paper-reviewer・道具は 3 つ）。接地は投稿先の Aims & Scope と規程（Step 0 で取った一次）と、論文の構成についての無料の文献 1 本以上（候補: Mensh & Kording 2017, PLoS Comput Biol, doi:10.1371/journal.pcbi.1005619・OpenAlex で OA を確認済み）。
- E は補足資料を読まない（編集者は本文で判定する）。
- 変更対象: `.claude/skills/paper-write/SKILL.md`（新規）・`.claude/skills/attack-me/SKILL.md`・`.claude/agents/paper-reviewer.md`・`CLAUDE.md`。
- 検証: 新しい Skill なので `empirical-prompt-tuning` を回すかを研究者に確かめる（サブエージェントの費用がかかる）。
