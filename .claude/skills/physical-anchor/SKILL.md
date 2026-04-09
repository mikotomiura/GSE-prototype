---
name: physical-anchor
description: >
  GSE の Lv3/Lv4 介入である Physical Anchor の設計規則。Flutter アプリとの連携・
  歩数/移動距離/歩行速度の計測設計・Wall Server からの拡張パターン。
  Physical Anchor 機能を設計する・Flutter 連携プロトコルを実装する・
  歩数センサー API を組み込むときに必須参照。以下の状況で必須参照:
  - Flutter アプリと Tauri バックエンドの通信プロトコルを設計するとき
  - 歩数・移動距離・歩行速度の計測 API を選定・実装するとき
  - Lv3 (軽度の身体活動) / Lv4 (積極的な外出) の介入ロジックを設計するとき
  - wall_server.rs を Physical Anchor 用に拡張するとき
  - Flutter の pedometer / geolocator プラグインを使うとき
allowed-tools: Read, Grep, Glob, Edit
---

# Physical Anchor 設計規則

## このスキルの目的

GSE のストレッチゴールである Lv3/Lv4 介入（身体的活動の促進）を
一貫したアーキテクチャで実装するための設計規則を定義する。
現時点では Wall (Lv2) が最高介入レベルだが、将来の拡張に備えてここに仕様を記録する。

## 適用範囲

### 適用するもの
- Flutter アプリ（Physical Anchor クライアント）の設計
- `wall_server.rs` の Physical Anchor 拡張
- 歩数・移動距離・速度の計測 API 設計

### 適用しないもの
- 現行の Wall (Lv2) / Zen Timer の実装（→ intervention-design Skill）

---

## 介入レベル定義

| レベル | 名称 | トリガー | 目標活動 | 完了条件 |
|---|---|---|---|---|
| Lv2 | Wall + Zen Timer | p_stuck > 0.70 × 30s | 2分間の休息 | タイマー完了 |
| Lv3 | Physical Anchor Light | p_stuck > 0.80 × 60s (想定) | 室内歩行 50〜100 歩 | 歩数達成 |
| Lv4 | Physical Anchor Full | p_stuck > 0.80 × 180s (想定) | 屋外散歩 500m 以上 | 距離達成 |

※ Lv3/Lv4 のトリガー閾値は確定していない。実装時に functional-design.md を更新すること。

---

## 主要なルール

### ルール 1: 計測指標の定義と単位

| 指標 | 単位 | 計測 API (Flutter) | 備考 |
|---|---|---|---|
| 歩数 | 歩 (steps) | `pedometer` プラグイン (StepCount) | セッション開始からの累積 |
| 移動距離 | メートル (m) | `geolocator` プラグイン (Position) | GPS ベース |
| 歩行速度 | m/s | 移動距離 / 経過時間 で算出 | 直接 API なし |
| 活動時間 | 秒 (s) | Flutter タイマー | Physical Anchor 開始からの経過 |

---

### ルール 2: 歩行速度の計算方法

Flutter の `geolocator` は速度 (`speed: m/s`) を直接提供するが、
屋内では GPS 精度が低いため、**歩数ベースの速度推定**を優先する。

```dart
// 推奨: 歩数 × 歩幅(推定) / 経過時間
const double STRIDE_LENGTH_M = 0.75;  // 平均歩幅 75cm

double estimatedSpeed(int steps, Duration elapsed) {
  if (elapsed.inSeconds == 0) return 0.0;
  return (steps * STRIDE_LENGTH_M) / elapsed.inSeconds;
}

// GPS 利用可能時はそちらを優先
double? gpsSpeed = position.speed;  // m/s、室外のみ信頼
```

---

### ルール 3: Flutter ↔ Tauri 通信プロトコル

Wall Server を拡張して Physical Anchor エンドポイントを提供する。

```
エンドポイント設計:

GET  /anchor         → Physical Anchor HTML (Flutter WebView or ブラウザ)
POST /anchor/start   → Physical Anchor セッション開始通知
POST /anchor/progress → 進捗報告 (steps, distance_m, speed_ms)
POST /anchor/complete → 完了通知 → Tauri が Wall 解除
```

```rust
// wall_server.rs 拡張例
#[derive(Deserialize)]
struct AnchorProgress {
    steps: u32,
    distance_m: f64,
    speed_ms: f64,  // m/s
    elapsed_s: u64,
}

// POST /anchor/progress を受信したら Tauri イベントで Frontend に通知
```

---

### ルール 4: 完了条件の判定は Rust 側で行う

Flutter から受け取った進捗データをもとに、完了条件の判定は Tauri 側が行う。
Flutter は計測値を送るだけ。

```rust
// ✅ 正しい設計（wall_server.rs）
fn check_completion(progress: &AnchorProgress, target: &AnchorTarget) -> bool {
    match target {
        AnchorTarget::Steps(n) => progress.steps >= *n,
        AnchorTarget::Distance(m) => progress.distance_m >= *m,
    }
}

// ❌ Flutter 側で完了判定しない（サーバーサイドに権限を持たせる）
```

---

### ルール 5: Flutter プラグイン選定基準

| プラグイン | 用途 | 対応 OS | 注意点 |
|---|---|---|---|
| `pedometer` | 歩数計測 | iOS, Android | Android はバックグラウンド権限が必要 |
| `geolocator` | GPS 位置・速度 | iOS, Android | 室外のみ高精度。権限ダイアログ必須 |
| `sensors_plus` | 加速度センサー | iOS, Android | 歩数の代替手段（歩行検出） |

Lv3（室内）では `pedometer` のみ使用。Lv4（屋外）では `geolocator` を追加。

---

### ルール 6: 目標値はユーザーが設定できるようにする（将来）

歩数・距離の目標値はハードコードせず、設定として保持する。

```rust
// 設定の例（将来の tauri-plugin-store 導入後）
pub struct AnchorConfig {
    pub lv3_steps_target: u32,      // デフォルト: 100 歩
    pub lv4_distance_target_m: f64, // デフォルト: 500 m
}
```

---

## チェックリスト

- [ ] 歩数・距離・速度の単位が統一されているか（steps, m, m/s）
- [ ] 完了条件の判定が Rust 側にあるか（Flutter 側ではない）
- [ ] Wall Server の拡張エンドポイントにトークン認証があるか
- [ ] Flutter プラグインが OS 権限ダイアログを適切に処理しているか
- [ ] 歩行速度がゼロ除算しないようになっているか

---

## 補足資料

- `flutter-integration.md` — Flutter アプリの実装スケッチ

## 関連する他の Skill

- `intervention-design` — Lv1/Lv2 の介入設計
- `data-privacy` — 位置情報・歩数データのプライバシー扱い
- `architecture-rules` — Wall Server 拡張時のモジュール配置
