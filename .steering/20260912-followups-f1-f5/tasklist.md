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

- [x] `ci.yml` top-level に `permissions: contents: read` (★ 個別付与ではなく既定を最小化)
- [x] T12: yaml パースで全 job の実効 permissions を検査 (★ 6/6 が保持)
- [x] **PR #196** 作成 → ★ CI 全緑 (⚠️ 予告した 3 点をログで実測: probe が `["self-hosted","gse-win"]` を解決 / `check` は g-gear-win-x64・macbook-air-m-arm64 で成功 / `frontend-check` 不変)
- [x] ⚠️ T14: `workflow_dispatch` (**ブランチ指定**) で `build-windows` を実機検証 —— ★ run 34683449467 が
      **success**、⚠️ **artifact 2 本 (windows-portable / windows-tools) のアップロードも成功**
      (= `upload-artifact` が `actions: write` を要らないことを**推定ではなく実測**で確認)。
      ★ `build-macos` は tag ref 必須なので予定どおり skip = **mac 実機は無傷**
- [ ] ⚠️ **残る未検証**: `build-macos` (★ tag でしか走らない)。⚠️ ただし使用 action の集合は
      `build-windows` と同一で、そちらが緑になったので残存リスクは小さい。`release` は
      job 側の `contents: write` のままで**本変更の影響を受けない**
- [ ] main へマージ

## Phase 2: PR-B = F-1 + F-2 (supply-chain 検知)

- [x] `scripts/check_toolchain_advisories.py` (★ `--self-test` 付き)
- [x] `scripts/tests/test_check_toolchain_advisories.py` (17 件)
- [x] T1〜T6 すべて合格 (★ 実データで 6 件検査 / ⚠️ 変異 `1.88.0`→exit 1・`1.76.0`→exit 1・`stable`→exit 2)
- [x] ⚠️★★★ `cargo update -p h2` が **7 crate の `windows-sys` も巻き戻した** → **h2 の 2 行だけ**を当て直し `cargo metadata --locked` で検算 (D6)
- [x] `.cargo/audit.toml` (★ 理由 + 依存経路 + 再点検期日 2026-12-12)
- [x] T7: **exit 0** (★ 630 crate / 2 件 waived / 0 stale)
- [x] ⚠️★★★ **cargo-audit が除外を黙って消す**ことを実測 → `scripts/check_dependency_audit.py` (+ unittest 17 件) を追加 (D7)
- [x] ⚠️★★★ 変異テストが**実バグ**を露出 (cp932 の `UnicodeEncodeError` が exit 1 を偽装) → UTF-8 強制 (D10)
- [x] T9: ゴールデン **6 本すべて byte-equal** / T11: MSRV 1.88 exit 0 / schema drift なし
- [x] T10: fmt / clippy `--features package -D warnings` / `cargo test --workspace` すべて exit 0
- [x] `.github/workflows/supply-chain.yml` (★ schedule 週次 + dispatch + paths 限定 PR)
- [x] `rust-toolchain.toml` 手順 0 を script へ差し替え (⚠️ 旧コマンドは git-bash で動かなかった・D11)
- [x] `docs/verification-runbook.md` §1 (g) 追加
- [ ] PR 作成 → ⚠️ T13: **CI run ログで検査件数を確認**
- [ ] main へマージ

## Phase 3: レビューと後片付け

- [ ] `code-reviewer` + `security-checker` を**並列**起動 → 反映
- [ ] `/cross-review` (★ ラッパー優先・パス限定)
- [ ] `decisions.md` を最終化
- [ ] ⚠️ `_handoff/next-session-followups-f1-f5.md` に結果を追記 (★ F-4 だけ残ることを明記)
- [ ] ⚠️ 未マージの `docs/handoff-followups-f1-f5` ブランチ (`1b8f500`) の扱いを研究者に確認
- [ ] `/finish-task`
