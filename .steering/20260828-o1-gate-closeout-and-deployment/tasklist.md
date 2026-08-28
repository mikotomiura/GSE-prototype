# タスクリスト

## 準備
- [x] 引き継ぎ `.steering/_handoff/next-session-prompt-o1-gate-closeout-and-deployment.md` を読む
- [x] ⚠️ **文書ではなく機械で状態を確かめる**: `check-o1-release-readiness.sh`（通過 12 / 未達 2）
- [x] ★ 一次資料を読む: `liveness.rs` / `lib.rs:4081` / `RecordingControls.tsx:523` /
      `GSE_O1_Submit.gs` / `GSE_O1_Form_Builder.gs` / `ci.yml:204` / `Cargo.toml` features
- [x] ★ 研究者判断を取る（liveness / フォーム作成の範囲 / 配布 URL / A-2 のゲート）

## 実装
- [x] **E-1** `RecordingControls.tsx` の削除後の案内に `o1Mode && paused` の分岐を足す
- [x] **A-1** `liveness::tray_starved` を新設 ＋ `lib.rs` に `O1_LIVENESS_TRAY_AFTER_MS` を配線
- [x] **A-2** 実測記録票 `o1-upload-timeout-measurement.md` を新設
- [x] **A-2** ゲートの検査を「実測の記録 ＋ コードの修正」の両方に差し替え
- [x] ★ ゲートの liveness 検査を「定数がある」→「**トレイに配線されている**」へ強化
- [x] **F-12** `ci.yml` の `cargo test` に `--features package` を足す
- [x] **E-4** `launch-o1-windows.bat` に BOM を追加（⚠️ CRLF は `.gitattributes` が既に担保。判断 4）
- [x] **E-5** `--selftest-dump` の持ち物を `MANIFEST` 配列に単一化
- [ ] ⚠️ **`reconcile.rs` の timeout の値** —— ★ **実測が先**（B-1 に依存・意図的に未着手）

## テスト
- [x] `cd src-tauri && cargo test --features package --workspace` → **562 passed / 0 failed**
- [x] ★ liveness の新規 5 テストが実際に走っていることを名前で確認
- [x] ★ F-12 を**実測で裏づけ**: `--features package` なし = 528 件・`reconcile::` **0 件**
- [x] `npx tsc --noEmit` → 緑
- [x] `check-o1-release-readiness.sh --selftest` → **27 / 27**（22 から +5）
- [x] `make-common-app-zip.sh --selftest` → **16 / 16**（14 から +2）
- [x] ⚠️ ★ **新しい検査を壊して赤になることを確かめた**（BOM 除去 / 二重管理へ戻す）
- [ ] ⚠️ **B-4 削除 UI の実機クリック** —— ★ 研究者が操作する（E-1 はこの経路で踏める）

## レビュー
- [x] code-reviewer ＋ security-checker（並列）→ **HIGH 4 件 / MEDIUM 8 件 / LOW 8 件**
- [x] ⚠️ **HIGH は全部直した**（下記）。★ どれも「壊して赤になる」ことを実測で確かめた
  - [x] **CRLF 検査が空回りしていた** —— `tr -cd '\\r'` は集合を「バックスラッシュと r」と読むので
        ⚠️ `rem` 行の `r` を数え、★ **LF only でも必ず通っていた**（実測で確認）。
        → バックスラッシュ 1 個に直し、⚠️ **陽性対照**（CR/BOM を剥いだ複製で落ちる）を追加
  - [x] **`o1Mode && !paused` が G1 文言に落ちる** —— ★ ローテート失敗 / 5 秒超過で到達する。
        ⚠️ そこで「すぐ止める」を出すと**ローテート経路そのものが消える**。→ `o1Mode` を外側へ
  - [x] **`grep -vc` が `set -euo pipefail` で無言中断** —— ★ 集計行を出さずに終了していた（実測）
  - [x] **`Form_O1/` が `.gitignore` に無い** —— ⚠️ `.gitignore` 自身が「一時 public にする運用がある」
        「履歴からは消せない」と書いている。→ `Form_O1/` を追加し、⚠️ **runbook から生 ID を外した**
- [x] MEDIUM の対応: 生の判定 `HOOK_NOT_DELIVERING`（判断 5）／`tray_starved` →
      **`participant_visible_starved`** へ改名し doc を実体に合わせる／`reconcile.rs` の
      アンカー喪失を赤にする／`recording_health` を含む**つないだ形**の回帰テストを追加
- [x] LOW の対応: 必須欄に「実効スループット」を追加・値に数字を要求／
      `MANIFEST` の説明を実体に合わせる／テスト件数の記述を実測に合わせる
- [x] `/cross-review`（Codex・パス限定）→ **4 件**。★ 2 件を採用して直し、1 件を起票、1 件は**不成立**
  - [x] ★ `participant_visible_starved` の `Some` 分岐が `health` を使っていない →
        **`Down` の部分集合**であることを式で固定（⚠️ 閾値を逆転させる回帰テストつき）
  - [x] ★ BOM+CRLF 検査が「CR が 1 個でもあれば通る」→ **全行 CRLF**（CR 数 == LF 数）に変更。
        ⚠️ 「1 行だけ LF」の陽性対照を追加
  - [x] ★ 記録票の**値の妥当性**を見ていない → **T-14 として起票**（⚠️ 自由記述の数値解析は壊れやすい）
  - [x] ⚠️ 「`cargo build` に feature が無いので package ビルドが未検証」→ **不成立**。
        ★ 一次資料で確認: `required-features = ["package"]` の 3 bin
        （`gse-package` / `gse-unpack` / `gse-submit`）は `cargo test --features package` で
        **実際にコンパイルされている**（テスト出力に 3 本とも出る）

## ドキュメント
- [x] `deployment-runbook.md`（★ 研究者の手作業。Drive ID を差し込んだ）
- [x] `open-issues.md`（★ 未解決を 1 か所に集約）
- [x] `decisions.md`（判断 1〜4）

## 完了処理
- [ ] git commit
- [ ] ★ 完了報告（⚠️ 外界に触った操作の列挙 / 一次資料と伝聞の区別 / 残ったもの）
