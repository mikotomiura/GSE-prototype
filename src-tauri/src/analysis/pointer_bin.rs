//! ポインタ活動の **1 秒ビン量子化**（O1 / ADR-014 **D4** の L-b 仕様）。
//!
//! ## ⚠️★★★ なぜ「量子化スカラだけ」なのか
//!
//! ★ ADR-014 D4 の禁止表は逐語でこう書いている:
//!
//! | 入れないもの | ⚠️ 理由 |
//! |---|---|
//! | **符号付き `dx`/`dy`（イベント単位）/ 絶対座標 / 解像度 / マルチモニタ配置** | ★ **累積すれば軌跡が復元でき画面内容の代理になる** |
//! | **イベント単位の移動量＋時刻の列** | ★ **mouse dynamics は個人識別可能な生体特徴**である |
//!
//! → ★★★ **1 秒ビンに畳んだ粗いバケットだけ**を残す。⚠️ 位置は 1 バイトも持たない。
//!
//! ## ★ なぜポインタが要るのか（★ 「あると便利」ではない）
//!
//! ⚠️ `starved_ms` は `GetLastInputInfo`（**マウス込み**）なので、
//! ★ **「マウスで作業していた」と「離席」を原理的に分離できない**（`liveness.rs` が
//! 既知の誤検知を「仕様」としてテストで固定している）。
//! → ★ O1 が保証する唯一のこと ——「**非打鍵作業を離席と誤分類しない**」—— が
//! このチャネル無しには成立しない。
//!
//! ## ⚠️ OS API を呼ばない
//!
//! ★ 生の移動量を受け取って**数に畳むだけ**の純関数である。
//! 生の値は `input/` の中で消え、⚠️ **ここから先へ 1 度も出ない**。

/// NDJSON に書く 1 秒ぶんのポインタ活動。
///
/// ⚠️★★★ **フィールドはこの 4 つで固定**である。★ 座標・方向・速度・軌跡は持たない。
#[derive(Debug, Clone, Copy, PartialEq, Eq)]
pub struct PointerBin {
    /// ビンの終端時刻（ms）。
    pub timestamp: u64,
    /// 移動量のバケット `0..=7`（★ [`quantize_move`] の doc に閾値表）。
    pub moved: u8,
    /// ビン内のボタン **押下** 回数（★ 0..=15 に飽和）。⚠️ どのボタンかは持たない。
    pub buttons: u8,
    /// ビン内のホイール **刻み** 回数（★ 0..=15 に飽和）。⚠️ 向き（上下）は持たない。
    pub wheel: u8,
}

impl PointerBin {
    /// ⚠️★★★ **ゼロ抑制**（ADR-014 D4 の L-b 仕様 / D5）。
    ///
    /// ★ 何も起きていない秒は **行を書かない**。⚠️ 書くと「在席の連続タイムライン」が
    /// 毎秒 1 行の密な形になり、★ **記録量が増える一方で情報は増えない**。
    pub fn is_empty(&self) -> bool {
        self.moved == 0 && self.buttons == 0 && self.wheel == 0
    }
}

/// ビン内で積んだ**生の**カウンタ。★ `input/` の中だけで生き、外へ出ない。
#[derive(Debug, Clone, Copy, Default, PartialEq, Eq)]
pub struct PointerAccum {
    /// ⚠️★★★ **符号を落とした移動量の総和** `Σ(|dx| + |dy|)`。
    ///
    /// ★ 符号を捨てるのは**足す前**である（⚠️ 後から捨てても方向は既に漏れている）。
    /// ★ ユークリッド距離ではなくマンハッタン和にするのは、**平方根の精度差で
    /// 端末ごとにバケット境界がずれるのを避ける**ため。
    pub abs_delta_sum: u64,
    /// ボタン押下回数（★ 離上は数えない）。
    pub button_presses: u32,
    /// ホイールの刻み回数（★ 絶対値）。
    pub wheel_ticks: u32,
}

impl PointerAccum {
    /// 移動を 1 件足す。⚠️ **呼び出し側で符号を落とす必要はない**（ここで落とす）。
    pub fn add_move(&mut self, dx: i32, dy: i32) {
        let d = (dx.unsigned_abs() as u64).saturating_add(dy.unsigned_abs() as u64);
        self.abs_delta_sum = self.abs_delta_sum.saturating_add(d);
    }

    pub fn add_button_press(&mut self) {
        self.button_presses = self.button_presses.saturating_add(1);
    }

    /// ホイールを 1 件足す。⚠️ 向きは捨てる。
    pub fn add_wheel(&mut self, delta: i32) {
        if delta != 0 {
            self.wheel_ticks = self.wheel_ticks.saturating_add(1);
        }
    }

    /// ビンを閉じて量子化する。★ 呼んだ側は [`PointerBin::is_empty`] でゼロ抑制する。
    pub fn close(self, timestamp: u64) -> PointerBin {
        PointerBin {
            timestamp,
            moved: quantize_move(self.abs_delta_sum),
            buttons: saturate_count(self.button_presses),
            wheel: saturate_count(self.wheel_ticks),
        }
    }
}

/// 移動量の総和を **8 段のバケット** に落とす。
///
/// ⚠️★★★ **粗さは意図である。** ★ 生のマウス単位はデバイス依存（DPI / ポーリングレート）なので、
/// 細かく残しても端末間で比較できないうえ、⚠️ **細かいほど個人識別性が上がる**。
///
/// | バケット | `Σ(|dx|+|dy|)` |
/// |---|---|
/// | 0 | 0（★ 完全に静止） |
/// | 1 | 1–8 |
/// | 2 | 9–32 |
/// | 3 | 33–128 |
/// | 4 | 129–512 |
/// | 5 | 513–2048 |
/// | 6 | 2049–8192 |
/// | 7 | 8193 以上 |
pub fn quantize_move(abs_delta_sum: u64) -> u8 {
    match abs_delta_sum {
        0 => 0,
        1..=8 => 1,
        9..=32 => 2,
        33..=128 => 3,
        129..=512 => 4,
        513..=2048 => 5,
        2049..=8192 => 6,
        _ => 7,
    }
}

/// 回数を `0..=15` に飽和させる。
///
/// ⚠️ 上限を置くのは、★ **異常な連打が回数そのもので個人を特徴づけるのを防ぐ**ためである。
pub fn saturate_count(n: u32) -> u8 {
    n.min(15) as u8
}

#[cfg(test)]
mod tests {
    use super::*;

    /// ⚠️★★★ **符号が残っていないこと**（★ 軌跡復元の入口を塞ぐ）。
    #[test]
    fn opposite_movements_are_indistinguishable() {
        let mut a = PointerAccum::default();
        a.add_move(10, 0);
        let mut b = PointerAccum::default();
        b.add_move(-10, 0);
        let mut c = PointerAccum::default();
        c.add_move(0, 10);
        assert_eq!(a.abs_delta_sum, b.abs_delta_sum, "左右が区別できてしまう");
        assert_eq!(a.abs_delta_sum, c.abs_delta_sum, "縦横が区別できてしまう");
    }

    /// ⚠️ 往復して原点へ戻る動きが「動いていない」に潰れないこと（★ 活動量としては正しく増える）。
    #[test]
    fn round_trip_movement_still_counts_as_activity() {
        let mut a = PointerAccum::default();
        a.add_move(50, 0);
        a.add_move(-50, 0);
        assert_eq!(a.abs_delta_sum, 100);
        assert!(!a.close(0).is_empty());
    }

    /// ★ バケット境界を上下で固定する。
    #[test]
    fn move_buckets_are_stable_at_their_boundaries() {
        for (sum, want) in [
            (0u64, 0u8),
            (1, 1),
            (8, 1),
            (9, 2),
            (32, 2),
            (33, 3),
            (128, 3),
            (129, 4),
            (512, 4),
            (513, 5),
            (2048, 5),
            (2049, 6),
            (8192, 6),
            (8193, 7),
            (u64::MAX, 7),
        ] {
            assert_eq!(quantize_move(sum), want, "Σ={sum} のバケット");
        }
    }

    /// ⚠️ 回数は 15 で頭打ち。
    #[test]
    fn counts_saturate_at_fifteen() {
        assert_eq!(saturate_count(0), 0);
        assert_eq!(saturate_count(15), 15);
        assert_eq!(saturate_count(16), 15);
        assert_eq!(saturate_count(u32::MAX), 15);
    }

    /// ⚠️★★★ **ゼロ抑制**: 何も起きていない秒は行にしない。
    #[test]
    fn empty_bin_is_suppressed() {
        assert!(PointerAccum::default().close(1000).is_empty());

        let mut only_move = PointerAccum::default();
        only_move.add_move(1, 0);
        assert!(!only_move.close(1000).is_empty());

        let mut only_button = PointerAccum::default();
        only_button.add_button_press();
        assert!(!only_button.close(1000).is_empty());

        let mut only_wheel = PointerAccum::default();
        only_wheel.add_wheel(-1);
        assert!(!only_wheel.close(1000).is_empty());
    }

    /// ⚠️ ホイールの向きを持たない。
    #[test]
    fn wheel_direction_is_discarded() {
        let mut up = PointerAccum::default();
        up.add_wheel(120);
        let mut down = PointerAccum::default();
        down.add_wheel(-120);
        assert_eq!(up.wheel_ticks, down.wheel_ticks);
        assert_eq!(up.close(0), down.close(0));
    }

    /// ⚠️ 0 のホイールイベントは数えない (★ 一部ドライバが送ってくる)。
    #[test]
    fn zero_wheel_delta_is_not_counted() {
        let mut a = PointerAccum::default();
        a.add_wheel(0);
        assert_eq!(a.wheel_ticks, 0);
    }

    /// ⚠️ 巨大な移動でオーバーフローしない。
    #[test]
    fn accumulation_saturates_instead_of_overflowing() {
        let mut a = PointerAccum {
            abs_delta_sum: u64::MAX - 1,
            ..Default::default()
        };
        a.add_move(i32::MIN, i32::MIN);
        assert_eq!(a.abs_delta_sum, u64::MAX);
        assert_eq!(a.close(0).moved, 7);
    }
}
