# タスクリスト

## 分解セッション（2026-09-27・Opus・本セッションで完了）

- [x] `git pull --ff-only`（main = `35c1e48`・Already up to date）
- [x] 作業ブランチ `feature/precondition8-t3-and-consent` を切る（★ main に直接コミットしない）
- [x] 一次資料を読む（第 20 版 9 マス / §3.9 / §2.13-1b / `validate_blocks.py:229-245` /
      `analyze.py:180-215, 590-594, 701-704, 874-908` / `o1-deletion-ledger.md` / `consent.md` /
      `GSE_G1_Form_Builder.gs:225-308` / `t3-person-ledger-design.md` / `t2-record-a-draft.md`）
- [x] ゲートを測り直す（O1 = 通過 22/未達 2・G1 = 通過 17/未達 3）
- [x] `verify` のベースライン緑を実測（selftest 2 本 / py_compile / bash -n）
- [x] grill（判断分岐 8 件を研究者裁定で閉じた → `decisions.md`）
- [x] `docs/glossary.md` に確定用語 5 件を追記
- [x] `requirement.md` / `design.md` / `decisions.md`
- [x] issue 5 本 ＋ acceptance 5 本 ＋ `_issue-plan.md` ＋ `_loop-config.json`
- [x] コミット `d03b517` ＋ push（★ **PR はまだ出さない** —— この枝が loop の `base_branch` であり、
      各 issue はここへ merge される。main への PR は `/finish-task` で出す）
- [ ] （任意）TASK-PRE: `codex-consult` で issue の独立性に第二意見（`docs/loop-engineering.md` Codex ゲート）
- [ ] ⚠️★★★ **`/clear` して新セッションで実行を始める**

## 実行セッション（★ 新セッションで行う）

- [ ] 基盤検証: `bash scripts/loop-run.sh .steering/20260927-precondition8-t3-and-consent --issues 004`
- [ ] ウェーブ 1: 001 / 002 / 005
- [ ] ウェーブ 2: 003（依存 001 / 002 / 004）
- [ ] `/loop-status` で board を確認（★ 単一書き手）
- [ ] 全 issue 緑 → TASK-POST `/cross-review` ＋ `code-reviewer` / `security-checker`
- [ ] `bash scripts/check-g1-collection-readiness.sh --selftest` を main チェックアウトで回す
- [ ] `/finish-task`（★ retrospective ＋ push → PR → CI 緑なら merge）

## 研究者に渡すもの（★ Loop では完了しない）

- [ ] `consent-diff-proposal.md` の**承認と反映**（⚠️ 3 文書同時・`migrateConsentForm()` は実行しない）
- [ ] T3 台帳の**実物の作成**とダミー P-ID での赤/黄/緑の実測（★ 別タスク・Chrome・要同席）
- [ ] G1 の**保管上限の数値**（★ 台帳は `g1-retention: unset` で起票する）
- [ ] 記録票 A / B / C の記入（G1 ゲートの残り未達 3 件）
- [ ] O1 リリースタグの更新（★ 本タスク範囲外・ゲート未達 2 件のうち 1 件）
