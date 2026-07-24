# design — アプローチ・変更対象・テスト戦略

## A: `--snapshot` 回帰を cargo test 化
- `replay.rs` の test mod に `snapshot_path()` helper と `replay_snapshot_goldens_byte_equal` を追加。
- main の `--snapshot` 経路と**同一関数** (`run_replay` + `compare_snapshots`) を駆動し、fixture の
  現行出力をコミット済みゴールデンの**絶対値** (FeatSnapshot 構造体等価) と突き合わせる。
- 既存 `replay_anonymized_matches_raw_features*` は raw==anon の**相対**比較で絶対ドリフトを検出できない
  (両辺同時にずれる) ため本テストが独立の門になる。
- drift 時の panic メッセージに再生成コマンドと HMM_VERSION bump 時の再生成必須を明記。

## B: golden 生成 (現行凍結挙動の記録)
- `gse-replay <fixture> > tests/snapshots/<name>.json` で生成。round-trip (`--snapshot`) exit 0 と
  2 回生成の同一性 (決定論) を確認済み。
- 対象: `phase1_ime_heavy.json` (6 snaps, IME pause + 沈黙: alpha=0.15/f5/f1 floor/β-writing),
  `category_coverage.json` (2 snaps, resolve_key_vk + Other 畳み込み + obs)。
- 非決定要素なし (wall-clock/RNG 無し・`is_repeat` は cfg(windows) 限定) → flaky リスク無し。

## D: `scripts/repro.sh`
- 方針 (experiment-tracking.md §): パイプラインは再実装せず `run-calibration-cohort.sh` に委譲。
  repro.sh は集計出力に**無い来歴**を外部 sidecar として固定する薄いラッパ (凍結ファイル不触)。
- 刻む来歴: HMM_VERSION (engine.rs const から grep 抽出=ドリフト不可) / repo commit (dirty 検出) /
  dataset commit / raw NDJSON sha256 (→ data.md, 生ログはコピーしない) / rustc + Cargo.lock hash (→ env.md)。
- `experiments/<YYYYMMDD>-<name>/` に provenance.json / data.md / env.md / notes.md stub / results/ を生成。
- 委譲は `bash "$COHORT_SCRIPT"` (exec bit 非依存・git-bash/Windows 対応)。sha256 は shasum/sha256sum 両対応。

## ③: RQ-2 落合カード + references 登録
- `docs/literature/20260724-agentic-coding-overreliance-detection.md` (9 カード) + `_index.md` 行 +
  `references.md` [V45]-[V53] append (V 名前空間・append-only・renumber なし・DOI/arXiv dedup 済)。
- 判定: (a) 過信は実在し害=確定 / (b) content-free 代理→害は PLAUSIBLE BUT UNPROVEN → Epic4 は先に de-risk。

## テスト戦略
- `cargo test --release --bin gse-replay` 全 23 パス (新規 golden 回帰含む・回帰なし)。
- repro.sh は合成 dataset (calib fixtures→raw/P000) で dry-run/実走 smoke: verdict=data_insufficient (正)。
- 凍結対象の git status 変更ゼロを検証。
