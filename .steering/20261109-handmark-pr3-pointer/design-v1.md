# 設計（第 1 案）—— 草と粒の 1 つずつの跡を Rust が持つ

前提は requirement.md と decisions.md の判断 1〜4。一次は ADR-051 D2・D3・D5・D7、ADR-050 D2〜D6・補訂 1。

## 実装アプローチ

### 1. 何が状態になるか

試作の窓は、草 1 本ごとの押し `push`（270 本）と粒 1 つごとのずれ `ox, oy`（140 個）を、描画のたびに実際の経過時間で積んでいた（試作 `HandmarkStage.tsx` の `updatePointer` と草・粒の描画の中）。押しは「カーソルの近くにあった草」にだけ足されて数秒で戻るので、カーソルが通った後に草の倒れが尾を引く。これが見本 Version 5 の見た目である。

第 1 案は、この 1 つずつの値をそのまま Rust の状態にする（判断 1 の「戻る値は Rust」の素直な写し）。

- 新しい積分器 `PointerStage`（`analysis/handmark/pointer.rs`・OS 非依存）を、打鍵の `Stage` と別に作る。
- 刻みは 16ms に固定する。絶対時刻の格子にそろえる（`Stage` の 250ms と同じ作法）。打鍵の 0.5 秒の遅れは入れない。
- 1 刻みの入力: その刻みの一点（正規化した位置・左の押下）か「読みなし」、カーソルとクリックの入れ切り、その時刻の打鍵の状態（粒の位置を出すため）。
- 持つ値: 平滑した速さ `(vx, vy)`、最後の一点、前の押下の値、草ごとの `push[270]`、粒ごとの `(ox, oy)[140]`。どれも 0 へ戻る値か最後の一点で、列ではない（ADR-050 D4 が許す形）。
- 式は試作の定数（`CURSOR_R`・`CURSOR_HALF_MS`・`CURSOR_PUSH`・`CURSOR_MAX`・`CURSOR_STILL`・`MOTE_R`・`MOTE_HALF_MS`・`MOTE_PULL`・`MOTE_MAX`）をそのまま使い、`dt = 16` の固定刻みに直す。半減は `0.5^(16/half)` の定数を掛ける。
- 波紋（クリック）は判断 1 のとおり窓の側の 6 枠に置く。Rust は「押した瞬間」と位置を 1 回だけ送る。年齢は窓の時計で決まり、描画の回数に依らない。

### 2. 配置を Rust に移す（草・粒の位置）

押しと寄りは「草・粒とカーソルの距離」で決まるので、Rust が草と粒の位置を知る必要がある。

- 配置の生成（いま `HandmarkStage.tsx` の `buildWorld`。Park–Miller の乱数で `layout_seed` から作る）を Rust の `analysis/handmark/world.rs` に移す。窓は、窓を開くとき・種が替わったときに、Rust から配置を 1 回受け取って描く（配置の真実源を 1 つにする）。
- 粒の今の位置は `drift`・`phase` と粒ごとの値の関数（1b の判断 9）。縦のゆらぎ `moteBob` は fbm のノイズを使うので、ノイズ（`hash2`・`noise2`・`fbm`）も Rust に写す。窓は今の式のまま描き、同じ値を出すことを node と Rust の両方で同じ表（固定の入力と期待値）に照らして縛る。
- 座標は **画面の実寸に依らない正準の座標**（横 16・縦 10 の比の箱、縦を 1 とする）で持つ。窓は正準の座標を画面に引き伸ばして描き、Rust はカーソルの一点を同じ写像で正準へ直す。
  - 理由: 実寸で持つと、再生には画面の大きさが要る。画面の大きさ（解像度）は ADR-014 D4 が O1 で入れないと決めた値なので、日ごとの行に残せない。
  - 代わりに、16:10 でない画面では距離が少し歪む（円が楕円になる）。

### 3. 打鍵の状態とのつなぎ

粒の位置は `phase`（打鍵の風の積分）に依る。打鍵の状態は「今 − 0.5 秒」までしか進まないので、時刻 `t` のポインタの刻みは、格子の時刻 `floor((t − 500) / 250) × 250` の打鍵の状態を使う。窓が描く粒も同じ遅れた `phase` なので、見た目とも合う。再生でも同じ規則で決まる。

### 4. 読みと駆動（ライブ）

- 読み: `input/handmark_pointer_macos.rs` が `NSEvent::mouseLocation`・`pressedMouseButtons` の最下位ビットを読む（試作の写し・権限なし・フックなし）。OS 非依存の型 `PointerSample`（`Debug`・`Display`・`Serialize` を持たない）は `input/handmark_pointer.rs`。
- 駆動: 今の駆動スレッド（250ms・`lib.rs` の `spawn_handmark_driver`）を 16ms で回す形に改める。
  - 打鍵の `Stage` の進め方と、日・門・行の処理は今の 250ms の格子のまま（`advance_to` は格子に合わせるので、呼ぶ回数で状態は変わらない・1a のテスト `the_number_of_advance_calls_does_not_change_the_state`）。
  - 16ms ごとに一点を読み、`PointerStage` を進める。
  - 一点の読みは `HANDMARK_DRIVER` のロックの外で行い、値は駆動役の関数へ引数で渡す。
- 一時停止（補訂 1 の項目 8）: `recording::is_paused()` が真の間は読まず、カーソルとクリックを切ったのと同じに扱う（跡を 0 にし、世代を進める）。
- 窓が閉じている間・門が閉じている間は読まない。

### 5. 窓への送り

- 打鍵の状態は今の `handmark-state`（250ms ごと）のまま。`StageState` は変えない（影響調べの推奨: 既存のビット一致の比較と呼び出し約 15 か所を保つ）。
- 跡は新しいイベント `handmark-trace`（手跡の窓だけ・`emit_to`）で送る。中身は `push[270]` と `(ox, oy)[140]` を f32 に丸めた数の配列と、世代。値が全部 0 になったら 1 回送って止める。
- 送る間隔は 33ms（入力のある間の描画の回数に合わせる）。送る間隔は状態に影響しない（状態は 16ms の刻みで決まり、送るのはその写し）。
- クリックは `handmark-ripple`（同じく手跡の窓だけ）で、押した瞬間の正準の位置を 1 回送る。
- 窓は受け取った跡を次の写しまで線形に寄せる（今の打鍵の状態の寄せ方と同じ）。遅れて届いた写しを捨てる規則は、試作の `receive`（世代・最小のずれ + 250ms）を写す。

### 6. 再生（判断 2）

- `analysis/handmark/pointer_replay.rs` に、`pointer_bin` の行の列から合成の一点の列を作る関数を置く。
  - 起点: 描画の種から決める（`SplitMix64` で正準の箱の中の点）。
  - 動き: 秒ごとに、その秒の `moved` のバケットの代表の距離（バケットの幅の幾何平均。マンハッタン和の point を、縦 900 point を 1 とみなして正準へ直す）を、種で決めた向きへ等速で 1 秒かけて動く。箱の縁で跳ね返す。
  - 押下: その秒の `buttons` 回を秒の中に等間隔に置く（左だけかは分からないので、全部を左とみなす・判断 2 の限界）。
  - `moved = 0` の秒（行が無い秒）は止まっている。
- 合成の一点の列を、ライブと同じ `PointerStage` に 16ms ごとに入れる。打鍵は既存の `replay_live` と同じ。
- 公開の口: `replay_with_pointer(presses, bins, seed, t0, t) -> (StageState, TraceState)`。PR 4 はこれを呼ぶ。

### 7. 入力ごとの入れ切り（判断 3）

- トレイ: 窓が出ている日だけ、「やめる」の上に「カーソル」「クリック」のチェックの項目を足す（手跡の語を出さない・PR 1 判断 7-4。文言は「カーソル」「クリック」・チェックの印つき（判断 5））。
- 状態: その日のうちは保つ（状態ファイル `handmark_day_state.json` に `cursor_off`・`click_off` を足す）。翌日は入った状態に戻る（全体の「やめる」と同じ・ADR-051 D2）。書けなかったときは切った側に倒す。
- 記録: `handmark_day` に `input_toggles: [{t, input: "cursor" | "click", on}]` を足す。上限は 64（`MAX_PER_DAY`）、超えたら `overflow`。区間の削除は、`day.rs` の `retain`・`redaction.rs` の `scrub_handmark_day`・`handmark_store.rs` の状態ファイルの scrub の 3 か所を同じコミットで直す（影響調べの HIGH）。
- 全体を「やめる」と、入力ごとの状態に関わらず窓が閉じる。入力ごとの状態は保つ。

## 変更対象

### 新規作成するファイル
- `src-tauri/src/analysis/handmark/world.rs` — 配置の生成（正準の座標）・ノイズ・粒の今の位置
- `src-tauri/src/analysis/handmark/pointer.rs` — `PointerStage`（16ms の固定刻み・草の押し・粒のずれ）
- `src-tauri/src/analysis/handmark/pointer_replay.rs` — `pointer_bin` からの合成の入力と `replay_with_pointer`
- `src-tauri/src/input/handmark_pointer.rs` — `PointerSample`（OS 非依存・`Debug` などなし）・前の値との差
- `src-tauri/src/input/handmark_pointer_macos.rs` — 一点の読み（`cfg(target_os = "macos")`）
- `src/components/handmarkStageTrace.ts` — 波紋の枠・受け取りの判定（DOM なし・試作の写しからホイールを除く）
- `scripts/handmark-stage-trace.test.mjs` — 試作の 9 件の写し（ホイールの 1 件は PR 5 に回し、配置・ノイズの照合の件を足す）
- `src-tauri/tests/fixtures/handmark_world_parity.json`（仮）— Rust と TS の配置・ノイズの照合の表

### 修正するファイル
- `src-tauri/src/analysis/handmark/mod.rs` — 宣言
- `src-tauri/src/analysis/handmark/day.rs` — `input_toggles`・上限・区間の削除
- `src-tauri/src/handmark_store.rs` — 入力ごとの状態の保存・起動での復元・状態ファイルの scrub
- `src-tauri/src/handmark_driver.rs` — 16ms の刻み・`PointerStage`・新しい `Effect`（`Trace`・`Ripple`・`Layout`）と行き先・入力ごとの入れ切り
- `src-tauri/src/handmark_stage.rs` — `emit_trace`・`emit_ripple`・`emit_layout`
- `src-tauri/src/lib.rs` — 駆動スレッドの 16ms 化と読み・一時停止・トレイの押下の配線
- `src-tauri/src/tray.rs` — 入力ごとの項目（今の 1 項目の前提を 3 項目へ）
- `src-tauri/src/logger.rs` — `HandmarkDayRow` と手書きの行・固定のテスト
- `src-tauri/src/schema_dto.rs`・`src-tauri/schema/current.json` — `input_toggles`
- `src-tauri/src/redaction.rs` — `scrub_handmark_day` に `input_toggles`
- `src-tauri/src/handmark_guard.rs` — 下の「検査」
- `src-tauri/src/input/mod.rs` — 宣言
- `src/components/HandmarkStage.tsx` — 配置を受け取る・跡と波紋を描く
- `package.json`・`.github/workflows/ci.yml` — `node --test` の step を frontend-check に足す（node 22 は `.ts` の型を除いて読む・CI の node は 22）
- `docs/functional-design.md`・`docs/glossary.md`（要れば）

## 影響範囲

- `StageState`・`replay`・`replay_live` は変えない。既存のビット一致のテストはそのまま。
- `handmark_day` の欄が増える → `logger.rs` の固定のテスト、`handmark_guard.rs` の欄名の一覧、`emit_schema`、gse-dataset の同期の PR。gse-replay は `handmark_day` を読み飛ばすので影響しない。
- トレイは 1 項目の前提で作られている（`TrayItem`・コードの変換・`handmark_tray_plan`/`after`・テスト）。3 項目に広げる。
- 駆動スレッドを 16ms にすると `HANDMARK_DRIVER` のロックを取る回数が 15 倍になる。トレイ・区間の削除・終了と競合するので、ロックの中の仕事を短く保ち、ロック順の注記（`lib.rs` 2312 行付近）を守る。
- CPU: 16ms の読みと 410 個の値の更新・33ms の送り。窓の側の描画は今と同じ回数。負荷は合成の入力とポインタを切った条件で外から測る（ADR-050 D2・補訂 1 の項目 7）。人の手の入力で描画の回数を計測に書かない。

## 既存パターンとの整合性

- 純関数と駆動役の分け方は PR 1 の `Stage`・`HandmarkDriver`（`Effect` を返す・IO は外）に乗る。`Effect::destination` の網羅の match に新しい出来事を足し、`Row` 以外は記録へ向かわないことを型で決める。
- 読みの型と配送は試作の `handmark_pointer.rs`・`handmark_stage_pointer.rs` を写し、配線は main に合わせて書き直す（ADR-051 D7）。
- 検査は PR 1 の `handmark_guard.rs` の形（`include_str!`・実行時に連結した対照の文字列）に、試作の `handmark_stage_guard.rs` の d3 の各検査を足す。

## テスト戦略

- **決定性（Rust）**: 同じ入力（打鍵・一点の列・種）からビット単位で同じ跡が出る。刻みの呼び方（16ms ずつ・まとめて）で跡が変わらない。一点の列だけ変えると跡が変わる（陰性の対照）。
- **戻る値**: 入力が止まると跡が 0 へ戻る（草 700ms・粒 900ms の半減）。最後の入力から 8 秒で全部 0。
- **切り・一時停止**: カーソルを切ると草の押しと粒のずれと最後の一点が 0、クリックを切ると波紋の送りが止まる。一時停止の間は読みの関数が呼ばれない（呼ばれた回数を数える偽の読み）。入れ直したとき前の跡が出ない。
- **再生**: `pointer_bin` の列から作る合成の一点の列が種と行で決まる。`replay_with_pointer` が同じ入力で同じ結果。行の無い秒は止まる。
- **配置の照合**: Rust の `world` と TS の配置・ノイズが同じ表の値を出す（Rust の cargo test と node のテストの両方が同じ表を読む）。
- **記録（ADR-050 D2〜D4）**: 検査を足す
  - 型: `PointerSample` に `Debug`・`Display`・`Serialize` が無い（`const` の評価で縛る）
  - ソース: ポインタのファイルが `LogEntry`・`tracing::`・`log_tx`・`std::fs`・通信・`crate::analysis::engine` などを含まない。`logger.rs`・`schema_dto.rs`・`submission.rs`・`packaging.rs` がポインタの型の名前を含まない
  - 窓: `HandmarkStage.tsx`・`handmarkStageTrace.ts` が保存先・`invoke`・`fetch` を含まない。`handmark-trace`・`handmark-ripple` を他の窓のコードが `listen` しない
  - macOS の読みのファイルが `NSEvent` のポインタの 2 つ以外を読まない（キーボードの状態を読まない）
  - 列: Rust の側は固定の長さの配列だけ。窓の側は名前を許した枠だけ
  - 振る舞い: 1 日分の打鍵とポインタを駆動役に通して、出た `Effect` のうち記録へ向かうのが `handmark_day` だけ
  - どの検査にも陽性対照。実物を壊して赤を見る変異（読みの後に `tracing` を足す・`Debug` を付ける・切ったのに跡を消さない・一時停止を見ない）
- **入れ切りの記録**: `input_toggles` が行に入り、区間の削除で消える（3 か所）。状態ファイルから起動で戻る。書けないと切った側に倒れる。
- **画面**: PR 1 の判断 11 の段取り（研究者が gse-next を止める時間に・一時の HOME）。カーソルで近くの草が倒れて尾を引く・粒が寄ってほどける・左クリックで波紋・トレイの入れ切りが効く・一時停止で跡が消える。
- 回帰: HMM は変えないので gse-replay の snapshot は任意（回して一致を見る）。

## ロールバック計画

- 1 つの PR なので revert で戻る。入口の門は変えないので、O1 の配布と本人の前期には影響しない。
- schema が変わるので、revert するときは gse-dataset の同期も戻す。

## この案の弱いところ（/reimagine の比べの材料）

- 配置とノイズを Rust と TS の 2 か所に持つ（照合の表で縛るが、二重の実装である）。
- 窓へ送る量が多い（410 個 × 毎秒 30 回）。
- 正準の座標で、16:10 でない画面では距離が歪む。
