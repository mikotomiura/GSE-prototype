---
name: intervention-design
description: >
  GSE の段階的介入システム設計規則。⚠️ Lv2 Wall / Zen Timer / Monk Mode / Early Unlock は
  2026-08-23 に削除された (ADR-015)。★ 現行は Lv1 Nudge と none/defer のみ。
  以下の状況で必須参照:
  - Overlay.tsx の Nudge 表示ロジックを変更するとき
  - 介入の発火トリガー・cooldown・daily cap を変更するとき
  - HIR (有害介入率) / dismiss 率の算出を変更するとき
  - intervention.rs の decide() / suppression を修正するとき
  - 介入 UI の非ブロック性 (クリック透過・box 化) を変更するとき
allowed-tools: Read, Grep, Glob, Edit
---



> ⚠️★★★ **2026-08-23: Lv2 Wall と Monk Mode は削除された**（**ADR-015**）。
> ★ 本 Skill の **Wall / Monk Mode / Early Unlock / QR / Zen Timer に関する記述はすべて無効**である。
> ⚠️ **ルール 5（Monk Mode は Wall を無効化するだけ）も無効** —— Monk Mode 自体が存在しない。
> ★ **有効なのは Lv1 Nudge と `none` / `defer` の扱いだけ**である。
> ⚠️ **HIR（有害介入率）は残る**（ADR-015 D3。★ ACT = `{nudge}` になった）。
> ★ Physical Anchor の運搬路は **ADR-015 D4 で空いた**（`physical-anchor` Skill 参照）。
> ⚠️ **見直し候補（未決）**: Nudge の時期（と有無）を本人が統制する経路 → `docs/architecture/intervention-decision-engine.md` §「見直し候補（未決）」R-1（2026-09-20 登録・★ Nudge を被験者に出す研究を設計する前に決める）。
# 段階的介入設計規則

## このスキルの目的

GSE の核心的なバリュー「不便益に基づく介入」を正しく実装・保守する。
閾値・タイミング・解除条件の設計意図を把握し、意図せぬ変更を防ぐ。

## 適用範囲

### 適用するもの
- `src/components/Overlay.tsx`（Nudge / Wall UI）
- `src-tauri/src/wall_server.rs`（Wall HTTP サーバー + Zen Timer）
- `src/App.tsx` の介入状態管理

### 適用しないもの
- `analysis/engine.rs`（p_stuck の計算ロジック → hmm-analysis Skill を参照）

---

## 介入レベル一覧

| レベル | 名称 | トリガー条件 | 解除条件 | 担当 |
|---|---|---|---|---|
| Lv1 | **Nudge** | p_stuck > 0.60 | p_stuck ≤ 0.60 で自動消失 | Frontend |
| Lv2 | **Wall** | p_stuck > 0.70 が累積 30 秒 | POST /unlock または長時間アイドル | Frontend + Rust |
| — | **Monk Mode** | ユーザーが手動トグル | 同上 | Frontend |

---

## 主要なルール

### ルール 1: Nudge は Frontend 完結（p_stuck > 0.60）

Rust への通知は不要。500ms ポーリングで取得した `p_stuck` を直接判定。

```typescript
// ✅ 正しい実装（Overlay.tsx）
const showNudge = cogState.p_stuck > 0.60 && !monkMode;

// ❌ 誤り: Nudge のために Tauri コマンドを追加しない
await invoke("trigger_nudge");  // 不要
```

---

### ルール 2: Wall は累積時間追跡で起動（30 秒）

`stuckAccumMsRef` で累積し、30,000ms 到達で `start_wall_server` を invoke。
p_stuck が 0.70 を下回ったらリセット。

```typescript
// ✅ 正しい累積ロジック（App.tsx / Overlay.tsx）
if (cogState.p_stuck > 0.70) {
  stuckAccumMsRef.current += deltaMs;
  if (stuckAccumMsRef.current >= 30_000 && !wallActive) {
    await startWall();
  }
} else {
  stuckAccumMsRef.current = 0;  // リセット
}
```

---

### ルール 3: Wall Server の graceful degradation

`start_wall_server` が失敗してもアプリはクラッシュしない。
Wall なしで継続（Nudge のみ有効）。

```typescript
// ✅ 正しいエラーハンドリング
try {
  const info = await invoke<WallServerInfo>("start_wall_server");
  setWallInfo(info);
  setWallActive(true);
} catch (e) {
  console.error("wall server failed:", e);
  // Wall なしで継続。Nudge は引き続き表示
}
```

---

### ルール 4: Zen Timer は 2 分 (120 秒)

スマートフォン側の Zen Timer は 120 秒固定。
この値を変更する場合は `wall_server.rs` の HTML 生成部分を修正。

```rust
// wall_server.rs 内の Zen Timer HTML
const ZEN_TIMER_SECONDS: u32 = 120;  // 2分: 変更時はここを修正
```

---

### ルール 5: Monk Mode は Wall を無効化するだけ

Monk Mode = true のとき、Wall 起動をスキップする。
Nudge は引き続き表示される（Monk Mode は Nudge を無効化しない）。

```typescript
// ✅ 正しい Monk Mode の適用
if (stuckAccumMsRef.current >= 30_000 && !wallActive && !monkMode) {
  await startWall();
}
// Nudge はそのまま表示
const showNudge = cogState.p_stuck > 0.60;  // monkMode の影響なし
```

---

### ルール 6: 解除エンドポイントは POST /unlock のみ

Wall の解除は必ずスマートフォンからの `POST /unlock` 経由。
セキュリティのためランダムトークンで認証。

```rust
// wall_server.rs
if request.method() == "POST" && request.url().starts_with("/unlock") {
    // トークン検証
    if token_valid(&request) {
        unlock_tx.send(()).ok();  // Tauri イベントで Frontend に通知
    }
}
```

---

### ルール 7: Early Unlock ボタン

緊急時用。表示条件は Wall 起動後（wallActive = true）のとき常時表示。
Early Unlock はトークン認証不要（ユーザーの PC 上の操作のため）。

---

## チェックリスト

- [ ] Nudge トリガーが p_stuck > 0.60 になっているか
- [ ] Wall トリガーが p_stuck > 0.70 かつ累積 30 秒になっているか
- [ ] Wall Server 失敗時に graceful degradation しているか
- [ ] Zen Timer が 120 秒になっているか
- [ ] Monk Mode が Wall のみを無効化し、Nudge は表示しているか
- [ ] POST /unlock にトークン認証があるか

---

## 補足資料

- `state-machine.md` — 介入状態遷移図

## 関連する他の Skill

- `hmm-analysis` — p_stuck の計算ロジック
- `typescript-standards` — Tauri IPC パターン・ポーリング実装
- `data-privacy` — Wall Server のセキュリティ要件
