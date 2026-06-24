# 設計（#1 backend 層2 根本修正 ＋ カード再現性確保）

## 実装アプローチ

### 1. 再現性確保（デバッグトリガ・debugView gate）
- **プローブ強制**: backend に `debug_force_probe(app)` コマンドを追加。スケジューラ発火時と同じ
  `probe_triggered`（source=random_probe・有効な `ProbeId`・直近 ~30s 窓を session_start でクランプ）を
  emit する。ProbeCard は既存 listener でカード表示 → 回答/skip で `record_realtime_*` を叩ける。
- **Nudge 強制**: `force_wall` と同方式で `FORCE_NUDGE: AtomicBool` ＋ `force_nudge()` コマンドを追加。
  `get_intervention_decision` の **overlay 分岐**で `FORCE_NUDGE.swap` を消費し、その場で
  `force_nudge_decision`（intervention.rs・action=Nudge・reason="debug_force"）を返す。overlay が自分の
  poll で直接 nudge を受けるため main の `decide()` 上書きと race しない。Overlay 既存ロジックが
  `nudgeVisible` を保持 → dismiss で `record_intervention_dismiss` を叩ける。
- フロント: `Dashboard.tsx` の debugView gate（既存 `force_wall` ボタンと同じ block）に
  「プローブを出す」「Nudge を出す」ボタンを追加。被験者バンドル（既定 OFF）には現れない。

### 2. 誤誘導ラベル是正（無条件で安全）
- `lib.rs` に `log_send_error(e: TrySendError<_>) -> String` ヘルパを追加。Full / Disconnected を
  文言で区別（Disconnected は「logger スレッド死亡＝ログファイル作成失敗の可能性」を明示）。
- `"log channel full: {}"` の 6 箇所（234/532/661/700/735/812）を `.map_err(log_send_error)?` に置換。
  これで repro 時に devtools の `console.error` で Full/Disconnected を即判別できる。

### 3. consumer 耐障害化 ＋ fail-loud（最有力 = Disconnected 対策）
- `SessionLogger::start` を **同期的に書込先を確定**してから thread を spawn する形に変更。
  - `open_log_target(primary)`: `File::create(primary)` 失敗時に **temp**（`std::env::temp_dir()/GSE-sessions/`）
    へフォールバック。それも失敗したら `io::sink()` へ縮退。戻り値で `Box<dyn Write + Send>` を返すため
    consumer ループの `writeln!` 群は無改変（sink は書き込みを捨てる）。
  - いずれの場合も **thread は必ず spawn** され channel を drain → `try_send` が Disconnected を返さない
    （= `record_*` コマンドのカードが閉じなくなる #1 を構造的に解消）。
  - `LogStatus { Ok | Fallback{intended,actual,error} | Disabled{error} }` を返す（fail-loud 情報源）。
- **fail-loud（IPC バナー）**: `run()` が `LogStatus` を受け取り Tauri managed state に保持。
  `get_log_status()` コマンドで DTO（`{ ok, mode, message_ja }`）をフロントへ返す。`Dashboard.tsx`（または
  App）が起動時に取得し、Ok 以外なら固定和文の警告バナーを常時表示（静かな全損を撲滅）。
- **起動時検証**: 上記の同期 File::create 自体が書込可否検証を兼ねる（GSE_DATASET 妥当性・macOS
  Documents 権限の失敗を起動時点で検知）。

## 変更対象

### 修正するファイル
- `src-tauri/src/logger.rs` — `SessionLogger::start` を同期 open + temp フォールバック + sink 縮退に変更。
  `LogStatus` enum / `open_log_target` / `create_file_at` / `temp_fallback_path` を追加。回帰テスト追加。
- `src-tauri/src/analysis/intervention.rs` — `force_nudge_decision` を追加（`force_wall_decision` に倣う）。
- `src-tauri/src/lib.rs` — `FORCE_NUDGE` static・`force_nudge` / `debug_force_probe` / `get_log_status`
  コマンド・`log_send_error` ヘルパ・`"log channel full"` 6 箇所置換・`run()` で LogStatus を managed state
  へ・`invoke_handler` 登録・`SessionLogger::start` の戻り値 4 タプル化に追従。
- `src/components/Dashboard.tsx` — debugView gate にデバッグボタン 2 個・fail-loud バナー。
- `src/components/Overlay.tsx` — （必要なら）force nudge を確実に拾うための微調整。原則 backend 側で
  完結させ、Overlay は既存ロジックのまま `interventionDecision.action==="nudge"` で表示する。

### 新規作成するファイル
- なし（既存ファイルへの追加のみ）。

## 影響範囲
- `SessionLogger::start` の戻り値が 3→4 タプルに変わる。caller = `lib.rs:1017` ＋ test 2 箇所
  （`logger.rs:1977`/`2075`）を追従。
- HMM 挙動・NDJSON schema は不変 → ゴールデン/Schema 再生成不要（schema_dto.rs を触らない）。
- `logger.rs` 変更のため security-checker 必須（data-privacy: パスは記録するがキー内容は不変）。

## 既存パターンとの整合性
- Nudge 強制は `force_wall`（FORCE_WALL atomic + ワンショット消費）に倣う。
- fail-loud は session_meta の fail-loud 化（commit 32fef54）と同じ思想。
- ProbeId は型で本文混入を排除（`ProbeId::generate`）。debug でも外部 String 経路を作らない。
- debugView gate は `VITE_GSE_DEBUG==="1"`（前タスク decisions 判断2・起動方法非依存）。

## テスト戦略
- 単体（logger.rs）: (a) primary が作成不能（親が file）でも `open_log_target` が temp に Fallback し
  書き込めること、(b) `LogStatus` が Fallback を返すこと。
- 単体（lib.rs or logger.rs）: `log_send_error` が Full / Disconnected を区別すること
  （bounded(1) を満杯 → Full、receiver drop → Disconnected）。
- 回帰: `cargo test --workspace` パス。`gse-replay --snapshot tests/snapshots/minimal.json` 現状一致。
- E2E: 本番ビルドで実機スモーク（プローブ/Nudge 表示→各ボタンで閉じ `record_*` が NDJSON に残る／
  書込失敗時に fail-loud バナー）。**実機 repro/リビルドは研究者（ユーザー）作業**。

## ロールバック計画
- フロント debug ボタン/バナーは差分が局所的で revert 容易。
- `SessionLogger::start` の戻り値変更は caller 追従が必要だが論理は加算的（フォールバック追加）で
  既存挙動（primary 成功時）は不変。問題時は open_log_target を従来の直接 File::create に戻すのみ。

## 実装結果（2026-06-26・最終）
- 計画どおり実装完了。`cargo test --lib` 221 件パス（新規: `open_log_target_*` ×2 /
  `log_send_error_distinguishes_full_and_disconnected` / `force_nudge_decision_is_pure_one_shot`）。
  `cargo fmt --check` クリーン・`clippy` 新規警告なし・`tsc --noEmit` パス・
  `gse-replay --snapshot tests/snapshots/minimal.json` 一致（HMM 不変確認）。
- レビュー反映（code-reviewer / security-checker, HIGH/CRITICAL なし）:
  - `force_nudge_decision` を `&self` の純ワンショット化（`last_decision` を汚さない）。
  - FORCE_WALL(main) / FORCE_NUDGE(overlay) の consumer ウィンドウ非対称を対比コメント化。
  - `create_file_at` を unix で file=0600 / dir=0700 に制限（キーストロークログを所有者限定・判断3）。
  - `get_log_status` 取得失敗時もバナーを出す（fail-loud の一貫性）。
  - `debug_force_probe` の同一 ms ID 衝突をコメント化。
- 判断は decisions.md（判断1 スコープ / 判断2 ゲート方針 / 判断3 権限）に記録。
- **残作業（研究者）**: 本番ビルドでの実機 repro / スモークテスト（blockers.md 参照）。
