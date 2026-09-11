# 改名の影響範囲（★ `impact-analyzer` の報告 ＋ **メインが一次で再確認**した結果）

- **調査日**: 2026-09-07
- ⚠️ **サブエージェントは報告ファイルを作れなかった**（★ `impact-analyzer` の定義に `Write` が無い）。
  → ★ **メインが受け取った内容を、一次で検算したうえで**本ファイルに落とした。

---

## ★★★ メインが一次で検算した 3 件

| # | 主張 | 検算コマンド | 実測 | 判定 |
|---|---|---|---|---|
| **1** | `compute_recovered_at` / `recovery_window_ms` は **HIR / Precision に効かない**（★ **DC のみ**） | `sed -n '430,470p' src-tauri/src/analysis/intervention_eval.rs` | ★ `precision` は `cm.tp / act_labeled`（`:440`）、`hir` も `act_labeled` 由来（`:435`）。★ `recovery_window_ms` を使うのは **`evaluate_defer_runs(&decisions, feats, recovery_window_ms)` → `dc`**（`:463-465`）**だけ** | ★★★ **主張が正しい。**⚠️★★★ **本タスクの design.md 初稿が「HIR / Precision」と書いていたのは誤り**（★ ADR-023 の枠組みをそのまま写した）。→ **訂正済み** |
| **2** | `gse-dataset` の `metrics.json` に対象フィールドは **1 件も無い** | `find /c/gse-dataset/metrics -name '*.json' \| wc -l` / `grep -rl '"outcome"' /c/gse-dataset/metrics/` | ★ **46 ファイル存在**し、★ `"outcome"` を含むファイル **0**、`self_recovery_without_paste` を含むファイル **0** | ★★★ **主張が正しい。**→ ⚠️ **requirement.md の Stop 条件（後方互換の判断が要る）には該当しない** |
| **3** | `scripts/build_analysis_db.py` が対象フィールド名を**文字列でハードコード**している | `sed -n '110,132p' scripts/build_analysis_db.py` | ★ `OUTCOME_SUM_FIELDS` に **`recovered_episode_count`**、`OUTCOME_AVG_FIELDS` に **`productive_manual_recovery_rate`** と **`self_recovery_without_paste`** | ★★★ **主張が正しい。**⚠️★★★ **これが実質的な外部契約であり、schema drift check の対象外なので気づきにくい** |

---

## ⚠️★★★ 最大の発見 —— 外部契約は `schema/current.json` ではなく **Python 側にある**

★ ADR-023 M2 は逐語で「**`schema_dto.rs` にも `schema/current.json` にも存在しない** → schema drift check は関係しない」と書いており、★ **それ自体は実測でも正しい**（★ 4 系統すべて grep 0 件 —— `schema_dto.rs` / `schema/current.json` / `lib.rs` の Tauri IPC / `src/` の TypeScript）。

⚠️★★★ **しかし「関係しない」で終わると取りこぼす。**★ 実際の消費者は:

| 消費者 | 実体 |
|---|---|
| ★ **`scripts/build_analysis_db.py`** | ★ `OUTCOME_SUM_FIELDS`（`:114-121`）/ `OUTCOME_AVG_FIELDS`（`:122-129`）に**文字列リテラル**で 3 件 |
| ★ **`scripts/fixtures/analysis_join/metrics/*.json`** | ★ **4 ファイル**（`P101/windows/sess_a` `sess_b` / `P102/macos/sess_c` / `P104/windows/sess_d`）にキーとして実在 |

→ ★★★ **Rust だけ改名すると、Python 側は列が全欠損したまま `has_metrics=True` で通る（＝ 無音で壊れる）。**
→ ⚠️ **本タスクで同時に直す。**

---

## ★ `OutcomeMetrics` が外へ出る経路（★ 実測で 1 本だけ）

- ★ **`gse-replay --metrics --json`** の JSON 出力（`OutcomeMetrics` は `#[derive(Serialize)]`・`metrics.rs:188`）
- ⚠️ `schema_dto.rs` / `schema/current.json` / Tauri IPC / `src/` TypeScript —— ★ **すべて 0 件**（実測）

---

## ⚠️ `recovery_window_ms` は **2 系統ある**（★ 混同すると波及範囲を誤る）

| 系統 | 所在 | Serialize されるか | 意味 |
|---|---|---|---|
| ★ **アウトカム系** | `OutcomeConfig.recovery_window_ms`（`metrics.rs:140`・既定 **5 分**） | ⚠️ **されない**（`OutcomeConfig` は `Debug, Clone, Copy` のみ） | ★ stuck エピソード後に `p_flow > 0.5` を探す窓 |
| ⚠️ **defer / DC 系** | `intervention_eval.rs` の **3 つの `Serialize` 構造体**のフィールド（`InterventionMetrics` / `InterventionSweepReport` / `CorrectionFloorReport`） | ★★★ **される**（`--intervention` / `--sweep` / `--corr-floor` の JSON キー） | ★ defer 区間が窓内に `p_flow > 0.5` へ到達したか（→ **DC**） |

→ ★ **本タスクが裁定したのはアウトカム系**である。⚠️ **defer / DC 系は別概念なので触らない。**

---

## ★★★ 確定した改名スコープ（★ ADR-024 で 1 件ずつ判定する）

### ★ 改名する（★ `OutcomeMetrics` の報告面 ＝ 論文・図表・`metrics.json` に出る）

| 旧 | 新 |
|---|---|
| `self_recovery_without_paste` | **`pflow_exit_without_receipt`** |
| `productive_manual_recovery_rate` | **`pflow_exit_manual_gain_rate`** |
| `recovered_episode_count` | **`pflow_exit_episode_count`** |
| `OutcomeConfig.recovery_window_ms` | **`pflow_exit_window_ms`** |
| `DEFAULT_RECOVERY_WINDOW_MS` | **`DEFAULT_PFLOW_EXIT_WINDOW_MS`** |
| `compute_recovered_at` | **`compute_pflow_exit_at`** |
| ローカル `self_recovery_no_paste` / `recovered_count` / `productive_recovery` | `pflow_exit_no_receipt` / `pflow_exit_count` / `pflow_exit_manual_gain` |

★ **`compute_pflow_exit_at` を含める理由**: ⚠️ 報告面には出ないが、
★ **今回の事故の起点が実装者の誤読だった**（ADR-023 D7 逐語「**これを書かないと、次の実装者が『独立した 2 つの測定』と読む**」）。
★ かつ **defer / DC 側でも意味は同じ**（`p_flow > 0.5` への到達）なので、**両方の呼び出し元で名前がより正確になる。**

### ⚠️ 改名しない（★ ADR-024 に「対象外」と理由つきで書く）

| 対象 | 理由 |
|---|---|
| `intervention_eval.rs` の `recovery_window_ms` フィールド（3 つの `Serialize` 構造体） | ⚠️★★★ **defer / DC の面であり、本裁定の射程外。**★ 改名すると **3 系統の CLI JSON キーが同時に変わる**（★ 得るものが無い） |
| `DEFAULT_DEFER_RECOVERY_WINDOW_MS`（`intervention_eval.rs:39`） | ★ 同上。⚠️ **`defer からの回復` は別概念** |
| `experiments/**` の Python 側の複製定数 | ★ 別 repo 相当の独立実装（`feasibility_probe.py:28-29` は metrics.rs の値をコメントで参照するだけで import 関係が無い）。⚠️ **experiments は凍結された記録**なので遡って書き換えない |
| `docs/adr/ADR-0xx` の本文 | ⚠️ **ADR 本文は書き換えない規約** |
| `.steering/` の過去タスク | ⚠️ **作業記録は当時の事実**。書き換えない |

---

## ⚠️ サブエージェント報告のうち **採らなかった** もの

★ 報告の「リスク TOP3」#3 は、`.steering/20260907-resumption-outcome-arbitration/` を
「**並行して走る別の意思決定プロセス**」と読み、ガバナンス上のリスクとして挙げていた。
→ ⚠️★★★ **これは誤りである。**★ 当該ディレクトリは **本タスク自身の作業記録**であり、
★ サブエージェントに与えた文脈にその情報が無かったために生じた誤読。★ **リスクは存在しない。**

## ⚠️ 未確認のまま残すもの

- ★ `gse-dataset` の 46 ファイルについて、`grep` ではなく `jq` でキーの悉皆確認はしていない。
  → ⚠️ ただし **`"outcome"` の文字列一致が 0 件**であり、
  ★ `OutcomeMetrics` は必ず `outcome` の下に入る（`replay.rs` の `SessionMetrics`）ので、
  **文字列一致 0 は「フィールドが無い」と同値**である。→ ★ **実害なし。**
