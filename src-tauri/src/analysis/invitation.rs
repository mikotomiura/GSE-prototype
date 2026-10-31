//! EH3 の招待（Physical Anchor の PC 面）を出すかどうかの状態機械（OS API 非依存の純ロジック）。
//!
//! 要件の SSOT は `.steering/20261011-portrait-eh3-prereg/implementation-requirements.md` の R-I1〜R-I15、
//! 値の根拠は `.steering/20261011-portrait-eh3-impl/design.md` §3.1・§6。
//!
//! ## 何を入力に持ち、何を持たないか
//!
//! 入力は 1 tick ごとの時刻・推定の停滞（`p_stuck`）・無操作の長さ・本人の設定・研究の条件・
//! セッションの区切りだけである。
//! ⚠️ **招待への応答（図像を押した・押さなかった・見たかどうか）を受け取る口を作らない**（R-I9・R-I10・
//! ADR-033 D3・D4）。図像から説明と設定の窓を開く操作は、この機械に届かない。
//! 設定の変更は外枠（出す・出さない・時間帯・上限）だけを変え、系の控え（閉じた後の間隔・1 区間 1 回）を解かない
//! （ADR-035 D4）。
//!
//! ## 出す規則（design §3.1）
//!
//! - 契機: `p_stuck ≥ 0.60` が 30 秒続いた（離席候補 `idle_ms ≥ 180 s` の中では出さない）。機会のスコアは使わない。
//! - 1 区間 1 回: 停滞の区間は、`p_stuck < 0.60` が 60 秒続くか、離席候補に入るか、セッションが区切れたら終わる。
//! - **繰り越さない**: 出せるのは区間が契機を満たした瞬間だけ。そのとき出せなければ（外枠の外・間隔の中・
//!   上限に達した・記録の一時停止中）、その区間は使い切ったものとして出さない
//!   （`.steering/20261011-portrait-eh3-impl/decisions.md` 判断 6 #2。9:00 や間隔明けの瞬間に出ると、
//!   出る時刻が状態より時計で決まり、M-4 の読みが濁る）。
//! - 失効: 提示から 60 秒（実時間）で、応答の有無に依らず閉じる。
//! - 即時に閉じる: 本人が止めた・時間帯の外に出た・研究の条件が偽・記録の一時停止・セッションの区切り。
//! - 閉じた後の間隔: 30 分。⚠️ **起点は「提示 + 失効の時間」**であって、実際に閉じた時刻ではない。
//!   本人が止めて早く閉じても、次に出せる時刻は早まらない（止めた・戻したの履歴が出す量を増やさない・ADR-035 D4 ①②）。
//! - 1 日（現地 4:00 区切り）の上限: 本人の選択 {1, 2, 4}・既定 2。内側の上限 4（ADR-026 PC-6）。
//! - 時間帯: 本人の選択 {終日, 9–18, 8–20, 6–22} 時・既定 終日。夜間の内側の制約は置かない
//!   （`.steering/20261011-portrait-eh3-after-impl/decisions.md` 判断 2。ADR-035 D1 の内側の制約 3 は
//!   Outdoor の型にかかり、本設計の招待は歩行・外出を促す型を持たない。屋外の型を足すなら戻る）。
//!
//! ## ADR-035 D1 の内側の制約（設定より内側で効く）
//!
//! ① 系の控え（閉じた後の間隔・1 区間 1 回）／② 上限 4（PC-6）／③ 安全条件（夜間の Outdoor 無効。屋外の型が無いので対象が無い）／
//! ④ 研究の条件（`meta.invitation_enabled`。EH3 では真・`.steering/20261011-portrait-eh3-impl/decisions.md` 判断 1 #1）。
//! これに加えて、記録の一時停止中は出さない（出たのに記録が無い提示を作らない・判断 6 #1）。

use serde::{Deserialize, Serialize};

use crate::analysis::intervention::AWAY_IDLE_MS;

/// 契機の `p_stuck` の閾値（本番の段）。Nudge と同じ値（較正中の推定に新しい値を足さない・design §6）。
pub const TRIGGER_P_STUCK: f64 = 0.60;
/// 契機の持続（本番の段。`p_stuck ≥ 閾値` が続く長さ）。
pub const TRIGGER_HOLD_MS: u64 = 30_000;

/// 契機の値の組。停滞の区間の始まり（閾値以上が `hold_ms` 続く）と終わり（閾値未満が
/// `EPISODE_END_HOLD_MS` 続く）は同じ閾値で決める。
///
/// 段は 2 つ。本番（`MAIN`）と、試作と利用者の検証の段（`PROTO`・`eh3.mode` の `trigger=proto`）。
/// 試作の段は招待を出やすい側に置き、その記録を根拠に本番の値を凍結の前に決める
/// （`.steering/20261011-portrait-eh3-after-impl/decisions.md` 判断 4・`.steering/20261012-eh3-trigger-values/`）。
/// ⚠️ `metrics.rs` の `p_stuck_trigger`（Stuck エピソードの定義）とは別の値であり、こちらを変えても動かない。
#[derive(Debug, Clone, Copy, PartialEq)]
pub struct Trigger {
    pub p_stuck: f64,
    pub hold_ms: u64,
}

impl Trigger {
    /// 本番の段（稿 §10.1 F-2・判断 1 #3）。
    pub const MAIN: Trigger = Trigger {
        p_stuck: TRIGGER_P_STUCK,
        hold_ms: TRIGGER_HOLD_MS,
    };
    /// 試作と利用者の検証の段（`eh3.mode` の `trigger=proto`）。
    ///
    /// 研究者が決めた（2026-10-12・`.steering/20261012-eh3-trigger-values/decisions.md` 判断 2）。0.50 は、
    /// 手を止めたときの頭打ち（0.54・Windows の実機）を越えるので、研究者が手を止めれば図像を確かめられる。
    /// 研究者の O1 の記録（4 日・作業 9.6 時間）では、本番の値の契機 35 回に対して 42 回、既定の提示は 6 回に対して 7 回。
    pub const PROTO: Trigger = Trigger {
        p_stuck: 0.50,
        hold_ms: 10_000,
    };
}

impl Default for Trigger {
    fn default() -> Self {
        Self::MAIN
    }
}

/// 契機の種類（ADR-040 D4・`.steering/20261101-invitation-wiring/design.md` §1）。
///
/// 出す規則（1 区間 1 回・失効・間隔・上限・時間帯・研究の条件・一時停止）は全部 [`InvitationMachine::tick`] で共有し、
/// 差し替えるのは「この tick で契機が立ったか」だけである。
/// 研究者の設定ファイル（`~/.gse/invitation_trigger.json`）はこの形の JSON 1 つをそのまま読む。
/// 未知の欄・欠けた値は読み込みで拒まれる（`deny_unknown_fields`・fail-closed）。
#[derive(Debug, Clone, Copy, PartialEq, Serialize, Deserialize)]
#[serde(tag = "kind", rename_all = "snake_case", deny_unknown_fields)]
pub enum TriggerKind {
    /// 推定器: `p_stuck ≥ p_stuck` が `hold_ms` 続いた（今の区間の追跡そのもの・既定は [`Trigger::MAIN`]）。
    Estimator { p_stuck: f64, hold_ms: u64 },
    /// friction_rising: `p_stuck(now) − p_stuck(now − window_ms) ≥ delta` が偽から真になった tick で立つ。
    /// 真の間は立ち直さない。既定の値は置かない。
    Rising { delta: f64, window_ms: u64 },
    /// 頻度を合わせた無作為: 離席候補の外・区切りでない tick ごとに、確率 `per_active_hour / 3600`（1 秒あたり）で立つ。
    /// 乱数は `seed` から再現する。既定の値は置かない。
    Random { per_active_hour: f64, seed: u64 },
    /// 立たない（統制の「なし」）。
    ///
    /// ⚠️ 空の構造体にしてあるのは、unit variant だと内部タグの enum で未知の欄が拒まれないため。
    #[serde(rename = "none")]
    Off {},
}

impl Default for TriggerKind {
    fn default() -> Self {
        Trigger::MAIN.into()
    }
}

impl From<Trigger> for TriggerKind {
    fn from(t: Trigger) -> Self {
        TriggerKind::Estimator {
            p_stuck: t.p_stuck,
            hold_ms: t.hold_ms,
        }
    }
}

impl TriggerKind {
    /// 範囲の検査（設定ファイルの読み込みで使う）。範囲外は `false`（招待を出さない側）。
    pub fn is_valid(&self) -> bool {
        match *self {
            TriggerKind::Estimator { p_stuck, .. } => {
                p_stuck.is_finite() && p_stuck > 0.0 && p_stuck <= 1.0
            }
            TriggerKind::Rising { delta, window_ms } => {
                delta.is_finite() && delta > 0.0 && delta <= 1.0 && window_ms > 0
            }
            TriggerKind::Random {
                per_active_hour, ..
            } => per_active_hour.is_finite() && per_active_hour > 0.0 && per_active_hour <= 60.0,
            TriggerKind::Off { .. } => true,
        }
    }

    /// JSON 1 つから読む。読めない・未知の欄・欠けた値・範囲外は `None`。
    pub fn from_json(text: &str) -> Option<TriggerKind> {
        serde_json::from_str::<TriggerKind>(text)
            .ok()
            .filter(TriggerKind::is_valid)
    }

    /// 記録の `condition` 欄の値（`invitation_condition` 行）。
    pub fn condition_name(&self) -> &'static str {
        match self {
            TriggerKind::Estimator { .. } => "estimator",
            TriggerKind::Rising { .. } => "rising",
            TriggerKind::Random { .. } => "random",
            TriggerKind::Off { .. } => "none",
        }
    }
}

/// splitmix64（外部 crate を足さない・seed から再現する）。
#[derive(Debug, Clone)]
struct SplitMix64(u64);

impl SplitMix64 {
    fn next_u64(&mut self) -> u64 {
        self.0 = self.0.wrapping_add(0x9E37_79B9_7F4A_7C15);
        let mut z = self.0;
        z = (z ^ (z >> 30)).wrapping_mul(0xBF58_476D_1CE4_E5B9);
        z = (z ^ (z >> 27)).wrapping_mul(0x94D0_49BB_1331_11EB);
        z ^ (z >> 31)
    }

    /// `[0, 1)` の一様乱数（上位 53 bit）。
    fn next_unit(&mut self) -> f64 {
        (self.next_u64() >> 11) as f64 / (1u64 << 53) as f64
    }
}

/// 契機の判定の状態（種類ごとの小さな状態。`tick` の本体は `triggered: bool` だけを受ける）。
#[derive(Debug, Clone, Default)]
enum Source {
    /// 今の区間の追跡（`Trigger` は機械が持つ）。
    #[default]
    Estimator,
    Rising(RisingState),
    Random(RandomState),
    Off,
}

#[derive(Debug, Clone)]
struct RisingState {
    delta: f64,
    window_ms: u64,
    /// `(時刻, p_stuck)`。先頭は「`now − window_ms` 以前で最も新しい」点。
    history: std::collections::VecDeque<(u64, f64)>,
    above: bool,
}

#[derive(Debug, Clone)]
struct RandomState {
    /// 1 秒あたりの確率。
    p_per_sec: f64,
    rng: SplitMix64,
    last_ms: Option<u64>,
}

impl RisingState {
    /// 1 tick 進める。偽から真になった tick で `true`。
    fn step(&mut self, now: u64, p: f64) -> bool {
        // 時計が戻ったら履歴を捨てる（前の時刻の点を基準にしない）
        if self.history.back().is_some_and(|&(t, _)| now < t) {
            self.history.clear();
            self.above = false;
        }
        self.history.push_back((now, p));
        let cutoff = now.saturating_sub(self.window_ms);
        while self.history.len() >= 2 && self.history[1].0 <= cutoff {
            self.history.pop_front();
        }
        let above = now >= self.window_ms
            && self
                .history
                .front()
                .is_some_and(|&(t, q)| t <= cutoff && p - q >= self.delta);
        let rose = above && !self.above;
        self.above = above;
        rose
    }

    fn reset(&mut self) {
        self.history.clear();
        self.above = false;
    }
}

impl RandomState {
    fn step(&mut self, now: u64) -> bool {
        let dt_s = self
            .last_ms
            .map_or(1.0, |t| (now.saturating_sub(t) as f64 / 1000.0).min(30.0));
        self.last_ms = Some(now);
        self.rng.next_unit() < self.p_per_sec * dt_s
    }
}
/// 停滞の区間が終わる条件（`p_stuck < 閾値` が続く長さ）。
pub const EPISODE_END_HOLD_MS: u64 = 60_000;
/// 提示から閉じるまで（実時間）。PC 面の曝露予算の実測は無い（PC-11）ので、見逃されても主課題を傷つけない側に短く置く。
pub const EXPIRY_MS: u64 = 60_000;
/// 閉じた後の間隔（起点は提示 + `EXPIRY_MS`）。
pub const GAP_AFTER_CLOSE_MS: u64 = 30 * 60_000;
/// 内側の 1 日の上限（ADR-026 PC-6・§6.3 の 2–4）。本人の選択はこの内側にだけ置く（ADR-035 D3）。
pub const HARD_DAILY_CAP: u32 = 4;
/// 1 日の上限の選択肢（N 択・ADR-035 D3）。
#[derive(Debug, Clone, Copy, PartialEq, Eq, Serialize, Deserialize)]
#[serde(rename_all = "snake_case")]
pub enum DailyCap {
    One,
    Two,
    Four,
}

impl DailyCap {
    pub const ALL: [DailyCap; 3] = [DailyCap::One, DailyCap::Two, DailyCap::Four];

    pub fn count(self) -> u32 {
        match self {
            DailyCap::One => 1,
            DailyCap::Two => 2,
            DailyCap::Four => 4,
        }
    }
}

/// 出してよい時間帯の選択肢（N 択）。
#[derive(Debug, Clone, Copy, PartialEq, Eq, Serialize, Deserialize)]
#[serde(rename_all = "snake_case")]
pub enum TimeWindow {
    /// 0:00–24:00（既定。控える側の既定は 1 日の上限が担う・判断 2）
    AllDay,
    /// 9:00–18:00
    Core,
    /// 8:00–20:00
    Extended,
    /// 6:00–22:00
    Wide,
}

impl TimeWindow {
    pub const ALL: [TimeWindow; 4] = [
        TimeWindow::AllDay,
        TimeWindow::Core,
        TimeWindow::Extended,
        TimeWindow::Wide,
    ];

    /// `[start, end)`（0:00 からの分）。
    pub fn range(self) -> (u32, u32) {
        match self {
            TimeWindow::AllDay => (0, 24 * 60),
            TimeWindow::Core => (9 * 60, 18 * 60),
            TimeWindow::Extended => (8 * 60, 20 * 60),
            TimeWindow::Wide => (6 * 60, 22 * 60),
        }
    }
}

/// 本人の設定（外枠）。設定の画面と `~/.gse/eh3_invitation.json` はこの形をそのまま使う
/// （未知の値は読み込みで拒まれる＝自由な値の入力の経路が無い・ADR-035 D3）。
#[derive(Debug, Clone, Copy, PartialEq, Eq, Serialize, Deserialize)]
#[serde(deny_unknown_fields)]
pub struct Settings {
    pub enabled: bool,
    pub window: TimeWindow,
    pub cap: DailyCap,
}

impl Default for Settings {
    /// ADR-035 D2: 有無は「出す」、上限は狭い側。時間帯は終日（時計で出す時刻を絞らない・判断 2）。
    fn default() -> Self {
        Self {
            enabled: true,
            window: TimeWindow::AllDay,
            cap: DailyCap::Two,
        }
    }
}

/// 1 tick の入力。⚠️ 招待への応答を表す欄は**置かない**（モジュールの doc）。
#[derive(Debug, Clone, Copy)]
pub struct TickInput {
    /// 実時間（epoch ms）。
    pub now_ms: u64,
    /// 現地の日（4:00 区切り・`eh3::local_day`）。上限の数え直しに使う。
    pub local_day: i64,
    /// 現地時刻の 0:00 からの分（時間帯の判定）。
    pub minute_of_day: u32,
    /// 推定の停滞の確率（`clean_score` 済みでなくてよい・NaN は 0 として扱う）。
    pub p_stuck: f64,
    /// 最後の打鍵からの無操作の長さ。
    pub idle_ms: u64,
    /// 研究の条件（内側の制約 ④）。
    pub research_enabled: bool,
    /// 記録が動いている（一時停止していない）。偽なら出さず、表示中なら閉じる（判断 6 #1）。
    pub recording_active: bool,
    /// 本人の設定（外枠）。
    pub settings: Settings,
    /// この tick でセッションが区切れた（終了・スリープ・日付の区切り）。
    pub session_boundary: bool,
}

/// 1 tick の出力。
#[derive(Debug, Clone, Copy, PartialEq, Eq)]
pub struct TickOutput {
    /// いま招待を出しているか（`invitation: present` / `none`）。
    pub present: bool,
    /// この tick で新しく出した（`invitation_present` 行を書く）。
    pub presented: bool,
    /// この tick で停滞の区間が契機を満たした（出したかどうかに依らない）。記録には書かない。
    /// 契機の値を記録で比べる道具（`examples/invitation_trigger_sweep.rs`）が数える。
    pub triggered: bool,
}

/// 招待の状態機械。
#[derive(Debug, Clone, Default)]
pub struct InvitationMachine {
    trigger: Trigger,
    source: Source,
    stuck_since: Option<u64>,
    below_since: Option<u64>,
    in_episode: bool,
    episode_used: bool,
    /// 表示中の提示の時刻。失効はこの値だけから決まる（古い提示の失効が新しい提示を消す経路が無い）。
    shown_at: Option<u64>,
    /// 次に出してよい最も早い時刻（提示 + 失効 + 間隔）。
    next_allowed_at: u64,
    day: Option<i64>,
    count_today: u32,
}

fn in_minutes(m: u32, (start, end): (u32, u32)) -> bool {
    start <= m && m < end
}

impl InvitationMachine {
    /// 本番の段の契機で作る。
    pub fn new() -> Self {
        Self::default()
    }

    /// 段の契機を指定して作る。
    pub fn with_trigger(trigger: Trigger) -> Self {
        Self {
            trigger,
            ..Self::default()
        }
    }

    /// 契機の種類を指定して作る（通常のモードの研究者の設定）。
    ///
    /// ⚠️ 範囲外の値（[`TriggerKind::is_valid`] が偽）は `Off`（立たない）として作る＝招待を出さない側。
    pub fn with_kind(kind: TriggerKind) -> Self {
        if !kind.is_valid() {
            return Self {
                source: Source::Off,
                ..Self::default()
            };
        }
        match kind {
            TriggerKind::Estimator { p_stuck, hold_ms } => {
                Self::with_trigger(Trigger { p_stuck, hold_ms })
            }
            TriggerKind::Rising { delta, window_ms } => Self {
                source: Source::Rising(RisingState {
                    delta,
                    window_ms,
                    history: std::collections::VecDeque::new(),
                    above: false,
                }),
                ..Self::default()
            },
            TriggerKind::Random {
                per_active_hour,
                seed,
            } => Self {
                source: Source::Random(RandomState {
                    p_per_sec: per_active_hour / 3600.0,
                    rng: SplitMix64(seed),
                    last_ms: None,
                }),
                ..Self::default()
            },
            TriggerKind::Off {} => Self {
                source: Source::Off,
                ..Self::default()
            },
        }
    }

    /// いま招待を出しているか。
    pub fn is_present(&self) -> bool {
        self.shown_at.is_some()
    }

    /// 外枠と内側の制約が、いま出すことを許すか（ADR-026 PC-12 の判定の前提・ADR-035 D1）。
    pub fn surface_allowed(input: &TickInput) -> bool {
        input.research_enabled
            && input.recording_active
            && input.settings.enabled
            && in_minutes(input.minute_of_day, input.settings.window.range())
    }

    /// 1 tick 進める。
    pub fn tick(&mut self, input: &TickInput) -> TickOutput {
        let now = input.now_ms;
        // 日が進んだときだけ数え直す（時計が戻って前の日に戻っても、上限の数を戻さない）
        if self.day.is_none_or(|d| input.local_day > d) {
            self.day = Some(input.local_day);
            self.count_today = 0;
        }

        let triggered = self.detect(input);

        let allowed = Self::surface_allowed(input);

        // 閉じる: 失効・外枠の外（止めた・時間帯の外・研究の条件・一時停止）・セッションの区切り。
        if let Some(shown) = self.shown_at {
            let expired = now.saturating_sub(shown) >= EXPIRY_MS;
            if expired || !allowed || input.session_boundary {
                self.shown_at = None;
            }
        }

        // 出す: 区間が契機を満たした瞬間だけ（繰り越さない）。出せなくても、その区間は使い切る。
        let mut presented = false;
        let cap = input.settings.cap.count().min(HARD_DAILY_CAP);
        if triggered && !self.episode_used {
            self.episode_used = true;
            if self.shown_at.is_none()
                && allowed
                && !input.session_boundary
                && self.count_today < cap
                && now >= self.next_allowed_at
            {
                self.shown_at = Some(now);
                self.next_allowed_at = now + EXPIRY_MS + GAP_AFTER_CLOSE_MS;
                self.count_today += 1;
                presented = true;
            }
        }

        TickOutput {
            present: self.shown_at.is_some(),
            presented,
            triggered,
        }
    }

    /// この tick で契機が立ったか（種類ごとの判定）。
    ///
    /// 推定器以外は「立った瞬間を 1 区間とみなす」: 立った tick で `episode_used` を戻し、
    /// 「その瞬間に出せなければ出さない」（繰り越さない）規則を同じ形で効かせる。
    fn detect(&mut self, input: &TickInput) -> bool {
        if matches!(self.source, Source::Estimator) {
            return self.track_episode(input);
        }
        let now = input.now_ms;
        let blocked = input.session_boundary || input.idle_ms >= AWAY_IDLE_MS;
        let p = if input.p_stuck.is_finite() {
            input.p_stuck
        } else {
            0.0
        };
        let fired = match &mut self.source {
            Source::Rising(r) => {
                if blocked {
                    r.reset();
                    false
                } else {
                    r.step(now, p)
                }
            }
            Source::Random(r) => {
                if blocked {
                    r.last_ms = None;
                    false
                } else {
                    r.step(now)
                }
            }
            Source::Estimator | Source::Off => false,
        };
        if blocked {
            self.end_episode();
        }
        if fired {
            self.episode_used = false;
        }
        fired
    }

    /// 停滞の区間を追う。この tick で区間が契機を満たした（`in_episode` が偽から真になった）なら `true`。
    fn track_episode(&mut self, input: &TickInput) -> bool {
        let now = input.now_ms;
        let away = input.idle_ms >= AWAY_IDLE_MS;
        if input.session_boundary || away {
            self.end_episode();
            return false;
        }
        let p = if input.p_stuck.is_finite() {
            input.p_stuck
        } else {
            0.0
        };
        if p >= self.trigger.p_stuck {
            self.below_since = None;
            let since = *self.stuck_since.get_or_insert(now);
            if !self.in_episode && now.saturating_sub(since) >= self.trigger.hold_ms {
                self.in_episode = true;
                return true;
            }
        } else {
            self.stuck_since = None;
            if self.in_episode {
                let since = *self.below_since.get_or_insert(now);
                if now.saturating_sub(since) >= EPISODE_END_HOLD_MS {
                    self.end_episode();
                }
            }
        }
        false
    }

    fn end_episode(&mut self) {
        self.in_episode = false;
        self.episode_used = false;
        self.stuck_since = None;
        self.below_since = None;
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    const T0: u64 = 1_760_000_000_000;
    const SEC: u64 = 1000;
    const MIN: u64 = 60 * SEC;
    /// 10:00（時間帯の中）
    const TEN: u32 = 10 * 60;

    /// `start_min`（現地時刻の分）から始まる時計での入力。
    fn input_from(start_min: u32, now_ms: u64, p_stuck: f64, settings: Settings) -> TickInput {
        TickInput {
            now_ms,
            local_day: 100,
            minute_of_day: (start_min + ((now_ms - T0) / MIN) as u32) % (24 * 60),
            p_stuck,
            idle_ms: 0,
            research_enabled: true,
            recording_active: true,
            settings,
            session_boundary: false,
        }
    }

    fn input(now_ms: u64, p_stuck: f64, settings: Settings) -> TickInput {
        input_from(TEN, now_ms, p_stuck, settings)
    }

    /// p_stuck の列（1 秒 1 値）を流し、提示の時刻（T0 からの秒）を返す。
    fn run_from(
        start_min: u32,
        p: &dyn Fn(u64) -> f64,
        settings: &dyn Fn(u64) -> Settings,
        secs: u64,
    ) -> Vec<u64> {
        let mut m = InvitationMachine::new();
        let mut out = Vec::new();
        for s in 0..secs {
            if m.tick(&input_from(start_min, T0 + s * SEC, p(s), settings(s)))
                .presented
            {
                out.push(s);
            }
        }
        out
    }

    fn run(p: &dyn Fn(u64) -> f64, settings: &dyn Fn(u64) -> Settings, secs: u64) -> Vec<u64> {
        run_from(TEN, p, settings, secs)
    }

    /// 経路独立性の検査の時計: 5:00 から 18 時間（終日でない 3 つの時間帯の境界をすべて通る）。
    const HIST_START_MIN: u32 = 5 * 60;
    const HIST_SECS: usize = 18 * 3600;

    fn widest() -> Settings {
        Settings {
            enabled: true,
            window: TimeWindow::AllDay,
            cap: DailyCap::Four,
        }
    }

    /// 時間帯を 9–18 時に狭めた設定（時間帯の境界の検査用）。
    fn core() -> Settings {
        Settings {
            window: TimeWindow::Core,
            ..Settings::default()
        }
    }

    /// 2 分ごとに停滞と非停滞が入れ替わる列。
    fn alternating(s: u64) -> f64 {
        if (s / 120).is_multiple_of(2) {
            0.9
        } else {
            0.1
        }
    }

    /// 決まった擬似乱数（xorshift）で、停滞の区間が散らばった p_stuck の列（6 時間）を作る。
    fn scenario(seed: u64) -> Vec<f64> {
        let mut x = seed.wrapping_mul(0x9E37_79B9_7F4A_7C15) | 1;
        let mut v = Vec::new();
        let mut stuck = false;
        for _ in 0..HIST_SECS {
            x ^= x << 13;
            x ^= x >> 7;
            x ^= x << 17;
            if x.is_multiple_of(400) {
                stuck = !stuck;
            }
            v.push(if stuck { 0.8 } else { 0.2 });
        }
        v
    }

    #[test]
    fn presents_only_after_thirty_seconds_of_stall() {
        let got = run(
            &|s| if s >= 10 { 0.9 } else { 0.1 },
            &|_| Settings::default(),
            120,
        );
        assert_eq!(got, vec![40], "10 秒目から 30 秒続いた 40 秒目に出す");
        let got = run(
            &|s| if (10..39).contains(&s) { 0.9 } else { 0.1 },
            &|_| Settings::default(),
            120,
        );
        assert!(got.is_empty(), "29 秒で途切れたら出さない");
    }

    #[test]
    fn expires_after_sixty_seconds_whatever_happens() {
        let mut m = InvitationMachine::new();
        let shown: Vec<bool> = (0..200)
            .map(|s| {
                m.tick(&input(T0 + s * SEC, 0.9, Settings::default()))
                    .present
            })
            .collect();
        assert!(!shown[29] && shown[30], "30 秒目に出る");
        assert!(shown[89] && !shown[90], "提示から 60 秒で閉じる");
    }

    #[test]
    fn one_invitation_per_stall_episode() {
        assert_eq!(
            run(&|_| 0.9, &|_| widest(), 3000).len(),
            1,
            "停滞が続いても 1 回"
        );
        let got = run(
            &|s| if (100..150).contains(&s) { 0.1 } else { 0.9 },
            &|_| widest(),
            3000,
        );
        assert_eq!(got.len(), 1, "60 秒未満の途切れは区間を終えない");
    }

    #[test]
    fn gap_of_thirty_minutes_after_close() {
        let got = run(&alternating, &|_| widest(), 3 * 3600);
        assert!(got.len() >= 2, "{got:?}");
        for w in got.windows(2) {
            assert!(
                w[1] - w[0] >= (EXPIRY_MS + GAP_AFTER_CLOSE_MS) / SEC,
                "{got:?}"
            );
        }
    }

    #[test]
    fn daily_cap_follows_the_choice() {
        for cap in DailyCap::ALL {
            let s = Settings { cap, ..widest() };
            let got = run(&alternating, &|_| s, 6 * 3600);
            assert_eq!(got.len() as u32, cap.count(), "{cap:?}");
        }
    }

    #[test]
    fn daily_count_resets_at_the_day_boundary() {
        let mut m = InvitationMachine::new();
        let mut n = 0;
        for s in 0..(6 * 3600u64) {
            let mut i = input(
                T0 + s * SEC,
                alternating(s),
                Settings {
                    cap: DailyCap::One,
                    ..widest()
                },
            );
            i.local_day = if s < 3 * 3600 { 100 } else { 101 };
            i.minute_of_day = TEN;
            if m.tick(&i).presented {
                n += 1;
            }
        }
        assert_eq!(n, 2);
    }

    #[test]
    fn does_not_present_while_away() {
        let mut m = InvitationMachine::new();
        for s in 0..300 {
            let mut i = input(T0 + s * SEC, 0.95, Settings::default());
            i.idle_ms = AWAY_IDLE_MS;
            assert!(!m.tick(&i).presented);
        }
    }

    #[test]
    fn closes_immediately_when_the_person_stops() {
        let mut m = InvitationMachine::new();
        let mut at_stop = None;
        for s in 0..60 {
            let settings = Settings {
                enabled: s < 40,
                ..Settings::default()
            };
            let o = m.tick(&input(T0 + s * SEC, 0.9, settings));
            if s == 39 {
                assert!(o.present);
            }
            if s == 40 {
                at_stop = Some(o.present);
            }
        }
        assert_eq!(at_stop, Some(false), "止めた tick で閉じる");
    }

    #[test]
    fn closes_immediately_when_the_window_ends() {
        let mut m = InvitationMachine::new();
        let mut last = true;
        for s in 0..60 {
            let mut i = input(T0 + s * SEC, 0.9, core());
            i.minute_of_day = if s < 40 { 17 * 60 + 59 } else { 18 * 60 };
            last = m.tick(&i).present;
        }
        assert!(!last, "18:00 で閉じる");
    }

    #[test]
    fn closes_at_a_session_boundary() {
        let mut m = InvitationMachine::new();
        for s in 0..35 {
            m.tick(&input(T0 + s * SEC, 0.9, Settings::default()));
        }
        assert!(m.is_present());
        let mut i = input(T0 + 35 * SEC, 0.9, Settings::default());
        i.session_boundary = true;
        assert!(!m.tick(&i).present);
    }

    #[test]
    fn an_old_expiry_never_closes_a_new_invitation() {
        let mut m = InvitationMachine::new();
        let mut presented = Vec::new();
        let mut present = Vec::new();
        for s in 0..(2 * 3600u64) {
            let o = m.tick(&input(T0 + s * SEC, alternating(s), widest()));
            if o.presented {
                presented.push(s as usize);
            }
            present.push(o.present);
        }
        assert!(presented.len() >= 2);
        let shown_secs = present[presented[1]..].iter().take_while(|x| **x).count();
        assert_eq!(shown_secs as u64, EXPIRY_MS / SEC, "2 回目も丸 60 秒出る");
    }

    #[test]
    fn stopping_early_does_not_bring_the_next_invitation_forward() {
        // 出た直後に止めて戻しても、次に出せる時刻は「提示 + 失効 + 間隔」のまま。
        let p = alternating;
        let normal = run(&p, &|_| widest(), 3 * 3600);
        let stopped = run(
            &p,
            &|s| Settings {
                enabled: !(31..=33).contains(&s),
                ..widest()
            },
            3 * 3600,
        );
        assert_eq!(normal[0], 30);
        assert_eq!(stopped[0], 30);
        assert!(stopped.get(1) >= normal.get(1), "{normal:?} / {stopped:?}");
    }

    /// 既定（終日）では夜も出す。本人が時間帯を狭めたときだけ出さない（夜間の内側の制約は置かない・判断 2）。
    #[test]
    fn the_default_presents_at_night_and_a_narrowed_window_does_not() {
        for minute in [23 * 60, 2 * 60, 5 * 60 + 59] {
            assert_eq!(
                run_from(minute, &|_| 0.9, &|_| Settings::default(), 60),
                vec![30],
                "既定は {minute} 分にも出す"
            );
            for window in [TimeWindow::Core, TimeWindow::Extended, TimeWindow::Wide] {
                let s = Settings {
                    window,
                    ..Settings::default()
                };
                assert!(
                    run_from(minute, &|_| 0.9, &|_| s, 60).is_empty(),
                    "{window:?} は {minute} 分に出さない"
                );
            }
        }
    }

    /// 既定（終日）では 0:00 を跨いでも閉じず、失効（60 秒）だけで閉じる。
    #[test]
    fn the_default_keeps_an_invitation_across_midnight_until_expiry() {
        let mut m = InvitationMachine::new();
        let mut present = Vec::new();
        for s in 0..120 {
            let o = m.tick(&input_from(
                23 * 60 + 59,
                T0 + s * SEC,
                0.9,
                Settings::default(),
            ));
            if o.present {
                present.push(s);
            }
        }
        // 23:59:30 に出て、0:00（s = 60）を越えても出たまま、60 秒で失効する
        assert_eq!(present.first(), Some(&30));
        assert_eq!(present.len() as u64, EXPIRY_MS / SEC, "{present:?}");
        assert!(present.contains(&60));
    }

    /// 既定（終日）では 4:00 の日の区切りの直前にも出せる。区切りで上限は数え直すが、
    /// 消えてから 30 分の間隔は消えない。
    #[test]
    fn the_day_boundary_resets_the_cap_but_not_the_gap() {
        let settings = Settings {
            cap: DailyCap::One,
            ..Settings::default()
        };
        let mut m = InvitationMachine::new();
        let mut presented = Vec::new();
        for s in 0..(3 * 3600u64) {
            let mut i = input_from(3 * 60 + 59, T0 + s * SEC, alternating(s), settings);
            // 3:59:00 に始まり、s = 60 で 4:00（次の日）
            i.local_day = if s < 60 { 100 } else { 101 };
            if m.tick(&i).presented {
                presented.push(s);
            }
        }
        // 3:59:30 に出す。次の日の 1 回は、提示 + 失効 60 秒 + 間隔 30 分（s = 1890）より後の
        // 最初の区間（s = 1920 に始まり 30 秒後）。上限 1 は日ごとなので、それ以上は出ない。
        assert_eq!(presented, vec![30, 1950]);
    }

    // ---- ADR-035 D1: 内側の制約は、設定を最大に広げても効く ----

    #[test]
    fn inner_constraints_hold_at_the_widest_settings() {
        let mut m = InvitationMachine::new();
        for s in 0..120 {
            let mut i = input(T0 + s * SEC, 0.95, widest());
            i.research_enabled = false;
            assert!(!m.tick(&i).presented, "④ 研究の条件が偽なら出さない");
        }
        let got = run(
            &|s| if (s / 60) % 2 == 0 { 0.9 } else { 0.1 },
            &|_| widest(),
            12 * 3600,
        );
        assert!(got.len() as u32 <= HARD_DAILY_CAP, "② 上限 4");
        for w in got.windows(2) {
            assert!(
                w[1] - w[0] >= (EXPIRY_MS + GAP_AFTER_CLOSE_MS) / SEC,
                "① 間隔"
            );
        }
    }

    // ---- ADR-035 D4 / Migration 1: 経路独立性 ----

    fn all_settings() -> Vec<Settings> {
        let mut v = Vec::new();
        for enabled in [false, true] {
            for window in TimeWindow::ALL {
                for cap in DailyCap::ALL {
                    v.push(Settings {
                        enabled,
                        window,
                        cap,
                    });
                }
            }
        }
        v
    }

    /// 設定の履歴: 30 分ごとに設定が替わる。
    fn history(seed: u64) -> impl Fn(u64) -> Settings {
        let opts = all_settings();
        move |s: u64| opts[(((s / 1800) * 7 + seed * 13) % opts.len() as u64) as usize]
    }

    /// 履歴の中で使った最も広い設定（外枠の和）。
    fn envelope(h: &dyn Fn(u64) -> Settings, secs: u64) -> Settings {
        let mut env = Settings {
            enabled: false,
            window: TimeWindow::Core,
            cap: DailyCap::One,
        };
        for s in 0..secs {
            let x = h(s);
            env.enabled |= x.enabled;
            if x.window.range().0 < env.window.range().0 {
                env.window = x.window;
            }
            if x.cap.count() > env.cap.count() {
                env.cap = x.cap;
            }
        }
        env
    }

    /// 非停滞が 61 秒以上続いている秒（停滞の区間が終わり、表示中の招待も無い）。
    fn quiet_seconds(sc: &[f64]) -> Vec<bool> {
        let mut out = vec![false; sc.len()];
        let mut low_run = 0u64;
        for (i, &p) in sc.iter().enumerate() {
            low_run = if p < TRIGGER_P_STUCK { low_run + 1 } else { 0 };
            out[i] = low_run > (EPISODE_END_HOLD_MS + SEC) / SEC;
        }
        out
    }

    /// ADR-035 Migration 1 ①: **設定の変更は状態に跡を残さない**。
    ///
    /// 停滞の区間の外（招待が出えない間）でだけ設定を替えた履歴は、ずっと同じ設定の場合と
    /// 提示の時刻が完全に一致する。⚠️ 区間の中で設定が違えば提示が違うのは当然なので、比べない
    /// （そこは ② が「広い外枠を超えない」で縛る）。
    #[test]
    fn settings_changes_leave_no_trace() {
        for seed in 0..40u64 {
            let sc = scenario(seed);
            let quiet = quiet_seconds(&sc);
            let p = |s: u64| sc[s as usize];
            let h = history(seed);
            for current in [Settings::default(), core(), widest()] {
                let constant = run_from(HIST_START_MIN, &p, &|_| current, sc.len() as u64);
                let with_history = run_from(
                    HIST_START_MIN,
                    &p,
                    &|s| if quiet[s as usize] { h(s) } else { current },
                    sc.len() as u64,
                );
                assert_eq!(with_history, constant, "seed {seed} ({current:?})");
            }
        }
    }

    /// ADR-035 Migration 1 ②: 広げた・狭めた・止めた履歴で出す量は、履歴の中で使った最も広い設定で
    /// 最初から動かした場合を超えない（広げたことが控えを解かない）。
    #[test]
    fn settings_history_never_exceeds_its_widest_envelope() {
        for seed in 0..40u64 {
            let sc = scenario(seed);
            let p = |s: u64| sc[s as usize];
            let h = history(seed);
            let env = envelope(&h, sc.len() as u64);
            let wide = run_from(HIST_START_MIN, &p, &|_| env, sc.len() as u64);
            let with_history = run_from(HIST_START_MIN, &p, &h, sc.len() as u64);
            assert!(
                with_history.len() <= wide.len(),
                "seed {seed}: 履歴つき {} > 外枠の和で最初から {} ({env:?})",
                with_history.len(),
                wide.len()
            );
        }
    }

    /// ③ 設定の変更で控え（間隔・1 区間 1 回）が解けない。
    #[test]
    fn changing_settings_does_not_lift_the_restraint() {
        let mut m = InvitationMachine::new();
        let mut presented = Vec::new();
        for s in 0..1200u64 {
            let settings = match s {
                40..=49 => Settings {
                    enabled: false,
                    ..widest()
                },
                _ if s % 100 < 50 => widest(),
                _ => Settings::default(),
            };
            if m.tick(&input(T0 + s * SEC, 0.9, settings)).presented {
                presented.push(s);
            }
        }
        assert_eq!(
            presented,
            vec![30],
            "止めて戻しても、同じ区間・間隔の中では出し直さない"
        );
    }

    /// 「広げた・戻したら控えを解く」偽の実装（陽性対照用）。
    #[derive(Default)]
    struct Leaky {
        inner: InvitationMachine,
        prev: Option<Settings>,
    }

    impl Leaky {
        fn tick(&mut self, i: &TickInput) -> TickOutput {
            if let Some(prev) = self.prev {
                let widened = i.settings.window.range().1 > prev.window.range().1
                    || i.settings.cap.count() > prev.cap.count()
                    || (i.settings.enabled && !prev.enabled);
                if widened {
                    // ⚠️ 広げたことを「受容」とみなして控えを解く —— ADR-035 D4 違反
                    self.inner.next_allowed_at = 0;
                    self.inner.episode_used = false;
                    self.inner.count_today = 0;
                }
            }
            self.prev = Some(i.settings);
            self.inner.tick(i)
        }
    }

    fn run_leaky(
        p: &dyn Fn(u64) -> f64,
        settings: &dyn Fn(u64) -> Settings,
        secs: u64,
    ) -> Vec<u64> {
        let mut m = Leaky::default();
        (0..secs)
            .filter(|&s| {
                m.tick(&input_from(HIST_START_MIN, T0 + s * SEC, p(s), settings(s)))
                    .presented
            })
            .collect()
    }

    /// 陽性対照: 偽の実装なら ① か ② が赤になる（検査が空回りしていないこと）。
    #[test]
    fn positive_control_a_machine_that_rewards_widening_is_caught() {
        let mut caught_1 = false;
        let mut caught_2 = false;
        for seed in 0..40u64 {
            let sc = scenario(seed);
            let quiet = quiet_seconds(&sc);
            let p = |s: u64| sc[s as usize];
            let h = history(seed);
            let n = sc.len() as u64;
            for current in [Settings::default(), core(), widest()] {
                let constant = run_from(HIST_START_MIN, &p, &|_| current, n);
                let leaky = run_leaky(&p, &|s| if quiet[s as usize] { h(s) } else { current }, n);
                caught_1 |= leaky != constant;
            }
            let env = envelope(&h, n);
            caught_2 |=
                run_leaky(&p, &h, n).len() > run_from(HIST_START_MIN, &p, &|_| env, n).len();
        }
        assert!(
            caught_1,
            "陽性対照が ① で赤にならない（検査が空回りしている）"
        );
        assert!(
            caught_2,
            "陽性対照が ② で赤にならない（検査が空回りしている）"
        );
    }

    /// 繰り越さない: 時間帯の外で契機を満たした区間は、時間帯に入っても出さない（判断 6 #2）。
    #[test]
    fn a_stall_triggered_outside_the_window_is_not_carried_over() {
        // 8:59:00 から停滞（契機は 8:59:30・時間帯 9–18 の外）。9:00 を越えても出さない。
        let got = run_from(8 * 60 + 59, &|_| 0.9, &|_| core(), 600);
        assert!(got.is_empty(), "{got:?}");
        // 対照: 9:00:00 から停滞なら 9:00:30 に出る
        assert_eq!(run_from(9 * 60, &|_| 0.9, &|_| core(), 600), vec![30]);
    }

    /// 繰り越さない: 間隔の中で契機を満たした区間は、間隔が明けても出さない。
    #[test]
    fn a_stall_triggered_inside_the_gap_is_not_carried_over() {
        // 1 回目は 30 秒目。区間を終え（2 分の非停滞）、間隔の中（例: 30 分目）から長い停滞を始める。
        let second_start = 30 * 60u64;
        let p = |s: u64| {
            if s < 120 || s >= second_start {
                0.9
            } else {
                0.1
            }
        };
        let got = run(&p, &|_| widest(), 2 * 3600);
        assert_eq!(
            got,
            vec![30],
            "間隔が明けた 31 分目に、続いている区間を出さない"
        );
    }

    /// 時計が前の日へ戻って、また進んでも、1 日の上限を数え直さない。
    #[test]
    fn going_back_a_day_does_not_reset_the_daily_count() {
        let mut m = InvitationMachine::new();
        let mut n = 0;
        for s in 0..(6 * 3600u64) {
            let mut i = input(
                T0 + s * SEC,
                alternating(s),
                Settings {
                    cap: DailyCap::One,
                    ..widest()
                },
            );
            i.local_day = if (s / 600) % 2 == 0 { 100 } else { 99 };
            i.minute_of_day = TEN;
            if m.tick(&i).presented {
                n += 1;
            }
        }
        assert_eq!(n, 1);
    }

    /// 記録の一時停止中は出さず、止めた tick で閉じる（判断 6 #1）。
    #[test]
    fn recording_pause_blocks_and_closes() {
        let mut m = InvitationMachine::new();
        for s in 0..120u64 {
            let mut i = input(T0 + s * SEC, 0.9, widest());
            i.recording_active = false;
            assert!(!m.tick(&i).presented, "停止中は出さない");
        }
        let mut m = InvitationMachine::new();
        for s in 0..31u64 {
            m.tick(&input(T0 + s * SEC, 0.9, widest()));
        }
        assert!(m.is_present());
        let mut i = input(T0 + 31 * SEC, 0.9, widest());
        i.recording_active = false;
        assert!(!m.tick(&i).present, "止めた tick で閉じる");
    }

    /// ADR-026 PC-12 / ADR-035 D1: 許す状態で停滞が続けば必ず出る（no-op を合格にしない）。
    #[test]
    fn presents_when_everything_allows_it() {
        assert_eq!(run(&|_| 0.9, &|_| Settings::default(), 60), vec![30]);
    }

    #[test]
    fn nan_p_stuck_is_not_a_stall() {
        assert!(run(&|_| f64::NAN, &|_| widest(), 120).is_empty());
    }

    /// 段の契機で、p_stuck の列（1 秒 1 値）を流し、提示と契機の時刻を返す。
    fn run_trigger(trigger: Trigger, p: &dyn Fn(u64) -> f64, secs: u64) -> (Vec<u64>, Vec<u64>) {
        let mut m = InvitationMachine::with_trigger(trigger);
        let (mut presented, mut triggered) = (Vec::new(), Vec::new());
        for s in 0..secs {
            let out = m.tick(&input(T0 + s * SEC, p(s), widest()));
            if out.presented {
                presented.push(s);
            }
            if out.triggered {
                triggered.push(s);
            }
        }
        (presented, triggered)
    }

    /// 試作の段（`.steering/20261012-eh3-trigger-values/`）は本番より出やすい側にある。
    #[test]
    #[allow(clippy::assertions_on_constants)] // 段の値は定数。書き換えたときに落とすための検査
    fn the_proto_stage_is_easier_than_main() {
        assert_eq!(InvitationMachine::new().trigger, Trigger::MAIN);
        assert_eq!(Trigger::default(), Trigger::MAIN);
        assert_eq!(Trigger::MAIN.p_stuck, 0.60);
        assert_eq!(Trigger::MAIN.hold_ms, 30_000);
        assert!(Trigger::PROTO.p_stuck <= Trigger::MAIN.p_stuck);
        assert!(Trigger::PROTO.hold_ms <= Trigger::MAIN.hold_ms);
        assert_ne!(Trigger::PROTO, Trigger::MAIN);
    }

    /// 境界: 閾値ちょうどが継続ちょうど続いた tick で出る。1 秒短い・閾値をわずかに下回るなら出ない。
    #[test]
    fn each_stage_presents_exactly_at_its_threshold_and_hold() {
        for trigger in [Trigger::MAIN, Trigger::PROTO] {
            let hold = trigger.hold_ms / SEC;
            let at = trigger.p_stuck;
            let (got, trig) = run_trigger(trigger, &|s| if s >= 10 { at } else { 0.0 }, 200);
            assert_eq!(
                got,
                vec![10 + hold],
                "{trigger:?}: 閾値ちょうどが継続ちょうど"
            );
            assert_eq!(trig, got, "{trigger:?}: 出せるときは契機と提示が同じ tick");
            let (got, trig) = run_trigger(
                trigger,
                &|s| {
                    if (10..10 + hold).contains(&s) {
                        at
                    } else {
                        0.0
                    }
                },
                200,
            );
            assert!(
                got.is_empty() && trig.is_empty(),
                "{trigger:?}: 1 秒足りない"
            );
            let below = at - 1e-9;
            let (got, _) = run_trigger(trigger, &|_| below, 200);
            assert!(got.is_empty(), "{trigger:?}: 閾値をわずかに下回る");
        }
    }

    /// 段の値の違いが提示に届く: 試作の段だけが届く列で、本番は出さない。
    #[test]
    #[allow(clippy::assertions_on_constants)]
    fn a_stall_only_proto_reaches_is_not_presented_on_main() {
        let p = Trigger::PROTO.p_stuck;
        let hold = Trigger::PROTO.hold_ms / SEC;
        let (proto, _) = run_trigger(Trigger::PROTO, &|_| p, 120);
        assert_eq!(proto, vec![hold]);
        // 試作の段は閾値も継続も本番より緩い（前提が崩れたら黙って飛ばさずに落とす）
        assert!(p < Trigger::MAIN.p_stuck && hold < Trigger::MAIN.hold_ms / SEC);
        assert!(run_trigger(Trigger::MAIN, &|_| p, 120).0.is_empty());
        let (main, _) = run_trigger(
            Trigger::MAIN,
            &|s| if s < hold + 1 { 0.9 } else { 0.0 },
            120,
        );
        assert!(main.is_empty());
    }

    /// 区間の終わりも段の閾値で決まる: 閾値以上（本番の閾値未満）の間は区間が続き、2 回目を出さない。
    #[test]
    fn the_episode_ends_by_the_stage_threshold() {
        let t = Trigger::PROTO;
        let hold = t.hold_ms / SEC;
        // 閾値ちょうどのまま 40 分続ける（間隔が明けても区間は終わらない）
        let (got, trig) = run_trigger(t, &|_| t.p_stuck, 2400);
        assert_eq!(got, vec![hold], "区間が続く限り 1 回");
        assert_eq!(trig, vec![hold]);
        // 契機の後、閾値を下回る 60 秒で区間が閉じ、間隔の後に新しい区間で出る
        let gap_end = hold + (EXPIRY_MS + GAP_AFTER_CLOSE_MS) / SEC;
        let p = |s: u64| {
            if s <= hold || s > gap_end {
                0.9
            } else {
                t.p_stuck - 0.01
            }
        };
        let (got, _) = run_trigger(t, &p, gap_end + hold + 5);
        assert_eq!(got, vec![hold, gap_end + 1 + hold]);
    }

    // ---- 契機の種類（ADR-040 D4・タスク B） ----

    /// 契機の種類を指定して 1 秒 1 tick で流し、(提示, 契機) の時刻（T0 からの秒）を返す。
    fn run_kind(
        kind: TriggerKind,
        p: &dyn Fn(u64) -> f64,
        mutate: &dyn Fn(u64, &mut TickInput),
        secs: u64,
    ) -> (Vec<u64>, Vec<u64>) {
        let mut m = InvitationMachine::with_kind(kind);
        let (mut shown, mut trig) = (Vec::new(), Vec::new());
        for s in 0..secs {
            let mut i = input(T0 + s * SEC, p(s), widest());
            mutate(s, &mut i);
            let out = m.tick(&i);
            if out.presented {
                shown.push(s);
            }
            if out.triggered {
                trig.push(s);
            }
        }
        (shown, trig)
    }

    fn nothing(_: u64, _: &mut TickInput) {}

    const RISING: TriggerKind = TriggerKind::Rising {
        delta: 0.3,
        window_ms: 10_000,
    };

    #[test]
    fn estimator_kind_equals_the_legacy_machine() {
        let p = |s: u64| if (10..300).contains(&s) { 0.9 } else { 0.1 };
        let (a, ta) = run_kind(Trigger::MAIN.into(), &p, &nothing, 4000);
        let (b, tb) = run_trigger(Trigger::MAIN, &p, 4000);
        assert_eq!((a, ta), (b, tb));
        assert_eq!(TriggerKind::default(), Trigger::MAIN.into());
    }

    #[test]
    fn rising_fires_on_the_rising_edge_only() {
        // 0.1 → 0.8 に 20 秒目で上がる。10 秒前の 0.1 との差 0.7 ≥ 0.3 が 20 秒目に真になる
        let p = |s: u64| if s >= 20 { 0.8 } else { 0.1 };
        let (shown, trig) = run_kind(RISING, &p, &nothing, 100);
        assert_eq!(trig, vec![20]);
        assert_eq!(shown, vec![20]);
        // 上がった後 10 秒たつと差が 0 になり偽へ。真の間は立ち直さない（20..30 は 1 回）
        let (_, trig) = run_kind(RISING, &p, &nothing, 29);
        assert_eq!(trig.len(), 1);
    }

    #[test]
    fn rising_does_not_fire_without_a_rise_or_a_full_window() {
        // 高いまま始まる（窓が埋まる前は基準が無い）・上がり幅が足りない
        let (_, trig) = run_kind(RISING, &|_| 0.9, &nothing, 200);
        assert!(trig.is_empty(), "平らな高さでは立たない: {trig:?}");
        let (_, trig) = run_kind(RISING, &|s| if s >= 20 { 0.35 } else { 0.1 }, &nothing, 100);
        assert!(trig.is_empty(), "差 0.25 < 0.3: {trig:?}");
        let (_, trig) = run_kind(RISING, &|s| if s >= 3 { 0.9 } else { 0.0 }, &nothing, 100);
        // 3 秒目の上がりは窓（10 秒）が埋まる前。10 秒目に基準（t=0 の 0.0）との差で立つ
        assert_eq!(trig, vec![10], "{trig:?}");
    }

    #[test]
    fn rising_re_arms_after_falling() {
        let p = |s: u64| {
            if (20..40).contains(&s) || s >= 200 {
                0.8
            } else {
                0.1
            }
        };
        let (_, trig) = run_kind(RISING, &p, &nothing, 300);
        assert_eq!(trig, vec![20, 200]);
    }

    #[test]
    fn rising_is_blocked_while_away_and_at_boundaries() {
        let p = |s: u64| if s >= 20 { 0.8 } else { 0.1 };
        let away = |s: u64, i: &mut TickInput| {
            if (15..60).contains(&s) {
                i.idle_ms = AWAY_IDLE_MS;
            }
        };
        let (_, trig) = run_kind(RISING, &p, &away, 100);
        // 離席候補の間は立たず、履歴も捨てる。離席が明けた 60 秒目の後、窓が埋まる 70 秒目の差は 0
        assert!(trig.is_empty(), "{trig:?}");
        let boundary = |s: u64, i: &mut TickInput| i.session_boundary = s == 18;
        let (_, trig) = run_kind(RISING, &p, &boundary, 100);
        // 区切り（18 秒）で履歴を捨てる。新しい基準は 19 秒の 0.1 で、窓が埋まる 29 秒に差 0.7 で立つ
        assert_eq!(trig, vec![29], "{trig:?}");
    }

    #[test]
    fn rising_treats_nan_as_zero() {
        let (_, trig) = run_kind(
            RISING,
            &|s| if s >= 20 { f64::NAN } else { 0.1 },
            &nothing,
            60,
        );
        assert!(trig.is_empty());
    }

    const RANDOM: TriggerKind = TriggerKind::Random {
        per_active_hour: 6.0,
        seed: 42,
    };

    #[test]
    fn random_is_reproducible_from_the_seed() {
        let (_, a) = run_kind(RANDOM, &|_| 0.0, &nothing, 20_000);
        let (_, b) = run_kind(RANDOM, &|_| 0.0, &nothing, 20_000);
        assert_eq!(a, b, "同じ seed は同じ列");
        let other = TriggerKind::Random {
            per_active_hour: 6.0,
            seed: 43,
        };
        let (_, c) = run_kind(other, &|_| 0.0, &nothing, 20_000);
        assert_ne!(a, c, "seed が違えば列も違う");
        // 推定の p_stuck には依らない
        let (_, d) = run_kind(RANDOM, &|_| 0.9, &nothing, 20_000);
        assert_eq!(a, d);
    }

    #[test]
    fn random_rate_matches_per_active_hour() {
        // 6 回/時 × 約 55 時間 ≈ 330 回（二項分布の標準偏差 ≈ 18 → 6σ の幅）
        let secs = 200_000;
        let (_, trig) = run_kind(RANDOM, &|_| 0.0, &nothing, secs);
        let expect = 6.0 * secs as f64 / 3600.0;
        assert!(
            (trig.len() as f64 - expect).abs() < 110.0,
            "{} 回（期待 {expect}）",
            trig.len()
        );
    }

    #[test]
    fn random_skips_away_and_boundary_ticks() {
        let always_away = |_: u64, i: &mut TickInput| i.idle_ms = AWAY_IDLE_MS;
        let (_, trig) = run_kind(RANDOM, &|_| 0.0, &always_away, 20_000);
        assert!(trig.is_empty(), "離席候補の間は立たない");
        let always_boundary = |_: u64, i: &mut TickInput| i.session_boundary = true;
        let (_, trig) = run_kind(RANDOM, &|_| 0.0, &always_boundary, 20_000);
        assert!(trig.is_empty(), "区切りの tick では立たない");
    }

    #[test]
    fn random_scales_with_elapsed_seconds() {
        // 5 秒間隔の tick は 1 回あたりの確率が 5 倍（時あたりの回数は同じ）
        let mut m = InvitationMachine::with_kind(RANDOM);
        let mut n = 0u32;
        let ticks = 40_000u64;
        for k in 0..ticks {
            let i = input(T0 + k * 5 * SEC, 0.0, widest());
            if m.tick(&i).triggered {
                n += 1;
            }
        }
        let expect = 6.0 * (ticks * 5) as f64 / 3600.0;
        assert!((n as f64 - expect).abs() < 110.0, "{n} 回（期待 {expect}）");
    }

    #[test]
    fn random_trigger_obeys_the_shared_rules() {
        // 立った瞬間に出せなければ出さない（1 日の上限 2 のあと立っても出ない）・間隔の 30 分を守る
        let mut m = InvitationMachine::with_kind(TriggerKind::Random {
            per_active_hour: 60.0,
            seed: 7,
        });
        let mut shown = Vec::new();
        for s in 0..(4 * 3600u64) {
            let i = input(T0 + s * SEC, 0.0, Settings::default());
            if m.tick(&i).presented {
                shown.push(s);
            }
        }
        assert_eq!(shown.len(), 2, "既定の上限 2: {shown:?}");
        assert!(shown[1] - shown[0] >= (EXPIRY_MS + GAP_AFTER_CLOSE_MS) / SEC);
    }

    #[test]
    fn off_never_fires() {
        let (shown, trig) = run_kind(TriggerKind::Off {}, &|_| 0.99, &nothing, 5000);
        assert!(shown.is_empty() && trig.is_empty());
    }

    #[test]
    fn invalid_kind_becomes_off() {
        for bad in [
            TriggerKind::Rising {
                delta: 0.0,
                window_ms: 1000,
            },
            TriggerKind::Random {
                per_active_hour: 0.0,
                seed: 1,
            },
            TriggerKind::Estimator {
                p_stuck: f64::NAN,
                hold_ms: 1000,
            },
        ] {
            let (shown, trig) = run_kind(bad, &|_| 0.99, &nothing, 5000);
            assert!(shown.is_empty() && trig.is_empty(), "{bad:?}");
        }
    }

    #[test]
    fn trigger_kind_json_is_fail_closed() {
        let ok = |t: &str| TriggerKind::from_json(t);
        assert_eq!(
            ok(r#"{"kind":"estimator","p_stuck":0.6,"hold_ms":30000}"#),
            Some(Trigger::MAIN.into())
        );
        assert_eq!(
            ok(r#"{"kind":"rising","delta":0.3,"window_ms":10000}"#),
            Some(RISING)
        );
        assert_eq!(
            ok(r#"{"kind":"random","per_active_hour":6,"seed":42}"#),
            Some(RANDOM)
        );
        assert_eq!(ok(r#"{"kind":"none"}"#), Some(TriggerKind::Off {}));
        for bad in [
            "",
            "not json",
            "{}",
            r#"{"kind":"unknown"}"#,
            // 欠けた値
            r#"{"kind":"rising","delta":0.3}"#,
            r#"{"kind":"random","seed":1}"#,
            r#"{"kind":"random","per_active_hour":6}"#,
            r#"{"kind":"estimator","p_stuck":0.6}"#,
            // 未知の欄
            r#"{"kind":"none","extra":1}"#,
            r#"{"kind":"rising","delta":0.3,"window_ms":1000,"x":1}"#,
            // 範囲外
            r#"{"kind":"rising","delta":-0.1,"window_ms":1000}"#,
            r#"{"kind":"rising","delta":1.5,"window_ms":1000}"#,
            r#"{"kind":"rising","delta":0.3,"window_ms":0}"#,
            r#"{"kind":"random","per_active_hour":0,"seed":1}"#,
            r#"{"kind":"random","per_active_hour":-1,"seed":1}"#,
            r#"{"kind":"random","per_active_hour":61,"seed":1}"#,
            r#"{"kind":"estimator","p_stuck":0,"hold_ms":1000}"#,
            r#"{"kind":"estimator","p_stuck":1.5,"hold_ms":1000}"#,
        ] {
            assert_eq!(ok(bad), None, "{bad:?}");
        }
    }

    #[test]
    fn condition_names_are_closed() {
        assert_eq!(TriggerKind::default().condition_name(), "estimator");
        assert_eq!(RISING.condition_name(), "rising");
        assert_eq!(RANDOM.condition_name(), "random");
        assert_eq!(TriggerKind::Off {}.condition_name(), "none");
    }

    #[test]
    fn splitmix64_matches_the_reference_vector() {
        // 参照実装（seed = 0）の先頭 2 値
        let mut r = SplitMix64(0);
        assert_eq!(r.next_u64(), 0xE220_A839_7B1D_CDAF);
        assert_eq!(r.next_u64(), 0x6E78_9E6A_A1B9_65F4);
    }
}
