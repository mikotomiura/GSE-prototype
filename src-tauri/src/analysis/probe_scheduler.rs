//! ランダム時点プローブのスケジューリング (v0.3 §4 / D-8 / D-14, Task B)。
//!
//! 主データ `realtime_label` の妥当性は「プローブ時点がモデル出力と無関係な
//! **一様ランダム**であること」に依存する (v0.3 §4.1)。本モジュールはその時刻生成を
//! **純粋ロジック**として実装する: OS API / Tauri / 時刻取得 / グローバル RNG を一切
//! 呼ばず、`now_ms` / `idle_ms` を引数で受け、RNG は seed 注入する。
//! スレッド起動・emit・ログ送信・実時刻取得は呼び出し側 (`lib.rs`) の責務
//! (architecture-rules: 純粋スケジューリングは analysis/ に閉じ OS API を呼ばない)。
//!
//! # スケジューリング方式 (DB-1: 同次 Poisson + rolling thinning)
//!
//! 指数間隔 (逆変換 `-ln(1-u)/λ`) で次候補時刻を抽選し、候補到来時に制約判定する:
//! - **away**: `idle_ms ≥ away_idle_ms` (離席, v0.3 §4.3) は適格外 → 棄却 (thin)
//! - **gap**:  直近の発火から `gap_min_ms` 未満 → 棄却
//! - **cap**:  直近 `cap_window_ms` 内に `cap_count` 件発火済み → 棄却
//!
//! 棄却時は次候補を再抽選するだけで発火しない。全制約を満たした候補のみ発火する。
//! 同次 Poisson は「件数条件付きで時刻が一様」= 一様ランダムの教科書的生成法であり、
//! `probe_assignment.scheduled_ts` の実現分布から一様性を監査証明しやすい (D-14)。
//!
//! 自己マーカー (hotkey) はスケジュール対象外で、窓計算 ([`self_marker_window`]) のみ提供する。

use rand::rngs::StdRng;
use rand::{Rng, SeedableRng};

/// ランダムプローブの分析窓 (v0.3 §4.2): プローブ時刻 `t` の **直前** 30 秒。
/// 申告は未来の打鍵を汚染するが過去は汚染しないため、`t−31s 〜 t−1s` のみを採る。
pub fn random_probe_window(t_ms: u64) -> (u64, u64) {
    (t_ms.saturating_sub(31_000), t_ms.saturating_sub(1_000))
}

/// 自己マーカーの分析窓 (v0.3 §4.2): `t−35s 〜 t−5s`。
/// 予告的な打鍵変化 (押下直前の手の動き) を避けるため手前を取る。
pub fn self_marker_window(t_ms: u64) -> (u64, u64) {
    (t_ms.saturating_sub(35_000), t_ms.saturating_sub(5_000))
}

/// `self_marker_window` を `session_start` でクランプした版 (DB-8 を self_marker に適用)。
/// セッション開始直後 (`t−35s < session_start`) でも窓始端が `session_start` を下回らず、
/// 開始前/前セッションの打鍵が窓に混入しない。`session_start_ms==0` (セッション外) では
/// クランプしない (epoch 0 まで窓を広げないため)。
pub fn self_marker_window_clamped(t_ms: u64, session_start_ms: u64) -> (u64, u64) {
    let (ws, we) = self_marker_window(t_ms);
    let ws = if session_start_ms > 0 {
        ws.max(session_start_ms)
    } else {
        ws
    };
    (ws, we)
}

/// backend 生成の不透明プローブ ID (DB-3)。
///
/// 唯一のコンストラクタ [`ProbeId::generate`] は seeded RNG から `[A-Za-z0-9_-]`
/// (base64url アルファベット) 16 文字を生成する。外部 `String` を受け取る経路を
/// 持たないことで、本文・ウィンドウタイトル由来の文字列が ID に混入するのを
/// **型で排除**する (Task A security-checker 申し送り / data-privacy ルール1)。
#[derive(Debug, Clone, PartialEq, Eq)]
pub struct ProbeId(String);

impl ProbeId {
    /// base64url アルファベット (64 文字)。全文字が `[A-Za-z0-9_-]` に収まる。
    const ALPHABET: &'static [u8; 64] =
        b"ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789-_";
    const LEN: usize = 16;

    /// seeded RNG から不透明 ID を生成する。
    pub fn generate<R: Rng + ?Sized>(rng: &mut R) -> Self {
        let s: String = (0..Self::LEN)
            .map(|_| Self::ALPHABET[rng.gen_range(0..Self::ALPHABET.len())] as char)
            .collect();
        ProbeId(s)
    }

    pub fn as_str(&self) -> &str {
        &self.0
    }
}

/// スケジューラ制約 (v0.3 §4.3)。既定値は設計書の値。
#[derive(Debug, Clone, Copy)]
pub struct ProbeConfig {
    /// 単位時間あたり発火率 (1/ms)。λ≈2回/30分 = 1/900_000。
    pub lambda_per_ms: f64,
    /// 最小発火間隔 (ms)。既定 8 分。
    pub gap_min_ms: u64,
    /// cap 判定ウィンドウ (ms)。既定 30 分。
    pub cap_window_ms: u64,
    /// cap ウィンドウ内の最大発火数。既定 2。
    pub cap_count: usize,
    /// 離席とみなす idle しきい値 (ms)。既定 180_000 (intervention.rs AWAY_IDLE_MS と一致)。
    pub away_idle_ms: u64,
    /// ウォームアップ: セッション開始からこの時間が経つまでプローブを発火しない (ms)。
    /// 既定はランダムプローブ窓の全長 31_000ms。これにより分析窓 `[t−31s, t−1s]` の始端が
    /// 必ず `session_start` 以降になり、セッション開始前の打鍵データが窓に混入しない
    /// (測定窓の妥当性。DB-8)。
    pub min_session_elapsed_ms: u64,
}

impl Default for ProbeConfig {
    fn default() -> Self {
        Self {
            lambda_per_ms: 2.0 / (30.0 * 60.0 * 1000.0), // 2回/30分
            gap_min_ms: 8 * 60 * 1000,                   // 8 分
            cap_window_ms: 30 * 60 * 1000,               // 30 分
            cap_count: 2,
            away_idle_ms: 180_000,          // 3 分
            min_session_elapsed_ms: 31_000, // ランダムプローブ窓 (t−31s) の全長
        }
    }
}

/// 発火が確定したプローブ。呼び出し側が `probe_assignment` ログと
/// `probe_triggered` emit に変換する (DB-4)。
#[derive(Debug, Clone, PartialEq, Eq)]
pub struct FiredProbe {
    pub probe_id: ProbeId,
    /// 発火 (= 予定) 時刻。`probe_assignment.scheduled_ts`。
    pub scheduled_ts: u64,
    /// セッション開始からの経過 ms。`probe_assignment.session_elapsed_ms`。
    pub session_elapsed_ms: u64,
    /// 分析窓 (random_probe: t−31s)。`probe_triggered.analysis_window_start_ms`。
    pub window_start_ms: u64,
    /// 分析窓終端 (random_probe: t−1s)。`probe_triggered.analysis_window_end_ms`。
    pub window_end_ms: u64,
}

/// ランダムプローブのスケジューラ (DB-1)。
///
/// 駆動側は 1Hz 程度で [`ProbeScheduler::poll`] を呼ぶ。`poll` は純粋
/// (実時刻も idle も引数) で、発火確定時のみ [`FiredProbe`] を返す。
pub struct ProbeScheduler {
    rng: StdRng,
    config: ProbeConfig,
    session_start_ms: u64,
    /// 次候補時刻 (epoch ms)。`now_ms` がこれに達したら制約判定する。
    next_candidate_ms: u64,
    /// 直近発火時刻 (gap 判定用)。発火するまで `None`。
    last_fire_ms: Option<u64>,
    /// cap_window 内の発火時刻 (cap 判定用, 古いものは prune)。
    recent_fires: Vec<u64>,
}

impl ProbeScheduler {
    /// 本番用: RNG を注入して生成する (`StdRng::from_entropy()` 等)。
    pub fn new(mut rng: StdRng, config: ProbeConfig, session_start_ms: u64) -> Self {
        // 設定健全性チェック: lambda は有限正値、cap_count は 1 以上であること。
        // 不正値だと指数間隔が inf/NaN になったり永久に発火しなくなる (cross-review 指摘)。
        // 本番は ProbeConfig::default() 固定なので debug ビルドでの早期検出に留める。
        debug_assert!(
            config.lambda_per_ms.is_finite() && config.lambda_per_ms > 0.0,
            "lambda_per_ms must be finite and > 0, got {}",
            config.lambda_per_ms
        );
        debug_assert!(config.cap_count >= 1, "cap_count must be >= 1");
        let first = session_start_ms.saturating_add(Self::sample_interval_ms(&mut rng, &config));
        Self {
            rng,
            config,
            session_start_ms,
            next_candidate_ms: first,
            last_fire_ms: None,
            recent_fires: Vec::new(),
        }
    }

    /// seed 注入コンストラクタ。本番は entropy 由来の u64 seed を渡して再現可能にし
    /// (DB-6: 一様性監査)、テストは固定 seed で決定論にする。
    pub fn from_seed(seed: u64, config: ProbeConfig, session_start_ms: u64) -> Self {
        Self::new(StdRng::seed_from_u64(seed), config, session_start_ms)
    }

    /// 指数分布の逆変換サンプリング: `interval = -ln(1-u)/λ`。
    /// `u→1` で `1-u→0` となり `ln(0)=-inf` に発散するため、`1-u` を `f64::EPSILON` で
    /// 下限クランプして無限大を防ぐ (発散は `u→1` 側のみで起きる)。
    fn sample_interval_ms(rng: &mut StdRng, config: &ProbeConfig) -> u64 {
        let u: f64 = rng.gen::<f64>();
        let one_minus_u = (1.0 - u).max(f64::EPSILON);
        let interval = -one_minus_u.ln() / config.lambda_per_ms;
        // 最低 1ms (0 間隔の連続発火を避ける)。上限は設けない (Poisson 裾を歪めない)。
        interval.max(1.0) as u64
    }

    /// 1 ティック進める。発火確定時のみ `Some(FiredProbe)` を返す。
    ///
    /// - `now_ms`: 現在時刻 (epoch ms, 駆動側が実時刻を渡す)
    /// - `idle_ms`: 最終打鍵からの経過 ms (駆動側が `last_key_ms` から計算)
    pub fn poll(&mut self, now_ms: u64, idle_ms: u64) -> Option<FiredProbe> {
        if now_ms < self.next_candidate_ms {
            return None;
        }

        // cap_window から外れた古い発火を prune (prune 対象は ≥cap_window 古い
        // = gap_min より十分古いため gap 判定には影響しない)。
        let cap_window = self.config.cap_window_ms;
        self.recent_fires
            .retain(|&t| now_ms.saturating_sub(t) < cap_window);

        let away = idle_ms >= self.config.away_idle_ms;
        // ウォームアップ: 窓 [t−31s, t−1s] がセッション内に完全に収まる前は発火しない
        // (始端が session_start を下回り、開始前の打鍵が窓に混入するのを防ぐ。DB-8)。
        let too_early =
            now_ms.saturating_sub(self.session_start_ms) < self.config.min_session_elapsed_ms;
        let gap_ok = self
            .last_fire_ms
            .is_none_or(|last| now_ms.saturating_sub(last) >= self.config.gap_min_ms);
        let cap_ok = self.recent_fires.len() < self.config.cap_count;

        // 次候補は発火有無に関わらず再抽選する (thinning)。
        // now_ms は 1Hz 量子化された離散値のため候補が最大 1tick 遅延するが、
        // λ(2回/30分) スケールに対し無視可能。
        self.next_candidate_ms =
            now_ms.saturating_add(Self::sample_interval_ms(&mut self.rng, &self.config));

        if away || too_early || !gap_ok || !cap_ok {
            return None; // 棄却 (thin)
        }

        // 発火確定。
        self.last_fire_ms = Some(now_ms);
        self.recent_fires.push(now_ms);
        let probe_id = ProbeId::generate(&mut self.rng);
        let (window_start_ms, window_end_ms) = random_probe_window(now_ms);
        Some(FiredProbe {
            probe_id,
            scheduled_ts: now_ms,
            session_elapsed_ms: now_ms.saturating_sub(self.session_start_ms),
            window_start_ms,
            window_end_ms,
        })
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    const SESSION_START: u64 = 1_700_000_000_000;
    const MIN: u64 = 60_000;

    /// seeded で長時間シミュレートし発火時刻列を集める (idle 固定)。
    fn simulate(seed: u64, horizon_ms: u64, idle_ms: u64) -> Vec<FiredProbe> {
        let mut sched = ProbeScheduler::from_seed(seed, ProbeConfig::default(), SESSION_START);
        let mut fires = Vec::new();
        let mut now = SESSION_START;
        let end = SESSION_START + horizon_ms;
        while now <= end {
            if let Some(f) = sched.poll(now, idle_ms) {
                fires.push(f);
            }
            now += 1000; // 1Hz ティック
        }
        fires
    }

    #[test]
    fn gap_between_fires_is_at_least_8min() {
        // 複数 seed で 8 時間シミュレート。連続発火間隔は常に ≥8 分。
        for seed in 0..8u64 {
            let fires = simulate(seed, 8 * 60 * MIN, 0);
            for w in fires.windows(2) {
                let gap = w[1].scheduled_ts - w[0].scheduled_ts;
                assert!(
                    gap >= 8 * MIN,
                    "seed {seed}: gap {gap}ms < 8min between fires"
                );
            }
        }
    }

    #[test]
    fn cap_at_most_2_per_any_30min_window() {
        for seed in 0..8u64 {
            let fires = simulate(seed, 8 * 60 * MIN, 0);
            let ts: Vec<u64> = fires.iter().map(|f| f.scheduled_ts).collect();
            // 各発火を起点に [t, t+30min) 内の発火数を数える。
            for (i, &t0) in ts.iter().enumerate() {
                let count = ts[i..].iter().take_while(|&&t| t < t0 + 30 * MIN).count();
                assert!(
                    count <= 2,
                    "seed {seed}: {count} fires within a 30min window"
                );
            }
        }
    }

    #[test]
    fn fires_occur_when_active() {
        // テストが空振り (vacuous) でないことを保証: アクティブなら必ず発火する。
        let fires = simulate(1, 8 * 60 * MIN, 0);
        assert!(
            !fires.is_empty(),
            "expected at least one fire over 8h active"
        );
    }

    #[test]
    fn away_excludes_all_fires() {
        // idle≥180s が継続する間は全候補が棄却され発火ゼロ (v0.3 §4.3 離席除外)。
        let fires = simulate(1, 8 * 60 * MIN, 200_000);
        assert!(
            fires.is_empty(),
            "away (idle≥180s) must thin all probes, got {}",
            fires.len()
        );
    }

    #[test]
    fn deterministic_for_same_seed() {
        let a = simulate(42, 4 * 60 * MIN, 0);
        let b = simulate(42, 4 * 60 * MIN, 0);
        assert_eq!(a, b, "same seed must produce identical fire sequence");
    }

    #[test]
    fn probe_id_uses_only_url_safe_alphabet() {
        let mut rng = StdRng::seed_from_u64(7);
        for _ in 0..1000 {
            let id = ProbeId::generate(&mut rng);
            assert_eq!(id.as_str().len(), ProbeId::LEN);
            assert!(
                id.as_str()
                    .chars()
                    .all(|c| c.is_ascii_alphanumeric() || c == '-' || c == '_'),
                "probe_id `{}` contains a non [A-Za-z0-9_-] char",
                id.as_str()
            );
        }
    }

    #[test]
    fn probe_id_reproducible_for_same_seed() {
        let mut r1 = StdRng::seed_from_u64(99);
        let mut r2 = StdRng::seed_from_u64(99);
        assert_eq!(ProbeId::generate(&mut r1), ProbeId::generate(&mut r2));
    }

    #[test]
    fn random_probe_window_is_t_minus_31_to_1() {
        let (s, e) = random_probe_window(SESSION_START);
        assert_eq!(s, SESSION_START - 31_000);
        assert_eq!(e, SESSION_START - 1_000);
    }

    #[test]
    fn self_marker_window_is_t_minus_35_to_5() {
        let (s, e) = self_marker_window(SESSION_START);
        assert_eq!(s, SESSION_START - 35_000);
        assert_eq!(e, SESSION_START - 5_000);
    }

    #[test]
    fn self_marker_window_clamped_to_session_start() {
        // セッション開始直後 (t−35s < session_start): 窓始端は session_start にクランプ。
        let t = SESSION_START + 10_000; // 開始 10s 後
        assert_eq!(
            self_marker_window_clamped(t, SESSION_START),
            (SESSION_START, t - 5_000)
        );
        // 十分経過後 (t−35s ≥ session_start): クランプされず通常窓。
        let t2 = SESSION_START + 60_000;
        assert_eq!(
            self_marker_window_clamped(t2, SESSION_START),
            (t2 - 35_000, t2 - 5_000)
        );
        // セッション外 (session_start==0): クランプしない (epoch 0 まで広げない)。
        assert_eq!(
            self_marker_window_clamped(100_000, 0),
            self_marker_window(100_000)
        );
    }

    #[test]
    fn windows_saturate_near_zero() {
        // 時刻が窓長より小さくてもパニックしない (saturating)。
        // t=10: 両端とも窓長より小さく 0 に飽和。
        assert_eq!(random_probe_window(10), (0, 0));
        assert_eq!(self_marker_window(10), (0, 0));
        // t=10s: start (t−35s) は 0 に飽和するが end (t−5s=5s) は飽和しない。
        assert_eq!(self_marker_window(10_000), (0, 5_000));
        assert_eq!(random_probe_window(10_000), (0, 9_000));
    }

    #[test]
    fn session_elapsed_is_measured_from_start() {
        let mut sched = ProbeScheduler::from_seed(3, ProbeConfig::default(), SESSION_START);
        let mut now = SESSION_START;
        loop {
            if let Some(f) = sched.poll(now, 0) {
                assert_eq!(f.session_elapsed_ms, f.scheduled_ts - SESSION_START);
                break;
            }
            now += 1000;
            assert!(
                now < SESSION_START + 8 * 60 * MIN,
                "no fire to check elapsed"
            );
        }
    }

    #[test]
    fn no_probe_until_window_fits_in_session() {
        // DB-8 ウォームアップ: session_elapsed < 31s では発火せず、発火したプローブの
        // 分析窓始端は必ず session_start 以降 (開始前データの混入なし)。
        // gap/cap/away を無効化し候補を毎秒到来させて guard 単体を検証する。
        let config = ProbeConfig {
            lambda_per_ms: 1.0 / 1000.0, // 平均 1s 間隔 → 候補が頻繁に到来
            gap_min_ms: 0,
            cap_window_ms: 1,
            cap_count: usize::MAX,
            away_idle_ms: u64::MAX,
            min_session_elapsed_ms: 31_000,
        };
        let mut sched = ProbeScheduler::from_seed(5, config, SESSION_START);
        let mut now = SESSION_START;
        let mut fired_any = false;
        while now < SESSION_START + 5 * MIN {
            if let Some(f) = sched.poll(now, 0) {
                fired_any = true;
                assert!(
                    f.session_elapsed_ms >= 31_000,
                    "fired too early: session_elapsed_ms={}",
                    f.session_elapsed_ms
                );
                assert!(
                    f.window_start_ms >= SESSION_START,
                    "analysis window precedes session_start ({} < {})",
                    f.window_start_ms,
                    SESSION_START
                );
            }
            now += 1000;
        }
        assert!(fired_any, "expected fires after the warm-up period");
    }
}
