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

## 4. ⚠️★★★ カウンタの設計（★ 初版は誤っていた。訂正して記録する）

### 4.1 置き場所 —— **logger 側**（実際に書かれた行を数える）

⚠️ 初版は `lib.rs::emit_ime_shadow` の `try_send` 直後で数えていた。
→ ★ それは「**出そうとした回数**」であって「**書かれた行数**」ではない:

- ⚠️★★★ **被験者が「止める」を押した区間の変換も数えていた** ——
  一時停止ゲートは writer ループの中にあり `ime_shadow` は確実に捨てられるのに、
  カウンタには残る。★ **「止めた区間は痕跡を残さない」(ADR-014 判断 3) が破れる。**
- ⚠️ チャネル満杯で行が落ちてもカウンタだけ進む。

→ ★ **`writeln!` の直後で数える**。⚠️ **ローテートで 0 に戻す**
（★ 戻さないと `log_path` と件数が別のファイルを指し、
**本機能が消そうとした「2 本できて取り違える」問題を再生産する**）。

### 4.2 ⚠️★★★ **順序で守るのはやめた** —— 2 つの数を 1 語に詰める

★ **2 度破れた**ので、構造で守る形に変えた。

| 回 | 何が破れたか | 実測 |
|---|---|---|
| 1 | 書き手が `abandoned` を先に増やし、**共有状態が `abandoned = emitted + 1` を通っていた** | ⚠️ 5000 万回中 **1034 万回** |
| 2 | 増分順序を直しても、⚠️ **ローテートの `reset` が読み出しの 2 回の `load` に挟まる** | ⚠️ **44 万回**（★ **本番でも起きうる**） |

→ ★ **上位 32bit = 書いた数 / 下位 32bit = 放棄** を 1 つの `AtomicU64` に詰めた。

```rust
tally:  fetch_add(if abandon { (1<<32) | 1 } else { 1<<32 }, Relaxed)
reset:  store(0, Relaxed)
read:   let v = load(Relaxed); (v >> 32, v & 0xFFFF_FFFF)
```

★ **読み・書き・リセットがすべて単一の不可分操作**になり、
⚠️ **不変条件が構造的に破れなくなった**（★ 順序の推論そのものが不要）。

⚠️ 桁あふれは 1 ファイル **42 億行**（≒ 250 GB 超）が必要で、ローテートで 0 に戻るため到達しない。

★ `confirmed` は `emitted - abandoned` で導出する。

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

## 8. レビュー対応（2026-09-11・`code-reviewer` + `security-checker` 並列）

★ security は **CRITICAL / HIGH ともに 0 件**。★ 二重ゲートは**実ビルドの grep で検証**された
（被験者バンドルに `get_ime_shadow_debug` / `log_path` / 「放棄」が **0 件**、
`VITE_GSE_DEBUG=1` ビルドでは出現 → **dead-code elimination が実在する**）。

| 優先 | 指摘 | 対応 |
|---|---|---|
| **HIGH-1** | ⚠️★★★ **カウンタ順序の不変条件が成立しない**（5000 万回中 1034 万回の違反を実測） | ✅ ★ 順序を反転。**壊した実装で赤くなること**を実測して確認（§4.2） |
| **HIGH-2** | ⚠️★★★ `log_path` はローテート追随・カウンタはしない → **読み出しが嘘をつく**（★ 本機能が消そうとした問題の再生産） | ✅ ローテートで **0 に戻す**。UI にも「(このファイルの行数)」と明記 |
| **SEC-M1** | ⚠️★★★ **止めた / 消した区間の変換も数える**（ADR-014 判断 3 に反する） | ✅ ★ カウンタを **logger の `writeln!` 直後**へ移した（一時停止ゲートの内側） |
| MED | テスト `the_debug_command_is_gated_on_the_backend` が **fail-open 2 経路**（コメントアウトを弾けない / 自分のアサーション文字列に当たって自分を通す） | ✅ **最初の文**の一致を見る + `expect` で fail-closed。★ コメントアウトで赤くなることを実測 |
| MED | `abandoned_never_exceeds_emitted` が**並行性を検証していない**（★ だから HIGH-1 を取り逃がした） | ✅ **書き手スレッドを立てて 200 万回読む**テストに置換 |
| MED | 診断漏れ検査の**既知の限界**が未記載 | ✅ doc に明記（ヘルパ経由は素通り / 対象は `get_diagnostics` 1 関数のみ） |
| LOW ×5 | 未使用 `Clone` / CSS は DCE されない / `String(e)` / `GSE_DEBUG` 一覧の未追記 / 空テンプレのコミット | ✅ 全件対応 |

### ⚠️★★★ この 2 件から学ぶこと

1. **「順序で不変条件が保てる」と書いたら、壊した実装で赤くなるまで信じない。**
   ★ 初版のテストは単一スレッドで `n <= n+1` を見るだけ＝**自明に真**で、欠陥を隠した。
2. **計器は「出そうとした回数」ではなく「実際に残った行」を数える。**
   ★ そうでないと、⚠️ **被験者が消したはずのものが研究者の画面に残る**。
