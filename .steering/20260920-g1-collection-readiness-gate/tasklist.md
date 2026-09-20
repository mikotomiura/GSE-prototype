# タスクリスト — G1 収集開始ゲート

## 調査（完了）
- [x] 前提条件 1〜7 の逐語を一次で確認（`preregistration.md:43-61` / `:226-234` / `:350-361` / `:69`）
- [x] `run.sh` の宣言と `run_cargo_filter` の実体（2 本だけ）
- [x] 前提条件 1 / 2 のテストが実在することの確認
- [x] 前提条件 3 が未達であることの確認（`consent.md` / `participant-guide.md` に 0 ヒット）
- [x] ゴールデンが 6 本・CI は 1 本しか回していないことの確認
- [x] `build_task_pages.py` の出力先（`pages/` は gitignore 済み）
- [x] Drive 検査スクリプトが**存在しない**ことの確認

## 設計（完了）
- [x] grill で 4 つの判断分岐を閉じる（`decisions.md` 判断 1〜4）
- [x] 実装段階の判断を記録（判断 5〜7）

## 実装（完了・コミット `9b64f52`）
- [x] 記録票 `collection-readiness-record.md` を新規作成（⚠️ 空欄のまま）
- [x] `scripts/check-g1-collection-readiness.sh` — 検査 [1]〜[8]
- [x] `--selftest`（変異試験・22 ケース）
- [x] `run.sh` の冒頭と結びに導線（★ 「この緑は前提条件を見ていない」を明記）
- [x] `docs/verification-runbook.md` §1 に (i) を追加＋合格条件に 1 行

## 検証（★ すべて 2026-09-20 に実測）
- [x] ゲート本体: **exit 1** / 通過 13・未達 6（前提条件 3・7 と記録票 A/B/C）。**5.4 秒**
- [x] `--selftest`: **exit 0** / 22 ケース全通過。**1 分 10 秒**
- [x] ⚠️ **空回りの検算**: 変異なしの fixture で出る ❌ を全部取り、`expect_red` の照合語と
      突き合わせた → **1 件が空回り**（「参加案内…」は変異しなくても出る）と判明し、
      「1 語目だけ足して 2 語目で赤になるか」へ差し替え ＋ 参加案内側の緑の対照を追加
- [x] `bash scripts/check-shell-portability.sh`: **exit 0**（通過 12 / 未達 0）
- [x] `bash run.sh`: **exit 0**（★ 既存の緑を壊していない）
- [x] ゴールデン 6 本の再生: 全本 rc=0（★ ゲート全体で 5.4 秒に収まる）

## レビュー
- [ ] `code-reviewer`（opus）＋ `security-checker`（opus）を並列（★ 範囲と禁止事項を明記）
- [ ] `/cross-review` 2 巡（パス限定）
- [ ] `/finish-task`
