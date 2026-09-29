# AI 疲労 文献 DB —— 読みやすい版と調査不足の issue（2026-09-29）

2026-09-28 の Claude 評価版に、記号を知らなくても読めるシートと、調査不足を issue にしたシートを足した版。
判断の経緯は同じ steering の `requirement.md` / `design.md` / `decisions.md`、issue の一覧は `../issues.md`。

⚠️ **AI の予備判定であり、人間 2 名の独立判定の代わりにならない。** 既存の 26 シート（元の 16＋前回の Claude 10）は 1 セルも変えていない。
⚠️ **判定者としてスクリーニングをする人は、判定が終わるまで追加シートと Claude／GPT のシートを読まない**（`../issues.md` の N-02）。
⚠️ `GSE照合` シート（前回）を含むので、公開用の `papers/` には置かない。

## 中身

| パス | 何か |
|---|---|
| `AI_fatigue_database_with_AI_appraisal_2026-09-29_claude.xlsx` | ★ 今回の版。橙のタブ 7 枚（★まず読む・論文ごとの要点・証拠の地図・調査不足とissue・件数の目安と種文献・照会の下書き・用語の読み替え）を追加 |
| `evidence/*.json` | 件数の目安を取った生の結果（Europe PMC・Semantic Scholar・J-STAGE・CiNii・OpenAlex の初回） |
| `evidence/*.py` | 上を取ったスクリプト（OpenAlex・Europe PMC・Semantic Scholar・J-STAGE／CiNii・Crossref の実在確認） |

入力は `../../20260928-ai-fatigue-db-appraisal/archive/AI_fatigue_database_with_AI_appraisal_2026-09-28_claude.xlsx`（SHA-256 `a84c6e3f…`・変更しない）。

## SHA-256

```
7170ea62a4493329d20f917535a184cf8dea0185f01ab1b34a85e7664d2a1205  AI_fatigue_database_with_AI_appraisal_2026-09-29_claude.xlsx
a84c6e3fac93bdc765d179a6b5ccb7bfbff94b3945203f10ee8d36874ecaf091  ../../20260928-ai-fatigue-db-appraisal/archive/AI_fatigue_database_with_AI_appraisal_2026-09-28_claude.xlsx（入力・変更なし）
```

⚠️ openpyxl の保存物は作成時刻を含むため、再生成するとハッシュは変わる（内容の同一性はセル単位で比べる）。

## 再生成

```bash
cd .steering/20260929-ai-fatigue-db-readable-and-gaps/scripts
python build_readable.py                    # archive/ の xlsx と ../issues.md を書き直す
python build_readable.py --mutate-test      # 既存シートへの書き込みで検算が止まることを確かめる（出力は置き換えない）
```

- 依存: `openpyxl`（3.1.5）。前回の `build_xlsx.py` の `snapshot`・`structure`・`same_file` を import する。
- 検算: 保存前後で既存 26 シートのセル値・入力規則・条件付き書式・結合セル・テーブル・定義名を比べ、崩れていれば出力を置き換えずに止まる。シートの並び（元 16 → 追加 7 → Claude 10）と、`スクリーニング!D5:F38` が全件「未判定」のままであることも確かめる。
- ⚠️ openpyxl は数式の計算済みの値を持たない（`fullCalcOnLoad=True` で Excel が開くときに再計算する）。LibreOffice でコピーを再計算し、数式 175 個にエラーがないこと、主要な数（中心-A 7・中心候補 13 など）が期待値どおりであることを確かめた。

## 限界

- 件数は「調べる価値」の目安で、PRISMA の件数ではない。OpenAlex は回数制限で途中から使えなかった。
- 種文献は実在を確認しただけで、本文は読んでいない。
- 平易な要約は 2026-09-28 の評価と抽出ノートに基づき、新しい一次確認はしていない。
