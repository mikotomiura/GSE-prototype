# 技術設計書

## 1. アーキテクチャ概要

### 全体図

```
┌─────────────────────────────────────────────────────────┐
│                    Tauri 2.0 App                        │
│                                                         │
│  ┌──────────────┐    ┌──────────────┐                   │
│  │ Main Window  │    │   Overlay    │   React 19 / TS   │
│  │ (Dashboard)  │◄──►│  (Nudge/Wall)│   500ms polling   │
│  └──────┬───────┘    └──────┬───────┘                   │
│         │    Tauri IPC      │    Tauri Events           │
│ ════════╪═══════════════════╪═══════════════════════════│
│         ▼                   ▼                           │
│  ┌──────────────────────────────────┐     Rust Backend  │
│  │         Tauri Commands           │                   │
│  │  get_cognitive_state, start_*    │                   │
│  └──────────────┬───────────────────┘                   │
│                 │                                       │
│    ┌────────────▼────────────┐                          │
│    │    Analysis Thread      │  1Hz timer-driven        │
│    │  ┌──────────────────┐   │                          │
│    │  │ FeatureExtractor │   │  30s rolling window      │
│    │  │  F1,F3,F4,F5,F6  │   │  5 features → 2 axes    │
│    │  └────────┬─────────┘   │                          │
│    │  ┌────────▼─────────┐   │                          │
│    │  │   HMM Engine     │   │  3×26 emission matrix    │
│    │  │  Forward Algo    │   │  EWMA + hysteresis       │
│    │  └──────────────────┘   │                          │
│    └────────────▲────────────┘                          │
│                 │ crossbeam channel                     │
│    ┌────────────┴────────────┐                          │
│    │     Hook Thread         │  WH_KEYBOARD_LL          │
│    │  InputEvent generation  │  Atomic flags             │
│    └─────────────────────────┘                          │
│                                                         │
│    ┌─────────────┐  ┌─────────────┐  ┌──────────────┐  │
│    │ IME Monitor │  │ IME Polling │  │   Logger     │  │
│    │  WinEvent   │  │ ImmGet*     │  │  NDJSON 5s   │  │
│    └─────────────┘  └─────────────┘  └──────────────┘  │
│                                                         │
│    ┌─────────────────────────────────┐                  │
│    │        Wall Server              │  tiny_http       │
│    │  QR → Phone → Zen Timer → POST  │  local network   │
│    └─────────────────────────────────┘                  │
└─────────────────────────────────────────────────────────┘
```

### 採用したパターン

- **アーキテクチャパターン**: マルチスレッド・イベント駆動 + レイヤードモジュール構成
- **採用理由**: キーボードフックは OS 制約により専用スレッド必須。1Hz 推論と入力収集の分離により、フックコールバックのレイテンシを最小化。Tauri の IPC が自然なレイヤー境界を提供。
- **トレードオフ**: Clean Architecture のような厳格な依存方向ルールは採用していない。モジュール数が少なく（input, analysis, wall_server, logger）、過度な抽象化よりも直接的な実装を優先。

## 2. 技術スタック

| レイヤー | 技術 | バージョン | 選定理由 |
|---|---|---|---|
| フレームワーク | Tauri | 2.0 | 軽量デスクトップアプリ、Rust バックエンド + Web フロントエンド |
| バックエンド言語 | Rust | stable | パフォーマンス、メモリ安全性、Windows API バインディング |
| フロントエンド | React + TypeScript | 19.1 / 5.8 | 宣言的 UI、型安全 |
| ビルドツール | Vite | 7.0 | 高速 HMR、Tauri との統合 |
| Windows API | windows crate | 0.58+ | 公式 Rust バインディング、winapi の後継 |
| スレッド間通信 | crossbeam-channel | 0.5 | 高性能 MPMC チャネル |
| HTTP サーバー | tiny_http | 0.12 | 最小限の HTTP サーバー（Wall 用） |
| QR コード | qrcode + base64 | 0.14 / 0.22 | SVG QR コード生成 |
| 非同期ランタイム | tokio | full features | Tauri 内部ランタイム。将来の重い I/O・ML 推論タスクで活用予定 |
| ログ | tracing + tracing-subscriber | 0.3 | 構造化ログ |
| エラーハンドリング | anyhow | — | アプリケーションレベルのエラー伝搬 |
| 将来: ML 推論 | ONNX Runtime | — | 学習済みモデルのクロスプラットフォーム推論 |

## 3. スレッドモデル

GSE は 6 つのスレッド/タスクで構成される。

| スレッド | 責務 | 通信方式 | 優先度 |
|---|---|---|---|
| **Main (Tauri)** | UI イベントループ、IPC ハンドラ | Mutex<Engine> 読み取り | 通常 |
| **Hook** | WH_KEYBOARD_LL + WinEvent | crossbeam Sender, Atomic flags | 高（OS 制約） |
| **Analysis** | 1Hz 特徴量抽出 + HMM 推論 | crossbeam Receiver, Mutex<Engine> 書込 | 通常 |
| **IME Monitor** | 候補ウィンドウ検出 | Atomic IME_ACTIVE | 低 |
| **IME Polling** | IME ON/OFF 検出 | Atomic IME_OPEN | 低 |
| **Logger** | NDJSON バッファリング + フラッシュ | Bounded channel (512) | 低 |

Wall Server は Lv2 介入時にのみ起動する一時的なスレッド。

### スレッド間データフロー

```
Hook Thread ──InputEvent──► crossbeam channel ──► Analysis Thread
     │                                                │
     ├── Atomic LAST_KEY_MS ──────────────────────────►│ (idle 検出)
     ├── Atomic IME_OPEN ─────────────────────────────►│ (β 切替)
     │                                                │
IME Monitor ── Atomic IME_ACTIVE ─────────────────────►│ (pause 検出)
IME Polling ── Atomic IME_OPEN ───────────────────────►│
     │                                                │
     │                                   Mutex<Engine> │
     │                                        │        │
     │                                        ▼        │
     │                                  Main Thread ──► Frontend (IPC)
     │                                                │
Analysis Thread ── LogEntry channel ──► Logger Thread ──► disk (.ndjson)
```

## 4. 主要コンポーネント

### 4.1 input::hook — キーボードフック

- **責務**: OS レベルのキー入力捕捉、IME モード変更検出
- **依存先**: windows crate, crossbeam-channel
- **インターフェース**: `InputEvent` 構造体を Sender 経由で送信
- **状態管理**: グローバル Atomic 変数（IME_OPEN, IME_ACTIVE, LAST_KEY_MS）
- **設計判断**: Relaxed ordering for LAST_KEY_MS（近似的な直近値で十分）、Acquire/Release for IME 状態（スレッド間可視性保証）

### 4.2 input::ime — IME 管理

- **責務**: IME ON/OFF 状態の正確な追跡、候補ウィンドウ検出
- **依存先**: windows crate (ImmGetOpenStatus, EnumWindows, UIAutomation)
- **インターフェース**: Atomic フラグ更新、LogEntry::ImeState 発行
- **状態管理**: ポーリングスレッドが wake_rx で駆動（フック発火時）、100ms フォールバック

### 4.3 analysis::features — 特徴量抽出

- **責務**: 生キーストローク → 5 特徴量への変換
- **依存先**: なし（純粋な計算）
- **インターフェース**: `FeatureExtractor` 構造体、`push()` / `extract()` メソッド
- **状態管理**: VecDeque バッファ（600 イベント、~30 秒分）

### 4.4 analysis::engine — HMM エンジン

- **責務**: 特徴量 → 認知状態確率の推定
- **依存先**: analysis::features
- **インターフェース**: `update()`, `update_silence()`, `register_keystroke()`, `state_probs()`
- **状態管理**: HMM 内部状態（forward 確率、EWMA 軸値、display_probs）を Mutex で保護

### 4.5 wall_server — Wall 介入サーバー

- **責務**: Lv2 介入の HTTP サーバー + QR コード生成 + スマートフォン連携
- **依存先**: tiny_http, qrcode, base64
- **インターフェース**: `start()` → WallServerInfo, `stop()`
- **状態管理**: サーバースレッドのライフサイクル、Windows Defender ファイアウォールルール

### 4.6 logger — セッションロガー

- **責務**: イベント + 状態の NDJSON 永続化
- **依存先**: serde_json
- **インターフェース**: `log()` → channel 送信、`flush()`, `close()`
- **状態管理**: バッファリングチャネル（512 エントリ）、5 秒間隔フラッシュ

## 5. データフロー

### フロー 1: キーストローク → 状態推定（1Hz サイクル）

1. ユーザーがキーを押す
2. Hook Thread が WH_KEYBOARD_LL コールバックで受信
3. InputEvent を生成し crossbeam channel へ send
4. Analysis Thread が recv_timeout で受信（1Hz ゲートまでバッファ）
5. 1Hz タイマー発火: FeatureExtractor が 5 特徴量を算出
6. IME_OPEN を参照し適切な β を選択
7. 特徴量 → (X, Y) 軸 → 観測ビンへ量子化
8. HMM Forward Algorithm で状態確率を更新
9. EWMA + ヒステリシス EMA で display_probs を平滑化
10. Mutex<Engine> に書き込み
11. Frontend が 500ms ポーリングで get_cognitive_state を呼び出し
12. ダッシュボード/オーバーレイに反映

### フロー 2: Lv2 Wall 介入

1. Frontend が p_stuck > 0.70 の累積時間を追跡（stuckAccumMsRef）
2. 累積 30 秒到達で start_wall_server を invoke
3. Rust が tiny_http サーバーを起動、ファイアウォールルール追加
4. QR コード SVG + URL を Frontend に返却
5. Frontend が Wall オーバーレイを表示（全画面ロック）
6. ユーザーがスマートフォンで QR をスキャン
7. スマートフォンブラウザが /shake にアクセス → Zen Timer HTML を受信
8. 2 分タイマー完了後、ユーザーが「Unlock Wall」をタップ
9. POST /unlock → Rust が Tauri イベント発火
10. Frontend が Wall オーバーレイを解除、stop_wall_server を invoke

## 6. 外部システム連携

| システム | 連携方式 | 認証 | 失敗時の挙動 |
|---|---|---|---|
| Windows Keyboard Hook | WH_KEYBOARD_LL (SetWindowsHookEx) | なし（OS 権限） | フック登録失敗 → 推定不能、アプリは起動 |
| Windows IME API | ImmGetOpenStatus, WinEvent | なし | フォールバック検出（VK_DBE_* → polling） |
| Wall Server (Phone) | HTTP (tiny_http) on random port | ランダムトークン | サーバー起動失敗 → Wall なしで継続 |
| Windows Defender Firewall | netsh advfirewall (子プロセス) | 管理者権限不要（ユーザースコープ） | ルール追加失敗 → スマートフォン接続不可 |
| ファイルシステム | std::fs (NDJSON ログ) | なし | 書き込み失敗 → ログドロップ、推定継続 |
| 学習データ収集 (将来) | HTTPS エンドポイント (未定) | オプトイン同意 + 匿名化 | セッション終了後バッチ送信。送信失敗 → ローカル保持、次回リトライ |

## 7. 設計上の制約とトレードオフ

### 採用しなかった選択肢

- **ITfThreadMgr グローバルフック**: UIPI によりブロックされるため、SetWindowsHookEx + WinEvent の組み合わせを採用
- **winapi crate**: メンテナンス停止。公式の windows crate (v0.58+) を採用
- **chrono**: 依存最小化のため手動で日時フォーマットを実装
- **tauri-plugin-store**: 現時点では設定永続化の必要が薄いため未導入（将来導入予定）
- **Clean Architecture**: モジュール数が少なく、厳格なレイヤー分離は過剰。直接的なモジュール構成を採用

### 許容する技術的負債

- **グローバル Atomic 変数**: Hook コールバックの制約（クロージャ不可）により、IME_OPEN / IME_ACTIVE / LAST_KEY_MS がグローバル。将来的にスレッドローカルストレージへの移行を検討
- **手動チューニング HMM**: パラメータがハードコーディング。ML モデル移行時にコンフィグファイル化が必要
- **Frontend ポーリング**: 500ms ポーリングは Tauri イベントプッシュに置換可能だが、現状のレイテンシ要件を満たしている

## 8. 拡張ポイント

### ML モデル移行（計画済み）

- **現状**: 手動チューニング HMM（3×26 emission matrix）
- **移行先**: ONNX Runtime による学習済みモデル推論
- **変更箇所**: `analysis::engine` の `update()` メソッドを差し替え。FeatureExtractor は共通利用可能
- **データ収集経路**: セッション終了後にオプトインでローカルログを匿名化し外部エンドポイントへバッチ送信。送信先・プロトコルは未定
- **前提条件**: 十分なセッションログデータの蓄積（ローカル + 収集サーバー）

### Physical Anchor（ストレッチゴール）

- **概要**: Lv3/Lv4 介入として身体的活動を促す Flutter アプリ
- **連携**: Tauri ↔ Flutter 間の通信プロトコル設計が必要
- **変更箇所**: Wall Server の拡張、または独立サービスとして実装
