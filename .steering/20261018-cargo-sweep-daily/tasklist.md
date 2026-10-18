# tasklist
- [x] 原因の実測（incremental のセッション数・ワークツリーごとの target・sweep の対象範囲）
- [x] 共有 target 案の影響調査（直接パスを参照するスクリプトと per-worktree 前提）→ 不採用
- [x] gse-cargo-sweep.sh の改修
- [x] インストーラを毎日実行に変更、README を更新
- [x] 実機で 1 回実行（rc=0・19.0Gi → 19.3Gi・全ワークツリーを走査）
- [ ] 研究者: `bash scripts/maintenance/install-cargo-sweep-launchd.sh` で再導入（launchctl）
