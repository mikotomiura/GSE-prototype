# タスクリスト: Phase 2b IME Shadow Features

## 準備
- [x] requirement.md 記入済み
- [x] design.md 記入済み (承認済み)
- [x] file-finder + impact-analyzer 完了

## 実装

### T1: hook.rs — Windows 専用 Atomic 追加
- [x] AtomicU32 import を非条件化 (macOS/Windows 共用)
- [x] `#[cfg(target_os = "windows")]` で 5 Atomic 宣言追加

### T2: hook_windows.rs — WinEvent + hook_callback 拡張
- [x] WinEvent IME_SHOW: `IME_COMPOSITION_START_MS.store(now)` + カウンターリセット
- [x] WinEvent IME_HIDE: dwell 計算 → `IME_SHADOW_DWELL_MS.store` + `IME_SHADOW_READY.store(true)`
- [x] hook_callback: IME_ACTIVE 中の arrow key → `IME_CANDIDATE_NAV_COUNT.fetch_add(1)`
- [x] hook_callback: IME_ACTIVE 中の ESC → `IME_SHADOW_ABANDON.store(true)`
- [x] super:: import に新 Atomic 追加

### T3: logger.rs — LogEntry::ImeShadow バリアント追加
- [x] LogEntry に ImeShadow バリアント追加
- [x] match アームで NDJSON writeln! 追加

### T4: schema_dto.rs — LogEntryDto::ImeShadow 追加
- [x] LogEntryDto に ImeShadow バリアント追加

### T5: lib.rs — IME Monitor スレッドで ImeShadow emit
- [x] active→false 遷移時に IME_SHADOW_READY チェック + emit
- [x] Safety valve (8s stale) パスでも shadow emit
- [x] emit_ime_shadow ヘルパー関数 (#[cfg(windows)])

### T6: replay.rs — ImeShadow 読み飛ばし
- [x] ReplayEvent に ImeShadow バリアント追加
- [x] timestamp() で None 返却 (ソート除外)
- [x] run_replay match アームに追加

## テスト

### T7: logger.rs 単体テスト
- [x] ImeShadow NDJSON フォーマット検証テスト 3 件 (normal/abandoned/zero)

### T8: 回帰テスト
- [x] cargo test 72/72 PASS
- [x] cargo clippy: 新規警告なし (既存 28 件は Phase 2b に無関係)

### T9: schema 再生成
- [x] `cargo run --bin emit_schema` で schema/current.json 更新 (ime_shadow バリアント追加確認)

## レビュー
- [x] code-reviewer + security-checker 並列実行
- [x] HIGH: Atomic ordering コメント追記 (hook.rs IME_SHADOW_READY)
- [x] MEDIUM: IME_CHANGE defensive fallback (hook_windows.rs)
- [x] MEDIUM: Stale リセット時の shadow emit フォールバック (lib.rs emit_ime_shadow)
- [x] MEDIUM: 既知の制約をコメント記録 (hook_windows.rs)
- [x] 修正後 cargo test 72/72 PASS

## ドキュメント
- [x] docs/architecture.md §4.1 に Windows Phase 2b Atomic 一覧追記
- [x] docs/architecture.md §4.6 に LogEntry::ImeShadow バリアント追記

## 完了処理
- [x] 実機検証: 5 セッション / 148 件の ime_shadow emit 確認 (gse_20260417_03-04時台)
- [x] /finish-task
