# 引き継ぎ: C（TRACE）—— 登録の後

作成 2026-10-21（Mac）。`next-session-ai-fatigue-c-registration-day.md` を置き換える（前の日まで・当日のメインの 1〜10 は判断 76・77 で済んだ）。

- 返答・記録・AskUserQuestion の引数は日本語で書く。記号を多用しない。
- 決めてほしいことは AskUserQuestion で、推奨と理由を添えて聞く。
- 共著者に見せる文には、ルールの明示と具体的な日付・期限を書かない。
- 引き継ぎの文を一次資料の代わりにしない。

## 始め方

研究の物は `~/TRACE`（main は `bbbaae7` 以降・push 済み）。記録は worktree `/Users/johnd/GSE-prototype-af-c`（ブランチ `docs/ai-fatigue-c-outline`）の `.steering/20261017-ai-fatigue-c-outline/`（判断は 77 まで）。手順は同じ場所の `registration-day.md`。

## 1. 済んだこと

- 2026-10-21 に OSF に登録した（https://osf.io/yckwq ・DOI 10.17605/OSF.IO/YCKWQ・判断 79）。登録版・外枠・草稿に DOI と日付を書いた（TRACE `8b235ce`）。

## 2. 次にやること

- 研究者が原田さんに「登録が済んだ」と伝える。あわせて、OSF の招待のメールからアカウントを有効にし、プロフィールに所属（Hiroshima University）を書いてもらう（任意・登録に後から出る）。
- Drive の草稿（docx と PDF）を登録済みの版に置き換えるかを研究者に聞く（判断 71・76 のやり方で、手直しが入っていないかを先に比べる）。
- `registration-day.md` の「登録の後すぐ」の「人 2 人の形」に従い、判定者 1 の段 1 を束ごとに回す。共著者の段 1 の冊（Drive の `TRACE_co-author_stage1.xlsx`・113 件）はそのまま使える（判断 76）。

## 3. 守ること

- OSF の登録の下書きや欄を手で直さない（登録は済んでいる。直しは OSF の Update の手順と逸脱の記録になる）。
- 抄録・全文・訳・AI の出力・検索の書き出しを repo や査読者に渡すファイルに写さない。確かめの検索をやり直さない。
- `git add -A` を使わない。PR は研究者が確かめてから。Drive の共有の設定と GitHub の公開設定は変えない。
- 研究者のメールアドレスを外のサービスに渡さない。
- この Mac の `python3` は 3.14。uv の 3.13 で通っても 3.14 で落ちることがある（判断 77）。
