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
///
/// # ⚠️★★★ **`pause_p50_ms` / `pause_p90_ms` / `pause_max_ms` は現状つねに同値である**
///
/// ★ 2026-09-15 の `code-reviewer` HIGH-1。**構造的な帰結であって、バグではない**:
///
/// - `features::PAUSE_THRESHOLD_MS` (= 2000ms) > `loop_step::ENGINE_TICK_MS` (= 1000ms)。
/// - pause は**再開側の press が属する tick** に帰属する (`super` のモジュール doc)。
/// - 同じ tick に終わる pause が 2 本あるとすると、再開時刻 `t1 < t2` は同一 tick なので
///   `t2 - t1 < 1000`。ところが `t2` で終わる pause の開始は `t1` 以降の press なので
///   `gap(t2) <= t2 - t1 < 1000 < 2000` となり、**`gap(t2) >= PAUSE_THRESHOLD_MS` に矛盾する**。
/// - → ★★★ **1 tick に pause は高々 1 本。要素数が 1 なので 3 分位はすべて同じ値になる。**
///
/// ★ 実測 (2026-09-15・`tests/fixtures/` の **14 本すべて**): `activity.pauses > 1` の tick は
/// **0 件**、`p50 != max` の行も **0 件**。
///
/// ⚠️★★★ **だから `p50` / `p90` を「分布の要約」として読んではならない。**
/// ★ 現状この 3 つは**同じ 1 本の pause 長**であり、`003.md` AC3 の不変式
/// `p50 <= p90 <= max` は**等号でしか成立せず、検出力を持たない**。
///
/// ★ 直し方は **集約窓を決める問題**であり、⚠️ **窓長は事前宣言 (pre-registration) 事項**なので
/// ここで勝手に決めない (★ ADR-030 D4 が `W` / `q` / `B` を P1 前の事前宣言としたのと同型)。
/// → ★ `.steering/20260914-mhd-feature-offline-tiers/blockers.md` **起票 7** で人にエスカレートしている。
#[derive(Debug, Clone, serde::Serialize)]
pub struct Dispersion {
    /// この tick に帰属する pause 長 (ms) の中央値相当 (nearest-rank 法)。要素 0 個なら `null`。
    /// ⚠️ 上の struct doc のとおり**現状は `pause_max_ms` と必ず同値**である。
    pub pause_p50_ms: Option<f64>,
    /// 同じく 90 パーセンタイル相当。⚠️ **現状は `pause_max_ms` と必ず同値**。
    pub pause_p90_ms: Option<f64>,
    /// 同じく最大値。★ 現状はこの tick に帰属する**唯一の pause の長さ**そのものである。
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
///
/// ⚠️★★★ **`Serialize` を持たないが、「出力に出ていない」とは読まないこと**
/// (2026-09-15・`security-checker` L1・実測で確認):
/// `surprise = (tick_mean - mean_ms) / std_ms` の `tick_mean` は**同じ行の
/// `activity.mean_iki_ms` として出ている**ので、**2 行あれば `mean_ms` / `std_ms` が連立で解ける**。
/// ★ 実測 (`instrument_rich.ndjson`): 復元値が生 NDJSON からの直接計算と**小数 10 桁まで一致**した。
///
/// ⚠️ **新しい露出ではない** —— ★ 提出される匿名化 NDJSON の `key` 行は
/// `(category, 相対 ms)` を**ミリ秒分解能のまま**持つ (`anonymize.rs` は `t` を相対化するだけで
/// 分解能を落とさない) ので、同じ値はそこからも厳密に再計算できる。
/// → ★ ただし **「baseline は出していない」を前提に判断すると誤る**ので、ここに記録しておく。
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
///
/// ⚠️ **線形補間の median とは一致しない** (2026-09-15・`code-reviewer` LOW)。
/// ★ 偶数個では**下側**を返す (`[10, 20]` → `10.0`。一般的な median は `15.0`)。
/// → ⚠️ 外部ツール・論文値と突き合わせるときは定義差を承知すること。
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
///
/// ⚠️ **標準偏差は母集団版 (÷ n) である** (2026-09-15・`code-reviewer` MEDIUM で明文化)。
/// ★ 標本版 (÷ (n-1)) ではない。⚠️ tick 内の n は 2〜3 が支配的なので**差は小さくない**。
/// ★ `SessionIkiBaseline::from_session_iki` も同じ ÷ n を使う (流儀を揃えてある)。
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
///
/// ⚠️★★★ **非有限値 (NaN / Inf) を出してはならない。**
/// ★ `serde_json` は NaN / Inf を**エラーにせず黙って `null` に書き換える**
/// (2026-09-15・`security-checker` L2・`serde_json` の `ser.rs` を実読して確認)。
/// → ⚠️ **`null` が「要素が 0 個だった」(AC4) と「計算が壊れた」の両方を意味してしまい、
/// 区別できなくなる。** ★ 現在は 0 除算を事前ガードしているので到達しないが
/// (`SessionIkiBaseline::from_session_iki` の `std_ms == 0.0` /
/// [`coefficient_of_variation`] の `m == 0.0`)、**将来の改修で壊れても無音である**。
/// → ★ 回帰は [`tests::emitted_values_are_always_finite`] が張る。
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

    /// ⚠️★★★ **2026-09-15 に検出力を足した** (`code-reviewer` HIGH-2)。
    ///
    /// ★ 旧版の入力は `[0, PAUSE_THRESHOLD_MS, PAUSE_THRESHOLD_MS+100]` ＝
    /// **pause 1 本・時刻重複なし**だったので `i-1` が常に 0 になり、
    /// ⚠️ **`gap` を `sorted[i] - sorted[0]` と書き間違えても、`next_expected` を進め忘れても
    /// 同じ結果を返した**（★ reviewer が mutation harness で 3 実装の出力一致を実測）。
    /// → ★ **pause 2 本以上 ＋ 同時刻重複**を入れて、対の突き合わせを実際に固定する。
    #[test]
    fn pause_durations_pairs_gap_with_resuming_ts() {
        use crate::analysis::features::PAUSE_THRESHOLD_MS;
        let press_ts = vec![0, PAUSE_THRESHOLD_MS, PAUSE_THRESHOLD_MS + 100];
        let durations = pause_durations(&press_ts);
        // 0 -> PAUSE_THRESHOLD_MS は閾値ちょうどで pause、続く +100 は pause でない。
        assert_eq!(durations.len(), 1);
        assert_eq!(durations[0].resuming_ts, PAUSE_THRESHOLD_MS);
        assert_eq!(durations[0].gap_ms, PAUSE_THRESHOLD_MS);

        // ★ pause 2 本。⚠️ 2 本目の gap は「直前の press との差」であり、
        //   **セッション先頭からの差ではない**（★ `sorted[i] - sorted[0]` と書くと 6000 になる）。
        let two = vec![0_u64, 3000, 6000];
        let d2 = pause_durations(&two);
        assert_eq!(d2.len(), 2);
        assert_eq!((d2[0].resuming_ts, d2[0].gap_ms), (3000, 3000));
        assert_eq!(
            (d2[1].resuming_ts, d2[1].gap_ms),
            (6000, 3000),
            "2 本目の gap は直前 press との差 (先頭との差ではない)"
        );

        // ★ 同時刻重複を挟む。⚠️ 重複で対がずれると gap が変わる。
        //   0 / 0 / 2500 / 2500 / 5000 → pause は 2500(gap 2500) と 5000(gap 2500)。
        let dup = vec![0_u64, 0, 2500, 2500, 5000];
        let d3 = pause_durations(&dup);
        assert_eq!(d3.len(), 2, "同時刻重複があっても pause は 2 本: {d3:?}");
        assert_eq!((d3[0].resuming_ts, d3[0].gap_ms), (2500, 2500));
        assert_eq!(
            (d3[1].resuming_ts, d3[1].gap_ms),
            (5000, 2500),
            "重複時刻を挟んでも直前 press との差になる"
        );

        // ★ 重複が「pause の開始側」に来る場合。
        //   0 / 2500 / 2500 / 2500 / 7000 → pause は 2500(gap 2500) と 7000(gap 4500)。
        let dup2 = vec![0_u64, 2500, 2500, 2500, 7000];
        let d4 = pause_durations(&dup2);
        assert_eq!(d4.len(), 2, "{d4:?}");
        assert_eq!((d4[0].resuming_ts, d4[0].gap_ms), (2500, 2500));
        assert_eq!((d4[1].resuming_ts, d4[1].gap_ms), (7000, 4500));
    }

    #[test]
    fn iki_cv_needs_at_least_two_points() {
        assert_eq!(coefficient_of_variation(&[]), None);
        assert_eq!(coefficient_of_variation(&[100]), None);
        // mean == 0 (同時刻打鍵のみ) は除算不能なので null。
        assert_eq!(coefficient_of_variation(&[0, 0]), None);
        // std と mean が等しくなる (gap 0 と 2*mean の2点) ため cv はちょうど 1.0。
        assert_eq!(coefficient_of_variation(&[0, 2000]), Some(1.0));
    }

    /// ⚠️★★★ **出力に非有限値 (NaN / Inf) が 1 つも出ないこと**
    /// (2026-09-15・`security-checker` L2)。
    ///
    /// ★ `serde_json` は NaN / Inf を**エラーにせず黙って `null` に書き換える**ので、
    /// ⚠️ 壊れた計算が **AC4 の「要素 0 個 = `null`」と見分けのつかない `null`** に化ける。
    /// → ★ 「壊れたら赤くなる」状態をここで作る (⚠️ 無音で通らせない)。
    #[test]
    fn emitted_values_are_always_finite() {
        use crate::analysis::features::PAUSE_THRESHOLD_MS;

        let check = |d: &Dispersion, label: &str| {
            for (name, v) in [
                ("pause_p50_ms", d.pause_p50_ms),
                ("pause_p90_ms", d.pause_p90_ms),
                ("pause_max_ms", d.pause_max_ms),
                ("iki_cv", d.iki_cv),
                ("surprise", d.surprise),
            ] {
                if let Some(x) = v {
                    assert!(
                        x.is_finite(),
                        "{label}: {name} が非有限 ({x}) —— serde_json は黙って null にする"
                    );
                }
            }
        };

        // ★ 分母が 0 になりうる入力を並べる (⚠️ 想像で並べていない: 0 除算の 2 経路に対応)。
        // (a) 全 IKI が同値 → baseline の分散 0
        let same = vec![100_u64, 100, 100];
        check(
            &compute_dispersion(
                &[],
                &same,
                SessionIkiBaseline::from_session_iki(&same).as_ref(),
            ),
            "全 IKI 同値",
        );
        // (b) 全 IKI が 0ms (同時刻打鍵のみ) → cv の分母 0
        let zeros = vec![0_u64, 0, 0];
        check(
            &compute_dispersion(
                &[],
                &zeros,
                SessionIkiBaseline::from_session_iki(&zeros).as_ref(),
            ),
            "全 IKI が 0ms",
        );
        // (c) 空 tick
        check(&compute_dispersion(&[], &[], None), "空 tick");
        // (d) 通常入力 + 極端に大きい pause
        let wide = vec![1_u64, u32::MAX as u64];
        check(
            &compute_dispersion(
                &[PAUSE_THRESHOLD_MS, u32::MAX as u64],
                &wide,
                SessionIkiBaseline::from_session_iki(&wide).as_ref(),
            ),
            "極端に広い分布",
        );

        // ★ 実際に serde_json を通して `null` が混ざらないことも見る (⚠️ 型だけでは足りない)。
        let d = compute_dispersion(
            &[PAUSE_THRESHOLD_MS],
            &[100, 300],
            SessionIkiBaseline::from_session_iki(&[100, 300]).as_ref(),
        );
        let json = serde_json::to_string(&d).expect("serialize");
        assert!(
            !json.contains("null"),
            "値が揃っている入力で null が出た (非有限値が null に化けた疑い): {json}"
        );
    }
}
