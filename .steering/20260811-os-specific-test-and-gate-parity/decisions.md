# 重要な設計判断

## 判断 4: code-reviewer 指摘への対応範囲 (2026-08-11 レビュー後)

- **判断日時**: 2026-08-11
- **背景**: `code-reviewer` から MEDIUM 3件・LOW 6件の指摘を受けた。
  すべてを本タスクで対応すると `/refactor` の「振る舞いを変える変更は含めない」
  「バグ修正・新機能追加を混ぜない」制約を超える恐れがあり、対応する/しないの線引きが必要だった。
- **選択肢**: 指摘ごとに個別判断 (一括採用/一括却下ではなく)。
- **採用**:
  - **対応した**: `ime_open_after_press` の `Option<bool>` → `ImeOpenTransition{Set/Toggle/None}` 化
    (MEDIUM-1)。`hook_macos.rs:354` が VK_KANJI トグルに既に `fetch_xor(true, AcqRel)` を使っており、
    Windows 側だけ load→store の非アトミック RMW だったのは是正すべき非対称と判断。
    副作用として MEDIUM-3 (Set/Toggle の縮退テスト) も型で構造的に解消。
    `is_typing_key` の境界値テスト追加 (LOW)。`ime_macos.rs::ImeSource` への Debug/PartialEq derive
    (LOW)。`ime_windows.rs` の矛盾した doc 一覧の削除 (LOW)。
  - **見送った**: press/release 遷移表を `hook.rs` へ移し Windows/macOS で共有する提案 (MEDIUM-2)。
    `is_stale_winevent_active` を struct 引数にする提案・`classify_ime_nav_key` のマジックナンバーへの
    named const 追加・`"CandidateUI"` 冗長条件の削除 (いずれも LOW)。
- **理由**: MEDIUM-1 は「今回touched した hook_windows.rs 単体で完結し、既存の macOS パターンに
  倣うだけ」で追加スコープが無い。一方 MEDIUM-2 はレビューで指摘された通り正しい観察だが、
  実行すると **`hook_macos.rs` (既存4テスト・未touch) への変更が必要**になり、
  decisions.md 判断1 で確定した「抽出範囲は hook_windows.rs のみ」を超える。ユーザー承認済みの
  design.md のスコープを検証中に無断で拡大しない (CLAUDE.md 禁止事項: 「ドキュメント化されていない
  設計判断を勝手に変更しない」)。
- **トレードオフ**: MEDIUM-2 を見送った結果、Windows/macOS の VK_DBE_* 遷移表は
  依然として 2 箇所に重複したまま (今回の変更で「無テストの重複」から「両方テスト済みの重複」に
  改善しただけ)。ドリフト (片方だけ表を書き換えて他方を忘れる) のリスクは残る。
- **影響範囲**: `hook_windows.rs` のみ (`ime_open_after_press` のシグネチャ変更、テスト更新)。
  `hook_macos.rs` は無変更。
- **見直しタイミング**: `hook_windows.rs` / `hook_macos.rs` の VK_DBE_* 遷移表のどちらかを
  変更する必要が生じたとき (ドリフトが実際に起きた/起きかけたとき)、MEDIUM-2 の共通化を
  別タスクとして実施することを検討する。

**補足 (2026-08-12, /cross-review 結果)**: Codex による独立レビューでも新規の論理的欠陥は
指摘されなかった。Codex が挙げた4点 (pubkey gate の形式検証の弱さ / fetch_xor でも
hook↔polling スレッド間競合は残る / 統合的な状態遷移テストの不在 / Windows CI での
テスト実行可否) はいずれも、本 decisions.md の判断3・判断4・design.md のテスト戦略で
既にスコープ外と明記済みか、diff-only レビューによる誤検知 (`check` job の既存
`cargo test --workspace` ステップを見落とした) だった。特に「hook↔polling スレッド間の
IME_OPEN 書き込み競合は fetch_xor でも解消しない」という指摘は判断4の
トレードオフ節で認めている限界と同一であり、Codex が独立に同じ結論に達したことは
判断4の妥当性を補強する。

**補足 (LOW, ドキュメント漏れの是正)**: `ime_macos.rs` の `select_ime_source` 抽出でも同様に
`JIS_KEYBOARD_SEEN.load(Acquire)` が `dirty == true` のときも無条件に評価されるようになった
(旧: `else if` による短絡)。100ms 周期のポーリングスレッド (フックコールバックではない) での
Acquire load 1 回であり、`is_japanese_ime_open()` (dispatch_sync_f) の呼び出し条件は
`match` により従来どおり遅延されるため実害はない。hook_windows.rs 側 (判断1/判断4) と
同じ「無条件 load は Atomic 読み取りのみで副作用なし」という等価性根拠が適用される。

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
