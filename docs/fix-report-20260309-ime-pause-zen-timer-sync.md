# Fix Report: IMEポーズ中イベント破棄 & Zen Timer手動解除同期 (v2.20)

**日付:** 2026-03-09
**対象バージョン:** v2.19 → v2.20

---

## 目的

macOS版で実装済みの2つの改善をWindows版に移植する:
1. IMEポーズ中のイベントバッファ汚染防止
2. Zen Timer（Wall解除タイマー）の手動解除仕様への変更

---

## 修正プロンプトの有効性判定

| Step | 指示内容 | 判定 | 理由 |
|------|---------|------|------|
| 1 | デグレ防止要件 | **制約条件** | 修正対象ではなく遵守事項 |
| 2 | IME pause中イベント破棄 | **有効** | pause中に`process_event()`を呼びバッファに蓄積しても、unpause時に`reset()`で全消去されるため無駄。CPU浪費かつ不要なメモリ使用 |
| 3a | Zen Timer手動解除 | **有効** | 自動解除では2分間「待つだけ」で済み、実際に離席・休憩する意図を強制できない |
| 3b | `wall-phone-connected`イベント発行 | **有効（バグ修正）** | Overlay.tsxが既にlistenしているが、バックエンドが一度も発行していなかった |
| 3c | `navigator.wakeLock` | **有効** | タイマー表示中にスマホ画面が消灯すると操作不能になるUX問題を防止 |

---

## 実施した修正

### 1. IMEポーズ中のイベント破棄 (`lib.rs`)

**修正前:**
```rust
Ok(event) => {
    extractor.process_event(event);  // ← pause中でも常にバッファへ
    // ログ記録
    let currently_paused = engine.get_paused();
    if currently_paused { was_paused = true; continue; }
    // ...以降の処理
}
```

**修正後:**
```rust
Ok(event) => {
    // ログ記録（全打鍵を記録、推論頻度とは独立）
    // IMEポーズ中はバッファ蓄積を含め全処理をスキップ
    let currently_paused = engine.get_paused();
    if currently_paused { was_paused = true; continue; }
    extractor.process_event(event);  // ← 非ポーズ時のみ
    // ...以降の処理
}
```

**効果:**
- 候補選択中のキーストローク（Space, Enter, 矢印等）がFeatureExtractorのバッファを汚染しない
- 不要な`process_event()`呼び出しによるCPU・メモリ使用を排除
- ログ記録は継続（IME中のキーイベントも生データとして保存）
- unpause時の`extractor.reset()`の動作は不変（クリーンスタートが保証される）

**副作用:** なし。unpause時にreset()でバッファが全消去されるため、pause中の蓄積は元々破棄されていた。

**型注釈の追加:** `process_event()`の呼び出し位置変更により、crossbeamチャネルの型推論が不可能になったため、`bounded::<InputEvent>(64)` と明示的な型注釈を追加。

### 2. Zen Timer手動解除 (`wall_server.rs` TIMER_HTML_TEMPLATE)

**修正前:** タイマーが0:00到達時に自動で`/unlock`をfetch → PCのWallが自動解除

**修正後:**
- タイマー0:00到達時にはUIのみ更新（`timerDone=true`）
- 「**Unlock Wall**」ボタンが表示される（`fadeIn`アニメーション付き）
- ユーザーがボタンをタップして初めて`/unlock`がfetch → Wallが解除

**UXテキスト変更:**
- `"Your PC unlocks automatically when the timer ends."` → `"Tap the button below when the timer ends."`
- タイマー完了後: `"Ready to unlock! Tap the button below."`

**設計意図:** 自動解除では「スマホの前で2分間座って待つ」だけで済んでしまい、実際に離席して身体を動かすという介入の本来の目的が形骸化する。手動タップにより、少なくともスマホを手に持って意識的にアクションを取る必要がある。

### 3. `wall-phone-connected`イベント発行 (`wall_server.rs`)

**修正前:** `/shake`エンドポイント（QRスキャン時にスマホが接続）でHTMLを返すだけ

**修正後:** HTMLレスポンスの前に`app.emit("wall-phone-connected", ())` を発行

**効果:** Overlay.tsxが既にlistenしていた`wall-phone-connected`イベントが実際に発火し、「Phone connected — Zen Timer running」バッジが正しく表示されるようになった。

### 4. `navigator.wakeLock` API追加 (`wall_server.rs` TIMER_HTML_TEMPLATE)

スマホ側タイマーページのJavaScriptに以下を追加:
```javascript
if('wakeLock' in navigator){
  navigator.wakeLock.request('screen').catch(function(){});
  document.addEventListener('visibilitychange',function(){
    if(document.visibilityState==='visible'){
      navigator.wakeLock.request('screen').catch(function(){});
    }
  });
}
```

**効果:** タイマー表示中にスマホの画面が自動消灯しない（Screen Wake Lock API対応ブラウザ）。`visibilitychange`イベントで復帰時にも再取得する。非対応ブラウザでは`catch`で静かにフォールバック。

---

## デグレッション防止チェック

- [x] 1Hz動的ゲート（`next_engine_update`）のループ制御 — 未変更
- [x] `is_repeat`除外の沈黙バッファ管理 — 未変更
- [x] 沈黙解除の3打鍵要件（silence-break protection） — 未変更
- [x] `f1 > 0.0` ガード条件 — 未変更
- [x] 沈黙ペナルティ（摩擦フロア）最低保証値 — 未変更
- [x] エミッションテーブルの全値 — 未変更
- [x] IME_ACTIVE ログ出力ロジック — 未変更
- [x] ポーズ→復帰時のバッファクリア（`extractor.reset()`） — 未変更
- [x] 3段階EWMA α遷移ロジック — 未変更
- [x] ペナルティビン（obs=25）確率 — 未変更

---

## ビルド確認

```
cargo build — OK (no warnings, no errors)
```
