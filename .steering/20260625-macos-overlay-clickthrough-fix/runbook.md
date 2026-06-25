# 実機検証 runbook（macOS overlay クリックスルー修正）

> 真因 = 非 key 窓 + WKWebView の `acceptsFirstMouse` 既定 false（decisions.md D6）。
> 修正 = overlay 窓生成に `accept_first_mouse(true)` を付与（lib.rs）。実機検証はユーザーが実施。

## 前提
- ブランチ `fix/macos-overlay-clickthrough`。
- `~/.cargo/bin/cargo build --target aarch64-apple-darwin` 済み（または `cargo tauri dev`）。
- Input Monitoring 権限付与済み（初回は付与→再起動）。
- **注意**: `accept_first_mouse` は窓生成時の属性。必ず**クリーンに再ビルドして再起動**してから検証
  （既存の dev プロセスを使い回さない）。

## 手順

### A. Probe カードのクリック検証
1. `cargo tauri dev` で起動 → セッション開始。
2. **別アプリ（例: テキストエディタ）を前面に**したまま（= GSE は非アクティブ）、
   プローブを強制発火（`debug_force_probe`・デバッグビルド）。
3. Probe カードの「回答する / 思い出せない / ✕」を押す。
4. 期待:
   - [ ] **初回クリックでボタンが反応**し `record_realtime_*` が走る（カードが閉じる）。
         ← acceptsFirstMouse が効いていれば非アクティブ窓でも初回から発火する。
   - [ ] devtools console にボタンの onClick 由来のログ／記録が出る（クリックが webview に届く）。
5. カード**外**の領域をクリック → 背後アプリが反応する（非ブロック透過維持）。

### B. Nudge カードのクリック検証
1. `force_nudge` で Nudge を表示。
2. 「詰まってない / 今はもがきたい / 閉じる」を押す。
3. 期待:
   - [ ] ボタンが反応し `record_intervention_dismiss` が走る（カードが閉じる）。
   - [ ] カード外クリックは背後へ透過。

### C. Wall（全画面ブロック）非回帰
1. `force_wall` で Wall 発動。
2. 期待:
   - [ ] 全画面ブロックが従来どおり機能（QR 解除のみ）。解除後 overlay が透過状態へ戻る。

## 結果の解釈
- **A/B のボタンが初回クリックで効く** → 修正成功（真因 = acceptsFirstMouse 確定）。
- **まだ無反応 / 背後アプリが反応する** → acceptFirstMouse だけでは不足。follow-up 候補:
  1. `tauri-nspanel` で **NSWindowStyleMaskNonActivatingPanel** 化（非アクティブ窓のクリック受理の
     AppKit 正攻法。Spotlight/Raycast 型 overlay の定石）。
  2. カード表示中だけ別生成する**専用カード窓**（codex ⑤）。
  3. `setIgnoreCursorEvents(false)` が効いているかの確認（カード表示時に窓が hit-test に参加しているか）。
- **初回だけ無反応で 2 回目に効く** → 窓が一旦 key 化している可能性（acceptFirstMouse 不適用経路）。
  窓属性が再ビルドで反映されているか／別経路で再生成していないかを確認。

## Windows 非回帰
- 本修正は macOS の WKWebView 挙動向け属性。Windows は従来どおり（`setIgnoreCursorEvents` 経路不変）。
- 可能なら実機で Probe/Nudge のクリックが従来どおり効くことを確認。

## 補足
- `accept_first_mouse` は **フォーカスを奪わない**（窓を key 化しない）。非ブロック設計は維持。
- 既知の相互作用（Tauri #6568: alwaysOnTop + acceptFirstMouse でドラッグ領域がずれる）あり。
  overlay は `data-tauri-drag-region` を使わないため該当しない見込みだが、ドラッグ系の異常が出たら参照。
