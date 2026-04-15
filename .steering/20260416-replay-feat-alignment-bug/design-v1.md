# 設計 v1 (初回案、/reimagine で退避): 調査アプローチと計測計画

> 本ファイルは `/reimagine` Step 1 で `design.md` から退避した初回案。
> 参照しない (Step 2 の宣言)。比較用に保存。

## 調査戦略

「現象の観測 → 内部状態の観測 → 仮説棄却による絞り込み」を順に。コード読解と実測を**並列**で進める。

## Phase 1: コード読解 (subagent 並列)

### 読むべきファイル
- `src-tauri/src/bin/replay.rs` 全量 (特に `run_replay()` 338 行付近〜)
- `src-tauri/src/analysis/loop_step.rs` の `step()` と `FeatSnapshot` struct
- `src-tauri/src/analysis/metrics.rs` の `nearest_feat()` / `compute_session_metrics()`
- `ENGINE_TICK_MS` 定数の値と使用箇所 (grep)

### 抽出したい情報
- feat 発生条件 (tick 到達時のみ? key 入来時のみ? both?)
- timestamp の付与ロジック (`t` は何から来るか: system clock / event ts / session_start + offset)
- replay 時の時間進行モデル (virtual clock vs wall-clock)
- Mac baseline が動いた経緯 (コミットログから)

## Phase 2: 実データ計測

### 入力
Windows セッション `C:\gse-dataset\raw\P000\gse_20260415_144120.ndjson` (user_label 6, feat 96, key 224)

### 計測1: 再生成 feat の timestamps を取り出す
`gse-replay --snapshot <tmp>.json` で regenerated feats を JSON ファイルに吐く手段があるか確認。なければ新規に `--dump-feats` フラグ追加 or 一時的に眼検で `eprintln!` 差し込み (デバッグ専用)。

### 計測2: timestamp 比較

| データ | 計測内容 |
|---|---|
| 元 NDJSON feat (96 件) | `t` 列を抽出、隣接 gap を見る |
| 再生成 feat | `t` 列を抽出、同セッションの label と差分 |
| label | 6 件の絶対時刻 |

### 計測3: 最小再現
手書き NDJSON (meta + 数個の key + 1 user_label) で再現を試み、依存パラメータを削減。

## Phase 3: 仮説検証

| 仮説 | 検証コマンド | 棄却条件 |
|---|---|---|
| H1 固定スケジュール | 再生成 feat gap が厳密に ENGINE_TICK_MS か | gap が元 NDJSON と同一なら棄却 |
| H2 label 除外影響 | label 行を NDJSON から除いた場合に feat 列が変化するか | 変化しないなら棄却 |
| H3 OS 差 | Mac baseline NDJSON で同じ再生成 feat 列差を確認 | Mac で差が無ければ Windows 固有 |
| H4 session_start 起点 | meta の session_start を変えて実行 | 影響無しなら棄却 |

## Phase 4: 修正判断

### Cheap な修正例
- `metrics.rs` の `nearest_feat()` が元 NDJSON feat を使うよう変更
- `LABEL_MATCH_WINDOW_MS` を ENGINE_TICK_MS 以上に緩める (例: 2000ms)

### Hard な修正
- replay の feat 再生成ロジックを元 NDJSON feat と同じ timestamp に揃える
- step() の feat 発生モデルを wall-clock ベースから event-ts ベースに変更

## 変更対象 (fix する場合)
- `src-tauri/src/analysis/metrics.rs`
- `src-tauri/src/bin/replay.rs`

## 影響範囲

| 影響先 | レベル | 根拠 |
|---|---|---|
| Phase 1 metrics 全般 | HIGH | 元 feat を破棄していたなら全セッション数値が変わる可能性 |
| `baseline_metrics.md` (Mac n=2) | HIGH | 数値再計算が必要 |
| `gse-dataset/metrics/P000/*` | MEDIUM | metrics JSON を再生成 push |
| gse-replay snapshot 回帰テスト | LOW | tests/snapshots/minimal.json は再生成 feat を expected として保持しているので不変 |

## テスト戦略

TDD 順序:
1. 失敗する統合テスト: `gse_20260415_144120.ndjson` (or 最小再現 fixture) を gse-replay に通して「warnings が空 OR support > 0」を期待
2. fix 実装
3. 既存 51 tests の全 PASS 確認
4. 上の統合テストを PASS に

## 既知の Open 点
- replay.rs コメントは「再生成」を明記しており、**意図的設計**の可能性
- Mac baseline は偶然動いたのか、Windows 特有か不明
