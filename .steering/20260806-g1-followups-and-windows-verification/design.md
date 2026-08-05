# 設計

## 実装アプローチ

前セッションの実装をやり直さず、**残った 3 系統だけ**を閉じる。

| 系統 | アプローチ |
|---|---|
| F-1 二重起動検査の頻度 | ★ **測ってから決める**。実測したうえで「非同期にすれば応答時間の懸念が消える」ので入れた |
| F-2 ロック保持範囲 | ブロックで囲って縮めるだけ（挙動不変） |
| F-3 空 NDJSON | ★ **順序の問題**なので順序で直す。`SessionLogger::start` を 2 段階に割り、ファイルを開くのを `.setup()` へ移す |
| Windows | ⚠️ 実機を触れないので **手順書 ＋ ビルド段取り**まで。実施は研究者 |
| 署名・公証 | ★ 研究者判断で案 A 確定 → **文書だけ**（実装で回避しない） |

## 変更対象

### 修正するファイル

- `src-tauri/src/logger.rs` — `LogChannel`（channel だけ先に作る型）を新設。
  `SessionLogger::start` は `LogChannel::new().start(..)` の薄いラッパに退避（**呼び出し側は無改変**）。
  `SessionLogger::spawn` が **共有 `SharedLogTarget` を上書き**する（新しい `Arc` を作らない）
- `src-tauri/src/lib.rs` —
  - `run()`: `logger::LogChannel::new()` に置換（★ ここではファイルを作らない）
  - `.setup()`: `log_channel.start(log_path, g1_source)` でファイルを開く
  - `spawn_duplicate_instance_check()` を新設し、`setup()` と `start_session()` の両方から使う
  - `start_session()`: `log.lock()` のスコープを縮める
- `experiments/20260801-controlled-friction-task/run.sh` — §5.1 に配線の検査を追加
- `experiments/20260801-controlled-friction-task/protocol.md` — §1.1 に「初回だけ必要な手順」（案 A）、
  §4b.2 に手順 0、§8 に手順書へのリンク
- `experiments/20260801-controlled-friction-task/notes.md` — §4 更新 ＋ §5 追加
- `.github/workflows/ci.yml` — `workflow_dispatch` を追加し、`build-windows` だけ手動で走らせられるように

### 新規作成するファイル

- `experiments/20260801-controlled-friction-task/windows-verification.md` — Windows 検証手順書
  （「操作 → 何を見る → 記録欄」の形・W-1〜W-8）

### 削除するファイル

- なし（★ 計測用の一時テストは計測後に削除した）

## 影響範囲

- ⚠️ ★ **`.manage()` の順序は変えていない。** `SharedLogTarget` を `LogChannel::new()` の時点で
  作り、`start()` が**同じ Arc を上書き**するため、`LogStatusState` の登録位置は従来のまま。
  → 前セッションが「別タスク」に送った理由（`.manage()` の順序に触る）は**回避できた**。
- `start()` 前に送られた行は bounded(512) に溜まる。`run()` から `.setup()` までは同一スレッドの
  数 ms なので溢れない（★ 溢れた場合は従来どおり `try_send` が落とす = 挙動は不変）。
- ★ `SessionLogger::start` の**シグネチャは不変**なので、既存のテスト 8 か所は無改変。

## 既存パターンとの整合性

- `run.sh` §5.1 は **§5（プローブ kill switch）と同じ形**にした:
  grep で配線を見る ＋ `cargo test` で挙動を見る ＋ cargo 不在は `note` で明示（黙って飛ばさない）。
- `spawn_duplicate_instance_check` は既存の「止めずに画面へ出す」方針（`setup()` 側）をそのまま踏襲。
- CI の `workflow_dispatch` は既存ジョブの `if` を足すだけで、**リリース経路（タグ）は無変更**。

## テスト戦略

- 単体: `logger::tests::log_channel_new_does_not_create_file_until_start` /
  `log_channel_buffers_entries_sent_before_start`（2 本・新規）
- 配線: `run.sh` §5.1（grep ＋ 上記 2 本の cargo 実走）
- 回帰: `cargo test --workspace` / `--features package` / golden replay 4 本 /
  `emit_schema` byte-equal / `npx tsc --noEmit`
- ★ **足した検査は全部その場で壊して赤を実測する**（4 通り。`decisions.md` D-3）
- ⚠️ **E2E（実機）は macOS でも未実施**。Windows は手順書のみ。

## ロールバック計画

- F-3: `run()` の `LogChannel::new()` を `SessionLogger::start(log_path, g1_source)` に戻し、
  `.setup()` の `log_channel.start(..)` を削るだけで元の挙動に戻る
  （★ `SessionLogger::start` を残してあるのはこのため）。⚠️ 戻すと `run.sh` §5.1 が**赤になる**。
- F-1: `start_session` の `spawn_duplicate_instance_check` 呼び出し 1 行を消す
- F-2: ブロックの `{}` を外す
- CI: `workflow_dispatch:` と 3 か所の `if` を戻す
