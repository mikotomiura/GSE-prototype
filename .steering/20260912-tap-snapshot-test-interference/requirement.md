# requirement — lib テストがグローバル `TAP_ENABLED_SNAPSHOT` を取り合う間欠赤を塞ぐ

## 背景

★ 2026-09-12 の `09bc9b4` レビュー (code-reviewer MEDIUM) で**別 PR 候補**として起票された。
⚠️ **今回 main が赤くなった件とは無関係** (★ あちらは `tests/macos_hook_rehook.rs` = 別バイナリ)。

## ⚠️★★★ 再現させた (★ 推測ではない)

★ 2 テストだけを `--test-threads=8` で **40 回**回したところ、**7 回失敗**した:

```
test input::liveness::tests::hook_reports_enabled_is_none_without_a_hook ... FAILED
assertion `left == right` failed
  left: Some(false)
 right: None
```

## ★ 機序

| テスト | 場所 | 何をするか |
|---|---|---|
| `tap_is_enabled_reads_snapshot_not_the_port` | `hook_macos.rs:1481` | ⚠️ **グローバル `TAP_ENABLED_SNAPSHOT` を `-1`/`1`/`0`/異常値に書き換える** |
| `hook_reports_enabled_is_none_without_a_hook` | `liveness.rs:607` | ★ `hook_reports_enabled()` が **`None`** であることを assert |

⚠️ 両者は **同じ lib テストバイナリ**にあり、`cargo test` は既定で**並列**に走らせる。
→ ★ 後者が読む瞬間に前者が `1` / `0` を書いていると、**`Some(true)` / `Some(false)` が返って落ちる**。

⚠️ **これは「たまたま今まで当たらなかった」だけで、いつ CI を赤くしてもおかしくない。**

## ゴール (受け入れ条件)

1. ★ 上記 40 回 × `--test-threads=8` の再現手順で **失敗 0 回**。
2. ⚠️ **テストを弱めないこと** —— `tap_is_enabled_reads_snapshot_not_the_port` の
   3 状態検査 (正常 / 不在 / 壊れ) と `hook_reports_enabled_is_none_without_a_hook` の
   「`Some(true)` と偽らない」という契約を**どちらも削らない**。
3. ★ `cargo clippy --all-targets [--features package] -- -D warnings` が exit 0、
   `cargo test --features package --workspace` が緑。

## スコープ外

- ⚠️ **新しい依存を足さない** (★ `serial_test` は未導入。テスト 2 本のために crate を増やさない)。
- ⚠️ `#[ignore]` や `--test-threads=1` の強制で**逃げない** (★ 他のテストの並列性まで殺す)。
- ⚠️ `tests/macos_hook_rehook.rs` (別バイナリ) には触らない。
- ⚠️ `HMM_VERSION` は bump しない (★ `analysis/` に触らない)。

## 運用メモ

- /reimagine 適用: **No**
- 理由: 「共有グローバルを触るテストを直列化する」という定型で、設計上の分岐が無い。
