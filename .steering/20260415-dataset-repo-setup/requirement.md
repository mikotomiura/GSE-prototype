# Dataset Repo (gse-dataset) を Phase 1 対応にし、macOS↔Windows の共有経路を確立

## 背景

`gse-prototype` Phase 1 で:
- Phase 0 で `meta.hmm_version` を追加
- Phase 1 Task 1 で `user_label` レコード追加
- 初回 GT 付きセッション 2 件 (`gse_20260415_080214.ndjson` / `gse_20260415_080921.ndjson`) が `~/Documents/GSE-sessions/` に蓄積

一方 `mikotomiura/gse-dataset` repo は既に整備済みだが:
- `schema/v1.json` には `meta.hmm_version` も `user_label` も未反映 → 現行 NDJSON を validate すると `additionalProperties: false` で FAIL する
- `anonymized/**/*.ndjson` が `.gitignore` で除外 → 共有手段がない
- OS 別ディレクトリ分離がない

ユーザー指示 (2026-04-15): **(B) anonymized のみ git 管理、raw は端末ローカル維持**

## ゴール

1. `schema/v2.json` で Phase 0/1 エントリ全 6 種 (`meta[with hmm_version]` / `session_start` / `key` / `feat` / `ime_state` / `user_label`) を正しく検証
2. `validate_schema.py` が v2 をデフォルトで使用
3. `import_sessions.py` が `--os {macos,windows}` フラグで OS 別ディレクトリに配置
4. `.gitignore` を緩めて `anonymized/**/*.ndjson` を tracked 対象に
5. 初回 2 セッションを anonymize → validate → commit → push
6. `gse-prototype/docs/development-guidelines.md` に gse-dataset 連携手順を追記
7. Phase 2+ で必要になる「gse-replay --metrics --json を anonymized に対して動かす」は別タスク。本タスクでは metrics JSON を raw から算出して metrics/ に同 commit する

## スコープ

### 含むもの
- `gse-dataset` 側:
  - `schema/v2.json` 作成 (v1.json は legacy 参照用に残置)
  - `scripts/validate_schema.py` 更新 (デフォルト v2、`--schema` で選択可)
  - `scripts/import_sessions.py` 更新 (`--os` フラグ)
  - `.gitignore` 更新 (`anonymized/**/*.ndjson` の exclusion を削除、`raw/**` は維持)
  - `README.md` 更新 (Phase 1 要素 + 同期プロトコル + schema version policy)
  - `metrics/P000/macos/` ディレクトリ + 初回 2 件の `*.metrics.json` (gse-replay --metrics --json 出力)
  - 初回 2 セッションを `anonymized/P000/macos/` に commit
- `gse-prototype` 側:
  - `.steering/20260415-dataset-repo-setup/{requirement,design,tasklist,decisions}.md`
  - `docs/development-guidelines.md` に §新セクション「Session データ管理 (gse-dataset repo)」
  - `CLAUDE.md` に 1 行ポインタ追加

### 含まないもの
- `gse-replay --metrics --from-feat-entries` モード (anonymized が vk なしなので step() 再実行不可、既存 feat 行を読む別モード) → Phase 2+
- 外部被験者 P001+ の IRB / インフォームドコンセント運用 (Phase 2+)
- `scripts/aggregate.py` 等の多セッション集計 (データ量が増えてから)
- Windows 端末でのセッション収集 (実機取得時に並列)
- `schema_version` を NDJSON に埋め込むこと (gse-prototype 側 production path 変更になるため先送り、`hmm_version` とファイル配置で版管理)

## 受け入れ条件

- [ ] `schema/v2.json` が現行 2 セッション (anonymize 前) の全行を validate 成功
- [ ] 同 2 セッション (anonymize 後) も validate 成功 (`key` → `cat` 変換のみ差分)
- [ ] `python scripts/validate_schema.py` がデフォルト v2 で動作、`--schema schema/v1.json` で v1 も使える
- [ ] `python scripts/import_sessions.py --os macos` で `raw/P000/macos/` に配置される
- [ ] `.gitignore` 変更後 `git check-ignore anonymized/P000/macos/gse_*.ndjson` が空 (tracked)
- [ ] 同コマンドで `raw/P000/macos/gse_*.ndjson` は依然 ignored
- [ ] `git status` で `anonymized/P000/macos/*.ndjson` と `metrics/P000/macos/*.metrics.json` が tracked で見える
- [ ] `gse-dataset` に anonymized 2 件 + metrics JSON 2 件が commit + push 済み
- [ ] `gse-prototype/docs/development-guidelines.md` に同期手順が反映
- [ ] `code-reviewer` + `security-checker` 両方で「anonymized に VK / 文字内容 / 生 timestamp 以外の個人情報が漏洩していない」ことを確認 (HIGH 0)

## 関連ドキュメント

- `.steering/20260415-phase1-ground-truth/baseline_metrics.md` (初回 2 件記録済、metrics 出力のソース)
- `docs/development-guidelines.md` §3 (Replay-as-Truth, 将来 §セクション追加)
- CLAUDE.md 「技術的制約」と「作業記録の運用ルール」
- gse-dataset/README.md (現行、Phase 1 用に改訂)

## 運用メモ

- **/reimagine 適用: No**
- **理由**: 設計判断は (B) 採用のみで既決着、残りは既存 schema / スクリプトの拡張タスク
- **前提**: `gse-prototype` main に Phase 1 3 コミット + M1 fix commit 済 (`2483909`)
- **privacy 原則**: raw NDJSON は GitHub private repo であっても push しない (将来 P001+ 被験者の外部データは暗号化ローカル保管、外部流出経路を 0 にする)
