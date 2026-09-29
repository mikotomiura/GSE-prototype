# 設計 —— サーヴェイ A 群の手順

★ 各サーヴェイの手順（情報源・検索式・ふるい・書き分け）は、**そのサーヴェイの検索を 1 本も回す前に**本書へ追記して固定する
（09-28 の評価プロトコル v1.0 と同じ作法）。固定した節は書き換えない。変えるときは `decisions.md` に「逸脱」として理由つきで書く。
各節の見出しに固定した日時を書く。

## 0. 共通の方針（2026-09-29 21:10 固定）

### 0.1 判定の規則

- 判定案は評価プロトコル v1.0（`../20260928-ai-fatigue-db-appraisal/design.md`）の §1（PCC）・§2（用途判定・中心-A / 中心-B）・§3（TA 段・全文段・除外理由 E1〜E6・迷ったら含める）をそのまま使う。
- 判定はメイン（Opus）が行う。サブエージェントは抽出だけ（Sonnet を明示）。
- ⚠️ 本評価は AI の予備判定であり、人間 2 名の独立判定の代わりにならない（v1.0 §0）。

### 0.2 3 つのファイルへの書き分け（引き継ぎ §3・判断 12 / 13）

| ファイル | 書いてよいもの | 書かないもの |
|---|---|---|
| `survey-S-xx.md`（事実） | 検索記録（情報源・検索式・実行日・件数・目で見た範囲）／書誌／抄録・本文に書いてあること（対象・標本・デザイン・測定・著者が報告した結果の向き）／入手できなかったこと | 判定の語（含める・除外・保留・E1〜E6・中心-A/B・中心候補・背景保持）／評価の語（良い・問題・懸念・弱い・強い・十分・不十分・べき 等）／GSE への言及 |
| `survey-S-xx-ai-judgments.md`（AI の判定案） | 判定案・除外理由・中心-A/B の見立て・COSMIN の評価・研究の質の懸念・DB への追加の提案 | GSE への言及 |
| `survey-S-xx-gse.md`（GSE の含意） | GSE の文書・既決事項との関係・アイディア issue の材料 | — |

- `-ai-judgments.md` の冒頭に「判定者は、自分の判定が終わるまで読まない」と書く。
- 完了報告・PR 本文には件数だけを書く。

### 0.3 機械の検査（`scripts/check_survey_files.py`）

- 事実のファイル（`survey-S-??.md`）に、禁止語（判定の語・評価の語・GSE の内部の語）が 1 つも無いこと。
- 事実のファイルの引用符（「」・“”・""）の中の逐語が 40 語（日本語は 80 字）を超えないこと。
- 判定案のファイルの冒頭に「自分の判定が終わるまで読まない」の注意があること。
- `evidence/` の JSON・TSV に抄録・本文の欄（`abstract`・`description`・`fullText` 等の鍵）が無いこと。
- ★ `--selftest`: 一時ディレクトリに写した事実のファイルへ、禁止語の区分ごとに 1 語ずつ埋めた変異を作り、**どれもが赤になる**ことを確かめる。変異の無い写しが緑になることも確かめる。

### 0.4 取得と保存

- 学術 API には研究者のメールアドレスを送らない（`mailto` に入れない）。User-Agent に GSE の名や個人の連絡先を入れない。
- 1 秒あたり 1 回程度に抑える。429 などで使えなかった情報源は「使えなかった」と記録する（件数を推測で埋めない）。
- ★ **repo に置くもの**: 検索スクリプト（実行した版）と、書誌だけの結果（題名・著者・年・収録先・DOI/URL・当たった検索式）。
- ⚠️ **repo に置かないもの**: 抄録の全文・本文・PDF・尺度の項目文（scratchpad に置く）。逐語の引用は 1 引用 40 語以内。
- 件数は「調べる価値」の目安であり、PRISMA の件数ではない。

### 0.5 本文の入手

- オープンアクセスの本文は読む（出版社の HTML・PMC・機関リポジトリ・著者公開版）。
- ScienceDirect・Springer・IEEE など、スクリプトを弾く出版社は無理に取りに行かない。本文が要るものは `researcher-requests.md` に **[研究者]** として並べる（N-01 を含む）。

### 0.6 サブエージェント

- 抽出は `general-purpose` に **model: sonnet を明示**して渡す。範囲・禁止事項（入れ子で起動しない・repo に書き込まない・外部に送信しない・メールアドレスを送らない）・締切（10〜15 分）・「読んでいない範囲は読んでいないと書く」を必ず書く。
- 同時に走らせるのは 3 本まで。
- 戻ってきた主張は、判定に使う前にメインが一次で確かめる。確かめた件と確かめていない件を、判定案のファイルで列を分けて示す。

### 0.7 成果物の置き場

```
.steering/20260929-ai-fatigue-surveys/
  survey-S-12.md / survey-S-12-ai-judgments.md / survey-S-12-gse.md
  survey-S-02.md / … （S-08・S-04・S-05 も同じ）
  db-proposals.md          ← DB への追加・修正の提案（★ 判定案の一種。判定者は判定前に読まない）
  researcher-requests.md   ← [研究者] 本文の入手・有料データベースの検索の依頼
  evidence/S-xx/           ← 検索スクリプトと書誌だけの結果
  scripts/check_survey_files.py
```

## 1. S-12 日本語の文献・日本の対象者の研究（2026-09-29 21:10 固定・検索の実行前）

### 1.1 問い

日本語で書かれた研究、または日本の対象者を扱った研究のうち、AI を利用・監督・評価する人の疲労を定義・測定・質的に分析したものはあるか（PCC は v1.0 §1）。

### 1.2 情報源と検索欄

| 情報源 | 経路 | 検索欄 | 備考 |
|---|---|---|---|
| J-STAGE | WebAPI `service=3`（`count=1000`） | `article`（題名）と `abst`（抄録）を別々に | 一次（API マニュアル Ver.2.0）: 各欄は**中間一致**・大文字小文字と全角半角を区別しない・同じ欄の半角スペースは AND・OR は無い。★ `text`（全文）は材料の疲労などを大量に拾うため、比較のため件数だけ記録する |
| CiNii Research | OpenSearch v1 `all`（JSON・`count=200` で最大 1,000 件） | `title`（題名） | `OR` と括弧が効く（2026-09-29 の試しで確かめた）。`description` 欄は `all` で 0 件を返した → 抄録の欄の検索は J-STAGE で行う |
| CiNii Research（KAKEN） | OpenSearch v1 `projects` | `title` | 研究課題（科研費）。論文ではないが、国内で取り組まれているかの手がかり |
| 国立国会図書館サーチ | OpenSearch | `title` | 雑誌記事索引（商業誌・業界誌を含む）・博士論文 |
| Europe PMC | REST（`resultType=lite`） | `TITLE_ABS`・`AFF` | 英語で書かれた、日本の対象者の研究 |
| Semantic Scholar | 一括検索（`/paper/search/bulk`） | 題名・抄録 | 同上 |
| OpenAlex | `/works?search=` | 題名・抄録・本文 | 同上。匿名で使えなければ「使えなかった」と記録 |

★ 検索できないもの（`researcher-requests.md` に書く）: 医中誌 Web（有料）・情報処理学会 電子図書館（スクリプトの検索口なし）・Google Scholar（自動取得を禁じている）・学会の予稿で J-STAGE に無いもの。

### 1.3 検索語

- **AI の語（日本語）A-ja**: `AI`・`人工知能`・`ChatGPT`・`大規模言語モデル`・`LLM`・`チャットボット`
- **疲労の語（日本語）F-ja**: `疲労`・`疲れ`・`疲弊`・`燃え尽き`・`バーンアウト`・`消耗`・`テクノストレス`
- **負担の語（日本語・副）B-ja**: `負担`・`負荷` —— 狭い AI の語（`生成AI`・`ChatGPT`・`大規模言語モデル`・`LLM`）とだけ組む（`AI` と組むと AI が人の負担を推定する研究を大量に拾うため）
- **AI の語（英語）A-en**: `generative AI`・`ChatGPT`・`large language model`・`artificial intelligence`・`chatbot`
- **疲労の語（英語）F-en**: `fatigue`・`burnout`・`exhaustion`・`technostress`
- **日本の語**: `Japan`・`Japanese`

| 情報源 | 組み方 |
|---|---|
| J-STAGE | A-ja × F-ja の全組（42 組）× 2 欄（題名・抄録）／狭い AI の語 × B-ja（8 組）× 2 欄／A-en × F-en（20 組）× 2 欄。OR が無いので組ごとに 1 回 |
| CiNii Research（all・projects） | 題名に `(A-ja を OR) (F-ja を OR)`・`(狭い AI の語を OR) (B-ja を OR)`・`(A-en を OR) (F-en を OR)` の 3 本 |
| 国立国会図書館サーチ | 題名に A-ja × F-ja の全組（OR の効き方を確かめていないため組ごと） |
| Europe PMC | `TITLE_ABS:(A-en) AND TITLE_ABS:(F-en) AND (TITLE_ABS:(Japan OR Japanese) OR AFF:Japan)` と、`AFF` を外した版 |
| Semantic Scholar | `(A-en を \|) + (F-en を \|) + (Japan \| Japanese)` |
| OpenAlex | `search=(A-en を OR) AND (F-en を OR) AND (Japan OR Japanese)` |

- 期間の制限は置かない（2026-09-29 までに公開されたもの）。

### 1.4 機械的なふるい（★ 判定ではない。事前に固定した正規表現）

- **AI の正規表現**: `生成\s*AI|人工知能|ChatGPT|チャット\s*GPT|大規模言語モデル|LLM|チャットボット|対話型\s*AI|Copilot|(?<![A-Za-z0-9])AI(?![A-Za-z])`（最後の `AI` は大文字だけ・前後が英字でないこと。★ `6AI`（`6Al` の誤記）を落とすため前に数字も置かない）と、英語の `artificial intelligence|generative|large language model|chatbot`（大文字小文字を区別しない）
- **疲労の正規表現**: `疲労|疲れ|疲弊|燃え尽き|バーンアウト|消耗|テクノストレス` と `fatigue|burn-?out|exhaust|technostress|weariness|tired`（大文字小文字を区別しない）
- **題名ふるい**: 題名に両方が当たる記録。
- **抄録ふるい**: 抄録の欄の検索で当たり、題名ふるいを通らなかった記録について、抄録（J-STAGE の論文ページ）を取り、同じ 2 つの正規表現を抄録に当てる。★ 抄録は scratchpad にだけ置く。
- ★ 英語の記録（Europe PMC 等）は、題名・抄録に AI の語・疲労の語・日本の語の 3 つが当たる記録（検索式そのものがふるい）。

### 1.5 出すもの

- `survey-S-12.md`（事実）: 検索記録の表（情報源・欄・検索式・実行日・総件数・取得件数・ふるいの通過数）／ふるいを通った記録の書誌と、抄録に書いてあること（対象・方法・測ったもの）／KAKEN の研究課題の書誌／検索できなかった情報源。
- `survey-S-12-ai-judgments.md`: ふるいを通った各記録の TA 段の判定案（v1.0 §3）と、「日本語の研究は見当たらない」と書けるかの見立て。
- `survey-S-12-gse.md`: I-04（日本語版）・「我々で作る」への含意。
- `evidence/S-12/`: スクリプトと書誌だけの結果（全取得記録の題名・年・収録先・URL・当たった検索式）。

### 1.6 限界として先に書いておくこと

- J-STAGE の中間一致は `AI` を英単語の一部（例: maintain）にも当てる。題名ふるいの正規表現で落とす。
- 抄録を持たない記録（CiNii・国立国会図書館サーチの多く）は題名ふるいだけになる。
- 検索できなかった情報源がある（1.2 の末尾）。「見当たらない」は、この範囲での記述にとどめる。

## 2. S-02 検索漏れ候補 11 件の抄録（＋ 標本の重なり・N-06）（2026-09-29 22:05 固定・抄録を読む前）

### 2.1 対象

`../20260929-ai-fatigue-db-readable-and-gaps/issues.md` 付録 C の [S-02] の 11 件（★ 印 8 件＋AF017 の引用追跡 3 件）。

| # | 書誌（付録 C のまま） | DOI |
|---|---|---|
| 1 | Asmi ほか 2026, JEIM（意思決定疲労） | 10.1108/jeim-10-2025-1027 |
| 2 | Honggang ほか 2026, Scientific Reports | 10.1038/s41598-026-45402-7 |
| 3 | Khoso ほか 2026, Acta Psychologica | 10.1016/j.actpsy.2026.107396 |
| 4 | Thorpe ほか 2025, AI & Society | 10.1007/s00146-025-02764-2 |
| 5 | Kim & Kim 2026, Technology in Society | 10.1016/j.techsoc.2026.103553 |
| 6 | Chung & Kwon 2025, Education and Information Technologies | 10.1007/s10639-024-13198-6 |
| 7 | Kang & Li 2025, Journal of Business Convergence | 10.31152/jb.2025.12.10.6.297 |
| 8 | Nobles 2026, Zenodo（系統的レビュー・非査読） | 10.5281/zenodo.22838191 |
| 9 | Kim & Lee 2024, Humanit Soc Sci Commun | 10.1057/s41599-024-04018-w |
| 10 | Hur & Shin 2024, J Serv Mark | 10.1108/JSM-03-2023-0115 |
| 11 | Jeong, Kim & Lee 2024, Front Public Health | 10.3389/fpubh.2024.1343932 |

N-06（同時に行う）: IEEE DataPort の 2 件 doi:10.21227/rz27-ze05・10.21227/94rd-ny74。

### 2.2 手順

1. **書誌**: Crossref（DataCite）で題名・著者・収録先・年・訂正の関係（`update-to`・`relation`）を取る。
2. **抄録**: Crossref の `abstract` → Europe PMC（`resultType=core`）→ Semantic Scholar → 出版社の公開ページの順に、最初に取れたものを使う。抄録は scratchpad にだけ置く。
3. **本文**: オープンアクセスのものは本文を取り（Europe PMC の全文・出版社の公開 HTML/PDF・Zenodo のファイル）、scratchpad に平文で置く。
4. **抽出**（本文を取れたもの）: `general-purpose` のサブエージェント（model: sonnet）に、scratchpad の平文ファイルを渡して、下の項目を抜き出させる。★ サブエージェントにはウェブを使わせない（渡したファイルだけを読む）。判定の語を使わせない。
   - デザイン・対象（N・母集団・国・収集の時期と場所）・疲労（または燃え尽き・消耗）の構成概念と尺度（出典・項目数・**項目が AI に触れているか**）・AI の利用の変数・疲労に関わる主な結果（数値つき）・データの公開・倫理の記載
5. **メインの裏取り**: 抽出の「疲労の尺度」「AI に触れているか」「N・国」「主な結果」の 4 点は、メインが平文ファイルで該当箇所を開いて確かめる。確かめた点としていない点を判定案のファイルで分ける。
6. **標本の重なり（#2 と #3）**: 著者・N・収集の時期・場所・尺度・募集の経路を並べて比べる（事実）。重なりの見立ては判定案。
7. **Zenodo のレビュー（#8）**: 採択研究の一覧を本文から取り、DB の 34 件・09-28 の検索漏れ候補 145 件と DOI・題名で突き合わせる（事実）。
8. **N-06**: DataCite の記述と DataPort のページで、データの生成方法（実測か合成か）・収集の手続き・倫理の記載を確かめる。

### 2.3 判定（判定案のファイル）

- TA 段は抄録で、全文段は本文を読めたものだけで判定する（v1.0 §3）。本文を読めないものは全文段を「保留」、全文確認は「入手不可」。
- 中心-A / 中心-B の見立ては v1.0 §2 の表どおり（項目文・定義・質問文に AI が明示されるか）。

### 2.4 出すもの

- `survey-S-02.md`（事実）・`survey-S-02-ai-judgments.md`・`survey-S-02-gse.md`・`evidence/S-02/`（書誌とスクリプト）。

## 3. S-08 AI 疲労の尺度の一覧（＋ N-07）（2026-09-29 22:30 固定・尺度の検索の前）

### 3.1 問い

AI に向けた疲労（項目文・定義に AI が出てくる疲労）は、何で測られてきたか。それぞれの項目数・下位尺度・AI への向け方・報告された信頼性・妥当性の検証・翻訳版。

### 3.2 対象にする測定

- **(a) AI に向けた疲労の測定**（一覧と COSMIN の評価の対象）: 項目文・定義・教示に AI（生成 AI・ChatGPT・AI の道具 等）が入る疲労・消耗・燃え尽きの測定。独自の尺度だけでなく、既存の尺度を AI に向けて書き換えたものも含める。
- **(b) AI の文脈の研究で使われた一般的な疲労・燃え尽きの尺度**: 名前と出典・使った研究だけを並べる（COSMIN の評価はしない）。
- ⚠️ テクノストレスの「ストレス要因」の尺度（過負荷・侵入など）、認知負荷、AI 不安は (a) に入れない（疲労ではない）。ただし (a) の研究の中で疲労と並べて測られていれば、その旨を書く。

### 3.3 情報源

1. DB の 34 件（評価版の抽出ノート `../20260928-ai-fatigue-db-appraisal/archive/evidence/extract-G*.md` を手がかりにし、数値は一次で確かめる）。
2. S-02・S-12 で見つかった候補。
3. 新しい検索（尺度の開発・検証）:
   - Europe PMC: `TITLE_ABS:("AI fatigue" OR "artificial intelligence fatigue" OR "generative AI fatigue" OR "ChatGPT fatigue" OR "AI-induced fatigue" OR "AI-related fatigue" OR "chatbot fatigue" OR "GenAI fatigue" OR "AI exhaustion" OR "AI burnout") AND TITLE_ABS:(scale OR questionnaire OR inventory OR instrument OR psychometric OR validation OR "factor analysis")`
   - Semantic Scholar 一括検索: 同じ語を `|` と `+` で。
   - Crossref の題名の検索（`query.title`）: `AI fatigue scale`・`AI fatigue questionnaire`・`generative AI fatigue scale`（関連度検索なので件数は記録せず、上位 50 件を目で見る）。
   - OpenAlex: 使えれば同じ式。使えなければ「使えなかった」と記録。
4. AF001 の前方の引用（翻訳版・再検証の有無）: Semantic Scholar の citations API。

### 3.4 抽出する項目（事実）

尺度の名前・出典・項目数・下位尺度・回答形式・AI への向け方（教示・項目のどこに AI が入るか。★ 項目文は書かず、項目番号と「AI が入るか」だけ）・開発の標本（N・国・言語）・報告された信頼性（α・ω・再検査）・構造の検証（EFA/CFA と適合度）・収束・弁別の検証・翻訳版の有無・入手できる場所（補足資料・データ）。

### 3.5 判定案のファイルで行う評価（COSMIN）

- COSMIN の「良い測定特性の基準」（構造的妥当性・内的一貫性・信頼性・測定誤差・仮説検証・異文化間妥当性・基準関連妥当性・反応性）ごとに、報告された結果を `+`（基準を満たす）・`−`（満たさない）・`?`（判定できない）で評価する。★ 合計点は付けない。
- 研究のバイアスのリスク（COSMIN RoB）は、本文を読めた研究だけ、特性ごとに `very good / adequate / doubtful / inadequate` で書く。読めない研究は「判定不能」。

### 3.6 N-07（AF001 の補足資料）

- 補足資料（Table S6 の全 15 項目）・ResearchBox 6748（事前登録・データ）で、項目と下位尺度の対応・採点・事前登録の範囲を確かめる。★ 項目文は repo に書かない（項目番号・下位尺度・AI が入る場所だけ）。
