# 設計 —— 手跡の PR 2（帯と見えていた時間）

前提: requirement.md、decisions.md 判断 1〜3。材料は試作の枝 `spike/handmark-stage`（読むだけ）。

## アプローチ

帯は「背景の層と同じ状態を受ける、もう 1 枚の窓」として足す。新しい状態・新しい行種は作らない。足すのは次の 4 つ。

1. 帯の窓の層 `src-tauri/src/handmark_edge_strip.rs`（macOS だけ・試作から写す）
2. 帯の描画 `src/components/HandmarkEdgeStrip.tsx` と、純粋な部分 `src/components/handmarkEdgeStrip.ts`（node で試す）
3. 駆動役の `visible_ms` の足し方（`handmark_driver.rs`・`analysis/handmark/day.rs`）
4. カーソルの近さ（`handmark_pointer_thread.rs` の出来事を 1 つ足す）

## 1. 帯の窓の層（`handmark_edge_strip.rs`）

- 窓: label `handmark-edge-strip`。`setup()`（メインスレッド）で隠したまま作る。14pt・透明・影なし・焦点を取らない・タスクバーに出さない。`overlay_panel::convert_overlay_to_panel` で非アクティブの NSPanel にし、クリック透過・浮く層・全 Space・全画面の補助（試作の `prepare` の 4 つの振る舞い・run16）。NSPanel にした窓は壊さない（閉じる要求は `order_out`）。
- 間引き: 背景の窓と同じく `background_throttling(Disabled)` を付ける（PR 3 の判断 12）。覆われたときに描かないのは窓の側の判断で行う（3 節）。
- 開け閉め: 駆動役の `Effect::OpenWindow` / `CloseWindow` で、背景の窓と一緒に開け閉めする（`run_handmark_effects` の 1 か所）。帯を作れなかった・出せなかったときは、背景は閉じない（帯は従）。applog に理由を 1 行（`handmark: edge strip unavailable`）残す。
- 置き場（試作の判断 5・6）: 見張りのスレッドが 250ms ごとに、主画面の `visibleFrame` の下端に帯を置く。画面に出ている層 0 の窓（自分のものを除く）に、主画面の幅いっぱいで下端まで届く窓があれば全画面とみなし、画面の下端に置く（`CGWindowListCopyWindowInfo` の層・pid・大きさだけを読む。アプリや窓の名前は読まない）。置いた下端の高さ（点）を Atomic に置く（近さの計算が読む）。
- 見えているか: 同じ見張りで `occlusionState` を読み、帯が出ていて見えているかを Atomic `STRIP_VISIBLE` に置く。変わったときだけ帯の窓へ `handmark-strip-visible`（真偽値）を `emit_to` する。
- 見張りは帯が出ている間だけ回す（閉じたら止まり、`STRIP_VISIBLE` を偽にする）。

## 2. 状態とカーソルの近さ

- 状態: `Effect::State` を背景の窓と帯の窓の両方へ `emit_to` する（同じ値・同じイベント名 `handmark-state`）。閉じたときの `null` も両方へ。帯は `phase`・`drift`・`speed`・`irreg` を受け、背景と同じく 250ms かけて寄せるだけで、窓の中で位相や漂いを積まない（試作は窓で積んでいた。判断 1）。
- 近さ: `handmark_pointer_thread::PointerDriver` に出来事 `PointerOut::StripNear(u8)`（0〜10）を足す。
  - 純関数 `strip_near(cursor_on, y_pt, bottom_pt) -> u8` は試作の式（帯の上で 10・帯から 80pt で 0）をそのまま写す。`y_pt` は読んだ一点の正準の箱の縦から主画面の高さで戻す（新しい読みは足さない）。
  - 出すのは値が変わったときだけ。カーソルが切れている・一時停止・窓が閉じている間は 0 を 1 回出して止める。
  - 行き先は帯の窓だけ（`emit_to(handmark-edge-strip, "handmark-strip-near", u8)`）。場（`TraceField`）には入れない＝状態に影響しない。記録・tracing には出さない（ADR-050 D2）。

## 3. 帯の描画（tsx）

- 中身は試作どおり: 風で揺れる線 1 本（濃さ 0.7）・下半分の薄い霧 1 本・粒 10 個。式は試作の `wave`・霧・粒を写し、位相と漂いは届いた状態の値を使う。
- 描く間隔は純関数 `nextFrameMs(...)` で決める（`handmarkEdgeStrip.ts`）:
  - 見えていない（`handmark-strip-visible` が偽）→ `null`（描かない。見えるようになったら再開）
  - 風がある（寄せている速さか届いた速さが 0 より大きい）か、近さの薄れが寄せの途中 → 33ms（約 30 回／秒）
  - それ以外 → 100ms（約 10 回／秒）
  - 閉じた（`null` が届いた）→ 止める
- 近さで薄くする: 届いた近さ 0〜10 を 0〜1 にし、濃さを `1 − 0.75 × 近さ` へ 120ms の時定数で寄せる（試作）。
- 窓は何も保存せず、何も返さない（`invoke` を呼ばない）。数値・文字は描かない。
- `src/main.tsx` の窓の label の分岐に `handmark-edge-strip` を足す。capabilities は `handmark-stage.json` の windows に足す（listen だけ）。

## 4. 見えていた時間（`visible_ms`）

- 状態ファイル（日の累計）に `visible_ms: u64`（`serde(default)`・version は 1 のまま。PR 3 の判断 9 と同じ理由）を足す。`add_visible(ms)` は `add_shown` の隣に置く。
- 駆動役: `on_strip_visible(bool)` を `on_window_status` の隣に足し、刻みの前に lib.rs が `STRIP_VISIBLE` を渡す。刻みでは `add_shown(gap)` と同じ条件（背景が出たと分かっている・時計が飛んでいない・日が変わっていない・間が 2 秒以内）かつ帯が見えているときだけ `add_visible(gap)` する。よって常に `visible_ms ≤ shown_ms`。
- 行: `visible_ms` は記録があれば `Some(累計)`、無ければ `None`（Windows・表が無いなど。これまでの `null` と同じ読み）。区間の削除では `shown_ms` と同じく消さない（日の量で、時刻を持たない）。
- schema: 欄は変えず、説明の文だけを「帯（下の縁）が出ていて覆われていなかった時間。背景の層は数えない」に改める。`emit_schema` で `current.json` を作り直し、gse-dataset の parity が文の差を見るなら同期の枝を出す。
- 限り（文書に書く）: 帯を作れなかった走行では `visible_ms` は増えない（`shown_ms` だけ増える）。applog の 1 行で分かる。`occlusionState` は「どこか 1 画素でも見えていれば見えている」の扱いで、帯の大半が隠れていても数えうる。

## 5. 検査（ADR-050 D3・`handmark_guard.rs`）

- イベント名 `handmark-strip-near`・`handmark-strip-visible` を使ってよいファイルを限る（Rust は `handmark_edge_strip.rs`・`handmark_pointer_thread.rs`・`lib.rs`、TS は帯の 2 ファイル）。陽性対照つき。
- 帯の窓の TS を、背景の窓の TS と同じ本文検査（保存・送信・`invoke`・推定の語が無い）の対象に足す。
- 近さの出来事が `TraceField` に触れないこと（場の値が近さの有無で変わらない）を性質のテストで縛る。
- `Effect::destination` は変えない（帯の開け閉め・状態は `Window`）。記録へ向かうのは `Row` だけのまま。
- macOS だけのモジュールの定数を `cfg` の無い検査から参照しない（PR 3 の E0433）。パスの区切りは `/` にそろえる。

## 変更対象

| ファイル | 変更 |
|---|---|
| `src-tauri/src/handmark_edge_strip.rs` | 新規（macOS だけ）。窓・NSPanel・見張り・置き場・`STRIP_VISIBLE`・下端の高さ |
| `src-tauri/src/handmark_driver.rs` | `on_strip_visible`・刻みで `add_visible` |
| `src-tauri/src/analysis/handmark/day.rs` | `visible_ms` の累計（`serde(default)`）・`add_visible` |
| `src-tauri/src/handmark_store.rs` | 行の `visible_ms` を累計から |
| `src-tauri/src/handmark_pointer_thread.rs` | `PointerOut::StripNear`・`strip_near`・帯の下端の口 |
| `src-tauri/src/lib.rs` | 帯の `setup`・開け閉め・状態の配り・近さの送り・`on_strip_visible` |
| `src-tauri/src/schema_dto.rs`・`schema/current.json` | `visible_ms` の説明の文 |
| `src-tauri/src/handmark_guard.rs` | 検査の拡張（5 節） |
| `src-tauri/capabilities/handmark-stage.json` | 帯の窓を足す |
| `src/components/HandmarkEdgeStrip.tsx`・`handmarkEdgeStrip.ts` | 新規 |
| `src/main.tsx` | label の分岐 |
| `scripts/handmark-edge-strip.test.mjs`・`package.json` | node のテスト（`test:handmark` に足す） |
| `docs/functional-design.md` など | 帯と `visible_ms` の記述（手跡の節があれば） |

`tray.rs` は変えない（帯だけの入れ切りは作らない）。

## テスト戦略

- Rust（全 OS で走る純粋な部分）: `visible_ms` の足し方（出ていない・確かめ前・時計の飛び・日の変わり目・帯が見えない間は足さない、`visible_ms ≤ shown_ms`、状態ファイルの往復と古いファイルの読み、区間の削除で残る）／`strip_near` の境界（帯の上・80pt・カーソル切り）／近さの出来事は変わったときだけ・切ったら 0 を 1 回・場の値に影響しない／`emit_schema` の byte-equal。
- node: `nextFrameMs` の 4 つの分岐・届いた状態へ寄せるだけで描画の回数に依らないこと（同じ時刻の見た目が呼び方で変わらない）・近さの寄せ。
- 変異: 帯が見えないときも足す → 赤／近さを場に入れる → 赤／覆われても描く → node が赤／帯のイベント名を別のファイルで使う → 検査が赤。
- 画面と CPU: requirement の受け入れ条件どおり（研究者が gse-next を止めた時間に、一時の HOME・開発版）。

## 実装の分け方

- 実装 A（Sonnet）: 4 節・2 節の近さ（Rust の純粋な部分）とテスト・schema。
- 実装 B（Sonnet）: 1 節・3 節・lib.rs の配線・検査・node。
- 区切りごとに私が fmt・clippy・test を走らせ直し、変異で守りを確かめる。
