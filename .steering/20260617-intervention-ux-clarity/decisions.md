# decisions.md — intervention-ux-clarity

## ID-1 Monk Mode は表示条件化 (Option A・ユーザー承認)
- **判断**: `interventionEnabled=true` のときだけ Monk Mode トグルを描画。ロジック (broadcast / Wall 無効化) は不変。
- **根拠**: interventionEnabled=false では `lib.rs:135` が全介入を gate し Monk Mode は no-op。「効かないのに見える」
  混乱を、機能を削らずに解消できる。一本化 (Option B) は Wall 単独 mute を失うため不採用。intervention-design ルール5 維持。

## ID-2 「放置で介入なし」は仕様 (バグでない) — 明文化で対応
- **判断**: 介入ロジックは変更しない。docs に発火/非発火条件を明記し期待ギャップを防ぐ。
- **根拠/証拠**: dogfood セッションは intervention_enabled:true で 154 decision 走行。
  - 放置中: `idle_ms=565042ms (9.4分)` で `p_stuck=0.0138` (idle で低下)・`suppressed_by:["away_idle"]`。
  - away_idle (`intervention.rs:176`) は **全介入**を none 化 (doc の「Wall 抑制」表記を「介入全停止」に訂正)。
  - 介入対象は「作業没入中の苦闘」(高 p_stuck × 2-30s 小休止)。放置 (idle) は対象外。

## ID-3 opportunity ゲートは n=1・DC=1.0 では変更しない (再評価を申し送り)
- **判断**: `intervention.rs` の閾値 (NUDGE_OPPORTUNITY_THRESHOLD=0.35 / pause 窓 / away_idle=180s) は本タスクで変えない。
- **証拠** (`gse-replay --intervention` on dogfood session):
  - Decisions 1111 = none 1082 / defer 29 / nudge 0 / wall 0。
  - 能動タイプ中に p_stuck 0.65〜0.92 を検知するも小休止と重ならず nudge 未発火。
  - **DC (defer correctness) = 1.000**: defer した苦闘は全て自己回復 (= 介入しなかったのは妥当)。Burden 0。
  - GT ラベル 0 件のため HIR/Precision は算出不可。
- **根拠**: n=1 かつ DC=1.0 で「ゲートが厳しすぎて有益な介入を逃した」証拠はない。閾値変更は forking paths/
  過適合リスク。ml-workflow 準拠で、**ラベル付き複数セッション**を集めて `gse-replay --intervention` の
  HIR/Precision/Burden を見てから判断するのが正道。
- **申し送り (将来タスク)**: 実スモークデータ蓄積後に opportunity 感度分析。候補ノブ: pause 窓拡大 /
  NUDGE_OPPORTUNITY_THRESHOLD 緩和 / away_idle 閾値。変更時は intervention_eval golden を更新し HMM_VERSION 流儀で記録。

## 申し送り
- 今回のセッションは `Documents\GSE-sessions\` に出力 = **GSE_DATASET 未設定**。本番収集前に環境変数設定 (runbook §0)。
- Codex /cross-review は jq 不在でスキップ見込み ([[project-codex-review-needs-jq]])。
