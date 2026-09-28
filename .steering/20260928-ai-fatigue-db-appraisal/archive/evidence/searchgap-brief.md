# 検索漏れ点検 brief（AI 疲労文献 DB）

## ゴール

既存 DB（34 件・`db-dois.txt`）は公開 Web 検索 53 クエリで作られ、**ヒット件数を記録していない**。
あなたは **学術 API で再現可能な検索**を行い、(1) クエリごとのヒット件数を記録した検索ログと、
(2) DB に **無い** 候補文献の一覧を `searchgap.md` に書く。

★ 採否の判定はしない。下の「予備ふるい」に当たるかどうかの**機械的な印**と、その根拠（題名・抄録の該当語）だけ付ける。

## 対象の定義（予備ふるいの基準・これ以外の理由で落とさない）

- 含める印: 題名または抄録に **fatigue / exhaustion / tiredness / burnout / weariness のいずれか** と、**人間が AI（生成 AI・chatbot・LLM・AI システム一般）を利用・監督・評価すること** の両方が出てくる文献。一次研究・レビュー・尺度研究・データセット論文を含む。
- 含めない印: AI（機械学習）が**人の疲労を検出・予測する道具**であるだけの研究（例: 運転者の疲労検出、EEG からの疲労分類）／材料・構造の fatigue（金属疲労など）／ニュース・ブログ。
- 期間: オンライン公開が 2026-09-28 以前。言語: 英語（日本語の文献が見つかれば別枠で記録）。

## 検索（最低限これを全部回す。1 クエリにつき結果の上位 50 件まで見る）

情報源: **OpenAlex**（`https://api.openalex.org/works?search=<q>&per-page=50`・`meta.count` がヒット件数）と **Crossref**（`https://api.crossref.org/works?query.bibliographic=<q>&rows=50`・`message.total-results`）。余裕があれば Europe PMC（`https://www.ebi.ac.uk/europepmc/webservices/rest/search?query=<q>&format=json&pageSize=50`）。

クエリ（引用符は完全一致）:
1. "AI fatigue"
2. "AI-induced fatigue"
3. "generative AI" fatigue
4. ChatGPT fatigue
5. chatbot fatigue users
6. "AI exhaustion" OR "AI burnout"
7. "decision fatigue" artificial intelligence
8. "cognitive fatigue" "generative AI"
9. "prompt fatigue" OR "prompting fatigue"
10. "AI technostress" fatigue
11. "AI fatigue scale" OR "AI fatigue" scale

- 各クエリの実行日時・情報源・ヒット件数・見た件数を検索ログに残す（API が 429 なら 5 秒あけて最大 3 回。取れなければ「取得失敗」と記録）。
- 取得結果の DOI を `db-dois.txt` と突き合わせ、DB に既にあるものは候補から外す（「既存 DB と一致」として件数だけ数える）。

## 出力（`searchgap.md`）

1. 検索ログ表: クエリ番号 / 情報源 / 日時 / ヒット件数 / 見た件数 / 既存 DB と一致した件数 / 予備ふるいに当たった新規件数
2. 新規候補表（最大 40 件・予備ふるいに当たったものを優先）: DOI / 題名 / 年・オンライン日 / 誌名 / 文献種別（一次研究・レビュー・尺度・データセット・会議・プレプリント）/ 根拠語（題名・抄録の該当語を短く）/ どのクエリで出たか
3. 当たらなかったが境界例と思われるもの（最大 10 件）とその理由

## 厳守事項

- **サブエージェントを起動しない（入れ子禁止）**。
- `C:/GSE-prototype` の中のファイルを作成・変更しない。書いてよいのは scratchpad だけ。git 操作はしない。
- 抄録全文を転載しない（根拠語だけ）。存在しない DOI を書かない（API の返り値からだけ書く）。
- **締切は起動から 25 分**。終わらなかったクエリは「未実行」と書いて返す。

## 返答（最終メッセージ）

10 行以内: 実行できたクエリ数、新規候補の件数（予備ふるいに当たったもの）、特に中心的に見える候補 5 件の DOI と題名。
