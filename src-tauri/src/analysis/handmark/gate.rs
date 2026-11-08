//! 入口の門の判定と、検め直しの契機（ADR-051 D5）。純関数。

use super::assignment::{Assigned, TableLoad};

/// 検め直しの間隔（ms）。
pub const RECHECK_MS: u64 = 60_000;

/// 閉じている理由（`handmark_day` の `reason`・固定の文字列）。
#[derive(Debug, Clone, Copy, PartialEq, Eq)]
pub enum CloseReason {
    TableMissing,
    TableBroken,
    ShaMissing,
    ShaMismatch,
    StateBroken,
    StateUnwritable,
    OffToday,
    AssignedOff,
    BeforeLate,
    AfterTable,
}

impl CloseReason {
    pub const ALL: [CloseReason; 10] = [
        CloseReason::TableMissing,
        CloseReason::TableBroken,
        CloseReason::ShaMissing,
        CloseReason::ShaMismatch,
        CloseReason::StateBroken,
        CloseReason::StateUnwritable,
        CloseReason::OffToday,
        CloseReason::AssignedOff,
        CloseReason::BeforeLate,
        CloseReason::AfterTable,
    ];

    pub fn as_str(self) -> &'static str {
        match self {
            CloseReason::TableMissing => "table_missing",
            CloseReason::TableBroken => "table_broken",
            CloseReason::ShaMissing => "sha_missing",
            CloseReason::ShaMismatch => "sha_mismatch",
            CloseReason::StateBroken => "state_broken",
            CloseReason::StateUnwritable => "state_unwritable",
            CloseReason::OffToday => "off_today",
            CloseReason::AssignedOff => "assigned_off",
            CloseReason::BeforeLate => "before_late",
            CloseReason::AfterTable => "after_table",
        }
    }
}

/// 状態ファイルの様子。
#[derive(Debug, Clone, Copy, PartialEq, Eq)]
pub enum StateStatus {
    /// 読めて、書き込みの試しも通った。
    Ok,
    Broken,
    Unwritable,
}

/// 門の判定。
#[derive(Debug, Clone, Copy, PartialEq, Eq)]
pub enum Decision {
    /// 段 1 のモードでない（行も理由も書かない）。
    NotS1,
    Open {
        assigned: Assigned,
    },
    Closed {
        reason: CloseReason,
        /// 表が読めたときの今日の割付。
        assigned: Option<Assigned>,
    },
}

impl Decision {
    pub fn is_open(&self) -> bool {
        matches!(self, Decision::Open { .. })
    }
}

/// 門を判定する。理由の優先順: 表 → 割付（出さない日）→ 状態ファイル → 切っている。
pub fn decide(
    s1_mode: bool,
    table: &TableLoad,
    today: i64,
    state: StateStatus,
    off_today: bool,
) -> Decision {
    if !s1_mode {
        return Decision::NotS1;
    }
    let reason = |reason| Decision::Closed {
        reason,
        assigned: None,
    };
    let (assigned, _) = match table {
        TableLoad::Missing => return reason(CloseReason::TableMissing),
        TableLoad::Broken => return reason(CloseReason::TableBroken),
        TableLoad::ShaMissing => return reason(CloseReason::ShaMissing),
        TableLoad::ShaMismatch => return reason(CloseReason::ShaMismatch),
        TableLoad::Ok { table, sha256 } => (table.assigned(today), sha256),
    };
    let closed = |reason| Decision::Closed {
        reason,
        assigned: Some(assigned),
    };
    match assigned {
        Assigned::Before => return closed(CloseReason::BeforeLate),
        Assigned::After => return closed(CloseReason::AfterTable),
        Assigned::Off => return closed(CloseReason::AssignedOff),
        Assigned::LateFirst | Assigned::On => {}
    }
    match state {
        StateStatus::Broken => closed(CloseReason::StateBroken),
        StateStatus::Unwritable => closed(CloseReason::StateUnwritable),
        StateStatus::Ok if off_today => closed(CloseReason::OffToday),
        StateStatus::Ok => Decision::Open { assigned },
    }
}

/// 検め直すか（起動・日付の変わり目・前回から 60 秒）。起動のときは `last_day = i64::MIN` を渡す。
/// 時計が戻ったときも検め直す。
pub fn needs_recheck(last_ms: u64, last_day: i64, now_ms: u64, today: i64) -> bool {
    last_day != today || now_ms < last_ms || now_ms - last_ms >= RECHECK_MS
}

#[cfg(test)]
mod tests {
    use super::*;
    use crate::analysis::handmark::assignment::Table;

    fn ok_table() -> TableLoad {
        TableLoad::Ok {
            table: Table {
                version: 1,
                s1_start_day: 100,
                early_days: 10,
                late_start_day: 110,
                days: vec![true, false, false, true],
            },
            sha256: "0".repeat(64),
        }
    }

    #[test]
    fn not_s1_writes_nothing() {
        assert_eq!(
            decide(false, &ok_table(), 110, StateStatus::Ok, false),
            Decision::NotS1
        );
        assert_eq!(
            decide(false, &TableLoad::Missing, 110, StateStatus::Broken, true),
            Decision::NotS1
        );
    }

    #[test]
    fn table_problems_close_with_their_reason() {
        for (t, r) in [
            (TableLoad::Missing, CloseReason::TableMissing),
            (TableLoad::Broken, CloseReason::TableBroken),
            (TableLoad::ShaMissing, CloseReason::ShaMissing),
            (TableLoad::ShaMismatch, CloseReason::ShaMismatch),
        ] {
            assert_eq!(
                decide(true, &t, 110, StateStatus::Ok, false),
                Decision::Closed {
                    reason: r,
                    assigned: None
                }
            );
        }
    }

    #[test]
    fn assignment_decides_the_open_days() {
        let t = ok_table();
        let d = |day| decide(true, &t, day, StateStatus::Ok, false);
        assert!(matches!(
            d(109),
            Decision::Closed {
                reason: CloseReason::BeforeLate,
                ..
            }
        ));
        assert_eq!(
            d(110),
            Decision::Open {
                assigned: Assigned::LateFirst
            }
        );
        assert_eq!(
            d(111),
            Decision::Open {
                assigned: Assigned::On
            }
        );
        assert!(matches!(
            d(112),
            Decision::Closed {
                reason: CloseReason::AssignedOff,
                ..
            }
        ));
        assert!(matches!(
            d(115),
            Decision::Closed {
                reason: CloseReason::AfterTable,
                ..
            }
        ));
    }

    #[test]
    fn state_and_off_close_an_open_day() {
        let t = ok_table();
        assert!(matches!(
            decide(true, &t, 111, StateStatus::Broken, false),
            Decision::Closed {
                reason: CloseReason::StateBroken,
                assigned: Some(Assigned::On)
            }
        ));
        assert!(matches!(
            decide(true, &t, 111, StateStatus::Unwritable, false),
            Decision::Closed {
                reason: CloseReason::StateUnwritable,
                ..
            }
        ));
        assert!(matches!(
            decide(true, &t, 111, StateStatus::Ok, true),
            Decision::Closed {
                reason: CloseReason::OffToday,
                ..
            }
        ));
    }

    #[test]
    fn reason_strings_are_fixed_and_distinct() {
        let all: Vec<&str> = CloseReason::ALL.iter().map(|r| r.as_str()).collect();
        assert_eq!(
            all,
            [
                "table_missing",
                "table_broken",
                "sha_missing",
                "sha_mismatch",
                "state_broken",
                "state_unwritable",
                "off_today",
                "assigned_off",
                "before_late",
                "after_table"
            ]
        );
    }

    #[test]
    fn recheck_on_start_day_change_and_sixty_seconds() {
        assert!(needs_recheck(0, i64::MIN, 1, 5));
        assert!(!needs_recheck(1_000, 5, 1_000 + 59_999, 5));
        assert!(needs_recheck(1_000, 5, 1_000 + 60_000, 5));
        assert!(needs_recheck(1_000, 5, 2_000, 6));
        assert!(needs_recheck(10_000, 5, 9_000, 5));
    }
}
