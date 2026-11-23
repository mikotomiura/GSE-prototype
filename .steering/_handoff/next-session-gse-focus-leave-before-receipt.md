# 引き継ぎ — 止まりの最中にフォーカスを離れることは、外部からの貼り付け（受領）に先立つか（オフラインの確かめ）

> 作成: 2026-11-01（研究者の決定・`.steering/20261101-gse-pre-stall-signal/decisions.md` 判断 4 の 1）。
> このメモを一次資料にしない。事実は一次（コード・ADR・decisions.md）で確かめ直す。
> 実装のトラック（`next-session-gse-nudge-off-and-invitation-wiring.md`）と項目 2（`next-session-gse-public-data-fit-item2.md`）とは独立で、別の worktree で並行してよい。

## 0 背景

- 公開データ（CoAuthor）では、推定の 30 秒の上がりが「AI を求めた手前」（`experiments/20261031-coauthor-pre-request-signal/`）にも「本人の停滞の手前」（`experiments/20261101-coauthor-pre-stall-signal/`）にも立たなかった。打鍵のリズムで「詰まる前」を先回りする前提は、このデータでは支持されない。
- 研究者の決定: 招待の契機は差し替えられる形で実装し、並行して、打鍵の外のチャネル（フォーカスの遷移）が契機の候補になるかを手元のログで確かめる。
- Claude が挙げた注意（研究者に伝え済み）:
  1. 循環: 副のアウトカム「ウィンドウを離れずに再開」（判断 14・`.steering/20261031-gse-small-n-research-design/decisions.md`）と同じ信号。契機に使うなら、契機かアウトカムのどちらかを替える。どちらを替えるかはこの確かめの結果で研究者が決める。
  2. 離れた時点では「前」でない（事後の契機になる）。
  3. フォーカスの遷移は時刻だけで、行き先と方向を持たない（ADR-030・ADR-029）。誤発火が多い見込み。
  4. 設定で有効なときだけ記録される。0 行は「無かった」のか「計器が無かった」のか判定できない（ADR-013 の capabilities で判定する）。

## 1 問い（研究者に条件を確かめてから決める）

手元の GSE のログで、本人の分布で立てた停滞の始まり（ADR-030）の最中・前後に、フォーカスの遷移があった停滞は、無かった停滞より、その後に外部からの貼り付け（ADR-024 の受領の定義）が来やすいか。

## 2 始め方

1. 返答・記録・AskUserQuestion は日本語で。決めることは推奨と理由を添えて AskUserQuestion で聞く。`/start-task` の作法で `.steering/` を作る（新しい worktree・origin/main から）。
2. 最初に一次で確かめる:
   - 手元にあるログ: どの NDJSON にフォーカスの遷移の行があるか（`capabilities` で判定・`scripts/capabilities_gate.py`）。この Mac に O1・G1・研究者本人のログがどれだけあるかは 2026-11-01 時点で確かめていない。被験者のログは復号の手順（`docs/pilot-runbook.md`）と同意の範囲（O1 の同意文書・`docs/o1-deletion-ledger.md`）を確かめてから使う。研究者本人のログから始めるのが安全。
   - 行の形: `schema_dto.rs` の `FocusTransition`（時刻だけ）と、受領の判定（ADR-024 D1・D4・`paste` 行の `external_paste_chars`）。
   - 停滞の始まりは `gse-replay --features`（GSE のログは `feat` 行を持つので観測区間が作られる）。
3. 研究者に聞く: 使うログの範囲・停滞の前後の窓（何秒）・比べ方・何なら「先立つ」と読むか。条件は計算の前にコミットする。
4. 打鍵の本文・NDJSON の生ログは外部の LLM（Codex を含む）に送らない（`data-privacy`）。repo に入れるのは集計だけ。
5. 完了時は code-reviewer と /cross-review を並列で。main へのマージは研究者の指示で PR なし・`[skip ci]`（G-GEAR の self-hosted CI と重ねない）。
