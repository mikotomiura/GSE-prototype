# attack-me skill —— 論文・事前登録のプレ査読（査読者役の panel と意図の監査役）

## 背景

- 研究者は一人で論文を書いている（IME 論文〔BRM 投稿予定〕・2 本目の論文〔EMSE〕）。投稿前に、身内の厳しい読み手がいない。
- 研究者の要望（2026-09-30・逐語の要旨）: 高いモデルのサブエージェントが査読者となり、(1) 論文が情報・文脈・求めている内容と十二分に一致しているか、(2) 冗長でなく美しくまとまり、読者が持ち帰れる内容か、(3) 具体的な穴が無いか、(4) ジャーナルのルールに従えているか を、査読者の研究内容・過去の論文を具体的に見たうえで批判的な下位人格を植え付け、客観的かつ厳密にジャッジしてからプレ査読を行わせる。
- 研究者の回答（2026-09-30・AskUserQuestion）:
  - 査読者役は **立場の査読者**（実在の論文を読ませてその分野の基準を引用つきで持たせる。実在の個人を名乗らせない）。
  - このタスクは **作って軽く検証** まで（査読の本番は回さない。最初の実戦は IME 論文の M3 の事前登録の下書き）。
  - 名前は **`attack-me`**（`!` は付けない）。
  - Codex は **既定では加えない**（任意の追加として手順だけ書く）。

## ゴール

`.claude/skills/attack-me/SKILL.md` があり、別のセッションのエージェントがこれだけを読んで、対象物（事前登録・原稿の外枠・原稿）のプレ査読を回せること。

## スコープ

### 含むもの
- `.claude/skills/attack-me/SKILL.md`（手順・役の作り方・評価表・依頼文のひな形・記録の置き場・禁止事項）。
- `CLAUDE.md` の研究トラック Skill の表に 1 行。
- empirical-prompt-tuning（Iteration 0 ＋ Lite 1 シナリオ・査読者役の起動の直前までを白紙の実行者に計画させる形）。

### 含まないもの
- 査読の本番の実行（原稿はまだ無い）。
- 実在の特定の人物の模擬。
- Codex を既定の panel に入れること。
- PR（研究者の指示: 次のセッションのタスクが終わった後にまとめて出す）。

## 受け入れ条件

- [ ] SKILL.md の frontmatter の description と本文の範囲が一致する（Iteration 0）
- [ ] 白紙の実行者が SKILL.md だけで、IME 論文の設計（design.md §0）を対象物に見立てた計画（context pack の目録・panel の 3 つの立場と接地の文献の探し方・依頼文 4 本）を作れ、`[critical]` 項目がすべて ○
- [ ] 実行者の不明瞭点を潰した差分が入っている（または不明瞭点ゼロ）
- [ ] 作業記録（requirement / design / tasklist）と commit（PR は出さない）

## 関連ドキュメント

- `.claude/skills/subagent-delegation/SKILL.md`（渡し方の契約: model・範囲・禁止事項・締切・入れ子禁止）
- `.claude/skills/verify-before-claiming/SKILL.md`（指摘の裏取り）
- `.claude/skills/empirical-prompt-tuning/SKILL.md`（作った直後の検証）
- `.steering/20260927-ime-observation-paper-eval-design/design.md` §0・§4・§5（IME 論文の主張・BRM の規程）

## 運用メモ
- /reimagine 適用: No
- 理由: Skill の文書であり、アーキテクチャや公開 API の判断を伴わない（研究者の回答で設計の分かれ目は閉じた）。
