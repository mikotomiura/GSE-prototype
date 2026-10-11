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

/// 契機の `p_stuck` の閾値。Nudge と同じ値（較正中の推定に新しい値を足さない・design §6）。
pub const TRIGGER_P_STUCK: f64 = 0.60;
/// 契機の持続（`p_stuck ≥ 閾値` が続く長さ）。
pub const TRIGGER_HOLD_MS: u64 = 30_000;
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
}

/// 招待の状態機械。
#[derive(Debug, Clone, Default)]
pub struct InvitationMachine {
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
    pub fn new() -> Self {
        Self::default()
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

        let triggered = self.track_episode(input);

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
        }
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
        if p >= TRIGGER_P_STUCK {
            self.below_since = None;
            let since = *self.stuck_since.get_or_insert(now);
            if !self.in_episode && now.saturating_sub(since) >= TRIGGER_HOLD_MS {
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
        assert_eq!(
            run_from(9 * 60, &|_| 0.9, &|_| core(), 600),
            vec![30]
        );
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
}
