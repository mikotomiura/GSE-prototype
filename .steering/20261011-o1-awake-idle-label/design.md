# 設計: o1-awake-idle-label（長い無入力の前処理）

## 意味（1 文で）

`feat` 行が途切れずに続いていても、入力と入力の間（ファイルの最初と最後を含む）が `idle_trim_input_gap_ms`（30 分）以上空いたら、その間の `feat` 行を「入力ファイルに無かった」のと同じに扱う。v1.2 の idle trim と同じ場所（`feat_ts` を作った直後）で、同じ元の `feat` 列について決め、落とす行は 2 つの規則の和集合とする。

- 原因のラベルは作らない（離席・休憩・就寝と呼ばない）。キー名にも原因を入れない。
- 入力は v1.2 §6.1 と同じ `key` 行（押下・解放とも）と `pointer_bin` 行（判断 6）。

## 規則（純関数）

`analysis/feat_offline/idle_trim.rs` に足す:

```text
input_gap_trim(feat_ts, input_ts, file_first, file_last, min_input_gap_ms) -> (kept_feat_ts, IdleTrimSummary)
```

`file_first` / `file_last` は前処理の前の `feat` 列の最小・最大の時刻（呼び出し側は idle trim の後の列を渡すので、境を別に渡す）。

1. 入力の時刻を昇順に並べる（範囲の外の入力も残す）。最初の入力が `file_first` より後のときだけ頭に `file_first` を、最後の入力が `file_last` より前のときだけ末尾に `file_last` を置く（点の列が昇順になる。code-reviewer L-8 で直した）。
2. 隣り合う 2 点 `a < b` の差 `b − a` が `min_input_gap_ms` **以上**なら、その間を落とす区間とする:
   - `a` が入力なら、`R` = `a` 以上で最初の `feat` 行（最後の入力を含む秒の行・v1.2 判断 6 と同じ）を残し、`R < t` の行を落とす。`a` が `file_first` なら、`file_first ≤ t` の行を落とす。
   - `b` が入力なら、`t < b` の行を落とす（`b` を含む秒の行 = `b` 以上で最初の行は残る）。`b` が `file_last` なら、`t ≤ file_last` の行を落とす。
3. `min_input_gap_ms = 0` なら何も落とさない（新しい前処理なしの実行 = v1.2 の主と同じ）。
4. 入力が 1 本も無いファイルは、`file_last − file_first ≥ min_input_gap_ms` なら全行を落とす。

長さは壁時計で測る（区間の中に `feat` 行の穴があっても差し引かない）。研究者のメモ「30 分以上打っていなければ」に合わせる。

`IdleTrimSummary`（既存の型を使い回す）: このステップで新たに落とした行の数と、落とした区間の列（1 本 = 1 つの無入力区間）。idle trim が先に落とした行は数えない。

### idle trim との関係

- 2 つとも元の `feat` 列と入力だけで決まる（idle trim は `feat` 行の穴、こちらは入力の間隔）。idle trim の後の列に掛けても、`file_first` / `file_last` を元の列から渡せば、落ちる行の集合は和集合と同じになる（idle trim は入力を含む秒の行を落とさないので `R` も変わらない）。
- 封筒は `provenance.idle_trim`（v1.2 のまま）と、新しい `provenance.input_gap_trim`（`dropped_feat_rows` と `spans`・idle trim が落とさなかった行だけ）。削った行の合計は 2 つの和。

## 値（凍結 JSON 1.2.0）

| キー | 運用値 | 探索空間 | 役割 |
|---|---|---|---|
| `idle_trim_input_gap_ms` | `1800000` | `{0, 1800000}` | 感度のみ |

- 検査: `0` か、`idle_trim_min_gap_ms` 以上かつ 24 時間以下。`idle_trim_min_gap_ms`（60 秒）より短い無入力を「作業していない」とみなすと、P1 が見たい停滞（`W` = 30 秒）そのものを削るため。
- 感度の実行は 5 → 6（`idle_trim_input_gap_ms=0` の 1 本 = v1.2 の主と同じ前処理）。選択の格子 27 通りは変わらない。

## 配線（`src-tauri/src/bin/replay.rs`）

- `P1Operational` を 11 キーに（`P1_OPERATIONAL_KEYS` / `as_pairs` / `apply_set` / `validate`）。
- `--features` 経路: `idle_trim` の直後に `input_gap_trim` を呼ぶ（入力の時刻は同じ `idle_trim_input_ts` を使う）。`file_first` / `file_last` は `idle_trim` の前の列から取る。
- 封筒: `config` に 1 値。`provenance.input_gap_trim`。

## 文書

- `docs/preregistration-p1-episode.md`: 冒頭に v1.3 改訂宣言（判断 1 の「研究者の実走〔本番外〕を見て決めた」・P1 の本番データは見ていない）。末尾に §7（規則・運用値・探索空間・読み方・代償）。
- `scripts/check_prereg_parity.py`: §7 の表も読む。
- ADR-030 補訂 5。
- `docs/glossary.md`「無入力の末尾の前処理」に追記（または新項）。`docs/functional-design.md` の P1 の特徴行の節。

## テスト

- `idle_trim.rs`（先に書いて赤を確かめる）: 長さの境界（`G − 1` / `G`）・最後の入力を含む秒の行を残す・次の入力を含む秒の行を残す・ファイルの最初と最後・入力が無い・`G = 0` で恒等・範囲の外の入力・`feat` の穴を含む区間・idle trim と合わせて和集合になる。
- `replay.rs`: 凍結値・`--set idle_trim_input_gap_ms=0` が overrides に出る・`validate` の境界・封筒の `provenance.input_gap_trim`・`prereg_version` 1.2.0。
- `src-tauri/tests/p1_restart_default_config.rs` などの既存の期待値（30 分の無入力を含まなければ変わらない見込み・実測で確かめる）。
- Python: `check_prereg_parity.py`（§7・自己検査の変異）・`p1_run_grid.py`（感度 6）・`p1_features_io.py`（3 極の一致に `input_gap_trim`）・`scripts/tests/`。
- 実走ファイル 3 本（repo の外）: 前処理あり・`idle_trim_input_gap_ms=0` で、観測区間の合計と落とした量を比べる（読むのは封筒だけ）。

## 変更しないもの

- 検出器（`stall_onset.rs`）・`HMM_VERSION`・アプリ・スキーマ。v1.2 の idle trim の規則と値。
