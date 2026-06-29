# 設計判断

## D1: 案A (sidecar/subprocess) を採用、案B (in-process) を不採用
**判断**: アプリ内提出は同梱 `gse-submit` を子プロセスとして起動する案A。
**根拠**:
- `age` 暗号は `Cargo.toml` の `feature = "package"` で隔離され、`packaging` module は
  `lib.rs:6` で `#[cfg(feature = "package")]`。blind アプリ本体 (default) に `age` を載せない方針 (D3)。
- 案B（in-process で `package_session` 直呼び）は Windows アプリ本体に `age` を載せる必要があり、
  隔離方針撤回＋`windows-sys` OOM 懸念（Cargo.toml メモ）。
- 案A は `age` を別プロセス `gse-submit` に閉じたまま両 OS で動作。さらに、親アプリが exec した
  子プロセスは Gatekeeper に再評価されない（バンドル内バイナリは app の信頼を継承）ため、
  別 exe/別スクリプトの quarantine 発火を根絶できる＝主目的を満たす。
- 隔離維持の観点から案Aが事実上一意。

## D2: 提出コマンドは `package` feature 非依存（default ビルドに載せる）
**判断**: `submit_latest_session` は subprocess を起動するだけで `age` を link しない。
**根拠**: `age` を link すると Windows アプリ本体に載り D3 を破る。subprocess 起動のみなら
default ビルドに置け、Windows アプリ本体（非 package）にもコマンドが存在し、両 OS でボタンが機能する。
- 副作用: `packaging::is_valid_participant_id`（feature gate）を呼べないため、同一規則の
  `is_valid_submit_participant_id`（英数字・1..=16）を lib.rs に複製。テストで規則一致を担保。

## D3: 公開鍵は repo にリソース同梱（ユーザー確認済）
**判断**: `src-tauri/resources/pubkey.txt` を commit し `tauri.conf bundle.resources` で `.app`/exe に内包。
コマンドは `app.path().resource_dir()` から解決し `GSE_RECIPIENT` env で gse-submit に渡す。
**根拠**: 公開鍵は非機密で commit 安全。.app は /Applications へ移動し配布フォルダの loose な
pubkey.txt と分離するため、in-app 提出を自己完結させるにはバンドル内包が必要。
**安全側**: 実鍵未確定間は age1 行を含まない placeholder にし、`resolve_recipient` が
「no age1 found」で fail-loud（誤った宛先への暗号化＝復号不能データ生成を防ぐ）。**リリース前に実鍵必須**。

## D4: CI 変更は不要と判明（当初プランから縮小）
**判断**: 当初プランの「Windows nsis に gse-submit.exe 同梱」「mac 内部 bin 署名補強」は
**いずれも不要**と実装中に判明。
**根拠**:
- mac: CI `build-macos` は既に `--features package` で `tauri build` し、`.app/Contents/MacOS/` に
  `gse-submit` を自動同梱。`bundle.resources`（pubkey.txt）は既存ビルドコマンドが自動で honor する。
  内部 bin の個別署名は機能上不要（exec'd 子プロセスは Gatekeeper 非再評価）。
- Windows: 被験者は**ポータブル版**を使い、配布フォルダに `gse-next.exe` / `gse-submit.exe` /
  `pubkey.txt` が **co-located**（参加者ガイド §2-B・§4）。`current_exe().parent()` 隣で解決できるため
  バンドル変更不要。NSIS インストーラ経路は対象外（fail-loud で「ツールが見つかりません」）。
- 結果として externalBin の mac 二重コピー衝突リスクを完全回避。低リスク。

## D5: fail-loud
**判断**: 提出失敗は frontend で赤字インライン表示（既存 record 失敗パターン同様）、リトライ可能。
backend は非 0 exit 時に stderr（無ければ stdout）を `Err` で返す。静かに失わない。
