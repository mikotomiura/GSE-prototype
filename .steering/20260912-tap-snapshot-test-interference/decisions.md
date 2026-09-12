# decisions — lib テストの `TAP_ENABLED_SNAPSHOT` 取り合い

## 決定 1: ⚠️★★★ **推測で起票せず、先に再現させた**

**決定**: ★ レビュー (code-reviewer MEDIUM) の指摘を**鵜呑みにせず、自分で再現条件を測った**。

**実測**: ★ 2 テストだけを `--test-threads=8` で **40 回**:

```
test input::liveness::tests::hook_reports_enabled_is_none_without_a_hook ... FAILED
assertion `left == right` failed
  left: Some(false)
 right: None
→ 失敗 7 / 40
```

**理由**: ⚠️ 「理屈上は起きうる」で直すと、★ **直ったかどうかを測る基準が無い**。
→ ★ 修正前の数字 (**7/40**) があって初めて、修正後の **0/40** が意味を持つ。
⚠️ これは `silent-failure-in-guard-scripts` の教訓
(★ **レビュアーの言う再現条件を鵜呑みにせず閾値を自分で測る**) と同じ作法である。

⚠️ **なお `cargo test --workspace` を 10 回回しても 1 回も出なかった** ——
★ 661 件の中に薄まると当たらない。→ ⚠️ **「フルで緑だから無い」は誤り。**

---

## 決定 2: ★ 依存を足さず、テスト専用の共有 `Mutex` で直列化する

**決定**: `hook.rs` に `#[cfg(test)] pub(crate) static TAP_SNAPSHOT_TEST_LOCK` を置き、
**書く側 (`hook_macos.rs`) と読む側 (`liveness.rs`) の両方**が取る。

**却下案**:

| 案 | ⚠️ 却下理由 |
|---|---|
| `serial_test` crate | ★ テスト 2 本のために**依存を増やす** (⚠️ 未導入だった) |
| `--test-threads=1` | ⚠️ **他の 659 件の並列性まで殺す** (★ CI 時間に直撃) |
| `#[ignore]` | ⚠️★★★ **検査を消すのと同じ**。★ 本 repo の方針 (緑で誤魔化さない) に真っ向から反する |
| `tap_is_enabled` を引数受け取りの純関数に割る | ★ 筋は良いが、⚠️ **公開 API の形が変わる**ので影響範囲が広い → 別途 |

**★ 置き場所の判断**: ⚠️ `hook.rs` の `mod hook_macos;` は**私有**なので、
`liveness.rs` から `hook_macos` 内の static には届かない。
→ ★ **門は OS 非依存の `hook.rs` に置く** (⚠️ 守る対象は macOS 固有だが、
**取る側が両方から見える**必要がある)。

**★ `#[cfg]` で OS 分岐させなかった理由**: ⚠️ Windows では `hook_reports_enabled()` が
常に `None` を返すので競合しないが、★ **分岐を増やすほどの理由が無い** (害もない)。

**⚠️ poison は握りつぶす** (`unwrap_or_else(|p| p.into_inner())`):
★ 片方が panic したときに他方まで落ちると**二重報告**になり、原因が読みにくくなる。
(★ `lib.rs` の log ロックと同じ作法)。

---

## 決定 3: ★ 「直った」の基準を**修正前と同じ手順・同じ回数**に置いた

| | 失敗回数 |
|---|---|
| ⚠️ 修正前 | **7 / 40** |
| ✅ 修正後 | **0 / 40** |

⚠️ **緑 1 回では足りない** —— ★ 元が間欠なので、同じ条件で同じ回数回さないと比較にならない。

★ **空振り検査も入れた**: ⚠️ `cargo test <filter>` は **0 件マッチでも成功する**ので、
**両テストが実際に走ったこと**を出力で確認した
(`2 passed; 0 failed; ... 659 filtered out`)。
(★ `silent-failure-in-guard-scripts` の「`cargo test --lib <filter>` の 0 件マッチ」型。)

---

## 決定 4: ★ 契約を弱めていないことを確認した

- ⚠️ `tap_is_enabled_reads_snapshot_not_the_port` の **3 状態検査** (正常 / 不在 / 壊れ) は**そのまま**。
- ⚠️ `hook_reports_enabled_is_none_without_a_hook` の「`Some(true)` と偽らない」契約も**そのまま**。
- ★ 足したのは **guard の取得 2 行**だけで、assert は 1 つも削っていない。

## 検証

| 検査 | 結果 |
|---|---|
| 再現手順 40 回 × `--test-threads=8` | ✅ **0 / 40** (⚠️ 修正前 7 / 40) |
| 両テストが実際に走ったか | ✅ `2 passed; 0 failed` |
| `cargo fmt --check` | ✅ EXIT=0 |
| `cargo clippy --all-targets -- -D warnings` | ✅ EXIT=0 |
| `cargo clippy --all-targets --features package -- -D warnings` | ✅ EXIT=0 |
| `cargo test --features package --workspace` | ✅ **705 passed / 0 failed** |
| ゴールデン | ✅ `OK: 15 snapshots match` |
| schema | ✅ byte-equal |
| `analysis/` 差分 | ✅ 無し (⚠️ `HMM_VERSION` 据え置き) |
