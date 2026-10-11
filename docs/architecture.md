# 技術設計書

## 1. アーキテクチャ概要

### 全体図

```
┌──────────────────────────────────────────────────────────────┐
│                       Tauri 2.0 App                          │
│                                                              │
│  ┌──────────────┐    ┌──────────────┐                        │
│  │ Main Window  │    │   Overlay    │   React 19 / TS        │
│  │ (Dashboard)  │◄──►│   (Nudge)    │   500ms polling        │
│  └──────┬───────┘    └──────┬───────┘                        │
│         │    Tauri IPC      │    Tauri Events                │
│ ════════╪═══════════════════╪════════════════════════════════│
│         ▼                   ▼                                │
│  ┌──────────────────────────────────┐        Rust Backend    │
│  │         Tauri Commands           │                        │
│  │  get_cognitive_state, get_*      │                        │
│  │  get_intervention_decision       │                        │
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
│    │  └────────┬─────────┘   │                               │
│    │  ┌────────▼─────────┐   │                               │
│    │  │ Intervention     │   │  Need + Opportunity + Policy  │
│    │  │ Policy State     │   │  cooldown / cap / defer       │
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
└──────────────────────────────────────────────────────────────┘
```

> ⚠️★★★ **2026-08-23: `wall_server.rs`（QR → Phone → Zen Timer → POST の tiny_http サーバー）は
> 全削除された**（**ADR-015 D1**）。★ 図からも外してある。
> ★ **PC ↔ スマホの境界を作り直す場合の設計は `docs/adr/ADR-017-expression-channel-boundary.md`**
> （★ PC → スマホの一方向イベント / ⚠️ **PC 側に常設の LAN リスナを置かない**）。

### 採用したパターン

- **アーキテクチャパターン**: マルチスレッド・イベント駆動 + レイヤードモジュール構成
- **採用理由**: キーボードフックは OS 制約により専用スレッド必須。1Hz 推論と入力収集の分離により、フックコールバックのレイテンシを最小化。Tauri の IPC が自然なレイヤー境界を提供。
- **トレードオフ**: Clean Architecture のような厳格な依存方向ルールは採用していない。モジュール数が少なく（input, analysis, logger）、過度な抽象化よりも直接的な実装を優先。

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
| ~~HTTP サーバー~~ | ~~tiny_http~~ | — | ⚠️ **2026-08-23 に依存ごと削除**（ADR-015 D1） |
| ~~QR コード~~ | ~~qrcode + base64~~ | — | ⚠️ **2026-08-23 に依存ごと削除**（ADR-015 D1） |
| 非同期ランタイム | tokio | full features | Tauri 内部ランタイム。将来の重い I/O・ML 推論タスクで活用予定 |
| ログ | tracing + tracing-subscriber | 0.3 | 構造化ログ |
| エラーハンドリング | anyhow | — | アプリケーションレベルのエラー伝搬 |
| 将来: ML 推論 | ONNX Runtime | — | 学習済みモデルのクロスプラットフォーム推論 |

## 3. スレッドモデル

GSE は 8 つのスレッド/タスクで構成される (★ G1 モード時のみ 2 つ増える。⚠️ **Cloak Resolver は Windows のみ**)。

| スレッド | 責務 | 通信方式 | 優先度 |
|---|---|---|---|
| **Main (Tauri)** | UI イベントループ、IPC ハンドラ | Mutex<Engine> 読み取り | 通常 |
| **Hook** | Win: WH_KEYBOARD_LL + WinEvent / mac: CGEventTap + CFRunLoop | crossbeam Sender, Atomic flags | 高（OS 制約） |
| **Analysis** | 1Hz 特徴量抽出 + HMM 推論、最新 FeatSnapshot 更新 | crossbeam Receiver, Mutex<Engine> 書込 | 通常 |
| **IME Monitor** | Win: 候補ウィンドウ検出 / mac: フック内で処理（別スレッド不要） | Atomic IME_ACTIVE | 低 |
| **IME Polling** | Win: ImmGet\* / mac: TIS ポーリング (GCD メインキュー経由) | Atomic IME_OPEN | 低 |
| **Cloak Resolver** | ★ **Windows のみ**。`EVENT_OBJECT_CLOAKED`/`UNCLOAKED` を受け、ウィンドウクラスを解決して (完全一致 `IME`) `IME_ACTIVE` を駆動する。⚠️ フックコールバックでは `GetClassNameW` を呼べない (`hook-constraints` Win-1) ための分離。畳み込みは `input/ime_cloak.rs` (OS 非依存) | `CLOAK_EVENT_TX` (bounded 256), Atomic IME_ACTIVE / IME_SHADOW_\* | 低 |
| **Logger** | NDJSON バッファリング + フラッシュ | Bounded channel (512) | 低 |
| **Probe Scheduler** | v0.3 較正: ランダム時点プローブの一様時刻生成 (Poisson+thinning) → `probe_assignment` ログ + `probe_triggered` emit。純ロジックは `analysis/probe_scheduler.rs` (OS API 非依存) | Atomic SESSION_START_MS 読取, LogEntry Sender, AppHandle emit | 低 |
| **G1 Block End** | ★ **G1 モード時のみ起動**。`g1::BLOCK_DURATION_MS` (5 分) でブロックの記録を終了し、`BlockEnd` 送信 + `g1-block-ended` emit | Atomic SESSION_START_MS / ANALYSIS_IDLE, LogEntry Sender, AppHandle emit | 低 |
| **G1 Duplicate Check** | ★ **G1 モード時のみ・起動 1 回**。他の GSE プロセスを OS に問い合わせ (`pgrep` / `tasklist`)、居れば `second-instance-blocked` emit | AppHandle emit | 低 |

⚠️★★★ **2026-08-23: `IME_ACTIVE` は推論を止めない (記録のみ)。**
★ 旧設計は「IME 候補ウィンドウ表示中は HMM 推論を一時停止する」だったが、
⚠️ 実測でこの信号は**候補リスト表示ではなく変換セッション全体**(ローマ字入力〜確定)を
覆うと分かった。→ ★ pause すると日本語論述の推定窓が **約 56〜60%** 消える
(⚠️ 実データ fixture `phase1_ime_heavy` では **94%**)。
→ ★ 研究者判断で `lib.rs` と `analysis/loop_step.rs` の両方から `set_paused` を外した
(`HMM_VERSION` 0.4.0 → **0.5.0**)。詳細は
`.steering/20260823-ime-active-cloak-rewiring/decisions.md` D-10。

純スケジューリング (指数間隔・thinning・窓計算・不透明 ProbeId 生成) は `analysis/probe_scheduler.rs` に隔離し OS API を呼ばない。スレッド起動・実時刻取得・emit・hotkey 配線は `lib.rs` 側に閉じる (architecture-rules)。

⚠️★★★ **2026-08-23 削除**: 旧文「Wall Server は Lv2 介入時にのみ起動する一時的なスレッド」は
`wall_server.rs` の全削除により無効（ADR-015 D1）。★ **現行に一時起動スレッドは無い。**

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
IME Monitor ── Atomic IME_ACTIVE ─────────────────────►│ (記録のみ)
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
Analysis Thread ── LatestFeatState ──► Tauri Command ──► analysis::intervention
Analysis Thread ── LogEntry channel ──► Logger Thread ──► disk (.ndjson)
```

## 4. 主要コンポーネント

### 4.1 input::hook — キーボードフック

- **責務**: OS レベルのキー入力捕捉、IME モード変更検出
- **依存先**: Win: windows crate / mac: core-graphics, core-foundation, ApplicationServices (FFI)
- **インターフェース**: `InputEvent` 構造体を Sender 経由で送信
- **状態管理**: グローバル Atomic 変数
  - 共通: IME_OPEN, IME_ACTIVE, LAST_KEY_MS, HOOK_ACTIVE
  - Windows 追加 (Phase 2b): IME_COMPOSITION_START_MS, IME_SHADOW_DWELL_MS, IME_CANDIDATE_NAV_COUNT, IME_SHADOW_ABANDON, IME_SHADOW_READY
  - macOS 追加: IME_COMPOSING, JIS_KEYBOARD_SEEN, CALLBACK_COUNT, CONSECUTIVE_TAP_FAILURES, USING_ACCESSIBILITY_FALLBACK
- **設計判断**: Relaxed ordering for LAST_KEY_MS（近似的な直近値で十分）、Acquire/Release for IME 状態（スレッド間可視性保証）。Phase 2b の IME Shadow atomics は IME_SHADOW_READY の Release/Acquire がフェンスとして機能し、他の shadow atomics の Relaxed store を可視にする
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

- **責務**: 特徴量 → 行動シグナル由来の作業状態スコア推定。Flow / Incubation / Stuck は脳内状態の直接分類ではなく、Need 判定に使う参考確率として扱う
- **依存先**: analysis::features, **analysis::heads**（§4.4b）
- **インターフェース**: `new_for_domain()`, `set_domain()`, `head_id()`, `update()`, `update_silence()`, `register_keystroke()`, `state_probs()`
- **状態管理**: HMM 内部状態（forward 確率、EWMA 軸値、display_probs、**走行中の head**）を Mutex で保護

### 4.4b analysis::heads — ドメイン推論ヘッド（ADR-002 / ADR-006・2026-08-18 追加）

- **責務**: β baseline を所有し、特徴量から潜在二軸 (X=Friction / Y=Engagement) を算出する。
  **どの head を走らせるかは宣言された `task_kind` が決め**、`ime_open`（観測）は
  Writing head 内部の within-writing 信号として使う（両者の役割は直交する）
- **依存先**: analysis::features のみ（OS API 非依存）
- **構成**:
  - `DomainInferenceHead` trait — `head_id()` / `latent_axes()` / `applies_backspace_penalty()`
  - `WritingHead` — `β_writing`（IME on）/ `β_writing_latin`（IME off・旧 `β_coding` の改名）
  - `CodingHeadV0` — `β_coding` シードを `ime_open` に関わらず適用（主信号の coding イベントは Epic 4）
  - `TaskDomain` / `head_for()` — ルーティング表（`_ =>` 禁止で網羅性をコンパイラに強制）
- **データフロー**: `logger::TaskKind` → `TaskDomain`（変換は `logger.rs` の `From` 1 本のみ）
  → `head_for()` → `CognitiveStateEngine::set_domain()`。
  ⚠️ 本番（`lib.rs::record_session_meta`）とリプレイ（`bin/replay.rs`）が**同じ変換経路**を通ることが、
  ゴールデンによる回帰保護が成立する前提である
- **記録**: 実際に走った head は `session_meta` の `head_id` に残る。
  ⚠️ `FeatSnapshot` には入れない（ゴールデン snapshot が壊れるため）

### 4.5 analysis::intervention — Opportunity MVP

- **責務**: Need (`p_stuck`) と Opportunity (`idle_ms`, F3/F4/F6, cooldown, daily cap, recent dismiss) を統合し、`none` / `nudge` / `defer` を返す
  （⚠️ **2026-08-23 訂正**: `wall` action と Monk Mode は削除された — ADR-015 D1 / D2。★ **ACT = `{nudge}`**）
- **依存先**: なし（純粋な計算）。OS API、Tauri、logger には依存しない
- **インターフェース**:
  - `InterventionPolicyState::decide(input) -> DecisionResult`
  - `InterventionPolicyState::record_dismiss(action, now_ms)`
  - `InterventionDecision` は Tauri IPC で Frontend に返され、NDJSON `intervention_decision` としても記録される
- **状態管理**: Tauri state の `InterventionState(Arc<Mutex<InterventionPolicyState>>)` が cooldown / daily cap / last decision を保持する
  （⚠️ **2026-08-23 訂正**: `wall_accum_ms`（Wall 累積時間）は削除 — ADR-015 D1）
- **MVP パラメータ**: Nudge `p_stuck >= 0.60`, Nudge cooldown 10 分, Nudge cap 6/day
  （⚠️ **2026-08-23 訂正**: Wall の閾値 6 種 / cooldown / daily cap は削除 — ADR-015 D1）
- **設計判断**: Main Window の `get_intervention_decision` 呼び出しだけが policy state を進める。Overlay Window は `last_decision` を読み取るだけにし、2 つの WebView による cooldown / cap の二重進行を防ぐ

### 4.6 ⚠️★★★ wall_server — **削除済み**（2026-08-23・ADR-015 D1）

- ⚠️★★★ **`src-tauri/src/wall_server.rs` は存在しない。**
  ★ 旧責務（Lv2 介入の HTTP サーバー + QR コード生成 + スマートフォン連携・`start()` / `stop()` ・
  Windows Defender ファイアウォールルール管理）は**すべて削除された**。依存 `tiny_http` / `qrcode` も外した。
- ⚠️ **PM-D11 が Physical Anchor の運搬路として再利用する前提だった経路であり、その前提は覆っている**
  （ADR-015 D4）。
- ★ **PC ↔ スマホの境界を作り直す場合の設計は `docs/adr/ADR-017-expression-channel-boundary.md`**:
  **PC → スマホの一方向の抽象状態イベント**（`level` / `seq` / `emitted_at` のみ・`level` 変化時だけ発火）で、
  ⚠️ **inbound の「歩いた」二値経路を第 1 版で作らない**／⚠️ **PC 側に常設の LAN リスナを置かない**。
  ★ 表現チャネル全体は `docs/architecture/expression-channel.md`。
- ⚠️★★★ **削除済みの LAN HTTP サーバを無審査で復活させない**（ADR-017 D4）。

### 4.7 logger — セッションロガー

- **責務**: イベント + 状態の NDJSON 永続化
- **依存先**: serde_json
- **インターフェース**: `log()` → channel 送信、`flush()`, `close()`
- **状態管理**: バッファリングチャネル（512 エントリ）、5 秒間隔フラッシュ
- **耐障害化 + fail-loud (#1 層2)**: `SessionLogger::start` は **spawn 前に書込先を同期確定**する（`open_log_target`）。
  primary（`GSE_DATASET/raw/<id>` or `~/Documents/GSE-sessions`）が `File::create` 失敗時は **temp**
  （`$TMPDIR/GSE-sessions/<pid>_<name>`）へフォールバックし、それも失敗したら `io::sink()` へ縮退する。
  いずれの場合も consumer スレッドは生かし続け、channel を Disconnected にしない（= `record_*` IPC が
  Err を返してプローブ/Nudge カードが閉じなくなる #1 を構造的に防ぐ）。書込先の状態は
  `LogStatus { Ok | Fallback | Disabled }` として返され、`get_log_status` IPC 経由で Dashboard が
  **fail-loud バナー**を常時表示する（静かな全損を撲滅）。NDJSON はキーストローク動態を含むため unix では
  `file=0600` に制限する。詳細は `data-privacy` Skill / `.steering/20260626-phase1-card-repro-backend-fix/`。
- ★ **G1 ローテート (2026-08-05)**: `LogEntry::BlockEnd` (現ファイルに `session_end` を書いて閉じる)
  と `LogEntry::Rotate { new_path }` (旧ファイルを閉じ、新ファイルを **新ファイルの実時刻の `meta`** で開く)
  を追加。★ **閉じるのと開くのを分けてある**——ブロック終了時に新ファイルを開くと
  10 ブロック目の後に `meta` 1 行だけの 11 本目が残り、`gse-submit` (最新 1 本を選ぶ) が
  空ファイルを提出してしまうため。開くのは次の `start_session` だけ。
  `block_closed` フラグにより `session_end` は **1 ファイルにつき 1 行**になる。
  書込先は `SharedLogTarget = Arc<Mutex<LogTarget{path,status}>>` で共有し、
  ⚠️ ローテート先が temp に落ちたときも `get_log_status` の fail-loud バナーが追随する。
  ⚠️ ファイル名は秒粒度なので `unique_path_from` が **logger スレッド内で**衝突を避ける
  (前ブロックの `truncate` による静かな全損の防止)。
- **Phase 1 バリアント**: `LogEntry::UserLabel { timestamp, label, recovered_at }` を追加。meta 行に `hmm_version` を埋め込む
- **Phase 2b バリアント**: `LogEntry::ImeShadow { timestamp, dwell_ms, candidate_nav_count, abandon }` を追加 (Windows のみ)。IME Monitor スレッドが active→false 遷移時に emit。HMM には統合しない
- **GSE v2 MVP バリアント**: `LogEntry::InterventionDecision { timestamp, action, need_score, opportunity_score, p_stuck, idle_ms, reason, suppressed_by }` を追加（⚠️ **2026-08-23 に `wall_accum_ms` を削除** — ADR-015 D1・NDJSON schema の破壊的変更として gse-dataset と parity 同期済み）。固定カテゴリと数値のみを記録し、本文・Unicode 文字・ウィンドウタイトルは含めない
- **v0.3 較正バリアント**: `LogEntry::ProbeAssignment` (プローブ時刻の監査記録) / `LogEntry::ReviewMarker` / `LogEntry::SessionMeta` (track/task_kind 宣言・セッション開始 UI) / `LogEntry::RealtimeLabel` (Q1/Q2 プローブ回答・**アプリ内 ProbeCard 経由**で `record_realtime_answer` から emit) は production で emit される (NDJSON で着地を確認済み)。一方 `LogEntry::VignetteResponse` (尺度理解テスト) は **schema (`schema_dto`) と format 関数・テストには存在するが、UI 経路が未配線でまだ emit されない**。いずれも schema drift check の対象に含まれる

### 4.8 Ground Truth ラベリング経路 (Phase 1)

- **責務**: ユーザーの主観的認知状態を NDJSON に記録し、Dashboard にリアルタイム可視化する
- **コンポーネント**:
  - `lib.rs::record_label_internal` — 共通ヘルパー。2 秒デバウンスを `AtomicU64::compare_exchange` で race-free に実装 (Tauri コマンド経路とグローバルホットキー経路の衝突を構造的に排除)
  - `lib.rs::record_user_label` — Tauri コマンド。`UserLabelKind::parse` で whitelist バリデーション (flow / incubation / stuck のみ)
  - `tauri-plugin-global-shortcut` プラグイン — 以下のホットキーを `setup()` で `app.global_shortcut().register()`:
    - `⌘⇧⌥ F/I/S` (macOS) / `Ctrl+Shift+Alt+F/I/S` (他) — 3 値の自覚ラベル (`user_label`)
    - `⌘⇧⌥ R` / `Ctrl+Shift+Alt+R` — レビューマーカー (`review_marker`、1 秒デバウンス)
    - `⌘⇧⌥ M` / `Ctrl+Shift+Alt+M` — 自己マーカー (v0.3、`probe_triggered` を `source: "self_marker"` で emit。希少な深い Stuck の副データ)
  - Dashboard `listen<{label, timestamp}>("user_label_recorded", ...)` — Tauri event を購読して counter state 更新
- **プライバシー制約**: UserLabel は `{flow, incubation, stuck}` の 3 値 enum + サーバー側 timestamp のみ。キーストローク文字内容は一切含まない

### 4.9 analysis::metrics — GT × FeatSnapshot 集計 (Phase 1)

- **責務**: UserLabel と HMM 推定結果を突き合わせ、混同行列・F1・中央値を算出する純粋関数群
- **インターフェース**:
  - `compute_session_metrics(labels: &[UserLabelEvent], feats: &[FeatSnapshot]) -> SessionMetrics`
  - `compute_pflow_exit_at(stuck_ts, feats, window_ms, p_flow_threshold) -> Option<u64>` — Stuck ラベル後に p_flow > 0.5 に達する最初の時刻を返す (オフライン後付け算出)
  - `format_pretty(m: &SessionMetrics) -> String`
- **計算ロジック**:
  - `argmax_class` のタイブレークは Flow > Incubation > Stuck の固定順
  - `nearest_feat` は ±1 秒窓でラベル時刻に最も近い FeatSnapshot を取得
  - `detection_lead_ms` は ±60 秒窓で同クラス argmax の最近傍 feat との差 (正 = HMM 先行)
  - Macro F1 は固定分母 3 (scikit-learn 互換)、Micro F1 = accuracy (matched labels のみ)
- **範囲ラベル (Phase 1 GT 改善)**:
  - `RangeLabel { start_ms, end_ms, label }` — セグメント区間全体にラベルを適用
  - `compute_range_metrics(range_labels, feats)` — 区間内の全 feat と比較し confusion matrix を構築。1 ラベルから N 個の feat-label ペアが生成され、統計検出力が点ラベルの約 30 倍
  - detection_lead / stuck_recovery は範囲ラベルでは算出しない (区間全体がラベルのため)
- **consume 側**: `bin/replay.rs::main` が `--metrics` / `--segments` フラグ検知時に呼ぶ

### 4.10 schema_dto + emit_schema — JSON Schema 生成 (Phase 1)

- **責務**: NDJSON 形式の JSON Schema を Rust 型から機械生成し、gse-dataset repo との drift を CI で検知
- **コンポーネント**:
  - `schema_dto::LogEntryDto` — `LogEntry` の `schemars::JsonSchema` 派生専用ミラー型 (production path 不干渉)
  - `bin/emit_schema` — `schema_for!(LogEntryDto)` の出力を stdout に pretty JSON で吐く
  - `src-tauri/schema/current.json` — 機械生成ゴールデンコピー (手編集禁止、`.gitattributes` で LF 固定)
  - CI ジョブ `check` が `emit_schema > /tmp/emitted.json && diff schema/current.json /tmp/emitted.json` で drift 検知
- **gse-dataset 同期**: 手動コピー (`cp src-tauri/schema/current.json /path/to/gse-dataset/schema/current.json`)

### 4.11 沈黙 3 状態機構（Silence 3-State Mechanism）

1Hz 推論ゲートにおける特徴量計算と HMM 更新は、**バッファの状態と沈黙秒数に応じて 3 つのパス**に分岐する。各パスで使用する EWMA α・摩擦フロア適用有無・呼び出す engine メソッドが異なる。分散実装 (`lib.rs` 分析スレッド + `features.rs::make_silence_observation` + `engine.rs::update_silence`) のため、全体像を以下に集約する。

#### 3 パスの定義

| パス名 | 発動条件 | engine 呼び出し | EWMA α | 摩擦フロア (Phase 2a) |
|--------|---------|----------------|--------|-----------|
| **TypingPath** | バッファ実データあり (f1 > 0) かつ `silence < 2s` | `update()` | 0.3 | なし。`pre_silence_features` をキャプチャ |
| **TransitionPath** | バッファ実データあり (f1 > 0) かつ `silence ≥ 2s` | `update_silence()` | 0.15 / 0.18 / 0.25 | 文脈あり: `ctx × time_scale` (線形、onset 8s / ramp 30s)。文脈なし: 従来フロア |
| **SilencePath** | バッファ空 (f1 = 0) かつ `silence ≥ 2s` | `update_silence()` | 0.15 / 0.18 / 0.25 | 文脈あり: `ctx + t(1-ctx)ctx` (非線形、onset 2s / ramp 30s)。文脈なし: 従来フロア |

いずれの条件にも該当しない（`silence < 2s` かつ `f1 = 0`、データ不足）場合は推論スキップ。

#### TransitionPath と SilencePath のフロア閾値差

Phase 2a で**比例キャリーフォワード方式**を導入。TypingPath 通過時に `pre_silence_features` をキャプチャし、沈黙中の F3/F6 合成に直前の摩擦文脈を反映する。文脈なし時 (セッション冒頭) は従来の時間ベースランプにフォールバック。

| パラメータ | TransitionPath (`loop_step.rs`) | SilencePath (`features.rs::make_silence_observation`) |
|------------|-----------------------------------|--------------------------------------|
| **文脈あり式** | `ctx × time_scale` (線形) | `ctx + time_scale × (1-ctx) × ctx` (非線形増幅) |
| onset | **8s** | **2s** |
| ramp | 30s | 30s |
| **フォールバック** (文脈なし) | F6 onset 8s / F3 onset 10s (≥10s でフロア 0.15/0.20) | F6 onset 10s / F3 onset 15s (≥10s でフロア 0.15/0.20) |

TransitionPath はバッファに実データがあるため onset を遅め (8s) にし、線形でバッファ値を補完するフロアとして適用。SilencePath はバッファ空のため onset を早め (2s) にし、非線形増幅で長時間沈黙の Stuck 移行を加速する。

#### 意図的に統合していない理由

2 つのパスは実装上似ており統合の誘惑があるが、GSE では**明示的に統合を避けている**:

1. **統合リスク > 保守利益**: 既存の挙動はゴールデンセッションで動作確認済み。統合リファクタは微妙な挙動変化のリスクが大きい
2. **責務の違い**: TransitionPath は「打鍵を見た直後の沈黙」、SilencePath は「純粋な無入力」を扱う。閾値差はこの意味論の違いを反映している
3. **原則 D (Keep What Works, Rename What's Confusing)**: コード削減自体を目的化しない。名前と文書で可読性を確保する

統合しない判断の詳細根拠は `.steering/20260414-improvement-roadmap/decisions.md` §3 を参照。

#### 拡張時の注意

Phase 2a で比例キャリーフォワード方式を導入済み (HMM_VERSION 0.3.0)。`pre_silence_features` を TypingPath でキャプチャし、TransitionPath / SilencePath で F3/F6 文脈フロアとして使用する。両パスの式・onset は**独立に維持する**こと（統合禁止）。設計詳細は `.steering/20260416-phase2a-synthetic-friction/design.md` を参照。

### 4.12 g1 — G1 統制タスク実験モード (2026-08-05)

- **責務**: 「いま G1 統制タスク実験の実施中か」**だけ**を判定する。効果の適用は `lib.rs` が行う
- **依存先**: なし (std のみ。`current_exe()` とプロセス列挙以外は純関数)
- **引き金 2 本** (`experiments/20260801-controlled-friction-task/preregistration.md §5.4-5`):
  - `marker` — 実行ファイルを**包むフォルダ**に `g1.mode` がある (配布形。mac は exe の 4 階層上 / Windows は 1 階層上)
  - `env` — `GSE_G1_MODE=1` (開発・検証用)
- ⚠️ ★ **起動時に 1 回だけ読み `OnceLock` に固定する。実行時トグルにしない。**
  プローブスケジューラは「スレッドごと起こさない」ことで「発火はしたが黙殺した」状態を
  構造的に消しており、実行時に切り替えられるとその性質が崩れる
- **G1 モードで起きること** (いずれも既定では起きない):
  1. プローブスケジューラを起こさない (★ 既存の `GSE_DISABLE_PROBES=1` は**無変更**。OR で足しただけ)
  2. `start_session` 2 回目以降でログをローテート (1 ブロック = NDJSON 1 ファイル)
  3. 5 分でブロックの記録を自動終了 (⚠️ **残り時間は出さない**。時間圧を入れないため)
  4. 二重起動を検出して画面に出す
  5. `meta` 行に `"g1_mode":"marker"|"env"` を刻む ＋ スタート画面に「G1 モードで動作しています」
- ⚠️ ★ **マーカーは `.app` の中に置けない**——実測で `codesign --verify --strict` が
  `a sealed resource is missing or invalid` になる。置き場所はバンドルの外だけである
- **非回帰**: G1 モードでないとき `meta` 行は従来と **byte-identical**
  (ゴールデンスナップショットと既存フィクスチャがこれに依存)
- ★ **例外**: `tauri-plugin-single-instance` だけは**通常運用にも効く**
  (2 個同時起動は Phase1 でも打鍵を 2 本の NDJSON に割る不具合なので、止めるほうが正しい)。
  ⚠️ ただしプラグインを持たない**旧ビルドとは共存する**ことを実測済みで、
  G1 モードではプロセス名の検査で二重化してある
- 詳細: `.steering/20260805-g1-app-mode-and-log-rotation/`

### 4.13 submission + reconcile — G1 提出物の収束型自動提出 (2026-08-08)

- **責務**: G1 実施中に、**被験者が提出の操作を 1 回もしなくても** ID 付きの `.age` が
  研究者へ届くようにする。`requirement.md` のゴールは「操作せずに届く」だが、
  ★ 守っている本体は **「データを失わない」** である
- **層の分かれ方** (⚠️ ★ **盲検アプリ本体に `age` も HTTP も載せない**・decisions D3):

  | モジュール | feature | 何を持つか |
  |---|---|---|
  | `submission.rs` | ★ **gate の外** | 提出物の**状態の規約**だけ (`.age` / `.sent` / 台帳 / 参加者 ID / 送信先設定のパスと名前)。アプリ本体も未送信件数を数えるため |
  | `reconcile.rs` | `package` | 収束器の本体 (走査・採番・匿名化+暗号化の呼び出し・送信・`.sent`) と `Uploader` trait |
  | `bin/submit.rs` | `package` | `--reconcile` / `--input` の入口 |
  | `lib.rs` | default | ★ **収束器を子プロセスで起こすだけ**。Tauri CSP を 1 文字も触らない |

- **★ 収束型 (reconciler) である** — 「いま何をすべきか」をイベントから決めず、
  毎回ディスクの状態を突き合わせて足りない仕事だけをする:

  ```
  ① 閉じ終わった NDJSON  … session_end を持つ、いま書いていないファイル
  ② それに対応する .age   … 無ければ作る (匿名化 → age 暗号化)
  ③ それに対応する .sent  … 無ければ送る (成功したら .sent を置く)

  未送信 N 件 = ② が在って ③ が無いものの数   ← ★ 別カウンタを持たない
  ```

- ⚠️★★ **イベント駆動にしなかった理由**: `preregistration.md §3.6` がブロックの事後除外を
  禁じているので、★ **1 ブロックの取りこぼしが回復不能な損失**になる。
  P-1 は 2 回とも「その瞬間に取るべき動作を取り損ねた」型で失敗した。
  → ★ 収束型では **取りこぼしという概念が無く、「再送」という特別処理も要らない**
- **起動のきっかけは 2 つとも「ヒント」**: ブロックの自動終了時 / アプリ起動時。
  ★ どちらを取りこぼしても次の機会に収束する。何度走らせても安全 (べき等)
- ⚠️ ★ **ブロック中には走らせない** (測定中の端末に余計な仕事をさせない)。
  ブロック終了時は、logger の `LogChannel::block_end_rx` で
  **`session_end` が書かれたことを観測してから**起こす (固定 sleep を使わない)
- **送信先**: GAS Web App → 研究者の Drive (`Form_G1/GSE_G1_Submit.gs`)。
  ★ 実測に基づく制約 — POST は **302 を返す**のでリダイレクト追従が必須 (メソッド強制は 405)、
  GAS の `e` に**ヘッダが無い**ので認証は**本文**、⚠️ **HTTP 200 は成功の証拠にならない**
  (GAS は例外でも 200)。→ ★ **`{"ok":true}` の明示応答を要求する**
- ⚠️★ **送信の成否は送信先から追えない** (実行数ページはログ本文を出さず Cloud ログも開けない・実測)。
  → ★ 端末側の `.sent` が唯一の真実源であり、**未送信件数の画面表示は必須の安全装置**である
- **止め方**: 配布フォルダの `g1-submit.json` を外すと ② までで止まる
  (`.age` はローカルに貯まる)。★ **再ビルド不要**・研究者側にだけあるスイッチ (decisions D-4)
- 詳細: `.steering/20260806-g1-auto-submit-on-block-end/`

### 4.14 o1 — O1 (R3-a) 自然作業の常時収集モード (2026-08-27)

- **責務**: 「いま O1 の収集中か」を判定し、**そのモードでだけ変わる方針**を純関数で持つ。
  効果 (門を通す / インジケータ / 宣言でのローテート / 猶予つき自動提出) の適用は
  `lib.rs` と `reconcile.rs` が行う。★ **`g1.rs` と同層・同じ流儀**である
- **依存先**: `g1`(階層計算の再利用) と `input::liveness`(テストのみ)。⚠️ OS API を呼ばない
- **引き金 2 本** (`g1.rs` の写し):
  - `marker` — 実行ファイルを**包むフォルダ**に **`o1.mode`** がある (配布形)
  - `env` — **`GSE_O1_MODE=1`** (開発・検証用)
- ⚠️★★★ **G1 とは相互排他である** —— 両方のマーカーがあると `o1::resolve` が
  **G1 を勝たせて O1 を落とす** (★ `preregistration.md §3.6` がブロックの事後除外を禁じており、
  G1 の 1 ブロックは取り返しがつかないため)。⚠️ 起動そのものは止めず `tracing::error!` で残す
- **O1 モードで起きること** (いずれも既定では起きない):

  | # | 何が変わるか | ★ なぜ |
  |---|---|---|
  | 1 | ⚠️★★★ **分析スレッドの門を通す** (`o1::analysis_gate_open`) | ★ 「開始する」を押さないと **打鍵だけが静かに欠け**、⚠️ **計器の欠損が「非打鍵区間」に化ける** (ADR-016 判断 4b-0) |
  | 2 | ⚠️★★★ 稼働中インジケータと `liveness` が **`recording_active` (= `!paused`)** を見る | ★ `session_active` は永久に false なので、放置すると「**記録しているのに『記録していません』**」と出て**同意文書 §4 の逐語と矛盾**し、`starved_ms` は**永久に 0** = フック死を検出できない |
  | 3 | ★ 介入を出さない (`INTERVENTION_ENABLED = false`) | ★ 判断 O1-5。⚠️ **既定は `true`** なので何もしなければ出る |
  | 4 | ★ スタート画面を出さず、宣言は `RecordingControls` から行う | ⚠️ 押させると `record_session_meta` が走り **未宣言を表せなくなる** (判断 4b-3) |
  | 5 | ★ 宣言 1 回 = **ローテート → `engine.reset()` → `session_meta`** (`lib.rs::o1_rotate`) | ⚠️ ローテートしないと `gse-replay` が「相異なる `task_kind` が 2 つ」で `Err`。⚠️ reset しないと新ファイル先頭 30 秒が前ファイルに依存する |
  | 6 | ★ **24 時間で日次ローテート** | ⚠️ `session_end` は Rotate / BlockEnd(G1) / 終了でしか書かれず、★ **閉じないファイルは提出候補にならない** |
  | 7 | ★ ファイル名が **`gse_o1_<ts>.ndjson`** になる | ⚠️ `schema` を変えずに O1 を識別する唯一の手段 (下記) |
  | 8 | ★ 提出は **`session_end` から 48 時間の猶予**の後・**承認なし** | ⚠️ 猶予は「**包む前**」に効かせる (下記) |

- ⚠️★★★ **なぜ `meta` 行ではなくファイル名で O1 を表すのか**: `g1_mode` と同じく
  `meta` 行に刻むほうが強いが、それは `schema_dto.rs` → `schema/current.json` の変更を伴い
  **gse-dataset の parity 更新**が要る。★ 本実装は「schema を 1 バイトも変えない」制約下で作った。
  ⚠️ **失敗様式は同等に fail-loud** —— マーカーが外れれば `gse_<ts>.ndjson` になり、
  **提出候補から外れて研究者に届かない** (無音でデータが増えることはない)。
  → ★ 研究者へ返す論点として `.steering/20260827-o1-collection-enablement/decisions.md` R-1 に記録
- ⚠️★★★ **48 時間の猶予は「削除保証」を守るための機構である** (`data-privacy` ルール 6):
  `delete_time_range` → `redact_dir` は **ローカルの `gse_*.ndjson` だけ**を書き換え、
  **`.age` は対象外**。→ ★ **包んだ時点で呼び戻せない**ので、猶予は **② 包む**ところに置く
  (③ 送信ではない)。⚠️ **48 時間は repo に無い恣意的な値**であり、後から動かさない
- **非回帰**: O1 モードでないとき、上の 8 つは **1 つも起きない**。
  ★ 分岐はすべて `o1::*` の純関数の中に閉じており、非 O1 では `session_active` と**同値**である
- 詳細: `.steering/20260827-o1-collection-enablement/` / ADR-014 D6・D8 / ADR-016 判断 4b

### EH3 の層（招待と肖像・2026-10-11）

EH3 のモード（O1 の上でだけ立つ・`eh3.rs`）のときだけ動く。EH3 でないときの記録と挙動は変わらない。

| 層 | 置き場 | スレッド | 記録 |
|---|---|---|---|
| 日の割り当て | `eh3.rs`（OS 非依存） | 分析スレッド（その日の最初の打鍵で数える。起動・一時停止からの再開・日次の切り替えの後にもその日の行を出し直す） | `eh3_day` |
| 招待 | `analysis/invitation.rs`（状態機械・応答を入力に持たない）→ `lib.rs` の `InvitationRunner`（1 秒ごと）→ overlay の図像（`get_invitation_state` を poll） | 分析スレッド | `invitation_present`（時刻だけ） |
| 肖像 | `analysis/portrait/`（何を出すか）→ `lib.rs` の `PortraitRunner`（1 秒ごと）→ 壁紙のスレッド（`wallpaper.rs` ＋ `wallpaper_{windows,macos}.rs`） | 分析スレッド → 壁紙のスレッド（Windows は COM の STA・macOS はメインスレッドへ依頼） | 記録しない（R-P9） |
| 電源の通知 | `input/power_{windows,macos}.rs` | OS のコールバック（`try_send` だけ） | 記録しない |

- 肖像の「終わり」は終了・スリープの直前・4:00 の区切り、「始まり」は起動・復帰・その日を数えた時点。終了の待ち合わせは固定の長さ（2 秒）でバックグラウンドのスレッドで行う（待ち時間から本人の操作が読めないように）。
- EH3 では probe と自己申告のカードを止め、GSE の窓への遷移を `focus_transition` に書かない。

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

### フロー 2: Opportunity 判定と Lv1 Nudge 介入

> ⚠️★★★ **2026-08-23 改訂**: 旧フローは **Lv2 Wall**（QR → Zen Timer → `POST /unlock`）を記述していたが、
> **ADR-015 D1 / D2 で Wall・Monk Mode・`wall_server.rs` を全削除**した。★ **現行の介入は Lv1 Nudge のみ**である。

1. Analysis Thread が 1Hz で `FeatSnapshot` を生成し、`LatestFeatState` に保持
2. Main Window が 500ms ごとに `get_intervention_decision` を invoke
3. Rust が `p_stuck` / `idle_ms` / F3/F4/F6 / cooldown / daily cap を `analysis::intervention` に渡す
4. `InterventionPolicyState` が Need + Opportunity + Policy を評価し、`none` / `nudge` / `defer` を返す
5. `intervention_decision` を NDJSON に記録（action / need_score / opportunity_score / suppressed_by）
6. action が `nudge` の場合、Overlay がメタ認知質問を**非ブロックで**表示する
   （⚠️ **クリック透過・自動消失**。★ 画面を塞がない）
7. ユーザーの dismiss / 無操作を `intervention_response` として記録する
   （⚠️ **`elapsed_ms` を書く経路は Wall 削除で無くなり、現状 production では常に `null`** — ADR-015 Consequences）
8. ⚠️ **Physical Anchor は未実装**（★ 段階呼称 Lv3/Lv4 は ADR-018 D7 で廃止方向）。★ 第 1 版の境界の形は **ADR-017 D3** が確定している
   （PC → スマホの一方向イベント / inbound を作らない / ⚠️ **完了条件は課さない** —— ADR-018 D1 で
   既決 D11 条件 2「完了条件は時間・往復」は取り下げ済み）

### フロー 3: Ground Truth ラベル記録 (Phase 1)

1. ユーザーがホットキー (`⌘⇧⌥ F/I/S` on macOS) を押す
2. `tauri-plugin-global-shortcut` のハンドラが fire、modifier + Code マッチで `UserLabelKind` を決定
3. `record_label_internal(log, label)` を呼び出し、`AtomicU64::compare_exchange` で 2 秒デバウンス (Tauri コマンド経路と同じヘルパーを共有)
4. デバウンス通過時: `SystemTime::now()` で timestamp 付与、`log_tx.try_send(LogEntry::UserLabel { timestamp, label, recovered_at: None })`
5. logger スレッドが 5 秒フラッシュ間隔で NDJSON に書き出し (`format_user_label_line`)
6. `app.emit("user_label_recorded", {label, timestamp})` で Tauri event 発火
7. Dashboard の `listen<...>` ハンドラが state 更新 → counter widget 再レンダリング
8. デバウンス失敗時: `tracing::warn!("debounced")` のみ、UI 変化なし

### フロー 4: `gse-replay --metrics` によるオフライン集計 (Phase 1)

1. 開発者が `cargo run --bin gse-replay -- <session.ndjson> --metrics [--json]` を実行
2. `parse_args` が `--metrics` / `--snapshot` の排他、`--json` が `--metrics` 必須を検証
3. `collect_logged_feats` が NDJSON を読み `{"type":"feat",...}` 行を `FeatSnapshot` として抽出 (production が wall-clock で書いた値を source of truth とする)
4. `collect_user_labels` が NDJSON を 2 度目に開き `{"type":"user_label",...}` 行を抽出
5. `analysis::metrics::compute_session_metrics` が以下を算出:
   - `nearest_feat` で各ラベルに対応する FeatSnapshot を取得 (±1 秒窓)
   - `argmax_class` で推定クラスを決定 (Flow > Inc > Stuck のタイブレーク)
   - 混同行列に加算、警告は `warnings` Vec に集約
   - `detection_lead_ms` を ±60 秒窓内の最近傍同クラス feat で計算
   - Stuck ラベルは `compute_pflow_exit_at` で p_flow > 0.5 到達時刻を探す
6. `format_pretty` または `serde_json::to_string_pretty(&metrics)` で出力
7. 開発者が出力を `gse-dataset/metrics/P000/<os>/` にコピーして commit (UC-GT3)

> **Note (2026-04-16)**: フロー 4 step 3 は以前 `run_replay` による step() 再実行で FeatSnapshot 列を生成していたが、virtual-clock tick と label の wall-clock 時刻が揃わず label 近接の feat を取りこぼすバグ (`.steering/20260416-replay-feat-alignment-bug/`) が顕在化。`collect_logged_feats` に切替済み。`run_replay` は `--snapshot` / デフォルト JSON 出力 (step() 決定論検証) 用途に残している。

### フロー 4b: `gse-replay --calibration` による v0.3 較正解析 (Task D・オフライン)

1. 開発者が `cargo run --bin gse-replay -- <s1.ndjson> [s2.ndjson ...] --calibration [--json]` を実行 (1 被験者の複数セッションを時刻順)
2. `parse_args` が全モード排他と `--calibration` の可変長 positional (≤`MAX_CALIBRATION_FILES`)・`--json` 条件を検証
3. 各ファイルで `load_calibration_session` が 1 パスで `session_meta`(track) / `probe_assignment`(件数) / `realtime_label`(→`ProbeRecord`) / `vignette_response`(→`VignetteRecord`) を抽出 (未知 enum・範囲外 q1/q2 は件数のみ warn で skip)、X/Y 源の `feat` は `collect_logged_feats` を再利用
4. `analysis::calibration_eval::compute_calibration_metrics` が以下を算出:
   - **時間隔離窓** (t−31s..t−1s) の `feat` を `AggSpec`(既定 ewma 中央値) で X/Y 集約 (probe 後窓は不使用 D-8)
   - **前向き holdout**: 先頭 2 セッション = 較正・残り = 評価 (§8)。C-index は評価セッションのみ
   - **方向付き C-index** (X↔Q1 / Y↔Q2)、**2段ゲート**、**MNAR 上下限**、**ビネット採点**、**二軸性**、Recall は withheld
   - `track=exploratory` は主指標から除外 (§1.3)
5. `format_calibration_pretty` または `serde_json::to_string_pretty(&report)` で出力 → `gse-dataset/metrics/P*/<os>/`
6. 被験者**横断**の最終 Go/Kill 判定 (`model_gate`/`measurement_gate` は純関数として実装済) と実データ評価は Task E

> **Note**: 既存 `metrics.rs` の confusion/precision/recall は v0.2 流のため流用せず (D-14)、C-index 系は独立モジュール `calibration_eval.rs` に実装。`ReplayEvent` に較正 4 variant を追加したが `timestamp()==None` で snapshot 経路 (`run_replay`) からは除外され、既存スナップショット回帰に影響しない。

### フロー 5: JSON Schema 生成と CI drift 検知 (Phase 1)

1. 開発者が `logger::LogEntry` を変更 (例: Phase 2b で `ImeShadow` バリアント追加)
2. `schema_dto::LogEntryDto` を同期して mirror 型を更新
3. `cargo run --bin emit_schema > src-tauri/schema/current.json` で生成物を更新
4. gse-dataset 側に `cp src-tauri/schema/current.json /path/to/gse-dataset/schema/current.json`
5. 両 repo で commit + push
6. CI (`.github/workflows/ci.yml` の `check` ジョブ) が両 OS で `emit_schema` を走らせ、
   `diff src-tauri/schema/current.json /tmp/emitted.json` で drift を検知
7. drift がある場合 CI FAIL — 開発者が forgot-sync を発見して対応

## 6. 外部システム連携

| システム | 連携方式 | 認証 | 失敗時の挙動 |
|---|---|---|---|
| Win: Keyboard Hook | WH_KEYBOARD_LL (SetWindowsHookEx) | なし（OS 権限） | フック登録失敗 → 推定不能、アプリは起動 |
| mac: CGEventTap | core-graphics CGEventTap | TCC Input Monitoring or Accessibility | 権限未付与 → ポーリング再試行、10 回失敗で Accessibility フォールバック |
| Win: IME API | ImmGetOpenStatus, WinEvent | なし | フォールバック検出（VK_DBE_\* → polling） |
| mac: TIS API | TISCopyCurrentKeyboardInputSource (Carbon) | なし | dispatch_sync_f で main GCD queue に dispatch（HIToolbox 制約） |
| mac: TCC System | CGPreflight/CGRequest, AXIsProcessTrusted | OS 権限 | tccutil reset でリカバリ可能。Dashboard に TCC リセットボタンあり |
| ~~Wall Server (Phone)~~ | — | — | ⚠️★★★ **2026-08-23 に削除**（ADR-015 D1）。★ 再設計は ADR-017 |
| ~~Win: Defender Firewall~~ | — | — | ⚠️ **Wall Server と共に削除**（ADR-015 D1） |
| ファイルシステム | std::fs (NDJSON ログ) | なし | 書き込み失敗 → ログドロップ、推定継続 |
| Win: Global Shortcut | `tauri-plugin-global-shortcut` (RegisterHotKey) | Capabilities 2 件 | 登録失敗 → `tracing::warn!` で継続、GT ラベリングなしでも動作維持 |
| mac: Global Shortcut | `tauri-plugin-global-shortcut` (Carbon RegisterEventHotKey) | Capabilities 2 件 | 同上 |
| **gse-dataset repo** (Phase 1) | git push/pull (`metrics/P*/<os>/*.metrics.json`) | GitHub 認証 | push 失敗 → ローカル保持、次回同期。生 NDJSON は絶対に repo に置かない |
| **JSON Schema sync** (Phase 1) | 手動コピー (`cp src-tauri/schema/current.json gse-dataset/schema/`) | — | CI drift check が両 repo の非整合を機械的にブロック |
| **G1 自動提出** (2026-08-08) | HTTPS POST (`gse-submit --reconcile` → GAS Web App → 研究者 Drive) | 本文の共有シークレット (⚠️ GAS の `e` にヘッダが無いためヘッダ認証は不可能・実測) | ★ `.age` はローカルに残り `.sent` が付かない → **次の機会に自動で送り直す**。未送信件数をスタート画面に表示 (fail-loud)。⚠️ 送るのは `.age` のみで生 NDJSON の経路は存在しない |
| 学習データ収集 (Phase 2+) | 未定 (gse-dataset 経由 or 別) | オプトイン同意 + 匿名化 | Phase 2 ML 訓練時に設計再検討 |

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
- **IME 状態機械**: macOS では WinEvent の IME 窓イベントに相当する、アプリを問わない IME イベント通知が見つかっていないため (⚠️ 2026-10-05 訂正: アプリが Accessibility で出す変換の通知はあるがアプリしだいで、使うかは未決・`survey-input-channels.md §7.5`)、CGEventTap コールバックが受け取るキーコード列の状態機械で IME_COMPOSING を追跡。シフトなし英字 → かな文字列の変換パターンを検出
  - ⚠️★★★ **2026-09-11 (issue 008): 判断の置き場所が変わった。** 状態機械の本体は `input/ime_compose.rs` (**OS 非依存**) にあり、`hook_macos.rs` は `ime_compose::drive` を呼ぶ 1 行だけになった。★ `hook_macos.rs` の `#[cfg(test)] mod tests` は **Windows では 1 行も走らない**ため、判断をあちらに置くと「確定 / 放棄を分ける規則」を**どちらの OS の CI も検証しない**状態になる (`ime_cloak.rs` と同じ理由で `#[cfg]` を付けない)
  - ★ この状態機械が **`ime_shadow` 行を macOS でも出す**ようになった。⚠️ **由来は Windows と違う** —— Windows の `dwell_ms` は窓イベントの観測値、macOS は打鍵からの推定値である (`nav` / `abandon` は両 OS とも打鍵由来)。★ 由来は `meta` 行の OS と `capabilities` 宣言で判別する。⚠️ 両 OS のデータを混ぜて学習・評価してはならない (`survey-input-channels.md §3.2`)
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

### Physical Anchor（未実装）

> ⚠️★★★ **2026-09-01 訂正 —— 見出しから段階呼称「Lv3/Lv4」を外した**（ADR-018 D7）。
> ★★★ **ADR-018 D1 / D2: 系は開始も完了も判定しない。** Physical Anchor が提示するのは
> **「いま画面から離れる」という方向づけ（invitation）**であり、
> **時間長・往復回数・再開のタイミングに系の側の閾値を置かない。**
> ⚠️★★★ **タイマー・カウントダウン・残り時間表示を実装しない**
> （★ これらは閾値を持たないと表示できず、持った瞬間に D1 が崩れる）。
> ★ **「離席候補区間があり、復帰した」は観測としては残す**が、**完了判定には使わない**（ADR-018 D3）。
> ⚠️ UI・表現層・ログのいずれにも `completed` / `achieved` / `達成` に相当する語を置かない。

- **概要**: **画面から離れることへの方向づけ**として**離席・歩行という身体的回帰**を促す。⚠️ **本フェーズでは未実装**
  （★ Phase1 の実体は **WoZ ＋ 自己申告**）。
- ⚠️★★★ **2026-08-30 訂正**: 旧文「**Wall Server の拡張、または独立サービスとして実装**」は無効である
  —— ★ `wall_server.rs` は ADR-015 D1 で削除され、**Physical Anchor は運搬路を失っていた**（ADR-015 D4）。
- ★ **境界の形は ADR-017 が確定した**:
  **PC → スマホの一方向の抽象状態イベント**（`level` / `seq` / `emitted_at` / **`epoch`**・`level` 変化時だけ発火）。
  ⚠️★★★ **2026-09-01 訂正 —— 契約は 4 フィールドである。** 旧文は `epoch` を落としていたが、
  **`epoch` が無いと再接続時に「欠落 / 巻き戻り / リプレイ / 再起動」を区別できない**（ADR-017 D2・S6）。
  ⚠️ **inbound の「歩いた」二値経路は第 1 版で作らない** ——
  ⚠️★★★ **2026-09-01 訂正: 根拠を ADR-018 D4 で書き換えた。**
  旧根拠は「完了条件が『時間・往復』（既決 D11 条件 2）なのでセンサの量が要らない」だったが、
  **既決 D11 条件 2 は ADR-018 D1 で取り下げられた**。
  ★ **新しい根拠: 完了判定を置かない ＝ センサが寄与しうる判定が存在しない**（＝ 要る余地が構造的に無い）。
  ★ **結論は不変で、むしろ再燃しなくなる**（旧根拠は完了条件が変われば再燃した）。
- ⚠️★★★ **量（歩数・距離・速度）を本人にも表現層にも渡さない**（典拠は **ADR-017 D10**。
  ⚠️ 既決 D11 条件 1「量は二値のみ」は ADR-018 D1 で**失効（moot）**した —— 量そのものを扱わなくなったため）。
  ⚠️ **歩行を MhD の観測に入れない**（既決 D10・合流点は表現層）。
- ⚠️★★★ **位置情報は `data-privacy` に規定が入るまで実装しない**（ADR-017 D9・★ 2026-08-30 実測で規定ゼロ）。
- ★ 詳細: `docs/adr/ADR-017-expression-channel-boundary.md` / `docs/architecture/expression-channel.md` /
  `.claude/skills/physical-anchor/SKILL.md`。
