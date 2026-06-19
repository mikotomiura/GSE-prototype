# 設計判断

## D1: 参加者 ID は env から「受け取るだけ」(採番はアプリ外)

アプリは参加者 ID を採番・割り当てしない。研究者がオフラインで採番し、env 変数で渡す。
アプリ側は受け取った ID を検証して保存先に使うのみ。
(`.steering/20260619-user-validation-data-collection/decisions.md` D1 を踏襲)

## D2: env 解決順は GSE_PARTICIPANT_ID → GSE_PID → "P000"

**背景**: handoff は logger 用に新変数 `GSE_PARTICIPANT_ID` を指定。一方 impact-analyzer の
調査で、既存 sync スクリプト (`sync-session.sh:58` 他) が `GSE_PID` (既定 P000) を使い
`metrics/$PID/` を決めていると判明。logger が `GSE_PARTICIPANT_ID` のみを読むと、研究者は
`GSE_PARTICIPANT_ID` (logger→raw/) と `GSE_PID` (sync→metrics/) の 2 変数を一致設定する
運用責任を負い、片方だけ設定すると raw と metrics が別 ID に分裂する footgun が残る。

**決定 (ユーザー選択)**: logger は `GSE_PARTICIPANT_ID` を最優先で読み、未設定なら既存
`GSE_PID` にフォールバック、両方未設定で `P000`。これにより:
- handoff の主変数名 `GSE_PARTICIPANT_ID` を尊重 (明示的に上書き可能)。
- 研究者が `GSE_PID` を 1 つ設定するだけで raw/ と metrics/ の両方が同一 ID で揃う。
- 既定 (両方未設定) は P000 不変。

**Why**: 二重管理 footgun の解消 > 変数の単純性。実データ収集で ID 不一致は静かなデータ
汚染になり、本プロジェクトの重視品質「正確性」に直結するため、整合を優先した。

## D3: ID バリデーションは allowlist (`[A-Za-z0-9_-]`, 1..=64)

**背景**: env 値はそのままパス構成要素 (`raw/$ID/`) になるため、`../` 等で
パストラバーサル/パス注入の余地がある。

**決定**: 拒否リスト (denylist) ではなく allowlist を採用。ASCII 英数字 + `_` + `-` のみ許可、
長さ 1..=64。これにより `.`(→`..`)、`/`、`\`、`:`、空白、null、改行、`~`、`$` をすべて一括拒否。
参加者 ID 規約 (`P000`/`P003` 等) は完全にカバー。trim 後に検証 (前後空白許容)。

**Why**: denylist は見落としが事故に直結する。allowlist は「許可した文字以外は全部不正」で
安全側に倒れる。不正値はログ (warn、生値は出さない) して次候補へフォールバック。

## D4: 参加者 ID を「完全自動生成 + ローカル永続化」に拡張 (2026-06-19 ユーザー方針転換)

**背景**: env 受け取り (D1〜D3) 完成後、ユーザーが「被験者が自分で GSE を操作しても ID が
**自動付与**される形にしたい」と要望。env 未設定だと全員 P000 に衝突する点を解消する。

**決定 (ユーザー選択 2 問)**:
- **ID の出どころ = アプリが完全自動生成** (入力 UI なし、端末ごとに一意な不透明 ID を生成・永続化)。
- **優先順 = 永続化値を最優先** → env → P000。

**承認済みサブ設計 (本セッションでプラン承認)**:
- ① **ID 形式 = `P` + 12桁ランダム hex** (例 `Pa3f9c2e1b7d0`)。`is_valid_participant_id` を通過し、
  sync の `P*` glob と互換を保ちつつ不透明・一意 (bare hex 案は sync 改修必須のため不採用)。
- ② **永続化先 = `~/.gse/participant_id`** (`USERPROFILE`/`HOME` 起点、既存 `fallback_log_dir` と同流儀)。
  logger を AppHandle に結合させず自己完結・テスト可能に保つ (Tauri `app_config_dir` 案は結合増で不採用)。
- ③ **env は override に徹し永続化しない**。永続ストアは自動生成 ID のみ保持。
- ④ **リセット手段 = `~/.gse/participant_id` 削除で次回再生成**。研究者 ID へ切替も削除→env or 再生成。

**Why / トレードオフ (明示)**: 本決定は **D1 (研究者オフライン採番) と衝突**する。不透明 ID は
ID→被験者の対応表を研究者が別管理する必要があり、`metrics/P*/` を前提とする sync/metrics 側の
追従改修が残る (本タスク外・別タスク)。ユーザーは選択時にこのトレードオフを認識済み。

**解決順 (実装)**: 永続化値(valid) → `GSE_PARTICIPANT_ID`(valid) → `GSE_PID`(valid)
→ 自動生成+永続化 → (P000 は生成/書込失敗時の最終フォールバックのみ)。

## D4 addendum: Part 2 実装中の判断 (2026-06-19、レビュー駆動)

実装と code-reviewer/security-checker レビューを経て確定した補足判断:

- **A. `anyhow` 不採用 → `std::io::Result`**: handoff は `persist_id` を `anyhow::Result` と
  していたが、`anyhow` は本 lib (`gse-next`) の依存ではない (`replay.rs` もコメントで言及のみ・
  実体は `Result<_, String>`)。新規 crate 追加禁止の制約に従い `std::io::Result` で伝播する。
  規約 (rust-standards ルール4「エラーを握りつぶさず伝播」) の意図は満たす。
- **B. `Resolution { Existing, Generated }` 型で「env を永続化しない」を構造保証**: 純粋関数
  `resolve_with_store` の戻り値を 2 値に分け、`Generated` のみ呼び出し側が `persist_id`。
  env / 永続化値由来は `Existing` で再永続化しない (D4 ③) ことを型レベルで担保する。
- **C. アトミック書込 (MEDIUM-2 対応)**: `persist_id_to` は同一ディレクトリの一時ファイル
  (`participant_id.tmp.<pid>`) へ書いてから `fs::rename` で差し替える。途中クラッシュ / 同時起動で
  ファイルが空 / 部分書き込みになり、次回 `load` が「空→再生成」に倒れて端末 ID が変わる事故
  (D4「再起動でも不変」違反) を防ぐ。`fs::rename` は Windows/Unix とも既存を置換しアトミック。
- **D. 永続化 I/O を path 引数化 (MEDIUM-1 対応)**: `persist_id_to(path,..)` / `load_id_from(path)`
  を分離し、env / home を汚さず一時ファイルで往復テスト可能にした。env 差し替えはプロセス共有で
  並列テストとレースするため採らず、FS 往復テストに留める (reviewer 合意)。
- **E. ファイルモード厳密化は見送り (LOW)**: security-checker LOW 指摘の `~/.gse/participant_id`
  を 0o600 にする件は、内容が不透明ランダム ID のみ (本文・PII 非由来、data-privacy ルール1 準拠) で
  実害が極小、かつ主ターゲット Windows は ACL 継承でユーザー専用のため見送る。macOS で厳密化が
  必要になれば `OpenOptions::mode(0o600)` を追加する (将来の任意対応)。
