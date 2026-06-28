# 設計判断と根拠

## D1: idle 退避は setPosition(画面外) + setSize(1x1) の両方を実行
- **判断**: idle 分岐で `setPosition(-20000,-20000)` に加え `setSize(1,1)` も呼ぶ。
- **根拠**: 画面外退避だけで幾何的にクリックは奪えなくなるが、1x1 縮小は二重の保険
  (万一 macOS が負座標を一部クランプする構成でも重なり面積を消す)。show 時は box/全画面の
  明示 setSize/setPosition が必ず復帰させるためコストゼロ。design.md の推奨どおり。

## D2: 退避と ignoresMouseEvents 設定の try/catch を分離
- **判断**: 退避 (setPosition/setSize) と `setOverlayInteractive(false)` を別 try/catch にする。
- **根拠**: 旧バグの増幅条件 = panel 変換失敗 → `setOverlayInteractive` throw → ignoresMouseEvents
  未設定 → 全画面透明窓が全クリック奪取。退避を独立に先行実行すれば、二次ガードが失敗しても
  一次ガード(幾何退避)で背後クリックは守られる。requirement.md の根本原因「増幅条件」を遮断。

## D3: 各 await 後に cancelled ガードを挿入
- **判断**: 退避の各 await 後に `if (cancelled) return`。
- **根拠**: idle→show 遷移で本 idle effect が stale 化したとき、退避が後続 show (box/全画面) を
  上書きする race を防ぐ。既存 show 分岐と同じ cancelled 規約に整合。

## D4: Rust debug command (ignoresMouseEvents 読み返し) は本タスクでは defer
- **判断**: next-session-prompt 手順4 の「(推奨) ignoresMouseEvents 読み返し番兵」は実装しない。
- **根拠**:
  1. **対象プロパティ違い**: 本修正の主因対策は *幾何退避* (窓位置/サイズ) であり、
     ignoresMouseEvents には依存しない。ignoresMouseEvents を読み返す番兵は本修正の一次ガードを
     検証できない (むしろ outer_position の検証が相応 — それは JS 既存 API で smoke 可能)。
  2. **追加リスク**: overlay_panel.rs は D7/D12 の delicate file。getter は plugin に無く、生 objc
     msg_send (BOOL 返却) を本ファイルへ追加する必要があり、非回帰死守領域に FFI を増やす。
  3. 受け入れ条件 (requirement.md) は debug command を要求していない。
- **フォローアップ**: 回帰番兵が必要なら、smoke で JS から `outerPosition()` を読み idle 時に
  画面外 (x<=-10000) を確認する軽量チェックを runbook に含める方が主因に即している (runbook.md 参照)。

## D5: show 経路のモニタ解決を currentMonitor() → resolveShowMonitor() (primaryMonitor フォールバック) へ
- **判断**: show 分岐 (applyFullscreenBlock / widgetOnly) の `currentMonitor()` を
  `(await currentMonitor()) ?? (await primaryMonitor())` (`resolveShowMonitor`) に置換。
- **根拠 (code-reviewer HIGH 指摘)**: D1 の退避で窓が画面外 (-20000,-20000) になると、macOS は
  `NSWindow.screen()==nil` → `currentMonitor()` が **null** を返しうる。すると:
  - widgetOnly: `setPosition` が `if (mon)` 内でスキップ → カードが画面外=不可視。
  - applyFullscreenBlock: setPosition/setSize 両方スキップ → Wall が 1x1 offscreen のまま=
    全画面ブロック不成立。
  毎セッション初回 probe は必ず offscreen から show するため高頻度で発火する退行。窓位置に
  依存しない primaryMonitor フォールバックで show は必ずオンスクリーンへ復帰する。退避を
  入れた以上 currentMonitor() (窓位置依存 API) は show の権威として不適切になったための置換。

## D6: idle 退避はクロスプラットフォーム (macOS 限定 #[cfg] 相当のゲートをしない)
- **判断**: 退避を OS 判定で macOS 限定にせず、Windows でも実行する。
- **根拠**: design.md は「退避は macOS 固有」と書くが、frontend に OS 判定が無く、ゲートには
  `@tauri-apps/plugin-os` の新規導入 (npm + Rust plugin + capability) が必要でバグ規模に不釣り合い。
  退避は Windows では無害 (Windows の `currentMonitor()` は MONITOR_DEFAULTTONEAREST で常に非 null、
  かつ D5 の primaryMonitor フォールバックで show は確実に復帰)。要件の真の制約「Windows 非回帰」は
  show 復帰の堅牢化で満たす。Windows 実機 smoke (probe/Wall/idle) で確認する (runbook.md §7)。

## D8: 観測 OS は Windows と訂正 — 幾何退避は機構非依存で Windows でも有効 (コード変更不要)
- **訂正 (ユーザー指摘 2026-06-29)**: 本バグの観測プラットフォームは macOS ではなく **Windows**
  (プライマリターゲット・被験者は Windows 11/Surface Pro 8)。当初 requirement/design は macOS 開発機
  での検証から macOS 固有機構で根本原因を framing していた。
- **Windows 機構 (確定・出典付き)**: 透明 Tauri/WebView2 窓は `setIgnoreCursorEvents(true)` を
  呼んでもクリックを素通りさせない既知の制約がある:
  - Tauri #11461 (Windows10「setIgnoreCursorEvents() not work」, closed not planned)
  - Tauri #13070 (透明領域が入力を奪い背後をブロック) / #2090 (同旨)
  → Windows では `set_ignore_cursor_events`(WS_EX_TRANSPARENT) 単独でクリック透過を保証できない
    (WebView2 子 HWND が透過を継承せずクリックを捕捉する系統の問題)。macOS の NSPanel 非 key 配送
    とは**別機構だが同一症状**。
- **含意**: 幾何退避 (画面外 -20000,-20000 + 1x1) は窓を WebView2 子 HWND ごと物理的に画面外へ
  出すため、クリック透過が効かない Windows でも背後クリックを一切奪わない。**機構非依存で
  macOS/Windows を同時に解決する**。これが「click-through 単独に頼らず幾何退避を一次ガードにする」
  (design.md 多層防御) 方針が Windows でも正しい根拠。
- **コード影響なし**: 退避は最初から OS ゲートなしのクロスプラットフォーム実装 (D6) で、退避に必要な
  capability (`allow-set-size`/`allow-set-position`/`allow-set-ignore-cursor-events`) は
  `capabilities/default.json` で main/overlay 両窓・全 OS に付与済み。よって本訂正でコード変更は不要、
  framing と smoke 優先順位 (Windows 実機を最優先) の更新のみ。
- **macOS 固有変更の Windows 安全性**: `resolveShowMonitor` (currentMonitor()==null フォールバック・D5)
  は macOS 退行対策だが、Windows の `currentMonitor()` は MONITOR_DEFAULTTONEAREST で常に非 null の
  ため primaryMonitor 経路に入らず無害 (退避後は offscreen rect に最も近いモニタ=単一モニタ被験者では
  唯一のモニタを返し、box/Wall は正しく復帰)。

## D7: 退避 race の最終正しさは Tauri IPC の FIFO 順序に依存 (cancelled ガードで縮小)
- **判断 (code-reviewer MEDIUM)**: cancelled ガードは「次の OS 書き込み」を止めるが、stale idle
  effect が**発行済み**の setSize(1,1)/setPosition(OFFSCREEN) が新 show の書き込みより後に OS へ
  着地しない保証は、Tauri IPC が invoke 順=適用順 (FIFO) であることに依存する。
- **根拠**: 既存 show 分岐も同じ FIFO 前提で動いており新たな前提ではない。世代トークン導入は
  過剰。idle⇄probe 高速トグル smoke を runbook に追加して実機で担保する (runbook.md §軽量回帰)。
