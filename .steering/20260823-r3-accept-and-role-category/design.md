# 設計 — R3 の Accept と役割カテゴリの技術調査

> 2026-08-23 / ⚠️ **文書のみ。`src-tauri/` は無変更。**

## アプローチ

★ 本タスクは **設計を新しく起こすのではなく、確定した研究者判断を既決文書へ正確に落とす**作業である。
→ ⚠️ `/reimagine` は適用しない（`requirement.md §運用メモ`）。

| 段 | 何をしたか |
|---|---|
| 1 | **grill** で研究者判断 6 件＋追加 3 件を確定（★ dev が決められない事項なので最初に閉じる） |
| 2 | **一次確認** —— ⚠️ 判断 6（VK 量子化）の実装コストを `anonymize.rs` / `replay.rs` で実測 |
| 3 | **技術調査** —— 役割カテゴリの迂回路を repo のソースと Microsoft 一次ドキュメントで確認 |
| 4 | **文書化** —— ADR-014 / ADR-013 D6 / ADR README / `docs/architecture/` 新規 / `.idea` 追記 |

## 変更対象

| ファイル | 変更 |
|---|---|
| `docs/adr/ADR-014-continuous-natural-work-collection.md` | ★ **Accepted** 化・研究者判断 6 件を本文化・Migration 改訂 |
| `docs/adr/ADR-013-collection-self-description.md` | ★ D6 の 2 行へ **R3 の範囲での条件付き解除**を追記 |
| `docs/adr/README.md` | ★ ADR-014 行のステータス更新 |
| `docs/architecture/workspace-behavior-observation.md` | ★ **新規**（メモの昇格先） |
| `docs/agent-shared.md` | ★ リンクハブへ 1 行追加 ＋ ADR 範囲の陳腐化訂正 |
| `.idea/20260819-user-validation-workspace-behavior-and-mhd.md` | ★ 昇格の追記 ＋ **2026-08-21 追記の誤り 2 件を訂正** |
| `.steering/20260823-r3-accept-and-role-category/` | ★ requirement / design / decisions / tasklist / role-category-feasibility |

## テスト戦略

⚠️★★★ **`cargo test` は走らせない。★ `src-tauri/` のコード変更がゼロだからである。**

★ 代わりに次の 3 つを検査した:

| # | 検査 | 結果 |
|---|---|---|
| 1 | ⚠️ **禁止語**（`効果` / `精度が上が` / `有効性` / `利得` を利得の意味で）が昇格文書に無いか | ★ **該当 1 行のみ・規約の *宣言* 箇所**（ADR-012 と同じ書き方） |
| 2 | ⚠️ **`citation-ssot`** —— §6 の数値 4 件が `docs/references.md` に登録されているか | ★ **[P118] / [P120] に登録済み**（⚠️ 2026-08-21 追記の「未登録」は誤りだった） |
| 3 | ⚠️ **既決を壊していないか** —— `research-positioning §5` / `§8` 段別表 / ADR-009 D2 / ADR-012 D7 制約 4 | ★ **4 つとも 1 文字も変えていない** |

## ⚠️ リスクと未解決

| # | リスク | ★ 受け方 |
|---|---|---|
| 1 | ⚠️★★★ **判断 6 が H-Y の主要アウトカムを過小評価させる** | ★ **実装前に `Punctuation` 追加の採否を研究者に返した**（decisions D-7 / ADR-014 Migration 8）。⚠️ **実装は本タスクで行わない** |
| 2 | ⚠️ **役割カテゴリが「取れる」と分かったことで、順序を飛ばす誘惑が生じる** | ★ ADR-009 D2 の順序を維持し、**「取れる ≠ 要る」を feasibility 文書の §0 と §4 の両方に書いた** |
| 3 | ⚠️ **R3 の宣言 UI が未設計のまま Accepted にした** | ★ **Migration 7-ii に「別タスク」と明記**。⚠️ R3-a（`task_kind` 非依存）は宣言 UI 無しで実装できるので、Accepted が実装を止めない |
