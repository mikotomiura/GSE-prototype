# 検索式の開発 v0 の記録（2026-10-01）

> ★ 検索式の**開発**であって、スクリーニングではない。件数と、種の DOI が結果に含まれるかだけを見た（題名・抄録で記録を選んでいない）。手順は `../design.md` §2（試しの前・2026-09-30 23:21 に固定）。
> 取得した記録の ID の一覧は repo の外（作業用の一時の置き場）にあり、ここには件数・種の再現・一覧の SHA-256 だけを書く。記録の JSON は式を SHA-256 で持ち、式の本文は §7（`../decisions.md` 判断 13）。
> 取得の直し（Zenodo・ERIC・Semantic Scholar の種の確かめ・途中で切れた応答）は、実行の後に入れた（`../decisions.md` 判断 11）。**語（A・F・B1）は変えていない**。
> ★ §1・§4・§5 の和・突き合わせ・機械の数は `search_dev_summary.py` が ID の一覧から数え直し、`summary_search_dev_v0_2026-10-01.json` に件数と一覧の SHA-256 だけを書いた（2026-10-01 のレビュー・判断 17）。

## 1. 件数（`search_dev_counts_v0_2026-10-01.json`・2026-10-01 01:37〜01:38）

| 情報源 | 式 | 件数（情報源が返した総数） | 取った ID（重複を除く） | うち DOI | 取った時刻 |
|---|---|---|---|---|---|
| Europe PMC | main（A AND F） | 4,349 | 4,342 | 4,177 | 01:38:38〜01:39:22 |
| Europe PMC | b1（B1 AND F） | 64 | 64 | 60 | 01:39:22〜01:39:23 |
| Semantic Scholar | main | 18,274 | 18,680 | 16,721 | 01:39:48〜01:40:36 |
| Semantic Scholar | main_v2（材料の疲労の語を除く） | 16,504 | 16,877 | 15,165 | 01:40:36〜01:41:23 |
| Semantic Scholar | b1 | 147 | 150 | 132 | 01:41:23〜01:41:24 |
| ERIC | main | 61 | 87（ERIC の ID 61 と、url の欄の DOI 26） | 26 | 01:47:48〜01:47:49 |
| arXiv | main | 1,858 | 1,856 | 1,856 | 01:39:25〜01:39:46 |
| Zenodo | main | 1 本の式は HTTP 500（F の語ごとの 13 本の総数の和は 4,109〈重なりを除く前・`search_dev_counts_v0_2026-10-01b.json`〉） | 3,326（13 本の和・重なりを除いた数） | 3,326 | 02:04:51〜02:31:50 |

- Semantic Scholar の「取った ID」が総数より多いのは、arXiv の ID を持つ記録を、情報源の DOI と arXiv の DOI の 2 つで数えるため。
- main の 5 本の和: DOI で重なりを除くと **21,686 件**（一覧の SHA-256 `0356cde195806bf1…`）。ほかに DOI の無い ID が 2,185 件（情報源をまたいで重なりを除いていない）。
- ★ 件数の 2 回目（`search_dev_counts_v0_2026-10-01b.json`・2026-10-01 02:58〜03:00）: Semantic Scholar の main は 18,275（1 回目 18,274）、ほかは同じ。Zenodo は 1 本の式が同じく HTTP 500 で、F の語ごとの 13 本の総数（fatigue 1,438 など）を記録した。
- ⚠️ 取った ID の数が総数より少ない情報源がある（Europe PMC 4,349 に対し 4,342・arXiv 1,858 に対し 1,856）。同じ DOI の記録が 2 つある（Europe PMC の別の出どころの記録・arXiv の版）と見られるが、確かめていない。arXiv と Zenodo の取得は、空のページで黙って止まる（総数に届かなくても止まる）。
- b1 の DOI 139 件のうち、main の和に無いのは 19 件。
- main_v2 は main から DOI で 1,556 件を除いた。⚠️ 除きの語の `composite`・`concrete` は人の研究の抄録にも出うる（例: 構造方程式の composite reliability）。Semantic Scholar で `(A) + (F) + "composite reliability"` は 1 件（02:14:30・記録は手元の件数だけで JSON は無い・判断 17）。
- 記録: 再現の数え直しの版は `search_dev_recall_v0_2026-10-01{,b,c,d}.json`（d が最終。取得の直しのたびに新しい名前で書いた）。

## 2. 種の有無（検索式の外で 1 件ずつ・`search_dev_seeds_2026-10-01{,b,c}.json`）

| 情報源 | 記録がある種 | 引き方 |
|---|---|---|
| Europe PMC | 7 / 25 | `DOI:"…"` |
| Semantic Scholar | 23 / 25 | DOI（arXiv の記録は `ARXIV:<id>`。S08-02 は 2 回目が 429 で、02:32:37 に 1 件だけ引き直した） |
| arXiv | 1 / 25 | `id_list` |
| Zenodo | 4 / 25 | `doi:"…"` |
| ERIC | 確かめていない | DOI で引く口が無い |

- 記録が無い種: どの情報源にも無いのは AF013 の 1 件（Europe PMC・Semantic Scholar・arXiv・Zenodo のどれにも無い）。

## 3. 種の再現（`search_dev_recall_v0_2026-10-01d.json`）

| 情報源 | 式 | 記録がある種のうち、結果に DOI がある | 落ちた種 |
|---|---|---|---|
| Europe PMC | main | **7 / 7** | — |
| Semantic Scholar | main | **22 / 23** | AF019 |
| Semantic Scholar | main_v2 | 22 / 23 | AF019（main と同じ） |
| arXiv | main | **1 / 1** | — |
| Zenodo | main | **4 / 4** | — |
| ERIC | main | 数えられない（記録がある種を確かめていない） | — |
| Europe PMC・Semantic Scholar | b1 | 0（B1 は道具の名の補いで、種はどれも道具の名を題名・抄録の語にしていない） | — |

- **main の 5 本の和で、種 25 件のうち 23 件が当たった**。当たらなかったのは AF013（どの情報源にも記録が無い）と AF019。
- **AF019 の落ちた理由**（題名だけで確かめた・`../design.md` §2.4）: 題名は “Insights from the Job Demands–Resources Model: AI's dual impact on employees’ work and life well-being” で、F の語が無い。Semantic Scholar の記録に抄録が無い（出版社が配っていない）ので、抄録の語で当たれない。→ **語の欠けではなく、情報源の抄録の欠け**（前の段の先例と同じ・`../../20260930-ai-fatigue-judge-file/decisions.md:65`）。F に「well-being」を足すのは範囲の語 C（疲労の族）を変えることになるので、足さない。
- → `../design.md` §2.5 の「語の欠けで落ちた種があれば語を足して版を上げる」に当たる種は無く、**版は v0 のまま**。
- main_v2 は種の再現を落とさない（`../design.md` §2.5 の「V2 は種の再現が落ちない場合だけ採る」の条件を満たす）。採るかは、§1 の注の除きの語と一緒に、最終の版を決めるとき（検索式の点検の後）に決める。

## 4. 登録前の段の 259 件との突き合わせ（★ 実行の後に足した確かめ・`../decisions.md` 判断 14）

- 259 件のうち DOI を持つ 255 件で、v0 の main の 5 本の和に DOI があるのは **194 件**（Europe PMC 111・Semantic Scholar 181・Zenodo 5・ERIC 4・arXiv 1。重なりあり）。
- 和に無い 65 件（DOI の無い 4 件を含む）を、候補の出どころの群で数えた（1 件ずつの判定はしていない）:

| 出どころの群 | 件数 | 和に無い |
|---|---|---|
| 探索版の DB（AF） | 34 | 20 |
| S-04 の作業負荷・時間だけの比較研究（S04-41〜S04-87・範囲の決定 (a) で候補にしたもの） | 47 | 22 |
| S-12（日本語の文献・日本の対象者） | 25 | 9 |
| S-05（自動化を見張る疲労・範囲の決定 (b)） | 9 | 6 |
| S-04 のほか | 39 | 3 |
| S-02 | 13 | 2 |
| S-14 | 46 | 2 |
| S-13 | 20 | 1 |
| S-08・S-15 | 26 | 0 |

- ★ **読み方**: 259 件は検索の正解の集合ではない（探索版の DB は背景の文献〈既存レビュー・尺度と理論の原著・方法論・訂正通知〉を含み、追加候補は判定の前の候補で、範囲に入るかは決まっていない）。ただし、**範囲の決定 (a) で候補にした「作業負荷・時間だけの比較研究」は、定義上、疲労の族の語（F）を題名・抄録に持たないので、A AND F では拾えない**。本検索でこの種類を集めるなら、別のブロックが要る（`protocol-ja.md` [GSRR-25] の確認待ち）。日本語の文献（S-12）は、本検索では J-STAGE・CiNii の口で別に集める（`../design.md` §2.2）。
- ⚠️ この突き合わせは `../design.md` §2 に無い、実行の後の確かめである。種の選び方（§2.3）は変えていない。

## 5. 雑音の見積もり（`../design.md` §2.4 の 3・件数だけ）

- 各情報源の main の DOI から無作為の 50 件（seed 20261001・並べた DOI の一覧からの抽出・`search_noise.py`）。題名は Crossref（無ければ DataCite）で引いた（2026-10-01 01:58〜02:00）。どの記録かは書かない（題名の一覧は repo の外）。

| 情報源 | 抽出の元（DOI） | 抽出の SHA-256 の先頭 | 題名が取れた | 題名に A の語 | 題名に F の語 | 両方 | 材料・構造の疲労と題名で分かる | AI が人の疲労・燃え尽きを検出・予測するだけと題名で分かる |
|---|---|---|---|---|---|---|---|---|
| Europe PMC | 4,177 | `8f5114851d55` | 50 | 20 | 10 | 3 | 0 | 4（ほかに題名だけでは決まらない 3） |
| Semantic Scholar | 16,721 | `332a8a73453d` | 48 | 19 | 6 | 4 | 6（ほかに 2） | 3 |

- 「題名に A・F の語」は v0 の語を語の境界で当てた機械の数（`summary_search_dev_v0_2026-10-01.json` の `noise`）。材料と検出の 2 つは、題名を読んだ数（開発の記録・スクリーニングではない・記録は件数だけ）。
- 題名に F の語が無い記録が大半（Europe PMC 40・Semantic Scholar 42）で、抄録の語で当たっている。

## 6. 取得の直し（`../decisions.md` 判断 11）

| 何が起きたか | 直し | 確かめ |
|---|---|---|
| Zenodo の 1 本の式（587 字）に、件数の問い合わせは HTTP 500。取得は HTTP 400 | 400 は 1 ページの件数（匿名は 25 件まで。応答の逐語「Page size cannot be greater than 25」）→ 25 件にした。500 は式の大きさ（A のブロックと F の語 1 つの式は通る）→ F の語ごとの (A) AND (f) の 13 本に分け、和を取る（A AND (f1 OR … OR f13) と論理的に同じ） | 13 本の総数の和は 4,108（1 回目の手元の確かめ）・4,109（2 回目の記録）・和は 3,326 |
| Zenodo の取得の途中で応答が切れた（IncompleteRead） | 再試行の対象に足した | 単体テスト |
| ERIC の API は DOI の欄を返さない（1 回目の再現は ERIC の ID だけで数え、DOI 0 件） | url の欄が doi.org のリンクのときだけ DOI とみなす（61 件中 26 件） | 単体テスト |
| Semantic Scholar は arXiv の記録を DataCite の DOI で持たない（S08-02 は DOI で引くと「無い」が、検索の結果には arXiv の ID から入っていた） | arXiv の DOI は `ARXIV:<id>` で引く | 02:32:37 に引き直して「有る」 |

- 単体テスト `test_search_dev.py` 18 本・`test_search_noise.py` 3 本が緑。直しを 1 つずつ外す変異（Zenodo の F の語を 1 つ落とす・1 ページ 100 件・1 ページ目で止める・ERIC の url を何でも DOI にする・Semantic Scholar で arXiv の ID を使わない・途中で切れた応答を再試行しない）はすべて赤。

## 7. 式の本文（v0・`search_dev.queries("v0")` と一字一句同じ）

- A（23 語）・F（13 語）・B1（10 語）・材料の除き（8 語）は `../design.md` §2.1〜§2.2 のとおり。空白・ハイフンを含む語は引用符で囲む。

### epmc main

- SHA-256: `f017112dad9dda1e24ba2c394fc243b809a01c6b482907003f931f50f701525e`

```
TITLE_ABS:("artificial intelligence" OR AI OR "generative AI" OR GenAI OR "generative artificial intelligence" OR ChatGPT OR "large language model" OR "large language models" OR LLM OR LLMs OR chatbot OR chatbots OR "conversational agent" OR "conversational agents" OR "AI assistant" OR "AI assistants" OR Copilot OR "machine learning" OR "AI-assisted" OR "AI-based" OR "AI scribe" OR "ambient AI" OR "algorithmic management") AND TITLE_ABS:(fatigue OR fatigued OR exhaustion OR exhausted OR burnout OR "burn-out" OR "burned out" OR "burnt out" OR weariness OR tiredness OR depletion OR depleted OR drained)
```

### epmc b1

- SHA-256: `184a111e56236ba63542476a30f475d5d21c3f84a3f0f0017b8650cdd8330328`

```
TITLE_ABS:("AI scribe" OR "ambient scribe" OR "ambient listening" OR "digital scribe" OR "AI-drafted" OR "AI-generated draft" OR "draft replies" OR "coding assistant" OR "GitHub Copilot" OR "code generation") AND TITLE_ABS:(fatigue OR fatigued OR exhaustion OR exhausted OR burnout OR "burn-out" OR "burned out" OR "burnt out" OR weariness OR tiredness OR depletion OR depleted OR drained)
```

### s2 main

- SHA-256: `ceaecdcf80b29131efc3e2f1d6206436b60326bbbb2a7d61b7366f61d09b65a6`

```
("artificial intelligence" | AI | "generative AI" | GenAI | "generative artificial intelligence" | ChatGPT | "large language model" | "large language models" | LLM | LLMs | chatbot | chatbots | "conversational agent" | "conversational agents" | "AI assistant" | "AI assistants" | Copilot | "machine learning" | "AI-assisted" | "AI-based" | "AI scribe" | "ambient AI" | "algorithmic management") + (fatigue | fatigued | exhaustion | exhausted | burnout | "burn-out" | "burned out" | "burnt out" | weariness | tiredness | depletion | depleted | drained)
```

### s2 main_v2

- SHA-256: `779a98fe9084292dec0a2c565cf98ce2cfc53ce4aedfbc9475f918c43fe8f2ca`

```
("artificial intelligence" | AI | "generative AI" | GenAI | "generative artificial intelligence" | ChatGPT | "large language model" | "large language models" | LLM | LLMs | chatbot | chatbots | "conversational agent" | "conversational agents" | "AI assistant" | "AI assistants" | Copilot | "machine learning" | "AI-assisted" | "AI-based" | "AI scribe" | "ambient AI" | "algorithmic management") + (fatigue | fatigued | exhaustion | exhausted | burnout | "burn-out" | "burned out" | "burnt out" | weariness | tiredness | depletion | depleted | drained) + -("fatigue life" | "fatigue crack" | "fatigue strength" | "fatigue damage" | alloy | weld | concrete | composite)
```

### s2 b1

- SHA-256: `1ceaeb88bbb7eac15b40b3a93b45d8b6c010ffdedc0e9379bd5539572404ad36`

```
("AI scribe" | "ambient scribe" | "ambient listening" | "digital scribe" | "AI-drafted" | "AI-generated draft" | "draft replies" | "coding assistant" | "GitHub Copilot" | "code generation") + (fatigue | fatigued | exhaustion | exhausted | burnout | "burn-out" | "burned out" | "burnt out" | weariness | tiredness | depletion | depleted | drained)
```

### eric main

- SHA-256: `a33571cb4389c830311a8d5e2c7e11a3306b680c00745329d1b200f26c15b565`

```
(title:("artificial intelligence" OR AI OR "generative AI" OR GenAI OR "generative artificial intelligence" OR ChatGPT OR "large language model" OR "large language models" OR LLM OR LLMs OR chatbot OR chatbots OR "conversational agent" OR "conversational agents" OR "AI assistant" OR "AI assistants" OR Copilot OR "machine learning" OR "AI-assisted" OR "AI-based" OR "AI scribe" OR "ambient AI" OR "algorithmic management") OR description:("artificial intelligence" OR AI OR "generative AI" OR GenAI OR "generative artificial intelligence" OR ChatGPT OR "large language model" OR "large language models" OR LLM OR LLMs OR chatbot OR chatbots OR "conversational agent" OR "conversational agents" OR "AI assistant" OR "AI assistants" OR Copilot OR "machine learning" OR "AI-assisted" OR "AI-based" OR "AI scribe" OR "ambient AI" OR "algorithmic management")) AND (title:(fatigue OR fatigued OR exhaustion OR exhausted OR burnout OR "burn-out" OR "burned out" OR "burnt out" OR weariness OR tiredness OR depletion OR depleted OR drained) OR description:(fatigue OR fatigued OR exhaustion OR exhausted OR burnout OR "burn-out" OR "burned out" OR "burnt out" OR weariness OR tiredness OR depletion OR depleted OR drained))
```

### arxiv main

- SHA-256: `0c797f87e9dd9afd9bac15d1d46493ac42ae34945ec591c5d9e52e8a6f8dd54b`

```
(ti:"artificial intelligence" OR abs:"artificial intelligence" OR ti:AI OR abs:AI OR ti:"generative AI" OR abs:"generative AI" OR ti:GenAI OR abs:GenAI OR ti:"generative artificial intelligence" OR abs:"generative artificial intelligence" OR ti:ChatGPT OR abs:ChatGPT OR ti:"large language model" OR abs:"large language model" OR ti:"large language models" OR abs:"large language models" OR ti:LLM OR abs:LLM OR ti:LLMs OR abs:LLMs OR ti:chatbot OR abs:chatbot OR ti:chatbots OR abs:chatbots OR ti:"conversational agent" OR abs:"conversational agent" OR ti:"conversational agents" OR abs:"conversational agents" OR ti:"AI assistant" OR abs:"AI assistant" OR ti:"AI assistants" OR abs:"AI assistants" OR ti:Copilot OR abs:Copilot OR ti:"machine learning" OR abs:"machine learning" OR ti:"AI-assisted" OR abs:"AI-assisted" OR ti:"AI-based" OR abs:"AI-based" OR ti:"AI scribe" OR abs:"AI scribe" OR ti:"ambient AI" OR abs:"ambient AI" OR ti:"algorithmic management" OR abs:"algorithmic management") AND (ti:fatigue OR abs:fatigue OR ti:fatigued OR abs:fatigued OR ti:exhaustion OR abs:exhaustion OR ti:exhausted OR abs:exhausted OR ti:burnout OR abs:burnout OR ti:"burn-out" OR abs:"burn-out" OR ti:"burned out" OR abs:"burned out" OR ti:"burnt out" OR abs:"burnt out" OR ti:weariness OR abs:weariness OR ti:tiredness OR abs:tiredness OR ti:depletion OR abs:depletion OR ti:depleted OR abs:depleted OR ti:drained OR abs:drained)
```

### zenodo main

- SHA-256: `cc8c5c617cfbe3dc8e1dd3073286faa7f14de1ef9889b61e3d571004f823f9c3`

```
("artificial intelligence" OR AI OR "generative AI" OR GenAI OR "generative artificial intelligence" OR ChatGPT OR "large language model" OR "large language models" OR LLM OR LLMs OR chatbot OR chatbots OR "conversational agent" OR "conversational agents" OR "AI assistant" OR "AI assistants" OR Copilot OR "machine learning" OR "AI-assisted" OR "AI-based" OR "AI scribe" OR "ambient AI" OR "algorithmic management") AND (fatigue OR fatigued OR exhaustion OR exhausted OR burnout OR "burn-out" OR "burned out" OR "burnt out" OR weariness OR tiredness OR depletion OR depleted OR drained)
```

### zenodo main の取得の式（F の語ごとの 13 本の和・判断 11）

- 1. `fatigue`: SHA-256 `fe8920b9a61efacc46d73dcfb22f8b16481710c12d92ea18a0b96e6f899295f3`（式は上の A のブロック AND (fatigue)）
- 2. `fatigued`: SHA-256 `1d32e03fda2498c92732466d1ead12bdcca28f021d64fe9a79b2e2f1ef7bfd8d`（式は上の A のブロック AND (fatigued)）
- 3. `exhaustion`: SHA-256 `91d739021504cf9922ad611d8f52b311db6aaf4e388a206dc60c62eda2759914`（式は上の A のブロック AND (exhaustion)）
- 4. `exhausted`: SHA-256 `d5b919e23c31d592d59ee26496e1f28aaaa4fb62bd683a9be42a42f251372560`（式は上の A のブロック AND (exhausted)）
- 5. `burnout`: SHA-256 `682ce4eecf529227d68c5b33958f802c039687918730972376e3d246b25588d6`（式は上の A のブロック AND (burnout)）
- 6. `burn-out`: SHA-256 `9dd9199b4d2fefd73dc960b6adabf3e1bd402481e01a2f2324cc524c4570af41`（式は上の A のブロック AND ("burn-out")）
- 7. `burned out`: SHA-256 `0717fa93ad69ecaa35befe73c13b2bc407d30fe2fb012a664b24548df1653ad3`（式は上の A のブロック AND ("burned out")）
- 8. `burnt out`: SHA-256 `61bdaa2cf3470407d2add3422236c6d7c404ffc7a8fa518117a90b88ed64d5f2`（式は上の A のブロック AND ("burnt out")）
- 9. `weariness`: SHA-256 `542861ceead292bf0ef0a230d0e67fcee11baf710b5cdb16b8f94538ebab03cf`（式は上の A のブロック AND (weariness)）
- 10. `tiredness`: SHA-256 `7b2080853f1294679b36c7af5f455b63c04614f05149d20e285414a3127cb5e0`（式は上の A のブロック AND (tiredness)）
- 11. `depletion`: SHA-256 `aa24afebb0bb7b554d072e741d73d09517d0d61ea6c289f9e7a84f87ac66fceb`（式は上の A のブロック AND (depletion)）
- 12. `depleted`: SHA-256 `9fbf6d2354ddfec192cd86d09fc5a0a22f85f84c60008d0a49bc70072b72f322`（式は上の A のブロック AND (depleted)）
- 13. `drained`: SHA-256 `bb65dc49eb3d85faddd5726ff5d6eaecc9d370a28053b1805bac93fc6ab713d3`（式は上の A のブロック AND (drained)）
