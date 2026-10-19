# 引き継ぎ: C（TRACE）—— 共著者の返事が来た後・登録の下書きの書き換えから登録まで

（外枠は Version 8・判断 62 で表 14 の勧めを絞り、集計の脚本に表どうしの参照の検査を足した後の状態）

作成 2026-10-19（Mac）。前の `next-session-ai-fatigue-c-after-two-human-tools.md` の §2「共著者の返事の後」と、
`next-session-ai-fatigue-c-ready-for-consult.md` を置き換える（どちらも済んだ所まで反映した）。
- 返答・記録・AskUserQuestion の引数は日本語で書く。記号を多用しない。
- 決めてほしいことは AskUserQuestion で、推奨と理由を添えて聞く。未決を完了報告に並べない。
- 共著者に見せる文には、ルールの明示と具体的な日付・期限を書かない。
- TRACE の符号化は、引き受けてもらえれば共著者が本体の集合を全部行う（判断 45・55）。「2 割」の前提で問いを作らない。段 1 の選別の 2 割は別で、今も生きている。
- 引き継ぎの文を一次資料の代わりにしない。判断 61 で、引き継ぎの一文（反例集を誰が答えを見ずに解くか）をそのまま草稿に写して誤った。書く前に添付・脚本・登録の下書きで確かめる。

## 始め方

研究の物は `~/TRACE`（https://github.com/mikotomiura/TRACE・非公開・main は 57bf451）。検討の記録は worktree
`/Users/johnd/GSE-prototype-af-c`（ブランチ `docs/ai-fatigue-c-outline`）の `.steering/20261017-ai-fatigue-c-outline/`
（判断は `decisions.md` の 62 まで）。

```
.steering/_handoff/next-session-ai-fatigue-c-after-coauthor-reply.md を読んで、§2 から進めて。共著者の返事はこれ: <返事を貼る>
```

## 1. いまの状態（判断 60・61 の後）

- 共著者に送った物（研究者が Discord で送る。文は `coauthor-discord.md`、長い版は `coauthor-consult.md`）。Drive の `TRACE/TRACE_Co-Author/` に:
  - 草稿 `TRACE_草稿_2026-10-18.docx`・`.pdf`（TRACE の 57bf451 の tex から作った版。TRACE 直下にも同じ docx）。人 2 人の形・段 1 の除外の監査・反例集まで入っている。
  - 案内 `TRACE_共著者への案内_2026-10-18.docx`（手元の `coauthor-guide.md` から `scripts/make_guide_docx.py` で作る）。
  - 段 1 の本番の冊 `TRACE_Co-Author_judge-sheet/TRACE_co-author_stage1.xlsx`（113 件・`--hold`・判定 0 件）。
  - 符号化の見本 `TRACE_Co-Author_coding-sheet/TRACE_符号化_author2_見本.xlsx`（架空の EX001・書き出せない）。
- 本番の冊で、まだ作れないもの: 段 2・3 の冊（第一著者の段 1 と網が済み、`c_screening.py coauthor-ids --stage 2` が ID を出してから）、符号化の本番の冊（本体の集合を閉じ、較正の直しを登録してから `c_coding_book.py make --coder author2 --ids`）。
- 登録の下書きは 0.15 で、まだ前の形（第一著者と独立の AI）。草稿と案内だけが人 2 人の形に先行している（草稿の冒頭の状態の注記にそう書いてある）。
- 道具: 選別は `c_screening.py`（`mode --set two-human | ai-screener`）、共著者の選別の冊は `make_coauthor_db.py`、符号化の冊と書き出しは `c_coding_book.py`。検査は `make_dummy.py`・`check_screening.py`・`check_validation_cases.py`・`check_coding_book.py [--mutate]`（openpyxl は `uv run --with openpyxl`）。
- 研究者に残っていること（返事と並行）: 反例集のキー（`registration-attachments/validation-cases/key.csv`・`key-items.csv`）の期待するコードをすべて確かめる（`findings.md` に「not yet done」とある。登録の前まで。確かめの表は `~/Documents/TRACE/key-check/TRACE_反例集キーの確かめ.xlsx`・判断 62。違う・迷うの行が来たら key.csv・key-items.csv・findings.md を直し `check_validation_cases.py` を走らせる）／Drive の `fulltext` を共著者に閲覧のみで共有する（研究者が行う）。

## 2. 次にやること（この順）

### 2.1 返事を読んで、形を決める

返事を研究者に貼ってもらい、次のどれかを AskUserQuestion で確かめる（推奨と理由を添えて）。返事があいまいなら、共著者への聞き直しの文を作るところまでで止める。
- A. 全部引き受ける（選別の 2 人目・符号化の全部・草稿を読む）→ 人 2 人の形（`two-human`）。
- B. 一部だけ（例: 選別だけ・符号化だけ・量を減らす）→ どこを人 2 人にし、どこを今の形に戻すかを研究者と決める。符号化の「2 割」の逃げ道は判断 57 で外したので、符号化を減らすなら研究者に改めて聞く（メインが 2 割を前提にしない）。
- C. 引き受けない（草稿を読むだけ・著者にならない）→ 今の登録の形（第一著者と独立の AI・`ai-screener`）に戻す。案内に書いた「全文の段を一度だけ一緒に見直す」形を使うかも聞く。
- 名前の英語表記・所属・ORCID が来ていれば控える（GSRR-2・草稿の著者欄・`registration-day.md`）。

### 2.2 登録の下書きを書き換える（A の場合。B は該当する所だけ）

`~/TRACE/registration-en.md`（0.15 → 0.16）。書き換えの前に、草稿（`manuscript/draft/main.tex`）の選別・符号化の節と、道具の実際の動き（`c_screening.py` の `coauthor_ids`・`draw_audit`・`audit_rows`・`screening_csv`、`c_coding_book.py`）を読み、登録をそれに合わせる。

- 共著者の名前と役割: GSRR-2・表 1（役割の表）・表 2。
- 選別（判断 34・44・45・54〜59）: GSRR-33・34・36〜41。判定者は人 2 人、AI は段 1 の網だけ（判定者にしない）。段 1 は共著者が 264 件と 300 件のそれぞれから無作為の 2 割（seed 20261018・20261023、合わせて 113 件）、80% に届かなければ残りも。どちらかが回せば全文の段へ。全文と中心は 2 人とも全部、一致すればその値、食い違えば 2 人で全文を見て合意（AI の答えは使わない）。網は、第一著者が除き AI が回すべきと答えた記録と、AI の出力が 2 回とも落ちた束の除外（判断 57）。保留の記録に全文が見つかれば共著者も判定し直す（判断 55）。片方の人だけが中心を付けた記録は合意で決め、件数を報告する（判断 56）。
- 段 1 の除外の監査（判断 58・59）: GSRR-33・37・41・65。第一著者だけで除いた記録から最大 30 件（seed 20261024）を網の記録を出すときに抜き（`audit.ids` に固定）、2 人とも全文で独立に判定。合意で含めれば元の集合へ（追加候補なら本体・確かめの標本なら確かめの層）。一致は選別の一致と分けて報告。共著者が段 1 を全部見たら監査は無い。流れ図は草稿の図 1 にそろえる。
- 公開物（GSRR-41）: author2 の列・`author2-workbooks.csv`・`screening-final.csv`・`screening-audit.csv`。
- 符号化（判断 45）: GSRR-44 の 6（今は「2 割以上か全部」）を全部に。GSRR-47・48・49 の一致と調整を、共著者が本体の集合を全部 1 回符号化する形に。共著者の書き出しの名前は `<file>_author2.csv`（列の辞書と `c_coding_book.py`）。反例集は共著者が本番の前に答えを見ずに解く（`cases.md` のとおり）。
- 感度分析（GSRR-62）: 分析 5（共著者の選別の古い形）を外すか直す。外枠 `manuscript/outline.md` の分析 5 と「12 月 31 日」の箇所も合わせる（外枠の版を上げる）。
- GSRR-9 の終わりの日（2027-03-31 は間に合わない・判断 46）を、研究者と決めた現実の日に。
- GSRR-65 の限界に、草稿の限界の段落との違いが無いか見る（草稿は 0.15 の GSRR-65 から閉じた因果の語の一覧と操作の文を写した）。
- 書き換えたら、草稿の冒頭の状態の注記から「登録の下書きより先行」の断りを外し、版の番号を新しい登録の下書き・外枠に合わせる。Drive の草稿（共著者フォルダの docx と PDF、TRACE 直下の docx）を置き換える（置き換えの前に、57bf451 から作り直した版と Drive の版を比べ、研究者の手直しが無いことを確かめる。PDF は文字、docx は作成日時以外）。案内の冒頭の状態の文（草稿と登録の下書きの関係）も直し、Drive の案内を置き換える（前回の docx とバイトで同じか確かめてから）。

C の場合: 草稿・README・`assets/flow.gif`（`assets/make_flow.py`）・案内を今の登録の形（第一著者と独立の AI）に戻す。道具は `mode --set ai-screener` でそのまま使える。監査と符号化の冊は人 2 人の形の物なので、残すか外すかを研究者に聞く。

### 2.3 区切りで

- 検査を全部走らせる（上の 4 本・`make_coding_form.py` の作り直しで差分なし・草稿の組版でエラー 0）。
- /cross-review（Claude の code-reviewer と Codex を直接並べる。TRACE はジョブの一時の場所に `git clone` した写しに GSE の `scripts/secrets-filter.sh` と `scripts/run-codex-review.sh` を写し、`.codex` を GSE のものにつなぐ・判断 56・61 のやり方）。
- 判断を `decisions.md` に、タスクリストを `tasklist.md` に。TRACE は main に push、GSE はブランチに push（PR は研究者が確かめてから）。

### 2.4 登録の日へ

`registration-day.md`（前の日まで・当日〔メイン〕・当日〔研究者〕）のとおり。選別の順を作って dryrun と比べる・材料の順を振り直す・Python の版・検査を全部・`hash_attachments.py`（添付 2 に `c_coding_book.py`・`check_coding_book.py` が入っている）・冒頭を版 1.0 に・**[at registration]** を 0 件に。OSF への写しと上げるのは研究者。識別子と日付が来たら、登録版・外枠・草稿に書く。
- 登録が済んだら、共著者に段 1 を始めてよいと知らせるのは研究者（冊は `--hold` のまま使える）。

## 3. 守ること

- 登録の前に判定を始めない（第一著者・AI・共著者のどれも）。
- 抄録・全文・訳・AI の出力・検索の書き出しを repo（GSE-prototype も TRACE も）に写さない。確かめの検索をやり直さない。
- `git add -A` を使わない。PR は研究者が確かめてから（push で止める）。
- Drive の共有の設定と、GitHub の公開設定は、研究者の確認なしに変えない。Drive の文書を上書きする前に、研究者の手直しが入っていないか比べる。
- 共著者の返事の文そのもの（個人の事情など）は、研究に要る事実（役割・名前・所属・ORCID）だけを記録に残す。
