# 設計 (v2 — /reimagine 再生成案)

## 実装アプローチ

中核は **「Stuck エピソード」という抽象を一級市民にし、その上に (a)(b) 指標を載せる** こと。
Stuck の判定基準 (トリガ) を関数の引数 (述語 + 閾値) として外出しし、algorithm 本体から切り離す。
これにより研究設計上の争点 (どの信号を Stuck とみなすか) をコードに焼き込まず、
`metrics.rs` 既存哲学「閾値を変えて過去セッションを再処理するだけで再計算できる」を踏襲する。

### 中核データフロー
1. `bin/replay.rs` が NDJSON を 3 つの content-free な時系列に収集する:
   - `paste_events: Vec<(t, chars: u64)>` (external_paste_chars が Some の paste 行)
   - `key_events: Vec<(t, is_backspace: bool)>` (vk から判定。文字生成キー判定も vk レンジで)
   - `feats` (既存 `collect_logged_feats`、p_stuck/p_flow を持つ)
2. `analysis/metrics.rs` の新純粋関数群が上記から算出:
   - `segment_stuck_episodes(feats, cfg) -> Vec<StuckEpisode>`: **p_stuck >= 閾値** の連続区間を
     1 エピソードに統合 (merge-gap で短い回復を吸収)。**自動・全セッションで算出可能・GT 不要**。
   - `compute_outcome_metrics(episodes, paste_events, key_events, feats, session_span, cfg)`。
3. `--metrics` 経路で `SessionMetrics.outcome: Option<OutcomeMetrics>` に格納 (additive)。

### なぜ p_stuck エピソードをトリガ既定にするか (v1 との最大の違い)
- **普遍性**: feat は全セッションに必ず在る。user_label は較正セッションにしか無く、介入発火は
  介入 OFF 条件で 0。パイロット (介入 ON/OFF・ラベル有無混在) の全セッションで同一定義で算出できる。
- **既存資産の再利用**: 回復判定は既存 `compute_recovered_at` (p_flow > 0.5) がそのまま使える。
  Stuck(p_stuck) → 回復(p_flow) は HMM の状態遷移そのもので、テスト済みプリミティブに乗る。
- **トリガは差し替え可能**: `StuckTrigger` enum (PStuckThreshold / UserLabel / InterventionFired)
  を引数に取り、既定 = PStuckThreshold。研究者は再処理で他トリガに切替可能。

## 算出する指標

### Stuck エピソード (基盤)
- `StuckEpisode { start_ms, end_ms }` = `p_stuck >= P_STUCK_TRIGGER` (既定 0.60) が
  `MERGE_GAP_MS` (既定 30s = 1 ウィンドウ) 以内の中断を挟んで連続する区間。

### (b) 自力解決率
- `manual_contribution_ratio = manual_insert_chars / (manual_insert_chars + external_paste_chars_total)`
  - `manual_insert_chars` = 文字生成キー press − backspace/delete press (content-free, vk のみ)、0 下限。
  - 分母 0 → `None`。
- `productive_manual_recovery_rate` = (エピソード後 `RECOVERY_WINDOW` 内に **external paste 無し**かつ
  **net_diff 正進行** (window 内 manual_insert_chars 純増 >= `NET_DIFF_MIN`) で回復したエピソード数)
  / (回復した全エピソード数)。「回復」= `compute_recovered_at` (p_flow>0.5) で既存定義。

### (a) AI依存度
- `external_paste_count` = paste 行数。
- `large_paste_rate` = (chars >= `LARGE_THRESHOLD`) / external_paste_count (paste 0 → None)。
- `paste_after_stuck_rate` = (エピソード後 `AFTER_WINDOW` 内に paste が 1 つ以上あったエピソード数)
  / 全エピソード数 (episode 0 → None)。
- `self_recovery_without_paste` = (回復窓内に paste 無しで回復したエピソード数) / 全エピソード数。
  ※ `productive_...` との差: こちらは net_diff 不問 (paste 無し回復のみ)、分母が全エピソード。
- `paste_count_per_hour` = external_paste_count / session_span_hours (補助)。

### 設定 (`OutcomeConfig`、既定値はコード定数 + コメントで根拠明示)
| キー | 既定 | 根拠 |
|---|---|---|
| `p_stuck_trigger` | 0.60 | intervention の Wall トリガ p_stuck>0.70 より緩め (候補は広めに拾い回復で絞る) |
| `merge_gap_ms` | 30_000 | 1 ローリングウィンドウ。瞬間的な p_stuck 低下を同一エピソードに統合 |
| `recovery_window_ms` | 300_000 | handoff 指定の 5 分 |
| `net_diff_min` | 1 | 「正進行」= 純増 1 文字以上 (v0.4 「net_diff 正進行」最小解釈)。承認で調整 |
| `large_threshold` | 50 | large paste = 50 文字以上 (1 行コード/1 文相当超) |
| `after_window_ms` | 120_000 | stuck 後 2 分以内の paste を「stuck 起因」とみなす |

## 変更対象

### 修正するファイル
- `src-tauri/src/analysis/metrics.rs` — `StuckEpisode` / `StuckTrigger` / `OutcomeConfig` /
  `OutcomeMetrics` 型、`segment_stuck_episodes()` / `compute_outcome_metrics()` 純粋関数、
  `SessionMetrics.outcome: Option<OutcomeMetrics>` 追加。
- `src-tauri/src/bin/replay.rs` — `collect_paste_events()` / `collect_key_events()` collector 追加
  (既存 collector と同流儀・`MAX_SESSION_BYTES` ガード)。`--metrics` 経路で outcome を算出。
  pretty 出力にも outcome 行追加。
- `src-tauri/tests/fixtures/outcome_*.ndjson` — stuck→paste / stuck→manual-recovery を含む golden。
- replay.rs テスト — `--metrics --json` の outcome 固定値スナップショット。

### 新規作成するファイル
- なし (既存モジュール拡張)。

## 既存パターンとの整合性
- 純粋関数 + Option 欠損安全 (既存 `Option<i64>` 中央値と同型)。`compute_recovered_at` を再利用。
- `analysis/` OS 非依存・`tracing`/`anyhow`・`println!` 不使用。
- collector はパース失敗スキップ・サイズガード (既存 `collect_key_timestamps` と同流儀)。
- 文字生成キー判定は content-free (vk レンジのみ。Unicode 内容に触れない = data-privacy ルール1)。

## テスト戦略
- 単体: episode 統合 (merge-gap 境界・連続 stuck)、manual_insert_chars (char−backspace・下限0)、
  比率ゼロ割→None、recovery×paste有無×net_diff の真理値表、旧 NDJSON (paste/chars 欠落) で panic しない。
- 統合 (Replay-as-Truth): 新 golden fixture + `--metrics --json` outcome 固定値スナップショット。
- 既存 `--snapshot` byte-equal 維持・既存 metrics golden は `outcome` 追加分のみ期待値更新。

## ロールバック計画
- `outcome` フィールド + 新関数を削除すれば旧挙動。golden は新規追加のため削除で復旧。

## 設計判断の履歴
- 実行回数: 1 回目 (/reimagine)
- 採用: **v2** (Stuck エピソード抽象 + `StuckTrigger` enum)
- ユーザー承認 (2026-06-23):
  - ① 既定 Stuck トリガ = **p_stuck エピソード** (`StuckTrigger::PStuckThreshold`, 既定 0.60)。
    user_label / 介入発火は enum で切替可能だが既定にしない。
  - ② `net_diff_min` = **1 文字** (最小解釈: 回復窓内 manual_insert_chars 純増 >= 1 で「正進行」)。
  - ③ 閾値セットは **既定値** (p_stuck_trigger=0.60 / large=50 / after_window=120s / merge_gap=30s /
    recovery_window=300s)。すべて `OutcomeConfig` で受け、コード定数 + 根拠コメントで明示。
- 根拠: パイロットは介入 ON/OFF・ラベル有無が混在 → 全セッションで算出できる p_stuck エピソードが
  M1 スモークでのパイプライン疎通検証に向く。トリガを enum 外出しで研究設計フォークを焼き込まない。
