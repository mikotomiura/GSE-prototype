# 設計

★ §2（検索式の下書き・種・判定の規則）は **2026-09-30、試しの検索を 1 本も回す前に**固定した。以後の変更は `decisions.md` に「開発の版」として理由つきで書き、本節は書き換えない（前タスクの作法）。
★ 試しの検索は**検索式の開発**であり、スクリーニングではない。件数と、種の DOI が結果に含まれるかだけを見る。題名・抄録を読んで記録を選ばない。

## 1. アプローチ

### 1.1 プロトコルの形

- `protocol-ja.md` を 1 本。節立ては GSRR（van den Akker ほか 2023, *Systematic Reviews* 12:170, doi:10.1186/s13643-023-02281-7・PMC10514995）の 65 項目に合わせる（§0 メタデータ 1〜9／§1 背景と問い 10〜16／§2 道具・資金・利益相反 17〜20／§3 検索 21〜32／§4 スクリーニング 33〜42／§5 抽出 43〜51／§6 まとめ 52〜65）。項目の番号を見出しに添え、英語の登録版で 1 対 1 に写せるようにする。
- 付録: A 登録前の段の開示（年表）／B 判定基準（除外理由コード・中心-A / B）／C 抽出フォーム／D 情報源ごとの検索式と試しの件数／E GSRR の項目との対応表。
- 準拠する手引き（書誌は Crossref で確かめた・2026-09-30）: JBI の手引き（Peters ほか 2020, doi:10.11124/JBIES-20-00167・DB の AF031）・JBI のプロトコルの手引き（Peters ほか 2022, doi:10.11124/JBIES-21-00242。⚠️ 無料の版が無い〈OpenAlex: closed〉ので本文は読まない。書誌だけ挙げ、項目は JBI Manual〈doi:10.46658/JBIMES-24-01・無料の web 版〉で確かめる）・抽出と提示（Pollock ほか 2023, doi:10.11124/JBIES-22-00123・green）・PRISMA-ScR（Tricco ほか 2018, doi:10.7326/M18-0850・DB の AF030。改訂中＝AF033）・PRISMA-S（Rethlefsen ほか 2021, doi:10.1186/s13643-020-01542-z）・PRESS 2015（McGowan ほか 2016, doi:10.1016/j.jclinepi.2016.01.021）。
- ★ 判定者 2 も読む文書なので、**AI の 1 件ずつの判定案・見立てを書かない**（件数・規則・手順だけ）。検査は前タスクの `check_survey_files.py` の禁止語の規則を当てる（§5）。

### 1.2 決まっていること（`decisions.md` 判断 1・2 と前タスクの判断）

- 定義文 = 案 A、範囲の語 = 案 C。用法の区分 U1〜U4 は**抽出の項目**にする（適格性の条件にしない）。U5（人でないもの）は範囲の外（E1 と同じ扱いか、新しいコードが要るかは §2.6 で決める）。
- 登録前の段（259 件）は開示し、登録したプロトコルは本検索以降と全体の抽出・まとめを縛る。
- 本検索でも判定者 1 は判定の前に AI の評価を読む。判定者 2 は AI の評価と見立てを開かない。判定者 2 の人選は研究者（未定）。
- 灰色文献は種類を問わず入れる。言語は英語と日本語（ほかは E7）。
- 無料の情報源だけ（judge-file 判断 3）。範囲の決定 (a)(b)（judge-file 判断 2）・候補の入口（判断 13・17）は v1.0 への追加としてそのまま引き継ぐ。
- ★ 範囲の決定 (b) を警報疲れ（S-06）に当てる: 論文が警報・提案を出す系を AI・機械学習と書く場合だけ P に当たる。規則だけの警報（従来の自動化）は E3。

## 2. 検索式の開発（★ 2026-09-30 固定・試しの前）

### 2.1 概念のブロック（英語）

- **A（AI）**: `"artificial intelligence" OR AI OR "generative AI" OR GenAI OR "generative artificial intelligence" OR ChatGPT OR "large language model" OR "large language models" OR LLM OR LLMs OR chatbot OR chatbots OR "conversational agent" OR "conversational agents" OR "AI assistant" OR "AI assistants" OR Copilot OR "machine learning" OR "AI-assisted" OR "AI-based" OR "AI scribe" OR "ambient AI" OR "algorithmic management"`
- **F（疲労の族・範囲の語 C）**: `fatigue OR fatigued OR exhaustion OR exhausted OR burnout OR "burn-out" OR "burned out" OR "burnt out" OR weariness OR tiredness OR depletion OR depleted OR drained`
- **本検索 = A AND F**（題名・抄録）。
- **補い B1（道具の名・職種の語・S-07）**: `("AI scribe" OR "ambient scribe" OR "ambient listening" OR "digital scribe" OR "AI-drafted" OR "AI-generated draft" OR "draft replies" OR "coding assistant" OR "GitHub Copilot" OR "code generation") AND F` — A の語を使わずに道具の名だけで書く研究を拾う。
- **S-10（強いデザイン）**: 検索のブロックにしない。本検索で含めた記録を、抽出の項目（デザイン）で数える（issue の next からの変更。理由: A AND F に設計の語を AND すると、本検索の部分集合を数え直すだけになる）。
- **S-06（警報疲れ）**: 本検索の F に `fatigue` があり、`"alert fatigue"`・`"alarm fatigue"` は A AND F で拾われる。★ 別のブロックにしない。範囲は §1.2 の (b) の当て方。

### 2.2 情報源（無料・スクリプトで回せるもの）と書き方

| 情報源 | 口 | 欄 | 書き方 |
|---|---|---|---|
| Europe PMC | REST `search`（`resultType=idlist`・`pageSize=1000`・cursorMark） | `TITLE_ABS` | `TITLE_ABS:(A) AND TITLE_ABS:(F)` |
| Semantic Scholar | 一括検索 `/graph/v1/paper/search/bulk`（`fields=externalIds,year`） | 題名・抄録 | `(A を \| で) + (F を \| で)`。語は引用符。★ 材料の疲労（fatigue life など）を除く版 V2 も試す: `+ -("fatigue life" \| "fatigue crack" \| "fatigue strength" \| "fatigue damage" \| alloy \| weld \| concrete \| composite)` |
| ERIC | `https://api.ies.ed.gov/eric/`（`search=`・`fields=id,title,doi`・`rows=2000`） | `title:`・`description:` | `(title:(A) OR description:(A)) AND (title:(F) OR description:(F))` の形。★ ERIC の構文は一次（API の説明）で確かめてから回す |
| arXiv | `http://export.arxiv.org/api/query`（`search_query`・`max_results`） | `ti:`・`abs:` | `(ti:A OR abs:A) AND (ti:F OR abs:F)`（語ごとに展開） |
| Zenodo | `https://zenodo.org/api/records`（`q`・`size`） | 全体（題名・説明） | `(A) AND (F)`（Elasticsearch の query string） |
| J-STAGE・CiNii Research | 前タスク S-12 の口と語（`../20260929-ai-fatigue-surveys/design.md` §S-12） | 題名・抄録 | ★ 本タスクでは試さない（S-12 の件数を開発の記録として引く） |

- **試さない情報源**（プロトコルには書く・試しは次の段）: ACM Digital Library・IEEE Xplore（web の検索口は無料。スクリプトの口が無い／キーの登録が要る）・Google Scholar（研究者が手で・自動取得を禁じている）・OATD（学位論文）。
- **使わない情報源**: Scopus・Web of Science・APA PsycInfo・医中誌 Web・ProQuest（有料）。OpenAlex の検索（匿名の検索が止まることがあり・キーの登録に連絡先が要る。前タスク判断 3）。Crossref の検索（真偽の演算子が無い。1 件の書誌の確かめにだけ使う）。
- 期間: 下限なし〜試しの日。言語の制限は検索でかけない（スクリーニングで E7）。
- ★ 連絡先（メールアドレス）を送らない。`User-Agent` は道具名だけ。

### 2.3 種（検索の検証に使う既知の記録・25 件）

★ **選び方の規則**（AI の判定案を使わない）: (1) S-11 の事実のファイルで、題名か抄録に AI に向けた疲労の語を使う記録 16 件と、目で見た補い 3 件（語の用法の事実）、(2) 前のサーヴェイの検索で種文献として事前に名指ししたもの（S-15: AF004・AF005／S-14: AF019・S02-09・S02-02）、(3) DB の AF011（題名に Decision Fatigue と AI）。重なりを除いて 25 件。

| 群 | 鍵（DOI は判定者用ファイルの archive の写し・SHA-256 `6984472e…` から） |
|---|---|
| 語を使う 16 | AF001・AF006・AF007・AF008・AF009・AF010・AF013・AF014・S02-07・S02-08・S04-37・S08-02・S08-03・S14-25・S14-31・S15-15 |
| 補い 3 | AF024・S02-12・S14-04 |
| 種文献 5 | AF004・AF005・AF019・S02-09・S02-02 |
| 題名 1 | AF011 |

- ⚠️ 種は「語を使う・種文献に選ばれた」記録に偏る（燃え尽きを一般の語で書く職場の研究は S-14 の種 3 件だけ）。これは限界としてプロトコルに書く。
- ⚠️ 情報源に記録が無い種（例: AF019 は Europe PMC に無い・judge-file 判断 9）は、再現の分母から外さず「情報源に無い」と別に数える。**情報源に記録があるか**は、DOI で 1 件ずつ引いて確かめる（検索式の外）。

### 2.4 試しで見るもの

1. 情報源・検索式ごとの件数（実行の日時・問い合わせの文字列そのまま）。
2. 種の再現: 情報源に記録がある種のうち、検索の結果に DOI が含まれる数。含まれない種は、題名・抄録のどの語が A・F に無いかを **書誌の題名だけ**で確かめる（抄録は scratchpad で読むが repo に書かない）。
3. ★ 題名・抄録を読んで結果を選ばない。雑音の見積もり（無作為の 50 件の題名で、材料の疲労・AI が疲労を検出するだけのものの数）は、**開発の記録**として件数だけ書く（どの記録かは書かない）。

### 2.5 直してよいこと・直さないこと（開発の版）

- 直してよい: 種が落ちた理由が「語の欠け」なら、その語を A・F・B1 に足して版を上げる（v0 → v1）。材料の疲労の除き（V2）を採るかは、種の再現が落ちない場合だけ。
- 直さない: 種を落とすために語を削ること。件数を減らすために F を狭めること（範囲は C で決まっている）。
- 各版の件数・再現・変えた語を `evidence/search-dev.md` と `decisions.md` に書く。最終の版をプロトコルの付録 D に写す。

### 2.6 判定の規則で、本タスクで案を作るもの（プロトコルに書く・研究者の確認は次の段で束ねる）

- E7（英語・日本語以外）: 題名・抄録の段で言語が分かる記録は、題名・抄録の段で E7。
- U5（人でないもの・例: モデルの性能の劣化の名）: 既存の E1（AI が人の疲労を検出・予測する道具であるだけ）の定義に当たらない。→ **E2**（人の疲労を定義・測定・質的分析していない）に当てる案（新しいコードを増やさない）。★ 案であることを書く。
- 本検索の結果で、登録前の段の 259 件と DOI が一致する記録は、判定をやり直さず「登録前の段で判定済み」として流れ図で分ける。

## 3. 変更対象ファイル

| ファイル | 変更内容 |
|---|---|
| `protocol-ja.md` | 新規（プロトコルの日本語の草稿） |
| `evidence/search_dev.py`・`evidence/test_search_dev.py` | 新規（試しの検索・種の再現。前タスクの `common.py` の柵を使う） |
| `evidence/search-dev.md`・`evidence/search_dev_*.json` | 新規（件数・再現・版。書誌の ID だけ・抄録なし） |
| `evidence/theory_rows.py`・`scripts/check_theory_rows.py` | 新規（理論の文献の貼れる xlsx と、その検査） |
| `archive/AI_fatigue_theory_rows_2026-09-30_claude.xlsx` | 新規（貼れるファイル。Downloads に写す） |
| `issue-status.md` | 新規（N-05・S-09・S-11 の状態） |
| `scripts/check_protocol_here.py` | 新規（前タスクの検査器の禁止語を protocol-ja.md・issue-status.md に当てる） |

## 4. 理論の文献の貼れるファイル（S-09 の決定）

- 入力: `../20260930-ai-fatigue-theory-and-usage/survey-S-09-ai-judgments.md` §2 の文献（DOI は `survey-S-09.md` の表）。書誌（著者・題名・誌名・巻・号・頁・年・オンラインの日）は Crossref で 1 件ずつ取る（書籍の章は Crossref の記録どおり。無い値は「未確認」）。
- 形: 元の DB（`../20260928-ai-fatigue-db-appraisal/archive/input/AI_fatigue_database_with_AI_appraisal_2026-09-18.xlsx`）の『文献DB』『研究情報』『書誌・出典』と**同じ列名・同じ順**の 3 シート＋『はじめに』（貼り方・ID の付け方・3 群の定義）。
  - 『文献DB』の「分類」= `尺度・理論`（DB の既存の値）。「理論」の区分と 3 群は、『研究情報』の「レビューでの位置づけ」の先頭に `理論｜疲労の仕組み` のように書く（★ DB に列を足さずに区分を持たせるため。列を足すかは研究者が貼るときに決める。『はじめに』に書く）。
  - ID: 仮の `TH01`〜。AF 番号は研究者が貼るときに付ける（『はじめに』に書く）。
  - 「確認レベル」: `Crossref の書誌・抄録確認`（抄録を読んだものは S-09 の事実のファイルのとおり）。
- 検査: 列名が元の DB と一致・書誌の値が Crossref の JSON と一致・DOI の重複なし・自我消耗の原典（Baumeister ほか 1998）の行に追試の行の ID が関連 ID として入っている（併記の規則）。
- 出力: repo の `archive/` と Downloads（新しい名前・排他的に作る。judge1.xlsx には触らない）。

## 5. テスト戦略

- `evidence/test_search_dev.py`: 検索式の組み立て（引用符・括弧・情報源ごとの書き方）と、種の再現の数え方（DOI の正規化・大文字小文字）を固定した例で確かめる。陰性対照（変異なしで緑）を先に確かめる。
- `scripts/check_theory_rows.py`: §4 の検査。変異（列名を 1 つ変える・巻を変える・関連 ID を消す）で赤になることを確かめる。
- `scripts/check_protocol_here.py`: 禁止語（前タスクの規則）と、GSRR の 65 項目の番号がすべて protocol-ja.md の見出しか対応表に出ること。

## 6. ロールバック計画

- 文書と検査だけで、DB・判定者用ファイル・評価版は変えない。戻すときはブランチを捨てる。Downloads に写した xlsx は新しい名前なので、消しても判定の作業に影響しない。

## 7. 259 件の間引き（★ 2026-09-30、検出を 1 本も回す前に固定・`decisions.md` 判断 3）

### 7.1 入力

- 259 件: 判定者用ファイルの archive の写し（SHA-256 `6984472e…`）の『判定シート』34 件と『追加候補』225 件（鍵・題名・DOI・年・誌名・事実のファイルでの表記）。
- 書誌の関係: Crossref（`/works/{doi}` の `author`・`type`・`relation`・`title`）と DataCite（`/dois/{doi}` の `creators`・`relatedIdentifiers`・`types`）を 1 件ずつ。連絡先を送らない。取った書誌（抄録を除く）は `evidence/dedup/` に置く。
- 抄録: 前タスク（theory-and-usage）が取った 259 件の抄録（別セッションの scratchpad・`records_2026-09-30_abs.json`・run_id `1980b7a2…`・input_sha256 `6984472e…` の一致を確かめてから読む）。repo に写さない。

### 7.2 観点（候補の組を出す検出器。どれか 1 つが当たれば組にし、当たった観点を全部記録する）

| 記号 | 観点 | 規則 |
|---|---|---|
| P1 | 書誌の関係 | Crossref の `relation` の `is-preprint-of`・`has-preprint`・`is-version-of`・`has-version`・`is-identical-to`・`is-same-as`・`is-manifestation-of`・`has-manifestation`・`is-translation-of`・`has-translation`、DataCite の `IsVersionOf`・`HasVersion`・`IsPreviousVersionOf`・`IsNewVersionOf`・`IsIdenticalTo`・`IsVariantFormOf`・`IsOriginalFormOf`・`IsTranslationOf`（大文字小文字は区別しない）が、259 件の中の別の DOI を指す |
| P2 | 題名の近さ | 正規化した題名（NFKC・小文字・英数字と空白だけ）の `difflib.SequenceMatcher` の比が 0.85 以上。または 0.60 以上で P3 の著者が 1 名以上重なる |
| P3 | 著者の重なり | 姓（Crossref・DataCite の family。無ければ表記から）の正規化（NFKD でアクセントを除き小文字）で 2 名以上が重なる。または筆頭著者の姓が同じで年の差が 1 以内 |
| P4 | 前刷り・写しの DOI | DOI の接頭が前刷り・写しの置き場（`10.21203` Research Square・`10.2139` SSRN・`10.31234` PsyArXiv・`10.31219` OSF・`10.31235` SocArXiv・`10.35542` EdArXiv・`10.20944` Preprints.org・`10.22541` Authorea・`10.1101` bioRxiv/medRxiv・`10.48550` arXiv・`10.5281` Zenodo・`10.36227` TechRxiv・`10.32388` 学会の前刷り〈記録どおり〉）の記録と、題名の比が 0.60 以上の記録 |
| P5 | 標本の指紋 | 抄録から、標本の名詞（participants・students・respondents・employees・workers・teachers・nurses・physicians・users・adults・individuals・learners・undergraduates・professionals・clinicians・people・subjects・学生・参加者 など）の前後 3 語以内の 30 以上の整数と `N = 数`・`n = 数` を取り、同じ数を持ち、かつ国名（国の一覧）が 1 つ以上重なるか著者が 1 名以上重なる組 |

- ★ レビュー・訂正通知・方法論も組の対象にする（同じ報告の版違いはありうる）。訂正通知と原著の組（AF034 と AF004 など）は「同じ報告」ではなく「訂正の関係」として別に記録する（判定基準の E4 で扱う既存の扱いを変えない）。

### 7.3 分け方（メインが 1 組ずつ、書誌の関係と抄録で確かめる）

| 区分 | 条件 | 判定者用ファイルでの扱い |
|---|---|---|
| **同じ報告** | 同じ論文の版違い: 題名がほぼ同じ・著者が同じで、(a) 書誌の関係（P1）があるか、(b) 一方が前刷り・写しの置き場にあり、抄録の標本・デザイン・主な数値が一致する | 1 件に寄せる。残す 1 件（代表）は、雑誌の版 ＞ 会議録 ＞ 前刷り ＞ リポジトリ・Zenodo の写し。★ **DB の行は消さない**: 組の片方が DB の行なら、版にかかわらず DB の行を代表にし、追加候補の側を寄せる（どちらが雑誌の版かを注に書く）。寄せた記録は『寄せた記録』シートに代表の鍵と一致点を並べる |
| **同じ研究の群** | 別の報告（題名・分析・問いが違う）だが、著者が重なり、かつ抄録で標本の N・国・対象・収集の時期のうち 2 つ以上が一致するか、論文が同じデータ・同じ標本と書く | 行は消さない。「同じ研究の群」の列に群の番号と、一致点・違う点（事実だけ）を書く。E5 かどうかは判定者が決める |
| **別の研究** | 組にはなったが、標本・対象・時期のどれかが明らかに違う、または一致を示す事実が無い | 何もしない。`dedup-259.md` に「調べて別と分かった組」として件数と理由を書く |
| **確かめられない** | 抄録が無く、書誌の関係も無い（著者と題名だけが近い） | 何もしない。`dedup-259.md` に並べる（判定者が本文で確かめる材料として、群の列に「要確認」と書くかは件数を見て決め、判断に記録する） |

- ★ 同じ報告に寄せるときは、両方の DOI の書誌（Crossref・DataCite の題名・著者・年）を `evidence/dedup/` に残す。
- ★ 分け方の理由は事実（関係の種類・一致した値）で書き、範囲の判断（E1〜E3）を書かない（判定者 2 も読むため）。

### 7.4 独立の第 2 の読み（多角的な確かめ）

- メインの分けを渡さずに、同じ組（書誌・抄録）を `general-purpose`（**model: sonnet を明示**・理由: 判断を含むが、メインが一次で裁定するので、やり直しが効く読み）に渡し、7.3 の規則だけで分けてもらう。入力は scratchpad のファイルだけ（ウェブ・repo の書き込み・入れ子の起動・外部への送信を禁止・締切 15 分）。
- メインの分けと食い違った組は、メインが一次（抄録・書誌の関係）で確かめ直し、`dedup-259.md` に食い違いと裁定を書く。★ 第 2 の読みは証拠ではなく、見落としを拾うための網である。

### 7.5 出すもの

- `evidence/dedup.py`（検出・書誌の取得）・`evidence/test_dedup.py`（各観点の陽性・陰性）・`evidence/dedup/`（書誌と組の JSON。抄録なし）。
- `dedup-259.md`（事実: 組・観点・区分・一致点。判定者 1・2 が読んでよい。1 件ずつの範囲の判定案を書かない）。
- 判定者用ファイルの作り直し: `judge_xlsx.py`（judge-file タスク）に、`dedup-259` の結果（寄せる記録・群）を読む処理を足す。『追加候補』から寄せた記録を外し、両方のシートに「同じ研究の群」の列を足し、『寄せた記録』シートを足す。`check_judge_xlsx.py` を合わせる。作り直す直前に Downloads の写しが archive と同じ SHA-256 かを確かめる（違えば止まって聞く）。

### 7.6 内容の群（★ 2026-09-30、付ける前に固定・`decisions.md` 判断 5）

- **目的**: 標本は別だが内容がほぼ同じ研究を、消さずに並べて見られるようにする（判定の材料ではなく並べ替えのため）。判定者用ファイルの列「内容の群（機械の分類）」に出す。
- **入力**: 題名・抄録（7.1 の抄録）・判定者用ファイルの要点の欄（追加候補）・元の DB の『研究情報』の「研究デザイン」「対象集団」「AI・利用環境」（DB 34 件）。抄録と要点は repo に写さない。
- **3 つの軸**（正規表現。大文字小文字を区別しない。各軸で上から順に最初に当たった値を採る）:

| 軸 | 値（優先の順）と語 |
|---|---|
| 文献の種類 | `レビュー等`: review・meta-analy・scoping・systematic review・guideline・checklist・corrigendum・erratum・correction・protocol for・framework（題名）／ それ以外は一次研究として下の 3 軸を付ける |
| 対象 | `医療者`: physician・clinician・nurse・doctor・radiolog・resident・surgeon・pharmacist・health care worker・healthcare professional・medical staff・general practitioner・provider・看護・医師 ／ `教員・研究者`: teacher・faculty・educator・instructor・academic staff・researcher・lecturer・教員 ／ `学生・学習者`: student・learner・undergraduate・pupil・EFL・学生 ／ `働く人（医療・教育の外）`: employee・worker・staff・knowledge worker・manager・developer・programmer・professional・accountant・banker・従業員・労働 ／ `消費者・一般の利用者`: consumer・customer・user・adult・public・citizen ／ `不明` |
| AI の種類 | `記録支援・下書き`: scribe・ambient・documentation・draft repl・draft respon・inbox・chart summar ／ `意思決定支援・警報・予測`: decision support・CDSS・AI-DSS・alert・alarm・predict・early warning・diagnos・computer-aided・triage ／ `生成 AI・対話`: generative・ChatGPT・LLM・large language model・chatbot・conversational・GPT・Copilot・GenAI ／ `AI 一般・導入`: artificial intelligence・AI・automation・robot・algorithm ／ `不明` |
| デザイン | `無作為化`: randomi[sz]ed・RCT・crossover trial ／ `比較（非無作為化・前後）`: pre-post・pre- and post・before and after・before-after・preintervention・quasi-experiment・controlled trial・comparative ／ `縦断`: longitudinal・time-lagged・three-wave・two-wave・panel・cohort・diary・experience sampling ／ `尺度開発`: scale development・validation・psychometric・factor analysis ／ `質的`: qualitative・interview・focus group・thematic・grounded theory・content analysis ／ `実験・模擬`: experiment・simulation ／ `横断調査`: cross-sectional・survey・questionnaire・structural equation・SEM・PLS・regression ／ `不明` |

- **群の名**: 一次研究は `対象｜AI の種類｜デザイン`、レビュー等は `レビュー等`。
- **メインの確かめ**: (a) どれかの軸が `不明` の記録はすべて、題名・抄録・要点・DB の欄を読んで直す（直したことを記録）。(b) 不明でない記録から無作為の 30 件（seed 20260930）を読み、3 軸の一致の数を書く（機械の分類の確からしさの目安）。直すのは (a) と、(b) で誤りと分かった記録だけ。
- ★ 範囲の判断（E1〜E3）はしない。群は判定の材料ではないと『はじめに』と列の見出しに書く。
