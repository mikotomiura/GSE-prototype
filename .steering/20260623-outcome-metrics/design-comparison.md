## 設計案比較 — outcome-metrics

### v1 の要旨
`SessionMetrics` に `outcome: Option<OutcomeMetrics>` を additive 追加。`productive_manual_recovery_rate`
の Stuck 候補トリガを **`user_label == stuck` 主・p_stuck 補助** とする。理由は「M3 Y価値検証の主旨は
ユーザーが行き詰まった後の自力回復であり GT ラベルが最も解釈容易」。閾値 (large=50/after=120s) は定数。

### v2 の要旨
**「Stuck エピソード」を一級抽象**にし、トリガを `StuckTrigger` enum + 閾値で外出し。既定トリガを
**`p_stuck >= 0.60` の連続区間 (merge-gap で統合)** とする。回復判定は既存 `compute_recovered_at`
(p_flow>0.5) を再利用。普遍性 (全セッションで算出可) と既存資産再利用を重視。同じく additive 追加。

### 主要な差異
| 観点 | v1 | v2 |
|---|---|---|
| Stuck トリガ既定 | user_label=stuck (GT) | p_stuck>=0.60 エピソード (自動) |
| 適用範囲 | ラベル有セッションが主 | **全セッション** (ラベル/介入 有無不問) |
| トリガ差替 | 補助フォールバック程度 | **enum で明示的に切替可能** (再処理で再計算) |
| 既存資産再利用 | 部分的 | `compute_recovered_at` をそのまま再利用 |
| 抽象度 | 指標ごとに個別計算 | StuckEpisode を共有基盤に集約 |
| 変更規模 | 中 | 中〜やや大 (episode 統合ロジック分) |
| テスト戦略 | 指標別単体+golden | episode 統合の境界テストが追加で必要 |
| リスク | ラベル疎なパイロットで分母が小さく不安定 | p_stuck 閾値の妥当性がパイロット結果に依存 (が再処理で調整可) |

### 推奨案
**v2 (ハイブリッド寄り)** — 理由:
1. **普遍性**: パイロットは介入 ON/OFF・ラベル有無が混在する。v1 (user_label 主) は無ラベル/介入
   セッションで分母 0 になりがちで、M1 スモークでの指標妥当性検証 (requirement 背景) が回らない。
   v2 の p_stuck エピソードは全セッションで算出でき、パイプライン疎通検証に向く。
2. **既存哲学との整合**: `metrics.rs` は「閾値を変えて再処理で再計算」を明文化している。トリガを
   enum で外出しする v2 はこの哲学の自然な延長で、研究設計フォーク (どの信号を Stuck とするか) を
   コードに焼き込まない。
3. **既存資産**: 回復判定 `compute_recovered_at` (p_flow>0.5) を再利用でき、新規ロジックが減る。
4. v1 の長所 (user_label による解釈容易性) は v2 の `StuckTrigger::UserLabel` として吸収済み
   (既定でないだけ) → ハイブリッドとして両立。

### ユーザー承認が必要な残フォーク (採用案に依らず)
- ① 既定トリガ: p_stuck エピソード (v2) / user_label (v1) / 介入発火 — のどれを既定にするか。
- ② net_diff「正進行」の閾値 (`net_diff_min`: 1 文字 / 20 文字 等)。
- ③ 閾値: `p_stuck_trigger`(0.60) / `large_threshold`(50) / `after_window`(120s) / `merge_gap`(30s)。
