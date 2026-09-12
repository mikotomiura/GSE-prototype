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

---

## 決定 6: ⚠️★★★ **レビュー 3 系統で「原因の断定」が退けられた** (2026-09-12)

**決定**: ★ **「(a) が main の赤の原因である」という断定を取り下げる。**
正しくは **「(a) を塞いだ。(b) は未排除。見分ける計器を入れた」**。

**理由** (★ code-reviewer HIGH ＋ 私自身の検算が一致):

⚠️ 旧コードの (a) の窓は `HOOK_ACTIVE=true` と snapshot ストアの間の
**`CGEventTapIsEnabled` 1 回分**で、テストは **100 ms ポーリング**後に読む。
→ ★ 1 回の assert が窓に当たる確率は概算 **1e-5〜1e-4**。
⚠️ **main の 2 run が続けて同じ箇所で赤くなる説明としては弱い。**

★ ただし **(a) が非現実的というわけではない**: ⚠️ 窓の幅は命令コストではなく
**スレッドのプリエンプション**で決まる。★ 負荷のかかった CI ランナーで
2 つのストアの間に 10〜100 ms 開くことは十分ありうる。
→ ⚠️ **どちらとも断定できない、が正確な状態である。**

⚠️★★★ **私は commit 表題に「main の赤の原因」と書いた。これは行き過ぎだった。**

---

## 決定 7: ★ **この修正が守ったのは本番ではなくテストだった** (security-checker MEDIUM)

**決定**: ⚠️ コメントの「観測側は `Acquire` で読んでから payload を読む」を訂正した。

**実測** (★ 自分で grep して確認した):

| 読み手 | `Ordering` | payload を後読みするか |
|---|---|---|
| `lib.rs:381` / `:774` / `:1117` / `tray.rs:91` | **`Relaxed`** | ⚠️ **しない** (フラグ単独) |
| `tests/macos_hook_rehook.rs:59` | `Acquire` | ★ **する** |

→ ⚠️★★★ **本番に同じ穴は無かった。** ★ 直したのは**テスト側の観測順序**である。
⚠️ PR 本文で「本番にも同じ穴がある」と読める書き方をしたのは誤り。

★ **それでも不変条件を立てる価値はある**: ⚠️ **次に payload を後読みする読み手が現れたとき、
黙って壊れないため**である (★ この理由をコメントに明記した)。

★ `lib.rs` / `tray.rs` を `Relaxed` のまま残した判断は **code-reviewer LOW が追認**した
(⚠️ 後読みしないなら `Relaxed` で正しい。`Release` store ↔ `Relaxed` load は壊れてはいない)。

---

## 決定 8: ⚠️★★★ **下ろし側は Ordering では閉じられない** (★ 3 系統が一致)

**決定**: ★ コメントを「下ろす側は**窓を縮めるだけ**」に訂正し、
⚠️ **「対になっている」という記述を削除**した。

**理由** (Codex HIGH ＋ code-reviewer HIGH ＋ security LOW-1):

1. ⚠️ `Release` ストアは**後続**のストア (payload クリア) が他スレッドから先に観測されるのを
   **禁じない** (★ 片方向バリア)。
2. ⚠️ より根本的に、読み手の load は**古い `true` を返しうる**ので、
   「フラグを見る → payload を読む」の **check-then-act の窓は原理的に残る**。
3. ⚠️ `Acquire` で `true` を読んだ側は、この `false` ストアとは**同期しない** (Codex MEDIUM-1)。

→ ★ **`Relaxed` → `Release` は規約統一 (共通-2) であって、窓を閉じる効果は無い。**
★ 読み手は `None` を許容すること (`tap_is_enabled()` は**診断専用**)。

---

## 決定 9: ⚠️★★★ **計器が (b) を (a) と誤読させる欠陥があった** (code-reviewer MEDIUM)

**決定**: `tap_diag()` を廃し、**フラグ → payload → フラグ の二度読み** (`observe_tap()`) にした。

**何が問題だったか**: ⚠️ 初版は
`assert_eq!(hook_reports_enabled(), Some(true), "... {}", tap_diag())` で、
★ **payload を読んだ「後」に `HOOK_ACTIVE` を読んでいた**。
→ ⚠️ 遷移期 (run loop 退出 → 2 秒 → 再設置) に当たると、
**(b) で落ちたのに `HOOK_ACTIVE=true` を出して (a) と誤読させる**。
⚠️★★★ **診断の存在意義を計器自身が壊していた** (★ `measurement-instrument-false-positives` と同型)。

**★ Codex HIGH への回答でもある**: ⚠️ 複数 atomic の一貫した snapshot は原理的に取れないので、
**double-check** で「その間に遷移が無かった」ことを示す形にした。

---

## 決定 10: ⚠️ **陽性対照が私の実装バグを捕まえた** (★ 2 回目)

**決定**: ★ 判定ロジックの**全 4 枝**に期待値つきの対照を当て、到達性も検査した。

**何が起きたか**: ⚠️ 初版の `match` は `(_, false, _) | (false, _, _)` を先に置いたため、
★ **`before != after` (遷移中) が (b) に吸われて誤ラベル**されていた ——
⚠️ **doc には「一致しなければ判定不能と出す」と書いたのに、実装はそうなっていなかった。**
→ ★ 対照が `NG` を出して発覚し、`if before != after` で先に切る構造へ直した。
⚠️ ついでに **ガードアームは網羅性に数えられない**ためコンパイルエラーになり、
★ `match` を入れ子にして解決した (= コンパイラも捕まえた)。

★ 対照の結果: **4 枝すべて到達・8 ケース全件一致**。
★ 実物でも「わざと assert を落として」診断が出ることを確認した
(⚠️ 出力は `[判定] ★ payload は読めている` = **正しい枝**)。

---

## 決定 11: ★ 別 PR 送り (⚠️ 本 PR でやらない)

- ⚠️ **テスト間干渉** (code-reviewer MEDIUM): `hook_macos.rs` の
  `tap_is_enabled_reads_snapshot_not_the_port` がグローバル `TAP_ENABLED_SNAPSHOT` を
  書き換える一方、同じ lib テストバイナリで**並列**に走る
  `liveness.rs:604 hook_reports_enabled_is_none_without_a_hook` は `None` を assert している。
  → ★ タイミング次第で `left: Some(true)` の**間欠赤**になりうる。
  ⚠️ ただし**今回の赤は別バイナリ** (`tests/macos_hook_rehook.rs`) なので**無関係**。
  → ★ `serial_test` か共有 `Mutex` で直列化する別 PR。

## 検証 (レビュー反映後)

| 検査 | 結果 |
|---|---|
| `cargo fmt --check` | ✅ EXIT=0 |
| `cargo clippy --all-targets -- -D warnings` | ✅ EXIT=0 |
| `cargo clippy --all-targets --features package -- -D warnings` | ✅ EXIT=0 |
| `cargo test --features package --workspace` | ✅ **705 passed / 0 failed** |
| `macos_hook_rehook` 連続 10 回 | ✅ pass=10 / fail=0 |
| ゴールデン | ✅ `OK: 15 snapshots match` |
| schema | ✅ byte-equal |
| `analysis/` 差分 | ✅ 無し (⚠️ `HMM_VERSION` bump 不要) |
| 判定ロジックの陽性対照 | ✅ **4 枝すべて到達・8/8 一致** |
| 実物での診断出力 | ✅ わざと落として確認 (正しい枝が出た) |
