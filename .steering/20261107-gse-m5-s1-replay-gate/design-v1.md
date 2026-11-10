# 設計（v1・PR 1 の再生）

PR 2（門・launcher・文書・schema の同期）の設計は、PR 1 の後にこのファイルの末尾へ足す（O1 の門の型にならうので /reimagine はかけない）。

## 実装アプローチ

再生は **駆動役 `S1Driver` ごと** 記録の行から回す。調停器 `Arbiter` だけを回すと、`Action` を行に写す規則（`Suppressed` の `t = wall.max(candidate_ts)`・`SupersedeOpenStrat` の順・日の問いの伏せと出し直し・一時停止で下ろすカード）を再生の側に書き直すことになり、本物の写し方とずれても気づけない。`S1Driver` は OS に触らない純粋な型で、`tick(&TickEnv, new_probe_id)`・`close_probe`・`day_row_for_close`/`commit_day_close`・`on_pause_requested`・`on_quit`・`finish_before_end` を公開している（`s1_driver.rs:307`・`488`・`503`・`531`・`548`・`565`・`607`）。

### 記録から作る入力

| 駆動役への入力 | 記録の行 | 根拠 |
|---|---|---|
| 枠（`start_frame`） | `probe_frame`（`frame_seed`・`anchor_ms`・設定 22 項目） | `logger.rs:1783-1829` が `ArbiterConfig` の全項目を書く。`lambda_per_ms` は `num()` の書式が往復で同じ値に戻るかを検査で固定する |
| 押下（`push_press`） | `key` の押下（`is_press: true`） | 駆動役へ送る押下は `key` 行を書く同じ `out.key` の押下で、一時停止の外だけ（`lib.rs:5313-5321`） |
| 遷移（`push_focus`） | `focus_transition` | 行を書いた遷移と同じものを送る（`lib.rs:5883-5889`） |
| 一時停止・再開（`TickEnv.paused`・`pause_epoch`） | `recording_pause`（`paused`） | |
| プローブを閉じる（`close_probe`） | 記録の `realtime_label` の `ts`（`probe_id` で記録の `probe_assignment` と結び、再生の割り当てと `(stratum, scheduled_ts)` で対応づける） | 閉じた時刻は本人の操作なので記録から借りる |
| 日の問いを閉じる | 記録の `day_question` の `t`・`closed_by`・`answered`（`closed_by` が `day_end` のものは再生が自分で出すので借りない） | 同上 |
| 終了（`on_quit`・`finish_before_end`） | `trigger: "quit"` の `day_question` と、ファイルの最後の `meta`（`End`） | |
| 時差 | 引数 `--utc-offset-secs`（必須） | 計画の判断 4 で行に書いていない。⚠️ 無作為の判定も `is_no_ask_block` が現地の日と分を使うので、日の問いだけでなく全体に要る |
| 日の問いの前日までの覚え | 引数 `--day-state <s1_day_state.json>`（任意） | NDJSON に入っていない（`~/.gse/s1_day_state.json`）。無ければ空から始め、覚えに依る行（`pickup`・`delayed`）は「覚えの外」に分ける |

### tick の時刻

記録には tick の時刻が無い。再生は `anchor_ms` から 1000 ms ごとに壁時計の tick を作り、入力はその行の時刻に届いたものとする（駆動役は 2 秒遅らせた時刻までの入力しか調停器に渡さないので、届く時刻の揺れは判定に入らない）。照合の鍵を tick の位相に依らないものにする:

- `probe_assignment`: `(stratum, scheduled_ts)` の完全一致。
- `probe_suppressed`: `(stratum, candidate_ts, reason)` の完全一致（`t` は tick の位相に依るので鍵にしない）。
- `day_question`: `(target_day, trigger, delayed, closed_by, answered)` が一致し、`shown_ts` の差が 1500 ms 以内。

### 照合の分類（JSON）

行種ごとに `matched`・`missing`（記録にあり再生に無い）・`extra`（再生にあり記録に無い）・`boundary`・`debug`・`outside_state` を数え、`missing`・`extra`・`boundary` は各行の鍵を並べる。

- `boundary`: 次のどれかにかかる不一致。一致・欠け・余りに混ぜない。
  - `recording_pause` の行の時刻の前 2000 ms（判断 2）。
  - 再生の tick の位相に依る 1 秒: 候補の時刻がカードを閉じた時刻の前後 1000 ms 以内（開いているカードの判定が tick の境で割れる）。
- `debug`: `debug: true` の行（判断 3）。照合から外し、数だけ出す。
- `outside_state`: `--day-state` が無いときの `pickup`・`delayed` の日の問い。

あわせてラベルの集計を出す: `answered`・`dismissed`・`dont_remember`・`superseded`（調停器が書いた差し替え・本人の未回答と分ける）・`paused_dropped`（`probe_assignment` あり・ラベルなし・次の行種の出来事が `recording_pause` の `paused: true`）・`unclosed`（ラベルなしでファイルの終わり）。回答率の分母から `superseded` と `paused_dropped` を外した値も出す（S1-A4・A7）。

### 複数のファイル

`--probes <file>...` で複数を受け、`meta.session_start` の順に並べて 1 本の時間の列として回す。ローテートをまたいで開いているカードは、古いファイルの `probe_assignment` と新しいファイルのラベルを `probe_id` で結ぶ。`probe_frame` が出るたびに `start_frame` で枠を作り直す（日の問いの状態は駆動役が引き継ぐ）。

### `--day-questions`

答えた `day_question` ごとに、`t` から次の現地 4:00（`eh3::local_day` の切れ目）か記録の終わりまでの `key` の押下の数を出す。区間の削除の後の記録ならその数は削除を反映する（計画 §3）。`--utc-offset-secs` が要る。

### 確かめ用のカードの印（判断 3）

- `ProbeCard`・`DayRowData` に `debug: bool` を足す。`debug_show_probe` は `apply` の後で自分のカードと `Effect::Assigned` に印を立てる（`Action` は `analysis/` の型なので触らない）。`DayCard.debug` は既にある（`s1_driver.rs:75`）ので `day_row_for_close` で写す。
- 行は手書きの書式関数（`logger.rs:710`・`725`・`777`・`1848`）なので、偽のときは何も足さず、真のときだけ末尾に `,"debug":true` を足す。本物の行のバイト列は変わらないことを既存の byte 固定の検査（`s1_rows_format_byte_equal` ほか）で守る。
- `schema_dto.rs` の 4 行種に `debug: Option<bool>`（`skip_serializing_if`）、`schema/current.json` を再生成する。⚠️ gse-dataset 側の同期は PR 2 でまとめるので、PR 1 の時点で `/finish-task` の parity check が赤になる。PR 1 のマージ前に gse-dataset 側を先に揃えるか、PR 1 に同期を含めるかは実装の前に研究者に聞く。
- `activity_label_*` の組み立ての引数は増やさない（`check-o1-release-readiness.sh` の正規表現が呼び出しの形を見ているため・impact-analyzer）。行の構造体に足した欄を書式関数が読む。

## 変更対象

### 新規作成するファイル
- `src-tauri/src/s1_replay.rs` — 行の読み取り・駆動役の再生・照合・集計（純粋・OS に触らない・`invitation_trigger.rs` と同じ置き方）。単体テストを同じファイルに置く。

### 修正するファイル
- `src-tauri/src/bin/replay.rs` — `--probes`・`--day-questions` の引数（相互排他の列 `1775-1796`・`--json` の許可・`--utc-offset-secs` と `--day-state` の許可）と呼び出し・使い方の文。
- `src-tauri/src/s1_driver.rs` — `ProbeCard.debug`・`DayRowData.debug`・`Effect::Assigned` の印・`debug_show_probe`。
- `src-tauri/src/logger.rs` — 4 行の構造体と書式関数の `debug`。
- `src-tauri/src/lib.rs` — 行を組み立てる箇所で `debug` を写す（`s1_day_question_entry`・`emit_s1_superseded`・`record_probe_response`・`record_probe_skip`・割り当ての行）。
- `src-tauri/src/schema_dto.rs`・`src-tauri/schema/current.json`。
- `src-tauri/src/lib.rs` の mod 宣言（`s1_replay`）。

## 影響範囲

- `--snapshot` のゴールデン: `run_replay` を触らない。`ReplayEvent` は `deny_unknown_fields` でないので `debug` の欄が増えても読める（`replay.rs:1252`）。6 本のゴールデンの byte-equal を回す。
- CI は `--snapshot` を 1 か所叩くだけ（`ci.yml:602`）。schema の drift 検査（`ci.yml:611-612`）は `current.json` の再生成で通す。
- `capabilities.rs` は行種単位なので変えない。
- 区間の削除は NDJSON に印を残さない（`redaction.rs`）。削除した区間の押下は再生から見えず、不一致になりうる。再生は削除の台帳（別ファイル）を読まないので、既知の限界として使い方の文と手順書に書く。

## 既存パターンとの整合性

- R1 の `--invitation`（`replay.rs:1842-1951`・照合の中身は `invitation_trigger.rs` の `build_recorded_ticks`・`replay_recorded`）と同じく、行を 1 パスで集め、中身はライブラリの純粋なモジュールに置き、失敗は `tracing::error` と exit 1（stdout を空に・fail-closed）。
- `--invitation` は再現して出すだけで記録と照合しない。照合の分類は新しく書く。
- 合成の記録は `replay.rs:4654-4673` と同じく検査の中で NDJSON の文字列を作る。

## テスト戦略

- 駆動役が書く行と再生の一致（往復）: 検査の中で `S1Driver` を合成の入力（押下・遷移・一時停止・閉じる）で回し、本物の書式関数で行を作って NDJSON にし、それを `s1_replay` に通して全件 `matched`。続けて 1 行消すと `missing`、1 行足すと `extra` が出る（壊すと赤）。押下の届く時刻を 0〜1900 ms 遅らせても一致する（2 秒の遅れが効いている）、2100 ms 遅らせると割れうる（陽性対照）。
- 一時停止の境目の 2 秒の不一致が `boundary` に入り `missing` に入らない。
- `debug: true` の行が `debug` に入る。本物の行の byte 固定の検査が変わらない。
- ローテートをまたぐカード（2 ファイル・`probe_id` で結ぶ）・一時停止で下ろしたカード（`paused_dropped`）・`superseded` の分け方。
- `--day-questions` の押下の数（4:00 の切れ目・JST と UTC）。
- 引数: `--probes` と `--invitation` の排他・`--utc-offset-secs` 無しの拒否・`--day-state` の読み取り失敗の拒否。
- `cargo test --workspace`・6 本のゴールデンの `--snapshot`・`emit_schema` の byte-equal。
- 手で: 2 本目の画面の確かめと同じ隔離した HOME の記録を `--probes` に通し、確かめ用のカードが `debug` に入ることを見る（記録は手元だけ・Codex に送らない）。

## 既知の限界（実装の前に分かっているもの）

- `S1_TICK_LAG_MS = 2000` で押下が届き切るかは、記録に届いた時刻が無いので直接は測れない。実の記録で `missing`・`extra` が 0 なら届き切っていたことの必要条件にとどまる。
- 区間の削除をまたぐ記録は一致しない。
- 前日までの覚えは `--day-state` を渡さない限り再生できない。

## ロールバック計画

PR を `git revert`。再生は新しいモードで、既存のモードと記録の行（`debug` が偽のとき）は変えないので、戻しても既存の記録と再生の結果は変わらない。
