# 重要な設計判断

## 判断 1: repro 前でも consumer 耐障害化＋fail-loud を今セッションで実装する

- **判断日時**: 2026-06-26（ユーザー確定 = AskUserQuestion「全部やる」）
- **背景**: タスク制約に「原因未特定のまま backend を憶測修正しない（repro の文字列で
  Full/Disconnected を確定してから）」とある。一方 Claude は実キーボードフック＋OS 権限＋実セッションを
  伴う repro を実行できず（前タスク blockers B1）、研究者しか repro/リビルドできない。
- **選択肢**:
  - A: 全部やる（デバッグトリガ＋誤誘導ラベル是正＋consumer 耐障害化＋fail-loud＋回帰テスト）
  - B: 安全な部分のみ（デバッグトリガ＋ラベル是正＋テスト）、consumer 耐障害化は repro 後の次セッション
- **採用**: A（ユーザー確定）
- **理由**: consumer 耐障害化（`File::create` 失敗で thread を死なせず temp フォールバック＋sink 縮退）は
  **Full / Disconnected の両方に有効**で、Disconnected を前提とした「憶測修正」ではない。`File::create`
  失敗で consumer が黙って死ぬ → channel Disconnected → NDJSON 全損・無通知は、どの症状経路でも成立する
  **実在の欠陥**であり、severity（較正データ全損）から fail-loud は必須（next-session-prompt 明記）。
  channel を構造的に Disconnected にしないことで #1（カードが閉じない）も原因側で解消する。
- **トレードオフ**: backlog（真の Full）専用の容量・drain 律速是正は未着手（repro で Full 確定時のみ）。
  ただし realtime_label を落とさない方針は維持。
- **影響範囲**: `logger.rs`（start の同期 open 化・4 タプル化）・`lib.rs`（caller 追従・状態 IPC）。
  HMM/schema 不変。
- **見直しタイミング**: 研究者の repro で `console.error` が「full」だった場合 → 真の backlog 対策
  （容量/drain）を別途検討。「disconnected」だった場合 → 本修正が直撃で当たる。

## 判断 2: デバッグコマンドのゲートはフロント (VITE_GSE_DEBUG) のみとし backend には cfg ゲートを置かない

- **判断日時**: 2026-06-26
- **背景**: security-checker MEDIUM 指摘 = `debug_force_probe`/`force_nudge` は `invoke_handler` に
  常時登録され、被験者バンドルでも DevTools/IPC から直接呼べる（backend ゲートなし）。`#[cfg(debug_assertions)]`
  か feature flag でリリースから外す案。
- **選択肢**:
  - A: フロント (VITE_GSE_DEBUG gate) のみ。backend は常時登録（既存 `force_wall` と同水準）
  - B: backend も `#[cfg(debug_assertions)]` で二重ゲート
- **採用**: A
- **理由**: フロントの `VITE_GSE_DEBUG` は **Vite ビルド時 env** で、Rust の `debug_assertions`
  （dev/release）とは独立。研究者のスモークテストは**本番（release）ビルド**で行う想定
  （next-session-prompt §4）で、そのとき `VITE_GSE_DEBUG=1` でビルドすればボタンを出せるが release では
  `debug_assertions` が OFF。B にすると「ボタンは出るが invoke が失敗」する不整合が起き、本番スモークの
  デバッグトリガが使えなくなる。Tauri IPC は同一アプリ WebView 内からのみ到達可能で外部ネットワークから
  叩けないため、これはセキュリティ境界ではなくデータ整合性（`reason="debug_force"` で解析除外可能）の話。
  既存 `force_wall` と同設計を踏襲し一貫性を保つ。
- **トレードオフ**: 被験者が能動的に DevTools を開けば debug 介入を発火しデータ汚染しうる（解析側で
  reason により除外可能）。盲検は `VITE_GSE_DEBUG` 既定 OFF で守られる（前タスク decisions 判断2）。
- **影響範囲**: `lib.rs` invoke_handler・`Dashboard.tsx` debugView gate。
- **見直しタイミング**: 被験者の DevTools 操作によるデータ汚染が実際に観測された場合、または本番スモークで
  デバッグトリガが不要になった場合は B（cfg ゲート）へ移行する。

## 判断 3: NDJSON ログファイルを unix で 0600 / ディレクトリ 0700 に制限

- **判断日時**: 2026-06-26
- **背景**: security-checker MEDIUM 指摘 = temp フォールバック先（`$TMPDIR/GSE-sessions`）が
  `TMPDIR` 上書きで共有ディレクトリ（例 `/tmp`）になると、キーストローク動態（VK コード列）を含む NDJSON が
  他ローカルユーザーに読まれうる。
- **採用**: `create_file_at` を unix で `OpenOptions.mode(0o600)`＋親 dir を `set_permissions(0o700)` にする。
- **理由**: primary/temp いずれの書込先でも NDJSON を所有者のみに制限すれば、共有 temp へ落ちても漏洩しない。
  キーストロークデータは data-privacy の最重要対象（ルール 2: ローカルのみ）であり、所有者限定は素直な強化。
  非 unix（Windows）は従来 `File::create`（NTFS ACL は既定で他ユーザー読取り不可）を維持。
- **トレードオフ**: 既存 primary パスの権限も締まる（gse-replay/gse-dataset 同期は同一ユーザーのため影響なし）。
- **影響範囲**: `logger.rs::create_file_at`（全 SessionLogger 書込先）。
