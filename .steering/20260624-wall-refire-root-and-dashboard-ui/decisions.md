# 設計判断 (wall-refire-root-and-dashboard-ui)

## D1: Wall 再発火の真因 = エッジ未検出 (cooldown では直らない)
- `App.tsx` の起動は `if (action==="wall" && !isWallActive) setTrue` でレベルトリガ。解除後も判定が
  "wall" のまま続く (overlay は `last_decision` を読むため lingering・action!=wall で false にする else 無し)
  ため毎ポーリング再起動していた。#24 の cooldown は `decide()` 内のみで、overlay の lingering
  last_decision 経路には効かない (これが「cooldown 入れても直らない」理由)。
- 修正: `wallHandledRef`(useRef) で **非 wall→wall の立ち上がりエッジでのみ起動**。解除後の lingering
  wall では handled=true のまま再起動せず、action が wall を離れたら handled=false で次エピソード許可。

## D2: 両ウィンドウが各自 isWallActive を set する構造は現状維持 (reviewer HIGH への対応記録)
- main = Dashboard・policy 駆動 (decide)。overlay = Wall 描画 + start_wall_server。両者が App を実行し
  各自 polling で isWallActive を set する。Wall 起動の真実源が曖昧という指摘はその通りだが、
  本修正で **main のエッジ検出が主防御**となり、overlay も handled=true により lingering 中は再起動せず、
  main が last_decision=defer に更新 (≤500ms) した時点で overlay の handled もリセットされる。
  よって再発火は解消。Wall 起動を main 単独へ集約 + overlay をイベント従属にする refactor は別タスク候補。

## D3: onBack は介入もクリアする (reviewer MEDIUM)
- スタート画面へ戻る瞬間に Wall が出ていると overlay が残るため、`handleBack` で
  `setIsWallActive(false)` も呼んでから `setIsStarted(false)`。Rust セッションは継続 (UI nav)、
  再開時 start_session が reset する。

## D4: start-screen のスクロール化 (見切れ修正)
- `justify-content:center + min-height:100vh + overflow 無し` は 800x600 窓でコンテンツ超過時に
  上下が切れスクロールも効かない (flexbox 既知挙動)。`flex-start + overflow-y:auto + max-height:100vh`
  にして全項目 (尺度理解テストボタン) に到達可能化。VignetteTest も同 class のため同時解消。

## D5: 戻る導線
- Dashboard: 「← 戻る」(onBack・アプリ終了しない) を「セッション終了」(quit_app) と別に nav 行で提供。
- VignetteTest: 質問画面に「← 戻る (中断)」(onComplete)。部分回答は各 record_vignette_response で記録済。

## 不変条件
- frontend のみ。backend/HMM/schema 不変 (cargo test 210緑・--snapshot 影響なし)。
