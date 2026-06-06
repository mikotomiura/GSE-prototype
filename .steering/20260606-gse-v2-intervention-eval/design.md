# 設計

## 実装アプローチ

`gse-replay` に `--intervention` 経路を追加し、既存セッションを v2 介入ポリシーで
**オフライン反実仮想リプレイ**する。`decide()` は純関数なので、ログから入力を
再構成して時刻順にステップすれば、本番を動かさずに「もし v2 が動いていたら
どう発火したか」を再現できる。

評価は 3 クラス分類精度ではなく **decision の質**を測る。v2 のコストは非対称
（有害介入 ≫ 見送り）なので、対称な macro-F1 は目的関数として不適。本タスクでは
素の指標 (HIR/Precision/DC/Burden) を出すところまでを実装し、非対称コスト J の
重み付けは別タスクに送る。

### 入力の再構成（decisions.md D1/D4 で確定）
- `p_stuck`: **logged feat から取得**（当初案の「HMM 再生出力」を D1 で上書き）。
  logged feat に p_stuck/f3/f4/f6/timestamp が全て揃っており、入力一式を単一の
  wall-clock 時間軸で再構成できる。replay 再生 p_stuck を使うと f3/f4/f6・GT と
  時間軸がずれ、replay-feat-alignment bug を再導入するため不採用。
- `f3 / f4 / f6`: logged feat から取得（再生 feat ではなく logged を使う。
  Phase 1 の clock semantic mismatch / replay-feat-alignment bug の教訓）。
- `idle_ms`: key **press** 間隔から復元（`collect_key_timestamps` 再利用、
  `feat.ts - 直前 press ts`）。production の `get_keyboard_idle_ms` と同セマンティクス。
- `monk_mode = false`, `wall_active = false`（counterfactual の基本ケース）。
- `decide()` を feat の timestamp 順にステップ（cooldown/daily_cap/wall 累積等の
  時間依存状態が正しく進むよう、実時刻を渡す）。

### GT の二値化と join（decisions.md D2 で確定）
- PROTECT = 旧 Flow / Incubation、STALL = 旧 Stuck。
- **調査結果**: Phase 1 で主力だった range GT (`.segments.txt`) は失われており
  (dataset `labeled/` は空、`.range.metrics.json` の算出結果のみ残存)、13 セッションに
  残る GT は NDJSON の疎な point `user_label`（合計 ~83 個、1 セッションは 0 個）のみ。
- **採用**: point label を **forward-fill で区間導出**（各 label が次 label まで状態保持、
  先頭/末尾はセッション端へ延伸して全区間カバー）し、`RangeLabel` 機構に乗せる。
  自己申告状態の持続を仮定するため verdict ではなく **screening** と位置づける（D2 限界）。

## 評価指標（formalization）

decision 二値化: ACT={nudge, wall} / HOLD={none, defer}

| GT \ decision | HOLD | ACT |
|---|---|---|
| PROTECT | 正しい抑制 (TN) | **有害介入 (FP)** |
| STALL | 見送り (FN) | 有益介入 (TP) |

- **HIR (有害介入率)** = ACT∩PROTECT / 全ACT … 最重要・安全性指標。pre-reg 上限案 ≤ 0.10
- **Precision** = TP / (TP+FP) = ACT∩STALL / 全ACT
- **DC (defer 正答率)** = defer 後 W 秒以内に PROTECT へ回復した区間 / 全 defer 区間
  - 回復判定は既存 `recovered_at`（p_flow>0.5 の最初の feat）ロジックを再利用。
  - 既存データは介入発火ゼロ＝「常に defer の世界」なので counterfactual で観測可能。
- **Burden** = ACT 回数 / セッション時間（過介入の代理）

出力は pretty-print（`format_pretty` に揃える）+ `--json`（`--metrics` と同形式）。

## 変更対象

### 修正するファイル
- `src-tauri/src/bin/replay.rs` — `--intervention` フラグ追加（既存フラグと排他）、
  入力再構成と decide() ステップ、結果整形。
- `src-tauri/src/analysis/metrics.rs` — 介入評価の純関数（HIR/Precision/DC/Burden）
  を追加。既存 range/point 基盤と confusion 機構を再利用。
- `src-tauri/src/analysis/intervention.rs` — 評価から呼べるよう必要なら可視性調整
  （ロジック変更はしない）。

### 新規作成するファイル
- 必要なら `src-tauri/src/analysis/intervention_eval.rs`（評価ロジックを分離する場合）。

### 削除するファイル
- なし。

## 影響範囲

- replay の引数排他チェックに `--intervention` を追加（`--metrics`/`--segment`/
  `--segments`/`--snapshot` と相互排他）。
- schema_dto.rs は触らない想定 → tier-3 schema parity guard は drift を出さないはず。
  万一 schema に触れたら `cargo run --bin emit_schema` で再生成し parity を確認。
- CI（現状ローカル検証）への影響なし。

## 既存パターンとの整合性

- `--metrics` の `compute_session_metrics` / `compute_range_metrics` /
  `format_pretty` / `--json` の構成に倣う。
- logged feat を直接使う（再生 feat を使わない）方針を踏襲。
- 純関数 + 単体テストの分離（`format_user_label_line` 等の既存スタイル）。

## テスト戦略

- 単体テスト: 合成入力で decide() ステップ → HIR/Precision/DC/Burden の境界値検証
  （例: 全 ACT が PROTECT に乗る → HIR=1.0、defer 後即回復 → DC=1.0）。
- 統合: 既存スナップショット or 小さな ndjson fixture で replay 経路を通す。
- 実データ: P000 の 13 セッションに `--intervention` を実行し結果を記録
  （これは検証であり自動テストではない）。

## 限界（design に明記）

- **cadence 差**: 本番は 500ms ポーリング、本評価は feat 1Hz ステップ。wall 累積
  タイミングに微差が出る。HIR の定性結論は頑健だが数値は近似。
- **フィードバック効果を再現不可**: 実際の介入は後続打鍵を変える（誤介入が stuck を
  誘発する相互作用）。オフラインは「発火したか」までで、UX 結果は測れない。
  → 受容性 (issue.md ⑤) と相互作用は前向き live 収集に委ねる。
- **ラベルが旧パラダイム由来**: GT は 3 クラス自己申告で取られた。PROTECT/STALL への
  写像は思想非依存だが、本評価は verdict ではなく **screening** と位置づける。

## ロールバック計画

`--intervention` は新規経路で既存挙動に非干渉。問題時はフラグ追加分を revert すれば
replay の既存機能は無影響。
