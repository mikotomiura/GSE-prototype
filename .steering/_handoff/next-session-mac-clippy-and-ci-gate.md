# mac セッション開始プロンプト — **mac 側の clippy を緑にし、CI の検査ゲートを閉じる**

> ✅ **完了**（2026-09-12・mac 実機で実施 → **PR #190**・⚠️ **main へのマージは未実施＝研究者判断**）。
> ★ 結果: mac 側 clippy **7 件** → `exit 0` ／ 起票 10② を閉じた ／ **R-1 = CI に clippy step を追加し、
> check の両 OS レグ ＋ frontend-check がすべて pass**。
> ⚠️★★★ **§5 の R-2 / R-3 / R-5 は依然として未決**。★ R-4 は
> **「観察できない」ことが判明した**（テストが skip を沈黙で表現するため。詳細は下記 §8）。
> → ★ 実施記録の一次資料は `.steering/20260912-mac-clippy-green-and-ci-gate/decisions.md`。
>
> ⚠️ 以下の §0〜§7 は**着手前の記述**であり、履歴として残す（★ 現状の根拠には使わない）。

> ✅ **旧ヘッダ**（作成 2026-09-12・Windows 機 = G-GEAR のセッションから委託・**未着手**）。
> ⚠️★★★ **このメモを一次資料にしない。** 実体は
> `.steering/20260912-post-mac-sync-cleanup/decisions.md`（★ 判断 8 / 9 / 12 / 13 / 14 と
> 末尾の「研究者判断に委ねる」表 R-1〜R-5）にある。
>
> ★ 前提: Windows 側の後片付けは **PR で main へ入っている**（コミット `025769e` / `80859ed` / `c5a5e69`）。
> → ⚠️ **まず `main` を pull すること。**

## §0 ⚠️★★★ なぜ mac でしかできないのか

★ Windows では **`hook_macos.rs` / `ime_macos.rs` / `observe_macos.rs` / `sensors_macos.rs` が
1 行もコンパイルされない**（`#[cfg]`）。
→ ⚠️★★★ **mac 側の clippy に何件あるかは、本機からは原理的に測れない。**

★ 実際に Windows 側では **51 件**出た（lib/bin 33 ＋ `#[cfg(test)]` 18）。
⚠️ **同種の lint が mac 固有ファイルにもある可能性が高い**（★ 同じ toolchain 1.94 の新 lint 群）。

⚠️ **本機で書いたが未検証の箇所が 1 つある**:
`src-tauri/src/input/ime_macos.rs` の `#[allow(clippy::new_without_default)]`
（★ `impl Default` を入れかけて撤回した跡。判断 9）。→ ★ **まずここがビルドを通るか確かめる。**

## §1 ⚠️★★★ 最初に実行する（★ `src-tauri/` から）

```bash
cd ~/<repo>/GSE-prototype && git checkout main && git pull
cd src-tauri

# ★ ① まず Windows で緑になった条件が mac でも緑かを見る
cargo clippy --quiet --all-targets -- -D warnings ; echo "exit=$?"

# ★ ② 件数と箇所を取る（⚠️ 1 回では全部出ない —— 下記 §2）
cargo clippy --quiet --all-targets --message-format=short -- -D warnings 2>&1 | grep -E '^src'
```

## §2 ⚠️★★★ **件数を当てにしない**（★ Windows で実際に踏んだ罠）

★ 当初 **29 件**と計測したが、**直すたびに次が現れて最終 51 件**になった。機序は 2 つ:

1. ⚠️ **clippy は lib が落ちた時点で止まる** → lib を緑にするまで **bin の指摘が 1 件も見えない**
   （★ Windows では lib を緑にした瞬間 `replay.rs` の 4 件が出現した）。
2. ⚠️ **`--all-targets` を付けないと `#[cfg(test)]` が一切解析されない**
   （★ `features.rs` で潰したのと**同じ lint** が `probe_scheduler.rs` のテストに生き残っていた）。

→ ★ **受け入れ条件は「N 件直す」ではなく `exit 0` に置くこと。**
★ `.claude/hooks/stop-check.sh` は 2026-09-12 に `--all-targets` を足してあるので、
⚠️ **mac でも同じ範囲が検査される**。

## §3 ★ 直し方の作法（⚠️ Windows 側で確立した 3 原則）

| 原則 | 中身 |
|---|---|
| ⚠️★★★ **lint の help を鵜呑みにしない** | ★ `logger.rs` では「字下げしろ」に従うと **doc の付け間違いを固定するところだった**（実際は `9eb1384` が doc と関数の間に static を挿入していた）。→ ★ **lint は「書式の指摘」ではなく「異常の兆候」として読む** |
| ⚠️★★★ **外部契約を lint の都合で動かさない** | ★ `schema_dto.rs` の doc は **schemars が JSON Schema の `description` に載せている**。字下げ / 空行が **そのまま schema drift** になるので `#[allow(clippy::doc_lazy_continuation)]` にした。⚠️ **mac 固有ファイルに同種があれば同じ判断を採る** |
| ⚠️★★★ **`#[allow]` を無言で置かない** | ★ Windows 側の 3 箇所すべてに「なぜ許容するか」を書いた |

⚠️★★★ **`iter()` 化で浮動小数の加算順序を変えないこと。**
★ `engine.rs` の HMM は `enumerate()` で添字を取るだけに留めた（⚠️ `sum()` / `fold` にしない）。
★ mac 固有ファイルに数値計算があれば同じ制約が効く。

## §4 ★ 検証（⚠️ Windows と同じ 5 点を通すこと）

```bash
cd src-tauri
cargo clippy --quiet --all-targets -- -D warnings   # ★ exit 0
cargo fmt --check
cargo test --workspace                               # ⚠️ 件数は Windows と違って当然（#[cfg] 差）
for f in tests/fixtures/*.ndjson; do b=$(basename "$f" .ndjson); \
  cargo run --quiet --bin gse-replay -- "$f" --snapshot "tests/snapshots/$b.json"; done
cargo run --bin emit_schema | diff - schema/current.json && echo "schema OK"
```

⚠️★★★ **ゴールデンがずれたら `HMM_VERSION` を bump してはならない。**
★ それは「挙動を変えた」合図ではなく **「その修正が誤っている」合図**である
（★ Windows 側は 226 snapshot が byte-equal のままだった）。

## §5 ⚠️★★★ 研究者判断（★ ここからは**私が決めなかった**もの）

| # | 事項 | 判断に要る材料 |
|---|---|---|
| **R-1** | ★ **CI (`check` job) に clippy step を足すか** | ⚠️ **§1 が緑になってから**でないと足せない（★ 足した瞬間 main の CI が赤になり全作業が止まる）。→ ★ **本タスクの主目的はこれを足せる状態にすること** |
| **R-2** | ⚠️ `rust-toolchain.toml` で toolchain を固定するか | ★ 今回の根本原因は **toolchain drift**（1.94 の新 lint）。⚠️ 固定すると lint 増加は止まるが **セキュリティ修正の追従も止まる**。★ CI は `dtolnay/rust-toolchain@stable` なので**両マシン ＋ CI に波及**する |
| **R-3** | ★ `rust-version = "1.87"` が mac の toolchain で問題ないか | ★ 根拠は **ローカル `rust-src` の `#[stable(since=..)]` 実測**（`is_multiple_of`=1.87.0 / `is_none_or`=1.82.0 / `repeat_n`=1.82.0 / `abs_diff`=1.60.0）。⚠️ **「1.87 で crate 全体がビルドできる」ことの実測ではない** |
| **R-4** | ⚠️ **CI 実行環境で `USERPROFILE` / `HOME` が立っているか** | ★ 立っていないと、2026-09-12 に追加した `redact_home_path_masks_real_home_from_env` が **静かに skip して回帰保護が実質無効**になる（⚠️ security review MEDIUM を閉じるために足したテスト）。→ ★ R-1 と同じ機会に見る |
| **R-5** | ⚠️ `scripts/run-codex-review.sh` の Windows 対応 | ★ Windows では **エラー 1312**（`--sandbox read-only` でシェルが起動できない）で使えず、`codex exec` 直接呼び出し＋「シェル禁止」明記で回避した。⚠️ **その結果 `.codex/budget.json` の更新が自己申告になる**（★ 2026-09-12 は +30,996 で `per_invocation_max` を僅かに超過。経緯は判断 14）。⚠️ **mac では再現しない問題**なので、mac 側で直すなら Windows 実機での確認が要る |

## §6 ★ 済んでいること / 未実施（⚠️ 混ぜない）

**済み**（2026-09-12・Windows 実機 = G-GEAR）:
- ★ Windows 側 clippy **51 件** → `--all-targets` 込みで **exit 0**
- ★ `cargo fmt --check` OK / `cargo test --workspace` **654 passed 0 failed**
- ★ ゴールデン **6 fixture / 226 snapshot byte-equal** / `emit_schema` byte-equal
- ★ `stop-check.sh` に `--all-targets` を追加
- ★ `Cargo.toml` に `rust-version = "1.87"` を宣言
- ★ `code-reviewer` / `security-checker` / `/cross-review`（Codex）を実施。⚠️ **マージを妨げる指摘ゼロ**
- ★ ローカルブランチ 26 本削除 / `gse-dataset` の未追跡 metrics 13 本削除

**未実施**（★ このメモの仕事）:
- ⚠️ **mac 側 clippy の件数すら分かっていない**（→ §1）
- ⚠️ `ime_macos.rs` の `#[allow(clippy::new_without_default)]` は **Windows で未検証**
- ⚠️ R-1〜R-5 は **どれも未決**

---

## §7 ★★★ 2026-09-12 追記 — **mac 側で先に測った事実と、研究者が下した判断**

> ⚠️ 本節は **mac セッション (Opus) が着手前に測った実測値と、研究者がその場で下した裁定**である。
> ★ 実行そのものは**コンテキストの都合で次セッションに送った**ので、**着手は `/start-task` から**。

### 7.1 ★ 研究者判断（★ §5 の R-1 を含む）

| # | 事項 | 裁定 |
|---|---|---|
| **S-1** | ★ **スコープ** | ✅ **clippy を `exit 0` にする ＋ `blockers.md` 起票 10②（`IME_OPEN.store` の Ordering）を直す**。⚠️ **起票 10①（素通しアーム）は入れない** |
| **R-1** | ★ CI (`check` job) に clippy step を足すか | ✅ **足す。ただし「緑にしてから」** —— ★ clippy が両 OS で `exit 0` になったことを確かめた**あと、同じ PR で** `ci.yml` に追加する |
| R-2〜R-5 | toolchain 固定 / `rust-version` / CI の `HOME` / `run-codex-review.sh` | ⚠️ **未決のまま**（★ この turn では諮っていない） |

### 7.2 ⚠️★★★ なぜ起票 10② を入れ、①を入れないのか（★ 理由まで持っていくこと）

**② を入れる理由 —— 「関連」ではなく *同じブロックの中* だった:**

```rust
// src-tauri/src/input/ime_macos.rs:77-81  (★ 2026-09-12 時点)
if last_state.map_or(true, |prev| prev != current_state) {   // ← ★ clippy 指摘 (77 行)
    last_state = Some(current_state);
    IME_OPEN.store(current_state, Ordering::Relaxed);        // ← ⚠️ 起票 10② (79 行)
    ...
}
```

★ clippy の `map_or` を直すには **77〜81 行を編集する**ので、79 行は目の前にある。
★ 判断基準は「**設計上の争点があるか**」——②は `hook-constraints` 共通-2（`IME_OPEN` の store は
**Release**）に照らして**正誤が決まる**ので争点が無い。
⚠️★★★ **`ime_windows.rs:289` が対になっている。片方だけ直さないこと**（★ 両 OS で規則を揃える）。
⚠️ ただし **lint 修正とは別コミットに分ける** —— ★「lint は挙動を 1 ビットも変えない」という
§4 の不変条件を、後から diff で読めるまま残すため。

**① を入れない理由:**
⚠️★★★ **VK 分布が変わりうるので `HMM_VERSION` の判断が要る**（`hook_macos.rs:243` の注記）。
★ §4 は「**ゴールデンがずれたら `HMM_VERSION` を bump するのではなく、その修正が誤っている合図**」を
受け入れ条件に置いているので、⚠️ **①を混ぜるとこの契約が壊れて赤の意味が読めなくなる。**
→ ★ ① は **起票 6（ライブ変換）と一緒に idea 議論 / Mh-D 全体の修正**に載せる（`decisions.md` 判断 12）。

### 7.3 ★ mac 側 clippy の実測（2026-09-12・`main` = `8d4b8c3`）

⚠️★★★ **`cargo clippy --quiet --all-targets -- -D warnings` は `exit=101`**（★ 緑ではない）。

★ 内訳は **7 件**（`--message-format=short` で実測）:

| ファイル:行 | lint |
|---|---|
| `lib.rs:3610` | `unused variable: was_active` |
| `lib.rs:854` / `lib.rs:862` | `this map_or can be simplified` |
| `hook_macos.rs:100` | `doc list item without indentation` |
| `hook_macos.rs:204` | `casting raw pointers to the same type and constness is unnecessary` |
| `hook_macos.rs:1062` | `manual implementation of .is_multiple_of()` |
| `ime_macos.rs:77` | `this map_or can be simplified` ← ★ **起票 10② の 2 行手前** |

⚠️★★★ **「7 件」を受け入れ条件にしないこと。** ★ §2 のとおり
**lib が緑になるまで bin の指摘は 1 件も見えない**ので、直すと増える。**基準は `exit 0`**。

★ **`lib.rs:854` / `862` は `#[cfg(target_os = "macos")]` ブロック内**（実測）——
⚠️ **Windows からは原理的に見えなかった**もので、§0 の主張が実地で裏づけられた。

### 7.4 ⚠️ `hook_macos.rs:204` は §3 の第 1 原則に当たる可能性が高い

★ `casting raw pointers ... (*const c_void -> *const c_void)` の help は
`&_dispatch_main_q as *const _` を勧めてくる。⚠️★★★ **ここは `dispatch_sync_f` に渡す
GCD のメインキューであり、FFI 境界**である。→ ★ **「書式の指摘」として従わず、
型が本当に一致しているかを一次資料（`#[link]` 宣言と `dispatch_sync_f` の署名）で
確かめてから当てること**（§3「lint の help を鵜呑みにしない」）。

### 7.5 ★ 着手時の状態（★ そのまま使える）

- `main` = `8d4b8c3`（PR #188 まで取り込み済み）・作業ツリーはクリーン・OPEN な PR ゼロ
- `cargo test --workspace` **659 passed / 0 failed** ／ ゴールデン `OK: 15 snapshots match` ／
  `emit_schema` **drift なし** ／ `cargo fmt --check` clean（★ すべて mac 実機で実測）
- ⚠️ `ime_macos.rs:35` の `#[allow(clippy::new_without_default)]` は **mac でビルドが通ることを確認済み**
  （★ §0 が「まずここがビルドを通るか確かめる」と書いていた件 —— **通っている**）


---

## §8 ★★★ 2026-09-12 実施結果（★ mac 実機・PR #190）

### 8.1 ✅ 達成したもの

| 項目 | 結果 |
|---|---|
| mac 側 clippy | ★ **7 件 → `exit 0`**（⚠️ §7.3 の実測どおり増えなかった。★ lib が最初から 7 件で止まっており、直したら bin の新規指摘は**出なかった**） |
| 起票 10② | ✅ **閉じた**。⚠️ store だけでなく **load 4 箇所も Acquire へ**（★ 下記 8.2） |
| **R-1（CI に clippy）** | ✅ **達成**。check 両 OS ＋ frontend-check すべて pass |
| 回帰 | ★ 659 passed 0 failed ／ ゴールデン **226 snapshot byte-equal** ／ schema drift なし。⚠️ **`HMM_VERSION` は bump していない** |
| レビュー | ★ code-reviewer / security-checker / `/cross-review`（Codex・**縮退なし**）— ⚠️ **マージを妨げる指摘ゼロ** |

### 8.2 ⚠️★★★ 判断を 1 つ撤回した —— **片側だけの Ordering 修正は silent no-op だった**

★ §7.1 の S-1 は「起票 10②（**`IME_OPEN.store` の Ordering**）を直す」と**括弧で store に絞って**
いたので、当初はそれに従って load 側を触らなかった。⚠️ **これは誤りだった。**

⚠️ **code-reviewer / security-checker が揃って指摘**: **store だけ Release にしても、
読み手が Relaxed なら happens-before は成立しない**。
→ ★ 「規則に合わせた」という**記録だけが残り、実際には何も保証していない**状態になるところだった。

★ 裁定の**理由**は「共通-2 に照らして**正誤が決まる**から争点が無い」であり、
**正しくするには対を閉じるしかない**ので、同じ根拠の射程内と判断して閉じた。
★ 実測後 `IME_OPEN.load(Ordering::Relaxed)` は **0 件**。

### 8.3 ⚠️★★★ R-4 は **観察できないことが分かった**（★ 質問そのものを変える必要がある）

★ R-4 は「CI 実行環境で `USERPROFILE` / `HOME` が立っているか」を**観察する**課題だったが、
⚠️ **`redact_home_path_masks_real_home_from_env` は env が無いと沈黙して skip する**ので、
★ **CI ログを見ても「通った」と「skip した」が区別できない**。

→ ⚠️ **観察可能にするには先にテスト側を変える必要がある**（★ env が無ければ **fail する**か、
  skip を**出力する**形にする）。⚠️ これは R-4 とは別の作業なので**本 PR では行っていない**。
★ これは `silent-success-is-not-visible` と同型の問題である。

### 8.4 ⚠️ 新しく起票したもの: **`IME_ACTIVE` の Ordering が 7 箇所 Relaxed**

★ `IME_OPEN` を閉じる過程で実測した（store 4 / load 3）。⚠️ `hook-constraints` 共通-2 は
**`IME_ACTIVE` も同じ規則**と定めている。
⚠️★★★ **本 PR では直していない** —— ★ `hook_windows.rs:603`（**フックコールバック内**）を含み、
**mac からは 1 行もコンパイルできない**ため。→ ★ **Windows 実機/CI と対で別 PR**にする。
（実測表は `20260911-outcome-arbitration-and-o1-preflight/blockers.md` 起票 10 と
  `20260912-mac-clippy-green-and-ci-gate/decisions.md` 末尾）

### 8.5 ★ CI の実測値（⚠️ 次に赤を見た人が読む数字）

| レグ | clippy step | job 全体 | ★ `timeout-minutes: 30` の余裕 |
|---|---|---|---|
| Windows | **42 秒** | 4m18s | ★ 25 分以上 |
| macOS | **49 秒** | 5m50s | ★ 24 分以上 |

⚠️★★★ **ディスクだけは余裕が無い**: `free before: 18 GiB (threshold=15 floor=8)` →
run 後の空きは **16 GiB**、`src-tauri/target` は **3.0 GiB**（★ 本 PR 前の実測 2.1 GiB から +0.9 GiB）。
→ ⚠️ **次の run で cargo-sweep が走る見込み**。★ ガードが設計どおり働くだけだが、
  **掃除が走った run は遅くなる**ので「遅い＝壊れた」と読み違えないこと（★ `free before:` を先に見る）。

⚠️★★★ **「clippy が赤」と「timeout で cancel」は `gh pr checks` では区別がつかない。**
★ `gh api repos/.../actions/jobs/<id>` の `.steps[].conclusion` まで降りる
（⚠️ timeout なら clippy step は `failure` ではなく **`cancelled`**）。

### 8.6 ⚠️ 残っている研究者判断

| # | 事項 | 状態 |
|---|---|---|
| — | ★ **PR #190 を main へマージするか** | ⚠️ **未実施**（★ CI は全緑・レビューは 3 系統とも通過） |
| R-2 | toolchain 固定 | ⚠️ **未決**。★ `@stable` ＋ `-D warnings` は**コード差分ゼロでも一斉に赤くなりうる**。⚠️ そのときは **「lint 修正が先」**・`-D warnings` を外して逃げない（★ 外した瞬間「見えないまま緑」へ戻る） |
| R-3 | `rust-version = "1.87"` の実証 | ⚠️ **未決**。★ 本 PR で `is_multiple_of`（安定化が**ちょうど 1.87**）を使ったので必要性は**上がった**。⚠️ MSRV を検査する CI job は**存在しない** |
| R-4 | CI の `USERPROFILE` / `HOME` | ⚠️ **観察不能と判明**（→ §8.3）。★ 先にテストを loud にする作業が要る |
| R-5 | `run-codex-review.sh` の Windows 対応 | ⚠️ **未決**（★ mac では再現しない） |
| 新 | `stop-check.sh` に `--features package` を足すか | ⚠️ **未決**。★ 足せば CI と揃うが、毎 Stop で age / reqwest を再解析するコストが乗る |
| 新 | `check` job に `permissions: contents: read` | ⚠️ **未決**（★ 本 PR が作った穴ではない・既存） |
