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

## 実行セッション（★ 新セッションで行う・2026-09-27 完了）

- [x] 基盤検証: `bash scripts/loop-run.sh .steering/20260927-precondition8-t3-and-consent --issues 004`
      → issue_done (attempt 1)
- [x] ウェーブ 1: 001 / 002 / 005（★ 実際は loop-run.sh の progress フラグの不具合で 005 が
      2 回黙って `blocked（依存 issue が未完のため未実行）`にされた——005 は `## Dependencies: なし`
      で実際には無関係。003 系の attempt が失敗した同バッチで progress=0 になり、while ループが
      無関係な 005 ごと打ち切っていた。手動で `--issues 005` 単独実行して解消。issue_done (attempt 1)）
- [x] ウェーブ 2: 003（依存 001 / 002 / 004）
      → ★ issue-plan の DAG は「issue 完了」と「base へのマージ」を別ものとして設計していたが
      （003.md 逐語「上の 3 本が**この作業ブランチに入ってから**実行する」）、loop-run.sh は
      issue 間で自動マージしないため、オーケストレータ（本セッション）が手動で
      `git merge --no-ff loop/00{1,2,4}-issue` を base へ実施してから 003 を再実行する必要があった。
      003 自身は自己ブロック→再実行で `no_progress_stop`（4 attempt とも実装は正しいが
      `check-g1-collection-readiness.sh --selftest` の実行に 120 秒超かかり commit に届かず）。
      worktree の未コミット差分をオーケストレータが独立検証（acceptance 25/25 green・pinned verify
      green）した上で Status/Execution Result のみ代行しコミット。詳細は issues/003.md 末尾。
- [x] `/loop-status` は今回未使用（board 確認より events.jsonl 直読みで代替。単一書き手の原則は維持）
- [x] 全 issue base へマージ済み → TASK-POST `code-reviewer`（Opus）/ `security-checker` 並列 ＋
      `codex-review`（budget.json 記帳済み）を実施。**確認した指摘 9 件を修正**（詳細は
      `fix(g1): TASK-POST レビュー...` コミット・`fix(g1): started_incomplete...` コミット）:
      - HIGH（確定・実行時クラッシュ）: `analyze.py` の `analysed_m` 抽出が TypeError
      - HIGH（確定・fail-open・3 系統一致）: `bool(rc.get("closed"))` の型緩さ
      - MEDIUM-HIGH（確定・issue 003/004 間の内部矛盾）: g1-deletion-ledger.md §2 が「やめた」と
        「削除の求め」を混同
      - MEDIUM（確定）: A-8 tombstone の非対称・理由の誤記／T3 の古い参照／005-acceptance.sh の
        staged 変更見逃し／consent-diff-proposal.md の migrateConsentForm 是正経路欠落／
        validate_blocks.py の「途中の穴」検出力喪失
      - 見送り（false positive 判定）: Codex 指摘「§5 実施記録の commit が decisions.md 判断1と
        矛盾」→ 判断1 は config.json（公表物）が対象で削除台帳（内部監査記録）には及ばない。
        既存 `docs/o1-deletion-ledger.md` が同じパターンを既に採用（security-checker が
        独立に「受容済みリスク」と裏付け）
- [x] `bash scripts/check-g1-collection-readiness.sh --selftest` を main（base）チェックアウトで
      複数回実施（マージ直後・レビュー修正後の 2 回とも green・42/42）
- [ ] `/finish-task`（★ retrospective ＋ push → PR → CI 緑なら merge）

## 研究者に渡すもの（★ Loop では完了しない）

- [ ] `consent-diff-proposal.md` の**承認と反映**（⚠️ 3 文書同時・`migrateConsentForm()` は実行しない）
- [ ] T3 台帳の**実物の作成**とダミー P-ID での赤/黄/緑の実測（★ 別タスク・Chrome・要同席）
- [ ] G1 の**保管上限の数値**（★ 台帳は `g1-retention: unset` で起票する）
- [ ] 記録票 A / B / C の記入（G1 ゲートの残り未達 3 件）
- [ ] O1 リリースタグの更新（★ 本タスク範囲外・ゲート未達 2 件のうち 1 件）
