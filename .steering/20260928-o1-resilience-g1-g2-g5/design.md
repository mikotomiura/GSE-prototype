# 設計 — o1-resilience-g1-g2-g5

> 一次の根拠は decisions.md §0 と本書の各節に行番号で残す（2026-09-28・worktree `feature/o1-resilience-g1-g2-g5` @ `e11111ee`）。

## 実装アプローチ

3 つとも **O1 モードの内側だけ**で効かせる。G1（`v0.1.36` 凍結）の挙動は 1 バイトも変えない。判定は純関数に切り出し、両 OS でテストする。

### G-5 送信見送り（32 MB 超）— `reconcile.rs`
- 送信ループ（`reconcile.rs:767-801`）は G1 と共有なので、**`CollectionMode::O1` のときだけ**次を行う:
  1. **送る前**: `.age` のバイト数が `O1_MAX_UPLOAD_BYTES = 32 * 1024 * 1024` を**超えたら**、uploader を呼ばずに隔離する。等号（ちょうど 32 MiB）は送る。GAS `GSE_O1_Submit.gs:218` の `> MAX_BYTES` と同じ境界にそろえる。
  2. **送った後**: 受け口が `too large` を返したら隔離する。そのために `Uploader::upload` の戻り値を `Result<(), UploadError>`（`TooLarge` / `Other(String)`）に変える。`HttpUploader` は応答 JSON の `error == "too large"` を**構造として読む**（`response_is_ok` と同じ流儀）。偽 uploader 4 本は機械的に追従させる。
     - ⚠️ G1 で `TooLarge` が返った場合は、**今までどおりエラーとして残すだけ**にする（G1 の受け口も同じ文言を返す: `Form_G1/GSE_G1_Submit.gs:146-147`）。
- 隔離の中身は `submission_dir/oversize/` への `rename`（同じボリューム内の移動）。`list_age_files` は非再帰（`submission.rs:308-325`）なので、移したファイルは以後の再送対象からも未送信の件数からも自然に外れる。**ファイルは消さない**。
- 採番は台帳 `manifest.jsonl` の最大値も見る（`reconcile.rs:553-565`。`append_manifest` は梱包の直後 `:722-732`）。したがって**隔離しても日番号は再利用されない**。研究者には、受け口の欠番検知（`GSE_O1_Ledger.gs`）が 5 日後に知らせる。
- 研究者向けの記録:
  - `ReconcileReport` に `quarantined` を足し、`GSE_RECONCILE` の要約 JSON に件数を出す（親プロセスが applog に残す: `lib.rs:2048`）。
  - 隔離 1 件ごとに `errors` にも 1 行積む。その回は exit 1 になり、`lib.rs` 側で `error!` が出る。**1 ファイルにつき 1 回きり**で、次の回は対象外なので繰り返さない。
  - ⚠️ ファイル名・P-ID は要約行に出さない（`submit.rs:416` の方針どおり）。
- 削除台帳: `docs/o1-deletion-ledger.md` の端末側（B-4）に `GSE-submissions/oversize/` を足す（削除保証の範囲が広がるため）。

### G-2 O1 定期再送 — `lib.rs` / `o1.rs` / `App.tsx`
- `ReconcileReason::O1Periodic = 5` を足す（`lib.rs:1785`）。`label()` は網羅 match なので、足し忘れはコンパイルで分かる。`App.tsx:52-58` の古いコメント（4 が抜けている）も直す。フロントの分岐は G1 の内側だけ（`App.tsx:695,705`）なので、表示は変わらない。
- 既存の O1 日次ローテートスレッド（`lib.rs:3884-3932`・60 秒ごとに確認）に相乗りする。純関数 `o1::periodic_reconcile_due(now_ms, last_ms)` と定数 `O1_PERIODIC_RECONCILE_MS = 6h` を足し、真なら `spawn_reconcile(O1Periodic)` を呼ぶ。
  - `last_ms` の起点はスレッド開始時刻（＝起動時の reconcile の直後）。
  - ローテートで reconcile したときも起点を更新する（直後に重ねて走らせないため）。
- 排他は既存の `ReconcileLock` で足りる（後から来たほうは `Busy` で何もしない）。新しい仕組みは作らない。

### G-1 O1 自動起動 — ★ 方式の変更を提案（研究者の承認が要る）
grill では「プラグイン」を選んでもらったが、一次で読んだ結果、**プラグインを使わず、同じことを自前で書く**ことを提案する。理由（すべて一次）:

| 問題 | 根拠 |
|---|---|
| 最新 2.6.0 は **tauri 2.12 以上を要求**する（repo は 2.10.2）ので、tauri 本体の版上げが付いてくる。2.5.1 なら避けられるが、古い版に固定することになる | crate の `Cargo.toml` |
| Windows の Run キーに**引用符なしで**パスを書く（`format!("{} {}", app_path, args)`）。ユーザー名にスペースがあると「引用符なしパス」の問題を踏む | `auto-launch-0.5.0/src/windows.rs` `enable()` |
| Windows の `enable()` は、タスクマネージャーでの無効化（`StartupApproved\Run`）を**有効へ書き戻す**。「被験者の選択を尊重する」（判断 2）と逆向き | 同上 |
| macOS の plist にパスを**エスケープせずに**埋め込む。`&` や `<` を含むフォルダでは壊れた plist になる | `auto-launch-0.5.0/src/macos.rs` `enable()` |

自前の中身（到達点はプラグインの LaunchAgent 方式と同じ）:
- **macOS**: `~/Library/LaunchAgents/com.johnd.gse-next.o1.plist` を書く。中身は `Label`、`ProgramArguments`（`.app/Contents/MacOS/gse-next` の実体パスを XML エスケープしたもの）、`RunAtLoad=true`。plist の文字列は純関数 `autostart::launch_agent_plist(exe)` で作り、テストで検証する。
- **Windows**: `HKCU\Software\Microsoft\Windows\CurrentVersion\Run` に、値名 `GSE-O1`・値 `"<exe>"`（**引用符つき**）を書く。`windows` crate の `RegSetKeyValueW` を使う（`Cargo.toml` の既存 `windows` 依存に `Win32_System_Registry` feature を足すだけ）。unsafe はラッパー関数 1 つに閉じる。`StartupApproved` には**触らない**。値の文字列は純関数で作り、テストする。
- **1 回だけ登録する**: 配布フォルダ（`o1.mode` の隣）に印ファイル `o1.autostart` を置き、印があれば何もしない。純関数 `o1::autostart_action(o1_mode, g1_mode, marker_exists) -> {Register, Skip}` を両 OS でテストする。
  - 印を配布フォルダに置く理由: 新しい版のフォルダを配り直したとき、**古いフォルダの exe を指したまま**になるのを防ぐため（データフォルダに置くと、新しいフォルダでは登録されない）。
  - 登録に失敗したら印を置かない（次の起動でもう一度試す）。applog に `warn!` を残す。
- 新しいファイル `src-tauri/src/autostart.rs` を作る（OS 依存は `#[cfg]` でこのファイルに閉じる。`analysis/` には置かない）。
- 被験者に見えるもの: macOS 13 以降は「バックグラウンド項目が追加されました」の通知が出る見込み（実験で確かめる）。Windows はタスクマネージャーの「スタートアップ アプリ」に出る。

### 文面（同意文書・README）— 研究者の承認が先
- README（`dist-readme-macos-o1.txt` / `dist-readme-windows-o1.txt`）の【3】「自動的に立ち上がるようにする（おすすめ）」の**手動手順を外し**、次の 3 点に差し替える。
  - 「初回の起動で、自動的に立ち上がるよう設定されます」
  - **切り方**（macOS: システム設定 → 一般 → ログイン項目と機能拡張 → gse-next をオフ／Windows: タスクマネージャー → スタートアップ アプリ → 無効）
  - **やめるときの消し方**
  - ⚠️ 手動手順を残すと二重起動になる。single-instance（`lib.rs:3716`・O1 でも無条件）が 2 個目を止めるたびに窓が前面に出てしまう。
- 同意文書に 1 文足すかどうかは、文面案を見て研究者が決める。

## 変更対象

### 修正するファイル
- `src-tauri/src/reconcile.rs` — G-5（隔離・`UploadError`・`quarantined`）
- `src-tauri/src/bin/submit.rs` — 要約 JSON に `quarantined`
- `src-tauri/src/lib.rs` — `O1Periodic`・ローテートスレッドへの相乗り・自動起動の呼び出し
- `src-tauri/src/o1.rs` — `periodic_reconcile_due` / `autostart_action` / 定数
- `src-tauri/Cargo.toml` — `windows` の feature 追加のみ
- `src/App.tsx` — コメントの数値対応
- `docs/o1-deletion-ledger.md`（B-4 に oversize/）・`docs/functional-design.md`・`docs/glossary.md`（O1 自動起動の定義を自前方式に合わせる）
- `experiments/20260801-controlled-friction-task/dist-readme-*-o1.txt`（文面。承認後に反映）

### 新規作成するファイル
- `src-tauri/src/autostart.rs` — 登録内容の生成（純関数）と OS ごとの書き込み

## 影響範囲
- G1: 送信ループの新しい処理は `CollectionMode::O1` の内側だけ。自動起動と定期再送も O1 だけ。
- `Uploader` trait の変更は reconcile.rs の中だけ（実装 5 本: 本番 1・偽 4）。
- 鮮度ゲート（`check-o1-release-readiness.sh`）は `Cargo.toml` を見ているので、今回の変更は「古い」と判定される側に入る。`Cargo.lock` を見ていない穴は既知で、今回は触らない。

## 既存パターンとの整合性
- 純関数＋両 OS テスト（`o1::decide` / `g1::folder_up` の流儀）。
- 応答 JSON を構造として読む（`response_is_ok`）。
- 印ファイル（`.sent` / `.age.ok` の流儀）。
- 周期処理は既存のローテートスレッドに相乗りする（新しいスレッドを作らない）。

## テスト戦略
- G-5:
  - 32 MiB+1 は uploader が呼ばれず `oversize/` に移る／ぴったり 32 MiB は送る
  - `TooLarge` 応答で移る
  - 移したものは次の回で数えない・送らない
  - **G1 では 32 MiB 超でも隔離しない**（負の対照）
  - 日番号が再利用されない
  - ⚠️ テスト用に 32 MiB のファイルを作らずに済むよう、上限を `ReconcileOptions` に持たせる（本番は定数）
- G-2: `periodic_reconcile_due` の境界（6h−1ms / 6h）。
- G-1: `autostart_action` の全組み合わせ（O1 × G1 × 印）・plist の中身（エスケープ）・Run 値の引用符。両 OS で走る純関数でテストする。
- 各テストは**壊して赤を見る**（変異検査）。
- `cargo test --workspace --features package`・fmt・clippy `-D warnings`・`npx tsc --noEmit`。Windows の registry 呼び出しは CI と研究者の実機でしか確かめられない（memory `windows-only-code-needs-ci`）。
- 実機: G-1 の Mac 小実験（`g1-mac-autostart-experiment.md`）。段階 A は Claude が実行できるが、**研究者の許可が要る**（研究者の Mac で O1 アプリをバックグラウンド起動し、打鍵の時刻を記録するため。送信先はダミー）。

## ロールバック計画
- O1 用のタグを打つ前なら PR を revert する。
- 配布後なら、被験者の端末で自動起動を解除してもらう（README の手順）。v0.1.37 に戻すこともできる（まだ誰にも配っていない）。

## 実装中に変わったこと（2026-09-28・decisions.md 判断 12）
- G-1 の登録条件に **O1 の同意確認（R-7）** を加えた。呼ぶのは起動時と `acknowledge_o1_enrollment` の直後の 2 か所。印ファイルは**先に**書き、書けなければ登録しない。
- G-5 の `UploadError::TooLarge` は応答本文を持ち、表示は従来の文言（G1 のログ不変）。`next_o1_day_number` は `oversize/` も数える。要約行の `quarantined` は 1 以上のときだけ。
- G-5 の実装中にテストで**包み直しの無限の繰り返し**を見つけて塞いだ（② の「包み済み」判定が `oversize/` を見ていなかった）。
