# 引き継ぎ: C（TRACE）—— 共著者から net1・h1 が戻った後

作成 2026-10-24（Mac）。前提は 2 つ:
- 判断 88: 共著者の 2 割の取り込み・一致（両群 80% 以上）・2 回目の冊（net1・h1）を置いた。
- 引き継ぎ `next-session-ai-fatigue-c-author1-stage2-rest.md` が済んでいる: 第一著者の段 2・3 の b20〜b22（27 件）が書き出し・push 済みで、端数の 8 件が束になるのを待っている（`next --stage 2` は 8 件で止まる）。判断 89 にその記録がある。**始める前に、判断 89 があること、`screening/s2/b20〜b22.author1.csv` がコミット・push 済みであることを確かめる。** 無ければ先にそちらの引き継ぎを行う。

- 返答・記録・AskUserQuestion の引数は日本語で書く。記号を多用しない。
- 決めてほしいことは AskUserQuestion で、推奨と理由を添えて聞く。
- 共著者に見せる文には、ルールの明示と具体的な日付・期限を書かない。
- 引き継ぎの文を一次資料の代わりにしない。手順の一次資料は `registration-day.md` の「人 2 人の形」（段 1 の 5〜6、段 2・3 の 1〜8、3 回目の冊）と、道具 `~/TRACE/scripts/c_screening.py` の止まりの文。

## 始め方

研究の物は `~/TRACE`。記録は worktree `/Users/johnd/GSE-prototype-af-c`（ブランチ `docs/ai-fatigue-c-outline`）の `.steering/20261017-ai-fatigue-c-outline/`。道具は `~/TRACE/scripts` で `uv run -q --with openpyxl python c_screening.py <命令>`。補助の脚本は `.steering/20261017-ai-fatigue-c-outline/scripts/`（`restore_coauthor_ids.py`・`edit_coauthor_intro.py`・`compare_stage2_db.py`・`export_stage2.sh`）。

## 1. 渡した冊（判断 88）

| 冊 | 件数 | 置いた版の SHA-256 | 大きさ | Drive の ID |
|---|---|---|---|---|
| `TRACE_co-author_stage1_net1.xlsx`（段 1・網 83 と混ぜた記録 83） | 166 | `bbe690ec7ba38228ffb16c2f5158f6d6c32fd470554e53c183f00be8f2ccf087` | 294,325 | `1Mo4GVf1MRaqdPz4m_2L4Ll0nymisH7kc` |
| `TRACE_co-author_stage2_h1.xlsx`（段 2・3） | 206 | `e47f7fc6ed0a95df476131f6e8be5f9f17329df0184f775dfad1fe9213aa3afc` | 362,020 | `1cjHvDH9EYMBzqygPGjDUCQAULkd7nBrU` |

- 研究者は冊を xlsx の添付で共著者に送る予定だった（Drive の `TRACE_Co-Author_judge-sheet/` にも同じ版がある）。戻りはメールの添付か、Drive のどちらか。
- h1 の全文のリンクは Drive の `TRACE/fulltext`（リンクを知っている全員が閲覧可・2026-10-24 に API で確かめた）。
- 1 回目の冊は Google スプレッドシートを通った `.xlsm` で戻り、判定のシートの ID の列が消えていた（判断 88）。今回の冊の『はじめに』には「Excel の形（.xlsx）のまま戻す」と書いてあるが、同じことは起きうる。

## 2. やること（この順）

### 2.1 戻った冊を確かめる（中身は開かない）

1. 研究者に、戻った冊をどこに保存したか（添付を保存した場所か、Drive か）を聞く。添付は名前が変わることがあるので、名前ではなく中身で確かめる。
2. それぞれ、大きさ・SHA-256 が上の表の版から変わったこと（変わっていなければ未記入のまま戻った）を確かめる。Drive にあれば、API（`get_file_metadata`）の大きさ・更新時刻と同期フォルダの版が同じことも見る（降りる前に読むと置いた版に見える）。
3. 構造だけ見る: `unzip -l` でマクロ（`vbaProject.bin`）が無いこと、`xl/workbook.xml` のシート名（はじめに・段1 または 段2・3・文献DB・判定基準）と、`GoogleSheetsCustomDataVersion2` の有無（あればスプレッドシートを通っている）。判定の値は読まない。
4. `~/Documents/TRACE/coauthor-returned/` に `TRACE_co-author_<冊>.returned-<日付-時刻>.<拡張子>` の名前で写し、`chmod a-w`。写しを `--file` に渡す。

### 2.2 net1 を取り込み、段 1 を締める

1. `import-coauthor --stage 1 --book net1 --file <写し>` → `screening/coauthor/net1.csv` と `books.csv` を名指しで add・コミット・push。
2. 「the workbook's records differ from net1」で止まり、extra に `#gid=…` が並んだら、ID の列が消えている。研究者に、判断 88 と同じ方法で直してよいか AskUserQuestion で聞いてから:
   - 作り直した冊を一時の場所に作る: `make_coauthor_db.py --stage 1 --book net1 --ids ../screening/coauthor/net1.ids --out <作業場所>`（名前の照合だけに使う）
   - `uv run -q --with openpyxl python -I .steering/…/scripts/restore_coauthor_ids.py <写し> <写し>.id-restored.xlsx <作り直した冊>`。A 列以外の違いが 0 で、ID が順まで一致したときだけ書き戻した冊ができる。止まったら取り込まずに研究者に伝える。
   - 書き戻した冊で取り込む。戻った冊と書き戻した冊の両方の SHA-256 を記録に書く（`books.csv` には書き戻した冊のものが入る）。
3. 段 1 の束ごとに `export-final --stage 1 --batch bNN`（b01〜b63）。どちらかが含めれば全文段へ。2 人とも除いて除外理由が違う記録は、道具が記録を名指しして止まる。研究者に名指しの記録を伝え、2 人で決めた理由を DB の『段1』の『最終の除外理由』に書いてもらい、Drive に保存・同期を確かめてから同じ束をやり直す。束ごとに出た CSV を名指しでコミットし、最後に push。束のループは bash の脚本か Python で回す（zsh は変数を空白で分けない）。
4. 共著者が net1 で含めた記録（第一著者は除いていた記録）の数を数える。これが 0 でなければ 2.3 と 2.4 が要る。

### 2.3 端数の束を切り、第一著者が判定する

1. `next --stage 2` → 端数の 8 件と、2.2 で共著者だけが含めた記録が順に束になる。9 件たまれば切れる。
2. 最後の 9 件に満たない束は `--short` で切る。このときは「もう来る記録が無い」（第一著者の段 1 がすべて済み、共著者の段 1 の冊は 2 割と net1 で終わり・両群 80% 以上で残りは要らない）に当たる。切る前に、`screening/coauthor/books.csv` の段 1 の冊（sample・net1）がすべて取り込み済み（`imported_utc` がある）で、`sample-agreement.csv` の `rest_needed` が両群とも no であることを確かめる（`coauthor-ids` は確かめるだけの命令ではなく、走らせると冊の記録を書くので、ここでは使わない）。
3. `screening/batches.csv` をコミット・push → 束と全文の有無の一覧 → 研究者が『段2・3』で判定 → `compare_stage2_db.py` で照合 → `export_stage2.sh bNN …` → push（手順は `author1-stage2-rest` の引き継ぎの 2.1〜2.3 と同じ）。CS03205（保留・E7）がここに入っていたら、研究者に直してもらう。
4. 共著者だけが含めた記録で全文が無いものは、判断 82・83・88 と同じ手順で取り寄せる（脚本 `scripts/fetch_fulltext.py` → curl は脚本と同じ正直な UA で公開の置き場だけ → ブラウザでの保存は研究者の許可を得てから 1 件ごとに新しいタブで → `update_trace_db.py` で DB を作り直し、入力の欄に違いが無いことを確かめる）。ブラウザに見せかける UA は使わない（権限で止められる）。

### 2.4 3 回目の冊（h2）—— 共著者だけが net1 で含めた記録があるとき

1. `coauthor-ids --stage 2 --book h2` → `coauthor/h2.ids` と `books.csv` をコミット・push。全文の無い監査の記録の警告は h1 のときの 10 件と同じなら気にしない（h2 には入らないはず）。
2. `make_coauthor_db.py --stage 2 --book h2 --ids ../screening/coauthor/h2.ids --out <作業場所>`。
3. `edit_coauthor_intro.py <冊> <作業場所>/TRACE_co-author_stage2_h2.xlsx` で『はじめに』の 2 行を直す（判断 88 で研究者が決めた文。2 セルだけ変わったことを脚本が確かめる）。
4. 冊の名前・置き場所・送り方を研究者に聞いてから置く。判定の欄が空で、著者 1 と AI の判定が入っていないことを確かめる。

### 2.5 h1 を取り込み、段 2・3 を締める

1. `import-coauthor --stage 2 --book h1 --file <写し>`。206 件すべてで第一著者の段 2 の判定がコミット・push されていないと止まる（2.3 が済んでいれば通る）。ID の列が消えていたら 2.2 の 2 と同じ（作り直す冊は `--stage 2 --book h1 --ids ../screening/coauthor/h1.ids`）。h1 の ID のセルも 206 件すべて『文献DB』の同じ ID の行にリンクしている（2026-10-24 に確かめた）。
2. コミット・push。取り込みは、そのときの第一著者の束のコミットを `books.csv` に記録する。取り込んだ後に第一著者の判定を書き出し直す・手で直してコミットすると、`export-final` と `release` が止まる。
3. 段 2 の束ごとに `differences --stage 2 --batch bNN`。2 人で決める記録（判定・除外理由が違う、または 2 人とも理由のない保留）が 2 人の値と一緒に出る。これは研究者が共著者と決めるための出力で、値を steering や repo に写さない（記録には件数だけ書く）。
4. 研究者が DB の『段2・3』の『最終』『最終の除外理由』（E5 なら『同じ標本の相手（E5）』も）を記入する。合意できない記録は『最終』に「合意できない」と書き、ほかの『最終…』は空。2 人とも含めて中心だけ割れた記録は段 2 には書かない（段 3 で書く）。一方が E6 で他方が全文を読んだ保留のときは、全文があるかを確かめて決める。E5 の 2 件（S04-21→S04-28・CS05713→S04-17）は判断 86 で入れてある。
5. 照合（控えを取ってから、違いが束の『最終…』の欄だけか）→ `export-final --stage 2 --batch bNN` → コミット・push。
6. `differences --stage 3 --batch bNN` → 研究者が『最終の中心』を記入 → `export-final --stage 3 --batch bNN` → コミット・push。
7. h2 の記録がある束は、h2 が戻るまで `export-final --stage 2` が止まる。それは正しい止まりで、h2 が戻ってから `import-coauthor --stage 2 --book h2` → 同じ手順。

### 2.6 記録

- 判断 90 以降に、戻った冊の SHA-256（戻った版と、書き戻したならその版）・取り込みのコミット・段 1 の締め（束の数・最終の除外理由を決めた件数）・共著者だけが含めた記録の数・束・段 2・3 の 2 人で決めた件数（合意できない件数）を書く。値（どの記録を誰がどう判定したか）は書かない。
- 終わったら次の引き継ぎを書く（`screening-csv`・`release` へ向かう段）。

## 3. 守ること

- OSF の登録の下書きや欄を手で直さない。
- 抄録・全文・訳・AI の出力（網の答えを含む）・検索の書き出し・共著者の判定の値を repo や査読者に渡すファイルに写さない（道具が書く CSV は除く）。網の答えは開かない。共著者の冊は、取り込むまで研究者もメインも開かない（構造と ID の列だけは見てよい）。
- Codex が DB に入力したときは、Drive の DB 本体に保存されたことと同期フォルダに降りてきたことを確かめてから照合する。
- `git add -A` を使わない。PR は研究者が確かめてから。Drive の共有の設定と GitHub の公開設定は変えない。
- 研究者のメールアドレスを外のサービスに渡さない。
