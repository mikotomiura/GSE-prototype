# Fix Report: Stuck確率の構造的5%頭打ち問題の修正 (v2.18)

**日付:** 2026-03-09
**対象バージョン:** v2.17 → v2.18

---

## 問題の概要

ログ分析により、`p_stuck`（Stuck確率）が構造的に**5%前後で頭打ち**となり、介入（Nudge/Wall）が発動しない重大な欠陥が判明。Nudge発動閾値（p_stuck > 0.60）・Wall発動閾値（p_stuck > 0.70）に到達することが不可能な状態だった。

## 根本原因

### 1. 摩擦（Friction）ペナルティの上限が低すぎる

`f6_floor`（削除後停止率）と `f3_floor`（修正率）の `clamp` 上限が、それぞれ **0.45** と **0.35** に制限されていた。これらの値では φ 正規化後の X（Cognitive Friction）が x_bin=3〜4（Stuck支配領域）に十分到達できず、HMMのStuck放射確率が低いままだった。

| パラメータ | 修正前 | 修正後 |
|---|---|---|
| f6_floor（lib.rs） | `clamp(0.0, 0.45)`、分母45 | `clamp(0.0, 1.0)`、分母30 |
| f3_floor（lib.rs） | `clamp(0.0, 0.35)`、分母50 | `clamp(0.0, 1.0)`、分母40 |
| f6_synthetic（features.rs） | `clamp(0.0, 0.45)`、分母60、オンセット8s | `clamp(0.0, 1.0)`、分母40、オンセット10s |
| f3_synthetic（features.rs） | `clamp(0.0, 0.35)`、分母100 | `clamp(0.0, 1.0)`、分母50 |

### 2. 沈黙検知の初動が遅い

推論ループにおいて、通常パス（α=0.30）から沈黙パス（α=0.15）への切り替え閾値が **5秒** だった。この間、stale なウィンドウデータが α=0.30 で繰り返しHMMに入力され、Incubation にロックインしていた。

| パラメータ | 修正前 | 修正後 |
|---|---|---|
| 通常→沈黙パス閾値（lib.rs） | `silence_secs < 5.0` | `silence_secs < 2.0` |

### 3. エミッションテーブルの崖効果

Incubation (State 1) の x=1 行において、y=1 の放射確率が **0.10** と高く、obs=2（Flow優位）から obs=6（Incubation優位）への遷移が急激だった。

| パラメータ | 修正前 | 修正後 |
|---|---|---|
| Incubation x=1 y=1 | 0.10 | 0.08 |

---

## 修正ファイルと変更箇所

### `src-tauri/src/lib.rs`

1. **Line 416:** `silence_secs < 5.0` → `silence_secs < 2.0`（沈黙パスの早期起動）
2. **Line 430:** `((silence_secs - 8.0) / 45.0).clamp(0.0, 0.45)` → `((silence_secs - 8.0) / 30.0).clamp(0.0, 1.0)`
3. **Line 431:** `((silence_secs - 10.0) / 50.0).clamp(0.0, 0.35)` → `((silence_secs - 10.0) / 40.0).clamp(0.0, 1.0)`

### `src-tauri/src/analysis/features.rs`

1. **make_silence_observation():** f6_synthetic の式を `((silence_secs - 8.0) / 60.0).clamp(0.0, 0.45)` → `((silence_secs - 10.0) / 40.0).clamp(0.0, 1.0)` に変更
2. **make_silence_observation():** f3_synthetic の式を `((silence_secs - 15.0) / 100.0).clamp(0.0, 0.35)` → `((silence_secs - 15.0) / 50.0).clamp(0.0, 1.0)` に変更
3. `silence_secs >= 10.0` 条件下の `max(0.15)` / `max(0.20)` フロア保証は維持

### `src-tauri/src/analysis/engine.rs`

1. **エミッションテーブル:** Incubation (State 1) x=1 行の y=1 を `0.10` → `0.08` に変更

---

## デグレッション防止チェック

以下の保護対象ロジックが変更されていないことを確認済み：

- [x] IME_ACTIVE のログ出力ロジック（v2.17）
- [x] ポーズ解除直後のバッファクリア `reset()`（v2.17）
- [x] 3段階 EWMA α の遷移ロジック（0.15 → 0.18 → 0.25）
- [x] `features.rs` が純粋な数学モデルであること（OS固有コードなし）
- [x] ペナルティビン（obs=25）の確率
- [x] y_bin=3 のエミッション確率

---

## 期待される効果

修正後の合成摩擦の時系列（features.rs、F5 飽和時）:

| 沈黙時間 | F3_合成 | F6_合成 | 到達予想 |
|---|---|---|---|
| 10s | 0.20 | 0.15 | Incubation |
| 20s | 0.20 | 0.25 | 境界域 |
| 30s | 0.30 | 0.50 | Stuck 移行開始 |
| 40s | 0.50 | 0.75 | Stuck |
| 50s | 0.70 | 1.00 | Deep Stuck |

- **Stuck到達時間:** ~50秒 → ~30秒に短縮
- **Nudge（Lv1）発動:** p_stuck が 0.60 を超えるようになる
- **Wall（Lv2）発動:** p_stuck が 0.70 を持続的に超えるようになる
- **沈黙パスの早期起動（2秒）:** stale データによる Incubation ロックインを防止

---

## ビルド確認

```
cargo build — OK (no warnings, no errors)
```
