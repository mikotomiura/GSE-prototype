# 設計判断 (outcome-metrics)

## CD-OM1: Stuck 候補の既定トリガ = p_stuck エピソード (ユーザー承認 2026-06-23)
- **判断**: `productive_manual_recovery_rate` 等の基盤となる「Stuck エピソード」の既定トリガを
  `StuckTrigger::PStuckThreshold` (p_stuck >= 0.60 の連続区間) とする。`UserLabel` / `InterventionFired`
  も enum に用意し再処理で切替可能だが既定にしない。
- **根拠**: パイロットは介入 ON/OFF・ラベル有無が混在。feat は全セッションに必ず在るため p_stuck
  トリガは全セッションで算出でき、M1 スモークのパイプライン疎通検証に向く。user_label は較正
  セッションにしか無く、介入発火は介入 OFF で 0 になり分母が不安定。
- **/reimagine**: 1 回実行し v1 (user_label 主) と比較。v2 (p_stuck エピソード + enum 外出し) を採用
  (`design-comparison.md`)。研究設計フォークをコードに焼き込まない方針。

## CD-OM2: manual_insert_chars の文字生成キー判定 (is_text_producing)
- **判断**: content-free に「文字生成キー」を VK レンジで判定する保守的集合を定義
  (英数 / Space / Enter / Tab / テンキー / OEM 句読点。修飾・ナビゲーション・ファンクション・
  backspace/delete を除外)。`manual_insert_chars = 文字生成キー press − backspace press` (0 下限)。
- **根拠**: data-privacy ルール1 は vk コード記録を許可。VK → 実文字のマッピングは行わない
  (Unicode 内容に触れない)。IME 経由の入力はキーストローク数の近似となるが、external_paste_chars
  を分母に別途加えるため (b) の主旨 (手入力 vs AI ペーストの分離) は保たれる
  (validation/decisions.md D7 SUPERSEDED の「案C 単独では不可」を解消)。
- **暫定性**: VK 集合は定義上の選択であり、パイロット後に調整しうる (再処理で再計算可能)。

## CD-OM3: 文字数欠落 paste (旧 NDJSON) は outcome から除外し件数を残す
- **判断**: `external_paste_chars` が None の paste 行 (capture-schema-freeze 以前) は文字数不明のため
  outcome 集計から除外する。ただし除外件数を `OutcomeMetrics.excluded_paste_count` に数値で残す。
- **根拠**: 除外を黙殺すると manual_contribution_ratio が manual 寄りに偏るのに研究者が気づけない
  (code-reviewer MEDIUM 指摘)。件数を残せば偏りの程度を後から判断できる。`collect_paste_events`
  が warn でも可視化する。

## CD-OM4: 閾値・net_diff 既定値 (ユーザー承認 2026-06-23)
- `p_stuck_trigger=0.60` (Wall トリガ 0.70 より緩め=候補を広く拾い回復で絞る) /
  `merge_gap_ms=30_000` (1 ローリングウィンドウ) / `recovery_window_ms=300_000` (handoff 指定 5 分) /
  `net_diff_min=1` (最小解釈: 純増 1 文字以上で「正進行」) / `large_threshold=50` / `after_window_ms=120_000`。
- すべて `OutcomeConfig` の定数 + 根拠コメントで明示。再処理で調整可能。

## CD-OM5: SessionMetrics.outcome は additive な Option ネスト (後方互換)
- **判断**: 既存 `SessionMetrics` (confusion/per_class/F1) を不変に保ち、`outcome: Option<OutcomeMetrics>`
  を追加するのみ。`compute_session_metrics` / `compute_range_metrics` は `None`、`--metrics` 経路が付与。
- **根拠**: gse-dataset の既存 `metrics/P*/` 利用側を壊さない (新キー追加のみ)。NDJSON schema 不変
  (emit_schema byte-equal を確認) → parity 不要。

## CD-OM7: cross-review (Claude ∥ Codex) 指摘への対応 (2026-06-23)
両系統が稼働 (Codex gpt-5.5・jq 導入済)。両者一致・採用指摘を本タスク内で消化:
- **AGREE-1 (HIGH)**: `OutcomeConfig.trigger` がドキュメント上「切替可」だが実装は p_stuck 固定 →
  `segment_stuck_episodes` で予約トリガ時は**空を返す**ガードを追加。docs (glossary/functional-design)
  を「現状 PStuckThreshold のみ実装」に修正。`segment_reserved_trigger_returns_empty_not_pstuck` で検証。
- **AGREE-2 (HIGH)**: collector 失敗時に `Some(0埋め)` を出していた (「実測ゼロ」と「データ無し」の混同) →
  `--metrics` 経路を「両 collector Ok 時のみ Some、失敗時は outcome=None + warnings 追記」に修正。
- **AGREE-3 (MEDIUM)**: `Ctrl+V` の `V` が manual_insert_chars に混入 → 実装は近似 (proxy) として維持し、
  `manual_insert_chars` の doc コメントに過大評価の注意を明記 (両者ともドキュメント対応で合意)。
- **CLAUDE-1 (MEDIUM)**: paste 文字数総和の u64 wrap → `saturating_add` で畳む。
  `outcome_paste_chars_total_saturates_no_overflow` で検証。
- **CODEX-2 (却下)**: `.codex/budget.json` の変更指摘はツールノイズ (ユーザー指示で対象外)。
- **CODEX-3 (確認)**: VK 時系列は `OutcomeMetrics` に保持せず pretty/JSON にも生列を出さない
  (数値のみ)。data-privacy ルール1 準拠を現状維持 (本 CD で記録)。

## CD-OM6: BufReader::lines() の行長無制限を受容 (security MEDIUM・脅威モデル明記)
- **判断**: 新 collector (`collect_paste_events` / `collect_key_events`) は既存 collector
  (`collect_user_labels` / `collect_logged_feats`) と同様に `BufReader::lines()` を用い、行長上限は
  設けない (ファイル全体は MAX_SESSION_BYTES=500MB でガード)。
- **根拠**: `--metrics` の入力は被験者自身/研究者のローカル NDJSON のみで攻撃者制御の入力経路は無い
  (リモート送信なし)。既存全 collector と同一流儀を保つ方が一貫性が高く、本 collector だけ別扱いに
  しない。単一巨大行 (≤500MB) による一時アロケーションは限定的 DoS 余地だが、ローカル信頼入力前提で
  受容する (security-checker が代替として「脅威モデル明記」を許容)。将来 collector を 1 パス統合する
  際に行長ガードもまとめて検討する。
