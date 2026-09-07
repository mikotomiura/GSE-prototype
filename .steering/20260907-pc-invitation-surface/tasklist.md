# タスクリスト — PS-Q7

## 準備
- [x] `.steering/_handoff/next-session-after-adr025.md` を読む（⚠️ 三次資料として扱う）
- [x] `docs/architecture/expression-channel.md` §3.5 / §4.1 / §4.2 / §6.2 / §7.1 / §7.5 / §8 を読む
- [x] `docs/adr/ADR-021` D6 / `ADR-025` 全文を読む
- [x] `verify-before-claiming` SKILL を読む
- [x] `intervention-design` SKILL を読む（⚠️ Wall 記述は無効・現行は Nudge のみ）
- [x] 一次で実測: `record_dismiss` の位置 / `invitation` の件数 / `intervention.rs` の閾値
- [x] `citation-ssot` SKILL を読む（★ append 直前に）
- [x] `literature-card` SKILL を読む（★ カード作成直前に）

## サーヴェイ（★ サブエージェント並列・メインは append のみ直列）
- [x] RQ-A 同一面の周辺表示の代償（★ Hodgetts & Jones 2014 の検算を含む）
- [x] RQ-B 集中時の周辺検出（★ Fukasawa & Shimomura 2021 の検算を含む）
- [x] RQ-C 提示タイミングと breakpoint
- [x] RQ-D 画面上の配置と静かな符号
- [x] RQ-E 再開後アウトカム（★ Brumby 2013 の検算を含む）
- [x] 敵対的 3 票検証（★ 対称フィルタ。有利な主張も同じ厳しさで）
- [x] `docs/references.md` へ append-only 登録（★ 次番号 P341 / V145 から）
- [x] `docs/literature/20260907-*.md` カード作成
- [x] `docs/literature/_index.md` へ 1 行追記

## 設計・裁定
- [x] `/reimagine` で PC 側要件表の **射程**を切る（★ 実装着手前）
- [x] PC 側要件表 `PC-1`〜`PC-n` を確定（★ 各行に一次。一次が無い行は「未決」と明記）
- [x] ⚠️ **ADR-025 D1 の「PC 側 UI」が E-11 に載っていない件**を裁く
- [x] ⚠️ **daily cap の文書 2–4 と実装 6 の食い違い**を要件として記録（★ 断定しない）
- [x] `ADR-026` を書く（★ Context / Decision / Alternatives / 却下リスト / Consequences / Migration）

## ドキュメント反映
- [x] `expression-channel.md` §3.6 新設（PC 側要件表）
- [x] `expression-channel.md` §7.5 に `A18`〜 追加
- [x] `expression-channel.md` §8 の `PS-Q7` 行を閉じる（★ 残る未決は別行）
- [x] `expression-channel.md` §6.2 に行番号の訂正注記
- [x] `docs/adr/README.md` の index に ADR-026
- [x] `docs/glossary.md` — ★ **新語は出なかったので触らない**（⚠️ `PC-n` は識別子であって用語ではない）

## 検査
- [x] `PYTHONUTF8=1 python scripts/check_citations.py` を「違反なし」まで
- [x] 本文の `[Pn]` / `[Vn]` が `references.md` に実在することを grep
- [x] `git status` で意図しない変更が無いこと（★ 実測: 変更は本タスクの 5 tracked + 3 untracked のみ。⚠️ 未踏スライド関連の既存変更は staged にしない）

## レビュー
- [x] `code-reviewer` ＋ `security-checker` を **並列**起動
- [x] HIGH 指摘を **本タスクで消化**（★ code-reviewer HIGH 3 件中 2 件が妥当・1 件は stale read。security-checker MEDIUM 1 + LOW 2 も消化）
- [ ] コミット
- [ ] `/cross-review` 第 1 巡（★ **コミット後・パス限定**）
- [ ] `/cross-review` 第 2 巡（★ 他文書との整合）

## 完了処理
- [ ] `design.md` 最終化
- [x] `decisions.md` 作成
- [ ] `/finish-task`
