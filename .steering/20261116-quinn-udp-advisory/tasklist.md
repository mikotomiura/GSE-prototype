# タスクリスト

- [x] origin/main から worktree と枝 chore/quinn-udp-advisory
- [x] 依存の経路と、コンパイルされるかの確認（されない）
- [x] Cargo.lock の 2 行を書き換え・`cargo metadata --locked`
- [x] cargo-audit 0.22.2 を入れ、監査スクリプトを対照つきで回す（before exit 1 / after exit 0）
- [x] `cargo test --locked --workspace`・gse-replay
- [x] /cross-review（code-reviewer と Codex）
- [x] target を消す
- [ ] コミット（push・PR・マージは研究者に確かめる）
