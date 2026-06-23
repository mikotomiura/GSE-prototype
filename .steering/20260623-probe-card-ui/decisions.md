# 設計判断 (probe-card-ui)

## D1: 非ブロックは「既存オーバーレイ窓の box 化」で実現 (新窓・cursor polling を不採用)
- 候補: (i) 専用 probe 窓新設 (ii) 既存窓を box 化 (iii) cursor 位置 forwarding。
- 採用 = (ii)。理由: 新窓は lifecycle/positioning/Win deadlock の新規リスク、cursor forwarding は
  OS cursor 取得 API の不確実性。既存窓 box 化は実績ある窓を再利用し最小変更。
- nudge は `top:42%` 配置のため box 化で位置が崩れる → **nudge は box 化対象外** (現状維持)。
  probe 単独時のみ box 化。probe+nudge 同時はまれ・安全側 (全画面) に倒す。

## D2: cross-review CRITICAL — probe→Wall 遷移で Wall が小窓ロックする危険を排除
- 指摘: box 化 (setSize 390x430) 後に Wall 発動 → `maximize()` だけでは WM 次第で小窓のまま復帰せず、
  QR が読めず**被験者が解除不能**になりうる。
- 対応: `applyFullscreenBlock` で **明示的に monitor 全域へ setPosition+setSize してから maximize**。
  maximize 単独に依存しない。physical 座標で扱い DPI 二重変換を回避。

## D3: cross-review HIGH — async effect race を cancelled で全 window 操作をゲート
- 連続 state 変化で旧 effect の maximize が新 effect の box 化を後勝ちで潰す race。
- 対応: `setPosition/setSize/maximize/unmaximize/setIgnoreCursorEvents` の各 await 後に `if (cancelled) return`。

## D4: フォールバック安全性 (graceful degradation)
- box 化のいずれかが失敗 → outer catch で `applyFullscreenBlock` (全画面+ブロック=現状挙動) に倒す。
  二重失敗も console.error で可視化。被験者を操作不能のまま放置しない設計を維持。

## D5: 多モニタ/スケール — physical 座標 + clamp (MEDIUM 対応)
- monitor.size/position は physical px。box 寸法は `PROBE_BOX_* * scaleFactor` で physical 化。
- 右上 x は `max(monitor.x, ...)` で画面外に出ないよう clamp。

## D6: カード高さ clamp (MEDIUM 対応)
- ProbeCard に `maxHeight: calc(100vh - 2.5rem)` + `overflowY:auto`。box 窓からはみ出して
  回答ボタンが透過領域に隠れるのを防ぐ。

## D8: cross-review (Claude∥Codex) 両者一致 HIGH 2件を適用
- **[1] catch 内 cancelled 漏れ**: 表示パスの outer catch 先頭に `if (cancelled) return;` を追加。
  stale effect のフォールバック全画面が新モードを上書きする race を防止。
  (applyFullscreenBlock 自体も内部 await ごとに cancelled 参照済み = C-1 は対応済み)。
- **[2] hide 失敗 → 全画面ブロック転落**: `!visible` の hide を独立 try/catch に分離し、失敗時は
  `setIgnoreCursorEvents(true)` に留めフォールバック全画面を呼ばない (何も出ていないのに操作不能の回避)。
- **[C-2] unmaximize 失敗**: swallow → `console.warn` に変更 (実機デバッグ可視化)。失敗時も box 化続行、
  最終的に効かなければ下の catch で全画面へ。
- **[3] 状態遷移 E2E (Playwright/Tauri mock) は本タスクで未実施 (follow-up)**: window mock 基盤が未整備で
  かつ GUI 挙動は実機必須のため。論理は防御的に実装済み・実機検証で代替 (D7)。`PROBE_BOX_*` 単一真実源化
  [C-3 LOW] も follow-up (maxHeight clamp でボタン隠れは緩和済み)。

## D7: GUI 挙動は実機検証前提 (制約の明示)
- window resize/position/cursor 透過・スライドインはヘッドレスで検証不可。tsc+vite build 緑・
  cargo test 緑までを CI 相当として確認し、**実機 (Win) でのスライドイン/透過/Wall 全画面維持は
  被験者セッションで確認**。フォールバックにより最悪でも現状挙動 (全画面) を保証。
