# タスクリスト

## 準備
- [x] requirement.md / 関連 Skill（data-privacy・architecture-rules）を読む
- [x] 提出系コード（packaging.rs / submit.rs / lib.rs / tauri.conf / ci.yml / launcher）を調査
- [x] A/B 設計判断 → 案A 採用（design.md）

## タスクB（暫定・即効）
- [x] `docs/participant-setup-guide.md` に mac 初回許可手順（GUI／Terminal）を追記 + 提出をアプリ内ボタン優先に再構成
- [ ] `提出する_mac.command` の xattr 修正を明示 pathspec で commit（finish-task で実施）

## タスクA（恒久・主目的）
- [x] A-1 backend: `submit_latest_session` コマンド＋ `SubmitOutcome` DTO＋invoke_handler 登録
- [x] A-1 純関数（id 検証・パス解決・stdout 解析）の Rust ユニットテスト（submit_command_tests 3 件）
- [x] A-3 bundle: `src-tauri/resources/pubkey.txt`（fail-loud placeholder）＋ `tauri.conf bundle.resources`
- [x] A-2 frontend: Dashboard 提出セクション（ID 入力＋ボタン＋fail-loud 表示）＋ App.css
- [x] A-4 CI: バンドル変更は不要（mac 自動同梱・Windows co-located）。cross-review を受け安全ゲート追加=
      pubkey リリースゲート＋ネストbin署名＋.app 内容アサート（build-macos）→ decisions.md D4 参照

## テスト
- [x] `cargo check`（default 本体＋context）/ `cargo check --features package --bin gse-submit`（隔離非回帰）
- [x] `cargo test --workspace`（lib 245 件＋bins 全 pass。submit_command_tests 含む）
- [x] `npx tsc --noEmit`（pass）＋ `npm run build`（vite pass）
- [x] CLI smoke: env-only(GSE_PARTICIPANT_ID/GSE_RECIPIENT, no TTY)→.age 生成→gse-unpack 復号→匿名化確認
- [ ] mac 実機 smoke（ダウンロード→アプリ承認→アプリ内提出→追加 Gatekeeper 無し）= ユーザー実施

## レビュー
- [x] code-reviewer ＋ security-checker（data-privacy 重点）並列起動 → HIGH/MEDIUM 対応済
- [x] `/cross-review`（Codex gpt-5.5・縮退なし）→ 統合レポート取得
- [x] HIGH 指摘対応: [1] CI で .app 内容アサート＋ネスト署名、[2] pubkey リリースゲート、
      [3] 失敗詳細のホームパス伏字、[4] フロント即時バリデーション

## 完了処理
- [ ] design.md の最終化・decisions.md（A/B 判断）
- [ ] git commit（type/scope）
- [ ] v0.1.21 同 ver 再リリース
- [ ] メモリ更新（build-ci-and-pilot-distribution に mac アプリ内提出を追記）
