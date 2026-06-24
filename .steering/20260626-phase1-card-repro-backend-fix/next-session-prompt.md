# 次セッション用 開始プロンプト（#1 backend 層2 根本修正 ＋ カード再現性確保）

> このファイル本文を新しいセッションの最初に貼る。GSE-prototype 用。
> 前タスク `20260625-phase1-pilot-fixes`（#1 層1 / #2 / #3）はコミット済
> （branch `feature/phase1-pilot-fixes`、commits ec12f2c〜b3e2a11）。本タスクはその積み残し #1 層2。

---

## 依頼
プローブ/Nudge カードのボタン無反応バグ（#1）の **backend 根本修正** を、再現性を確保したうえで完了させる。
実装系なので **`/start-task`**（task-name=`phase1-card-repro-backend-fix`、本ディレクトリを利用）で steering を起こす。
**ブランチは `feature/phase1-pilot-fixes` を継続**（#1 層1 と同じ PR に属するため）。`/fix-bug` で進める。
backend（logger.rs/lib.rs）変更時は `rust-standards`/`data-privacy`/`hook-constraints` を参照し security-checker 必須。

## 背景（前タスクで確定した事実）
- 3 コマンド（`record_realtime_answer:674` / `record_realtime_skip:706` / `record_intervention_dismiss:234`）の
  共通失敗点 = bounded log channel `tx.try_send`（`logger.rs:789` = `bounded(512)`）。parse 系は全 round-trip 整合で否定済。
- consumer は起動時から常時 drain。毎回失敗の筋は **(a) consumer 死亡 → Disconnected**（`File::create` 失敗で
  `logger.rs:799-804` early return → 以後全 try_send が Disconnected）か **(b) 真の backlog → Full**。
- **最有力仮説 = (a) Disconnected による静かな全データ消失**（前タスク追加調査・blockers B1 詳細）:
  ログパス `default_log_path()` = `$GSE_DATASET/raw/<pid>/...` or fallback `~/Documents/GSE-sessions/...`。
  `File::create` 失敗（GSE_DATASET 誤指定 / **macOS の Documents アクセス未許可**＝ build .app の TCC 未付与等）で
  consumer スレッドが tracing::error のみで死亡 → channel Disconnected。キーストロークは `let _ = try_send`
  （`lib.rs:1144`）でエラー握り潰し → **NDJSON 全損・無通知**、probe/nudge コマンドは Err → カードが閉じない。
  normal load で 512 滞留は非現実的なため Full より Disconnected が濃厚。**深刻度＝較正データ全損なので fail-loud 必須**。
- crossbeam `TrySendError` Display は Full/Disconnected を区別するが、コマンドが両方 `"log channel full"` で潰すため
  **ラベルが誤誘導**（disconnected を full と表示）。
- **前タスクで層1（フロント）は完了**: 両カードとも成功時のみ閉じ、失敗時はカード保持＋インラインエラー＋リトライ。
  無限再表示ループ・死んだボタン化は解消済（`Overlay.tsx` / `ProbeCard.tsx`）。**未解決は backend 層2 のみ**。
- 前タスクで repro 試行 → **再現せず**（その実行では try_send 失敗せず）。原因 = 間欠的＋プローブが出にくい
  （ランダム平均15分・M ホットキーのみ）。**週判定はプローブ発火に無関係**（`probe_scheduler.rs` 確認済）。

## やること（着手順）
### 1【再現性確保】デバッグ用プローブ/Nudge 強制トリガを追加（最優先・これで repro 可能に）
- `debugView`（`VITE_GSE_DEBUG==="1"`、`Dashboard.tsx:163` 既存）gate で、**プローブカードと Nudge を即時に出すボタン**を追加。
  - プローブ: backend に `probe_triggered`(source=random_probe, 有効な probe_id) を即 emit するデバッグコマンド、
    または既存の self-marker（M ホットキー＝`lib.rs:1310`）導線をデバッグボタン化。
  - Nudge: 既存 `force_wall`（`Dashboard.tsx` debugView gate）と同方式で `force_nudge` 的なワンショット。
- これで card→回答→`record_*` と nudge→dismiss→`record_intervention_dismiss` の経路を能動的にテストできる。
- 被験者バンドルから完全除去（debugView 既定 OFF）を維持。`data-privacy`/`intervention-design` 参照。

### 2【根本確定】上記で repro し、console.error の生文字列を確定
- カードのインラインエラー発生時、devtools に出る `record_*` 行（**"...full channel" か "...disconnected channel" か**）を確認。
  これが層2 修正の確定情報。NDJSON 生ログ・キー内容は扱わない。

### 3【backend 層2 修正】（TDD: 回帰テスト先行）
- **誤誘導ラベル是正（無条件で安全）**: `lib.rs` の 3 コマンドの `"log channel full: {}"` を
  Full / Disconnected で文言分岐（`try_send` の `TrySendError` を match）。診断容易化。
- **consumer 耐障害化＋fail-loud（Disconnected の場合・最有力）**: `logger.rs:799-804` の `File::create` 失敗で
  スレッドが黙って死ぬ問題を是正。(1) 確実に書ける場所（temp 等）へフォールバックしデータ全損を防ぐ、
  (2) 失敗を**ユーザーに見える形で通知**（起動時バナー/IPC でフロントへ＝静かな全損を撲滅）、
  (3) 起動時に書込可否を検証（GSE_DATASET 妥当性・macOS Documents 権限）。
  ※ session_meta の fail-loud 化（commit 32fef54）と同じ思想。
- **backlog 是正（Full の場合）**: 容量・drain 律速を是正（realtime_label は落とさない方針維持）。
- 回帰テスト追加（consumer 耐障害 or 文言分岐）。`cargo test --workspace` パス。HMM 不変なら
  `gse-replay --snapshot` は現状維持で確認（schema_dto.rs を触らないこと）。

### 4【研究運用】被験者の起動方法を確定し end-to-end スモークテスト
- 本番ビルド配布（`tauri build`）か dev 配布かを決定（盲検は `VITE_GSE_DEBUG` 既定 OFF で起動方法に依存せず守られる）。
- 決めたビルドで: セッション開始→プローブ/Nudge 表示→各ボタンで確実に閉じ `record_*` が NDJSON に残る、
  第2週でモデル出力が出ない、を実機確認。

### 5【完了処理】
- code-reviewer + security-checker（logger.rs 変更で必須）→ `/finish-task` で `/cross-review`。
- `feature/phase1-pilot-fixes` の PR を出す（前タスク #1 層1/#2/#3 ＋本タスク 層2 をまとめて）。

## 真実源（先に読む）
- 前タスク `.steering/20260625-phase1-pilot-fixes/`（design.md 層1/層2 分離・decisions 判断1/2・blockers B1）。
- `src-tauri/src/lib.rs`（234/674/706 コマンド・1395- プローブスレッド・1310 self-marker ホットキー・debugView は frontend）。
- `src-tauri/src/logger.rs`（788- `SessionLogger::start`・789 bounded(512)・799-804 File::create・827- consumer loop）。
- `src/components/{Overlay,ProbeCard,Dashboard}.tsx`（層1 実装済・debugView gate）。
- `src-tauri/src/analysis/probe_scheduler.rs`（発火条件＝週非依存。poll の away/too_early/gap/cap）。

## 制約
- NDJSON 生ログ・キーストローク内容を外部 LLM/クラウドに送らない（data-privacy）。devtools エラー文字列のみ扱う。
- `*.rs` は `architecture-rules`/`rust-standards`/`hook-constraints`、`src/` は `typescript-standards`（any 禁止）。
- 既存テストを無断削除しない。HMM 挙動を変えるなら `HMM_VERSION` bump＋ゴールデン再生成。
- 原因未特定のまま backend を憶測修正しない（repro の文字列で Full/Disconnected を確定してから）。
- diff に未関係な未ステージ変更（budget.json/scripts/docs削除/MEMO）を混ぜない。
