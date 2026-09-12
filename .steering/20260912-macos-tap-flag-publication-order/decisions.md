# decisions — macOS 公開フラグの公開順

## 決定 1: ★ 不変条件を立てた —— **公開フラグは payload の後に立て、payload より先に下ろす**

**決定**: `hook_macos.rs` の `HOOK_ACTIVE` を、設置時は payload の**後**へ移し、
下ろす 3 経路はすべて payload クリアの**前**に保ったまま `Ordering` を `Release` に揃えた。

| | 旧 (⚠️ 壊れていた) | 新 |
|---|---|---|
| 設置 (`:937`→`:972`) | `HOOK_ACTIVE=true` → snapshot → port | snapshot → port → **`HOOK_ACTIVE=true`** |
| 退出 (`:1017`) | `HOOK_ACTIVE=false` (**Relaxed**) → port=null → snapshot=-1 | 同順・**Release** |
| 防衛 (`:883`) | `HOOK_ACTIVE=false` (**Relaxed**) → port=null → snapshot=-1 | 同順・**Release** |

**理由**: ★ release/acquire の happens-before は「**フラグを書く前に書いたもの**」しか運ばない。
⚠️ フラグを先に立てると、フラグを `Acquire` で見た側が payload の**初期値** (`-1`) を読みうる。
★ `tests/macos_hook_rehook.rs:59` は実際に `HOOK_ACTIVE` を `Acquire` で待ってから
`hook_reports_enabled()` を読んでおり、**この経路が CI を赤くした**。

★ `Relaxed` → `Release` は `hook-constraints` Skill の**共通-2** (観測側が `Acquire` なら store は `Release`) に従った。
⚠️ 旧コードは**対になっていなかった**。

**却下案**:
- ★ テストの `wait_for_hook` の後に `sleep` を入れて誤魔化す → ⚠️ **却下**。
  症状を隠すだけで、**本番の観測側 (`lib.rs` / `tray.rs`) の穴は残る**。
- ★ `tap_is_enabled()` を「`HOOK_ACTIVE` が true なら `Some(true)`」に変える → ⚠️ **却下**。
  `-1` は「不明」を表す設計で、⚠️ **嘘を返さない**という既存の意思決定
  (`tap_is_enabled` の doc・`tap_is_enabled_reads_snapshot_not_the_port` テスト) に反する。

---

## 決定 2: ⚠️★★★ **「緑になった」を「直った」と言わない**

**決定**: ★ 本 PR は**再現テストを書けていない**。そのことを明記して出す。

**理由**: ⚠️ 公開順の穴は **µs オーダーの窓**であり、テストから再現的に踏ませる手段が無い。
★ 修正前も**手元では 6/6 緑**だったので、⚠️ **修正後に緑でも「たまたま当たらなかっただけ」と
区別が付かない。**

★ 実際に測ったこと (⚠️ これは「悪化していない証拠」であって「直った証明」ではない):

| 検査 | 結果 |
|---|---|
| `macos_hook_rehook` **連続 10 回** | ✅ **pass=10 / fail=0** |
| `cargo test --features package --workspace` | ✅ 11 スイート **705 件** passed / 0 failed |
| `cargo clippy --all-targets -- -D warnings` | ✅ EXIT=0 |
| `cargo clippy --all-targets --features package -- -D warnings` | ✅ EXIT=0 |
| `cargo fmt --check` | ✅ EXIT=0 |
| ゴールデン `gse-replay --snapshot` | ✅ `OK: 15 snapshots match` |
| `emit_schema` vs `schema/current.json` | ✅ byte-equal |
| `analysis/` の差分 | ✅ **無し** (⚠️ `HMM_VERSION` bump 不要) |

⚠️ **main の CI が 1 回緑になっても「直った」と報告しないこと。** ★ 間欠なので複数 run を見る。

---

## 決定 3: ★ 直せないものは**切り分けられるように**した (⚠️ 本 PR の主たる価値)

**決定**: `tap_diag()` を足し、`None` で落ちる 3 つの assert に**必ず**添えた。

```
[診断] HOOK_ACTIVE=true (★ true のまま None なら **公開順の穴 (a)**、
false なら **tap の実失効 (b)**) / watchdog_recoveries=0
(★ 増えていれば層 2 が復帰を試みた = (b) の裏づけ)
```

**理由**: ⚠️★★★ **`None` は 2 つの状態を区別できない** ——
(a) payload 未公開 / (b) tap が実際に死んだ (`:891` / `:1017` が `-1` を書く)。
★ 2026-09-12 に main が 2 本続けて赤くなったとき、⚠️ **ログにこの区別が無く、
コード読解で推定するしかなかった**。→ ★ 次は**ログだけで決着させる**。

⚠️ **だから本 PR は (a) を直したが、(b) の可能性を消していない。**
★ もし次に `HOOK_ACTIVE=false` 付きで赤くなれば、⚠️ **真因は (b) であり本 PR では足りない**
(= ランナー上で tap が短命という別問題)。★ その判定が**自動でできる**ようになった、というのが成果である。

**★ 陽性対照**: ⚠️ 「診断を書いたが出ない」が最悪なので、
**わざと assert を落として実際に出力されることを確認した** (EXIT=101 ＋ 上記文字列を確認・対照は完全復元)。

---

## 決定 4: ★ Windows 側 (`hook_windows.rs`) は触らない

**決定**: ⚠️ `hook_windows.rs` の `HOOK_ACTIVE` は **`Relaxed` のまま残した** (`:446` / `:484` / `:520`)。

**理由**: ★ Windows には `TAP_PORT` / `TAP_ENABLED_SNAPSHOT` に相当する **payload が無い**
(⚠️ `hook_reports_enabled()` は Windows で常に `None` —— 「有効か」を聞く API が無いため)。
→ ★ **守るべき happens-before が存在しない**ので、本 PR の不変条件は適用されない。
⚠️ **スコープを広げて Windows 実機で未検証の変更を入れない。**

**⚠️ 申し送り**: ★ `lib.rs:381` / `lib.rs:1117` / `tray.rs:91` は `HOOK_ACTIVE` を **`Relaxed`** で読んでいる。
⚠️ これらは**診断表示用**なので実害は薄いが、★ 本 PR の不変条件に乗るなら `Acquire` が正しい。
→ **別 PR の候補** (⚠️ 本 PR では変えない)。

---

## 決定 5: ★ ディスクを 3.3 GiB 空けた (⚠️ threshold を割っていた)

**決定**: `target/debug/incremental` と `target/aarch64-apple-darwin/debug/incremental` を削除した。

**実測**:

| | 空き |
|---|---|
| 掃除前 | ⚠️★★★ **14.1 GiB** (= CI の disk guard の **threshold 15 GiB を割っていた**) |
| 掃除後 | ✅ **17.5 GiB** |

★ `target` は 9.8 GiB → **6.5 GiB**。
⚠️★★ **開発クローンと self-hosted ランナーは同一ディスク** (`/dev/disk3s5`) なので、
★ **開発クローンの target がランナーの disk guard を発火させる**。
(★ ランナー側の target は 579 MiB と小さい)。

⚠️ `incremental` は**純粋なビルドキャッシュ**なので削除は安全 (★ 再ビルドで再生成される)。
