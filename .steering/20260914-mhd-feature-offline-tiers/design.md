# 設計 — タスク 2（Mh-D 特徴量の Tier 別オフライン実装）

> ★ **issue 単位の設計は `_issue-plan.md` と `issues/00X.md` が持つ。**
> ここに書くのは **全 issue に共通する骨格**だけ。判断の根拠は `decisions.md`。

## 実装アプローチ

```text
NDJSON ──▶ bin/replay.rs (--features)  ──▶ analysis/feat_offline/
             ★ 既存 loader (ReplayEvent) と       mod.rs      … FeatureRow と tick ループ
               仮想時刻グリッドを再利用            activity.rs … T0
                                                  boundary.rs … T1b
                                                  dispersion.rs … T1a
                                                  revision.rs … T1c
                                                  stall_onset.rs … t0 検出器
                                                  restart.rs  … T1d
                                                  quality.rs  … Q
```

- ★ **計算本体はすべて `analysis/` の純関数**（⚠️ OS API を呼ばない。`architecture-rules`）。
- ★ CLI は `bin/replay.rs` にモードを 1 本足すだけ（★ `--sweep` / `--nudge-diag` と同じ増築の前例）。
- ⚠️★★★ **`features.rs` / `engine.rs` / `loop_step.rs` は読むだけ**（★ ADR-030 **D1**）。

## 出力の形（★ `decisions.md` 判断 2）

```json
[
  { "t_ms": 30000,
    "activity":    { "keys": 42, "deletes": 3, "pastes": 0, "mean_iki_ms": 180, "pauses": 2, "net_production": 39 },
    "boundary":    { "prev_cat_counts": {…}, "next_cat_counts": {…}, "space": 7, "enter": 1,
                     "sentence_punctuation": 2, "ime_dwell_ms": 0, "ime_nav": 0, "ime_abandon": 0 },
    "dispersion":  { "pause_p50_ms": 320, "pause_p90_ms": 1800, "pause_max_ms": 4200, "iki_cv": 0.7, "surprise": 1.2 },
    "revision":    { "delete_run_max": 3, "delete_runs": 1, "rewrite_count": 0, "redelete_count": 0,
                     "loop_depth_max": 0, "local_recurrence": 0.0 },
    "stall_onset": { "is_onset": false, "s_ms": null, "t0_ms": null, "theta_person_ms": 2100,
                     "task_kind": "writing", "phase": "unspecified" },
    "restart":     { "post_t0_inserts": null, "post_t0_deletes": null, "post_t0_navigations": null,
                     "restop_ms": null, "stable_generation_ms": null },
    "quality":     { "capabilities": {…}, "hook_health": {…}, "missing_reasons": [], "observability_mask": {…} } }
]
```

⚠️★★★ **欠けているものは `null`。0 で埋めない**（★ `.idea/survey:194`「**欠測を 0 として入力せず、
推論の抑制・abstention に使う**」）。

### ⚠️ 命名規約（★ 衝突を避けるため）

★ ADR-030 は **`t0` を `stall onset` の時刻**の意味で使い、**`T0` を Tier 名**として使う。
→ ⚠️ **フィールド名に `T0` 系の綴りを使わない。** ★ Tier はブロック名（`activity` など）で呼ぶ。
（★ `docs/glossary.md` の「Tier のブロック名」に登録済み）

## 変更対象

### 新規作成
- `src-tauri/src/analysis/feat_offline/mod.rs` ほか Tier ごとに 1 ファイル（★ 詳細は `_issue-plan.md`）

### 修正
- `src-tauri/src/bin/replay.rs` — `--features` モード（★ issue 001 のみ）
- `src-tauri/src/analysis/mod.rs` — `pub mod feat_offline;`（★ issue 001 のみ）

### ⚠️ 触らない
- `features.rs` / `engine.rs` / `loop_step.rs` / `schema_dto.rs` / `logger.rs` / `capabilities.rs`
- `HMM_VERSION` / `tests/snapshots/*.json` / `docs/preregistration-v0.3.md`

## 影響範囲

| 影響先 | 内容 | 対処 |
|---|---|---|
| ゴールデン replay | ⚠️ `bin/replay.rs` を触るので経路に隣接する | ★ `verify.test` の後段でゴールデンを**毎 attempt** 回す |
| `emit_schema` parity | ★ `schema_dto.rs` を触らないので影響しない | ★ 触ったら Stop Condition |
| `gse-dataset` | ★ `--features` の出力は**共有しない**（中間成果物） | ★ `docs/development-guidelines.md` §10 のとおり `metrics.json` だけが共有物 |
| `analysis/` の OS 非依存 | ★ 純関数のみ | ★ `architecture-rules` |

## 既存パターンとの整合性

- ★ `analysis/intervention_eval.rs` / `calibration_eval.rs` / `cohort.rs` と同じ
  「**production 不変・OS API 非依存の後付け解析**」パターン。
- ★ テストは各モジュール内の `#[cfg(test)] mod tests`（★ `replay.rs` のゴールデン検証も同じ形）。

## テスト戦略

| 層 | 何を見るか |
|---|---|
| 単体（`#[cfg(test)]`） | ★ **正しさ**（手計算との一致・境界値・因果性・禁止事項） |
| `acceptance.sh` | ★ **出力に出ていること**と**退化していないこと**（⚠️ `cargo test` が見ない部分） |
| ゴールデン replay | ★ **既存経路を 1 mm も動かしていないこと** |

⚠️★★★ **`cargo test` が無条件に緑になる issue では AC 未充足のまま `issue_done` になる**
（★ `loop-run.sh` のコメント逐語）→ ★ **全 7 本に `acceptance.sh` を書いた。**

## ロールバック計画

★ 全 issue が **追加のみ**（新規モジュール ＋ 新モード）なので、
`analysis/feat_offline/` の削除 ＋ `replay.rs` / `analysis/mod.rs` の 2 行の revert で戻る。
⚠️ 既存の推定経路・schema・snapshot を 1 バイトも変えていないので、revert の影響は
`--features` が消えることだけ。
