---
name: architecture-rules
description: >
  GSE のモジュール依存方向・レイヤー分離・禁止パターン。新しいファイルを追加する・
  既存モジュールを変更する・リファクタリングするときに必須参照。以下の状況で必須参照:
  - src-tauri/src/ に新しい *.rs ファイルを追加するとき
  - analysis/ モジュールに Windows API を追加しようとしているとき
  - input/ と analysis/ の責務境界が不明なとき
  - lib.rs に新しい Tauri コマンドを追加するとき
  - src/ (Frontend) に状態推定ロジックを置こうとしているとき
  - mod.rs の pub mod を更新するとき
allowed-tools: Read, Grep, Glob, Edit
---

# アーキテクチャ規則

## このスキルの目的

GSE のレイヤー構造を維持し、OS 固有コードの漏れ・循環参照・責務の混在を防ぐ。

## 適用範囲

### 適用するもの
- `src-tauri/src/` 配下のすべての Rust ファイル
- `src/` (Frontend) の責務判断

### 適用しないもの
- `docs/` の文書構成（別途 repository-structure.md を参照）

---

## 主要なルール

### ルール 1: モジュール依存方向（一方向のみ）

```
Frontend (src/)
    │  Tauri IPC のみ
    ▼
lib.rs  ←─── 各モジュールを統合・Tauri コマンド定義
    │
    ├──► input::hook    (OS キャプチャ層)
    ├──► input::ime     (IME 検出層)
    ├──► analysis::features       (計算層)
    ├──► analysis::engine         (推論層)
    ├──► analysis::intervention   (介入判定層。★ 純粋関数)
    ├──► logger                   (永続化層)
    └──► overlay_panel            (Nudge の表示。★ OS 依存)
```

⚠️★★★ **`wall_server` は存在しない。**★ **2026-08-23 に Lv2 Wall ごと削除された**（**ADR-015**）。
★ 実測（2026-09-07）: `src-tauri/src/wall_server.rs` は**不在**で、コード参照も 0 件。
→ 通常モードの介入だった Nudge は ADR-040 D1 で既定を無効にした（本体では出さない）。介入サーバー層という段は無い（2026-11-03 更新: PC 側の身体回帰の招待は EH3 モードで実装済み・`analysis/invitation.rs`。2026-11-01 から通常のモードの第 2 週でも動く。散歩の促進とその計測は行わず、身体回帰の後は離席候補明けの作業上の状態（打鍵の再開と受領の有無・フォーカスの遷移・ポインタ）で見る〔2026-11-03 研究者の言・ADR-024・ADR-023 D4・ADR-016〕）。

**禁止**: モジュール間の直接依存（例: `logger` が `analysis::engine` を直接呼ぶ）。
★ ただし **`analysis/` 内のサブモジュール間の参照は可**である
（★ 実例: `analysis::metrics` が `analysis::loop_step::FeatSnapshot` と
`analysis::intervention::AWAY_IDLE_MS` を import している）。

---

### ルール 2: `analysis/` に Windows API を置いてはならない

`analysis/` は純粋な計算ロジック。OS API は `input/` に閉じ込める。

```rust
// ❌ 禁止（analysis/engine.rs 内）
use windows::Win32::UI::Input::KeyboardAndMouse::GetAsyncKeyState;

// ✅ 正しい設計
// input/hook.rs → InputEvent を生成して crossbeam channel で送信
// analysis/features.rs → InputEvent を受け取って計算するだけ
```

---

### ルール 3: `src/` (Frontend) にビジネスロジックを置いてはならない

状態推定・閾値判定・HMM 計算はすべて Rust 側で完結させる。

```typescript
// ❌ 禁止（src/ 内）
const isStuck = features[2] > 0.5 && flightTime < 100;

// ✅ 正しい設計
const { p_stuck } = await invoke<CognitiveState>("get_cognitive_state");
// Rust 側が判定済みの確率値のみを受け取る
```

---

### ルール 4: 新規ファイル追加時の手順

1. **レイヤー判定**: `input/`（OS 依存）か `analysis/`（計算）か、それ以外か？
2. **ディレクトリ選択**: 既存モジュールへの追加 or 新モジュール（lib.rs で mod 宣言）
3. **命名**: snake_case.rs
4. **mod.rs 更新**: `pub mod new_module;` を追加
5. **docs 更新**: アーキテクチャに影響する変更は `docs/architecture.md` を更新

---

### ルール 5: グローバル TSF フック（ITfThreadMgr）は使わない

⚠️★★★ **2026-08-22 に *理由* を訂正した**（★ **結論は変わらない**。SSOT は
`docs/agent-shared.md` 技術的制約 7）。

⚠️ **旧文「UIPI によりブロックされる」は誤りである。**
★ **UIPI の禁止 5 項目**（window handle validation / `SendMessage`・`PostMessage` /
thread hooks / journal hooks / **DLL injection**）に **TSF も COM も含まれていない**。
★ かつ UIPI は「**同一の整合性レベルでは一切干渉しない**」ので、通常環境では**発動すらしない**。

★ **真の障壁はアーキテクチャである** —— `ITfThreadMgr::Activate` は逐語
「**Activates TSF for the calling thread**」であり、`ITfSource::AdviseSink` に
**リモート対象を指定する引数が構文上存在しない**。
⚠️ **権限を上げても・UIAccess を付けても・管理者で実行しても取得できない**（そういう API が無い）。

⚠️ **別途禁止**: **DLL 注入を伴うグローバルフック**（`WH_GETMESSAGE` / `WH_CALLWNDPROC`）で
`WM_IME_*` を拾うこと。★ **こちらは UIPI 第 5 項（DLL injection）に直撃する。**

★ **採る手段**: IME 検出は `SetWindowsHookEx + WinEvent + ImmGetOpenStatus`。
★ プロセス跨ぎの観測は **WinEvent (`WINEVENT_OUTOFCONTEXT`)** —— DLL 注入不要で、
★ **コールバック引数に文字列が 1 つも無く content-free が構造的に保証される**。

---

### ルール 6: 循環参照禁止

`input` → `analysis` の依存は禁止（`analysis` が `input` を参照してはならない）。
データは crossbeam channel 経由で一方向に流れる。

---

## チェックリスト

- [ ] `analysis/` 内に Windows API のインポートがないか
- [ ] モジュール間の直接依存がないか（lib.rs 経由のみ）
- [ ] 新ファイル追加時に mod.rs を更新したか
- [ ] Frontend に閾値計算・状態推定ロジックが混入していないか
- [ ] ITfThreadMgr / グローバル TSF フックを使っていないか
- [ ] 循環参照が生じていないか

---

## 補足資料

- `decision-tree.md` — 「このコードはどこに置くべきか」判断フロー

## 関連する他の Skill

- `rust-standards` — Rust 固有の実装規則
- `hook-constraints` — input/ 層のコールバック制約
- `typescript-standards` — Frontend 層の責務制限
