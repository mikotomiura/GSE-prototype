# 設計 (gentle-intervention-ui)

## 実装アプローチ

### Nudge: 応答まで保持 + 非ブロック + 穏やか (Overlay.tsx)
- 表示状態を live action から切り離す。`nudgeVisible` state を導入: action==="nudge" かつ未表示・未 dismiss で
  **一度 true にしたら、ユーザー応答 or タイムアウトまで保持** (live action が none/defer/wall に変わっても消さない)。
  - 応答: 既存 dismiss ボタン → record_intervention_dismiss → 非表示 + dismissed。
  - タイムアウト: 既定 60s で reason="silent" を送って非表示 (CD7 silent の実送出)。
  - Wall 発動時 (isWallActive) は nudge を畳む。
- 非ブロック: 既存 box 化 (PR #21 の probeOnly) を **nudge にも適用**。`widgetOnly = (probe||nudge) && !wall`
  で右下 box に縮小 + クリック透過。nudge は右下に配置。
- 穏やか CSS: ゆっくりフェードイン (~325ms 減速)、単一の控えめ色。

### Wall: ゆっくり減光フェードイン (Overlay.tsx + App.css)
- `wall-layer` の即時不透明 (opacity 即 1 / bg 0.98) をやめ、**CSS アニメーションで数秒かけて減光**
  (`wall-dim-in`: opacity 0→1・backdrop を徐々に)。落ち着いた配色。QR/早期解除/接続バッジは維持。
- 全画面ブロック自体は維持 (Wall=ブロックは意図) だが視覚的 onset を緩和。

### 自己ラベル: ワンタップ self_marker (lib.rs + Dashboard.tsx)
- backend: `#[tauri::command] record_self_marker()` — now + SESSION_START から self_marker_window_clamped で
  窓算出、`realtime_label_answered(now, &ProbeRef::SelfMarker, q1=5, q2=1, latency=0, ws, we)` を try_send。
  q1=5(とても詰まった)/q2=1(進んでない) = Stuck 象限の自己申告。handler 登録。
- グローバルホットキー Ctrl+Shift+Alt+D を追加し、押下で同じ記録 (既存 M=カード式は据え置き)。
  debounce は既存 LAST_SELF_MARKER_MS を流用。
- Dashboard: 「🔴 今とても詰まっている」ボタン (セッション中常時) → invoke("record_self_marker")。

## 変更対象

### 修正するファイル
- `src/components/Overlay.tsx` — nudge 保持ロジック + widgetOnly(nudge) box 化 + wall フェード。
- `src/components/Dashboard.tsx` — 自己ラベルボタン。
- `src/App.css` — nudge 穏やか + wall-dim-in keyframes + self-marker button。
- `src-tauri/src/lib.rs` — record_self_marker コマンド + D ホットキー + handler 登録。

### 新規作成 / 削除
- なし

## 影響範囲
- HMM/engine/features 不変 → `--snapshot` byte-equal・`HMM_VERSION` 不変。
- schema 不変 (realtime_label は既存・self_marker 既存)。replay 不変。
- 既存 M ホットキー (カード式 self_marker) は据え置き (回帰なし)。F/I/S UserLabel も不変。

## 既存パターンとの整合性
- typescript-standards: any 不使用・invoke 型付き・UI のみ・useState/useRef。
- rust-standards: tracing/try_send・既存 record_realtime_answer / build_probe_ref と同流儀。
- data-privacy: self_marker は固定カテゴリ + 時刻 + 窓のみ・本文なし。

## テスト戦略
- cargo test --workspace 緑 (record_self_marker は State 依存のため純粋部分のみ; 既存 build_probe_ref テスト活用)。
- --snapshot byte-equal・tsc+vite build 緑。
- 実機 GUI: nudge 保持/非ブロック/右下、wall 減光、ボタン+ホットキーで self_marker 記録を手元確認。

## ロールバック計画
- 加算的。問題時は branch 破棄。各機能は独立に無効化可 (ボタン削除 / nudge ロジック差し戻し)。
