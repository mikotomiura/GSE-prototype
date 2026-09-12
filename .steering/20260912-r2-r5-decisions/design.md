# 設計: R-2〜R-5

## ★ grill 中に実測した事実 (⚠️ ここだけは推測でない・2026-09-12 / 本機 = G-GEAR)

⚠️ **裁定の根拠はすべてこの表である。** ★ handoff の記述を一次資料にしていない。

| # | 検証 | コマンド | 結果 | 帰結 |
|---|---|---|---|---|
| 1 | repo 直下の `rust-toolchain.toml` は**サブディレクトリでも効くか** | scratchpad に `tc-probe/rust-toolchain.toml` を置き `tc-probe/sub/` で `rustup show active-toolchain` | ★ `1.94.1-... (overridden by '<...>/tc-probe/rust-toolchain.toml')` | ✅ CI の `working-directory: src-tauri` の **6 つの cargo step すべてに効く** |
| 2 | ⚠️ **`+toolchain` はファイルを上書きするか** | 同ディレクトリで `cargo +1.87 --version` | ★ `cargo 1.87.0 (99624be96 2025-05-06)` | ✅ **R-2 で固定しても R-3 の検証は成立する** → ⚠️ PR の順序に技術的制約は無い |
| 3 | 未導入の toolchain は自動 DL されるか | 同上 (1.87.0 は未導入だった) | ★ `info: downloading 6 components` → 成功 | ✅ R-3 に `rustup toolchain install` は**不要**。⚠️ 副作用で本機に 1.87.0 が入った |
| 4 | 新規 toolchain に **host target の std** が入っているか | `rustup target list --installed --toolchain 1.94.1` | ★ `x86_64-pc-windows-msvc` (= host) | ✅ ⚠️ **`targets` をファイルに書かない**判断の根拠 (下記 決定 3) |
| 5 | `matrix.target` は host と同一か | `ci.yml` L269-274 | ★ win=`x86_64-pc-windows-msvc` / mac=`aarch64-apple-darwin` | ✅ 両レグとも **host = target**。#4 と合わせ `targets` 不要が確定 |
| 6 | ⚠️ `check` job の cargo は `--target` を渡すか | `grep -- --target ci.yml` | ★ L389/399/402/411/436 の **5 箇所すべて**が `--target ${{ matrix.target }}` | ✅ #5 と合わせ、固定後も target 解決は変わらない |

## PR-B (先) — R-3 ＋ R-4

### R-3: MSRV `1.87` の実証

- ★ 変更対象: `src-tauri/Cargo.toml` の `rust-version` **注記のみ** (値は実測次第)。
- ★ 手順: `cd src-tauri && cargo +1.87 check --all-targets --features package`
- ⚠️ **限界を先に明記する**: ★ 本機は Windows なので **`hook_macos.rs` / `observe_macos.rs` /
  `ime_macos.rs` は 1 行もコンパイルされない**。→ ⚠️ 「crate 全体」ではなく
  **「Windows 側の cfg 集合で」** 通ることの実測である。★ 注記にそう書く
  (`docs/agent-shared.md`「手元の検証は CI の代替にならない」)。
- ⚠️ **継続保証はしない** (裁定: CI に MSRV job は足さない)。★ 次に新しい std API を
  使ったときに気付く仕組みは**無い**ことを注記に残す。

### R-4: `redact_home_path` テストの loud 化

- ★ 変更対象 1: `src-tauri/src/lib.rs:5260` `redact_home_path_masks_real_home_from_env`
  - ⚠️ `else { return; }` (無音 skip) → `else { panic!(...) }`
  - ★ panic メッセージに **「なぜ skip させないか」** を書く (env 経路の回帰保護であること)。
- ★ 変更対象 2: `.github/workflows/ci.yml` `check` job
  - ⚠️★★★ **`env:` で HOME / USERPROFILE を上書きしない** (決定 4)。
  - ★ `cargo test` step の**前**に「env 前提の検査 step」を置く。
  - ⚠️ **値は出力しない** —— ★ 値には OS ユーザー名が入る。これはまさに本テストが
    守っている情報である (`data-privacy`)。**set/unset の別だけ**を出す。
    ⚠️ **`${VAR:+set}` 系のイディオムは採らなかった** (★ 判断 10) —— `if [ -n .. ]` を使う。

## PR-A (後) — R-2: toolchain 固定

- ★ 新規: **repo 直下** `rust-toolchain.toml`

  ```toml
  [toolchain]
  channel = "1.94.1"
  components = ["clippy", "rustfmt"]
  ```

  ⚠️ `targets` は**書かない** (実測 #4/#5)。★ 書くと相手 OS の std を両機に入れ、
  mac のディスク (threshold 15GiB) を無駄に食う。
- ★ `ci.yml`: **3 つの `dtolnay/rust-toolchain@stable` はそのまま残す** (決定 5)。
  注記だけ足して「実際に cargo が使う版は `rust-toolchain.toml` が決める」と明示する。
- ⚠️ `.claude/hooks/stop-check.sh` は **repo 内で cargo を叩く**ので自動的に 1.94.1 になる
  (★ 現在も 1.94.1 なので**挙動は変わらない**)。

## テスト戦略

| 対象 | 手段 | Done |
|---|---|---|
| R-3 | `cargo +1.87 check --all-targets --features package` | exit 0 |
| R-4 (テスト側) | `cargo test --features package --workspace` | exit 0 ＋ 当該テストが **実行された**ことを `--nocapture` なしで確認 (★ panic 側に倒したので、走れば緑・走らなければ赤) |
| R-4 (変異) | `else` を `return` に戻す変異で、⚠️ **CI の検査 step が意味を失う**ことを確認 | ★ 変異版が「env 不在でも緑」になることを実証 |
| R-2 | `rustup show active-toolchain` / ゴールデン `gse-replay --snapshot` | `overridden by` を含む / 226 snapshot が byte-equal |
| 全体 | `cargo clippy --all-targets --features package -- -D warnings` | exit 0 |
