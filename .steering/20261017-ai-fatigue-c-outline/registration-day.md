# 登録の当日の手順（C・TRACE）

作成 2026-10-18。上から順に行う。「研究者」と書いた手順は研究者が行い、それ以外はメインが行う。

## 前の日まで

1. 研究者: 共著者に相談文（`coauthor-consult.md`・docx）を送り、次の 2 つを受け取る。
   - 登録に載せる名前（英語）・所属・ORCID
   - 2 人目のコードを全件にするか 2 割にするか。これは本番のコードの前（2027 年 1 月）まででよく、登録の時点では要らない。
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
   - `uv run --with openpyxl python check_screening.py` が緑であること（選別の道具・判断 33）。
   - TRACE の DB を作り直したら、『段1』に全文の列が無く、『段2・3』があること（`make_trace_db.py`）。判定が 1 件も入っていない今の DB を上書きしてよい。
5. 添付 3（検索式・`query-strings.md`。第 16 節は確かめの検索）と GSRR-25 の **[at registration]** の中身を確かめる。選別の順の一覧に確かめの標本（群 `coverage_sample`・300 件）が入っていること。dryrun は 2026-10-18 の版（564 件）と比べる。
6. `python3 hash_attachments.py` で `sha256.txt` を作り、次の箇所に SHA-256 を書く。
   - 添付 2・3（確かめの検索の道具 2 本・新しい記録の一覧・検索の記録）・4・5・6（6 には選別の道具 3 本が入る）
   - GSRR-33（選別の順の一覧）
   - GSRR-64（脚本）
7. 冒頭を書き換える。
   - 「Registration draft 0.12 … Not yet registered」を版 1.0 と登録の日付にする。
   - 残った **[at registration]** を grep し、0 件にする。
8. 確かめる。
   - 体裁の検査（`_style_check.py`）。残るのは、意図して置いている日本語の語の一覧の 3 件だけ。
   - 草稿の組版（`latexmk`）。
9. 登録版・添付・`sha256.txt` をコミットし、push する。

## 当日（研究者）

10. OSF Registries で GSRR の様式を選び、各項目に登録版の文を写す。添付 1〜6 と `sha256.txt` を上げる。
11. 登録の識別子（DOI）と日付をメインに伝える。メインはそれを登録版・外枠・草稿に書き、コミットする。

## 登録の後すぐ（選別・束ごとに繰り返す。判断 33）

順番（判断 34）: 登録したらすぐ、判定者 1 と AI の選別を束ごとに回す。共著者（B+ を引き受けた場合）は後を追う。段 1 の 2 割は `make_coauthor_db.py --stage 1` の 1 冊、段 2 は束が全文段に回るたびに `--stage 2 --batch bNN --ids <その束の ID>` の 1 冊を渡す。登録の前には誰も判定しない（見本の `--preview` だけ配ってよい）。

道具は `scripts/c_screening.py`（`uv run --with openpyxl python c_screening.py <命令>`）。repo に置くのは ID・判定・SHA-256・時刻だけで（`screening/`）、抄録・全文・AI の出力の JSON は `~/TRACE-screening/s<段>-<束>/` に置く。

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

選別の後: `screening-csv` → `python3 c_synthesis.py --screening ../screening/screening.csv`（前半・後半の 2 本も同じく）→ `review-quotes` → 研究者が `~/TRACE-screening/quote-review.csv` の全行に scale_item（yes/no）を付ける → `release --out <公開の置き場所>` → `verify-removed --out <同じ>`。

- 選別の後（確かめの検査）: `python3 c_synthesis.py --screening ../screening/screening.csv --coverage-sample ../registration-attachments/coverage/new-records.csv` で `coverage.csv`（表 16）。判定の済んでいない記録が残っていれば `complete` が 0 になり、上下の幅で読む。
- 11 月: 較正の 1 回目（探索の集合の 11 研究）。12 月: 4 週以上あけて 2 回目。
