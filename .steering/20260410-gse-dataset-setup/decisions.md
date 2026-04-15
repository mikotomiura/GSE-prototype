# 設計判断記録

## Decision 1: モノレポ統合の方針

**判断**: macOS リポ (GSE-prototype-for-mac) を Windows リポ (GSE-prototype) に統合し、
`#[cfg(target_os)]` によるコンパイル時条件分岐で OS 固有コードを分離する。

**根拠**:
- コードの 80% が共通（HMM エンジン、特徴量抽出、Wall Server、Logger）
- macOS 版が既に dispatcher パターン (`hook.rs` → `hook_macos.rs`) を採用していた
- HMM パラメータ変更の二重メンテが解消される

**結果**: Rust バックエンド統合完了。CI (GitHub Actions) で両 OS ビルド成功確認済み。

## Decision 2: gse-dataset を別リポジトリで管理

**判断**: セッションログデータを `gse-dataset` (private) として GSE-prototype とは別リポで管理。

**根拠**:
- データとコードのライフサイクルが異なる
- 生ログに VK コードが含まれるため、コードリポジトリに混ぜない
- Phase 2 (5名データ収集) で被験者データを含むため private 必須

## Decision 3: logger.rs のデフォルトパスを gse-dataset に変更 (初版: 2026-04-10、2026-04-16 に revise)

**当初判断 (2026-04-10)**: `~/Documents/GSE-sessions/` → `gse-dataset/raw/P000/` に直接保存。環境変数 `GSE_DATASET` → 兄弟ディレクトリ自動検出 → フォールバック の 3 段優先。

**Revise (2026-04-16、Phase 0.5 close-out)**: 兄弟ディレクトリ自動検出 (exe から最大 5 階層上を走査して `gse-dataset/raw/P000/` を優先するマジック) を**撤廃**。CI / 別開発マシン / Tauri bundle 配布先で予期しないパスに書き込むリスクがあったため、env `GSE_DATASET` + fallback の 2 段に簡素化した。

- `logger.rs:291-317` の自動探索コードを削除
- `default_log_path()` に `tracing::info!(resolved_log_dir, source)` を追加して保存先を常時可視化
- 開発者は shell rc / PowerShell `$PROFILE` で `GSE_DATASET` を一度だけ明示的に設定する運用に移行 (`docs/development-guidelines.md §10.2` 参照)
- 自動 import の手間は変わらず (env 設定後は以前と同じく dataset に直接書く)

**Refs**: `.steering/20260415-windows-onboarding/blockers.md` BL-1 Closed、`.steering/20260416-replay-feat-alignment-bug/decisions.md` D1 (同じ logger.rs 領域の別負債)

## Decision 4: Stop hook を command 型に変更

**判断**: `.claude/settings.json` の Stop hook を `prompt` 型 → `command` 型に変更し、
`git diff --name-only` で変更ファイルが 0 件の場合はスキップ。

**根拠**: コード変更を伴わない会話で無限ループが発生していた。
