# リポジトリ構造定義書

## 1. ディレクトリ構成

```
GSE-prototype/
├── src/                          # Frontend ソースコード (React/TypeScript)
│   ├── App.tsx                   #   メインアプリケーションコンポーネント
│   ├── App.css                   #   グローバルスタイル (CSS 変数、テーマ)
│   ├── main.tsx                  #   React エントリポイント
│   ├── vite-env.d.ts             #   Vite 型定義
│   ├── assets/                   #   静的アセット (SVG アイコン等)
│   └── components/               #   UI コンポーネント
│       ├── Dashboard.tsx         #     認知状態ダッシュボード
│       └── Overlay.tsx           #     Nudge/Wall 介入オーバーレイ
│
├── src-tauri/                    # Backend ソースコード (Rust/Tauri)
│   ├── Cargo.toml                #   Rust 依存関係定義
│   ├── Cargo.lock                #   ロックファイル
│   ├── tauri.conf.json           #   Tauri アプリ設定 (ウィンドウ, CSP, 識別子)
│   ├── build.rs                  #   Tauri ビルドスクリプト
│   ├── capabilities/             #   Tauri 2.0 パーミッション定義
│   │   └── default.json          #     デフォルト権限 (main + overlay + global-shortcut)
│   ├── schema/                   #   NDJSON JSON Schema (機械生成ゴールデン、Phase 1)
│   │   ├── current.json          #     emit_schema bin の出力 (手編集禁止)
│   │   └── README.md             #     sync プロトコル
│   ├── tests/                    #   テストフィクスチャとスナップショット
│   │   ├── fixtures/             #     ゴールデンセッション NDJSON
│   │   └── snapshots/            #     gse-replay --snapshot 比較用 JSON
│   ├── src/                      #   Rust ソースコード
│   │   ├── main.rs               #     エントリポイント (lib.rs へ委譲)
│   │   ├── lib.rs                #     アプリセットアップ, スレッド起動, IPC ハンドラ
│   │   │                         #       + record_user_label / global-shortcut (Phase 1)
│   │   ├── logger.rs             #     NDJSON セッションロガー
│   │   │                         #       + UserLabelKind enum / LogEntry::UserLabel (Phase 1)
│   │   ├── schema_dto.rs         #     [NEW Phase 1] LogEntry ミラー DTO (schemars 派生専用)
│   │   ├── capabilities.rs       #     [NEW 2026-08-19] このビルドが何を記録できるかの宣言表 (ADR-013)
│   │   ├── g1.rs                 #     [NEW 2026-08] G1 統制タスク実験モードの判定 (OS API 非依存)
│   │   ├── participant_id.rs     #     participant_id 検証の単一情報源 (feature 非依存)
│   │   ├── packaging.rs          #     匿名化 + age 暗号化 SSOT (#[cfg(feature = "package")] gated)
│   │   ├── overlay_panel.rs      #     macOS: overlay 窓の NSPanel 化 FFI グルー (#[cfg(macos)] gated)
│   │   ├── sensors.rs            #     センサーモジュール dispatch (#[cfg(macos)] gated)
│   │   ├── sensors_macos.rs      #     macOS: SensorManager stub (CoreMotion 予約)
│   │   ├── bin/                  #     サブコマンド実装
│   │   │   ├── replay.rs         #       gse-replay: セッション再実行 + --snapshot / --metrics / --calibration
│   │   │   ├── cohort.rs         #       [v0.3 Task E] gse-cohort: 被験者横断コホート判定 (calib JSON 集約)
│   │   │   └── emit_schema.rs    #       [NEW Phase 1] schema_dto → JSON Schema stdout
│   │   ├── input/                #     入力キャプチャ層 (プラットフォーム固有コード)
│   │   │   ├── mod.rs            #       モジュールエクスポート + platform dispatch
│   │   │   ├── hook.rs           #       共有アトミック変数 + #[cfg] 振り分け
│   │   │   ├── hook_windows.rs   #       Windows: WH_KEYBOARD_LL + WinEvent フック
│   │   │   ├── hook_macos.rs     #       macOS: CGEventTap + CFRunLoop + IME 状態機械 + TCC
│   │   │   ├── ime.rs            #       IME platform dispatch (#[cfg] + #[path])
│   │   │   ├── ime_cloak.rs      #       cloak/uncloak の畳み込み (★ OS 非依存・両 OS でテスト)
│   │   │   ├── ime_windows.rs    #       Windows: ImmGet* + WinEvent + UIAutomation + cloak resolver
│   │   │   └── ime_macos.rs      #       macOS: TIS ポーリング + GCD dispatch
│   │   └── analysis/             #     認知状態推定層 (プラットフォーム非依存)
│   │       ├── mod.rs            #       モジュールエクスポート
│   │       ├── features.rs       #       5 特徴量抽出 (30s ローリングウィンドウ)
│   │       ├── engine.rs         #       HMM エンジン (Forward Algorithm)
│   │       ├── loop_step.rs      #       1Hz ゲート + FeatSnapshot 生成
│   │       ├── intervention.rs   #       Opportunity MVP (Need/Opportunity → none/nudge/wall/defer)
│   │       ├── intervention_eval.rs #    v2 介入ポリシーのオフライン反実仮想評価 (HIR/Precision/DC/Burden)
│   │       ├── probe_scheduler.rs #      [v0.3] ランダム時点プローブの純スケジューリング (Poisson+thinning)
│   │       ├── metrics.rs        #       [Phase 1] UserLabel × FeatSnapshot 集計
│   │       ├── calibration_eval.rs #     [v0.3] 較正解析 (時間隔離窓 C-index/2段ゲート/MNAR/ビネット採点)
│   │       └── cohort.rs         #       [v0.3 Task E] 被験者横断コホート判定 (純関数・gate 再利用・read-model DTO)
│   ├── icons/                    #   アプリアイコン (各サイズ)
│   ├── gen/                      #   Tauri 自動生成ファイル (スキーマ)
│   └── .cargo/config.toml        #   Cargo ビルド設定
│
├── docs/                         # 永続ドキュメント
│   ├── functional-design.md      #   機能設計書
│   ├── architecture.md           #   技術設計書
│   ├── repository-structure.md   #   本ファイル
│   ├── development-guidelines.md #   開発ガイドライン
│   ├── glossary.md               #   ユビキタス言語定義
│   └── *.pdf                     #   提案書・技術設計書 (原本)
│
├── .claude/                      # Claude Code 設定
│   ├── commands/                 #   スラッシュコマンド定義
│   ├── settings.local.json       #   ローカル設定
│   ├── agents/                   #   サブエージェント
│   ├── skills/                   #   スキル
│   └── hooks/                    #   フック
│
├── .codex/                       # Codex CLI 連携設定 (config.toml, agents/, hooks/, hooks.json)
├── .agents/                      # 共有エージェント定義 (skills/)
├── scripts/                      # 同期・検証スクリプト (sync-session.*, sync-all.*, check_schema_parity.py 等)
│
├── .steering/                    # 作業記録
│   ├── _setup-progress.md        #   環境構築進捗
│   └── _template/                #   タスク用 5 ファイルテンプレート
│
├── .github/                      # GitHub Actions ワークフロー (ci.yml 等)
├── .vscode/                      # エディタ設定
├── dist/                         # Vite/Tauri ビルド出力 (生成物、git 管理外)
├── public/                       # 静的ファイル (Vite が配信)
├── index.html                    # SPA エントリポイント
├── package.json                  # npm 依存関係・スクリプト
├── tsconfig.json                 # TypeScript 設定
├── tsconfig.node.json            # Vite 用 TypeScript 設定
├── vite.config.ts                # Vite ビルド設定
├── CLAUDE.md                     # Claude Code への指示 (リポジトリ直下、ポインタ型)
├── AGENTS.md                     # Codex CLI への指示
├── README.md                     # プロジェクト概要 (英語)
├── README.ja.md                  # プロジェクト概要 (日本語)
├── advice.md                     # 開発メモ・チューニング記録
└── .gitignore                    # Git 除外パターン
```

## 2. ディレクトリの責務

### `src/`

- **目的**: React/TypeScript フロントエンド
- **置くべきもの**: UI コンポーネント、スタイル、Tauri IPC 呼び出し
- **置くべきでないもの**: ビジネスロジック、認知状態推定ロジック、OS API 呼び出し

### `src-tauri/src/`

- **目的**: Rust バックエンドロジック
- **置くべきもの**: キーストロークフック、認知状態推定、セッション管理、Tauri コマンド
- **置くべきでないもの**: UI 描画ロジック

#### `src-tauri/src/input/`

- **目的**: OS レベルの入力キャプチャ（プラットフォーム固有コードの格納先）
- **置くべきもの**: キーボードフック、IME 状態検出、InputEvent 定義、プラットフォーム固有キーコードマッピング、TCC 権限管理（macOS）
- **置くべきでないもの**: 特徴量計算、状態推定ロジック
- **プラットフォーム振り分け**: `hook.rs` / `ime.rs` が `#[cfg(target_os)] + #[path]` で `*_windows.rs` / `*_macos.rs` に振り分け

#### `src-tauri/src/analysis/`

- **目的**: キーストローク分析と認知状態推定
- **置くべきもの**: 特徴量抽出、HMM エンジン、`heads/` (ADR-002/006 ドメイン推論ヘッド: β baseline を所有し潜在二軸を算出)、`loop_step`、`intervention` (Opportunity MVP)、`intervention_eval` (オフライン評価)、`probe_scheduler` (v0.3 純スケジューリング)、`metrics` (Phase 1 GT 集計)、`calibration_eval` (v0.3 較正解析: C-index/2段ゲート/MNAR)、将来の ML 推論
- **置くべきでないもの**: OS API 呼び出し、入力イベント捕捉、タイムスタンプ生成 (`SystemTime` は `lib.rs` で付与)

#### `src-tauri/src/capabilities.rs` (2026-08-19)

- **置くべきもの**: 「**このビルドが何を記録できるか**」の宣言表 (ADR-013 D1/D2)。
  `KNOWN_LINE_TYPES` (全行種の候補集合) / `unconditional()` / `THRESHOLD_GATED` / `app_version()`
- **置くべきでないもの**: ⚠️ OS API 呼び出し。★ `#[cfg]` を**反映**はするが**呼ばない**
- ⚠️★★★ **導出元は「送出元があるか」であって writer ではない**。
  `LogEntry` の variant や `logger.rs` が書ける行種から導出すると
  **macOS で `ime_shadow` を過大申告する** (送出元は Windows 限定)
- ★ 腐りは**テストが止める**: 網羅 (`logger.rs` の `"type":"<x>"` 走査) / OS 対 /
  宣言集合が `KNOWN_LINE_TYPES` を過不足なく割ること
- 詳細: `docs/adr/ADR-013-collection-self-description.md` /
  `.steering/20260819-g1-reboot-and-instrument-fix/`

#### `src-tauri/src/g1.rs` (2026-08)

- **置くべきもの**: 「いま G1 統制タスク実験の実施中か」の**判定だけ**。
  `g1.mode` マーカーの探索パス計算 (純関数)、`GSE_G1_MODE` の解釈 (純関数)、
  `BLOCK_DURATION_MS` / `G1Source`、プロセス列挙の出力パース (純関数)、
  ★ **`decide_start_action`**「開始する」押下時にログをどう扱うか (純関数・2026-08-19 G-1)
- **置くべきでないもの**: ★ **効果の適用**。ローテートも 5 分タイマーもプローブ停止も
  `lib.rs` が行う (このモジュールは「判定」だけを持つ)
- ⚠️ **プラットフォーム分岐は引数に出す**: `exe_to_folder_levels()` が階層数を返し、
  `folder_up(exe, levels_up)` は純関数。★ **両 OS の形を片方の OS 上で検証できる**
- ⚠️ **OS 依存はプロセス列挙だけ**（`pgrep` / `tasklist` を**絶対パス**で起動する。
  相対名だと Windows が `current_exe()` のディレクトリを System32 より先に探すため）
- 詳細: `docs/architecture.md §4.12` / `.steering/20260805-g1-app-mode-and-log-rotation/`

#### `src-tauri/src/schema_dto.rs` (Phase 1)

- **目的**: NDJSON JSON Schema を機械生成するための DTO ミラー型
- **置くべきもの**: `LogEntry` を schemars 派生可能な形にミラーした型 (`LogEntryDto`)
- **置くべきでないもの**: 実際の NDJSON 書き込みロジック (`logger.rs::writeln!` が本体、DTO は派生専用)
- **production path 不干渉**: `logger.rs::LogEntry` 本体には `Serialize` を派生させない (float フォーマット固定のゴールデン保護)

#### `src-tauri/src/bin/` (Phase 1)

- **目的**: サブコマンドとして独立して動作する実行バイナリ
- **`replay.rs`**: ゴールデンセッション NDJSON を再実行する `gse-replay` CLI (`--snapshot` / `--metrics` / `--calibration` / `--json`)
- **`cohort.rs`**: 被験者別 calibration レポート JSON を集約する `gse-cohort` CLI (v0.3 Task E)。`metrics/P*/<os>/*.calib.json` を走査し `analysis::cohort::cohort_verdict` でコホート Go/Kill/INCONCLUSIVE を出す
- **`emit_schema.rs`**: `schema_dto::LogEntryDto` から JSON Schema を stdout に吐く (CI drift check が consume)

#### `src-tauri/schema/` (Phase 1)

- **目的**: 機械生成 JSON Schema のゴールデンコピー
- **`current.json`**: `emit_schema` の最新出力、手編集禁止
- **CI 連携**: `.github/workflows/ci.yml` の `check` ジョブが diff で drift 検知
- **gse-dataset 連携**: 本ファイルを gse-dataset repo の `schema/current.json` に手動コピーする (`docs/development-guidelines.md §10` 参照)

### `docs/`

- **目的**: 永続的なプロジェクトドキュメント
- **置くべきもの**: 設計書、修正レポート、提案書原本
- **置くべきでないもの**: 一時的な作業メモ（→ `.steering/`）

### `.claude/`

- **目的**: Claude Code の設定・拡張一式
- **管理方針**: Git 管理下に置く（チーム共有）

### `.steering/`

- **目的**: タスク単位の作業記録
- **構造**: `[YYYYMMDD]-[task-name]/` 形式でタスクごとにディレクトリ作成

## 3. ファイル命名規則

| 種類 | 規則 | 例 |
|---|---|---|
| Rust ソース | snake_case.rs | `wall_server.rs`(削除済), `features.rs` |
| Rust プラットフォーム固有 | {module}\_{platform}.rs | `hook_windows.rs`, `hook_macos.rs`, `ime_macos.rs` |
| Rust モジュール | ディレクトリ + mod.rs | `input/mod.rs` |
| React コンポーネント | PascalCase.tsx | `Dashboard.tsx`, `Overlay.tsx` |
| TypeScript ユーティリティ | camelCase.ts | （現在なし） |
| CSS | コンポーネント名.css | `App.css` |
| ドキュメント | kebab-case.md | `functional-design.md` |
| 修正レポート | `fix-report-YYYYMMDD-<summary>.md` | `fix-report-20260308-emission-ime-logging.md` |
| 設定ファイル | ツール標準に従う | `Cargo.toml`, `package.json`, `tsconfig.json` |

## 4. モジュール依存方向

```
Frontend (src/)
    │
    │ Tauri IPC (invoke / listen / emit user_label_recorded)
    ▼
lib.rs (Tauri commands, thread orchestration)
    │   + record_user_label コマンド / global-shortcut プラグイン (Phase 1)
    │
    ├──► input::hook    (OS キャプチャ)
    │    ├── hook_windows.rs  (Win: WH_KEYBOARD_LL)
    │    └── hook_macos.rs    (mac: CGEventTap + IME 状態機械)
    ├──► input::ime     (IME 検出)
    │    ├── ime_cloak.rs     (★ OS 非依存: cloak の畳み込み)
    │    ├── ime_windows.rs   (Win: WinEvent + ImmGet* + cloak resolver)
    │    └── ime_macos.rs     (mac: TIS + GCD)
    ├──► analysis::features (特徴量抽出)
    ├──► analysis::engine   (HMM 推論)
    ├──► analysis::loop_step (1Hz ゲート + FeatSnapshot)
    ├──► analysis::intervention (Opportunity MVP: Need/Opportunity → none/nudge/wall/defer)
    ├──► analysis::intervention_eval (gse-replay --intervention で使用、オフライン評価)
    ├──► analysis::probe_scheduler (v0.3: 純スケジューリング、起動/emit は lib.rs 側)
    ├──► analysis::metrics  (Phase 1: GT × FeatSnapshot 集計、gse-replay --metrics で使用)
    ├──► analysis::calibration_eval (v0.3: 較正解析、gse-replay --calibration で使用、オフライン)
    ├──► analysis::cohort   (v0.3 Task E: 被験者横断判定、gse-cohort で使用、calibration_eval の gate 再利用)
    ├──► logger         (セッションログ, UserLabel / probe_assignment 等のバリアント含む)

schema_dto (Phase 1, production path と独立)
    │
    ▼
bin/emit_schema ──► schema/current.json (CI drift check ─── gse-dataset 同期)
```

- **依存方向**: lib.rs が各モジュールを統合。モジュール間の直接依存は最小限。
- **循環参照**: 禁止。input → analysis の方向のみ（features.rs の型を hook.rs が利用するケースなし）。
- **OS 固有コード**: `input/` モジュール + `sensors*.rs` に閉じ込める。`analysis/` は純粋な計算（プラットフォーム非依存）。`hook_macos.rs` 内の CGKeyCode → Windows VK マッピングにより、analysis 層は両プラットフォームで同一の VK コードを受け取る。

## 5. 新規ファイル追加時のルール

1. **レイヤー判定**: このファイルは input（OS 層）か analysis（計算層）か、それ以外か？
2. **ディレクトリ選択**: 既存のモジュールに属するなら同ディレクトリに追加。新モジュールは lib.rs で mod 宣言を追加。
3. **命名規則**: 上記表に従う。
4. **mod.rs 更新**: Rust ファイル追加時は対応する mod.rs の pub mod を更新。
5. **ドキュメント更新**: アーキテクチャに影響する変更は `docs/architecture.md` を更新。
6. **プラットフォーム固有ファイル**: `{module}_{platform}.rs` の命名規則に従い、対応する dispatch ファイル（hook.rs, ime.rs）に `#[cfg] + #[path]` を追加。

## 6. 禁止パターン

- ❌ `analysis/` 内で Windows API または macOS フレームワークを直接呼ぶ（OS 依存コードは `input/` + `sensors/` に閉じる）
- ❌ フックコールバック内でブロッキング操作を行う（チャネル send + Atomic store のみ）
- ❌ `src/` (Frontend) にビジネスロジックを置く（状態推定は Rust 側で完結）
- ❌ `winapi` crate を使用する（`windows` crate v0.58+ のみ）
- ❌ グローバル TSF フックを試みる（UIPI でブロックされる）
- ❌ `docs/` に一時的な作業メモを置く（→ `.steering/`）
