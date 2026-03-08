# Fix Report: macOS 修正レポートの Windows 版適用判定・移植サマリー

**日付:** 2026-03-08
**対象:** 2件の macOS 修正レポートの Windows 版適用判定と実施
**ビルド検証:** `cargo build` 成功確認済み

---

## 1. 判定対象レポート

| # | レポート | ファイル |
|---|---------|---------|
| 1 | `fix-report-20260308-silence-stuck-gradient.md` | Silence → Stuck 勾配緩和と Nudge 猶予時間の確保 |
| 2 | `fix-report-20260308-frontend-and-hook-resilience.md` | フロントエンド介入ライフサイクル修正 & イベントドロップ検知 |

---

## 2. 判定結果一覧

### レポート1: Silence → Stuck 勾配緩和（全3件）

| 修正箇所 | 判定 | 理由 |
|---------|------|------|
| lib.rs: F6/F3 フロア計算の分母拡大 | **適用** | HMM 分析ロジックはプラットフォーム非依存の純粋な数学処理 |
| engine.rs: EWMA α の 3段階化 | **適用** | 同上。沈黙検出後の確率上昇速度制御はOS非依存 |
| features.rs: 合成摩擦パラメータ緩和 | **適用** | 同上。純粋サイレンスパスの obs 計算はOS非依存 |

### レポート2: フロントエンド & フック復元力（全4件）

| 修正箇所 | 判定 | 理由 |
|---------|------|------|
| App.tsx: ポーリングガード統一 | **適用** | React/TypeScript はクロスプラットフォーム。オーバーレイのセッション前ポーリング問題は Windows でも同一 |
| App.tsx: IPC 失敗時の安全側フォールバック | **適用** | Tauri IPC はクロスプラットフォーム。バックエンドクラッシュ時の Wall 誤発動リスクは Windows でも同一 |
| hook.rs: イベントドロップ時の警告ログ | **適用** | macOS の `hook_macos.rs` と同一の `let _ = sender.try_send(event)` パターンが Windows の `hook.rs` にも存在 |
| hook_macos.rs: IME_OPEN Acquire オーダリング | **非適用** | macOS 固有のコンポジション状態マシンのパターン。Windows の `hook.rs` では VK_KANJI トグルが同一スレッド内で完結しており `Relaxed` が正しい |

---

## 3. 技術的課題の詳細と修正内容

### 3.1 Silence → Stuck 勾配が急すぎる問題

**根本原因:** 沈黙ペナルティ（F3/F6 合成摩擦）の上昇分母が小さく、14秒付近で EWMA'd X が x_bin=2→3 の境界を一気に超え、Lv1 Nudge から Lv2 Wall までの猶予が1秒未満だった。さらに EWMA α が15秒で 0.15→0.25 に一気にジャンプし、確率上昇が加速されていた。

**修正:**

#### lib.rs — Fix 6（実データ＋サイレンスパス）
```rust
// Before:
let f6_floor = ((silence_secs - 8.0) / 25.0).clamp(0.0, 0.50);
let f3_floor = ((silence_secs - 10.0) / 30.0).clamp(0.0, 0.40);

// After:
let f6_floor = ((silence_secs - 8.0) / 45.0).clamp(0.0, 0.45);
let f3_floor = ((silence_secs - 10.0) / 50.0).clamp(0.0, 0.35);
```

#### engine.rs — update_silence EWMA α
```rust
// Before (2段階):
let alpha = if silence_secs >= 15.0 { 0.25 } else { 0.15 };

// After (3段階):
let alpha = if silence_secs >= 25.0 { 0.25 }
       else if silence_secs >= 15.0 { 0.18 }
       else { 0.15 };
```

#### features.rs — make_silence_observation（純粋サイレンスパス）
```rust
// Before:
f6_synthetic: /50.0, clamp 0.50 | f3_synthetic: /80.0, clamp 0.40

// After:
f6_synthetic: /60.0, clamp 0.45 | f3_synthetic: /100.0, clamp 0.35
```

**期待効果:** Nudge→Wall 間の猶予が1秒 → 5-8秒に拡大。ユーザーが行動変容を起こす余裕が生まれる。

---

### 3.2 オーバーレイのセッション前ポーリング

**根本原因:** オーバーレイウィンドウはセッション開始前から常時ポーリングを実行していた（`windowLabel !== "overlay"` 条件で除外されていたため）。

**修正:**
- ポーリングガードを `if (!isStarted) return;` に統一
- `handleStart()` で `emit("session-started")` を発行
- オーバーレイ側に `listen("session-started")` を追加し `isStarted` を同期

---

### 3.3 IPC 失敗時の Wall 誤発動リスク

**根本原因:** catch ブロックが `console.error` のみで、IPC 失敗時に前回の高い stuck 値が維持され、Wall 累積カウンターが不正に加算され続ける。

**修正:** catch ブロックで状態を安全側にリセット:
```typescript
catch (e) {
  console.error("Failed to fetch state:", e);
  setCognitiveState({ flow: 1.0, incubation: 0.0, stuck: 0.0 });
  stuckAccumMsRef.current = 0;
}
```

---

### 3.4 イベントドロップの無警告消失

**根本原因:** `hook.rs` の `let _ = sender.try_send(event)` でチャネル満杯時のイベントドロップが完全に無視されていた。

**修正:** `tracing::warn!` でドロップを記録:
```rust
if let Err(e) = sender.try_send(event) {
    tracing::warn!("InputEvent dropped (channel full): {}", e);
}
```

---

## 4. 非適用の修正とその理由

| 修正 | 理由 |
|------|------|
| hook_macos.rs: IME_OPEN `Relaxed` → `Acquire` | macOS の CGEventTap コールバック内のコンポジション状態マシンが JIS キー処理の `Release` ストアを確実に読む必要があったもの。Windows の `hook.rs` では VK_KANJI トグルは `hook_callback` 同一スレッド内で load→store が完結しており、`Relaxed` が正しい（同一スレッド内では CPU のメモリモデルにかかわらず自スレッドの書き込みは常に可視）。 |

---

## 5. 副作用検討（全修正の総合評価）

| 項目 | 影響 | 判定 |
|------|------|------|
| 通常タイピング中の HMM 動作 | 変更なし（`update()` α=0.3 は不変） | 安全 |
| Backspace ペナルティ | 変更なし（obs=25 メカニズム不変） | 安全 |
| IME ペナルティ抑制 | 変更なし（`!ime_open` ガード不変） | 安全 |
| Incubation 検出 | 沈黙初期（0-15秒）の動作は不変 | 安全 |
| 真の Stuck 検出 | 30秒以上の沈黙では引き続き Stuck に到達。到達時間が約10秒延長 | 安全 |
| Stuck からの回復速度 | 変更なし（回復は `update()` α=0.3 で処理） | 安全 |
| メインウィンドウのポーリング | 変更なし（既に isStarted で制御） | 安全 |
| オーバーレイの Nudge/Wall 表示 | セッション開始後のみ動作（設計通り） | 安全 |
| IPC 一時的障害 | 次回成功時に正しい値に復帰 | 安全 |
| Wall 累積タイマー | IPC 失敗時はリセットにより誤発動防止 | 安全 |
| hook コールバック性能 | warn! は失敗時のみ発火（通常パスは分岐1つ追加のみ） | 安全 |

---

## 6. 変更ファイル一覧

| ファイル | 変更内容 |
|---------|---------|
| `src-tauri/src/lib.rs` | F6/F3 フロア計算の分母拡大（25→45, 30→50）、キャップ値微調整 |
| `src-tauri/src/analysis/engine.rs` | update_silence: 2段階 α → 3段階 α (0.15/0.18/0.25) |
| `src-tauri/src/analysis/features.rs` | make_silence_observation: F6/F3 合成摩擦の分母拡大（50→60, 80→100）、キャップ値微調整 |
| `src-tauri/src/input/hook.rs` | try_send 失敗時の tracing::warn! 追加 |
| `src/App.tsx` | ポーリングガード統一、session-started イベント発行/購読、IPC 失敗フォールバック |
