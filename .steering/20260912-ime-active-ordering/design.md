# 設計: `IME_ACTIVE` の Ordering を対に閉じる

## アプローチ

⚠️★★★ **片側だけ直さない。** ★ mac が 判断 5b で一度踏んで撤回した罠 ——
**store だけ `Release` にしても読み手が `Relaxed` なら happens-before は成立しない**。
→ ★ 「規則に合わせた」という**記録だけが残る silent no-op** になる。

## 変更内容 (7 箇所)

| # | 箇所 | before | after |
|---|---|---|---|
| 1 | `input/hook.rs` `is_ime_active()` | `load(Relaxed)` | `load(Acquire)` |
| 2 | `input/hook_windows.rs` IME_SHOW/CHANGE | `store(true, Relaxed)` | `store(true, Release)` |
| 3 | `input/hook_windows.rs` IME_HIDE | `store(false, Relaxed)` | `store(false, Release)` |
| 4 | `input/hook_windows.rs` フックコールバック内 | `load(Relaxed)` | `load(Acquire)` |
| 5 | `input/ime_windows.rs` | `store(false, Relaxed)` | `store(false, Release)` |
| 6 | `input/ime_windows.rs` | `load(Relaxed)` | `load(Acquire)` |
| 7 | `lib.rs` | `store(false, Relaxed)` | `store(false, Release)` |

### ⚠️ #4 は**フックコールバック内**だが、共通-1 に反しない

★ 共通-1 の禁止リストは **Mutex / ブロッキング send / I/O / ヒープ確保 / ログ / sleep** であり、
**atomic load は入っていない** (⚠️ むしろ共通-1 は「Atomic 操作 + channel send **のみ**」と定める)。
★ `Acquire` load は x86-64 では `Relaxed` と**同一命令** (フェンスを生まない) なので、
⚠️ コールバックのレイテンシ要件にも影響しない。

## ★ 再発防止 (⚠️ mac は実測しただけで仕掛けが無かった)

`input/hook.rs` に `ordering_invariant_tests::guarded_atomics_never_use_weak_ordering` を追加。

- ★ **`capabilities.rs` と同じ様式**で `include_str!` により**ソースの実物**を走査する。
  ⚠️ 規則は「どの変数か」に依存する (`LAST_KEY_MS` は `Relaxed` で**正しい**) ので、
  **`AtomicBool` の型では表せない**。
- ⚠️★★★ **`#[cfg]` を付けない。** ★ 文字列として読むので `hook_windows.rs` が
  1 行もコンパイルされない macOS でも**中身を検査できる**。
  ⚠️ `#[cfg]` を付けると**相手側 OS の CI が素通り**し、今回の「片 OS でしか見ていない」状態に戻る。
- ★ 針は `concat!` で割る —— ⚠️ **本ファイル自身も走査対象**なので、
  割らないと**テストのリテラルが自分に引っかかる**。
- ★ **コメント行は除外** (⚠️ 規則を説明する文章が引っかかるため)。
  → ⚠️ 「落ちすぎない」方向の限界であり、**実コードの見落としは生まない**。

## テスト戦略

⚠️★★★ **「足したら緑だった」は検査が効いている証拠にならない。**
→ ★ **変異させて赤になることを実測する**。

★ 実測済み (2026-09-12): `hook_windows.rs:603` の `Acquire` を `Relaxed` に戻すと

```
hook-constraints 共通-2 違反: 保護対象の static に弱い Ordering が使われている。
input/hook_windows.rs:603 | if is_press && IME_ACTIVE.load(Ordering::Relaxed) {
test result: FAILED. 0 passed; 1 failed
```

★ **行番号と該当行を名指しで返す**ことまで確認し、復元後は緑。

## ⚠️ 振る舞いへの影響

★ `Release` / `Acquire` は `Relaxed` より**強い**制約であり、**緩めていない**。
→ ⚠️ 可視性が保証されるようになるだけで、観測される値の系列が変わることはない。
★ ゴールデン 6 fixture / 226 snapshot は byte-equal のまま (★ replay は単一スレッド)。
⚠️ したがって `HMM_VERSION` は bump しない。
