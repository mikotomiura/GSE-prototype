# 設計（調査・方針メモ。実装は次セッション）

## 現状の確定事実（調査済み）
- overlay は独立窓 label="overlay"（`lib.rs:1681`）: `transparent(true) decorations(false)
  always_on_top(true) skip_taskbar(true) visible(false)`、非フォーカス設計。Tauri v2 +
  `macos-private-api`。
- カード表示時、`Overlay.tsx` 統合 effect（`:130-211`）が窓を右上 box（`PROBE_BOX_W=390 ×
  PROBE_BOX_H=430`、margin 12）へ縮小し `win.setIgnoreCursorEvents(false)`（`:191`）を await。
  例外なく box 化成功（カードは見える）が、**クリックは透過し続け背後アプリが反応**（実機確認）。
- CSS は無実: `.overlay-root` は `pointer-events:auto`、カードも auto（Nudge は明示 auto）。
- 推論: `ignoresMouseEvents=NO` なら 390×430 の box 全体がクリックを取るはずだが透過する →
  **`setIgnoreCursorEvents(false)` が実効化していない**（or 透過窓 hit-test/first-mouse 問題）。
- Probe / Nudge 両方で発症。`#1`(logger disconnected) とも F4(idle/away) とも別根本原因。

## codex-consult の指摘（2026-06-25・要反映）
1. **非フォーカスとクリック受理は別問題**: `canBecomeKeyWindow`/activation policy/`acceptsFirstMouse:`
   次第で「初回クリックだけ捨てられる」「hover/focus 不安定」。検証は**「背後アプリがアクティブな
   まま初回クリックでボタン action が発火するか」**を必須項目に。
2. **小箱 C は multi-display / Retina scale / Dock・menu bar / Stage Manager / フルスクリーン Space /
   Mission Control で座標崩れ**。`NSScreen.visibleFrame` 基準の再配置・display change・scale 変更時
   再計算が要る。
3. **透明余白のクリック奪取は安全性問題**（背後の閉じる/送信/購入を潰す）。余白最小化＋実測で許容領域決定。
   `pointer-events:none` は NSWindow レベルでは透過させない点を明文化。
4. **B（直接 setIgnoresMouseEvents:NO）は状態競合注意**: JS・Tauri API・Rust command が同 NSWindow を
   触ると show/hide/resize 後に最後の呼出順で壊れる。**macOS overlay interaction state machine を Rust
   に寄せ、JS は intent だけ送る**形が安全。
5. **候補外**: `NSPanel` 化 / `nonactivatingPanelMask` / `acceptsMouseMovedEvents` / `collectionBehavior`
   整理。さらに**「カード表示中だけ専用の小窓を別生成し、全画面透明 overlay と分離」**が有力
   （1 窓に「全画面透明 overlay」と「clickable card」を背負わせない）。
6. **D（カーソル追従）は信頼性コスト高**（権限/遅延/CPU/欠落/署名）→ 最後の手段。
7. **真因未確定のまま固定するな**: まず `ignore=false` 実行後に Rust 側で実 `ignoresMouseEvents` を
   読み返してログ化し、Tauri/WRY 更新での再発を防ぐ。

## 次セッションの方針（root-cause-first）
- **Step 0（診断）**: Rust 側で overlay の NSWindow `ignoresMouseEvents` を読み返すデバッグ手段を入れ、
  JS が `setIgnoreCursorEvents(false)` した後の**実値**を確認する。これで分岐を確定:
  - (i) 値が YES のまま → set 呼出が no-op → Rust 側直接設定 or 窓再生成 or 専用窓。
  - (ii) 値は NO だが透過 → 透過窓 per-pixel hit-test + `acceptsFirstMouse`/`canBecomeKey` 問題 →
    NSPanel 化 / acceptsFirstMouse / 専用窓。
- **採用方針（仮・診断後に確定）**: 第一候補は **専用カード窓の分離（codex #5）** または
  **Rust 側 overlay interaction state machine（codex #4）**。C は補助だが multi-display/安全性の弱点を
  認識した上で box を card サイズに最小化する場合のみ。D は採用しない。

## 変更対象（見込み・診断後に確定）
- `src-tauri/src/lib.rs` — overlay 窓生成オプション / NSWindow 操作の Tauri command（macos cfg）。
- `src/components/Overlay.tsx` — 窓制御を「intent 送信」に寄せる、box ジオメトリ、display change 対応。
- （専用窓案なら）新 window label + 生成・表示制御。
- macOS NSWindow 操作は `objc2`/`cocoa` 経由・**メインスレッド制約（GCD）厳守**（hook-constraints mac-2/5）。

## テスト戦略
- 単体: 窓ジオメトリ計算（visibleFrame クランプ等）を純関数化できれば cargo test。
- 実機（macOS, tauri dev）: **背後アプリ active のまま初回クリックでボタン発火** / 多ディスプレイ /
  Retina / フルスクリーン Space で確認。Windows 非回帰（クリック維持）。
- 真値ログ: `ignoresMouseEvents` 読み返しを残し回帰検知に使う。

## ロールバック計画
- 介入 UI のクリック周りのみの変更に留め、問題時は Wall 全画面ブロック経路（既存）に影響しない設計にする。
- ブランチ `fix/macos-overlay-clickthrough`（独立 PR）。
