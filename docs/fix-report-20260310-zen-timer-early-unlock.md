# Fix Report: Zen Timer 早期解除ボタン追加 (v2.21)

**日付:** 2026-03-10
**対象バージョン:** v2.20 → v2.21

---

## 目的

Wall（介入ロック）発動時にスマートフォンに表示される Zen Timer 画面に、ユーザーが任意のタイミングでロックを解除できる「早期解除する」ボタンを追加する。

---

## 修正プロンプトの有効性判定

| 項目 | 判定 | 理由 |
|------|------|------|
| デグレ防止要件 | **遵守可能** | 変更は `TIMER_HTML_TEMPLATE` 文字列内の HTML/CSS/JS のみ |
| 早期解除ボタン追加 | **有効** | 既存の `/unlock` エンドポイントを再利用。新規エンドポイント不要 |
| CSS スタイリング | **有効** | セカンダリアクション風で主ボタンと視覚的に差別化 |
| JS 処理 | **有効** | `finishUnlock()` 共通関数を抽出し、二重解除を `done` フラグで防止 |

### 副作用分析

- **Rust ロジック:** `engine.rs`, `features.rs`, `lib.rs` — 変更なし
- **サーバーロジック:** `dispatch_request()`, `/unlock` エンドポイント, ポート割り当て — 変更なし
- **フロントエンド:** `Overlay.tsx`, `App.tsx` — 変更なし
- **既存の Unlock Wall ボタン:** タイマー完了後に表示される動作は不変
- **二重解除防止:** `done` フラグにより、早期解除ボタンと通常ボタンのどちらが先に押されても `/unlock` は1回のみ POST

---

## 実施した修正

### 対象ファイル: `src-tauri/src/wall_server.rs` (HTMLテンプレート文字列のみ)

### 1. HTML要素の追加

タイマー下部に早期解除ボタンを追加:
```html
<button class="early-unlock-btn" id="earlyUnlockBtn"
        onclick="doEarlyUnlock()">&#x1F513; 早期解除する</button>
```

- 常時表示（タイマー進行中に使用可能）
- タイマー完了時（0:00到達後）に `display:none` で非表示化（代わりに主ボタン「Unlock Wall」が表示される）

### 2. CSSスタイル

```css
.early-unlock-btn {
  margin-top: 1.5rem;
  padding: 0.6rem 1.5rem;
  font-size: 0.85rem;
  font-weight: 500;
  color: rgba(248,250,252,0.5);      /* 半透明テキスト */
  background: transparent;            /* 背景なし */
  border: 1px solid rgba(248,250,252,0.2); /* 控えめなボーダー */
  border-radius: 8px;
  cursor: pointer;
}
```

**設計意図:** 主ボタン（緑・大・太字）と差別化し、セカンダリアクション風の控えめなデザインにすることで、タイマー完了まで待つことを暗に推奨しつつ、緊急時の早期解除も可能にする。

### 3. JavaScript処理

```javascript
// 共通解除関数（二重呼び出し防止付き）
function finishUnlock() {
  done = true;
  // UI更新 + /unlock POST
  // 両ボタンを非表示化
}

// タイマー完了後の解除（既存）
window.doUnlock = function() {
  if (done || !timerDone) return;
  finishUnlock();
};

// 早期解除（新規）— timerDone ガードなし
window.doEarlyUnlock = function() {
  if (done) return;
  finishUnlock();
};
```

**二重解除防止:** `done` フラグにより、どのパスからも `/unlock` POST は1回のみ実行される。

### 4. タイマー完了時のボタン遷移

```javascript
if (remaining <= 0 && !timerDone) {
  // ...
  unlockBtn.classList.add('visible');     // 主ボタン表示
  earlyUnlockBtn.style.display = 'none'; // 早期解除ボタン非表示
}
```

タイマーが0:00に到達すると、早期解除ボタンは消え、代わりに目立つ主ボタン「Unlock Wall」が表示される。

---

## デグレッション防止チェック

- [x] HMM 推論ロジック（78個のエミッション確率）— 未変更
- [x] 1Hz 動的ゲート — 未変更
- [x] 沈黙バッファ管理・3打鍵要件 — 未変更
- [x] WallServer 起動・停止ロジック — 未変更
- [x] ポート割り当て・ファイアウォールルール — 未変更
- [x] `/unlock` エンドポイントのルーティング — 未変更
- [x] `Overlay.tsx` / `App.tsx` の通信・表示ロジック — 未変更
- [x] `wall-phone-connected` イベント発行 — 未変更
- [x] `navigator.wakeLock` — 未変更

---

## ビルド確認

```
cargo build — OK (no warnings, no errors)
```

---

## v2.20 との関係

v2.20 ではタイマー完了後の手動タップを必須とする設計に変更した。v2.21 はその主ボタンの動作を維持しつつ、タイマー進行中にも解除可能なセカンダリボタンを追加する。これにより「2分待つことを推奨するが強制はしない」UXポリシーに移行した。
