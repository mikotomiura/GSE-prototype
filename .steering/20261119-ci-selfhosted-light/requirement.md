# CI を研究者の機械で軽く回す（Windows の check を G-GEAR へ戻す）

## 背景

- 2026-11-19、PR #428（手跡の Windows 版）の hosted のジョブ（Windows の check・frontend-check・audit）が「支払いの失敗か使用額の上限」で始まらなかった。GitHub Pro の Actions の無料分（月 3,000 分）を使い切った。
- 主な原因: 2026-11-05 に研究者の判断で変数 `GSE_WIN_FORCE_HOSTED=1` を置き（`.steering/20261105-ci-win-force-hosted/`・G-GEAR が別の計算で忙しいため）、Windows の check を `windows-latest`（分の消費が 2 倍）で回していた。
- G-GEAR の runner（`g-gear-win-x64`）は、GitHub がしばらく使われていない登録を自動で消したため 11-17 から落ちていた。2026-11-19 に研究者が登録し直した（online・`gse-win`）。
- 研究者の決定（2026-11-19）:
  - Windows の check を G-GEAR に戻し、CI の処理の優先度を下げる（研究者の作業が先に CPU を取る）。
  - frontend-check は self-hosted に移さず、無料分が戻るまで待つ。
  - audit は hosted のまま（`check_workflow_invariants.py` の HOSTED_ONLY・実機に復号の鍵がある）。
- push（`feature/*`）と PR で同じ CI が 2 回走り、G-GEAR の Windows で直列に待っていた（memory・10-09）。

## ゴール

- self-hosted（G-GEAR・Mac）の `check` で、ジョブの処理（cargo とその子）が通常より低い優先度で走る。
- `feature/*` への push では CI を走らせない（main への PR と main への push で走る）。
- 変数 `GSE_WIN_FORCE_HOSTED` を消し、Windows の check が G-GEAR で走る。

## スコープ

- やる: `.github/workflows/ci.yml` の check の頭に優先度を下げる段と確かめの段・push の枝・docs の記述・変数の削除。
- やらない: frontend-check・audit を self-hosted へ移すこと。使用額の上限の変更。`CARGO_BUILD_JOBS` の変更（既に 2）。

## 受け入れ条件

- [ ] `check_workflow_invariants.py`（--self-test・本検査・unittest）が緑
- [ ] 実際の run で、G-GEAR の check のログに `Runner.Worker (...) -> BelowNormal` と、後の段の優先度が `BelowNormal` であることが出る
- [ ] 同じく Mac の check で `nice 10` が出る
- [ ] G-GEAR と Mac の check が緑

## 運用メモ
- /reimagine 適用: No
- 理由: CI の設定の小さな変更で、方針は研究者が決めた（2026-11-19）
