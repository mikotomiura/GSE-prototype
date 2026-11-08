# 設計（1b・macOS の窓・トレイ・配線）

1a（main 4fad97bf）の上に足す。判断 7 の 4 問を実装の形にしたもの。ここに無い分岐を見つけたら、決めずに `blockers.md` に書いて止める。

## 1. 駆動役 `handmark_driver.rs`（OS 非依存・`s1_driver.rs` の作法）

- 中身: `Evaluation`（1a）・`Stage`（1a）・溜めた打鍵の列・前回の検め直しの時刻と日・前回の行の時刻・前回の刻みの時刻・窓が出ているか。
- 入口（どれも `Vec<Effect>` を返す。IO は `HandmarkFs` 越し）:
  - `new(fs, s1_mode, now, today)`: 起動。門を評価し、行を出し、開いていれば窓を開く。
  - `on_press(t)`: 打鍵の時刻を溜めるだけ（`is_press && !recording::is_paused()` のときに lib.rs が呼ぶ）。
  - `tick(fs, now, today)`: 250 ms ごとに lib.rs が呼ぶ。
    1. 時計の飛び（判断 7-2）: `now < 前回` か `now − 前回 > 1 日` なら、`Stage::new(種, now)` で取り直し、`note_stage_start(now)`。溜めた打鍵は捨てる。
    2. 日付の変わり目: 前の日の最後の行 → 門を検め直す → 新しい日の最初の行。
    3. 前回の検め直しから 60 秒なら検め直す。閉じれば `CloseWindow`、開けば `OpenWindow`（開くたびに新しい `Stage` と `note_stage_start`）。
    4. 開いていれば: 目標 `target = now − 500`。溜めた打鍵のうち `t ≤ target` を時刻の順に `press` し、`advance_to(target)`。`StageState` を `State` として出す（窓へ配る）。`add_shown(now − 前回の刻み)`。
    5. 前回の行から 5 分なら `save` と行。`save` の失敗は `note_save_failed`（閉じれば `CloseWindow`）。
  - `turn_off(fs, now)` / `turn_on(fs, now)`: 1a の関数を呼び、門の結果に合わせて `CloseWindow` / `OpenWindow` と行。
  - `on_redact(fs, from, to)`: `scrub_state` を呼ぶ（区間の削除の経路から）。
  - `on_quit(fs, now)`: `save` と最後の行。
- `Effect`: `OpenWindow { layout_seed }`・`CloseWindow`・`State(StageState)`・`Row(HandmarkDayRow)`・`TrayItem(TrayItem)`（`Hidden`・`Stop`〔「背景を今日は止める」〕・`Restore`〔「背景を戻す」〕）。
- トレイの項目を出すのは、今日の割付が `LateFirst` か `On` のときだけ（出す日でない日に止める・戻すは意味を持たない）。門が `off_today` で閉じているときは `Restore`、開いているときは `Stop`、それ以外は `Hidden`。
- 再生との一致: `replay` に、記録の打鍵の時刻と同じ遅れの規則（`target = now − 500` まで）を当てる関数を `analysis::handmark::state` に足し、ライブの `tick` の列と再生が `to_bits` で一致することを、500 ms 以内の遅れの打鍵を含む 200 通りでテストする。

## 2. lib.rs の配線（`S1_DRIVER` の作法に合わせる）

- `static HANDMARK_DRIVER: Mutex<Option<HandmarkDriver>>`。段 1 のモードのときだけ作る（1a の `DiskFs::from_env(exe)`・`GSE_DEBUG=1` のときだけ環境変数の表）。
- 押下: 既存の受信ループで、`event.is_press && !crate::recording::is_paused()` のときに `on_press(event.timestamp)`。ロックは短く（フックのコールバックの中ではない受信側のスレッドであることを確かめる。`hook-constraints`）。
- 刻み: 250 ms の専用のスレッド（試作の `start_wind` の作法）。
- 区間の削除: `delete_time_range` の中で `on_redact`。
- 終了: 既存の終了の経路（`request_quit` など）で `on_quit`。
- `Effect::Row` は `LogEntry::HandmarkDay` にして既存の `log_tx` へ。`OpenWindow` / `CloseWindow` / `State` は窓の層へ。`TrayItem` はトレイへ。

## 3. 窓（`handmark_stage.rs`・macOS だけ）と描画（`src/components/HandmarkStage.tsx`）

- 試作 `handmark_stage_spike.rs`（窓の作り・NSWindow の階層・クリックを通す）と `capabilities/handmark-stage.json` を写す。環境変数の門（`GSE_HANDMARK_STAGE_SPIKE`）は外し、駆動役の `OpenWindow` / `CloseWindow` だけで開け閉めする。閉じる要求は止めて隠す（試作の判断どおり）。
- TSX は試作の描画を写し、次を変える:
  - 風・位相・漂いは、Rust から 250 ms ごとに届く `StageState` を使う。`performance.now()` から位相や漂いを積まない。描画の間は前の状態から次の状態へ線形に寄せるだけ（描画の回数は状態に影響させない）。
  - 草と粒の配置の種は、固定の 11 ではなく `layout_seed`。
  - ポインタ・クリック・ホイールの処理は全部外す（PR 3・5）。
  - 描画の回数: 試作どおり（入力があれば毎フレーム・無ければ絞る）。
- `src/main.tsx` の窓の振り分けは試作に合わせる。`typescript-standards`（`any` 禁止）。

## 4. トレイ（`tray.rs`）

- main の `tray.rs` の作り（招待の項目の差し込み `menu.insert(item, 2)`・`request_quit`）に合わせ、項目を 1 つ差し込む。文言は「背景を今日は止める」／「背景を戻す」で、`TrayItem` で出し分け、`Hidden` では出さない。
- 既存のテスト `tray_labels_never_leak_cognitive_state` の対象にこの 2 つの文言を足す。

## 5. 検査

- 記録の検査の差し替え: 1 日分の打鍵を駆動役に流し（`new` → `tick` の列 → `turn_off` → `turn_on` → `on_quit`）、出た `Effect` のうち記録に向かうものが `Row`（= `handmark_day`）だけであることを見る（1a の自作の行の比べを置き換える）。
- `capabilities.rs` の `s1_line_types_are_declared_only_in_s1` の送出元の一覧に `handmark_day` を足す。
- 門のテスト: 開いた後に表を消す → 60 秒後の `tick` で `CloseWindow` が出る。`turn_off` で `CloseWindow`・翌日の `tick` で `OpenWindow`（割付が出す日なら）。
- 時計の飛び・遅れて届く打鍵・`save` の失敗のテスト。

## 6. 画面の確かめ（判断 7-1・研究者と一緒に・PR の完了の条件）

- 研究者が gse-next を止められる時間に、`HOME` を一時ディレクトリに替え、`GSE_DEBUG=1 GSE_S1_MODE=1 GSE_HANDMARK_TABLE=<作った表>` で開発版を起動する。表は `gse-handmark-table` で今日が後期の初日になるように作る。
- 見ること: 窓が出る・打鍵で動く・止めると消える・戻すと出る・表を消すと 60 秒以内に消える・トレイの文言。`HOME` の下の NDJSON の `handmark_day` を読み、行の中身を確かめる。
