# タスクリスト: R-2〜R-5 (✅ **完了**)

## Phase 0: grill (✅ 完了)

- [x] 一次資料 3 本を読む (handoff を一次資料にしない)
- [x] 実測 6 件で判断分岐を潰す (design.md の表)
- [x] 研究者裁定を 7 件記録 (decisions.md 決定 1〜7)

## Phase 1: PR-B = **PR #193** — R-3 ＋ R-4 (✅ **main へマージ済み `2bcf35d`**)

### R-3 (✅ 完了)
- [x] `cargo +1.87 check --all-targets --features package` を実測 → ⚠️ **exit 101**
- [x] ⚠️ **真の下限を特定** —— `time@0.3.47` 他が **1.88.0** を要求 (`cargo metadata` で全数走査)
- [x] `rust-version` を **1.88** へ訂正 ＋ 注記を全面改訂
- [x] `cargo +1.88 check` → **exit 0** (4m58s)
- [x] ⚠️ 手順を `docs/verification-runbook.md` §1 (f) に恒久化 (★ 回す場所が無い手順は回らない)

### R-4 (✅ 完了)
- [x] `lib.rs` の `else { return; }` → `else { panic!(..) }`
- [x] `ci.yml` `check` job の**先頭**に env 前提の検査 step
- [x] ⚠️★★★ **Windows の空振りを修正** (`pwsh → git-bash` で MSYS2 が `HOME` を合成する)
- [x] ⚠️ 既存の値漏れも修正 (assert の失敗メッセージ ＋ 要素完全一致マスク ＋ `\` 形)
- [x] 変異テスト **6 形態**で実証
- [x] ★ repo 内の裸 `return;` を全数走査 (修正前 1 / 修正後 0・検出器を検算)

### 共通 (✅ 完了)
- [x] fmt / clippy `-D warnings` / test / ゴールデン / schema すべて緑
- [x] code-reviewer + security-checker を**並列**起動 → HIGH 1 / MEDIUM 5 / LOW 4 を反映
- [x] `/cross-review` (★ **ラッパーを先に試した** = R-5 の検証)
- [x] PR #193 → **CI 全緑** → **main へマージ** → main run も success

## Phase 2: PR-A = **PR #194** — R-2 (🔄 **CI 確認中**)

- [x] repo 直下に `rust-toolchain.toml`
- [x] ⚠️★★★ **固定先を 1.98.1 へ訂正** (★ 1.94.1 は本機の値で、CI は 1.98.1 だった)
- [x] `profile = "minimal"` (★ 1.3 GiB のうち 726 MiB が `rust-docs`)
- [x] ⚠️ `targets` はファイルに書かない ＋ ★ **step 側で `--target` を強制**
- [x] ⚠️★★★ **明示 `rustup toolchain install` step を 3 job へ** (★ disk guard より**前**)
- [x] ⚠️ `--no-self-update` (★ 実行して副作用を発見)
- [x] `ci.yml` 3 箇所の注記 (★ `check` を正典・他は 1 行参照)
- [x] 1.98.1 で全ゲート緑 (⚠️ clippy の lint 集合が違うので回し直した)
- [x] code-reviewer + security-checker を並列起動 → **HIGH 4 件**を反映
- [x] `/cross-review` → HIGH 1 件を反映 / FP 1 件を反証
- [x] ⚠️ **初回 CI で見る 4 点**を**事前に PR 本文へ書いてから**実測 → すべて期待どおり
- [ ] 🔄 cross-review 反映後の CI 緑を確認
- [ ] main へマージ (★ 研究者判断)

## R-5 (✅ **閉じた**・PR 不要)

- [x] ラッパー `run-codex-review.sh` が **exit 0** で完走 (★ **3 回連続**)
- [x] **予算台帳が自動計上**された = ラッパー経由の客観証拠
- [x] ⚠️ 切り分け (版差 / 権限差) は**未了**と明記 (★ 3 回とも codex-cli 0.152.1)

## Phase 3: 後片付け (✅ 完了)

- [x] handoff `next-session-mac-clippy-and-ci-gate.md` の失効行を訂正
- [x] ⚠️ `_handoff/README.md` の**同一失効文**も訂正 (★ 索引側の方が読まれる)
- [x] handoff `next-session-r2-r5-decisions.md` に結果表を追加
- [x] 本機の `1.87` toolchain を削除 (★ 約 1.3 GiB 回収・`1.88` は MSRV 検査用に残す)
- [ ] `/finish-task` (★ PR #194 のマージ後)

## ⚠️ 研究者へ申し送り (★ 2026-09-12 に実行機まで裁定済み)

★ **引き継ぎメモは 2 本**:
`.steering/_handoff/next-session-followups-f1-f5.md`（★ Windows / OS 非依存）と
`.steering/_handoff/next-session-mac-default-clippy.md`（⚠️ **mac 実機・F-4 の前提**）。

| # | 事項 | 実行機 | 状態 |
|---|---|---|---|
| **F-1** | ⚠️★★★ **toolchain 由来 advisory の検知手段**（★ **最優先**） | ★ Windows / OS 非依存 | ⚠️ **未決**。★ security-checker と Codex が**独立に**指摘。⚠️ `cargo audit` の射程外で、緩和は「版上げ手順 0 で人が見る」だけ。★ 頻度は約 7 年で 6 件だが、⚠️ **唯一の critical（CVE-2024-24576 / `process::Command`）が製品コード 20 箇所のクラスに当たる** |
| **F-2** | `cargo-audit` / dependabot | ★ Windows / OS 非依存 | ⚠️ **未決**。★ **F-1 と一体で設計する**（⚠️ 別々に足すと検知手段が 2 系統に割れる） |
| **F-3** | `stop-check.sh` に `--features package` | ⚠️ **両機**（★ コストが違う） | ⚠️ **未決**。★ Windows 実測（warm・1.98.1）: **10s → 14s**（+4 秒/Stop）。⚠️ **mac の数字は未測定** |
| **F-4** | default features の clippy を CI に足す | ⚠️★★★ **mac 先行 → Windows** | ⚠️ **未決**。★ Windows は **exit 0**（実測）／⚠️ **mac は未検証**。⚠️ ローカル hook は WARN のみでブロックしないので**気づけない**。→ ★ **R-1 と同じ順序**（① mac で緑 → ② CI に足す） |
| **F-5** | `permissions: contents: read` | ★ Windows / OS 非依存 | ⚠️ **未決**。★ 実測: `frontend-check` / `release` のみ保有、⚠️ **`decide-win-runner` / `check` / `build-windows` / `build-macos` の 4 job に無い**（既存の穴）。★ **最も安く独立** |
| **F-6** | `.codex/budget.json` の上限 300,000 | — | ✅ **裁定済み = 据え置く**（判断 52）。★ 根拠: 履歴 30 日の中央値 **97,558** / ⚠️ **200,000 超が 6 日（20%）** / 本タスク単独で **170,400**。→ ⚠️ 200,000 に戻すと 5 日に 1 日はガードに当たる |
| **F-7** | `git-workflow` Skill の `wall` 残存 | — | ✅ **完了**（**PR #195** → main `f92be8d`）。⚠️ 直す過程で「SSOT の一覧が実績の大半を覆っていない」ことも判明し、**実測表を併記**した |
