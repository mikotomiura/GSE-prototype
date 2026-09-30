# 設計: 判定者用ファイル（N-02）

## アプローチ

前タスクの下書き `../20260929-ai-fatigue-db-readable-and-gaps/prior-draft/judge_xlsx.py` を出発点に、本タスクの `scripts/` に作り直す（下書きは `build_xlsx.py` の未コミット版に依存していて、そのままでは動かない）。

1. **判定シート（DB 34 件）**: 元の DB（`../20260928-ai-fatigue-db-appraisal/archive/input/AI_fatigue_database_with_AI_appraisal_2026-09-18.xlsx`・Downloads の同名ファイルと SHA-256 一致）の『文献DB』から書誌だけを取る（ID・題名・著者・年・掲載誌・公表区分・DOI・URL）。元の DB の『分類』『優先度』は DB 作成者の分類なので載せない。
2. **追加候補シート（157 件・decisions.md 判断 11・13 → ★ 2026-09-30 に B9 の採択研究から 2 件を足して 159 件・判断 15 → S-04 §3.1 の 34 件を足して 193 件・判断 17 → S-04 §3.2 の 13 件を足して 206 件・判断 20）**: 研究者の決定（`decisions.md` 判断 2）で範囲に入った候補。行は `scripts/candidates.py` のデータ（事実のファイル・節・行の目印）で定め、**要点の欄は事実のファイルの該当行・節から機械的に抜き出す**（手で書かない）。
   - S-02 §2 の 11 件（節 `### #n`）・S-12 §4.1 の 5 件と §4.2 の日本以外 4 件・S-04 §2 の 34 件と §5 の 5 件・S-05 §6 の 9 件。重なり（Liu 2024 = S-12 §4.2 と S-04 §5、AI-Echo = S-12 §4.1 と S-04 §2.1）は 1 行にまとめ、要点は出どころごとに並べる。★ 2026-09-30 に足した: S-02 §7 の 2 件（判断 15）・S-04 §3.1 の 34 件（作業負荷・時間だけの比較・判断 17）・S-04 §3.2 の 13 件（同じ種類で抽出の表の分類の外にあったもの・判断 20）→ 206 件。
   - 題名・年・掲載誌: S-04・S-05 の抽出の表（evidence の TSV）を DOI で引く。無ければ事実のファイルの書誌の表記。事実のファイルに DOI が無い行は、抽出の表の番号（例: R193）で DOI を与え、データにその出どころを書く。
3. **本文の入手の列**: DB 34 件と追加候補の DOI について、OpenAlex の `open_access`（DOI で 1 件ずつ・連絡先を送らない）を `evidence/oa_2026-09-30.json` に保存し、「無料の版あり／無料の版なし（OpenAlex の記録）／DOI なし」を事実として載せる（`decisions.md` 判断 3: 有料は入手しない → 全文段は保留）。
4. **はじめに・判定基準・集計**: 判定基準は評価プロトコル v1.0 ＋ 2026-09-30 の範囲の決定。判定者 1 のファイルには「判定の前に DB 34 件について評価版ファイルの AI の評価を読んでいる」事実を 1 行書く（`decisions.md` 判断 1）。判定者 2 は未定なので `--judge 2` で同じ形のファイルを後で作れるようにする。
5. **出力の保護**（下書きの直すこと 1・3）: 出力先が既にあれば止まる。`--force` でも、既存のファイルに記入（未判定以外）があれば止まる。出力先のディレクトリは作らない（無ければ止まる）。`--copy-to DIR` も同じ規則。

## 検査（`scripts/check_judge_xlsx.py`）

| 検査 | 範囲 |
|---|---|
| 常に禁止の語（評価の語・GSE の語・`Claude`・AI の評価の痕跡の語） | xlsx の zip の**全パーツ**の文字列（セル・共有文字列・コメント・定義名・文書のプロパティ・データの入力規則・条件付き書式・ヘッダー／フッター・テーブル） |
| 判定の語（`含める`・`除外`・`保留`・`中心-A`・`中心-B`・`全文段`・E1〜E6 など） | 許す格納先: 『判定基準』シート・判定シートと追加候補シートの見出しの行・『集計』シートの A 列と数式・データの入力規則・条件付き書式。**それ以外のセル・コメント・定義名・文書のプロパティ・シート名・ヘッダー／フッター・リンクの表示で赤** |
| `GPT`（単独の語。`ChatGPT` は書誌なので除く） | 書誌と要点の列以外で赤 |
| 記入欄の初期値 | すべて `未判定` か空 |
| ID | 判定シートの ID が元の DB の 34 件と同じ順 |
| 要点の出どころ | 追加候補の要点が、事実のファイルから抜き出し直したものと一致する |
| 元の DB | 入力 xlsx の SHA-256 が固定値と一致する（読むだけで変えない） |

- 語の一覧は `../20260929-ai-fatigue-surveys/scripts/check_survey_files.py` の `JUDGE`・`EVAL`・`GSE`（と正規表現）を import して使い、判定者用ファイル固有の語（AI の評価の痕跡）を足す。
- `--selftest`: 生成したファイルの写しに、**格納先ごとに**禁止語を入れる変異を作り、すべて赤になることを確かめる（セル・許す格納先の外のセル・記入欄の初期値・コメント・定義名・文書のプロパティ・シート名・ヘッダー／フッター・データの入力規則・条件付き書式・リンクの表示・要点の改変・ID の入れ替え）。変異なしの写しは緑になることも確かめる（陰性対照）。

## 変更対象ファイル

- `scripts/candidates.py`（新）— 追加候補のデータ（事実のファイル・節・行の目印・DOI の出どころ）
- `scripts/judge_xlsx.py`（新）— 判定者用ファイルの生成
- `scripts/check_judge_xlsx.py`（新）— 検査と変異試験
- `scripts/fetch_oa.py`（新）— OpenAlex の `open_access` の取得（`../20260929-ai-fatigue-surveys/evidence/common.py` の URL の許可・リダイレクトの柵・排他的な作成を使う）
- `evidence/oa_2026-09-30.json`（新・生成物）— DOI・OA の有無・OA の URL だけ（抄録の鍵を持たない）
- `archive/judge/AI_fatigue_judge-sheet_2026-09-30_judge1.xlsx`（新・生成物）— 記入前の判定者 1 用。Downloads に `--copy-to` で写す
- `memo-issues.md`・`decisions.md`・`requirement.md`・`tasklist.md`（本タスク）
- `../20260929-ai-fatigue-surveys/survey-S-08.md`（節の番号の直し）・`researcher-requests.md`（有料を外す）

## 既存パターンとの整合

- 行の高さの見積もり・書体・色は `../20260929-ai-fatigue-db-readable-and-gaps/scripts/build_readable.py` と同じ（前回の評価版と見た目を揃える）。自前で持つ（未コミット版の `build_xlsx.py` に依存しない＝下書きの直すこと 2）。
- DOI のリンクは `urllib.parse.quote` を通す（直すこと 4）。
- 検査の語の一覧は、サーヴェイの検査器と同じ SSOT を import する（別の一覧を作らない）。

## テスト戦略

- `python scripts/check_judge_xlsx.py <出力>`: 本物が緑。
- `python scripts/check_judge_xlsx.py --selftest`: 変異がすべて赤・陰性対照が緑。
- `python ../20260929-ai-fatigue-surveys/scripts/check_survey_files.py`（と `--selftest`）: 更新した事実のファイルを含めて違反 0。
- 出力の保護: 既存の出力先で止まること・記入のあるファイルは `--force` でも止まることを selftest に入れる。
- 手で確かめること: Excel（または LibreOffice）で開いて、入力規則・リンク・行の高さ・集計の数式が動くこと。

---

# サーヴェイ（研究者のメモから・`decisions.md` 判断 7）

★ 本節は **2026-09-30 03:54、S-15・S-14・S-13 の検索を 1 本も回す前に**固定した。以後の変更は `decisions.md` に「逸脱」として理由つきで書き、本節は書き換えない。
★ 共通の作法は前タスクの `../20260929-ai-fatigue-surveys/design.md` §0（3 つのファイルへの書き分け・機械の検査・取得と保存・本文の入手・サブエージェント）をそのまま使う。本タスクで変える点だけを下に書く。

## S0. 共通（本タスクで変える・足す点）

- **費用**: 無料の情報源だけ（`decisions.md` 判断 3）。Europe PMC・Semantic Scholar（一括検索）・Crossref（DOI の 1 件の取得）。OpenAlex の検索は使わない（前タスクの判断 3・9）。OpenAlex の 1 件の取得（`/works/doi:`）は OA の有無だけに使う。
- **置き場**: 本タスクのディレクトリ（`survey-S-15.md`・`survey-S-15-ai-judgments.md`・`survey-S-15-gse.md` ほか、`evidence/S-15/` ほか）。検査は `../20260929-ai-fatigue-surveys/scripts/check_survey_files.py` の `run()` を本タスクのディレクトリに当てる（`scripts/check_surveys_here.py`）。
- **取得のスクリプト**: `evidence/search_round.py`（3 本で共通・問いごとの検索式は同じファイルの表）。`../20260929-ai-fatigue-surveys/evidence/common.py` の `merge_abstract`（空で上書きしない）・`ensure_outside_repo`・`write_pair`（書誌と抄録の対）・`guarded_opener`（許した URL とリダイレクト）を使う。抄録の HTML は**タグの名前を限って**除く（`p < .001` の `<` を消さない・前タスク判断 11）。
- **期間**: 情報源に公開の年が 2026 年以前と記録されたもの（検索の日 2026-09-30 まで）。
- **既出の除き**: DB の 34 件・前タスクのサーヴェイ（S-02・S-04・S-05・S-12）の記録・本タスクで先に回したサーヴェイの記録と DOI が一致するものは「既出」とし、抽出に回さない（事実のファイルに件数だけ書く）。
- **0 段目（機械のふるい）**: 題名＋抄録に、問いごとの 3 群の語が**すべて**当たる記録。★ 通過が 250 件を超えたら、**0b 段**（3 群のうち、問いごとに決めた 1 群の語が**題名に**当たるもの）を当てる。★ どちらの段も、問いごとの種文献（DOI）がすべて通るかで確かめ、通らなければ正規表現の漏れとして直し、その直しを `decisions.md` に書く（前タスク判断 10 の作法）。
- **抽出**: `general-purpose`・**model: sonnet を明示**・1 本あたり 80 件以下・同時に 3 本まで・締切 15 分。入力は scratchpad の抄録の JSON だけ（ウェブ・repo への書き込み・入れ子の起動・外部への送信を禁止）。抜き出す項目は問いごとに下に書く（判定はさせない）。
- **メインの確認**: 表に載せる条件（問いごと）に当たる行は、メインが抄録で対象・N・デザイン・測定・著者が報告した向きを確かめてから事実のファイルに載せる。無料の本文があるもの（PMC・OA）は、時間の順序や定義に関わる行だけ本文で確かめる。
- **判定者用ファイルへの反映**: 事実の表に載せた一次研究のうち、DB・既存の追加候補に無いものを追加候補に足す。★ S-15 で見つかる自動化の研究は、研究者の決定（判断 2 (b)）に従い、論文が対象の系を AI・機械学習と書くものだけを足す。

## S1. S-15 AI への過信と疲労の両方向

### 問い

(a) 疲労（精神的疲労・意思決定疲労・消耗・睡眠不足・課題の時間経過）が、AI・自動化の助言の受け入れ（過信・自動化バイアス・確かめない受け入れ）を増やすか。(b) AI への依存・確かめない受け入れが、その後の疲労・消耗を増やすか（または減らすか）。(c) 両方を測った研究は、どちらを先に測った・操作したか。

### 検索

- Europe PMC（`TITLE_ABS`・`resultType=core`・全件）:
  - E1: `TITLE_ABS:("automation bias" OR overreliance OR "over-reliance" OR overtrust OR "over-trust" OR "AI reliance" OR "reliance on AI" OR "AI dependence" OR "AI dependency" OR "algorithmic advice" OR "advice taking" OR complacency) AND TITLE_ABS:(fatigue OR "decision fatigue" OR "mental fatigue" OR "ego depletion" OR exhaustion OR "sleep deprivation" OR sleepiness OR burnout) AND TITLE_ABS:("artificial intelligence" OR "machine learning" OR "decision support" OR algorithm OR "large language model" OR ChatGPT OR "generative AI" OR automation OR automated)`
  - E2: `TITLE_ABS:("decision fatigue" OR "mental fatigue" OR "cognitive fatigue") AND TITLE_ABS:("artificial intelligence" OR "decision support" OR "machine learning" OR "large language model" OR "generative AI" OR ChatGPT OR algorithm)`
- Semantic Scholar 一括検索:
  - S1: `("automation bias" | overreliance | "over-reliance" | "AI reliance" | "reliance on AI" | "AI dependence" | complacency) + (fatigue | "decision fatigue" | "mental fatigue" | exhaustion | depletion)`
  - S2: `("decision fatigue" | "mental fatigue" | "cognitive fatigue") + ("AI advice" | "AI recommendations" | "decision support" | "algorithmic advice" | "AI-assisted")`
  - S3: `("generative AI" | ChatGPT | "large language model") + (dependence | dependency | overreliance) + (fatigue | exhaustion | burnout)`
- 種文献（0 段目で必ず通ること）: AF004 `10.1016/j.actpsy.2025.105725`・AF005 `10.3389/fpsyg.2026.1879080`。

### 0 段目の 3 群

- 依存: `(?i)automation bias|over-?reliance|over-?trust|reliance|reliant|rely|dependen|complacen|advice[- ]taking|algorithm(ic)? advice|acceptance of (AI|algorithm)`
- 疲労: `(?i)fatigue|depletion|exhaust|burn-?out|sleep|tired|drowsi`
- AI・自動化: `(?i)artificial intelligence|\bAI\b|machine learning|algorithm|decision support|automat|large language model|\bLLM|ChatGPT|generative`
- 0b 段で題名に求める群: **疲労**。

### 事実の表に載せる条件

一次研究で、(1) AI・自動化への依存・受け入れ（行動の指標か自己報告）と (2) 疲労・消耗・燃え尽き・眠気（自己報告・課題の時間経過・睡眠の操作を含む）の**両方を測るか操作**しているもの。レビュー・理論は別の表に題名と主張だけ。

### 抽出の項目

デザイン（実験・縦断・横断・質的）・対象・N・国・系の種類（論文の書き方どおり: AI・機械学習・LLM・従来の自動化）・依存の測り方・疲労の測り方・**どちらを先に測った／操作したか**・著者が報告した向きと値。

## S2. S-14 AI のストレッサー・テクノストレスから燃え尽き・消耗へ

### 問い

AI に関わるストレッサー（テクノストレス・AI への不安・AI による仕事の不安〈STARA の認識を含む〉）と、燃え尽き・消耗・ストレインの関係を実証した研究は何か。デザイン（縦断・介入を含む）と、燃え尽きの尺度（MBI・CBI・OLBI・BAT など）は何か。

### 検索

- Europe PMC:
  - E1: `TITLE_ABS:(technostress OR "techno-stress" OR technostressor OR technostressors OR "AI anxiety" OR "AI awareness" OR STARA OR "AI-induced stress" OR "AI stressors" OR "AI-related stress") AND TITLE_ABS:(burnout OR "burn-out" OR exhaustion OR "emotional exhaustion" OR strain) AND TITLE_ABS:("artificial intelligence" OR "generative AI" OR ChatGPT OR "machine learning" OR "large language model" OR robot OR algorithm)`
  - E2: `TITLE_ABS:("artificial intelligence" OR "generative AI" OR ChatGPT OR "large language model") AND TITLE_ABS:("Maslach Burnout Inventory" OR "Copenhagen Burnout Inventory" OR "Oldenburg Burnout Inventory" OR "Burnout Assessment Tool" OR "Shirom-Melamed")`
- Semantic Scholar 一括検索:
  - S1: `(technostress | technostressor | "AI anxiety" | "AI awareness" | STARA | "AI stressor") + (burnout | exhaustion | strain) + ("artificial intelligence" | "generative AI" | ChatGPT)`
  - S2: `("AI-induced technostress" | "AI technostress" | "AI-stressors" | "AI stressors") + (burnout | exhaustion | well-being)`
- 種文献: AF019 `10.1016/j.ijinfomgt.2025.102887`・S-02 #9 `10.1057/s41599-024-04018-w`・S-02 #2 `10.1038/s41598-026-45402-7`。

### 0 段目の 3 群

- ストレッサー: `(?i)technostress|techno-stress|stressor|AI anxiety|AI awareness|STARA|job insecurity|stress`
- 燃え尽き: `(?i)burn-?out|exhaust|strain|fatigue`
- AI: `(?i)artificial intelligence|\bAI\b|machine learning|algorithm|automat|robot|large language model|\bLLM|ChatGPT|generative`
- 0b 段で題名に求める群: **燃え尽き**。

### 事実の表に載せる条件

一次研究で、AI に関わるストレッサー・AI の利用・導入を説明変数・文脈にし、燃え尽き・消耗・ストレインを尺度で測ったもの。★ S-04 で表にした医療の記録支援の比較研究は既出として除く。

### 抽出の項目

デザイン・対象（職種・学生）・N・国・AI に関わる変数（ストレッサーの種類）・燃え尽きの尺度の名前と下位尺度・時点の数・著者が報告した向き（媒介・調整を含む）。

## S3. S-13 組織の水準の AI 疲労

### 問い

(a) 組織の要因（導入の進め方・方針の明確さ・リーダーシップ・訓練・組織の支援）が、働く人の AI に関わる疲労・燃え尽き・消耗を左右すると報告した研究。(b) 組織を単位とする疲れ（変化の疲れ・取り組みの過多・AI の導入の疲れ）を AI と結びつけた研究。(c) チーム・組織を分析の単位にした研究。

### 検索

- Europe PMC:
  - E1: `TITLE_ABS:("artificial intelligence" OR "generative AI" OR ChatGPT OR "AI adoption" OR "AI implementation") AND TITLE_ABS:(organizational OR organisational OR leadership OR "organizational support" OR "change management" OR "human resource" OR "AI policy" OR managerial OR supervisor) AND TITLE_ABS:(fatigue OR burnout OR exhaustion OR "change fatigue")`
  - E2: `TITLE_ABS:("change fatigue" OR "initiative fatigue" OR "transformation fatigue" OR "innovation fatigue" OR "AI fatigue") AND TITLE_ABS:(organization OR organisation OR organizational OR organisational OR workplace OR employee OR employees)`
- Semantic Scholar 一括検索:
  - S1: `("change fatigue" | "transformation fatigue" | "innovation fatigue" | "AI fatigue") + (organization | organisation | workplace | employees)`
  - S2: `("AI adoption" | "AI implementation" | "generative AI") + (leadership | "organizational support" | "change management" | "AI policy") + (burnout | exhaustion | fatigue)`
- 種文献: S-02 #11 `10.3389/fpubh.2024.1343932`・AF019 `10.1016/j.ijinfomgt.2025.102887`。

### 0 段目の 3 群

- 組織: `(?i)organi[sz]ation|leader|manager|supervisor|human resource|\bHR\b|change management|polic|team|climate|culture|workplace`
- 疲労: `(?i)fatigue|burn-?out|exhaust|strain`
- AI: `(?i)artificial intelligence|\bAI\b|machine learning|algorithm|automat|large language model|\bLLM|ChatGPT|generative|digital transformation`
- 0b 段で題名に求める群: **組織**。

### 事実の表に載せる条件

一次研究で、(a)〜(c) のどれかに当たり、疲労・燃え尽き・消耗（または変化の疲れ）を測るか質的に分析したもの。

### 抽出の項目

デザイン・分析の単位（個人・チーム・組織）・対象・N・国・組織の変数（名前と役割: 説明・媒介・調整）・疲労系の測り方・著者が報告した向き。

## S4. 出すもの（3 本とも）

- `survey-S-1x.md`（事実）: 検索記録（情報源・検索式・実行の時刻・件数・0 段目と 0b 段の通過・既出）・事実の表・数のまとめ。
- `survey-S-1x-ai-judgments.md`: 事実の表の研究の TA 段の判定案・中心-A/B の見立て・研究の質の懸念・DB への提案。冒頭に「自分の判定が終わるまで読まない」。
- `survey-S-1x-gse.md`: GSE の文書との関係（短く）。
