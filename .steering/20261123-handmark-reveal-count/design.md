# 設計

## 実装アプローチ

判定は駆動役（`handmark_driver.rs`・純粋）に置き、OS の呼び出しは出来事（`Effect`）を受けて `lib.rs` が OS ごとのファイルへ渡す。今の「やめる」「描く」と「カーソル」「クリック」と同じ作り。

### 1. 駆動役（純粋）

- 状態 `revealed: bool`（いまどけているか）を持つ。
- トレイの項目 `RevealItem { Hidden, Reveal, Return }`。文言は `Reveal` が「ほかの窓をどける」、`Return` が「窓を戻す」。窓を出している（`window_open`）ときだけ `Hidden` 以外にする。`sync_tray` で今の項目と一緒に知らせる（`Effect::RevealItem`）。
- 出来事 `Effect::Reveal(bool)`（真 = どける・偽 = 戻す）。行き先は窓の側（記録へは向かない・`destination` の網羅の match に足す）。
- `toggle_reveal(fs, shown, now)`: 押された項目の文言（メニューに出ていた側）が駆動役の今の項目と違えば何もしない（今の「やめる」と同じ照合）。
  - `Reveal`: 一時停止中でなければ日の累計の回数を 1 足し、状態ファイルへ保存する（書けなければ今の `save_or_clean_up` の始末）。`revealed = true`、`Effect::Reveal(true)`。行は書かない（行を書くと押した時刻が行の `t` に出るため。回数は次の 5 分の行に載る・判断 2）。
  - `Return`: `revealed = false`、`Effect::Reveal(false)`。数えない。
- 自動で戻す: どけている間に、窓を閉じる（「やめる」・門が閉じる・窓の失敗・保存の失敗）・日が変わる・終了するときは、`Effect::Reveal(false)` を先に出して `revealed = false` にする（判断 4）。`close_window` と日の変わり目と `on_quit` の 3 か所に置く。駆動スレッドが抜けたときの後始末（`lib.rs` の `HandmarkWindowGuard` の Drop）でも、項目を隠して OS の戻しを直接呼ぶ（判断 6）。

### 2. 日の累計と行

- `DayRecord` に `reveal_count: u64`（`#[serde(default)]`・古い状態ファイルは 0 と読む）。`add_reveal()`。日の変わり目で 0、`minimal_keeping_off` でも 0（量は時刻を落とす形に残さない・`shown_ms` と同じ）。
- `Evaluation::add_reveal()`（`add_shown` と同じく今日の記録の日だけ）。
- `HandmarkDayRow` と行に `reveal_count`（`visible_ms` の直後・記録が無いときは null）。
- schema（`schema_dto.rs` の `HandmarkDay`）に `reveal_count: Option<u64>` と説明。`emit_schema` で `current.json` を作り直し、gse-dataset の写しと照合する。

### 3. 区間の削除

`shown_ms`・`visible_ms` と同じ「前後の行の差を引く」規則に、回数を 3 つ目の量として足す（predist-fixes 判断 1）。

- `HandmarkSnap`・`HandmarkSub` に `reveals`。行の `reveal_count` が無い・null の行は 0 と読む（古い行）。
- `handmark_subtractions`: 差を回数にも取り、3 つの量のどれかが 0 でなければ引く。区切り（累計が 0 から始め直した所）は、3 つの量のどれかが前の写しより減った所とする（判断 6）。
- 引く式は 1 つにする: `day::subtract_count` を行（`subtract_handmark_day`）と走行中の累計（`DayRecord::subtract`）の両方が使う（片方だけ変わると差から区間の量が読めるため・今の `subtract_totals` の約束）。
- `subtract_handmark_day` は、行に数の `reveal_count` があるときだけ書き換える（古い行の形を変えない）。

### 4. OS の呼び出し

覚えた一覧はメモリにだけ置き、記録・tracing に出さない（判断 5 の window-boundary 判断 5「この一覧は記録しない」）。

- macOS（`handmark_reveal_macos.rs`）: メインスレッドで、`NSWorkspace.runningApplications` のうち窓を持てるアプリ（`activationPolicy != Prohibited`・判断 6 で広げた）で、隠れておらず、自分でないものの pid を覚える。自分を前面に出してから `NSApplication.hideOtherApplications` を呼ぶ（試作 run9・run10 で、前面のアプリは外から `hide()` しても隠れずに残った）。戻すときは覚えた pid のアプリだけ `unhide()`（終了していれば飛ばす）。
- Windows（`handmark_reveal_windows.rs`）: `EnumWindows`（上から下の重なり順）で、見えていて最小化されておらず、DWM で隠されておらず、持ち主の窓が無く、ツール窓でなく、自分のプロセスでなく、シェルの窓（`Progman`・`WorkerW`・`Shell_TrayWnd`・`Shell_SecondaryTrayWnd`）でないトップレベルの窓を覚え、`ShowWindowAsync(SW_SHOWMINNOACTIVE)` で最小化する（応答しないアプリで止まらないよう非同期）。戻すときは下から上の順に、まだ在り、覚えたときと同じプロセスの窓で、最小化されたままの窓だけ `ShowWindowAsync(SW_RESTORE)`（判断 6）。窓の題名は読まない（内容の語が入りうる）。
- 候補の判定は OS に依らない純関数（`handmark_reveal.rs`・cfg なし）に置き、両 OS の CI で走るテストで縛る（Windows の窓の属性の組み合わせ・戻す順・戻す前の在否）。
- 呼ぶのは `run_on_main_thread` の中から。失敗は tracing に固定の文だけ（数も pid も出さない）。

### 5. トレイ

- `tray.rs` に 2 つ目の手跡の項目（`MENU_HANDMARK_REVEAL`）。今の「やめる」と同じ作り（Atomic に駆動役の望む項目、更新スレッドが 1 秒ごとに出し入れ・文言の変更、押下は出ていた文言を駆動役に渡す）。位置は「やめる」のすぐ上。
- `handmark_tray_labels_are_plain` に 2 つの文言を足す。
- 押したことは applog にも出さない（今の手跡の項目と同じ）。

### 6. ADR と同意文書

- ADR-051 に補訂（どけた回数は日の行の累計・押した時刻は残さない・Windows は見えていた窓の最小化と復元・自動で戻す契機）。本文は書き換えない。
- 同意文書の条件 4 の行に「満たした（本タスク・版は 3 名の版のタグで決まる）」を書き足す。文面は変えない。

## 変更対象

### 修正するファイル
- `src-tauri/src/analysis/handmark/day.rs` — `reveal_count`・`add_reveal`・`subtract_count`・`subtract` の引数
- `src-tauri/src/handmark_store.rs` — `add_reveal`・`row`・`snap_of`・`scrub_record`・`unavailable_row`
- `src-tauri/src/handmark_driver.rs` — `revealed`・`RevealItem`・`Effect::Reveal`・`Effect::RevealItem`・`toggle_reveal`・自動で戻す
- `src-tauri/src/logger.rs` — `HandmarkDayRow.reveal_count` と書き出し
- `src-tauri/src/redaction.rs` — `reveals` の写しと差・行の書き換え
- `src-tauri/src/schema_dto.rs`・`src-tauri/schema/current.json` — `reveal_count`
- `src-tauri/src/handmark_guard.rs` — 設計の項目一覧に `reveal_count`
- `src-tauri/src/tray.rs` — 2 つ目の手跡の項目
- `src-tauri/src/lib.rs` — 出来事の実行・トレイ押下・`mod` の宣言
- `docs/adr/ADR-051-handmark-in-stage1-late-period.md` — 補訂
- `.steering/20261114-gse-stage1-n3-consent/consent-draft-s1.md` — 条件 4 の行への書き足し（文面は変えない）
- `docs/functional-design.md`・`docs/glossary.md` — 必要なら

### 新規作成するファイル
- `src-tauri/src/handmark_reveal.rs` — 候補の判定と戻す順の純関数（cfg なし）
- `src-tauri/src/handmark_reveal_macos.rs` — macOS のどける・戻す
- `src-tauri/src/handmark_reveal_windows.rs` — Windows のどける・戻す

## 影響範囲

- `handmark_day` の行に項目が 1 つ増える。読む側は机上の道具（`desk.rs`・知らない項目を読み飛ばす）・gse-replay・実験の script（件数だけ）。どれも壊れない見込みを、テストと grep で確かめる。
- gse-dataset の schema の写し（parity の検査）を更新する PR が要る（Q3 の 7 択のときの gse-dataset PR #10 と同じ）。
- 本人の段 1 の配布フォルダ（v0.1.42）には入らない。

## 既存パターンとの整合性

- 純粋な駆動役が出来事を返し、`lib.rs` が実行する（`handmark_driver` と `run_handmark_effects`）。
- トレイの項目の出し入れは Atomic と更新スレッド、押下は出ていた文言で照合（`MENU_HANDMARK`）。
- 量の削除は前後の行の差、式は 1 つ（`subtract_totals`）。
- OS 非依存の純関数＋OS ごとのファイル（`handmark_desktop.rs` と `handmark_desktop_windows.rs`）。

## テスト戦略

- 単体テスト（`cargo test`・両 OS の CI で走る）:
  - 駆動役: 窓を出していないと項目は `Hidden`・押しても何もしない／どけると回数が 1 増え `Reveal(true)`・行は出ない／戻すと数えない／古い文言の押下は捨てる／一時停止中は数えない／「やめる」・日の変わり目・門が閉じる・終了で `Reveal(false)` が先に出る／`destination` で `Reveal` が記録に向かわない
  - 日の累計: 古い状態ファイルを 0 と読む・日の変わり目で 0・JSON の形の固定
  - 行: 書き出しの byte-equal の固定・記録が無い日は null
  - 区間の削除: 区間の中のどけた回数が後の行と走行中の累計から引かれる・古い行（`reveal_count` 無し）を書き換えない・3 つの量の差
  - OS 非依存の候補の判定と戻す順
  - トレイの文言の非開示語
  - `handmark_guard` の設計の項目一覧（駆動役の出口で記録に向かうのが `Row` だけのまま）
- 変異: 数える／数えないの分岐・削除の差に回数を入れる箇所・自動で戻す 3 か所を外して赤を見る。
- `cargo run --bin emit_schema` で schema を作り直し、`/finish-task` の parity check で gse-dataset と照合する。
- 実機（このタスクの外・引き継ぎに書く）: Mac は 12-09 以降（全画面の中・前面のアプリ・押した時に見えていたアプリだけ戻るか・帯と背景が隠れないか）、Windows は G-GEAR（最小化と復元・最大化の窓・管理者の窓が残ること）。

## ロールバック計画

注意（本人の段 1）: 状態ファイル `~/.gse/handmark_day_state.json` は版をまたいで 1 つで、`DayRecord` は `deny_unknown_fields`。この版を段 1 のモードでこの Mac で動かすと `reveal_count` を書き、本人の gse-next（v0.1.42）がそれを壊れた状態ファイルとして扱う。12-08 までは、この版を段 1 のモードで動かさない（判断 5 の理由がもう 1 つ増える）。

コミットを revert すれば戻る。状態ファイルの新しい項目は `#[serde(default)]` なので、古い版で読むと `deny_unknown_fields` で壊れた扱いになる点に注意する（古い版へ戻すときは、その日の状態ファイルが 0 から始まる。`visible_ms` を足したときと同じ）。
