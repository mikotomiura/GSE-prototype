//! 段 1 の駆動役の純粋な部分（カードの状態と、調停器の `Action` から出来事 `Effect` への写し）。
//!
//! ★ Tauri・logger・OS API・IO を持たない。`lib.rs` の駆動スレッドとコマンドが、
//!   ここが返す [`Effect`] を行（`LogEntry`）と画面（emit）と状態ファイルに変える。
//!   行の組み立てを `lib.rs` に残すのは、`capabilities` の送出元の検査と O1 の配布の門
//!   （`scripts/check-o1-release-readiness.sh`）が `lib.rs` を見るため（本タスクの decisions 判断 4）。
//!
//! 設計の一次は `.steering/20261107-gse-m5-s1-driver-ui/design.md`（v2 を土台にしたハイブリッド）。
//!
//! ## カードの真実は backend が持つ
//!
//! 画面に出すカードは [`S1Driver::visible_card`] で決まり、調停器に渡す `open_card` は
//! [`S1Driver::open_card_for_arbiter`] で決まる。2 つは同じ状態（プローブのカード・日の問いのカード）から
//! 導くので、無作為の問いが出たとき日の問いを伏せ、無作為が閉じたら出し直す（引き継ぎ §2 の 8）は、
//! 別の経路を書かずに成り立つ。画面は伏せていることを知らない。
//!
//! ## 時刻を 2 秒遅らせる（[`S1_TICK_LAG_MS`]）
//!
//! 押下とフォーカスの遷移は別のスレッドから遅れて届く。壁時計のまま判定すると、候補の直前の押下が
//! まだ届いていない tick ができ、記録の `key` 行から同じ調停器を回す再生（3 本目の `gse-replay --probes`）と
//! 結果が割れる。調停器には壁時計から 2 秒引いた時刻を渡し、その時刻までの入力だけを渡す。

use serde::Serialize;

use crate::analysis::probe_arbiter::{
    Action, Arbiter, ArbiterConfig, DayClosedBy, DayQuestion, DayState, DayTrigger, OpenCard,
    Stratum, SuppressReason, TickInput,
};

/// 調停器に渡す時刻の遅れ（壁時計 − この値）。★ その時刻までの押下が届き切ってから判定する。
pub const S1_TICK_LAG_MS: u64 = 2_000;

/// トレイの終了の補助で、日の問いの答えを待つ長さ（計画の判断 10）。
pub const EOD_QUIT_WAIT_MS: u64 = 60_000;

/// tick の壁時計の間隔がこれ以上空いたら、スリープからの復帰とみなす（電源の通知の予備・肖像と同じ値）。
pub const GAP_AS_POWER_RESUME_MS: u64 = 30_000;

/// 待ち行列に溜める入力の上限（駆動スレッドが止まっていても膨らみ続けないように）。
const MAX_PENDING: usize = 4096;

/// 現地の日（4:00 区切り）と暦の分を、同じ瞬間から求める（`TickInput::local_day`・`local_minute`）。
///
/// ★ `analysis::probe_arbiter::local_at` の前提（同じ `now_ms` から求めた日と分）を、ここで 1 か所に閉じる。
pub fn local_clock(now_ms: u64, utc_offset_secs: i32) -> (i64, u32) {
    (
        crate::eh3::local_day(now_ms, utc_offset_secs),
        crate::eh3::local_minute_of_day(now_ms, utc_offset_secs),
    )
}

/// 開いているプローブのカード（1 枚まで）。
#[derive(Debug, Clone, PartialEq, Eq)]
pub struct ProbeCard {
    pub probe_id: String,
    pub stratum: Stratum,
    pub scheduled_ts: u64,
    pub window_start_ms: u64,
    pub window_end_ms: u64,
    /// 研究者の画面の確かめ用に出したカード（`debug_show_probe`）。★ 行に `"debug":true` を付ける（3 本目の判断 3）。
    pub debug: bool,
}

/// 開いている日の問いのカード（1 枚まで）。
#[derive(Debug, Clone, Copy, PartialEq, Eq)]
pub struct DayCard {
    pub card_id: u64,
    pub target_day: i64,
    pub trigger: DayTrigger,
    pub delayed: bool,
    pub in_window: bool,
    /// 最初に出した時刻（壁時計）。
    pub shown_ts: u64,
    /// トレイの終了の補助で出したか（ボタンが「答えて終了／答えずに終了」になる）。
    pub quit_flow: bool,
    /// 研究者の画面の確かめ用に出したカード（調停器の覚えの外）。★ 閉じても日の問いの状態を変えない。
    pub debug: bool,
}

/// 画面の確かめ用のカードの番号の帯（★ 2^53 未満にする: 画面の JavaScript の数で丸められないように。
/// 調停器の通し番号は 1 から数えるので重ならない）。
const DEBUG_CARD_ID_BASE: u64 = 1 << 52;

/// 画面に送るカードの状態（全体）。★ `stratum`・対象の日・契機は本人に見せない。
#[derive(Debug, Clone, PartialEq, Eq, Serialize)]
#[serde(tag = "kind", rename_all = "snake_case")]
pub enum S1CardView {
    None,
    Probe {
        probe_id: String,
        window_start_ms: u64,
        window_end_ms: u64,
    },
    Day {
        card_id: u64,
        /// 翌日の拾い直し（文を「昨日の作業に」にする）。
        delayed: bool,
        quit_flow: bool,
    },
}

/// `day_question` 行の中身（`lib.rs` が `logger::DayQuestionRow` に写す）。
#[derive(Debug, Clone, Copy, PartialEq, Eq)]
pub struct DayRowData {
    pub t: u64,
    pub shown_ts: u64,
    pub in_eod_window: bool,
    pub target_day: i64,
    pub trigger: DayTrigger,
    pub delayed: bool,
    pub answered: bool,
    pub closed_by: DayClosedBy,
    pub motivation: Option<u8>,
    pub latency_ms: Option<u64>,
    pub duration_ms: Option<u64>,
    /// 研究者の画面の確かめ用のカードの行（★ 行に `"debug":true` を付ける・3 本目の判断 3）。
    pub debug: bool,
}

/// 駆動役が起こす出来事。`lib.rs` が実行する。
#[derive(Debug, Clone)]
pub enum Effect {
    /// `probe_frame` 行（★ `t = anchor_ms`・本タスクの判断 1）。
    Frame {
        anchor_ms: u64,
        frame_seed: u64,
        config: ArbiterConfig,
    },
    /// `probe_suppressed` 行。
    Suppressed {
        t: u64,
        candidate_ts: u64,
        stratum: Stratum,
        reason: SuppressReason,
    },
    /// `probe_assignment` 行。
    Assigned {
        probe_id: String,
        scheduled_ts: u64,
        session_elapsed_ms: u64,
        stratum: Stratum,
        /// 研究者の画面の確かめ用のカード（3 本目の判断 3）。
        debug: bool,
    },
    /// 層化のカードを無作為に差し替えた（`realtime_label`・`activity_label` を `superseded` で 2 行）。
    Superseded { t: u64, card: ProbeCard },
    /// `day_question` 行。
    DayRow(DayRowData),
    /// 画面のカードが変わった（`s1_card_state` を emit する）。
    CardChanged,
    /// 日の問いの状態ファイルを書く。
    SaveDayState(DayState),
}

/// 1 tick の外からの事実（`lib.rs` の駆動スレッドが Atomic と時計から集める）。
#[derive(Debug, Clone, Copy)]
pub struct TickEnv {
    pub wall_ms: u64,
    pub utc_offset_secs: i32,
    pub paused: bool,
    /// `recording::pause_epoch()`（1 秒の中の止めて再開を取りこぼさない）。
    pub pause_epoch: u64,
    /// 電源の復帰の通知の世代。
    pub power_gen: u64,
}

/// 段 1 の駆動役の状態。
#[derive(Debug)]
pub struct S1Driver {
    arbiter: Option<Arbiter>,
    /// 調停器が無い間（同意の前・取り消しの後）の日の問いの状態機械。
    parked_day: Option<DayQuestion>,
    /// 最後に枠を作った世代（`S1_FRAME_GEN`）。
    frame_gen: Option<u64>,
    probe: Option<ProbeCard>,
    day: Option<DayCard>,
    presses: Vec<u64>,
    focus: Vec<u64>,
    /// この走行で最初の tick を調停器に知らせたか。
    started: bool,
    last_paused: bool,
    last_pause_epoch: u64,
    last_power_gen: u64,
    last_wall_ms: Option<u64>,
    /// 止める側のコマンドが先に伏せを済ませた（tick で二重に `on_pause` を呼ばない）。
    pause_handled: bool,
    /// 最後に保存した日の問いの状態。
    saved: Option<DayState>,
}

impl S1Driver {
    /// `day` は状態ファイルから作った日の問い（壊れていれば `DayQuestion::disabled()`）。
    pub fn new(day: DayQuestion, env: &TickEnv) -> Self {
        let saved = day.state().cloned();
        Self {
            arbiter: None,
            parked_day: Some(day),
            frame_gen: None,
            probe: None,
            day: None,
            presses: Vec::new(),
            focus: Vec::new(),
            started: false,
            last_paused: env.paused,
            last_pause_epoch: env.pause_epoch,
            last_power_gen: env.power_gen,
            last_wall_ms: None,
            pause_handled: env.paused,
            saved,
        }
    }

    /// 調停器があるか（枠を作った後で、取り消していない）。
    pub fn is_active(&self) -> bool {
        self.arbiter.is_some()
    }

    /// 最後に枠を作った世代。
    pub fn frame_gen(&self) -> Option<u64> {
        self.frame_gen
    }

    fn day_question_mut(&mut self) -> Option<&mut DayQuestion> {
        match self.arbiter.as_mut() {
            Some(a) => Some(a.day_question_mut()),
            None => self.parked_day.as_mut(),
        }
    }

    fn day_question(&self) -> Option<&DayQuestion> {
        match self.arbiter.as_ref() {
            Some(a) => Some(a.day_question()),
            None => self.parked_day.as_ref(),
        }
    }

    /// 枠を作る（作り直す）。日の問いの状態は引き継ぐ（`Arbiter::into_day_question`）。
    pub fn start_frame(
        &mut self,
        gen: u64,
        anchor_ms: u64,
        frame_seed: u64,
        config: ArbiterConfig,
    ) -> Vec<Effect> {
        let day = match self.arbiter.take() {
            Some(a) => a.into_day_question(),
            None => self.parked_day.take().unwrap_or_else(DayQuestion::disabled),
        };
        let arbiter = Arbiter::new(config, frame_seed, anchor_ms, day);
        let effect = Effect::Frame {
            anchor_ms,
            frame_seed: arbiter.frame_seed(),
            config,
        };
        self.arbiter = Some(arbiter);
        self.frame_gen = Some(gen);
        // ★ 新しい枠の起点より前の入力は渡さない（起点の前の押下で候補を判定しない）
        self.presses.retain(|&t| t >= anchor_ms);
        self.focus.retain(|&t| t >= anchor_ms);
        vec![effect]
    }

    /// 押下（特徴量に流れるキーの押下・一時停止の外）を受ける。
    pub fn push_press(&mut self, t_ms: u64) {
        if self.presses.len() < MAX_PENDING {
            self.presses.push(t_ms);
        }
    }

    /// 自分の窓へ移る・戻る遷移を除いたフォーカスの遷移を受ける。
    pub fn push_focus(&mut self, t_ms: u64) {
        if self.focus.len() < MAX_PENDING {
            self.focus.push(t_ms);
        }
    }

    /// 調停器に渡す、いま開いているカード。★ プローブが出ていれば日の問いを伏せていても `Random`/`Strat`。
    pub fn open_card_for_arbiter(&self) -> Option<OpenCard> {
        match (&self.probe, &self.day) {
            (Some(p), _) => Some(if p.stratum == Stratum::Random {
                OpenCard::Random
            } else {
                OpenCard::Strat
            }),
            (None, Some(d)) => Some(OpenCard::Day {
                target_day: d.target_day,
            }),
            (None, None) => None,
        }
    }

    /// 画面に出すカード。★ 一時停止の間は何も出さない。プローブがあれば日の問いは伏せる。
    pub fn visible_card(&self, paused: bool) -> S1CardView {
        if paused {
            return S1CardView::None;
        }
        match (&self.probe, &self.day) {
            (Some(p), _) => S1CardView::Probe {
                probe_id: p.probe_id.clone(),
                window_start_ms: p.window_start_ms,
                window_end_ms: p.window_end_ms,
            },
            (None, Some(d)) => S1CardView::Day {
                card_id: d.card_id,
                delayed: d.delayed,
                quit_flow: d.quit_flow,
            },
            (None, None) => S1CardView::None,
        }
    }

    /// 1 秒に 1 回。`new_probe_id` は entropy から `probe_id` を作る（候補の乱数とは別・1 本目の判断 5）。
    pub fn tick(&mut self, env: &TickEnv, new_probe_id: &mut dyn FnMut() -> String) -> Vec<Effect> {
        let mut out = Vec::new();
        let wall = env.wall_ms;
        let now = wall.saturating_sub(S1_TICK_LAG_MS);
        let epoch_changed = env.pause_epoch != self.last_pause_epoch;
        // ★ 止まった縁: 止める側のコマンドが先に済ませていなければ、ここで伏せる（予備）
        if env.paused && (!self.last_paused || epoch_changed) && !self.pause_handled {
            out.extend(self.on_pause_requested(wall, env.utc_offset_secs));
        }
        let resumed = !env.paused && (self.last_paused || epoch_changed);
        if !env.paused {
            self.pause_handled = false;
        }
        let gap = self
            .last_wall_ms
            .is_some_and(|t| wall.saturating_sub(t) >= GAP_AS_POWER_RESUME_MS || wall < t);
        let power_resumed = env.power_gen != self.last_power_gen || gap;
        self.last_paused = env.paused;
        self.last_pause_epoch = env.pause_epoch;
        self.last_power_gen = env.power_gen;
        self.last_wall_ms = Some(wall);
        if resumed {
            // ★ 再開で日の問いが見えるようになる（画面は伏せていたので知らせる）
            out.push(Effect::CardChanged);
        }

        if self.arbiter.is_none() {
            self.presses.clear();
            self.focus.clear();
            out.extend(self.save_if_changed());
            return out;
        }

        // この tick に渡す入力（`now` 以下・昇順）。一時停止の間は渡さない。
        let mut presses: Vec<u64> = Vec::new();
        let mut focus: Vec<u64> = Vec::new();
        if env.paused {
            self.presses.clear();
            self.focus.clear();
        } else {
            split_due(&mut self.presses, now, &mut presses);
            split_due(&mut self.focus, now, &mut focus);
        }
        let (local_day, local_minute) = local_clock(now, env.utc_offset_secs);
        let input = TickInput {
            now_ms: now,
            key_presses_ms: &presses,
            focus_transitions_ms: &focus,
            paused: env.paused,
            resumed,
            open_card: self.open_card_for_arbiter(),
            local_day,
            local_minute,
            app_started: !self.started,
            power_resumed,
        };
        self.started = true;
        let actions = match self.arbiter.as_mut() {
            Some(a) => a.tick(&input),
            None => Vec::new(),
        };
        out.extend(self.apply(&actions, wall, new_probe_id));
        out.extend(self.save_if_changed());
        out
    }

    /// 調停器の `Action` を出来事に写す（★ 順は `SupersedeOpenStrat` → `FireProbe`）。
    pub(crate) fn apply(
        &mut self,
        actions: &[Action],
        wall: u64,
        new_probe_id: &mut dyn FnMut() -> String,
    ) -> Vec<Effect> {
        let mut out = Vec::new();
        let anchor = self.arbiter.as_ref().map_or(0, Arbiter::anchor_ms);
        for action in actions {
            match *action {
                Action::Suppress {
                    stratum,
                    candidate_ts,
                    reason,
                } => out.push(Effect::Suppressed {
                    t: wall.max(candidate_ts),
                    candidate_ts,
                    stratum,
                    reason,
                }),
                Action::SupersedeOpenStrat => {
                    if self
                        .probe
                        .as_ref()
                        .is_some_and(|p| p.stratum != Stratum::Random)
                    {
                        if let Some(card) = self.probe.take() {
                            out.push(Effect::Superseded { t: wall, card });
                            out.push(Effect::CardChanged);
                        }
                    }
                }
                Action::FireProbe {
                    stratum,
                    scheduled_ts,
                } => {
                    let probe_id = new_probe_id();
                    let (window_start_ms, window_end_ms) =
                        crate::analysis::probe_scheduler::random_probe_window(scheduled_ts);
                    out.push(Effect::Assigned {
                        probe_id: probe_id.clone(),
                        scheduled_ts,
                        session_elapsed_ms: scheduled_ts.saturating_sub(anchor),
                        stratum,
                        debug: false,
                    });
                    self.probe = Some(ProbeCard {
                        probe_id,
                        stratum,
                        scheduled_ts,
                        window_start_ms,
                        window_end_ms,
                        debug: false,
                    });
                    out.push(Effect::CardChanged);
                }
                Action::ShowDayQuestion {
                    card_id,
                    target_day,
                    trigger,
                    delayed,
                    in_window,
                } => {
                    self.day = Some(DayCard {
                        card_id,
                        target_day,
                        trigger,
                        delayed,
                        in_window,
                        shown_ts: wall,
                        quit_flow: false,
                        debug: false,
                    });
                    out.push(Effect::CardChanged);
                }
                Action::CloseDayQuestion {
                    card_id,
                    target_day: _,
                    closed_by,
                } => {
                    // ★ 持っていない `card_id` は無視する。調停器は覚えを捨て済みなので `on_closed` は呼ばない。
                    let matches = match (card_id, self.day) {
                        (Some(id), Some(d)) => d.card_id == id,
                        (None, Some(_)) => true,
                        (_, None) => false,
                    };
                    // ⚠️ 照合してから取り出す（先に `take()` すると、持っていない番号でもカードが消える）
                    if let Some(d) = self.day.filter(|_| matches) {
                        self.day = None;
                        out.push(Effect::DayRow(DayRowData {
                            t: wall.max(d.shown_ts),
                            shown_ts: d.shown_ts,
                            in_eod_window: d.in_window,
                            target_day: d.target_day,
                            trigger: d.trigger,
                            delayed: d.delayed,
                            answered: false,
                            closed_by,
                            motivation: None,
                            latency_ms: None,
                            duration_ms: None,
                            debug: d.debug,
                        }));
                        out.push(Effect::CardChanged);
                    }
                }
            }
        }
        out
    }

    /// いまのプローブのカードが `probe_id` のものなら、その控えを返す（コマンドが行を書く前に照らす）。
    pub fn probe_card(&self, probe_id: &str) -> Option<&ProbeCard> {
        self.probe.as_ref().filter(|p| p.probe_id == probe_id)
    }

    /// 行を書けたプローブのカードを閉じる。
    pub fn close_probe(&mut self, probe_id: &str) -> Vec<Effect> {
        if self.probe_card(probe_id).is_some() {
            self.probe = None;
            vec![Effect::CardChanged]
        } else {
            Vec::new()
        }
    }

    /// いまの日の問いのカード。
    pub fn day_card(&self) -> Option<DayCard> {
        self.day
    }

    /// 日の問いのカードを閉じたときの行を作る（★ 状態は変えない。行を書けたら [`Self::commit_day_close`]）。
    pub fn day_row_for_close(
        &self,
        card_id: u64,
        wall: u64,
        motivation: Option<u8>,
        closed_by: DayClosedBy,
        latency_ms: Option<u64>,
        duration_ms: Option<u64>,
    ) -> Option<DayRowData> {
        let d = self.day.filter(|d| d.card_id == card_id)?;
        let motivation = motivation.filter(|m| (1..=5).contains(m));
        let answered = closed_by == DayClosedBy::Answer && motivation.is_some();
        Some(DayRowData {
            t: wall.max(d.shown_ts),
            shown_ts: d.shown_ts,
            in_eod_window: d.in_window,
            target_day: d.target_day,
            trigger: d.trigger,
            delayed: d.delayed,
            answered,
            closed_by,
            motivation: if answered { motivation } else { None },
            latency_ms,
            duration_ms,
            debug: d.debug,
        })
    }

    /// 日の問いのカードを閉じる（回答・閉じる・終了・待ちの切れ）。★ `on_closed` を呼ぶのはここだけ。
    pub fn commit_day_close(&mut self, card_id: u64, answered: bool) -> Vec<Effect> {
        let Some(d) = self.day.filter(|d| d.card_id == card_id) else {
            return Vec::new();
        };
        self.day = None;
        if !d.debug {
            if let Some(q) = self.day_question_mut() {
                q.on_closed(d.card_id, d.target_day, answered);
            }
        }
        let mut out = vec![Effect::CardChanged];
        out.extend(self.save_if_changed());
        out
    }

    /// 一時停止を押した（★ `set_paused` の前に呼ぶ）。開いているプローブのカードは行を書かずに下ろし
    /// （止めた後は行を書けない・本人の `dismissed` と混ぜない）、日の問いは伏せたまま持つ。
    pub fn on_pause_requested(&mut self, wall: u64, utc_offset_secs: i32) -> Vec<Effect> {
        self.pause_handled = true;
        let mut out = Vec::new();
        if self.probe.take().is_some() {
            out.push(Effect::CardChanged);
        }
        // ★ tick と同じく遅らせた時刻で日と分を引く（4:00 の境目の 2 秒で日がずれないように）
        let (day, minute) = local_clock(wall.saturating_sub(S1_TICK_LAG_MS), utc_offset_secs);
        if let Some(a) = self.arbiter.as_mut() {
            let config = *a.config();
            a.day_question_mut().on_pause(&config, day, minute);
        }
        out.push(Effect::CardChanged);
        out
    }

    /// トレイの終了。尋ねるなら日の問いのカードを終了の形で出して `true`。
    pub fn on_quit(
        &mut self,
        wall: u64,
        utc_offset_secs: i32,
        paused: bool,
    ) -> (bool, Vec<Effect>) {
        if paused {
            return (false, Vec::new());
        }
        let open = self.open_card_for_arbiter();
        let (day, minute) = local_clock(wall.saturating_sub(S1_TICK_LAG_MS), utc_offset_secs);
        let Some(a) = self.arbiter.as_mut() else {
            return (false, Vec::new());
        };
        let config = *a.config();
        match a.day_question_mut().on_quit(&config, day, minute, open) {
            Some(Action::ShowDayQuestion {
                card_id,
                target_day,
                trigger,
                delayed,
                in_window,
            }) => {
                self.day = Some(DayCard {
                    card_id,
                    target_day,
                    trigger,
                    delayed,
                    in_window,
                    shown_ts: wall,
                    quit_flow: true,
                    debug: false,
                });
                let mut out = vec![Effect::CardChanged];
                out.extend(self.save_if_changed());
                (true, out)
            }
            _ => (false, Vec::new()),
        }
    }

    /// 終了の直前（`End` の前）。開いている日の問いを `closed_by = quit` で書き、プローブは行なしで下ろす。
    pub fn finish_before_end(&mut self, wall: u64) -> Vec<Effect> {
        let mut out = Vec::new();
        self.probe = None;
        if let Some(d) = self.day {
            if let Some(row) =
                self.day_row_for_close(d.card_id, wall, None, DayClosedBy::Quit, None, None)
            {
                out.push(Effect::DayRow(row));
            }
            out.extend(self.commit_day_close(d.card_id, false));
        }
        out.extend(self.save_if_changed());
        out
    }

    /// 同意の取り消し（本タスクの判断 2）。カードは行を書かずに下ろし、調停器を捨てる（以後の行は 0）。
    pub fn revoke(&mut self) -> Vec<Effect> {
        self.probe = None;
        if let Some(d) = self.day.take() {
            if let Some(q) = self.day_question_mut() {
                q.on_closed(d.card_id, d.target_day, false);
            }
        }
        if let Some(a) = self.arbiter.take() {
            self.parked_day = Some(a.into_day_question());
        }
        self.frame_gen = None;
        self.presses.clear();
        self.focus.clear();
        let mut out = vec![Effect::CardChanged];
        out.extend(self.save_if_changed());
        out
    }

    /// 研究者の画面の確かめ用（debug ビルドの門の下からだけ呼ぶ）: プローブのカードを出す。
    pub fn debug_show_probe(
        &mut self,
        wall: u64,
        stratum: Stratum,
        probe_id: String,
    ) -> Vec<Effect> {
        // ★ 同意の後（枠がある）だけ。同意の前に行を書かない。
        if self.probe.is_some() || !self.is_active() {
            return Vec::new();
        }
        let mut out = self.apply(
            &[Action::FireProbe {
                stratum,
                scheduled_ts: wall,
            }],
            wall,
            &mut || probe_id.clone(),
        );
        // ★ 調停器の `Action` は `analysis/` の型なので印を持たせず、写した後で立てる（3 本目の判断 3）
        if let Some(card) = self.probe.as_mut() {
            card.debug = true;
        }
        for e in out.iter_mut() {
            if let Effect::Assigned { debug, .. } = e {
                *debug = true;
            }
        }
        out
    }

    /// 研究者の画面の確かめ用: 日の問いのカードを出す（調停器の覚えの外の通し番号）。
    pub fn debug_show_day(
        &mut self,
        wall: u64,
        utc_offset_secs: i32,
        delayed: bool,
    ) -> Vec<Effect> {
        if self.day.is_some() || !self.is_active() {
            return Vec::new();
        }
        let (day, _) = local_clock(wall, utc_offset_secs);
        self.day = Some(DayCard {
            card_id: DEBUG_CARD_ID_BASE + wall % 1_000_000,
            target_day: if delayed { day - 1 } else { day },
            trigger: if delayed {
                DayTrigger::Pickup
            } else {
                DayTrigger::EveningIdle
            },
            delayed,
            in_window: false,
            shown_ts: wall,
            quit_flow: false,
            debug: true,
        });
        vec![Effect::CardChanged]
    }

    /// 枠の行を送れなかった（次の tick で枠を作り直す）。
    pub fn forget_frame(&mut self) {
        self.frame_gen = None;
    }

    /// 状態ファイルを書けなかった（次の tick で書き直す）。
    pub fn mark_unsaved(&mut self) {
        self.saved = None;
    }

    fn save_if_changed(&mut self) -> Vec<Effect> {
        let now_state = self.day_question().and_then(DayQuestion::state).cloned();
        match now_state {
            Some(s) if self.saved.as_ref() != Some(&s) => {
                self.saved = Some(s.clone());
                vec![Effect::SaveDayState(s)]
            }
            _ => Vec::new(),
        }
    }
}

/// `pending` のうち `now` 以下を `out` へ昇順で移す（残りは次の tick）。
fn split_due(pending: &mut Vec<u64>, now: u64, out: &mut Vec<u64>) {
    pending.sort_unstable();
    let k = pending.partition_point(|&t| t <= now);
    out.extend(pending.drain(..k));
}

#[cfg(test)]
mod tests {
    use super::*;
    use crate::analysis::probe_arbiter::DayRecord;

    const JST: i32 = 9 * 3600;
    /// 2026-11-06 18:59:00 UTC（JST 2026-11-07 03:59）。
    const T_1859Z: u64 = 1_793_991_540_000;
    const DAY_2026_11_06: i64 = 20_763;

    fn env(wall_ms: u64) -> TickEnv {
        TickEnv {
            wall_ms,
            utc_offset_secs: JST,
            paused: false,
            pause_epoch: 0,
            power_gen: 0,
        }
    }

    fn driver_with_frame(anchor: u64) -> S1Driver {
        let mut d = S1Driver::new(DayQuestion::new(DayState::default()), &env(anchor));
        d.start_frame(0, anchor, 7, ArbiterConfig::default());
        d
    }

    fn ids() -> impl FnMut() -> String {
        let mut n = 0u32;
        move || {
            n += 1;
            format!("ID{n:014}")
        }
    }

    // ---- 現地の日と分（引き継ぎ §2 の 4: JST と UTC の両方） ----

    #[test]
    fn local_clock_jst_crosses_the_4am_cutoff() {
        // JST 03:59 はまだ前の日（11-06）・04:01 で 11-07
        assert_eq!(local_clock(T_1859Z, JST), (DAY_2026_11_06, 3 * 60 + 59));
        assert_eq!(
            local_clock(T_1859Z + 120_000, JST),
            (DAY_2026_11_06 + 1, 4 * 60 + 1)
        );
    }

    #[test]
    fn local_clock_utc_at_the_same_instant() {
        // 同じ瞬間でも UTC では 18:59・同じ日の夕方（JST とは暦の分が違う）
        assert_eq!(local_clock(T_1859Z, 0), (DAY_2026_11_06, 18 * 60 + 59));
        assert_eq!(
            local_clock(T_1859Z + 120_000, 0),
            (DAY_2026_11_06, 19 * 60 + 1)
        );
        // UTC の 04:00 の前後で日が変わる
        let utc_0359 = T_1859Z + (9 * 3600) * 1000; // 2026-11-07 03:59 UTC
        assert_eq!(local_clock(utc_0359, 0), (DAY_2026_11_06, 3 * 60 + 59));
        assert_eq!(
            local_clock(utc_0359 + 120_000, 0),
            (DAY_2026_11_06 + 1, 4 * 60 + 1)
        );
    }

    // ---- 伏せと出し直し（引き継ぎ §2 の 8） ----

    fn show_day(d: &mut S1Driver, wall: u64, card_id: u64) {
        d.apply(
            &[Action::ShowDayQuestion {
                card_id,
                target_day: 5,
                trigger: DayTrigger::EveningIdle,
                delayed: false,
                in_window: true,
            }],
            wall,
            &mut ids(),
        );
    }

    #[test]
    fn random_probe_hides_day_card_and_it_returns_after_answer() {
        let mut d = driver_with_frame(1_000_000);
        show_day(&mut d, 2_000_000, 3);
        assert!(matches!(
            d.visible_card(false),
            S1CardView::Day { card_id: 3, .. }
        ));
        assert_eq!(
            d.open_card_for_arbiter(),
            Some(OpenCard::Day { target_day: 5 })
        );

        let fx = d.apply(
            &[Action::FireProbe {
                stratum: Stratum::Random,
                scheduled_ts: 2_100_000,
            }],
            2_100_500,
            &mut ids(),
        );
        assert!(fx.iter().any(|e| matches!(e, Effect::Assigned { .. })));
        // 伏せている間: 画面はプローブ、調停器には Random
        let S1CardView::Probe { probe_id, .. } = d.visible_card(false) else {
            panic!("probe should be visible");
        };
        assert_eq!(d.open_card_for_arbiter(), Some(OpenCard::Random));
        // 答えてプローブを閉じる → 日の問いが同じ番号で戻る。`on_closed` は呼ばれていない
        d.close_probe(&probe_id);
        assert!(matches!(
            d.visible_card(false),
            S1CardView::Day { card_id: 3, .. }
        ));
        assert_eq!(d.day_card().map(|c| c.card_id), Some(3));
    }

    #[test]
    fn day_close_calls_on_closed_once_and_records_answer() {
        let mut d = driver_with_frame(1_000_000);
        show_day(&mut d, 2_000_000, 1);
        let row = d
            .day_row_for_close(
                1,
                2_050_000,
                Some(4),
                DayClosedBy::Answer,
                Some(900),
                Some(1500),
            )
            .expect("row");
        assert!(row.answered);
        assert_eq!(row.motivation, Some(4));
        assert_eq!(row.shown_ts, 2_000_000);
        assert!(row.in_eod_window);
        d.commit_day_close(1, true);
        assert!(d.day_card().is_none());
        // ★ 答えた日として状態に残る（on_closed が回答を受けた）
        let st = d.day_question().and_then(DayQuestion::state).unwrap();
        assert!(st.days.get(&5).is_some_and(|r| r.answered));
        // 2 度目は何もしない（番号が無い）
        assert!(d.commit_day_close(1, true).is_empty());
    }

    #[test]
    fn day_row_rejects_out_of_range_and_unanswered_motivation() {
        let mut d = driver_with_frame(1_000_000);
        show_day(&mut d, 2_000_000, 1);
        let r = d
            .day_row_for_close(1, 2_050_000, Some(9), DayClosedBy::Answer, None, None)
            .unwrap();
        assert!(!r.answered && r.motivation.is_none());
        let r = d
            .day_row_for_close(1, 2_050_000, Some(3), DayClosedBy::Dismiss, None, None)
            .unwrap();
        assert!(
            !r.answered && r.motivation.is_none(),
            "閉じたなら回答は書かない"
        );
        assert!(d
            .day_row_for_close(2, 2_050_000, Some(3), DayClosedBy::Answer, None, None)
            .is_none());
    }

    #[test]
    fn close_day_question_ignores_unknown_card_id_and_writes_day_end() {
        let mut d = driver_with_frame(1_000_000);
        show_day(&mut d, 2_000_000, 4);
        let fx = d.apply(
            &[Action::CloseDayQuestion {
                card_id: Some(99),
                target_day: 5,
                closed_by: DayClosedBy::DayEnd,
            }],
            3_000_000,
            &mut ids(),
        );
        assert!(fx.is_empty(), "持っていない番号は無視");
        assert!(d.day_card().is_some());
        let fx = d.apply(
            &[Action::CloseDayQuestion {
                card_id: Some(4),
                target_day: 5,
                closed_by: DayClosedBy::DayEnd,
            }],
            3_000_000,
            &mut ids(),
        );
        let row = fx
            .iter()
            .find_map(|e| match e {
                Effect::DayRow(r) => Some(*r),
                _ => None,
            })
            .expect("day_end row");
        assert_eq!(row.closed_by, DayClosedBy::DayEnd);
        assert!(!row.answered);
        assert!(d.day_card().is_none());
        // `card_id: None`（駆動役だけが持っていた）でも閉じる
        show_day(&mut d, 3_100_000, 6);
        let fx = d.apply(
            &[Action::CloseDayQuestion {
                card_id: None,
                target_day: 5,
                closed_by: DayClosedBy::DayEnd,
            }],
            4_000_000,
            &mut ids(),
        );
        assert!(fx.iter().any(|e| matches!(e, Effect::DayRow(_))));
    }

    // ---- 差し替え ----

    #[test]
    fn supersede_then_fire_keeps_old_strat_id_and_opens_random() {
        let mut d = driver_with_frame(1_000_000);
        d.apply(
            &[Action::FireProbe {
                stratum: Stratum::LowOperationEnd,
                scheduled_ts: 2_000_000,
            }],
            2_000_000,
            &mut ids(),
        );
        let old = d.probe.clone().unwrap();
        let mut gen = ids();
        let _ = gen();
        let fx = d.apply(
            &[
                Action::SupersedeOpenStrat,
                Action::FireProbe {
                    stratum: Stratum::Random,
                    scheduled_ts: 2_200_000,
                },
            ],
            2_200_100,
            &mut gen,
        );
        let sup = fx
            .iter()
            .find_map(|e| match e {
                Effect::Superseded { card, .. } => Some(card.clone()),
                _ => None,
            })
            .expect("superseded");
        assert_eq!(sup.probe_id, old.probe_id);
        assert_eq!(d.probe.as_ref().map(|p| p.stratum), Some(Stratum::Random));
        assert_ne!(d.probe.as_ref().unwrap().probe_id, old.probe_id);
    }

    #[test]
    fn supersede_never_touches_a_random_card() {
        let mut d = driver_with_frame(1_000_000);
        d.apply(
            &[Action::FireProbe {
                stratum: Stratum::Random,
                scheduled_ts: 2_000_000,
            }],
            2_000_000,
            &mut ids(),
        );
        let fx = d.apply(&[Action::SupersedeOpenStrat], 2_000_500, &mut ids());
        assert!(fx.is_empty());
        assert!(d.probe.is_some());
    }

    #[test]
    fn assigned_elapsed_is_from_anchor_and_window_is_random_probe_window() {
        let mut d = driver_with_frame(1_000_000);
        let fx = d.apply(
            &[Action::FireProbe {
                stratum: Stratum::Resumption,
                scheduled_ts: 1_500_000,
            }],
            1_500_000,
            &mut ids(),
        );
        assert!(fx.iter().any(|e| matches!(
            e,
            Effect::Assigned {
                probe_id,
                scheduled_ts: 1_500_000,
                session_elapsed_ms: 500_000,
                stratum: Stratum::Resumption,
                debug: false,
            } if probe_id == "ID00000000000001"
        )));
        let p = d.probe.clone().unwrap();
        assert_eq!(
            (p.window_start_ms, p.window_end_ms),
            (1_500_000 - 31_000, 1_500_000 - 1_000)
        );
    }

    // ---- 一時停止・終了・取り消し ----

    #[test]
    fn pause_drops_probe_without_rows_and_hides_everything() {
        let mut d = driver_with_frame(1_000_000);
        show_day(&mut d, 2_000_000, 1);
        d.apply(
            &[Action::FireProbe {
                stratum: Stratum::Random,
                scheduled_ts: 2_100_000,
            }],
            2_100_000,
            &mut ids(),
        );
        let fx = d.on_pause_requested(2_200_000, JST);
        assert!(
            fx.iter().all(|e| matches!(e, Effect::CardChanged)),
            "行は書かない"
        );
        assert!(d.probe.is_none());
        assert_eq!(d.visible_card(true), S1CardView::None);
        // 日の問いは持ったまま（再開で戻る）
        assert!(matches!(d.visible_card(false), S1CardView::Day { .. }));
    }

    #[test]
    fn short_pause_inside_one_second_is_seen_as_resume() {
        let mut d = driver_with_frame(1_000_000);
        let mut e = env(2_000_000);
        d.tick(&e, &mut ids());
        // 止めてすぐ再開（epoch が 2 進み、今は再開）
        e.wall_ms += 1000;
        e.pause_epoch = 2;
        let fx = d.tick(&e, &mut ids());
        assert!(fx.iter().any(|x| matches!(x, Effect::CardChanged)));
        assert!(!d.pause_handled);
    }

    #[test]
    fn finish_before_end_writes_quit_row_and_drops_probe() {
        let mut d = driver_with_frame(1_000_000);
        show_day(&mut d, 2_000_000, 2);
        d.apply(
            &[Action::FireProbe {
                stratum: Stratum::Random,
                scheduled_ts: 2_100_000,
            }],
            2_100_000,
            &mut ids(),
        );
        let fx = d.finish_before_end(2_300_000);
        let rows: Vec<_> = fx
            .iter()
            .filter_map(|e| match e {
                Effect::DayRow(r) => Some(*r),
                _ => None,
            })
            .collect();
        assert_eq!(rows.len(), 1);
        assert_eq!(rows[0].closed_by, DayClosedBy::Quit);
        assert!(!rows[0].answered);
        assert!(!fx.iter().any(|e| matches!(e, Effect::Superseded { .. })));
        assert!(d.probe.is_none() && d.day.is_none());
    }

    #[test]
    fn revoke_writes_no_rows_and_stops_the_arbiter() {
        let mut d = driver_with_frame(1_000_000);
        show_day(&mut d, 2_000_000, 1);
        d.apply(
            &[Action::FireProbe {
                stratum: Stratum::Random,
                scheduled_ts: 2_100_000,
            }],
            2_100_000,
            &mut ids(),
        );
        let fx = d.revoke();
        assert!(fx
            .iter()
            .all(|e| matches!(e, Effect::CardChanged | Effect::SaveDayState(_))));
        assert!(!d.is_active());
        assert_eq!(d.visible_card(false), S1CardView::None);
        // 取り消しの後は tick しても行が出ない
        let fx = d.tick(&env(9_000_000), &mut ids());
        assert!(fx
            .iter()
            .all(|e| matches!(e, Effect::CardChanged | Effect::SaveDayState(_))));
    }

    // ---- 枠の作り直しと入力 ----

    #[test]
    fn restart_frame_keeps_day_card_numbering() {
        // JST 2026-11-07 18:00 の壁時計（日の問いの時間帯の中）
        let wall = T_1859Z + 14 * 3600 * 1000 + 60_000;
        let (d1, minute) = local_clock(wall, JST);
        assert_eq!(minute, 18 * 60);
        let next_day_wall = wall + 24 * 3600 * 1000;
        let d2 = local_clock(next_day_wall, JST).0;
        let seen = DayRecord {
            seen_keys: true,
            ..DayRecord::default()
        };
        let mut state = DayState::default();
        state.days.insert(d1, seen);
        state.days.insert(d2, seen);
        let mut d = S1Driver::new(DayQuestion::new(state.clone()), &env(1_000_000));
        d.start_frame(0, 1_000_000, 7, ArbiterConfig::default());
        let (asked, _) = d.on_quit(wall, JST, false);
        assert!(asked);
        let first = d.day_card().unwrap().card_id;
        d.commit_day_close(first, false);
        d.start_frame(1, 5_000_000, 8, ArbiterConfig::default());
        assert_eq!(d.frame_gen(), Some(1));
        // 次の日の終了の補助では、番号が続き番号になる（1 に戻らない）
        let (asked, _) = d.on_quit(next_day_wall, JST, false);
        assert!(asked);
        assert_eq!(d.day_card().unwrap().card_id, first + 1);
        // 陰性の対照: 新しい DayQuestion から作り直すと番号は 1 に戻る（into_day_question が要る理由）
        let mut fresh = S1Driver::new(DayQuestion::new(state), &env(1_000_000));
        fresh.start_frame(0, 1_000_000, 7, ArbiterConfig::default());
        let (asked, _) = fresh.on_quit(next_day_wall, JST, false);
        assert!(asked);
        assert_eq!(fresh.day_card().unwrap().card_id, 1);
    }

    #[test]
    fn split_due_keeps_future_inputs_for_next_tick() {
        let mut pending = vec![30, 10, 50, 20];
        let mut out = Vec::new();
        split_due(&mut pending, 25, &mut out);
        assert_eq!(out, vec![10, 20]);
        assert_eq!(pending, vec![30, 50]);
    }

    #[test]
    fn tick_passes_lagged_time_and_only_due_presses() {
        let mut d = driver_with_frame(1_000_000);
        let wall = 1_100_000;
        d.push_press(wall - 1_000); // まだ遅れの中（次の tick）
        d.push_press(wall - 3_000); // 渡る
        d.tick(&env(wall), &mut ids());
        assert_eq!(d.presses, vec![wall - 1_000]);
    }

    #[test]
    fn no_rows_before_a_frame_exists() {
        let mut d = S1Driver::new(DayQuestion::new(DayState::default()), &env(0));
        d.push_press(10);
        let fx = d.tick(&env(5_000_000), &mut ids());
        assert!(fx.iter().all(|e| matches!(e, Effect::SaveDayState(_))));
        assert_eq!(d.visible_card(false), S1CardView::None);
        assert!(d.presses.is_empty());
    }

    #[test]
    fn debug_day_card_id_fits_js_number_and_leaves_state_alone() {
        let mut d = driver_with_frame(1_000_000);
        d.debug_show_day(T_1859Z, JST, false);
        let id = d.day_card().unwrap().card_id;
        // ★ 画面の JavaScript の数で丸められない（2^53 未満）
        assert!(id < (1u64 << 53));
        let before = d.day_question().and_then(DayQuestion::state).cloned();
        let row = d
            .day_row_for_close(
                id,
                T_1859Z + 5_000,
                Some(4),
                DayClosedBy::Answer,
                None,
                None,
            )
            .unwrap();
        assert!(row.answered);
        d.commit_day_close(id, true);
        assert!(d.day_card().is_none());
        // ★ 確かめ用のカードは日の問いの状態（その日に答えたか）を変えない
        assert_eq!(
            d.day_question().and_then(DayQuestion::state).cloned(),
            before
        );
        // 同意の前（枠が無い）は確かめ用のカードも出さない
        let mut idle = S1Driver::new(DayQuestion::new(DayState::default()), &env(0));
        assert!(idle.debug_show_day(T_1859Z, JST, false).is_empty());
        assert!(idle
            .debug_show_probe(T_1859Z, Stratum::Random, "ID00000000000009".into())
            .is_empty());
    }

    /// M5 の 3 本目の判断 3: 確かめ用のカードの行だけに印が立ち、本物のカードには立たない。
    #[test]
    fn debug_cards_mark_their_rows_and_real_cards_do_not() {
        let mut d = driver_with_frame(1_000_000);
        let fx = d.debug_show_probe(T_1859Z, Stratum::Random, "ID00000000000009".into());
        assert!(fx
            .iter()
            .any(|e| matches!(e, Effect::Assigned { debug: true, .. })));
        assert!(!fx
            .iter()
            .any(|e| matches!(e, Effect::Assigned { debug: false, .. })));
        assert!(d.probe_card("ID00000000000009").unwrap().debug);
        d.close_probe("ID00000000000009");

        d.debug_show_day(T_1859Z, JST, false);
        let id = d.day_card().unwrap().card_id;
        let row = d
            .day_row_for_close(id, T_1859Z + 5_000, None, DayClosedBy::Dismiss, None, None)
            .unwrap();
        assert!(row.debug);

        // 本物のカード（調停器の発火）は印を持たない
        let mut real = driver_with_frame(1_000_000);
        let fx = real.apply(
            &[Action::FireProbe {
                stratum: Stratum::Random,
                scheduled_ts: 1_500_000,
            }],
            1_500_000,
            &mut ids(),
        );
        assert!(fx
            .iter()
            .any(|e| matches!(e, Effect::Assigned { debug: false, .. })));
        assert!(!real.probe.as_ref().unwrap().debug);
    }

    #[test]
    fn failed_frame_and_save_are_retried_next_tick() {
        let mut d = driver_with_frame(1_000_000);
        assert_eq!(d.frame_gen(), Some(0));
        d.forget_frame();
        assert_eq!(d.frame_gen(), None, "枠を作り直させる");
        // 状態を変えてから保存の失敗を知らせると、次の tick でもう一度 SaveDayState が出る
        d.push_press(2_000_000);
        let fx = d.tick(&env(2_010_000), &mut ids());
        assert!(fx.iter().any(|e| matches!(e, Effect::SaveDayState(_))));
        let fx = d.tick(&env(2_011_000), &mut ids());
        assert!(
            !fx.iter().any(|e| matches!(e, Effect::SaveDayState(_))),
            "変わらなければ出ない"
        );
        d.mark_unsaved();
        let fx = d.tick(&env(2_012_000), &mut ids());
        assert!(
            fx.iter().any(|e| matches!(e, Effect::SaveDayState(_))),
            "失敗の後は書き直す"
        );
    }

    #[test]
    fn view_hides_internal_fields() {
        let mut d = driver_with_frame(1_000_000);
        d.apply(
            &[Action::FireProbe {
                stratum: Stratum::LowOperationEnd,
                scheduled_ts: 2_000_000,
            }],
            2_000_000,
            &mut ids(),
        );
        let json = serde_json::to_string(&d.visible_card(false)).unwrap();
        assert!(json.contains("\"kind\":\"probe\""));
        assert!(!json.contains("stratum") && !json.contains("low_operation"));
    }
}
