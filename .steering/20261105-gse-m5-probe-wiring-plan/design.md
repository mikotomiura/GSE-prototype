# 設計（v2）—— プローブの配線（ADR-031 M5）と日の終わりの問い

v1（`design-v1.md`）を読ませない別のエージェント（Opus）が、要件と一次資料だけから作った案。行番号は main（`be9f14de`）。メインが一次で確かめた主張: `eh3.rs:52` `DAY_CUTOFF_HOUR = 4`・`lib.rs:193/1929` `O1_LOG_OPENED_MS`・`lib.rs:3677-3683` overlay の `show()` は `start_session` の中だけ・`recording.rs:15-23` 一時停止の検査は `KNOWN_LINE_TYPES` から導く・`eh3.rs:334-343` `resolve` は O1 のときだけ立つ・`eh3.rs:710` `focus_row_allowed`・`probe_scheduler.rs:392-393` 次の候補は `now + interval`。

## 0 骨格

1. 段 1 は O1 の上に載る層として作る（EH3 と同じ作り方）。印は `s1.mode`、`meta` には `s1_mode` を足す。O1 の `is_o1()` の分岐はすべてそのまま効く。
2. 問いを出す判断は純粋な調停器 1 つ（`analysis/probe_arbiter.rs`）にまとめる。`lib.rs` は、Atomic を読んで入力を作り、調停器の出力を行と emit に変える薄い駆動役だけにする。`gse-replay --probes` は記録から同じ調停器を回す。
3. 無作為の枠は seed と起点だけで決まる候補の列にする（候補の時刻がポーリングの時刻に左右されない）。層化はこの枠を読むだけで、書き換えない。
4. 6 択の門は、型 `EsmConsent` を「段 1 かつ本人の同意の印あり」でしか作れないように変える。O1 だけのときは `None`（ADR-043 D8）。
5. 日の終わりの問いは、同じ調停器の中の別の小さな状態機械にする。端末の中の状態ファイル（`~/.gse/s1_day_state.json`）で再起動をまたぐ。

## 1 新しいモード（段 1）の作り方

O1 の今の作り:
- O1 は起動時に 1 回だけ決まる `OnceLock`（`o1.rs:758-775`）。ファイル名 `gse_o1_*`（`o1.rs:393`）、提出の猶予（`o1.rs:62`）、導入 ID（`o1.rs:786-812`）、同意の確認（`submission.rs:309-332`）は、どれも `is_o1()` に結び付いている。
- `start_session` は O1 では拒まれる（`lib.rs:3443-3446`）。プローブのスレッドは `SESSION_START_MS == 0` の間、待つ（`lib.rs:5556-5562`）。このため O1 ではプローブが構造的に出ない。止める条件は env・G1・EH3 の 3 つ（`lib.rs:5517-5523`）。
- EH3 は「O1 の上にだけ立つ層」の先例（`eh3::resolve`・`eh3.rs:334-343`）。`meta` には `o1_mode`・`o1_install_id` の直後に断片を足す（`logger.rs:1599-1638`）。

| 案 | 中身 | 判定 |
|---|---|---|
| A 層（採る） | `s1.rs` を新しく置き、印 `s1.mode` と env `GSE_S1_MODE=1` で判定。`s1::resolve(detected, o1_active, eh3_active)` は O1 のときだけ立てる。`meta` に `"s1_mode":"marker"|"env"` | 採る。提出・自動起動・導入 ID・削除・ファイル名・`start_session` の拒否・ショートカットを登録しないこと（`lib.rs:5678`）・介入の拒否（`lib.rs:3064`）を、コードを変えずに共有できる。印が無い O1 の配布は 1 バイトも変わらない。EH3 が同じ形で動いている |
| B O1 と並ぶ別のモード | `O1Source` を `Mode::{O1, S1}` に広げ、`is_o1()` の約 20 箇所を分け直す | 採らない。分け忘れると O1 の約束（提出・停止）が段 1 で黙って外れる |
| C O1 のまま設定ファイルで問いを開く | `~/.gse/` の JSON | 採らない。O1 は実行時に切り替えない（`o1.rs:22-26`）。`meta` で分けられない |
| D 段 1 で `start_session` を通す | 今のプローブのスレッドを流用 | 採らない。`SESSION_START_MS` を 0 に戻す経路が無く、自動提出が止まる（`lib.rs:3438-3442`） |

細部:
- EH3 との同時は立てない: EH3 は招待を出す（`eh3.rs:1618`）ので「招待を出さない」とぶつかる。両方の印があれば両方を落として O1 のままにし、`tracing::error!` に残す（`o1::resolve` が G1 との衝突で落とす作法・`o1.rs:129-141`）。研究者に確かめる（§7 の 1）。
- プローブを止める条件: 段 1 では今のスレッドを起こさない（`probes_disabled || s1::is_s1()`）。代わりに段 1 の駆動スレッドを起こす。そのスレッドは `GSE_DISABLE_PROBES` を見ない（Windows の自動起動は `.bat` を通らず env が乗らない・`autostart.rs:17-19`。尊重すると手で起動した日と自動起動の日で挙動が割れる）。env が立っていたら warn を 1 行残す。段 1 の `.bat` は env を付けない（§7 の 3）。
- Nudge と招待: R1 の枝の `invitation_settings_editable` は O1 を除く。Nudge は `record_session_meta` が O1 で拒まれる（`lib.rs:3064-3067`）うえ R1 で既定が無効。追加の作業は要らないが、検査 `s1_never_shows_invitation_or_nudge` で固定する。
- 起点: `SESSION_START_MS` を使わず `O1_LOG_OPENED_MS`（`lib.rs:193`。ローテートで引き直す・`lib.rs:1929`）にする。EH3 の `EH3_REEMIT_GEN`（`lib.rs:1922`）と同じ形の世代の数 `S1_FRAME_GEN` をローテートで進め、世代が変わったら枠を作り直して `probe_frame` 行を出し直す。
- フォーカスの遷移: EH3 と同じく、GSE 自身の窓へ移る遷移と戻る遷移を行に出さない（`eh3::focus_row_allowed`・`eh3.rs:710`。呼び出しは `lib.rs:4807-4831`）。カードを押したこと自体が `resumption` の引き金になるのを防ぎ、行に残る遷移と検出器が見る遷移を一致させる。

## 2 調停（`analysis/probe_arbiter.rs`・新規・純粋な関数）

`Arbiter::tick(&TickInput) -> Vec<Action>` を 1 秒に 1 回進める。`TickInput` は `now_ms`・`last_key_press_ms`・`last_focus_transition_ms`（自分の窓を除く）・`paused`・`resumed_at_ms`・`open_card`（無作為・層化・日の問い）・`utc_offset_s`・`power_resumed`・`app_started` だけ。`p_stuck`・HMM の状態・engine を入れる欄を持たない（ADR-031 D2）。

(a) 無作為の枠 `RandomFrame`（主）
- 候補の列は `c_{k+1} = c_k + interval_k`。`interval_k` は `StdRng::seed_from_u64(seed)` から引き、分布は今の `sample_interval_ms`（`probe_scheduler.rs:353-363`）と同じ。今の `ProbeScheduler` は `now + interval` で次を引く（`probe_scheduler.rs:392-393`）ので、候補の時刻が 1 Hz のポーリングに引きずられ、記録だけからは同じ時刻を出せない。段 1 では列を起点に固定する。今の `ProbeScheduler` は通常のモードと Phase1 のために変えない。
- 候補ごとの判定は自分の状態だけで行う: `away`（無操作 180 秒以上）・`warmup`（起点か再開から 31 秒以内）・`gap`（前の無作為の発火から 6 分以内）・`cap`（20 分に 2 回）・`no_ask`（c）・`card_open`（無作為のカードが未回答で開いている）。当たれば `Suppress{stratum: random, reason}`、当たらなければ `Fire`。
- 層化のカードが開いていても無作為は出す。層化のカードは閉じ、`realtime_label` と `activity_label` を `skip_reason = "superseded"` で書く（`SkipReason` に 1 値を足す・`logger.rs:273-293`）。無作為の判定に層化の状態は入らない。
- 一時停止の間の候補は判定しない（行は書けない・`recording.rs:64`）。

(b) 層化 `StrataDetector`（補い）
- `low_operation_end`: 押下と押下の間が `STRAT_LOW_OP_MIN_GAP_MS` 以上空いた後の最初の押下の時刻。
- `resumption`: 押下と押下の間が `STRAT_RESUME_MIN_GAP_MS` 以上空き、その間に自分の窓でないフォーカスの遷移が 1 本以上あった後の最初の押下の時刻。両方に当たる時刻は `low_operation_end` にする（§7 の 4）。
- 引き金の時刻を `probe_assignment.scheduled_ts` に書く（新しい欄は足さない）。
- 抑制: 前の無作為か層化の発火から `STRAT_GUARD_AFTER_ANY_MS` 以内なら `gap`・層化だけの上限で `cap`・次の無作為の候補が `STRAT_YIELD_BEFORE_RANDOM_MS` 以内なら `yielded`（判断 9）・何かのカードが開いていれば `card_open`・`no_ask`・`away`。
- 層化は `RandomFrame::next_candidate_ms()` と `last_fire_ms()` を読むだけ（`&self`）。型で書けないようにする。

(c) 申告を求めない区間 `NoAskPlan`（既定は無効・判断 2）
- 現地時刻の日（4:00 区切り・`eh3::local_day`）を `NO_ASK_BLOCK_MS` の区画に割り、`splitmix64(seed ^ day ^ block)` が `NO_ASK_FRACTION` 未満なら「問わない区画」。乱数は R1 の `analysis/invitation.rs` の splitmix64 を使う。
- 有効のときは、区画の中の無作為の候補を作ったうえで `no_ask` として抑制する。候補の列は有効と無効で同じ。層化も同じく抑制。
- 無効のとき（既定）は `probe_frame` に `no_ask_enabled:false` を書き、抑制の行は出ない。

(d) 日の終わりの問い `DayQuestion`（§3）
- 無作為を動かさない: 無作為が発火したときに日の問いのカードが開いていれば、伏せて保ち（記録しない）、無作為に答えた後で出し直す。次の無作為の候補が `EOD_YIELD_BEFORE_RANDOM_MS` 以内なら、出すのを待つ（ADR-048 D3）。

調停の順（1 tick の中）: ① `RandomFrame` → ② `StrataDetector`（①と枠を読むだけ）→ ③ `DayQuestion`（①②を読むだけ）。「②③を外しても①の出力の列が等しい」ことを検査で固定する。

1 時間の最大の合計（判断 8）: 無作為は 20 分に 2 回まで（60 分に 6 回）、層化は 1 時間に 3 回まで。`S1_MAX_PROBES_PER_HOUR = 9` を定数にし、検査で設定から導いた値と一致させる。同意文書（R4）にはこの定数を書く。

再現（`gse-replay --probes`）: 入力は `probe_frame`（seed・起点・定数）・`key` 行の押下・`focus_transition`・`recording_pause`・`probe_assignment` と `realtime_label`（カードが開いていた区間）。これで `TickInput` を秒ごとに組み、同じ `Arbiter` を回し、記録の `probe_assignment`・`probe_suppressed` と「一致・欠け・余り」を JSON で出す。候補の時刻と件数は厳密に一致させ、判定の理由の 1 秒の量子化のずれは「境界の 1 秒」として別に数える。

## 3 日の終わりの問い（ADR-048 D3・S1-F5〜F8・F10）

- 契機（主）: 現地時刻が `[EOD_WINDOW_START, EOD_WINDOW_END)` で、押下が `EOD_IDLE_MS` 以上途切れた時点でカードを出す。席を離れていればカードは残り、戻ったときに答える。「途切れの後に打鍵が戻った時点」で出す案もある（§7 の 5）。
- 補助（トレイの終了）: 時間帯の中で当日まだ尋ねていなければカードを出す。ボタンは「答えて終了」「答えずに終了」で、`EOD_QUIT_WAIT_MS` 待っても押されなければ終了する。`shutdown` の前に行を書く。
- 補助（一時停止）: 止めるのは即座にする。時間帯の中の一時停止は「同じ日のうちに再開したら、再開の直後に尋ねる」予約にする（`trigger:"pause_resume"`・§7 の 6）。
- 1 日の上限: 対象の日 1 つにつき当日 1 回と拾い直し 1 回まで。回答は更新させない。
- 日付の切れ目: 現地時刻 4:00（`eh3::DAY_CUTOFF_HOUR`・§7 の 7）。時差は `UtcOffsetCache`（`lib.rs:4167`）から取るが、行には書かない（判断 4）。
- 翌日の拾い直し: 切れ目の後の最初の利用（起動・`PowerEvent::Resumed`（`lib.rs:979-1019`）・切れ目の後の最初の押下のうち最も早いもの）で尋ねる。対象は「段 1 で押下を観測し、当日の回答が無く、拾い直しをまだ尋ねていない、いちばん新しい日」。前日なら「昨日の作業について」と尋ね `delayed:true`。それより古ければ尋ねない（仮・§7 の 8）。当日のカードが切れ目まで開いていたら `closed_by:"day_end"` で閉じ、拾い直しの対象にする。電源の通知のスレッドは今は肖像があるときだけ起こしている（`lib.rs:4175-4179`）ので、段 1 でも起こす（`power::start` を 2 回呼んでよいかは確かめていない・1 本にまとめる）。
- 再起動をまたぐ状態: `~/.gse/s1_day_state.json` に直近 `DAY_STATE_KEEP_DAYS` 日の `{day, seen_keys, asked_same_day, asked_pickup, answered}` だけ。書き方は `eh3::save_ledger`（一時ファイル → 置き換え → `sync_all`・`eh3.rs:498-516`）。壊れていたら `Broken` で、この走行では日の問いを出さない（`eh3.rs:471-482`）。NDJSON にも提出物にも入れない。
- 記録（新しい行種 `day_question`・時刻の鍵は `"t"` = 閉じた時刻）: `{type, t, shown_ts, shown_local_minute, target_day, trigger:"evening_idle"|"quit"|"pause_resume"|"pickup", delayed, answered, closed_by:"answer"|"dismiss"|"day_end"|"quit", items_version, motivation:1..5|null, latency_ms (表示→最初の操作), duration_ms (最初の操作→送信)}`。
- 項目は前期では動機づけの 1 項目（手跡は main に無い）。文は S-DQ の候補の表からの仮の文で `items_version:"dq-draft-1"`。目盛りは S-DQ の表を読んで決める（§7 の 11）。
- 回答の後の打鍵の量は行に書かず、`key` 行から `gse-replay --day-questions` が回答の時刻から切れ目までの押下の数を出す（区間の削除の後の数が削除を反映する）。

## 4 行種・schema・capabilities・一時停止・削除・画面

| 行種 | 状態 | 欄（要点） |
|---|---|---|
| `probe_frame` | 新規 | `t`・`frame_seed`（2^53−1 以下・R1 の招待の seed と同じ制約）・`anchor_ms`・無作為の 7 定数・層化の定数・`no_ask_enabled`・`no_ask_block_ms`・`no_ask_fraction`・`arbiter_version` |
| `probe_suppressed` | 新規（判断 9） | `t`・`candidate_ts`・`stratum`・`reason`: `away`・`warmup`・`gap`・`cap`・`yielded`・`card_open`・`no_ask` |
| `probe_assignment` | 既存 | `stratum` が 3 値すべてを取る（今は常に `random`・`lib.rs:5636-5644`） |
| `realtime_label` | 既存 | `skip_reason` に `superseded` |
| `activity_label` | 既存（送出元が初めてできる） | 変更なし（`logger.rs:685-735`） |
| `day_question` | 新規 | §3 |
| `meta` | 既存 | `s1_mode` を `o1_install_id` の直後・`eh3_*` の前に |

- capabilities: `activity_label` を `emitterless` から外し（`capabilities.rs:473-480`）、検査 `activity_label_has_no_emitter_until_it_is_wired`（`capabilities.rs:511-`）を ADR-031 D4 の手順どおり消す。`activity_label`・`probe_frame`・`probe_suppressed`・`day_question` を `config_gated`（`capabilities.rs:212`）に入れる。`config_gated` がモードで出し分けるかは実装のタスクで確かめる（EH3 は `eh3_line_types_are_declared_only_in_eh3`・`capabilities.rs:585` の型がある）。
- 3 点セット（ADR-031 D4-4）: `LogEntry::line_type()`・`KNOWN_LINE_TYPES`・一時停止の検査。一時停止の検査は `KNOWN_LINE_TYPES` から導くので（`recording.rs:15-23`）、新しい行種は自動で入る。
- 削除: 新しい 3 行種は時刻の鍵を `"t"` にする。`line_timestamp` の別名の列（`redaction.rs:163-167`）は変えない。`probe_frame` を消すとその区間の再現ができなくなるが、削除を優先する（§7 の 9）。
- schema: `schema_dto.rs` → `emit_schema` → `schema/current.json` の byte-equal、R3 の gse-dataset の同期。
- 画面: overlay の窓は `start_session` の中でしか `show()` されない（`lib.rs:3677-3683`）ので、O1 では表示されていない。段 1 では、同意の印があれば setup の後（NSPanel 化の後・`lib.rs:5782-5786`）に `show()` し、Overlay.tsx の idle の退避（画面外・クリック透過）に任せる。窓を隠すと webview の JS が休眠して `probe_triggered` を取りこぼす（`Overlay.tsx:264-274`）。
- `ProbeCard.tsx` は payload の `activity: true` のときに 6 択を出し、3 問を 1 枚に。自由記述なし。文は「直前の30秒」（`ProbeCard.tsx:181`）。`stratum` は本人に見せない。今のカードは表示中に来た新しいプローブを捨てる（`ProbeCard.tsx:64-73`）が、段 1 ではこの判断を調停器が持つ（`card_open`・`superseded`）。
- `DayQuestionCard.tsx` を新しく作り、Overlay.tsx でプローブのカードと排他に出す。App.tsx に `get_s1_mode`。段 1 の登録の画面に問いへの同意の項目。

## 5 6 択の門と同意の承認

- `activity_label_allowed(stage1_mode: bool, consent_ack: bool) -> Option<EsmConsent>` に読み替え、O1 だけでは常に `None`。既存の検査 `activity_label_needs_both_o1_and_consent`（`o1.rs:854-`）を書き換える（既存の検査の意味を変えるので PR に明記する）。
- `consent_ack` は実行時の事実: `submission::s1_probe_consent_acknowledged()` が `~/.gse/s1_probe_consent` の有無を見る。段 1 の登録の画面（O1 の `acknowledge_o1_enrollment` と同じ形・`lib.rs:2880-2890`）で、問いへの同意の項目を本人が押したときだけ書く（ADR-043 D7）。中身は時刻と `consent_version` だけ（`submission.rs:320-332`）。
- 配布物の門: 段 1 の配布の検査（`check-o1-release-readiness.sh` を段 1 用に分ける）は、段 1 の同意文書（R4）の承認の印（例 `<!-- s1-esm-consent: approved -->`）を要求する。本人の試し（R5）の配布物に求めるかは §7 の 2。
- 段 1 の回答は新しいコマンド `record_probe_response`・`record_probe_skip` にまとめ、`EsmConsent` を得てから `realtime_label` と `activity_label` を同じ `probe_id` で 2 行書く。今の `record_realtime_answer`・`record_realtime_skip` は O1 では今のまま拒む（`lib.rs:3155/3198`）。
- 同意の印が無い間は、駆動スレッドが調停器を作らない（`probe_frame` を含め行が 0）。

## 6 変更対象

| ファイル | 種別 | 変更 |
|---|---|---|
| `src-tauri/src/s1.rs` | 新規 | 印と env の判定・`resolve`・`OnceLock`・`is_s1()`・`detect_from_env()`（`eh3.rs`・`o1.rs` の鏡像） |
| `src-tauri/src/analysis/probe_arbiter.rs` | 新規 | `RandomFrame`・`StrataDetector`・`NoAskPlan`・`DayQuestion`・`Arbiter::tick`・定数 |
| `src-tauri/src/s1_day_state.rs` | 新規 | 日の問いの状態ファイルの読み書き（IO を `analysis/` の外に置く） |
| `src-tauri/src/analysis/probe_scheduler.rs` | 修正（小） | `sample_interval_ms` を `pub(crate)` にして共有。`ProbeScheduler` の挙動は変えない |
| `src-tauri/src/analysis/mod.rs` | 修正 | モジュールを足す |
| `src-tauri/src/o1.rs` | 修正 | `activity_label_allowed` の引数の意味と検査 |
| `src-tauri/src/submission.rs` | 修正 | `s1_probe_consent_acknowledged`・`write_s1_probe_consent` |
| `src-tauri/src/lib.rs` | 修正 | 起動時の `s1::set_mode`・今のプローブのスレッドの条件に `is_s1()`・段 1 の駆動スレッド・`S1_FRAME_GEN`・フォーカスの絞り込みに `is_s1()`・電源の通知を段 1 でも・`record_probe_response`・`record_probe_skip`・`record_day_question`・`get_s1_mode`・`acknowledge_s1_probe_consent`・overlay の起動時の表示・終了の経路の日の問い |
| `src-tauri/src/logger.rs` | 修正 | `LogEntry::{ProbeFrame, ProbeSuppressed, DayQuestion}`・整形の純粋関数・`line_type`・`SkipReason::Superseded`・`s1_meta_fragment` |
| `src-tauri/src/capabilities.rs` | 修正 | 宣言と検査 |
| `src-tauri/src/schema_dto.rs`・`src-tauri/schema/current.json` | 修正 | 3 行種・`s1_mode`・`superseded` |
| `src-tauri/src/redaction.rs` | 修正（検査の見込み） | 新しい行種が `"t"` で消えることの検査 |
| `src-tauri/src/tray.rs` | 修正 | 終了の補助の契機（終了の要求を駆動役へ渡す） |
| `src-tauri/src/bin/replay.rs` | 修正 | `--probes`・`--day-questions`（R1 の `--invitation` と相互に排他） |
| `src/components/ProbeCard.tsx`・`src/probeTypes.ts` | 修正 | 6 択・新しいコマンド・`superseded` |
| `src/components/DayQuestionCard.tsx` | 新規 | 日の問い |
| `src/components/Overlay.tsx`・`src/App.tsx`・`src/components/Dashboard.tsx` | 修正 | カードの排他・段 1 の判定・登録の画面の同意の項目 |
| 段 1 の配布の検査・`.bat` | 修正 | `s1.mode`・`GSE_DISABLE_PROBES` を付けない・同意の印（置き場は実装のタスクで確かめる） |

v2 の変更対象表は `analysis/probe_arbiter.rs` に状態ファイルの読み書きも入れていたが、`analysis/` に IO を置かない規約（agent-shared 技術制約 11）に合わせ、メインが `s1_day_state.rs` に分けた。

### 仮の定数（探索用・R6′ で入れ直す）

| 名前 | 仮の値 | 出典・理由 |
|---|---|---|
| `S1_RANDOM_CONFIG` | `ProbeConfig::default()`（λ 2 回/30 分・空け 6 分・20 分に 2 回・最大の間隔 22 分・離席 180 秒・ウォームアップ 31 秒） | S1-A1・`probe_scheduler.rs:164-176` |
| `STRAT_LOW_OP_MIN_GAP_MS` | 90_000 | 離席（180 秒）より短い低操作 |
| `STRAT_RESUME_MIN_GAP_MS` | 15_000 | 窓の切り替えごとに立てない |
| `STRAT_GUARD_AFTER_ANY_MS` | 360_000 | 判断 8。空けの 6 分に揃える |
| `STRAT_CAP_COUNT` / `STRAT_CAP_WINDOW_MS` | 1 / 1_200_000 | 層化の別の上限 |
| `STRAT_YIELD_BEFORE_RANDOM_MS` | 120_000 | 層化が譲る |
| `S1_MAX_PROBES_PER_HOUR` | 9（6 + 3） | 同意文書と一致させる |
| `NO_ASK_ENABLED` | false | 判断 2 |
| `NO_ASK_BLOCK_MS` / `NO_ASK_FRACTION` | 3_600_000 / 0.2 | S1-A6 の候補 |
| `EOD_WINDOW_START_MIN` / `EOD_WINDOW_END_MIN` | 1020（17:00）/ 1380（23:00） | S1-F5 |
| `EOD_IDLE_MS` | 1_200_000 | 離席の 180 秒と分ける（S1-F5） |
| `EOD_YIELD_BEFORE_RANDOM_MS` | 120_000 | 無作為を動かさない |
| `EOD_QUIT_WAIT_MS` | 60_000 | 終了を長く止めない |
| 日の切れ目 | 4:00（`eh3::DAY_CUTOFF_HOUR`） | S1-F6・S1-D1 |
| `PICKUP_MAX_TARGET_AGE_DAYS` | 1 | 前日だけ尋ねる（仮） |
| `DAY_STATE_KEEP_DAYS` | 7 | 状態ファイルを小さく保つ |

## 既存パターンとの整合性

- 判定は純粋な関数に置き、効果は `lib.rs` が適用する（`o1.rs:13`・`eh3.rs:10`）。`OnceLock` は起動時に 1 回（`o1.rs:758-765`）。印を env より優先（`o1.rs:108-117`）。
- O1 の上の層は EH3 の先例（`eh3::resolve`・`meta` の断片の順・`focus_row_allowed`・状態ファイルの原子的な書き込み・壊れていたら出さない）に従う。
- 型で門を守る（`EsmConsent`・`o1.rs:249-270`）。UI と IPC の両方で塞ぐ（`lib.rs:2953`・`3443`）。
- `stratum` は `Option` にしない（`logger.rs:1031-1036`）。新しい行種の時刻の鍵は `"t"`（ADR-031 D6）。3 点セットをそろえる（ADR-031 D4-4）。
- seed を記録して再現する（今は trace だけ・`lib.rs:5612-5622`。段 1 では行に出す）。
- 本文・アプリ名・自由記述を持たない（data-privacy ルール 7・ADR-031 D3）。新しい欄は数値と固定の文字列だけ。

## テスト戦略

Rust の単体（`probe_arbiter.rs`）:
- `random_candidates_depend_only_on_seed_and_anchor`（ポーリングの間隔を変えても候補の列が一致）
- `strata_never_change_random_candidates_or_fires`（層化と日の問いを on/off しても無作為の候補・発火・抑制の列が等しい・複数の seed・8 時間）
- `strata_read_frame_without_mutation`
- `random_fires_over_open_strat_card_and_supersedes_it`・`random_suppressed_card_open_only_by_random_card`
- `strat_yields_before_random_candidate`・`strat_guard_after_any_probe`・`strat_cap_counts_only_strata`
- `low_operation_end_fires_at_first_press_after_gap`・`resumption_requires_non_own_focus_in_gap`・`both_conditions_label_low_operation_end`
- `no_ask_disabled_by_default_emits_no_suppression`・`no_ask_keeps_candidate_list_identical`・`no_ask_blocks_are_deterministic_from_seed`
- `paused_candidates_are_not_judged`・`warmup_restarts_after_resume`
- `hourly_max_total_matches_consent_constant`
- `arbiter_input_has_no_estimator_fields`（`include_str!` で本文に `p_stuck`・`hmm`・`engine` が無い）
- 日の問い: `eod_fires_once_in_window_after_idle`・`eod_not_outside_window`・`eod_waits_for_random`・`pickup_asks_yesterday_once_with_delayed`・`pickup_skips_target_older_than_one_day`・`no_more_than_two_asks_per_target_day`・`day_end_closes_open_card_then_pickup`・`pause_in_window_defers_to_resume_same_day`・`day_state_broken_disables_eod_this_run`・`day_state_survives_restart`。時差は JST と UTC の両方で。

モードと門: `s1_requires_o1`・`s1_and_eh3_both_dropped`・`s1_marker_beats_env`・`env_value_exactly_1`・`activity_label_none_for_o1_even_with_consent`・`activity_label_some_only_for_s1_with_ack`・`s1_never_shows_invitation_or_nudge`・`o1_meta_unchanged_without_s1_marker`（`meta` の byte-equal）・`s1_meta_fragment_order`。

行と schema: 整形の純粋関数ごとの byte-equal（3 行種）・`realtime_label_skip_superseded`・`capabilities` の分割の検査・一時停止で新しい行種が落ちること・`new_s1_rows_are_deleted_by_t`・`day_question_point_interval`・`emit_schema` の byte-equal・既存のゴールデンのスナップショット（`gse-replay --snapshot`）の回帰。

replay: 小さな fixture で `--probes` が全件一致し、1 行消すと「欠け」を出す。`--day-questions` の回答の後の押下の数。

画面（実機・macOS と Windows）: 段 1 の印で起動し、同意の前はカードが出ない。同意の後に debug ビルドだけの口（`ensure_debug_enabled` の下）で無作為・層化・日の問いを出し、見える・押せる・背後のクリックを奪わない（`debug_overlay_window_state`・`lib.rs:490-`）。一時停止の間は出ない。終了の補助で「答えずに終了」が 60 秒以内に終わる。NDJSON を `gse-replay --probes` で照らす。

## 前提の枝との衝突点（R1 = `feature/nudge-default-off`）

| ファイル | R1 の変更 | M5 との衝突 |
|---|---|---|
| `lib.rs`（+246） | `close_normal_invitation`・`invitation_settings_editable`・`InvitationRunner`・`record_session_meta` の `invitation_enabled`・`start_session` と `shutdown`・`run()` の招待の runner | 段 1 の駆動スレッド・起動時の判定・`shutdown` の日の問い・電源の通知の条件。R1 が main に入った後で行番号を引き直す |
| `logger.rs`（+155） | `invitation_condition` | `LogEntry`・`line_type`・整形関数の並びへの追記 |
| `schema/current.json`（+92）・`schema_dto.rs`（+43） | `invitation_condition` | 同じ配列への追記。`emit_schema` で作り直す |
| `capabilities.rs`（+56） | `invitation_condition` の宣言 | `config_gated` と分割の検査 |
| `redaction.rs`（+27） | `invitation_condition` を消さない側へ | 検査の追記 |
| `tray.rs`（+48） | 招待の項目の動的な差し込み（位置 2） | 終了の補助。メニューの組み立てが同じ関数 |
| `bin/replay.rs`（+320） | `--invitation` | 相互に排他なモードの列 |
| `src/App.tsx`（+16） | `PHASE_WEEKS` | `get_s1_mode` |
| `analysis/invitation.rs` | splitmix64 | `NoAskPlan` が依存する（R1 が入らなければ複製になる） |

段 1 で招待が出ないのは R1 の `invitation_settings_editable` が O1 を除くことに頼る。R1 の形が変われば `s1_never_shows_invitation_or_nudge` の期待を引き直す。main の 188 コミットは `src-tauri/`・`src/` を変えていないので、R1 の rebase の衝突は文書だけ（メインが確かめた）。

## 7 研究者に確かめること

2026-11-05 に 1・2・3・6・9・10・12 を研究者が決めた（decisions.md 判断 4〜10。すべて推奨どおり。10 は「時差を残さず、`day_question` に現地の日付と現地の分だけを書く」）。残りの 4・5・7・8・11・13 は仮の値で作り、事前登録で決める。

1. 段 1 と EH3 の印が両方あるとき: 両方を落とすか、段 1 を勝たせるか。
2. 本人の試し（R5）の配布物に、段 1 の同意文書の承認の印を求めるか。本人の同意の印（登録の画面）だけでよいか。
3. 段 1 で `GSE_DISABLE_PROBES=1` を無視する（自動起動と挙動をそろえる）のでよいか。
4. 層化の 2 つの引き金の定義（空きの閾値・両方に当たる時刻の扱い）と、打鍵が戻った瞬間に出すことの是非（割り込みが大きい）。
5. 日の問いを「途切れが閾値に達した時点」で出すか、「途切れの後に打鍵が戻った時点」で出すか。
6. 一時停止の補助の契機を「同じ日の再開の直後に尋ねる」にする案でよいか。
7. 日付の切れ目を 4:00（EH3 と同じ）にし、S1-D1 と同じにするか。
8. 対象の日が前日でないときに尋ねないか、日付を示して尋ねるか。拾い直しの期限。
9. `probe_frame` を区間の削除の対象にするか、`meta` と同じく残すか。
10. 日の問いの再現のために `utc_offset_s` を行に残すか（残せば地域が粗く分かる。残さなければ時間帯の判定を再現できない）。
11. 日の問いの前期の項目の数（1 か 2）と目盛り。
12. `skip_reason = "superseded"` を足してよいか（schema の enum を 1 値増やす）。
13. 1 時間の最大の合計（仮に 9 回）を同意文書に書く数として受け入れるか、層化の上限を下げるか。

## ロールバック

- 段 1 の効果はすべて `s1::is_s1()` の下にある。印 `s1.mode` を外して起動し直せば O1 の挙動に戻る（`o1_meta_unchanged_without_s1_marker` が保証）。
- コードは PR を `git revert` で戻す。schema の追加は additive で古い記録は読める。新しい行を含む記録を古い gse-dataset に通すと未知の行種で落ちうる（R3 の側は確かめていない）。
- `~/.gse/s1_day_state.json` と `~/.gse/s1_probe_consent` は段 1 でしか読まないので、残っていても O1 には効かない。

## 読んでいない・確かめていない範囲（v2 の作り手の申告）

- 読んでいない: data-privacy 以外の SKILL.md の本文、ADR-047 の本文、S-DQ のカード、`Overlay.tsx` の後半、`schema_dto.rs`、`replay.rs` の中身、`capabilities::config_gated` の中身、`.bat` を作る場所、R1 の `redaction.rs` の差分の中身。
- 確かめていない: `power::start` を 2 回呼んでよいか。Windows で overlay のカードを押したときにフォーカスの遷移が起きるか。`config_gated` がモードで出し分けるか。

## 設計判断の履歴

- 実行回数: 1 回目
- 採用: ハイブリッド（v2 を土台に、日の問いの状態ファイルの IO を `analysis/` の外の `s1_day_state.rs` に置く点を v1 から残す）
- 根拠: 研究者が推奨どおり選んだ（2026-11-05）。v1 は画面の窓・自分の窓へのフォーカスの遷移・一時停止の検査の 3 点で一次の事実を外していた。v2 は無作為の枠を記録から厳密に再現でき、EH3 の先例に揃う。比べは `design-comparison.md`。
