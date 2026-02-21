# GSE-Next — Generative Struggle Engine

[🇺🇸 English](./README.md) | [🇯🇵 日本語](./README.ja.md)

**GSE-Next** は Windows 向けのリアルタイム認知状態推定システムです。全アプリケーションのキーストローク動的特徴を監視し、ユーザーが **Flow（集中・生産性）**・**Incubation（思考的休止）**・**Stuck（停滞・フラストレーション）** のいずれの状態にあるかを推定します。Stuck 状態が持続した場合、アンビエントな視覚フィードバックで状態変化を促します。

コーディング・執筆などの創造的作業中に、キーストロークのマイクロ行動が認知状態の代理変数として機能するかを研究する *Generative Struggle Engine* プロジェクトの研究プロトタイプです。

---

## アーキテクチャ概要

```
┌─────────────────────────────────────────────────────────┐
│                  Windows (グローバル)                    │
│   WH_KEYBOARD_LL フック    WinEvent フック (IME)         │
└────────────┬────────────────────────┬───────────────────┘
             │ InputEvent             │ IME_ACTIVE フラグ
             ▼                        ▼
┌────────────────────────┐   ┌────────────────────┐
│  hook.rs (フックスレッド)│   │ ime.rs (IMEスレッド)│
└────────────┬───────────┘   └────────────────────┘
             │ crossbeam チャネル
             ▼
┌──────────────────────────────────────────────────┐
│           分析スレッド (lib.rs)                   │
│                                                  │
│  ┌─────────────────┐    ┌──────────────────────┐ │
│  │  features.rs    │    │    engine.rs         │ │
│  │  特徴量抽出      │───▶│  CognitiveStateEngine│ │
│  │  F1〜F6 (30秒)  │    │  HMM フォワードパス  │ │
│  └─────────────────┘    └──────────────────────┘ │
│                                    │              │
│  ┌─────────────────┐               │              │
│  │  logger.rs      │◀──────────────┘              │
│  │  NDJSON ライター │   feat イベント              │
│  └─────────────────┘                              │
└──────────────────────────────────────────────────┘
             │ Arc<Mutex<[f64;3]>>
             ▼  (500ms ごとに Tauri IPC でポーリング)
┌──────────────────────────────────────────────────┐
│           フロントエンド (React / TypeScript)     │
│                                                  │
│  App.tsx ──▶ Dashboard.tsx  (確率バー, Mist UI)  │
│          └──▶ Overlay.tsx   (Nudge / Wall UI)    │
└──────────────────────────────────────────────────┘
```

---

## 技術スタック

| レイヤー | 技術 | バージョン |
| --- | --- | --- |
| フロントエンド | React + TypeScript + Vite | React 19, TS 5.8, Vite 7 |
| バックエンド | Rust + Tauri | Tauri 2.0 |
| Windows API | `windows` クレート (Win32 + WinRT) | v0.58 |
| 非同期ランタイム | Tokio | v1 |
| スレッド間通信 | crossbeam-channel | v0.5 |
| ロギング | tracing + カスタム NDJSON ロガー | — |
| 推論エンジン | ONNX Runtime (ort) | 2.0.0-rc.0（予約済） |

---

## 特徴量抽出 — F1〜F6

すべての特徴量は、キーイベントごとに **30 秒スライディングウィンドウ** で計算されます。

| 特徴量 | 名称 | 定義 | ベースライン β |
| --- | --- | --- | --- |
| **F1** | Median Flight Time（中央 Flight Time） | 直近 5 イベントの押下間隔の移動平均（ms） | 250 ms |
| **F2** | Flight Time Variance（分散） | ウィンドウ内 FT の分散 | 2000 ms² |
| **F3** | Correction Rate（修正率） | (Backspace + Delete) / 全押下数 | 10 % |
| **F4** | Burst Length（バースト長） | 連続入力（FT < 200 ms）の平均文字数 | 2 文字 |
| **F5** | Pause Count（ポーズ回数） | 2000 ms 以上の押下間隔の数 | 3 回 / 30 s |
| **F6** | Pause-After-Delete Rate（削除後停止率） | Backspace/Delete 直後に ≥ 2 s 停止する割合 | 15 % |

**正規化:** 各特徴量は個人ベースライン正規化関数 φ で変換します:

```
φ(x, β) = clamp((x − β) / (2β), 0.0, 1.0)
```

ベースライン値は Surface Pro 8 + 日本語 IME 入力パターンに合わせてキャリブレーション済みです。

---

## 潜在軸 — Friction（摩擦）& Engagement（没入度）

単一スカラースコアの代わりに、6 つの正規化特徴量から 2 つの独立した軸を算出します。

### X 軸: Friction（0 = スムーズ → 1 = 停滞）

タイピングの「つまずき」を示す特徴量の加重和（重み合計 1.0）:

```
X = 0.30·φ(F3) + 0.25·φ(F6) + 0.25·φ(F1) + 0.20·φ(F5)
```

### Y 軸: Engagement（0 = 受動的 → 1 = 没入）

生産的な出力フローを示す特徴量の加重和（重み合計 1.0）:

```
Y = 0.40·φ(F4) + 0.35·(1 − φ(F1)) + 0.25·(1 − φ(F5))
```

HMM 更新前に各軸を独立に EWMA 平滑化（α = 0.3）します:

```
X_t = 0.3 · X_raw + 0.7 · X_{t−1}
Y_t = 0.3 · Y_raw + 0.7 · Y_{t−1}
```

**なぜ 2 軸か？** Incubation（思考ポーズ）と Stuck（停滞）はともに低エンゲージメントですが、Friction で区別できます。1 次元スコアではこれらを混同しやすい一方、Friction × Engagement 平面では明確に分離できます:

| 領域 | Friction | Engagement | 推定状態 |
| --- | --- | --- | --- |
| 低 F・高 E | 低い | 高い | **Flow** |
| 低 F・低 E | 低い | 低い | **Incubation** |
| 高 F・低 E | 高い | 低い | **Stuck** |

---

## HMM 推論エンジン

平滑化後の (X, Y) を 5 × 5 グリッド（25 の自然観測ビン）に離散化し、3 状態 HMM に入力します。26 番目のペナルティビンが Backspace 連打の強制オーバーライドを担当します。

```
x_bin = floor(X × 5).min(4)      # Friction ビン  [0..4]
y_bin = floor(Y × 5).min(4)      # Engagement ビン [0..4]
obs   = x_bin × 5 + y_bin        # 自然ビン    [0..24]
obs   = 25                        # ペナルティビン (streak ≥ 5)
```

### 遷移行列 A（文献根拠あり、Phase 1 では固定パラメータの平滑化フィルタとして使用）

|  | → Flow | → Incubation | → Stuck |
| --- | --- | --- | --- |
| **Flow** | 0.92 | 0.07 | 0.01 |
| **Incubation** | 0.10 | 0.82 | 0.08 |
| **Stuck** | 0.05 | 0.15 | 0.80 |

文献根拠:

- **Flow 持続率 (0.92):** Csikszentmihalyi (1990)。期待継続時間 = 1/(1−0.92) = 12.5 秒。
- **Incubation 持続率 (0.82):** Sio & Ormerod (2009) メタ分析。期待継続時間 = 5.6 秒。
- **Stuck 持続率 (0.80):** Hall et al. (2024)。期待継続時間 = 5.0 秒。

### 放出行列 B（3 状態 × 26 ビン）

各行は P(obs | state) を Friction × Engagement の 5×5 グリッド + ペナルティビンで表します。

```
// グリッド: x = Friction [0..4], y = Engagement [0..4], obs = x*5 + y

//                 x=0    x=1    x=2    x=3    x=4  │ penalty
//                (低F)  (低F)  (中)   (高F)  (高F) │  [25]
Flow:
  y=0 (低E)     0.01   0.01   0.00   0.00   0.00  │  0.00
  y=1           0.02   0.02   0.01   0.00   0.00  │
  y=2           0.05   0.05   0.03   0.00   0.00  │
  y=3           0.16   0.14   0.06   0.00   0.00  │
  y=4 (高E)     0.20   0.16   0.08   0.00   0.00  │

Incubation:
  y=0 (低E)     0.15   0.14   0.10   0.05   0.04  │  0.01
  y=1           0.10   0.10   0.08   0.04   0.03  │
  y=2           0.04   0.04   0.03   0.01   0.01  │
  y=3           0.01   0.01   0.01   0.00   0.00  │
  y=4 (高E)     0.00   0.00   0.00   0.00   0.00  │

Stuck:
  y=0 (低E)     0.00   0.00   0.02   0.10   0.16  │  0.99
  y=1           0.00   0.00   0.04   0.16   0.22  │
  y=2           0.00   0.00   0.02   0.07   0.12  │
  y=3           0.00   0.00   0.00   0.02   0.05  │
  y=4 (高E)     0.00   0.00   0.00   0.00   0.02  │
```

ペナルティビン 25 は **5 回以上の連続 Backspace** 検出時に有効化され、軸の値によらず P(Stuck) ≈ 1 を強制します。

---

## IME ガード（日本語入力対応）

日本語 IME 変換中の誤 Stuck 判定を防ぐ 3 段階検出:

1. **WinEvent フック（主要）** — `SetWinEventHook` で `EVENT_OBJECT_IME_CHANGE/SHOW/HIDE` をグローバル監視。`IME_ACTIVE` アトミックフラグを設定。ローマ字→ひらがな変換フェーズもカバー。
2. **EnumWindows スキャン（副次）** — IME 候補ウィンドウのクラス名（`CandidateUI_UIElement`, `IME`, `*Candidate*`）で可視ウィンドウを検索。
3. **UIAutomation（最終手段）** — フォーカス要素のロケール・クラス名を確認。

IME アクティブ中: キーストローク分析を一時停止（`set_paused(true)`）し、EWMA をリセットして状態汚染を防止。

---

## 視覚フィードバック

### Dashboard（360×480 px、常時最前面）

- Flow / Incubation / Stuck の確率をリアルタイムにバー表示
- 優位状態のラベルとカラーコーディング（緑 / 黄 / 赤）
- **Mist（霧）エフェクト**: Stuck が 30 秒以上支配的 → 半透明の赤いオーバーレイがフェードイン

### Overlay ウィンドウ（フルスクリーン、透過）

- **Nudge レイヤー**: `stuck > 0.6` → 赤いビネット表示、透明度 = (stuck − 0.6) / 0.3
- **Wall レイヤー**: Stuck が 30 秒持続 → 全画面オーバーレイ "Time to Move!" — デバイスを物理的に動かすまでブロック（WinRT 加速度センサーで検出）

---

## セッションログ

各セッションは NDJSON 形式で `Documents/GSE-sessions/gse_YYYYMMDD_HHMMSS.ndjson` に保存されます。

```jsonc
{"type":"meta","session_start":1771605721400}
{"type":"key","t":1771605742429,"vk":162,"press":true}
{"type":"feat","t":1771605742778,"f1":312.0,"f2":1820.0,"f3":0.08,"f4":3.2,"f5":1.0,"f6":0.0,
              "p_flow":0.82,"p_inc":0.14,"p_stuck":0.04}
```

アプリ終了時（`quit_app` コマンド）にロガーをフラッシュし、`behavioral_gt.py` を自動実行してセッションの後処理ラベリングを行います。

---

## ファイル構成

```text
GSE-Next/
├── src/                           # フロントエンド (React/TypeScript)
│   ├── components/
│   │   ├── Dashboard.tsx          # メインウィジェット、確率バー、Mist エフェクト
│   │   └── Overlay.tsx            # Nudge ビネット + Wall ブロッキングオーバーレイ
│   ├── App.tsx                    # ルート: 状態ポーリング、Wall タイマー、センサーイベント
│   ├── App.css                    # スタイリング、アニメーション、カラーパレット
│   └── main.tsx                   # React エントリーポイント
├── src-tauri/                     # バックエンド (Rust/Tauri 2.0)
│   ├── src/
│   │   ├── analysis/
│   │   │   ├── engine.rs          # CognitiveStateEngine — HMM, Friction/Engagement 軸, EWMA
│   │   │   └── features.rs        # FeatureExtractor — F1〜F6, φ(), 30 秒ウィンドウ
│   │   ├── input/
│   │   │   ├── hook.rs            # WH_KEYBOARD_LL + WinEvent IME フック
│   │   │   └── ime.rs             # ImeMonitor — 3 段階 IME 検出
│   │   ├── lib.rs                 # Tauri セットアップ、コマンドハンドラ、スレッド生成
│   │   ├── logger.rs              # NDJSON セッションロガー（バックグラウンドスレッド）
│   │   ├── sensors.rs             # WinRT 加速度センサー + ジオロケーション（60 Hz）
│   │   └── main.rs                # バイナリエントリーポイント
│   ├── capabilities/default.json  # Tauri 2.0 パーミッション宣言
│   ├── tauri.conf.json            # ウィンドウ設定、バンドル設定
│   └── Cargo.toml                 # Rust 依存関係
├── analysis/                      # Python 後処理スクリプト
│   ├── behavioral_gt.py           # 行動的代理変数ラベリング（F6 ベース）
│   └── hmm_sensitivity.py         # HMM パラメータ感度分析
├── package.json
├── vite.config.ts
└── tsconfig.json
```

---

## ビルドと実行

### 前提条件

- Node.js v18 以上
- Rust (stable)
- Windows SDK（Visual Studio Build Tools に含まれる）

### コマンド

```bash
# Node 依存関係のインストール
npm install

# 開発モード（ホットリロード）
npm run tauri dev

# 本番ビルド
npm run tauri build
```

出力: `src-tauri/target/release/gse-next.exe`

---

## 既知の問題

### コンパイル時のメモリ枯渇

**症状:** `rustc` が `memory allocation failed` または `STATUS_STACK_BUFFER_OVERRUN` でクラッシュする。

**原因:** `windows` クレート v0.58 のコンパイルは非常にメモリを消費します。

**回避策:**

```bash
RUST_MIN_STACK=67108864 cargo build -j 1
# 開発モードの場合:
RUST_MIN_STACK=67108864 npm run tauri dev
```

または Windows の仮想メモリ（ページファイル）を増やす:
*システムのプロパティ → 詳細設定 → パフォーマンス設定 → 仮想メモリ*

### 管理者権限について

グローバルキーボードフック（`WH_KEYBOARD_LL`）は、対象アプリケーションと同等以上の整合性レベルが必要です。昇格されたウィンドウへのフックには GSE-Next を管理者として実行してください。

---

## 変更履歴

### v2.3 — 2軸 HMM 観測モデル（Friction × Engagement）

- **観測モデルをリファクタリング:** 単一スカラー `S_stuck` を廃止し、独立した 2 軸 — **Friction**（X）と **Engagement**（Y）— に移行。Incubation と Stuck の識別精度が向上。
- **25+1 ビングリッド:** 5 × 5 の自然ビン（obs = x\_bin × 5 + y\_bin）+ Backspace 連打専用ペナルティビン（obs = 25、連打 ≥ 5 回で発動）。
- **軸別 EWMA:** `axes_ewma: (f64, f64)` で X・Y を独立に平滑化（α = 0.3 は維持）。
- **放出行列を再設計:** 3 × 11 から 3 × 26 へ。Flow は（低X・高Y）、Incubation は（低X・低Y）、Stuck は（高X・低Y）にピーク。
- **安全装置を維持:** Backspace 連打 ≥ 5 のペナルティと、遷移行列ベースのジッタ抑制は変更なし。

### v2.2 — Overlay・センサー・セッションロガー

- `Overlay.tsx` を追加（Nudge ビネット + Wall レイヤー）
- `sensors.rs` を追加（WinRT 加速度センサーによる Wall アンロック）
- `logger.rs` を追加（NDJSON セッションログ）
- `analysis/` ディレクトリを追加（`behavioral_gt.py`, `hmm_sensitivity.py`）
- 終了時: `quit_app` が `behavioral_gt.py` を自動実行しセッションフォルダを開く

### v2.1 — IME ガード & HMM 安定性修正

- **IME 修正:** UIAutomation 単体から 3 段階（WinEvent + EnumWindows + UIAutomation）検出へ変更。日本語変換中の誤 Stuck 判定を解消。
- **EWMA 平滑化**（α=0.3）を S_stuck に適用し、瞬間的なキーストロークスパイクを抑制。
- **HMM チューニング:** 初期 Flow 事前確率を 0.50→0.70 に引き上げ、Incubation 事前確率を 0.40→0.20 に引き下げ。
- **Mutex 安全性:** 全 `unwrap()` をポイズニング対応パターンマッチに置き換え。

### v2.0 — GSE-Next 初回リリース

- プロトタイプ v1 から Tauri 2.0 に移植
- 個人ベースライン正規化付き 6 特徴量抽出（F1〜F6）を実装
- 文献根拠のある遷移行列を持つ HMM を実装
- グローバルキーボードフック + WinEvent IME 検出を実装
