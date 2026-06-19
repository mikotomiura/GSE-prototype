# 参加者 ID を設定可能化 (logger.rs の P000 ハードコード解消)

## 背景

`src-tauri/src/logger.rs` の `default_log_path()` は、セッション NDJSON の保存先を
`$GSE_DATASET/raw/P000/` と **`P000` 固定でハードコード**している。
ユーザー検証 (複数参加者 P001/P002/... のデータ収集) を行うには、参加者ごとに
保存先ディレクトリを分ける必要があるが、現状は全参加者が `P000` に上書きされてしまう。

`.steering/20260619-user-validation-data-collection/decisions.md` D1 の前提であり、
同タスクの punch list ① にあたる。研究者はオフラインで参加者 ID を採番・割り当てし、
アプリ側は **受け取るだけ** という責務分離を取る。

## ゴール

参加者 ID を環境変数 `GSE_PARTICIPANT_ID` から受け取り、保存先を切り替えられる。
既存の `GSE_DATASET` env+fallback パターンに倣い、P000 既定挙動は完全に不変に保つ。

## スコープ

### 含むもの (Part 1: env 受け取り — 実装完了・未コミット)
- `logger.rs` `default_log_path()` の `P000` ハードコード解消。
- `GSE_PARTICIPANT_ID` → `GSE_PID` → `P000` から参加者 ID を受け取る (env override 層)。
- ID 形式バリデーション (allowlist `[A-Za-z0-9_-]` 1..=64 + Windows 予約名拒否、
  パストラバーサル/パス注入防止)。

### 含むもの (Part 2: 自動生成 — D4 で追加・次セッションで実装)
- 被験者が GSE を操作すると参加者 ID が**自動付与**される (env 未設定でも P000 衝突しない)。
- アプリが端末ごとに一意な不透明 ID (`P` + 12桁 hex) を生成し `~/.gse/participant_id` に永続化。
- 解決順: 永続化値 → env(`GSE_PARTICIPANT_ID`→`GSE_PID`) → 自動生成+永続化 → P000(最終fallback)。
- 詳細は decisions.md D4 (承認済みサブ設計 ①〜④)。

### 含まないもの
- 採番プール生成・割り当て運用、ID→被験者 対応表の管理 (研究者オフライン)
- sync スクリプト / `metrics/P*/` 集計側の追従改修 (D4 のトレードオフ、別タスク)
- 入力 UI / オンボーディング画面 (完全自動生成のため不要)、ダッシュボードへの ID 表示
- anonymize.py / package-session / (a)(b)メトリクス / DuckDB / フォーム

## 受け入れ条件

- [ ] `GSE_PARTICIPANT_ID=P003` で `$GSE_DATASET/raw/P003/` に解決される
- [ ] 未設定で従来どおり `P000` (snapshot byte-equal 不変)
- [ ] 不正 ID (`../`、空、過長、パス区切り文字) を拒否し安全な既定へフォールバック
- [ ] `cargo test --workspace` green
- [ ] `gse-replay --snapshot` byte-equal
- [ ] `emit_schema` drift なし

## 関連ドキュメント

- docs/development-guidelines.md §Session データ管理 / §10 データ privacy
- `.steering/20260619-user-validation-data-collection/decisions.md` D1
- Skill: data-privacy / rust-standards / architecture-rules

## 運用メモ
- /reimagine 適用: No
- 理由: スコープが厳密に限定された小規模実装 (既存 env+fallback パターンの踏襲)。
  設計上の自由度は ID バリデーション方針のみで、最良案は自明。
