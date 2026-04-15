# Docs Phase 1 Backfill — design

## 実装アプローチ

追記主体で現状構成を維持。セクション番号の再配置は行わず、Phase 1 要素を既存構成の適切な位置に挿入する。

### 各 doc への追加要素

#### `docs/repository-structure.md`
- ディレクトリツリーを更新:
  ```
  src-tauri/
    src/
      analysis/
        metrics.rs  [NEW Phase 1]
      bin/
        replay.rs
        emit_schema.rs  [NEW Phase 1]
      schema_dto.rs  [NEW Phase 1]
      ...
    schema/
      current.json  [NEW Phase 1, 機械生成ゴールデン]
      README.md
  ```
- 依存方向図 (モジュール layer) に `schema_dto` を追加: production path から独立した schema 生成専用モジュール

#### `docs/functional-design.md`
- 新規セクション「§N. Ground Truth 収集機構 (Phase 1)」:
  - 背景: HMM 推定と真の認知状態のズレを定量化する必要
  - 機能: ⌘⇧⌥ F/I/S ホットキー、2s デバウンス、Dashboard counter widget、metrics JSON 出力
  - 非機能: production path 汚染ゼロ原則 (/reimagine v2)
- ユースケース追加:
  - UC-GT1: 開発者がラベリングしながら作業
  - UC-GT2: オフラインでのメトリクス集計 (`--metrics`)
  - UC-GT3: 端末間での metrics 共有 (gse-dataset repo)

#### `docs/architecture.md`
- §主要コンポーネントに以下を追加:
  - `record_user_label` Tauri コマンド + global-shortcut プラグイン
  - `logger::LogEntry::UserLabel` バリアント
  - `analysis::metrics` 純粋関数モジュール
  - `schema_dto` DTO ミラー + `bin/emit_schema`
- データフロー §に追加:
  - **UserLabel 記録パス**: ホットキー発火 → `record_label_internal` → compare_exchange デバウンス → `log_tx.try_send(UserLabel)` → logger 書き込み + `user_label_recorded` Tauri event → Dashboard counter 更新
  - **Metrics 算出パス**: `gse-replay <s> --metrics` → `run_replay` で FeatSnapshot 生成 + `collect_user_labels` で UserLabel 抽出 → `compute_session_metrics` → pretty-print / JSON
  - **Schema 生成パス**: `schema_dto::LogEntryDto` → `cargo run --bin emit_schema` → `src-tauri/schema/current.json` → CI drift check → gse-dataset へ手動 sync

#### `docs/glossary.md`
- 新規用語 8+ 項目:
  - UserLabel (GT ラベル、Flow/Incubation/Stuck)
  - Ground Truth (GT): ユーザー自認の認知状態
  - ConfusionMatrix: 正解 × 推定の 3×3 行列
  - metrics.json: `gse-replay --metrics --json` 出力
  - detection_lead_ms: ラベル時刻 - HMM argmax 時刻、正=HMM 先行
  - schema_dto: schema 生成用 DTO ミラー型
  - macro F1 / micro F1: クラス別 F1 の平均方式
  - recovered_at: Stuck ラベル後の p_flow > 0.5 到達時刻
  - hmm_version: `analysis::engine::HMM_VERSION` の SemVer
  - HMM_VERSION と schema version は独立した軸であることを明記

#### `docs/development-guidelines.md §3 範囲区分`
- 表に 1 行追加:
  | GT メトリクス | `gse-replay --metrics` | 高 | Phase 1 以降、GT 付きセッションの定量評価 |
- schema drift check を §テスト方針に 1 段落追加

#### `README.md` / `README.ja.md`
- 既存の「セッションリプレイ CLI」セクション直後に「Ground Truth ラベリング (Phase 1)」サブセクションを追加:
  - ⌘⇧⌥ F/I/S の押下方法
  - NDJSON 出力サンプル
  - `gse-replay --metrics` の出力サンプル
  - gse-dataset repo への metrics push ワークフロー

## 変更対象

### 修正するファイル
- `docs/repository-structure.md`
- `docs/functional-design.md`
- `docs/architecture.md`
- `docs/glossary.md`
- `docs/development-guidelines.md` (§3 のみ、§10 は既存)
- `README.md`
- `README.ja.md`

### 新規作成するファイル
- `.steering/20260415-docs-phase1-backfill/{requirement,design,tasklist,decisions}.md`

### 削除するファイル
なし

## 影響範囲

| 影響先 | レベル | 根拠 | 対処 |
|---|---|---|---|
| コード | NONE | docs のみ変更 | — |
| CI | NONE | ci.yml 変更なし | — |
| チーム理解 | POSITIVE | Phase 2 着手前に古い情報を一掃 | — |

## 既存パターンとの整合性

- docs のトーン・用語・Markdown スタイルを既存部分に合わせる
- セクション番号の再採番は避け、各 doc 末尾または自然な挿入箇所に追記
- 日本語 (README.ja.md / docs/) と英語 (README.md) の記述粒度を揃える

## テスト戦略

- **T-D1**: monorepo 全文検索で新規用語 (UserLabel / metrics.rs / schema_dto 等) が docs/ 配下で少なくとも 1 箇所ヒット
- **T-D2**: 監査エージェント (Explore) 再実行で指摘ゼロ
- **T-D3**: README.md / README.ja.md の記述粒度が一致 (段落数・コマンド例数が揃う)

## ロールバック計画

- 各 doc の変更を `git revert` で即ロールバック可能
- コード変更なし、CI 影響なし

## 既知の Open 点

- **図 (Mermaid) を入れるか**: architecture.md は既存で Mermaid 利用の有無未確認。既存構成を尊重、文章中心で記述しつつ既に Mermaid があれば図も 1 つ追加する
- **glossary の列挙順**: 既存 glossary のアルファベット順 or 機能分類順を確認してから合わせる
