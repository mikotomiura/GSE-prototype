# 設計 —— M5 の 1 本目（B1〜B3）

土台は計画の `.steering/20261105-gse-m5-probe-wiring-plan/design.md`（v2 ハイブリッド）。ここには、1 本目の範囲と、R1 の後の main（`8edc2d4b`）を読んで計画から変えた点だけを書く。行番号は `8edc2d4b`。

## 実装アプローチ

1. 段 1 の層 `s1.rs` を `o1.rs`・`eh3.rs` の鏡像で作る。印 `s1.mode` の有無（中身は見ない・`o1::decide` と同じ）と env `GSE_S1_MODE` の完全一致 `"1"`。`resolve(detected, o1_active, eh3_detected)` は O1 のときだけ立て、EH3 の印もあれば両方を落とす（計画の判断 7）。
2. 純粋な調停器 `analysis/probe_arbiter.rs` を作る。駆動役（2 本目）が 1 秒ごとに `TickInput` を渡し、`Vec<Action>` を受け取る。IO・時刻の取得・乱数の entropy・OS API・推定器を持たない。
3. 新しい行種 3 つと `SkipReason::Superseded` と `meta` の `s1_mode` を、logger・schema・capabilities・redaction にそろえて足す。送出元が無いので capabilities では `emitterless`（本タスクの判断 2）。

## 計画から変えた点（本タスクの判断 4〜7）

| # | 計画 | 変えた形 | 理由 |
|---|---|---|---|
| 4 | `TickInput` に `utc_offset_s` を入れ、調停器が `eh3::local_day` で日を出す | `TickInput` に現地の日 `local_day: i64` と現地の分 `local_minute: u32` を入れ、駆動役が `eh3::local_day`・`eh3::local_minute_of_day`（`eh3.rs:353/359`）で計算する | `analysis/` が最上位のモジュール `eh3` に依存しない（`architecture-rules` ルール 1）。時差の変換は `eh3` の既存の検査が守る。JST と UTC の検査は、調停器では「日の切れ目をまたぐ `local_day` の列」で書き、変換そのものは 2 本目の駆動役の検査に置く |
| 5 | 候補の列は seed と起点で決まる（`probe_id` の出し方は書いていない） | 間隔の乱数（`StdRng::seed_from_u64(frame_seed)`）と `probe_id` の乱数を分ける。`probe_id` は駆動役が entropy から作って `Action` に添える | 同じ乱数の列から `probe_id` も引くと、発火したかどうかで後の候補の時刻が変わり、「候補の列は seed と起点だけで決まる」が崩れる |
| 6 | `SkipReason` に `Superseded` を足す | 加えて、`calibration_eval::SkipReasonKind`（`calibration_eval.rs:75-90`）にも足す。UI からの `record_realtime_skip`（`lib.rs:3352-3356`）は `Superseded` を拒む（調停器だけが書く値にする） | impact-analyzer の指摘を一次で確かめた: `SkipReasonKind::parse` が知らない値の行を `gse-replay` は `unknown_enum_lines` に数えて捨てる（`replay.rs:3896-3899`）。検査は 1 つも赤くならない。UI が `superseded` を名乗れると、本人の未回答と差し替えが混ざる |
| 7 | 起動時に `s1::set_mode` を 1 行 | `eh3::set_mode`（`lib.rs:4169`）の前に段 1 を判定し、両方の印があれば EH3 も落としてから `eh3::set_mode` する | EH3 は先に `set_mode` されると後から落とせない（`OnceLock`） |

## 変更対象

### 新規

- `src-tauri/src/s1.rs`: `MARKER_FILE_NAME = "s1.mode"`・`ENV_VAR = "GSE_S1_MODE"`・`S1Source {Marker, Env}`・`decide`・`resolve`・`modes_conflict_with_eh3`・`set_mode`・`mode`・`is_s1`・`detect_from_env`。
- `src-tauri/src/analysis/probe_arbiter.rs`:
  - 定数（計画 design.md §6 の表のとおり）と `ArbiterConfig`（`ProbeConfig::default()`＋層化・問わない区間・日の問いの定数）。`ARBITER_VERSION = "s1-arbiter-1"`。
  - `RandomFrame`: `frame_seed`・`anchor_ms`。候補は `c_0 = anchor`、`c_{k+1} = c_k + sample_interval_ms(rng)`。判定の理由は `away`・`warmup`・`gap`・`cap`・`no_ask`・`card_open`。一時停止の間の候補は判定せずに飛ばす。
  - `StrataDetector`: `TickInput` の押下の時刻の列から `low_operation_end`・`resumption` の引き金を出す。抑制は `gap`・`cap`・`yielded`・`card_open`・`no_ask`・`warmup`。`RandomFrame` は `&` でしか読まない。
  - `NoAskPlan`: 既定は無効。`SplitMix64(frame_seed ^ day ^ block)` で区画を決める（`invitation.rs` の `SplitMix64` を `pub(crate)` にして使う）。
  - `DayQuestion` と `DayState`（日ごとの `seen_keys`・`asked_same_day`・`asked_pickup`・`answered`・serde で読み書きできる純データ・`DAY_STATE_KEEP_DAYS` 日で刈る）。契機は夕方の途切れ・翌日の拾い直し・一時停止の後の再開・終了（`on_quit`）。壊れた状態では作らない（`DayQuestion::disabled()`）。
  - `Arbiter::tick(&mut self, &TickInput) -> Vec<Action>`: ① `RandomFrame` → ② `StrataDetector` → ③ `DayQuestion`。
  - `TickInput`: `now_ms`・`key_presses_ms`（前の tick からの押下の時刻）・`focus_transitions_ms`（同じ・自分の窓を除いたもの）・`paused`・`resumed`・`open_card: Option<OpenCard>`・`local_day`・`local_minute`・`app_started`・`power_resumed`。推定器の欄は持たない。
  - `Action`: `FireProbe {stratum, scheduled_ts}`・`Suppress {stratum, candidate_ts, reason}`・`SupersedeOpenStrat`・`ShowDayQuestion {target_day, trigger, delayed}`・`CloseDayQuestion {target_day, closed_by: DayEnd}`。

### 修正

| ファイル | 変更 |
|---|---|
| `analysis/mod.rs` | `pub mod probe_arbiter;`（`pointer_bin` と `probe_scheduler` の間） |
| `analysis/probe_scheduler.rs` | `sample_interval_ms` を `pub(crate)`。挙動は変えない |
| `analysis/invitation.rs` | `SplitMix64` と `next_u64`・`next_unit` を `pub(crate)` |
| `analysis/calibration_eval.rs` | `SkipReasonKind::Superseded` |
| `lib.rs` | `mod s1;`・起動時の判定（判断 7）・`record_realtime_skip` で `Superseded` を拒む |
| `o1.rs` | `activity_label_allowed(stage1_mode, consent_ack)` に読み替え（式は同じ `a && b`）。doc と検査 `activity_label_needs_both_o1_and_consent` を段 1 の意味に書き換え、名前も `activity_label_needs_both_s1_and_consent_ack` に |
| `submission.rs` | `S1_PROBE_CONSENT_FILE_NAME = "s1_probe_consent"`・`S1_PROBE_CONSENT_VERSION`・`s1_probe_consent_acknowledged()`・`write_s1_probe_consent(now_ms)`（中身は `acknowledged_at` と `consent_version` だけ）。パスを引数に取る純粋に近い内側の関数を分けて検査する |
| `logger.rs` | `LogEntry::{ProbeFrame, ProbeSuppressed, DayQuestion}`・`line_type`・整形の純粋関数 3 つ・書き出しの腕・`SkipReason::Superseded`・`SuppressReason`・`DayQuestionTrigger`・`DayQuestionClosedBy`・`s1_meta_fragment`（`o1_mode_fragment` の o1 と eh3 の間） |
| `schema_dto.rs` → `schema/current.json` | 3 行種・`meta.s1_mode`・`skip_reason` の `superseded`。`emit_schema` で作り直す |
| `capabilities.rs` | `KNOWN_LINE_TYPES` に 3 つ。`emitterless` の Windows 版と非 Windows 版の両方に 3 つ（本タスクの判断 2） |
| `redaction.rs` | `probe_frame` を区間の削除から外す（`:163`・検査の `:615`・`:664` の 3 か所。先例は R1 の `invitation_condition`）。他の 2 行種は `"t"` で消える |

### 行の形（すべて時刻の鍵は `"t"`）

- `probe_frame`: `t`（枠を作った時刻）・`frame_seed`（2^53−1 以下）・`anchor_ms`・`arbiter_version`・無作為の 7 定数・層化の 6 定数・`no_ask_enabled`・`no_ask_block_ms`・`no_ask_fraction`・日の問いの 3 定数（時間帯の始まりと終わりの分・途切れの長さ）。
- `probe_suppressed`: `t`（判定した時刻）・`candidate_ts`・`stratum`・`reason`。
- `day_question`: `t`（閉じた時刻）・`shown_ts`・`shown_local_minute`・`target_day`（現地の日の番号 = 1970-01-01 からの日数・`eh3::local_day` と同じ数え方）・`trigger`・`delayed`・`answered`・`closed_by`・`items_version`・`motivation`（1..5 か null）・`latency_ms`・`duration_ms`。時差は書かない（計画の判断 4）。

## 既存パターンとの整合

- 層は EH3 の先例（`eh3::resolve`・`meta` の断片・`OnceLock`）、門は `EsmConsent` の型（`o1.rs:270`）、印の判定は `o1::decide`・`o1_enabled_by_env`（`o1.rs:108-117`・`:92-94`）。
- 行種の追加は R1 の `invitation_condition` の一式（`logger.rs:1170/1232/1674/2413`・`capabilities.rs`・`redaction.rs`）。
- 無作為の分布は `ProbeScheduler::sample_interval_ms` を共有する（`probe_scheduler.rs:353`）。`ProbeScheduler` は変えない。

## テスト戦略

- `cargo test --workspace`（`src-tauri/` から）で、計画の tasklist の B1〜B3 の検査名を置く。次は 2 本目へ回す: `s1_never_shows_invitation_or_nudge`（招待と Nudge を止めるのは駆動役と `record_session_meta` の経路で、ここでは純粋な部分が無い。実装時に純関数で書けるなら 1 本目に入れる）、時差の変換を含む JST と UTC の検査（判断 4）。
- 調停器の検査は計画のテスト戦略の `probe_arbiter.rs` の全項目。8 時間の模擬を複数の seed で回す。
- 書き出しの byte-equal（3 行種と `meta` の断片）、`line_type_matches_known_line_types` のサンプルに 3 つを足す。`SkipReason` の往復の検査に `Superseded`。
- `cargo run --bin gse-replay -- tests/fixtures/minimal.ndjson --snapshot tests/snapshots/minimal.json` と、他のゴールデンの `--snapshot`。
- `cargo run --bin emit_schema` と `schema/current.json` の byte-equal。`cargo clippy --all-targets -- -D warnings`・`cargo fmt --check`。
- 実機での確かめ: なし（画面と駆動役が無い）。Windows は CI で見る。

## ロールバック

- PR を `git revert`。印 `s1.mode` を置かなければ、本タスクの後も配布物の挙動と記録は 1 バイトも変わらない（`o1_meta_unchanged_without_s1_marker`）。schema の追加は additive。

## 実装中に変わった点（2026-11-06・最終化）

- `day_question` は `shown_local_minute` を書かず `in_eod_window`（真偽）を書く（decisions 判断 9・時差を出さない）。`Action::ShowDayQuestion` に `in_window` を足した。
- 区間の削除: `day_question` は `shown_ts`〜`t`、`probe_suppressed` は `candidate_ts`〜`t`。2 つ目の時刻が 0 なら点（判断 8・10）。
- 調停器: 無作為の離席は候補の時刻 `c` 以前の最後の押下から判定し、この tick の押下は ① の後に反映する。溜まった候補の問わない区画は候補ごとの時刻で引く（`local_at`）。一時停止の再開に加えてスリープの復帰でもウォームアップと日の問いの途切れの起点をやり直す。拾い直しはカードが開いていれば持ち越す（判断 10）。
- `s1::resolve_with_eh3` を足し、`lib.rs` は戻り値を `eh3::resolve` に渡す。
- `bin/replay.rs` に 3 行種の読み飛ばしの変種を足した（足さないと段 1 の記録が `--snapshot` で読めない）。`calibration_eval::SkipReasonKind` に `superseded`。
- 2 本目へ回したもの: `.steering/_handoff/next-session-gse-m5-part2-driver-ui.md` §2。
