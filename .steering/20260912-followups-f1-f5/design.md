# design — 申し送り F-1 / F-2 / F-3 / F-5

## アプローチ

★ **検知経路を 1 か所に置く**。⚠️ 依存層と toolchain 層を別々に足すと 2 系統に割れるので、
**単一の workflow** に集め、**同じ script を人も手元で回せる**形にする
(⚠️ 「回す場所が無い手順は回らない」= 判断 20 M4 の教訓)。

## 変更対象

### PR-A (F-5) — `ci.yml` の権限

| ファイル | 変更 |
|---|---|
| `.github/workflows/ci.yml` | ★ **top-level** に `permissions: contents: read` を置く |

⚠️★★★ **なぜ「4 job に個別付与」ではなく top-level なのか**: ★ 直したい失敗様式は
「**job を足したとき permissions を書き忘れ、repo 既定の広い権限を継ぐ**」である。
個別付与は**今ある 4 job しか直さない**が、top-level は**今後足す job も既定で最小**になる。
★ 既存の 2 job (`frontend-check` = `contents: read` / `release` = `contents: write`) は
job 側の宣言が top-level を**上書きする**ので挙動は変わらない。

★ **`contents: read` で足りる根拠** (⚠️ 実測 = `ci.yml` を読んで使用 action を全数列挙した):
`actions/checkout` / `dtolnay/rust-toolchain` / `Swatinem/rust-cache` / `actions/setup-node` /
`actions/upload-artifact` / `actions/download-artifact` / `./.github/actions/disk-guard` /
`softprops/action-gh-release` (★ `release` のみ・既に `contents: write`)。
⚠️ artifact と cache は **Actions ランタイムトークン**を使い `GITHUB_TOKEN` を使わない。
★ `decide-win-runner` の `gh api .../actions/runners` は **`secrets.RUNNER_STATUS_TOKEN` (別 PAT)**
を使っており (`ci.yml:196`)、`permissions:` の影響を受けない
(⚠️ そもそも `GITHUB_TOKEN` では取得できないと `ci.yml:137` に実測が記録されている)。

⚠️★★★ **検証の限界を先に書く**: ★ `build-windows` / `build-macos` / `release` は
`if` により **tag push か `workflow_dispatch` でしか走らない**。
→ ⚠️ **通常の PR 実行では検証できない**。★ そこで **`workflow_dispatch` をブランチ指定で発火**し、
`build-windows` を実機で緑にしてからマージする (⚠️ tag を選ぶと Release ができるので**ブランチを選ぶ**)。

### PR-B (F-1 + F-2) — supply-chain 検知

| ファイル | 変更 |
|---|---|
| `scripts/check_toolchain_advisories.py` | ★ **新規**。`rust-toolchain.toml` の `channel` と rust-lang/rust advisory を突合 |
| `scripts/tests/test_check_toolchain_advisories.py` | ★ **新規**。unittest (★ repo の既存作法) |
| `.cargo/audit.toml` | ★ **新規**。⚠️ 修正不能な advisory の**明示的な**除外 + 根拠 + 再点検期日 |
| `src-tauri/Cargo.lock` | ⚠️ `h2` 0.4.15 → **0.4.19** (RUSTSEC-2026-0258 の修正) |
| `.github/workflows/supply-chain.yml` | ★ **新規**。3 層を 1 job で検査 |
| `rust-toolchain.toml` | ★ 版上げ手順 0 を script 呼び出しへ差し替え |
| `docs/verification-runbook.md` | ★ §1 に (g) を追加 |

## 設計判断

### D1: 別 workflow ファイルにする (`ci.yml` に足さない)

★ `schedule:` を `ci.yml` に足すと、⚠️ **ci.yml の全 job が週次で発火**してしまう
(`check` / `build-macos` は **self-hosted 実機**)。各 job に `if` を足して抑えるのは
⚠️ 既に複雑な `if` 群をさらに複雑にする。→ ★ **`supply-chain.yml` を独立させる**。

### D2: 発火条件

- `schedule` (週次) — ★ **これが「回す場所」**。⚠️ 新しい advisory はコード差分ゼロで現れるので、
  PR 発火だけでは永久に気づかない。
- `workflow_dispatch` — ★ 人が今すぐ確かめたいとき。
- `pull_request` (⚠️ **paths 限定**: `Cargo.lock` / `rust-toolchain.toml` / `package-lock.json` /
  本 workflow / 本 script) — ★ 依存や toolchain を動かした PR でその場で分かる。

### D3: ⚠️★★★ 「非ブロッキング」は設定で作らない —— **既に構造的に成立している**

★ 実測 (2026-09-12): `gh api repos/mikotomiura/GSE-prototype/branches/main/protection`
→ **`404 Branch not protected`**。⚠️ つまり **required check は 1 つも無く**、
本 job が赤でもマージは機械的には止まらない。
→ ★ `continue-on-error` を**書かない** (⚠️ 書くと「赤」が「緑」に見え、信号が消える)。
★ 本 job の役割は **門ではなく信号**である。

### D4: ⚠️ 3 層をどう検査するか (★ 各層で「何件を検査したか」を出力に出す)

| 層 | 手段 | ★ 緑の条件 |
|---|---|---|
| toolchain (rustc / std / cargo) | `scripts/check_toolchain_advisories.py` | ★ `channel` が全 advisory の範囲外 |
| Rust 依存 630 crate | `cargo-audit audit --file src-tauri/Cargo.lock` | ★ vulnerability 0 件 (⚠️ warning は既定どおり赤にしない) |
| フロント npm | `npm audit --omit=dev` | ★ **本番依存**のみを門にする |

⚠️★★★ **npm の dev 依存 7 件を門にしない理由**: ★ 実測で `vite` / `postcss` / `nanoid` /
`browserslist` / `esbuild` / `@babel/core` 由来であり、**被験者に配る Tauri バイナリの
実行時経路ではない**。⚠️ ただし「無い」ことにはしないので、**全体の `npm audit` を
情報として出力し、`--omit=dev` だけで exit code を決める**。

### D5: ⚠️ 現状が赤なので、足す前に緑にする (★ R-1 と同じ順序)

⚠️★★★ **実測 (2026-09-12・cargo-audit 0.22.2・本機): `exit 1` / vulnerability 3 件**。
★ 確かめずに CI へ足していたら **新 job は初日から赤**だった。

| ID | crate | 経路 (★ `cargo tree` で実測) | 扱い |
|---|---|---|---|
| RUSTSEC-2026-0258 | `h2 0.4.15` | `reqwest` ← ⚠️ **`--features package` のみ** = `gse-submit` | ★ **直す** (`cargo update -p h2` → **0.4.19**・semver 互換) |
| RUSTSEC-2026-0194 | `quick-xml 0.38.4` | `plist 1.8.0` ← `tauri 2.10.2` (⚠️ **macOS 経路**) | ⚠️ **直せない** → 明示除外 |
| RUSTSEC-2026-0195 | 同上 | 同上 | ⚠️ **直せない** → 明示除外 |

★ `quick-xml` が直せない根拠 (実測): ⚠️ 修正版は **0.41.0** で、`plist 1.8.0` が
`0.38` を要求しているため `cargo update -p quick-xml` は **`Locking 0 packages`** を返す
(= semver 内に解が無い)。→ ★ **上流 (tauri / plist) が上げるまで待つしかない**。

⚠️★★★ **除外は「無音 skip」ではない**。★ `.cargo/audit.toml` に **ID / 理由 / 再点検期日**を
書き、⚠️ **`cargo-audit` の出力に "N advisories ignored" として毎回現れる**
(= 判断: R-4 で `panic!` に変えたのと同じ「黙らせない」原則)。
★ 露出評価も書く: 当該 advisory は **未信頼 XML に対する二次関数的処理時間 (DoS)** であり、
GSE が `plist` に渡すのは**自前バンドルの `Info.plist`** で被験者入力ではない。

### D6: ★ script の「空振り」を構造的に封じる

⚠️ 判断: 本タスクの受け入れ条件は「exit 0」**ではない**。
★ script は必ず **検査した advisory を全件表 (HIT / ok) で出力**し、件数を出す。
⚠️ `channel` が `stable` / `nightly-*` など**版として読めない値**のときは
**exit 0 にせず失敗させる** (★ 「比較できなかった」を「安全」と読み替えない)。
★ `--self-test` と `scripts/tests/test_*.py` で **当たる版が本当に赤になること**を固定する。

## テスト戦略

| # | 検査 | 期待 |
|---|---|---|
| T1 | `python3 scripts/check_toolchain_advisories.py --self-test` | exit 0・⚠️ 変異ケースが全て意図どおり |
| T2 | `python3 -m unittest scripts.tests.test_check_toolchain_advisories` | exit 0 |
| T3 | 実データで `check_toolchain_advisories.py` (channel=1.98.1) | exit 0・★ **6 件検査したと出力に出る** |
| T4 | ⚠️ 変異: `--channel 1.88.0` | **exit 1** (CVE-2025-11233 に当たる) |
| T5 | ⚠️ 変異: `--channel 1.76.0` | **exit 1** (★ critical CVE-2024-24576 に当たる) |
| T6 | ⚠️ 変異: `--channel stable` | **exit 2** (★ 比較不能を緑にしない) |
| T7 | `cargo-audit audit --file src-tauri/Cargo.lock` (h2 更新後) | **exit 0** |
| T8 | `npm audit --omit=dev` | 0 件 |
| T9 | ⚠️ `Cargo.lock` 更新後の**ゴールデン回帰** `gse-replay --snapshot` | byte-equal |
| T10 | `cargo test --workspace` / `cargo clippy -D warnings` / `cargo fmt --check` | 緑 |
| T11 | ⚠️ MSRV 検査 (runbook §1 (f)) —— ★ **依存を更新したので回す** | 緑 |
| T12 | `ci.yml` を yaml パースし **全 job が実効 permissions を持つ**ことを確認 | 緑 |
| T13 | ★ PR-A / PR-B の **CI run ログを読む** | ⚠️ 「緑」ではなく**検査件数**を確認 |
| T14 | ★ PR-A で **`workflow_dispatch` (ブランチ指定)** を発火し `build-windows` を緑にする | 緑 |

## レビュー

- `code-reviewer` + `security-checker` を**並列**起動。
- `/cross-review` (★ `scripts/run-codex-review.sh` を先に・パス限定)。

## 却下した案

- ⚠️ **dependabot 導入**: ★ 検知は本 workflow に一本化するので重複。⚠️ 2-3 人チームに
  自動更新 PR のノイズが勝る。★ ただし **GitHub Actions の版固定**は別論点として申し送る。
- ⚠️ **`ci.yml` に audit step を足す**: ★ D1 のとおり `schedule` が全 job を巻き込む。
- ⚠️ **`stop-check.sh` に `--features package` を足す (F-3)**: ★ 裁定 = **足さない** (decisions D4)。
