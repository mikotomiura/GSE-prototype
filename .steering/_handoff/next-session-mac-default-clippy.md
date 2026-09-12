# mac セッション開始プロンプト — **default features の clippy を mac で緑にする（F-4 の前提）**

> ✅ **現行**（作成 2026-09-12・Windows 機 = G-GEAR のセッションから・**未着手**）。
> ⚠️★★★ **このメモを一次資料にしない。** 実体は
> `.steering/20260912-r2-r5-decisions/decisions.md`（★ 判断 53 / 54）にある。
>
> ⚠️★★★ **これは `next-session-followups-f1-f5.md` の F-4 の前提工程である。**
> ★ **本メモが終わるまで F-4（CI に default features の clippy を足す）に着手しない。**

## §0 ⚠️★★★ なぜ mac が要るのか（★ ここを取り違えない）

★ **CI の clippy は `ci.yml:559` の 1 箇所だけ**で、**`--features package` 付き**である（実測）。
→ ⚠️ **default features のみの clippy は CI に存在しない。**

| | default features の clippy |
|---|---|
| ★ Windows 実機 | ✅ **exit 0**（2026-09-12 実測・1.98.1・warm 10s） |
| ⚠️★★★ **mac 実機** | ⚠️ **未検証** |

- ⚠️ mac セッション（2026-09-12）が実測したのは
  **`--all-targets --features package --target aarch64-apple-darwin`** であって、
  ⚠️ **`--features package` を外した形ではない**。
- ⚠️★★★ **ローカル `stop-check.sh` は default features で回るが、`WARN` を出すだけでブロックしない**
  → ★ **mac 側で警告が出ていても誰も気づかない構造**になっている。
  （★ 実測: `.claude/hooks/stop-check.sh` は
   `cargo clippy --manifest-path "$MANIFEST" --quiet --all-targets -- -D warnings` を
   `>/dev/null 2>&1` で捨て、失敗時に `echo "[stop] WARN: ..."` するだけ）
- → ⚠️★★★ **緑を確かめずに CI へ足すと main が即赤になり全作業が止まる。**
  ★ これは **R-1（CI の clippy ゲート）で学んだ順序そのもの**である:
  **① mac で緑にする → ② CI に足す**。

## §1 ★ やること

### 手順 1: ⚠️ **まず測る**（★ 件数を受け入れ条件にしない）

```bash
cd src-tauri
cargo clippy --all-targets -- -D warnings ; echo "EXIT=$?"
```

- ★ **受け入れ条件は `exit 0`** であり、⚠️ **件数ではない**
  （★ 教訓: clippy は lib が落ちた時点で止まるので、**直すと次が見える**。
   ⚠️ 2026-09-12 に「29 件」と見えたものが最終的に **51 件**になった実績がある）。
- ⚠️ `--target aarch64-apple-darwin` は**付けても付けなくてもよい**が、
  ★ **CI と比較するなら付けない方**（CI の default features 版は**まだ存在しない**ため）。

### 手順 2: ★ 出た指摘を直す（⚠️ 作法は本 repo の既存判断に従う）

⚠️★★★ **lint の help を鵜呑みにしない。** ★ 2026-09-12 に**まさにこれで救われた**実例:

- ★ `doc_lazy_continuation` が `logger.rs` で出たとき、⚠️ **字下げして黙らせていたら
  「doc が別の static に付いている」という実在の欠陥を固定してしまうところだった**
  （★ `git show 9eb1384^` で、doc が元は `fn write_meta_start` に直付けされていたと判明）。
- ★ `schema_dto.rs` の doc は **schemars が JSON Schema の `description` に載せる外部契約**なので、
  ⚠️ **整形すると schema drift になる** → `#[allow]` ＋ 理由コメントで黙らせる。
- ⚠️ **浮動小数の加算順序を変えない**（★ `iter().sum()` / `fold` への書き換え禁止）——
  ゴールデンが割れるのは**修正が誤っている合図**であって `HMM_VERSION` bump の合図ではない。
- ⚠️ **`new_without_default` に安易に `impl Default` を足さない** ——
  ★ `ImeMonitor::new()` は **COM を初期化する**ので、`Default`（安価・副作用なし が慣習）に
  してはいけない（★ 2026-09-12 に一度足して**撤回した**）。

### 手順 3: ★ 緑になったら **両スコープで**確かめる

```bash
cd src-tauri
cargo clippy --all-targets -- -D warnings                                   # default features
cargo clippy --all-targets --features package -- -D warnings               # ★ CI と同じ（退行防止）
cargo test --features package --workspace                                  # 11 スイート
cargo run --bin gse-replay -- tests/fixtures/minimal.ndjson --snapshot tests/snapshots/minimal.json
cargo run --bin emit_schema                                                # schema/current.json と byte-equal
```

- ⚠️★★★ **`--features package` 側の退行を必ず見る** —— ★ default 側を直した結果、
  `#[cfg(feature = "package")]` の中が壊れることがありうる。
- ⚠️ **`HMM_VERSION` は bump しない**（★ ゴールデンが byte-equal なら挙動は変わっていない）。

### 手順 4: ⚠️ **CI には足さない**（★ ここで止める）

- ★ **本メモの仕事は「mac を緑にする」まで**である。
- ⚠️ CI への追加（F-4）は **Windows 側のセッション**が
  `next-session-followups-f1-f5.md` に従って行う。
- → ★ 完了報告に **「mac の default features clippy は exit 0」と明記**すること
  （⚠️ これが F-4 の着手条件になる）。

## §2 ⚠️ mac 実機の環境について（★ 2026-09-12 の変更が効く）

- ⚠️★★★ **toolchain が固定された**（PR #194 / main `a5960b9`）。
  ★ repo の中で `cargo` を叩くと **rustup が自動で `1.98.1` へ切り替える**
  （`rust-toolchain.toml` / `profile = "minimal"` / `components = ["clippy","rustfmt"]`）。
- ★ **CI ランナー（`macbook-air-m-arm64`）には既に `1.98.1` が入っている**
  （★ 実測: 2 回目の run で install step が **1 秒**だった = 導入済み）。
  ⚠️ **開発用クローンと CI ランナーが同一ユーザー（`/Users/johnd/...`）なら
  `~/.rustup` を共有するので追加ダウンロードは起きない見込み**。
  → ★ ⚠️ **これは推測なので、最初に `rustup show active-toolchain` を叩いて確かめること。**
  期待する出力: `1.98.1-aarch64-apple-darwin (overridden by '.../rust-toolchain.toml')`
- ⚠️★★★ **mac のローカル `stable` が古い場合、clippy の lint 集合が変わる。**
  ★ Windows 機はローカル `stable` が **1.94.1**（5.5 か月前）で、⚠️ **CI の 1.98.1 と
  別の lint 集合を検査していた**ことが 2026-09-12 に判明した。
  → ⚠️ **mac でも同じズレがあった可能性がある**。★ 固定によって解消されるが、
  **その結果 default features 側で新しい lint が出るかもしれない**（= 本メモの仕事）。
- ★ ディスク（CI ランナー・**guard 自身の計器**）: `free before: 19 GiB (threshold=15 floor=8)` /
  `wiped=false`。⚠️ **`df -h` の数字で外挿しないこと**（★ guard の `df -Pk` と食い違う実績がある）。

## §3 ★ ついでに測ってほしいこと（⚠️ F-3 の判断材料・**任意**）

★ `stop-check.sh` に `--features package` を足すか（F-3）は、**hook が走る機械のコスト**で決まる。
⚠️ **Windows の数字は mac に当てはまらない**ので、mac で作業する頻度が高いなら測っておく:

```bash
cd src-tauri
time cargo clippy --all-targets -- -D warnings                 # 現状の hook と同じ
time cargo clippy --all-targets --features package -- -D warnings   # 足した場合
```

★ Windows 実機の実測（2026-09-12・warm・1.98.1）: **10s → 14s**（★ 増分 +4 秒/Stop）。

## §4 ★ 進め方（CLAUDE.md 準拠）

1. ★ `/start-task` を起動する（⚠️ **実装系は必ず先**）。
2. ★ `docs/agent-shared.md` → `docs/development-guidelines.md` §1/§3 を先読み。
3. ★ Skill を Read: `rust-standards` / `architecture-rules` /
   （`hook_macos.rs` / `ime_macos.rs` を触るなら）`hook-constraints` / `verify-before-claiming`。
4. ★ レビューは **`code-reviewer` + `security-checker` を並列**起動。
5. ★ 完了時に **`/cross-review`**（⚠️ mac では 1312 の問題は元々起きない）。
6. ⚠️ `.steering/[YYYYMMDD]-[task-name]/` の記録を省略しない。

## §5 ⚠️ 蒸し返さないこと（★ 2026-09-12 に決着済み）

- ★ toolchain を固定するか／固定先の版（**1.98.1**）／`targets` を書くか／`@stable` を残すか
  → **全て決着**（`20260912-r2-r5-decisions/decisions.md` 決定 1 / 3 / 5・判断 31〜35）。
- ★ MSRV（**1.88**）と継続検査 CI job を足さない判断 → **決着**（決定 2・判断 39）。
- ★ `.codex/budget.json` の上限 **300,000 据え置き** → **決着**（判断 52）。
