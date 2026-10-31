# 引き継ぎ — 招待の契機と配線（ADR-040 D4・Migration 2・タスク B）

> 作成: 2026-10-31（タスク A の後）。このメモを一次資料にしない。事実はコード・ADR・decisions で確かめ直す。

## 0 前提

- ADR-040 は main に入っている（PR #369）。
- タスク A（Nudge の既定の無効化）は `feature/nudge-default-off`（worktree `/Users/johnd/GSE-prototype-nudge-off`）でローカルにコミット済み（a39cf2a5・c1e280e8）。**未 push**: ci.yml は `feature/*` の push でも CI を起動し、G-GEAR が重い計算をしている間は載せないため。push と PR は研究者が G-GEAR の空きを言ってから。記録は `.steering/20261031-nudge-default-off/`。
- タスク B はタスク A の上（`feature/nudge-default-off` の先端）から切るか、A が main に入ってから origin/main から切る。どちらにするかは始める時の状況で決める（A が未マージなら A の上から）。

## 1 研究者が決めたこと（2026-10-31・AskUserQuestion）

1. 招待を出す範囲: **通常のモードでは出す・O1 では出さない**・EH3 は今のまま。
   - O1 は同意文書に介入が出る旨が無い（判断 O1-5）ので出さない。
   - 通常のモードの出し方は EH3 と同じ既定（`invitation.rs` の `Settings::default` = 出す・終日・1 日 2 回）で、本人が設定で変えられる（ADR-035）。
   - 第1週の盲検較正では出さない（推定への応答を混ぜない）。この点は私の推奨の説明に含めて研究者が選んだ。実装の前に第2週の扱いも含めて確かめる。
2. 契機の既定: **今の挙動のまま**（`p_stuck ≥ 0.60` が 30 秒）。`friction_rising` と頻度を合わせた無作為の時刻は、注入できる・選べる契機として足すだけ。EH3 の挙動は変えない（事前登録が未凍結・`experiments/20261011-portrait-eh3/`）。

## 2 やること（ADR-040 Migration 2）

1. `friction_rising` の契機を足す（値は注入できる形・既定では使わない）。
2. 頻度を合わせた無作為の時刻で出す条件を足す（判断 14）。
3. 通常のモードの配線（上の 1）。記録は session_meta と別の行で、条件（推定器 / 無作為 / なし）と推定器の版が後から分かるようにする。
4. 新しい契機を `gse-replay` で記録から再現できるようにする（時機のオフライン評価）。

## 3 守ること

- 招待は応答を入力に持たない（ADR-033）・本人の統制（ADR-035）・EH3 を壊さない。
- `/start-task` から。完了時は `/cross-review`。push は G-GEAR の空きを確かめてから（docs だけなら `[skip ci]` の道がある。コードを含むなら研究者に聞く）。
- Skill: `architecture-rules`・`rust-standards`・`typescript-standards`・`intervention-design`・`data-privacy`・`reproducibility-discipline`。HMM の挙動は変えない見込み（変えるなら `HMM_VERSION`）。
