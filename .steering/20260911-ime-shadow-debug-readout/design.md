# 設計 — `ime_shadow` の生存読み出し（研究者専用）

> ★ ブランチ: `feat/ime-shadow-debug-readout`（⚠️ **PR #182 の上に積んである**）

## 1. 採用した方針

**既存の `debug_force_probe` / `force_nudge` と同じ二重ゲートに載せる。**

| 層 | ゲート | 効果 |
|---|---|---|
| backend | `ensure_debug_enabled()` = `GSE_DEBUG=1` | ⚠️ フラグ無しでは **`Err` を返す** |
| frontend | `debugView` = `VITE_GSE_DEBUG=1`（ビルド時） | ⚠️ 被験者バンドルに**描画コードごと入らない** |

## 2. ⚠️★★★ なぜ既存の診断パネルに足さないのか（★ 本設計の最重要点）

`src/components/Dashboard.tsx` の診断パネル（`get_diagnostics` の結果）は
**`debugView` で囲まれていない**。

- ★ フックが **20 秒以上**有効にならないときに出る**トラブルシュート用**で、**被験者にも出る**
- ⚠️ しかも `Object.entries(diagnostics).map(...)` で **全フィールドをそのまま吐く**

→ ⚠️★★★ **`DiagnosticInfo` に件数を足した瞬間、被験者が自分の「放棄回数」を見る。**
★ 較正は**完全ブラインド**が前提なので、これは設計違反である。

→ ★ **別コマンド・別 DTO・別ブロック**にした。
⚠️ この不変条件は型では表せないので、**ソースの実物を検査するテスト**で固定した（§5）。

## 3. 変更対象

| ファイル | 変更 |
|---|---|
| `src-tauri/src/input/hook.rs` | `IME_SHADOW_EMITTED` / `IME_SHADOW_ABANDONED`（⚠️ **プロセス内のみ**） |
| `src-tauri/src/lib.rs` | `tally_ime_shadow()` / `ImeShadowDebugDto` / `get_ime_shadow_debug` / handler 登録 / テスト 5 本 |
| `src/components/Dashboard.tsx` | `ImeShadowDebug` 型 / state 2 つ / **`debugView` で囲んだ**ブロック |
| `src/App.css` | `.debug-ime-shadow*` |

⚠️ **`schema_dto.rs` / `schema/current.json` は触らない** —— ★ **NDJSON の行は 1 行も増えない**。

## 4. ⚠️ カウンタの設計（★ 順序に意味がある）

```
tally_ime_shadow: abandoned を先に → emitted を後に
get_ime_shadow_debug: emitted を先に → abandoned を後に
```

★ この組み合わせなら、読み出しが 2 つの store の間に挟まっても
**`abandoned <= emitted` が保たれる**（⚠️ 逆順だと `abandoned > emitted` という
**あり得ない値**が見える）。★ ずれても「確定が 1 件多く見える」だけで符号は壊れない。

★ **`confirmed` は別カウンタを持たず `emitted - abandoned` で導出する**
（⚠️ 3 つ別々に増やすと、読み出しの瞬間に和が合わない）。

⚠️ カウンタは **NDJSON に載らない**。★ プロセス内なので**再起動で 0 に戻る**。

## 5. テスト戦略

| # | テスト | 何を守る |
|---|---|---|
| 1 | `tally_counts_confirmed_and_abandoned` | 確定を差で出せる |
| 2 | `abandoned_never_exceeds_emitted` | §4 の不変条件 |
| 3 | `the_debug_command_is_gated_on_the_backend` | ⚠️ backend ゲートの消失 |
| 4 | `the_participant_visible_diagnostics_do_not_carry_the_tally` | ⚠️★★★ **被験者への漏れ** |
| 5 | `the_readout_block_is_gated_on_the_frontend` | ⚠️ frontend ゲートの消失 |

★ 3〜5 は `capabilities.rs` と同じ様式で **`include_str!` によるソース検査**。
⚠️ 型では表せない「UI と backend にまたがる不変条件」なので、これが唯一の手段。

### ⚠️ テスト 5 が自分の粗を捕まえた（★ 記録する価値がある）

★ 初版は `find("get_ime_shadow_debug")` で**最初の出現**を探していたが、
⚠️ それは **interface の doc コメント**（ファイル冒頭・gate の外）に当たって**赤になった**。
→ ★ `invoke<ImeShadowDebug>("get_ime_shadow_debug")` という**呼び出しの実体**を狙うよう直した。
⚠️ **ソース文字列の検査は狙いを外すと簡単に嘘をつく**、という実例である。

## 6. ★ これで mac 実機確認がどう変わるか

| | 従来 | 本変更後 |
|---|---|---|
| 書き込み先の特定 | ⚠️ `ls -lt` で探す（★ **2 本できる**ので取り違えやすい） | ★ **画面に絶対パスが出る** |
| 確定 / 放棄の確認 | `jq` で NDJSON を開く | ★ **画面に件数と内訳が出る** |
| 0 件の意味 | ⚠️ 判別に手間 | ★ **「計器が動いていない」と画面が言う** |

⚠️ ただし **`dwell_ms` の妥当性**と**行数 vs 操作回数**（合算・打ち切りの検出）は
**引き続き jq が要る**。→ ★ 引き継ぎの jq 手順は**消さない**。

## 7. ロールバック

ブランチを破棄すれば親（PR #182）は無傷。⚠️ NDJSON も schema も触っていないので、
**データ面のロールバックは不要**。
