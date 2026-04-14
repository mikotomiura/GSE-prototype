# 技術設計書

## 1. アーキテクチャ概要

### 全体図

```
┌──────────────────────────────────────────────────────────────┐
│                       Tauri 2.0 App                          │
│                                                              │
│  ┌──────────────┐    ┌──────────────┐                        │
│  │ Main Window  │    │   Overlay    │   React 19 / TS        │
│  │ (Dashboard)  │◄──►│  (Nudge/Wall)│   500ms polling        │
│  └──────┬───────┘    └──────┬───────┘                        │
│         │    Tauri IPC      │    Tauri Events                │
│ ════════╪═══════════════════╪════════════════════════════════│
│         ▼                   ▼                                │
│  ┌──────────────────────────────────┐        Rust Backend    │
│  │         Tauri Commands           │                        │
│  │  get_cognitive_state, start_*    │                        │
│  │  [macOS] reset_tcc, open_ax_*   │                        │
│  └──────────────┬───────────────────┘                        │
│                 │                                            │
│    ┌────────────▼────────────┐                               │
│    │    Analysis Thread      │  1Hz timer-driven             │
│    │  ┌──────────────────┐   │                               │
│    │  │ FeatureExtractor │   │  30s rolling window           │
│    │  │  F1,F3,F4,F5,F6  │   │  5 features → 2 axes         │
│    │  └────────┬─────────┘   │                               │
│    │  ┌────────▼─────────┐   │                               │
│    │  │   HMM Engine     │   │  3×26 emission matrix         │
│    │  │  Forward Algo    │   │  EWMA + hysteresis            │
│    │  └──────────────────┘   │                               │
│    └────────────▲────────────┘                               │
│                 │ crossbeam channel                          │
│    ┌────────────┴────────────────────────────────┐           │
│    │            Hook Thread (Platform)            │           │
│    │  Win: WH_KEYBOARD_LL + WinEvent             │           │
│    │  mac: CGEventTap + CFRunLoop                │           │
│    │  InputEvent generation / Atomic flags        │           │
│    └─────────────────────────────────────────────┘           │
│                                                              │
│    ┌─────────────────┐  ┌─────────────────┐  ┌───────────┐  │
│    │   IME Monitor   │  │   IME Polling   │  │  Logger   │  │
│    │ Win: WinEvent   │  │ Win: ImmGet*    │  │ NDJSON 5s │  │
│    │ mac: (hook内)   │  │ mac: TIS + GCD  │  │           │  │
│    └─────────────────┘  └─────────────────┘  └───────────┘  │
│                                                              │
│    ┌─────────────────────────────────┐                       │
│    │        Wall Server              │  tiny_http            │
│    │  QR → Phone → Zen Timer → POST  │  local network        │
│    └─────────────────────────────────┘                       │
└──────────────────────────────────────────────────────────────┘
```

### 採用したパターン

- **アーキテクチャパターン**: マルチスレッド・イベント駆動 + レイヤードモジュール構成
- **採用理由**: キーボードフックは OS 制約により専用スレッド必須。1Hz 推論と入力収集の分離により、フックコールバックのレイテンシを最小化。Tauri の IPC が自然なレイヤー境界を提供。
- **トレードオフ**: Clean Architecture のような厳格な依存方向ルールは採用していない。モジュール数が少なく（input, analysis, wall_server, logger）、過度な抽象化よりも直接的な実装を優先。

## 2. 技術スタック

| レイヤー | 技術 | バージョン | 選定理由 |
|---|---|---|---|
| フレームワーク | Tauri | 2.0 (macos-private-api) | 軽量デスクトップアプリ、Rust バックエンド + Web フロントエンド |
| バックエンド言語 | Rust | stable | パフォーマンス、メモリ安全性、OS API バインディング |
| フロントエンド | React + TypeScript | 19.1 / 5.8 | 宣言的 UI、型安全 |
| ビルドツール | Vite | 7.0 | 高速 HMR、Tauri との統合 |
| Windows API | windows crate | 0.58+ | 公式 Rust バインディング（Windows のみ） |
| macOS 入力 | core-graphics + core-foundation | 0.24 / 0.10 | CGEventTap + TIS API（macOS のみ） |
| macOS フレームワーク | ApplicationServices, Carbon, System | OS 提供 | TCC 権限チェック、GCD dispatch、TIS 入力ソースクエリ |
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
| **Hook** | Win: WH_KEYBOARD_LL + WinEvent / mac: CGEventTap + CFRunLoop | crossbeam Sender, Atomic flags | 高（OS 制約） |
| **Analysis** | 1Hz 特徴量抽出 + HMM 推論 | crossbeam Receiver, Mutex<Engine> 書込 | 通常 |
| **IME Monitor** | Win: 候補ウィンドウ検出 / mac: フック内で処理（別スレッド不要） | Atomic IME_ACTIVE | 低 |
| **IME Polling** | Win: ImmGet\* / mac: TIS ポーリング (GCD メインキュー経由) | Atomic IME_OPEN | 低 |
| **Logger** | NDJSON バッファリング + フラッシュ | Bounded channel (512) | 低 |

Wall Server は Lv2 介入時にのみ起動する一時的なスレッド。

**macOS 固有のスレッド動作:**
- Hook Thread: CGEventTap を CFRunLoop に登録し、専用スレッドで CFRunLoopRun() をブロッキング実行。タップ無効化時は自動再作成ループ（3 秒ポーリング）
- IME Polling: macOS では JIS 物理キー検出（フック内、高速）と TIS ポーリング（dispatch_sync_f でメイン GCD キューへ dispatch）のデュアルパス
- IME Monitor: macOS では CGEventTap コールバック内の状態機械で処理するため、専用スレッド不要

### スレッド間データフロー

```
Hook Thread ──InputEvent──► crossbeam channel ──► Analysis Thread
     │  Win: WH_KEYBOARD_LL callback                  │
     │  mac: CGEventTap callback (CGKeyCode→VK変換)   │
     │                                                │
     ├── Atomic LAST_KEY_MS ──────────────────────────►│ (idle 検出)
     ├── Atomic IME_OPEN ─────────────────────────────►│ (β 切替)
     │  [mac] IME_COMPOSING ──────────────────────────►│ (変換中検出)
     │                                                │
IME Monitor ── Atomic IME_ACTIVE ─────────────────────►│ (pause 検出)
     │  Win: WinEvent + EnumWindows + UIAutomation     │
     │  mac: (CGEventTap 内で処理 — 別スレッド不要)     │
IME Polling ── Atomic IME_OPEN ───────────────────────►│
     │  Win: ImmGetOpenStatus                          │
     │  mac: TIS via dispatch_sync_f → main GCD queue  │
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
- **依存先**: Win: windows crate / mac: core-graphics, core-foundation, ApplicationServices (FFI)
- **インターフェース**: `InputEvent` 構造体を Sender 経由で送信
- **状態管理**: グローバル Atomic 変数
  - 共通: IME_OPEN, IME_ACTIVE, LAST_KEY_MS, HOOK_ACTIVE
  - macOS 追加: IME_COMPOSING, JIS_KEYBOARD_SEEN, CALLBACK_COUNT, CONSECUTIVE_TAP_FAILURES, USING_ACCESSIBILITY_FALLBACK
- **設計判断**: Relaxed ordering for LAST_KEY_MS（近似的な直近値で十分）、Acquire/Release for IME 状態（スレッド間可視性保証）
- **プラットフォーム振り分け**: `hook.rs` が共有アトミック変数と `#[cfg(target_os)] + #[path]` で `hook_windows.rs` / `hook_macos.rs` に振り分け
- **macOS 固有**: CGKeyCode → Windows VK マッピングテーブルにより、analysis 層は両プラットフォームで同一の VK コードを受け取る

### 4.2 input::ime — IME 管理

- **責務**: IME ON/OFF 状態の正確な追跡、候補ウィンドウ検出
- **依存先**: Win: windows crate (ImmGetOpenStatus, EnumWindows, UIAutomation) / mac: Carbon (TIS\*), System (GCD dispatch_sync_f)
- **インターフェース**: Atomic フラグ更新、LogEntry::ImeState 発行
- **状態管理**: ポーリングスレッドが wake_rx で駆動（フック発火時）、100ms フォールバック
- **プラットフォーム振り分け**: `ime.rs` が `#[cfg(target_os)] + #[path]` で `ime_windows.rs` / `ime_macos.rs` に振り分け
- **macOS 固有**: デュアルパス検出 — Path A: JIS 物理キー検出（CGEventTap 内、\~5ms）/ Path B: ANSI キーボード TIS ポーリング（GCD メインキュー経由、100ms 間隔）。TIS API は HIToolbox 制約によりメインスレッド必須

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
- **状態管理**: サーバースレッドのライフサイクル、Win: Windows Defender ファイアウォールルール / mac: 追加管理不要（ユーザースコープポートバインド）

### 4.6 logger — セッションロガー

- **責務**: イベント + 状態の NDJSON 永続化
- **依存先**: serde_json
- **インターフェース**: `log()` → channel 送信、`flush()`, `close()`
- **状態管理**: バッファリングチャネル（512 エントリ）、5 秒間隔フラッシュ

### 4.7 沈黙 3 状態機構（Silence 3-State Mechanism）

1Hz 推論ゲートにおける特徴量計算と HMM 更新は、**バッファの状態と沈黙秒数に応じて 3 つのパス**に分岐する。各パスで使用する EWMA α・摩擦フロア適用有無・呼び出す engine メソッドが異なる。分散実装 (`lib.rs` 分析スレッド + `features.rs::make_silence_observation` + `engine.rs::update_silence`) のため、全体像を以下に集約する。

#### 3 パスの定義

| パス名 | 発動条件 | engine 呼び出し | EWMA α | 摩擦フロア |
|--------|---------|----------------|--------|-----------|
| **TypingPath** | バッファ実データあり (f1 > 0) かつ `silence < 2s` | `update()` | 0.3 | なし |
| **TransitionPath** | バッファ実データあり (f1 > 0) かつ `silence ≥ 2s` | `update_silence()` | 0.15 / 0.18 / 0.25 | F6 onset 8s / F3 onset 10s（≥10s でフロア 0.15 / 0.20） |
| **SilencePath** | バッファ空 (f1 = 0) かつ `silence ≥ 2s` | `update_silence()` | 0.15 / 0.18 / 0.25 | F6 onset 10s / F3 onset 15s（≥10s でフロア 0.15 / 0.20） |

いずれの条件にも該当しない（`silence < 2s` かつ `f1 = 0`、データ不足）場合は推論スキップ。

#### TransitionPath と SilencePath のフロア閾値差

両パスは似て非なる摩擦フロアを持つ:

| パラメータ | TransitionPath (`lib.rs` 分析スレッド内ブランチ) | SilencePath (`features.rs::make_silence_observation`) |
|------------|-----------------------------------|--------------------------------------|
| F6 onset | **8s** | **10s** |
| F6 ramp | 30s | 40s |
| F6 floor (≥10s) | 0.15 | 0.15 |
| F3 onset | **10s** | **15s** |
| F3 ramp | 40s | 50s |
| F3 floor (≥10s) | 0.20 | 0.20 |

TransitionPath が先行するのは、「直近まで実データがあったユーザーが沈黙に入った」状況を「完全な無入力のユーザー」より早く Stuck 方向へ引くため。

#### 意図的に統合していない理由

2 つのパスは実装上似ており統合の誘惑があるが、GSE では**明示的に統合を避けている**:

1. **統合リスク > 保守利益**: 既存の挙動はゴールデンセッションで動作確認済み。統合リファクタは微妙な挙動変化のリスクが大きい
2. **責務の違い**: TransitionPath は「打鍵を見た直後の沈黙」、SilencePath は「純粋な無入力」を扱う。閾値差はこの意味論の違いを反映している
3. **原則 D (Keep What Works, Rename What's Confusing)**: コード削減自体を目的化しない。名前と文書で可読性を確保する

統合しない判断の詳細根拠は `.steering/20260414-improvement-roadmap/decisions.md` §3 を参照。

#### 拡張時の注意

Phase 2a（Synthetic Friction 再設計）では、TransitionPath と SilencePath の両方にゲート条件（直前の φ(F3) / φ(F6) に基づく文脈判定）を追加する計画がある。その際も**両パスの閾値は独立に維持する**こと。統合してはならない。

## 5. データフロー

### フロー 1: キーストローク → 状態推定（1Hz サイクル）

1. ユーザーがキーを押す
2. Hook Thread がコールバックで受信（Win: WH_KEYBOARD_LL / mac: CGEventTap）
3. InputEvent を生成し crossbeam channel へ send（macOS: CGKeyCode → VK 変換後）
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
3. Rust が tiny_http サーバーを起動（Win: ファイアウォールルール追加 / mac: 追加設定不要）
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
| Win: Keyboard Hook | WH_KEYBOARD_LL (SetWindowsHookEx) | なし（OS 権限） | フック登録失敗 → 推定不能、アプリは起動 |
| mac: CGEventTap | core-graphics CGEventTap | TCC Input Monitoring or Accessibility | 権限未付与 → ポーリング再試行、10 回失敗で Accessibility フォールバック |
| Win: IME API | ImmGetOpenStatus, WinEvent | なし | フォールバック検出（VK_DBE_\* → polling） |
| mac: TIS API | TISCopyCurrentKeyboardInputSource (Carbon) | なし | dispatch_sync_f で main GCD queue に dispatch（HIToolbox 制約） |
| mac: TCC System | CGPreflight/CGRequest, AXIsProcessTrusted | OS 権限 | tccutil reset でリカバリ可能。Dashboard に TCC リセットボタンあり |
| Wall Server (Phone) | HTTP (tiny_http) on random port | ランダムトークン | サーバー起動失敗 → Wall なしで継続 |
| Win: Defender Firewall | netsh advfirewall (子プロセス) | 管理者権限不要（ユーザースコープ） | ルール追加失敗 → スマートフォン接続不可 |
| ファイルシステム | std::fs (NDJSON ログ) | なし | 書き込み失敗 → ログドロップ、推定継続 |
| 学習データ収集 (将来) | HTTPS エンドポイント (未定) | オプトイン同意 + 匿名化 | セッション終了後バッチ送信。送信失敗 → ローカル保持、次回リトライ |

## 7. プラットフォーム抽象化

### 振り分けパターン

`input/` モジュールは `#[cfg(target_os)] + #[path]` 属性で OS 固有実装を振り分ける。

```
hook.rs (共有アトミック変数 + platform dispatch)
  ├── #[cfg(windows)]  → hook_windows.rs   (WH_KEYBOARD_LL + WinEvent)
  └── #[cfg(macos)]    → hook_macos.rs     (CGEventTap + CFRunLoop + IME 状態機械)

ime.rs (platform dispatch)
  ├── #[cfg(windows)]  → ime_windows.rs    (ImmGet* + WinEvent + UIAutomation)
  └── #[cfg(macos)]    → ime_macos.rs      (TIS ポーリング + GCD dispatch)

sensors.rs (#[cfg(macos)] のみ)
  └── sensors_macos.rs  (SensorManager stub — CoreMotion 予約)
```

### キーコードの統一

`hook_macos.rs` 内で CGKeyCode を Windows VK コードに変換する。analysis 層（features.rs, engine.rs）は VK コードのみを扱い、プラットフォーム非依存を維持する。

### macOS TCC 権限フロー

macOS ではキーボードイベント傍受に TCC (Transparency, Consent, and Control) 権限が必要。

```
App起動
  │
  ▼
CGPreflightListenEventAccess()
  ├── true → CGEventTap (ListenOnly) 作成 → 成功 → Hook Active
  │
  └── false → CGRequestListenEventAccess()
              → システム設定 (Input Monitoring) を開く
              → ポーリングで Preflight 再チェック
              │
              └── ListenOnly タップ 10回連続失敗 (ad-hoc署名CDHash不安定)
                   │
                   ▼
                  AXIsProcessTrustedWithOptions(prompt: true)
                  → GCD dispatch_sync_f でメインスレッドへ dispatch
                  → Accessibility ダイアログ表示
                  │
                  ├── 付与 → CGEventTap (Default) 作成 → Hook Active
                  │         USING_ACCESSIBILITY_FALLBACK = true
                  │
                  └── 未付与 → Dashboard に手動設定ボタン表示
                              → open_accessibility_settings() で
                                System Settings を直接オープン
```

**Tauri コマンド（macOS のみ）:**
- `reset_input_monitoring()` — tccutil reset でリセット後、CGRequestListenEventAccess() を再発行
- `reset_accessibility()` — tccutil reset で Accessibility エントリをリセット
- `open_accessibility_settings()` — `x-apple.systempreferences:` URL スキームでシステム設定を直接オープン

## 8. 設計上の制約とトレードオフ

### 採用しなかった選択肢（Windows）

- **ITfThreadMgr グローバルフック**: UIPI によりブロックされるため、SetWindowsHookEx + WinEvent の組み合わせを採用
- **winapi crate**: メンテナンス停止。公式の windows crate (v0.58+) を採用
- **chrono**: 依存最小化のため手動で日時フォーマットを実装
- **tauri-plugin-store**: 現時点では設定永続化の必要が薄いため未導入（将来導入予定）
- **Clean Architecture**: モジュール数が少なく、厳格なレイヤー分離は過剰。直接的なモジュール構成を採用

### macOS 固有の設計判断

- **CGKeyCode → VK マッピング**: hook_macos.rs 内に変換テーブルを持つ。analysis 層をプラットフォーム非依存に保つための意図的な設計。マッピング精度はキーボードレイアウト（JIS/ANSI/ISO）に依存
- **GCD dispatch_sync_f**: TIS API と AXIsProcessTrustedWithOptions はメインスレッド必須（HIToolbox/AppKit 制約）。フックスレッドから dispatch_sync_f でメインキューへ同期 dispatch する。メインスレッドからの呼び出しはデッドロックするため禁止
- **IME 状態機械**: macOS では WinEvent に相当する IME イベント通知がないため、CGEventTap コールバック内の状態機械で IME_COMPOSING を追跡。シフトなし英字 → かな文字列の変換パターンを検出
- **macos-private-api**: Tauri の macos-private-api feature はオーバーレイウィンドウ動作に必要。この feature はプライベート API を使用するため、Mac App Store 配布には非対応
- **デュアル権限フォールバック**: ad-hoc 署名では TCC CDHash が不安定なため、Input Monitoring → Accessibility の自動フォールバックを実装。開発ビルドでの実用性を確保

### 許容する技術的負債

- **グローバル Atomic 変数**: Hook コールバックの制約（クロージャ不可）により、IME_OPEN / IME_ACTIVE / LAST_KEY_MS がグローバル。将来的にスレッドローカルストレージへの移行を検討
- **手動チューニング HMM**: パラメータがハードコーディング。ML モデル移行時にコンフィグファイル化が必要
- **Frontend ポーリング**: 500ms ポーリングは Tauri イベントプッシュに置換可能だが、現状のレイテンシ要件を満たしている

## 9. 拡張ポイント

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
