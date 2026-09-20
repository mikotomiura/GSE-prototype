# 設計

## 実装アプローチ

`--features` の出力を **`{ provenance, config, rows }`** の 3 キー object でくるむ。
封筒は **`bin/replay.rs` が組み立てる**（`analysis/feat_offline/` は行だけを作り続ける）。

★ 理由: 封筒に載るのは **NDJSON の `meta` 行**と**入力ファイルの同一性**と
**CLI 側の設定値**であり、どれも「セッションの計算」ではなく「実行の由来」である。
`feat_offline` は OS 非依存の計算層で、ファイルパスも CLI 引数も知らない。

```
{
  "provenance": {
    "sharing": { "gse_dataset": "prohibited", "anonymized": false,
                 "absolute_epoch_ms": true, "rule": "docs/glossary.md 特徴行" },
    "tool": "gse-replay",
    "tool_version": "<CARGO_PKG_VERSION>",
    "source_basename": "instrument_rich.ndjson",
    "source_sha256": "<先頭 16 桁>",
    "session_start": 1758000000000,
    "hmm_version": "2.23",
    "app_version": "0.3.0",
    "g1_mode": null,
    "o1_mode": null,
    "keyboard_layout": null,
    "capabilities": { ... }        // ★ 判断 3: 行から移した
  },
  "config": {
    "w_ms": 30000, "q": 0.99, "b_ms": 30000, "net_diff_min": 20,
    "hole_gap_ms": 2000, "warmup_count": null,
    "max_feature_ticks": 1000000,
    "hmm_version": "2.23", "engine_tick_ms": 1000, "pause_threshold_ms": 2000
  },
  "rows": [ { "t_ms": ..., "activity": {...}, ..., "quality": {...} } ]
}
```

⚠️ `provenance.hmm_version` は **`meta` 行の値**（収集時）、
`config.hmm_version` は **この実行のバイナリの値**（解析時）。★ 意味が違うので両方載せる
（★ 一致しないことが起きうる —— 古いログを新しいバイナリで読むと起きる。それが読めること自体が目的）。

## 変更対象

### 修正するファイル

- `src-tauri/Cargo.toml` — `sha2 = "0.10"` を直接依存に追加。
  ★ **新規の供給元を増やさない**: `sha2 0.10.9` は既に `wry` / `tauri-codegen` 経由で
  ビルドツリーに入っている（`Cargo.lock:4278` 実測）。`reqwest` を足したときと同じ論拠。
- `src-tauri/src/bin/replay.rs`
  - `FeatureEnvelope` / `FeatureProvenance` / `SharingMarker` / `FeatureConfigDto` を定義。
  - `collect_meta_session_facts()` を追加（`meta` 行から `session_start` / `hmm_version` /
    `app_version` / `g1_mode` / `o1_mode` / `keyboard_layout` を取る）。
    ★ `collect_meta_capabilities` と同じ作法（まず `Value` で受ける）。
  - `sha256_prefix_of_file()` を追加（ストリーミングで読む。⚠️ 全体をメモリに載せない）。
  - `--features` 経路で `rows` を封筒に入れて直列化。
  - usage の `--features` 行を更新。
- `src-tauri/src/analysis/feat_offline/quality.rs`
  - `Quality` から `capabilities` フィールドを削除。`serialize_capabilities` を削除。
  - `quality_column` の引数を `capabilities: Option<Arc<Value>>` → `capabilities_declared: bool`。
  - モジュール doc を更新（「封筒へ移した」ことと移した先を書く）。
- `src-tauri/src/analysis/feat_offline/mod.rs`
  - `QualityInputs.capabilities` → `capabilities_declared: bool`。
- `.steering/20260914-mhd-feature-offline-tiers/issues/00{1..8}-acceptance.sh`
  - `--features` の出力を受ける行を `| jq '.rows'` にする（**1 本 1 行**）。
  - ★ 「この検査は rows だけを見ている」とコメントを足す。
  - `007-acceptance.sh` のみ、`capabilities` 関連 AC（AC6 / AC7 / AC8 / AC9 / AC10）を
    封筒側に合わせて書き換える。
- `.github/workflows/ci.yml` — 共有の門を `check` job に足す。
- `docs/glossary.md` — 「封筒」「共有の門」を追加。特徴行の行に封筒の形を追記。
- `.steering/20260914-mhd-feature-offline-tiers/blockers.md` — 起票 2 / 5 を閉じる。

### 新規作成するファイル

- `scripts/check_no_feature_output.sh` — 共有の門。
  - 既定は `git ls-files` の追跡ファイルを走査（本リポ）。
  - `--root <dir>` で任意のツリー（`gse-dataset` のクローン）に向けられる。
  - 判定は **(a) `sharing.gse_dataset == "prohibited"` を含む JSON**
    **(b) `t_ms` ＋ `activity` ＋ `boundary` ＋ `dispersion` ＋ `stall_onset` の 5 キーを
    すべて持つオブジェクトの配列**（★ 封筒を剥がされた形）の **どちらか 1 つでも当たれば赤**。
  - ⚠️ **ファイル名では判定しない**（★ `.gitignore` の名前依存が代替にならない、という起票 5 の逐語）。
- `.steering/20260920-envelope-issues/envelope-acceptance.sh` — 封筒自体の検査。
- `.steering/20260920-envelope-issues/measurements.md` — 突然変異の実測記録
  （★ `.steering/20260920-loop-foundation-fixes/measurements.md` が手本）。

### 削除するファイル

なし。

## 影響範囲

| 対象 | 影響 | 対処 |
|---|---|---|
| `gse-replay --snapshot` / `--metrics` / その他モード | **無し** | `--features` 経路だけを触る |
| `scripts/build_analysis_db.py` | **無し** | `P*/*/*.metrics.json` だけを読む（`:223` 実測） |
| `emit_schema` / `check_schema_parity.py` | **無し** | `LogEntryDto` だけが対象（`emit_schema.rs` 全 37 行） |
| ゴールデンスナップショット | **無し** | `FeatSnapshot` の配列で `--features` とは別経路 |
| issue 004 / 006 の acceptance | 配列前提だけ直す | ⚠️ 実装が無いので `.revision` / `.restart` は依然 null 前提で赤のまま |

## 既存パターンとの整合性

- `collect_meta_capabilities` の作法（「まず `Value` で受け、構造化は専用の関数が担う」）を踏襲する。
  ⚠️ `ReplayEvent::Meta` に型付きフィールドを足さない（security-checker LOW-1 の再発を避ける）。
- 出力は `to_writer_pretty` で `BufWriter` へ直接流す（判断 24・security-checker LOW-3）。
- ファイルサイズ上限（`MAX_SESSION_BYTES`）・`capabilities` の形検査は既存のものをそのまま使う。

## テスト戦略

- **単体テスト**（`cargo test --manifest-path src-tauri/Cargo.toml --workspace`）
  - `quality.rs` / `mod.rs` の既存テストを `capabilities` 削除に合わせて更新。
  - `replay.rs` に `sha256_prefix_of_file` と `collect_meta_session_facts` のテストを追加。
- **受け入れ検査**（shell ＋ jq）
  - `envelope-acceptance.sh` — 封筒の形・マーカー・`config` の値・**2 回実行のバイト同一**。
  - 既存 8 本 — 001 / 002 / 003 / 005 / 007 / 008 を**実測で緑**にする。
- **突然変異**（`measurements.md` に記録）
  - 封筒を配列に戻す → 8 本が赤になるか。
  - `sharing` マーカーを消す → `check_no_feature_output.sh` が (b) で拾うか。
  - `rows` を剥がして保存 → 同スクリプトが (b) で拾うか。
  - `t_ms` だけの JSON を置く → 赤にならないか（**偽陽性の確認**）。

## ロールバック計画

- 封筒は `bin/replay.rs` の `--features` 経路と `feat_offline/quality.rs` の 1 フィールドに閉じる。
- 戻すときは `git revert` 1 コミット。⚠️ acceptance 8 本も同じコミットに入れる
  （**分けると片側だけ戻って全部赤になる**）。
