# macOS でオーバーレイのカード/Nudge ボタンがクリックスルーして反応しない

## 背景

被験者向けの非ブロック介入 UI（commit `414ef1d`）で、プローブ回答カード（`ProbeCard.tsx`）と
Nudge カード（`Overlay.tsx`）が **macOS で表示はされるがボタンを押しても反応しない**。

ユーザー実機確認（2026-06-25, macOS, `tauri dev`）:
- カードのボタンを押しても onClick が発火しない（devtools console に何も出ない）。
- インラインエラー（「記録に失敗しました」）も fail-loud バナーも出ない。
- カードの「外」もボタンも、クリックすると**背後のアプリが反応**する＝クリックが overlay 窓を素通り。
- Probe と Nudge の**両方**で同症状。

## 確定済みの原因（調査で特定）

- overlay は独立窓（label="overlay"、`lib.rs:1681`）で `transparent(true) decorations(false)
  always_on_top(true) visible(false)`、フォーカスは奪わない設計。
- カード表示時、`Overlay.tsx` の統合 effect が右上 box に縮小し `win.setIgnoreCursorEvents(false)`
  を呼ぶ（`Overlay.tsx:191`）が、**macOS でこれが効かずクリックが透過し続ける**。
- CSS は無実: `.overlay-root` は `pointer-events:auto`、カードも auto（Nudge は明示 auto）。
  → クリックが webview に届く前に OS 窓を素通り＝ウィンドウ単位のクリックスルー制御の問題。
- `#1`（カード無反応）の logger disconnected 経路とは**別の根本原因**（クリックが届かないので
  `record_*` まで到達しない）。F4（idle/away）とも無関係。

## ゴール

- macOS で、カード/Nudge 表示中に**カード領域のクリックはボタンに届く**（onClick 発火・記録される）。
- 同時に**カード外のクリックは背後アプリへ透過する非ブロック設計を維持**（フォーカスを奪わない）。
- Windows の既存挙動を壊さない（Windows では現状クリックは効いている前提）。

## スコープ

### 含むもの
- macOS の overlay 窓のクリックスルー解除を実効化する修正（`Overlay.tsx` の制御、必要なら
  Rust 側 NSWindow レベル操作 / 窓生成オプション、CSS の hit-test 補助）。
- Probe / Nudge 両方が macOS で操作可能になること。

### 含まないもの
- Wall（全画面ブロック）の挙動変更（現状維持）。
- F4 / logger #1 の再修正。
- Windows 固有のオーバーレイ改修（回帰させないことのみ担保）。

## 受け入れ条件

- [ ] macOS `tauri dev` で Probe カードの「回答する/思い出せない/✕」が押せて `record_realtime_*` が走る。
- [ ] macOS で Nudge の「詰まってない/今はもがきたい/閉じる」が押せて `record_intervention_dismiss` が走る。
- [ ] カード外のクリックは背後アプリへ透過する（非ブロック維持・フォーカス非奪取）。
- [ ] Windows で回帰しない（少なくともロジック上の非破壊を確認）。
- [ ] 実機（macOS）でユーザーが操作確認（runbook）。

## 関連
- `src/components/Overlay.tsx`（統合 effect・setIgnoreCursorEvents）/ `ProbeCard.tsx` / `App.css`
- `src-tauri/src/lib.rs:1681`（overlay WebviewWindowBuilder）
- `intervention-design` / `typescript-standards` / `hook-constraints`(macOS GCD/メインスレッド) Skill

## 運用メモ
- /reimagine 適用: No（代わりに `codex-consult` で macOS overlay クリックスルーの定石を第二意見として確認）
- 理由: 設計空間は「窓設定 / JS 側トグル / Rust NSWindow 操作 / CSS hit-test」の組合せで、
  macOS 固有の癖が強い。ゼロ再生成より、既知の定石を codex で確認しつつ最小修正を当てる方が早い。
