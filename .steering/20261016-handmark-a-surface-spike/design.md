# 設計

## アプローチ

既存アプリの中に、macOS だけで動く別窓 `handmark` を足す。環境変数 `GSE_HANDMARK_SPIKE=1` を立てて起動したときだけ、`setup()` の中（メインスレッド）で窓を作る。窓は透明で枠がなく、画面の右下の端に 48×48 px で置く。既存の overlay と同じ手順で非アクティブの NSPanel にし（`overlay_panel::convert_overlay_to_panel` をそのまま呼ぶ）、マウスのイベントは常に無視させる。

打鍵は、分析スレッドが `rx.recv_timeout` で受けた直後（`lib.rs:4224` の `Ok(event)` 分岐）で拾う。`event.is_press` のときだけ、打鍵の時刻（`event.timestamp`・フックが取った壁時計のミリ秒）と通し番号を `emit_to("handmark", …)` で窓へ送る。キーの種類も内容も送らない。キーリピートはフックの側で既に除いている（`hook_macos.rs:525`・`:622`）。フックのコールバックには手を入れない。

窓の側は、受けたら印の光る動き（約 120 ms）を最初からやり直す。計測を有効にしたとき（`GSE_HANDMARK_SPIKE_MEASURE=1`）だけ、描画の後の 2 つ目の `requestAnimationFrame` で `Date.now() − 打鍵の時刻` を求め、通し番号と遅れの 2 つだけを Rust へ返す。Rust はそれを一時ディレクトリの CSV（`$TMPDIR/gse-handmark-spike/latency-<起動時刻>.csv`）に書く。NDJSON にも applog にも書かない。

### 取り込みからの除外と fail-closed（判断 6）

1. 窓を `visible(false)` で作る。
2. NSPanel 化する。
3. `set_content_protected(true)` を呼ぶ。
4. NSWindow の `sharingType` を objc2-app-kit で読み返し、`None` であることを確かめる。

1〜4 のどれかが失敗したら、窓を閉じて出さない（tracing に warn を 1 行）。どれも通ったときだけ `show()` する。設定は効いたのに実際には写る、という場合は読み返しでは分からないので、研究者の目視で確かめる（判断 5）。人為的な失敗は `GSE_HANDMARK_SPIKE_FORCE_PROTECT_FAIL=1` で手順 3 を失敗扱いにして起こす。この失敗は模擬なので、結果にはそう書く。

### 規則（親タスク判断 16）をどこで守るか

| 規則 | どこで守るか |
|---|---|
| 推定を使わない | 新しいモジュールは `engine`・`invitation`・`FeatSnapshot`・`p_stuck` を use しない。分析スレッドで呼ぶのは「時刻と番号を送る」1 行だけで、推定の結果より前、`LoopInput::Key` を作る位置で呼ぶ |
| 本人の操作を記録しない | 窓はマウスを受けず、invoke も計測の返却だけ。計測の CSV は環境変数で有効にしたときだけ書き、研究者の試視では有効にしない（判断 4） |
| 持ち越さない | 状態は窓の中の 1 つの動きだけ。ファイルにもストアにも残さない。例外は計測を有効にしたときの CSV だけで（判断 3・4）、合成の打鍵の計測でだけ使い、試視では有効にしない |
| 一時停止を尊重する | 記録の一時停止中は小面に知らせず、CSV にも書かない（判断 8） |
| すぐ閉じられる | トレイのメニューに「小面を閉じる」を足す（`handmark` の窓があるときだけ）。窓の CloseRequested は全体の終了から外す（`lib.rs:5805`） |
| 数値・良し悪しを載せない | 窓に描くのは色の印 1 つだけ。文字を描かない |

## 変更対象ファイル

- `src-tauri/src/handmark_spike.rs`（新規・`#[cfg(target_os = "macos")]`）: 環境変数の読み取り、窓の生成と NSPanel 化、除外の設定と読み返し、打鍵の通知、計測の CSV、トレイから閉じる処理
- `src-tauri/src/lib.rs`: mod の宣言、`setup()` で窓を作る 1 か所、分析スレッドで通知する 1 か所、`on_window_event` で `handmark` を除く 1 か所、invoke のコマンド 1 つの登録（いずれも cfg macos）
- `src-tauri/src/tray.rs`: 「小面を閉じる」の項目（cfg macos・窓があるときだけ）
- `src-tauri/capabilities/handmark.json`（新規）: `windows: ["handmark"]`、`core:default` だけ
- `src/main.tsx`: label `handmark` の分岐（背景を透明にし、専用の部品だけを描く）
- `src/components/HandmarkSurface.tsx`（新規）: 印・光る動き・計測の返却
- 合成の打鍵を流すスクリプト（`.steering/20261016-handmark-a-surface-spike/` に置く。osascript で 1 文字ずつ間を空けて約 200 回）

触らない: `analysis/` 全体（`portrait/` を含む）・`eh3.rs`・`wallpaper*.rs`・`hook_*.rs`・`logger.rs`・`schema_dto.rs`。

## 既存パターンとの整合

- 窓の生成は overlay（`lib.rs:5712-5740`）と EH3 の説明の窓（`lib.rs:5749-5775`）に倣う。既存は除外の設定に失敗しても warn だけで続けるが、小面は判断 6 によって窓を出さない側に倒す。
- NSPanel 化は `overlay_panel.rs:38` を流用する。クリックの透過は `set_ignore_mouse_events(true)` を Rust の側で 1 回だけ設定する。
- 窓の出し分けは既存の label の方式（`src/main.tsx:11`）。
- 環境変数のゲートは `GSE_DEBUG` と同じく「"1" のときだけ真」。

## 測る条件と限界

- 分析スレッドは、セッションが動いていないと打鍵を門で捨てる（`lib.rs:4199`）。そのため小面が光るのはセッション中だけで、計測もセッションを開始してから行う。本体に入れるときもセッション中だけ動く前提なら、実際と同じ条件になる。
- 遅れの区間は「フックが打鍵の時刻を取る → channel → 分析スレッド → emit → WebView → 描画の後の 2 つ目のフレーム」。画面に光が出るまで（合成とディスプレイ）は含まないので、研究者のスローモーション撮影で抜き取る（判断 3）。
- 合成の打鍵は、実際のキーボードの入力から CGEventTap までの区間を含まない。
- 時刻の基準はどちらも壁時計のミリ秒（Rust の `SystemTime`、JS の `Date.now()`）。同じ機械の同じ時計なので比べられるが、計測中に時計が補正されると外れ値になる。外れ値は除かずにそのまま書く。

## テスト戦略

- `cargo test --manifest-path src-tauri/Cargo.toml --workspace`: 既存のテストが緑のままか。新しいテストは純粋な関数だけに付ける（環境変数の解釈、CSV の 1 行の書式）。
- `cargo clippy` と `npx tsc --noEmit`。
- `scripts/check_invitation_surface.py`: 画面の取り込みを検出する API の名前を書いていないか。
- `gse-replay --snapshot`: 分析の挙動は変えないので任意。通知の 1 行が `LoopInput` を変えないことを確かめるために 1 回だけ回す。
- 実機（Mac）:
  - 遅れ: 合成の打鍵 約 200 回 → CSV から 95 パーセンタイルと最大を出す。
  - 前面・クリックの透過・フォーカス: AX と手で確かめる（小面の上をクリックすると奥の窓に届く、打鍵中にフォーカスが移らない、全画面のアプリの上にも出る）。
  - fail-closed: 模擬の失敗で窓が出ないこと（AX で窓の有無を見る）。
  - 取り込み・抜き取り撮影・試視: 研究者の手順書を渡す。
- Windows: 環境変数を立てなければ何も変わらないこと。cfg で閉じるので、CI の Windows のビルドで確かめる（push の後）。
