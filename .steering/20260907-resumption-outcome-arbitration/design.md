# 設計

## 実装アプローチ

★ **(b′) を「新しい観測」ではなく「既存の 3 つの時刻列の突き合わせ」として実装する。**

⚠️★★★ **新しく観測するものはゼロである**（★ ADR-023 D1 の「計器は新設ゼロ」が (b′) でも保たれる）。
★ 一次で確認した在庫:

| 必要なもの | 状態 | 一次 |
|---|---|---|
| stuck エピソードの切り出し | ★ **ある** | `metrics.rs:258 segment_stuck_episodes` |
| 打鍵の時刻列（ギャップは隣接差分） | ★ **ある** | `metrics.rs:171 KeyPress { timestamp, vk }` |
| 離席候補の閾値 180s | ⚠️ **あるが置き場所が違う** | `intervention.rs:10 AWAY_IDLE_MS`（★ **private const**）→ ★ `pub` 化して SSOT を 1 つにする |
| receipt の時刻 | ★ **ある** | `metrics.rs:166 PasteEvent { timestamp, chars }` |
| CIF / 競合リスク | ⚠️★★★ **無い** | `OutcomeMetrics` は `Option<f64>` の比率だけ（`metrics.rs:189-224`）。★ ADR-023 D6 逐語「主指標を生存時間にすることは、いまの `OutcomeMetrics`（比率のみ）の形を超える」 |

---

## estimand（★ 判断 4 の実装形）

```
  stuck エピソード              離席候補ギャップ            観測
  [start_ms .. end_ms]          (>= away_gap_ms)
  ─────────────────┐            ┌──────────┐
   p_stuck >= 0.60 │            │  打鍵なし │
  ─────────────────┘            └──────────┘
                    gap_start ──┘          └── resumed_at = t0（★ 時間原点）
                                                │
                                                ├─ 主イベント : receipt (paste) が起きた
                                                ├─ 競合イベント: 次の離席候補ギャップが始まった
                                                └─ 打ち切り   : 観測終了（feats / keys の末尾）
```

- ★ **紐づけ規則**: `gap_start` が `[ep.start_ms, ep.end_ms + cfg.after_window_ms]` に入るとき、
  その ギャップを そのエピソードに紐づける。
  ⚠️ **新しいノブを増やさず、既存の `after_window_ms`（既定 120s・`metrics.rs:146` 逐語
  「エピソード後この窓 (ms) 内の paste を stuck 起因とみなす」）の意味をそのまま使う。**
- ★ **1 エピソードに複数のギャップが紐づきうる。**★ 各 (episode, gap) 対を **1 事象**として数え、
  ⚠️ **寄与したエピソード数も別に出す**（★ 1 エピソードが事象数を支配していないかを読み手が見られるように）。
- ★ **同時刻のタイブレークは「受領を優先」**（★ 保守的側 —— `receipt_free` を高く出さない向き）。

### CIF（Aalen–Johansen・競合リスク）

★ 事象時刻 `t_1 < t_2 < ...` について:

```
S(t_0) = 1
S(t_j) = S(t_{j-1}) * (1 - (d1_j + d2_j) / n_j)
CIF_receipt(t) = Σ_{t_j <= t}  S(t_{j-1}) * d1_j / n_j
receipt_free_resumption(t) = 1 - CIF_receipt(t)
```

- `n_j` = `t_j` 直前のリスク集合サイズ / `d1_j` = 受領 / `d2_j` = 次の離席候補
- ★ **地平は 5 分 / 10 分**（ADR-023 D6 逐語）
- ⚠️ **依存 crate を足さない**（★ 純粋関数 30 行程度。`rust-standards` ルール 7）

---

## 変更対象

### 修正するファイル

- `src-tauri/src/analysis/intervention.rs` — `AWAY_IDLE_MS` を `pub const` にする（★ SSOT 化のみ。値も挙動も変えない）
- `src-tauri/src/analysis/metrics.rs` — 主変更
  - ★ **新規**: `ResumptionEvent` / `ResumptionOutcome` / `ReceiptFreeResumption`
  - ★ **新規**: `segment_resumptions()` / `classify_resumption()` / `cif_receipt()`
  - ★ **新規**: `OutcomeConfig.away_gap_ms`（既定 = `intervention::AWAY_IDLE_MS`）
  - ⚠️ **改名**: 下記「改名表」
  - ★ `OutcomeMetrics` に `receipt_free_resumption: ReceiptFreeResumption` を追加
  - ★ `fmt_*` の表示行を更新
- `src-tauri/src/bin/replay.rs` — 改名の追随（★ 実測 1 箇所 ＋ テスト）
- `src-tauri/src/analysis/intervention_eval.rs` — 改名の追随（★ `compute_recovered_at` を import）
- `docs/glossary.md` — 例外条項（`:247`）と `:248` の指標名を新版へ揃える ＋ 用語追加
- `docs/adr/README.md` — ADR-024 を index に追加
- `experiments/20260906-interruption-resumption-arm1/notes.md` — §5 の表と定型文 / §10 の未決を閉じる

### 新規作成するファイル

- `docs/adr/ADR-024-resumption-outcome-without-estimator.md` — 裁定の SSOT

### 削除するファイル

- ★ **なし**（⚠️ 既存指標は削除せず副次へ降格する＝判断 2）

### ⚠️ 改名表（★ 判断 6 —— 一括判断。**「すべて改名する」ではない**）

> ★ 判定基準: **`recovery` が「解決した」を含意する位置にあるか**、
> かつ **論文・図表・被験者向け説明に出るか**（★ ADR-023 D6 の害の根拠は逐語
> 「**指標名は論文・図表・被験者向け説明に出る**」）。
> ⚠️ **加えて、実装者の誤読を招く位置にあるものも対象にする** ——
> ★ D7 自身が逐語「**これを書かないと、次の実装者が『独立した 2 つの測定』と読む**」と書いており、
> ★ **今回の事故の起点はまさに実装者の誤読だった**。

| 旧 | 新 | 判定理由 |
|---|---|---|
| `self_recovery_without_paste` | **`pflow_exit_without_receipt`** | ★ ADR-023 D6 が改名を決めた 1 件。⚠️ **`stuck_exit_without_receipt` からずらした**理由は判断 2 |
| `productive_manual_recovery_rate` | **`pflow_exit_manual_gain_rate`** | ★ **報告に出る指標**（`metrics.json`）。⚠️ `recovery` を含み、かつ `p_flow` 依存であることが名前から読めない |
| `recovered_episode_count` | **`pflow_exit_episode_count`** | ★ 同上（`metrics.rs:222` で出力済み） |
| `compute_recovered_at` | **`compute_pflow_exit_at`** | ⚠️ **報告には出ないが、実装者の誤読を招く位置にある**（★ 今回の事故の起点） |
| `recovery_window_ms` (OutcomeConfig) | **`pflow_exit_window_ms`** | ★ 同上（★ 5 分・`metrics.rs:157`） |
| `DEFAULT_RECOVERY_WINDOW_MS` | **`DEFAULT_PFLOW_EXIT_WINDOW_MS`** | ★ 同上（★ 15 分・`metrics.rs:12`。⚠️ **上と値が違う**ので、名前で区別が付くようにする） |
| ローカル `self_recovery_no_paste` / `recovered_count` / `productive_recovery` | `pflow_exit_no_receipt` / `pflow_exit_count` / `pflow_exit_manual_gain` | ★ 呼応させる |
| ⚠️ `DEFAULT_DEFER_RECOVERY_WINDOW_MS`（`intervention_eval.rs:39`） | ⚠️ **改名しない** | ★ **defer からの回復は別概念**（★ **DC の算出**。⚠️ HIR ではない —— 一次で確認）。⚠️ 本裁定の射程外 |
| ⚠️ `intervention_eval.rs` の `recovery_window_ms` フィールド（`InterventionMetrics` / `InterventionSweepReport` / `CorrectionFloorReport`） | ⚠️ **改名しない** | ⚠️★★★ **3 つとも `Serialize` されており、改名すると `--intervention` / `--sweep` / `--corr-floor` の JSON キーが同時に変わる**（★ 実測）。★ defer / DC の面であり、得るものが無い |
| ★ `scripts/build_analysis_db.py` の `OUTCOME_*_FIELDS` | ★ **同時に更新** | ⚠️★★★ **実質的な外部契約。schema drift check の対象外**（→ `impact-rename.md`） |
| ★ `scripts/fixtures/analysis_join/metrics/*.json`（4 件） | ★ **同時に更新** | ★ 上の入力フィクスチャ |

★★★ **影響範囲は確定した**（→ `impact-rename.md`・★ メインが一次で 3 件検算済み）。

---

## 影響範囲

| 影響先 | 対処 |
|---|---|
| ★ `FeatSnapshot` 列 | ⚠️★★★ **1 byte も変えない** —— ★ `HMM_VERSION` を **bump しない**。→ **ゴールデン再生成 不要** |
| ★ `schema_dto.rs` / `schema/current.json` | ★ **無関係**（★ `OutcomeMetrics` は NDJSON の行種ではなく `gse-replay` の *出力*。ADR-023 M2 逐語）。⚠️ **ただし `emit_schema` の byte-equal 比較は Done 条件に入れる**（D-4） |
| ★ `gse-dataset` の既存 `metrics.json` | ★★★ **影響なし（実測）** —— ★ **46 ファイル存在するが、`"outcome"` を含むものは 0 件**（★ HMM 精度指標だけの古い形）。→ ⚠️ **requirement.md の Stop 条件には該当しない** |
| ★ Frontend (`src/`) | ★ **無関係**（★ 実測: `src/` に対象識別子 **0 件**。Tauri IPC (`lib.rs`) にも `OutcomeMetrics` は出ない） |
| ⚠️★★★ **`scripts/build_analysis_db.py`** | ⚠️★★★ **これが実質的な外部契約である** —— ★ `OUTCOME_SUM_FIELDS` / `OUTCOME_AVG_FIELDS` に**文字列でハードコード**（`:114-129`）。⚠️ **schema drift check の対象外なので無音で壊れる。**→ ★ **同じコミットで直す** |
| ⚠️ `scripts/fixtures/analysis_join/metrics/*.json` | ★ **4 ファイル**にキーとして実在 → ★ 同時に更新する |
| ⚠️★★★ `intervention_eval.rs` の **DC (defer 正答率)** | ★ `compute_recovered_at` の**改名のみ**（★ 挙動不変）。⚠️★★★ **初稿は「HIR / Precision」と書いていたが誤り** —— ★ 一次で `precision` は `cm.tp / act_labeled`（`:440`）、`hir` も `act_labeled` 由来（`:435`）と確認。★ `recovery_window_ms` を使うのは `evaluate_defer_runs(...) -> dc`（`:463-465`）**だけ**である |

---

## 既存パターンとの整合性

- ★ `analysis/` は **OS 非依存の純粋関数**のまま（`architecture-rules` ルール 2）。
  ★ `intervention.rs` ← `metrics.rs` の参照は **`analysis/` 内**であり、
  既に `metrics.rs` は `crate::analysis::loop_step::FeatSnapshot` を import している（★ 同型）。
- ★ 分母 0 の比率は `None`（★ `ratio()` の既存規約・`metrics.rs` 冒頭 doc 逐語「NaN を出さない」）。
- ★ 命名は snake_case / 定数は SCREAMING_SNAKE_CASE（`rust-standards` ルール 6）。
- ★ `println!` / `eprintln!` は使わない（`rust-standards` ルール 3）。
- ⚠️ **依存 crate を足さない**（`rust-standards` ルール 7）—— CIF は自前の純粋関数。

---

## テスト戦略

### 単体テスト（★ `metrics.rs` の `#[cfg(test)]` に追加）

| test 名 | 何を固定するか |
|---|---|
| `resumption_requires_away_gap` | ⚠️ 179s のギャップは事象にならない / 181s はなる（★ 境界） |
| `resumption_links_to_episode_within_after_window` | ★ 紐づけ規則（`after_window_ms` 外のギャップは紐づかない） |
| `resumption_outcome_receipt_wins_tie` | ★ 同時刻は受領を優先（★ 保守的側） |
| `resumption_outcome_next_away_candidate_is_competing` | ★ 次の離席候補ギャップの開始が競合イベントとして分類される |
| `resumption_outcome_censored_at_observation_end` | ★ 地平前に観測が終われば打ち切り |
| `cif_receipt_monotone_and_bounded` | ★ CIF が単調非減少 かつ `[0,1]` |
| `cif_receipt_matches_hand_computation` | ★★★ **手計算した既知の値と一致**（★ 競合ありの 3 事象で検算） |
| `receipt_free_resumption_none_when_no_events` | ★ 事象 0 → `None`（★ NaN を出さない） |
| `receipt_free_resumption_has_no_pflow_dependency` | ⚠️★★★ **AC-2** —— ★ **`p_flow` を全部 0.0 にしても値が変わらない**ことを固定する |
| `away_gap_default_matches_intervention_ssot` | ⚠️★★★ **AC-3** —— ★ `OutcomeConfig::default().away_gap_ms == intervention::AWAY_IDLE_MS` |

> ⚠️★★★ **検査自体の空回りを検査する**（`verify-before-claiming` ルール 5b・
> ★ B1 の `--selftest` で確立した作法）: **正常 / 不在 / 壊れている**の 3 状態を作る。
> ★ `receipt_free_resumption_has_no_pflow_dependency` は「不在」側、
> ★ `cif_receipt_matches_hand_computation` は「壊れている」を検出する側。

### 回帰テスト

- ★ `cargo run --bin gse-replay -- tests/fixtures/minimal.ndjson --snapshot tests/snapshots/minimal.json`
  → ⚠️★★★ **`FeatSnapshot` 列は不変なので byte-equal のまま通るはず。**
  ⚠️ **通らなければ Stop 条件**（requirement.md）。
- ★ `cargo run --bin emit_schema` の出力が `src-tauri/schema/current.json` と byte-equal。

### E2E

- ★ **不要**（⚠️ UI にも `InterventionDecision` にも出さない＝ AC-4）。

---

## ロールバック計画

- ★ **単独コミット 3 本に割る**:
  1. `chore(metrics): AWAY_IDLE_MS を pub 化して SSOT を 1 つにする`
  2. `refactor(metrics): recovery 系識別子を pflow_exit 系へ改名する`（★ **挙動不変**）
  3. `feat(metrics): receipt_free_resumption を追加する`（★ 新規のみ）
- → ★ **2 が問題を起こしたら 2 だけ revert できる**（★ 1 と 3 は独立）。
- ⚠️ `HMM_VERSION` を触らないので、**ゴールデンの巻き戻しは発生しない**。
