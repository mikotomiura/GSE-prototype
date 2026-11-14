//! 日の累計と切る状態（状態ファイル `~/.gse/handmark_day_state.json` の中身）と、日付の変わり目。
//!
//! 純粋な値の型。ファイルの読み書きは `crate::handmark_store`。

use serde::{Deserialize, Serialize};

pub const STATE_VERSION: u32 = 1;
/// `toggles`・`input_toggles`・`stage_starts` の 1 日の上限。超えたら新しいものを入れず `overflow` を真にする。
pub const MAX_PER_DAY: usize = 64;

/// 切った／戻した時刻（UTC の ms）。
#[derive(Debug, Clone, Copy, PartialEq, Eq, Serialize, Deserialize)]
#[serde(deny_unknown_fields)]
pub struct Toggle {
    pub t: u64,
    pub on: bool,
}

/// 入力ごとの入れ切りの対象（ポインタの 2 つの入力）。JSON では `"cursor"` / `"click"`。
#[derive(Debug, Clone, Copy, PartialEq, Eq, Serialize, Deserialize)]
#[serde(rename_all = "snake_case")]
pub enum PointerInput {
    Cursor,
    Click,
}

impl PointerInput {
    /// 行に書く固定の語。
    pub fn as_str(self) -> &'static str {
        match self {
            PointerInput::Cursor => "cursor",
            PointerInput::Click => "click",
        }
    }
}

/// 入力ごとに切った／戻した時刻（UTC の ms）。ポインタの値は持たない（時刻・入力の種類・入れたかだけ）。
#[derive(Debug, Clone, Copy, PartialEq, Eq, Serialize, Deserialize)]
#[serde(deny_unknown_fields)]
pub struct InputToggle {
    pub t: u64,
    pub input: PointerInput,
    pub on: bool,
}

/// その日の累計。
#[derive(Debug, Clone, PartialEq, Eq, Serialize, Deserialize)]
#[serde(deny_unknown_fields)]
pub struct DayRecord {
    pub version: u32,
    /// 現地の日の番号（`eh3::local_day`）。
    pub day: i64,
    /// その日に出ていた時間（ms）。
    pub shown_ms: u64,
    /// その日に帯（下の縁）が出ていて覆われていなかった時間（ms）。常に `shown_ms` 以下。
    /// 古い状態ファイルには無い（0 として読む）。
    #[serde(default)]
    pub visible_ms: u64,
    pub toggles: Vec<Toggle>,
    /// 切っている。
    pub off: bool,
    /// 初めて表示した日（単一の日付。累積の量ではない）。
    pub first_shown_day: Option<i64>,
    /// 手跡を出し始めた時刻（再生で位相の起点に使う）。
    pub stage_starts: Vec<u64>,
    pub overflow: bool,
    /// 入力ごとの切った／戻した（PR 3）。古い状態ファイルには無い（空として読む）。
    #[serde(default)]
    pub input_toggles: Vec<InputToggle>,
    /// カーソルの入力を切っている（古い状態ファイルには無い・入っているとして読む）。
    #[serde(default)]
    pub cursor_off: bool,
    /// クリックの入力を切っている。
    #[serde(default)]
    pub click_off: bool,
}

impl DayRecord {
    pub fn new(day: i64) -> Self {
        Self {
            version: STATE_VERSION,
            day,
            shown_ms: 0,
            visible_ms: 0,
            toggles: Vec::new(),
            off: false,
            first_shown_day: None,
            stage_starts: Vec::new(),
            overflow: false,
            input_toggles: Vec::new(),
            cursor_off: false,
            click_off: false,
        }
    }

    /// 区間の削除で書き直せないときの「切った状態を保つ最小の形」: 時刻を全部落とし、`off` と
    /// 入力ごとの切った状態（切った側）だけ残す。
    pub fn minimal_keeping_off(&self) -> Self {
        let mut min = Self::new(self.day);
        min.off = self.off;
        min.cursor_off = self.cursor_off;
        min.click_off = self.click_off;
        min
    }

    /// 日付が進んだら今日にして、日の量を空に戻す（`first_shown_day` は残す）。変わったら真。
    /// 時計が巻き戻った（`today < day`）ときは何も変えない（その間は呼び出し側が足さない）。
    pub fn roll_to(&mut self, today: i64) -> bool {
        if today <= self.day {
            return false;
        }
        let first = self.first_shown_day;
        *self = Self::new(today);
        self.first_shown_day = first;
        true
    }

    /// 出ていた時間を足す。足したら、初めて表示した日を（まだなら）今日にする。
    pub fn add_shown(&mut self, ms: u64) {
        if ms == 0 {
            return;
        }
        self.shown_ms = self.shown_ms.saturating_add(ms);
        if self.first_shown_day.is_none() {
            self.first_shown_day = Some(self.day);
        }
    }

    /// 帯が見えていた時間を足す（呼び出し側が `add_shown` と同じ条件のときだけ呼ぶ）。
    /// `first_shown_day` は `add_shown` の仕事なので触れない。
    pub fn add_visible(&mut self, ms: u64) {
        self.visible_ms = self.visible_ms.saturating_add(ms);
    }

    /// 切った／戻した（`off` が切った）。上限を超えたら記録は足さず `overflow` を立てる。
    pub fn set_off(&mut self, t: u64, off: bool) {
        self.off = off;
        if self.toggles.len() >= MAX_PER_DAY {
            self.overflow = true;
        } else {
            self.toggles.push(Toggle { t, on: !off });
        }
    }

    /// 入力ごとに切った／戻した。`on` が入れた。状態は必ず更新し、記録は上限を超えたら足さず
    /// `overflow` を立てる（`toggles` と同じ規則）。
    pub fn set_input(&mut self, t: u64, input: PointerInput, on: bool) {
        match input {
            PointerInput::Cursor => self.cursor_off = !on,
            PointerInput::Click => self.click_off = !on,
        }
        if self.input_toggles.len() >= MAX_PER_DAY {
            self.overflow = true;
        } else {
            self.input_toggles.push(InputToggle { t, input, on });
        }
    }

    /// 手跡を出し始めた時刻を足す。
    pub fn note_stage_start(&mut self, t: u64) {
        if self.stage_starts.len() >= MAX_PER_DAY {
            self.overflow = true;
        } else {
            self.stage_starts.push(t);
        }
    }

    /// 区間 `[from_ms, to_ms]`（両端を含む）に入る `toggles`・`input_toggles`・`stage_starts` の要素を消す
    /// （区間の削除）。消したものがあれば真。`shown_ms`・`off`・`cursor_off`・`click_off`・`overflow` は
    /// 時刻でないので変えない。
    pub fn scrub_range(&mut self, from_ms: u64, to_ms: u64) -> bool {
        if from_ms > to_ms {
            return false;
        }
        let inside = |t: u64| from_ms <= t && t <= to_ms;
        let (a, b, c) = (
            self.toggles.len(),
            self.stage_starts.len(),
            self.input_toggles.len(),
        );
        self.toggles.retain(|x| !inside(x.t));
        self.input_toggles.retain(|x| !inside(x.t));
        self.stage_starts.retain(|t| !inside(*t));
        a != self.toggles.len() || b != self.stage_starts.len() || c != self.input_toggles.len()
    }

    /// 読み込んだ中身を検める。
    pub fn is_valid(&self) -> bool {
        self.version == STATE_VERSION
            // 帯が見えていた量は、窓が出ていた量を超えない(駆動役は shown と一緒にしか足さない)。
            && self.visible_ms <= self.shown_ms
            && self.toggles.len() <= MAX_PER_DAY
            && self.stage_starts.len() <= MAX_PER_DAY
            && self.input_toggles.len() <= MAX_PER_DAY
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn roll_resets_the_day_but_keeps_first_shown_day() {
        let mut r = DayRecord::new(10);
        r.add_shown(5_000);
        r.add_visible(3_000);
        r.set_off(1, true);
        r.note_stage_start(2);
        assert_eq!(r.first_shown_day, Some(10));
        assert!(!r.roll_to(10));
        assert_eq!(r.shown_ms, 5_000);
        assert!(r.roll_to(11));
        assert_eq!(r.day, 11);
        assert_eq!(r.shown_ms, 0);
        assert_eq!(r.visible_ms, 0, "日の変わり目で 0 に戻る");
        assert!(r.toggles.is_empty() && r.stage_starts.is_empty());
        assert!(!r.off && !r.overflow);
        assert_eq!(r.first_shown_day, Some(10));
    }

    #[test]
    fn roll_ignores_a_clock_that_went_back() {
        let mut r = DayRecord::new(10);
        r.set_off(1, true);
        r.add_shown(5);
        let before = r.clone();
        assert!(!r.roll_to(9));
        assert_eq!(r, before);
    }

    #[test]
    fn first_shown_day_is_set_once() {
        let mut r = DayRecord::new(10);
        r.add_shown(0);
        assert_eq!(r.first_shown_day, None);
        r.add_shown(1);
        r.roll_to(11);
        r.add_shown(1);
        assert_eq!(r.first_shown_day, Some(10));
    }

    #[test]
    fn overflow_keeps_the_old_entries_and_drops_the_new() {
        let mut r = DayRecord::new(1);
        for i in 0..(MAX_PER_DAY as u64 + 5) {
            r.set_off(i, i % 2 == 0);
            r.note_stage_start(i);
        }
        assert_eq!(r.toggles.len(), MAX_PER_DAY);
        assert_eq!(r.stage_starts.len(), MAX_PER_DAY);
        assert!(r.overflow);
        assert_eq!(r.toggles[0].t, 0);
        assert_eq!(r.stage_starts[MAX_PER_DAY - 1], MAX_PER_DAY as u64 - 1);
        // 溢れた後も切った状態は最新
        r.set_off(999, false);
        assert!(!r.off);
        let mut ok = DayRecord::new(1);
        assert!(!ok.overflow);
        ok.set_off(1, true);
        assert!(ok.is_valid());
    }

    #[test]
    fn visible_ms_above_shown_ms_is_invalid() {
        let mut r = DayRecord::new(1);
        r.add_shown(5_000);
        r.add_visible(5_000);
        assert!(r.is_valid(), "等しいのは正常");
        r.add_visible(1);
        assert!(!r.is_valid(), "visible_ms > shown_ms は壊れた状態ファイル");
        // 往復しても壊れたまま(読み込み側 parse_state が Broken に倒す)
        let back: DayRecord = serde_json::from_str(&serde_json::to_string(&r).unwrap()).unwrap();
        assert!(!back.is_valid());
    }

    #[test]
    fn scrub_range_removes_only_inner_times_inclusive() {
        let mut r = DayRecord::new(1);
        for t in [10u64, 20, 30] {
            r.set_off(t, t != 20);
            r.note_stage_start(t + 1);
        }
        r.add_shown(7);
        assert!(!r.scrub_range(40, 50));
        assert!(!r.scrub_range(30, 10));
        assert!(r.scrub_range(20, 21));
        assert_eq!(
            r.toggles.iter().map(|t| t.t).collect::<Vec<_>>(),
            vec![10, 30]
        );
        assert_eq!(r.stage_starts, vec![11, 31]);
        assert_eq!(r.shown_ms, 7);
        r.add_visible(5);
        assert!(r.scrub_range(0, u64::MAX));
        assert_eq!(
            (r.shown_ms, r.visible_ms),
            (7, 5),
            "日の量は時刻でないので残る"
        );
        assert!(r.toggles.is_empty() && r.stage_starts.is_empty());
    }

    /// 古い形（PR 3 より前・`input_toggles` などが無い）の状態ファイルを読める。
    #[test]
    fn the_old_json_shape_is_still_read() {
        let old = r#"{"version":1,"day":20410,"shown_ms":0,"toggles":[{"t":5,"on":false}],"off":true,"first_shown_day":null,"stage_starts":[],"overflow":false}"#;
        let r: DayRecord = serde_json::from_str(old).unwrap();
        assert!(r.is_valid() && r.off);
        assert_eq!(r.visible_ms, 0, "visible_ms の無い古いファイルは 0");
        assert!(r.input_toggles.is_empty() && !r.cursor_off && !r.click_off);
        assert_eq!(r.toggles, vec![Toggle { t: 5, on: false }]);
    }

    #[test]
    fn json_shape_is_fixed() {
        let mut r = DayRecord::new(20_410);
        r.set_off(5, true);
        r.set_input(6, PointerInput::Cursor, false);
        r.set_input(7, PointerInput::Click, false);
        r.set_input(8, PointerInput::Cursor, true);
        assert_eq!(
            serde_json::to_string(&r).unwrap(),
            concat!(
                r#"{"version":1,"day":20410,"shown_ms":0,"visible_ms":0,"toggles":[{"t":5,"on":false}],"off":true,"#,
                r#""first_shown_day":null,"stage_starts":[],"overflow":false,"#,
                r#""input_toggles":[{"t":6,"input":"cursor","on":false},{"t":7,"input":"click","on":false},{"t":8,"input":"cursor","on":true}],"#,
                r#""cursor_off":false,"click_off":true}"#
            )
        );
        let back: DayRecord = serde_json::from_str(&serde_json::to_string(&r).unwrap()).unwrap();
        assert_eq!(back, r);
    }

    #[test]
    fn input_toggles_overflow_scrub_and_roll() {
        let mut r = DayRecord::new(1);
        for i in 0..(MAX_PER_DAY as u64 + 3) {
            r.set_input(i, PointerInput::Cursor, i % 2 == 1);
        }
        assert_eq!(r.input_toggles.len(), MAX_PER_DAY);
        assert!(r.overflow);
        assert!(r.is_valid());
        // 溢れた後も状態は最新（最後の i = 66 は偶数 → 切った）
        assert!(r.cursor_off);
        // 区間の削除: 入力の記録も消え、状態は変わらない
        let mut r = DayRecord::new(1);
        for t in [10u64, 20, 30] {
            r.set_input(t, PointerInput::Click, t == 20);
        }
        assert!(!r.scrub_range(40, 50));
        assert!(r.scrub_range(20, 20));
        assert_eq!(
            r.input_toggles.iter().map(|x| x.t).collect::<Vec<_>>(),
            vec![10, 30]
        );
        assert!(r.click_off, "the state is not a time and stays");
        // 日が変わると両方入った状態に戻り、記録は空
        assert!(r.roll_to(2));
        assert!(r.input_toggles.is_empty() && !r.cursor_off && !r.click_off);
        // 最小の形は切った状態を保ち、時刻を落とす
        let mut r = DayRecord::new(3);
        r.set_off(1, true);
        r.set_input(2, PointerInput::Cursor, false);
        let m = r.minimal_keeping_off();
        assert!(m.off && m.cursor_off && !m.click_off);
        assert!(m.toggles.is_empty() && m.input_toggles.is_empty());
    }

    #[test]
    fn visible_ms_round_trips_and_adds_without_touching_first_shown_day() {
        let mut r = DayRecord::new(5);
        r.add_visible(40);
        r.add_visible(2);
        assert_eq!(r.first_shown_day, None);
        let back: DayRecord = serde_json::from_str(&serde_json::to_string(&r).unwrap()).unwrap();
        assert_eq!(back.visible_ms, 42);
        assert_eq!(back, r);
    }
}
