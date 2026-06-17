# プロジェクト共通コンテキスト (Claude Code / Codex CLI 共通)

このファイルは **Claude Code と Codex CLI の両方** が読みます。
プロジェクトの **不変的な事実** だけを記載してください。
Claude / Codex 固有の動作プロトコルはここに書きません
(それぞれ `CLAUDE.md` / `AGENTS.md` に書きます)。

## プロジェクト概要

- **名称**: GSE (Generative Struggle Engine)
- **目的**: キーストローク動態から認知状態 (Flow / Incubation / Stuck) を推定し、
  段階的介入 (Lv1 Nudge → Lv4 The Wall + Physical Anchor) で「生産的苦闘」を守る不便益 HCI フレームワーク
- **主要技術**: Tauri 2.0 + Rust (Backend: KB Hook / HMM / ONNX) + React/TypeScript (Frontend)
  + Python/PyTorch (ML 学習) + Flutter (ストレッチ: Physical Anchor)
- **ターゲット**: Windows 11 (Surface Pro 8 + Type Cover) + macOS 13+ (Accessibility / Input Monitoring)
- **チーム規模**: 小規模 (2-3 人)
- **重視する品質特性**: 正確性 (認知状態推定の精度、誤判定の最小化)
- **現フェーズ**: v0.3 較正 (キャリブレーション)。データ収集より先に設計懸念に対応する v2 再設計を実装中。

## アーキテクチャ要約

入力層 (`input/`) が OS 固有のキーボード/IME フックでイベントを捕捉し、Atomic + channel で
分析層 (`analysis/`) に渡す。分析層は 30 秒ローリングウィンドウで 5 特徴量を抽出し、HMM
(Forward Algorithm) で 3 状態確率を推定、1Hz ゲートで `FeatSnapshot` を生成する。`intervention`
が介入要否を判定し、`logger` が NDJSON にセッションを記録、`wall_server` が Lv2 Wall を提供する。
`analysis/` は **プラットフォーム非依存** (OS API は `input/` + `sensors*.rs` に隔離)。
詳細は `docs/architecture.md`。

## 主要ディレクトリ

- `src/` — React/TypeScript フロントエンド (UI / Tauri IPC のみ。ビジネスロジック禁止)
- `src-tauri/src/input/` — OS レベル入力キャプチャ (`hook_*` / `ime_*`、プラットフォーム固有)
- `src-tauri/src/analysis/` — 認知状態推定 (features / engine / loop_step / intervention / probe_scheduler / metrics、OS 非依存)
- `src-tauri/src/` — `lib.rs` (統合・IPC・スレッド起動)、`logger.rs`、`wall_server.rs`、`schema_dto.rs`
- `src-tauri/bin/` — `gse-replay` (回帰/評価 CLI)、`emit_schema` (JSON Schema 生成)
- `docs/` — 永続ドキュメント (5 ファイル + `external-skills.md` + 設計書 PDF)
- `.steering/` — タスク単位の作業記録 (`[YYYYMMDD]-[task-name]/`)
- `.claude/` — Claude Code 用 (skills / agents / commands / hooks)
- `.codex/` — Codex CLI 用 (config.toml / hooks)
- `scripts/` — 同期・検証スクリプト (sync-session.* / check_schema_parity.py 等)

詳細は `docs/repository-structure.md`。

## 技術的制約 (厳守 — 両エージェント共通)

1. **Windows API**: `windows` crate (v0.58+) のみ。`winapi` は禁止
2. **macOS API**: `core-graphics` + `core-foundation`。低レベル FFI は `#[link]` 宣言
3. **unsafe**: Win32 API / macOS FFI 呼び出しに限定し、ラッパー構造体内に隔離
4. **フックコールバック**: Atomic 操作 + channel send のみ。ブロッキング禁止 (Win/mac 共通)
5. **GCD dispatch_sync_f**: メインスレッドからの呼び出し禁止 (デッドロック)
6. **TCC 権限**: Input Monitoring → Accessibility のフォールバックチェーンを維持
7. **グローバル TSF フック禁止**: UIPI でブロックされる (Windows のみ)
8. **Rust ログ**: `tracing` のみ。`println!` / `eprintln!` 禁止
9. **エラーハンドリング**: `anyhow::Result` を使用
10. **Tauri 2.0**: capabilities で権限管理。v1 allowlist は使わない
11. **レイヤー分離**: `analysis/` 内で OS API を直接呼ばない (OS 依存は `input/` + `sensors*.rs` に閉じる)

## コーディング規約サマリ

- 命名: Rust=`snake_case.rs` (プラットフォーム固有は `{module}_{platform}.rs`)、
  React=`PascalCase.tsx`、TS ユーティリティ=`camelCase.ts`、docs=`kebab-case.md`
- 1 関数 1 責任。TypeScript は `any` 禁止 (型を明示)
- エラーは握りつぶさず `anyhow::Result` で伝播。ログは `tracing`

詳細は `docs/development-guidelines.md` §1。

## テスト方針サマリ (Replay-as-Truth)

ゴールデンセッション NDJSON を `gse-replay` CLI で再実行し、`FeatSnapshot` 列の
**byte-equal 一致** で回帰保護するのが背骨。リプレイ 1 本が単体/統合/回帰/GT 評価/チューニングを兼ねる。

```bash
# 回帰検証 (最優先)
cargo run --bin gse-replay -- tests/fixtures/minimal.ndjson --snapshot tests/snapshots/minimal.json
# 単体テスト
cargo test --workspace
# Schema drift check (gse-dataset 整合)
cargo run --bin emit_schema   # 出力を src-tauri/schema/current.json と byte-equal 比較
```

- モード系フラグ (`--snapshot` / `--metrics` / `--segments` / `--intervention`) は相互排他
- HMM 挙動を変えたら `HMM_VERSION` を bump → ゴールデン再生成 → 差分が意図通りか `.steering/` に記録
- `input/` の OS フックは実機手動確認。`analysis/` は `cargo test` で両 OS 共通検証

詳細は `docs/development-guidelines.md` §3。

## git ワークフロー基本

- **メイン**: `main` (常にビルド可能)。作業ブランチ: `[type]/[task-name]`
  (type = feature / fix / refactor / docs / chore)
- **コミット**: `[type]([scope]): [説明]` + 本文 + `Refs: .steering/[YYYYMMDD]-[task-name]/`
  (type = feat / fix / refactor / docs / chore / test、scope = engine / hook / ime / wall / frontend / logger 等)
- 1 コミット 1 論理単位。バージョンは README changelog + 重要変更時にコミット末尾 `(vX.XX)`

詳細は `docs/development-guidelines.md` §2 / `git-workflow` Skill。

## データ repo (gse-dataset) 連携

セッション NDJSON は本リポジトリに **コミットしない**。共有アーティファクトは
`gse-replay --metrics --json` 出力 (`metrics.json`) のみで、
[mikotomiura/gse-dataset](https://github.com/mikotomiura/gse-dataset) (private) の
`metrics/P*/<os>/` に置く。NDJSON Schema は `schema_dto.rs` から `emit_schema` で機械生成
(CI が drift 検知)。キーストローク内容・NDJSON 生ログは外部 LLM に送信しない。
詳細は `docs/development-guidelines.md` §10 / `data-privacy` Skill。

## CI / 運用上の注意

- CI は GitHub Actions (`.github/workflows/ci.yml`) で構成済みだが、無料枠 (3000h) 超過のため
  現状クラウド CI は利用不可。**ローカル検証で代替** (`cargo test --workspace` /
  `gse-replay --snapshot` / `emit_schema` diff を手元実行)。
- Hook はすべて bash 前提。Windows では **git-bash 必須** (PowerShell では動かない)。

## 詳細ドキュメント (リンクハブ)

| ファイル | いつ読むか |
|---|---|
| `docs/functional-design.md` | 機能の意図・要件・ユースケースを確認したい時 |
| `docs/architecture.md` | アーキテクチャ・スレッドモデル・データフローを確認したい時 |
| `docs/repository-structure.md` | ファイル配置・命名規則・モジュール依存方向を確認したい時 |
| `docs/development-guidelines.md` | コーディング規約・テスト方針・レビュー基準を確認したい時 |
| `docs/glossary.md` | 用語の正確な定義を確認したい時 (禁止用語の確認も含む) |
| `docs/external-skills.md` | 公式 (anthropics/skills) 由来の Skill 一覧、外部 LLM 送信可否 |

## 公式 Skill (Phase 2 で導入)

公式 Skill の一覧と「外部 LLM への送信可否」の単一真実源は `@docs/external-skills.md` を参照。
全て Apache 2.0 で送信制限なし。ただし NDJSON セッションログ・キーストローク内容は送信禁止
(`data-privacy` Skill 参照)。
