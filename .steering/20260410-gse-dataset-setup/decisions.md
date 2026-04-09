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

## Decision 3: logger.rs のデフォルトパスを gse-dataset に変更

**判断**: `~/Documents/GSE-sessions/` → `gse-dataset/raw/P000/` に直接保存するよう変更。

**根拠**: import_sessions.py による手動インポートの手間を排除。
環境変数 `GSE_DATASET` → 兄弟ディレクトリ自動検出 → フォールバック の優先順位。

## Decision 4: Stop hook を command 型に変更

**判断**: `.claude/settings.json` の Stop hook を `prompt` 型 → `command` 型に変更し、
`git diff --name-only` で変更ファイルが 0 件の場合はスキップ。

**根拠**: コード変更を伴わない会話で無限ループが発生していた。
