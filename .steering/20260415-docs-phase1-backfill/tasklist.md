# タスクリスト — Docs Phase 1 Backfill

## 準備
- [x] 監査レポート (Explore agent) の結果把握
- [x] 該当実装 commits (461e920 / 71674f2 / e80ea33 / 2483909 / 18c47a0 / 3947927) の内容把握

## 調査
- [x] D-1: 既存 `docs/repository-structure.md` の構造を精読
- [x] D-2: 既存 `docs/functional-design.md` のセクション構成を精読
- [x] D-3: 既存 `docs/architecture.md` の構成 (Mermaid 有無、データフロー表現方法) を精読
- [x] D-4: 既存 `docs/glossary.md` の列挙順・粒度を精読
- [x] D-5: README.md / README.ja.md の既存 gse-replay セクションの位置と粒度を確認

## 実装 (HIGH)
- [x] H-1: `docs/repository-structure.md` — ディレクトリツリー更新 (新規ファイル 5 件)、依存方向に schema_dto を追加
- [x] H-2: `docs/functional-design.md` — Ground Truth 収集機構の新セクション、UC-GT1〜3 追加
- [x] H-3: `docs/architecture.md` — 主要コンポーネントに Phase 1 追加、データフロー 3 パス追加

## 実装 (MEDIUM)
- [x] M-1: `docs/glossary.md` — 新規用語 8+ 項目追加
- [x] M-2: `docs/development-guidelines.md §3` — 範囲区分表に `--metrics` 行追加、schema drift check 段落追加
- [x] M-3: `README.md` — 「Ground Truth ラベリング」サブセクション追加 (gse-replay セクション直後)
- [x] M-4: `README.ja.md` — 同じ内容を日本語で追加 (粒度を README.md に合わせる)

## 検証
- [x] V-1: 新規用語が docs/ 配下で検索ヒットするか grep 確認
- [x] V-2: 監査エージェント再実行で指摘ゼロを確認
- [x] V-3: `npx tsc --noEmit` + `cargo build` で docs 変更によりビルドが影響していないか (念のため)

## レビュー
- [x] R-1: code-reviewer でドキュメント品質・用語一貫性を確認
- [x] R-2: MEDIUM 指摘対応

## 完了処理
- [x] `.steering/20260415-docs-phase1-backfill/decisions.md` 作成 (追記配置ポリシー、glossary 列挙方式の決定事項)
- [x] git commit: `docs: backfill Phase 1 (GT + metrics + gse-dataset) across repo-structure / functional / architecture / glossary / guidelines / README`
- [x] git push

## スコープ外 (本タスクでは扱わない)

- 新機能実装
- docs の大規模リストラクチャ / セクション番号再採番
- Phase 2+ 用語の先行追加 (IRB / consent / LR score 等)
- CLAUDE.md の更新 (既に §データ repo 連携 で対応済み)
