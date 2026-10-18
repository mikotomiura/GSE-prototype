# 登録の当日の手順（C・TRACE）

作成 2026-10-18（2026-10-19 に TRACE リポジトリへの移動に合わせて直した・判断 53）。上から順に行う。
脚本・登録版・添付・外枠・草稿は `~/TRACE`（https://github.com/mikotomiura/TRACE・非公開）にある。下の `cd scripts` は `cd ~/TRACE/scripts`、`registration-attachments/` は `~/TRACE/registration-attachments/` と読む。コミットと push はすべて `~/TRACE` で行う。「研究者」と書いた手順は研究者が行い、それ以外はメインが行う。

## 前の日まで

1. 研究者: 共著者に相談文（`coauthor-consult.md`・docx）を送り、次の 2 つを受け取る。
   - 登録に載せる名前（英語）・所属・ORCID
   - 選別の 2 人目（段 1 の 2 割と全文・中心の段）と、本体の集合の符号化を全部引き受けられるか（判断 34・45。引き受けられなければ登録の下書きの戻す規則に従う）。
2. OSF の全文 3 件（R02・R22・R35）は 2026-10-18 に取り直した（OSF の登録の書式を API から組み立てた・判断 36）。済み。
   - 全文や抄録を足したら、`uv run --with openpyxl python update_trace_db.py` を 1 回打つ。Drive の `AI-fatigue/TRACE/fulltext` への写し・同期待ち・Drive のリンクの表・2 冊の DB（判定者 1 用は記入を引き継ぐ）までを行う（判断 36）。抄録を差し替えたら、先に `ja.json` の訳を足す。
   - 判定者 1 の DB を Excel で開いたまま作り直さない（閉じてから打つ）。
3. 研究者: OpenAlex の無料の API キーを申請し（2026-10-18 に済み）（https://help.openalex.org/api/authentication/）、届いたキーを `~/.config/openalex/api_key` に 1 行で置く（`chmod 600`）。メインはキーの値を見ない。
4. 確かめの検索を 1 回だけ走らせる（判断 38）。**2026-10-18 に済み**（判断 40。書き出しは `~/Documents/TRACE/search/2026-10-18/`、書誌と数は `registration-attachments/coverage/`）。やり直さない（やり直すと標本が変わる）。3 つの情報源を同じ日に。書き出しは repo の外（抄録が入る）。
   ```
   cd scripts
   OUT=~/Documents/TRACE/search/$(date +%Y-%m-%d)
   python3 -I c_search.py selftest
   python3 -I c_search.py openalex  $OUT     # 研究者のキー（~/.config/openalex/api_key）を使う。無ければキーなしで走り、枠切れは HTTP 429
   python3 -I c_search.py europepmc $OUT
   python3 -I -u c_search.py acm-receive $OUT   # 待ち受けたまま、ブラウザで次をする（-u で合言葉がすぐ出る）
   ```
   - ACM: 自分で開いたタブで `https://dl.acm.org/` を開き、サイトの確かめが自然に通るのを待つ（押さない）。`acm_export.js` の中身を貼り、待ち受けが出した `await acmExport(QUERY, 8765, "<その回だけの合言葉>")` を、QUERY に式を入れて走らせる。待ち受けは、決めた式・件数が合う・ACM のページからの 1 回だけを保存して止まる。
   - 抽出: `python3 -I c_search.py merge $OUT --records264 ~/Documents/TRACE/data/records264.json --source-db <元の DB の最終版.xlsx>`
   - `$OUT/new-records.csv` と `$OUT/search-log.json` を `registration-attachments/coverage/` に写す（書誌と数だけ。抄録の入った `new_records.json` と書き出しは写さない）。
   - 添付 3 の第 16 節・GSRR-7・10・21・32 の **[at registration]** に、日時・件数・ファイルの SHA-256 を書く。
5. 確かめの標本 300 件を選別の材料に足す（判断 38）。**2026-10-18 に済み**（判断 41）。
   - 抄録の日本語の機械訳を足す（`ja.json` に CS の ID で）。
   - `make_screening_candidates.py` が確かめの標本を群 `coverage_sample` として出し、TRACE の DB と `c_screening.py` が CS の記録を読む（`records-coverage.json`・`make_coverage_records.py`）。

## 当日（メイン）

1. 登録版の GSRR-2 に、共著者の名前・所属・ORCID を書く。
2. 選別の順を作る。dryrun（2026-10-18・確かめの標本を入れた 564 件）との diff が空であることを確かめ、材料の order を振り直す（2026-10-18 に dryrun の順で振ってある）。TRACE の DB の行の順はこの順。
   ```
   cd scripts
   python3 make_screening_candidates.py <判定者 1 の表.xlsx（AI_fatigue_additional_candidates_judge1.xlsx）> ../registration-attachments/coverage/new-records.csv > /tmp/candidates.csv
   python3 c_synthesis.py --screening-order /tmp/candidates.csv > ../registration-attachments/screening-order.csv
   diff ../registration-attachments/screening-order.csv ../registration-attachments/dryrun/screening-order-2026-10-18.csv
   python3 make_coverage_records.py order --data ~/Documents/TRACE/data --order ../registration-attachments/screening-order.csv
   ```
3. 使った Python の版を GSRR-33 に書く（`python3 --version`）。
4. 確かめる。
   - `python3 make_coding_form.py ../registration-attachments/coding-form` でコード用紙を作り直し、git diff が空であること。
   - `python3 make_dummy.py` が緑であること。
   - `python3 -I c_search.py selftest` と `python3 -I make_coverage_records.py selftest` が緑であること（確かめの検索・判断 40〜42）。
   - `uv run --with openpyxl python check_screening.py` が緑であること（選別の道具・判断 33）。
   - TRACE の DB を作り直したら、『段1』に全文の列が無く、『段2・3』があること（`make_trace_db.py`）。判定が 1 件も入っていない今の DB を上書きしてよい。
5. 添付 3（検索式・`query-strings.md`。第 16 節は確かめの検索）と GSRR-25 の **[at registration]** の中身を確かめる。選別の順の一覧に確かめの標本（群 `coverage_sample`・300 件）が入っていること。dryrun は 2026-10-18 の版（564 件）と比べる。
6. `python3 hash_attachments.py` で `sha256.txt` を作り、次の箇所に SHA-256 を書く。
   - 添付 2・3（確かめの検索の道具 2 本・新しい記録の一覧・検索の記録）・4・5・6（6 には選別の道具 3 本が入る）
   - GSRR-33（選別の順の一覧）
   - GSRR-64（脚本）
7. 冒頭を書き換える。
   - 「Registration draft 0.14 … Not yet registered」（その時の版）を版 1.0 と登録の日付にする。
   - 残った **[at registration]** を grep し、0 件にする。
8. 確かめる。
   - 体裁の検査（`_style_check.py`）。残るのは、意図して置いている日本語の語の一覧の 3 件だけ。
   - 草稿の組版（`latexmk`）。
9. 選別の形を決める（判断 55）。共著者が選別の 2 人目を引き受けたなら `c_screening.py mode --set two-human`、引き受けなければ `mode --set ai-screener`。形は最初の束を切る前に 1 回だけ決まり、後から変えられない。`screening/mode.txt` をコミットする。
10. 登録版・添付・`sha256.txt` を `~/TRACE` でコミットし、push する。

## 当日（研究者）

11. OSF Registries で GSRR の様式を選び、各項目に登録版の文を写す。添付 1〜6 と `sha256.txt` を上げる。
12. 登録の識別子（DOI）と日付をメインに伝える。メインはそれを登録版・外枠・草稿に書き、コミットする。

## 登録の後すぐ（選別・束ごとに繰り返す。判断 33）

順番（判断 34・54）: 登録したらすぐ、判定者 1 の選別を束ごとに回す。共著者は後を追う。登録の前には誰も判定しない（見本の `--preview` と、始める日を待つ旨の `--hold` の冊だけ配ってよい）。下の「段 1」「段 2・3」の手順は、今の登録の形（第一著者と AI・`ai-screener`）のもの。共著者が引き受けた形（`two-human`）では、その後の「人 2 人の形」の節に従う。

道具は `~/TRACE/scripts/c_screening.py`（`uv run --with openpyxl python c_screening.py <命令>`）。判定は `~/TRACE/screening/` に書き出され、`~/TRACE` でコミット・push する。repo に置くのは ID・判定・SHA-256・時刻だけで（`screening/`）、抄録・全文・AI の出力の JSON は `~/TRACE-screening/s<段>-<束>/` に置く。

段 1（題名・抄録）:
1. `next --stage 1` で束を切る（9 件・固定の順）。`batches.csv` をコミットする。
2. `prepare --stage 1 --batch bNN` で AI の作業ディレクトリを作る。
3. 研究者: DB の『段1』で束の 9 件を判定する（全文のシート・フォルダは開かない）。
4. `export-author --stage 1 --batch bNN` → 出た CSV を `git add`（ファイルを名指し）・コミット・push。
5. `gate --stage 1 --batch bNN` が ready を出したら、AI を走らせる（`prompt.txt` の文・`call.md` の設定・サブエージェント 1 つ）。
6. `check-ai --stage 1 --batch bNN`。書式が通らなければ同じ文で 1 回だけ取り直す。2 回とも駄目なら、その束は著者 1 だけで決まる。目録（`.ai.csv`）をコミットする。
7. `differences --stage 1 --batch bNN` → 研究者: `differences-1.md` を読み、示された記録の『最終』『最終の除外理由』を記入する。
8. `export-final --stage 1 --batch bNN` → コミット・push。研究者はこの後、その束の全文を開いてよい。

段 2・3（全文と中心を同じ束で）:
1. `next --stage 2`（段 1 を通った記録が順に 9 件たまったら切れる。12 月 31 日の締めにだけ `--short`）。
2. `prepare --stage 2 --batch bNN`。
3. 研究者: 『段2・3』で判定し、含める記録には中心も付ける。E5 は除外理由に E5。
4. `export-author --stage 2 --batch bNN` → コミット・push → `gate` → AI → `check-ai` → 目録をコミット。
5. `differences --stage 2 --batch bNN` → 研究者: `differences-2.md`（AI の中心と note は出ない）を読み、『最終』を記入する。最後に含めることになった記録で自分が含めていなかったものには『中心』も付ける。E5 で除くなら『同じ標本の相手（E5）』を書く。
6. `export-final --stage 2 --batch bNN` → 出た CSV（後付けの中心の `author1-late.csv` があればそれも）をコミット・push。push するまで次の段 3 の一覧は出ない。
7. `differences --stage 3 --batch bNN` → 研究者: `differences-3.md` を読み、示された記録の『最終の中心』を記入する。
8. `export-final --stage 3 --batch bNN` → コミット・push。

保留の記録に後で全文が見つかったら: 全文を fulltext フォルダに置き、`next --stage 2 --revisit ID,ID`（9 件まで・保留のものだけ）で新しい束を切る。研究者はその記録の『最終…』の欄を空にしてから、段 2・3 の 2〜8 と同じ手順で判定する。前の回の判定も残り、公開物には両方が出る。

### 人 2 人の形（`two-human`・判断 54・55）

判定するのは第一著者と共著者の 2 人。AI は段 1 で、第一著者が除いた記録を拾い直して共著者に回す網としてだけ使う（AI の答えは最終を決める材料にしない。`differences --stage 1` は止まり、AI の引用や理由は出ない。ただし最終の CSV の ai 列と、網を待つ記録の止まりの文で、AI が回すべきと答えたかは研究者にも分かる）。段 2・3 では AI を走らせない（`prepare`・`gate`・`check-ai` は止まる）。共著者の冊は `make_coauthor_db.py` で作り、Drive の `TRACE/Co-Author/` に置く。冊には第一著者と AI の判定が入らない。共著者が返した冊は、`import-coauthor` で取り込むまで研究者は開かない。

共著者への受け渡し（判断 44・55）:
- 1 回目（登録の直後）: 段 1 の 2 割の冊。追加候補 264 件から 53 件（seed 20261018）と、確かめの標本 300 件から 60 件（seed 20261023）、合わせて 113 件。`make_coauthor_db.py --stage 1 --out <置き場所>`。⚠️ Drive の今の段 1 の冊は 264 件からの 53 件だけ。作り直して置き換えるのは研究者に確かめてから。
- 2 回目（第一著者の段 1 が 564 件すべて済み、2 割の冊が戻った後）: 段 2・3 の冊（全文段に回った記録の全部）と、段 1 の追加の冊（網の記録。2 割の一致が 80% に届かなかったときは段 1 の残りの全部）を同時に渡す。
- 3 回目（要るときだけ）: 追加の段 1 の冊で共著者だけが回した記録の段 2・3 の冊と、保留の記録に全文が見つかったときの判定し直しの冊。どちらも `coauthor-ids --stage 2 --book h2`（名前は新しく）が、全文段に回った記録のうちその回の共著者の判定がまだ無いものを出す。冊を作り、戻ったら `import-coauthor --stage 2 --book h2`。`coauthor-ids --stage 2` が「no record」で止まれば、渡す物は残っていない。

段 1:
1. 段 1 の束は上の「段 1」の 1〜6 と同じ（`next`・`prepare`・研究者が判定・`export-author` → コミット・push → `gate` → AI → `check-ai` → 目録をコミット）。7 の `differences --stage 1` は使わない（止まる）。
2. 共著者の 2 割の冊が戻ったら: `import-coauthor --stage 1 --book sample --file <戻った冊>` → `coauthor/` をコミット・push。第一著者の判定が 2 割の記録すべてでコミット・push されていないと止まる。
3. `coauthor-agreement` で 2 割の一致を出す（含める・除外の一致の割合。除外理由は数えない）。`coauthor/sample-agreement.csv` をコミットする。80% 以上なら残りは要らない。
4. 第一著者の段 1 がすべて済んだら: `coauthor-ids --stage 1 --book net1` → 出た `coauthor/net1.ids` をコミット → `make_coauthor_db.py --stage 1 --book net1 --ids ../screening/coauthor/net1.ids --out <置き場所>`。80% に届かなかったときは、同じ命令が網ではなく段 1 の残りの全部を出す。
5. 追加の冊が戻ったら `import-coauthor --stage 1 --book net1 --file <戻った冊>` → コミット・push。
6. `export-final --stage 1 --batch bNN`（束ごと）。どちらかの人が含めれば全文段へ。2 人とも除いて除外理由が違う記録は、2 人で決めた理由を研究者が『最終の除外理由』に書く（命令が記録を名指しして止まる）。共著者の判定を待つ記録があると止まる。コミット・push。

段 2・3:
1. `next --stage 2`。第一著者か共著者が段 1 で含めた記録が順に 9 件たまれば切れる（段 1 の最終を待たない）。来る記録がもう無いとき、または 12 月 31 日の締めにだけ `--short`。
2. 研究者: 『段2・3』で判定し、含める記録には中心も付ける → `export-author --stage 2 --batch bNN` → コミット・push。
3. 共著者の段 2・3 の冊: `coauthor-ids --stage 2 --book h1` → `coauthor/h1.ids` をコミット → `make_coauthor_db.py --stage 2 --book h1 --ids ../screening/coauthor/h1.ids --out <置き場所>`。確かめの標本の記録も入る（判断 54）。
4. 冊が戻ったら `import-coauthor --stage 2 --book h1 --file <戻った冊>` → コミット・push。冊のすべての記録で第一著者の段 2 の判定がコミット・push されていないと止まる。取り込みは、そのときの第一著者の束のコミットを `coauthor/books.csv` に記録する。取り込んだ後に第一著者の判定を書き出し直す・手で直してコミットすると、`export-final` と `release` が止まる（段 1 も同じ）。
5. `differences --stage 2 --batch bNN` が、2 人で決める記録（判定・除外理由が違う、または 2 人とも理由のない保留）を 2 人の値と一緒に出す。2 人で全文を見て決め、研究者が『最終』を記入する（AI の答えは使わない）。E5 で除くなら『同じ標本の相手（E5）』も書く。
6. `export-final --stage 2 --batch bNN` → コミット・push。
7. `differences --stage 3 --batch bNN` → 2 人の中心が違う・どちらかが境界・どちらかが中心を付けていない（含めなかった）記録を、2 人で決めて『最終の中心』に書く。
8. `export-final --stage 3 --batch bNN` → コミット・push。

保留の記録に後で全文が見つかったら（判断 55）: `next --stage 2 --revisit ID` で束を切り、研究者は『最終…』の欄を空にしてから判定し、`export-author` → コミット・push。続けて `coauthor-ids --stage 2 --book h2` が、その回の共著者の判定がまだ無い記録を出すので、冊を作って共著者に渡す。前の回の共著者の判定は数えない（新しい冊が戻るまで `export-final` は止まる）。

選別の後（人 2 人の形）: `screening-csv` が 4 本を書く。`screening-final.csv`（全記録の最終の値・1 人で決まった記録も入る）は、確かめの検査（`--coverage-sample`）が `screening.csv` の隣から自動で読む（両方の形で同じ）。残りの 3 本:`screening.csv`（段 1 は 2 割の記録だけ、段 2・3 は 2 人が判定した記録）を `c_synthesis.py --screening` に渡す。`screening-stage1-extra.csv`（網と残り。無作為の標本ではないので一致は別に読む）と `screening-net.csv`（網が何件を回し、共著者が何件を含めたか）は数を報告する。前半・後半の 2 本は作らない（AI の答えを読みながら進む偏りは、この形には無い）。`screening-csv` は、片方の人だけが中心を付けた（もう片方が全文段で含めなかった）記録の数も出す。この記録の中心は 2 人の合意で決まる。`release` は判定に共著者の列を足し、`author2-workbooks.csv`（冊ごとの作った時刻・取り込んだ時刻・戻った冊の SHA-256）も書く。

### 選別の後（今の形）

選別の後: `screening-csv` → `python3 c_synthesis.py --screening ../screening/screening.csv`（前半・後半の 2 本も同じく）→ `review-quotes` → 研究者が `~/TRACE-screening/quote-review.csv` の全行に scale_item（yes/no）を付ける → `release --out <公開の置き場所>` → `verify-removed --out <同じ>`。

- 選別の後（確かめの検査）: `python3 c_synthesis.py --screening ../screening/screening.csv --coverage-sample ../registration-attachments/coverage/new-records.csv` で `coverage.csv`（表 16）。判定の済んでいない記録が残っていれば `complete` が 0 になり、上下の幅で読む。
- 11 月: 較正の 1 回目（探索の集合の 11 研究）。12 月: 4 週以上あけて 2 回目。
