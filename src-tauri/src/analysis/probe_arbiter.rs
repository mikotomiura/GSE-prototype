//! 段 1（ADR-043）の問いの調停器 —— C4 のプローブ（無作為の枠が主・層化は補い）と日の終わりの問い。
//!
//! ★ 純粋なロジックだけを持つ（OS API・時刻の取得・entropy・IO・推定器を持たない）。駆動役（`lib.rs`）が
//! 1 秒ごとに [`TickInput`] を作って [`Arbiter::tick`] に渡し、返ってきた [`Action`] を行と画面に変える。
//! `gse-replay --probes` は記録から同じ調停器を回す（M5 の 3 本目）。
//!
//! 設計の一次は `.steering/20261105-gse-m5-probe-wiring-plan/design.md` §2・§3 と、
//! `.steering/20261106-gse-m5-s1-core/design.md`（計画から変えた 4 点）。
//!
//! ## 3 つの部品と順序（1 tick の中）
//!
//! 1. 無作為の枠 [`RandomFrame`]（主）。候補の時刻の列は `frame_seed` と起点 `anchor_ms` だけで決まる
//!    （`c_{k+1} = c_k + interval_k`）。ポーリングの時刻にも、他の部品の状態にも左右されない。
//! 2. 層化 [`StrataDetector`]（補い）。打鍵の途切れの後の最初の押下で引き金を出す。無作為の枠は `&` で読むだけ。
//! 3. 日の問い [`DayQuestion`]。無作為を動かさない（次の候補が近ければ待つ）。
//!
//! 「② ③ を外しても ① の出力の列が等しい」ことを検査で固定する
//! （`strata_never_change_random_candidates_or_fires`）。
//!
//! ## 推定器を入れない（ADR-031 D2・ADR-047）
//!
//! [`TickInput`] は打鍵とフォーカスの遷移の時刻・一時停止・開いているカード・現地の日と分だけを持つ。
//! 推定器の確率や状態を入れる欄を持たない（`arbiter_input_has_no_estimator_fields`）。
//!
//! ## 仮の定数
//!
//! 頻度と閾値は探索用の仮の値である（確定は R6 の後の R6′）。値と出典は計画の design.md §6 の表。

use std::collections::BTreeMap;

use rand::rngs::StdRng;
use rand::SeedableRng;
use serde::{Deserialize, Serialize};

use crate::analysis::invitation::SplitMix64;
use crate::analysis::probe_scheduler::{ProbeConfig, ProbeScheduler};

/// 調停器の版。★ 判定の規則を変えたら上げる（`probe_frame` 行に書き、再現の照合に使う）。
pub const ARBITER_VERSION: &str = "s1-arbiter-1";

/// `frame_seed` の上限（2^53 − 1）。★ JS の数値で丸められない範囲（R1 の招待の seed と同じ制約）。
pub const FRAME_SEED_MAX: u64 = (1u64 << 53) - 1;

/// 層化: 押下の間がこれ以上空いた後の最初の押下を `low_operation_end` にする（離席の 180 秒より短い）。
pub const STRAT_LOW_OP_MIN_GAP_MS: u64 = 90_000;
/// 層化: 押下の間がこれ以上空き、その間に自分の窓でないフォーカスの遷移があった後の最初の押下を `resumption` にする。
pub const STRAT_RESUME_MIN_GAP_MS: u64 = 15_000;
/// 層化: 前の発火（無作為か層化）からこの時間以内なら出さない（無作為の空け 6 分に揃える）。
pub const STRAT_GUARD_AFTER_ANY_MS: u64 = 360_000;
/// 層化だけの上限の回数。
pub const STRAT_CAP_COUNT: usize = 1;
/// 層化だけの上限の窓。
pub const STRAT_CAP_WINDOW_MS: u64 = 1_200_000;
/// 層化: 次の無作為の候補がこの時間以内なら譲る（`yielded`）。
pub const STRAT_YIELD_BEFORE_RANDOM_MS: u64 = 120_000;
/// 1 時間の問いの最大の合計（無作為 6 ＋ 層化 3）。★ 同意文書（R4）に書く数と一致させる。
pub const S1_MAX_PROBES_PER_HOUR: u64 = 9;
/// 申告を求めない区間を使うか（既定は無効・計画の判断 2）。
pub const NO_ASK_ENABLED: bool = false;
/// 申告を求めない区間の区画の長さ。
pub const NO_ASK_BLOCK_MS: u64 = 3_600_000;
/// 申告を求めない区画の割合。
pub const NO_ASK_FRACTION: f64 = 0.2;
/// 日の問いの時間帯の始まり（現地の分・17:00）。
pub const EOD_WINDOW_START_MIN: u32 = 1020;
/// 日の問いの時間帯の終わり（現地の分・23:00・この分は含まない）。
pub const EOD_WINDOW_END_MIN: u32 = 1380;
/// 日の問い: 押下がこの時間以上途切れたら出す（離席の 180 秒と分ける）。
pub const EOD_IDLE_MS: u64 = 1_200_000;
/// 日の問い: 次の無作為の候補がこの時間以内なら出すのを待つ。
pub const EOD_YIELD_BEFORE_RANDOM_MS: u64 = 120_000;
/// 日の問い: 拾い直しで尋ねる対象の日の古さの上限（前日だけ）。
pub const PICKUP_MAX_TARGET_AGE_DAYS: i64 = 1;
/// 日の問いの状態に残す日数。
pub const DAY_STATE_KEEP_DAYS: i64 = 7;

/// 調停器の設定（仮の定数の組）。`probe_frame` 行にそのまま書く。
#[derive(Debug, Clone, Copy)]
pub struct ArbiterConfig {
    /// 無作為の枠の分布と抑制（`ProbeConfig::default()`・S1-A1）。
    pub random: ProbeConfig,
    /// 層化を使うか（★ 検査で外して ① の列が変わらないことを見るために置く。本番は常に真）。
    pub strata_enabled: bool,
    pub strat_low_op_min_gap_ms: u64,
    pub strat_resume_min_gap_ms: u64,
    pub strat_guard_after_any_ms: u64,
    pub strat_cap_count: usize,
    pub strat_cap_window_ms: u64,
    pub strat_yield_before_random_ms: u64,
    pub no_ask_enabled: bool,
    pub no_ask_block_ms: u64,
    pub no_ask_fraction: f64,
    pub eod_window_start_min: u32,
    pub eod_window_end_min: u32,
    pub eod_idle_ms: u64,
    pub eod_yield_before_random_ms: u64,
}

impl Default for ArbiterConfig {
    fn default() -> Self {
        Self {
            random: ProbeConfig::default(),
            strata_enabled: true,
            strat_low_op_min_gap_ms: STRAT_LOW_OP_MIN_GAP_MS,
            strat_resume_min_gap_ms: STRAT_RESUME_MIN_GAP_MS,
            strat_guard_after_any_ms: STRAT_GUARD_AFTER_ANY_MS,
            strat_cap_count: STRAT_CAP_COUNT,
            strat_cap_window_ms: STRAT_CAP_WINDOW_MS,
            strat_yield_before_random_ms: STRAT_YIELD_BEFORE_RANDOM_MS,
            no_ask_enabled: NO_ASK_ENABLED,
            no_ask_block_ms: NO_ASK_BLOCK_MS,
            no_ask_fraction: NO_ASK_FRACTION,
            eod_window_start_min: EOD_WINDOW_START_MIN,
            eod_window_end_min: EOD_WINDOW_END_MIN,
            eod_idle_ms: EOD_IDLE_MS,
            eod_yield_before_random_ms: EOD_YIELD_BEFORE_RANDOM_MS,
        }
    }
}

impl ArbiterConfig {
    /// 設定から導いた 1 時間の最大の合計（半開の 1 時間に収まる発火の数の上限）。
    pub fn hourly_max_total(&self) -> u64 {
        const HOUR: u64 = 3_600_000;
        let random = (HOUR / self.random.cap_window_ms) * self.random.cap_count as u64;
        let strata = if self.strata_enabled {
            (HOUR / self.strat_cap_window_ms) * self.strat_cap_count as u64
        } else {
            0
        };
        random + strata
    }

    /// 日の問いの時間帯の中か（現地の分）。
    fn in_eod_window(&self, local_minute: u32) -> bool {
        (self.eod_window_start_min..self.eod_window_end_min).contains(&local_minute)
    }
}

/// 問いが出た理由（`probe_assignment.stratum`）。★ `logger::ProbeStratum` に写す。
#[derive(Debug, Clone, Copy, PartialEq, Eq)]
pub enum Stratum {
    Random,
    LowOperationEnd,
    Resumption,
}

/// 候補を出さなかった理由（`probe_suppressed.reason`・計画の判断 9）。
#[derive(Debug, Clone, Copy, PartialEq, Eq)]
pub enum SuppressReason {
    /// 離席（押下が離席の閾値以上途切れている）。
    Away,
    /// 起点か一時停止の再開から、分析窓の全長が経っていない。
    Warmup,
    /// 前の発火から空けの時間が経っていない。
    Gap,
    /// 上限の窓の中の回数に達した。
    Cap,
    /// 層化が次の無作為の候補に譲った。
    Yielded,
    /// 別のカードが開いている（無作為は無作為のカードだけを見る）。
    CardOpen,
    /// 申告を求めない区画の中。
    NoAsk,
}

impl SuppressReason {
    pub fn as_str(self) -> &'static str {
        match self {
            Self::Away => "away",
            Self::Warmup => "warmup",
            Self::Gap => "gap",
            Self::Cap => "cap",
            Self::Yielded => "yielded",
            Self::CardOpen => "card_open",
            Self::NoAsk => "no_ask",
        }
    }

    pub fn parse(s: &str) -> Option<Self> {
        Some(match s {
            "away" => Self::Away,
            "warmup" => Self::Warmup,
            "gap" => Self::Gap,
            "cap" => Self::Cap,
            "yielded" => Self::Yielded,
            "card_open" => Self::CardOpen,
            "no_ask" => Self::NoAsk,
            _ => return None,
        })
    }

    pub const ALL: [Self; 7] = [
        Self::Away,
        Self::Warmup,
        Self::Gap,
        Self::Cap,
        Self::Yielded,
        Self::CardOpen,
        Self::NoAsk,
    ];
}

/// 日の終わりの問いを出した契機（`day_question.trigger`）。
#[derive(Debug, Clone, Copy, PartialEq, Eq)]
pub enum DayTrigger {
    /// 時間帯の中で押下が途切れた。
    EveningIdle,
    /// 時間帯の中のトレイの終了。
    Quit,
    /// 時間帯の中で一時停止し、同じ日に再開した直後。
    PauseResume,
    /// 翌日の最初の利用（拾い直し）。
    Pickup,
}

impl DayTrigger {
    pub fn as_str(self) -> &'static str {
        match self {
            Self::EveningIdle => "evening_idle",
            Self::Quit => "quit",
            Self::PauseResume => "pause_resume",
            Self::Pickup => "pickup",
        }
    }

    pub fn parse(s: &str) -> Option<Self> {
        Some(match s {
            "evening_idle" => Self::EveningIdle,
            "quit" => Self::Quit,
            "pause_resume" => Self::PauseResume,
            "pickup" => Self::Pickup,
            _ => return None,
        })
    }

    pub const ALL: [Self; 4] = [
        Self::EveningIdle,
        Self::Quit,
        Self::PauseResume,
        Self::Pickup,
    ];
}

/// 日の終わりの問いのカードが閉じた理由（`day_question.closed_by`）。
#[derive(Debug, Clone, Copy, PartialEq, Eq)]
pub enum DayClosedBy {
    Answer,
    Dismiss,
    /// 日の切れ目まで開いていた（拾い直しの対象になる）。
    DayEnd,
    /// トレイの終了で閉じた（「答えずに終了」・待ちの切れ）。
    Quit,
}

impl DayClosedBy {
    pub fn as_str(self) -> &'static str {
        match self {
            Self::Answer => "answer",
            Self::Dismiss => "dismiss",
            Self::DayEnd => "day_end",
            Self::Quit => "quit",
        }
    }

    pub fn parse(s: &str) -> Option<Self> {
        Some(match s {
            "answer" => Self::Answer,
            "dismiss" => Self::Dismiss,
            "day_end" => Self::DayEnd,
            "quit" => Self::Quit,
            _ => return None,
        })
    }

    pub const ALL: [Self; 4] = [Self::Answer, Self::Dismiss, Self::DayEnd, Self::Quit];
}

/// いま開いているカード（駆動役が画面の状態から渡す）。
#[derive(Debug, Clone, Copy, PartialEq, Eq)]
pub enum OpenCard {
    /// 無作為の問いのカード（未回答）。
    Random,
    /// 層化の問いのカード（未回答）。
    Strat,
    /// 日の終わりの問いのカード。
    Day { target_day: i64 },
}

/// 1 tick の入力。★ 推定器の欄を持たない（ADR-031 D2）。
#[derive(Debug, Clone, Copy)]
pub struct TickInput<'a> {
    pub now_ms: u64,
    /// 前の tick からの押下の時刻（特徴量に流れるキーの押下・昇順）。
    pub key_presses_ms: &'a [u64],
    /// 前の tick からのフォーカスの遷移の時刻（★ 自分の窓へ移る遷移・戻る遷移を除いたもの・昇順）。
    pub focus_transitions_ms: &'a [u64],
    /// 一時停止の間か。★ 一時停止の間は入力を見ず、候補を判定しない（行を書けないため）。
    pub paused: bool,
    /// この tick で一時停止から再開したか。
    pub resumed: bool,
    pub open_card: Option<OpenCard>,
    /// 現地の日（4:00 区切り・1970-01-01 からの日数・`eh3::local_day`）。
    pub local_day: i64,
    /// 現地の暦の分（0..1440・`eh3::local_minute_of_day`）。
    pub local_minute: u32,
    /// 起動して最初の tick か。
    pub app_started: bool,
    /// スリープから戻った tick か（`PowerEvent::Resumed`）。
    pub power_resumed: bool,
}

/// 調停器の出力。駆動役が行（`probe_assignment`・`probe_suppressed`・`day_question`）と画面に変える。
#[derive(Debug, Clone, Copy, PartialEq, Eq)]
pub enum Action {
    /// 問いを出す。`scheduled_ts` は無作為なら候補の時刻、層化なら引き金の押下の時刻。
    FireProbe { stratum: Stratum, scheduled_ts: u64 },
    /// 候補を出さなかった。
    Suppress {
        stratum: Stratum,
        candidate_ts: u64,
        reason: SuppressReason,
    },
    /// 開いている層化のカードを閉じ、`skip_reason = "superseded"` で記録する（無作為が出たため）。
    SupersedeOpenStrat,
    /// 日の終わりの問いを出す。
    ShowDayQuestion {
        target_day: i64,
        trigger: DayTrigger,
        delayed: bool,
    },
    /// 日の終わりの問いのカードを閉じる（日の切れ目）。
    CloseDayQuestion {
        target_day: i64,
        closed_by: DayClosedBy,
    },
}

/// 外部の entropy から `frame_seed` を作る（2^53 − 1 以下に落とす）。
pub fn frame_seed_from_entropy(raw: u64) -> u64 {
    raw & FRAME_SEED_MAX
}

// ---------------------------------------------------------------------------
// ① 無作為の枠
// ---------------------------------------------------------------------------

/// 無作為の枠。★ 候補の列は `frame_seed` と `anchor_ms` だけで決まる（本タスクの判断 5）。
#[derive(Debug, Clone)]
pub struct RandomFrame {
    rng: StdRng,
    config: ProbeConfig,
    next_candidate_ms: u64,
    last_fire_ms: Option<u64>,
    recent_fires: Vec<u64>,
}

impl RandomFrame {
    pub fn new(frame_seed: u64, config: ProbeConfig, anchor_ms: u64) -> Self {
        let mut rng = StdRng::seed_from_u64(frame_seed);
        let first = anchor_ms.saturating_add(ProbeScheduler::sample_interval_ms(&mut rng, &config));
        Self {
            rng,
            config,
            next_candidate_ms: first,
            last_fire_ms: None,
            recent_fires: Vec::new(),
        }
    }

    /// 次の候補の時刻。
    pub fn next_candidate_ms(&self) -> u64 {
        self.next_candidate_ms
    }

    /// 直前の無作為の発火の時刻。
    pub fn last_fire_ms(&self) -> Option<u64> {
        self.last_fire_ms
    }

    fn advance(&mut self) {
        let step = ProbeScheduler::sample_interval_ms(&mut self.rng, &self.config);
        self.next_candidate_ms = self.next_candidate_ms.saturating_add(step);
    }

    /// 候補 `c` の判定の理由（`None` なら発火）。
    fn judge(&mut self, c: u64, ctx: &JudgeCtx) -> Option<SuppressReason> {
        let cap_window = self.config.cap_window_ms;
        self.recent_fires
            .retain(|&t| c.saturating_sub(t) < cap_window);
        let idle = ctx
            .last_press_ms
            .map_or(u64::MAX, |p| ctx.now_ms.saturating_sub(p));
        if idle >= self.config.away_idle_ms {
            Some(SuppressReason::Away)
        } else if c.saturating_sub(ctx.warmup_origin_ms) < self.config.min_session_elapsed_ms {
            Some(SuppressReason::Warmup)
        } else if self
            .last_fire_ms
            .is_some_and(|l| c.saturating_sub(l) < self.config.gap_min_ms)
        {
            Some(SuppressReason::Gap)
        } else if self.recent_fires.len() >= self.config.cap_count {
            Some(SuppressReason::Cap)
        } else if ctx.no_ask {
            Some(SuppressReason::NoAsk)
        } else if ctx.open_card == Some(OpenCard::Random) {
            Some(SuppressReason::CardOpen)
        } else {
            None
        }
    }

    fn record_fire(&mut self, c: u64) {
        self.last_fire_ms = Some(c);
        self.recent_fires.push(c);
    }
}

/// 判定に使う 1 tick の文脈。
struct JudgeCtx {
    now_ms: u64,
    last_press_ms: Option<u64>,
    warmup_origin_ms: u64,
    open_card: Option<OpenCard>,
    no_ask: bool,
}

// ---------------------------------------------------------------------------
// ② 層化
// ---------------------------------------------------------------------------

/// 層化の引き金の検出と抑制。★ 無作為の枠は `&` でしか受け取らない（書き換えられない）。
#[derive(Debug, Clone, Default)]
pub struct StrataDetector {
    last_press_ms: Option<u64>,
    focus_since_last_press: bool,
    last_fire_ms: Option<u64>,
    recent_fires: Vec<u64>,
}

impl StrataDetector {
    /// 押下とフォーカスの遷移を時刻の順に流し、最初の引き金（時刻と層）を返す。
    fn detect(
        &mut self,
        config: &ArbiterConfig,
        presses: &[u64],
        focus: &[u64],
    ) -> Option<(u64, Stratum)> {
        let mut trigger = None;
        let (mut i, mut j) = (0, 0);
        while i < presses.len() || j < focus.len() {
            // 同じ時刻なら遷移を先に（遷移の直後の押下を「戻った」と読む）
            let take_focus = j < focus.len() && (i >= presses.len() || focus[j] <= presses[i]);
            if take_focus {
                if self.last_press_ms.is_some() {
                    self.focus_since_last_press = true;
                }
                j += 1;
                continue;
            }
            let p = presses[i];
            i += 1;
            if let Some(prev) = self.last_press_ms {
                let gap = p.saturating_sub(prev);
                let hit = if gap >= config.strat_low_op_min_gap_ms {
                    // ★ 両方に当たる時刻は `low_operation_end`（計画 §7 の 4）
                    Some(Stratum::LowOperationEnd)
                } else if gap >= config.strat_resume_min_gap_ms && self.focus_since_last_press {
                    Some(Stratum::Resumption)
                } else {
                    None
                };
                if trigger.is_none() {
                    trigger = hit.map(|s| (p, s));
                }
            }
            self.last_press_ms = Some(p);
            self.focus_since_last_press = false;
        }
        trigger
    }

    /// 層化の引き金 `t` の判定の理由（`None` なら発火）。
    fn judge(
        &mut self,
        config: &ArbiterConfig,
        frame: &RandomFrame,
        t: u64,
        warmup_origin_ms: u64,
        open_card: Option<OpenCard>,
        no_ask: bool,
    ) -> Option<SuppressReason> {
        self.recent_fires
            .retain(|&f| t.saturating_sub(f) < config.strat_cap_window_ms);
        let last_any = self.last_fire_ms.max(frame.last_fire_ms());
        let next_random = frame.next_candidate_ms();
        if t.saturating_sub(warmup_origin_ms) < config.random.min_session_elapsed_ms {
            Some(SuppressReason::Warmup)
        } else if last_any.is_some_and(|l| t.saturating_sub(l) < config.strat_guard_after_any_ms) {
            Some(SuppressReason::Gap)
        } else if self.recent_fires.len() >= config.strat_cap_count {
            Some(SuppressReason::Cap)
        } else if next_random >= t && next_random - t <= config.strat_yield_before_random_ms {
            Some(SuppressReason::Yielded)
        } else if no_ask {
            Some(SuppressReason::NoAsk)
        } else if open_card.is_some() {
            Some(SuppressReason::CardOpen)
        } else {
            None
        }
    }

    fn record_fire(&mut self, t: u64) {
        self.last_fire_ms = Some(t);
        self.recent_fires.push(t);
    }
}

// ---------------------------------------------------------------------------
// 申告を求めない区間（既定は無効）
// ---------------------------------------------------------------------------

/// 申告を求めない区画の判定（純関数・`frame_seed` と現地の日と区画で決まる）。
pub fn is_no_ask_block(
    config: &ArbiterConfig,
    frame_seed: u64,
    local_day: i64,
    local_minute: u32,
) -> bool {
    if !config.no_ask_enabled || config.no_ask_block_ms == 0 {
        return false;
    }
    let block = (u64::from(local_minute) * 60_000) / config.no_ask_block_ms;
    let day = (local_day as u64).wrapping_mul(0x9E37_79B9_7F4A_7C15);
    let mut r = SplitMix64(frame_seed ^ day ^ block.rotate_left(32));
    r.next_unit() < config.no_ask_fraction
}

// ---------------------------------------------------------------------------
// ③ 日の終わりの問い
// ---------------------------------------------------------------------------

/// 対象の日 1 つぶんの状態。★ 端末の中だけに置く（NDJSON にも提出物にも入れない）。
#[derive(Debug, Clone, Copy, Default, PartialEq, Eq, Serialize, Deserialize)]
pub struct DayRecord {
    /// 段 1 でその日に押下を観測したか。
    pub seen_keys: bool,
    /// その日のうちに尋ねたか。
    pub asked_same_day: bool,
    /// 翌日に拾い直しで尋ねたか。
    pub asked_pickup: bool,
    /// 答えたか。
    pub answered: bool,
}

/// 再起動をまたぐ日の問いの状態（`~/.gse/s1_day_state.json` の中身・読み書きは `s1_day_state.rs`）。
#[derive(Debug, Clone, Default, PartialEq, Eq, Serialize, Deserialize)]
pub struct DayState {
    pub days: BTreeMap<i64, DayRecord>,
}

impl DayState {
    fn prune(&mut self, today: i64) {
        self.days.retain(|&d, _| today - d < DAY_STATE_KEEP_DAYS);
    }
}

/// 日の終わりの問いの状態機械。★ 状態ファイルが壊れていたらこの走行では出さない（[`Self::disabled`]）。
#[derive(Debug, Clone)]
pub struct DayQuestion {
    state: Option<DayState>,
    last_local_day: Option<i64>,
    pickup_checked_day: Option<i64>,
    pause_reserved_day: Option<i64>,
    last_press_ms: Option<u64>,
}

impl DayQuestion {
    pub fn new(state: DayState) -> Self {
        Self {
            state: Some(state),
            last_local_day: None,
            pickup_checked_day: None,
            pause_reserved_day: None,
            last_press_ms: None,
        }
    }

    /// 状態ファイルが壊れていた走行。日の問いを出さない。
    pub fn disabled() -> Self {
        Self {
            state: None,
            last_local_day: None,
            pickup_checked_day: None,
            pause_reserved_day: None,
            last_press_ms: None,
        }
    }

    /// 書き戻す状態（無効なら `None`）。
    pub fn state(&self) -> Option<&DayState> {
        self.state.as_ref()
    }

    fn record(&mut self, day: i64) -> Option<&mut DayRecord> {
        Some(self.state.as_mut()?.days.entry(day).or_default())
    }

    fn tick(
        &mut self,
        config: &ArbiterConfig,
        input: &TickInput,
        open_card: Option<OpenCard>,
        next_random_ms: u64,
        out: &mut Vec<Action>,
    ) {
        if self.state.is_none() {
            return;
        }
        let today = input.local_day;
        // 日の切れ目: 開いている日の問いのカードを閉じ、予約を捨てる
        if self.last_local_day.is_some_and(|d| d != today) {
            if let Some(OpenCard::Day { target_day }) = open_card {
                out.push(Action::CloseDayQuestion {
                    target_day,
                    closed_by: DayClosedBy::DayEnd,
                });
            }
            self.pause_reserved_day = None;
            if let Some(s) = self.state.as_mut() {
                s.prune(today);
            }
        }
        let day_changed_now = self.last_local_day.is_some_and(|d| d != today);
        self.last_local_day = Some(today);
        if input.paused {
            return;
        }
        // 切れ目で閉じたカードはこの tick では開いていないものとして扱う
        let mut open = if day_changed_now && matches!(open_card, Some(OpenCard::Day { .. })) {
            None
        } else {
            open_card
        };
        let pressed = !input.key_presses_ms.is_empty();
        if let Some(&last) = input.key_presses_ms.last() {
            self.last_press_ms = Some(last);
            if let Some(r) = self.record(today) {
                r.seen_keys = true;
            }
        }

        // 翌日の拾い直し（切れ目の後の最初の利用）
        if self.pickup_checked_day != Some(today)
            && (input.app_started || input.power_resumed || pressed)
        {
            self.pickup_checked_day = Some(today);
            if open.is_none() {
                if let Some(target) = self.pickup_target(today) {
                    if let Some(r) = self.record(target) {
                        r.asked_pickup = true;
                    }
                    out.push(Action::ShowDayQuestion {
                        target_day: target,
                        trigger: DayTrigger::Pickup,
                        delayed: true,
                    });
                    open = Some(OpenCard::Day { target_day: target });
                }
            }
        }

        // 一時停止の後の再開
        if input.resumed && self.pause_reserved_day.take() == Some(today) && open.is_none() {
            if let Some(trigger) = self.same_day_ask(today, DayTrigger::PauseResume) {
                out.push(trigger);
                open = Some(OpenCard::Day { target_day: today });
            }
        }

        // 夕方の途切れ（主）
        let idle = self
            .last_press_ms
            .map_or(0, |p| input.now_ms.saturating_sub(p));
        let random_near = next_random_ms >= input.now_ms
            && next_random_ms - input.now_ms <= config.eod_yield_before_random_ms;
        if open.is_none()
            && config.in_eod_window(input.local_minute)
            && self.last_press_ms.is_some()
            && idle >= config.eod_idle_ms
            && !random_near
        {
            if let Some(a) = self.same_day_ask(today, DayTrigger::EveningIdle) {
                out.push(a);
            }
        }
    }

    /// 拾い直しの対象（前日で、押下があり、答えておらず、拾い直しをまだ尋ねていない日）。
    fn pickup_target(&self, today: i64) -> Option<i64> {
        let state = self.state.as_ref()?;
        let (&day, rec) = state
            .days
            .range(..today)
            .rev()
            .find(|(_, r)| r.seen_keys && !r.answered && !r.asked_pickup)?;
        let _ = rec;
        (today - day <= PICKUP_MAX_TARGET_AGE_DAYS).then_some(day)
    }

    /// 当日の問いを出せるなら出す（押下を観測していて、当日まだ尋ねていない）。
    fn same_day_ask(&mut self, today: i64, trigger: DayTrigger) -> Option<Action> {
        let r = self.record(today)?;
        if !r.seen_keys || r.asked_same_day || r.answered {
            return None;
        }
        r.asked_same_day = true;
        Some(Action::ShowDayQuestion {
            target_day: today,
            trigger,
            delayed: false,
        })
    }

    /// 一時停止を押した。時間帯の中なら、同じ日の再開の直後に尋ねる予約をする（止めるのは即座）。
    pub fn on_pause(&mut self, config: &ArbiterConfig, local_day: i64, local_minute: u32) {
        if self.state.is_some() && config.in_eod_window(local_minute) {
            self.pause_reserved_day = Some(local_day);
        }
    }

    /// トレイの終了。時間帯の中で当日まだ尋ねていなければ、尋ねる（「答えて終了／答えずに終了」）。
    pub fn on_quit(
        &mut self,
        config: &ArbiterConfig,
        local_day: i64,
        local_minute: u32,
        open_card: Option<OpenCard>,
    ) -> Option<Action> {
        if open_card.is_some() || !config.in_eod_window(local_minute) {
            return None;
        }
        self.same_day_ask(local_day, DayTrigger::Quit)
    }

    /// カードが閉じた（答えた・閉じた・終了）。★ 回答は更新させない（一度答えた日は答えたまま）。
    pub fn on_closed(&mut self, target_day: i64, answered: bool) {
        if answered {
            if let Some(r) = self.record(target_day) {
                r.answered = true;
            }
        }
    }
}

// ---------------------------------------------------------------------------
// 調停器
// ---------------------------------------------------------------------------

/// 段 1 の問いの調停器。
#[derive(Debug, Clone)]
pub struct Arbiter {
    config: ArbiterConfig,
    frame_seed: u64,
    anchor_ms: u64,
    frame: RandomFrame,
    strata: StrataDetector,
    day: DayQuestion,
    last_press_ms: Option<u64>,
    resumed_at_ms: Option<u64>,
}

impl Arbiter {
    /// `frame_seed` は [`FRAME_SEED_MAX`] 以下に落とす。`anchor_ms` は記録のファイルを開いた時刻。
    pub fn new(config: ArbiterConfig, frame_seed: u64, anchor_ms: u64, day: DayQuestion) -> Self {
        let frame_seed = frame_seed & FRAME_SEED_MAX;
        Self {
            config,
            frame_seed,
            anchor_ms,
            frame: RandomFrame::new(frame_seed, config.random, anchor_ms),
            strata: StrataDetector::default(),
            day,
            last_press_ms: None,
            resumed_at_ms: None,
        }
    }

    pub fn config(&self) -> &ArbiterConfig {
        &self.config
    }

    pub fn frame_seed(&self) -> u64 {
        self.frame_seed
    }

    pub fn anchor_ms(&self) -> u64 {
        self.anchor_ms
    }

    pub fn frame(&self) -> &RandomFrame {
        &self.frame
    }

    pub fn day_question(&self) -> &DayQuestion {
        &self.day
    }

    pub fn day_question_mut(&mut self) -> &mut DayQuestion {
        &mut self.day
    }

    /// 1 秒に 1 回進める。順は ① 無作為 → ② 層化 → ③ 日の問い。
    pub fn tick(&mut self, input: &TickInput) -> Vec<Action> {
        let mut out = Vec::new();
        let now = input.now_ms;
        if input.resumed {
            self.resumed_at_ms = Some(now);
        }
        let warmup_origin = self
            .resumed_at_ms
            .unwrap_or(self.anchor_ms)
            .max(self.anchor_ms);
        let no_ask = is_no_ask_block(
            &self.config,
            self.frame_seed,
            input.local_day,
            input.local_minute,
        );
        let mut open = input.open_card;

        if input.paused {
            // ★ 一時停止の間の候補は判定しない（行を書けない）。入力も見ない。
            while self.frame.next_candidate_ms() <= now {
                self.frame.advance();
            }
            self.day.tick(
                &self.config,
                input,
                open,
                self.frame.next_candidate_ms(),
                &mut out,
            );
            return out;
        }
        if let Some(&last) = input.key_presses_ms.last() {
            self.last_press_ms = Some(last);
        }

        // ① 無作為の枠
        while self.frame.next_candidate_ms() <= now {
            let c = self.frame.next_candidate_ms();
            let ctx = JudgeCtx {
                now_ms: now,
                last_press_ms: self.last_press_ms,
                warmup_origin_ms: warmup_origin,
                open_card: open,
                no_ask,
            };
            match self.frame.judge(c, &ctx) {
                Some(reason) => out.push(Action::Suppress {
                    stratum: Stratum::Random,
                    candidate_ts: c,
                    reason,
                }),
                None => {
                    self.frame.record_fire(c);
                    if open == Some(OpenCard::Strat) {
                        out.push(Action::SupersedeOpenStrat);
                    }
                    out.push(Action::FireProbe {
                        stratum: Stratum::Random,
                        scheduled_ts: c,
                    });
                    open = Some(OpenCard::Random);
                }
            }
            self.frame.advance();
        }

        // ② 層化（① の枠は読むだけ）
        if self.config.strata_enabled {
            if let Some((t, stratum)) = self.strata.detect(
                &self.config,
                input.key_presses_ms,
                input.focus_transitions_ms,
            ) {
                match self
                    .strata
                    .judge(&self.config, &self.frame, t, warmup_origin, open, no_ask)
                {
                    Some(reason) => out.push(Action::Suppress {
                        stratum,
                        candidate_ts: t,
                        reason,
                    }),
                    None => {
                        self.strata.record_fire(t);
                        out.push(Action::FireProbe {
                            stratum,
                            scheduled_ts: t,
                        });
                        open = Some(OpenCard::Strat);
                    }
                }
            }
        }

        // ③ 日の終わりの問い（①② を読むだけ）
        self.day.tick(
            &self.config,
            input,
            open,
            self.frame.next_candidate_ms(),
            &mut out,
        );
        out
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    const T0: u64 = 1_800_000_000_000;
    const SEC: u64 = 1_000;
    const MIN: u64 = 60 * SEC;
    /// JST の現地の日の番号の例（値そのものに意味は無い・日の切れ目の列を作るだけ）。
    const DAY0: i64 = 20_000;

    fn input<'a>(now: u64, presses: &'a [u64], focus: &'a [u64]) -> TickInput<'a> {
        TickInput {
            now_ms: now,
            key_presses_ms: presses,
            focus_transitions_ms: focus,
            paused: false,
            resumed: false,
            open_card: None,
            local_day: DAY0,
            local_minute: 600,
            app_started: false,
            power_resumed: false,
        }
    }

    /// 決定的な打鍵の模様: 1 秒おきの押下のかたまりと、長さの違う途切れ、途切れの中の遷移。
    fn workload(horizon_ms: u64) -> (Vec<u64>, Vec<u64>) {
        let gaps = [
            10 * SEC,
            30 * SEC,
            100 * SEC,
            200 * SEC,
            20 * SEC,
            25 * MIN,
            5 * SEC,
        ];
        let mut presses = Vec::new();
        let mut focus = Vec::new();
        let mut t = T0 + 5 * SEC;
        let mut k = 0usize;
        while t < T0 + horizon_ms {
            for _ in 0..40 {
                presses.push(t);
                t += SEC;
            }
            let g = gaps[k % gaps.len()];
            if k.is_multiple_of(2) {
                focus.push(t + g / 2);
            }
            t += g;
            k += 1;
        }
        (presses, focus)
    }

    /// 1 秒ごとに回し、カードは出たら 20 秒で答えて閉じる駆動役の模擬。
    fn simulate(arb: &mut Arbiter, horizon_ms: u64, step_ms: u64) -> Vec<(u64, Action)> {
        simulate_with(arb, horizon_ms, step_ms, 20 * SEC)
    }

    /// `answer_after_ms` でカードを閉じる版（★ 長くすると、層化のカードと無作為の候補が重なる）。
    fn simulate_with(
        arb: &mut Arbiter,
        horizon_ms: u64,
        step_ms: u64,
        answer_after_ms: u64,
    ) -> Vec<(u64, Action)> {
        let (presses, focus) = workload(horizon_ms);
        let mut out = Vec::new();
        let mut open: Option<(OpenCard, u64)> = None;
        let (mut pi, mut fi) = (0, 0);
        let mut now = T0;
        while now < T0 + horizon_ms {
            now += step_ms;
            let ps = pi;
            while pi < presses.len() && presses[pi] <= now {
                pi += 1;
            }
            let fs = fi;
            while fi < focus.len() && focus[fi] <= now {
                fi += 1;
            }
            if open.is_some_and(|(_, at)| now.saturating_sub(at) >= answer_after_ms) {
                open = None;
            }
            let mut inp = input(now, &presses[ps..pi], &focus[fs..fi]);
            inp.open_card = open.map(|(c, _)| c);
            for a in arb.tick(&inp) {
                match a {
                    Action::FireProbe {
                        stratum: Stratum::Random,
                        ..
                    } => open = Some((OpenCard::Random, now)),
                    Action::FireProbe { .. } => open = Some((OpenCard::Strat, now)),
                    _ => {}
                }
                out.push((now, a));
            }
        }
        out
    }

    fn random_only(actions: &[(u64, Action)]) -> Vec<Action> {
        actions
            .iter()
            .map(|(_, a)| *a)
            .filter(|a| {
                matches!(
                    a,
                    Action::FireProbe {
                        stratum: Stratum::Random,
                        ..
                    } | Action::Suppress {
                        stratum: Stratum::Random,
                        ..
                    }
                )
            })
            .collect()
    }

    fn candidates(actions: &[(u64, Action)]) -> Vec<u64> {
        random_only(actions)
            .iter()
            .map(|a| match a {
                Action::FireProbe { scheduled_ts, .. } => *scheduled_ts,
                Action::Suppress { candidate_ts, .. } => *candidate_ts,
                _ => unreachable!(),
            })
            .collect()
    }

    fn new_arb(seed: u64, config: ArbiterConfig) -> Arbiter {
        Arbiter::new(config, seed, T0, DayQuestion::new(DayState::default()))
    }

    // --- ① 無作為の枠 ------------------------------------------------------

    /// 候補の列は seed と起点だけで決まり、ポーリングの間隔に左右されない。
    #[test]
    fn random_candidates_depend_only_on_seed_and_anchor() {
        for seed in [1u64, 42, 9_007_199_254_740_991] {
            let a = simulate(
                &mut new_arb(seed, ArbiterConfig::default()),
                4 * 3_600_000,
                SEC,
            );
            let b = simulate(
                &mut new_arb(seed, ArbiterConfig::default()),
                4 * 3_600_000,
                3 * SEC,
            );
            assert_eq!(candidates(&a), candidates(&b), "seed={seed}");
            assert!(candidates(&a).len() > 8);
        }
        let x = candidates(&simulate(
            &mut new_arb(1, ArbiterConfig::default()),
            3_600_000,
            SEC,
        ));
        let y = candidates(&simulate(
            &mut new_arb(2, ArbiterConfig::default()),
            3_600_000,
            SEC,
        ));
        assert_ne!(x, y, "seed が違えば列が違う");
    }

    /// ⚠️★★★ 層化と日の問いを on/off しても、無作為の候補・発火・抑制の列は等しい（8 時間・複数の seed）。
    #[test]
    fn strata_never_change_random_candidates_or_fires() {
        // ★ カードを閉じるまでの時間を 2 通り: 20 秒（ふつう）と 8 分（層化のカードが無作為の候補と重なる）
        for (seed, answer_after) in [
            (3u64, 20 * SEC),
            (17, 8 * MIN),
            (2026, 8 * MIN),
            (77_777, 20 * SEC),
        ] {
            let with = simulate_with(
                &mut new_arb(seed, ArbiterConfig::default()),
                8 * 3_600_000,
                SEC,
                answer_after,
            );
            let cfg_off = ArbiterConfig {
                strata_enabled: false,
                ..ArbiterConfig::default()
            };
            let mut off = Arbiter::new(cfg_off, seed, T0, DayQuestion::disabled());
            let without = simulate_with(&mut off, 8 * 3_600_000, SEC, answer_after);
            assert_eq!(random_only(&with), random_only(&without), "seed={seed}");
            if answer_after > 20 * SEC {
                assert!(
                    with.iter().any(|(_, a)| *a == Action::SupersedeOpenStrat),
                    "seed={seed}: 層化のカードと無作為の候補が重なっていない（検査が空回りする）"
                );
            }
            // 層化が実際に動いていること（空回りでない）
            assert!(
                with.iter().any(|(_, a)| matches!(
                    a,
                    Action::FireProbe {
                        stratum: Stratum::LowOperationEnd | Stratum::Resumption,
                        ..
                    }
                )),
                "seed={seed}: 層化が 1 回も出ていない"
            );
        }
    }

    /// 層化は枠を `&` でしか受け取らない（型で書けないことを、本文の署名で確かめる）。
    #[test]
    fn strata_read_frame_without_mutation() {
        let src = include_str!("probe_arbiter.rs");
        let body = src.split("#[cfg(test)]").next().unwrap();
        assert!(
            body.contains("frame: &RandomFrame,"),
            "層化の判定が枠を & で受け取っていない"
        );
        assert!(
            !body.contains("frame: &mut RandomFrame"),
            "枠を書き換える署名がある"
        );
    }

    /// 層化のカードが開いていても無作為は出し、層化のカードを差し替える。
    #[test]
    fn random_fires_over_open_strat_card_and_supersedes_it() {
        let mut arb = new_arb(5, ArbiterConfig::default());
        let c = arb.frame().next_candidate_ms();
        let presses = [c - SEC];
        let mut inp = input(c, &presses, &[]);
        inp.open_card = Some(OpenCard::Strat);
        let acts = arb.tick(&inp);
        assert_eq!(
            acts[..2],
            [
                Action::SupersedeOpenStrat,
                Action::FireProbe {
                    stratum: Stratum::Random,
                    scheduled_ts: c
                }
            ]
        );
    }

    /// 無作為の `card_open` は無作為のカードだけで立つ（層化・日の問いのカードでは立たない）。
    #[test]
    fn random_suppressed_card_open_only_by_random_card() {
        for (card, expect_open) in [
            (OpenCard::Random, true),
            (OpenCard::Strat, false),
            (OpenCard::Day { target_day: DAY0 }, false),
        ] {
            let mut arb = new_arb(5, ArbiterConfig::default());
            let c = arb.frame().next_candidate_ms();
            let presses = [c - SEC];
            let mut inp = input(c, &presses, &[]);
            inp.open_card = Some(card);
            let acts = arb.tick(&inp);
            let suppressed = acts.contains(&Action::Suppress {
                stratum: Stratum::Random,
                candidate_ts: c,
                reason: SuppressReason::CardOpen,
            });
            assert_eq!(suppressed, expect_open, "{card:?}");
        }
    }

    /// 一時停止の間の候補は判定しない（行が出ない）。
    #[test]
    fn paused_candidates_are_not_judged() {
        let mut arb = new_arb(9, ArbiterConfig::default());
        let mut fired_or_suppressed = 0;
        let mut now = T0;
        while now < T0 + 3 * 3_600_000 {
            now += SEC;
            let mut inp = input(now, &[], &[]);
            inp.paused = true;
            fired_or_suppressed += arb
                .tick(&inp)
                .iter()
                .filter(|a| matches!(a, Action::FireProbe { .. } | Action::Suppress { .. }))
                .count();
        }
        assert_eq!(fired_or_suppressed, 0);
        assert!(arb.frame().next_candidate_ms() > now, "枠は進んでいる");
    }

    /// 再開の直後はウォームアップをやり直す。
    #[test]
    fn warmup_restarts_after_resume() {
        let mut arb = new_arb(11, ArbiterConfig::default());
        // 枠の候補の 10 秒前に再開する
        let c = arb.frame().next_candidate_ms();
        let resume = c - 10 * SEC;
        let mut inp = input(resume, &[], &[]);
        inp.resumed = true;
        arb.tick(&inp);
        let presses = [c - SEC];
        let acts = arb.tick(&input(c, &presses, &[]));
        assert!(
            acts.contains(&Action::Suppress {
                stratum: Stratum::Random,
                candidate_ts: c,
                reason: SuppressReason::Warmup,
            }),
            "{acts:?}"
        );
    }

    /// 1 時間の最大の合計は設定から導いた値と一致し、模擬の中の半開の 1 時間もそれを超えない。
    #[test]
    fn hourly_max_total_matches_consent_constant() {
        assert_eq!(
            ArbiterConfig::default().hourly_max_total(),
            S1_MAX_PROBES_PER_HOUR
        );
        for seed in [1u64, 8, 99] {
            let acts = simulate(
                &mut new_arb(seed, ArbiterConfig::default()),
                8 * 3_600_000,
                SEC,
            );
            let fires: Vec<u64> = acts
                .iter()
                .filter_map(|(_, a)| match a {
                    Action::FireProbe { scheduled_ts, .. } => Some(*scheduled_ts),
                    _ => None,
                })
                .collect();
            for &start in &fires {
                let n = fires
                    .iter()
                    .filter(|&&f| f >= start && f < start + 3_600_000)
                    .count();
                assert!(n as u64 <= S1_MAX_PROBES_PER_HOUR, "seed={seed}: {n} 回");
            }
        }
    }

    /// 本文（検査を除く）に推定器の語が無い。
    #[test]
    fn arbiter_input_has_no_estimator_fields() {
        let src = include_str!("probe_arbiter.rs");
        let body = src.split("#[cfg(test)]").next().unwrap();
        for word in [
            concat!("p_", "stuck"),
            concat!("hm", "m"),
            concat!("eng", "ine"),
            concat!("p_", "flow"),
        ] {
            assert!(!body.to_lowercase().contains(word), "{word} が本文にある");
        }
        // 対照: 同じ探し方で本文の語は見つかる
        assert!(body.contains("key_presses_ms"));
    }

    #[test]
    fn frame_seed_is_limited_to_53_bits() {
        assert_eq!(frame_seed_from_entropy(u64::MAX), FRAME_SEED_MAX);
        let arb = Arbiter::new(
            ArbiterConfig::default(),
            u64::MAX,
            T0,
            DayQuestion::disabled(),
        );
        assert_eq!(arb.frame_seed(), FRAME_SEED_MAX);
    }

    // --- ② 層化 --------------------------------------------------------------

    /// 層化の判定だけを見るための、無作為の候補が遠い時刻を探す。
    fn arb_with_far_random(seed: u64) -> (Arbiter, u64) {
        let mut arb = new_arb(seed, ArbiterConfig::default());
        // ウォームアップに当たらないよう、起点から 10 分より後の候補まで枠を進める
        while arb.frame().next_candidate_ms() < T0 + 10 * MIN {
            arb.frame.advance();
        }
        let c = arb.frame().next_candidate_ms();
        (arb, c)
    }

    #[test]
    fn low_operation_end_fires_at_first_press_after_gap() {
        let mut det = StrataDetector::default();
        let cfg = ArbiterConfig::default();
        assert_eq!(
            det.detect(&cfg, &[T0], &[]),
            None,
            "最初の押下は引き金にならない"
        );
        let p = T0 + 95 * SEC;
        assert_eq!(
            det.detect(&cfg, &[p, p + SEC, p + 2 * SEC], &[]),
            Some((p, Stratum::LowOperationEnd))
        );
        assert_eq!(det.detect(&cfg, &[p + 3 * SEC], &[]), None);
    }

    #[test]
    fn resumption_requires_non_own_focus_in_gap() {
        let cfg = ArbiterConfig::default();
        let mut det = StrataDetector::default();
        det.detect(&cfg, &[T0], &[]);
        assert_eq!(
            det.detect(&cfg, &[T0 + 20 * SEC], &[]),
            None,
            "遷移が無ければ出さない"
        );
        let mut det = StrataDetector::default();
        det.detect(&cfg, &[T0], &[]);
        assert_eq!(
            det.detect(&cfg, &[T0 + 20 * SEC], &[T0 + 8 * SEC]),
            Some((T0 + 20 * SEC, Stratum::Resumption))
        );
        let mut det = StrataDetector::default();
        det.detect(&cfg, &[T0], &[]);
        assert_eq!(
            det.detect(&cfg, &[T0 + 10 * SEC], &[T0 + 5 * SEC]),
            None,
            "空きが短ければ出さない"
        );
    }

    #[test]
    fn both_conditions_label_low_operation_end() {
        let cfg = ArbiterConfig::default();
        let mut det = StrataDetector::default();
        det.detect(&cfg, &[T0], &[]);
        assert_eq!(
            det.detect(&cfg, &[T0 + 100 * SEC], &[T0 + 50 * SEC]),
            Some((T0 + 100 * SEC, Stratum::LowOperationEnd))
        );
    }

    /// 層化の判定の一式: 譲る・前の発火の後・層化だけの上限。
    #[test]
    fn strat_yields_before_random_candidate() {
        let (mut arb, c) = arb_with_far_random(21);
        let cfg = *arb.config();
        let t = c - 60 * SEC;
        let r = arb.strata.judge(&cfg, &arb.frame, t, T0, None, false);
        assert_eq!(r, Some(SuppressReason::Yielded));
        // 対照: 候補が譲る幅より遠ければ出す
        let t = c - 5 * MIN;
        assert_eq!(arb.strata.judge(&cfg, &arb.frame, t, T0, None, false), None);
    }

    #[test]
    fn strat_guard_after_any_probe() {
        let (mut arb, c) = arb_with_far_random(22);
        let cfg = *arb.config();
        // 無作為が c で出たことにする
        arb.frame.record_fire(c);
        arb.frame.advance();
        let t = c + 3 * MIN;
        assert_eq!(
            arb.strata.judge(&cfg, &arb.frame, t, T0, None, false),
            Some(SuppressReason::Gap)
        );
    }

    #[test]
    fn strat_cap_counts_only_strata() {
        let cfg = ArbiterConfig {
            strat_guard_after_any_ms: 0,
            strat_yield_before_random_ms: 0,
            ..ArbiterConfig::default()
        };
        let mut arb = Arbiter::new(cfg, 23, T0, DayQuestion::disabled());
        // 無作為の発火が何度あっても層化の上限には数えない
        for k in 0..5 {
            arb.frame.record_fire(T0 + MIN + k * SEC);
        }
        let t = T0 + 2 * MIN;
        assert_eq!(arb.strata.judge(&cfg, &arb.frame, t, T0, None, false), None);
        arb.strata.record_fire(t);
        assert_eq!(
            arb.strata.judge(&cfg, &arb.frame, t + MIN, T0, None, false),
            Some(SuppressReason::Cap)
        );
    }

    // --- 申告を求めない区間 --------------------------------------------------

    #[test]
    fn no_ask_disabled_by_default_emits_no_suppression() {
        let acts = simulate(
            &mut new_arb(31, ArbiterConfig::default()),
            8 * 3_600_000,
            SEC,
        );
        assert!(!acts.iter().any(|(_, a)| matches!(
            a,
            Action::Suppress {
                reason: SuppressReason::NoAsk,
                ..
            }
        )));
    }

    #[test]
    fn no_ask_keeps_candidate_list_identical() {
        let on = ArbiterConfig {
            no_ask_enabled: true,
            no_ask_fraction: 0.5,
            ..ArbiterConfig::default()
        };
        let a = simulate(
            &mut new_arb(32, ArbiterConfig::default()),
            8 * 3_600_000,
            SEC,
        );
        // local_minute は模擬の中で一定なので、区画が問わない側に当たる seed を探す
        let seed = (0..200u64)
            .find(|&s| is_no_ask_block(&on, s & FRAME_SEED_MAX, DAY0, 600))
            .expect("問わない区画に当たる seed がある");
        let a2 = simulate(
            &mut new_arb(seed, ArbiterConfig::default()),
            8 * 3_600_000,
            SEC,
        );
        let b2 = simulate(&mut new_arb(seed, on), 8 * 3_600_000, SEC);
        assert_eq!(
            candidates(&a2),
            candidates(&b2),
            "候補の列は有効と無効で同じ"
        );
        assert!(b2.iter().any(|(_, x)| matches!(
            x,
            Action::Suppress {
                reason: SuppressReason::NoAsk,
                ..
            }
        )));
        let _ = a;
    }

    #[test]
    fn no_ask_blocks_are_deterministic_from_seed() {
        let on = ArbiterConfig {
            no_ask_enabled: true,
            ..ArbiterConfig::default()
        };
        let pattern = |seed| {
            (0..1440u32)
                .step_by(60)
                .map(|m| is_no_ask_block(&on, seed, DAY0, m))
                .collect::<Vec<_>>()
        };
        assert_eq!(pattern(7), pattern(7));
        let hits: usize = (0..50u64)
            .map(|s| pattern(s).iter().filter(|&&b| b).count())
            .sum();
        let rate = hits as f64 / (50.0 * 24.0);
        assert!(
            (0.1..0.3).contains(&rate),
            "割合 {rate} が設定 0.2 から大きく外れる"
        );
        // 同じ区画の中では変わらない
        assert_eq!(
            is_no_ask_block(&on, 7, DAY0, 61),
            is_no_ask_block(&on, 7, DAY0, 119)
        );
    }

    // --- ③ 日の終わりの問い ------------------------------------------------

    /// 日の問いだけを動かすための入力（無作為の候補は遠い）。
    fn day_input<'a>(now: u64, day: i64, minute: u32, presses: &'a [u64]) -> TickInput<'a> {
        TickInput {
            local_day: day,
            local_minute: minute,
            ..input(now, presses, &[])
        }
    }

    fn shows(acts: &[Action]) -> Vec<(i64, DayTrigger, bool)> {
        acts.iter()
            .filter_map(|a| match a {
                Action::ShowDayQuestion {
                    target_day,
                    trigger,
                    delayed,
                } => Some((*target_day, *trigger, *delayed)),
                _ => None,
            })
            .collect()
    }

    fn cfg() -> ArbiterConfig {
        ArbiterConfig::default()
    }

    /// 時間帯の中で途切れが閾値に達したら 1 回だけ出す。
    #[test]
    fn eod_fires_once_in_window_after_idle() {
        let mut dq = DayQuestion::new(DayState::default());
        let mut out = Vec::new();
        let far = u64::MAX;
        dq.tick(
            &cfg(),
            &day_input(T0, DAY0, 1100, &[T0]),
            None,
            far,
            &mut out,
        );
        assert!(shows(&out).is_empty());
        dq.tick(
            &cfg(),
            &day_input(T0 + 19 * MIN, DAY0, 1119, &[]),
            None,
            far,
            &mut out,
        );
        assert!(shows(&out).is_empty(), "閾値の前は出さない");
        dq.tick(
            &cfg(),
            &day_input(T0 + 20 * MIN, DAY0, 1120, &[]),
            None,
            far,
            &mut out,
        );
        assert_eq!(shows(&out), vec![(DAY0, DayTrigger::EveningIdle, false)]);
        out.clear();
        dq.on_closed(DAY0, false);
        dq.tick(
            &cfg(),
            &day_input(T0 + 21 * MIN, DAY0, 1121, &[T0 + 21 * MIN]),
            None,
            far,
            &mut out,
        );
        dq.tick(
            &cfg(),
            &day_input(T0 + 45 * MIN, DAY0, 1145, &[]),
            None,
            far,
            &mut out,
        );
        assert!(shows(&out).is_empty(), "当日は 2 回目を出さない");
    }

    #[test]
    fn eod_not_outside_window() {
        let mut dq = DayQuestion::new(DayState::default());
        let mut out = Vec::new();
        dq.tick(
            &cfg(),
            &day_input(T0, DAY0, 600, &[T0]),
            None,
            u64::MAX,
            &mut out,
        );
        dq.tick(
            &cfg(),
            &day_input(T0 + 30 * MIN, DAY0, 630, &[]),
            None,
            u64::MAX,
            &mut out,
        );
        dq.tick(
            &cfg(),
            &day_input(T0 + 60 * MIN, DAY0, 1380, &[]),
            None,
            u64::MAX,
            &mut out,
        );
        assert!(shows(&out).is_empty());
    }

    #[test]
    fn eod_waits_for_random() {
        let mut dq = DayQuestion::new(DayState::default());
        let mut out = Vec::new();
        dq.tick(
            &cfg(),
            &day_input(T0, DAY0, 1100, &[T0]),
            None,
            u64::MAX,
            &mut out,
        );
        let now = T0 + 20 * MIN;
        dq.tick(
            &cfg(),
            &day_input(now, DAY0, 1120, &[]),
            None,
            now + MIN,
            &mut out,
        );
        assert!(shows(&out).is_empty(), "次の無作為の候補が近ければ待つ");
        dq.tick(
            &cfg(),
            &day_input(now + 5 * MIN, DAY0, 1125, &[]),
            None,
            u64::MAX,
            &mut out,
        );
        assert_eq!(shows(&out).len(), 1);
    }

    /// 翌日の最初の利用で前日を 1 回だけ尋ね、遅れた回答の印を付ける。
    #[test]
    fn pickup_asks_yesterday_once_with_delayed() {
        let mut dq = DayQuestion::new(DayState::default());
        let mut out = Vec::new();
        dq.tick(
            &cfg(),
            &day_input(T0, DAY0, 700, &[T0]),
            None,
            u64::MAX,
            &mut out,
        );
        let next = T0 + 24 * 3_600_000;
        dq.tick(
            &cfg(),
            &day_input(next, DAY0 + 1, 500, &[next]),
            None,
            u64::MAX,
            &mut out,
        );
        assert_eq!(shows(&out), vec![(DAY0, DayTrigger::Pickup, true)]);
        out.clear();
        // 同じ日に再起動しても、もう尋ねない（状態ファイルの印）
        let state = dq.state().unwrap().clone();
        let mut dq2 = DayQuestion::new(state);
        let mut inp = day_input(next + MIN, DAY0 + 1, 501, &[]);
        inp.app_started = true;
        dq2.tick(&cfg(), &inp, None, u64::MAX, &mut out);
        assert!(shows(&out).is_empty());
    }

    #[test]
    fn pickup_skips_target_older_than_one_day() {
        let mut dq = DayQuestion::new(DayState::default());
        let mut out = Vec::new();
        dq.tick(
            &cfg(),
            &day_input(T0, DAY0, 700, &[T0]),
            None,
            u64::MAX,
            &mut out,
        );
        let later = T0 + 2 * 24 * 3_600_000;
        dq.tick(
            &cfg(),
            &day_input(later, DAY0 + 2, 500, &[later]),
            None,
            u64::MAX,
            &mut out,
        );
        assert!(shows(&out).is_empty(), "2 日前は尋ねない");
    }

    #[test]
    fn no_more_than_two_asks_per_target_day() {
        let mut dq = DayQuestion::new(DayState::default());
        let mut out = Vec::new();
        let far = u64::MAX;
        dq.tick(
            &cfg(),
            &day_input(T0, DAY0, 1100, &[T0]),
            None,
            far,
            &mut out,
        );
        dq.tick(
            &cfg(),
            &day_input(T0 + 20 * MIN, DAY0, 1120, &[]),
            None,
            far,
            &mut out,
        );
        dq.on_closed(DAY0, false);
        assert_eq!(
            dq.on_quit(&cfg(), DAY0, 1130, None),
            None,
            "当日はもう尋ねない"
        );
        let next = T0 + 24 * 3_600_000;
        dq.tick(
            &cfg(),
            &day_input(next, DAY0 + 1, 500, &[next]),
            None,
            far,
            &mut out,
        );
        dq.on_closed(DAY0, false);
        let n2 = next + 24 * 3_600_000;
        dq.tick(
            &cfg(),
            &day_input(n2, DAY0 + 2, 500, &[n2]),
            None,
            far,
            &mut out,
        );
        let for_day0 = shows(&out).iter().filter(|(d, _, _)| *d == DAY0).count();
        assert_eq!(for_day0, 2);
    }

    /// 切れ目まで開いていたカードは `day_end` で閉じ、拾い直しの対象になる。
    #[test]
    fn day_end_closes_open_card_then_pickup() {
        let mut dq = DayQuestion::new(DayState::default());
        let mut out = Vec::new();
        let far = u64::MAX;
        dq.tick(
            &cfg(),
            &day_input(T0, DAY0, 1300, &[T0]),
            None,
            far,
            &mut out,
        );
        dq.tick(
            &cfg(),
            &day_input(T0 + 20 * MIN, DAY0, 1320, &[]),
            None,
            far,
            &mut out,
        );
        assert_eq!(shows(&out).len(), 1);
        out.clear();
        let open = Some(OpenCard::Day { target_day: DAY0 });
        let next = T0 + 8 * 3_600_000;
        dq.tick(
            &cfg(),
            &day_input(next, DAY0 + 1, 300, &[next]),
            open,
            far,
            &mut out,
        );
        assert_eq!(
            out[0],
            Action::CloseDayQuestion {
                target_day: DAY0,
                closed_by: DayClosedBy::DayEnd
            }
        );
        dq.on_closed(DAY0, false);
        assert_eq!(shows(&out), vec![(DAY0, DayTrigger::Pickup, true)]);
    }

    /// 時間帯の中の一時停止は、同じ日の再開の直後に尋ねる。日をまたいだら尋ねない。
    #[test]
    fn pause_in_window_defers_to_resume_same_day() {
        let mut dq = DayQuestion::new(DayState::default());
        let mut out = Vec::new();
        let far = u64::MAX;
        dq.tick(
            &cfg(),
            &day_input(T0, DAY0, 1100, &[T0]),
            None,
            far,
            &mut out,
        );
        dq.on_pause(&cfg(), DAY0, 1101);
        let mut p = day_input(T0 + MIN, DAY0, 1101, &[]);
        p.paused = true;
        dq.tick(&cfg(), &p, None, far, &mut out);
        assert!(shows(&out).is_empty(), "止めるのは即座・その間は出さない");
        let mut r = day_input(T0 + 5 * MIN, DAY0, 1105, &[]);
        r.resumed = true;
        dq.tick(&cfg(), &r, None, far, &mut out);
        assert_eq!(shows(&out), vec![(DAY0, DayTrigger::PauseResume, false)]);

        let mut dq = DayQuestion::new(DayState::default());
        let mut out = Vec::new();
        dq.tick(
            &cfg(),
            &day_input(T0, DAY0, 1370, &[T0]),
            None,
            far,
            &mut out,
        );
        dq.on_pause(&cfg(), DAY0, 1371);
        let next = T0 + 8 * 3_600_000;
        let mut r = day_input(next, DAY0 + 1, 300, &[]);
        r.resumed = true;
        dq.tick(&cfg(), &r, None, far, &mut out);
        assert!(
            !shows(&out)
                .iter()
                .any(|(_, t, _)| *t == DayTrigger::PauseResume),
            "日をまたいだ再開では尋ねない"
        );
    }

    #[test]
    fn day_state_broken_disables_eod_this_run() {
        let mut dq = DayQuestion::disabled();
        let mut out = Vec::new();
        dq.tick(
            &cfg(),
            &day_input(T0, DAY0, 1100, &[T0]),
            None,
            u64::MAX,
            &mut out,
        );
        dq.tick(
            &cfg(),
            &day_input(T0 + 30 * MIN, DAY0, 1130, &[]),
            None,
            u64::MAX,
            &mut out,
        );
        assert!(out.is_empty());
        assert_eq!(dq.on_quit(&cfg(), DAY0, 1130, None), None);
        assert!(dq.state().is_none());
    }

    /// 状態は serde で往復でき、再起動の後も「当日は尋ねた」を覚えている。古い日は刈られる。
    #[test]
    fn day_state_survives_restart() {
        let mut dq = DayQuestion::new(DayState::default());
        let mut out = Vec::new();
        dq.tick(
            &cfg(),
            &day_input(T0, DAY0, 1100, &[T0]),
            None,
            u64::MAX,
            &mut out,
        );
        dq.tick(
            &cfg(),
            &day_input(T0 + 20 * MIN, DAY0, 1120, &[]),
            None,
            u64::MAX,
            &mut out,
        );
        let json = serde_json::to_string(dq.state().unwrap()).unwrap();
        let back: DayState = serde_json::from_str(&json).unwrap();
        assert_eq!(&back, dq.state().unwrap());
        let mut dq2 = DayQuestion::new(back);
        assert_eq!(
            dq2.on_quit(&cfg(), DAY0, 1125, None),
            None,
            "再起動の後も当日は尋ねない"
        );

        let mut old = DayState::default();
        old.days.insert(DAY0 - 30, DayRecord::default());
        let mut dq3 = DayQuestion::new(old);
        dq3.tick(
            &cfg(),
            &day_input(T0, DAY0, 600, &[]),
            None,
            u64::MAX,
            &mut out,
        );
        dq3.tick(
            &cfg(),
            &day_input(T0 + 1, DAY0 + 1, 600, &[]),
            None,
            u64::MAX,
            &mut out,
        );
        assert!(!dq3.state().unwrap().days.contains_key(&(DAY0 - 30)));
    }

    /// 日の切れ目の列は現地の日の番号で決まる（JST と UTC で同じ時刻でも日が違えば別の日として扱う）。
    /// ★ 時差の変換そのもの（`eh3::local_day`）は駆動役の検査に置く（本タスクの判断 4）。
    #[test]
    fn day_boundaries_follow_local_day_not_wall_time() {
        // 同じ UTC の時刻でも、JST では翌日・UTC では当日になるような 2 つの列
        let at = T0;
        for (today, tomorrow) in [(DAY0, DAY0 + 1), (DAY0 + 5, DAY0 + 6)] {
            let mut dq = DayQuestion::new(DayState::default());
            let mut out = Vec::new();
            dq.tick(
                &cfg(),
                &day_input(at, today, 700, &[at]),
                None,
                u64::MAX,
                &mut out,
            );
            dq.tick(
                &cfg(),
                &day_input(at + SEC, tomorrow, 701, &[at + SEC]),
                None,
                u64::MAX,
                &mut out,
            );
            assert_eq!(shows(&out), vec![(today, DayTrigger::Pickup, true)]);
        }
    }

    #[test]
    fn enum_strings_round_trip() {
        for r in SuppressReason::ALL {
            assert_eq!(SuppressReason::parse(r.as_str()), Some(r));
        }
        for t in DayTrigger::ALL {
            assert_eq!(DayTrigger::parse(t.as_str()), Some(t));
        }
        for c in DayClosedBy::ALL {
            assert_eq!(DayClosedBy::parse(c.as_str()), Some(c));
        }
        assert_eq!(SuppressReason::parse("thin"), None);
    }
}
