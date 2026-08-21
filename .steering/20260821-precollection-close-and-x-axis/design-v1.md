# 設計 v1 (初回案) — 案 A: `compare_exchange` で終了権をアトミックに取る

> ⚠️ **これは退避された初回案である。** 採否は `design-comparison.md` を見よ。

## 実装アプローチ

引き継ぎメモが先頭に挙げた案 A をそのまま採る。

`SESSION_START_MS` を **ブロックの同一性を表すトークン**とみなし、自動終了スレッドは
`compare_exchange(observed_start, 0)` で **終了権をアトミックに奪う**。
失敗したら「その間に新しいブロックが始まっていた」ので**中止**する。
加えて、アイドル待ちの直後に `SESSION_START_MS == 0` を**再確認**してから `BlockEnd` を送る。

```rust
// 自動終了スレッド
let start = SESSION_START_MS.load(Acquire);
if start == 0 { continue }
if now - start < BLOCK_DURATION_MS { continue }

// ★ 終了権をアトミックに取る。失敗 = 新しいブロックが始まっていた → 中止。
if SESSION_START_MS
    .compare_exchange(start, 0, AcqRel, Acquire)
    .is_err()
{
    continue;
}
block_session_active.store(false, Release);

// アイドル待ち (最大 1500 ms)
while !ANALYSIS_IDLE.load(Acquire) { ... }

// ★ 待っている間に押されていないか再確認
if SESSION_START_MS.load(Acquire) != 0 { continue }

send(BlockEnd)
```

## 変更対象

### 修正するファイル
- `src-tauri/src/lib.rs` — 自動終了スレッドの 1)〜3) を上記に差し替える
- `src-tauri/src/g1.rs` — 判定を純関数 `decide_block_end` に切り出す
- `src-tauri/src/input/liveness.rs` — 所見 C の 1 行 (`starved_ms_carried_into_new_window`)

## 既存パターンとの整合性

- ★ ロックを増やさない。既存の `intervention` → `log` のロック順序に**一切触れない**
  ので、順序反転の危険がゼロである。
- ★ `SESSION_START_MS` は既に「ブロック中か」を表すフラグとして複数箇所で読まれており
  (`lib.rs:2388` ほか)、それを**同一性トークンに格上げする**のは自然な拡張である。

## テスト戦略

- `g1::decide_block_end` の純関数テスト (両 OS 共通)
- ⚠️ 交錯の 2 方向は **CAS の戻り値**でしか表現できないため、
  「押下が後」のケースは**純関数では表現できない** (下記の残課題)。

## ⚠️★★★ 残課題 (v1 が閉じきれていないところ)

**「押下が後」の交錯が閉じない。**

`start_session` は `Rotate` / `SessionStart` を **ログのロックの中**で送り、
`SESSION_START_MS.store(now)` は**ロックを抜けた後**で行う (`lib.rs:2193`)。
→ ★ **「`Rotate` は送られたが `SESSION_START_MS` はまだ 0」という窓が実在する。**

したがって、アイドル待ちの直後に `SESSION_START_MS == 0` を確認しても
**その窓の中では 0 のまま通過し**、`BlockEnd` が**新しいファイル**へ `session_end` を書く。

⚠️ 本当に守りたい不変条件は
「**`BlockEnd` は次のブロックの `Rotate` より前にログ channel へ入る**」
であって、`SESSION_START_MS` の値ではない。
→ ★ **原子変数の比較では表現できない** (2 つの操作の順序を要求しているため)。

## ロールバック計画

`git revert` で足りる (状態を持たない変更のため)。
