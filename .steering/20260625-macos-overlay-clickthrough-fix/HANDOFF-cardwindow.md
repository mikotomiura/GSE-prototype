# 次セッション開始プロンプト（macOS 介入カードのクリック無反応 — 専用不透明 card 窓への移設）

> このファイル本文を新セッションの最初に貼る。GSE-prototype 用。実装系なので `/fix-bug` で継続。
> ブランチは **`fix/macos-overlay-clickthrough`**（WIP コミット済み）。`*.rs`/`*.tsx` 変更につき
> `architecture-rules`/`rust-standards`/`typescript-standards`/`intervention-design`/`hook-constraints` 参照。

---

## 0. いま直している不具合（最重要・一言で）
macOS で被験者向け介入カード（**Probe** = `ProbeCard.tsx`、**Nudge** = `Overlay.tsx`）が
**表示されてもボタンが押せない**（クリックが透明 overlay 窓を素通りして背後アプリが反応）。
複数回の実機検証で原因を**実測で確定**済み（下記）。今は「専用の不透明 card 窓」への移設を実装中。

## 1. 確定した根本原因（実測で確認済み・ここが肝）
1. **透明 overlay 窓は macOS でマウスイベントを webview に一切配送しない。**
   DIAG 計器（カードに紫バッジで pointer/click カウント）で、カード上の **pointerDown も click も
   ずっと 0**。＝ クリックが webview の DOM に届いていない。CSS でもボタンでも記録経路でもない。
2. **隠れた窓（`hide()`/orderOut）は macOS で webview の JS が休眠し、Tauri イベントを取りこぼす。**
   新規 card 窓に `[CARD] CardWindow mounted` は出るが、`debug_force_probe` を 76 回 emit しても
   `onActiveChange(true)` が一度も出ない＝ `probe_triggered` が休眠中の card 窓に届かない。
   （overlay が動いていたのは `start_session` で show 済みで JS が起きていたから。）

## 2. 除外済み（**もう試さない**・時間の無駄）
- ❌ `ignoresMouseEvents` を Rust から直接 NO に設定（第一試行）→ 効かない。透明窓は別ゲート。
- ❌ `accept_first_mouse(true)`（commit ded646c の内容）→ 単独では効かない。透明窓が素通りさせるため。
- ❌ overlay を `transparent(false)` にする → **全画面が不透明の濃紺で覆われ操作不能**になった
  （`start_session` が overlay を maximize+show したまま React が hide しないため）。スクショで確認・revert 済み。
- ❌ `InterventionAction` の serde 命名（"Nudge" vs "nudge"）→ `snake_case` 指定済みで正しい。シロ。
- ❌ 「nudge が出ないのは overlay ポーリングの休眠」説 → **誤り**。ログに
  `[DIAG] force_nudge consumed by overlay poll` が出る＝ポーリングは回って消費している。
  （nudge が出にくいのは force_nudge がワンショットフラグ＋500ms poll で取りこぼしやすいだけ。
   一度出れば nudgeVisible が保持。ただし**透明 overlay なのでクリックは効かない**＝本丸はやはり透明窓。）
- 参考: #1 backend ログchannel 不具合（別タスク `.steering/20260626-phase1-card-repro-backend-fix/`）は
  **別件**。dev 実行では fallback で `File::create` 成功・channel 切断なし（記録は届けば残る）。混同しない。

## 3. 採用方針（確定）= 専用 **不透明** card 窓へ移設
透明 overlay は **Wall（全画面ブロック）専用**に残し、Probe/Nudge は **新しい不透明 small 窓
`label="card"`** に載せる。不透明窓は macOS で通常どおりクリックを受ける。窓外は窓が無いので
背後へ透過＝**非ブロック設計は維持**。フォーカスも奪わない（`focused(false)`）。

### 隠れ窓 JS 休眠への対処（重要）
card 窓は **hide() しない**。常に show のまま **画面外(-20000,-20000) ⇄ 右上** を `setPosition` で
出し入れする。`start_session` で一度 show して JS を起こす（`position(-20000,-20000)` で生成済みなので
show してもユーザーには見えない）。

## 4. いま出来ている実装（WIP・このブランチにコミット済み）
**Rust `src-tauri/src/lib.rs`:**
- setup() に `label="card"` 窓を追加: 不透明・`decorations(false)`・`always_on_top`・`skip_taskbar`・
  `accept_first_mouse(true)`・`resizable(false)`・`inner_size(380,480)`・`position(-20000,-20000)`・
  `focused(false)`・`visible(false)`。
- `start_session`: overlay の show に続けて **card 窓も show**（画面外で JS 起こし）。
- overlay 窓は**元に戻した**（`transparent(true)`・accept_first_mouse 無し）= Wall 専用。
- `card_dbg(msg)` コマンド追加（stdout に `[CARD] ...` を出す診断）。invoke_handler に登録済み。

**Frontend:**
- `src/components/CardWindow.tsx`（新規）: `label="card"` 窓のルート。`ProbeCard` を描画。
  probeActive で 右上⇄画面外 を `setPosition`（hide しない）。`[CARD]` 診断 + 2秒ハートビート。
- `src/App.tsx`: `windowLabel === "card"` → `<CardWindow/>` を return。import 追加済み。
- `src/components/Overlay.tsx`: **ProbeCard を撤去**（card 窓へ移設のため）。import も削除。
  Nudge と Wall はまだ overlay に残っている（= Nudge は**まだ透明窓なのでクリック不可**）。
- `src/main.tsx`: overlay body を transparent に戻す（元のまま）。

**DIAG 計器（検証用・最後に全部消す）:** ← 完了前に必ず除去
- `lib.rs`: `card_dbg` コマンド + 登録（203, 1776 付近）、`get_intervention_decision` 内の
  `tracing::info!("[DIAG] force_nudge consumed by overlay poll")`（291 付近）。
- `ProbeCard.tsx`: `diagPointer`/`diagClick` state・`onPointerDown`・紫バッジ・回答するの onClick 計測。
- `Overlay.tsx`: 同様の `diagPointer`/`diagClick`・nudge カードの onPointerDown・紫バッジ・閉じるの計測。
- `CardWindow.tsx`: `dbg()`・heartbeat・各種 `[CARD]` ログ。

## 5. 次にやること（着手順）
1. **検証**: `GSE_DEBUG=1 VITE_GSE_DEBUG=1 npm run tauri dev` → スタート → 別アプリ前面 →
   📝 プローブ強制表示。期待:
   - 端末に `Card window shown off-screen (JS wake)`、`[CARD] heartbeat N` が継続、
     プローブ押下で `[CARD] ProbeCard onActiveChange(true)` → `move on-screen` → `on-screen OK`。
   - **画面右上に不透明カードが出てクリックが効く**（紫 DIAG が増える／「回答する」で閉じる／
     NDJSON に `realtime_answer` が残る）。
   - もし `onActiveChange(true)` すら出ない → イベントがまだ届いていない。次の手は「card 窓を
     画面外で常時 show のまま（今の方式）でも JS が休眠するか」を heartbeat で確認し、休眠するなら
     **probe を card 窓へ `emit_to("card", ...)` で直接送る**／Rust に pending probe を持たせ
     card 窓が show 時に fetch する方式へ。
2. **Probe が効いたら Nudge も card 窓へ移設**: Overlay の nudge UI（`aside.nudge-card` 一式 +
   `handleNudgeDismiss` + silent タイマー）を CardWindow へ移す。nudge のトリガは**ポーリング依存を
   やめてイベント push** に: `force_nudge` を `app.emit("show-nudge")` に変更し、実 nudge は main 窓
   （常時 JS 稼働）の poll が `action==="nudge"` を検知して `emit("show-nudge")`。card 窓が listen して表示。
   （overlay 側の FORCE_NUDGE/nudge ロジックは撤去。overlay は Wall 専用に。）
3. **DIAG 計器を全部除去**（上の一覧）。`main.tsx`/`Overlay.tsx`/`ProbeCard.tsx`/`CardWindow.tsx`/`lib.rs`。
4. **見た目調整**: card 窓 380x480 の余白を詰める（カードサイズに）。multi-display/Retina で右上座標が
   崩れないか（`currentMonitor` の scale 反映済み）。
5. **テスト**: `cargo build --target aarch64-apple-darwin` / `npm run build` / `cargo test --lib`。
   実機 smoke（Probe/Nudge クリック可・カード外は透過・Wall 全画面ブロック非回帰・Windows 非回帰）。
6. **完了処理**: code-reviewer + security-checker → `/cross-review`（無関係な未ステージ変更は stash）→ PR。

## 6. ビルド/テストの定石
```bash
# 開発起動（デバッグボタン＋backend gate 両方必須）
GSE_DEBUG=1 VITE_GSE_DEBUG=1 npm run tauri dev
# 静的検証
~/.cargo/bin/cargo build --target aarch64-apple-darwin
npx tsc --noEmit
cd src-tauri && ~/.cargo/bin/cargo test --lib
```
- **dev は必ず `GSE_DEBUG=1`（runtime gate）と `VITE_GSE_DEBUG=1`（ボタン表示）の両方**。
  片方だけだと「ボタンは見えるが backend が拒否して無反応」になる（過去のハマりどころ）。
- dev ログ（NDJSON）は `~/Documents/GSE-sessions/gse_*.ndjson`。`realtime_answer`/`realtime_skip`/
  `intervention_dismiss` が出ていればクリックが backend に届いた証拠（クリック成否の客観指標）。

## 7. 主要ファイル
- `src-tauri/src/lib.rs`: overlay/card 窓生成（setup, ~1686/~1710）、`start_session`(~1006)、
  `force_nudge`(~194)、`debug_force_probe`(~204)、`get_intervention_decision`(~266)、`card_dbg`(~203)。
- `src/App.tsx`: 窓ルーティング（`windowLabel` で card/overlay/main 分岐）、500ms poll（main/overlay）。
- `src/components/CardWindow.tsx`: card 窓ルート（probe 描画・位置制御）。
- `src/components/Overlay.tsx`: overlay 窓（現状 Nudge+Wall。Nudge は card へ移す予定）。
- `src/components/ProbeCard.tsx`: probe カード本体（listen `probe_triggered`）。
- `src/main.tsx`: 窓別 body 背景（overlay のみ transparent）。

## 8. 制約（厳守）
- 非ブロック維持（カード外は背後へ透過）＋フォーカス非奪取。Wall 全画面ブロックは現状維持。
- macOS NSWindow/objc 操作は不要になった（不透明窓方式なので objc FFI は使わない）。
- `winapi`/`println!`/`eprintln!`/`any` 禁止。Rust は `tracing`/`anyhow`。HMM/`schema_dto.rs` 不変。
- Windows 非回帰（card 窓は Windows でも普通に動くはず。透明問題は macOS 固有）。
- 既存テスト無断削除しない。diff に無関係な未ステージ変更を混ぜない。

## 9. メモリ
`macos-overlay-clickthrough-bug.md` を最新化すること（真因＝透明窓＋隠れ窓JS休眠、card 窓方式）。
commit ded646c の説明（accept_first_mouse で直る）は**誤り**なので memory も訂正する。
