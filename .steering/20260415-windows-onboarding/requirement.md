# Windows Onboarding — 実機での Phase 1 受け入れ検証と GT 収集ワークフロー確立

## 背景

2026-04-15 時点で Phase 1 実装 (GT ラベリング + metrics 算出 + gse-dataset 連携) は
macOS 側で完成・検証済み。しかし Windows 側は以下が未検証:

- `cargo build --target x86_64-pc-windows-msvc` は CI では緑化しているが、実機
  ビルド + 実機起動は未実施
- グローバルホットキー `Ctrl+Shift+Alt+F/I/S` の Windows `RegisterHotKey` 経由での
  実動作
- Windows 固有のセッション NDJSON フォーマット整合性 (`hmm_version` / `feat.obs`
  境界、CRLF 問題)
- gse-dataset への `metrics/P000/windows/` パス経由のデータ蓄積
- macOS 側との集約 (`aggregate_metrics.py`) での両 OS データ混在動作

Windows 実機を取得した時点で、本ドキュメントを Claude Code Windows に渡すことで
**追加実装ゼロ** で受け入れ検証 + 初回データ収集が完了できる状態を目指す。

## ゴール

1. Windows 実機での Phase 1 全機能の初回スモーク検証 (1 セッション以上)
2. gse-dataset の `metrics/P000/windows/` に初回 metrics JSON を commit + push
3. macOS 側での pull 後、`aggregate_metrics.py` が両 OS のデータを統合集計することの確認
4. 両 OS のセッションが schema v2 (`schema/current.json`) で等しく validate 成功
5. 発見した Windows 固有ブロッカーを `.steering/20260415-windows-onboarding/blockers.md` に記録

## スコープ

### 含むもの
- Windows 環境構築 (Visual Studio Build Tools C++ workload、Node.js 22+、Rust stable、Git、SSH 認証)
- 両 repo の初回 clone
- `npm install && cargo tauri dev` で Dashboard 起動
- 実機でのラベリング操作 (Ctrl+Shift+Alt+F/I/S を各 1-2 回)
- セッション終了後の NDJSON 抽出 + `gse-replay --metrics --json` 実行
- `gse-dataset/metrics/P000/windows/` への配置 + commit + push
- 定常運用のためのショートカットスクリプト (PowerShell) の雛形
- Windows 固有ブロッカーの発見と記録

### 含まないもの
- Windows 実機環境そのものの用意 (物理 PC / VM / レンタル)
- Tauri bundle (installer) の作成 (既存 CI の build-windows ジョブがタグ push 時に担当)
- Phase 2 以降の Synthetic Friction 再設計・IME Shadow Features 等の新機能
- 外部被験者 P001+ のセットアップ (IRB 取得まで)

## 受け入れ条件

### 環境構築
- [ ] Rust stable (`rustc --version` が表示される)
- [ ] Node.js 22+ (`node --version`)
- [ ] Visual Studio Build Tools (C++ workload 導入済み、`link.exe` が PATH にある)
- [ ] Git 2.40+ + SSH 認証 (`ssh -T git@github.com` が成功)
- [ ] `git config --global core.autocrlf input` 設定済み (CRLF トラブル予防)

### 両 repo の clone
- [ ] `C:\Users\<me>\repos\GSE-prototype\` が存在
- [ ] `C:\Users\<me>\repos\gse-dataset\` が存在
- [ ] 両 repo の `main` ブランチが最新 (pull 済み)

### ビルド
- [ ] `cd GSE-prototype\src-tauri && cargo build --target x86_64-pc-windows-msvc` が warning 0 で完了
- [ ] `cargo test --workspace --target x86_64-pc-windows-msvc` 全 PASS (51 tests)
- [ ] `cargo run --bin gse-replay --target x86_64-pc-windows-msvc -- tests\fixtures\minimal.ndjson --snapshot tests\snapshots\minimal.json` が `OK: 15 snapshots match`
- [ ] `cargo run --bin emit_schema --target x86_64-pc-windows-msvc > tmp\emitted.json` + `fc schema\current.json tmp\emitted.json` で drift 0
- [ ] `cd GSE-prototype && npm install && npx tsc --noEmit` エラー 0

### 実機検証 (1 セッション以上)
- [ ] `npm run tauri dev` で Dashboard が起動し、Counter widget が `GT: Flow 0 / Inc 0 / Stuck 0 Ctrl+Shift+Alt F/I/S` を表示
- [ ] `Ctrl+Shift+Alt+F` 押下で Flow counter が 1 → 2s 以内再押下でデバウンス (Flow のまま) → 3s 後押下で 2
- [ ] `Ctrl+Shift+Alt+I` と `Ctrl+Shift+Alt+S` で Inc / Stuck も各 1 回以上
- [ ] セッション終了で `%USERPROFILE%\Documents\GSE-sessions\gse_*.ndjson` に 1 ファイル生成
- [ ] `python scripts/validate_schema.py <session>` が OK

### gse-dataset 連携
- [ ] `cargo run --bin gse-replay -- <session> --metrics --json > gse-dataset\metrics\P000\windows\<name>.metrics.json`
- [ ] `git add metrics/P000/windows/ && git commit -m "data(P000-windows): first session YYYY-MM-DD" && git push`
- [ ] macOS 側で `git pull` 後、`python scripts/aggregate_metrics.py` に Windows 分が含まれることを確認 (session_count が +1)

### 記録
- [ ] `.steering/20260415-windows-onboarding/completion-log.md` に実行日時・セッションファイル名・発見したブロッカー (なければ「none」) を記録
- [ ] 発生したブロッカーは `blockers.md` に型・症状・暫定回避策を記載

## 関連ドキュメント
- `docs/development-guidelines.md §10` (Session データ管理)
- `.steering/20260415-dataset-repo-setup/` (dataset repo 設計)
- `.steering/20260415-phase1-counter-ui/verification_log.md` (macOS 版検証手順)
- gse-dataset README.md (同期プロトコル)

## 運用メモ
- **/reimagine 適用: No** — 既存の macOS 側検証フローを Windows 固有の記述に翻訳するのみ
- **前提**: GSE-prototype main が `720b2bb` 以降 (本日の全 push が反映済み)
- **Claude Code 投入方法**: 本タスクディレクトリを丸ごと Windows 側の git clone 先に入れ、「Windows 実機で Phase 1 onboarding を完了してください、手順は `.steering/20260415-windows-onboarding/tasklist.md` に従ってください」と投げる
