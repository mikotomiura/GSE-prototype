# tasklist — 文献接地 1 ラウンド

## 順序 0: 起票 11（ESM 監査 criterion）の研究者判断

- [x] 起票 11 を一次で読む（`.steering/20260911-.../blockers.md:408-`）
- [x] `security-checker` の 4 点を読む（★ 規約の穴 / 第三者同意 / `capabilities` 粒度 / 出したら消せない）
- [x] ⚠️★★★ **研究者へ 2 択（＋縮約案）を提示して判断を取る**
      → ★★★ **2026-09-13 決定 = 「(a) 6 択フルを取る」**
- [x] 判断と **残作業 ①〜④** を `.steering/20260911-.../blockers.md` へ落とす
- [ ] ★ 引き継ぎ／全体順序（§6 の 1b）へ反映する（⚠️ **レビュー結果を織り込んでから新引き継ぎを書く**）

## 順序 1: 文献接地（起票 4 / 起票 5）

### 準備

- [x] `/literature-review` を起動し `citation-ssot` を読む
- [x] ★ 次番号を **実測**（`[P357]` / `[V146]`・2026-09-13）
- [x] ⚠️ `.idea/survey` を **全文 551 行**読む（★ 前セッションの失敗 1 を繰り返さない）
- [x] ★ §13 の 33 件を references.md と機械突合 → **21 件未登録**を確認

### 探索（★ サブエージェント並列）

- [x] 隊 A: Tabarsi 2022 ／ Zou & Godfrey 2012
- [x] 隊 B: Conijn 2022 ／ Willett & Singer 1995 ／ Fine & Gray 1999
- [x] 隊 C: Zou & Carl 2026 ＋ ENJA15/RUC17 ／ Nahum-Shani 2018
- [x] ★ 3 隊の報告を回収

### 判定と登録

- [x] claim 抽出（★ 「GSE の判断を動かしうる主張」だけ）
- [x] 敵対的検証 3 票（⚠️ **対称フィルタ**・GSE に有利な主張も同じ厳しさで）
- [x] ★ 起票 5 の裁定（`.idea §3.1` ⇄ `[P273]` の**どちらが一次確認済みか**）
- [x] `docs/references.md` へ append（⚠️ **メインが直列**・`[P357]` / `[V146]` から）
- [x] `docs/literature/20260913-<slug>.md` を生成（★ 落合 6 項目 ＋ 否決リスト）
- [x] `docs/literature/_index.md` に 1 行追記

## 順序 2: ADR-030 への接地

- [x] `Context-3b` へ inline `[Pn]` を追記（⚠️ **D1〜D11 は変えない**）
- [x] ★ D2 の反復エピソード規則に **Willett & Singer (1995)** を張る（★ 取得できたら）
- [x] `docs/research-positioning.md` への還元（★ または「不要」の明示）

## 検算

- [x] `PYTHONUTF8=1 python scripts/check_citations.py` を **「違反なし」まで**繰り返す
- [x] ⚠️ 手 grep 併用（★ `check_doc_lexicon.py` は ADR を検査していない）
- [x] ★ 重複 key の手動突合（⚠️ **持ち越しの一次取得も対象に含める**）

## 完了処理

- [x] 起票 4 / 起票 5 を `.steering/20260913-mhd-inference-ssot/blockers.md` で解決へ
- [x] `decisions.md` に本ラウンドの判断を記録
- [x] ⚠️★★★ **即コミット**（★ 複数ラウンドが同居すると `git add -p` で分離できない）
- [ ] `code-reviewer` ＋ `security-checker` を並列 → `/cross-review`（2 巡・パス限定）
