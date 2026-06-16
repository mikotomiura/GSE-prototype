# Task D「オフライン解析 gse-replay 拡張」

## 背景

v0.3 較正スモーク (D-14) の実装順 A→(B∥C)→**D**→E の D。
A(schema, PR#4 merge 済) / B(probe scheduler: probe_assignment + probe_triggered emit) /
C(frontend: realtime_label / session_meta / vignette_response 記録) は実装済。

記録された NDJSON を読み、**時間隔離窓**で X(認知摩擦)↔主観 Q1 を照合する
オフライン解析パイプラインがまだ無い。methodology (v0.3) は凍結済みで、これを
初めて「動くコード」に落とす。**frontend は起動しない**(NDJSON 解析のみ)。

## ゴール

`gse-replay` に較正解析パスを追加し、記録済み NDJSON から以下を算出して
metrics.json に出力できること:
1. 時間隔離窓 (t−31s..t−1s) での X/Y 集約
2. 被験者内 方向付き C-index (X↔Q1 / Y↔Q2)
3. 2段ゲート判定 (測定法ゲート → モデルゲート Go/Kill/INCONCLUSIVE)
4. MNAR 上下限 (無回答を全高摩擦/全低摩擦と仮定した範囲報告)
5. ビネット採点 (PreReg-1: q1/q2→象限推論→expected_quadrant 一致率)

## スコープ

### 含むもの (Task D = (1)〜(7))
- (1) replay.rs に consumption variant 追加 (probe_assignment / realtime_label /
  session_meta / vignette_response を ReplayEvent でパース。TA-3)。既存 Feat/Key 再生は不変。
- (2) 時間隔離窓抽出: 各 realtime_label の [analysis_window_start_ms, analysis_window_end_ms]
  内の FeatSnapshot を集め X/Y を集約。probe 後窓 (t..t+60s) は使わない (D-8)。
- (3) 被験者内 方向付き C-index (§7): 集約 X と Q1 の順位一致割合 (0.5=偶然/1.0=完全/<0.5=逆)。
  Y と Q2 も。前向き holdout (最初の2セッションで β 較正→凍結→残りで評価 §8)。
- (4) 2段ゲート判定 (D-10/PreReg-2/4): 測定法ゲート(回答率≥80%・latency 中央値≤10s・
  有効≥20件/人・ビネット6/8 かつ80%通過) → 通過時のみモデルゲート
  (C-index 中央値≥0.65 & 全員>0.55=Go / 中央値≤0.55 or 2人以上≤0.50=Kill / 他=INCONCLUSIVE)。
- (5) MNAR 上下限 (PreReg-7): 未回答を全高摩擦/全低摩擦と置いた上下限併報。被験者除外しない。
  無回答率 >20% 注意・>30% 主分析不成立。
- (6) ビネット採点 (PreReg-1): vignette_response の (q1,q2)→象限推論→expected_quadrant 一致率。
- (7) 出力: metrics.json (gse-replay 形式) に上記を載せ gse-dataset 連携 (§10)。

### 含まないもの (Task E 以降へ延期・明記)
- 実データ収集・3-5名スモーク・Go/Kill 最終運用判定 (Task E)
- 前向き holdout の multi-session 実データ評価 (D では「最初の2で凍結」ロジックまで)
- context_beacon / waveform_label / task_checkpoint の解析
- Recall 点推定 (PreReg-6/§9: 独立陽性<30件で原理的に検出力なし)
- 既存 metrics.rs の confusion/precision/recall の流用 (D-14 禁止)

## 受け入れ条件

- [ ] replay.rs が新4 type をパースし、既存 snapshot 回帰 (`--snapshot`) を壊さない
- [ ] 合成 NDJSON fixture で C-index/2段ゲート/MNAR/ビネット採点が決定論的に検証される (golden test)
- [ ] track=exploratory を主指標に混ぜない (確証と探索の隔離 §1.3)
- [ ] Recall 点推定を出さない (分母は一様ランダムプローブのみ)
- [ ] `cargo test --workspace` / `cargo clippy` 緑、main ビルド可維持、schema 不変 (A 凍結)
- [ ] 解析は analysis/ に閉じ OS API を呼ばない (architecture-rules)
- [ ] /finish-task で /cross-review (Claude code-reviewer ∥ Codex codex-review) 必須

## 運用メモ
- /reimagine 適用: **Yes**
- 理由: 設計判断が複数案ありうる (A. 窓内 X/Y 集約方法=中央値 vs 平均 vs 末尾値・沈黙ビン扱い、
  B. C-index 対象軸とペアリング・holdout 最小セッション数)。handoff も /reimagine を推奨。

## 関連ドキュメント
- `.idea/GSE_事後ラベリングシステム設計書_v0.3.md` §4.2/§6.4/§7/§8/§9/§10/§15(PreReg-1..8)
- `docs/preregistration-v0.3.md` (PreReg 凍結)
- `.steering/20260612-retro-labeling-and-corner-intervention/decisions.md` D-8/D-10/D-11/D-12/D-14
- `.steering/20260616-probe-schema/decisions.md` TA-3 (replay consumption variant は D)
- `.steering/20260616-probe-collect/decisions.md` (C が記録する形)
- `src-tauri/src/bin/replay.rs` / `logger.rs` / `analysis/metrics.rs` / `loop_step.rs`
