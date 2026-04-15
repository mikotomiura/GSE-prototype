# タスクリスト — gse-dataset Phase 1 対応 (v2 採用)

## Stage A: gse-prototype 側 — schema 生成基盤
- [x] A-1: `src-tauri/Cargo.toml` に `schemars = "0.8"` を dependency 追加
- [x] A-2: `src-tauri/src/schema_dto.rs` 新規作成 — LogEntry の JsonSchema 派生ミラー型 (6 バリアント)
- [x] A-3: `src-tauri/src/lib.rs` に `pub mod schema_dto;` 追加
- [x] A-4: `src-tauri/src/bin/emit_schema.rs` 新規作成 — stdout に pretty JSON 出力
- [x] A-5: `cargo run --bin emit_schema` で出力検証 (全 6 バリアントが oneOf に含まれること)
- [x] A-6: `cargo test --workspace` 退行ゼロ
- [x] A-7: `cargo build --target aarch64-apple-darwin` warning 0

## Stage B: gse-prototype 側 — schema/ ディレクトリ + CI drift check
- [x] B-1: `src-tauri/schema/current.json` コミット (機械生成物のゴールデンコピー)
- [x] B-2: `src-tauri/schema/README.md` — 「このディレクトリは emit_schema 出力のゴールデン、手編集禁止」
- [x] B-3: `.github/workflows/ci.yml` の check ジョブに schema drift 検知ステップ追加 (`cargo run --bin emit_schema | diff src-tauri/schema/current.json -`)
- [x] B-4: `tests/fixtures/minimal.ndjson` が現行 schema で validate 成功することをローカルで確認 (Python jsonschema で事前検証、CI には含めない)

## Stage C: gse-prototype 側 — docs
- [x] C-1: `docs/development-guidelines.md` に §新セクション「Session データ管理 (gse-dataset 連携)」
  - metrics.json を共有の主役にする方針
  - 各端末でのワークフロー (gse-replay --metrics --json → gse-dataset/metrics/ に commit)
  - schema drift 発生時の対処 (emit_schema 再実行 → 両 repo を同期)
- [x] C-2: `CLAUDE.md` に 1 行追加: 「セッションデータは `mikotomiura/gse-dataset` repo で管理 (schema は gse-prototype から機械生成)」

## Stage D: gse-dataset 側 — schema 生成物の配置
- [x] D-1: `gse-prototype/src-tauri/schema/current.json` を `gse-dataset/schema/current.json` にコピー
- [x] D-2: `gse-dataset/schema/v1.json` を削除
- [x] D-3: `gse-dataset/schema/README.md` 新規 — 「このファイルは gse-prototype の `cargo run --bin emit_schema` 出力。手編集禁止、sync プロトコルは development-guidelines.md 参照」

## Stage E: gse-dataset 側 — scripts 修正
- [x] E-1: `scripts/validate_schema.py` — デフォルトで `schema/current.json` を読む (環境変数や `--schema` フラグで上書き可)
- [x] E-2: `scripts/import_sessions.py` — `--os {macos,windows}` フラグ追加、`raw/P<NNN>/<os>/` に配置
- [x] E-3: `scripts/aggregate_metrics.py` 新規 — `metrics/P*/**/*.metrics.json` を glob し、全体の macro F1 平均 / Stuck precision 平均 / セッション数を stdout に出す
- [x] E-4: `scripts/requirements.txt` に必要なら追加 (jsonschema は既存)

## Stage F: gse-dataset 側 — README 全面改訂
- [x] F-1: Phase 1 要素 (user_label, hmm_version) を反映
- [x] F-2: schema は機械生成であることと sync 手順を明記
- [x] F-3: 共有の主役が metrics.json であることを説明
- [x] F-4: anonymized NDJSON の commit は Phase 2 ML training 時に判断することを明記
- [x] F-5: ディレクトリ構造セクションを v2 に合わせて更新
- [x] F-6: 各端末での運用プロトコル (macOS / Windows) をコマンドレベルで記載

## Stage G: 初回データ投入
- [x] G-1: gse-prototype で `cargo run --bin gse-replay -- ~/Documents/GSE-sessions/gse_20260415_080214.ndjson --metrics --json` 実行 → JSON 保存
- [x] G-2: 同じく gse_20260415_080921.ndjson の metrics JSON 保存
- [x] G-3: `gse-dataset/metrics/P000/macos/gse_20260415_080214.metrics.json` と `gse_20260415_080921.metrics.json` に配置
- [x] G-4: `python scripts/validate_schema.py` で raw 2 件を validate 成功 (raw は実行ディレクトリで指定)
- [x] G-5: `python scripts/aggregate_metrics.py` で 2 件集計が動くことを確認
- [x] G-6: `.gitignore` が anonymized/raw を ignored、metrics/schema を tracked にしていることを `git check-ignore` で確認

## Stage H: レビュー
- [x] H-1: `code-reviewer` 並列起動 — gse-prototype 側 (schema_dto.rs / emit_schema.rs / CI) + gse-dataset 側 (scripts 3 ファイル)
- [x] H-2: `security-checker` 並列起動 — metrics JSON に VK / 文字内容 / 生 timestamp が漏洩していないこと確認
- [x] H-3: HIGH 対応、MEDIUM はユーザー判断

## Stage I: commit + push
- [x] I-1: gse-prototype commit — `feat(schema): emit JSON Schema from Rust types (gse-dataset sync)`
- [x] I-2: gse-prototype push
- [x] I-3: gse-dataset commit — `feat(schema): v2 machine-generated, metrics-first sharing (Phase 1)`
- [x] I-4: gse-dataset push
- [x] I-5: GitHub Actions で schema drift check が緑であることを確認

## Stage J: 完了処理
- [x] J-1: `.steering/20260415-dataset-repo-setup/decisions.md` 作成 — v2 採用理由、schema 機械生成の設計、anonymized 先送り判断
- [x] J-2: Phase 2a 着手前チェックリスト (retrospective 更新) に「anonymize commit 方針判断」を追加

## スコープ外 (別タスク)

- `gse-replay --metrics --from-feat-entries` モード (Phase 2a+)
- `scripts/sync_schema.sh` 等の同期自動化 (Phase 2+)
- 外部被験者 P001+ の IRB 運用 (Phase 2+)
- anonymized NDJSON の commit 切替 (Phase 2 ML training 時)
- Windows 端末での sync 実機検証 (Windows 実機確保時)
