# タスクリスト: CI ディスク枯渇の恒久対策

## 緊急対応 (完了)

- [x] 削除前に `df -h /` と内訳を記録
- [x] `pgrep -f Runner.Worker` でジョブ非実行を確認
- [x] runner の `src-tauri/target` (2.7G) を削除 → 空き 3.0Gi
- [x] cargo registry cache/src・git checkouts を削除 → 空き 3.5Gi
- [x] ローカルクローンの `src-tauri/target` (31G) を削除 → 空き **33Gi**
- [x] リスナー生存とソース無傷を確認

## 恒久対策

- [x] `cargo install cargo-sweep` (0.8.0)
- [x] `ci.yml` の `check` に Disk guard step を追加
- [x] `actionlint` で新規指摘ゼロを確認
- [x] `~/.local/bin/gse-cargo-sweep.sh` を作成・shellcheck 通過
- [x] `local.gse.cargo-sweep.plist` を作成・`plutil -lint` 通過
- [x] スクリプトを手動実行して動作確認

## 未完 (ユーザー操作が必要)

- [ ] launchd への登録 — auto mode のクラシファイアに `launchctl` がブロックされたため
      ユーザーが手動実行する:
      `launchctl bootstrap gui/$(id -u) ~/Library/LaunchAgents/local.gse.cargo-sweep.plist`
- [ ] 孤児プロセス PID 3499 の終了 — 同じく `kill` がブロックされた。
      8/8 から 22 日ハングしている `cargo test` バイナリ (親は launchd)。`kill 3499`

## 後続タスク (PR #135 マージ後)

- [ ] sccache の CI 限定導入を検討
- [ ] `~/Library/Caches` (12G) の棚卸し — Chrome 5.7G / Claude vm_bundles 10G。
      ⚠️ アプリ終了後でないと安全に消せない
