# 設計 —— issue 004（`revision.rs`）/ 006（`restart.rs`）

> ★ 裁定の根拠は `decisions.md`（判断 1〜4）。⚠️ ここには**実装の形**だけを書く。

## 1. `revision.rs`（`T1c` = 削除と挿入の遷移の形）

### 入力の正規化（★ AC3「引数が `KeyCategory` と時刻だけ」を構造で満たす）

```text
&[KeyPress]  --(境界のアダプタ)-->  Vec<CategorizedPress { t_ms, category: KeyCategory }>
                                    ★ 純関数はこれだけを受け取る（vk を見ない）
```

- `KeyCategory` は `crate::analysis::anonymize::KeyCategory::from_vk`。
  ★ `replay.rs::category_representative_vk` が `from_vk` の逆であることは既存テストが固定しており、
  **匿名化 NDJSON でも raw でも同じ category が出る**。
- 挿入系 / 削除系の判定は `KeyCategory` から引くが、
  ⚠️ **`mod.rs::key_net_delta`（ADR-030 D3 の SSOT）と全 VK で一致することを単体テストで固定する**
  （`category_class_matches_key_net_delta`）。★ 新しい分類を作らない（判断 1 の「却下した細部」）。

### 走りと burst

```text
burst   : super::extract_pause_resumptions（features::PAUSE_THRESHOLD_MS）で切る極大の press 列
走り    : burst の中で、削除系 press が連続する極大列（U1: 削除系以外はすべて切る / U4: 長さ 1 から）
走りの閉じ: 次の削除系以外の press の時刻 ／ 無ければ burst の閉じ
burst の閉じ: 最後の press + PAUSE_THRESHOLD_MS
```

### tick への帰属（U3・判断 1 の細目）

| フィールド | 単位 | 載せる tick | 単位が無い tick |
|---|---|---|---|
| `delete_runs` | 走り | 走りの閉じ | `0` |
| `delete_run_max` | 走り | 走りの閉じ | `null` |
| `del_to_ins_transitions` | 遷移 | 遷移を確定させた挿入系 press | `0` |
| `delete_runs_after_first_in_burst` | 走り | 走りの閉じ | `0` |
| `di_alternations_max` | burst | burst の閉じ | `null` |
| `category_bigram_repeat_rate` | burst | burst の閉じ | `null` |

⚠️ 閉じがグリッド外の単位は捨てる（`stall_onset::column_from_onsets` と同じ規約）。

### 算出式

- `di_alternations`（burst 単位）: press 列から挿入系 / 削除系だけを残し、
  隣接する同じ記号を潰した列の長さ − 1（★ 0 以上。D/I が 0 個なら `0`）。
- `category_bigram_repeat_rate`（burst 単位）:
  `1 − (相異なる bigram の種類数 / bigram の総数)`。bigram が 0 個なら `null`（U2）。

## 2. `restart.rs`（`T1d` = 再開）

### `stall_onset.rs` から出すもの（V2）

```rust
pub(super) struct ConditionAInterval {
    pub a: u64,
    pub b: u64,
    /// 変化点だけ (時刻, 条件 A の値)。先頭はこの区間の最初の評価時刻とその値。
    pub changes: Vec<(u64, bool)>,
    /// この区間で確定した onset (s 昇順)。
    pub onsets: Vec<ConfirmedOnset>,
}
pub(super) fn condition_a_timeline(keys, feat_ts, config) -> Vec<ConditionAInterval>
```

- ⚠️ **検出のアルゴリズムは変えない** —— `detect_stall_onsets_for_interval` が変化点を
  **ついでに返す**ようにするだけ（★ 条件 A を二重に評価しない = V2 の目的）。
- ★ 条件 A は評価時刻の間で一定（`net` は `key t` と `key t + W` でしか変わらない）ので、
  **変化点だけで任意時刻の値を復元できる**。

### 1 行ぶんの計算（onset 行だけ）

```text
o      = t0 + config.b_ms                      ★ 値は決めない（AC4）
窓     = [o, min(同区間の次の onset の s, b+1))  ★ E2（V1）。右端 b は確定扱い（V2）
窓が無い = (o > b) または (次の onset の s <= o)  → post_t0_* / resumption_count は null（V5）

生成区間 = 条件 A が false の極大区間 ∩ [o, b]   ★ V6。r_k は開始（o にクリップ）、s'_k は閉じ
restop_ms                     = s'_1 − o        （s'_1 が無い → null）
stable_generation_ms          = s'_1 − r_1      （同上）
stable_generation_net_presses = [r_1, s'_1) の net_production（★ super::net_production）
resumption_count              = 窓の中で始まる生成区間の本数
post_t0_inserts/deletes/navigations = 窓の中の press を ADR-030 D3 の写像で数えたもの
```

- ⚠️ `r` / `s'` は **窓ではなく観測区間**で決まる（issue 006 Background「束ね方に依存しない量」）。
- ★ onset が無い行は 7 フィールドとも `null`（AC3）。

### 配線（判断 4）

```text
build_feature_rows
  ├─ stall_onset_column(...)            -> Vec<StallOnset>      （既存・変更なし）
  ├─ condition_a_timeline(...)          -> Vec<ConditionAInterval>（V2 で新設）
  └─ restart_column(&stall_onset_col, &timeline, keys, config) -> Vec<Restart>
```

⚠️ **向きは `stall_onset` → `restart` の一方向だけ**（AC7: 転帰側を検出側に渡さない）。

## 3. 付随して直すもの

- `001-acceptance.sh`: 最上位キー集合へ `restart` / `revision` を足す（★ 判断 18 の先例）。
- `006-acceptance.sh`: AC6 の fixture を `stall_onset_observed.ndjson` へ（V3）。
  ★ 「V3 が未裁定なら意図的に落ちる」という fail メッセージの注記を外す。
- `blockers.md` 起票 20: 打ち切りの**追跡時間**（V4）と E2 の過剰分割（V1 の代償）を研究者へ上げる。

## 4. テスト戦略

| AC | test |
|---|---|
| 004 AC2 | `revision::tests::delete_runs_match_hand_computed` |
| 004 AC3 | `revision::tests::revision_uses_no_text_content` |
| 004 AC6 | `revision::tests::category_bigram_repeat_rate_matches_definition` |
| ★ 判断 1 の SSOT 固定 | `revision::tests::category_class_matches_key_net_delta`（全 VK） |
| 006 AC2 | `restart::tests::restart_is_anchored_at_t0_not_pause` |
| 006 AC3 | `restart::tests::no_onset_yields_null_not_zero` |
| 006 AC7 | `restart::tests::restart_is_not_fed_into_detection` |
| 006 AC9 | `restart::tests::censored_restop_yields_null_not_zero` |
| ★ V6 の固定 | `restart::tests::generation_already_open_at_origin_clips_r1_to_origin` |
| 回帰 | `cargo test --workspace` ＋ ゴールデン replay（★ `--snapshot` は `FeatSnapshot` なので影響なし） |
