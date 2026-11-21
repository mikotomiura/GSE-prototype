//! `context` = **文脈の量**（`docs/glossary.md`）の 1 tick ぶんの数。
//!
//! 研究解析の層で区間を作業の文脈でまとめるための材料である
//! （`.steering/20261121-auto-context-segmentation/`）。
//!
//! - 窓で集約しない。tick の中の数だけを出し、窓の長さは解析側の引数にする（design.md v2 の 1）。
//! - **推論に流さない**（ADR-014 D4b）。この列は他の Tier（`activity` / `stall_onset` / `restart` など）の
//!   計算へも、`features.rs` / `engine.rs` / `FeatSnapshot` へも渡さない。出力にだけ載せる。
//! - 観測から種別を作らない（ADR-010 D3・ADR-012 D3）。ここにあるのは数だけで、名前は付けない。
//!
//! ## 欠測の読み方
//!
//! 非打鍵の列（`focus_transitions` / `pointer_*` / `ime_on`）は、入力が `None` なら全 tick で `null`。
//! `None` にするか `Some(&[])` にするかは**呼び出し側**が `capabilities` から決める
//! （`analysis/` に `capabilities` の意味を持ち込まない。極 B の `pointer_active_ts` と同じ作法）。
//! `Some(..)` なら、行の無い tick は 0（`focus_transitions`）または `false`（`pointer_active`）である。
//!
//! ## tick への帰属
//!
//! - `focus_transition` 行: 時刻 `t` を含む tick。
//! - `pointer_bin` 行: 時刻 `t` は**ビンの終端**で、行は `(t − 1000, t]` を覆う（`pointer_bin.rs`）。
//!   `t − 1` ms を含む tick に帰属させる。ビンと tick が揃っていれば覆う 1 秒がそのまま 1 tick になり、
//!   ずれていても覆う時間の大半が入る tick になる（終端 `t` の tick に入れると、ビンが揃ったときに
//!   1 ms しか重ならない次の tick へずれる・code-reviewer LOW）。
//! - `ime_state` 行: tick の終端（`tick_end − 1` ms）の時点で効いている状態。tick の中で何度切り替わっても
//!   最後の状態だけを見る。最初の `ime_state` 行より前の tick は `null`（状態が分からない）。
//! - グリッドの外（原点より前・右端より後）の行は数えない。グリッドは打鍵などの入力だけで決まる
//!   （`mod.rs` の原点の規則）ので、非打鍵の行がグリッドを広げることはない。
//!   ただし `ime_state` だけは状態なので、原点より前の行の状態を最初の tick へ繰り越す。

use std::collections::BTreeMap;

use crate::analysis::anonymize::KeyCategory;
use crate::analysis::metrics::KeyPress;

/// `pointer_bin` 行のうち、`context` が読む値。
#[derive(Debug, Clone, Copy, PartialEq, Eq)]
pub struct PointerBinLite {
    /// ビンの終端時刻（絶対 epoch ms）。
    pub t: u64,
    /// 移動量のバケット `0..=7`。
    pub moved: u8,
}

/// `ime_state` 行のうち、`context` が読む値。
#[derive(Debug, Clone, Copy, PartialEq, Eq)]
pub struct ImeStateLite {
    pub t: u64,
    /// IME モードがオンか（`ime_state.on`）。
    pub on: bool,
}

/// `context` の入力。`None` は「その列を出さない（全 tick で null）」。
#[derive(Debug, Clone, Copy, Default)]
pub struct ContextInputs<'a> {
    /// `focus_transition` 行の時刻（順不同でよい）。
    pub focus_ts: Option<&'a [u64]>,
    /// `pointer_bin` 行（順不同でよい）。
    pub pointer_bins: Option<&'a [PointerBinLite]>,
    /// `ime_state` 行（順不同でよい）。
    pub ime_states: Option<&'a [ImeStateLite]>,
}

/// 1 tick ぶんの `context`。
#[derive(Debug, Clone, Default, PartialEq, Eq, serde::Serialize)]
pub struct Context {
    /// tick 内の全 press の `KeyCategory` ごとの数（観測されたものだけ・疎な map）。
    /// 合計は `activity.keys` と一致する。
    /// `boundary.prev_cat_counts` / `next_cat_counts`（pause の直前・直後だけ）とは別物である。
    pub cat_counts: BTreeMap<String, u64>,
    /// tick 内の `focus_transition` 行の数。同じアプリの中の窓の切り替えも 1 回に数えるので、
    /// **注意の逸脱の頻度として読まない**（`schema_dto.rs` の `FocusTransition` の doc）。
    pub focus_transitions: Option<u64>,
    /// tick に帰属する `pointer_bin` 行があるか（ゼロ抑制なので、行がある＝その秒に活動があった）。
    pub pointer_active: Option<bool>,
    /// tick に帰属する `pointer_bin` 行の `moved` の合計（行が無ければ 0）。
    pub pointer_moved: Option<u64>,
    /// tick の終端で IME モードがオンか。
    pub ime_on: Option<bool>,
}

/// 全 tick の `context` を作る。`keys` は press だけ（`mod.rs` と同じ列）。
pub fn context_column(
    keys: &[KeyPress],
    inputs: &ContextInputs,
    tick_count: usize,
    grid_origin_ms: u64,
    tick_ms: u64,
) -> Vec<Context> {
    let tick_of = |t: u64| -> Option<usize> {
        if t < grid_origin_ms || tick_ms == 0 {
            return None;
        }
        let idx = ((t - grid_origin_ms) / tick_ms) as usize;
        (idx < tick_count).then_some(idx)
    };

    let mut cat_counts: Vec<BTreeMap<String, u64>> = vec![BTreeMap::new(); tick_count];
    for k in keys {
        if let Some(idx) = tick_of(k.timestamp) {
            *cat_counts[idx]
                .entry(KeyCategory::from_vk(k.vk).as_str().to_string())
                .or_insert(0) += 1;
        }
    }

    let focus: Option<Vec<u64>> = inputs.focus_ts.map(|ts| {
        let mut v = vec![0u64; tick_count];
        for &t in ts {
            if let Some(idx) = tick_of(t) {
                v[idx] += 1;
            }
        }
        v
    });

    let pointer: Option<Vec<(bool, u64)>> = inputs.pointer_bins.map(|bins| {
        let mut v = vec![(false, 0u64); tick_count];
        for b in bins {
            // `(t − 1000, t]` を覆う。`t − 1` を含む tick に帰属させる（モジュール doc）。
            if let Some(idx) = tick_of(b.t.saturating_sub(1)) {
                v[idx].0 = true;
                v[idx].1 += u64::from(b.moved);
            }
        }
        v
    });

    let ime: Option<Vec<Option<bool>>> = inputs.ime_states.map(|states| {
        let mut sorted = states.to_vec();
        // 同じ時刻の行は入力の順を保つ（安定ソート）。後の行が勝つ。
        sorted.sort_by_key(|s| s.t);
        let mut v = vec![None; tick_count];
        let mut j = 0usize;
        let mut current: Option<bool> = None;
        for (idx, slot) in v.iter_mut().enumerate() {
            // tick の終端（排他）= 原点 + (idx + 1) × tick_ms。それより前の行までを反映する。
            let tick_end = grid_origin_ms.saturating_add((idx as u64 + 1) * tick_ms);
            while j < sorted.len() && sorted[j].t < tick_end {
                current = Some(sorted[j].on);
                j += 1;
            }
            *slot = current;
        }
        v
    });

    (0..tick_count)
        .map(|idx| Context {
            cat_counts: std::mem::take(&mut cat_counts[idx]),
            focus_transitions: focus.as_ref().map(|v| v[idx]),
            pointer_active: pointer.as_ref().map(|v| v[idx].0),
            pointer_moved: pointer.as_ref().map(|v| v[idx].1),
            ime_on: ime.as_ref().and_then(|v| v[idx]),
        })
        .collect()
}

#[cfg(test)]
mod tests {
    use super::*;

    const TICK: u64 = 1000;
    const ORIGIN: u64 = 1_000_000;

    fn key(t: u64, vk: u32) -> KeyPress {
        KeyPress { timestamp: t, vk }
    }

    #[test]
    fn none_inputs_give_null_columns_but_keep_cat_counts() {
        let keys = [key(ORIGIN, 0x41), key(ORIGIN + 10, 0x20)];
        let col = context_column(&keys, &ContextInputs::default(), 2, ORIGIN, TICK);
        assert_eq!(col.len(), 2);
        assert_eq!(col[0].cat_counts.get("alphabetic"), Some(&1));
        assert_eq!(col[0].cat_counts.get("space"), Some(&1));
        assert!(col[1].cat_counts.is_empty());
        for c in &col {
            assert_eq!(c.focus_transitions, None);
            assert_eq!(c.pointer_active, None);
            assert_eq!(c.pointer_moved, None);
            assert_eq!(c.ime_on, None);
        }
    }

    #[test]
    fn empty_some_inputs_give_zero_not_null() {
        let inputs = ContextInputs {
            focus_ts: Some(&[]),
            pointer_bins: Some(&[]),
            ime_states: Some(&[]),
        };
        let col = context_column(&[], &inputs, 3, ORIGIN, TICK);
        for c in &col {
            assert_eq!(c.focus_transitions, Some(0));
            assert_eq!(c.pointer_active, Some(false));
            assert_eq!(c.pointer_moved, Some(0));
            // `ime_state` 行が 1 本も無ければ状態は分からない。
            assert_eq!(c.ime_on, None);
        }
    }

    /// 陽性対照: focus を 1 行足すと、その tick の `focus_transitions` だけが 1 増える。
    #[test]
    fn one_focus_row_moves_only_its_tick() {
        let base = ContextInputs {
            focus_ts: Some(&[]),
            ..Default::default()
        };
        let before = context_column(&[], &base, 3, ORIGIN, TICK);
        let one = [ORIGIN + 1500];
        let after = context_column(
            &[],
            &ContextInputs {
                focus_ts: Some(&one),
                ..Default::default()
            },
            3,
            ORIGIN,
            TICK,
        );
        assert_eq!(after[1].focus_transitions, Some(1));
        assert_eq!(after[0], before[0]);
        assert_eq!(after[2], before[2]);
    }

    #[test]
    fn tick_edges_are_half_open() {
        let ts = [ORIGIN + 999, ORIGIN + 1000];
        let col = context_column(
            &[],
            &ContextInputs {
                focus_ts: Some(&ts),
                ..Default::default()
            },
            2,
            ORIGIN,
            TICK,
        );
        assert_eq!(col[0].focus_transitions, Some(1));
        assert_eq!(col[1].focus_transitions, Some(1));
    }

    #[test]
    fn rows_outside_the_grid_are_not_counted() {
        let ts = [ORIGIN - 1, ORIGIN + 2000];
        let col = context_column(
            &[],
            &ContextInputs {
                focus_ts: Some(&ts),
                ..Default::default()
            },
            2,
            ORIGIN,
            TICK,
        );
        assert_eq!(col[0].focus_transitions, Some(0));
        assert_eq!(col[1].focus_transitions, Some(0));
    }

    #[test]
    fn pointer_bin_is_attributed_by_its_end_time_and_moved_sums() {
        // 終端 ORIGIN+2000 は (ORIGIN+1000, ORIGIN+2000] を覆う = tick 1 にちょうど揃う。
        // 終端 ORIGIN+1500 は (ORIGIN+500, ORIGIN+1500] を覆い、t−1 = ORIGIN+1499 も tick 1。
        let bins = [
            PointerBinLite {
                t: ORIGIN + 2000,
                moved: 3,
            },
            PointerBinLite {
                t: ORIGIN + 1500,
                moved: 2,
            },
        ];
        let col = context_column(
            &[],
            &ContextInputs {
                pointer_bins: Some(&bins),
                ..Default::default()
            },
            3,
            ORIGIN,
            TICK,
        );
        assert_eq!(col[0].pointer_active, Some(false));
        assert_eq!(col[1].pointer_active, Some(true));
        assert_eq!(col[1].pointer_moved, Some(5));
        assert_eq!(col[2].pointer_active, Some(false));
    }

    #[test]
    fn ime_on_carries_forward_and_last_change_in_tick_wins() {
        let states = [
            ImeStateLite {
                t: ORIGIN + 1200,
                on: true,
            },
            ImeStateLite {
                t: ORIGIN + 1800,
                on: false,
            },
            ImeStateLite {
                t: ORIGIN + 2100,
                on: true,
            },
        ];
        let col = context_column(
            &[],
            &ContextInputs {
                ime_states: Some(&states),
                ..Default::default()
            },
            5,
            ORIGIN,
            TICK,
        );
        assert_eq!(col[0].ime_on, None);
        assert_eq!(col[1].ime_on, Some(false));
        assert_eq!(col[2].ime_on, Some(true));
        assert_eq!(col[3].ime_on, Some(true));
        assert_eq!(col[4].ime_on, Some(true));
    }

    #[test]
    fn cat_counts_sum_equals_presses_in_tick() {
        let keys = [
            key(ORIGIN, 0x41),
            key(ORIGIN + 1, 0x42),
            key(ORIGIN + 2, 0x08),
            key(ORIGIN + 3, 0xA0),
            key(ORIGIN + 1001, 0x0D),
        ];
        let col = context_column(&keys, &ContextInputs::default(), 2, ORIGIN, TICK);
        assert_eq!(col[0].cat_counts.values().sum::<u64>(), 4);
        assert_eq!(col[0].cat_counts.get("alphabetic"), Some(&2));
        assert_eq!(col[0].cat_counts.get("backspace"), Some(&1));
        assert_eq!(col[0].cat_counts.get("modifier"), Some(&1));
        assert_eq!(col[1].cat_counts.values().sum::<u64>(), 1);
    }
}
