# 設計

## 実装アプローチ

置き場は `papers/public-data-findings/kit/estimator/`。自前の `[workspace]` を持つ独立 crate にし、GSE の workspace と CI から切り離す（先例 `papers/ime-observation/kit/logger/` と同じ形）。

24767c7e（作業ツリーの `src-tauri/` と同一であることを `git diff --stat` で確認済み）のファイルを、次の 3 種に分けて写す。

1. **逐語**（1 バイトも変えない）: `analysis/` の engine・features・heads/writing・heads/coding・key_gate・loop_step・intervention・feat_offline/*（9 ファイル）と `prereg/p1-episode.json`。テストも一緒に写して `cargo test` で走らせる。
2. **テストの節だけ外す**: `analysis/anonymize.rs`・`analysis/heads/mod.rs`・`analysis/metrics.rs`。テストが切り出さない部分（`schema_dto`・`probe_scheduler`）を参照するため、末尾の `#[cfg(test)] mod tests` だけを落とす。本体は逐語。
3. **新規・縮めた写し**:
   - `src/lib.rs`: `pub mod analysis; pub mod logger;` だけ。lib の名は `gse_next_lib` のままにして、replay.rs の `use` 行を変えずに済ませる。
   - `src/analysis/mod.rs`: 宣言を 9 つ（anonymize・engine・feat_offline・features・heads・intervention・key_gate・loop_step・metrics）に絞る。
   - `src/logger.rs`: `logger.rs` の `TaskKind`（`enum`・`as_str`・`parse`・`From<TaskKind> for TaskDomain`）の抜粋。抜粋の範囲は目印の行で示す。
   - `src/bin/replay.rs`: 引数なしの経路と `--features`（`--feature-config`・`--set`・`--pole`）に要る部分を残し、それ以外（`--snapshot` の比較・`--metrics`・`--segment(s)`・`--intervention`・`--sweep`・`--nudge-diag`・`--corr-floor`・`--calibration`）と、その部分だけが使う関数と、テストの節を消す。`ReplayEvent` の 24 種と `run_replay` の読み飛ばしの腕は全部残す（未知の行で落ちる挙動を変えないため）。`include_str!("../../prereg/p1-episode.json")` は同じ相対の配置にして変えない。

`metrics.rs` は縮めずに `intervention.rs` ごと逐語で持ち込む（`feat_offline` の `OutcomeConfig` の既定値を書き換える案 A は、推定器のコードに手を入れることになるので採らない）。

`Cargo.toml` は package の版を `0.1.40` にする（`env!("CARGO_PKG_VERSION")` が `--features` の封筒の `provenance.tool_version` に出るため、変えると出力が変わる）。package 名は `gse-estimator`、bin 名は `gse-replay`（封筒の `tool` は文字列で "gse-replay" に固定されている）。依存は serde（derive）・serde_json（`float_roundtrip`）・sha2・tracing・tracing-subscriber。`Cargo.lock` は `src-tauri/Cargo.lock` を写して cargo に使わない項を落とさせ、使う crate の版を本体と同じにする（serde_json 1.0.149 ほか）。ライセンスは `MIT OR Apache-2.0`（`LICENSE-MIT`・`LICENSE-APACHE`）。

元との対応は `manifest.json`（種別 file / trimmed / new・元のパス・SHA-256）と `PROVENANCE.md`（何を外したか）に書く。差分の一覧は `diff -u` で作る（`provenance/replay.rs.diff` ほか）。先例と違い、今回は GSE の推定器であることを公開物で明示する（判断 37）。

## 門（全件一致）

比べの道具 `gate/compare-replay.sh`: 置き換えの replay として各計算のスクリプトに渡す小さなスクリプト。同じ引数と入力で旧（`~/gse-public-data/klicke/bin/gse-replay`・SHA-256 `26cae610…33bb3`）と新の両方を走らせ、stdout・終了コード・stderr のバイトを比べて 1 行の記録（引数の種類・一致・不一致）を追記し、旧の出力をそのまま返す（当初は stderr を比べない案だったが、比べて一致した。下の「実装で変わった点」）。

通す計算（見た書き手だけ。中間は repo の外の一時の置き場に作って最後に消す。既存の中間とも一致を確かめる）:

- CS1 2019 年版: `experiments/20261104-cs1-landscape/scripts/build_cs1.py`（取り置きの一覧は除外にだけ使う・元の計算と同じ）と、`--set` の変種 3 つ（`rebuild_onsets.py`: q995・w15・w60）。
- CoAuthor: セッション単位（`20261031-coauthor-pre-request-signal` の変換→replay→`add_feat`→`--features`）と書き手ごとにつないだもの（`20261106-findings-paper1-exploration/scripts/coauthor_writer_onsets.py`）。
- KLiCKe: `20261101-klicke-early-stall-trigger/scripts/build_work.py`。

計算のスクリプトは書き換えない（replay のパスを引数・環境変数で渡すだけ）。凍結の SHA-256 検査を持つ `run*.sh` は通さず、中の python を直に呼ぶ。

陽性対照: 推定器の係数を 1 か所変えた新の版（作業の一時のコピー・コミットしない）で、CS1 の `--limit` の小さい範囲を通し、不一致が出ることを確かめる。

ディスクの空きが 6 GiB なので、データごとに順に回し、中間は 1 つ終えるごとに消す。

## 変更対象

### 新規作成するファイル
- `papers/public-data-findings/kit/estimator/` 一式（Cargo.toml・Cargo.lock・src/・prereg/・manifest.json・PROVENANCE.md・LICENSE-*・README.md・gate/）

### 修正するファイル
- なし（`src-tauri/` は触らない）

## 影響範囲

GSE 本体には影響しない（workspace 外・CI の対象外）。`.gitignore` に `kit/estimator/target/` を入れる。

## 既存パターンとの整合性

`papers/ime-observation/kit/logger/`（自前の `[workspace]`・逐語の写しと manifest の SHA-256）に合わせる。

## テスト戦略

- 単体テスト: 写した `analysis/` のテスト（逐語で写したもの）を `cargo test` で走らせる。
- 統合テスト: 上の門（3 データの見た書き手の全課題・引数なしと `--features` と `--set` の変種）。件数と不一致 0 を記録する。陽性対照つき。
- manifest の照合: 逐語の項の SHA-256 が 24767c7e の元と一致すること。

## ロールバック計画

`papers/public-data-findings/kit/estimator/` を消すだけで戻る。

## 実装で変わった点（2026-11-06）

- `PROVENANCE.md` は作らず、README の表と `provenance/manifest.json`（種別 file / trimmed / excerpt / cut / lock / new）と `provenance/check_provenance.py`（`--self`・`--upstream`・`--write`）にした。`Cargo.lock` は種別 lock（判断 3）。
- 比べの道具は stderr も比べる（一致した）。不一致のときだけ新しい版の終了コードと入力の SHA-256 を記録する（判断 2）。
- 門は並列 4 で回す。並列 7 ではディスクが埋まり、基準の版ごと落ちた（判断 2）。
- 門は不一致・作り漏れ・途中の段の失敗で終了コード 1、`GATE_WORK` が repo の中なら 2（判断 3）。
