# 設計（1a・OS 非依存）

判断 1 の 6 問を実装の形にしたもの。ここに無い分岐を実装の途中で見つけたら、勝手に決めず `blockers.md` に書いて止める。

## 0. 置き場所（architecture-rules ルール 1・4）

| ファイル | 中身 | IO |
|---|---|---|
| `src-tauri/src/analysis/handmark/mod.rs` | 下の 4 つの `pub mod` | なし |
| `analysis/handmark/state.rs` | 状態の純関数（試作 `handmark_wind.rs` の写し＋位相・漂い・種） | なし |
| `analysis/handmark/assignment.rs` | 割付の表の解釈・日の割付・SHA-256 の照合・描画の種 | なし（バイト列を受ける） |
| `analysis/handmark/day.rs` | 日の累計と切る状態（状態ファイルの中身の型）・日付の変わり目 | なし |
| `analysis/handmark/gate.rs` | 入口の門の判定・検め直しの契機 | なし |
| `src-tauri/src/handmark_store.rs` | 表・`.sha256`・状態ファイル・印のファイルの読み書き・書き込みの試し | あり |
| `src-tauri/src/bin/gse-handmark-table.rs` | 研究者が表を作る道具 | あり |
| `logger.rs`・`schema_dto.rs`・`capabilities.rs`・`redaction.rs` | `handmark_day` の行 | — |

1a では `lib.rs` に配線しない（窓・トレイと一緒に 1b で配線する）。使われない公開の項目には、試作と同じく `#[cfg_attr(not(test), allow(dead_code))]` をモジュールの宣言に付け、「1b で配線する」と注記する。

## 1. 状態の純関数（ADR-051 D5 のライブの契約と再生の契約）

- 入力: 打鍵の時刻の列（UTC の ms・`InputEvent` の `timestamp` と同じ時計・`is_press && !recording::is_paused()` のものだけ。1b で lib.rs から渡す）、種（u64）、起点 `t0`（その走行で手跡を出し始めた時刻）、時刻 `t`。ポインタの口は PR 3 で足す（PR 1 は打鍵だけ）。
- 固定の時間刻み: 250ms。刻みの格子は絶対の時刻の 250 の倍数に揃える（`t0` を 250 の倍数に切り下げた点から）。
- 状態 `StageState { speed, irreg, phase, drift, layout_seed }`:
  - `speed`・`irreg`: 試作の `Wind::tick` の式と定数をそのまま（テストも写す）。
  - `phase`: 刻みごとに `phase += (前の speed + 新しい speed) / 2 × 0.25`（試作の窓が 250ms かけて線形に寄せていた積分と同じ）。
  - `drift`: `(格子の時刻 − 格子の起点) / 1000 + 種から決まるずれ`（ずれは splitmix64 で [0, 1000) の実数）。入力に依らない基層の時間。
  - `layout_seed`: 種から決まる u32（窓が草と粒の配置に使う。試作の固定値 11 の置き換え）。
- 純関数の形: `Stage::new(seed, t0)`・`press(t)`・`advance_to(t)`（格子の点まで刻みを進める）・`state()`。`replay(presses, seed, t0, t) -> StageState` を用意し、ライブも再生も同じ `Stage` を通す。
- 性質のテスト（`proptest` を使わない。依存を増やさない・固定の種の小さな擬似乱数で入力の列を 200 通り作る）:
  1. 同じ入力から `StageState` の各 f64 の `to_bits()` が一致する。
  2. 種だけを変えると `drift` か `layout_seed` が変わる（陰性の対照）。
  3. 描画の回数を状態に影響させない: `advance_to` を途中で何回呼んでも、1 回で `t` まで進めたのと `to_bits()` で一致する。
  4. 打鍵の順序と時刻だけで決まる（キーの種類を受ける口が型に無い）。

## 2. 割付の表（判断 1-1・ADR-051 D4）

- 置き場所: 配布形は `s1::marker_path_for(exe, levels)` の親（`s1.mode` と同じフォルダ）の `handmark_assignment.json` と `handmark_assignment.sha256`。開発・検証は環境変数 `GSE_HANDMARK_TABLE=<表のパス>` で、SHA-256 のファイルは同じフォルダの同じ名前で拡張子を `.sha256` に替えたもの。
- 形式（`serde(deny_unknown_fields)`・`version` は 1 だけ）:
  ```json
  {"version":1,"s1_start_day":20400,"early_days":10,"late_start_day":20410,"days":[true,false,false,true]}
  ```
  - `*_day` は `eh3::local_day` の数え方（4:00 区切り）。`late_start_day == s1_start_day + early_days` を検める。
  - `days[i]` は後期の (i+2) 日目の「あり・なし」（後期の初日は割付の外で必ず表示・表に入れない）。長さは 1〜400。2 日ずつのブロックの中で並べ替えた結果であることを検める（各ブロック `[2k, 2k+1]` が true 1 つと false 1 つ。最後のブロックは 1 つでもよい）。
- `.sha256` の中身: 先頭の空白で区切った最初の語が 64 桁の 16 進（大文字小文字は問わない）。表のファイルのバイト列そのものの SHA-256 と比べる（`sha2` は既存の依存）。
- 日の割付 `assigned(day) -> Assigned`: `Before`（前期）・`LateFirst`（後期の初日）・`On`・`Off`・`After`（表の外）。
- 描画の種 `draw_seed(table_sha256_hex, day) -> u64`: `SHA-256(sha256_hex + ":" + day の 10 進)` の先頭 8 バイト（big endian）。前期の日にも同じ式で決まる（ADR-051 D3 の「前期の日の種は日付と表の SHA-256 から」。PR 4 で固定するときの第一の候補として書く）。

## 3. 日の状態ファイルと印（判断 1-4・1-6）

- `~/.gse/handmark_day_state.json`: `{"version":1,"day":20410,"shown_ms":0,"toggles":[{"t":..,"on":false}],"off":false,"first_shown_day":20410,"stage_starts":[..],"overflow":false}`。書き方は `s1_day_state::save` と同じ（一時ファイル → `sync_all` → 置き換え）。読めない・壊れているときは `Broken` を返し、その日は出さない。
- 日付が変わったら `day` を今日にし、`shown_ms`・`toggles`・`off`・`stage_starts`・`overflow` を空に戻す（`first_shown_day` は残す。単一の日付で、累積の量ではない）。
- `toggles` と `stage_starts` は 1 日 64 個まで。超えたら古いものを捨てず、新しいものを入れずに `overflow` を真にする（行にも出す）。
- 切る操作: 状態ファイルに `off = true` と切った時刻を書く。失敗したら `~/.gse/handmark_off_<day>` を作る（中身は空）。戻す操作は状態ファイルに書き、印があれば消す。どちらも失敗したらこの走行では出さない側に倒す（戻す操作の失敗では出さないまま）。
- 起動のとき: 状態ファイルと今日の印を読み、その後に状態ファイルへの書き込みを試す（読んだ中身をそのまま書き直す）。書けなければ、その日は出さない（理由 `state_unwritable`）。印があれば出さない（理由 `off_today`）。
- 障害を注入するテスト: 状態ファイルと印の書き込みを差し替えられる形（`trait HandmarkFs` か、関数の引数に書き込み関数を渡す）にして、次を縛る。
  1. 出している → 切る（状態ファイルの書き込みが失敗・印の書き込みは成功）→ 落ちる → 同じ日に起動 → 出さない。
  2. 出している → 切る（両方失敗）→ 落ちる → 同じ日に起動（まだ書けない）→ 出さない。
  3. 翌日に起動すると、割付どおりに戻る（前日の印は見ない）。
  - 残る穴（両方失敗して、起動のときには書ける）は、テストで「望ましい振る舞い」として縛らない。`handmark_store.rs` の冒頭と `decisions.md` に書く。
- 再起動で 0 に戻らない: 1 日の途中で 2 回起動した列で、後の行の `shown_ms` が前の行の値以上であること・机上で最後の行を採れば二重に数えないことをテストする（行の生成までを関数にしてテストする）。

## 4. 入口の門（判断 1-5・ADR-051 D5）

- 開く条件: 段 1 のモード（`s1` の判定が `Some`）∧ 表が読めて検めに通る ∧ `.sha256` が一致 ∧ 状態ファイルが読めて書ける ∧ 今日の割付が `LateFirst` か `On` ∧ 切っていない。
- 閉じる理由（行の `reason`・固定の文字列）: `table_missing`・`table_broken`・`sha_missing`・`sha_mismatch`・`state_broken`・`state_unwritable`・`off_today`・`assigned_off`・`before_late`・`after_table`。段 1 のモードでないときは行を書かない（理由も書かない）。
- 検め直しの契機: 起動・日付の変わり目・前回から 60 秒。純関数 `needs_recheck(last_ms, last_day, now_ms, today) -> bool`。
- テスト: 開いた後に表を消す（読み込みの結果を `Missing` にする）と、60 秒後の検め直しで閉じる。`.sha256` を書き換えると閉じる。

## 5. `handmark_day` の行（判断 1-2・ADR-051 D4）

- 書く時点: 起動（門の判定の後）・日付の変わり目（前の日の最後の写しと、新しい日の最初の写し）・終了・5 分ごと。中身はその日の累計の写し。机上では日ごとに最後の行を採る（`schema_dto` の doc に書く）。
- 項目（`day_question` と同じく、現地の分は書かない。日は現地の日の番号）:
  - `t`（書いた時刻・UTC の ms）・`day`・`assigned`（`before`・`late_first`・`on`・`off`・`after`・`unknown`〔表が無いなど〕）・`late_start_day`（null 可）・`first_shown_day`（null 可）
  - `shown_ms`（その日に出ていた時間）・`visible_ms`（1a・1b では常に null。見えていた時間の計り方は PR 2）
  - `toggles`（`[{"t":..,"on":bool}]`）・`stage_starts`（`[ms]`・再生で位相の起点に使う）・`overflow`
  - `table_sha256`（64 桁の小文字・null 可）・`draw_seed`（16 桁の 16 進の文字列・JSON の数の精度を避ける・null 可）・`reason`（null 可）
- `capabilities.rs`: 段 1 のときだけ `config_gated` に入れる（`day_question` と同じ作法）。
- `redaction.rs`: 行は残し、削除区間に入る `toggles` の要素と `stage_starts` の要素だけを消す（判断 1-2）。テストを足す。
- `schema_dto.rs` → `cargo run --bin emit_schema` → `schema/current.json` を更新する。gse-dataset との parity は /finish-task で見る（gse-dataset 側の同期は別の PR）。
- 書く値はすべて型の決まった数・真偽・固定の文字列・16 進だけにする（外部由来の文字列を入れない）。`format_*_line` で書く（`format_day_question_line` の作法）。

## 6. 記録の検査（ADR-050 D3 のうち打鍵だけの PR 1 に当たる行・試作 `handmark_stage_guard.rs` の考え方）

- 振る舞い: 1 日分の打鍵の列を `Stage` と日の累計に流し、門の判定と行の生成を通したとき、生じる `LogEntry` が `HandmarkDay` だけであること。
- 型: `handmark_day` の行の型に、打鍵の時刻・キー・風の値（`speed`・`irreg`・`phase`）を持つ欄が無いこと（`schema/current.json` の `handmark_day` の項目名が上の §5 の一覧と一致することをテストで縛る）。
- 語の検査: 新しいファイルの本文に、記録の口（`LogEntry::Key` など試作の検査が見ていた語）が出ないことを見る検査と、わざと語を含む文字列で検査が赤になる陽性対照（対照の文字列は実行時に連結して作る・memory: gate-green-but-artifact-broken の型 4）。

## 7. `gse-handmark-table`

- 引数: `--seed <u64> --s1-start-day <i64> --early-min <u32> --early-max <u32> --late-days <u32> --out <dir>`。
- 前期の長さは `[early_min, early_max]` から種で一様に引く。`days` は後期の 2 日目から `late_days − 1` 日分を 2 日ずつのブロックで並べ替える。擬似乱数は splitmix64（依存を増やさない）。
- 出力: `<dir>/handmark_assignment.json`（改行で終わる・キーの順は固定）と `<dir>/handmark_assignment.sha256`（`<hex>  handmark_assignment.json\n`）。標準出力に SHA-256 を出す（既存の bin の作法を見て合わせる）。
- テスト: 同じ引数から同じバイト列・出力を §2 の検めに通すと通る・種を変えると変わる。

## テスト戦略

- `cargo test --manifest-path src-tauri/Cargo.toml --workspace`・`cargo clippy`（既存の設定）・`cargo fmt`・`emit_schema` の byte-equal。
- `analysis/` のテストは両 OS で走る（`cfg` を付けない）。`handmark_store.rs` のファイルの権限に頼るテストは `cfg(unix)` を付け、差し替えの関数のテストを主にする。
