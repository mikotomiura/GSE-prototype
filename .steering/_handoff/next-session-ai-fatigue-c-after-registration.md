# 引き継ぎ: C（TRACE）—— 登録の後

作成 2026-10-21（Mac）。`next-session-ai-fatigue-c-registration-day.md` を置き換える（前の日まで・当日のメインの 1〜10 は判断 76・77 で済んだ）。

- 返答・記録・AskUserQuestion の引数は日本語で書く。記号を多用しない。
- 決めてほしいことは AskUserQuestion で、推奨と理由を添えて聞く。
- 共著者に見せる文には、ルールの明示と具体的な日付・期限を書かない。
- 引き継ぎの文を一次資料の代わりにしない。

## 始め方

研究の物は `~/TRACE`（main は `bbbaae7` 以降・push 済み）。記録は worktree `/Users/johnd/GSE-prototype-af-c`（ブランチ `docs/ai-fatigue-c-outline`）の `.steering/20261017-ai-fatigue-c-outline/`（判断は 77 まで）。手順は同じ場所の `registration-day.md`。

## 1. 研究者がすること（当日の 11・12）

- OSF Registries で GSRR の様式を選び、各項目に `~/TRACE/registration-en.md`（版 1.0）の文を写す。添付 1〜7 と `registration-attachments/sha256.txt` を上げる。
- 登録の識別子（DOI）と日付をメインに伝える。

## 2. メインがすること（識別子が来たら）

- 登録版・外枠・草稿に DOI と日付を書く。草稿 `manuscript/draft/main.tex` の 26・27 行目（「not yet registered」「registration draft 0.21」）を登録済みの版 1.0 に直し、組版と docx を作り直す。Drive の草稿を置き換えるかは研究者に聞く。
- 共著者に「登録が済んだ」と伝えるのは研究者。段 1 の冊（Drive の `TRACE_co-author_stage1.xlsx`・113 件・`--hold`）はそのまま使える（判断 76）。
- その後は `registration-day.md` の「登録の後すぐ」の「人 2 人の形」に従い、判定者 1 の段 1 を束ごとに回す。

## 3. 守ること

- 登録が済むまで判定を始めない（第一著者・AI・共著者のどれも）。
- 抄録・全文・訳・AI の出力・検索の書き出しを repo や査読者に渡すファイルに写さない。確かめの検索をやり直さない。
- `git add -A` を使わない。PR は研究者が確かめてから。Drive の共有の設定と GitHub の公開設定は変えない。
- 研究者のメールアドレスを外のサービスに渡さない。
- この Mac の `python3` は 3.14。uv の 3.13 で通っても 3.14 で落ちることがある（判断 77）。
