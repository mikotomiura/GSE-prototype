# タスクリスト — Epic 1

## 前提確認
- [x] git fetch・PR #69/#70 が origin/main にマージ済みを確認
- [x] Phase1 未完を確認（reminder 未デプロイ・GATE2 FAIL）→ 研究者に着手承認を得た
- [x] main から worktree/branch `docs/post-phase1-epic1` を作成（GAS 作業を温存）
- [x] §1 材料を読了（Epic0 4点 / 改善設計書 / research-positioning §1/§8/§9 / wbs §改訂予定 / references 書式）
- [x] /start-task で steering 作成

## SSOT 昇格（docs/architecture/）
- [x] `docs/architecture/gse-v2-overview.md`
- [x] `docs/architecture/domain-adapter-boundary.md`
- [x] `docs/architecture/intervention-decision-engine.md`

## ADR 起票（docs/adr/）
- [x] `docs/adr/README.md`（索引・ステータス凡例）
- [x] `docs/adr/ADR-006-task-kind-beta-wiring.md`（★最優先・最詳細）
- [x] `docs/adr/ADR-001-hmm-as-writing-baseline.md`
- [x] `docs/adr/ADR-004-decision-engine-boundary.md`
- [x] `docs/adr/ADR-007-receptivity-decomposed-vs-unified.md`
- [x] `docs/adr/ADR-002-domain-local-inference.md`
- [x] `docs/adr/ADR-003-accountability-outside-core.md`
- [x] `docs/adr/ADR-005-event-envelope-versioning.md`

## 検証
- [x] コードゼロ変更を確認（git diff に src-tauri/ src/ が無い）
- [x] 相互リンク・引用 [Pn]/[Vn] の実在チェック（9 件全て references.md に実在）
- [x] /finish-task（Step1-3 実行・schema parity skip・test/security は docs-only で N/A）
- [x] /cross-review（Codex 独立レビュー）→ 有効指摘4件を反映（enum 8変種・pure化容易の弱化・ADR-006/002 の2段階bump明確化・Gate D見出し）。誤検知1件（Codex が別ツリー参照）
- [x] IME 誤解防止の注記を ADR-006 に追加（日本語IMEデータ収集・dataset公開は全案で保全）
- [ ] コミット（ユーザー承認待ち）
- [x] ADR-006 推奨・研究者判断待ち点を完了報告に明記
