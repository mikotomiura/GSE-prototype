# GSE v2 Intervention Eval（オフライン反実仮想評価）

## 背景

v2 (opportunity MVP) で Need/Opportunity/defer の介入ポリシー
`analysis::intervention::decide()` を導入したが、**その判断品質を測るデータが
1 件も存在しない**。既存の GT 付きセッション (`C:\gse-dataset\raw\P000`、
Windows 13 件) は全て v2 以前のパラダイムで収集され `intervention_decision=0`。

一方 issue.md は「打鍵リズムだけで実用精度の状態判別ができるのか」を問うており、
Phase 1 では「タイポ多い Flow を誤 Stuck 介入し、実際の stuck を誘発した」
有害介入が実データで観測されている。

文脈 (mouse/構造) 追加や新規 live 収集に進む前に、**defer-first 設計が
この有害介入を抑制できるかを、既存データだけで先に検証する**必要がある。

`decide()` は `(p_stuck, f3, f4, f6, idle_ms)` の決定論的純関数であり、
入力は既存ログから再構成できる。さらに既存データは「常に defer の世界」
(介入発火ゼロ) なので、defer 後の自然回復が観測でき、**DC (defer 正答率) の
counterfactual はこのデータでしか取れない**。

## ゴール

`gse-replay` に `--intervention` 経路を追加し、既存セッションを v2 ポリシーで
リプレイして以下の指標を算出・出力できること。13 セッション全てに適用し、
「v2 が Phase 1 の有害誤 Stuck パターンを抑制できているか」を結論として報告する。

## スコープ

### 含むもの
- `gse-replay <session.ndjson> --intervention [--json]` の追加。
- 既存ログから `InterventionInput` を再構成し `decide()` を時刻順にステップ。
- 評価指標の算出: HIR / Precision / DC / Burden（下記 design 参照）。
- 単体テスト（純関数評価 + replay 経路）。
- 13 セッションの実行結果を steering に記録。

### 含まないもの
- 新規データ収集（live 収集はしない）。
- 文脈 (mouse / scroll / focus role / 構造特徴) の追加。
- HMM パラメータ・emission/transition の変更。
- Dashboard の旧「認知状態断定表示」リフレーミング（次タスク task #2）。
- 期待コスト J の重み `w_FP/w_FN/w_df/w_b` と回復窓 `W` の pre-registration
  （閾値確定は別タスク。今回は素の指標算出まで）。
- ONNX / 学習モデル移行。

## 受け入れ条件

- [ ] `--intervention` が既存の `--metrics`/`--segment`/`--segments`/`--snapshot`
      と排他で動く。
- [ ] HIR / Precision / DC / Burden が pretty-print と `--json` の両方で出る。
- [ ] GT は PROTECT(=Flow/Incubation) / STALL(=Stuck) に二値化して評価する。
- [ ] decision は ACT={nudge,wall} / HOLD={none,defer} に二値化する。
- [ ] cadence (feat 1Hz vs 本番 500ms) とフィードバック効果を再現できない
      限界が design.md に明記されている。
- [ ] `analysis/` に OS API が入らない。`tracing` のみ。`anyhow::Result`。
- [ ] `cargo test` と `cargo fmt` が通る。
- [ ] 13 セッションの HIR/DC/Precision/Burden が steering に記録されている。

## 関連ドキュメント

- docs/architecture.md（データフロー・1Hz ゲート）
- docs/development-guidelines.md §10（replay / metrics / schema 運用）
- docs/glossary.md（PROTECT/STALL・参考スコア・recovered_at・混同行列）
- docs/gse-v2-redesign.md（Need/Opportunity/defer・Phase 3 指標）
- .steering/20260415-phase1-ground-truth/baseline_metrics.md（既存指標の形式）

## 運用メモ

- /reimagine 適用: No
- 理由: 評価方法 (HIR/DC/Precision/Burden、非対称コストの考え方) は事前議論で
  確定済み。本タスクはツール実装と既存データ算出に限定する。
