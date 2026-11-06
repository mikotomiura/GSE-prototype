# 設計（採用: v2 を土台にしたハイブリッド）—— M5 の 2 本目「段 1 の駆動役と画面」

- 作成: 2026-11-07（design.md・design-v1.md を読まずに、requirement.md・decisions.md 判断 1/2/4/5/6・引き継ぎ §2・計画・1 本目・一次のコードから独立に組んだ）
- 拘束条件: decisions 判断 1（`probe_frame` の `t` = `anchor_ms`）・判断 2（取り消しを同意の項目と同じ画面に）・判断 4（O1 の配布の門を段 1 に合わせて直す・送出元は `lib.rs` に置く）・判断 5（日の問いの仮の文と `dq-draft-1`）・判断 6（途中の同意は O1 のローテートを 1 回起こす）。

## アプローチ

### 骨格（v2 の芯は 3 つ）

1. **カードの真実源は backend の駆動役が持つ。** 画面（overlay の webview）は「いま出すべきカード」の状態を描くだけの受け手にする。イベントは差分ではなく **状態の全体**（`s1_card_state`）を送り、画面はいつでも `get_s1_card` で取り直せる。日の問いを伏せる・出し直す（引き継ぎ §2 の 8）は、駆動役の中の「表示の選び方」1 か所で決まり、画面は伏せていることを知らなくてよい。
2. **純粋な駆動役（`s1_driver.rs`）と、副作用の実行役（`lib.rs` の駆動スレッドとコマンド）に割る。** `s1_driver.rs` は Tauri も logger も持たず、`Arbiter` の `Action` とカードの状態を「出来事（`Effect`）」の列に変える。`LogEntry` を組むのはすべて `lib.rs` に残す。これで (a) `capabilities` の送出元の検査（`include_str!("lib.rs")`・`capabilities.rs:644-660` の型）と、(b) O1 の配布の門の送出元の検査（`check-o1-release-readiness.sh:124-139` が `lib.rs` を grep する）が空回りしない（判断 4 の「送出元を `lib.rs` の外に置く案は門を空回りさせる」）。
3. **入力は「時刻つきの事実」を専用の口から受け、駆動役は固定の遅れ（`S1_TICK_LAG_MS = 2000`）で読む。** 押下とフォーカスの遷移は別スレッドからチャネルで遅れて届くので、壁時計そのままで判定すると「候補の直前の押下がまだ届いていない」tick が生じ、3 本目の `gse-replay --probes`（記録の `key` 行から同じ調停器を回す）と結果が割れる。2 秒遅らせた時刻を `TickInput::now_ms` にすれば、その時刻までの押下は届き切っており、生きている走行と再生が一致する（一時停止の境目の ±1 秒は残る・下の「読んでいない」）。

### スレッドと状態の持ち方

| 案 | 中身 | 判定 |
|---|---|---|
| A 専用スレッド（採る） | 今のプローブのスレッド（`lib.rs:5708-5870`）と同じ場所で、段 1 なら代わりに `s1-driver` スレッドを起こす。1 秒の sleep で回す。`AppHandle` を持つので画面へ emit できる | 採る。プローブのスレッドが分けられている理由（「1Hz Analysis Thread はレイテンシ要件があり AppHandle も持たない」`lib.rs:5696-5698`）がそのまま当てはまる。印の無い O1 では起こさないので、分析スレッドの中身は押下を 1 本流す以外に変わらない |
| B 分析スレッドの中 | 押下・`UtcOffsetCache`・電源の受け口（`lib.rs:4348-4372`）が手元にある | 採らない。tick が `recv_timeout` の 1Hz マークと打鍵の到着に揺れる（`lib.rs:4420-4426`）。`AppHandle` が無く、画面への出し入れのために別の口が要る。コマンド（回答）からカードを閉じるには結局ロックで共有する必要があり、分析スレッドのロック待ちが特徴量の 1Hz を遅らせうる |
| C 今のプローブのスレッドを作り替える | `ProbeScheduler` を `Arbiter` に置き換える | 採らない。印の無い O1・通常運用・G1 の経路（`SESSION_START_MS` 待ち・`GSE_DISABLE_PROBES`）と同じ関数に段 1 の分岐が入り、「印の無い走行は変わらない」を本文で示しにくい |

状態の持ち方:

- `static S1_DRIVER: Mutex<Option<S1Driver>>`（`lib.rs`）。`None` = 段 1 でない・同意が無い・取り消した（行は 0）。駆動スレッドが tick ごとに短く取り、コマンド（回答・閉じる・同意・取り消し・終了）も同じロックで取る。
- ロックの順序は **`S1_DRIVER` → `LogState`**（`LogState` の中では `try_send` だけ）。`o1_rotate` は `O1_ROTATE → LogState → DECLARED_TASK_KIND`（`lib.rs:202-215`）なので、**`S1_DRIVER` を持ったまま `o1_rotate` を呼ばない**（同意の時のローテートはロックの外で先に済ませる・下の「コマンド」）。
- `S1Driver`（`s1_driver.rs`・純粋）が持つもの: `Option<Arbiter>`・`frame_gen`（最後に枠を作った `S1_FRAME_GEN`）・`probe: Option<ProbeCardState>`（`probe_id`・`stratum`・`scheduled_ts`・窓・出した時刻）・`day: Option<DayCardState>`（`card_id`・`target_day`・`trigger`・`delayed`・`in_window`・`shown_ts`・`quit_flow`）・押下と遷移の待ち行列・前の tick の壁時計・`app_started` を出したか・一時停止の前の値・電源の世代。
- 調停器は 1 本目の `Arbiter::new(config, frame_seed, anchor_ms, day)`（`probe_arbiter.rs:903`）。ローテートで枠を作り直すとき、日の問いの状態（`showing`・`next_card_id`）を引き継がないと開いているカードの通し番号がぶつかる（`DayQuestion::new` は `next_card_id: 1`・`probe_arbiter.rs:611-625`）。→ 純粋な小さな追加 `Arbiter::into_day_question(self) -> DayQuestion` を `probe_arbiter.rs` に足し、新しい `Arbiter::new(.., day)` に渡す。

### 入力の集め方

| 入力 | 出どころ | 口 | 備考 |
|---|---|---|---|
| 押下 | 分析スレッドの `out.key`（`is_press`）＝特徴量に流れるキーだけ（`lib.rs:4461-4467`） | `S1_PRESS_TX: OnceLock<Sender<u64>>`（bounded 1024・`try_send`・溢れは `AtomicU64` で数えて warn） | 段 1 のときだけ送る（`if s1::is_s1()`）。印の無い O1 では 1 命令も増えない分岐にする。昇順は到着順で保たれるが、駆動役で `sort_unstable` してから渡す |
| フォーカスの遷移 | observe のドレイン（`lib.rs:5017-5040`） | `S1_FOCUS_TX`（bounded 256） | `eh3_focus_filter` を `is_eh3() \|\| is_s1()` に広げ（`lib.rs:5019`）、`allowed` のときだけ行と同じ時刻を送る。行に残る遷移と検出器の入力が一致する（計画 §1） |
| 一時停止 | `set_recording_paused`（`lib.rs:2125-2148`） | (a) **止める方向**は、コマンドが `set_paused(true)` の **前** に `s1_on_pause_requested(now)` を直接呼ぶ。(b) **再開**は駆動スレッドが `recording::is_paused()` の偽への変化で知る | (a) で画面をすぐ伏せ、`DayQuestion::on_pause(config, day, minute)`（`probe_arbiter.rs:828`）をその時刻の現地の日と分で呼ぶ。1 秒以内の止める→再開は (b) が見落とすので、`recording.rs` に変化の世代 `PAUSE_EPOCH: AtomicU64` を足し、世代が進んでいて今が再開なら `resumed = true` にする |
| 電源 | `power::start`（`power.rs:37-42`・2 回目は黙って何もしない） | **受け口を 1 本にまとめる** `start_power_hub(need_portrait, need_s1)` を `run()` で 1 回だけ呼ぶ。中継スレッドが `PowerEvent` を受け、肖像には今と同じ bounded(8) で転送し、段 1 には `S1_POWER_RESUMED_GEN: AtomicU64` を進める | 今は肖像があるときだけ購読している（`lib.rs:4369-4373`）。段 1 と EH3 は同時に立たない（`s1::resolve_with_eh3`・`lib.rs:4191-4193`）が、「同時に立たないから大丈夫」に頼らない形にする。予備として、tick の壁時計の間隔が 30 秒以上空いたら復帰とみなす（肖像の `GAP_AS_RESUME_MS = 30_000`・`lib.rs:867`・`lib.rs:1016-1018` と同じ作法） |
| 現地の日と分 | 駆動スレッドが自分の `UtcOffsetCache`（`lib.rs:632-657`）を持つ | 純関数 `s1_driver::local_clock(now_ms, offset_secs) -> (i64, u32)` = (`eh3::local_day`・`eh3::local_minute_of_day`)（`eh3.rs:353/359`） | `local_day` と `local_minute` は同じ `now_ms`（遅らせた時刻）から求める（`local_at` の注意・`probe_arbiter.rs:871-872`）。OS の時刻帯は `lib.rs` で引き、`s1_driver.rs` には秒数だけ渡す（技術的制約 11） |
| 起動 | 駆動役がこの走行で最初に調停器を回す tick | `app_started = true` を 1 回だけ | ローテートで枠を作り直しても立てない |

1 tick（駆動スレッド）:

1. `wall = epoch_ms()`、`now = wall - S1_TICK_LAG_MS`。`S1_FRAME_GEN` と同意を見る（下の「枠」）。調停器が無ければ待ち行列を捨てて次へ。
2. チャネルを全部ドレインし、`now` 以下の押下・遷移だけを今回の `TickInput` に渡す（残りは次の tick）。一時停止の間は空で渡す（調停器は見ない・`probe_arbiter.rs:303-304`）。
3. `TickInput { now_ms: now, key_presses_ms, focus_transitions_ms, paused, resumed, open_card, local_day, local_minute, app_started, power_resumed }` を作り、`Arbiter::tick` を呼ぶ。`open_card` は `S1Driver::open_card_for_arbiter()`（下）。
4. 返った `Action` 列を `S1Driver::apply` で `Effect` 列に変え、ロックを放してから `lib.rs` が実行する（行の送信・emit・状態の保存）。

### 枠（`probe_frame`）と同意

- 起点は `O1_LOG_OPENED_MS`（`lib.rs:200`）。`o1_rotate` が `EH3_REEMIT_GEN` を進める隣（`lib.rs:2028`）で `S1_FRAME_GEN` も進める。
- 駆動役は「段 1 で、同意の印があり（`submission::s1_probe_consent_acknowledged()`・`submission.rs:349`）、`O1_LOG_OPENED_MS != 0`」のときだけ調停器を持つ。世代が変わったら `frame_seed_from_entropy(rand::random())` で新しい枠を作り、`probe_frame` を `t = anchor_ms`（判断 1）で 1 行書く。日の問いの状態は `into_day_question` で引き継ぐ。
- 日の状態は新規の `s1_day_state.rs`: `~/.gse/s1_day_state.json` を `eh3::save_ledger`（一時ファイル → 置き換え → `sync_all`・`eh3.rs:498`）の作法で読み書き。壊れていたら `DayQuestion::disabled()`（`probe_arbiter.rs:627`）。保存は tick の後、`DayState` が前回保存から変わったときだけ（`DayState` は `PartialEq`・`Clone` を持つ）。NDJSON・提出物には入れない。
- 同意の行の書き方: `probe_frame` は区間の削除で消えない（計画の判断 8）ので、時刻は `anchor_ms` にそろえ、押した時刻は印のファイル（`acknowledged_at`）にだけ残る（判断 1）。

### Action から行と画面への写し方

| Action | 行（`lib.rs` が組む） | 画面 | 駆動役の状態 |
|---|---|---|---|
| `FireProbe { stratum, scheduled_ts }` | `probe_assignment`（`probe_id` は `ProbeId::generate`・`probe_scheduler.rs:117`、`session_elapsed_ms = scheduled_ts - anchor_ms`、`stratum` を 3 値で） | プローブのカードを出す（日の問いが開いていれば伏せる） | `probe = Some(..)`。窓は `[max(scheduled_ts - 30_000, anchor_ms), scheduled_ts]`（文「直前の30秒」・`ProbeCard.tsx:181`） |
| `Suppress { stratum, candidate_ts, reason }` | `probe_suppressed`（`t = now`・`candidate_ts`・`stratum`・`reason`） | なし | なし |
| `SupersedeOpenStrat` | 開いている層化のカードについて `realtime_label` と `activity_label` を `skip_reason = superseded` で 2 行（同じ `probe_id`）。**組むのは `lib.rs` の `emit_s1_superseded`**（6 択の門を通す・下） | 層化のカードを下ろす（同じ tick の `FireProbe` が無作為のカードを出す） | `probe` を差し替え。`Action` は `SupersedeOpenStrat` → `FireProbe` の順で来る（`probe_arbiter.rs:1023-1028`）ので、`apply` はこの順に処理する |
| `ShowDayQuestion { card_id, target_day, trigger, delayed, in_window }` | なし（行は閉じた時に 1 行） | 日の問いのカードを出す（プローブが開いていれば伏せたまま持つ。調停器は開いているカードがあると出さない作りだが、守りとして） | `day = Some(DayCardState { card_id, .., in_window, shown_ts: now })` |
| `CloseDayQuestion { card_id, target_day, closed_by }` | 駆動役が持つカードと `card_id` が合えば `day_question` を 1 行（`closed_by = day_end`・`answered = false`・`in_eod_window = 持っていた in_window`）。`card_id = None` で駆動役が日の問いを持っていれば、それを閉じる | 日の問いのカードを下ろす | `day = None`。**`on_closed` は呼ばない**（調停器は覚えを捨て済み・`probe_arbiter.rs:340-343`） |

- `in_window` → `DayQuestionRow::in_eod_window` にそのまま写す。現地の分は持たない・書かない（引き継ぎ §2 の 5・1 本目の判断 9・`logger.rs:862-865`）。
- `day_question` の `t` は閉じた時刻、`shown_ts` は最初に出した時刻、`latency_ms` は画面が測る「最後に見えるようになった時刻から最初の操作まで」（伏せていた時間を入れない）、`duration_ms` は最初の操作から送信まで。`items_version = DAY_QUESTION_ITEMS_VERSION`（`logger.rs:887`）。

`open_card_for_arbiter()`（引き継ぎ §2 の 8 の要）:

```text
match (probe, day) {
  (Some(p), _)       => Some(if p.stratum == Random { Random } else { Strat }),  // 日の問いを伏せている間も Random/Strat
  (None, Some(d))    => Some(Day { target_day: d.target_day }),
  (None, None)       => None,
}
```

- 画面の実際と一致させるため、画面に何を出すかも同じ関数から導く（`visible_card() = probe があれば probe、無ければ day`）。伏せる・出し直すの指示は調停器から来ない（引き継ぎ §2 の 8）が、この形なら **無作為のカードが閉じた瞬間に `visible_card()` が日の問いに戻る** ので、出し直しの経路を別に書く必要が無い。
- 日の問いを閉じたら（回答・閉じる・終了・待ちの切れ）、`day_question_mut().on_closed(card_id, target_day, answered)` を呼ぶ（`probe_arbiter.rs:853`）。呼ぶ場所は `S1Driver::close_day(card_id, closed_by, answer)` の 1 か所に集める。
- 一時停止の間は画面に何も出さない（`visible_card()` は `paused` なら `None`）が、`open_card_for_arbiter()` は上のまま渡す（調停器は一時停止の間、画面の値を信じない・`probe_arbiter.rs:667-669`）。

一時停止とプローブのカード: 止めた後は行を書けない（`recording::is_writable_while_paused`）。止める前に「未回答」を書くと本人の `dismissed` と混ざる。→ **止めた時点で開いていたプローブのカードは行を書かずに下ろす**（`probe_assignment` はあり・ラベル行は無い・直後に `recording_pause` 行がある、という並びで 3 本目の `--probes` が「一時停止で下ろした」と分類できる）。日の問いのカードは伏せたまま持ち、再開で出し直す。止めている間に日の切れ目を越えて `CloseDayQuestion` が来たら、行は書けないので落とし（`tracing::info!`）、拾い直しは調停器の状態（`answered = false`）が引き受ける。

### コマンド

| コマンド | 引数 | 中身 |
|---|---|---|
| `get_s1_mode` | なし | `Option<String>`（`s1::mode()` の `as_str`）。`get_o1_mode` と同じ形 |
| `get_s1_consent` | なし | 同意の印があるか（登録の画面の表示用） |
| `acknowledge_s1_probe_consent` | なし | 段 1 でなければ `Err`。`submission::write_s1_probe_consent(now)` → **ロックの外で** `o1_rotate(.., KeepCurrent, "s1 consent")`（判断 6・一時停止の間は `o1_rotate` が `Err` を返す・`lib.rs:1985-1990` → そのまま本人に返す）→ overlay を `show()`。駆動役は次の tick で世代の変化を見て枠を作る |
| `revoke_s1_probe_consent` | なし | `S1_DRIVER` を取り、開いているカードを**行を書かずに**下ろす（ハイブリッドで v1 から: 判断 2 の「以後の行は 0」・本人の `dismissed` と混ぜない。一時停止と終了でプローブを行なしで下ろすのと同じ理由）→ 印のファイルを消す（`submission.rs` に `remove_s1_probe_consent` を足す）→ 調停器を捨てる（日の問いの状態は保存してから）→ 画面の状態を空で送る |
| `record_probe_response` | `probe_id`・`q1_friction`・`q2_progress`・`category`・`latency_ms` | 駆動役が持つ `probe.probe_id` と一致するときだけ受ける（古いカード・二重送信を弾く）。窓は駆動役が持つ値を使い、UI からは受けない。6 択の門を通してから `realtime_label_answered` と `activity_label_answered` を 2 行。送れたらカードを閉じる |
| `record_probe_skip` | `probe_id`・`skip_reason`（`dont_remember`・`dismissed` だけ）・`latency_ms` | 同上で `realtime_label_skipped` と `activity_label_skipped`。`superseded` と `none` は拒む（`record_realtime_skip` と同じ・`lib.rs:3361-3364`）。`superseded` は駆動スレッドの `emit_s1_superseded` だけが書く（引き継ぎ §2 の 6） |
| `record_day_question` | `card_id`・`motivation: Option<u8>`（1..5）・`latency_ms`・`duration_ms` | 駆動役の `day.card_id` と一致するときだけ。`motivation` があれば `closed_by = answer`、無ければ `dismiss`（終了の流れの中なら `quit`）。行を書いてから `close_day` |
| `get_s1_card` | なし | いま出すべきカードの状態（`s1_card_state` と同じ形）。画面の取り直し用 |

6 択の門（引き継ぎ §2 の 3）:

```rust
// lib.rs の 3 か所（record_probe_response・record_probe_skip・emit_s1_superseded）だけ
let Some(consent) = crate::o1::activity_label_allowed(
    crate::s1::is_s1(),
    crate::submission::s1_probe_consent_acknowledged(),
) else { return Err(..) /* 駆動スレッドでは warn して行を書かない */ };
```

- `realtime_label` も同じ `consent` を得てから書く（O1 の `label_row_allowed` は O1 でラベル行を拒む・`lib.rs:3298`。段 1 のコマンドはそれを迂回するので、迂回の条件を 6 択の門と同じにする）。
- 既存の `record_realtime_answer`・`record_realtime_skip` は変えない（O1 では今のまま拒む）。

### overlay の表示

- 今は overlay を `start_session` の中でしか `show()` しない（計画 §4・`lib.rs:5904-5914` の注記）。段 1 では、setup の NSPanel 化（`lib.rs:5975-5980`）の **後** に「`s1::is_s1() && s1_probe_consent_acknowledged()` なら、窓を画面外・1×1 に置いてから `show()`」を 1 か所足す（ハイブリッドで v1 から: Overlay.tsx の退避の effect が走る前に、透明の窓が Windows で一瞬背後のクリックを奪うのを防ぐ）。同意のコマンドも同じ関数を呼ぶ。同意を押したときは `acknowledge_s1_probe_consent` が `show()` する。`hide()` は使わない（webview の JS が休眠する・`Overlay.tsx:264-274`）。何も出さない間は Overlay.tsx の退避（画面外 1x1・クリック透過・`Overlay.tsx:271-293`）に任せる。
- 休眠で取りこぼしても、カードは backend の状態なので、画面は `get_s1_card` を (a) マウント時 (b) `s1_card_state` を受けた時 (c) 窓の `focus`・`visibilitychange` で取り直す。差分のイベントを落としても状態は戻る。
- 段 1 の overlay にも `set_content_protected(true)` を掛ける（EH3 と同じ受動的除外・`lib.rs:5933-5937`）。6 択のカードが画面共有に映ると、研究に参加していることが共有の相手に見えるため。

### トレイの終了の補助

- `tray.rs:192-196` の終了を `crate::request_quit(app)` に替える。段 1 でなければ今の `shutdown_and_exit` をそのまま呼ぶ（印の無い O1 は変わらない）。
- 段 1: `S1_DRIVER` を取り、`day_question_mut().on_quit(config, day, minute, open_card_for_arbiter())`（`probe_arbiter.rs:835`）。`None` なら終了へ。`Some(ShowDayQuestion)` なら日の問いを「答えて終了／答えずに終了」の形（`quit_flow = true`）で出し、待ち合わせのスレッドを起こす: `EOD_QUIT_WAIT_MS = 60_000`（仮・`s1_driver.rs` の定数）待つか、`record_day_question`（答えた・答えずに終了）を受けたら終了へ。待ちが切れたら `closed_by = quit`・`answered = false` で 1 行書いて終了へ。
- 待っている間にもう一度「GSE を終了」を押したら、待たずに `closed_by = quit` で書いて終了する（`claim_shutdown` はまだ取っていないので 2 回目で弾かれない）。
- 終了の順序: `shutdown` は `End` を先に送る（`lib.rs:3902-3906`）。その後は行が書けない。→ `shutdown` の冒頭（`claim_shutdown` の直後・`close_normal_invitation` の隣）で `s1_finish_before_end(&log)` を同期で呼ぶ: 開いている日の問いを `closed_by = quit` で書く、`on_closed(.., false)`、日の状態を保存、調停器を捨てる。プローブのカードは行を書かずに下ろす（終了を本人の `dismissed` と混ぜない・Phase1 で終了時にカードが消えたときと同じ扱い）。`try_send` だけなのでメインのスレッドから呼んでも塞がない。× で閉じる（`lib.rs:6008-6015`）・`quit_app` も同じ `shutdown` を通るので、補助（問いを出す）は無くても日の問いの行は残る。

### 画面

- `App.tsx`: `get_s1_mode` を起動時に 1 回（`get_o1_mode` と同じ形・`App.tsx:329-343`）。
- `RecordingControls.tsx`（O1 の登録の画面・`get_o1_enrollment`・`acknowledge_o1_enrollment` の隣・`RecordingControls.tsx:184-233`）に段 1 の項目: 同意の前は説明と「問いに同意する」、同意の後は「問いへの同意を取り消す」（判断 2）。段 1 でなければ何も出さない。
- `Overlay.tsx`: 段 1 のときは `S1CardHost`（新規・`src/components/S1CardHost.tsx`）を出し、今の `ProbeCard` の `probe_triggered` の購読の経路は使わない（段 1 では今のプローブのスレッドが起きないので、そもそも来ない）。`probeActive` 相当の「箱を出すか」は `S1CardHost` の状態から決める。プローブのカードと日の問いのカードは排他（backend が 1 つしか「見える」と言わない）。
- `ProbeCard.tsx`: 描画と送信を分け、段 1 では親から `card` を props で受ける形（`activity: true` で 3 問を 1 枚・6 択・自由記述なし・`stratum` は見せない）。送信は `record_probe_response`／`record_probe_skip`。送れなかったらカードを残す（今の作法・`ProbeCard.tsx:96-113`）。
- `DayQuestionCard.tsx`（新規）: 文は判断 5（「今日の作業にどのくらい熱意を持てましたか」・拾い直しは「昨日の作業に」・1「まったく」〜5「とても」）。`quit_flow` のときはボタンを「答えて終了」「答えずに終了」に。
- `probeTypes.ts`: `S1CardState`（`{ kind: "none" } | { kind: "probe", .. } | { kind: "day", .. }`）・`ActivityCategory`・`DayTrigger` を足す。`any` を使わない。

### capabilities とログ

- `capabilities.rs`: `fn s1_line_types(s1: bool) -> Vec<&'static str>`（真なら `["activity_label","day_question","probe_frame","probe_suppressed"]`）を `eh3_line_types` の型（`capabilities.rs:288-294`）で足し、`config_gated()` で `v.extend(s1_line_types(crate::s1::is_s1()))`。4 行種を `emitterless` から外す（`capabilities.rs:494-523`）。検査 `activity_label_has_no_emitter_until_it_is_wired`（`capabilities.rs:554`）を消し（1 本目の判断 2・ADR-031 D4 の手順）、`s1_line_types_are_declared_only_in_s1` を足す: 偽なら空、真なら 4 つ、`lib.rs` に `LogEntry::ProbeFrame {`・`LogEntry::ProbeSuppressed {`・`LogEntry::DayQuestion(`・`activity_label_answered(` があること、writer が `logger.rs` にあること。同意が無い走行は 4 行種が 0 行になるが、`config_gated` の読み（0 行は判定不能）と合う。
- 起動のログ（引き継ぎ §2 の 2・`lib.rs:4194-4202`）を「STAGE 1 MODE ENABLED: probes and the end-of-day question are shown once the participant consents to the questions (consent={}). Nudge and invitations stay OFF.」に改める。同意の有無も 1 語だけ添える。
- 段 1 のプローブのスレッドの起動のログ: `GSE_DISABLE_PROBES` が立っていたら「段 1 では見ない」と warn を 1 行（計画 §1）。
- 今のプローブのスレッドを止める条件に `|| crate::s1::is_s1()` を足す（`lib.rs:5728`）。止めた理由のログに `s1=` を足す。

### O1 の配布の門（判断 4）

- `check-o1-release-readiness.sh` の 6 択の節（`:115-145`）を、送出元がある版について次の形に直す:
  1. `lib.rs` のコメントでない行の `activity_label_allowed(` の呼び出しを全部拾い、どれも第 1 引数が `crate::s1::is_s1()` で、`o1::is_o1()` を含まないこと。満たせば「6 択は段 1 だけの送出元」として **O1 の ESM 追補の承認の印を求めない**。満たさなければ今と同じく承認の印を求める（`o1` を渡す呼び出しが入ったら赤に戻る）。
  2. 送出元が門を通っていること（今の検査をそのまま）。
  3. O1 の配布物に `s1.mode` が無いこと（配布物の置き場所の見方はこのスクリプトの他の節にならう）。
- `--selftest` に対照を足す: 陽性（`is_s1()` だけ → 緑・承認の印なし）、陰性（`is_o1()` を渡す行を混ぜる → 承認の印が無ければ赤）、陰性（配布物に `s1.mode` → 赤）。⚠️ 対照の文字列は実行時の連結で作り、検査対象のファイルに書かない（自己参照で空回りした先例がある）。

## 変更対象ファイル

| ファイル | 種別 | 変更 |
|---|---|---|
| `src-tauri/src/s1_driver.rs` | 新規 | `S1Driver`（カードの状態・`open_card_for_arbiter`・`visible_card`・`apply(Action) -> Vec<Effect>`・`close_day`・`on_pause_requested`・待ち行列の遅れの切り出し）、`local_clock`、`S1_TICK_LAG_MS`・`EOD_QUIT_WAIT_MS`、検査。Tauri・logger・OS API を持たない |
| `src-tauri/src/s1_day_state.rs` | 新規 | `~/.gse/s1_day_state.json` の読み書き（`eh3::save_ledger` の作法・壊れていたら `Broken`） |
| `src-tauri/src/analysis/probe_arbiter.rs` | 修正（小） | `Arbiter::into_day_question(self) -> DayQuestion`。判定の規則は変えないので `ARBITER_VERSION` は据え置き |
| `src-tauri/src/lib.rs` | 修正 | `S1_DRIVER`・`S1_FRAME_GEN`・`S1_PRESS_TX`・`S1_FOCUS_TX`・`S1_POWER_RESUMED_GEN`、`o1_rotate` で世代を進める、分析スレッドから押下を送る、observe のフィルタを段 1 にも、電源の受け口のまとめ、駆動スレッド、`emit_s1_*`（行の組み立て・6 択の門）、コマンド 8 つと `invoke_handler`、setup の overlay の `show()`、`shutdown` の `s1_finish_before_end`、`request_quit`、起動のログ、今のプローブのスレッドの停止条件、本文の検査 |
| `src-tauri/src/recording.rs` | 修正（小） | `PAUSE_EPOCH` を `set_paused` の変化で進める（依存を持たない葉のまま） |
| `src-tauri/src/submission.rs` | 修正（小） | `remove_s1_probe_consent`（取り消し） |
| `src-tauri/src/tray.rs` | 修正（小） | 終了を `crate::request_quit` に |
| `src-tauri/src/capabilities.rs` | 修正 | `s1_line_types`・`emitterless` から 4 行種を外す・検査の入れ替え |
| `src-tauri/src/main.rs` または `lib.rs` の `mod` 宣言 | 修正 | `mod s1_driver; mod s1_day_state;` |
| `scripts/check-o1-release-readiness.sh` | 修正 | 判断 4 の 3 点と selftest の対照 |
| `src/components/S1CardHost.tsx` | 新規 | 状態の受け取り・取り直し・2 枚の排他 |
| `src/components/DayQuestionCard.tsx` | 新規 | 日の問い・終了の形 |
| `src/components/ProbeCard.tsx` | 修正 | 描画を props で受ける形・段 1 の 6 択と送信先 |
| `src/components/Overlay.tsx` | 修正 | 段 1 で `S1CardHost` を出す・箱の大きさの決め方に段 1 のカードを足す |
| `src/components/RecordingControls.tsx` | 修正 | 同意と取り消しの項目 |
| `src/App.tsx` | 修正 | `get_s1_mode` |
| `src/probeTypes.ts` | 修正 | 型の追加 |

schema（`schema_dto.rs`・`schema/current.json`）は変えない（行種は 1 本目で入っている）。`emit_schema` の byte-equal は確かめる。

## 既存パターンとの整合

- 専用スレッドで 1Hz・`AppHandle` で emit・`try_send` だけ: 今のプローブのスレッド（`lib.rs:5743-5866`）と同じ。
- 層の判定と「印が無ければ 1 バイトも変わらない」: EH3 の作り（`eh3_line_types`・`eh3_focus_filter`・`EH3_REEMIT_GEN`）をそのままなぞる。印の無い O1 で増えるのは `if s1::is_s1()` の分岐だけ。
- 状態ファイルの書き方: `eh3::save_ledger`（`eh3.rs:498-516`）・`write_s1_probe_consent_at`（`submission.rs:376-`）と同じ一時ファイル → 置き換え。
- 送信できなかったらカードを残す: `ProbeCard.tsx:96-113` の作法。
- 型による門: `EsmConsent`（`o1.rs:274-275`）からしか 6 択の行を作れない。加えて本文の検査と配布の門の二重の網（`o1.rs:270-273` が挙げる「直接構築の抜け道」への対処）。
- 「止める方向の行は `set_paused` の前に」: `set_recording_paused` の作法（`lib.rs:2121-2124`）に、段 1 の画面を伏せる呼び出しを同じ位置で足す。
- `analysis/` に OS API を入れない: 時刻帯は `lib.rs` の `UtcOffsetCache`、純粋な駆動役はクレート直下（`g1.rs`・`o1.rs` と同じ置き方）。

## テスト戦略

### Rust の単体（`s1_driver.rs`・`s1_day_state.rs`・`probe_arbiter.rs`）

- `local_clock`: JST（+32400）と UTC（0）の両方で、4:00 の前後・0:00 の前後・17:00（時間帯の始まり）の前後の `(day, minute)` を固定値で（引き継ぎ §2 の 4）。同じ瞬間でも JST と UTC で日が割れる例を 1 つ入れる。
- 伏せと出し直し（§2 の 8）: 日の問いを出す → 無作為が発火 → `visible_card` が probe・`open_card_for_arbiter` が `Random` → 回答で probe を閉じる → `visible_card` が day に戻り、`on_closed` は呼ばれていない。続けて日の問いに答える → `on_closed(card_id, target_day, true)` が 1 回だけ。
- `CloseDayQuestion` の `card_id` 一致・不一致・`None`（駆動役だけが持っていた）で、行の `Effect` が 0 か 1。`on_closed` を呼ばない。
- `SupersedeOpenStrat` → `FireProbe` の順で、superseded の `Effect` が古い `probe_id` を持ち、新しいカードが無作為になる。
- 遅れの切り出し: `now` より後の押下は次の tick に残り、昇順で渡る。一時停止の間は空。
- `PAUSE_EPOCH` が 2 進んで今が再開なら、`resumed = true` の tick が 1 回だけ。
- ローテート: 枠を作り直しても `into_day_question` で `card_id` が続き番号になる（`DayQuestion::new` で作ると 1 に戻ることを陰性の対照に）。
- `in_window` が `in_eod_window` に写り、行の `Effect` に現地の分が無い。
- `s1_day_state`: 往復・壊れたファイルで `Broken`・書きかけ（tmp）を残さない。
- 一時停止で下ろしたプローブのカードに行の `Effect` が無い／取り消しでは `dismissed` が出る。

### 本文の検査（`include_str!` で `lib.rs`・`tray.rs` を読む）

- `activity_label_allowed(` の呼び出しはすべて `crate::s1::is_s1()` を第 1 引数に持ち、`lib.rs` のどこにも `activity_label_allowed(crate::o1::is_o1()` が無い（§2 の 3）。
- `activity_label_answered(`・`activity_label_skipped(` を含む関数は `record_probe_response`・`record_probe_skip`・`emit_s1_superseded` の 3 つだけ。
- `power::start(` が `lib.rs` に 1 回だけ（受け口のまとめ）。
- `record_probe_skip` が `Superseded` を拒む。
- 今のプローブのスレッドの停止条件に `s1::is_s1()` が入っている。
- `capabilities`: `s1_line_types_are_declared_only_in_s1`、`config_gated_line_types_are_not_declared_unconditional`（既存）が緑。
- 印の無い O1: 既存の `logger::tests::o1_meta_unchanged_without_s1_marker` と、既存のゴールデン（`gse-replay --snapshot`）が byte-equal。
- `check-o1-release-readiness.sh --selftest` の陽性・陰性。

### 画面の実機の確かめ（macOS は自分で AX と画面の取得、Windows は CI と研究者の手）

1. 同意の前: overlay は `show()` されず、カードは出ない（`get_s1_card` が `none`）。
2. 同意を押す: ローテートで新しいファイルができ、先頭近くに `probe_frame`（`t = anchor_ms`）。
3. 定数を短くした研究者デバッグの起動（`GSE_DEBUG` の門の中だけ）でプローブを出す: カードが見える・押せる（AX で押下）・背後のアプリのクリックを奪わない（カードの外をクリックして背後が反応する）。
4. 日の問いを出した状態で無作為を出す: 日の問いが消え、無作為に答えると日の問いが戻る。
5. 一時停止の間は何も出ない・再開で日の問いが戻る。
6. トレイの終了 → 日の問いの終了の形 → 「答えずに終了」で 60 秒以内に終わる・何も押さなくても 60 秒で終わる。NDJSON の最後に `day_question`（`closed_by = quit`）と `session_end` がこの順。
7. 取り消し: カードが消え、以後 `probe_*` の行が 0。
8. NDJSON は 8〜12 秒待ってから数える。

## ロールバック

- 1 本の PR で入れる。戻すときは revert 1 回。印 `s1.mode` が無い走行は分岐の外なので、戻しても戻さなくても O1 の記録は同じ。
- 実機で問題が出たら、配布の前なら `s1.mode` を外すだけで素の O1 に戻る（`s1::resolve`）。本人の試しの最中なら「問いへの同意を取り消す」で行が止まる。
- `~/.gse/s1_day_state.json` と `~/.gse/s1_probe_consent` は消してよい（日の問いの状態は失われ、拾い直しが 1 回分出ないだけ）。

## 読んでいない・確かめていない

- `design.md`・`design-v1.md` は禁止のとおり読んでいない。比べるのは研究者と /reimagine の側。
- `probe_arbiter.rs` は契約の doc・`judge`・`DayQuestion::tick`・`Arbiter::tick` だけ読んだ。`StrataDetector::judge` が日の問いのカードが開いているときに `card_open` で止めるかは読んでいない（`apply` の守りで吸収する前提）。
- `hook-constraints`・`architecture-rules`・`data-privacy` の各 SKILL.md、`docs/agent-shared.md` 以外の規約は、締切のため読んでいない（system の要約で代えた）。
- `Overlay.tsx` はマウント直後に退避の effect が走るか（初回の `visible = false` で画面外 1x1 に行くか）を本文で追い切っていない。O1 で今まで一度も `show()` していない窓を `show()` した直後に、透明の全画面が一瞬でも背後のクリックを奪わないかは実機で見る（memory の overlay のクリック奪取の先例）。
- `recording::is_writable_while_paused` が新しい 3 行種を落とすことは計画 §4 の記述（`KNOWN_LINE_TYPES` から導く）に頼った。
- `check-o1-release-readiness.sh` の配布物の置き場所の見方（3 の `s1.mode` の検査）は他の節を読んでいない。
- `S1_TICK_LAG_MS = 2000` で押下が届き切るかは、分析スレッドの `recv_timeout` の遅れを測っていない。一時停止の境目では、画面の都合で `set_paused` の時刻にすぐ伏せる一方、調停器は遅れた時刻で `paused` を受けるので、境目の ±2 秒は再生と一致しない（3 本目で `recording_pause` 行の時刻を使って合わせるか決める）。
- 開いているプローブのカードがローテート（日次・宣言）をまたぐと、`probe_assignment` は古いファイル、ラベル行は新しいファイルに入る。3 本目の `--probes` がファイルをまたいで `probe_id` で結ぶ前提にした（確かめていない）。
- Windows の電源の通知（`power_windows.rs`）と、受け口をまとめたときの肖像の挙動は CI と研究者の手でしか確かめられない。
- 同意の後に overlay を `show()` するのをコマンドのスレッドから行ってよいか（Windows の `WebviewWindow` の操作のスレッド）は確かめていない。だめなら `run_on_main_thread` に包む。

## 設計判断の履歴

- 実行回数: 1 回目
- 採用: ハイブリッド（v2 を土台に、v1 から 2 点: 取り消しは行を書かずに下ろす・overlay は画面外 1×1 に置いてから `show()`）
- 根拠: 研究者が推奨どおり選んだ（2026-11-07）。v2 は再生との一致（2 秒の遅れ）・一時停止の取りこぼし・どの終了経路でも日の問いの行を `End` の前に書く点で、v1 が外していた穴を塞ぐ。比べは `design-comparison.md`。v1 は `design-v1.md`。

## 実装中に変わった点と既知の限界（2026-11-07）

- `App.tsx` は変えなかった。段 1 の判定（`get_s1_mode`）は `Overlay.tsx` と `S1ConsentPanel.tsx` がそれぞれ読む。今の `ProbeCard.tsx` は変えず、段 1 のカードは `S1ProbeCard.tsx` に分けた（通常のモードの経路を 1 バイトも変えないため）。
- 確かめ用の口（`debug_force_s1_probe`・`debug_force_s1_day_question`・`GSE_DEBUG=1` の下だけ）と、Dashboard の debugView のボタンを足した。確かめ用のカードは調停器の外で出し、日の問いの状態を変えない。
- 既知の限界: 一時停止の間に閉じた日の問いの行は書けない（診断ログに残す・翌日の拾い直しの対象）。一時停止の境目の ±2 秒は再生と一致しない。プローブのカードがローテートをまたぐと `probe_assignment` は古いファイル、ラベルの行は新しいファイルに入る（3 本目の `--probes` が `probe_id` でファイルをまたいで結ぶ）。状態ファイルの書き込みはロックの外で、まれに古い状態が後に書かれうる。画面への状態の通知は順が逆転しうる（5 秒の取り直しで戻る）。終了の待ちの間に無作為の問いが出ると、日の問いは伏せられたまま 60 秒で終わる（行は `quit`）。
