# タスクリスト

## 準備
- [x] `docs/adr/ADR-021` / `ADR-017` / `expression-channel.md` §3.5 / §4.1 / §4.2 / §6 / §7.1 / §7.5 / §8 を読む
- [x] 必須 Skill を Read（`verify-before-claiming` / `citation-ssot` / `browser-verification` / `reproducibility-discipline`）
- [x] `docs/references.md` の次番号を実測（**[P268] / [V125]**）
- [x] ⚠️ 引き継ぎが指定した試視資材を実測 → **音のみと判明**（→ decisions 判断 1）

## 【第 1】OS 制約の一次調査（★ サブエージェント並列）
- [x] iOS ロック画面ウィジェット（更新頻度 / アニメーション / 色）
- [x] 背景実行と受信経路（★ ADR-017 D4 制約 1 との両立）
- [x] リプレイ・順序（S3）
- [x] ペアリング（S1）の iOS 側
- [x] iOS Live Activities / Dynamic Island / AOD / secure lock screen
- [x] Android のロック画面の面 / secure lock screen / `CompanionDeviceManager`（★ ライブ壁紙が唯一の面と判明）
- [x] 曝露量の外的妥当性（★ [P264] の分母を一次で確認・2024 年の [P268] を追加）
- [ ] ⚠️ macOS / Windows のファイアウォール on-demand 開閉（S5） — **未着手**（★ W-1 の実装時課題へ送る）

## 【第 2】層 A（視覚）試視ハーネス
- [x] `layerA.config.json`（写像 / 振動 / 出題内訳 / 禁止語の SSOT）
- [x] `player/layerA.html`（較正 → 1a → 1b → 教示 → 1b' → 遷移検知 → 結果 → 機械検算）
- [x] ⚠️★★★ 写像の封印（C7）／較正ゲート／マスク／catch／混同行列＋Wilson CI
- [x] invitation の 2 符号（A-7 の振動 ／ 静的な環の開口）
- [x] `scripts/selftest.py`（30 項目）＋ `--selfcheck`（★ 壊した config 6 種）
- [x] `run.sh` / `SEED` / `env.md` / `data.md` / `notes.md`（再現性規約の必須構成）
- [x] ★ 実機換算パネル（★ 1° がウィジェット幅の何割かを出す）
- [ ] ⚠️ **周辺視ブロック（A-4）** — ★ 未実装（config に枠だけ）

## テスト・検証
- [x] Python 機械検査 **30 PASS / 0 FAIL**（実測）
- [x] `--selfcheck` **6 / 6 の壊しを検出**（実測）
- [x] ⚠️★★★ **ブラウザで実測** → **欠陥 2 件を検出して修正**（→ notes.md §3）
- [x] ページ内機械検算 **12 PASS / 0 FAIL**（実測）
- [x] 4 状態の見た目をスクリーンショットで確認
- [ ] ⚠️★★★ **試視の実施** — ★ **研究者本人が回す。ここが本体**

## ドキュメント
- [x] `.steering/` の requirement / design / decisions / survey
- [x] `docs/references.md` に `[P268]` を append（★ DOI 重複を検算済み）
- [x] `docs/architecture/expression-channel.md` を追随（§3.5.1b / §3.5.2b 新設・§4.1 / §7.5 A12–A15 / §8）
- [x] `docs/adr/ADR-022` を起票（D1–D9）＋ `docs/adr/README.md` に索引と ADR-021 への改訂注記

## レビュー
- [ ] `code-reviewer` + `security-checker` を並列起動
- [x] `/cross-review`（★ `docs/adr docs/architecture` の 691 行に限定・exit 0）→ **指摘 5 件を全部反映**（→ decisions 判断 10）
- [x] `python scripts/check_citations.py` が **違反なし**（★ 2 回実行して確認）

## 完了処理
- [x] git commit（★ ハーネスと survey）
- [ ] `docs/` 追随のコミット
- [ ] 次セッション用の引き継ぎ
