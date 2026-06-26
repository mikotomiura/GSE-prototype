# タスクリスト

## 調査（このセッションで完了）
- [x] 症状の切り分け（debug_force_probe 経由・console 無反応・赤帯なし・両カード・背後アプリ反応）
- [x] CSS 無実を確認（overlay-root/カードは pointer-events:auto）
- [x] 窓構成特定（独立 overlay 窓・transparent/decorations(false)/always_on_top・非フォーカス）
- [x] 真因の方向確定（setIgnoreCursorEvents(false) が macOS で実効化していない）
- [x] codex-consult 実施（盲点 7 点を design.md に反映）
- [x] 次セッション用プロンプト作成（next-session-prompt.md）

## 実装（/fix-bug）
- [x] 第一試行（誤診・撤回）: Rust 側 click-through 権威化（setIgnoresMouseEvents 直接操作＋読み返し）。
      実機で**解決せず** → 真因は ignoresMouseEvents ではないと判明。Rust objc 機構は全撤去。
- [x] 真因確定（ソースレベル調査）: **非 key 窓 + WKWebView acceptsFirstMouse 既定 false**。
      非アクティブ窓のクリックがボタンへ配送されず毎回握りつぶされる（decisions.md D6）。
- [x] 最小修正: overlay 窓生成に `WebviewWindowBuilder::accept_first_mouse(true)` を付与（lib.rs）。
      `setIgnoreCursorEvents` の toggle は従来 JS 経路を維持（このゲートは正しく動作）。
- [x] ビルド検証: cargo build (aarch64) OK / npm run build (tsc && vite build) OK。
- [ ] **macOS 実機操作確認（ユーザー・runbook.md）**: 非アクティブ窓で Probe/Nudge が初回クリックで発火。
      ＋ Windows 非回帰。
- [ ] 完了処理: code-reviewer + security-checker（差分が builder 1 行のため軽量）→ /cross-review → PR。

## 実装 v3（NSPanel 化・D7・ユーザー承認 2026-06-26）
- [x] Web 調査で真因＝非 key 窓のクリック非ルーティングを確定。canonical = NSPanel 化（decisions D7）。
- [x] WIP card 窓系を revert: CardWindow.tsx 削除 / lib.rs の card 窓生成・start_session show・card_dbg 撤去 /
      App.tsx の card 分岐撤去 / Overlay.tsx に ProbeCard 復帰 / main.tsx コメント復帰。
- [x] DIAG 計器を全除去（Overlay.tsx / ProbeCard.tsx の diagPointer/diagClick・紫バッジ・[DIAG] log /
      lib.rs の force_nudge consumed log）。grep でヒットゼロ確認（security-checker）。
- [x] Cargo.toml: tauri-nspanel 依存追加（macOS gate・rev 固定 18ffb9a2）。
- [x] lib.rs: tauri_nspanel プラグイン登録 + setup() で overlay を to_panel() → 非アクティブ mask(1<<7) +
      canBecomeKeyWindow=YES(自動) + Floating level(4) + collection behavior。overlay_panel.rs 新規。
- [x] ビルド検証: cargo build (aarch64) OK / npx tsc --noEmit clean / cargo test --lib 227 passed / npm run build OK。
- [x] code-reviewer + security-checker 実行。CRITICAL/HIGH ゼロ。MEDIUM 反映（rev 固定・順序・コメント）。
- [x] 実機 dev 起動でクラッシュ捕捉（D8: NSPanel + `maximize()` が WKWebView を NSRangeException で
      クラッシュ）→ maximize/unmaximize を全廃し明示 setSize/setPosition に置換。再ビルド OK。
- [x] **macOS 実機 smoke（ユーザー）**: クラッシュ解消・**ボタン押下可（クリック解決）**・
      `isKeyWindow=false`（フォーカス非奪取）・Wall full flow 非回帰 を確認。真因＝capability 不足（D11）+
      NSPanel（D7）+ Rust 権威 ignore_mouse（D9）+ hide 廃止（D10）+ maximize 撤去（D8）+ resign_key（D12）。

## 「記録に失敗」の真因確定と修正（このセッション・D13）
- [x] **真因確定（channel ではなかった）**: 計器 (fe_dbg で Err 文字列をターミナルへ) を仕込み実機再現。
      `[FE] record_realtime_answer FAILED: window_end_ms must be >= window_start_ms`。log channel `try_send`
      には到達せず、**`record_realtime_*` の窓検証で弾かれていた**。コミット済み backend 修正(342a444)は
      正しく無関係。詳細 `investigation-record-failure.md`。
- [x] **修正**: `self_marker_window_clamped`(probe_scheduler.rs) が窓**終端**を未クランプで、起動5s以内の
      プローブ/マーカーで `we = t−5s < session_start ≤ ws` に反転していた。`let we = we.max(ws);` で終端を
      始端以上にクランプ（セッション未収窓はゼロ幅 `[ws,ws]` に畳む）。回帰テスト追加。実スケジューラは
      31s ウォームアップで非該当。M/D 自己マーカーの起動直後ラベル損失も同時に解消。
- [x] DIAG/診断（fe_dbg・[PANEL]/[FE] log・overlay HB・ignoresMouseEvents 読み戻し）を**全除去**。grep ゼロ。
- [x] cargo build/tsc/cargo test グリーン（228 passed）→ replay snapshot 一致（HMM 不変）。
- [x] **実機 smoke（ユーザー）**: 起動3.0s（<5s）のデバッグプローブで `FAILED` 消失・`realtime_label` が
      NDJSON に着地（ゼロ幅窓 we−ws=0）・nudge dismiss も intervention_response 着地・5s 超は通常窓。
- [x] code-reviewer + security-checker（CRITICAL/HIGH ゼロ）。MEDIUM 反映: 非macOS set_overlay_interactive の
      no-op 可視化（warn）/ 死んだ `allow-hide` capability 除去。
- [x] commit（git-workflow・対象ファイル列挙・無関係未ステージ除外）= 8aca4db。
- [x] /cross-review（commit 済タスク差分 HEAD~1..HEAD・secrets-filter→budget→codex read-only）。
      Codex High「widgetOnly box化失敗→全画面ブロック化」は**誤検知寄りと判定**: 非ブロックへ倒すと
      窓全体 ignoresMouseEvents=true でカード自体クリック不能=死んだボタン (元バグ) に戻る。較正データ
      優先で全画面ブロック維持が正、コメントで trade-off を明文化 (Overlay.tsx)。他 (to_panel 失敗フォール
      バック・nspanel supply-chain・macOS 手動検証) は Claude レビュー/decisions/runbook と一致・対応済 or 既知。
- [x] メモリ `macos-overlay-clickthrough-bug.md` を「解決済（capability+NSPanel）」+ D13 record 真因(窓反転)修正に更新。
- 引き継ぎ全文: `HANDOFF-nspanel-DONE-and-record-failure.md`

## 完了処理
- [x] decisions.md（D5 第一試行・D6 真因訂正・D7 NSPanel 確定）
- [x] runbook.md（acceptFirstMouse 前提に更新・不足時の NSPanel/専用窓 follow-up 明記）
- [ ] runbook.md を NSPanel 前提に更新（実機検証項目）
- [ ] ブランチ fix/macos-overlay-clickthrough で commit・PR（実機検証後）
