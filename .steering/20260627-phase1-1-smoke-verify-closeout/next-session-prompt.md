# 次セッション用 開始プロンプト（#1 本番スモーク検証 → 後追い → クローズ）

> このファイル本文を新しいセッションの最初に貼る。GSE-prototype 用。
> 前タスク `20260626-phase1-card-repro-backend-fix`（#1 backend 層2）はコミット済・**PR #31 マージ済**。
> 起動方法/fail-loud の docs も **PR #32 マージ済**。本タスクはその実機検証とクローズ。

---

## 依頼
PR #31 でマージ済みの **#1（プローブ/Nudge カードのボタン無反応・出っぱなし）backend 層2 修正**を、
**本番ビルドの実機スモーク**で検証し、結果に応じて後追い修正して **#1 をクローズ**する。
実装/検証系なので **`/start-task`**（task-name=`phase1-1-smoke-verify-closeout`、本ディレクトリを利用）で
steering を起こす。**ブランチは新規**（後追い修正があれば `fix/phase1-1-...`、検証/記録のみなら `chore/...`）。
backend を再修正する場合は `rust-standards`/`data-privacy`/`hook-constraints` 参照、`logger.rs` 変更なら
security-checker 必須。

## 背景（確定事実）
- **#1 症状**: プローブ/Nudge カードのボタンを押しても `record_*` が静かに失敗し、カードが閉じず出っぱなし。
- **根本（静的調査で確定）**: 3 コマンド共通の唯一の失敗点 = log channel `try_send`。最有力 =
  **Disconnected**（`File::create` 失敗で consumer スレッド死亡 → 以後 channel Disconnected → 全 record 失敗）。
  最有力原因 = **macOS の Documents/TCC 権限**（本番 .app）または `GSE_DATASET` 誤指定。
- **PR #31 で実装済（マージ済）**:
  - consumer 耐障害化: `SessionLogger::start` を spawn 前同期 open（primary→**temp フォールバック**→`io::sink()` 縮退）。
    consumer を死なせず **channel を Disconnected にしない** → 「出っぱなし」を構造的に解消。
  - fail-loud: `LogStatus` ＋ `get_log_status` IPC → Dashboard が書込先の警告バナーを常時表示。NDJSON は unix で 0600。
  - 誤誘導ラベル是正: `log_send_error` で Full/Disconnected を区別。
  - 再現性確保: `debug_force_probe`(📝) / `force_nudge`(💡)。**二重 gate**（`VITE_GSE_DEBUG=1` ビルド時＋`GSE_DEBUG=1` 実行時）。
  - 層1（フロント・先行マージ）: 失敗時カード保持＋インラインエラー＋リトライ（死んだボタン/無限再表示は解消済）。
- **未検証 = 実機本番スモークのみ**（Claude は実キーボードフック＋OS 権限＋実セッションを再現できない＝前タスク blockers B1）。

## やること（着手順）
### 1【本番ビルド & 起動】（研究者作業・最重要。dev では TCC 文脈が異なり repro しにくい）
- `VITE_GSE_DEBUG=1 npm run tauri build` で本番ビルド → 起動時に `GSE_DEBUG=1` を渡す。
  - macOS: `open App.app` は env を渡さない → `GSE_DEBUG=1 "App.app/Contents/MacOS/<bin>"` 直接実行 or `launchctl setenv`。
  - Windows: 起動前シェルで `set GSE_DEBUG=1`（or System 環境変数）。両 OS で確認できると望ましい。
- 手順詳細は `docs/calibration-smoke-runbook.md` §1.1–1.2。

### 2【スモーク実行 & 結果確定】（devtools 文字列のみ扱う・NDJSON 生ログ/キー内容は扱わない）
- **📝プローブ強制表示** → Q1/Q2 回答 or skip → **カードが確実に閉じ**、NDJSON に `realtime_label` 行が残るか。
- **💡Nudge強制表示** → dismiss → カードが閉じ `intervention_response` 行が残るか。
- **fail-loud バナーの有無**（「一時フォルダに保存」/「保存できません」）と、出た場合の保存先パス。
- 失敗が出る場合は devtools `console.error` の文字列（**"...full" か "...disconnected" か**）を確定。

### 3【結果に応じた後追い修正】
- **全 OK**（カード閉じる・記録残る・バナー無し）→ #1 を**クローズ**。blockers B1 を解除、steering に検証結果を記録。
- **fail-loud バナー出現**（temp フォールバック/disabled）→ 原因を特定し恒久対処:
  GSE_DATASET 誤指定なら設定ガイド、**macOS Documents/TCC** なら entitlements/Info.plist と起動時権限導線を確認・改善。
- **console.error が "full"**（真の backlog・前タスク未対応分）→ 容量/drain 律速を是正（realtime_label を落とさない方針維持）。
  → backend 変更時は回帰テスト先行・`cargo test --workspace`・`gse-replay --snapshot` 現状維持（schema_dto.rs を触らない）。

### 4【任意・小・別件だが効果大】cross-review の Codex 縮退の恒久対処
- `scripts/run-codex-review.sh` の実行権限欠如で Codex が `Permission denied` 縮退する。`git add --chmod=+x`
  ＋ secrets-filter の自己ブロック回避（wrapper の diff を `--cached` 化）。memory `cross-review-codex-self-block` 参照。

### 5【クローズ処理】
- code-reviewer（backend 触れば security-checker）→ `/finish-task` で `/cross-review`（Codex 権限を直してから）。
- 後追い修正があれば PR。検証のみなら steering 更新＋ chore コミット。

## 真実源（先に読む）
- `.steering/20260626-phase1-card-repro-backend-fix/`（design 実装結果・decisions 判断1/2/3・blockers B1）。
- `docs/calibration-smoke-runbook.md`（§1.1 二重 gate 起動・§1.2 デバッグトリガ&バナー・§4 トラブルシュート）。
- `src-tauri/src/logger.rs`（`open_log_target`/`LogStatus`/`create_file_at` 0600）。
- `src-tauri/src/lib.rs`（`ensure_debug_enabled`/`get_log_status`/`debug_force_probe`/`force_nudge`/`log_send_error`）。
- `src/components/Dashboard.tsx`（fail-loud バナー・debug ボタン・debugView gate）。

## 制約
- NDJSON 生ログ・キーストローク内容を外部 LLM/クラウドに送らない（devtools エラー文字列・集計のみ扱う）。
- 実機 repro/ビルド/スモークは研究者（ユーザー）作業。Claude は結果を受けて判断・修正・記録する。
- HMM 挙動を変えない（変えるなら HMM_VERSION bump＋ゴールデン再生成）。`schema_dto.rs` を触らない。
- diff に無関係な未ステージ変更（budget.json/scripts/docs削除/MEMO）を混ぜない（現在 working tree に残置）。
- スモークで #1 が解消し切らない場合、原因未特定のまま憶測修正しない（console.error/バナーで確定してから）。
