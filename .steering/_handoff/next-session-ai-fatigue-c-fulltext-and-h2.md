# 引き継ぎ: C（TRACE）—— 見直しの後の全文の取り寄せ・段 2 の束・共著者の h2

作成 2026-10-24（Mac）。前提は判断 90〜97（`.steering/20261017-ai-fatigue-c-outline/decisions.md`）。**始める前に、判断 97 があること、TRACE の `screening/revisions.csv` に段 1（61 束）と段 2（11 束）の行があること、TRACE が `4f04bc3` 以降で push 済みであることを確かめる。**

- 返答・記録・AskUserQuestion の引数は日本語で書く。記号を多用しない。
- 決めてほしいことは AskUserQuestion で、推奨と理由を添えて聞く。
- 共著者に見せる文には、ルールの明示と具体的な日付・期限を書かない（判定基準の中身は書いてよい）。
- 引き継ぎの文を一次資料の代わりにしない。手順の一次資料は TRACE の `registration-day.md` の「人 2 人の形」と、道具 `~/TRACE/scripts/c_screening.py` の止まりの文。決まりの一次資料は `registration-attachments/ai-screening/instructions.md`（付録 6）§3・§4 と登録の GSRR-33・36。
- 共著者の 16 件の冊が戻ったときの手順は別の引き継ぎ `next-session-ai-fatigue-c-reasons-return.md`。この引き継ぎと並行してよい（段 1 の残り 14 束は全文の段へ進む記録を増やさない。どれも 2 人とも除外の記録）。

## 始め方

研究の物は `~/TRACE`。記録は worktree `/Users/johnd/GSE-prototype-af-c`（ブランチ `docs/ai-fatigue-c-outline`）の `.steering/20261017-ai-fatigue-c-outline/`。道具は `~/TRACE/scripts` で `uv run -q --with openpyxl python c_screening.py <命令>`。補助の脚本は `.steering/20261017-ai-fatigue-c-outline/scripts/`（`compare_stage2_db.py`・`export_stage2.sh`・`edit_coauthor_intro.py` など）。

## 1. いまの状態（2026-10-24 の終わり）

- 第一著者の見直し（判断 92〜97）: 登録の付録 6 の決まり（理由の順・E3 の意味・段 1 の狭い E2・「入力が述べていなければ不明」）を取り違えていたので、第一著者の除外をすべて見直した。段 1 は 390 件中 227 件が変わり（含めるに変えた 146）、段 2 は 44 件中 16 件が変わった（含める 6・保留 6・理由 4）。道具は `import-revision` で別ファイル（`s{1,2}/<束>.author1-revised.csv`）に記録し、元の `author1.csv` は残している。2 割の標本の一致率・網・監査の分母は元の値、それ以外（締め・段 2 の束・h2・中心）は見直し後の値で読む（判断 93・94）。
- 段 1: 63 束のうち 49 束が締め済み。残り 14 束は 2 人で決める 16 件待ち（別の引き継ぎ）。
- 全文の段へ進む記録（`sure_includes`）は 347。段 2 の束は b22 まで（198 件）で、**まだ束になっていない記録が 149 件**（見直しで新しく進む 141 件と、h1 にある端数の 8 件: CS00978・CS01146・CS02953・CS03205・CS04223・CS04602・CS06609・CS08707）。149 件のうち全文があるのは 48、無いのは 101（`chrome_status.json` で一度も試していないもの 78、前に試して paywalled 15・nourl 5・failed 3）。
- 共著者の h1（206 件）は戻っている（写し `~/Documents/TRACE/coauthor-returned/TRACE_co-author_stage2_h1.returned-20261024-1430.xlsx`・SHA-256 `cc7afabc…`・読み取り専用）が、**まだ取り込んでいない**。取り込みは、h1 の 206 件すべてで第一著者の段 2 の判定がコミット・push された後（端数の 8 件が残っている）。
- h2 の対象（どの段 2 の冊にも無い全文の段の記録）は 141 件。h2 の冊の名前と置き場所は研究者が決め済み: `TRACE_co-author_stage2_h2.xlsx` を Drive の `TRACE_Co-Author_judge-sheet` に置き、共有と連絡は研究者（判断 90）。
- DB と冊の『判定基準』には、付録 6 で欠けていた 6 行が入った（TRACE `bc4ae21`・判断 96）。h2 の冊にも自動で入る。

数え方: 上の数は道具の関数（`sure_includes`・`batches`・`make_trace_db.fulltext_file`）で数えた。⚠️ `c_screening.DEFAULTS["fulltext"]` は `~` を展開していない `Path` なので、`fulltext_file` に渡す前に `os.path.expanduser` する（展開しないと全件「全文なし」になる。2026-10-24 に一度踏んだ）。

## 2. やること（この順）

### 2.1 149 件の全文を取り寄せる

1. 全文の無い 101 件の ID を一時の場所（scratchpad）に書き出す（上の関数で数え直してから）。
2. `python3 -I fetch_fulltext.py --ids <ファイル> --data ~/Documents/TRACE/data --fulltext ~/Documents/TRACE/fulltext --search ~/Documents/TRACE/search/2026-10-18`（`meta.json` と `chrome_status.json` の控えは脚本が `backup/` に取る）。
3. 残りは OpenAlex の `open_access` を正直な UA（脚本と同じ `TRACE-review-fulltext/1.0 …`）の curl で見て、無料の版があるものだけ curl で取る。ブラウザに見せかける UA は使わない（権限で止められる）。
4. curl で断られる無料の版は、研究者の許可を得てから Chrome で 1 件ごとに新しいタブを開き、ページの中から取ってダウンロードの形で保存する（判断 88・90）。⚠️ 2026-10-24 に Wiley（onlinelibrary.wiley.com）は 3 回とも新しいタブに戻されて開けなかった（CS10084 は研究者が手で保存できる、と伝えてある）。開けないサイトは 2〜3 回で止めて研究者に渡す。Chrome を使う前に `browser-verification` Skill を読む。
5. 保存したら `%PDF` か HTML であること、題名の語の一致（`fetch_fulltext.matches`、0.6 以上）を確かめ、`~/Documents/TRACE/fulltext/<ID>.pdf` に置き、`chrome_status.json` に状態を足す（足す前に控え、足した後に控えと比べて違いが足した分だけか確かめる）。無料の版が無いものも状態（paywalled・nourl・failed）を書く。
6. Excel が閉じていることを確かめ、DB の控えを取り（SHA-256 を記録）、`uv run -q --with openpyxl python update_trace_db.py`。控えと比べ、『段1』と『段2・3』の入力の欄に違いが無いこと（違いは全文の欄・ファイルのリンク・『全文』のシートだけ）を確かめる。Drive の API で大きさが同じことを見る（作り直すと Drive の ID が変わる）。

### 2.2 段 2 の束を切り、第一著者が判定する

1. `next --stage 2` を 9 件ずつ。149 件なら 16 束と端数 5 件。最後の束は「もう来る記録が無い」ときだけ `--short`（段 1 の第一著者は全部済み、共著者の段 1 の冊も済み、残り 14 束の 16 件は 2 人とも除外なので増えない。切る前にこれを確かめる）。
2. `screening/batches.csv` をコミット・push → 束と全文の有無の一覧を研究者に渡す → 研究者が DB の『段2・3』で判定する（全文が無ければ保留＋E6）。CS03205（DB に「保留・E7」が入っていた記録）が束に入ったら、研究者に直してもらう（判断 89）。
3. Codex に判定を入れてもらうときは、Drive の DB に保存することと控えに触れないことを頼む。控えは取った直後に SHA-256 を記録し、照合の前に一致を確かめる（判断 89 の失敗）。
4. `compare_stage2_db.py` で照合（違いが束の行の判定・除外理由・中心・読んだ範囲・根拠メモだけ）→ `export_stage2.sh bNN …` → push。⚠️ 判定基準に足した決まり（段 2 の理由の順 E4・E1・E3・E2・E5・E7、Q1〜Q5 のどれかが不明なら理由なしの保留、E5 は本文自身が同じ標本と述べるときだけ）に沿っているかを、根拠メモから一度確かめる（判断 96 と同じやり方: 各問いの最初の答えだけを読む）。

### 2.3 h1 を取り込む

1. h1 の 206 件すべてで第一著者の段 2 の判定がコミット・push されたら（端数の 8 件が 2.2 で済んだら）、`import-coauthor --stage 2 --book h1 --file <h1 の写し>`。ID の列が消えていたら判断 88 と同じ方法で研究者に聞いてから直す（`restore_coauthor_ids.py`）。取り込みは段 2 の見直しのコミットを `books.csv` に `bNNr=` として記録する。
2. その後の締め（`differences --stage 2`・研究者が『最終…』を記入・`export-final --stage 2`・段 3）は、前の引き継ぎ `next-session-ai-fatigue-c-after-net1-h1-return.md` の 2.5 と同じ。⚠️ 共著者の h1 は前の判定基準（6 行を足す前）で判定されている。食い違いは 2 人で決める段で解く。⚠️ 共著者の冊の根拠メモには「（ChatGPT判定）」がある（判断 91・研究者は補助と分かっている）。

### 2.4 h2 を作る

1. 全文の取り寄せ（2.1）が済んでから。`coauthor-ids --stage 2 --book h2` → `coauthor/h2.ids` と `books.csv` をコミット・push。141 件になるはず（違えば理由を確かめる）。
2. `make_coauthor_db.py --stage 2 --book h2 --ids ../screening/coauthor/h2.ids --out <作業場所>` → `edit_coauthor_intro.py <冊> <作業場所>/TRACE_co-author_stage2_h2.xlsx`（『はじめに』の 2 行・判断 88）。判定の欄が空で、著者 1 と AI の判定が入っていないこと、『判定基準』に 6 行が入っていることを確かめる。
3. Drive の `TRACE_Co-Author_judge-sheet` に置き、API で大きさが同じことを確かめる。共有と連絡は研究者。

### 2.5 記録

- 判断 98 以降に、取り寄せの数（脚本・curl・ブラウザ・無料の版なし）、DB の作り直し（控えと SHA-256）、束（名前と件数）、h1 の取り込みのコミット、h2 の件数と SHA-256 を書く。値（どの記録を誰がどう判定したか）は書かない。
- 終わったら次の引き継ぎを書く（h2 が戻った後、段 2・3 の締め、`screening-csv`・`release` へ）。

## 3. まだ済んでいないこと

- `/cross-review`（Codex との独立レビュー・タスク完了時に必須）は、道具の改修（TRACE `c9158e4`・`f71dcb1`・`e2ebee8`・`bc4ae21`）に回していない。code-reviewer は 2 回通した（判断 94）。`/cross-review` は GSE の repo の差分を前提にしているので、TRACE の差分にどう回すか（または縮退して理由を書くか）を決める。
- 論文に書く逸脱: 第一著者が付録 6 の決まりを取り違えて判定し、見直したこと（件数・方法・元の判定を残したこと・一致率の扱い）、道具を直したこと、共著者が ChatGPT を補助に使ったこと。文案はまだ無い。

## 4. 守ること

- OSF の登録の下書きや欄を手で直さない。
- 抄録・全文・訳・AI の出力・検索の書き出し・共著者の判定の値を repo や査読者に渡すファイルに写さない（道具が書く CSV は除く）。網の答えは開かない。
- `git add -A` を使わない。PR は研究者が確かめてから。Drive の共有の設定と GitHub の公開設定は変えない。
- 状態の repo（`~/TRACE`）で rebase・squash をしない（段 2 の見直しのコミットの照合で止まる・判断 94）。
- 道具は見直しのファイルを毎回 git で照合するので遅い（`export-final` を 63 束回すと 10 分を超える）。長い繰り返しは裏で回す。
- 研究者のメールアドレスを外のサービスに渡さない。
