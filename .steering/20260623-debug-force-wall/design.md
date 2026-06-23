# 設計 (debug-force-wall)

## 実装アプローチ

既存の **decision polling 経路を再利用**して Wall を強制発動する。新たな wall 起動経路を作らず、
`get_intervention_decision` が `action=wall` を返せば App.tsx が `isWallActive(true)` にし、Overlay が
wall_server 起動 + Wall 表示する既存フローに乗る (両ウィンドウが polling で同期)。

- `FORCE_WALL: AtomicBool` を lib.rs に追加。`force_wall` コマンドが true にセット。
- `get_intervention_decision` (main ウィンドウ分岐) で、INTERVENTION_ENABLED より前に
  `FORCE_WALL.swap(false)` を確認。true なら policy の `force_wall_decision()` を呼び
  action=wall (reason="debug_force") を返す + ログ。
- **ワンショット**: 一度 wall を返せば App が isWallActive=true にし、次 tick から `is_wall_active=true`
  → 既存の wall_active 分岐が wall を維持。解除 (sensor-accelerometer) で通常へ戻る。FORCE_WALL は消費済み。
- overlay ウィンドウは `last_decision()` を読むため、main が last_decision=wall に更新すれば overlay も拾う。

## 変更対象

### 修正するファイル
- `src-tauri/src/analysis/intervention.rs` — `InterventionPolicyState::force_wall_decision(now_ms, idle_ms)`
  追加。current_action=Wall・last_decision=wall(reason="debug_force")を設定し返す。単体テスト追加。
- `src-tauri/src/lib.rs` — `FORCE_WALL: AtomicBool`、`#[tauri::command] force_wall()`、
  `get_intervention_decision` 先頭付近で消費して force 決定を返す + ログ。generate_handler に登録。
- `src/components/Dashboard.tsx` — 較正モード時のみ表示する「Wall 強制発動 (デバッグ)」ボタン →
  `invoke("force_wall")`。invoke import 追加。

### 新規作成 / 削除
- なし

## 影響範囲
- HMM (engine/features) 不変 → `--snapshot` byte-equal・`HMM_VERSION` 不変。
- schema 不変 (reason は既存 String、新カテゴリ不要)。replay 不変 (force_wall は replay 経路外)。
- 通常動作 (ボタン非押下) では FORCE_WALL=false のまま → 既存挙動と完全同一 (pilot 非汚染)。
- 強制 wall は intervention_decision(action=wall, reason="debug_force") としてログ → 解析時に除外可能。

## 既存パターンとの整合性
- AtomicBool フラグ + コマンド (INTERVENTION_ENABLED と同流儀)。decision は既存 polling で同期。
- rust-standards: anyhow/tracing・固定 reason 文字列。typescript-standards: invoke 型付き・UI のみ・
  ボタンは calibrationMode gate (既存 prop)。

## テスト戦略
- 単体: `force_wall_decision` が action=Wall・reason="debug_force"・last_decision 更新を返す。
- `cargo test --workspace` 緑・`--snapshot` byte-equal (HMM 不変) 回帰確認。tsc+vite build 緑。
- 実機: 較正モードでボタン → Wall 表示 → QR → スマホ解除 → A2 intervention_response 捕捉を確認 (手元)。

## ロールバック計画
- 加算的変更。問題時は branch 破棄。FORCE_WALL は既定 false なので無効化は容易。
