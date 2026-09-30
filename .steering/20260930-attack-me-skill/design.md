# 設計 —— attack-me skill

## アプローチ

- 形: Skill 1 本（`.claude/skills/attack-me/SKILL.md`）。コマンド（`.claude/commands/`）は作らない（Skill 名で呼べる・`/attack-me` の入口は Skill で足りる）。
- 役: **立場の査読者 3 人**（R1 手法の核・R2 隣接分野・R3 投稿先の方法論と再現性）＋ **意図の監査役 1 人**。すべて `general-purpose`・`model: opus` を明示・1 メッセージで並列・入れ子禁止（`subagent-delegation`）。編集者の判定はメインが書く。
- 接地: 各立場に実在の論文 2〜3 本（無料で読める版だけ・OpenAlex / WebSearch）。査読者役は先にその論文から「この立場が求める基準」を逐語で抜き出してから査読する。★ 実在の個人を名乗らせない（研究者の回答）。
- 分離: 査読者役には本物の査読者が見るもの（対象物・公開物・投稿規程の一次）だけ。内部の意図（設計文書・判断）は監査役にだけ渡す。混ぜると、読者に見えない穴を査読者が埋めてしまう。
- 品質の担保: 指摘は「位置と逐語・理由（接地の引用）・解消の条件・自信」の型で出させ、メインが一次で裏取り（`verify-before-claiming`）してから採る。査読の結果は研究の証拠にしない。
- stage: `prereg`（凍結の前・固定の十分さを重く見る）／`outline`／`manuscript`／`revision`。
- 記録: `.steering/<task>/attack-me/round-<N>/`（context・panel・review-R1〜R3・audit・verdict）。公開物の範囲に置かない。
- Codex: 既定では加えない（研究者の回答）。任意の追加の手順だけを書く（本文をプロンプトに貼る・予算と機密フィルタを先に確かめる）。

## 変更対象

- 新規: `.claude/skills/attack-me/SKILL.md`
- 変更: `CLAUDE.md` の「研究トラック Skill」の表に 1 行
- 新規: `.steering/20260930-attack-me-skill/`（requirement / design / tasklist / tuning の記録）

## テスト戦略

- empirical-prompt-tuning の Lite（研究者の回答「作って軽く検証」）: Iteration 0（description と本文の整合）＋ 1 シナリオ（IME 論文の公開 README を stage `outline` の対象物に見立て、round 1 の起動の直前まで＝context・panel・依頼文 4 本を白紙の実行者に書かせる）。要件チェックリスト 7 項目（`[critical]` 2 つ: A / B の分離・立場の接地と成りすまし禁止）。不明瞭点を潰す差分を入れ、必要なら iter 2。
- 査読の本番（Opus 4 本）は回さない。最初の実戦は IME 論文の M3 の事前登録の下書き。
