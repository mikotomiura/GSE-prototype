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
│   │   └── default.json          #     デフォルト権限 (main + overlay)
│   ├── src/                      #   Rust ソースコード
│   │   ├── main.rs               #     エントリポイント (lib.rs へ委譲)
│   │   ├── lib.rs                #     アプリセットアップ, スレッド起動, IPC ハンドラ
│   │   ├── logger.rs             #     NDJSON セッションロガー
│   │   ├── wall_server.rs        #     Lv2 Wall HTTP サーバー + QR + Zen Timer
│   │   ├── input/                #     入力キャプチャ層
│   │   │   ├── mod.rs            #       モジュールエクスポート
│   │   │   ├── hook.rs           #       WH_KEYBOARD_LL フック + WinEvent
│   │   │   └── ime.rs            #       IME 状態検出 (ImmGet*, EnumWindows)
│   │   └── analysis/             #     認知状態推定層
│   │       ├── mod.rs            #       モジュールエクスポート
│   │       ├── features.rs       #       5 特徴量抽出 (30s ローリングウィンドウ)
│   │       └── engine.rs         #       HMM エンジン (Forward Algorithm)
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
│   ├── CLAUDE.md                 #   プロジェクト指示ファイル
│   ├── commands/                 #   スラッシュコマンド定義
│   ├── settings.local.json       #   ローカル設定
│   ├── agents/                   #   サブエージェント (Phase 4 で構築)
│   ├── skills/                   #   スキル (Phase 3 で構築)
│   └── hooks/                    #   フック (Phase 6 で構築)
│
├── .steering/                    # 作業記録
│   └── _setup-progress.md        #   環境構築進捗
│
├── public/                       # 静的ファイル (Vite が配信)
├── index.html                    # SPA エントリポイント
├── package.json                  # npm 依存関係・スクリプト
├── tsconfig.json                 # TypeScript 設定
├── tsconfig.node.json            # Vite 用 TypeScript 設定
├── vite.config.ts                # Vite ビルド設定
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

- **目的**: OS レベルの入力キャプチャ
- **置くべきもの**: キーボードフック、IME 状態検出、InputEvent 定義
- **置くべきでないもの**: 特徴量計算、状態推定ロジック

#### `src-tauri/src/analysis/`

- **目的**: キーストローク分析と認知状態推定
- **置くべきもの**: 特徴量抽出、HMM エンジン、将来の ML 推論
- **置くべきでないもの**: OS API 呼び出し、入力イベント捕捉

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
| Rust ソース | snake_case.rs | `wall_server.rs`, `features.rs` |
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
    │ Tauri IPC (invoke / listen)
    ▼
lib.rs (Tauri commands, thread orchestration)
    │
    ├──► input::hook    (OS キャプチャ)
    ├──► input::ime     (IME 検出)
    ├──► analysis::features (特徴量抽出)
    ├──► analysis::engine   (HMM 推論)
    ├──► logger         (セッションログ)
    └──► wall_server    (Lv2 介入)
```

- **依存方向**: lib.rs が各モジュールを統合。モジュール間の直接依存は最小限。
- **循環参照**: 禁止。input → analysis の方向のみ（features.rs の型を hook.rs が利用するケースなし）。
- **OS 固有コード**: `input/` モジュールに閉じ込める。`analysis/` は純粋な計算。

## 5. 新規ファイル追加時のルール

1. **レイヤー判定**: このファイルは input（OS 層）か analysis（計算層）か、それ以外か？
2. **ディレクトリ選択**: 既存のモジュールに属するなら同ディレクトリに追加。新モジュールは lib.rs で mod 宣言を追加。
3. **命名規則**: 上記表に従う。
4. **mod.rs 更新**: Rust ファイル追加時は対応する mod.rs の pub mod を更新。
5. **ドキュメント更新**: アーキテクチャに影響する変更は `docs/architecture.md` を更新。

## 6. 禁止パターン

- ❌ `analysis/` 内で Windows API を直接呼ぶ（OS 依存コードは `input/` に閉じる）
- ❌ フックコールバック内でブロッキング操作を行う（チャネル send + Atomic store のみ）
- ❌ `src/` (Frontend) にビジネスロジックを置く（状態推定は Rust 側で完結）
- ❌ `winapi` crate を使用する（`windows` crate v0.58+ のみ）
- ❌ グローバル TSF フックを試みる（UIPI でブロックされる）
- ❌ `docs/` に一時的な作業メモを置く（→ `.steering/`）
