# mac セッション開始プロンプト — **mac 側の clippy を緑にし、CI の検査ゲートを閉じる**

> ✅ **現行**（作成 2026-09-12・Windows 機 = G-GEAR のセッションから委託・**未着手**）。
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
