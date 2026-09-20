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

## 実装
- [ ] 記録票 `collection-readiness-record.md` を新規作成（⚠️ 空欄のまま）
- [ ] `scripts/check-g1-collection-readiness.sh` — 検査 [1]〜[8]
- [ ] `--selftest`（変異試験・検査ごとに 1 つ以上の `expect_red`）
- [ ] `run.sh` の結びに導線を 1 行
- [ ] `docs/verification-runbook.md` §1 に項を追加

## 検証
- [ ] `bash scripts/check-g1-collection-readiness.sh` を実行し、**赤**であること・理由が読めることを実測
- [ ] `bash scripts/check-g1-collection-readiness.sh --selftest` が **exit 0** であることを実測
- [ ] `bash scripts/check-shell-portability.sh` が緑
- [ ] ゴールデン 6 本の所要時間を実測して記録

## レビュー
- [ ] `code-reviewer`（opus）＋ `security-checker`（opus）を並列（★ 範囲と禁止事項を明記）
- [ ] `/cross-review` 2 巡（パス限定）
- [ ] `/finish-task`
