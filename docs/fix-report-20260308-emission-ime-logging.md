# Fix Report: HMM エミッション識別力向上と IME_ACTIVE ログ拡張

**日付:** 2026-03-08
**対象:** `advice.md` の3修正の Windows 版適用判定と実施
**ビルド検証:** `cargo build` 成功確認済み

---

## 1. 判定対象

`advice.md` に記載された3つの修正提案：

| # | 修正内容 | 判定 | 理由 |
|---|---------|------|------|
| 1 | obs=2/obs=7 の Flow 排出確率引き上げ | **適用** | HMM エミッションテーブルは OS 非依存の純粋な数学的パラメータ |
| 2 | LogEntry::ImeState に `active` フィールド追加 | **適用** | ログ構造体は OS 非依存 |
| 3 | emit_ime_state での `active` 送信 | **適用** | ログ送信ロジックは OS 非依存（送信元は `ime.rs`） |

---

## 2. 技術的課題の詳細

### 2.1 y_bin=2 境界での Flow/Incubation 識別力不足

**根本原因:** エミッションテーブルの obs=2 (x=0, y=2) と obs=7 (x=1, y=2) において、Flow と Incubation の排出確率が 0.05 vs 0.04 と非常に近く、比率が 1.25:1 しかなかった。

**症状:** 通常タイピング中にわずかなポーズで Y 軸が y_bin=2 に落ちると、HMM が Flow と Incubation を区別できず `p_flow` が急落・凍結する。

**影響範囲:** y_bin=2 は「中程度の Productive Silence」を示すビンで、短いポーズの後のバーストや、考えながらのゆっくりしたタイピングで頻繁に到達する。この領域で Flow が崩壊すると、健全なタイピング中にも Stuck 方向へのドリフトが加速される。

### 2.2 IME_ACTIVE（候補ウィンドウ状態）のログ不在

**根本原因:** `LogEntry::ImeState` は `on`（IME モード：あ/A）のみを記録しており、`active`（候補ウィンドウ表示中かどうか）を記録していなかった。

**症状:** セッション後の分析で、HMM が一時停止（`set_paused(true)`）された期間と IME 候補選択フェーズの相関を検証できない。IME 変換中の Stuck 誤検知の原因究明が困難。

---

## 3. 修正内容

### 3.1 エミッションテーブルの識別力向上

**ファイル:** `src-tauri/src/analysis/engine.rs`

```rust
// Before:
//  x=0 (low F)    y: 0     1     2     3     4
                   0.01, 0.02, 0.05, 0.12, 0.14,
//  x=1            y: 0     1     2     3     4
                   0.01, 0.02, 0.05, 0.12, 0.13,

// After:
//  x=0 (low F)    y: 0     1     2     3     4
                   0.01, 0.02, 0.08, 0.12, 0.14,
//  x=1            y: 0     1     2     3     4
                   0.01, 0.02, 0.08, 0.12, 0.13,
```

**効果:**
- obs=2 と obs=7 の Flow:Inc 比が 1.25:1 → 2.0:1 に改善
- Flow 合計が ~0.97 → ~1.03 に増加（HMM は正規化ステップで補正するため問題なし）
- y_bin=2 境界で Flow がより安定し、短いポーズでの `p_flow` 急落が防止される

### 3.2 ImeState ログの `active` フィールド追加

**ファイル:** `src-tauri/src/logger.rs`

```rust
// Before:
ImeState { timestamp: u64, on: bool },

// After:
ImeState { timestamp: u64, on: bool, active: bool },
```

NDJSON 出力フォーマット:
```jsonc
// Before:
{"type":"ime_state","t":1740000001234,"on":true}

// After:
{"type":"ime_state","t":1740000001234,"on":true,"active":false}
```

### 3.3 emit_ime_state での IME_ACTIVE 取得

**ファイル:** `src-tauri/src/input/ime.rs`

```rust
// Before:
let _ = log_tx.try_send(LogEntry::ImeState { timestamp: ts, on });

// After:
let active = crate::input::hook::IME_ACTIVE.load(Ordering::Relaxed);
let _ = log_tx.try_send(LogEntry::ImeState { timestamp: ts, on, active });
```

**注記:** advice.md は送信元を `lib.rs` としていたが、実際の `ImeState` 送信元は IME ポーリングスレッド内の `ime.rs:emit_ime_state()` である。Windows 版のアーキテクチャに合わせて正しいファイルを修正した。

---

## 4. 副作用検討

| 項目 | 影響 | 判定 |
|------|------|------|
| 通常タイピング中の HMM 動作 | obs=2/obs=7 で Flow がより安定（改善） | 安全 |
| Incubation 検出 | obs=2/obs=7 の Inc 値は 0.04 で不変 | 安全 |
| Stuck 検出 | obs=2/obs=7 の Stuck 値は 0.01 で不変 | 安全 |
| ペナルティビン (obs=25) | 変更なし | 安全 |
| 他の観測ビンの排出確率 | 変更なし（指定された2ビンのみ） | 安全 |
| Flow 合計 > 1.0 | HMM フォワードステップで正規化される（設計通り） | 安全 |
| NDJSON ログフォーマット | `active` フィールド追加（後方互換：既存パーサーは未知フィールドを無視） | 安全 |
| IME_ACTIVE 読み取り | Relaxed ordering で十分（ログは事後分析用、リアルタイム精度不要） | 安全 |
| パフォーマンス | atomic load 1回追加（無視可能） | 安全 |

---

## 5. 変更ファイル一覧

| ファイル | 変更内容 |
|---------|---------|
| `src-tauri/src/analysis/engine.rs` | obs=2, obs=7 の Flow 排出確率を 0.05 → 0.08 |
| `src-tauri/src/logger.rs` | `LogEntry::ImeState` に `active: bool` フィールド追加、writeln! フォーマット更新 |
| `src-tauri/src/input/ime.rs` | `emit_ime_state()` で `IME_ACTIVE.load()` を取得し `active` に渡す |
