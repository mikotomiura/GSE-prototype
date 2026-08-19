# v0.1.27 の Rust 変更のコードレビュー (2026-08-20・事後)

⚠️ ★ 本ファイルは**実装の後**に行った独立レビューの記録である。
実装セッションとは別セッションで、`git show 2261652` の diff と現在のソースを一次資料として読んだ。

対象コミット: `2261652 feat(logger): 収集仕様を自己記述にし G-1 二度押しを直す (v0.1.27)`
参照した Skill: `hook-constraints` / `verify-before-claiming`

## 検証方法

★ **テストが緑であることを根拠にしない。** 実装を読み、主張 (docstring・コミットメッセージ) と
実体が一致するかを突き合わせた。境界値は**テストの有無**ではなく**両側から閉じているか**で見た。

実行した検証: `cargo test --workspace liveness` → **22 passed / 0 failed**

## ✅ 確かめられたこと

### 1. 2 トラックの閾値分割は厳密に排他

| 主張 (docstring) | 実体 |
|---|---|
| 「`peak >= log_after_ms` のものは数えない … 2 つのトラックは閾値できれいに分割される」 | `health()` は `starved_ms >= 30_000` で `Suspect` / `tick()` は `prev_starved_ms < 30_000` で計上 |

→ ★ **隙間も重複も無い。** しかも境界は**両側から**固定されている:

- `starve_window_boundary_is_exclusive`: `29_999` → `Some(1)` / `30_000` → `None`
- `hook_health_semantics_unchanged`: `29_999` → `Ok` / `30_000` → `Suspect`

### 2. 1Hz ループ (`lib.rs`) の呼び出し順序

- `prev_starved_ms` を `step()` の**前**に取得 ✅
- 窓集計を `if health == prev_health && !rehook { continue; }` より**前**に配置 ✅
  (後ろに置くと**平常時こそ**窓がまるごと消える)
- `elapsed_ms` は公称 `TICK_MS` ではなく `Instant::elapsed()` の実測 ✅
- ブロック境界の reset (`is_new_block_epoch`) を `tick()` の**前**に実行 ✅

### 3. hook コールバックの制約 (`hook-constraints` 共通-1 / 共通-3)

Windows / macOS とも、コールバック内は `CALLBACK_COUNT` / `EVENTS_DROPPED` の
`fetch_add(1, Ordering::Relaxed)` **だけ**。★ ログ出力 (`dropped` の `tracing::error!`) は
1Hz ループ側にある → **コールバック内でログを書かない**規則を守っている。

### 4. G-1 の核心 — `swap` をログのロックの**中**で行う

★ これが無いと、並行二度押しで
「A が swap → B が swap → B が先にロックを取ってローテート → B が `SessionStart` → その後 A が
`SessionStart`」＝ **新ファイルに `session_start` 2 本** (P010 block07 と同じ形) が残る。
ロックの中で swap すれば「誰が新規か」と「何を書くか」が同時に決まる。

`decide_start_action` の真理値表も設計 (`design.md` §1.2) ＋ 判断 12 と一致:

| `g1` | `was_active` | `meta_recorded` | `blocks_started` | → |
|---|---|---|---|---|
| false | * | * | * | `NotG1` |
| true | true | **false** | * | `RetryAfterMetaFailure` (**1 行も書かない**) |
| true | true | true | * | `RotateForRestart` (カウンタを増やさない) |
| true | false | * | >0 | `RotateForNewBlock` |
| true | false | * | 0 | `FirstBlock` |

⚠️ ★ 設計の enum は 3 値だったが実装は 5 値。判断 12 (`RetryAfterMetaFailure`) の追加と、
`NoRotate` を `NotG1` / `FirstBlock` に割った差である。**意味は同じで実装のほうが明示的**。

### 5. 失敗時に「黙って間違った状態へ進まない」が全層で一貫している

| 箇所 | 失敗時の扱い |
|---|---|
| 容量ガード | `log_channel_has_room(&tx, 2)` を **`swap` より前** (2033 行 vs 2083 行) で実行。★ **G1 のときだけ**なので通常運用は不変 |
| `Rotate` の `try_send` 失敗 | fail-loud で中止し `Err` を返す。★ 巻き戻しが枝で違う — `RotateForNewBlock` はカウンタを戻し `session_active=false` / ⚠️ `RotateForRestart` は **`true` のまま** (前セッションはまだ開いて計測中。false にすると「`session_end` の無い開きっぱなしのファイル」を停止扱いにする) |
| `SessionStart` の `try_send` 失敗 | ここまで来ると巻き戻せないので `Err` は返さず `ERROR` ログに必ず残す (⚠️ `validate_blocks.py` は 0 本を FAIL にしない設計なので**黙って通る**) |
| `HookHealth` の `try_send` 失敗 | ★ `dropped_at_last_line` / `peak_starved_ms` / `prev_health` を**1 つも進めない**。進めると次 tick が `continue` に落ち、遷移が**永久に消える** |

★ 容量ガードの docstring が正直である: 「これは**予約ではなく確認**であり原子的な保証にはならない。
だから送信側の失敗処理を省いてはならない」→ 実際に省いていない。

### 6. `dropped_delta` (ADR-013 D4 穴 B)

- 基準は「前回**行が出た**時点」(`dropped_at_last_line`)。★ `tracing` 用の `prev_dropped` とは
  **別変数**である (混ぜると「前回行からの差分」でなくなる)
- ブロック開始で基準を引き直す → ファイル境界をまたがない
- 行の形は `dropped_delta_is_written_alongside_cumulative_dropped` が固定
  (`"dropped":3,"dropped_delta":3`)。★ 累積 `dropped` は非破壊で残している

### 7. `anonymize.rs` (+35 行) — ★ 実装変更ゼロ、テストのみ

匿名化器は未知フィールドを serde の往復で素通りさせるので、新しい行種には
**コードではなく固定 (pin) が要る**。テストは**両方向**を assert している:

| 対象 | 期待 |
|---|---|
| `starve_window.t` | 相対化される (`1060000` → `60000`) |
| `win_ms` / `n_lt30` / `sum_lt30_ms` | ★ **そのまま** (相対化してはならない側も固定) |
| `hook_health.dropped_delta` | 件数なので不変 |
| `meta.app_version` / `capabilities` | ★ **保たれる** (落とすと「計器が無い」と誤判定される) |

→ ★ 「絶対 epoch が匿名化済みデータに載る」経路が塞がれている。

### 8. 網羅テストに陽性対照が組み込まれている

- `ndjson_rows_are_written_only_by_logger` が「走査範囲が正しい」という**前提そのもの**を検査
- `every_capability_has_a_reachable_emitter` は、ソース走査が壊れて空集合になると**落ちる**
  → ★ `capabilities_covers_every_line_type` の**空振り (vacuous pass) を防ぐ対照**になっている

## ⚠️ 見つけた点 3 件 — ★ 研究者判断で**無視**（2026-08-20）

★ いずれも低影響。**直さない**と決めた。⚠️ ただし「気づいていなかった」ことにしないため残す。

### A. `every_capability_has_a_reachable_emitter` に偽陰性の経路がある

`line_types_in_logger_source()` は `logger.rs` を `#[cfg(test)]` ごと走査するので、
★ **テストの期待値文字列にしか現れない行種**も「writer あり」と判定する。
⚠️ docstring の「既知の限界」は「送出元が実在してもバグで呼ばれない可能性」までで、
この経路は含まれていない。

### B. 1Hz サンプリングより短いエピソードは原理的に見えない

`starved_ms` は tick 単位でしか進まないので、1 秒未満で閉じた micro エピソードは
`0 → 0` にしか見えず `n_lt30` に入らない。→ ★ **`n_lt30` は下側に偏る。**
⚠️ 記録済みの「既知の切り捨て」はブロック末尾の端数の話で、この**分解能**の話は別件である。

### C. `RotateForRestart` のときだけエピソードが 1 本、新ブロックへ誤帰属しうる

二度押し経路では `session_active` が `true` のままなので、`is_new_block_epoch` で窓を reset した
**同じ tick** に、reset 前に貯まっていた `prev_starved_ms` が「正→0」として**新しい窓へ**計上されうる。
★ 通常のブロック境界では `session_active` が false になり `prev_starved_ms` が 0 なので発火しない。

⚠️ 気になるのは、`tick()` の docstring が **「誤帰属より既知の切り捨てを採る」**と方針を明記している
のに、★ **新設した二度押し経路だけがその例外**になっている点である
(実害は二度押し 1 回につきエピソード 1 本ぶん)。

## ★ 結論

**v0.1.27 の Rust 変更に欠陥は見つからなかった。** 上記 A/B/C 以外に指摘は無い。
特に「失敗したときに黙って間違った状態へ進まない」が hook 側・ロガー側・G-1 側で
**一貫して**守られている。

## ⚠️ このレビューで見ていないもの（★ 混ぜない）

- `capabilities.rs` の定数表 (`KNOWN_LINE_TYPES` / `CONFIG_GATED` 等) の**中身の妥当性**
  (テストは集合の割り切りを見るが、「その行種が本当に config で止まるか」は見ていない)
- `logger.rs` の `Rotate` 処理本体 (`write_meta_end` → `open_log_target` → `write_meta_start`)
- `schema_dto.rs` の +69 行
- ★ **`starve_window` の実発火は依然として未観測**。B の分解能もあり、実データで 0 行だったときに
  「条件未達」か「計器不良」かを切り分ける材料は現状ない。
