//! 手跡（段 1 の後期・ADR-051）の駆動役の純粋な部分（`s1_driver.rs` の作法）。
//!
//! Tauri・logger・OS API を持たない。IO は `HandmarkFs`（1a）越し。`lib.rs` の駆動スレッド（250 ms）と
//! コマンド・トレイが、ここが返す [`Effect`] を行・窓・トレイに変える。
//!
//! 設計の一次は `.steering/20261108-handmark-stage1-late-pr1/design-1b.md` §1。
//!
//! ## 時刻
//!
//! 打鍵の時刻（`InputEvent` の `timestamp`）と `now` は同じ時計（UTC の ms）。状態は「`now − 500 ms`」までしか
//! 進めない（判断 7-3）。届いた打鍵は時刻の順に溜め、進めるときに入れる。500 ms 以内の遅れなら、記録の打鍵から
//! `analysis::handmark::state::replay_live` で再現した状態と `to_bits` で一致する。

use crate::analysis::handmark::assignment::Assigned;
use crate::analysis::handmark::gate::{CloseReason, Decision, RECHECK_MS};
use crate::analysis::handmark::state::{Stage, StageState, LIVE_LAG_MS};
use crate::handmark_store::{scrub_state_file, turn_off, turn_on, Evaluation, HandmarkFs};
use crate::logger::HandmarkDayRow;

/// 行を書く間隔（その日の累計の写し）。
pub const ROW_MS: u64 = 300_000;
/// 刻みの間隔がこれを超えたら時計の飛びとみなす（1 日）。
pub const CLOCK_JUMP_MS: u64 = 86_400_000;
/// 刻みの間がこれを超えたら、その間は出ていた時間に足さない(スリープ)。
pub const SLEEP_GAP_MS: u64 = 2_000;
/// 溜める打鍵の上限（駆動スレッドが止まっていても膨らまないように）。
const MAX_PENDING: usize = 8192;

/// トレイの項目。手跡の語と状態の名前は被験者に見せない（文言は「やめる」／「描く」）。
#[derive(Debug, Clone, Copy, PartialEq, Eq)]
pub enum TrayItem {
    Hidden,
    /// 出ているので「やめる」。
    Stop,
    /// 今日は切ってあるので「描く」。
    Restore,
}

impl TrayItem {
    /// メニューの文言（`Hidden` は出さない）。
    pub fn label(self) -> Option<&'static str> {
        match self {
            TrayItem::Hidden => None,
            TrayItem::Stop => Some("やめる"),
            TrayItem::Restore => Some("描く"),
        }
    }
}

/// 窓の層が知らせる窓の様子(窓を作れない・出せないときは `Failed`)。
#[derive(Debug, Clone, Copy, PartialEq, Eq)]
pub enum WindowStatus {
    /// まだ分からない(出す依頼の直後)。
    Pending,
    /// 窓が出た。
    Shown,
    /// 窓を作れなかった・出せなかった。
    Failed,
}

/// 駆動役の出来事。
#[derive(Debug, Clone, PartialEq)]
pub enum Effect {
    OpenWindow { layout_seed: u32 },
    CloseWindow,
    State(StageState),
    Row(HandmarkDayRow),
    TrayItem(TrayItem),
}

/// 出来事の行き先。
#[derive(Debug, Clone, Copy, PartialEq, Eq)]
pub enum Destination {
    /// 記録（NDJSON）。
    Log,
    Window,
    Tray,
}

impl Effect {
    /// ★ 記録へ向かうのは `Row` だけ（網羅の match なので、足すと必ずここで決めることになる）。
    pub fn destination(&self) -> Destination {
        match self {
            Effect::Row(_) => Destination::Log,
            Effect::OpenWindow { .. } | Effect::CloseWindow | Effect::State(_) => {
                Destination::Window
            }
            Effect::TrayItem(_) => Destination::Tray,
        }
    }
}

/// 今日の評価から、トレイの項目を決める（出す日でない日に止める・戻すは意味を持たない）。
pub fn tray_item(ev: &Evaluation) -> TrayItem {
    match ev.decision {
        Decision::Open { .. } => TrayItem::Stop,
        Decision::Closed {
            reason: CloseReason::OffToday,
            assigned: Some(Assigned::LateFirst | Assigned::On),
        } => TrayItem::Restore,
        _ => TrayItem::Hidden,
    }
}

/// 駆動役。
pub struct HandmarkDriver {
    ev: Evaluation,
    s1_mode: bool,
    stage: Option<Stage>,
    /// 今の `Stage` の起点（これより前の打鍵は入れない・再生と同じ）。
    stage_t0: u64,
    pending: Vec<u64>,
    window_open: bool,
    /// 窓の層が「出た」と知らせた(それまでは出ていた時間を積まない)。
    window_confirmed: bool,
    last_recheck_ms: u64,
    last_row_ms: u64,
    last_tick_ms: u64,
    last_tray: TrayItem,
}

impl HandmarkDriver {
    /// 起動。門を評価し、行を出し、開いていれば窓を開く。
    pub fn new(fs: &dyn HandmarkFs, s1_mode: bool, now: u64, today: i64) -> (Self, Vec<Effect>) {
        let ev = Evaluation::run(fs, s1_mode, today, None);
        let mut d = Self {
            ev,
            s1_mode,
            stage: None,
            stage_t0: now,
            pending: Vec::new(),
            window_open: false,
            window_confirmed: false,
            last_recheck_ms: now,
            last_row_ms: now,
            last_tick_ms: now,
            last_tray: TrayItem::Hidden,
        };
        let mut fx = Vec::new();
        d.push_row(now, &mut fx);
        if d.ev.is_open() {
            d.open_window(now, &mut fx);
        }
        d.sync_tray(&mut fx);
        (d, fx)
    }

    pub fn is_window_open(&self) -> bool {
        self.window_open
    }

    pub fn today(&self) -> i64 {
        self.ev.today
    }

    pub fn evaluation(&self) -> &Evaluation {
        &self.ev
    }

    pub fn tray(&self) -> TrayItem {
        self.last_tray
    }

    /// 打鍵の時刻を溜めるだけ（窓が出ていないときは捨てる）。
    pub fn on_press(&mut self, t: u64) {
        if self.window_open && self.pending.len() < MAX_PENDING {
            self.pending.push(t);
        }
    }

    fn push_row(&self, now: u64, fx: &mut Vec<Effect>) {
        if let Some(r) = self.ev.row(now) {
            fx.push(Effect::Row(r));
        }
    }

    fn sync_tray(&mut self, fx: &mut Vec<Effect>) {
        let t = tray_item(&self.ev);
        if t != self.last_tray {
            self.last_tray = t;
            fx.push(Effect::TrayItem(t));
        }
    }

    fn new_stage(&mut self, now: u64) {
        let seed = self.ev.draw_seed().unwrap_or(0);
        self.stage = Some(Stage::new(seed, now));
        self.stage_t0 = now;
        self.pending.clear();
        self.ev.note_stage_start(now);
    }

    fn open_window(&mut self, now: u64, fx: &mut Vec<Effect>) {
        self.new_stage(now);
        self.window_open = true;
        self.window_confirmed = false;
        self.last_tick_ms = now;
        let layout_seed = self.stage.as_ref().map_or(0, |s| s.state().layout_seed);
        fx.push(Effect::OpenWindow { layout_seed });
    }

    fn close_window(&mut self, fx: &mut Vec<Effect>) {
        self.window_open = false;
        self.window_confirmed = false;
        self.stage = None;
        self.pending.clear();
        fx.push(Effect::CloseWindow);
    }

    /// 門の結果に窓を合わせる。
    fn reconcile(&mut self, now: u64, fx: &mut Vec<Effect>) {
        let open = self.ev.is_open();
        if self.window_open && !open {
            self.close_window(fx);
        } else if !self.window_open && open {
            self.open_window(now, fx);
        }
        self.sync_tray(fx);
    }

    fn recheck(&mut self, fs: &dyn HandmarkFs, now: u64, today: i64, fx: &mut Vec<Effect>) {
        let prior = self.ev.record.clone();
        self.ev = Evaluation::run(fs, self.s1_mode, today, prior);
        self.last_recheck_ms = now;
        self.reconcile(now, fx);
    }

    /// 250 ms ごとに呼ぶ。
    pub fn tick(&mut self, fs: &dyn HandmarkFs, now: u64, today: i64) -> Vec<Effect> {
        let mut fx = Vec::new();
        let jumped = now < self.last_tick_ms || now - self.last_tick_ms > CLOCK_JUMP_MS;
        let day_changed = today != self.ev.today;
        let prev_tick = self.last_tick_ms;
        self.last_tick_ms = now;

        if day_changed {
            // 前の日の最後の行 → 門を検め直す → 新しい日の最初の行
            self.push_row(now, &mut fx);
            let was_open = self.window_open;
            self.recheck(fs, now, today, &mut fx);
            if was_open && self.window_open {
                // 描画の種は日で変わる。取り直して新しい日の起点を残す。
                self.new_stage(now);
                let layout_seed = self.stage.as_ref().map_or(0, |s| s.state().layout_seed);
                fx.push(Effect::OpenWindow { layout_seed });
            }
            self.push_row(now, &mut fx);
            self.last_row_ms = now;
        } else if jumped && self.window_open {
            // 時計の飛び（スリープからの復帰もここ）: 起点を取り直す。溜めた打鍵は捨てる。
            self.new_stage(now);
        }
        let recheck_due =
            now.saturating_sub(self.last_recheck_ms) >= RECHECK_MS || now < self.last_recheck_ms;
        if !day_changed && recheck_due {
            self.recheck(fs, now, today, &mut fx);
        }

        if self.window_open {
            let target = now.saturating_sub(LIVE_LAG_MS);
            if let Some(stage) = self.stage.as_mut() {
                let mut due: Vec<u64> = Vec::new();
                self.pending.retain(|&p| {
                    if p <= target {
                        due.push(p);
                        false
                    } else {
                        true
                    }
                });
                due.sort_unstable();
                for p in due {
                    if p >= self.stage_t0 {
                        stage.press(p);
                    }
                }
                stage.advance_to(target);
                fx.push(Effect::State(stage.state()));
            }
            // 窓が出たと分かってから、かつ 1 刻みの間が 2 秒以内のときだけ(スリープの間は足さない)
            let gap = now.saturating_sub(prev_tick);
            if self.window_confirmed && !jumped && !day_changed && gap <= SLEEP_GAP_MS {
                self.ev.add_shown(gap);
            }
        }

        if now.saturating_sub(self.last_row_ms) >= ROW_MS || now < self.last_row_ms {
            self.last_row_ms = now;
            if self.ev.record.is_some() && self.ev.save(fs).is_err() {
                self.ev.note_save_failed();
                self.reconcile(now, &mut fx);
            }
            self.push_row(now, &mut fx);
        }
        fx
    }

    /// トレイの「やめる」。
    pub fn turn_off(&mut self, fs: &dyn HandmarkFs, now: u64) -> Vec<Effect> {
        let mut fx = Vec::new();
        turn_off(fs, &mut self.ev, now);
        self.reconcile(now, &mut fx);
        self.push_row(now, &mut fx);
        fx
    }

    /// トレイの「描く」。戻せなければ出さないまま。
    pub fn turn_on(&mut self, fs: &dyn HandmarkFs, now: u64) -> Vec<Effect> {
        let mut fx = Vec::new();
        if turn_on(fs, &mut self.ev, now).is_ok() {
            self.reconcile(now, &mut fx);
            self.push_row(now, &mut fx);
        }
        fx
    }

    /// 窓の層の様子を受け取る(次の tick より前に呼ぶ)。`Failed` なら `window_unavailable` で閉じる。
    pub fn on_window_status(&mut self, status: WindowStatus, now: u64) -> Vec<Effect> {
        let mut fx = Vec::new();
        match status {
            WindowStatus::Pending => {}
            WindowStatus::Shown => {
                if self.window_open {
                    self.window_confirmed = true;
                }
            }
            WindowStatus::Failed => {
                if self.window_open {
                    self.ev.set_window_unavailable(true);
                    self.reconcile(now, &mut fx);
                    self.push_row(now, &mut fx);
                }
            }
        }
        fx
    }

    /// 区間の削除: 状態ファイルと走行中の累計から区間内の時刻を消す。書き直せなければ状態ファイルを消す。
    /// 消せなかったら `false`(呼び出し側が削除の結果に失敗を載せる)。後で `Stage` を取り直す。
    pub fn on_redact(
        &mut self,
        fs: &dyn HandmarkFs,
        from_ms: u64,
        to_ms: u64,
        now: u64,
    ) -> (Vec<Effect>, bool) {
        let mut fx = Vec::new();
        let ok = if self.ev.record.is_some() {
            if self.ev.scrub_state(fs, from_ms, to_ms).is_ok() {
                true
            } else {
                // 書けない: 状態ファイルを消す(切っていたなら印を残す)。走行中の累計は書けなかったと扱う
                if self.ev.record.as_ref().is_some_and(|r| r.off) {
                    let _ = fs.write_mark(self.ev.today);
                }
                self.ev.note_save_failed();
                self.reconcile(now, &mut fx);
                fs.remove_state().is_ok()
            }
        } else {
            // 状態ファイルが壊れていて累計が無い: ファイルを直接直す(壊れていれば消す)
            scrub_state_file(fs, from_ms, to_ms).is_ok()
        };
        if self.window_open {
            // 区間の後の起点を取り直す(消した起点を再生が必要としないように)
            self.new_stage(now);
        }
        (fx, ok)
    }

    /// 終了: 保存して最後の行。
    pub fn on_quit(&mut self, fs: &dyn HandmarkFs, now: u64) -> Vec<Effect> {
        let mut fx = Vec::new();
        if self.ev.record.is_some() && self.ev.save(fs).is_err() {
            self.ev.note_save_failed();
        }
        self.push_row(now, &mut fx);
        fx
    }
}

#[cfg(test)]
mod tests {
    use super::*;
    use crate::analysis::handmark::state::{replay_live, SplitMix64};
    use crate::handmark_store::testfs::{with_table, MemFs};

    const ON_DAY: i64 = 20_411;
    const OFF_DAY: i64 = 20_412;
    const NEXT_ON_DAY: i64 = 20_414;
    const T0: u64 = 1_800_000_000_000;

    fn has(fx: &[Effect], f: impl Fn(&Effect) -> bool) -> bool {
        fx.iter().any(f)
    }
    fn opened(fx: &[Effect]) -> bool {
        has(fx, |e| matches!(e, Effect::OpenWindow { .. }))
    }
    fn closed(fx: &[Effect]) -> bool {
        has(fx, |e| matches!(e, Effect::CloseWindow))
    }
    fn row_reason(fx: &[Effect]) -> Option<Option<&'static str>> {
        fx.iter().find_map(|e| match e {
            Effect::Row(r) => Some(r.reason),
            _ => None,
        })
    }

    #[test]
    fn start_opens_the_window_and_writes_a_row_on_an_open_day() {
        let fs = with_table();
        let (d, fx) = HandmarkDriver::new(&fs, true, T0, ON_DAY);
        assert!(d.is_window_open());
        assert!(opened(&fx));
        assert_eq!(row_reason(&fx), Some(None));
        assert!(has(&fx, |e| *e == Effect::TrayItem(TrayItem::Stop)));
    }

    #[test]
    fn start_stays_closed_and_says_why() {
        let fs = MemFs::default();
        let (d, fx) = HandmarkDriver::new(&fs, true, T0, ON_DAY);
        assert!(!d.is_window_open());
        assert!(!opened(&fx));
        assert_eq!(row_reason(&fx), Some(Some("table_missing")));
        assert_eq!(d.tray(), TrayItem::Hidden);
        // 出さない日にトレイの項目を出さない
        let fs = with_table();
        let (d, fx) = HandmarkDriver::new(&fs, true, T0, OFF_DAY);
        assert!(!opened(&fx) && d.tray() == TrayItem::Hidden);
        assert_eq!(row_reason(&fx), Some(Some("assigned_off")));
        // 段 1 でなければ行も窓も無い
        let (_, fx) = HandmarkDriver::new(&fs, false, T0, ON_DAY);
        assert!(fx.is_empty());
    }

    #[test]
    fn deleting_the_table_closes_the_window_at_the_next_recheck() {
        let fs = with_table();
        let (mut d, _) = HandmarkDriver::new(&fs, true, T0, ON_DAY);
        *fs.table.borrow_mut() = None;
        let mut now = T0;
        let mut closed_at = None;
        while now < T0 + 70_000 {
            now += 250;
            let fx = d.tick(&fs, now, ON_DAY);
            if closed(&fx) {
                closed_at = Some(now - T0);
                break;
            }
        }
        assert_eq!(closed_at, Some(60_000));
        assert!(!d.is_window_open());
    }

    #[test]
    fn turn_off_closes_and_the_next_open_day_opens_again() {
        let fs = with_table();
        let (mut d, _) = HandmarkDriver::new(&fs, true, T0, ON_DAY);
        let fx = d.turn_off(&fs, T0 + 1_000);
        assert!(closed(&fx));
        assert!(has(&fx, |e| *e == Effect::TrayItem(TrayItem::Restore)));
        assert_eq!(row_reason(&fx), Some(Some("off_today")));
        // 同じ日のうちは何度でも戻せる
        let fx = d.turn_on(&fs, T0 + 2_000);
        assert!(opened(&fx));
        assert!(has(&fx, |e| *e == Effect::TrayItem(TrayItem::Stop)));
        let _ = d.turn_off(&fs, T0 + 3_000);
        assert!(!d.is_window_open());
        // 翌日(割付が出す日の 20414)の tick で出る
        let day = 86_400_000;
        let fx = d.tick(&fs, T0 + day * 3, NEXT_ON_DAY);
        assert!(opened(&fx), "{fx:?}");
        // 出さない日の tick は閉じる・トレイは隠す
        let fx = d.tick(&fs, T0 + day * 4, NEXT_ON_DAY + 1);
        assert!(closed(&fx), "{fx:?}");
        assert!(!d.is_window_open());
        assert_eq!(d.tray(), TrayItem::Hidden);
        assert!(has(&fx, |e| *e == Effect::TrayItem(TrayItem::Hidden)));
        // 日が変わったので、前の日の最後の行の次に新しい日の最初の行が来る
        let last_reason = fx.iter().rev().find_map(|e| match e {
            Effect::Row(r) => Some(r.reason),
            _ => None,
        });
        assert_eq!(last_reason, Some(Some("after_table")));
    }

    #[test]
    fn day_change_writes_the_last_row_then_the_first_row() {
        let fs = with_table();
        let (mut d, _) = HandmarkDriver::new(&fs, true, T0, ON_DAY);
        let fx = d.tick(&fs, T0 + 250, ON_DAY + 3);
        let rows: Vec<&HandmarkDayRow> = fx
            .iter()
            .filter_map(|e| match e {
                Effect::Row(r) => Some(r),
                _ => None,
            })
            .collect();
        assert_eq!(rows.len(), 2);
        assert_eq!((rows[0].day, rows[1].day), (ON_DAY, ON_DAY + 3));
        // 窓は出たまま(新しい日の種で取り直す)
        assert!(d.is_window_open() && opened(&fx));
        assert!(!closed(&fx));
    }

    #[test]
    fn a_clock_jump_takes_a_new_origin_and_forgets_pending_presses() {
        let fs = with_table();
        let (mut d, _) = HandmarkDriver::new(&fs, true, T0, ON_DAY);
        d.on_press(T0 + 100);
        let _ = d.tick(&fs, T0 + 250, ON_DAY);
        let n0 = d.evaluation().record.as_ref().unwrap().stage_starts.len();
        // 後ろへ戻る
        d.on_press(T0 + 10_000);
        let _ = d.tick(&fs, T0 - 5_000, ON_DAY);
        let n1 = d.evaluation().record.as_ref().unwrap().stage_starts.len();
        assert_eq!(n1, n0 + 1);
        // 溜めていた打鍵は捨てた: 速さは 0 のまま
        let fx = d.tick(&fs, T0 - 4_750, ON_DAY);
        let st = fx.iter().find_map(|e| match e {
            Effect::State(s) => Some(*s),
            _ => None,
        });
        assert_eq!(st.unwrap().speed, 0.0);
        // 1 日を超えて前へ飛ぶ(スリープからの復帰)
        let _ = d.tick(&fs, T0 - 4_750 + 2 * 3_600_000 * 24 / 2 + 1, ON_DAY);
        let n2 = d.evaluation().record.as_ref().unwrap().stage_starts.len();
        assert_eq!(n2, n1 + 1);
        // 飛んだ間は表示の量に足さない
        assert!(d.evaluation().record.as_ref().unwrap().shown_ms < 10_000);
    }

    #[test]
    fn a_failed_periodic_save_closes_the_window() {
        let fs = with_table();
        let (mut d, _) = HandmarkDriver::new(&fs, true, T0, ON_DAY);
        let mut now = T0;
        // 5 分の直前まで進める(60 秒ごとの検め直しは書けるうちに通す)
        while now + 250 < T0 + ROW_MS {
            now += 250;
            let _ = d.tick(&fs, now, ON_DAY);
        }
        fs.fail_state_write.set(true);
        // 5 分の保存と検め直しが重なる刻みで閉じる
        let mut got_close = false;
        for _ in 0..400 {
            now += 250;
            let fx = d.tick(&fs, now, ON_DAY);
            if closed(&fx) {
                got_close = true;
                break;
            }
        }
        assert!(got_close);
        assert_eq!(
            d.evaluation().row(now).unwrap().reason,
            Some("state_unwritable")
        );
    }

    #[test]
    fn shown_time_accumulates_and_survives_in_the_five_minute_row() {
        let fs = with_table();
        let (mut d, _) = HandmarkDriver::new(&fs, true, T0, ON_DAY);
        let _ = d.on_window_status(WindowStatus::Shown, T0);
        let mut now = T0;
        let mut last_row = None;
        while now < T0 + ROW_MS + 1_000 {
            now += 250;
            for e in d.tick(&fs, now, ON_DAY) {
                if let Effect::Row(r) = e {
                    last_row = Some(r);
                }
            }
        }
        let r = last_row.expect("5 分の行");
        assert!(r.shown_ms >= ROW_MS - 500, "{}", r.shown_ms);
        assert_eq!(r.stage_starts, vec![T0]);
    }

    #[test]
    fn redact_scrubs_the_running_record_and_the_state_file() {
        let fs = with_table();
        let (mut d, _) = HandmarkDriver::new(&fs, true, T0, ON_DAY);
        let _ = d.turn_off(&fs, T0 + 1_000);
        let _ = d.turn_on(&fs, T0 + 2_000);
        let (_, ok) = d.on_redact(&fs, T0, T0 + 5_000, T0 + 6_000);
        assert!(ok);
        let rec = d.evaluation().record.as_ref().unwrap();
        assert!(rec.toggles.is_empty());
        assert!(rec.stage_starts.iter().all(|t| *t > T0 + 5_000));
        let (d2, fx) = HandmarkDriver::new(&fs, true, T0 + 7_000, ON_DAY);
        let row = fx.iter().find_map(|e| match e {
            Effect::Row(r) => Some(r.clone()),
            _ => None,
        });
        assert!(row.unwrap().toggles.is_empty());
        let _ = d2;
    }

    #[test]
    fn quit_saves_and_writes_the_last_row() {
        let fs = with_table();
        let (mut d, _) = HandmarkDriver::new(&fs, true, T0, ON_DAY);
        let _ = d.tick(&fs, T0 + 250, ON_DAY);
        let fx = d.on_quit(&fs, T0 + 1_000);
        assert_eq!(fx.len(), 1);
        assert!(matches!(fx[0], Effect::Row(_)));
    }

    /// ライブの tick の列(500 ms 以内に遅れて届く打鍵を含む)と、記録の打鍵からの再生が to_bits で一致する。
    #[test]
    fn live_ticks_match_the_replay_with_late_presses_in_200_cases() {
        for case in 0..200u64 {
            let fs = with_table();
            let (mut d, _) = HandmarkDriver::new(&fs, true, T0, ON_DAY);
            let seed = d.evaluation().draw_seed().unwrap();
            let mut r = SplitMix64::new(case + 1);
            // 打鍵(時刻 p・届く時刻 a)
            let mut presses: Vec<(u64, u64)> = Vec::new();
            let mut t = T0 + r.below(300);
            for _ in 0..r.below(150) {
                let span = if r.below(5) == 0 { 4_000 } else { 250 };
                t += 1 + r.below(span);
                presses.push((t, t + r.below(501)));
            }
            // tick の時刻(250 ms ごとにずれを付ける)
            let end = presses.last().map_or(T0, |p| p.0) + 3_000;
            let mut ticks = Vec::new();
            let mut now = T0;
            while now < end {
                now += 250 + r.below(60);
                ticks.push(now);
            }
            // 到着と tick を時刻の順に流す(同時刻は到着が先)
            let mut events: Vec<(u64, u8, usize)> = presses
                .iter()
                .enumerate()
                .map(|(i, p)| (p.1, 0u8, i))
                .chain(ticks.iter().enumerate().map(|(i, t)| (*t, 1u8, i)))
                .collect();
            events.sort();
            let mut last_state = None;
            let mut last_tick = T0;
            for (_, kind, i) in events {
                if kind == 0 {
                    d.on_press(presses[i].0);
                } else {
                    last_tick = ticks[i];
                    for e in d.tick(&fs, ticks[i], ON_DAY) {
                        if let Effect::State(s) = e {
                            // 各刻みの状態を、その刻みまでの記録の打鍵からの再生と比べる
                            let times: Vec<u64> = presses.iter().map(|p| p.0).collect();
                            let want = replay_live(&times, seed, T0, ticks[i]);
                            assert_eq!(s.bits(), want.bits(), "case {case} tick {}", ticks[i] - T0);
                            last_state = Some(s);
                        }
                    }
                }
            }
            let times: Vec<u64> = presses.iter().map(|p| p.0).collect();
            let want = replay_live(&times, seed, T0, last_tick);
            assert_eq!(last_state.unwrap().bits(), want.bits(), "case {case}");
        }
    }

    /// 記録に向かう出来事は `Row`(= `handmark_day`)だけ。
    #[test]
    fn only_rows_go_to_the_log() {
        let fs = with_table();
        let (mut d, mut all) = HandmarkDriver::new(&fs, true, T0, ON_DAY);
        for i in 1..400u64 {
            d.on_press(T0 + i * 120);
            all.extend(d.tick(&fs, T0 + i * 250, ON_DAY));
        }
        all.extend(d.turn_off(&fs, T0 + 100_000));
        all.extend(d.turn_on(&fs, T0 + 101_000));
        all.extend(d.on_redact(&fs, T0, T0 + 10, T0 + 101_500).0);
        all.extend(d.on_quit(&fs, T0 + 102_000));
        assert!(all.iter().any(|e| e.destination() == Destination::Window));
        for e in &all {
            if e.destination() == Destination::Log {
                assert!(matches!(e, Effect::Row(_)));
            }
        }
        assert!(all.iter().filter(|e| matches!(e, Effect::Row(_))).count() >= 4);
    }

    #[test]
    fn tray_labels_are_plain_and_hidden_when_not_applicable() {
        assert_eq!(TrayItem::Hidden.label(), None);
        assert_eq!(TrayItem::Stop.label(), Some("やめる"));
        assert_eq!(TrayItem::Restore.label(), Some("描く"));
    }

    #[test]
    fn a_window_failure_closes_with_its_reason_and_adds_no_shown_time() {
        let fs = with_table();
        let (mut d, _) = HandmarkDriver::new(&fs, true, T0, ON_DAY);
        // 窓の層が失敗を知らせる前の刻みでも、出たと分かるまでは積まない
        for i in 1..=8u64 {
            let _ = d.tick(&fs, T0 + i * 250, ON_DAY);
        }
        let fx = d.on_window_status(WindowStatus::Failed, T0 + 2_250);
        assert!(closed(&fx));
        assert_eq!(row_reason(&fx), Some(Some("window_unavailable")));
        assert!(!d.is_window_open());
        assert_eq!(d.tray(), TrayItem::Hidden);
        let rec = d.evaluation().record.as_ref().unwrap();
        assert_eq!(rec.shown_ms, 0);
        assert_eq!(rec.first_shown_day, None);
        // 次の tick でも積まない
        let _ = d.tick(&fs, T0 + 2_500, ON_DAY);
        assert_eq!(d.evaluation().record.as_ref().unwrap().shown_ms, 0);
        // 60 秒の検め直しでもう一度試す(窓の層が出せれば戻る)
        let mut now = T0 + 2_500;
        let mut reopened = false;
        while now < T0 + 70_000 {
            now += 250;
            if opened(&d.tick(&fs, now, ON_DAY)) {
                reopened = true;
                break;
            }
        }
        assert!(reopened);
        let _ = d.on_window_status(WindowStatus::Shown, now);
        let _ = d.tick(&fs, now + 250, ON_DAY);
        assert!(d.evaluation().record.as_ref().unwrap().shown_ms > 0);
        assert!(d
            .evaluation()
            .record
            .as_ref()
            .unwrap()
            .first_shown_day
            .is_some());
    }

    #[test]
    fn an_hour_of_sleep_is_not_added_to_the_shown_time() {
        let fs = with_table();
        let (mut d, _) = HandmarkDriver::new(&fs, true, T0, ON_DAY);
        let _ = d.on_window_status(WindowStatus::Shown, T0);
        let _ = d.tick(&fs, T0 + 250, ON_DAY);
        let before = d.evaluation().record.as_ref().unwrap().shown_ms;
        let _ = d.tick(&fs, T0 + 250 + 3_600_000, ON_DAY);
        let after = d.evaluation().record.as_ref().unwrap().shown_ms;
        assert_eq!(before, after, "1 時間の空白を足していない");
        // 2 秒ちょうどまでは足す
        let _ = d.tick(&fs, T0 + 250 + 3_600_000 + 2_000, ON_DAY);
        assert_eq!(
            d.evaluation().record.as_ref().unwrap().shown_ms,
            after + 2_000
        );
    }

    #[test]
    fn redact_failures_remove_the_state_file_and_report_false() {
        let fs = with_table();
        let (mut d, _) = HandmarkDriver::new(&fs, true, T0, ON_DAY);
        let _ = d.turn_off(&fs, T0 + 100);
        fs.fail_state_write.set(true);
        let (fx, ok) = d.on_redact(&fs, T0, T0 + 1_000, T0 + 2_000);
        assert!(ok, "書けなくても消せたので成功");
        assert!(closed(&fx) || !d.is_window_open());
        assert_eq!(fs.read_state(), crate::handmark_store::ReadResult::Missing);
        // 消すこともできない
        let fs = with_table();
        let (mut d, _) = HandmarkDriver::new(&fs, true, T0, ON_DAY);
        fs.fail_state_write.set(true);
        fs.fail_state_remove.set(true);
        assert!(!d.on_redact(&fs, T0, T0 + 1_000, T0 + 2_000).1);
        // 状態ファイルが壊れていて累計が無い起動でも、直接消す
        let fs = with_table();
        *fs.state.borrow_mut() = Some(b"{broken".to_vec());
        let (mut d, _) = HandmarkDriver::new(&fs, true, T0, ON_DAY);
        assert!(d.evaluation().record.is_none());
        assert!(d.on_redact(&fs, T0, T0 + 1_000, T0 + 2_000).1);
        assert_eq!(fs.read_state(), crate::handmark_store::ReadResult::Missing);
    }

    #[test]
    fn redact_takes_the_origin_again_while_the_window_is_open() {
        let fs = with_table();
        let (mut d, _) = HandmarkDriver::new(&fs, true, T0, ON_DAY);
        let _ = d.on_redact(&fs, T0, T0 + 500, T0 + 1_000);
        let starts = &d.evaluation().record.as_ref().unwrap().stage_starts;
        assert_eq!(starts, &vec![T0 + 1_000]);
    }

    /// 500 ms ちょうどの境界: 届いた打鍵が `now − 500 ≥ p` になる刻みで初めて状態に入る。
    #[test]
    fn the_500ms_boundary_is_exact() {
        let fs = with_table();
        let (mut d, _) = HandmarkDriver::new(&fs, true, T0, ON_DAY);
        let seed = d.evaluation().draw_seed().unwrap();
        let p = T0 + 1_000;
        let times = [p];
        d.on_press(p);
        for now in [T0 + 1_499, T0 + 1_500, T0 + 1_750, T0 + 2_000, T0 + 2_250] {
            let fx = d.tick(&fs, now, ON_DAY);
            let st = fx.iter().find_map(|e| match e {
                Effect::State(s) => Some(*s),
                _ => None,
            });
            let want = replay_live(&times, seed, T0, now);
            assert_eq!(st.unwrap().bits(), want.bits(), "now {}", now - T0);
        }
        // 1499 では入らず(速さ 0)、1500 の刻みで入る
        let (mut d2, _) = HandmarkDriver::new(&fs, true, T0, ON_DAY);
        d2.on_press(p);
        let st = |fx: &[Effect]| {
            fx.iter()
                .find_map(|e| match e {
                    Effect::State(s) => Some(*s),
                    _ => None,
                })
                .unwrap()
        };
        let a = st(&d2.tick(&fs, T0 + 1_499, ON_DAY));
        let b = st(&d2.tick(&fs, T0 + 1_750, ON_DAY));
        assert_eq!(a.speed, 0.0);
        assert!(b.speed > 0.0);
    }
}
