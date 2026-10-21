# 引き継ぎ: C（TRACE）—— 登録の後

（2026-10-21 に `next-session-ai-fatigue-c-stage2.md` で置き換えた。）

作成 2026-10-21（Mac）。`next-session-ai-fatigue-c-registration-day.md` を置き換える（前の日まで・当日のメインの 1〜10 は判断 76・77 で済んだ）。

- 返答・記録・AskUserQuestion の引数は日本語で書く。記号を多用しない。
- 決めてほしいことは AskUserQuestion で、推奨と理由を添えて聞く。
- 共著者に見せる文には、ルールの明示と具体的な日付・期限を書かない。
- 引き継ぎの文を一次資料の代わりにしない。

## 始め方

研究の物は `~/TRACE`（main は `8b235ce` 以降・push 済み）。記録は worktree `/Users/johnd/GSE-prototype-af-c`（ブランチ `docs/ai-fatigue-c-outline`）の `.steering/20261017-ai-fatigue-c-outline/`（判断は 79 まで）。手順は同じ場所の `registration-day.md`。

## 1. 済んだこと

- 2026-10-21 に OSF に登録した（https://osf.io/yckwq ・DOI 10.17605/OSF.IO/YCKWQ・判断 79）。登録版・外枠・草稿に DOI と日付を書いた（TRACE `8b235ce`）。

## 2. 次にやること（この順・研究者が 2026-10-21 に決めた）

### 2.1 Drive の草稿を登録済みの版に置き換える

- 置き換えると決まっている（研究者）。置き換える前に、Drive の 3 つ（共著者フォルダの `TRACE_草稿_2026-10-18.docx`・`.pdf`、TRACE 直下の docx）が判断 76 で置いた版のままかを比べる（docx の作成と更新の時刻・cmp）。違えば止めて研究者に聞く。
- TRACE `8b235ce` 以降の草稿（`manuscript/draft/main.pdf`・`main.docx`。組版済み）で同じ名前で置き換え、cmp で一致を確かめる。
- 案内（`TRACE_共著者への案内_2026-10-18.docx`）に「登録の前」「登録が済んだら連絡する」の文が残っていないかを見る。直すなら判断 71・76 のやり方（Drive の docx の run の中だけ・研究者の手直しを残す）で、先に研究者に聞く。

### 2.2 判定者 1 の段 1 を始める

- 手順は `registration-day.md` の「登録の後すぐ」の「人 2 人の形」の段 1（共通の手順「段 1」の 1〜6、7 は使わない）。道具は `~/TRACE/scripts/c_screening.py`（`uv run --with openpyxl python c_screening.py <命令>`）。形は `two-human` に固めてある（`screening/mode.txt`）。
- 1 束ずつ: `next --stage 1` → `batches.csv` をコミット → `prepare --stage 1 --batch bNN` → 研究者が DB の『段1』で 9 件を判定（全文は開かない）→ `export-author --stage 1 --batch bNN` → 出た CSV を名指しで add・コミット・push → `gate` → AI の網（`prompt.txt`・`call.md`・サブエージェント 1 つ）→ `check-ai --stage 1 --batch bNN --model-id <サブエージェントの記録の model> --claude-code-version <claude --version>`（打ち間違いで止まっても `--another-model` は本当に別の模型のときだけ）→ 目録をコミット。
- 研究者の判定の DB は Drive の `TRACE/TRACE_database.xlsx`（判断 76 で作り直した・564 件・入力 0）。研究者が Excel で開いている間は作り直さない。
- 共著者の段 1 の冊（`TRACE_co-author_stage1.xlsx`・113 件）は、研究者が「登録が済んだ」と伝えれば共著者がそのまま使える。戻ってきたら `import-coauthor --stage 1 --book sample --file <戻った冊>`（取り込むまで研究者は開かない）。
- 原田さんへの連絡（登録が済んだこと・OSF のアカウントを有効にしてプロフィールに所属を書くこと）は研究者がする。

## 3. 守ること

- OSF の登録の下書きや欄を手で直さない（登録は済んでいる。直しは OSF の Update の手順と逸脱の記録になる）。
- 抄録・全文・訳・AI の出力・検索の書き出しを repo や査読者に渡すファイルに写さない。確かめの検索をやり直さない。
- `git add -A` を使わない。PR は研究者が確かめてから。Drive の共有の設定と GitHub の公開設定は変えない。
- 研究者のメールアドレスを外のサービスに渡さない。
- この Mac の `python3` は 3.14。uv の 3.13 で通っても 3.14 で落ちることがある（判断 77）。
