# タスクリスト — Task B backend プローブ scheduler

## 準備
- [x] v0.3 §4/§14, D-8/D-14, Task A 申し送り を精読
- [x] file-finder で統合点(1Hz loop / start_session / global-shortcut / emit / idle / mod.rs / IME thread)特定
- [x] dependency-checker で rand crate 影響確認 → `rand = "0.8"`(lock に 0.8.5 既存), StdRng, rand_distr 不要
- [x] logger 側 producer API(ProbeAssignment / ProbeRef / realtime_label_*)確認

## 設計 (/add-feature Step 3 → 2案比較)
- [x] 設計判断 A: スケジューリング方式 → **A1 Poisson+thinning**(ユーザー承認, DB-1)
- [x] 設計判断 B: B↔C イベント契約 → **B が窓確定し emit に含める**(DB-4)
- [x] design.md 最終化(2案比較を埋込 = /reimagine 相当, ユーザーが実装続行を選択)

## 実装
- [x] `analysis/probe_scheduler.rs` 新規(純粋ロジック・OS API 非依存・seed 注入可能)
  - [x] 指数間隔サンプリング + gap/cap/away thinning
  - [x] 時間隔離窓計算(random_probe: t−31s..t−1s / self_marker: t−35s..t−5s)
  - [x] 不透明 ProbeId 生成(newtype・唯一のコンストラクタが seeded RNG・外部 String 不可)
- [x] `analysis/mod.rs` に `pub mod probe_scheduler;` 追加
- [x] `src-tauri/Cargo.toml` に `rand = "0.8"` 追加
- [x] lib.rs: SESSION_START_MS(static AtomicU64)を start_session で store・スレッドで Acquire 読取
- [x] lib.rs: 専用プローブスレッドを setup() で spawn(AppHandle + logger tx)・1Hz sleep ポーリング
- [x] lib.rs: プローブ確定時に `LogEntry::ProbeAssignment` 送信 + `probe_triggered` emit
- [x] lib.rs: 自己マーカー hotkey(Ctrl+Shift+Alt+M = KeyM)登録 + handler 分岐(debounce, self_marker emit)
- [x] DB-6: 本番 seed を entropy 由来 u64 で引き tracing に記録(一様性監査の再現性)

## テスト
- [x] seeded RNG で gap≥8分 / cap≤2回/30分 / away(idle≥180s)除外 を検証する決定論テスト
- [x] 窓計算の単体テスト(両 source・0 近傍 saturating)
- [x] probe_id が `[A-Za-z0-9_-]` のみ・長さ固定・同一 seed 再現 のテスト
- [x] `cargo test --lib` 緑(108 passed = 既存97 + 新規11, 既存テスト不変)

## レビュー (並列起動)
- [x] code-reviewer + security-checker + test-runner を並行起動
- [x] HIGH 指摘: なし。MEDIUM 対応: DB-6(seed 記録)・clamp コメント修正・saturating_add・DB-7(idle 整理)
- [x] security: CRITICAL/HIGH/MEDIUM なし(型レベル ID 不透明性・atomic 順序・非インジェクション 確認)

## ドキュメント
- [x] docs/architecture.md スレッドモデルに Probe Scheduler 行追加(6→7 スレッド)
- [ ] glossary への用語追加: 不要(random probe / time isolation は Task A 凍結時に追加済)

## 完了処理
- [x] design.md 最終化 / decisions.md(DB-1..DB-7)
- [x] clippy 新規警告ゼロ / npm run build 緑 確認
- [ ] /finish-task(schema parity check 含む)→ commit
