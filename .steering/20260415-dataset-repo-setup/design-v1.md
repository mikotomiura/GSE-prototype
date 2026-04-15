# design-v1 — gse-dataset Phase 1 対応 (初稿、/reimagine 対象)

> **注記**: 本 v1 は /reimagine の対象。破棄候補として design-comparison.md で比較する。

## 全体方針 (v1)

**(B) anonymized のみ git 管理** を前提に、既存 gse-dataset の「raw は端末ローカル、anonymized を pipeline 経由で git に入れる」思想を最小拡張する。

## 物理構造 (v1)

```
gse-dataset/
├── schema/
│   ├── v1.json          # legacy (Phase 0 未対応)
│   └── v2.json          # Phase 0/1 対応 (新規)
├── scripts/
│   ├── import_sessions.py  # --os フラグ追加
│   ├── anonymize.py        # 変更なし (key 以外は passthrough)
│   └── validate_schema.py  # --schema フラグ対応、デフォルト v2
├── raw/P000/<os>/          # git-ignored
│   ├── macos/
│   └── windows/
├── anonymized/P000/<os>/   # tracked (.gitignore 削除)
│   └── macos/
└── metrics/P000/<os>/      # tracked (新規ディレクトリ)
    └── macos/              # gse-replay --metrics --json 出力
```

## スキーマ v2 (v1)

- v1.json の 5 種 + `user_label` 追加、`meta` に `hmm_version` オプション付与
- `recovered_at` は `["integer", "null"]`
- `schema_version` は NDJSON 内に埋め込まない (gse-prototype 側 production path 変更を避ける)

## 同期プロトコル (v1)

各端末で以下を順に実行:
1. `python scripts/import_sessions.py --participant P000 --os macos`
2. `cargo run --bin gse-replay -- raw/P000/macos/gse_*.ndjson --metrics --json > metrics/P000/macos/<name>.metrics.json` (gse-prototype 側で実行、手動コピー)
3. `python scripts/anonymize.py raw/P000/macos/*.ndjson --outdir anonymized/P000/macos/`
4. `python scripts/validate_schema.py anonymized/P000/macos/*.ndjson`
5. `git add anonymized/ metrics/ && git commit && git push`

## 版管理戦略 (v1)

- `hmm_version`: gse-prototype/engine.rs の HMM_VERSION (SemVer)、NDJSON meta に埋まる
- `schema/v<N>.json`: NDJSON フォーマット版。Phase 変更時に bump
- 両者は独立
- 版不一致検知は `validate_schema.py` に任せる

## トレードオフ (v1)

- **pros**: 既存 repo 構造を踏襲、変更最小、privacy を維持
- **cons**:
  - gse-replay が anonymized を直接処理できない (vk なし) → metrics は事前に raw から算出して commit する 2 段運用
  - OS 別ディレクトリ分離は被験者 1 人が複数 OS 使う場合のみ意味があり、外部被験者 P001+ では冗長の可能性
  - metrics JSON の自動化なし (人手で gse-prototype → gse-dataset の間をコピー)
  - Windows 端末での sync がまだ未設計 (import_sessions.py はそのまま動く想定だが未検証)
