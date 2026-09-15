//! `T1a` (分布・個人相対) — pause 長の分布統計 (p50/p90/max) と IKI の CV、
//! およびセッション内 baseline からの逸脱 (surprise) (ADR-030 D10)。
//!
//! ⚠️★★★ **pause の長さを「短い/中/長い」の区分に分けて意味を割り当てることはしない** —
//! [P121] は事前宣言した 4 区分すべてが成績と負相関を示し、弁別は長さではなく
//! 直前イベントにあると結論している (それは `T1b` = `boundary` の担当)。
//! ここで作るのは **分布の要約値そのもの**であって、区分ごとの解釈ではない。
//!
//! pause の判定そのものは `super::extract_pause_resumptions` (共有ヘルパ、
//! `features.rs::PAUSE_THRESHOLD_MS` が SSOT) にそのまま委ねる。本モジュールは
//! 対になる直前 press との差分から長さ (`gap_ms`) を添えるだけで、独自の pause
//! 判定や新しい数値定数は 1 つも持たない (Codex TASK-PRE 指摘 5)。
//!
//! # surprise の baseline は「セッション内」である (★ 研究者採択 2026-09-14)
//!
//! `decisions.md` 判断 3 のとおり、baseline は**このセッション内の IKI 分布**から作る。
//! ⚠️ `ADR-030 D4` の `θ_person` (個人 × `task_kind` の分位点) とは別物 — D4 は
//! `t0` 検出器の閾値の話であって、`T1a` の baseline の話ではない。混同しないこと。

/// 1 tick ぶんの `T1a` (分布・個人相対) 値。
#[derive(Debug, Clone, serde::Serialize)]
pub struct Dispersion {
    /// この tick に帰属する pause 長 (ms) の中央値相当 (nearest-rank 法)。要素 0 個なら `null`。
    pub pause_p50_ms: Option<f64>,
    /// 同じく 90 パーセンタイル相当。
    pub pause_p90_ms: Option<f64>,
    /// 同じく最大値。
    pub pause_max_ms: Option<f64>,
    /// この tick に帰属する IKI (打鍵間隔) の変動係数 (std / mean)。要素 2 個未満、
    /// または mean が 0 (同時刻打鍵のみ) なら `null`。
    pub iki_cv: Option<f64>,
    /// セッション全体の IKI baseline からのこの tick の逸脱 (z 相当: `(tick_mean - baseline_mean) / baseline_std`)。
    /// baseline が定義できない (セッション全体で IKI が 2 個未満、または分散 0) か、
    /// この tick に IKI が 1 件も無ければ `null`。
    pub surprise: Option<f64>,
}

/// セッション全体の IKI 分布から取る baseline (mean / std)。1 セッションにつき 1 回だけ
/// 計算し、各 tick の [`compute_dispersion`] に引数として渡す (AC5: シグネチャが
/// セッション全体の統計を引数に取る = tick ローカルには絶対に作り直さない)。
#[derive(Debug, Clone, Copy)]
pub struct SessionIkiBaseline {
    mean_ms: f64,
    std_ms: f64,
}

impl SessionIkiBaseline {
    /// セッション全体 (全 tick 分をまとめた) の IKI 値から baseline を作る。
    /// 2 個未満、または分散が 0 (全値が同一) だと z 相当の分母が定義できないため `None`。
    pub fn from_session_iki(all_iki_ms: &[u64]) -> Option<Self> {
        if all_iki_ms.len() < 2 {
            return None;
        }
        let mean_ms = mean(all_iki_ms)?;
        let variance = all_iki_ms
            .iter()
            .map(|&v| {
                let d = v as f64 - mean_ms;
                d * d
            })
            .sum::<f64>()
            / all_iki_ms.len() as f64;
        let std_ms = variance.sqrt();
        if std_ms == 0.0 {
            return None;
        }
        Some(Self { mean_ms, std_ms })
    }
}

fn mean(values: &[u64]) -> Option<f64> {
    if values.is_empty() {
        return None;
    }
    Some(values.iter().map(|&v| v as f64).sum::<f64>() / values.len() as f64)
}

/// nearest-rank 法 (線形補間なし) で分位点を取る。`sorted_ascending` は昇順ソート済みを
/// 仮定する。要素 0 個なら `None` (**呼び出し側は 0 で埋めない**)。
/// `rank = ceil(q * n)` (1-indexed, `[1, n]` にクランプ) — 標準的な nearest-rank 定義。
fn quantile(sorted_ascending: &[u64], q: f64) -> Option<f64> {
    let n = sorted_ascending.len();
    if n == 0 {
        return None;
    }
    let rank = (q * n as f64).ceil() as usize;
    let idx = rank.clamp(1, n) - 1;
    Some(sorted_ascending[idx] as f64)
}

/// IKI 値の変動係数 (std / mean)。2 個未満、または mean が 0 (同時刻打鍵のみ) なら `None`。
fn coefficient_of_variation(values: &[u64]) -> Option<f64> {
    if values.len() < 2 {
        return None;
    }
    let m = mean(values)?;
    if m == 0.0 {
        return None;
    }
    let variance = values
        .iter()
        .map(|&v| {
            let d = v as f64 - m;
            d * d
        })
        .sum::<f64>()
        / values.len() as f64;
    Some(variance.sqrt() / m)
}

/// pause 1 件ぶんの長さ。`resuming_ts` は帰属先 tick の判定に使う
/// (`super::build_feature_rows` の「pause は再開側の tick に帰属する」規則と対称)。
#[derive(Debug, Clone, Copy)]
pub struct PauseDuration {
    pub resuming_ts: u64,
    pub gap_ms: u64,
}

/// press 時刻列から pause (長さ付き) の列を作る。pause の判定は `super::extract_pause_resumptions`
/// (共有ヘルパ) にそのまま委ね、本関数は対になる直前 press との差分から長さを添えるだけ
/// (`boundary::pause_boundary_pairs` と対称の手法。判定を再実装しない)。
pub fn pause_durations(press_ts: &[u64]) -> Vec<PauseDuration> {
    let mut sorted: Vec<u64> = press_ts.to_vec();
    sorted.sort_unstable();
    let resumptions = super::extract_pause_resumptions(&sorted);

    let mut pending = resumptions.into_iter();
    let mut next_expected = pending.next();
    let mut out = Vec::new();
    for i in 1..sorted.len() {
        let Some(expected) = next_expected else {
            break;
        };
        if sorted[i] == expected {
            out.push(PauseDuration {
                resuming_ts: sorted[i],
                gap_ms: sorted[i].saturating_sub(sorted[i - 1]),
            });
            next_expected = pending.next();
        }
    }
    out
}

/// tick ごとの `Dispersion` を作る純関数。`pause_ms_in_tick` / `iki_ms_in_tick` は
/// 呼び出し側 (`super::build_feature_rows`) が既に tick へ帰属済みの値を渡す
/// (`activity::compute_t0_activity` / `boundary::compute_boundary` と対称)。
/// `baseline` はセッション全体から一度だけ作ったものを渡す (tick ごとに作り直さない)。
pub fn compute_dispersion(
    pause_ms_in_tick: &[u64],
    iki_ms_in_tick: &[u64],
    baseline: Option<&SessionIkiBaseline>,
) -> Dispersion {
    let mut sorted_pause: Vec<u64> = pause_ms_in_tick.to_vec();
    sorted_pause.sort_unstable();

    let surprise = match (mean(iki_ms_in_tick), baseline) {
        (Some(tick_mean), Some(b)) => Some((tick_mean - b.mean_ms) / b.std_ms),
        _ => None,
    };

    Dispersion {
        pause_p50_ms: quantile(&sorted_pause, 0.5),
        pause_p90_ms: quantile(&sorted_pause, 0.9),
        pause_max_ms: quantile(&sorted_pause, 1.0),
        iki_cv: coefficient_of_variation(iki_ms_in_tick),
        surprise,
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    /// AC2: 分位点が境界値 (要素 0 / 1 / 2 / 偶数 / 奇数個) で正しい。
    #[test]
    fn quantiles_handle_boundary_sizes() {
        assert_eq!(quantile(&[], 0.5), None);
        assert_eq!(quantile(&[], 1.0), None);

        assert_eq!(quantile(&[42], 0.5), Some(42.0));
        assert_eq!(quantile(&[42], 0.9), Some(42.0));
        assert_eq!(quantile(&[42], 1.0), Some(42.0));

        let two = [10, 20];
        assert_eq!(quantile(&two, 0.5), Some(10.0));
        assert_eq!(quantile(&two, 0.9), Some(20.0));
        assert_eq!(quantile(&two, 1.0), Some(20.0));

        let even = [10, 20, 30, 40];
        assert_eq!(quantile(&even, 0.5), Some(20.0));
        assert_eq!(quantile(&even, 1.0), Some(40.0));

        let odd = [10, 20, 30, 40, 50];
        assert_eq!(quantile(&odd, 0.5), Some(30.0));
        assert_eq!(quantile(&odd, 0.9), Some(50.0));
        assert_eq!(quantile(&odd, 1.0), Some(50.0));
    }

    /// AC4: 要素が 0 個のとき `dispersion` の全フィールドが `null` (0 で埋めない)。
    #[test]
    fn empty_window_is_null_not_zero() {
        let d = compute_dispersion(&[], &[], None);
        assert_eq!(d.pause_p50_ms, None);
        assert_eq!(d.pause_p90_ms, None);
        assert_eq!(d.pause_max_ms, None);
        assert_eq!(d.iki_cv, None);
        assert_eq!(d.surprise, None);
    }

    /// AC5: surprise はセッション全体の baseline (関数の引数) からの逸脱として計算される
    /// — tick ローカルの値だけからは作り直さない。
    #[test]
    fn surprise_is_session_relative() {
        // mean=100, std=20 になるよう選んだセッション全体の IKI。
        let session_iki = vec![80, 120, 80, 120];
        let baseline = SessionIkiBaseline::from_session_iki(&session_iki).expect("variance > 0");

        let spike = compute_dispersion(&[], &[140], Some(&baseline));
        assert_eq!(spike.surprise, Some(2.0)); // (140 - 100) / 20

        let calm = compute_dispersion(&[], &[100], Some(&baseline));
        assert_eq!(calm.surprise, Some(0.0));

        // baseline が無い (呼び出し側がセッション全体で分散 0 等と判断した) tick は null。
        let no_baseline = compute_dispersion(&[], &[140], None);
        assert_eq!(no_baseline.surprise, None);
    }

    #[test]
    fn pause_durations_pairs_gap_with_resuming_ts() {
        use crate::analysis::features::PAUSE_THRESHOLD_MS;
        let press_ts = vec![0, PAUSE_THRESHOLD_MS, PAUSE_THRESHOLD_MS + 100];
        let durations = pause_durations(&press_ts);
        // 0 -> PAUSE_THRESHOLD_MS は閾値ちょうどで pause、続く +100 は pause でない。
        assert_eq!(durations.len(), 1);
        assert_eq!(durations[0].resuming_ts, PAUSE_THRESHOLD_MS);
        assert_eq!(durations[0].gap_ms, PAUSE_THRESHOLD_MS);
    }

    #[test]
    fn iki_cv_needs_at_least_two_points() {
        assert_eq!(coefficient_of_variation(&[]), None);
        assert_eq!(coefficient_of_variation(&[100]), None);
        // mean == 0 (同時刻打鍵のみ) は除算不能なので null。
        assert_eq!(coefficient_of_variation(&[0, 0]), None);
        // std とmean が等しくなる (gap 0 と 2*mean の2点) ため cv はちょうど 1.0。
        assert_eq!(coefficient_of_variation(&[0, 2000]), Some(1.0));
    }
}
