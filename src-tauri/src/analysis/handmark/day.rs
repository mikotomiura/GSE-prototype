//! 日の累計と切る状態（状態ファイル `~/.gse/handmark_day_state.json` の中身）と、日付の変わり目。
//!
//! 純粋な値の型。ファイルの読み書きは `crate::handmark_store`。

use serde::{Deserialize, Serialize};

pub const STATE_VERSION: u32 = 1;
/// `toggles` と `stage_starts` の 1 日の上限。超えたら新しいものを入れず `overflow` を真にする。
pub const MAX_PER_DAY: usize = 64;

/// 切った／戻した時刻（UTC の ms）。
#[derive(Debug, Clone, Copy, PartialEq, Eq, Serialize, Deserialize)]
#[serde(deny_unknown_fields)]
pub struct Toggle {
    pub t: u64,
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
    pub toggles: Vec<Toggle>,
    /// 切っている。
    pub off: bool,
    /// 初めて表示した日（単一の日付。累積の量ではない）。
    pub first_shown_day: Option<i64>,
    /// 手跡を出し始めた時刻（再生で位相の起点に使う）。
    pub stage_starts: Vec<u64>,
    pub overflow: bool,
}

impl DayRecord {
    pub fn new(day: i64) -> Self {
        Self {
            version: STATE_VERSION,
            day,
            shown_ms: 0,
            toggles: Vec::new(),
            off: false,
            first_shown_day: None,
            stage_starts: Vec::new(),
            overflow: false,
        }
    }

    /// 日付が変わったら今日にして、日の量を空に戻す（`first_shown_day` は残す）。変わったら真。
    pub fn roll_to(&mut self, today: i64) -> bool {
        if self.day == today {
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

    /// 切った／戻した（`off` が切った）。上限を超えたら記録は足さず `overflow` を立てる。
    pub fn set_off(&mut self, t: u64, off: bool) {
        self.off = off;
        if self.toggles.len() >= MAX_PER_DAY {
            self.overflow = true;
        } else {
            self.toggles.push(Toggle { t, on: !off });
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

    /// 読み込んだ中身を検める。
    pub fn is_valid(&self) -> bool {
        self.version == STATE_VERSION
            && self.toggles.len() <= MAX_PER_DAY
            && self.stage_starts.len() <= MAX_PER_DAY
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn roll_resets_the_day_but_keeps_first_shown_day() {
        let mut r = DayRecord::new(10);
        r.add_shown(5_000);
        r.set_off(1, true);
        r.note_stage_start(2);
        assert_eq!(r.first_shown_day, Some(10));
        assert!(!r.roll_to(10));
        assert_eq!(r.shown_ms, 5_000);
        assert!(r.roll_to(11));
        assert_eq!(r.day, 11);
        assert_eq!(r.shown_ms, 0);
        assert!(r.toggles.is_empty() && r.stage_starts.is_empty());
        assert!(!r.off && !r.overflow);
        assert_eq!(r.first_shown_day, Some(10));
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
    fn json_shape_is_fixed() {
        let mut r = DayRecord::new(20_410);
        r.set_off(5, true);
        assert_eq!(
            serde_json::to_string(&r).unwrap(),
            r#"{"version":1,"day":20410,"shown_ms":0,"toggles":[{"t":5,"on":false}],"off":true,"first_shown_day":null,"stage_starts":[],"overflow":false}"#
        );
    }
}
