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
