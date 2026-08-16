# レビュー結果と対応（2026-08-16）

★ 3 系統を独立に走らせた: **`code-reviewer`** ／ **`security-checker`**（並列）／ **Codex**（`/cross-review` 相当）。

> ⚠️ `/cross-review` コマンドは**そのままでは使えなかった**。★ 理由: 同コマンドは `git diff`（全体）を
> 対象にするが、本 repo には**他タスク由来の未コミット変更が 27 件**あり、
> (i) 2814 insertions で `manual_approval_threshold_lines` 2000 を超える、
> (ii) `scripts/secrets-filter*.sh` がファイル名の `secret` にマッチして Step 2 の fail-closed に当たる。
> → ★ **`scripts/run-codex-review.sh -- <paths>` を直接呼び、本タスクのパスだけに限定した**
> （★ wrapper が公式に受け付ける形。★ `secrets-filter.sh` は **exit 0**＝`--ack-filtered` は使っていない）。

---

## ★★★ 契約の検証（3 系統すべてで一致）

★ **「記録するだけで HMM にも X/Y 合成式にも 1 バイトも流さない」は破られていない。**

- `engine.rs` / `intervention.rs` の diff は **空**
- `HMM_VERSION` = `0.3.0` のまま
- golden 4 本の差分は **新フィールドの追加のみ**（`p_*` / `raw_*` / `ewma_*` / `obs` / `f1`〜`f6` は不動）
- 新フィールドを読む本番コードは **ゼロ**

---

## HIGH（★ 2 件・いずれも対応済み）

### H-1: `keys` は「今から遡る 30 秒窓」ではない —— **沈黙中は凍結してくり返される**

- **指摘元**: `code-reviewer`
- ★ **一次で確認した**（`features.rs`）: `cutoff = last_ts.saturating_sub(30_000)` の `last_ts` は
  **バッファ最後のイベント時刻**であって `now_ms` ではない。★ `extractor.reset()` は
  **IME pause 遷移でしか呼ばれない**ので、通常の沈黙ではバッファが残り続ける。
- ★ **実測**: `deep_silence.json` は `t=…008000` 〜 `t=…051000` の **44 行連続で `keys=12, bs_keys=2`**。
  ★ 打鍵ゼロの 43 秒間、同じ 12 打が毎秒書かれている。
- ⚠️★★★ **私が書いた doc（「ウィンドウ内の総キー押下数」）とテスト名
  （`..._are_scoped_to_the_30s_window`）は、この事実を誤って伝えていた。**
  ★ このまま golden と gse-dataset に焼き付いていたら、
  **`progress_proxy` を feat 行ごとに積分する消費者が同じ打鍵を数十回二重計上する**。
- ★ **対応**:
  1. ★ **意味の正本を `loop_step.rs` の `FeatSnapshot::keys` doc に一本化**し、実測つきで
     「累積でない／窓の右端は最後の打鍵時刻／**行をまたいで足し上げるな**」を明記。
     ★ 他 4 か所（`features.rs` / `schema_dto.rs` / `logger.rs` / `replay.rs`）は
     1〜2 行に縮めて正本を参照（★ LOW 指摘「同趣旨が 5 箇所に逐語重複」も同時に解消）。
  2. ★ テスト名を `tier0_key_counts_use_the_30s_window_ending_at_the_last_event` に改名。
  3. ★ **凍結挙動そのものを固定するテストを追加**
     （`tier0_key_counts_freeze_while_silent_because_the_window_follows_the_last_event`）。
  4. ★ **解析側が読む場所にも書いた**: `docs/development-guidelines.md §10.3.2` を新設。
- ⚠️ **`keys_window_end_ms` の追加は見送った**（★ 研究者判断 D3 のフィールド構成を変えるため）。
  → ★ 窓の右端は同じ NDJSON の `key` 行から復元できる。**T0-Q6 として次に渡す**。

### H-2: `window_keys` 退避（本変更の中核判断）が**どのテストでも観測できなかった**

- **指摘元**: `code-reviewer`
- ★ 一次で確認した: `loop_step.rs` は **419 行で `#[cfg(test)] mod tests` が 1 つも無かった**。
  ★ golden 側も、SilencePath 行を持つのは `phase1_ime_heavy` の 6 行だけで、**全行 `keys=0`**
  （★ バッファ空なので実測値も 0 ＝ 差が出ない）。
  → ⚠️★★★ **`window_keys` を `log_features.keys` に戻しても golden は byte-identical で全テスト緑だった。**
- ★ **食い違う条件**: SilencePath の分岐条件は `f1 == 0.0` であって**バッファ空ではない**。
  ★ 全フライトタイムが 2000ms 以上なら `f1 == 0.0` かつ `keys > 0` になる。
- ★ **対応**: `loop_step.rs` に `mod tests` を新設（4 件）。
  - `silence_path_with_nonempty_buffer_records_measured_key_counts`（★ 中核）
  - `silence_path_with_empty_buffer_records_zero_key_counts`
  - `typing_path_records_measured_key_counts`
  - `engine_output_is_invariant_to_tier0_key_counts`（★ 下記 M-4）
- ★★★ **変異テストで実効性を確認した**: `keys: window_keys` を `keys: log_features.keys` に
  差し替えると、★ **狙いどおり当該テストだけが `left: (0, 0) / right: (3, 1)` で落ちた**（★ その後復元）。

---

## MEDIUM（★ 5 件・すべて本タスクで消化）

| # | 指摘元 | 内容 | ★ 対応 |
|---|---|---|---|
| M-1 | `security-checker` | ⚠️★ **`anonymize.rs` は allow-list でなく passthrough** —— `feat` に足したフィールドは**匿名化のレビューを経ずに `.age` バンドルへ載る**。今回の 2 値は無害だが、CD1 の防御が producer 側の注意力だけに依存している | ★ **`anonymized_feat_line_field_set_is_pinned` を追加**。`schema_dto::LogEntryDto::Feat` から実際に行を作り、匿名化後の**キー集合を固定** ＋ **`type` 以外が全部数値**（＝本文性のある文字列がゼロ）を assert。★ 以後 `feat` に足すと**必ずこのテストが落ちてプライバシー判断を踏む** |
| M-2 | `code-reviewer` | `format_feat_line` が **17 引数中 13 個が連続する `f64`** で、呼び出し側で `p_inc`/`p_stuck` を入れ替えてもコンパイルが通る | ★ **`struct FeatLine` に束ねた**。書き出し側は field init shorthand なので**名前が合わないとコンパイルが通らない**。★ `#[allow(clippy::too_many_arguments)]` も不要になった |
| M-3 | `code-reviewer` + Codex | 旧ログ欠測 → `0` の注意書きが **Rust の doc にしか無い**。実際の消費者は Python/DuckDB 側 | ★ `collect_logged_feats` が欠測行数を数えて **`tracing::warn!` を 1 回出す**（`Do NOT compute progress_proxy from this session`）。★ 加えて `docs/development-guidelines.md §10.3.2` に表で明記 |
| M-4 | `code-reviewer` | `Features` が「5 特徴量」から「5 特徴量 ＋ 非特徴量 2」の混成型になり、⚠️★★★ **`engine.rs` が読み始めるのを止めるものが散文の doc しか無い** | ★ **`engine_output_is_invariant_to_tier0_key_counts` を追加**。`keys`/`bs_keys` **以外が同一**の 2 つの `Features` を HMM に通し、`raw_*`/`ewma_*`/`obs`/`alpha`/`p_*` が **`to_bits()` で bit-identical** であることを assert。★ 散文の契約が実行可能な契約になった |
| M-5 | Codex | `bs_keys > keys` の入力検証が無い。⚠️ 壊れた NDJSON で将来 `keys − bs_keys` が **u64 underflow** する | ★ `TryFrom<LoggedFeatDto>` に不変条件を追加（★ 既存の NaN/範囲検証と同じ層）。★ 境界（`bs_keys == keys`）と旧ログ（`0/0`）は通ることをテストで固定 |

---

## LOW（★ 対応済み）

- ★ `ewma_x: 0.11115` は f64 の二進表現に依存して読み手を誤らせる → **`0.25` に変更**。
- ★ 同趣旨の警告文が 5 ファイルに逐語重複 → **正本 1 か所 ＋ 参照**に整理（H-1 と同時）。
- ★ tasklist のチェックボックス未更新 / `golden-regeneration.md` が untracked → **本コミットで解消**。
- ★ `gse-dataset` 側が未コミット → **本コミットと同時に commit**（⚠️ **push は研究者**）。

---

## ⚠️★ 付随して見つかった既存の誤り（★ 本タスクの変更とは無関係）

★ `src/bin/replay.rs` の golden 一覧コメントは
**「`deep_silence` は … バッファ枯渇後の SilencePath (`make_silence_observation`) の両方を踏む」**
と書いていたが、⚠️ **これは事実ではない**。

★ 実測（4 本の `f1` の値集合）:

| golden | `f1` の値集合 | 経路 |
|---|---|---|
| `deep_silence` | **`[150.0]`** | ★ **全 51 行 TransitionPath**（SilencePath を踏まない） |
| `minimal` | `[140.0]` | TypingPath / TransitionPath |
| `category_coverage` | `[120.0]` | 同上 |
| `phase1_ime_heavy` | **`[2000.0]`** | ★ SilencePath |

★ 原因は H-1 と同じ: **`FeatureExtractor` は IME pause 遷移でしか `reset()` されず、窓も
最後の打鍵に追従する**ので、沈黙が何秒続いても `f1` は 150.0 のまま。
→ ★ **コメントを実測に訂正した**（★ 挙動は変えていない）。
★ SilencePath の分岐自体は本タスクで追加した `loop_step.rs` の unit test が直接カバーする。

---

## ⚠️ 採らなかった指摘

| 指摘 | 出所 | ★ 採らなかった理由 |
|---|---|---|
| `FeatSnapshot` を `Option<u64>` にして欠測と 0 打を型で分ける | Codex / `code-reviewer` LOW | ★ tasklist が `keys: u64` を指定しており（研究者の設計）、`Option` は解析コード全体に伝播する。★ **消費者がゼロの今払うコストとしては重い**。→ ★ **T0-Q5 として次に渡す**（`decisions.md` 判断 7） |
| `keys_window_end_ms` を additive に足す／セッション累積カウンタを別に持つ | `code-reviewer` H-1 の (3) | ★ フィールド構成は研究者判断 D3 の範囲。★ 窓の右端は `key` 行から復元できる。→ ★ **T0-Q6 として次に渡す** |
| リング容量 600 の恒久対応（`register_keystroke` と同じ層で計数） | `code-reviewer` M | ★ 窓の定義に触れると特徴量が変わる＝ HMM 挙動が変わる。★ **本タスクの契約に反する**ので doc 明記に留めた。→ **T0-Q7** |
| `cargo audit` の導入 | `security-checker` | ★ 本 diff に依存の増減がゼロ。★ CI 側の別タスク |
