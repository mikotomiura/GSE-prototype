# design — clipboard-paste-count

## 実装アプローチ (ユーザー承認済み 2026-06-19)

- **検出方式**: 既存キーボードフックで Ctrl+V (Win) / Cmd+V (mac) を検出。OS クリップボード
  API は読まない = 中身に一切触れない。
- **記録粒度**: 1 ペースト = 1 NDJSON 行 `{"type":"paste","t":<ms>}`。回数は行数で算出、
  各ペーストの時刻も保持 (指標 #5 の時系列分析用)。中身フィールドは作らない。

## データフロー

```
hook callback (input/, OS依存)
  V押下(0x56) && 修飾キー押下 → InputEvent.is_paste = true
    Windows: 判定の瞬間に GetAsyncKeyState(VK_CONTROL) で Ctrl 実状態を読む
             (当初案の CTRL_DOWN Atomic 追跡は固着/左右非対称のため不採用。decisions.md D3)
    macOS:   CGEvent::get_flags() の Command マスクを直接読む
  └─ EVENT_SENDER.try_send(InputEvent)  ← 既存 channel をそのまま再利用
        ↓ crossbeam channel
  analysis スレッド (lib.rs)
    event.is_paste なら log_tx_analysis.try_send(LogEntry::Paste { timestamp })
    ※ LogEntry 変換は analysis/ の外 (lib.rs) で実施 = architecture-rules ルール6 遵守
    ※ step()/loop_step.rs は一切変更しない (paste は feature 計算に使わない)
        ↓ crossbeam channel
  SessionLogger スレッド (logger.rs)
    writeln!(writer, r#"{{"type":"paste","t":{}}}"#, timestamp)
```

## 変更対象

### 修正するファイル
1. `analysis/features.rs` — `InputEvent` に `pub is_paste: bool` 追加 + test helper 3 箇所
2. `input/hook.rs` — 変更なし (当初の CTRL_DOWN Atomic 案は撤回。decisions.md D3)
3. `input/hook_windows.rs` — GetAsyncKeyState(VK_CONTROL) で Ctrl 実状態判定 → V&&Ctrl で is_paste=true
4. `input/hook_macos.rs` — get_flags() Command マスクで Cmd+V → is_paste=true
5. `schema_dto.rs` — `LogEntryDto::Paste { t: u64 }` variant 追加
6. `logger.rs` — `LogEntry::Paste { timestamp }` + writer match アーム
7. `lib.rs` — analysis スレッドで event.is_paste → LogEntry::Paste 送出
8. `bin/replay.rs` — `ReplayEvent::Paste { t }` + timestamp()=None + run_replay match アーム
9. `README.md` / `README.ja.md` — InputEvent ドキュメントに is_paste を反映
10. `tests/fixtures/*.ndjson` — paste 行を1行追加して parse 確認 (snapshot 不変を確認)
11. `src-tauri/schema/current.json` — emit_schema 再生成
12. `C:/gse-dataset/schema/current.json` — 同期コピー (既存 drift も一緒に解消)

### 新規作成 / 削除するファイル
- なし

## 影響範囲

- NDJSON スキーマ変更 → emit_schema 再生成 + dataset parity が必須 (取りこぼし注意)。
- exhaustive match 3 箇所 (logger writer / replay timestamp / replay run_replay) に variant
  追加漏れがあるとコンパイルエラー → ビルドで即検知。
- 既存 drift (probe_assignment 等 4 variant) が gse-dataset 側に存在 → 本タスクの同期で一緒に解消。

## 既存パターンとの整合性

- IME_CANDIDATE_NAV_COUNT 等の Atomic フラグパターン (hook.rs) に倣う。
- LogEntry::ImeState の「hook で Atomic/flag → 別スレッドで LogEntry 送出」パターンに倣う。
- schema_dto.rs / logger.rs / replay.rs の 3 型ミラー同期パターンを踏襲。

## なぜ InputEvent に is_paste を足すか (代替比較)

- 既存 channel 再利用で plumbing 不要・per-event timestamp 取得・FeatureExtractor 不読で
  FeatSnapshot 不変 (byte-equal 保持)・InputEvent は NDJSON 非シリアライズ (漏洩経路なし)。
- 却下: 専用 paste channel (plumbing 増)、AtomicU32 集計 (時刻喪失)。

## テスト戦略

- 単体: `cargo test --workspace` 緑 (field 追加で test helper 経由の既存 test を壊さない)。
  paste 検出ロジックの単体テストを追加 (V&&Ctrl→is_paste、V単体→false 等)。
- 統合/回帰: `gse-replay --snapshot` byte-equal (paste を features 未利用 → 不変)。
  fixture に paste 行を1行足し gse-replay が panic せず読めること。
- schema: `emit_schema` 再生成 → current.json 更新 → dataset コピー → parity exit 0。
- E2E (実機手動): Ctrl+V/Cmd+V で paste 行が出る・**中身は出ない**こと。
- レビュー: code-reviewer + security-checker 並列 (焦点=中身が一切メモリ/ログに残らない)。

## ロールバック計画

- 単一 PR・論理単位コミット。問題時はブランチ revert。
- schema は emit_schema 再生成 + dataset 再コピーで元 variant 構成に戻せる。

## スコープ外

- (a) AI 依存度指標の算出 (#5) / anonymize/package (#3#4) / features/HMM 組み込み
