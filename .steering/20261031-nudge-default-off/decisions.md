# 設計判断

## D1: 既定の無効化の実体は「初期値」と「第2週」の両方（研究者の回答・2026-10-31）

- 決定: `lib.rs:122` の `INTERVENTION_ENABLED` の初期値を false にし、`App.tsx` の第2週の `interventionEnabled` も false にする。`condition` と `label_pool` は据え置く。
- 理由: 初期値だけを変えても、第2週を選べば Nudge は出続ける。判断のロジックと overlay は残るので、戻すのは 1 行で済む。
- 却下案: 初期値だけ false（運用で守ることになる）／第2週の選択肢を外す（post_intervention の置き場所が使われなくなる）。

## D2: docs の直しは事実を書く文書に限る

- 決定: README・agent-shared・architecture・verification-runbook・pilot-runbook・Skill（architecture-rules・intervention-design）を直す。research-positioning の論証、文献カード、未踏の提出物、WBS の過去の計画、ADR の本文は触らない。
- 理由: 論証の文書の「Nudge のみ」は「Wall を消した後の介入は労力を課さない」という主張の材料で、既定の無効化で結論は変わらない（労力を課す介入は依然ない）。ADR の本文は書き換えない規約。

## D3: 第2週の表示名を「第2週 (介入)」から「第2週 (Nudge なし)」に改める

- 決定: 識別子 `week2_intervention` は変えず、画面の `label` と `description` だけを事実に合わせる。
- 理由: Nudge が出ないのに「介入」と表示すると、研究者が条件を取り違える。第2週も推定状態はブラインドで、表示は開発ビルドだけ（`Dashboard.tsx:249-251`）なので、「推定を表示」とも書かない。
- 却下案: 識別子も改名する（session_meta には出ないが、変える利点がなく差分だけ増える）。
