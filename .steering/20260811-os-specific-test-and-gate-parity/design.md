# 設計

## 実装アプローチ

3 つの独立したサブタスクを順に進める (相互依存なし、それぞれ 1 コミット以上):

1. **`hook_windows.rs` のロジック抽出 + テスト** — コールバック本体 (`hook_callback` /
   `win_event_callback`) の構造・呼び出し順序は変えない。コールバック内の `match` /
   条件式のうち「Win32 API を呼ばず、入力から出力が一意に決まる」部分だけを同ファイル内の
   トップレベル関数として抽出し、コールバックからはその関数を呼ぶ形に置き換える。
   `hook_macos.rs` の `should_request_input_monitoring` 等 (L541-566) と同じ様式
   (「Permission decisions (pure — テストできる形に切り出す)」節を参考に
   「IME mode decisions (pure)」節を新設)。
2. **`ime_windows.rs` / `ime_macos.rs` へのテスト追加** — 既存コードに埋め込まれた
   判定式を同様に純関数として抽出し、テストを追加する。
   ★ `ime_macos.rs` の対象コードはフックコールバックではなくポーリングスレッド内なので
   `hook-constraints` の「コールバック内は Atomic+channel のみ」制約の対象外。
3. **`ci.yml` の `build-windows` job に pubkey.txt gate を追加** — `build-macos` の
   `Verify researcher public key present (release gate)` ステップと同一の grep 条件を、
   `build-windows` job にも追加する。実行タイミングは `npm ci` の後・`Build Tauri app` の前
   (macOS 側と同じ位置)。

**振る舞いを変えないことの保証方法**:
- 抽出する関数は既存の `match` / `if` 式をそのまま関数本体に移すだけで、条件分岐の追加・削除は行わない。
- 各抽出後に `cargo build --target <該当OS>` (macOS 対象分はローカルで) + 既存 `cargo test --workspace`
  を実行し、既存テスト (330件, 2026-08-11 時点で全 green 確認済み) に regression がないことを確認する。
- Windows 側の変更はこのマシン (macOS) ではコンパイル対象外 (`#[cfg(target_os = "windows")]`)
  のため、**Windows CI (windows-latest, `check` job) が緑になることを持って「振る舞い不変」の確認とする**。
  ローカルでの `cargo build`/`cargo test` は macOS 側の変更 (`ime_macos.rs`) のみ検証できる。
- ci.yml の変更は「pubkey.txt がプレースホルダのときに fail する」という新規動作の**追加**であり、
  既存ジョブの動作を変更しない (既存ステップの前後関係・既存 grep 条件を変えない)。

**段階的な変更ステップ** (tasklist.md に対応、1 項目 = 1 コミット):
1. `ime_macos.rs` の抽出 + テスト (ローカルで検証可能、最も安全 → 最初に着手しパターンを確立する)
2. `ime_windows.rs` の抽出 + テスト (macOS ローカルではコンパイル対象外。構文チェックのみ手元で行い、
   Windows CI で最終確認)
3. `hook_windows.rs` の抽出 + テスト (同上、Windows CI 依存)
4. `ci.yml` の pubkey gate 追加 (コード変更なし、YAML のみ。既存 `build-macos` ステップの複製に近い)
5. Windows CI (windows-latest) が緑になることを確認 — 本タスクの完了条件

## 変更対象

### 修正するファイル

- `src-tauri/src/input/hook_windows.rs` —
  - 既存の `is_typing_key(vk_code: u32) -> bool` (L76-90, 既に純関数・0テスト) にテストを追加。
  - `hook_callback` L397-411 (IME モードキー押下時の `IME_OPEN` 遷移判定) を
    `fn ime_open_after_press(vk_code: u32, current_ime_open: bool) -> Option<bool>` として抽出
    (`Some(new_value)` = 遷移する、`None` = 対象キーでない)。呼び出し側は `Some` のとき
    `IME_OPEN.store(..)` + `IME_STATE_DIRTY.store(true, ..)` を行う (Atomic 操作はコールバック側に残す)。
  - `hook_callback` L436-446 (IME モードキー**離**時の遷移判定、Surface Type Cover 固有) を
    `fn ime_open_after_release(vk_code: u32) -> Option<bool>` として抽出。
  - `hook_callback` L421-431 (IME 変換中のナビゲーション/放棄キー分類) を
    `enum ImeNavAction { Navigate, Abandon, Other }` +
    `fn classify_ime_nav_key(vk_code: u32) -> ImeNavAction` として抽出。
  - `hook_callback` L487-495 (`is_ime_mode_key` インライン `matches!`) を
    トップレベル関数 `fn is_ime_mode_key(vk_code: u32) -> bool` として抽出 (呼び出し側は関数呼び出しに置換するだけ)。
  - `#[cfg(test)] mod tests` を追加し、上記関数に対する回帰テストを書く
    (`hook_macos.rs` の 4 テストと同等の水準 = 各関数につき最低 2 ケース)。

- `src-tauri/src/input/ime_windows.rs` —
  - `is_candidate_window_open` L105-110 (WinEvent stale reset の判定) を
    `fn is_stale_winevent_active(winevent_active: bool, enumwindows_active: bool, uia_active: bool) -> bool`
    として抽出。呼び出し側は既存どおり `IME_ACTIVE.store(false, ..)` を行う。
  - `is_ime_candidate_window_visible` のコールバック内 L152 のクラス名判定を
    `fn is_ime_candidate_class_name(class: &str) -> bool` としてコールバック外に抽出し、
    ドキュメント化済みの除外規則 (MSCTFIME / 完全一致 "IME" を含めない) をテストで固定する。
  - `#[cfg(test)] mod tests` を追加。

- `src-tauri/src/input/ime_macos.rs` —
  - `spawn_ime_open_polling_thread` L66-72 の優先順位分岐 (dirty → JIS_KEYBOARD_SEEN → TIS) を
    `enum ImeSource { HookFlag, TisQuery }` +
    `fn select_ime_source(dirty: bool, jis_keyboard_seen: bool) -> ImeSource` として抽出。
  - `#[cfg(test)] mod tests` を追加。

- `.github/workflows/ci.yml` —
  - `build-windows` job に、`build-macos` job の `Verify researcher public key present (release gate)`
    ステップ (既存 L 該当箇所、`grep -qE '^[[:space:]]*age1[0-9a-z]+' src-tauri/resources/pubkey.txt`)
    と同一条件のステップを追加。位置は `npm ci` の後・`Build Tauri app` の前。

### 新規作成するファイル
- なし

### 削除するファイル
- なし

## 影響範囲

- `hook_windows.rs` は `hook.rs:174-175` の `#[path]` 経由でのみ参照される private submodule。
  抽出する関数は同ファイル内に留め、`pub(super)`/`pub` は付けない (外部から呼ばれる必要がない)。
  → `hook.rs` / `lib.rs` への影響なし (impact-analyzer 確認済み)。
- `ime_windows.rs` / `ime_macos.rs` の抽出関数も同様に非公開のまま。`ImeMonitor` の公開 API
  (`is_candidate_window_open`, `spawn_ime_open_polling_thread`) のシグネチャは変えない。
- `ci.yml` の変更は `build-windows` job 内のみ。`release` job の `needs` 条件・成果物一覧は変えない。
  ⚠️ pubkey.txt がプレースホルダのままタグ push すると **Windows ビルドも fail するようになる**
  (現状は macOS のみ fail していた)。これは意図した変更 (release gate の対称化) だが、
  次回タグ release 時に pubkey.txt が正しく設定されているか事前確認が必要。

## 既存パターンとの整合性

- 純関数抽出 + `#[cfg(test)] mod tests` は `hook_macos.rs` L532-566, L913-978 のパターンに従う。
- OS ごとに規則が異なるテストを対にする方針は `liveness.rs` L397-487 のパターンに従うが、
  今回抽出する関数は Windows/macOS で対応する概念が異なる (VK コード体系が違う)ため、
  「同名の対テスト」ではなく「各ファイル内で完結したテスト」とする
  (liveness.rs の `tick_indicates_input` のような **同一関数の OS 別実装**とは性質が異なるため)。

## テスト戦略

- 単体テスト: 各抽出関数について、境界値 (対象キー/対象外キー、true/false 両分岐) を最低 2 ケースずつ。
  `hook_macos.rs` の既存テストのようにコメントで「なぜこの分岐が壊れると何が起きるか」を明記する。
- 統合テスト: 対象外 (フック本体の統合的な動作確認は実機依存であり、本タスクのスコープ外)。
- 手動確認が必要な項目: Windows 実機での CGEventTap 相当 (WH_KEYBOARD_LL) 動作確認は
  requirement.md のスコープ外。CI (windows-latest) の緑化を完了条件とする。

## ロールバック計画

各コミットが独立した最小単位のため、問題が出たコミットのみ `git revert` すればよい。
`ci.yml` の pubkey gate 追加が次回リリースで意図せず Windows ビルドを止める場合は、
該当ステップのみ revert すれば `build-macos` 側の gate には影響しない。
