# blockers（1a 実装中に見つけた、設計に無い分岐・Claude が仮に決めたもの。止まってはいない）

1. gse-replay の ReplayEvent に `handmark_day`（読み飛ばし専用）を足した。`KNOWN_LINE_TYPES` の受理検査が要求するため。
2. `capabilities.rs` の `handmark_day` は段 1 のとき宣言するが、送出元（lib.rs）は 1b。`s1_line_types_are_declared_only_in_s1` の送出元リストには足していない（1b で足す）。
3. 区間指定削除で `handmark_day` の要素だけ消えたとき、`redact_file` の戻り値（落とした行数）には数えない。画面の「消しました（件）」に出ない。数えるかは未決。
4. `Stage::press` は格子を過ぎてから届いた打鍵を刻みに反映しない（ライブの遅れの扱いは 1b で受信側が決める）。state.rs の冒頭に記載。
5. 読めない `.sha256` は `sha_mismatch`、読めない表は `table_broken` に倒した。
6. 検め直し（60 秒）では状態ファイルの書き込みを試さない（起動と日付の変わり目だけ）。
7. 検査用のモジュール `handmark_guard.rs` は `s1_driver_wiring_tests`（lib.rs のソース走査）を壊さないよう、lib.rs でなく handmark_store.rs から `#[path]` で宣言した。

# 判断 4 の直しで見つけたもの（止まってはいない）

- `Stage::advance_to` は未来の巨大な時刻（例 u64::MAX 近く）を渡されると、250ms 刻みで回り続ける。溢れは直したが、上限は設計に無いので入れていない。1b で受信側が時計の飛びを弾くか決める。
- `turn_off` は、開いているときだけ `OffToday` に変わる。すでに別の理由で閉じていれば、その理由を残す（`decide` の優先順どおり）。
- `scrub_state` は累計が無い（状態ファイルが壊れている）ときは何もしない。
