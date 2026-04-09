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
    ├──► analysis::features  (計算層)
    ├──► analysis::engine    (推論層)
    ├──► logger         (永続化層)
    └──► wall_server    (介入サーバー層)
```

**禁止**: モジュール間の直接依存（例: `wall_server` が `analysis::engine` を直接呼ぶ）

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

UIPI（User Interface Privilege Isolation）によりブロックされる。
IME 検出は `SetWindowsHookEx + WinEvent + ImmGetOpenStatus` を使う。

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
