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
- [x] ✅ 検証用パッケージを作り、**Google Drive に配置**（研究者がアップロード）
  - [x] Windows = 9 ファイル（平ら）／macOS = `G1-macOS.dmg` 1 ファイル。★ MCP で**サイズ照合**した
        （⚠️ **バイト同一性は未確認**）。`g1.mode` の **0 バイトが Drive 上に残存**
  - [x] ⚠️★ 一度 `.app` を**フォルダとして**上げてしまい（実行ビットが失われる形）、dmg に差し替えて解消
  - [x] ⚠️★ **私が確認せずに Dropbox へ上げた**（研究者の指示は Google Drive）。削除済み。
        ★ **指定と違う場所へ出す前に必ず確認する**
- [ ] ⚠️ ★ **W-1〜W-8**: 研究者が **P-1 の Windows 実施を進めた**（2026-08-06）が、
      ★ **結果はまだ受け取っていない**。⚠️ 見ていないものを「動いた」と書かない
- [ ] ⚠️ ★ **`tasklist` の実出力を受け取ってパーサを実測検証する**（W-4・★ 最優先）
- [ ] ⚠️★★ **Windows 上の `cargo test` が 1 度も走っていない** → `gh run rerun 31029374567`
- [ ] ⚠️ `origin` より **3 コミット先**。push が要る（★ 本セッションでは push が拒否された）

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

---

## 8. ★★ 2026-08-06（後半）— **Windows 実施の結果を受け取った**

`.steering/_handoff/next-session-prompt-g1-windows-results.md` の入口を消化した。

### 受け取ったもの / 受け取っていないもの

- [x] ★ **生 NDJSON 4 本**（`~/Downloads/P1_windows/`）
- [ ] ⚠️★★ **W-4 の `tasklist` 生出力** — **未受領**。
      → `g1::other_pids_from_tasklist` は**実機未検証のまま**（`g1.rs` のコメントは**まだ正しい**）
- [ ] ⚠️ W-1b / W-5 / W-6 の観察記録 — **未受領**（試していない / 見ていない）

### ★ 実施されたのは検証ではなく **P-1 本番 4 ブロック**だった

⚠️ ★ `windows-verification.md` は「W-1〜W-8 が緑にならないと回せない」と書いてあるが、
**検証を通さずに本番が回った**。★ これも事実として記録した（`notes.md §7-6`）。

### データ側から確かめたこと（★ 実測）

- [x] ★★ **5 分の自動終了が Windows 実機で効いた**: 4 本とも `session_start`→`session_end` = **301.0 秒**
      （mac 回は 11:37 / 4:04 / 7:14 / 9:57）。★ **G1 モードが作られた理由そのものが解決した**
- [x] `g1_mode:"marker"` が 4 本とも（`"env"` は 0 件 = 配布形の経路で立っている）
- [x] `probe_assignment` / `probe_triggered` / `realtime_label` が **4 本とも 0 行**（`§5.4-2`）。
      ★ 対照に `meta`(2) / `feat`(297〜300) を数えて**数え方が生きている**ことを確認済み
- [x] `§2.9` 適格性ゲート: keydown 1222 / 992 / 720 / 1259 → **最小でも閾値の 7.2 倍**
- [x] ★ **`ime_shadow` は Windows では出る**（70〜135 行/本）。mac は 0 = 構造的欠測
- [x] ⚠️ **W-7(3) は未達**: 1〜3 本目は `session_end` の後ろに `ime_state` が 4/2/3 行。
      ★ **R-9 で「直さない」と決めた非ゲート producer**。解析経路 (`read_block` / `scan_ndjson`) は
      これを読まないので**壊れない**ことを実測で確認した

### 転記

- [x] `windows-verification.md` の記録欄 W-1〜W-8（★ 「実測 / 未受領 / 試していない」を書き分け）
- [x] `notes.md` に **§7**（P-1 Windows 回・7-1〜7-6）
- [x] `blocks/PILOT-win.json` に `file` 4 件（★ 研究者確認: ブロック 1〜4 = 時刻順 = copy/HI/LO/copy）
- [x] `validate_blocks.py --dataset` で **PILOT-win は警告 0**（`produced_chars` 未記入の note のみ）
- [x] `bash run.sh` **GREEN (rc=0)** — ★ cargo ゲートも **2/2 + 2/2 本走らせて**確認

### ★ ここから出た新しいタスク

- [x] ⚠️★★ **提出 (`.age`) が 1 本も作られない**という設計の穴を特定
      → `.steering/20260806-g1-auto-submit-on-block-end/`（研究者判断 D-1/D-2/D-3 を記録済み）

### ✅★ 9. W-4 が埋まった（PR #88 を取り込んだあと・2026-08-06）

Windows 機側の Claude Code が `windows-measurements.md` として一次データを採取
（★ 指示は「情報収集だけ・コードは 1 行も直さない」→ 守られている）。

- [x] ★ 該当なし文言の実測: **`ja-JP` でも英語**・**`rc=0`**・**stdout**・`/FO CSV` でも CSV 化されない
- [x] ★ 該当ありの実測: `"gse-next.exe","17456","Console","3","47,644 K"`
- [x] ★ **生出力をそのまま `g1.rs` のテスト入力にした**（`tasklist_csv_extracts_pid_column` /
      `tasklist_ignores_no_task_message`）
- [x] ⚠️★★ **わざと壊して赤を実測した（2 通り）**
      - 区切りを素の `,` に → ⚠️ ★ **実測行だけでは赤にならなかった**（メモリ列のカンマは最終列で
        PID 列より後ろ）。→ ★ **テストが弱い**と分かったので、素のカンマ分割で 2 列目がずれる行
        （イメージ名にカンマ・★ **構成であって実測ではない**）を足して**赤を出せる**ようにした
      - 自分の PID を除外する `filter` を外す → **2 本赤**
- [x] ★ ⚠️ **現行実装に誤りは無かった**ので **パーサ本体は 1 行も変えていない**
      （変えたのは doc コメントとテストのみ。テスト 15 → 18 本）
- [x] ★★ **Windows 上の `cargo test` が初めて走った**: **294 passed / 0 failed / rc=0**
- [x] macOS 側の回帰: `cargo test --workspace` **297 passed / 0 failed**（+3 = 追加したテスト）／
      `replay_snapshot_goldens_byte_equal` 緑 ／ `emit_schema` **byte-equal** ／
      `npx tsc --noEmit` **rc=0** ／ clippy に `g1` 由来の指摘なし

### ⚠️★ 9-1. 文書の誤りを 2 件直した（★ どちらも実測で踏んだもの）

- [x] ★ **repo 直下の `cargo test --workspace` は空振りする**（`Cargo.toml` は `src-tauri/`）。
      ⚠️ ★ **macOS でも同じ**であることを実測 → **Windows 固有ではなく文書側の誤り**。
      → `docs/agent-shared.md` のテスト方針サマリに `cd src-tauri` / `--manifest-path` を明記
- [x] ⚠️ ★ **`~/.cargo/bin/cargo` が dangling shim で動かない環境がある**（このセッションの macOS）。
      `ls` ではリンクが見えるので気づきにくく、`run.sh` の cargo ゲートが黙って飛ぶ。
      → `docs/verification-runbook.md` に警告を追加

### ⚠️ まだ残っていること

- [ ] **W-3 の「検出できる」ことの実測** — ★ 2 個同時起動の実出力は未採取
- [ ] W-1b（対照）／ W-5（コンソール窓）／ W-6（`SystemRoot` 乗っ取り）
- [ ] macOS の Gatekeeper（Finder ダブルクリック 1 回）

### ✅★★ 10. W-1b / W-3 / W-6 も埋まった（PR #89 = `windows-measurements.md` M-5〜M-9）

- [x] **W-1b**: マーカー無し → `g1_mode` 無し。★ **同じ検証内でマーカー側では表示が出た**
      → 「常に G1 と出る実装」を Windows でも棄却
- [x] **W-3**: ⚠️★★ **同名 exe では `tasklist` が 2 行にならない**（2 個目は **14 ms** で自死・
      `tasklist` 1 回 ≒57 ms より短い。209 サンプルで 0 回）。★ 出た警告は
      `second-instance-blocked` 由来で **`other_instance_running()` の経路ではない**
- [x] ★★ **E-1（Windows 側が自分で足した陽性対照）**: プラグインを持たない同名プロセスで
      本当の 2 プロセスを作り、**偽 `tasklist.exe` を置いたまま**検査 → **警告が出た**。
      → ★ 「検査が走った」「System32 の本物が使われた」「実機 CSV をパースできた」が **1 回で 3 つ**
- [x] **W-6**: 痕跡ファイル無し = 乗っ取られず。★ ダミー単体の動作確認を**先に**やっている
- [x] ★ F-3 の非回帰: ブロックされた 2 個目の NDJSON は **0 本**（Windows でも効いている）
- [x] ★ **E-1 の 2 行出力をテストに入れ替えた**（構成した値 → 実測値）。
      ★ ⚠️ **文言は「日本語になりうる」ではなく実際に日本語になった**（同じ 1 台で
      `cmd.exe`=英語 / PowerShell 経由=日本語・条件未特定）→ ★ **文言列挙方針なら破綻していた**。
      性質（`","` で 2 列以上・2 列目が数値）を固定する方針が実測で正当化された
- [x] ★ 壊して赤を再実測（自分の PID 除外を外す → 2 本赤）／ `cargo test --workspace` **297 passed / 0 failed**

### ⚠️★★ 10-1. 依頼外で見つかった 2 件（**未追試・直していない**）

- [ ] ★ **× で閉じてもプロセスが残る**。原因はコードで確認済み: `lib.rs` が実行時に
      **`overlay` という 2 つ目の窓**を作り、Tauri は全窓が閉じたときに終了するため
      **overlay が残る限り死なない**（`CloseRequested`/`ExitRequested` の処理は無い）。
      ⚠️ 被験者が × で閉じて開き直すと「開いたのに何も起きない」になりうる（R-7 が警戒した形）
- [ ] ⚠️★★ **合成打鍵がフックに乗らなかった**（`SendKeys` / `keybd_event` とも）。★ 原因未特定。
      ★ フックは注入イベントを弾いていない（`LLKHF_INJECTED` 判定なし・grep 確認）。
      ★★ 同じ機の P-1 本番では実キーが 1440〜2518 打記録されている = **フック自体は壊れていない**。
      ⚠️ ★ ただし **実キーボードでの確認は 1 度もしていない**

### ⚠️ まだ残っていること（更新）

- [ ] **W-5（コンソール窓）** — ★ 目か録画でしか判定できない。**「光らなかった」とは書けない**
- [ ] ★ **本物の GSE が 2 個並んだ状態**（E-1 は代用プロセス）
- [ ] 新品端末での TCC / 初回起動 ／ macOS の Gatekeeper（Finder ダブルクリック）
