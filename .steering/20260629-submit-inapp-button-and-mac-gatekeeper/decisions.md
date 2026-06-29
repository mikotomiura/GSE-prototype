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

## D4: CI のバンドル変更は不要、ただし安全ゲート/署名を追加（cross-review 反映で改訂）
**判断**: gse-submit を新たにバンドルする変更（externalBin 等）は **不要**。ただし cross-review
（Codex+Claude 一致 HIGH）を受け、**リリース安全ゲートとネスト署名・存在アサート**を `ci.yml` に追加した。
**根拠（バンドル不要）**:
- mac: CI `build-macos` は既に `--features package` で `tauri build` し、`.app/Contents/MacOS/` に
  `gse-submit` を自動同梱。`bundle.resources`（pubkey.txt）は既存ビルドコマンドが自動で honor する。
- Windows: 被験者は**ポータブル版**を使い、配布フォルダに `gse-next.exe` / `gse-submit.exe` /
  `pubkey.txt` が **co-located**（参加者ガイド §2-B・§4）。`current_exe().parent()` 隣で解決できるため
  バンドル変更不要。NSIS インストーラ経路は対象外（fail-loud で「ツールが見つかりません」）。
  → externalBin の mac 二重コピー衝突リスクを完全回避。
**追加した CI 変更（cross-review HIGH [1][2] 対応）**:
- `build-macos` に **pubkey リリースゲート**: `resources/pubkey.txt` に `age1` 行が無ければ tag ビルドを
  fail（プレースホルダのままリリースして全参加者が提出不能になるのを機械的に防ぐ）。dev/test は通らない。
- `build-macos` の再署名ステップで **ネストヘルパ bin（gse-submit/gse-package/gse-unpack）を個別 ad-hoc 署名**
  ＋ **`.app` 内に gse-submit と pubkey.txt が存在することをアサート**（欠落でリリース停止）。
  ※ 現行リリースも未署名ネスト bin を同梱済で実害報告はないが、署名整合・AMFI 対策の belt-and-suspenders。
- Windows の pubkey は**配布時に loose 配置**（make-participant-zip / 手動）で repo/CI 管理外のため CI ゲート対象外。

## D6: 失敗詳細のホームパス伏字（cross-review [3] / data-privacy 対応）
**判断**: `run_submit_blocking` が UI へ返す失敗詳細は `redact_home_path` で `$HOME`/`$USERPROFILE` を
`~` に置換する。**根拠**: gse-submit の失敗メッセージに `/Users/<実名>/...` が混入し得る。被験者が
エラー画面をスクショ共有しても OS ユーザー名（実名）が漏れないようにする。ログには exit code のみ。

## D7: フロント即時バリデーション（cross-review [4] / UX）
**判断**: `handleSubmit` で `/^[a-zA-Z0-9]{1,16}$/` を即時チェックし、不正 ID で IPC 往復しない。
最終防線は backend `participant_id::is_valid_participant_id`（同一規則・SSOT）。

## D8: 配布最小化 — researcher 専用 CLI を mac .app から除去（ユーザー選択 B・2026-06-29）
**判断**: CI `build-macos` の再署名前に `gse-package`/`gse-unpack` を `.app/Contents/MacOS/` から `rm`。
**根拠**: macOS バンドラは `--features package` ビルドの全 `[[bin]]` を自動コピーするが、被験者配布物に
研究者専用 CLI（手動提出・**復号**）は不要。`gse-unpack` は秘密鍵が無ければ無力で機密漏れではないが
（鍵は配布しない）、配布物を最小化する。Release のツール資産は `target/release/` 由来の別経路なので
研究者は引き続き取得可。strip 後に署名し署名整合を保つ。残存検知アサートも追加。
**配布の含意（確定）**: mac=`.dmg` 1つで自己完結。Windows=ポータブルゆえ単一化不可で
`gse-next.exe`+`gse-submit.exe`+`pubkey.txt` の co-located フォルダが必須（`.bat`/`gse-package.exe` は任意、
`gse-unpack.exe` は被験者に渡さない）。

## D5: fail-loud
**判断**: 提出失敗は frontend で赤字インライン表示（既存 record 失敗パターン同様）、リトライ可能。
backend は非 0 exit 時に stderr（無ければ stdout）を `Err` で返す。静かに失わない。
