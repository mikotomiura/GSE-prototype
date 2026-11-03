# 判断

## 判断 1: 理想は research-positioning §1 に追記する

- 決定: §1 の 2026-10-31 改訂ブロックの直後に「2026-11-03 追記」として置く。
- 理由: 人数と主張の上限がそこに書かれており、理想はその上限の外側の話なので隣に置くと読み違えにくい。事前登録（段 1 の契約）や ADR（本文を書き換えない）には置かない。
- 却下案: 事前登録の草案に書く（段 1 の解析の契約に、段 1 の外の話が混ざる）。新しい ADR（決定ではなく目標なので合わない）。

## 判断 2: Physical Anchor の記述の範囲

- 研究者の指示: 「Physical Anchor は情報として古いので削除してください。散歩促進とその計測はすでに手配している」。
- 今回の追記には入れない（済み）。他の文書の範囲は研究者に確かめる。
- 研究者の回答（AskUserQuestion）: 共通の文書も直す。ADR と文献カードは履歴なので本文を書き換えない。語 Physical Anchor は概念の名として残す。
- 直した文書: `docs/agent-shared.md`・`CLAUDE.md`（Skill 表の Lv 表記）・`README.md`・`README.ja.md`・`docs/architecture.md`・`docs/functional-design.md`・`docs/glossary.md`・`docs/research-positioning.md`（2026-11-03 追記に注記・履歴の本文は残す）。
- 書き方: 確かめた事実（PC 側の招待は EH3 モードで実装済み・`analysis/invitation.rs`）と、研究者の言（散歩の促進とその計測は手配済み）を分けて書いた。手配の中身と記録の場所は、この repo では確かめられていないと明記した。
- 不便益の条件 1: 「Physical Anchor は未実装なので満たされない」という理由を、「散歩の促進は手配済みだが、条件 1 を満たすかは検証していない」に替えた。「不便益 HCI である」と書かない禁止は変えない。
- 残した食い違いの候補: README の「GSE は身体活動を一切センシングしない」と ADR-017 D10（歩数・距離・位置を本体から恒久的に外す）は、計測の手配が GSE 本体の外なら食い違わない。中身が分からないので触らず、研究者に伝える。

## 判断 3: /cross-review の指摘への対応

- Codex は予算のゲートで止まった（574,580 / 600,000）。Claude（code-reviewer）だけで行った。
- 採用した指摘:
  - 運用文書と Skill に残っていた現在形の「未実装」「Nudge のみ」を直した。対象は `docs/pilot-runbook.md`・`docs/verification-runbook.md`・`docs/architecture.md` の改訂注・`.claude/skills/architecture-rules/SKILL.md`。`docs/wbs-verification-halfyear.md` には注を足した。
  - research-positioning の注記に、履歴として扱う範囲を書いた（「以下の本文は履歴」より後、§1 の残りから §9 まで）。
  - 集団の平均の効果は「人数と主張の上限」を引き、ADR-042 D1 は人をまたぐ予測の行にだけ引いた。
  - 3〜5 名（全体）と 2〜4 名（段 1 の確認）の違いを書いた。
  - [V303] の人数に合わせて「数十〜二百ほど」にした。
  - README の「手配済み」に「研究者の言」を添えた。
- 採らなかった指摘:
  - README に「計測は GSE 本体の外」と書く案は採らなかった。中身を確かめていないため。ADR-017 D10 との関係は研究者に確かめる。
  - `intervention-design` Skill の「Wall なしで継続（Nudge のみ有効）」は、Wall Server の旧ルールの文脈なので触らない。
