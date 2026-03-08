# Fix Report: Silence → Stuck 勾配緩和と Nudge 猶予時間の確保

**日付:** 2026-03-08
**対象ファイル:** `src-tauri/src/lib.rs`, `src-tauri/src/analysis/engine.rs`, `src-tauri/src/analysis/features.rs`
**関連ログ:** `gse_20260308_034634.ndjson`

---

## 1. 問題の発見経緯

セッションログ `gse_20260308_034634.ndjson`（6.1分、904キー押下）の包括的分析により、以下の技術的課題が判明した。

### 1.1 Lv1 Nudge 介入ウィンドウの不在

2つの Stuck エピソードにおいて、`p_stuck` が 0.60（Lv1 Nudge 閾値）を超えてから 0.70（Lv2 Wall 閾値）に到達するまでの猶予が **1秒未満** であった。

```
Episode 1 (+16s→+17s): p_stuck 0.5880 → 0.7148  (gap = 1秒)
Episode 2 (+16s→+17s): p_stuck 0.5879 → 0.7147  (gap = 1秒)
```

Nudge が表示されてからユーザーが行動を変える猶予がなく、即座に Wall が発動する設計上の問題。

### 1.2 完全再現パターン（決定論的軌跡）

両エピソードの数値軌跡が **完全に同一** であった。これは `make_silence_observation()` が `silence_secs` のみに依存する決定論的関数であるため。

```
+0~10s:  obs=6/7, alpha=0.15, p_stuck ≈ 0.02 (Incubation 方向)
+10s:    alpha → 0.25 に一気に昇格
+11~13s: obs=11, p_stuck = 0.03→0.06
+14s:    obs=16 にジャンプ (x_bin: 2→3), p_stuck = 0.06→0.20
+15~17s: obs=16 連続, p_stuck = 0.41→0.71 (指数的上昇)
```

### 1.3 根本原因

2つの要因の複合：

1. **F3/F6 合成摩擦の上昇勾配が急すぎる**: `lib.rs` Fix 6 の分母（F6: 25.0, F3: 30.0）が小さく、14秒付近で EWMA'd X が x_bin=2→3 の境界（0.60）を一気に超える
2. **EWMA α の 2段階ジャンプ**: 15秒で α=0.15→0.25 に一気に昇格し、obs=16（Stuck 優勢ビン）に到達後の確率上昇が加速される

---

## 2. 修正内容

### 2.1 沈黙ペナルティ（F3/F6）の上昇勾配の緩和

#### `lib.rs` Fix 6（実データ＋サイレンスパス）

```rust
// Before:
let f6_floor = ((silence_secs - 8.0) / 25.0).clamp(0.0, 0.50);
let f3_floor = ((silence_secs - 10.0) / 30.0).clamp(0.0, 0.40);

// After:
let f6_floor = ((silence_secs - 8.0) / 45.0).clamp(0.0, 0.45);
let f3_floor = ((silence_secs - 10.0) / 50.0).clamp(0.0, 0.35);
```

**効果:** 14秒時点での F6 値が 0.24→0.13 に低下し、phi6 が 0.50→0.05 に大幅減少。X 軸が x_bin=3 (Stuck 領域) に到達するタイミングが ~14s → ~25s に後退。

#### `features.rs` make_silence_observation（純粋サイレンスパス）

```rust
// Before:
let mut f6_synthetic = ((silence_secs - 8.0) / 50.0).clamp(0.0, 0.50);
let mut f3_synthetic = ((silence_secs - 15.0) / 80.0).clamp(0.0, 0.40);

// After:
let mut f6_synthetic = ((silence_secs - 8.0) / 60.0).clamp(0.0, 0.45);
let mut f3_synthetic = ((silence_secs - 15.0) / 100.0).clamp(0.0, 0.35);
```

**注意:** features.rs パスは30秒ウィンドウが完全に空の場合のみ使用される（通常の15-30秒サイレンスでは lib.rs パスが優先）。既存の onset 時間（F6: 8s, F3: 15s）とフロア値（F6 ≥ 0.15, F3 ≥ 0.20 at ≥10s）は維持。

### 2.2 沈黙時 EWMA α の 3段階化

#### `engine.rs` update_silence

```rust
// Before (2段階):
let alpha = if silence_secs >= 15.0 { 0.25 } else { 0.15 };

// After (3段階):
let alpha = if silence_secs >= 25.0 {
    0.25  // 完全に固まった状態
} else if silence_secs >= 15.0 {
    0.18  // Nudge 領域を緩やかに推移させるための中間ギア
} else {
    0.15  // 初期サイレンス
};
```

**効果:** 15-25秒区間で α=0.25→0.18 に低下。EWMA の時定数が 4秒→5.6秒に増加し、obs の x_bin 境界超え後の確率上昇速度が約28%鈍化。

---

## 3. 期待される動作変化

### Before（修正前）
```
沈黙開始 → +14s obs=16 到達 → +16s Lv1 Nudge → +17s Lv2 Wall (gap: 1秒)
```

### After（修正後、推定）
```
沈黙開始 → +20-22s obs=16 到達 → +22-24s Lv1 Nudge → +27-30s Lv2 Wall (gap: 5-8秒)
```

Nudge が表示されてからユーザーが「タイピングを再開する」「気分転換する」などの行動変容を起こす余裕が生まれる。

---

## 4. 副作用の検討

| 項目 | 影響 | 判定 |
|---|---|---|
| 通常タイピング中の HMM 動作 | 変更なし（`update()` α=0.3 は不変） | 安全 |
| Backspace ペナルティ | 変更なし（obs=25 メカニズム不変） | 安全 |
| IME ペナルティ抑制 | 変更なし（`!ime_open` ガード不変） | 安全 |
| Incubation 検出 | 沈黙初期（0-15秒）の動作は不変 | 安全 |
| 真の Stuck 検出 | 30秒以上の沈黙では引き続き Stuck に到達（α=0.25 + obs=16） | 安全、ただし到達時間が約10秒延長 |
| F5 蓄積ロジック | 変更なし（`silence_secs / 2.0` 加算は不変） | 安全 |
| features.rs フロア値 | F6 ≥ 0.15, F3 ≥ 0.20 を維持（auto-recovery 防止） | 安全 |
| Stuck からの回復速度 | 変更なし（回復は `update()` α=0.3 で処理） | 安全 |

---

## 5. 観測ビン利用率の補足

ログ分析で観測ビン利用率が 46.2%（12/26ビン使用）であることが判明した。これは今回の修正のスコープ外だが、将来的な改善候補として記録する。

使用ビン: {1, 2, 3, 4, 6, 7, 8, 10, 11, 12, 15, 16}
未使用ビン: {0, 5, 9, 13, 14, 17-24, 25}

obs=25（Backspace ペナルティ）が一度も出現しなかったのは、セッションの 71% で IME が ON であり、ペナルティが正しく抑制されたため。

---

## 6. 関連ファイル変更一覧

| ファイル | 変更内容 |
|---|---|
| `src-tauri/src/lib.rs` | Fix 6: F6/F3 フロア計算の分母を拡大、キャップ値を微調整 |
| `src-tauri/src/analysis/engine.rs` | update_silence: 2段階 α → 3段階 α (0.15/0.18/0.25)、ドキュメントコメント更新 |
| `src-tauri/src/analysis/features.rs` | make_silence_observation: F6/F3 合成摩擦の分母を拡大、キャップ値を微調整 |
| `README.md` | EWMA α 記述を3段階に更新、合成摩擦公式を更新 |
| `README.ja.md` | 同上（日本語版） |
| `CLAUDE.md` | EWMA α 記述を3段階に更新 |
