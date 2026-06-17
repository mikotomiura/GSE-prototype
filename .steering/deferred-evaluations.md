# Deferred Empirical Evaluations

このファイルはセッション開始時・`/verify-setup` 時にスキャンし、
dispatch 可能な環境なら優先的に実行する。

---

## implementation-workflow — deferred 2026-06-16

- **理由**: Phase 4 の Structural-only (Iteration 0) は完了。Full tier は `/verify-setup` (Phase 9) で実施予定。
- **想定 tier**: Full（最重要 Skill — `/add-feature`, `/fix-bug`, `/refactor` の 3 コマンドが参照する DRY の要）
- **実施条件**: Phase 7 `/setup-commands` 完了後（参照元コマンドが揃ってから評価する方が実態に即している）

### シナリオ草案

1. **median**: `analysis/probe_scheduler.rs` に新しいスケジューリング戦略を追加する（`/add-feature` フロー）
2. **edge-low**: テスト 0 件のモジュール (`intervention.rs`) のバグ修正（`/fix-bug` + TDD 挿入オーバーライド確認）
3. **adversarial**: `implementation-workflow` Skill を Read せずに独力で実装しようとするエージェントが、骨格に引き戻されるか

### チェックリスト草案

- [critical] Step A で `docs/agent-shared.md` と `requirement.md` を Read した → 理由: 設計の土台
- [critical] Step C でユーザー承認を得てから Step D に進んだ → 理由: プロセス契約の核
- [critical] Step F で `cargo test --workspace` をパスした → 理由: 回帰保護の最低ライン
- Step B で file-finder と impact-analyzer を並列起動した
- Step G で code-reviewer と security-checker を並列起動した
- Step G の HIGH 指摘に対応した
- Step I のコミットメッセージに `Refs:` がある

タグ比率: 3/7 = 43% → やや高い。Full 実施時に 2 個に絞るか検討（5 項目に削減して 2/5=40%）。
