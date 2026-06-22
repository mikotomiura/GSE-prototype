# outcome-metrics — v0.4 アウトカム指標算出 (gse-replay --metrics)

> 親 handoff: `.steering/20260619-user-validation-data-collection/handoff-phaseB-metrics.md`
> 根拠: WBS v2 §4.0(0.10)/§4.3(M3) + codex-review v0.4 §4.1/§4.2 +
> `.steering/20260623-capture-schema-freeze/decisions.md` (CD1 external_paste_chars, CD5 同期読み)

## 背景

`capture-schema-freeze` (PR #18, commit `0043380`, main 反映済) で **捕捉 (不可逆) が完了**:
`external_paste_chars` / `intervention_response`(dismiss_reason) / `condition` / `label_pool` が
NDJSON に残るようになった。次は捕捉済みデータから **(a) AI依存度・(b) 自力解決率の指標を算出**する
解析側 (WBS 0.10 + §4.1)。指標算出は捕捉と違い後から再計算可能だが、パイロット前にパイプラインを
通しておくと M1 スモークで指標の妥当性を検証できる。

## ゴール

`gse-replay --metrics --json` が捕捉済み NDJSON から (a)(b) のアウトカム指標を**数値のみ**で
出力し (本文・キーストローク内容を一切含めない)、golden スナップショットで回帰保護される。

## スコープ

### 含むもの — `gse-replay --metrics` (+ `--json`) の拡張
捕捉済み NDJSON (key / paste.external_paste_chars / feat.p_stuck / intervention_response) から算出:
- **(b) 自力解決率**:
  - `manual_contribution_ratio = manual_insert_chars / (manual_insert_chars + external_paste_chars)`
  - `productive_manual_recovery_rate` = Stuck 候補後 5 分以内に external paste なしで net_diff 正進行の割合
- **(a) AI依存度**: `external_paste_count` / `large_paste_rate` / `paste_after_stuck_rate` /
  `self_recovery_without_paste`。`paste_count_per_hour` は補助指標。
- `manual_insert_chars` は**既存 `key` イベント列から導出** (文字生成キー − backspace。新規捕捉なし)。
- 出力は `metrics.json` (共有アーティファクト, gse-dataset `metrics/P*/<os>/`)。数値のみ・本文なし。

### 含まないもの
- NDJSON schema 変更 (算出のみ。**emit_schema/parity 不要**)。
- `blind_quality_score` (第三者ブラインド評価=人手・運用、WBS 0.13)。
- `source_role` (paste 元の内外分類=設計フォーク、WBS 0.9 残)。
- (c) 自己効力感・NASA-TLX (アンケート)。DuckDB join (WBS C/§6)。features/HMM 組み込み。
- AB/BA・MRT の割付実装 (condition の a/b/nudge/defer 配線。別タスク)。

## 受け入れ条件

- [ ] `gse-replay --metrics --json` が (a)(b) 指標 (manual_contribution_ratio /
      productive_manual_recovery_rate / external_paste_count / large_paste_rate /
      paste_after_stuck_rate / self_recovery_without_paste) を出力
- [ ] manual_insert_chars が key 列から content-free に導出 / external_paste_chars を分母に使用
- [ ] golden metrics スナップショットで回帰保護・`cargo test --workspace` 緑・`--snapshot` byte-equal
- [ ] 旧 NDJSON (external_paste_chars 欠落) で panic しない (null 耐性)
- [ ] metrics.json に数値のみ・本文非混入。code-reviewer/security-checker/cross-review で CRITICAL/HIGH なし

## 関連ドキュメント

- WBS v2 §4.0(0.10)/§4.3(M3) / codex-review v0.4 §4.1・§4.2
- `.steering/20260623-capture-schema-freeze/decisions.md` (CD1 external_paste_chars, CD5 同期読み)
- `docs/development-guidelines.md` §3 (Replay-as-Truth) / §10 (data repo)
- Skill: `data-privacy` / `architecture-rules` / `rust-standards` / (`hmm-analysis` は周辺のみ・engine 不触)

## 運用メモ
- /reimagine 適用: Yes
- 理由: `productive_manual_recovery_rate` の厳密定義 (Stuck 候補トリガ = p_stuck閾値 / user_label /
  介入発火 / probe Q1 のどれか、net_diff 正進行・5分窓・external paste なしの定義) が重く、
  複数案が考えられ最良案が自明でない (handoff §要承認①が /reimagine 推奨)。
