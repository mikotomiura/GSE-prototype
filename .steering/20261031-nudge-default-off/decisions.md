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

## D4: レビューの指摘への対応（security-checker・/cross-review 1 巡目・2026-10-31）

- 第2週の `label_pool`（`post_intervention`）に、Nudge が出る環境の旧データと出ない新データが混ざる（security-checker LOW・cross-review MEDIUM 一致）。据え置きは D1 のとおり。旧データと新データは session_meta の `intervention_enabled` で分ける。`logger.rs` の `LabelPool` の doc をこの形に直した。下流で `label_pool` を読むコードは今は無い（replay.rs の `#[allow(dead_code)]`）。`schema_dto.rs` の doc は「介入可視」と書いていないので触らない（emit_schema の出力を変えない）。
- 第2週の false を守るテストが無い（cross-review MEDIUM 一致）。フロントに単体テストの基盤（vitest 等）が無く、tsc も cargo test も App.tsx の値を見ない。基盤を入れるのは範囲外とし、残りとして記録する。守っているのは初期値（定数の const assert）だけである。
- D2 に挙げた intervention-design Skill を diff に入れていなかった（cross-review LOW）。description に ADR-040 D1 を足した。ルール 3（Wall Server）は削除済みの機能の記述で、触らない。
- pilot-runbook の「介入は無い」に「招待は EH3 モードでだけ動く」を添えた（README と揃える）。
- Codex の `FORCE_NUDGE` の言及は既存のデバッグ仕様（`GSE_DEBUG=1` の門）で、指摘に数えない。
