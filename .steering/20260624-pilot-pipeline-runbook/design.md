# 設計 — M1 パイロット パイプライン結線 + Y runbook

## 実装アプローチ

被験者→研究者→分析の 3 ストリームを end-to-end に結線する。新規ロジックは作らず、
既存の自己完結部品 (gse-package / gse-replay / sync-session / build_analysis_db) の **隙間を
埋める結合材** を追加する。

```
[被験者端末]                          [研究者端末]                       [分析]
raw NDJSON                            P###_x.age (受領)
  │ gse-package (匿名化+age暗号化)       │ gse-unpack (age復号)  ← GAP①
  ▼                                     ▼
P###_x.age ──Dropbox File Request──▶  匿名化 NDJSON
                                        │ sync-session --no-commit
                                        ▼
                                      metrics/P###/<os>/*.metrics.json
                                        │ gen_sessions_manifest.py  ← GAP②
                                        ▼ + survey/*.csv (配置規約)  ← GAP③
                                      sessions.csv (phase 手記入)
                                        │ build_analysis_db.py (#6)
                                        ▼
                                      cross_section
```

## 変更対象

### 新規作成するファイル
- `src-tauri/src/bin/unpack.rs` — **gse-unpack** CLI (decrypt: `.age`→匿名化 NDJSON、age crate)。
  `package` feature gate。`--keygen` で age 鍵ペア生成 (秘密鍵→ファイル, 公開鍵→stdout) も提供し、
  age CLI 不在環境でも全フローが回るようにする (本機は age CLI 未導入)。GAP①。
- `scripts/gen_sessions_manifest.py` — gse-dataset の `metrics/P*/<os>/*.metrics.json` を走査し
  `participant_id,session_id,os,phase` を出力。既存 sessions.csv の phase 記入を保全マージ。GAP②。
- `scripts/templates/survey-template.csv` — survey CSV 最小スキーマ (P-ID/phase/尺度 + D8 WoZ 列)。GAP③。
- `docs/pilot-runbook.md` — Y パイロット運用 runbook (被験者 + 研究者手順)。GAP④。
- `scripts/pilot-smoke.sh` — end-to-end 統合スモーク (合成 session で全段検証)。GAP⑤。

### 修正するファイル
- `src-tauri/Cargo.toml` — `[[bin]] name="gse-unpack" required-features=["package"]` を追加。
- `scripts/fixtures/analysis_join/README.md` — survey 最小スキーマに D8 WoZ 列を追記。

### 削除するファイル
- なし。

## 既存パターンとの整合性
- **gse-unpack** は **gse-package の鏡像**: 同じ素朴 `--key value` パーサ、同じ `package` feature gate、
  age crate (CLI 非依存)、`is_valid_participant_id` 同等のパス検証、`tracing`/`anyhow` 不使用の
  `Result<_, String>` + `ExitCode` (package.rs と同一様式)。**architecture-rules**: bin は
  `analysis/` の純粋関数 (anonymize) を呼ぶのみで OS API は触らない。
- **gen_sessions_manifest.py** は build_analysis_db.py と同じ stdlib のみ・同じ
  `session_id = filename[:-len(".metrics.json")]` 規約・`.range` 除外を踏襲。
- **pilot-runbook.md** は `calibration-smoke-runbook.md` の節構成 (前提/ビルド/被験者/研究者/
  トラブルシュート) に倣う。
- **pilot-smoke.sh** は sync-session.sh の bash 様式 (`set -euo pipefail`、exit code 規約、
  `[pilot-smoke]` プレフィックス) を踏襲。

## decrypt の形態 (設計判断) — decisions.md D-PP1 参照
研究者側 decrypt を **Rust `gse-unpack` bin** とする (shell + age CLI ラッパではなく)。
理由: (1) 検証ゲート (end-to-end smoke) が必須受け入れ条件だが **本機に age CLI 未導入** のため、
CLI 依存だと gate がローカルで回らない。(2) transfer-pipeline D1 が「自己完結 Rust bin」を選んだのと
対称。(3) `cargo test --features package` で復号往復を回帰保護できる。鍵は `--identity <keyfile>`
で repo 外から渡し、コミットしない。

## 鍵・プライバシー設計 (data-privacy 厳守)
- age 秘密鍵は **repo 外**。gse-unpack `--keygen` の出力先はデフォルトで repo 外 (`~/.gse/` 等) を
  案内し、`.gitignore` にも鍵パターンを足す (多層防御)。
- 復号後の平文 NDJSON は **匿名化済** (gse-package が VK→category 済) だが、それでも生 NDJSON 同様
  gse-dataset / 本 repo にコミットしない。共有は `metrics.json` のみ。
- smoke は一時ディレクトリ (scratchpad/`mktemp`) で完結し、鍵・平文・age を残さず後始末する。

## テスト戦略
- **単体 (Rust)**: `cargo test --features package` で gse-unpack の keygen→encrypt→decrypt 往復、
  不正 participant id 拒否、匿名化ペイロード一致を検証 (package.rs のテスト様式)。
- **統合 (E2E)**: `scripts/pilot-smoke.sh` が合成 session (outcome_metrics.ndjson) を
  package→unpack→sync-session→gen_sessions_manifest→build_analysis_db に通し `cross_section`
  行 > 0 を assert。実データ非依存・age CLI 非依存。
- **回帰不変**: `cargo test --workspace` / `gse-replay --snapshot minimal` / `emit_schema` parity
  が本タスクで不変 (ロジック非変更)。

## ロールバック計画
全て新規ファイル + Cargo.toml への bin 追加 1 行 + README 追記のみ。gse-unpack は feature gate で
default ビルド (Tauri 本体) に載らないため、問題時は bin 定義と新規ファイル削除で原状復帰。
既存挙動への影響なし。
