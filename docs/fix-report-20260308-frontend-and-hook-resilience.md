# Fix Report: フロントエンド介入ライフサイクル修正 & イベントドロップ検知

**日付:** 2026-03-08
**対象ファイル:** `src/App.tsx`, `src-tauri/src/input/hook_macos.rs`
**関連:** 包括的コードベース監査により検出された3つの優先課題

---

## 1. 問題の発見経緯

前回のセッションログ分析（`gse_20260308_034634.ndjson`）に続くコードベース全体の監査で、以下の3つの技術的課題が検出された。

- フロントエンド介入システム監査（Agent 3）: 5件中2件が優先対応
- スレッディング・競合状態監査（Agent 2）: 3件中1件が優先対応

---

## 2. 課題と修正内容

### 2.1 セッション未開始時のオーバーレイポーリング（Medium-High）

#### 問題
`App.tsx:59` の条件 `if (windowLabel !== "overlay" && !isStarted) return;` により、オーバーレイウィンドウはセッション開始前から常時ポーリングを実行していた。

バックエンドは `session_active=false` の間イベントをドレインするためデフォルト値（stuck=0.05）が返され **現時点での実害は低い** が、バックエンドにバグが混入した場合にセッション未開始でも Wall が発動するリスクがあった。

#### 修正内容
1. ポーリング条件を `if (!isStarted) return;` に変更（両ウィンドウ統一）
2. `handleStart()` でセッション開始時に `emit("session-started")` Tauri イベントを発行
3. オーバーレイ側に `listen("session-started")` を追加し `isStarted` を同期

```typescript
// App.tsx — Fix 1: ポーリングガード統一
useEffect(() => {
  if (!isStarted) return;  // 旧: if (windowLabel !== "overlay" && !isStarted) return;
  // ...
}, [isStarted, windowLabel]);

// App.tsx — Fix 1: セッション開始イベント発行
const handleStart = async () => {
  await invoke("start_session");
  setIsStarted(true);
  emit("session-started");  // 追加
};

// App.tsx — Fix 1: オーバーレイ側の購読
useEffect(() => {
  if (windowLabel !== "overlay") return;
  const unlisten = listen("session-started", () => setIsStarted(true));
  return () => { unlisten.then((f) => f()); };
}, [windowLabel]);
```

#### 副作用検討
| 項目 | 影響 | 判定 |
|---|---|---|
| メインウィンドウのポーリング | 変更なし（既に isStarted で制御） | 安全 |
| オーバーレイの Nudge/Wall 表示 | セッション開始後のみ動作（設計通り） | 安全 |
| useEffect の依存配列 | `[isStarted, windowLabel]` — 変更なし | 安全 |
| タイマーリーク | cleanup で clearInterval 済み | 安全 |

---

### 2.2 IPC 失敗時の安全側フォールバック（Medium）

#### 問題
`App.tsx:91-93` の catch ブロックが `console.error` のみで、IPC 失敗時に前回の高い stuck 値がそのまま維持され、Wall 累積カウンターが不正に加算され続ける。

ネットワーク遅延やバックエンドクラッシュ時に Lv2 Wall が誤発動する危険性があった。

#### 修正内容
catch ブロックで状態を安全側にリセット:

```typescript
catch (e) {
  console.error("Failed to fetch state:", e);
  setCognitiveState({ flow: 1.0, incubation: 0.0, stuck: 0.0 });
  stuckAccMsRef.current = 0;
}
```

#### 副作用検討
| 項目 | 影響 | 判定 |
|---|---|---|
| 一時的な IPC 失敗 | 次回成功時に正しい値に復帰 | 安全 |
| ダッシュボード表示 | 一瞬 Flow 100% が表示される（無害） | 許容 |
| Wall 累積 | リセットにより連続失敗でも Wall 不発動 | 安全（設計意図通り） |
| Nudge 表示 | stuck=0 で即座に Nudge 消失 | 安全 |

---

### 2.3 イベントドロップ時の警告ログ追加（Medium）

#### 問題
`hook_macos.rs:278` の `let _ = sender.try_send(event)` でチャネル（bounded(64)）満杯時のイベントドロップが完全に無視され、デバッグ・原因究明が不可能だった。

高負荷時や分析スレッドの処理遅延時にイベントが失われても、ログに何も記録されない。

#### 修正内容
`tracing::warn!` でドロップを記録（CLAUDE.md の規約に従い `eprintln!` ではなく `tracing` を使用）:

```rust
if let Err(e) = sender.try_send(InputEvent {
    vk_code,
    timestamp,
    is_press,
    is_repeat,
    is_backspace,
}) {
    tracing::warn!("InputEvent dropped (channel full): {}", e);
}
```

#### 追加修正: IME_OPEN メモリオーダリング
同ファイル `hook_macos.rs:249` の `IME_OPEN.load(Ordering::Relaxed)` を `Ordering::Acquire` に変更。JIS キー処理で `Release` オーダリングで書き込まれた値を、コンポジション状態マシンが確実に読み取れるようにする。

#### 副作用検討
| 項目 | 影響 | 判定 |
|---|---|---|
| CGEventTap コールバック性能 | warn! は失敗時のみ発火（通常パスは分岐1つ追加のみ） | 安全 |
| tracing ログ出力 | 既存の NDJSON ロガーとは独立 | 安全 |
| Acquire オーダリング | Release-Acquire ペアの正しい使用（性能差は無視可能） | 安全 |
| Windows 版 | windows_impl.rs 未作成のため非対象（将来移植時に同様の対応が必要） | N/A |

---

## 3. 未対応の残存課題（将来改善候補）

前回監査で検出された以下の課題は今回のスコープ外:

| # | 課題 | 重要度 | 理由 |
|---|------|--------|------|
| 1 | lib.rs:537-579 — 8秒 IME フェイルセーフの競合窓 | Low-Medium | 実害報告なし |
| 2 | Overlay.tsx — QR サーバー失敗時のエラー UI 不在 | Medium | UX 改善のみ |
| 3 | App.tsx + Dashboard — Monk Mode 500ms 競合ウィンドウ | Low-Medium | 極めて短い窓 |
| 4 | 観測ビン利用率 46.2% (12/26) | Low | HMM 精度改善候補 |

---

## 4. ファイル変更一覧

| ファイル | 変更内容 |
|---|---|
| `src/App.tsx` | ポーリングガード統一、session-started イベント発行/購読、IPC 失敗フォールバック |
| `src-tauri/src/input/hook_macos.rs` | try_send 失敗ログ追加、IME_OPEN Relaxed→Acquire |
| `README.md` | セッション開始画面セクション更新（ポーリングガード・IPC フォールバック記述） |
| `README.ja.md` | 同上（日本語版） |
