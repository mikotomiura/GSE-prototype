# 引き継ぎ —— 設計の整理の後（段 1 の配布までの道筋に沿って進める）

> 作成: 2026-11-03（`.steering/20261103-gse-design-consolidation/` の後）。このメモを一次資料にしない。事実は ADR・地図・decisions.md で確かめ直す。

## 0 決まったこと（一次は decisions.md 判断 1〜12）

- ADR-044（Accepted）: HMM 0.5.0 は段 1 の終わりまで直さない。`p_stuck` は固定 baseline の比べの床と H3 の手がかりに限る。ADR-019 D6 の検討は順を残し、置き場所を表の特徴へ。
- 地図 `docs/architecture/gse-design-map.md`: 層ごとの状態（§1）・段 1 と段 2 に関わる Proposed の ADR（§2）・段 1 の配布までの道筋 R1〜R10（§3）・M5 の設計（§4）。
- M5 の決定: O1 の仕組みを使う新しいモード（判断 5）・枝を先に（判断 6）・毎回 Q1・Q2・6 択（判断 7）・無作為は層化を見ず層化が譲る（判断 8）・抑制は `probe_suppressed`（判断 9）・段 1 のモードで Nudge と招待を出さない（判断 10）。

## 1 次の候補（地図 §3 の順・どれが済んだかは main の log と worktree で確かめてから勧める）

1. R1: 招待の配線の枝の残り（研究者の実機の確かめ → main の取り込み → push → schema parity）。`.steering/_handoff/next-session-gse-invitation-wiring.md`（枝 `feature/nudge-default-off` の上にある）。最初の待ちはここ。
2. R2: M5 の実装。R1 の後に main から新しい worktree を切り、`/start-task` から。地図 §4.3 の 8 項目が出発点。`/reimagine` をかけるかを最初に研究者に聞く。頻度と閾値は探索用の仮の定数。
3. R4: 段 1 の同意文書の草案（R1 を待たずに書ける）。`next-session-esm-consent-next-study.md` と ADR-031 M2・M6 の改訂案の 6 択の部分・地図 §3 の R4 の待ち。
4. `research-positioning.md` §1・WBS B1〜B4 の改訂（ADR-041 Migration 4・ADR-043 Migration 5）。地図 §0 のずれを直す。`next-session-gse-small-n-design-revision.md`。

## 2 注意

- 返答・問いは日本語で。決めることは AskUserQuestion で 1 問ずつ、推奨と理由を添えて。
- O1 の 11-01 08:30 以降の記録と、取っておいた公開データの書き手（`holdout.json`）を開かない。
- Codex に O1・段 1 の記録の本文を送らない。今日（11-03）の Codex は 611,586 / 700,000（研究者が上限を上げた）。
- 本人の探索（R5）が倫理審査の前にできるかは研究者が確かめる（地図 §3.2）。
