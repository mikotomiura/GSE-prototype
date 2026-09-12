# tasklist — 申し送り F-1 / F-2 / F-3 / F-5

## Phase 0: 調査・裁定 (✅ 完了)

- [x] 一次資料で現状を再実測 (⚠️ handoff を根拠にしない)
- [x] ★ `ci.yml` を yaml パース → `permissions:` 欠落 **4 job** を確認
- [x] ★ `cargo tree` で `--features package` が default の**上位集合**であること (`cfg(not(feature))` 0 件) を確認
- [x] ⚠️ ただし **lint 結果は互いに上位集合でない** (dead_code) → F-4 の前提は正しい
- [x] ★ `gh api repos/rust-lang/rust/security-advisories` → **6 件**・突合可能な `vulnerable_version_range`
- [x] ⚠️★★★ **`cargo-audit` が今日すでに赤** (exit 1 / vulnerability 3 / warning 13) を実測
- [x] ★ `cargo tree` で 3 件の経路を特定 / `cargo update --dry-run` で修正可能性を実測
- [x] ★ `npm audit --omit=dev` = **0 件** / 全体 7 件は全て dev
- [x] ★ `main` に **branch protection 無し** (404) を実測
- [x] ★ `.cargo/audit.toml` (repo 直下) が実際に効くことを実測 (3 → 1 件)
- [x] grill で方式を裁定 (単一 CI job / F-3 は足さない / PR 2 本)

## Phase 1: PR-A = F-5 (`ci.yml` の権限)

- [ ] `ci.yml` top-level に `permissions: contents: read`
- [ ] T12: yaml パースで全 job の実効 permissions を検査
- [ ] PR 作成 → CI 緑
- [ ] ⚠️ T14: `workflow_dispatch` (**ブランチ指定**) で `build-windows` を実機検証
- [ ] main へマージ

## Phase 2: PR-B = F-1 + F-2 (supply-chain 検知)

- [ ] `scripts/check_toolchain_advisories.py` (★ `--self-test` 付き)
- [ ] `scripts/tests/test_check_toolchain_advisories.py`
- [ ] T1〜T6 (self-test / unittest / 実データ / 変異 3 種)
- [ ] ⚠️ `cargo update -p h2` (0.4.15 → 0.4.19)
- [ ] `.cargo/audit.toml` (★ 理由 + 再点検期日つき明示除外)
- [ ] T7: `cargo-audit` が **exit 0**
- [ ] T9: ゴールデン回帰 byte-equal / T11: MSRV 検査
- [ ] T10: fmt / clippy / test 緑
- [ ] `.github/workflows/supply-chain.yml`
- [ ] `rust-toolchain.toml` 手順 0 を script へ差し替え
- [ ] `docs/verification-runbook.md` §1 (g) 追加
- [ ] PR 作成 → ⚠️ T13: **CI run ログで検査件数を確認**
- [ ] main へマージ

## Phase 3: レビューと後片付け

- [ ] `code-reviewer` + `security-checker` を**並列**起動 → 反映
- [ ] `/cross-review` (★ ラッパー優先・パス限定)
- [ ] `decisions.md` を最終化
- [ ] ⚠️ `_handoff/next-session-followups-f1-f5.md` に結果を追記 (★ F-4 だけ残ることを明記)
- [ ] ⚠️ 未マージの `docs/handoff-followups-f1-f5` ブランチ (`1b8f500`) の扱いを研究者に確認
- [ ] `/finish-task`
