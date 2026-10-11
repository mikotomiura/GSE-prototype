//! 肖像の更新の予定（U-4 の型 `recent`・OS API 非依存）。
//!
//! EH1 第 5 回の `portrait.py` の `schedule`（`kind="recent"`）の、時刻を 1 つずつ受け取る形への移植。
//! 親の判断 13（U-4 の確定）と R-P3:
//! - 予定はセッションの始まりから `INTERVAL_MS` ごと。
//! - 打鍵の最中（予定の時刻の前 `WINDOW_MS` に打鍵がある）は、その予定を飛ばして次へ。
//! - `RECENT_MS` 以上の不在の中では更新しない（予定の前 `RECENT_MS` に打鍵が無ければ飛ばす）。
//! - スリープ中に過ぎた予定は取り戻さない（実時間が飛んだら、過ぎた予定は捨てる）。

/// 予定の間隔（EH1 の既定 300 s）。
pub const INTERVAL_MS: u64 = 300_000;
/// 打鍵の最中とみなす窓（EH1 の既定 5 s）。
pub const WINDOW_MS: u64 = 5_000;
/// 不在とみなす長さ（U-4: 60 s）。
pub const RECENT_MS: u64 = 60_000;
/// 予定を過ぎてからこれ以上たって気づいたものは、スリープなどで過ぎたとみなして捨てる。
pub const LATE_TOLERANCE_MS: u64 = 2_000;

/// 1 セッションの予定。
#[derive(Debug, Clone)]
pub struct Schedule {
    next_slot_ms: u64,
}

impl Schedule {
    /// セッションの始まり（予定の起点）。
    pub fn new(session_start_ms: u64) -> Self {
        Self {
            next_slot_ms: session_start_ms + INTERVAL_MS,
        }
    }

    /// `now_ms` までに来た予定のうち、更新すべきものがあれば `true`（1 回の呼び出しで高々 1 回）。
    ///
    /// `presses` は直近の打鍵の時刻（昇順。少なくとも直近 `RECENT_MS + LATE_TOLERANCE_MS` を含む）。
    /// 予定の時刻 `u` 以前の最後の打鍵 1 つで、「窓の中に打鍵があるか」「直近 60 s に打鍵があるか」の
    /// 両方が決まる（`_has_press(lo, hi]` と同じ）。`u` より後の打鍵は見ない。
    pub fn due(&mut self, now_ms: u64, presses: &[u64]) -> bool {
        let mut fire = false;
        while self.next_slot_ms <= now_ms {
            let u = self.next_slot_ms;
            self.next_slot_ms += INTERVAL_MS;
            if now_ms - u > LATE_TOLERANCE_MS {
                continue; // スリープなどで過ぎた予定は取り戻さない
            }
            let Some(p) = presses.iter().rev().find(|p| **p <= u).copied() else {
                continue; // まだ打鍵が無い = 不在の中
            };
            if u - p < WINDOW_MS {
                continue; // 打鍵の最中
            }
            if u - p >= RECENT_MS {
                continue; // 60 s 以上の不在の中
            }
            fire = true;
        }
        fire
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    const S0: u64 = 1_000_000;

    #[test]
    fn fires_at_a_slot_after_a_short_pause() {
        let mut s = Schedule::new(S0);
        let slot = S0 + INTERVAL_MS;
        assert!(!s.due(slot - 1, &[slot - 20_000]));
        assert!(
            s.due(slot, &[slot - 20_000]),
            "20 秒前に打鍵: 打鍵の最中でも不在でもない"
        );
    }

    #[test]
    fn skips_while_typing_and_inside_an_absence() {
        let slot = S0 + INTERVAL_MS;
        let mut s = Schedule::new(S0);
        assert!(!s.due(slot, &[slot - 2_000]), "打鍵の最中は飛ばす");
        let mut s = Schedule::new(S0);
        assert!(
            !s.due(slot, &[slot - 60_000]),
            "60 秒以上の不在の中では更新しない"
        );
        let mut s = Schedule::new(S0);
        assert!(!s.due(slot, &[]), "打鍵がまだ無い");
        // 飛ばした予定は次の予定へ（取り戻さない）
        assert!(!s.due(slot + 1000, &[slot - 20_000]));
        assert!(s.due(slot + INTERVAL_MS, &[slot + INTERVAL_MS - 20_000]));
    }

    #[test]
    fn a_press_just_after_the_slot_is_not_seen() {
        // 予定を 1 秒過ぎて評価した: 予定の後の打鍵は見ず、予定以前の最後の打鍵で決める
        let slot = S0 + INTERVAL_MS;
        let mut s = Schedule::new(S0);
        assert!(s.due(slot + 1000, &[slot - 20_000, slot + 500]));
    }

    #[test]
    fn slots_passed_during_sleep_are_not_caught_up() {
        let mut s = Schedule::new(S0);
        // 3 回ぶんの予定を寝過ごして起きた
        let wake = S0 + 3 * INTERVAL_MS + 30_000;
        assert!(!s.due(wake, &[wake - 10_000]), "過ぎた予定は捨てる");
        let next = S0 + 4 * INTERVAL_MS;
        assert!(s.due(next, &[next - 10_000]), "起きた後の次の予定から");
    }
}
