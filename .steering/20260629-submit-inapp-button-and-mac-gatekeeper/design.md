# 設計

## 実装アプローチ

**案A (sidecar/subprocess) を採用**。提出をアプリ内ボタン化し、既に Gatekeeper 承認済みの
GSE アプリから `gse-submit` を子プロセスとして `exec` する。親アプリが exec した子プロセスは
Gatekeeper に再評価されない（バンドル内バイナリは app の信頼を継承）ため、別 exe/別スクリプトの
quarantine 発火を根絶する。

### なぜ案A（案B 不採用の理由）
`age` 暗号は `Cargo.toml` の `feature = "package"` で隔離され、`packaging` module は
`lib.rs:6` で `#[cfg(feature = "package")]`。macOS リリースは既に `--features package` ビルドで
`age`＋`gse-submit` が `.app/Contents/MacOS/` に同梱済み。一方 Windows nsis は `package` 非使用。
- 案B（in-process で `package_session` 直呼び）は Windows アプリ本体に `age` を載せる＝隔離方針撤回
  ＋ `windows-sys` OOM 懸念。
- 案A は `age` を別プロセス `gse-submit` に閉じたまま両 OS で動作。隔離維持の観点から事実上一意。

提出ロジックは `packaging.rs`（匿名化＋age 暗号の SSOT）を `gse-submit` 経由で再利用し、重複実装しない。

## 変更対象

### 修正するファイル
- `src-tauri/src/lib.rs` — 新 Tauri コマンド `submit_latest_session` ＋ Serialize DTO `SubmitOutcome`
  ＋ `invoke_handler` 登録。`age` を link しない（subprocess 起動のみ）ので default ビルドに載る。
- `src/components/Dashboard.tsx` — 提出セクション（参加者 ID 入力＋「提出する」ボタン＋fail-loud 結果表示）。
- `src-tauri/tauri.conf.json` — `bundle.resources` に pubkey.txt（mac/win）／win 時 gse-submit.exe。
- `.github/workflows/ci.yml` — Windows nsis に gse-submit.exe 同梱、mac 内部 bin 署名補強。
- `scripts/submit/提出する_mac.command` — 未コミットの xattr 修正を明示 pathspec で commit（内容変更なし）。
- `docs/participant-setup-guide.md` — mac 初回許可手順（GUI／Terminal `xattr -dr`）を追記/整理。

### 新規作成するファイル
- `src-tauri/resources/pubkey.txt` — 研究者 age 公開鍵（非機密・commit 安全）。未確定間はコメント行のみの
  placeholder にして `resolve_recipient` が fail-loud（誤鍵暗号化防止）。リリース前に実鍵必須。

### 削除するファイル
- なし

## 影響範囲
- 提出経路: 既存 `gse-submit` CLI / Windows 手動提出は非回帰（同じ binary を別経路で起動するだけ）。
- ビルド: Windows nsis に提出ツールビルド＋同梱ステップが増える。mac は既存同梱を流用。
- 盲検: ボタンは被験者ビルドで表示（debug 機能ではない）。介入/ゲートのロジックは不変。

## 既存パターンとの整合性
- `std::process::Command` での外部プロセス起動は `submit.rs:79 reveal_in_file_manager` に前例。
- Tauri コマンド＋Serialize DTO＋`invoke_handler` 登録は `lib.rs` の既存 30+ コマンドに倣う。
- フロントの fail-loud インライン error は既存の record 失敗表示パターンに合わせる。`any` 禁止。
- `is_valid_participant_id` は `logger.rs:1249`（非 feature-gate）を再利用。

## テスト戦略
- 単体テスト: コマンドの participant_id 検証・binary/recipient パス解決・stdout からの `.age` パス抽出を
  純関数に切り出して Rust ユニットテスト（spawn 自体は OS 依存なので分離）。
- 統合テスト: `cargo build`（mac/win cfg）＋ `cargo test --workspace`＋`cargo build --features package
  --bin gse-submit`＋`npx tsc --noEmit`＋`npm run build`。
- E2E: mac 実機 smoke（ダウンロード→承認→アプリ内提出→`.age` 生成・追加 Gatekeeper 無し→`gse-unpack` 復号）。

## ロールバック計画
- ボタン追加は加算的。問題時はフロントのセクションを隠す or コマンド未登録に戻すだけで既存の
  手動提出経路（ランチャ／別 exe）に縮退。CI 変更も revert 可能。タグ再リリースは旧 artifact を再アップで戻せる。
