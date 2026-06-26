# 実機検証 runbook（macOS overlay クリックスルー修正 — NSPanel 方式・decisions D7）

> 真因 = 非 key/非アクティブ NSWindow がクリックを content view へルーティングしない（透明性は無関係）。
> 修正 = overlay 窓を tauri-nspanel で **非アクティブ NSPanel**（`NSWindowStyleMaskNonActivatingPanel`
> + 自動 `canBecomeKeyWindow=YES`、Floating level）へ変換（`overlay_panel.rs` / `lib.rs` setup）。
> 実機検証はユーザーが実施。

## 前提
- ブランチ `fix/macos-overlay-clickthrough`。card 窓方式は revert 済み（Probe は overlay に復帰）。
- `~/.cargo/bin/cargo build --target aarch64-apple-darwin` 済み（初回は git 依存 tauri-nspanel を取得）。
- Input Monitoring 権限付与済み（初回は付与→再起動）。
- **クリーンに再ビルドして再起動**してから検証（既存 dev プロセスを使い回さない）。
- 開発起動: `GSE_DEBUG=1 VITE_GSE_DEBUG=1 npm run tauri dev`（runtime gate + ボタン表示の二重必須）。

## 手順

### A. Probe カードのクリック検証（最重要）
1. 起動 → セッション開始。
2. **別アプリ（テキストエディタ等）を前面に**したまま（= GSE は非アクティブ）、
   📝 プローブを強制発火（`debug_force_probe`・デバッグビルド）。
3. 期待:
   - [ ] 画面右上に Probe カードが出る（probe_triggered が overlay に届き表示される）。
   - [ ] **初回クリックで「回答する/思い出せない/✕」が反応**し、カードが閉じる。
   - [ ] クリックしても**前面の別アプリがアクティブのまま**（フォーカスを奪わない＝非アクティブ Panel）。
   - [ ] NDJSON に `realtime_answer` / `realtime_skip` が残る（`~/Documents/GSE-sessions/gse_*.ndjson`）。
4. カード**外**をクリック → 背後アプリが反応（`setIgnoreCursorEvents(true)` 領域は透過）。

### B. Nudge カードのクリック検証
1. `force_nudge` で Nudge を表示。
2. 期待:
   - [ ] 「詰まってない/今はもがきたい/閉じる」が初回クリックで反応し `intervention_dismiss` が残る。
   - [ ] カード外クリックは背後へ透過。

### C. Wall（全画面ブロック）非回帰
1. `force_wall` で Wall 発動。
2. 期待:
   - [ ] 全画面ブロックが従来どおり機能（QR 解除のみ）。背後アプリへクリックが**漏れない**
         （= 非アクティブ Panel + `setIgnoreCursorEvents(false)` でも hit-test はブロックされる）。
   - [ ] Wall 内の QR/ボタンはクリック可。解除後 overlay が透過状態へ戻る。

### D. IME 非回帰（Floating level の確認・GSE 固有の最重要）
1. 日本語入力に切替え、ローマ字でかな漢字変換（変換候補ウィンドウを出す）。
2. 期待:
   - [ ] IME 合成・候補確定が**従来どおり動く**（panel level を Floating に固定したため。
         tauri-nspanel #104 の「高 level が IME をブロック」を回避できているか）。
   - [ ] 候補ウィンドウ表示中に HMM が pause する（IME_ACTIVE 検出は従来経路・非回帰）。

### E. macOS 26 (Tahoe) クラッシュ確認
- [ ] 起動時に WKWebView が落ちない。wry #1576 は macOS 26 **Beta 2** の Apple フォント登録バグ
      （`status: upstream`・wry/tauri 側の不具合ではない）。Beta 2 で落ちる場合の暫定回避は
      Font Book → Advanced → Reset Fonts。**現行の macOS 26 リリース（26.0.1+）で検証**すること。

## 結果の解釈
- **A/B が初回クリックで効き、かつ前面アプリのフォーカスを奪わない** → 修正成功（NSPanel 確定）。
- **まだ無反応 / 背後アプリが反応する** → panel 変換が効いていない。確認:
  1. 端末ログに `Failed to convert overlay to NSPanel` が出ていないか（出ていれば to_panel 失敗）。
  2. setup() がメインスレッドで走っているか（to_panel は main 限定）。
- **クリックは効くが前面アプリがアクティブ化される（フォーカスを奪う）** → style mask が
  非アクティブになっていない。`set_style_mask(1<<7)` が適用されているか確認。
- **JS の show/hide/setSize が効かず overlay の表示制御が壊れる**（box 化しない/隠れない等）
  → Panel 化で標準窓 API が一部効かない可能性（Agent2 の懸念）。その場合のフォールバックは
  Rust 側で `panel.show()` / `order_out` / `set_ignore_mouse_events` を Tauri command 化して
  Overlay.tsx から invoke する（窓制御を Rust へ寄せる）。

## Windows 非回帰
- tauri-nspanel は macOS 限定依存・登録も `#[cfg(target_os = "macos")]`。Windows は overlay 窓・
  `setIgnoreCursorEvents` 経路とも従来どおり（変更なし）。
- 可能なら実機で Probe/Nudge のクリックが従来どおり効くことを確認。

## 補足
- 非アクティブ Panel は窓を key 化してもアプリを foreground 化しない（非ブロック設計を維持）。
- 既知 gotcha: nspanel #104（高 level で IME ブロック→Floating 固定で回避）/ #110
  （最後の panel を閉じると ExitRequested 不発火→終了経路を要確認）/ #115（tracking-area 自動リサイズ）。
