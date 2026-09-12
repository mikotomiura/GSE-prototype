# 設計

## 実装アプローチ

★ 3 段に分け、**コミットを分ける**。

1. **lint 修正** (振る舞い不変) — `fix(clippy)`
2. **`IME_OPEN` の Ordering 修正** (振る舞いを変える) — `fix(ime)`
3. **CI に clippy ゲートを足す** (R-1) — `ci`

⚠️★★★ 1 と 2 を分けるのは、**「lint は挙動を 1 ビットも変えない」という不変条件**を
後から diff で読めるまま残すため (引き継ぎ §7.2)。

### ★ lint に従わなかった 2 箇所 (§3 第 1 原則: help を鵜呑みにしない)

- `hook_macos.rs:100` `doc_list_item_without_indentation`
  → ⚠️ help は「字下げしろ」だが、当該文は**箇条書きの続きではなく独立した段落**。
    字下げすると意味が変わる。★ 空行 (`///`) を入れて段落を分けた。
- `hook_macos.rs:204` `unnecessary_cast`
  → ⚠️ FFI 境界 (GCD メインキュー) なので**一次資料で確かめてから**当てた:
    `#[link(name="System")] static _dispatch_main_q: c_void` と
    `dispatch_sync_f(queue: *const c_void, ..)` が一致しており、
    `as *const _ as *const c_void` の後段は真に no-op。
    ★ help の `as *const _` (推論) ではなく**型を明記**した。

## 変更対象

### 修正するファイル
- `src-tauri/src/lib.rs` — `was_active` の束縛に `#[cfg(target_os="windows")]` / `is_some_and` ×2
- `src-tauri/src/input/hook_macos.rs` — doc 段落 / 二重キャスト / `is_multiple_of`
- `src-tauri/src/input/ime_macos.rs` — `is_none_or` / `IME_OPEN.store` を Release
- `src-tauri/src/input/ime_windows.rs` — `IME_OPEN.store` を Release (★ mac と対)
- `.github/workflows/ci.yml` — `check` job に clippy step を追加 (R-1)

## 影響範囲

- ★ lint 修正は**振る舞い不変**。ゴールデン 226 snapshot が byte-equal であることで検証する。
- ⚠️ Ordering 修正は**メモリ順序を変える**が、緩める方向ではなく**強める**方向 (Relaxed→Release)
  なので、既存の Acquire 側 load と対になり規則どおりになる。
- ⚠️ CI step の追加は **main の CI を赤にしうる**ので、両 OS が緑であることを確かめてから足す。

## 既存パターンとの整合性

- `hook-constraints` 共通-2 (`IME_OPEN` の store は Release / load は Acquire)
- `.claude/hooks/stop-check.sh` の clippy と**同じ範囲** (`--all-targets` / `-D warnings`) を CI に置く

## テスト戦略

- 単体: `cargo test --workspace` (★ 659 passed から減らさない)
- 回帰: ゴールデン 6 fixture / 226 snapshot が byte-equal
  ⚠️★★★ **ずれたら `HMM_VERSION` を bump せず、修正が誤っている合図として扱う**
- drift: `emit_schema` が `schema/current.json` と byte-equal
- CI: PR を出して両 OS レグが緑になることを確認する (★ これが R-1 の受け入れ条件)

## ロールバック計画

- 3 コミットに分けてあるので、CI step (3) だけ revert すればゲートを外せる。
- lint 修正 (1) は振る舞い不変なので revert しても機能影響はない。
