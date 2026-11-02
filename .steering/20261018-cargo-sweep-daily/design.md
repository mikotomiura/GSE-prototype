# design

## 採らなかった案: target をワークツリー間で共有（`CARGO_TARGET_DIR`）
依存の重複そのものは消えるが、採らない。
- `release/gse-replay` などが**最後にビルドしたワークツリーの物で上書きされる**。実験が別ブランチのバイナリで走りうるため、再現性の規約に反する
- `scripts/run-calibration-cohort.sh`、`scripts/install-researcher-tools.sh`、`experiments/*/run.sh` が `src-tauri/target/release/...` を直接参照している
- `.steering/20260926-p1-main-prep` は `resource_isolation: per-worktree` を前提にしている

`CARGO_INCREMENTAL=0` も採らない（自分のコードを直すたびの再ビルドが遅くなる）。

## 変更対象
- `scripts/maintenance/gse-cargo-sweep.sh`: `KEEP_DAYS` の既定を 3 に変更。ワークツリーを列挙するようにし、`prune_incremental` を追加
  - 旧コードの `[ local ] && swept_local=1 || swept_runner=1` は、3 本目以降の対象をランナー扱いにしてしまう。そのため `elif` に直した
- `scripts/maintenance/install-cargo-sweep-launchd.sh`: plist から `Weekday` を外し、毎日 03:00 に実行
- `scripts/maintenance/README.md`: 「週次」の記述を更新

## テスト戦略
実機で `bash scripts/maintenance/gse-cargo-sweep.sh` を実行し、ログで全ワークツリーと rc を確認する。
launchd への再登録（`install-cargo-sweep-launchd.sh`）は auto mode で `launchctl` がブロックされるため、研究者が手動で行う。
