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
use crate::analysis::handmark::day::PointerInput;
use crate::analysis::handmark::gate::{CloseReason, Decision, RECHECK_MS};
use crate::analysis::handmark::state::{Stage, StageState, LIVE_LAG_MS};
use crate::handmark_store::{
    rewrite_or_remove, scrub_state_file, turn_input_off, turn_input_on, turn_off, turn_on,
    Evaluation, HandmarkFs,
};
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
    OpenWindow {
        layout_seed: u32,
    },
    CloseWindow,
    State(StageState),
    Row(HandmarkDayRow),
    TrayItem(TrayItem),
    /// ポインタのスレッドへの入れ切り（窓を出している・カーソルが入っている・クリックが入っている）。
    /// 窓を開く・閉じる・入れ切りが変わる・日が変わる・門が閉じるたびに、その時点の値で 1 回出す。
    /// `open` は窓を出していること（全体の「やめる」で閉じれば false。入力ごとの状態は保つ）。
    PointerGate {
        open: bool,
        cursor: bool,
        click: bool,
    },
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
            Effect::OpenWindow { .. }
            | Effect::CloseWindow
            | Effect::State(_)
            | Effect::PointerGate { .. } => Destination::Window,
            Effect::TrayItem(_) => Destination::Tray,
        }
    }
}

/// トレイの「カーソル」「クリック」の押下の照合（AppHandle を要らない純関数）。
///
/// `shown_checked` は押された項目の、メニューに出ていた印（入っていれば true）。`driver_items` は駆動役の
/// 今の状態（`input_items()`）。窓を出していない（`None`）・表示が古い（駆動役の今の状態が出ていた印と違う）
/// ときは `None`（何もしない）。そうでなければ `Some(on)`（`on` は入れる側 = 出ていた印の反対）。
pub fn decide_tray_input(
    shown_checked: bool,
    driver_items: Option<(bool, bool)>,
    input: PointerInput,
) -> Option<bool> {
    let (cursor_on, click_on) = driver_items?;
    let now_on = match input {
        PointerInput::Cursor => cursor_on,
        PointerInput::Click => click_on,
    };
    (now_on == shown_checked).then_some(!shown_checked)
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
    /// 帯の窓の層が最後に知らせた「帯が見えている」(窓を閉じる・開くたびに偽へ戻す)。
    strip_visible: bool,
    last_recheck_ms: u64,
    last_row_ms: u64,
    last_tick_ms: u64,
    last_tray: TrayItem,
    /// 最後に出した `(open, cursor, click)`（閉じた初期の値から始める。変わらなければ出さない）。
    last_gate: (bool, bool, bool),
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
            strip_visible: false,
            last_recheck_ms: now,
            last_row_ms: now,
            last_tick_ms: now,
            last_tray: TrayItem::Hidden,
            last_gate: (false, true, true),
        };
        let mut fx = Vec::new();
        d.push_row(now, &mut fx);
        if d.ev.is_open() {
            d.open_window(now, &mut fx);
        }
        d.sync_tray(&mut fx);
        d.sync_gate(false, &mut fx);
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

    /// ポインタの入れ切りを出す。値が変わったとき（`force` なら変わらなくても）1 回。
    fn sync_gate(&mut self, force: bool, fx: &mut Vec<Effect>) {
        let (cursor, click) = self.ev.inputs_on();
        let g = (self.window_open, cursor, click);
        if force || g != self.last_gate {
            self.last_gate = g;
            fx.push(Effect::PointerGate {
                open: g.0,
                cursor: g.1,
                click: g.2,
            });
        }
    }

    /// 窓を出している間だけ `Some((カーソルが入っているか, クリックが入っているか))`（トレイの項目用）。
    pub fn input_items(&self) -> Option<(bool, bool)> {
        self.window_open.then(|| self.ev.inputs_on())
    }

    /// トレイの「カーソル」「クリック」。`on` が入れる側。窓を出していないときは何もしない。
    /// 切るのは書けなくても切る・入れるのは書けなければ切ったまま（`turn_input_on` の作法）。
    pub fn set_input(
        &mut self,
        fs: &dyn HandmarkFs,
        input: PointerInput,
        on: bool,
        now: u64,
    ) -> Vec<Effect> {
        let mut fx = Vec::new();
        if !self.window_open {
            return fx;
        }
        let applied = if on {
            turn_input_on(fs, &mut self.ev, input, now).is_ok()
        } else {
            // 状態ファイルに書けず印を書けたとき（`MarkOnly`）は、その日は手跡全体を出さない側に倒れて
            // 門が閉じる。窓をここで閉じる（再起動を待たない）。
            turn_input_off(fs, &mut self.ev, input, now);
            self.reconcile(now, &mut fx);
            true
        };
        if applied {
            self.push_row(now, &mut fx);
            self.sync_gate(false, &mut fx);
        }
        fx
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
        self.strip_visible = false;
        self.last_tick_ms = now;
        let layout_seed = self.stage.as_ref().map_or(0, |s| s.state().layout_seed);
        fx.push(Effect::OpenWindow { layout_seed });
    }

    fn close_window(&mut self, fx: &mut Vec<Effect>) {
        self.window_open = false;
        self.window_confirmed = false;
        self.strip_visible = false;
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
                if self.strip_visible {
                    self.ev.add_visible(gap);
                }
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
        self.sync_gate(day_changed, &mut fx);
        fx
    }

    /// トレイの「やめる」。
    pub fn turn_off(&mut self, fs: &dyn HandmarkFs, now: u64) -> Vec<Effect> {
        let mut fx = Vec::new();
        turn_off(fs, &mut self.ev, now);
        self.reconcile(now, &mut fx);
        self.push_row(now, &mut fx);
        self.sync_gate(false, &mut fx);
        fx
    }

    /// トレイの「描く」。戻せなければ出さないまま。
    pub fn turn_on(&mut self, fs: &dyn HandmarkFs, now: u64) -> Vec<Effect> {
        let mut fx = Vec::new();
        if turn_on(fs, &mut self.ev, now).is_ok() {
            self.reconcile(now, &mut fx);
            self.push_row(now, &mut fx);
            self.sync_gate(false, &mut fx);
        }
        fx
    }

    /// 窓の層の様子を受け取る(次の tick より前に呼ぶ)。`Failed` なら `window_unavailable` で閉じる。
    pub fn on_window_status(&mut self, status: WindowStatus, now: u64) -> Vec<Effect> {
        let mut fx = Vec::new();
        match status {
            WindowStatus::Pending => {}
            WindowStatus::Shown => {
                if self.window_open && !self.window_confirmed {
                    self.window_confirmed = true;
                    // 計測の起点を置き直す(出たと分かる前の時間を入れない)
                    self.last_tick_ms = now;
                }
            }
            WindowStatus::Failed => {
                if self.window_open {
                    self.ev.set_window_unavailable(true);
                    self.reconcile(now, &mut fx);
                    self.push_row(now, &mut fx);
                    self.sync_gate(false, &mut fx);
                }
            }
        }
        fx
    }

    /// 帯の窓の層が知らせた「帯が見えている」を持つ(次の tick より前に呼ぶ。値を持つだけ)。
    /// 窓を閉じる・開くと偽に戻るので、帯の層が改めて知らせるまで足さない。
    pub fn on_strip_visible(&mut self, visible: bool) {
        self.strip_visible = visible;
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
                // 書けない: 始末は `scrub_state_file` と共通（`rewrite_or_remove`・入力ごとの切りも保つ）。
                let snapshot = self.ev.record.clone();
                self.ev.note_save_failed();
                self.reconcile(now, &mut fx);
                snapshot.is_some_and(|r| rewrite_or_remove(fs, &r).is_ok())
            }
        } else {
            // 状態ファイルが壊れていて累計が無い: ファイルを直接直す(壊れていれば消す)
            scrub_state_file(fs, from_ms, to_ms).is_ok()
        };
        if self.window_open {
            // 区間の後の起点を取り直す(消した起点を再生が必要としないように)
            self.new_stage(now);
        }
        self.sync_gate(false, &mut fx);
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
    fn decide_tray_input_matches_the_shown_mark_with_the_drivers_state() {
        use PointerInput::{Click, Cursor};
        // 窓を出していない → 何もしない。
        assert_eq!(decide_tray_input(true, None, Cursor), None);
        // 出ていた印が駆動役の状態と同じなら、反対を入れる側として返す。
        assert_eq!(
            decide_tray_input(true, Some((true, false)), Cursor),
            Some(false)
        );
        assert_eq!(
            decide_tray_input(false, Some((true, false)), Click),
            Some(true)
        );
        // 違う（表示が古い）→ 何もしない。
        assert_eq!(decide_tray_input(false, Some((true, false)), Cursor), None);
        assert_eq!(decide_tray_input(true, Some((true, false)), Click), None);
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
        all.extend(d.set_input(&fs, PointerInput::Cursor, false, T0 + 101_200));
        all.extend(d.set_input(&fs, PointerInput::Click, false, T0 + 101_300));
        all.extend(d.set_input(&fs, PointerInput::Cursor, true, T0 + 101_400));
        all.extend(d.on_redact(&fs, T0, T0 + 10, T0 + 101_500).0);
        all.extend(d.on_quit(&fs, T0 + 102_000));
        assert!(all
            .iter()
            .any(|e| matches!(e, Effect::PointerGate { .. })
                && e.destination() == Destination::Window));
        assert!(all.iter().any(|e| e.destination() == Destination::Window));
        for e in &all {
            if e.destination() == Destination::Log {
                assert!(matches!(e, Effect::Row(_)));
            }
        }
        assert!(all.iter().filter(|e| matches!(e, Effect::Row(_))).count() >= 4);
    }

    fn gates(fx: &[Effect]) -> Vec<(bool, bool, bool)> {
        fx.iter()
            .filter_map(|e| match e {
                Effect::PointerGate {
                    open,
                    cursor,
                    click,
                } => Some((*open, *cursor, *click)),
                _ => None,
            })
            .collect()
    }

    #[test]
    fn an_input_toggle_emits_the_pointer_gate_once_with_the_current_values() {
        let fs = with_table();
        let (mut d, fx) = HandmarkDriver::new(&fs, true, T0, ON_DAY);
        // 窓を開いた起動で 1 回（開いている・両方入っている）
        assert_eq!(gates(&fx), vec![(true, true, true)]);
        assert_eq!(d.input_items(), Some((true, true)));
        let fx = d.set_input(&fs, PointerInput::Cursor, false, T0 + 1_000);
        assert_eq!(gates(&fx), vec![(true, false, true)]);
        assert_eq!(d.input_items(), Some((false, true)));
        // 行にも入る（記録へ向かうのは Row だけ）
        let row = fx.iter().find_map(|e| match e {
            Effect::Row(r) => Some(r.clone()),
            _ => None,
        });
        assert_eq!(
            row.unwrap().input_toggles,
            vec![(T0 + 1_000, "cursor", false)]
        );
        let fx = d.set_input(&fs, PointerInput::Click, false, T0 + 2_000);
        assert_eq!(gates(&fx), vec![(true, false, false)]);
        let fx = d.set_input(&fs, PointerInput::Cursor, true, T0 + 3_000);
        assert_eq!(gates(&fx), vec![(true, true, false)]);
        // 通常の tick では出ない（変わっていない）
        assert!(gates(&d.tick(&fs, T0 + 3_250, ON_DAY)).is_empty());
    }

    #[test]
    fn a_failed_write_cuts_an_input_but_cannot_turn_it_on() {
        let fs = with_table();
        let (mut d, _) = HandmarkDriver::new(&fs, true, T0, ON_DAY);
        fs.fail_state_write.set(true);
        // 印も書けない（書けるときは全体を出さない側に倒れる・下の別のテスト）
        fs.fail_mark_write.set(true);
        let fx = d.set_input(&fs, PointerInput::Click, false, T0 + 1_000);
        assert_eq!(gates(&fx), vec![(true, true, false)], "書けなくても切る");
        // 入れるのは書けなければ切ったまま（出来事も出さない）
        let fx = d.set_input(&fs, PointerInput::Click, true, T0 + 2_000);
        assert!(fx.is_empty());
        assert_eq!(d.input_items(), Some((true, false)));
    }

    #[test]
    fn a_failed_input_cut_with_a_mark_closes_the_window_and_stays_closed_after_a_restart() {
        let fs = with_table();
        let (mut d, _) = HandmarkDriver::new(&fs, true, T0, ON_DAY);
        fs.fail_state_write.set(true);
        let fx = d.set_input(&fs, PointerInput::Click, false, T0 + 1_000);
        assert!(closed(&fx), "全体を出さない側に倒れて窓を閉じる");
        assert_eq!(gates(&fx), vec![(false, true, false)]);
        assert_eq!(d.input_items(), None);
        assert!(fs.marks.borrow().contains(&ON_DAY));
        // 起動し直してもその日は出ない。
        fs.fail_state_write.set(false);
        let (d2, fx2) = HandmarkDriver::new(&fs, true, T0 + 5_000, ON_DAY);
        assert!(!d2.is_window_open() && !opened(&fx2));
    }

    #[test]
    fn a_failed_redact_rewrite_keeps_an_input_cut_through_the_driver() {
        let fs = with_table();
        let (mut d, _) = HandmarkDriver::new(&fs, true, T0, ON_DAY);
        let _ = d.set_input(&fs, PointerInput::Cursor, false, T0 + 500);
        // 区間の削除で、書き直し（全体）だけ失敗する
        fs.fail_state_writes_left.set(1);
        let (_, ok) = d.on_redact(&fs, T0, T0 + 10_000, T0 + 20_000);
        assert!(ok);
        let (d2, _) = HandmarkDriver::new(&fs, true, T0 + 60_000, ON_DAY);
        assert_eq!(
            d2.input_items(),
            Some((false, true)),
            "カーソルは切れたまま"
        );
    }

    #[test]
    fn stopping_closes_the_gate_but_keeps_the_inputs_and_drawing_restores_it() {
        let fs = with_table();
        let (mut d, _) = HandmarkDriver::new(&fs, true, T0, ON_DAY);
        let _ = d.set_input(&fs, PointerInput::Cursor, false, T0 + 500);
        let fx = d.turn_off(&fs, T0 + 1_000);
        assert_eq!(
            gates(&fx),
            vec![(false, false, true)],
            "open=false・入力ごとの状態は保つ"
        );
        assert_eq!(d.input_items(), None, "窓が無い間はトレイの項目を出さない");
        // 窓が無い間の入れ切りは何もしない
        assert!(d
            .set_input(&fs, PointerInput::Click, false, T0 + 1_500)
            .is_empty());
        let fx = d.turn_on(&fs, T0 + 2_000);
        assert_eq!(gates(&fx), vec![(true, false, true)]);
        assert_eq!(d.input_items(), Some((false, true)));
    }

    #[test]
    fn a_new_day_puts_both_inputs_back_and_emits_the_gate_once() {
        let fs = with_table();
        let (mut d, _) = HandmarkDriver::new(&fs, true, T0, ON_DAY);
        let _ = d.set_input(&fs, PointerInput::Cursor, false, T0 + 500);
        let _ = d.set_input(&fs, PointerInput::Click, false, T0 + 600);
        let fx = d.tick(&fs, T0 + 1_000, ON_DAY + 3);
        assert_eq!(gates(&fx), vec![(true, true, true)]);
        assert_eq!(d.input_items(), Some((true, true)));
        // 変わらないままの日替わりでも、日が変わるたびに 1 回出す
        let fx = d.tick(&fs, T0 + 1_000 + 86_400_000, ON_DAY + 6);
        assert_eq!(gates(&fx).len(), 1, "{fx:?}");
        // 出さない日に変われば閉じた値が出る
        let fx = d.tick(&fs, T0 + 2_000 + 2 * 86_400_000, ON_DAY + 7);
        assert!(gates(&fx).last().is_some_and(|g| !g.0), "{fx:?}");
    }

    #[test]
    fn closing_the_gate_by_a_failure_or_an_unwritable_state_emits_the_gate() {
        let fs = with_table();
        let (mut d, _) = HandmarkDriver::new(&fs, true, T0, ON_DAY);
        let fx = d.on_window_status(WindowStatus::Failed, T0 + 100);
        assert_eq!(gates(&fx), vec![(false, true, true)]);
        // 起動から閉じている日は、起動で何も出さない（閉じた初期の値のまま）
        let fs2 = MemFs::default();
        let (_, fx) = HandmarkDriver::new(&fs2, true, T0, ON_DAY);
        assert!(gates(&fx).is_empty());
        let (_, fx) = HandmarkDriver::new(&fs, false, T0, ON_DAY);
        assert!(fx.is_empty());
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

    /// Pending の刻み → 遅れて Shown → 次の刻みで、Shown より前の時間が `shown_ms` に入らない。
    #[test]
    fn time_before_the_window_was_confirmed_is_not_counted() {
        let fs = with_table();
        let (mut d, _) = HandmarkDriver::new(&fs, true, T0, ON_DAY);
        for i in 1..=6u64 {
            let _ = d.tick(&fs, T0 + i * 250, ON_DAY);
        }
        assert_eq!(d.evaluation().record.as_ref().unwrap().shown_ms, 0);
        let _ = d.on_window_status(WindowStatus::Shown, T0 + 1_600);
        let _ = d.tick(&fs, T0 + 1_750, ON_DAY);
        assert_eq!(d.evaluation().record.as_ref().unwrap().shown_ms, 150);
    }

    fn vis(d: &HandmarkDriver) -> (u64, u64) {
        let r = d.evaluation().record.as_ref().unwrap();
        (r.shown_ms, r.visible_ms)
    }

    /// 帯が見えない間は足さない。見えていれば `shown_ms` と同じだけ足す。
    #[test]
    fn visible_time_follows_the_strip_and_never_exceeds_shown() {
        let fs = with_table();
        let (mut d, _) = HandmarkDriver::new(&fs, true, T0, ON_DAY);
        let _ = d.on_window_status(WindowStatus::Shown, T0);
        let _ = d.tick(&fs, T0 + 250, ON_DAY);
        let _ = d.tick(&fs, T0 + 500, ON_DAY);
        assert_eq!(vis(&d), (500, 0), "帯が見えない間は足さない");
        d.on_strip_visible(true);
        let _ = d.tick(&fs, T0 + 750, ON_DAY);
        let _ = d.tick(&fs, T0 + 1_000, ON_DAY);
        assert_eq!(vis(&d), (1_000, 500), "見えていれば shown と同じだけ");
        d.on_strip_visible(false);
        let _ = d.tick(&fs, T0 + 1_250, ON_DAY);
        assert_eq!(vis(&d), (1_250, 500));
        assert!(vis(&d).1 <= vis(&d).0);
    }

    /// 窓が出たと分かる前・時計の飛び・2 秒超の間・日の変わり目は足さない。
    #[test]
    fn visible_time_is_not_added_where_shown_is_not() {
        let fs = with_table();
        let (mut d, _) = HandmarkDriver::new(&fs, true, T0, ON_DAY);
        d.on_strip_visible(true);
        // 窓が出たと分かる前
        let _ = d.tick(&fs, T0 + 250, ON_DAY);
        assert_eq!(vis(&d), (0, 0));
        let _ = d.on_window_status(WindowStatus::Shown, T0 + 250);
        let _ = d.tick(&fs, T0 + 500, ON_DAY);
        assert_eq!(vis(&d), (250, 250));
        // 1 時間の空白(時計の飛び)
        let _ = d.tick(&fs, T0 + 500 + 3_600_000, ON_DAY);
        assert_eq!(vis(&d), (250, 250));
        // 2 秒ちょうどまでは足す・2 秒を超える間は足さない(飛びの後の最初の刻みは起点の取り直し)
        let base = T0 + 500 + 3_600_000;
        let _ = d.tick(&fs, base + 2_000, ON_DAY);
        assert_eq!(vis(&d), (2_250, 2_250));
        let _ = d.tick(&fs, base + 2_000 + 2_001, ON_DAY);
        assert_eq!(vis(&d), (2_250, 2_250), "2 秒を超える間は足さない");
        // 日の変わり目の刻みは足さず、新しい日は 0 から
        let _ = d.tick(&fs, base + 2_000 + 2_251, ON_DAY + 3);
        assert_eq!(vis(&d), (0, 0));
        assert!(vis(&d).1 <= vis(&d).0);
    }

    /// 閉じて開き直したら、帯の層が改めて知らせるまで足さない。
    #[test]
    fn visible_time_waits_for_a_fresh_report_after_reopening() {
        let fs = with_table();
        let (mut d, _) = HandmarkDriver::new(&fs, true, T0, ON_DAY);
        let _ = d.on_window_status(WindowStatus::Shown, T0);
        d.on_strip_visible(true);
        let _ = d.tick(&fs, T0 + 250, ON_DAY);
        assert_eq!(vis(&d), (250, 250));
        let _ = d.turn_off(&fs, T0 + 300);
        assert!(!d.is_window_open());
        let fx = d.turn_on(&fs, T0 + 400);
        assert!(opened(&fx));
        let _ = d.on_window_status(WindowStatus::Shown, T0 + 450);
        let _ = d.tick(&fs, T0 + 700, ON_DAY);
        assert_eq!(vis(&d), (500, 250), "知らせが来るまで足さない");
        d.on_strip_visible(true);
        let _ = d.tick(&fs, T0 + 950, ON_DAY);
        assert_eq!(vis(&d), (750, 500));
    }

    /// 行の `visible_ms` は累計があれば `Some`、五分の行にも載る。区間の削除で消えない。
    #[test]
    fn visible_time_reaches_the_row_and_survives_a_redact() {
        let fs = with_table();
        let (mut d, _) = HandmarkDriver::new(&fs, true, T0, ON_DAY);
        let _ = d.on_window_status(WindowStatus::Shown, T0);
        d.on_strip_visible(true);
        let _ = d.tick(&fs, T0 + 250, ON_DAY);
        assert_eq!(d.evaluation().row(T0 + 250).unwrap().visible_ms, Some(250));
        let (_, ok) = d.on_redact(&fs, T0, T0 + 10_000, T0 + 300);
        assert!(ok);
        assert_eq!(vis(&d), (250, 250), "区間の削除で消さない");
        let mut now = T0 + 250;
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
        // 最初の刻みから帯が見えていたので、五分の行の時点では shown と同じ(行を出した後の刻みは含まない)
        assert_eq!(r.visible_ms, Some(r.shown_ms));
    }

    /// 切っていて、状態ファイルも印も書けない: 状態ファイルを消さず失敗を返し、再起動で切ったまま。
    #[test]
    fn redact_keeps_the_off_state_when_nothing_can_be_written() {
        let fs = with_table();
        let (mut d, _) = HandmarkDriver::new(&fs, true, T0, ON_DAY);
        let _ = d.turn_off(&fs, T0 + 100);
        fs.fail_state_write.set(true);
        fs.fail_mark_write.set(true);
        let (_, ok) = d.on_redact(&fs, T0, T0 + 1_000, T0 + 2_000);
        assert!(!ok);
        fs.fail_state_write.set(false);
        fs.fail_mark_write.set(false);
        assert_ne!(fs.read_state(), crate::handmark_store::ReadResult::Missing);
        let (d2, fx) = HandmarkDriver::new(&fs, true, T0 + 3_000, ON_DAY);
        assert!(!d2.is_window_open());
        assert_eq!(row_reason(&fx), Some(Some("off_today")));
    }
}
