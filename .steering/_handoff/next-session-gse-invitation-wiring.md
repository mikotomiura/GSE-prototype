# 引き継ぎ — 招待の配線（ADR-040 Migration 1・2・T1）の残り

> 更新: 2026-11-01（タスク A・B の実装・レビュー 2 巡・研究者の決定まで済み）。このメモを一次資料にしない。

## 0 状態

- ブランチ `feature/nudge-default-off`（worktree `/Users/johnd/GSE-prototype-nudge-off`）。**未 push**（研究者の決定 2026-11-01: 実機の確かめか G-GEAR の空きの後）。
- 記録: タスク A `.steering/20261031-nudge-default-off/`、タスク B `.steering/20261101-invitation-wiring/`（決定とレビューの対応は decisions.md 判断 1〜5）。
- 最後の検証（2026-11-01・d83d0468）: `cargo test --workspace` 1054 passed・0 failed、clippy `-D warnings` 0、tsc 0、emit_schema byte-equal。

## 1 残り（この順）

1. 済み（2026-11-06・AX で私が操作。トレイの後から差し込む項目は今回 AX で読めて押せた）。手順 1〜5 は期待どおり、図像は記録の `invitation_present` で確かめた（目では見ていない）。途中で「設定の窓の × でアプリ全体が終わる」不具合を見つけ、`390dce62`・`7be6a83d` で直した（`.steering/20261106-settings-window-close-quits/`）。通常のモードには終了以外にセッションを止める手段が無く、「← 戻る」は画面だけを戻す（従来どおり）。元の手順: 第 1 週で始めてトレイに「印の説明と設定」が無い → 第 2 週で始めて 2 秒ほど後に項目が出る・押すと設定の窓が開く → 「出さない」にしても項目が残り窓を開ける → 停止で項目が消え、第 1 週で再開しても出ない → 状態表示と終了の項目が崩れない。招待の図像が第 2 週で出ることは、契機を立ちやすくした `~/.gse/invitation_trigger.json`（例 `{"kind":"estimator","p_stuck":0.5,"hold_ms":10000}`）で早く見られる。
2. ~~push の前に `git fetch` し origin/main を取り込む（T3 の d6b1e978 以降）。テストを回し直す。~~ 済み（2026-11-05・`9d49cac2`・origin/main `be9f14de` まで。ソースの重なり 0・衝突は文書 8 ファイル。cargo test 1054 passed・clippy 0・fmt 差分なし・tsc 0・emit_schema byte-equal）。実機の確かめはこの取り込みの後のコードで行う。残りは: G-GEAR が空いているかを研究者に確かめてから push（`feature/*` は self-hosted の CI が走る）。PR も研究者に確かめてから。
3. gse-dataset の schema parity: `schema/current.json` に `InvitationCondition` が増えた。gse-dataset 側の同期は別作業。
4. `_handoff/README.md` の T1 の行を、push の時に更新する。

## 2 未決（研究者・合流で）

- 説明と設定の窓の文（`InvitationSettings.tsx`）は推定器の契機を前提にしている。無作為・なし・上がりを使う前に、文と同意の扱い（盲検か）を決める（decisions.md 判断 3）。
- 通常のモードの同意文書に `invitation_present`・`invitation_condition` が載っているか。
- 契機の中身（T2・T3 の結果を見て・three-parallel-tracks §4）。T3 は「見えない」（`experiments/20261101-focus-leave-before-receipt/notes.md`）。
