# 重要な設計判断

## 判断 1: hook_windows.rs の抽出範囲

- **判断日時**: 2026-08-11
- **背景**: `hook_windows.rs` は WH_KEYBOARD_LL コールバックで、`hook-constraints` skill の制約
  (コールバック内は Atomic + channel send のみ) がある。テストを追加するには何らかの形で
  ロジックを切り出す必要があるが、切り出し方の範囲を確定する必要があった。
- **選択肢**:
  - A: 判定/変換ロジック（純粋関数部分）のみ抽出。コールバックの構造・呼び出し順序は変えない
  - B: コールバック内の実装を大きく作り替えて全面的にテスト可能な形にする
- **採用**: A
- **理由**: ユーザー判断 (grill 時の回答)。挙動変更ゼロを保証しやすく、`hook_macos.rs` の
  既存パターン (`should_request_input_monitoring` 等) と一貫する。B は事故のリスクが高く、
  今回のゴール (テストカバレッジの是正) に対して過剰。
- **トレードオフ**: `is_paste` (GetAsyncKeyState 依存) のように Win32 呼び出しと不可分な
  ロジックは抽出対象外のまま残る = 完全なカバレッジにはならない。
- **影響範囲**: `hook_windows.rs` 内の抽出関数の設計（design.md「変更対象」参照）。
- **見直しタイミング**: `hook_windows.rs` のコールバック全体を書き直す別タスクが発生したとき。

## 判断 2: Windows 側の動作確認体制

- **判断日時**: 2026-08-11
- **背景**: 本セッションは macOS 上で動作しており、`#[cfg(target_os = "windows")]` の
  コードはこのマシンでは 1 行もコンパイルされない (memory `windows-only-code-needs-ci` と同型)。
  Windows 側の変更の実行確認手段を確定する必要があった。
- **選択肢**:
  - A: CI (windows-latest, `check` job) のみで確認
  - B: CI に加え、別途 Windows 実機セッション (Windows 側 Claude Code) に確認を依頼する
- **採用**: B
- **理由**: ユーザー判断。CI が唯一の実行経路だが、CI が緑でも「実機のフックが実際に打鍵を
  正しく分類するか」までは保証しない。memory `windows-agent-collection-only` の運用実績
  (Windows 実機収集は Windows 側 Claude Code に依頼する) に倣う。
- **トレードオフ**: 本タスク単体では実機確認まで完了しない。CI 緑化を本タスクの完了条件とし、
  実機確認は別途依頼として切り出す。
- **影響範囲**: requirement.md の受け入れ条件は CI 緑化まで。実機確認は tasklist.md に含めない。
- **見直しタイミング**: Windows 実機セッションへの依頼を実施したとき、その結果を本 steering
  ディレクトリに追記する。

## 判断 3: Windows 側 release gate の対象

- **判断日時**: 2026-08-11
- **背景**: `build-macos` job には pubkey.txt のプレースホルダ検査があるが、Windows は
  `--no-bundle` のポータブル exe でリソース埋め込みの経路が無く、macOS と同じ「dmg 埋め込み
  前提」の検査はそのままでは移植できない。
- **選択肢**:
  - A: `src-tauri/resources/pubkey.txt` 自体のプレースホルダ検査を `build-windows` job にも追加
       (実際に exe に同梱されなくても、リポジトリの鍵ファイルが未設定のままリリースされる事故を防ぐ)
  - B: gse-submit.exe/gse-unpack.exe の成果物存在確認 (既存) のみで十分とする
  - C: 今回のスコープ外とする (配布構造が本質的に違うため「対称化」自体が不適切な可能性)
- **採用**: A
- **理由**: ユーザー判断。Windows のポータブル配布フォルダも最終的には同じ
  `src-tauri/resources/pubkey.txt` に由来する鍵を researcher が手動で同梱する運用であり、
  リポジトリ側のプレースホルダ検査は配布構造に依存しない共通の安全網として機能する。
- **トレードオフ**: この検査は「exe に実際に鍵が同梱されているか」までは保証しない
  (Windows の配布フォルダ組み立ては CI 外の手動/半自動プロセスのため)。真の意味での
  「同梱物検査」の対称化は今回のスコープ外 (requirement.md 参照)。
- **影響範囲**: `.github/workflows/ci.yml` の `build-windows` job のみ。
- **見直しタイミング**: Windows ポータブル配布フォルダの組み立てが CI 化されたとき、
  そこで本物の同梱検査を追加すべきか再検討する。
