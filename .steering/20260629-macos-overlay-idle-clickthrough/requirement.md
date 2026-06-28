# 要件: オーバーレイ idle 残存による背後クリック阻害の修正

> **【2026-06-29 訂正・重要】観測プラットフォームは macOS ではなく Windows。**
> 当初 requirement/design は macOS 機での開発検証から macOS 固有機構 (NSPanel 非 key 配送・
> `ignoresMouseEvents` tri-state・Tahoe OS 退行) で根本原因を framing していたが、被験者の実問題は
> **Windows 11 (プライマリターゲット・Surface Pro 8) で発生**している。
> - **Windows 機構 (確定・出典付き)**: 透明 Tauri/WebView2 窓は `setIgnoreCursorEvents(true)` を
>   呼んでも**クリックを素通りさせない** (Tauri #11461 Windows10「not planned」/ #13070 / #2090)。
>   = Windows ではクリック透過 (`set_ignore_cursor_events`) 単独に頼れない。
> - **したがって幾何退避 (画面外 -20000,-20000 + 1x1) が Windows でも必須かつ唯一堅牢な解**。
>   退避は窓 (WebView2 子 HWND ごと) を物理的に画面外へ出すため、透過の効かない Windows でも
>   背後クリックを一切奪わない。**機構非依存で macOS/Windows 双方を同時に解決する**。
> - 実装は最初からクロスプラットフォーム (OS ゲートなし・decisions D6) なので**コード変更は不要**、
>   訂正は framing と smoke 優先順位 (Windows 実機を最優先) のみ。詳細は decisions.md D8。

## 背景（症状）
被験者が他アプリ（例: ブラウザの Google Docs）で作業中、**透明なオーバーレイ窓が画面に残存し、
背後アプリへのクリックを奪う**（「すけようとさせている謎の透明画面の残存が邪魔をしている」）。

これは過去に解決済みの `macos-overlay-clickthrough-bug`（カードのボタンが押せない＝D7-D13、
commit e1362ce）の **逆向きの残存問題**。前者はカードを操作可能にする修正で、本件は
「idle 時にオーバーレイが背後をブロックする」未解決の構造的欠陥。

## 根本原因（2026-06-29 厳密調査で確定）
オーバーレイ窓の idle 処理が `ignoresMouseEvents=YES` に頼るだけで、**窓を画面外退避も縮小もしない**。
- `src/components/Overlay.tsx:167-174` … idle 分岐は `setOverlayInteractive(false)` のみ。
  **`setSize` / `setPosition` を一切呼ばない**。Wall 後は全画面、Probe 後は右上 390x430 box の
  まま、透明・always_on_top・CanJoinAllSpaces で画面に残る。
- `src-tauri/src/overlay_panel.rs:55` … コメントが「カードは画面外退避するので常駐コストは
  無視できる」と**退避を前提**にしているが、現在その退避は実装されていない（嘘になっている）。
- revert された card 窓方式（`.steering/20260625-macos-overlay-clickthrough-fix/HANDOFF-cardwindow.md:42`）は
  idle 時に `画面外(-20000,-20000) ⇄ 右上` へ `setPosition` していた。`runbook.md:9` で card 窓方式は
  revert され、**その offscreen 退避だけが失われた**。
- 増幅条件: `convert_overlay_to_panel` 失敗（`lib.rs:1828-1829`、ログのみで続行）や
  `get_webview_panel("overlay")` 失敗時、`set_panel_interactive` が Err → idle の
  `setOverlayInteractive(false)` が throw → `console.warn` だけ（`Overlay.tsx:171`）→
  `ignoresMouseEvents` が一度も設定されず、全画面透明窓が全クリックをブロックする。

## Web 調査の裏付け（厳密リサーチ・出典付き）
- tauri#13070: 単一の大きな透明 WebView 領域は「still captures input, blocking interactions with
  underlying windows」。tauri#11461 / #2090 / wry#1266 も同旨。`ignoresMouseEvents` は脆い tri-state。
- Apple Forums 814798: macOS Tahoe **26.3-RC / 26.4-beta** で borderless/透明全画面オーバーレイが
  ignoresMouseEvents に関わらず全クリックを奪う OS 退行（styleMask の .titled 除去がトリガ＝NSPanel 化と一致）。
  → **ただし本機は 26.5.1 (25F80) GA** のため OS 退行は主因ではなく、アプリ側構造欠陥が主因と判断。
- 推奨修正（独立に一致）: idle は ignoresMouseEvents 単独に頼らず、**画面外退避 or 1x1 縮小**で
  幾何的にクリックを奪えなくする（JS は生かす）。ignoresMouseEvents=YES は二次ガードとして併用。

## ゴール
idle（Probe/Nudge/Wall いずれも非表示）時に、オーバーレイ窓が背後アプリのクリックを
**一切奪わない**。かつ webview の JS（`probe_triggered` リスナー等）は休眠させない（D10 維持）。

## 受け入れ条件
- [ ] Probe 応答後・Wall 解除後の idle 状態で、画面のどこをクリックしても背後アプリが反応する。
- [ ] idle 時にオーバーレイが視覚的にも不可視（透明窓が残って見えない）。
- [ ] Probe 発火時はカードが**見えてクリックでき**、カード外は透過（既存の非ブロック設計を非回帰）。
- [ ] Wall 発動時は全画面ブロックが従来どおり効く（非回帰）。
- [ ] 前面アプリのタイピングフォーカスを奪わない（D12 非回帰）。
- [ ] Windows 非回帰（idle 退避は macOS 固有で Windows 経路を壊さない）。
- [ ] 実機 smoke（下記 runbook チェックリスト）green。

## 非対象
- HMM / probe スケジューラ / 提出パイプライン（別タスク）。
- 提出ランチャ問題（本セッションで別途対応済み・要 commit と Drive 反映）。
