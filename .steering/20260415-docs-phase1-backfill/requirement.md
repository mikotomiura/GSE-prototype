# Docs Phase 1 Backfill — Ground Truth 機能 + gse-dataset 連携の永続ドキュメント化

## 背景

2026-04-15 に Phase 1 (ground-truth / metrics / counter-ui) + CI matrix build 拡充 + gse-dataset 連携 (dataset-repo-setup) を完了したが、永続ドキュメント (docs/ 配下 + README) が実装に追いついていない。

Explore エージェントによる監査で以下のギャップが判明:

### HIGH (実装との矛盾)
- `docs/repository-structure.md` に `schema_dto.rs` / `analysis/metrics.rs` / `bin/emit_schema.rs` / `schema/current.json` が未記載
- `docs/functional-design.md` に Ground Truth 機能 (UserLabel / ⌘⇧⌥ F/I/S / Dashboard counter / `gse-replay --metrics`) が未反映、ユースケースも Phase 0 止まり
- `docs/architecture.md` の主要コンポーネント/データフロー図に user_label パス・schema 生成パイプラインが存在しない

### MEDIUM (追加記載推奨)
- `docs/glossary.md` に UserLabel / Ground Truth / ConfusionMatrix / metrics.json / detection_lead_ms 等の新規用語が未追加
- `docs/development-guidelines.md §3` の範囲区分表に `gse-replay --metrics` vs `--snapshot` の使い分け記述がない
- `README.md` / `README.ja.md` の Phase 1 GT セクションの可視性が低い、gse-dataset 連携ワークフローの説明が薄い

### OK (反映済み、変更不要)
- `CLAUDE.md` のデータ repo 連携セクション
- `docs/development-guidelines.md §10 Session データ管理`

## ゴール

Phase 2 着手前に、永続ドキュメント 6 ファイルに Phase 1 実装を完全に反映する。6 ヶ月後の自分や外部協力者が古い情報で判断を誤るリスクを排除する。

## スコープ

### 含むもの

1. `docs/repository-structure.md` 改訂: Phase 1 で追加された新規ファイル・新規モジュールをツリーに反映、依存方向図を更新
2. `docs/functional-design.md` 改訂: Ground Truth 機能セクション新設、ユースケース UC-GT* 追加 (ラベリング / metrics 集計)
3. `docs/architecture.md` 改訂: §主要コンポーネントに `record_user_label` / global-shortcut プラグイン / `schema_dto` / `metrics` を追加、データフロー §に user_label 記録パス + schema 生成パイプラインを追加
4. `docs/glossary.md` 改訂: Phase 1 新規用語 (UserLabel / Ground Truth / ConfusionMatrix / metrics.json / detection_lead_ms / schema_dto / macro F1 / micro F1 / recovered_at) を追加
5. `docs/development-guidelines.md §3` 拡張: 範囲区分表に `--metrics` / `--snapshot` 使い分け行追加、schema drift check の位置づけ明示
6. `README.md` / `README.ja.md` 改訂: Phase 1 GT ラベリング+metrics 算出セクションを可視性高く配置、gse-dataset 連携ワークフローを追加

### 含まないもの
- 新機能の実装 (純粋にドキュメント反映のみ)
- `CLAUDE.md` の変更 (既に対応済み)
- `docs/development-guidelines.md §10` の変更 (既に対応済み)
- glossary に IRB / インフォームドコンセント等の Phase 2+ 用語を足すこと (必要になった時に追加)
- docs の大規模リストラクチャ (セクション構成は維持、追記主体)

## 受け入れ条件

- [ ] `docs/repository-structure.md` のディレクトリツリーに `src-tauri/src/schema_dto.rs`, `src-tauri/src/analysis/metrics.rs`, `src-tauri/src/bin/emit_schema.rs`, `src-tauri/schema/` が現れる
- [ ] `docs/functional-design.md` に Ground Truth ラベリング機能セクションと 2-3 件のユースケース記載
- [ ] `docs/architecture.md` のデータフローに user_label 記録パス (global-shortcut → record_label_internal → logger → Tauri event → Dashboard) と schema 生成パイプライン (schema_dto → emit_schema → CI drift check) が図示 or 文章化
- [ ] `docs/glossary.md` に 8 項目以上の Phase 1 用語が追加
- [ ] `docs/development-guidelines.md §3` の範囲区分表に `gse-replay --metrics` 行が追加、使い分けが明示
- [ ] `README.md` / `README.ja.md` の「使い方」または「機能」セクションに GT ラベリングと `--metrics` のコマンド例追加
- [ ] git commit + push、CI 緑確認
- [ ] 監査再実行 (file-finder or Explore agent) で指摘ゼロ

## 関連ドキュメント

- `.steering/20260415-phase1-ground-truth/` (Task 1)
- `.steering/20260415-phase1-metrics/` (Task 2)
- `.steering/20260415-phase1-counter-ui/` (Task 3)
- `.steering/20260415-ci-matrix-build/`
- `.steering/20260415-dataset-repo-setup/`
- CLAUDE.md (docs を先に読むという指針)

## 運用メモ

- **/reimagine 適用: No**
- **理由**: 設計判断なし、既存実装を文書に忠実に写すドキュメント作業
- **前提**: 上記 4 タスクの commit が main に反映済み (`3947927` 時点で完了)
