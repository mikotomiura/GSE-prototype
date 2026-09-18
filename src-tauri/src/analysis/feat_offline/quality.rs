//! `Q`（evidence quality）— その tick の証拠がどれだけ信頼できるかを、**計器側の事実だけ**
//! で記述する (issue 007)。
//!
//! ⚠️★★★ **`Q` は状態特徴ではない。** `.idea/survey:194` 逐語「欠測を 0 として入力せず、
//! 推論の抑制・abstention に使う」。`ADR-030 D10` 逐語「`Q` は `none` / `defer` へ退く根拠で
//! あって、認知状態の説明変数ではない」。本モジュールは出力に載せるだけで、他 Tier の計算
//! へは 1 バイトも渡さない (`super::build_feature_rows` の呼び出し順を参照)。
//!
//! # 欠測理由は計器側の事実に限る
//!
//! `missing_reasons` は次の 3 語だけから成る許可リストである。**被験者由来の理由
//! (一時停止・区間削除) は絶対に含めない** — `gse-replay --metrics --json` の出力は
//! `gse-dataset` へ共有されるため、被験者由来の理由が混じると「端末内で完結する」という
//! 削除の約束が研究者側の共有物に漏れる (`docs/o1-deletion-ledger.md`)。
//!
//! - `"capability_undeclared"` — `meta` 行に `capabilities` が無い (全行)
//! - `"hook_dead"` — `observability_mask.hook == false`、または tick 内に `alive=false` の行がある
//! - `"dropped_events"` — tick 内に `dropped_delta > 0` の `hook_health` 行がある
//!
//! `feat` 行の穴 (削除・一時停止・計器欠損のいずれか、原因は区別しない・区別してはいけない)
//! は `missing_reasons` に**理由を付けない** —— `observability_mask.feat = false` とだけ書く
//! (ADR-030 D8 (b-2))。観測区間は独自に判定せず `super::stall_onset::observed_intervals`
//! (008) をそのまま使う。

use super::stall_onset::observed_intervals;

/// `hook_health` 行 1 件 (issue 007 用の集約入力)。`dropped_delta` が欠落した旧ログ行は
/// 収集側 (`bin/replay.rs`) が `0` に正規化してから渡す (このフィールド自体は常に書かれて
/// おり、欠けるのは 2026-08-19 より前の行だけであるため「値が無い」を「0」とみなしても
/// 情報は失われない。欠測を 0 で埋めるのは *この 1 フィールドの後方互換* であって、
/// 本モジュールが計算する `missing_reasons` / `null` の規約とは別の話である)。
#[derive(Debug, Clone, Copy)]
pub struct HookHealthEvent {
    pub t_ms: u64,
    pub alive: bool,
    pub starved_ms: u64,
    pub rehook: bool,
    pub dropped_delta: u64,
}

/// tick 内に `hook_health` 行が 1 本以上あるときだけ埋まる集約値。
#[derive(Debug, Clone, Copy, PartialEq, serde::Serialize)]
pub struct QualityHookHealth {
    pub alive: bool,
    pub starved_ms: u64,
    pub rehook: bool,
    pub dropped_delta: u64,
}

/// `feat` 行 (観測区間) と `hook_health` (生存監視) それぞれの可観測性。
#[derive(Debug, Clone, Copy, PartialEq, serde::Serialize)]
pub struct ObservabilityMask {
    /// tick が 008 の観測区間 (`observed_intervals`) と交わるか。理由は付けない。
    pub feat: bool,
    /// `t < tick_end` を満たす最後の `hook_health` 行の `alive` (状態の持ち越し)。
    /// そういう行が 1 つも無ければ `None` (= 判定不能。ADR-013 D1)。
    pub hook: Option<bool>,
}

/// 1 tick ぶんの `Q`。
#[derive(Debug, Clone, PartialEq, serde::Serialize)]
pub struct Quality {
    /// `meta` 行の `capabilities` を加工せずそのまま載せる。宣言が無ければ `None`
    /// (⚠️ 空配列・空オブジェクトで埋めない)。
    pub capabilities: Option<serde_json::Value>,
    pub hook_health: Option<QualityHookHealth>,
    pub missing_reasons: Vec<String>,
    pub observability_mask: ObservabilityMask,
}

/// tick が観測区間のどれかと交わるかどうかの列 (ADR-030 D8 (b-2) の観測区間をそのまま使う)。
/// tick `k` は `[t_k, t_k + tick_ms)`、区間は `[a, b]` (閉区間・`feat` 行の実測値)。
/// 交わる条件は `t_k <= b && t_k + tick_ms > a`。
fn feat_mask_column(
    feat_ts: &[u64],
    hole_gap_ms: u64,
    tick_count: usize,
    grid_origin_ms: u64,
    tick_ms: u64,
) -> Vec<bool> {
    let intervals = observed_intervals(feat_ts, hole_gap_ms);
    let mut mask = vec![false; tick_count];
    let mut iv_idx = 0usize;
    for (k, slot) in mask.iter_mut().enumerate() {
        let t_k = grid_origin_ms + k as u64 * tick_ms;
        let tick_end = t_k + tick_ms;
        // 過去 (b < t_k) になった区間は以後の tick とも交わらないので読み飛ばす。
        while iv_idx < intervals.len() && intervals[iv_idx].1 < t_k {
            iv_idx += 1;
        }
        if let Some(&(a, b)) = intervals.get(iv_idx) {
            *slot = t_k <= b && tick_end > a;
        }
    }
    mask
}

/// 1 Hz tick 単位の `Quality` 列を作る。`super::build_feature_rows` から呼ばれる。
///
/// - `capabilities`: `meta` 行の値 (無ければ `None`)。全行にそのまま複製する。
/// - `hook_health`: `hook_health` 行の列 (時刻昇順でなくてよい)。
/// - `feat_ts` / `hole_gap_ms`: 008 の観測区間の入力と同じもの (別に読み直さない)。
pub fn quality_column(
    tick_count: usize,
    grid_origin_ms: u64,
    tick_ms: u64,
    capabilities: Option<&serde_json::Value>,
    hook_health: &[HookHealthEvent],
    feat_ts: &[u64],
    hole_gap_ms: u64,
) -> Vec<Quality> {
    let mut sorted_hh: Vec<HookHealthEvent> = hook_health.to_vec();
    sorted_hh.sort_by_key(|e| e.t_ms);

    let feat_mask = feat_mask_column(feat_ts, hole_gap_ms, tick_count, grid_origin_ms, tick_ms);
    let capability_undeclared = capabilities.is_none();

    let mut hh_idx = 0usize;
    let mut carried_alive: Option<bool> = None;
    let mut rows = Vec::with_capacity(tick_count);
    for (k, &feat) in feat_mask.iter().enumerate() {
        let t_k = grid_origin_ms + k as u64 * tick_ms;
        let tick_end = t_k + tick_ms;

        let mut tick_events: Vec<HookHealthEvent> = Vec::new();
        while hh_idx < sorted_hh.len() && sorted_hh[hh_idx].t_ms < tick_end {
            let ev = sorted_hh[hh_idx];
            carried_alive = Some(ev.alive);
            if ev.t_ms >= t_k {
                tick_events.push(ev);
            }
            hh_idx += 1;
        }

        let hook_health_field = if tick_events.is_empty() {
            None
        } else {
            Some(QualityHookHealth {
                alive: tick_events.iter().all(|e| e.alive),
                starved_ms: tick_events.iter().map(|e| e.starved_ms).max().unwrap_or(0),
                rehook: tick_events.iter().any(|e| e.rehook),
                dropped_delta: tick_events.iter().map(|e| e.dropped_delta).sum(),
            })
        };

        let mask = ObservabilityMask {
            feat,
            hook: carried_alive,
        };

        let mut reasons: Vec<String> = Vec::new();
        if capability_undeclared {
            reasons.push("capability_undeclared".to_string());
        }
        let hook_dead = mask.hook == Some(false) || tick_events.iter().any(|e| !e.alive);
        if hook_dead {
            reasons.push("hook_dead".to_string());
        }
        if tick_events.iter().any(|e| e.dropped_delta > 0) {
            reasons.push("dropped_events".to_string());
        }
        reasons.sort();

        rows.push(Quality {
            capabilities: capabilities.cloned(),
            hook_health: hook_health_field,
            missing_reasons: reasons,
            observability_mask: mask,
        });
    }
    rows
}

#[cfg(test)]
mod tests {
    use super::*;

    fn caps() -> serde_json::Value {
        serde_json::json!({
            "unconditional": ["key"],
            "threshold_gated": ["hook_health"],
            "config_gated": []
        })
    }

    fn hh(t_ms: u64, alive: bool, dropped_delta: u64) -> HookHealthEvent {
        HookHealthEvent {
            t_ms,
            alive,
            starved_ms: 0,
            rehook: false,
            dropped_delta,
        }
    }

    /// AC2: `missing_reasons` はどんな入力でも 3 語の許可リストの外に出ない。
    #[test]
    fn missing_reasons_are_instrument_side_only() {
        const ALLOWED: [&str; 3] = ["capability_undeclared", "dropped_events", "hook_dead"];
        let c = caps();
        let scenarios: Vec<Vec<Quality>> = vec![
            quality_column(5, 0, 1000, None, &[], &[], 2000),
            quality_column(5, 0, 1000, Some(&c), &[hh(500, false, 3)], &[], 2000),
            quality_column(
                10,
                0,
                1000,
                Some(&c),
                &[hh(2500, true, 0), hh(7200, false, 9)],
                &[0, 1000, 9000],
                2000,
            ),
        ];
        for rows in scenarios {
            for row in rows {
                for reason in &row.missing_reasons {
                    assert!(
                        ALLOWED.contains(&reason.as_str()),
                        "許可リスト外の理由が出た: {reason}"
                    );
                }
            }
        }
    }

    /// AC3: 被験者由来語 (一時停止 / 区間削除) がどんな入力でも出力に現れない。
    /// ⚠️ `capabilities` はそのまま複製するフィールドなので対象外
    /// (行種名としての `recording_pause` は許容される・007-acceptance.sh も除外している)。
    #[test]
    fn participant_originated_reasons_are_never_emitted() {
        let forbidden = ["recording_pause", "redaction", "redact", "participant"];
        let c = serde_json::json!({"unconditional": ["recording_pause"]});
        let rows = quality_column(5, 0, 1000, Some(&c), &[hh(500, false, 1)], &[0, 4500], 2000);
        for row in rows {
            for reason in &row.missing_reasons {
                for f in forbidden {
                    assert!(
                        !reason.contains(f),
                        "missing_reasons に被験者由来語が出た: {reason}"
                    );
                }
            }
        }
    }

    /// AC4: 欠測は `null`。`0` や空配列・空オブジェクトへフォールバックしない。
    #[test]
    fn missing_is_null_not_zero() {
        let rows = quality_column(3, 0, 1000, None, &[], &[], 2000);
        for row in &rows {
            assert_eq!(row.hook_health, None, "hook_health 行が無ければ null");
            assert_eq!(
                row.observability_mask.hook, None,
                "hook_health 未観測なら null"
            );
        }
    }

    /// AC7: `capabilities` が無い (宣言が無い) ことは `null` で表す。空配列で埋めない。
    #[test]
    fn absent_capabilities_is_null_not_empty() {
        let rows = quality_column(2, 0, 1000, None, &[], &[], 2000);
        for row in &rows {
            assert_eq!(row.capabilities, None);
            assert_eq!(
                row.missing_reasons,
                vec!["capability_undeclared".to_string()]
            );
        }
    }

    /// AC9: `feat` の穴には理由を付けない。`observability_mask.feat = false` とだけ書く。
    #[test]
    fn feat_hole_is_masked_without_a_reason() {
        let c = caps();
        // 観測区間: [0, 1000] と [5000, 6000] (間の 2000..5000 が穴)。hole_gap_ms=1000。
        let feat_ts = [0, 1000, 5000, 6000];
        let rows = quality_column(7, 0, 1000, Some(&c), &[], &feat_ts, 1000);
        // tick 2,3,4 (t_k = 2000,3000,4000) は穴 (直前の区間終端 1000 から 4000 は超えず、
        // 区間 [5000,6000] とも交わらない)。
        for idx in [2usize, 3, 4] {
            assert!(!rows[idx].observability_mask.feat, "tick {idx} は穴のはず");
            assert!(
                rows[idx].missing_reasons.is_empty(),
                "穴 tick {idx} に理由が付いた: {:?}",
                rows[idx].missing_reasons
            );
        }
        assert!(rows[0].observability_mask.feat);
        assert!(rows[5].observability_mask.feat);
    }

    /// AC10: `mask.hook` は状態を持ち越す。alive=false の後は alive=true の行が来るまで
    /// `false` のまま (`hook_dead` も立ち続ける)。
    #[test]
    fn hook_state_carries_forward_until_next_row() {
        let c = caps();
        let rows = quality_column(
            6,
            0,
            1000,
            Some(&c),
            &[hh(500, false, 0), hh(4500, true, 0)],
            &[],
            2000,
        );
        assert_eq!(rows[0].observability_mask.hook, Some(false));
        assert_eq!(rows[1].observability_mask.hook, Some(false));
        assert_eq!(rows[2].observability_mask.hook, Some(false));
        assert_eq!(rows[3].observability_mask.hook, Some(false));
        assert!(rows[3].missing_reasons.contains(&"hook_dead".to_string()));
        assert_eq!(rows[4].observability_mask.hook, Some(true));
        assert!(!rows[4].missing_reasons.contains(&"hook_dead".to_string()));
        assert_eq!(rows[5].observability_mask.hook, Some(true));
    }

    /// 境界: `hook_health` 行が 1 本も無い入力で panic しない。
    #[test]
    fn empty_hook_health_produces_null_mask_for_every_row() {
        let rows = quality_column(4, 0, 1000, None, &[], &[], 2000);
        assert_eq!(rows.len(), 4);
        for row in rows {
            assert_eq!(row.observability_mask.hook, None);
            assert_eq!(row.hook_health, None);
        }
    }
}
