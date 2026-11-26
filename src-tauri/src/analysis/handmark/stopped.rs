//! 手跡の止まりの層（ADR-056）の純関数。今の手跡の状態（[`StageState`](super::state::StageState)）には
//! 触れず、別の層として重ねる（`.steering/20261121-handmark-stopped-state-prototype/` 判断 10）。
//!
//! - 見えの度合い `v` は、`Stage::idle_since`（`is_idle` が初めて真になった格子の刻み）からの短い立ち上がりだけで
//!   決まる。立ち上がりが終われば 1 のままで、止まりの長さを持たない（ADR-056 D1・D2）。
//! - 返してよいか（門）は、打鍵と記録の一時停止の時刻だけで決まる。起動・戻し（`Stage` の起点）と一時停止の
//!   明けの後に 1 回以上の打鍵があり、一時停止の外のときだけ開く（ADR-056 D7・判断 2・判断 8）。
//! - 自律の動き [`ambient`] は、日の種と絶対の時刻の 1 秒ごとの節の擬似乱数を、全幅 W の窓の重みで足した値。
//!   W より離れた 2 つの時刻は節を共有しないので、記憶は W で切れる。`grid_start` も周期の関数も使わない
//!   （ADR-056 D2）。使う演算は四則と `sqrt` だけ（IEEE 754 で正しく丸められ、Rust は勝手に FMA へ縮めない）で、
//!   和は節の番号の昇順に固定してあるので、どの機械でも同じビット列になる（`cos` などの数学関数は使わない）。
//! - 推定の出力・キーの種類・系の状態は入らない（入力の型に口が無い・ADR-047 D2・ADR-048 D2）。

use super::state::{splitmix64, Stage, LIVE_LAG_MS};

/// 節の間隔（絶対の時刻・ms）。
const NODE_MS: u64 = 1_000;
const RISE_MS_DEFAULT: u64 = 2_000;
const RISE_MS_MAX: u64 = 10_000;
const WINDOW_S_DEFAULT: u64 = 20;
const WINDOW_S_MIN: u64 = 5;
const WINDOW_S_MAX: u64 = 120;
const STRENGTH_DEFAULT: f64 = 0.5;
/// 節の値を引くときの、チャネルの混ぜ（日の種の値と重ならないようにする定数）。
const NODE_SALT: u64 = 0x5DEE_CE66_D1CE_4E5B;

/// 自律の動きの見た目の形（研究者が切り替える・判断 4）。
#[derive(Debug, Clone, Copy, PartialEq, Eq, serde::Serialize)]
#[serde(rename_all = "lowercase")]
pub enum StoppedForm {
    /// 草と粒の場の下を流れる淡い帯。
    Band,
    /// 粒がゆっくり自分で漂う。
    Motes,
    /// 風の向きが自分で揺らぐ。
    Wind,
}

impl StoppedForm {
    fn code(self) -> u64 {
        match self {
            StoppedForm::Band => 1,
            StoppedForm::Motes => 2,
            StoppedForm::Wind => 3,
        }
    }
}

/// 研究者用の設定（`GSE_DEBUG` が立っているときだけ読む）。無ければ止まりの層は切ったまま。
#[derive(Debug, Clone, Copy, PartialEq)]
pub struct StoppedCfg {
    pub form: StoppedForm,
    /// 見えてくる移り変わりの長さ（ms）。
    pub rise_ms: u64,
    /// 記憶の窓（平滑の窓の全幅・秒）。
    pub window_s: u64,
    /// 見えの上限（0〜1）。
    pub strength: f64,
}

/// 環境変数の値を読む（例: `form=band;rise_ms=2000;window_s=20;strength=0.5`）。
///
/// `debug` が偽、値が無い・空・`off` なら `Ok(None)`（切ったまま）。読めない値は `Err`（呼ぶ側が警告を出して
/// 切ったままにする）。足りない項目は既定の値で埋める。
pub fn parse_stopped_cfg(raw: Option<&str>, debug: bool) -> Result<Option<StoppedCfg>, String> {
    let Some(raw) = raw.map(str::trim).filter(|s| !s.is_empty()) else {
        return Ok(None);
    };
    if !debug || raw.eq_ignore_ascii_case("off") {
        return Ok(None);
    }
    let mut cfg = StoppedCfg {
        form: StoppedForm::Band,
        rise_ms: RISE_MS_DEFAULT,
        window_s: WINDOW_S_DEFAULT,
        strength: STRENGTH_DEFAULT,
    };
    for item in raw.split(';').map(str::trim).filter(|s| !s.is_empty()) {
        let (key, value) = item
            .split_once('=')
            .map(|(k, v)| (k.trim(), v.trim()))
            .ok_or_else(|| "項目に = が無い".to_string())?;
        match key {
            "form" => {
                cfg.form = match value {
                    "band" => StoppedForm::Band,
                    "motes" => StoppedForm::Motes,
                    "wind" => StoppedForm::Wind,
                    _ => return Err("form は band・motes・wind のどれか".to_string()),
                }
            }
            "rise_ms" => {
                cfg.rise_ms = value
                    .parse::<u64>()
                    .ok()
                    .filter(|v| *v <= RISE_MS_MAX)
                    .ok_or_else(|| format!("rise_ms は 0〜{RISE_MS_MAX}"))?
            }
            "window_s" => {
                cfg.window_s = value
                    .parse::<u64>()
                    .ok()
                    .filter(|v| (WINDOW_S_MIN..=WINDOW_S_MAX).contains(v))
                    .ok_or_else(|| format!("window_s は {WINDOW_S_MIN}〜{WINDOW_S_MAX}"))?
            }
            "strength" => {
                cfg.strength = value
                    .parse::<f64>()
                    .ok()
                    .filter(|v| (0.0..=1.0).contains(v))
                    .ok_or_else(|| "strength は 0〜1".to_string())?
            }
            _ => return Err("知らない項目がある".to_string()),
        }
    }
    Ok(Some(cfg))
}

/// 時刻 `t_ms` の窓（全幅 `window_ms`）に入る節の番号の範囲（両端を含む）。節の時刻と `t_ms` の差の絶対値が
/// `window_ms / 2` 未満の節だけを使う。
fn node_range(t_ms: u64, window_ms: u64) -> (u64, u64) {
    let half = window_ms / 2;
    // 節の時刻 > t - half かつ 節の時刻 < t + half
    let lo_t = u128::from(t_ms) + 1;
    let lo_t = lo_t.saturating_sub(u128::from(half));
    let lo = lo_t.div_ceil(u128::from(NODE_MS));
    let hi_t = (u128::from(t_ms) + u128::from(half)).saturating_sub(1);
    let hi = hi_t / u128::from(NODE_MS);
    (
        u64::try_from(lo).unwrap_or(u64::MAX),
        u64::try_from(hi).unwrap_or(u64::MAX),
    )
}

/// 節 `n` のチャネル `c` の値（[−1, 1)）。日の種と節の番号だけで決まる。
fn node_value(seed: u64, n: u64, c: u64) -> f64 {
    let h = splitmix64(seed ^ splitmix64(n.wrapping_mul(4).wrapping_add(c) ^ NODE_SALT));
    (h >> 11) as f64 / (1u64 << 53) as f64 * 2.0 - 1.0
}

/// 自律の動きの 3 チャネル（帯の変位・粒の漂い・風の向きの入力・それぞれおよそ [−1, 1]）。
///
/// 節の値（分散 1/3）を、全幅 `window_ms` の重み `(1 − (2d/W)²)²` で足し、重みの二乗の和の平方根で割る。これで
/// どの時刻でも分散が同じ（1/9・標準偏差 1/3）になり、W を変えても強さが変わらない。±1 を超えた分は切る。
pub fn ambient(seed: u64, t_ms: u64, window_ms: u64) -> [f64; 3] {
    let (lo, hi) = node_range(t_ms, window_ms);
    let w_full = window_ms as f64;
    let mut out = [0.0f64; 3];
    for (c, slot) in out.iter_mut().enumerate() {
        let (mut s, mut s2) = (0.0f64, 0.0f64);
        let mut n = lo;
        while n <= hi {
            let d = (i128::from(n) * i128::from(NODE_MS) - i128::from(t_ms)) as f64;
            let x = 2.0 * d / w_full;
            let w = (1.0 - x * x) * (1.0 - x * x);
            s += w * node_value(seed, n, c as u64);
            s2 += w * w;
            match n.checked_add(1) {
                Some(next) => n = next,
                None => break,
            }
        }
        *slot = if s2 > 0.0 {
            (s / (3.0 * s2).sqrt()).clamp(-1.0, 1.0)
        } else {
            0.0
        };
    }
    out
}

/// 窓へ渡す止まりの層の 1 コマ（`handmark-stopped`）。
#[derive(Debug, Clone, Copy, PartialEq, serde::Serialize)]
pub struct StoppedFrame {
    /// 見えの度合い（0〜1）。止まりの長さに依らない。
    pub v: f64,
    pub ambient: [f64; 3],
    pub form: StoppedForm,
    pub strength: f64,
}

impl StoppedFrame {
    /// 各 f64 のビット列まで比べるための写し。
    pub fn bits(&self) -> [u64; 6] {
        [
            self.v.to_bits(),
            self.ambient[0].to_bits(),
            self.ambient[1].to_bits(),
            self.ambient[2].to_bits(),
            self.strength.to_bits(),
            self.form.code(),
        ]
    }
}

/// 返してよいか（門）。打鍵と一時停止の時刻だけを持つ（列も履歴も持たない）。
///
/// 開くのは、一時停止の外で、起点 `t0` と最後の再開のどちらよりも後（同じ時刻を含む）に打鍵があるとき。
/// 時刻を比べるだけなので、打鍵と一時停止の適用の順に依らない（一時停止どうしは時刻の順に入れる）。
#[derive(Debug, Clone, Copy, PartialEq, Eq)]
pub struct StopGate {
    t0: u64,
    last_press: Option<u64>,
    last_resume: Option<u64>,
    paused: bool,
}

impl StopGate {
    /// `paused` は起点 `t0` の時点で記録が一時停止中か（`t0` までの一時停止の出来事をすべて入れた後の状態）。
    pub fn new(t0: u64, paused: bool) -> Self {
        Self {
            t0,
            last_press: None,
            last_resume: None,
            paused,
        }
    }

    pub fn on_press(&mut self, t: u64) {
        if t >= self.t0 {
            self.last_press = Some(self.last_press.map_or(t, |p| p.max(t)));
        }
    }

    /// 記録の一時停止の始まり（`true`）・終わり（`false`）。時刻の順に入れる。
    pub fn on_pause(&mut self, t: u64, paused: bool) {
        if !paused && self.paused {
            self.last_resume = Some(t);
        }
        self.paused = paused;
    }

    pub fn is_open(&self) -> bool {
        !self.paused
            && self
                .last_press
                .is_some_and(|p| self.last_resume.is_none_or(|r| p >= r))
    }
}

/// 止まりの層の 1 コマを作る。`grid_t` は `Stage` が最後に処理した格子の点。
pub fn stopped_view(
    idle_since: Option<u64>,
    grid_t: u64,
    gate_open: bool,
    seed: u64,
    cfg: &StoppedCfg,
) -> StoppedFrame {
    let v = match (gate_open, idle_since) {
        (true, Some(_)) if cfg.rise_ms == 0 => 1.0,
        (true, Some(start)) => (grid_t.saturating_sub(start) as f64 / cfg.rise_ms as f64).min(1.0),
        _ => 0.0,
    };
    StoppedFrame {
        v,
        ambient: ambient(seed, grid_t, cfg.window_s * 1_000),
        form: cfg.form,
        strength: cfg.strength,
    }
}

/// `t0` の時点で一時停止中か（`t0` 以下の時刻の出来事を時刻の順に入れた後の状態）。
pub fn paused_at(pauses: &[(u64, bool)], t0: u64) -> bool {
    pauses
        .iter()
        .take_while(|(t, _)| *t <= t0)
        .last()
        .is_some_and(|(_, p)| *p)
}

/// 打鍵の時刻の列（昇順）と一時停止の出来事（`(時刻, 一時停止か)`・時刻の昇順）から、時刻 `t` の止まりの層を
/// 出す。風の積分は [`replay`](super::state::replay) と同じ順で `Stage` に流す。
pub fn replay_stopped(
    presses: &[u64],
    pauses: &[(u64, bool)],
    seed: u64,
    t0: u64,
    t: u64,
    cfg: &StoppedCfg,
) -> StoppedFrame {
    let mut s = Stage::new(seed, t0);
    let mut gate = StopGate::new(t0, paused_at(pauses, t0));
    for &p in presses {
        if p > t {
            break;
        }
        if p < t0 {
            continue;
        }
        s.press(p);
        gate.on_press(p);
    }
    for &(pt, paused) in pauses {
        if pt > t {
            break;
        }
        // 起点と同じ時刻の出来事も入れる（`paused_at` が畳んだものと同じ値なので冪等・駆動役と同じ条件）
        if pt >= t0 {
            gate.on_pause(pt, paused);
        }
    }
    s.advance_to(t);
    stopped_view(s.idle_since(), s.grid_t(), gate.is_open(), seed, cfg)
}

/// ライブの規則（時刻 `now` には「`now − LIVE_LAG_MS` まで」）を、記録から再現する。
pub fn replay_stopped_live(
    presses: &[u64],
    pauses: &[(u64, bool)],
    seed: u64,
    t0: u64,
    now: u64,
    cfg: &StoppedCfg,
) -> StoppedFrame {
    replay_stopped(
        presses,
        pauses,
        seed,
        t0,
        now.saturating_sub(LIVE_LAG_MS),
        cfg,
    )
}

#[cfg(test)]
mod tests {
    use super::*;
    use crate::analysis::handmark::state::SplitMix64;

    fn cfg(rise_ms: u64, window_s: u64) -> StoppedCfg {
        StoppedCfg {
            form: StoppedForm::Band,
            rise_ms,
            window_s,
            strength: 0.5,
        }
    }

    /// 打鍵を 6 秒ほど続けた後、黙る。
    fn burst(t: u64) -> Vec<u64> {
        (0..40u64).map(|k| t + k * 150).collect()
    }

    #[test]
    fn the_config_is_off_unless_debug_and_set() {
        let raw = Some("form=motes;rise_ms=3000;window_s=30;strength=0.25");
        assert_eq!(parse_stopped_cfg(raw, false), Ok(None));
        assert_eq!(parse_stopped_cfg(None, true), Ok(None));
        assert_eq!(parse_stopped_cfg(Some("  "), true), Ok(None));
        assert_eq!(parse_stopped_cfg(Some("off"), true), Ok(None));
        assert_eq!(
            parse_stopped_cfg(raw, true),
            Ok(Some(StoppedCfg {
                form: StoppedForm::Motes,
                rise_ms: 3_000,
                window_s: 30,
                strength: 0.25,
            }))
        );
        assert_eq!(
            parse_stopped_cfg(Some("form=wind"), true),
            Ok(Some(StoppedCfg {
                form: StoppedForm::Wind,
                rise_ms: RISE_MS_DEFAULT,
                window_s: WINDOW_S_DEFAULT,
                strength: STRENGTH_DEFAULT,
            }))
        );
        for bad in [
            "form=leaf",
            "rise_ms=-1",
            "rise_ms=10001",
            "window_s=4",
            "window_s=121",
            "strength=1.5",
            "strength=NaN",
            "speed=2",
            "form",
        ] {
            assert!(parse_stopped_cfg(Some(bad), true).is_err(), "{bad}");
        }
    }

    #[test]
    fn ambient_does_not_depend_on_when_the_stage_started() {
        // 自律の動きは日の種と絶対の時刻だけで決まる（ADR-056 D2 の (iii)）。起点の違う 2 本の再生で比べる。
        let c = cfg(2_000, 20);
        let t = 1_700_000_000_000u64;
        let presses: Vec<u64> = burst(t - 600_000);
        for start_shift in [0u64, 1_000, 37_250, 3_600_000] {
            let a = replay_stopped(&presses, &[], 9, t - 600_000 - start_shift, t, &c);
            let b = replay_stopped(&presses, &[], 9, t - 600_000, t, &c);
            assert_eq!(a.ambient.map(f64::to_bits), b.ambient.map(f64::to_bits));
        }
    }

    #[test]
    fn times_further_apart_than_the_window_share_no_node() {
        for window_s in [5u64, 10, 20, 30, 120] {
            let w = window_s * 1_000;
            for t in [0u64, 999, 1_000, 1_700_000_000_123, u64::MAX - w] {
                let (lo, hi) = node_range(t, w);
                assert!(lo <= hi, "{t} {w}");
                // 窓の中の節はどれも |差| < W/2
                for n in [lo, hi] {
                    let d = (i128::from(n) * 1_000 - i128::from(t)).unsigned_abs();
                    assert!(d < u128::from(w / 2), "{t} {w} {n}");
                }
                // 範囲は最大（1 つ外側の節は窓の外）。狭すぎる範囲は分散の正規化で隠れるので、ここで縛る
                let outside = |n: u64| {
                    (i128::from(n) * 1_000 - i128::from(t)).unsigned_abs() >= u128::from(w / 2)
                };
                if lo > 0 {
                    assert!(outside(lo - 1), "{t} {w} lo");
                }
                if let Some(n) = hi.checked_add(1) {
                    assert!(outside(n), "{t} {w} hi");
                }
                // W ちょうど離れた時刻とは、節を共有しない
                if let Some(t2) = t.checked_add(w) {
                    let (lo2, _) = node_range(t2, w);
                    assert!(lo2 > hi, "{t} {w}");
                }
            }
        }
    }

    #[test]
    fn ambient_stays_in_range_and_depends_on_the_seed() {
        let mut r = SplitMix64::new(4);
        let mut differ = 0;
        for _ in 0..500 {
            let t = 1_600_000_000_000 + r.below(1_000_000_000);
            let a = ambient(1, t, 20_000);
            let b = ambient(2, t, 20_000);
            for x in a.iter().chain(b.iter()) {
                assert!((-1.0..=1.0).contains(x) && x.is_finite(), "{x}");
            }
            if a != b {
                differ += 1;
            }
        }
        assert_eq!(differ, 500);
        assert!(ambient(1, u64::MAX, 120_000).iter().all(|x| x.is_finite()));
        assert!(ambient(1, 0, 5_000).iter().all(|x| x.is_finite()));
    }

    #[test]
    fn ambient_has_the_same_spread_at_any_time_and_window() {
        // 標準偏差はおよそ 1/3 で、W にも節に対する位置にも依らない（分散を重みの二乗の和で揃えた）。
        for window_ms in [10_000u64, 30_000] {
            for offset in [0u64, 250, 500] {
                let (mut s, mut s2, n) = (0.0f64, 0.0f64, 4_000u64);
                for k in 0..n {
                    let x = ambient(7, 1_600_000_000_000 + k * 97_000 + offset, window_ms)[0];
                    s += x;
                    s2 += x * x;
                }
                let mean = s / n as f64;
                let sd = (s2 / n as f64 - mean * mean).sqrt();
                assert!((sd - 1.0 / 3.0).abs() < 0.03, "{window_ms} {offset} {sd}");
            }
        }
    }

    #[test]
    fn v_rises_then_stays_at_one_however_long_the_stop() {
        let c = cfg(2_000, 20);
        let t0 = 1_000_000u64;
        let presses = burst(t0 + 1_000);
        // 立ち上がりの途中は 0 より大きく 1 より小さい刻みがあり、止まりが始まる前は 0
        let mut seen_mid = false;
        let mut start = None;
        for k in 0..400u64 {
            let t = t0 + 1_000 + k * TICK;
            let f = replay_stopped(&presses, &[], 3, t0, t, &c);
            assert!((0.0..=1.0).contains(&f.v));
            if f.v > 0.0 && f.v < 1.0 {
                seen_mid = true;
            }
            if f.v > 0.0 && start.is_none() {
                start = Some(t);
            }
        }
        assert!(seen_mid);
        let start = start.expect("the stop starts within 100 s");
        // 立ち上がりの後は、1 分・1 時間・1 日・30 日で、v も含めて同じ（自律の動きは時刻で変わる）
        for later in [60_000u64, 3_600_000, 86_400_000, 30 * 86_400_000] {
            let f = replay_stopped(&presses, &[], 3, t0, start + later, &c);
            assert_eq!(f.v.to_bits(), 1.0f64.to_bits(), "{later}");
        }
    }

    const TICK: u64 = crate::analysis::handmark::state::TICK_MS;

    #[test]
    fn v_is_zero_until_the_first_press_after_start_or_resume() {
        let c = cfg(0, 20);
        let t0 = 5_000_000u64;
        let long = 3_600_000u64;
        // 起動の直後（戻した直後も `Stage` を作り直すので同じ）: 打鍵が無いまま長く止まっても 0
        assert_eq!(replay_stopped(&[], &[], 1, t0, t0 + long, &c).v, 0.0);
        // 打鍵の後に止まれば 1
        let presses = burst(t0 + 1_000);
        assert_eq!(replay_stopped(&presses, &[], 1, t0, t0 + long, &c).v, 1.0);
        // 一時停止の間は 0
        let p_at = t0 + 600_000;
        let pauses = [(p_at, true)];
        assert_eq!(
            replay_stopped(&presses, &pauses, 1, t0, t0 + long, &c).v,
            0.0
        );
        // 一時停止が明けた後も、最初の打鍵までは 0（判断 2）
        let r_at = t0 + 900_000;
        let pauses = [(p_at, true), (r_at, false)];
        assert_eq!(
            replay_stopped(&presses, &pauses, 1, t0, t0 + long, &c).v,
            0.0
        );
        // 明けた後に打鍵があれば、その後の止まりで 1
        let mut after = presses.clone();
        after.extend(burst(r_at + 1_000));
        assert_eq!(replay_stopped(&after, &pauses, 1, t0, t0 + long, &c).v, 1.0);
        // 起点の前の一時停止が明けていなければ、起点からずっと 0
        let before = [(t0 - 10, true)];
        assert_eq!(
            replay_stopped(&presses, &before, 1, t0, t0 + long, &c).v,
            0.0
        );
    }

    #[test]
    fn pointer_only_use_after_a_press_still_shows_the_stop() {
        // 打鍵だけで決めるので、打鍵の後にマウスだけを使う間（打鍵が無い）も v が上がる（判断 8）。
        let c = cfg(2_000, 20);
        let t0 = 2_000_000u64;
        let presses = burst(t0 + 1_000);
        assert_eq!(
            replay_stopped(&presses, &[], 4, t0, t0 + 600_000, &c).v,
            1.0
        );
    }

    #[test]
    fn the_gate_does_not_depend_on_the_order_of_presses_and_pauses() {
        let mut r = SplitMix64::new(12);
        let (mut open, mut shut) = (0, 0);
        for case in 0..300u64 {
            let t0 = 1_000_000 + r.below(1_000);
            // 起点で一時停止中から始まる件も混ぜる
            let start_paused = r.below(4) == 0;
            let mut gate_a = StopGate::new(t0, start_paused);
            let mut gate_b = StopGate::new(t0, start_paused);
            let mut gate_c = StopGate::new(t0, start_paused);
            let mut presses = Vec::new();
            let mut pauses = Vec::new();
            let mut t = t0;
            let mut paused = start_paused;
            for _ in 0..r.below(20) {
                t += r.below(50_000);
                if r.below(3) == 0 {
                    paused = !paused;
                    pauses.push((t, paused));
                } else if !paused {
                    presses.push(t);
                }
            }
            for &p in &presses {
                gate_a.on_press(p);
            }
            for &(pt, pp) in &pauses {
                gate_a.on_pause(pt, pp);
            }
            for &(pt, pp) in &pauses {
                gate_b.on_pause(pt, pp);
            }
            for &p in presses.iter().rev() {
                gate_b.on_press(p);
            }
            // 無作為に混ぜた順（一時停止どうしは時刻の順のまま）
            let (mut i, mut j) = (0, 0);
            while i < presses.len() || j < pauses.len() {
                if j >= pauses.len() || (i < presses.len() && r.below(2) == 0) {
                    gate_c.on_press(presses[i]);
                    i += 1;
                } else {
                    gate_c.on_pause(pauses[j].0, pauses[j].1);
                    j += 1;
                }
            }
            assert_eq!(gate_a.is_open(), gate_b.is_open(), "case {case}");
            assert_eq!(gate_a.is_open(), gate_c.is_open(), "case {case}");
            if gate_a.is_open() {
                open += 1;
            } else {
                shut += 1;
            }
        }
        // 陽性対照: 開いた件と閉じた件が両方ある（比べが常に偽どうしになっていない）
        assert!(open > 20 && shut > 20, "open {open} shut {shut}");
    }

    /// 起点と同じ時刻の一時停止の出来事は、起点で畳んだ状態と同じに扱う（駆動役と同じ `>= t0`）。
    #[test]
    fn a_pause_at_exactly_t0_keeps_the_gate_shut() {
        let c = cfg(0, 20);
        let t0 = 5_000_000u64;
        let presses = burst(t0 + 1_000);
        // 起点と同じ時刻に止め、打鍵（記録には残らない想定だが、門が閉じていることを見るために入れる）の後に開く
        let pauses = [(t0, true)];
        assert_eq!(
            replay_stopped(&presses, &pauses, 1, t0, t0 + 600_000, &c).v,
            0.0
        );
        let pauses = [(t0, true), (t0 + 1, false)];
        assert_eq!(
            replay_stopped(&presses, &pauses, 1, t0, t0 + 600_000, &c).v,
            1.0
        );
        let mut g = StopGate::new(t0, false);
        g.on_press(t0 + 5);
        g.on_pause(t0, true);
        assert!(!g.is_open());
    }

    #[test]
    fn replay_stopped_gives_bit_identical_frames_and_live_is_the_lagged_replay() {
        let c = cfg(3_000, 10);
        let t0 = 9_000_000u64;
        let presses = burst(t0 + 2_000);
        let pauses = [(t0 + 100_000, true), (t0 + 130_000, false)];
        for k in 0..200u64 {
            let now = t0 + k * 997;
            let a = replay_stopped_live(&presses, &pauses, 5, t0, now, &c);
            let b = replay_stopped(&presses, &pauses, 5, t0, now - LIVE_LAG_MS, &c);
            assert_eq!(a.bits(), b.bits());
        }
    }
}
