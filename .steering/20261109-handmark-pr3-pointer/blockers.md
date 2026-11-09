# blockers / 自分で決めた細部（A1〜A4・実装役）

仕様どおりに進められなかった点は無い。次の細部は仕様に書かれていなかったので実装役が決めた。レビューで確かめてほしい。

1. `TraceField::new` の前の押下は `true`（最初の一点まで「押されている」とみなす）。駆動役が窓を開いた瞬間に押しっぱなしでも波紋が出ない。副作用: 再生の合成の押下が刻み 1 に当たると、その 1 回は波紋にならない。
2. `advance_to` は `Step { sample: None, cursor_on: false, click_on: false }` で刻みを埋める（読みなしでは入れ切りは結果に効かないので同じ）。場・速さが 0 で最後の入力が無い（`is_idle`）間は、刻みを回さず格子へまとめて進める。
3. 「最後の入力」は、カーソルが前の一点から動いた刻み、または波紋の出た刻み。位置が動かないまま 8 秒で、場は正確に 0 になる。
4. `PointerDriver`: 窓を最初に開いた tick（実効の入れ切りが立った最初の tick）で `TraceField::new(now)`。その tick は世代を進めず（epoch 0）、全部 0 の `Trace` を 1 回出す。刻みが無い tick（`target - grid_t < 16`）は `read` を呼ばない。以後の変化は `reset()`（世代 +1）して 0 の `Trace` を出す。窓がまだ一度も開いていないときの変化は何も出さない。
5. `PointerOut::Trace` は `Box<TraceState>`（clippy の large_enum_variant）。`PointerOut` に `Debug` は無い（テストは `matches!` と `==`）。
6. `next_wait_ms`（A4 の直しで書き換え）: 実効の入れ切りがある（窓が開いていて・一時停止でなく・カーソルかクリックが入っている）間は、止まっていても常に 16。250 は読まない間（閉じている・一時停止・両方切っている）だけ。理由: 補訂 1 の項目 1 は 16ms ごとの読みで、8 秒止まった後に 250ms で読むと最初の短いクリックを取りこぼす。これで `WARM_MS`・`warm_until_ms` は不要になり消した（`TraceField::is_active` は pub のまま残る）。
7. 合成の一点（`trace_replay`）: 区間が重なる・逆順の行は前を優先（直前に採った行の終端以前の行は捨て、始めを直前の終端へ切り詰める）。`t0` 以前の行は使わない。向きは `SplitMix64::new(seed ^ timestamp).below(16)`。座標は f64 で計算して f32 に落とす。表の `cos 45°` は clippy の approx_constant のため `FRAC_1_SQRT_2` を使う（表の末位が 1 ulp 変わるだけ）。
8. ライブの一致のテストは、`tick` を 16ms ちょうど（格子の時刻）ごとに呼び、読みは合成の一点を順に返す。窓を最初に開く tick（`t0`）では読まない前提。epoch は両方 0 で、`bits()`（世代込み）が一致する。確かめていないこと: 16ms ちょうどでない呼び出し間隔でのライブと再生の差（仕様の外）。
9. 確かめていないこと: macOS の実機読み（A5 以降）・窓の受け取り・Windows の CI（`input/handmark_pointer.rs` は cfg なしの `pub`）。

## A5（入力ごとの入れ切りの記録・実装役が決めた細部）

10. 状態ファイルの `version` は **1 のまま**。`input_toggles`・`cursor_off`・`click_off` は `serde(default)` の追加で、古い状態ファイル（欄なし）をそのまま読める。上げると `is_valid` が古いファイルを Broken にして当日の累計が消えるため。逆向き（新しいファイルを古いバイナリで読む）は `deny_unknown_fields` で Broken になるが、配布は前に進むだけなので扱わない。固定のテストは、古い形を読めるテスト（`the_old_json_shape_is_still_read`）と新しい形の固定（`json_shape_is_fixed`）に分けた。
11. 関数は既存の `turn_off`/`turn_on` に合わせて 2 本: `turn_input_off(fs, ev, input, now) -> ToggleOutcome`（`State` か `NotPersisted`。印は作らない＝`MarkOnly` は返さない）・`turn_input_on(...) -> Result<(), RestoreFailed>`（書けなければ前の状態へ戻して Err）。駆動役の `set_input` が `on` で振り分ける。`Evaluation::inputs_on() -> (カーソルが入っている, クリックが入っている)` を足した（累計が無いときは `(true, true)`・そのとき窓は開かない）。
12. 記録の日が今日と違う間（時計の巻き戻り）は、切る側は状態（`cursor_off`/`click_off`）だけ切って記録には足さない・入れる側は `RestoreFailed`（`turn_on` と同じ作法）。
13. 区間の削除で書き直せず最小の形に落とすとき（`scrub_state_file` と駆動役の `on_redact`）は、`DayRecord::minimal_keeping_off` で `off` に加え `cursor_off`/`click_off` も残す（切った側に倒す）。時刻の列は全部落とす。
14. `schema_dto` の `input_toggles` は `serde(default)`（schemars では必須から外れる）。PR 3 より前の行（欄なし）が schema に対して有効なままになる。gse-dataset の同期で確かめてほしい。
15. `handmark_guard.rs` の `the_handmark_day_schema_has_exactly_the_designed_fields` は A5 の時点で赤になるので、欄名の一覧に `input_toggles` を足した（A7 の予定の一部を前倒し）。
16. `capabilities.rs` は行種の名前の一覧だけで欄の列挙は無いので変更なし。

## A6（駆動役・実装役が決めた細部）

17. `Effect::PointerGate` は `last_gate`（`(open, cursor, click)`・初期値は閉じた `(false, true, true)`）と比べて、変わったときだけ出す。例外は日が変わる `tick` で、変わらなくても 1 回出す（仕様の「日が変わるたびに」）。初期値を閉じた側にしたので、閉じた日の起動・段 1 でない走行では何も出ない（既存の「段 1 でなければ出来事なし」のテストを保つ）。
18. `set_input` は窓を出していないとき何もしない（トレイの項目も出ない）。切った・入れたら行も 1 つ出す（`turn_off` と同じ）。入れるのが書けずに失敗したときは出来事を何も出さない。
19. `lib.rs` の `run_handmark_effects` は網羅の match なので `Effect::PointerGate { .. } => {}`（受け取って捨てる）を足しただけ。配線は B2。
20. 駆動役の `on_redact` の最小の形も `minimal_keeping_off` を使う（A5 の 13）。

## A7（検査・実装役が決めた細部）

21. `FILES` は 8 → 12 件（末尾に `trace.rs`・`trace_replay.rs`・`input/handmark_pointer.rs`・`handmark_pointer_thread.rs`）。`FILES[5]` の添字は不変。ポインタの本文の検査は `pointer_files()`（`FILES[8..]`）を見る。**B1・B4 で足すとき**: `FILES` の末尾に `("input/handmark_pointer_macos.rs", include_str!(...))` を足し、配列の長さを 13 に、`pointer_files()` は `FILES[8..]` のままで新しい分も含む（`assert_eq!(files.len(), 4)` を 5 に直す）。macOS の読みには、試作の「境界」の検査（`modifierFlags`・`keyCode`・`CGEvent`・`addGlobalMonitor`・`unsafe` が無いこと・`mouseLocation`/`pressedMouseButtons` が在ること）を写して足す。窓の TS（`HandmarkStage.tsx`・`handmarkStageTrace.ts`）は `include_str!("../../src/components/...")` の別の一覧（試作の `WINDOW`）で、`invoke`・`localStorage`・`fetch`・`console`・配列を作る行の名前の一覧（試作の `d4_lists_only_named_slots`）を写す。TS の検査は B4 で作る。
22. 禁じる語の一覧は検査ファイル（走査の対象外）に書き、陽性対照は「実際の本文の先頭に語を実行時に足した本文」で赤になることを確かめる（試作と同じ作法）。`File` は部分一致だが、現在の 4 ファイルの本文には当たらない（当たったらその語を単位で見るよう直す）。追加で禁じた語: `log_tx`・`info!(`・`warn!(`・`debug!(`・`error!(`・`trace!(`・`println`・`eprintln`・`dbg!`。
23. 型の層は試作の `Probe`（固有の定数と trait の既定の定数の特殊化）を写し、`assert_not_printable!` マクロで 7 型 × 3 trait を `const _: () = assert!` にした（実装すればテストのビルドが止まる）。陽性対照 `Probe::<f64>`・`Probe::<String>` が真。記録の側への逆向きは型の名前を `std::any::type_name` から実行時に得る（改名に追従）。
24. 列の検査は構造体の定義（`struct Name {` から対応する `}`）だけを見る（関数の中の `Vec` は対象外。`TraceState::bits` が `Vec` を返すのは定義でないので許す）。識別子の単位で比べる（`Vec` が `VecDeque` に当たらないように）。`PointerReader` は今は存在しないので、あれば検査する形にした。
25. 振る舞いの検査は、駆動役を 600 秒ぶん（16ms ごと）回し、`PointerGate` の値を `PointerDriver` の `Gate` へ流して、合成の一点（`trace_replay::synth_points`）を読みとして通す。カーソル・クリックの入れ切り・全体のやめる・描くを途中に入れ、`Trace`・`Ripple` が出ていること（空回りでない）と、記録へ向かうのが `Row` だけであることを見る。`PointerOut` の網羅の match（`pointer_out_goes_to_the_log`）は腕を足すとコンパイルが止まる。
26. 自分で変異を 1 つ入れて確かめた: `trace.rs` の末尾に `std::fs::read` を足すとソースの検査が赤になり、戻すと緑（メインの変異の確認は別に行う）。

## B（macOS の配線・トレイ・窓・node のテスト・実装役が決めた細部）

27. **objc2-app-kit の宣言（B1 で確認）**: `~/.cargo/registry/src/*/objc2-app-kit-0.3.2/src/generated/NSEvent.rs` の `mouseLocation`（1140 行）と `pressedMouseButtons`（1148 行）はどちらも `pub fn`（safe）で、`MainThreadMarker` を引数に取らず、`extern_class!` にも `MainThreadOnly` の指定が無い（`NSEvent` は `super(NSObject)` のみ）。→ メインスレッドでないポインタのスレッドから呼べる宣言。ただし「宣言が許す」ことの確認で、Apple の実装がスレッドセーフかまでは確かめていない（試作は同じ読みを別スレッドで動かして実測している）。
28. `emit_trace` / `emit_ripple` は仕様の `(app, &TraceState)` に **`t_ms: u64` を足した**（窓が遅れた値を捨てるのに送った時刻が要り、時計を駆動役と同じ UTC の ms にするため呼び出し側の `now` を渡す）。`emit_ripple` は `&RipplePoint` を取る。payload の欄名は試作に合わせて camelCase（`epoch`・`tMs`・`cells` / `tMs`・`x`・`y`）。Rust の欄は `t_ms`。
29. `BEND_MAX`・`MOTE_MAX` は `trace.rs` で `pub` にした（窓への量子化が使う）。窓の TS 側の同名の定数は手で写している（`handmarkStageTrace.ts`）。値の一致を機械で検査してはいない（変えたら両方直す）。
30. 画面の大きさは `handmark_stage::prepare` で `monitor.size() / scale_factor`（論理 point）を `AtomicU32` 2 つ（f32 のビット）に置く。窓を出すたびに置き直す。`scale_factor <= 0` のときは置かない（前の値のまま・最初は 0 で `to_point` が `None`）。ディスプレイ構成が変わったとき（主画面の入れ替え）は次に窓を出すまで古い。
31. ポインタのスレッドは終了の `is_shutting_down()` を 1 周ごとに見て抜ける。駆動スレッドが落ちたときは `HandmarkWindowGuard::drop` が門を 0 にする（ポインタのスレッドは次の tick で `PointerDriver` が閉じた門を見て 0 の場を 1 回送り、250ms 待ちに戻る）。ポインタのスレッド自体がパニックしたときの再起動はしない（窓は動かないだけで、打鍵の側は影響を受けない）。
32. トレイの項目（B3）: 状態は 2 つの `AtomicU8` の配列（あるべき状態・実際に出している状態、符号 0 = 出さない・1 = 印なし・2 = 印あり）。駆動役の `Effect::PointerGate { open, cursor, click }` から `open.then_some((cursor, click))` で書く（`input_items()` と同じ値）。メニューの `CheckMenuItem` は押すと **自分で印を反転する**ので、押した直後に `HANDMARK_INPUT_RESYNC` を立て、更新スレッドが次の 1 秒の周回で駆動役の状態へ印を言い直す（`handmark_input_plan` の `force`）。駆動役が拒否した（表示が古い・入れるのが書けなかった）ときもこれで印が戻る。差し込みの位置は「やめる」の上（無ければ終了の前）、カーソルはクリックの前。純関数は `handmark_input_plan`・`handmark_input_after`・`handmark_input_step`（実行を closure で受け、成功した結果を照合の値として返す）・`handmark_input_index`。
33. 押下の向き: メニューに出ていた印の反対を `on` として `handmark_set_input_from_tray` へ渡し、そこで駆動役の今の状態（`input_items()`）と `on` が食い違うとき（= 表示が古い）は何もしない。窓を出していない（`input_items()` が `None`）・終了中も何もしない。
34. 窓（B4）: 場の寄せは `TRACE_TICK_MS = 33`（Rust の送る間隔）で線形。窓の時計は `performance.now()`。TTL（1000ms）は場を最後に受け取ってから。**場が 0 だけの写し（Rust は止まる時に 1 回送る）も「受け取った」に数える**（その後は 0 のまま・描画は絞る）。`handmark-state` の null で場と波紋を消す。世代が進んだ（`receive` の `reset`）ときも消す。波紋の種は世代を持たないので遅れ（場と同じ基準）だけで捨てる。波紋の 2 重の輪は配列のリテラルを避けて `ring()` を 2 回呼ぶ（D4 の検査が列の作成を見るため）。
35. 検査（`handmark_guard.rs`）: `FILES` は 13 件（末尾に macOS の読み）。`pointer_files()` は `FILES[8..]` のまま 5 件。新しい検査: macOS の読みが `NSEvent::` で `mouseLocation`・`pressedMouseButtons` 以外を読まない（陽性対照つき）／窓の TS が保存・返送・通信の語を含まない／他の `src/` のファイルが `handmark-trace`・`handmark-ripple` を含まない（`read_dir` で `src/` を辿り、手跡の窓の 2 ファイルを除く・陽性対照つき）／`handmark_stage.rs` が全窓への `.emit(` を使わない／窓の列が名前を許した枠（草・粒・波紋・場の 3 本）だけ（陽性対照つき）。変異で赤を確認: macOS の読みに `NSEvent::modifierFlags_class` を足す→赤、窓の TSX に `localStorage`・`const trail = [];` を足す→赤、`src/` に `handmark-ripple` を含む .ts を置く→赤（どれも戻して緑）。
36. node のテスト（B5）: 試作の 9 件からホイールの件（7 件目）を外し、8 件目（実時間で減らす）を「最後の受け取りから 1 秒で場が 0 になる」件に置き換え、場の件（i8 を戻す・不正な場を受けない・補間 3 件・寄せ・波紋の遅れ・世代）を足して 14 件。TTL で実際に場を消す処理は `HandmarkStage.tsx` の中（`sweepPointer`）にあり node では試していない（判定 `traceExpired` と、消した後の場の読みだけ）。
37. `package.json` に `test:handmark`。`ci.yml` の frontend-check（`npx tsc --noEmit` の後）に step を足した。**node のバージョン**: `setup-node@v4` の `node-version: 22` はメジャーの範囲で、最新の 22.x に解決されるか、ランナーのツールキャッシュに既にある 22.x が使われる（`check-latest` は既定 false）。後者が 22.18 未満だと `.ts` を直接読めないので、step の先頭で `process.versions.node` を見て 22.18 未満なら理由を言って落とす（静かに失敗しない）。ランナーの実際の版は確かめていない（CI を回さないと分からない）。
38. `tsc --noEmit`: `tsconfig.json` の `include` は `["src"]` なので `scripts/` は入らない。`src/components/handmarkStageTrace.ts` は tsc を通る（`.mjs` のテストは型検査の対象外）。
39. **Windows の cfg の目視確認**（手元は macOS で Windows のビルドは走らない）: macOS だけが使う `HANDMARK_POINTER_GATE`・`spawn_handmark_pointer`・`handmark_stage::{emit_trace, emit_ripple, screen_size_pt}`・`input::handmark_pointer_macos` には `#[cfg(target_os = "macos")]`（`handmark_stage.rs` は `imp` の中）。`Effect::PointerGate` の腕は `open`・`cursor`・`click` を全 OS で使う（トレイの状態へ）。トレイの関数・`handmark_set_input_from_tray` は全 OS で使われる。定数 `TRACE_EVENT`・`RIPPLE_EVENT` はモジュール直下（検査が全 OS で使う）。これで未使用の警告は出ないはずだが、Windows の clippy は走らせていない。
40. 確かめていないこと: 実機で動くか（読み・場の送り・窓の描画・波紋）／トレイの押下が実際に効くか（CheckMenuItem の自動反転と言い直し・差し込み位置・押した後の印）／格子の粗さの見え方／Windows の clippy／CI の node の版／16 ms ごとの `epoch_ms()` と `is_paused()` の費用（軽いはずだが測っていない）。B1+B2 の commit は `tray::set_handmark_inputs` を参照するので、その commit 単独ではビルドできない（B3 の commit と対）。
