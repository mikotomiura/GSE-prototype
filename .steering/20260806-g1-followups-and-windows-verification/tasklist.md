# タスクリスト — G1 follow-up / Windows 検証の準備 / 配布手順の確定

## 0. 準備
- [x] `_handoff/next-session-prompt-g1-followups.md` を読む
- [x] `20260805-g1-app-mode-and-log-rotation/` の `decisions.md` R-7 / R-8 / R-9 と
      `tasklist.md` §9 / §10 を読む（★ 「なぜ今やらないか」まで）
- [x] 研究者に 2 点確認（① Windows は CI ビルドから ／ ② 署名は案 A で確定）

## 1. follow-up（コード）
- [x] **F-2**: `start_session` の `log.lock()` を送信の間だけに縮める
- [x] **F-1**: 二重起動の検査をブロック開始ごとにも走らせる
  - [x] ★ **先に測った**: `other_instance_running()` = **18〜28 ms**（macOS・5 回）
        ⚠️ Windows の `tasklist` は**未計測**
  - [x] 測定用テストは計測後に削除した
  - [x] ★ 応答時間に載せない（別スレッド）。`setup()` と共用の
        `spawn_duplicate_instance_check()` に集約
- [x] **F-3**: 空 NDJSON — ログを開くのを `.setup()` へ移す
  - [x] ★ 一次資料で順序を確認（`tauri` 2.10.2 `app.rs` / plugin 2.4.3 `platform_impl`）
  - [x] `logger::LogChannel`（channel だけ先に作る）を新設。`SessionLogger::start` は薄いラッパ
  - [x] ★ `.manage()` の順序は**変えていない**（共有 Arc を上書きする形にした）
  - [x] ⚠️ 提出側の `has_any_data_row` は**残した**（置き換えではなく二重化）

## 2. 検査（★ 足したらその場で壊す）
- [x] `logger.rs` に単体 2 本（`new()` は作らない／先に送った行を落とさない）
- [x] `run.sh §5.1` に配線の検査（grep ＋ `cargo test` 実走 ／ cargo 不在は `note` で明示）
- [x] 自己レビューで 1 本追加: ★ **`meta` が必ず 1 行目**（F-3 でバッファ経路ができたため
      新しく必要になった不変条件。`validate_blocks.py §5.4-6` / `analyze.py` が 1 行目を読む）
- [x] ★★ **5 通り壊して赤を実測**（`decisions.md` D-4 に表で記録）
      ⚠️ うち 1 つは**想定と違う場所で落ちた**。そのまま記録した

## 3. 回帰
- [x] `cargo test --workspace` = **294 / rc=0**（lib 271 = 従来 269 ＋ 新規 2）
- [x] `cargo test --workspace --features package` = **279 / rc=0**
- [x] golden replay **4 本**（minimal / category_coverage / phase1_ime_heavy / deep_silence）rc=0
- [x] `emit_schema` の出力が `schema/current.json` と **byte-equal**
- [x] `npx tsc --noEmit` = rc=0
- [x] `cargo clippy --all-targets` = ★ **新規の警告ゼロ**（残る警告は HEAD にもある既存分）
- [x] `analyze.py --selftest` / `validate_blocks.py --selftest` / `build_task_pages.py --selftest`
      / `validate_materials.py --strict` = すべて rc=0
- [x] ⚠️ `cargo test | tail` を使わない（exit code を直接読む）

## 4. Windows（★ **実施していない**）
- [x] `windows-verification.md` を作成（W-1〜W-8・「操作 → 何を見る → 記録欄」）
- [x] CI に `workflow_dispatch` を追加（★ タグを切らずに `build-windows` だけ走らせる）
- [x] `actionlint` = 新規指摘ゼロ（既存 2 件は HEAD にも出る）
- [x] ✅ ★ **手動発火を実測した**（2026-08-06・run `31029380118`）
  - [x] ⚠️ ★ **デフォルトブランチに `workflow_dispatch` が無いと発火できない**ことが確定
        → `ci.yml` だけの PR **#86** を `main` へ merge（`fa21812`・アプリのコードは 0 行）
  - [x] ★ 発火後は **`build-windows` だけ**が走り、他 3 ジョブは skipped（`if` 条件どおり）
  - [x] ★ pull_request では `build-windows` が skipped（通常の PR を重くしない）
  - [x] ✅ **ビルド成功**（run `31029380118`）。artifact を落として `file` で確認:
        `gse-next.exe` = `PE32+ (GUI) x86-64` 10,474,496 B ／ `gse-submit.exe` 968,192 B ／
        `gse-unpack.exe` 736,768 B（★ 研究者専用・被験者に配らない）。⚠️ 保持 7 日（`2026-08-12` 失効）
- [ ] ⚠️★ **私が push 由来の `check` を巻き添えで cancel した**（`concurrency` が同一グループ）。
      ★ **Windows 上の `cargo test` は 1 度も走っていない** → `gh run rerun 31029374567` が要る
- [ ] ⚠️ ★ **W-1〜W-8 は 1 項目も実施していない**（Windows 実機が要る）
- [ ] ⚠️ ★ **`tasklist` の実出力を受け取ってパーサを実測検証する**（W-4）

## 5. 配布（署名・公証）
- [x] ★ 研究者判断で **案 A（現状維持）に確定** → `decisions.md` D-1
- [x] `protocol.md §1.1` に「初回だけ必要な手順」（`xattr -dr` ／ SmartScreen ／
      ★ **G1-app から出さない** ／ ⚠️ 再署名は入れない）
- [x] `protocol.md §4b.2` に手順 0（当日より前に開けることを確かめる）
- [x] `notes.md §4` を更新（★ 案 B / C の副次効果を**取らない**と決めたことも書いた）

## 6. 文書
- [x] `notes.md` に §5（本セッションの follow-up 3 件）
- [x] `protocol.md §8` に `windows-verification.md` へのリンク
- [x] `.steering/20260806-.../` requirement / design / decisions / tasklist
- [x] ★ `docs/architecture.md` は前セッションのコミット `d63e590` で更新済み（本タスクで再確認）

## 7. 完了処理
- [x] git commit（★ 3 コミットに分けた: fix(logger) / chore(ci) / docs(experiments)）
- [x] `run.sh` が **GREEN (rc=0)** に戻ることをコミット後に確認
- [x] `/cross-review` — ★ ゲート全通過。⚠️ **予算は日付ロールオーバーで 0 から**だった
      （引き継ぎメモの 178,666 は前日分。★ **メモの数字を根拠にせずその場で計算した**）。
      Codex 実消費 **26,803** トークン
- [x] ★ **両者一致 HIGH = 0 件**
- [x] ★ MEDIUM 1 件を採用: ⚠️ **`cargo test --lib <filter>` は 0 件マッチでも rc=0**。
      → `run_cargo_filter` で本数まで数える。⚠️ ★ **既存の kill switch 検査にも同じ穴があった**ので
      両方直した（`§5.4-2` を守るゲートが黙って緑になる型）。★ 2 通り壊して赤を実測（D-4 #6/#7）
- [x] LOW 1 件を採用（`SessionLogger` 即 drop の前提を doc に明記）
- [x] ⚠️ LOW 1 件は**採用しない**と決めて理由を記録（IME の `try_send` warn）
- [x] ★ 副作用を隠さず記録: **`meta.session_start` が `.setup()` 到達後にずれる**
      （G1 でないときも変わる = 「1 バイトも変えない」原則の 2 つ目の例外）
- [ ] 修正ぶんの追加コミット
