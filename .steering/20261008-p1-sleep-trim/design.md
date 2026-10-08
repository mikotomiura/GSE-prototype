# 設計: p1-sleep-trim

## 意味（1 文で）

前処理は「該当する `feat` 行が入力ファイルに無かった」のと同じに扱う。`gse-replay --features` は、`feat` 行の時刻列を作った直後に 1 回だけ削る。以後の計算（観測区間・stall onset・品質のマスク・dispersion の窓・tick の右端・封筒の `observed_intervals`）は、すべて削った後の列だけを見る。

- 別のスクリプトで行を落とした NDJSON を通した場合と、結果が一致する（判断 2 の却下案と同じ意味）。
- 原因のラベルは作らない（ADR-030 D8 (b-2)）。規則は構造だけで書く（穴の長さ・入力の有無）。キーの名前にも「sleep」を入れない。

## 規則（純関数）

`analysis/feat_offline/idle_trim.rs`（新設・OS 非依存）:

```text
idle_trim(feat_ts, input_ts, min_gap_ms, max_trim_ms) -> (kept_feat_ts, IdleTrimSummary)
```

1. `feat_ts` と `input_ts` を昇順・重複除去する。
2. 終わりの点 `h` の集合: 隣の `feat` 行との差が `min_gap_ms` 以上ある `feat` 行（穴の直前）と、最後の `feat` 行。
3. 各 `h` について、`L` = `h` 以下で最大の `input_ts`（無ければ「無い」）。`R` = `L` 以上で最初の `feat` 行（最後の入力を含む秒の行・判断 6）。`cut = max(R, h − max_trim_ms)`（`h − max_trim_ms` は 0 で飽和、`L` が無ければ `h − max_trim_ms`）。
4. `cut < t ≤ h` の `feat` 行を落とす。
5. `max_trim_ms = 0` なら `cut = h` で、何も落ちない（前処理なしの実行）。

計算: `cut` は `h` について単調非減少（`L` も `h − max_trim_ms` も単調）。各 `feat` 行 `t` について、`t` 以上で最初の `h` を二分探索で引き、その `cut < t` なら落とす（その `h` の `cut` が `h ≥ t` の中で最小なので、これで十分）。

`IdleTrimSummary`: 落とした `feat` 行の数と、落とした行のつながり（連続する落とした行の最初と最後の時刻）の列。

入力 `input_ts` は `key` 行の時刻（押下・解放とも）と `pointer_bin` 行の時刻（ビンの終端）。`ime_*` / `focus_transition` / `clipboard` / `hook_health` などは入れない（判断 1）。

## 値（凍結 JSON 1.1.0）

| キー | 運用値 | 探索空間 | 役割 |
|---|---|---|---|
| `idle_trim_min_gap_ms` | `60000` | `{60000}` | 固定 |
| `idle_trim_max_ms` | `1800000` | `{0, 1800000}` | 感度のみ |

検査（`validate`）: `idle_trim_min_gap_ms > hole_gap_ms`（穴にならない間隔で削らない）。`idle_trim_max_ms` は 24 時間以下（自己 DoS の門ではなく、桁の取り違えを止める）。

## 配線（`src-tauri/src/bin/replay.rs`）

- `P1Operational` に 2 フィールド（必須・`deny_unknown_fields` のまま）。`P1_OPERATIONAL_KEYS` / `as_pairs` / `apply_set` / `validate` を 10 キーに。
- `--features` 経路: `collect_all_feat_timestamps` の直後に、新しい収集関数で `key` 行（押下・解放とも・キーの種類を問わない）と `pointer_bin` 行の時刻を 1 回の走査で集め、`idle_trim` を呼ぶ。以後は削った列を使う。
  - `keys`（`collect_key_events`）は使わない。あちらは押下だけで、キーの種類を解決できない行を捨てるので、「最後の `key` 行」とずれる。
  - 極 B の `pointer_rows`（`collect_pointer_bin_timestamps`）は触らない（極の経路を変えない）。
  - tick の右端は「入力と `feat` 行の最大」のまま。ファイルの最後を削ると右端も縮むが、削った範囲には onset が立たないので、onset が格子の外に出ることはない（`mod.rs` の module doc の issue 008 の理由に反しない）。
- 封筒: `config` に 2 値。`provenance.idle_trim` に `dropped_feat_rows` と `spans`（`{a_ms, b_ms}` の列）。
- `--snapshot` / `--metrics` などのモードは触らない（`--features` だけ）。

## 文書

- `docs/preregistration-p1-episode.md`: 冒頭に v1.2 改訂宣言。本文の既存の節は書き換えず、末尾に「## 6. v1.2 で足した運用値と探索空間」を足す（`check_prereg_parity.py` が読む表を置く）。読み方（2 本で挟む・補正済みと呼ばない）と代償を書く。
- ADR-030 補訂 4: 補訂 1 項目 1（観測区間は `feat` 行の存在だけ）と項目 1.6（先読みの範囲）を、P1 の前処理として上書きする。
- O1 事前登録の草案: §4 の前処理の検査の近くに、この前処理への参照を足す（PR #329 の merge 後）。
- `docs/glossary.md`: 用語を足すかを確かめる（「観測区間」の項があれば追記）。

## テスト

- `idle_trim.rs` の単体テスト（先に書いて赤を確かめる）: 穴の長さの境界（59,999 / 60,000）、上限の境界、入力の種類、ファイルの最後、短い穴をまたぐ無入力の連続、入力が 1 本も無い、`max_trim_ms = 0` で恒等、`feat` の順不同・重複。
- `replay.rs`: 凍結値・`--set idle_trim_max_ms=0` で overrides に出る・`validate` の境界・封筒の `provenance.idle_trim`・`prereg_version` 1.1.0。
- `src-tauri/tests/p1_restart_default_config.rs`: 凍結の既定でファイルの最後が削られる。期待値を導き直す（導出をテストのコメントに書く）。
- Python: `check_prereg_parity.py`（§6 を読む・自己検査の変異を足す）、`p1_run_grid.py`（感度の実行が 5）、`scripts/tests/`。
- 実記録（P998・repo の外）: 前処理あり・なし・`warmup_count=10` で、観測区間と onset を比べる。

## 変更しないもの

- 検出器（`stall_onset.rs` の条件 A / B・θ・`observed_intervals`）。`key` 行の先読みゼロの検査はそのまま通る。
- `HMM_VERSION`（`engine.rs` / `features.rs` / `loop_step.rs` / `key_gate.rs` を触らない）。
- アプリ（`input/` / `lib.rs` / `logger.rs`）・スキーマ。
