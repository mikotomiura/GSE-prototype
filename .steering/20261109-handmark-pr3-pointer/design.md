# 設計（第 2 案）—— 画面の粗い格子の上の「跡の場」を Rust が持ち、草と粒は場を読むだけ

前提は requirement.md と decisions.md の判断 1〜5。一次は ADR-051 D2・D3・D5・D7、ADR-050 D2〜D6・補訂 1。

## 実装アプローチ

### 1. 考え方: 状態は小さく、配置に依らず、打鍵に依らない

要件の芯は 2 つである。ライブと再生が同じ Rust の関数を通ること、その関数が描画の回数に依らないこと。PR 4 は、この関数の出力から見た目の特徴を作り、予測器を比べる。そうであれば、関数の出力は次の性質を持つほうがよい。

- **小さい**: PR 4 の特徴にそのまま使え、窓へ送る量も少ない。
- **配置に依らない**: 草や粒の並び（`layout_seed` で決まる）を Rust が知らなくてよい。窓の描き方を変えても関数は変わらない。
- **打鍵に依らない**: 打鍵の状態は 0.5 秒遅れて進む。ポインタの関数がそれを読まなければ、2 つの積分器は独立に進み、遅れの規則を跨がない。

そこで、跡を「画面の上の粗い格子の場」として持つ。

- 画面を、実寸に依らない **正準の箱**（縦 1・横 1.6）で表す。箱を **横 16 × 縦 10 の格子**（1 マスは縦の 0.1 角）に切る。
- 格子のマスごとに 3 つの戻っていく値を持つ。
  - `bend`: 草を横に倒す量（符号つき）
  - `pull_x`, `pull_y`: 粒を寄せる向きと量
- カーソルが動くと、カーソルの近くのマスに、動きの速さに比例した量を足す（距離で重みを付ける。試作の `CURSOR_R`・`MOTE_R` の半径に合わせる）。`bend` はカーソルの横の速さの向き、`pull` はマスの中心からカーソルへの向き。
- どのマスの値も、半減（`bend` は 700ms・`pull` は 900ms、試作の値）で 0 へ戻る。上限で切る。
- 窓は、草 1 本・粒 1 つの位置で場を双一次補間して読み、倒し・ずらしに使う。窓は跡の値を積まない（届いた場を次の写しまで寄せるだけ）。

これは ADR-050 D4 の「戻っていく値」の形である。場は位置の列ではなく、決まった数のマスの、0 へ戻る量である。カーソルが通った場所に跡が数秒残るのは試作の草の尾と同じで、それ以上は残らない。

### 2. 刻みと関数

- `analysis/handmark/trace.rs`（OS 非依存）に `TraceField` を置く。
  - 刻みは 16ms に固定し、絶対時刻の格子にそろえる。
  - 1 刻みの入力は、「一点（正準の位置・左の押下）か読みなし」と「カーソル・クリックの入れ切り」。打鍵は入れない。
  - 持つ値: `cells: [[f32; 3]; 160]`、平滑した速さ `(vx, vy)`、最後の一点、前の押下。
  - 出力: 場の写し `TraceState { epoch, cells }` と、その刻みで押下が始まったかとその位置（波紋の種）。
- 半減の係数は `0.5^(16/half)` の定数。足す量は試作の `CURSOR_PUSH`・`MOTE_PULL` の式を、`dt = 16` とマスの重みに直す（細かな値は画面で合わせ、合わせた値を定数として固定する）。
- 値は f32 で持ち、演算の順を固定する（同じ入力でビット単位で同じ）。
- 打鍵の `Stage`・`StageState`・`replay`・`replay_live` は変えない。

### 3. 読みと駆動（ライブ）

- 読み: `input/handmark_pointer.rs`（OS 非依存の型 `PointerSample`。`Debug`・`Display`・`Serialize` なし）と `input/handmark_pointer_macos.rs`（`NSEvent::mouseLocation`・`pressedMouseButtons` の最下位ビット）。試作の写し。
- **ポインタの専用スレッド**を立てる（`lib.rs`・macOS だけ）。16ms ごとに一点を読み、`TraceField` を進め、33ms ごとに窓へ場を送る。`TraceField` はこのスレッドだけが持つ。
  - 駆動役（250ms・`HANDMARK_DRIVER` のロック）とはロックを共有しない。駆動役からは、「窓が開いているか」「カーソル・クリックが入っているか」「世代」を Atomic で受ける。入れ切りや窓の開閉で世代を進めると、ポインタのスレッドは次の刻みで場を 0 にする。
  - これで、16ms の仕事がトレイ・区間の削除・終了のロックと競合しない。
- 一時停止（補訂 1 の項目 8）: 刻みごとに `recording::is_paused()` を見る。真の間は読まず、両方切ったのと同じに扱う（場を 0・世代を進める）。
- 窓が閉じている・両方切っている間は、読まず、送らず、16ms の待ちを 250ms に延ばす（負荷を抑える。延ばしても状態は 0 のままなので結果は変わらない）。
- 正準の箱への写し: スレッドは窓を開いたときに主画面の大きさを一度だけ読み、一点を `(x / W × 1.6, y / H)` に直す。大きさは写しに使うだけで、どこにも渡さない。

### 4. 窓への送り

- 打鍵の状態は今の `handmark-state` のまま。
- 場は新しいイベント `handmark-trace`（手跡の窓だけ・`emit_to`）で送る。中身は世代と、160 × 3 の値を i8 に量子化した配列（上限で割って −127〜127）。値が全部 0 の写しは 1 回送って止める。
- 波紋は `handmark-ripple` で、押下が始まった刻みの正準の位置を 1 回送る。窓は 6 枠に入れる（ADR-050 D4・判断 1）。
- 窓の受け取りは、試作の `receive`（古い世代を捨てる・最小のずれ + 250ms より遅い写しを捨てる・切った知らせは遅れても効く）を写す。

### 5. 再生（判断 2）

- `analysis/handmark/trace_replay.rs` に、`pointer_bin` の行の列から合成の一点の列を作る関数を置く。
  - 起点は描画の種から（`SplitMix64` で箱の中の点）。
  - 秒ごとに、`moved` のバケットの代表の距離（バケットの幅の幾何平均の point を、縦 900 point を 1 とみなして正準へ直す）を、種で決めた向きへ 1 秒かけて等速で動く。箱の縁で跳ね返す。
  - その秒の `buttons` 回の押下を秒の中に等間隔に置く（全部を左とみなす・判断 2 の限界）。
  - 行の無い秒は止まっている。
- 合成の一点を 16ms ごとに `TraceField` に入れる。打鍵の側は既存の `replay_live`。
- 公開の口: `replay_trace(bins, seed, t0, t) -> TraceState`（打鍵と独立なので、PR 4 は `replay_live` と並べて呼ぶ）。

### 6. 入力ごとの入れ切り（判断 3・5）

- トレイ: 窓が出ている日だけ、「やめる」の上に「カーソル」「クリック」のチェックの項目。
- 状態: その日のうちは保つ（`handmark_day_state.json` に `cursor_off`・`click_off`）。翌日は入った状態に戻る。書けなかったら切った側に倒す。
- 記録: `handmark_day` に `input_toggles: [{t, input: "cursor" | "click", on}]`。上限 64・超えたら `overflow`。区間の削除は `day.rs`・`redaction.rs` の `scrub_handmark_day`・`handmark_store.rs` の状態ファイルの scrub の 3 か所を同じコミットで直す。
- 駆動役は入れ切りの状態を Atomic でポインタのスレッドへ写す。全体の「やめる」で窓が閉じれば、ポインタのスレッドも止まる。

## 変更対象

### 新規作成するファイル
- `src-tauri/src/analysis/handmark/trace.rs` — `TraceField`（場・16ms の固定刻み）
- `src-tauri/src/analysis/handmark/trace_replay.rs` — `pointer_bin` からの合成の一点と `replay_trace`
- `src-tauri/src/input/handmark_pointer.rs` — `PointerSample` と前の値との差（OS 非依存）
- `src-tauri/src/input/handmark_pointer_macos.rs` — 一点の読み（macOS）
- `src-tauri/src/handmark_pointer_thread.rs` — ポインタのスレッドの純粋な部分（読む口と送る口を引数に取る・テストで偽を渡せる）。スレッドの起動だけ `lib.rs`
- `src/components/handmarkStageTrace.ts` — 波紋の枠・受け取りの判定・場の補間（DOM なし）
- `scripts/handmark-stage-trace.test.mjs` — 試作の 9 件の写し（ホイールの件と、実時間で減らす件は形が変わるので置き換える）＋場の補間の件

### 修正するファイル
- `src-tauri/src/analysis/handmark/mod.rs`・`src-tauri/src/input/mod.rs` — 宣言
- `src-tauri/src/analysis/handmark/day.rs` — `input_toggles`
- `src-tauri/src/handmark_store.rs` — 入力ごとの状態の保存・復元・scrub
- `src-tauri/src/handmark_driver.rs` — 入力ごとの入れ切り・Atomic への写し（`Effect` に `PointerGate { open, cursor, click, epoch }` を足し、行き先は `Window` 側）
- `src-tauri/src/handmark_stage.rs` — `emit_trace`・`emit_ripple`
- `src-tauri/src/lib.rs` — ポインタのスレッドの起動・トレイの押下
- `src-tauri/src/tray.rs` — 入力ごとの項目
- `src-tauri/src/logger.rs`・`src-tauri/src/schema_dto.rs`・`src-tauri/schema/current.json`・`src-tauri/src/redaction.rs` — `input_toggles`
- `src-tauri/src/handmark_guard.rs` — 検査を広げる
- `src/components/HandmarkStage.tsx` — 場を受けて草と粒に当てる・波紋
- `package.json`・`.github/workflows/ci.yml` — `node --test` の step
- `docs/functional-design.md`

## 既存パターンとの整合性

- 純関数（`TraceField`）と、IO を引数で受ける薄い駆動（ポインタのスレッドの純粋な部分）の分け方は、PR 1 の `Stage`・`HandmarkDriver` と同じ。
- 読みの型・世代・受け取りの判定は試作（`handmark_pointer.rs`・`handmark_stage_pointer.rs` の `Forwarder`・`handmarkStageTrace.ts`）を写す。試作の Forwarder も駆動役と別のスレッドだった。
- 検査は PR 1 の `handmark_guard.rs` の形に、試作の `handmark_stage_guard.rs` の d3 の各検査を足す。

## テスト戦略

- **決定性**: 同じ一点の列からビット単位で同じ場。刻みの進め方（1 刻みずつ・まとめて）で変わらない。一点を 1 つ変えると変わる（陰性の対照）。
- **戻る**: 動きが止まると場が半減で 0 へ戻り、8 秒で全部 0。
- **溜めない**: マスの数は定数で、値は上限で切れる。長く動かし続けても値が上限を超えない。
- **切り・一時停止**: 世代が進むと場が 0。一時停止の間は読みの口が呼ばれない（偽の読みで数える）。入れ直したとき前の跡が出ない。クリックを切ると波紋の種が出ない。
- **再生**: `pointer_bin` の列から作る一点の列が種と行で決まる。`replay_trace` が同じ入力で同じ結果。行の無い秒は止まる。合成の一点を `TraceField` に入れた結果と、ライブの経路（ポインタのスレッドの純粋な部分に偽の読みで同じ一点を渡す）の結果が一致する。
- **窓（node）**: 試作の枠と受け取りの件に、場の補間（マスの中心で値そのもの・境で連続）を足す。
- **記録（ADR-050 D2〜D4）**: 型（`const` の評価）・ソース（ポインタのファイルが記録・`tracing::`・ファイル・通信・推定を含まない。記録の側がポインタの型名を含まない）・窓（保存・`invoke`・`fetch` を含まない、新しいイベント名を他の窓が `listen` しない）・macOS の読みがポインタの 2 つ以外を読まない・列（Rust は固定長の配列だけ・窓は名前を許した枠だけ）・振る舞い（1 日分の打鍵とポインタを通して、記録へ向かうのは `handmark_day` だけ）。どれにも陽性対照。変異で赤を見る。
- **入れ切りの記録**: `input_toggles` の書き出し・区間の削除（3 か所）・起動での復元・書けないときに切った側。
- **画面**: PR 1 の判断 11 の段取り。カーソルで近くの草が倒れて尾を引く・粒が寄ってほどける・波紋・入れ切り・一時停止。格子の粗さが目に見えるか（マスの境で草の倒れがそろって見えないか）を研究者に見てもらう。

## ロールバック計画

- revert で戻る。入口の門は変えない。schema の変更は gse-dataset の同期も戻す。

## この案の弱いところ

- 格子が粗いと、隣り合う草が同じように倒れ、試作より「近くの草だけ」の細かさが落ちうる。16 × 10 で足りるかは画面で見る（足りなければ 32 × 20 にしても 1920 値・i8 で 2 KB）。
- 粒が「カーソルを追い越さない」試作の上限（残りの距離で切る）は、場では粒ごとの距離を知らないので写せない。粒のずれの上限（`MOTE_MAX`）で代える。
- 正準の箱なので、16:10 でない画面では場が少し伸び縮みする。

## 設計判断の履歴
- 実行回数: 1 回目
- 採用: v2（格子の場）
- 根拠: 研究者が選んだ（2026-11-09）。二重の実装・打鍵の遅れとの結合・ロックの競合が無く、関数が小さく配置に依らないので PR 4 の特徴にそのまま使える。見た目の細かさは画面の確かめで判定し、足りなければ格子を 32 × 20 にする。比べは design-comparison.md、退けた案は design-v1.md。
