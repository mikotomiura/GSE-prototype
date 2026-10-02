# レビューを狙った探索の記録（2026-10-02）

- 目的: 新規性の確認（`novelty-check.md`）の前提 (a)「既存レビューを系統的に探していない」を埋める（decisions.md 判断 1）。
- 実行: サブエージェント 1 本（general-purpose・sonnet・締切 20 分 → 実際は約 35 分）と、メインの軽い取り直し（OpenAlex・判断 6）。実行日時 2026-10-02 02:50〜03:53（JST）。
- データ: `data/search-runs.json`（問い合わせ 132 行）・`data/search-records.json`（重複を寄せた 5,721 件・抄録なし・層と読む一覧の印つき）。新しい表の『探索の検索式』『探索の一覧』も同じもの。抄録はコミットしない（scratchpad の作業ファイルだけ）。

## 1. 定義（design.md §3・走らせる前に固定した）

- 題名か抄録に **AI の語**（artificial intelligence・AI〈大文字の単語〉・generative AI・ChatGPT・large language model(s)・LLM(s)・chatbot(s)・machine learning・algorithm(s)/algorithmic・automation/automated・自動化・人工知能・生成 AI）と **疲労の語**（fatigue・exhaustion・burnout/burn-out・weariness・tiredness・technostress・疲労・燃え尽き・バーンアウト・テクノストレス）の両方があり、**レビューの語**（review・meta-analysis/analyses・meta-synthesis・state of the art・レビュー・総説・メタ分析）を持つか、API の種別がレビュー（OpenAlex の type＝review・Europe PMC の pubTypeList に review・Semantic Scholar の publicationTypes に Review）。
- 期間 2020-01-01〜実行日。言語は問わない。照合は Python の正規表現（`AI` 以外は大文字小文字を無視・**語境界なし**）。
- API（無料・鍵なし・**メールアドレスを送らない**）: OpenAlex（`mailto` なし）・Europe PMC・Crossref（`mailto` なし）・Semantic Scholar（鍵なし）。検索式は疲労の語ごとに「AI の語の OR」AND「疲労の語」AND「レビューの語の OR」。総数が 2,000 を超えたら AI の語を 1 語ずつに分けた。種別＝レビューの問い合わせを疲労の語ごとに別に足した（OpenAlex の分は走らず・下記）。Crossref は `query.bibliographic = "{AI の語} {疲労の語} review"` の 10 × 6 の組（各 2,000 件で打ち切り）。

## 2. 件数

| API | 問い合わせ | 失敗 | 総数 | 取得 | 条件を通った | 打ち切り | 429 の回数 |
|---|---|---|---|---|---|---|---|
| OpenAlex | 38 | **16**（429） | 10,978 | 10,989 | 8,326 | 0 | 38 |
| Europe PMC | 22 | 0 | 1,551 | 1,551 | 1,468 | 0 | 0 |
| Crossref | 36 | 0 | 135,526,721 | 72,000 | 416 | **36**（各 2,000 件） | 0 |
| Semantic Scholar | 36 | 0 | 8,951 | 8,951 | 7,883 | 0 | 8（待って再試行して成功） |

- OpenAlex の失敗 16 = サブエージェントの 14（件数を確かめる問い合わせが 429・種別＝レビューの問い合わせを含む）＋ メインの軽い取り直し 2（題名の検索・待ち時間を延ばしても 429 → 打ち切り・判断 6）。広い語での取り直し（14 の式・AI の語ごとに分割）は 30 分の上限で止められ、結果をファイルに書く前だった（記録なし）。
- 重複を寄せた（DOI か正規化した題名）後: **5,721 件**。研究者の DB・追加候補との重なり: 79 件（C220 70・DB34 8・MERGED 1）。

## 3. 層（題名だけを見る機械の規則・判断 4）

| 層 | 規則 | 件数 |
|---|---|---|
| A1 | 題名に AI の語（狭い: artificial intelligence・AI・generative AI・ChatGPT・LLM・large language model・chatbot・人工知能・生成 AI）・疲労の語・レビューの語（review・systematic・scoping・meta-analys・meta-synthesis・umbrella・state of the art・literature・レビュー・総説・メタ分析）が全部ある | 81 |
| B1 | AI の語が広い方（machine learning・algorithm・automation・自動化）だけで同じく 3 つが揃う | 41 |
| A2・B2 | 題名にレビューの語は無いが、OpenAlex か Europe PMC の種別がレビュー | 3・2 |
| A3・B3 | 種別がレビューなのは Semantic Scholar だけ | 144・88 |
| C | 題名に疲労とレビューの語だけ | 331 |
| D | その他 | 5,031 |

## 4. 読む一覧（判断 5・6・7）

- A1＋B1（122 件）を題名で寄せると 99 件。題名の語の規則で分けた: AI が検出・予測・監視する型 36（検出・予測・監視・識別・分類・診断・ウェアラブル・EEG・ECG・sEMG・HRV・運転者・信号・センサーの語）／人でない疲労 14（亀裂・鋼・コンクリート・溶接・複合材・構造・材料・疲労寿命などの語）／査読の報告 1（題名が「Review of:」）／それ以外 48。
- ユーザーの指摘（「全部 ML 関連での技術的な話により初めてない？」）を受けて、読む対象を「それ以外」の 48 件（R01〜R48）に絞った（判断 5）。規則が明らかに外れた R42（眼の指標による疲労の評価）・R48（日本語の題名の複合材料の疲労）を外して 46 件（判断 6）。
- 46 件のうち、無料の版が無い 5 件（R04・R15・R19・R31・R33）は抄録だけ、既に読んだ 2 件（R28＝S02-08＝Nobles・R29＝AF014）と訂正通知（R45）を除く **38 件の本文を読む**（判断 7・サブエージェント 4 本で抽出・結論に使う箇所はメインが本文で確かめる）。
- 候補に足すかの判定は、次のタスクで残りの 213 件と一緒に行う（判断 4）。

## 5. この探索の限界

- 語境界なし・抄録込みの照合と、広い AI の語（machine learning・algorithm・automation）のために、技術系の記録（材料の疲労の予測・疲労の検出）を大量に呼び込んだ（判断 5 の反省）。
- OpenAlex は 16 回の問い合わせが抜けている（種別＝レビューの問い合わせが 1 本も走っていない）。Crossref は 36 回とも関連度順の上位 2,000 件で打ち切り。
- 読む対象は題名の語で決めたので、題名にレビューの語が無いレビュー（A3・B3・C の中）は読んでいない。
- 無料の版が無い 5 件は抄録だけ。
- 有料のデータベース（Scopus・Web of Science など）は使っていない。
