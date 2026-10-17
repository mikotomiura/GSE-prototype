# 登録の当日の手順（C・TRACE）

作成 2026-10-18。上から順に行う。「研究者」と書いた手順は研究者が行い、それ以外はメインが行う。

## 前の日まで

1. 研究者: 共著者に相談文（`coauthor-consult.md`・docx）を送り、次の 2 つを受け取る。
   - 登録に載せる名前（英語）・所属・ORCID
   - 2 人目のコードを全件にするか 2 割にするか。これは本番のコードの前（2027 年 1 月）まででよく、登録の時点では要らない。
2. OSF が開いているかを確かめる。2026-10-17・18 は 503（メンテナンス中）。
   - 開いたら、OSF のメンテナンスで取れなかった文献の全文 3 件（R02・R22・R35）を取り直し、TRACE の DB を作り直す。

## 当日（メイン）

1. 登録版の GSRR-2 に、共著者の名前・所属・ORCID を書く。
2. 選別の順を作る。dryrun との diff が空であることを確かめる（2026-10-18 に確かめたときは同じだった）。TRACE の DB の行の順はこの順。
   ```
   cd scripts
   python3 make_screening_candidates.py <判定者 1 の表.xlsx> > /tmp/candidates.csv
   python3 c_synthesis.py --screening-order /tmp/candidates.csv > ../registration-attachments/screening-order.csv
   diff ../registration-attachments/screening-order.csv ../registration-attachments/dryrun/screening-order-2026-10-17.csv
   ```
3. 使った Python の版を GSRR-33 に書く（`python3 --version`）。
4. 確かめる。
   - `python3 make_coding_form.py ../registration-attachments/coding-form` でコード用紙を作り直し、git diff が空であること。
   - `python3 make_dummy.py` が緑であること。
5. 添付 3（検索式・`query-strings.md`）と GSRR-25 の **[at registration]** の中身を確かめる。
6. `python3 hash_attachments.py` で `sha256.txt` を作り、次の箇所に SHA-256 を書く。
   - 添付 2・4・5
   - GSRR-33（選別の順の一覧）
   - GSRR-64（脚本）
7. 冒頭を書き換える。
   - 「Registration draft 0.11 … Not yet registered」を版 1.0 と登録の日付にする。
   - 残った **[at registration]** を grep し、0 件にする。
8. 確かめる。
   - 体裁の検査（`_style_check.py`）。残るのは、意図して置いている日本語の語の一覧の 3 件だけ。
   - 草稿の組版（`latexmk`）。
9. 登録版・添付・`sha256.txt` をコミットし、push する。

## 当日（研究者）

10. OSF Registries で GSRR の様式を選び、各項目に登録版の文を写す。添付 1〜6 と `sha256.txt` を上げる。
11. 登録の識別子（DOI）と日付をメインに伝える。メインはそれを登録版・外枠・草稿に書き、コミットする。

## 登録の後すぐ

- AI の選別者を 264 件に当てる。
  - 束は固定の順で 9 件ずつ。束ごとに、著者 1 の判定をコミットして push してから走らせる。
  - 呼び出しの文と設定は `registration-attachments/ai-screening/call.md` のとおり。
- 判定者 1（研究者）は `~/Documents/TRACE/TRACE_database.xlsx` で選別を始める。
  - 段 1 は題名と抄録だけで判定し、全文は束の段 1 の判定をコミットしてから開く。
- 11 月: 較正の 1 回目（探索の集合の 10 研究）。12 月: 4 週以上あけて 2 回目。
