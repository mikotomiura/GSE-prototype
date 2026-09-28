# AI 疲労 文献 DB の Claude 再評価 — アーカイブ

研究者の依頼（2026-09-28）で、外部の AI 疲労文献 DB（34 件）を
適格性 → 方法論 → 領域別 / 照合 → スクリーニングの順に、一次資料に当たり直して評価した記録。
判断の経緯は同じ steering の `requirement.md` / `design.md`（プロトコル v1.0）/ `decisions.md` にある。

⚠️ **AI の予備判定であり、人間 2 名の独立判定の代わりにならない。** 元ワークブックの人間用の判定欄は変更していない。
⚠️ **GSE との照合は別シートにあり、採否には使っていない**（プロトコル §7）。
⚠️ `GSE照合` シートを含むので、公開用の `papers/` には置かない。

## 中身

| パス | 何か |
|---|---|
| `input/AI_fatigue_database_with_AI_appraisal_2026-09-18.xlsx` | 研究者から受け取った元ファイル（入力のスナップショット・16 シート・既存 AI 評価＝GPT を含む） |
| `AI_fatigue_database_with_AI_appraisal_2026-09-28_claude.xlsx` | ★ 評価版。元の 16 シートはそのまま、`Claude…` など 10 シートを追加 |
| `evidence/input-G1〜G6.md`・`db-dois.txt` | 抽出担当に渡した入力（題名・DOI・URL のみ。元 DB の値と既存評価の結論は渡していない） |
| `evidence/extract-brief.md` | 抽出の規則（記載なし／未確認の区別・JBI の項目文・締切・禁止事項） |
| `evidence/extract-G1〜G6.md` | 一次資料からの抽出ノート（サブエージェント・Sonnet） |
| `evidence/searchgap-brief.md`・`searchgap.md`・`searchgap-analysis.json` | 学術 API による検索漏れ点検（11 クエリ・見た 933 件・予備ふるい） |
| `evidence/verify.md` | 反証役による 10 主張の再照合（偽の主張 1 件を混入し、否定されたことを確認） |
| `scripts/data_a.py`・`data_b.py`・`data_c.py` | ★ 判定の本体（34 件の評価文・照合事項・検索漏れ候補の判定） |
| `scripts/assemble.py`・`build_xlsx.py` | シート定義を組み立て、元ワークブックに追加して保存し、元シートの不変を検算する |

⚠️ 論文の本文・PDF は入れていない（著作権。元 DB の方針「全文 PDF や尺度の全設問は同梱しない」と同じ）。
抽出ノートの逐語は 1 引用 40 語以内。

## SHA-256

```
48ba8b908413fc8112ec35852d4317389500f577092e7be47384628b5f7ce8b0  input/AI_fatigue_database_with_AI_appraisal_2026-09-18.xlsx
7833be448b25e9f346e73508d669adb3a1d9f2c6434f320c42fe6f755d53771f  AI_fatigue_database_with_AI_appraisal_2026-09-28_claude.xlsx
```

★ 研究者の Downloads にある 2 ファイルと一致することを確認済み（評価版は Codex レビュー反映後の版・2026-09-29）。
その他のファイルのハッシュは `sha256sum` で取り直せる。

## 再生成

```bash
cd .steering/20260928-ai-fatigue-db-appraisal/archive/scripts
python assemble.py                      # scripts/claude_eval.json を作る
python build_xlsx.py claude_eval.json   # ../AI_fatigue_database_with_AI_appraisal_2026-09-28_claude.xlsx を上書き
```

- 依存: `openpyxl`（本評価では 3.1.5）。
- `build_xlsx.py` は保存後に、元 16 シートの全セルが変わっていないこと・`スクリーニング!D5:F38` が全件「未判定」のまま・元のテーブル 14 個・入力規則・条件付き書式・結合セル・定義名が残っていることを確かめ、崩れていれば出力先を置き換えずに終了コード 1 で止まる（一時ファイルに保存して検算し、通ったときだけ置換）。構成は内容レベルで比べる（入力規則の式・条件付き書式のルールと書式の中身・テーブルの範囲とスタイル・定義名の値）。★ 変異 5 種（判定欄への書き込み・入力規則の削除・入力規則の式・テーブルのスタイル・条件付き書式の式）で赤になり、既存の出力が無傷で一時ファイルも残らないことを確認済み。出力先が入力と同じファイルなら（大文字小文字違い・リンク経由も）止まる。数式は概要と比較シートの決まった列だけに許し、題名などが `=` で始まっても文字列として保存する。
- ⚠️ openpyxl は保存時に条件付き書式の差分書式 ID（dxfId）を詰め直す。番号は変わるが、指す書式の中身は 12 範囲すべてで同じであることを確認した（比較は中身で行う）。
- `assemble.py` は design §9 の検査（必須欄の空欄なし・段の値域・除外理由の E コードの値域・判定と理由の整合）を assert する（★ 変異 3 種で止まることを確認済み）。
- ★ アーカイブ内のスクリプトだけで再生成したファイルが、納品物とセル単位で一致することを確認済み（2026-09-28）。
- ⚠️ 保存は openpyxl なので数式の計算済みの値を持たない（`fullCalcOnLoad=True` で Excel が開くときに再計算する）。
  LibreOffice でコピーを再計算し、数式 112 個に予期しない空・エラーがないことを確認した（空は元の `AI判定比較!E5:E38` が人間の判定欄の空に `""` を返すもののみ）。

## 評価の限界（詳細は xlsx の `Claude評価基準` シート）

- 盲検ではない（メインは既存 AI 評価を読んでから判定した。緩和策は design.md §0）。
- 全文に届かなかった件: AF002・AF003・AF009・AF015・AF021・AF025・AF027・AF028・AF031。
- 抽出の一部は WebFetch の要約経由（AF005 の項目文は言い換えだったので、メインが逐語を取り直した）。
- 検索漏れ候補は題名と機械抽出の根拠語だけで判定（抄録は未読）。Europe PMC と日本語文献は未検索。
- 正式な JBI・RoB・COSMIN・GRADE の判定ではない。
