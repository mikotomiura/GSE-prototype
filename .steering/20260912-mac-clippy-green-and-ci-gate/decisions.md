# 設計判断

## 判断 1: ⚠️★★★ `hook_macos.rs:100` は lint の help に**従わなかった**

- ★ `doc_list_item_without_indentation` の help は「字下げしろ」と言う。
- ⚠️ しかし当該文 (`` `AtomicPtr` は安全な共有セルとして用いる。``) は
  **箇条書き 2 項目の続きではなく、doc 全体を締める独立した段落**である。
  字下げすると「ライフタイム安全性」の項目の一部になり、**意味が変わる**。
- **対応**: 空行 (`///`) を入れて段落を分けた。
- ★ これは引き継ぎ §3 第 1 原則 (**lint は書式の指摘ではなく異常の兆候として読む**) の
  適用例である。⚠️ 実際、異常は「字下げが無いこと」ではなく **段落の区切りが無かったこと**だった。

## 判断 2: ⚠️★★★ `hook_macos.rs:204` の FFI キャストは**一次資料で確かめてから**当てた

- ★ clippy: `casting raw pointers to the same type and constness is unnecessary`
  (`*const c_void -> *const c_void`)、help は `&_dispatch_main_q as *const _`。
- ⚠️ ここは **GCD の `dispatch_sync_f` に渡すメインキュー = FFI 境界**なので、
  「同じ型だ」という clippy の主張自体を検算した:
  - `src/input/hook_macos.rs:167` `static _dispatch_main_q: std::ffi::c_void;`
  - `src/input/hook_macos.rs:168-172` `fn dispatch_sync_f(queue: *const std::ffi::c_void, ..)`
  → ★ `&_dispatch_main_q as *const _` は**引数の型から `*const c_void` に推論される**ので、
    後段の `as *const c_void` は真に no-op。
- **対応**: ★ help の `*const _` (推論) ではなく **`as *const std::ffi::c_void` と型を明記**した。
  ⚠️ FFI 境界で型を推論に委ねると、将来 `dispatch_sync_f` の署名が変わったとき
  **黙って別の型へ推論される**。★ 明記しておけば署名が変わった瞬間にコンパイルが落ちる。

## 判断 3: `was_active` は `_` 前置ではなく `#[cfg]` で閉じた

- ★ clippy の help は `_was_active`。⚠️ しかしそれだと **Windows 側で「意図的に使わない変数」**
  という誤った合図になる。
- ★ 実体は「**使用箇所 (`emit_ime_shadow` の呼び出し) が `#[cfg(target_os = "windows")]` に
  閉じている**」ことなので、束縛にも同じ `#[cfg]` を付けて**両者を 1 つの真実に縛った**。
- ⚠️ 片方だけ `#[cfg]` が付いている状態こそが lint の指した異常だった (判断 1 と同型)。

## 判断 4: ★ lint 修正と Ordering 修正を**別コミットに分けた**

- ⚠️★★★ lint 修正は「**振る舞いを 1 ビットも変えない**」という不変条件を持ち、
  その検証が「ゴールデン 226 snapshot が byte-equal」である。
- ★ Ordering 修正は**メモリ順序という振る舞いを変える**ので、同じコミットに混ぜると
  ⚠️ **後から diff を読んでも「どちらが挙動を変えたのか」が区別できなくなる**。
- **対応**: `5e29fec` (lint) → `5aa05e4` (Ordering) → `df471ca` (CI) の 3 コミット。

## 判断 5: 起票 10② は**両 OS 対で**直した

- ★ `hook-constraints` 共通-2 は `IME_OPEN` の store = **Release** / load = **Acquire**。
- ★ 実測すると `IME_OPEN.store` は 7 箇所あり、`hook_macos.rs` ×2 / `hook_windows.rs` ×3 は
  既に Release、⚠️ **ime ポーリングスレッドの 2 箇所だけが Relaxed のまま**だった。
- **対応**: `ime_macos.rs:79` と `ime_windows.rs:289` を同時に Release へ。
  ⚠️ 片方だけ直すと **OS 間で規則がずれる** (引き継ぎ §7.2 の明示指示)。

## 判断 5b: ⚠️★★★ 起票 10② の **load 側も閉じた** (★ レビューで判断を**撤回**した)

- ⚠️ 当初は「研究者裁定 S-1 の文言が括弧で **`IME_OPEN.store`** に絞っているから」
  load 側を触らないと決めた。★ **これは誤りだった。**
- ⚠️★★★ **code-reviewer / security-checker が揃って指摘**: store だけ Release にしても
  **読み手が Relaxed なら happens-before は成立しない**。
  → ★ 片側だけの修正は「直したつもりで**何も保証していない**」＝ silent no-op であり、
    ⚠️ **「規則に合わせた」という記録だけが残る**のが最も悪い。
- ★ 裁定 S-1 の**理由**は「共通-2 に照らして**正誤が決まる**から争点が無い」である。
  → ★ 正しくするには**対を閉じるしかない**ので、同じ根拠の射程内と判断して閉じた。
- **対応** (実測して残っていた 4 箇所):
  `lib.rs:3506` / `:3592` / `:3619` / `hook.rs:41` (`is_ime_open()`) を `Acquire` へ。
  ★ 実測後 `IME_OPEN.load(Ordering::Relaxed)` は **0 件**。
- ★ `is_ime_open()` は**呼び出し元 0 件**だったが、⚠️ **将来の呼び出し元が誤った Ordering を
  継承する入口**なので直し、doc に「対を崩さないこと」と書いた。
- ⚠️ **`IME_ACTIVE` は本 PR では触っていない** → 下の「新しい起票」を見よ。

## 判断 6: ⚠️★★★ 起票 10① は**入れなかった** (研究者裁定 S-1)

- ★ `macos_vk_to_vk` の素通しアームを直すと **VK 分布が変わりうる**。
- ⚠️ 本タスクの受け入れ条件は「**ゴールデンがずれたら `HMM_VERSION` を bump せず、
  その修正が誤っている合図として扱う**」である。①を混ぜると**この契約が壊れて
  赤の意味が読めなくなる**。
- → ★ ① は起票 6 (ライブ変換) と一緒に Mh-D 全体の修正として扱う。

## 判断 7: CI の clippy step は `--features package` を**付ける**

- ★ 既存の `cargo test` step が `--features package` を付けている理由 (ci.yml の注記) と同じ:
  ⚠️ 落とすと `reconcile.rs` (25 件) / `packaging.rs` (9 件) が検査の外に出る。
  ★ `reconcile` は **O1 の「48 時間の猶予」を守る当の機構**である。
- ⚠️ 「lint だけ範囲を狭める」と、**そこだけ見えないまま緑**になる。
- ★ mac 実機で CI と同一スコープ
  (`--all-targets --features package --target aarch64-apple-darwin -- -D warnings`) が
  **exit 0** であることを実測してから足した。

## 判断 8: `components: clippy` を**明示**した

- ⚠️★★★ `dtolnay/rust-toolchain` は `--profile minimal` で入れるので **clippy は既定で入らない**。
- ⚠️ 無いまま step を置くと、**「lint が走らなかった」のか「lint が緑だった」のか
  ログから区別できない** (= silent success を作る)。
- ★ 明示すれば、clippy が無い環境では **toolchain step 側が落ちる** (loud failure)。

## 判断 9: clippy step を check job の**末尾**に置いた

- ★ ビルド / テスト / ゴールデン / schema の**既存シグナルの順序を変えない**ため。
- ⚠️ lint は今回新しく足した門なので、先に既存の門を鳴らす方が、赤が出たときに
  「何が壊れたのか」を読み違えにくい。

## ⚠️★★★ 研究者判断に委ねる (本タスクでは**やらない**)

| # | 事項 | 現状 |
|---|---|---|
| **R-2** | `rust-toolchain.toml` で toolchain を固定するか | ⚠️ **未決**。★ 今回の根本原因は toolchain drift (1.94 の新 lint)。固定すると lint 増加は止まるが**セキュリティ修正の追従も止まる**。CI は `dtolnay/rust-toolchain@stable` なので**両マシン ＋ CI に波及**する |
| **R-3** | `rust-version = "1.87"` が実際にビルド可能か | ⚠️ **未決**。★ 根拠は `rust-src` の `#[stable(since=..)]` 実測であって「1.87 で crate 全体がビルドできる」ことの実測ではない。⚠️ 今回 `is_multiple_of` (1.87) を**新たに使った**ので、MSRV の実証の必要性は**上がった** |
| **R-4** | CI 実行環境で `USERPROFILE` / `HOME` が立っているか | ⚠️ **未観察**。★ 立っていないと `redact_home_path_masks_real_home_from_env` が**静かに skip して回帰保護が実質無効**になる。⚠️ **テストが skip を沈黙で表現している**ので、CI ログを見ても区別がつかない → ★ 観察するには「env が無ければ fail する」か「skip を出力する」形に変える必要がある (別タスク) |
| **R-5** | `scripts/run-codex-review.sh` の Windows 対応 | ⚠️ **未決**。★ mac では再現しない問題なので、直すなら Windows 実機での確認が要る |

---

## ★ レビュー結果 (2026-09-12)

### code-reviewer / security-checker (並列) — ⚠️ **CRITICAL / HIGH のコード指摘はゼロ**

| 指摘 | 優先度 | 対応 |
|---|---|---|
| `.steering/` が未コミットで `Refs:` が dangling | HIGH | ✅ 対応 (steering をコミット) |
| `IME_OPEN` の load が Relaxed のまま = 対が閉じていない | MEDIUM | ✅ 対応 (判断 5b・`94e57d3`) |
| ci.yml の注記「ローカル gate と同じ範囲」が**事実と違う** | MEDIUM | ✅ 対応 (注記を訂正。⚠️ `--features package` は CI 側にしか無い) |
| `@stable` ＋ `-D warnings` は toolchain 更新日に一斉に赤くなる | MEDIUM | ⚠️ **R-2 として研究者判断へ** (下記の運用規則を明記) |
| clippy が永続 `target/` に第 2 の成果物を積む / `timeout-minutes: 30` を圧迫 | MEDIUM | ⚠️ **初回 CI 実行で実測してから**較正する (下記) |
| `check` job に `permissions:` が無い | MEDIUM | ⚠️ **本 diff が作った穴ではない** (既存の `cargo build`/`test` が同条件)。follow-up へ |
| `is_ime_active()` など `IME_ACTIVE` 側の Ordering | LOW | ⚠️ **新しい起票へ** (下記) |
| `dtolnay/rust-toolchain@stable` が可変参照 | LOW | ★ 既知 (ci.yml L98-103)。新しい供給元は増えていない |

★ FFI キャスト (`hook_macos.rs:205`) は **両レビュアーが独立に「アドレス・型とも同一で等価」と確認**。
★ `is_multiple_of` の安定化は **1.87.0** で `rust-version = "1.87"` と**ちょうど同値** (余裕なし)。

### ⚠️★★★ `-D warnings` ＋ `@stable` の運用規則 (★ R-2 が決まるまでの暫定)

★ toolchain が更新された日、**コード差分ゼロでも PR が一斉に赤くなりうる**。
→ ★ そのときの行動は **「lint 修正が先」**。⚠️ `-D warnings` を外して逃げないこと
  (★ 外した瞬間に「見えないまま緑」へ戻る)。
★ `check` job は `!startsWith(github.ref, 'refs/tags/')` なので **リリース経路は塞がらない**。

### ⚠️ 初回 CI 実行で**必ず見る**もの (★ 見ないと次から赤の意味が読めない)

1. **clippy step の所要時間** — `timeout-minutes: 30` に対する余裕。★ 5 分を切るなら上げる。
2. **`src-tauri/target` のサイズ** — ⚠️ ディスクガードは **job 冒頭に 1 回・mac レグのみ**
   なので、clippy 分の増分は**次の run まで検知されない**。
3. ⚠️★★★ **「clippy が赤」と「job が timeout で cancel」をログで区別すること。**
   ★ 区別しないと緑赤がコイントスに戻る。

## ⚠️★★★ 新しい起票: `IME_ACTIVE` の Ordering が**混在している** (★ 本 PR ではやらない)

- ★ 実測 (2026-09-12・`main` + 本ブランチ):

  | 種別 | `Release`/`Acquire` | ⚠️ `Relaxed` |
  |---|---|---|
  | store | `ime_windows.rs:476/514/540/555` / `ime_compose.rs:396/939/1110` | `lib.rs:3583` / `hook_windows.rs:212` / `hook_windows.rs:253` / `ime_windows.rs:124` |
  | load | `ime_compose.rs:441` ほかテスト / `ime_macos.rs:45` / `:80` | `hook.rs:32` (`is_ime_active()`) / `ime_windows.rs:574` / `hook_windows.rs:603` |

- ⚠️ `hook-constraints` 共通-2 は **`IME_ACTIVE` も `IME_OPEN` と同じ規則**と定めている。
  → ★ **store 4 / load 3 の計 7 箇所が規則違反**で残っている。
- ⚠️ **本 PR に入れなかった理由**: ★ 起票 10② が名指ししたのは `IME_OPEN` だけであり、
  `IME_ACTIVE` は **Windows のフックコールバック内 (`hook_windows.rs:603`) を含む 7 箇所**に
  及ぶ。⚠️ **本機では `hook_windows.rs` が 1 行もコンパイルされない**ので、
  ★ 変更の正しさを**手元で検査できない**。→ **Windows 実機/CI と対で行う別 PR にする。**
- ★ 見込み: Acquire/Release へ強めるのは**緩める方向ではない**ので安全。
  ⚠️ ただし `hook_windows.rs:603` は**フックコールバック内**なので、
  `hook-constraints` 共通-1 (ブロッキング禁止) に照らして確認すること
  (★ acquire load は x86 では単なる `mov`・ARM64 では `ldar` で**ブロックしない**)。

### `/cross-review` (Codex 独立レビュー・2026-09-12) — ⚠️ **両者一致の HIGH はゼロ・コード変更不要**

★ `scripts/run-codex-review.sh` exit 0 / 機密フィルタのブロックなし /
予算 used=57,445 (budget 300,000) ＝ **縮退なしで完走**。

| Codex の指摘 | 判定 | 理由 |
|---|---|---|
| MSRV 破壊 (`is_multiple_of` 等) | ⚠️ **却下** | ★ `rust-version = "1.87"` が既に宣言済み。`is_multiple_of` の安定化が**ちょうど 1.87**、他は以前。⚠️ Codex 自身が「最新 stable 前提なら問題なし」と留保していた |
| CI の clippy scope が既存シグナルと一致しない | ✅ **採用済み** | ★ まさに本 PR で注記を訂正した点 (⚠️ 非対称は意図的) |
| Ordering のコメントが実態より強く見える | ⚠️ **却下寄り** | ★ `ime_macos.rs` の読み手は `IME_STATE_DIRTY.swap(AcqRel)` → `JIS_KEYBOARD_SEEN.load(Acquire)` → `IME_OPEN.load(Acquire)` の順で読む構造。⚠️ x86/ARM の実機挙動としては差が出にくいという指摘は一理あるが、**Rust の抽象メモリモデル上は正当な強化** |
| メモリ順序変更に対するテストが無い | ⚠️ **LOW・follow-up** | ★ メモリ順序をユニットテストで検出するのは困難。→ 下記 follow-up へ |

### ★ follow-up 候補 (⚠️ 本 PR では**やらない**)

1. ⚠️ **`stop-check.sh` に `--features package` を足すか** —— ★ 足せば注記の非対称が消えるが、
   毎 Stop で age / reqwest を再解析するコストが乗る。**研究者判断**。
2. ⚠️ **default features のみの clippy が CI に無い** (Codex 指摘) —— ★ CI は
   `--features package` 付きだけを走らせている。⚠️ ローカル gate が default 側を見ているので
   **穴ではない**が、CI 単独では片方しか見ていない。
3. ⚠️ `check` job に `permissions: contents: read` を明示 (security-checker MEDIUM・**既存の穴**)。
4. ⚠️ `IME_ACTIVE` の Ordering 7 箇所 (★ 上の新起票)。
