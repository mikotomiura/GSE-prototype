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
