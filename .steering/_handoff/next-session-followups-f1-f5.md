# セッション開始プロンプト — **R-2〜R-5 の申し送り F-1〜F-5 を片付ける**

> ⚠️ **一部消化済み**（作成 2026-09-12・Windows 機 = G-GEAR。★ **F-4 だけが残っている** —— 下記「結果」節を先に読むこと）。
> ⚠️★★★ **このメモを一次資料にしない。** 実体は
> `.steering/20260912-r2-r5-decisions/decisions.md`（★ 判断 52〜54 が本メモの根拠）と
> 同ディレクトリの `tasklist.md` 末尾の申し送り表にある。
>
> ⚠️ **mac 実機が要るのは F-4 だけ**である（★ 判断 53 で一次資料から判定した）。
> ★ **F-4 は先に `next-session-mac-default-clippy.md` を mac で回してから**着手すること。

---

## ✅ 2026-09-12 の結果（★ **F-1 / F-2 / F-3 / F-5 は決着。残りは F-4 だけ**）

| | 結果 | main |
|---|---|---|
| **F-1 + F-2** | ✅ `.github/workflows/supply-chain.yml` を新設（3 層を 1 job・**週次 schedule**） | PR **#197** → `6239d5b` |
| **F-3** | ✅ **裁定 = 足さない**（⚠️ lint 結果は互いに上位集合でないので片側追加では非対称が消えない） | — |
| **F-5** | ✅ `ci.yml` **top-level** に `permissions: contents: read` | PR **#196** → `757b663` |
| ⚠️ **F-4** | ⚠️ **未着手**（★ **mac 先行が必須** → `next-session-mac-default-clippy.md`） | — |

★ 実体は `.steering/20260912-followups-f1-f5/decisions.md`（**D1〜D15**）にある。

### ⚠️★★★ 次に読む人が取り違えやすい 4 点

1. ⚠️ **`cargo audit` は導入前からすでに赤だった**（vulnerability 3 件）。
   ★ 確かめずに CI へ足していたら新 job は**初日から赤**。→ `h2` を 0.4.19 へ、
   `quick-xml` の 2 件は**期日つき**で明示除外（★ `plist` ← `tauri` 経路で semver 内に解が無い）。
2. ⚠️★★★ **`cargo update -p <crate>` は指定した crate 以外も書き換える。**
   ★ 実測: `-p h2` が **7 crate の `windows-sys` を巻き戻した**（`--dry-run` は予告しない）。
   → ★ **必ず `git diff` を見て最小差分に絞る**。
3. ⚠️★★★ **`cargo audit` を直接叩かない。** ★ 除外した advisory は**出力から跡形もなく消える**
   （件数すら出ない）。→ `scripts/check_dependency_audit.py` 経由で回すこと
   （★ 除外 ID を毎回印字し、**stale / 期日切れを赤にする**）。
   ⚠️ **`$CARGO_HOME/audit.toml`（個人設定）も効く**ので、ラッパーは `CARGO_HOME` を隔離し
   実行後に検算している。
4. ⚠️ **`main` に branch protection が無い**（実測 404）。→ ★ 新 job は**門ではなく信号**。
   赤を見たら人が動くこと。

### ★ 新しい申し送り（F-8 / F-9）

| # | 事項 | 状態 |
|---|---|---|
| **F-8** | ⚠️ **GitHub Actions の版が可動タグのまま**（`actions/checkout@v4` 等）。★ `ci.yml` は self-hosted で走る job があり SHA ピンの follow-up が既に記録済み。`supply-chain.yml` は **hosted 限定なので対象外**と理由を書いた | ⚠️ **未決**（★ 研究者裁定） |
| **F-9** | ⚠️ **workflow の構文検査（actionlint 等）が無い**。★ 今回は「供給網の PR で新しい第三者 action を増やすのは本末転倒」として採らなかった（D15） | ⚠️ **未決** |

### ★ 運用で覚えておくこと

- ⚠️ `/cross-review` は `GH_TOKEN: ${{ secrets.GITHUB_TOKEN }}` の 1 行で
  **secrets-filter に必ず当たる**（★ `gh_token` パターンの構造的 over-block）。
  → ★ 該当行を人が確認したうえで `--ack-filtered`（⚠️ 自動では付けない）。
- ★ 手元での供給網点検は `docs/verification-runbook.md` **§1 (g)** に 3 本ある
  （⚠️ **repo 直下から**回すこと）。

## §0 ⚠️ 前提（★ 2026-09-12 に終わったこと）

★ R-2〜R-5 は**全て決着済み**で、**PR #193 / #194 / #195 が main に入っている**。

| | 結果 | main |
|---|---|---|
| **R-2** | toolchain を `rust-toolchain.toml` で **1.98.1** に固定 | `a5960b9` |
| **R-3** | `rust-version` を **1.88** へ訂正（⚠️ `1.87` は誤りだった） | `2bcf35d` |
| **R-4** | 無音 skip を `panic!` へ ＋ CI に env 前提の検査 step | `2bcf35d` |
| **R-5** | ✅ **閉じた**（`run-codex-review.sh` が 3 回連続成功・台帳が自動計上） | — |
| **F-6** | ✅ **裁定済み** —— `.codex/budget.json` の上限 **300,000 は据え置く**（判断 52） | — |

⚠️★★★ **蒸し返さないこと**: ★ R-2 の「固定するか否か」／固定先の版／`targets` を書くか／
`@stable` を残すか は**全て決着済み**（決定 1 / 3 / 5・判断 31〜35）。

## §1 ★ やること（F-1〜F-5）

### ⚠️★★★ F-1: toolchain 由来の advisory を検知する手段（★ **最優先**）

- ⚠️ **security-checker と Codex が *独立に* 同じ点を挙げた**（判断 39 / 50）。
- ★ **問題の構造**（⚠️ ここを取り違えない）:

  | 層 | 固定の仕方 | 検知手段 |
  |---|---|---|
  | 依存 crate（630 個） | `Cargo.lock` に **checksum 付き** | ★ RustSec / `cargo audit` が射程 |
  | ⚠️ **toolchain**（rustc / std / **cargo** / clippy） | ★ 名前のみ（ハッシュなし） | ⚠️★★★ **射程外** |

- ⚠️ **「`cargo audit` を入れれば足りる」は成立しない** —— ★ cargo-audit は `Cargo.lock` の
  依存しか見ず、**toolchain 同梱の cargo は見ない**。⚠️ RustSec DB に `std` の advisory は
  **1 件も無い**（★ rust-lang/rust の repo advisory にしか無い）。
- ★ **頻度の実像**（一次: `gh api /repos/rust-lang/rust/security-advisories`・約 7 年で **6 件**）:
  ⚠️★★★ **唯一の critical（CVE-2024-24576 / `std::process::Command` の Windows 引数エスケープ）が
  GSE の製品コード 20 箇所のクラスに当たる**（`lib.rs` / `g1.rs` / `bin/submit.rs` / `hook_macos.rs`）。
  → ★ 「低頻度だから無視してよい」ではなく「**低頻度だが当たれば自分のコードに当たる**」。
- ★ **現在の緩和**: `rust-toolchain.toml` の**版上げ手順 0**（人が advisory を見る）のみ。
- ⚠️ **選択肢**（★ 研究者裁定が要る）:
  1. ★ 現状維持（手順 0 だけ）＋ `docs/verification-runbook.md` に定期点検の行を足す
  2. ⚠️ **非ブロッキングの CI job**（`gh api` で advisory を引いて `channel` と比較）
  3. ⚠️ `cargo-audit` ＋ dependabot（= F-2 と一体で解く）
- ⚠️★★★ **どれを採るにせよ、「回す場所が無い手順は回らない」を思い出すこと**
  （★ 判断 20 の M4 でまさにこれをやった —— `Cargo.toml` のコメントにしか無かった MSRV 検査を
  `docs/verification-runbook.md` §1 (f) へ移した）。

### ★ F-2: `cargo-audit` / dependabot の導入

- ⚠️ **現状 repo に依存脆弱性の検知経路が無い**（実測: `cargo-audit` 未導入 /
  `ci.yml` に audit step **0 件** / `.github/` に dependabot 設定 **なし**）。
- ★ 参考（本タスクで security-checker が実測した既存状態）:
  `npm audit` は **7 件**（high 4 / moderate 1 / low 2）で、⚠️ **全て devDependencies 側**
  （vite / postcss / nanoid / browserslist / esbuild / @babel/core / baseline-browser-mapping）。
  → ★ **被験者に配る Tauri バイナリの実行時経路ではない**。⚠️ ただし「無い」わけではない。
- ⚠️ **F-1 と一体で設計する**（★ 別々に足すと検知手段が 2 系統に割れる）。

### ⚠️ F-3: `stop-check.sh` に `--features package` を足すか

- ★ 現状（実測・`.claude/hooks/stop-check.sh`）:
  `cargo clippy --manifest-path "$MANIFEST" --quiet --all-targets -- -D warnings`
  → ⚠️ **`--features package` が無い**ので、CI（付き）とローカル（無し）で**範囲が非対称**。
- ★ **Windows 実機の実測**（2026-09-12・warm・1.98.1）:

  | 形 | exit | 所要 |
  |---|---|---|
  | `--all-targets`（現状） | **0** | **10s** |
  | `--all-targets --features package`（CI と同じ） | **0** | **14s** |

  → ★ **増分は約 +4 秒/Stop**（⚠️ warm の話。★ cold はもっと掛かる）。
- ⚠️★★★ **mac 側のコストは Windows から測れない** —— ★ hook は**作業している機械**で走る。
  → ⚠️ mac で作業する頻度が高いなら、**mac でも同じ 2 本を測ってから決める**。
- ★ **判断の軸**: 非対称を消す価値 ⇔ 毎 Stop の +4 秒（★ age / reqwest の再解析）。

### ⚠️★★★ F-4: default features のみの clippy を CI に足す（★ **mac 先行が必須**）

- ★ 実測: CI の clippy は **`ci.yml:559` の 1 箇所だけ**で **`--features package` 付き**。
  → ⚠️ **default features のみの clippy は CI に存在しない。**
- ★ **Windows は緑**（2026-09-12 実測: `cargo clippy --all-targets -- -D warnings` → **exit 0**）。
- ⚠️★★★ **mac は未検証である。** ★ mac セッションが測ったのは
  `--all-targets --features package --target aarch64-apple-darwin` であって、
  ⚠️ **`--features package` を外した形ではない**。
  ⚠️ ローカル `stop-check.sh` は default features で回る**が `WARN` を出すだけでブロックしない**
  → ★ **mac 側で警告が出ていても誰も気づかない構造**。
- → ⚠️★★★ **緑を確かめずに CI へ足すと main が即赤になり全作業が止まる。**
  ★ これは **R-1 で学んだ順序そのもの**（① mac で緑にする → ② CI に足す）。
  → **`next-session-mac-default-clippy.md` を先に回すこと。**

### ★ F-5: `check` 等に `permissions: contents: read` を明示する

- ★ 実測（`ci.yml` を yaml でパースして確認）:

  | job | `permissions:` |
  |---|---|
  | `frontend-check` | ✅ `contents: read` |
  | `release` | ✅ `contents: write` |
  | ⚠️ `decide-win-runner` / `check` / `build-windows` / `build-macos` | ⚠️ **無し（4 job）** |

- ⚠️ **本タスクが作った穴ではない**（★ 既存）。⚠️ ただし `check` は **self-hosted 実機**で走るので、
  既定の広い権限のままにしておく理由も無い。
- ★ **最も安い変更**であり、⚠️ **F-1〜F-4 と独立**なので単独 PR で先に片付けてよい。

## §2 ⚠️ この repo の作法（★ 本タスクで効いたもの）

- ⚠️★★★ **「実測した」と書くときは *どの環境で* 測ったかを必ず併記する。**
  ★ 本タスクで **3 回**踏んだ ——（a）`bash → bash` の結果を CI の `pwsh → git-bash` に当てはめた
  （b）本機の `stable` を見て「CI も同じ版」と決めつけた（c）SSOT の一覧を実績と照合せず写した。
  → ★ **CI について論じるなら CI の run ログが唯一の一次資料**。手元の値は傍証にすらならない。
- ⚠️★★★ **「何も起きていない」と「成功した」を区別しない判定を書かない。**
  ★ 本タスクで **3 回**踏んだ ——（a）`--exact` の名前間違いで `running 0 tests` / exit 0
  （b）CI 待機ループを `pending == 0` で判定し**未発火を完了と誤読**
  （c）R-4 が直した無音 skip そのもの。
- ★ **レビュー指摘を直したら、直したものを動かして出力を読む。**
  ⚠️ 本タスクで `rustup toolchain install` が **rustup 自身を self-update する**副作用を、
  **誰の指摘にもなく実行して初めて**見つけた（判断 48）。
- ★ **ディスクを語るなら guard 自身の `free before:` 行だけを根拠にする**
  （⚠️ `df -h` と `df -Pk` は食い違う。★ 過去に 1 GiB ずれて予測を外した）。

## §3 ★ 進め方（CLAUDE.md 準拠）

1. ★ `/start-task` を起動する（⚠️ **実装系は必ず先**）。grill で F-1〜F-5 のうち
   **どれを 1 タスクにまとめるか**を確定する（★ F-1 と F-2 は一体・F-5 は独立で安い）。
2. ★ `docs/agent-shared.md` のリンクハブから該当 docs を先読みする。
3. ★ 該当 Skill を Read する（`git-workflow` / `verify-before-claiming` / `architecture-rules`）。
4. ★ レビューは **`code-reviewer` + `security-checker` を並列**起動する。
5. ★ 完了時に **`/cross-review` を必ず回す**（⚠️ **ラッパー `scripts/run-codex-review.sh` を先に試す** ——
   ★ 3 回連続で成功しており、1312 は再現していない。⚠️ パス限定で回すこと）。
6. ⚠️ `.steering/` の記録を省略しない。

## §4 ⚠️ 注意（★ 環境について）

- ★ **本機（G-GEAR）の toolchain は `rust-toolchain.toml` により 1.98.1 に切り替わる**。
  ⚠️ ローカルの `stable` は **1.94.1 のまま古い**（★ 2026-09-12 時点）。
  → ★ repo の外で `cargo` を叩くと **1.94.1 が使われる**ので混同しないこと。
- ★ 本機に残る toolchain: `stable(1.94.1)` / `1.88`（★ MSRV 検査用・消さない）/ `1.94.1` / `1.98.1`。
  ⚠️ `1.87` は 2026-09-12 に削除済み。
- ★ MSRV 検査は `docs/verification-runbook.md` §1 **(f)** に手順がある
  （⚠️ **依存を更新した回だけ**回す。★ 継続検査する CI job は**無い** = 研究者裁定）。
