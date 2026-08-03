# Issue [00X]: [title]
verify_level: parse            # parse | recheck（AC直結/security/公開API/データ移行/課金 は recheck）
## Goal / ## Background
## Scope (In / Out) / ## Allowed Files   ← 並列可能性はこの集合の交差で判定する
## Acceptance Criteria  → 各項目に対応 test 名を明記（AC↔test マッピング）
## Test Plan / ## Stop Conditions
## Dependencies      ← 依存 issue の id。DAG を成し循環禁止
## Status            ← 実行体が更新（single writer: モードA=worktreeループ / モードB=loop-worker / モードC=scripts/loop-run.sh）
## Execution Result  ← 完了時。PR本文になる
