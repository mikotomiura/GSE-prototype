# 引き継ぎ（macOS 介入カード クリック修正＝完了／露出した「記録に失敗」＝次の課題）

> このファイル本文を新セッション冒頭に貼る。GSE-prototype 用。ブランチ **`fix/macos-overlay-clickthrough`**。
> 実装系。`*.rs`/`*.tsx`/capabilities を触るので `architecture-rules`/`rust-standards`/
> `typescript-standards`/`intervention-design`/`hook-constraints`/`data-privacy` を参照。
> **未コミット**（WIP commit は f770ae4 のまま。今回の変更は全て working tree）。

## 0. 結論（一言）
**macOS の介入カード クリック無反応バグは解決した**（Probe/Nudge のボタンが効き、前面アプリの
タイピングフォーカスも奪わない＝実機確認済み）。**そのクリック修正で隠れていた別バグ「記録に失敗」
（`record_realtime_answer`/`record_realtime_skip` が失敗）が露出**した。これが次セッションの主タスク。

## 1. 確定した真因と修正（decisions.md D7〜D12 に詳細）
症状を追う過程で**複数のゲートが直列に存在**していた。最終的に効いた修正は以下の重ね合わせ：

1. **★真の即時ブロッカー = Tauri capability 不足（D11）**: `capabilities/default.json` が overlay 窓に
   `core:window:allow-set-size` / `allow-set-position` を**与えていなかった**。box 化の
   `setSize → setPosition → setOverlayInteractive(true)` の順で `setSize` が permission 例外を投げ、
   **クリック透過解除（ignoresMouseEvents=NO）に到達せず**素通りしていた。→ 2 権限を追加（`allow-maximize` は
   D8 で禁止のため除去）。これが当初からの本当の主因（カードは position:fixed で出るのに押せない症状に一致）。
2. **NSPanel 化（D7）= gate2 + 非フォーカス**: overlay 窓を tauri-nspanel で非アクティブ NSPanel
   （`NSWindowStyleMaskNonActivatingPanel=1<<7` + `canBecomeKeyWindow=YES` 自動 + Floating level=4）へ
   変換。非 key 窓でもクリックが webview へ配送される。`src-tauri/src/overlay_panel.rs`（新規）。
3. **クリック受理は Rust 権威（D9）**: JS の `setIgnoreCursorEvents` は NSPanel 化窓で実効しないため、
   Tauri command `set_overlay_interactive(interactive)` → `RawNSPanel::set_ignore_mouse_events(!interactive)`
   を直接叩く。Overlay.tsx の 4 箇所を置換。
4. **idle hide 廃止（D10）**: idle 時に `win.hide()` すると webview JS が休眠し probe_triggered を
   取りこぼす。hide せず「透明＋クリック透過」で出したまま JS を生かす。
5. **maximize/unmaximize 全廃（D8）**: NSPanel 化窓で `maximize()` は内部 `setStyleMask:` が WKWebView の
   contentLayoutRect オブザーバ解除に失敗し **NSRangeException でクラッシュ**。全画面化は明示
   `setSize`/`setPosition`（モニタ全域）で行う。
6. **フォーカス非奪取（D12）**: `win.show()` が `makeKeyAndOrderFront` で panel を key 化してしまう
   （`set_becomes_key_only_if_needed(true)` では抑止できなかった）。`set_panel_interactive` で
   `set_ignore_mouse_events` 後に **`resign_key_window()`** を呼び、奪った key を即返す。
   → 実機ログで **`interactive=true -> ignoresMouseEvents=false isKeyWindow=false isVisible=true`** を確認。
   クリックは `accept_first_mouse(true)`（overlay builder）+ 非アクティブ panel で非 key のまま届く。

### 実機確認できたこと（dev・GSE_DEBUG=1 VITE_GSE_DEBUG=1）
- 起動クラッシュ無し（D8 解決）。HB（overlay JS 生存）継続。probe_triggered が ProbeCard に到達。
- プローブ表示 → ボタン押下で **クリックは効く**（押下可能）。`isKeyWindow=false`（フォーカス非奪取）。
- Wall full flow（QR/スマホ接続→unlock）非回帰 OK。

## 2. ★次セッションの主タスク：「記録に失敗」（record 失敗）の調査・修正
**症状**: プローブのボタンを押せるようになった結果、`ProbeCard.tsx` が `record_realtime_answer`
（または `record_realtime_skip`）を invoke → **失敗して「記録に失敗しました。もう一度お試しください。」**
のインラインエラーを表示（カードは保持）。

**原因の方向（未確定・要調査）**: `lib.rs fn record_realtime_answer` は
`log.lock().tx.try_send(LogEntry::realtime_label_answered(...)).map_err(log_send_error)` で、
**log channel への `try_send` 失敗**時に Err を返す。= ログチャネルが full or 受信側 disconnect。
これは**今回の overlay 変更とは無関係**（record/logger は未変更）。クリックが効かず従来この経路に
到達できなかったため**隠れていた既存バグ**で、別タスク **`.steering/20260626-phase1-card-repro-backend-fix/`**
（#1 backend log channel 不具合）と同根の可能性が高い。

**調査の起点**:
- `logger.rs` の channel 種別（bounded/unbounded）・容量・writer スレッド生存。`try_send` が
  `Full` か `Disconnected` か（`log_send_error` の分岐）を**まず tracing で切り分け**る。
- `debug_force_probe` 経路特有か（`build_probe_ref(source="random_probe", probe_id)` 検証含む）。
  実プローブ（scheduler 発火）でも同様に失敗するか確認。
- `.steering/20260626-phase1-card-repro-backend-fix/` の調査記録・要件を先に読む（重複調査回避）。
- `log-analyzer` サブエージェントで NDJSON / dev ログを解析させると速い。

## 3. ★着手前に必ずやる「DIAG/診断の全除去」（コミット前提）
実機検証用に仕込んだ診断を**すべて削除**してから完了処理へ。一覧：
- `src-tauri/src/lib.rs`:
  - `fn fe_dbg`（コマンド定義）+ invoke_handler の `fe_dbg,` 登録。
  - `set_overlay_interactive` 冒頭の `tracing::info!("[PANEL] set_overlay_interactive called...")`。
- `src-tauri/src/overlay_panel.rs`:
  - `set_panel_interactive` 内の **`// DIAG TEMP` ブロック**（`use ...objc...; msg_send! で ignoresMouseEvents/
    isKeyWindow 読み戻し + tracing::info!("[PANEL] ...")`）を丸ごと削除。`is_key`/`ignores` 関連。
    → これを消すと objc の deprecated/unexpected-cfg 警告も消える。
  - `set_ignore_mouse_events` / `resign_key_window` 本体は**残す**（本番ロジック）。
- `src/components/Overlay.tsx`:
  - **overlay HB** の useEffect（`invoke("fe_dbg", {msg:`overlay HB ${n}`})` の setInterval）削除。
  - 統合 effect 内の `invoke("fe_dbg", ...)` 3 箇所（effect 入口 / after show / widget calling /
    CATCH）削除。
- `src/components/ProbeCard.tsx`:
  - listener 冒頭の `invoke("fe_dbg", {msg:`ProbeCard probe_triggered received...`})` 削除。
  - `onActiveChange` effect 内の `invoke("fe_dbg", {msg:`ProbeCard onActiveChange...`})` 削除。
- grep 確認: `grep -rn "fe_dbg\|\[PANEL\]\|\[FE\]\|overlay HB\|DIAG TEMP" src src-tauri/src` がゼロになること。
- 注: 旧 WIP の DIAG（card_dbg/diagPointer/紫バッジ等）は既に revert 済み（card 窓方式ごと撤去）。

## 4. 変更ファイル一覧（このセッションの working tree・未コミット）
- `src-tauri/Cargo.toml` — `tauri-nspanel`（git・**rev 固定** 18ffb9a2…・macOS gate）追加。
- `src-tauri/Cargo.lock` — 上記 + transitive（cocoa/objc/block 等）。
- `src-tauri/capabilities/default.json` — **`allow-set-size` / `allow-set-position` 追加**・`allow-maximize` 除去。★主因修正。
- `src-tauri/src/overlay_panel.rs`（新規）— `convert_overlay_to_panel`（to_panel + style mask + level +
  collection behavior + becomes_key_only_if_needed）/ `set_panel_interactive`（ignore_mouse_events +
  resign_key_window + ★DIAG 読み戻し=要除去）。
- `src-tauri/src/lib.rs` — `mod overlay_panel`(cfg macos) / builder に `tauri_nspanel::init()`(cfg) /
  setup() で `convert_overlay_to_panel` / `set_overlay_interactive` コマンド + 登録 /
  `fe_dbg`(★要除去) + 登録 / start_session の maximize 撤去（show のみ）/ card 窓系・card_dbg・旧 DIAG は revert 済。
- `src/App.tsx` — card 窓ルーティング撤去（revert 済）。
- `src/components/Overlay.tsx` — ProbeCard 復帰 / `setOverlayInteractive` ヘルパ + 4 箇所置換 /
  idle hide 廃止 / maximize・unmaximize 撤去 / ★HB・effect 診断（要除去）。
- `src/components/ProbeCard.tsx` — 旧 DIAG 撤去済 / ★listener・onActiveChange の fe_dbg（要除去）。
- `src/main.tsx` — コメント revert 済。
- `src/components/CardWindow.tsx` — **削除**（card 窓方式撤去）。

## 5. ビルド/テスト定石
```bash
# dev（デバッグボタン＋backend gate 両方必須）
GSE_DEBUG=1 VITE_GSE_DEBUG=1 npm run tauri dev
# 静的検証
cd src-tauri && ~/.cargo/bin/cargo build --target aarch64-apple-darwin
npx tsc --noEmit
cd src-tauri && ~/.cargo/bin/cargo test --lib --target aarch64-apple-darwin   # 直近 227 passed
```
- dev ログ NDJSON: `~/Documents/GSE-sessions/gse_*.ndjson`。`realtime_answer`/`realtime_skip` が
  残れば記録成功（= 記録失敗バグ解決の客観指標）。
- 既知の残警告: `lib.rs:~1428 was_active 未使用`（既存・本タスク無関係）。DIAG 除去後はこれのみになる想定。

## 6. 完了処理（記録失敗の修正後）
1. DIAG 全除去（§3）→ `cargo build` / `tsc` / `cargo test --lib` グリーン確認。
2. 実機 smoke 再確認（クリックでカード閉じ＋`realtime_answer` が NDJSON に残る＋フォーカス非奪取＋
   Wall 非回帰＋IME 合成非回帰）。runbook: 同ディレクトリ `runbook.md`（NSPanel 前提に更新済）。
3. `code-reviewer` + `security-checker` 並列 → `/cross-review`（Claude∥Codex）。
   - 無関係な未ステージ変更（`.codex/budget.json`/`advice.md`/削除済 docs PDF/`scripts/*.sh`/`MEMO`/
     他 `.steering/` 等、**セッション開始時から存在**）は **stash してから** cross-review（codex 自己ブロック回避）。
4. コミット（`git-workflow` 準拠・`git add` は対象ファイル列挙、`-A` 禁止）。Refs: 本 steering。
   - メッセージ例: `fix(overlay): macOS 介入カードのクリックを NSPanel 化＋capability 修正で受理`。
   - 末尾 `Co-Authored-By: Claude Opus 4.8 (1M context) <noreply@anthropic.com>`。
5. メモリ更新: `macos-overlay-clickthrough-bug.md`（真因＝capability + NSPanel・解決済に更新）。

## 7. 既に更新済みの記録
- `decisions.md` … D7（NSPanel 採用）/ D8（maximize クラッシュ）/ D9（gate1 Rust 権威）/
  D10（hide 廃止 JS 休眠）/ **D11（★capability 主因）** / D12（resign_key でフォーカス非奪取）。
- `tasklist.md` … 実装 v3（NSPanel）まで反映。記録失敗は**未追記**（次セッションで追加）。
- `runbook.md` … NSPanel 前提の実機検証手順。
- メモリ `macos-overlay-clickthrough-bug.md` … D7〜D10 までは反映済（D11/D12 と「解決」は未反映）。

## 8. 制約（厳守）
- 非ブロック維持（カード外は背後へ透過）＋フォーカス非奪取（D12 維持）。Wall 全画面ブロック非回帰。
- panel level は **Floating 固定**（nspanel #104：高 level が IME をブロック・日本語 IME 必須制約）。
- maximize/unmaximize/fullscreen トグルは NSPanel 化窓で**禁止**（D8）。サイズは setSize/setPosition。
- `winapi`/`println!`/`eprintln!`/`any` 禁止。Rust は `tracing`/（このリポジトリは anyhow 非依存→
  `tauri::Result`/`Result<_,String>`）。HMM/`schema_dto.rs` 不変。Windows 非回帰（nspanel は macОS gate）。
- 既存テスト無断削除しない。diff に無関係な未ステージ変更を混ぜない。
