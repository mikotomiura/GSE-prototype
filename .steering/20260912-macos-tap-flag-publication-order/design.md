# design — 公開フラグの公開順

## 不変条件 (★ 本 PR で明文化する)

> ⚠️★★★ **公開フラグは payload の後に立て、payload より先に下ろす。**

★ 理由: release/acquire の happens-before は「**フラグを書く前に書いたもの**」だけを運ぶ。
⚠️ フラグを先に立てると、フラグを `Acquire` で見た側が payload の**初期値**を読みうる。

| | 旧 (⚠️ 壊れている) | 新 |
|---|---|---|
| **設置** | `HOOK_ACTIVE=true` → snapshot → port | snapshot → port → **`HOOK_ACTIVE=true`** |
| **退出** | `HOOK_ACTIVE=false` → port=null → snapshot=-1 | **`HOOK_ACTIVE=false`** → port=null → snapshot=-1 |

★ **退出側は元から正しい** (⚠️ 下ろすのは先で良い) —— ただし `Ordering` が `Relaxed` なので
`Release` に揃える (★ 観測側は `Acquire` で読んでおり、対になっていない)。

## 変更対象

- `src-tauri/src/input/hook_macos.rs` — 設置時の `HOOK_ACTIVE.store(true)` の位置、
  退出時の `Ordering`
- `src-tauri/tests/macos_hook_rehook.rs` — 失敗時の切り分け情報

## ⚠️ テスト戦略 (★ ここが本 PR の肝)

⚠️★★★ **「緑になった」では直ったと言えない。** ★ 元から間欠 (手元 6/6 緑・CI で 2/2 赤) なので、
**修正後に緑でも、たまたま当たらなかっただけかもしれない。**

→ ★ 採る手は 2 つ:

1. **切り分け情報を出す** —— ⚠️ 次に赤くなったとき、(a) 公開順 と (b) tap の実失効 を
   **ログで区別できる**ようにする。★ `HOOK_ACTIVE` が **true のまま** snapshot が `-1` なら (a)、
   **false に落ちている**なら (b)。
2. **連続実行** —— ★ `macos_hook_rehook` を 10 回連続で回す
   (⚠️ これは「直った証明」ではなく「悪化していない証拠」)。

⚠️ **`HOOK_ACTIVE` を直接 assert する陽性対照は書けない** —— ★ 公開順の穴は
**µs オーダーの窓**であり、テストから再現的に踏ませる手段が無い
(⚠️ 「再現テストを書けませんでした」と正直に書く。★ 書けたふりをしない)。
→ ★ 代わりに **不変条件をコメントで明文し、切り分け情報を残す**ことで次回に備える。
