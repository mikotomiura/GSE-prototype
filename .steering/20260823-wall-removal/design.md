# 設計 — Wall (Lv2 介入) の全削除

> 2026-08-23

## アプローチ

★ **コンパイラと型検査に依存箇所を列挙させる**方式を採った（手作業の grep 網羅に頼らない）。

| 段 | 手順 |
|---|---|
| 1 | ★ **中核の型から削る** —— `InterventionAction::Wall` / 構造体フィールド / const |
| 2 | ★ `cargo check` が壊れた箇所を全部挙げるので、上流から順に潰す |
| 3 | ★ Frontend は `npx tsc --noEmit` で同じことをする |
| 4 | ★ 最後に `npm run build` / ゴールデン replay / schema parity で外形を確認 |

⚠️ **この方式の弱点が 1 度出た** —— ★ **コメント見出しを目印にした範囲削除**は型検査に引っかからない
（消した先が別機能でも、その機能を使っていた変数が「未使用」になるだけ）。
→ ★ **`TS6133` の増加**を「消しすぎ」の検出器として使った（変更前 0 件 → 変更後 3 件で気づいた）。

## 変更対象

| 層 | ファイル |
|---|---|
| Rust 判定 | `analysis/intervention.rs` / `analysis/intervention_eval.rs` |
| Rust ログ | `logger.rs` / `schema_dto.rs` / `schema/current.json` |
| Rust 統合 | `lib.rs` / **`wall_server.rs`（削除）** / `Cargo.toml` |
| Frontend | `App.tsx` / `components/Overlay.tsx` / `components/Dashboard.tsx` / `App.css` |
| 文書 | **ADR-015（新設）** / `intervention-design` / `physical-anchor` Skill / `repository-structure` / `agent-shared` / `CLAUDE.md` / `adr/README` |

## テスト戦略

| # | 検査 | 意図 |
|---|---|---|
| 1 | `cargo test --workspace` | ★ **461 = 465 − 削除した Wall テスト 4 本**。★ 数が合うことで「巻き込み削除」を検出する |
| 2 | ゴールデン replay | ★ **Replay-as-Truth**。特徴量が 1 bit も変わっていないこと |
| 3 | `emit_schema` → gse-dataset parity | ★ schema の破壊的変更が**両側で同期している**こと |
| 4 | `npx tsc --noEmit` | ★ **未使用シンボルの増加**を「消しすぎ」の検出器に使う |
| 5 | `npm run build` | ★ 実際にバンドルが作れること |

## ⚠️ リスクと受け方

| # | リスク | ★ 受け方 |
|---|---|---|
| 1 | ⚠️ **既存データが読めなくなる** | ★ **削除前に実測** —— フィクスチャ全数と gse-dataset の `metrics/` に `wall` が **1 件も無い**ことを確認した |
| 2 | ⚠️ **凍結中の G1 事前登録と表記がずれる** | ★ **書き換えない**（凍結の意味を守る）。⚠️ **ずれを記録として残す**（ADR-015 D5） |
| 3 | ⚠️★★★ **Physical Anchor が運搬路を失う** | ★ **ADR-015 D4 で「覆した」と明記**し、`physical-anchor` Skill の冒頭と description に警告を入れた |
| 4 | ⚠️ **Skill の description が誤起動を招く** | ★ **本文バナーだけでなく frontmatter も直した**（description は起動条件そのもの） |
| 5 | ⚠️ **テストの無断削除** | ★ 削除した 4 本を `decisions.md` D-5 に**名前と検査内容つきで列挙**した |
