# 設計: 手跡の下の縁の帯とどける操作（試作の枝）

前提は設計のタスクの design.md（論点 1〜7）と decisions.md（判断 1〜7）。ここではその実装の形だけを書く。

## アプローチ

進め方は 3 段。段 1 の結果で段 2・3 の前提が変わりうるので、段 1 を先に確かめる。

- **段 1（最小の帯と確かめ 1〜3）**: 中身が線 1 本だけの帯の窓を作り、全画面の上に出るか（テキストエディット・ブラウザ・エディタ）と、トレイから前面に出られるか（全画面の外と中）を確かめる。どける操作は「前面に出られたか」を読んで記録するところまで（隠さない）。
- **段 2（帯の中身と風）**: 風を Rust に移して両方の窓へ配り、帯に線・霧・粒・カーソルで薄くする・描く回数・覆われたら止めるを入れる。負荷を測る（確かめ 4）。
- **段 3（どける操作）**: 隠す・戻す・終了時に戻す・やめたことを知らせる。段 1 の結果で、やめる判定（判断 6 のままか事後確認か）を決めてから書く。

いずれも試作の範囲で、背景の層と同じく開発用のビルドで `GSE_HANDMARK_STAGE_SPIKE=1` のときだけ動く。

### 帯の窓（段 1）

- ラベル `handmark-edge-strip`。`handmark_stage_spike::setup` の中で背景の窓の後に作る（同じ環境変数）。
- 主画面の下の縁に、幅は画面の全体・高さ 14 点。透明・枠なし・影なし・`focused(false)`・`skip_taskbar`。
- `overlay_panel.rs` と同じく `tauri_nspanel` の `to_panel()` で非アクティブの NSPanel にする（`set_style_mask(1<<7)`）。層は Floating（4）。overlay と同じく上げない（tauri-nspanel #104 の IME の件）。collection behavior は `CanJoinAllSpaces | Stationary | IgnoresCycle | FullScreenAuxiliary`。`setIgnoresMouseEvents(true)`。`orderFrontRegardless` で出し、key にしない。
- NSPanel の窓は壊すとプロセスが落ちる（`handmark_spike.rs`・`lib.rs` の `on_window_event`）。`on_window_event` に新しいラベルの分岐（`prevent_close` して隠す）を足す。
- 確かめ用に、帯の `occlusionState`・`isOnActiveSpace`・`isVisible`・層を 1 秒ごとに `tracing` へ出す（開発用のビルドだけ。アプリの名前は書かない）。
- capabilities は `handmark-stage.json` の `windows` に新しいラベルを足す（`core:default` だけ。listen に要る）。
- `src/main.tsx` にラベルの分岐を足し、`HandmarkEdgeStrip.tsx` を描く。段 1 の中身は、ゆっくり揺れる線 1 本。

### 前面に出られるかの読み（段 1・確かめ 3）

- トレイに「背景を見る」を足す。段 1 では、選ぶと `NSApplication.activate`（自分を前面に出す）を呼び、最大 1 秒の間 50ms ごとに `NSRunningApplication.currentApplication().isActive()` を読む（メインスレッドを止めない。別スレッドで待ち、読みは `run_on_main_thread`）。結果（出られたか・待った時間）を `tracing` に出すだけで、何も隠さない。

### 風（段 2・判断 1）

- 新しいファイル `handmark_wind.rs`（OS 非依存の純粋な計算）: 打鍵の時刻を固定長の輪（例 256 個）に入れ、250ms ごとに `speed` と `irreg` の目標を出す。式と定数は `HandmarkStage.tsx` の `tick()`・`irregularity()` をそのまま移す（`WINDOW_MS`・`TICK_MS`・`SPEED_PER_KEY`・`MAX_KEYS_PER_SEC`・`WIND_DECAY`・`MIN_SPEED`・`IRREG_*`）。
- `handmark_stage_spike` に 250ms のスレッドを置き、`notify_key()` は時刻を輪に入れる。目標の値を専用のイベント名 `handmark-wind` で背景と帯の 2 つのラベルへ `emit_to` する（全窓の `emit` は使わない）。
- 窓の側は受け取った目標へ 250ms かけて寄せる（今の補間のまま）。`HandmarkStage.tsx` から `presses`・`tick` の風の部分を外す。打鍵のイベント（`handmark-stage-key`）は描画を起こす合図として残し、帯にも送る。

### 帯の中身（段 2・論点 2・3・5）

- 風で揺れる線 1 本（主）・その下に薄い霧 1 本・粒を少し（10 前後）。濃さ 70%・太さ 14 点は仮。
- 描く回数: 最後の入力から 4 秒（`ACTIVE_HOLD_MS`）の間は 33ms ごと、それ以外は 100ms ごと。
- 覆われたら止める: まず WebKit が覆われた窓の描画を自分で止めるか（`document.visibilityState`・描いた回数）を測る。止めないなら、Rust が 250ms ごとに `occlusionState` を読み、変わったときだけ帯へ知らせる。
- カーソルで薄くする: カーソルの値を帯へ渡すのは ADR-040 D1 の背景の層の範囲の広げ方になる。帯へは座標を送らず、Rust の側（`handmark_stage_pointer.rs`）で「帯に近いか」を 0〜1 の数 1 つにして、帯専用のイベント名で帯だけへ `emit_to` する。検査（`handmark_stage_guard.rs`）の `WINDOW` に `HandmarkEdgeStrip.tsx` を足し、保存・返送・列の検査を帯にも当てる。`handmark-stage-pointer` の名前は帯で使わない（検査 :473 のまま）。

### どける操作（段 3・論点 6）

- 新しいファイル `handmark_reveal.rs`（macOS）と、順番を決める純粋な関数（OS 非依存・テストする）。
- 隠す: 見えている regular のアプリ（自分を除く・pid だけ）と層 0 の窓の前後の順番（`CGWindowListCopyWindowInfo` の pid と窓の番号だけ。名前は読まない）と前面のアプリを覚える → 前面に出て待つ（段 1 の読み）→ 出られなければやめる（または段 1 の結果しだいで事後確認）→ `hide()` し、`isHidden` を読み直す。
- 戻す: 覚えたアプリだけ `unhide()`。前面が自分のままなら、奥から順に前へ出し最後に元の前面のアプリ。前面が他のアプリに替わっていたら前へ出し直さない。覚えた一覧を捨てる。
- トレイの項目の文字は「背景を見る」と「戻す」を実際の状態で切り替える（トレイの 1 秒のスレッドで、覚えたアプリが全部見えていれば「背景を見る」に戻し一覧を捨てる）。チェック印は付けない。
- やめたとき: 項目の文字を数秒だけ「背景を見る（前に出られませんでした）」にする（文言は試して決める）。
- 終了時: `shutdown()` の先頭で、覚えた一覧があれば `unhide()` する。落ちたときは戻せない旨を steering に書く。
- 覚えた一覧・アプリの名前・回数は、ログにもファイルにも書かない。

## 変更対象ファイル

- `src-tauri/src/handmark_stage_spike.rs` — 帯の窓の作成・NSPanel 化・確かめ用の読み・風のスレッドと配布・`notify_key` の変更
- `src-tauri/src/handmark_wind.rs`（新）— 風の純粋な計算とテスト
- `src-tauri/src/handmark_reveal.rs`（新）— どける操作（macOS）と順番の純粋な関数・テスト
- `src-tauri/src/handmark_stage_pointer.rs` — 帯に近いかの数 1 つを帯へ送る
- `src-tauri/src/handmark_stage_guard.rs` — `WINDOW` に帯を足す・新しいイベント名の検査
- `src-tauri/src/tray.rs` — 「背景を見る / 戻す」の項目
- `src-tauri/src/lib.rs` — `mod` の宣言・`on_window_event` の分岐・`shutdown()` で戻す
- `src-tauri/capabilities/handmark-stage.json` — ラベルを足す
- `src/main.tsx`・`src/components/HandmarkEdgeStrip.tsx`（新）・`src/components/HandmarkStage.tsx`（風を受け取る形に）

## 既存パターンとの整合

- NSPanel 化は `overlay_panel.rs`（tauri-nspanel・Floating 固定・非アクティブ）。窓の層と振る舞いの直接の設定は `handmark_stage_spike.rs::prepare`（objc2-app-kit）。
- 窓へは専用のイベント名で `emit_to`（ADR-040 D3 の表の行）。
- 試作の項目はトレイで `is_shown` のときだけ差し込む（`tray.rs` の既存の試作の項目）。

## テスト戦略

- `cargo test --manifest-path src-tauri/Cargo.toml --workspace`: 風の計算（TS の式と同じ値になるか・輪の上限・打鍵なしで 0 へ）、どける順番（自分を除く・前から隠していたアプリを戻さない・奥から順で最後に前面）、ADR-040 の検査（帯を足した `WINDOW` で緑・陽性対照で赤）。
- `npx tsc --noEmit`・`cargo clippy`。
- HMM と記録は変えないので、`gse-replay --snapshot` は回帰の確認として 1 回だけ回す。
- 手動（実機・研究者の目視を言葉で聞く）: 確かめ 1〜4、帯の見え方、どける・戻す。

### 実機の確かめの起動の形（要確認）

開発版は識別子 `com.johnd.gse-next` と単一起動のプラグイン（`/tmp/<識別子>_si.sock`）を O1 と共有するので、そのまま起動すると O1 とぶつかる（前のタスクの判断 8）。O1 を止めずに確かめるため、開発版の識別子だけを起動のときに変える（`npx tauri dev --config` で `identifier` を `com.johnd.gse-next-spike` に）。記録は一時フォルダ（`GSE_DATASET`）に書かせ、終わったら消す。止めるのは自分が起動したプロセス番号だけ。
