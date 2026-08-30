# 詰まりと解決 — O1 リリースと配布物の作り直し

## B-1. ⚠️★★★ 引き継ぎメモの D-4 の判定条件が**誤っている**

**メモの記述**（`next-session-prompt-o1-release-and-rebuild.md` §1-D-4）:

> ⚠️ `gse-app.log` に **`Probe scheduler thread started` が出ていない**こと

**実測**（v0.1.30 の配布物・O1 モードが確実に立っている状態）:

```
2026-08-30T05:36:59.067386Z  WARN gse_next_lib: O1 MODE ENABLED (source=marker): ...
2026-08-30T05:36:59.929353Z  INFO gse_next_lib: Probe scheduler thread started   ← ★ 出る
```

★ **O1 モードでも、このスレッドは必ず起動する。** → ⚠️ メモの条件は**永久に満たされない**。

### なぜそうなるのか（★ コードで確定）

`src-tauri/src/lib.rs:4418-4436`:

```rust
let disabled_by_g1 = g1_mode();
let probes_disabled = disabled_by_env || disabled_by_g1.is_some();   // ⚠️ O1 が入っていない
...
if !probes_disabled { thread::spawn(|| { tracing::info!("Probe scheduler thread started"); ... }) }
```

⚠️ ★ **プローブ抑止のゲートは `g1_mode()` しか見ていない。** O1 は明示的に止められていない。

### ではなぜ実害が出ないのか（★ 実測で確認）

スケジューラ本体は `SESSION_START_MS == 0` のあいだ `continue` するだけで、何も生まない。
そして `src/App.tsx:336` が逐語:

> ★ `start_session` も `record_session_meta` も **呼ばない** ——
> 記録は backend で既に走っており、宣言は被験者が任意のときに行う。

→ ★ O1 では `SESSION_START_MS` が 0 のままなので、**スケジュールが 1 件も作られない**。

**客観検証**（★ `lib.rs:4423` 自身が指定する方法 = NDJSON の `probe_assignment` 行数）:

| ファイル | `probe_assignment` | `probe_triggered` |
|---|---|---|
| `gse_o1_20260830_053659.ndjson` | **0** | **0** |
| `gse_o1_20260830_053726.ndjson` | **0** | **0** |

⚠️★ **私は最初これを 1 件と誤報告した。** `grep -c 'probe_assignment'` は
**行内の文字列**を数えるだけで、実体は `meta` 行（1 行目）の中の文字列だった。
→ ★ 型で数え直して 0 を確認した（memory `measurement-instrument-false-positives` と同型）。

### ⚠️★★ 残る潜在欠陥（★ 本セッションの発見・未修正）

★ O1 のプローブ抑止は **「たまたま `start_session` が呼ばれないから」成立している**。
⚠️ **設計としての門が無い。** G1 には明示ゲート (`disabled_by_g1`) があるのに O1 には無い。

→ ⚠️ 将来 O1 で `SESSION_START_MS` を立てる変更が入ると、
**被験者にランダムプローブが飛ぶ**（★ 同意文書に無い割り込み）。
★ しかも `lib.rs:4424` の「止まっているつもりを防ぐ番兵」warn も、O1 では**出ない**
（`probes_disabled` が false なので）。

**推奨**: `probes_disabled` に `crate::o1::is_o1()` を足し、O1 でも番兵 warn を出す。
⚠️ **本セッションでは直していない**（★ D の通し確認が主目的で、挙動を変えると
いま測っている配布物と実体がずれるため）。→ ★ 別 PR で。

### ★ 正しい判定条件（★ メモを直すならこれ）

- ❌ 「`Probe scheduler thread started` が出ていないこと」
- ✅ 「**NDJSON に `probe_assignment` 型の行が 0 であること**」（★ コードの指定と一致する）

---

## B-2. ⚠️ TCC 権限が新バイナリで再要求された（★ 未解決・研究者の操作が要る）

**メモの記述**: 「⚠️ TCC は前回**既に許可済み**だった（`input_monitoring=true accessibility=true`）」

**実測**: ⚠️ **新しいバイナリでは許可されていない。**

```
WARN ... Input Monitoring permission not granted. Opening System Settings ...
WARN ... Input Monitoring (ListenOnly) failed 3 times. Switching to Accessibility permission fallback ...
WARN ... CGEventTap creation still failing via Accessibility after 5 attempts.
ERROR ... keyboard hook may be dead: the system saw input but the hook was not called
          (keystrokes may NOT be recorded) starved_ms=30095
```

★ トレイは `HookDown (⚠ GSE — 計測できていません（研究者に連絡してください）)` を表示している
＝ **番兵は正しく働いている**（★ 黙って壊れていない）。

→ ⚠️ **`key` 行が出るかの確認 (D-4) は、許可を与えるまで実施できない。**

---

## B-2b. ✅ セッション NDJSON 2 本の消失は**研究者による手動削除**（★ 不具合ではない）

★ 通し確認の途中で `gse_o1_20260830_053659.ndjson` / `gse_o1_20260830_053726.ndjson` が
両方消えた。⚠️ ゴミ箱にも他の場所にも無く、削除に類するログ行も
`redaction_ledger.jsonl` も無かったため、**アプリ側の不具合の可能性**を疑って調査した。

→ ★ **研究者が Finder で手動削除したもの**と確認（2026-08-30・本人の回答）。
（★ アプリは終了時に `Opening session folder` でセッションフォルダを Finder に開く。）

⚠️★ **推測で「削除された」と書かずに本人に確認したのは正しかった** ——
もし不具合だったなら、これは「被験者のデータが黙って消える」最悪の欠陥であり、
★ リリース作業を止めてでも先に潰すべき事象だった。

★ 教訓として残す: **痕跡が無いこと自体は原因を決めない。**
「ゴミ箱に無い / ログに無い」は「アプリが消した」の証拠にも「人が消した」の証拠にもならない。

## B-3. ⚠️ Apps Script の `SHARED_SECRET` 未更新（★ §1-E をブロックしている）

送信側（`Form_O1/o1_submit.json`）はローテート済みだが、受信側は研究者の手作業が要る。
→ ★ 済むまで送信 timeout の実測 (§1-E) は実施できない。★ 詳細は `decisions.md` D-2。
