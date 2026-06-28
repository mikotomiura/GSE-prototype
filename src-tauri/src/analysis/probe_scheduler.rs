//! ランダム時点プローブのスケジューリング (v0.3 §4 / D-8 / D-14, Task B)。
//!
//! 主データ `realtime_label` の妥当性は「プローブ時点がモデル出力と無関係な
//! **一様ランダム**であること」に依存する (v0.3 §4.1)。本モジュールはその時刻生成を
//! **純粋ロジック**として実装する: OS API / Tauri / 時刻取得 / グローバル RNG を一切
//! 呼ばず、`now_ms` / `idle_ms` を引数で受け、RNG は seed 注入する。
//! スレッド起動・emit・ログ送信・実時刻取得は呼び出し側 (`lib.rs`) の責務
//! (architecture-rules: 純粋スケジューリングは analysis/ に閉じ OS API を呼ばない)。
//!
//! # スケジューリング方式 (DB-1: 同次 Poisson + rolling thinning + soft max-gap)
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
//! ## soft max-gap (DB-15): 枯渇 (early-cluster→drought) の是正
//!
//! 純・同次 Poisson は指数分布の長い裾により**初期にクラスタし以降数十分枯渇する**
//! (実機 v2 で観測: 序盤に 2 回続けて出た後ほぼ出ない)。候補間隔を `max_gap_ms` で
//! **上限クランプ** (censored exponential: 打ち切り点に確率質量が乗る。再正規化はしない)
//! することで、候補は必ず `max_gap_ms` 以内に到来し、セッション全体へ均一にカバレッジが
//! 広がる。これは ESM の **stratified random sampling** (各時間ブロックに 1 回ランダム) に
//! 相当する標準手法で、間隔上限を設ける代わりにブロック内タイミングのランダム性
//! (= 認知状態との独立性) を**概ね**保つ (完全独立ではない: 打ち切り点の確率質量が弱い
//! 周期性を生み、作業状態が時間帯と相関する場合に僅かな歪みが残る。decisions.md D3)。
//! 一様性 (条件付き一様) の厳密さは緩むが、これは
//! 「均等カバレッジ」とのトレードオフであり、X1 較正にとっては枯渇による偏りの方が有害
//! である (decisions.md D3 / research-positioning §4)。
//!
//! ※実効発火レートは名目 λ を上回る: max_gap クランプが間隔の floor を、cap_window 短縮
//! (30→20min) が cap 天井 (4/h→6/h) を引き上げる。名目 λ は逆変換の基準レートであって
//! 実現分布の平均ではない (decisions.md D2 のレート注記)。
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

/// プローブ駆動側が「最終打鍵時刻 (`last_key_ms`)」から idle を求める純ロジック (F4)。
///
/// `last_key_ms == 0` は **「idle 不明」** を表す: (a) セッション開始前で一度も打鍵がない、
/// または (b) 何らかの経路で最終打鍵時刻が失われた状態。このとき `away_idle_ms` を返し、
/// [`ProbeScheduler::poll`] 側で **away (離席) 扱い → プローブ抑止** に倒す。
///
/// 狙い (多層防御): macOS の CGEventTap が OS 都合で一時失効し `LAST_KEY_MS` が
/// 0 リセットされても (本来 `hook_macos.rs` 側で保持するが)、駆動側でも離席中の
/// プローブ誤発火を防ぐ保険となる。通常時 (`last_key_ms > 0`) は `now − last_key` を返す。
///
/// `away_idle_ms` ちょうどを返すことで away に倒せるのは、[`ProbeScheduler::poll`] の
/// away 判定が `idle_ms >= away_idle_ms` (境界を含む) だからである (両者は同じ閾値前提)。
///
/// 注意: Dashboard 表示用の `get_keyboard_idle_ms` (lib.rs) はこの保守化を適用せず
/// `last==0 → 0` を維持する (表示としては「未打鍵 = idle 0」が自然なため。設計判断)。
pub fn driver_idle_ms(now_ms: u64, last_key_ms: u64, away_idle_ms: u64) -> u64 {
    if last_key_ms == 0 {
        // idle 不明 → away 寄り (プローブを発火させない)。
        return away_idle_ms;
    }
    now_ms.saturating_sub(last_key_ms)
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
    // 窓終端も始端以上にクランプする。セッションが窓終端オフセット (t−5s) より若い
    // (`t − session_start < 5s`) と、終端 `t−5s` が `session_start` を下回り `we < ws` に
    // 反転する。この反転窓は `record_realtime_*` の検証 (`we >= ws`) で弾かれ、ラベルが
    // 静かに失われる (debug_force_probe を起動直後に叩く・起動 5s 以内に M/D 自己マーカーを
    // 押す等)。セッション内に収まらない窓は `[ws, ws]` (ゼロ幅) に畳む = 「有効な開始前
    // データなし」を正しく表す。実スケジューラは 31s ウォームアップがあり到達しない。
    let we = we.max(ws);
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

    /// 受領した不透明 ID が backend 生成形式 (`[A-Za-z0-9_-]`・長さ `LEN`) かを検証する (DC-3 / #7)。
    /// frontend から戻ってきた `probe_id` を realtime_label command で再検証するのに使う
    /// (本文/タイトル由来文字列の混入を境界で遮断・data-privacy)。
    pub fn is_valid(s: &str) -> bool {
        s.len() == Self::LEN && s.bytes().all(|b| Self::ALPHABET.contains(&b))
    }
}

/// スケジューラ制約 (v0.3 §4.3)。既定値は設計書の値。
#[derive(Debug, Clone, Copy)]
pub struct ProbeConfig {
    /// 逆変換サンプリングの基準レート (1/ms)。λ≈2回/30分 = 1/900_000。名目値であり、
    /// max_gap クランプと cap_window で実効発火レートは λ を上回る (モジュール doc 参照)。
    pub lambda_per_ms: f64,
    /// 最小発火間隔 (ms)。既定 6 分 (密集と窓重複の抑止)。
    pub gap_min_ms: u64,
    /// cap 判定ウィンドウ (ms)。既定 20 分。短いほど cap による dead-zone が短く、
    /// 「2 連発→以降長時間枯渇」の枯渇期間が縮む (旧 30 分→20 分)。
    pub cap_window_ms: u64,
    /// cap ウィンドウ内の最大発火数。既定 2 (バースト抑止)。
    pub cap_count: usize,
    /// soft max-gap (ms)。候補間隔をこの値で打ち切り、指数分布の長い裾が生む数十分の
    /// 枯渇を防ぐ (DB-15)。既定 22 分。`max_gap_ms >= gap_min_ms` を要する
    /// (下回ると候補が gap で連続棄却され意味をなさない)。u64::MAX で打ち切り無効
    /// (= 純・同次 Poisson、テスト用)。
    pub max_gap_ms: u64,
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
            lambda_per_ms: 2.0 / (30.0 * 60.0 * 1000.0), // 2回/30分 (基準レート・名目)
            gap_min_ms: 6 * 60 * 1000,                   // 6 分
            cap_window_ms: 20 * 60 * 1000,               // 20 分
            cap_count: 2,
            max_gap_ms: 22 * 60 * 1000, // 22 分 soft max-gap (枯渇防止 DB-15)
            away_idle_ms: 180_000,      // 3 分
            min_session_elapsed_ms: 31_000, // ランダムプローブ窓 (t−31s) の全長
        }
    }
}

impl ProbeConfig {
    /// 較正専用プロファイル (M0 凍結・decisions D1)。構造化された較正セッション
    /// (condition=blind_calibration) で**ラベル収量を優先**する。default (Phase2 配備・侵襲最小)
    /// とは分離し、注入で共存させる (本番は lib.rs が condition に応じて選択)。
    ///
    /// 根拠 (T0 サーベイ docs/literature/20260628-calibration-sampling-density.md):
    /// - ESM 標準は 6/日だが「総スケジュール回数は compliance とも dropout とも無相関・頻度↔期間は
    ///   トレードオフ (>10/日 と >14日 の同時は無)」[V25 Wrzus&Neubauer 2023][V26 Jones 2019]
    ///   ＝ 構造化セッション内の**高密度・短時間**は compliance を崩さず許容される。
    /// - measurement independence は維持: stratified random (soft max-gap) のままで、小休止合わせ
    ///   (opportune moment) は入れない (L0 較正の独立性 [V18]-[V23])。
    ///
    /// 収量逆算 (概算): 90 分セッションで提示 ~10-14 件 → compliance ~80% で有効 ~8-11/セッション →
    /// **2-3 セッション/人で有効 ≈ 20 件 (GATE2)**。GSE ドメインの実 compliance は未測定のため
    /// 概算であり、M0 凍結ビルドの P007 confirmatory 再走で実測して較正する。
    pub fn calibration() -> Self {
        Self {
            // ~1回/6分 (default 1/15分の ~2.5×・収量優先)。
            lambda_per_ms: 1.0 / (6.0 * 60.0 * 1000.0),
            gap_min_ms: 3 * 60 * 1000, // 3 分 (31s 分析窓の非重複を保ちつつ密度確保)
            cap_window_ms: 20 * 60 * 1000, // 20 分 (rolling 測定窓は維持)
            // 較正は収量優先で cap を実質無効化 (λ=1/6分・20分の期待発火≈3.3 に対し 4 はほぼ非拘束。
            // バースト上限としてのみ残し、通常は λ と gap_min が律速)。
            cap_count: 4,
            max_gap_ms: 10 * 60 * 1000, // 10 分 (短セッションの drought 防止・soft censoring 維持)
            away_idle_ms: 180_000,      // 3 分 (離席除外は default と不変)
            min_session_elapsed_ms: 31_000, // 31s warm-up (窓が session_start を割らない・DB-8)
        }
    }
}

/// 新セッション検出時のプローブスケジューラ初期化判定 (純ロジック・M0 D1)。
///
/// lib.rs のスケジューラスレッドが Atomic から読んだ値を渡す。session_meta の condition は
/// **どの session_start のものか** (`meta_for_session_start_ms`) を session_start と照合してから
/// 採用する。これにより「前セッションの古い meta が新セッションに適用される」事故 (世代未照合の
/// 取り違え) を防ぐ (cross-review HIGH)。meta 未受領のまま grace を超えたらサイレント全滅を避けて
/// default で起動する (fallback)。
#[derive(Debug, Clone, Copy, PartialEq, Eq)]
pub enum ProbeInitDecision {
    /// まだ初期化しない (この session_start 向けの session_meta 受領待ち・grace 内)。
    Wait,
    /// 初期化する。`calibration`=較正プロファイルを使う / `meta_fallback`=meta 未受領で grace 切れの
    /// default 化 (呼び出し側は warn する)。
    Start {
        calibration: bool,
        meta_fallback: bool,
    },
}

/// 初期化判定。`meta_for_session_start_ms == session_start_ms` のときだけ `meta_is_calibration` を
/// 採用する (世代照合)。未照合かつ grace 超過なら default で起動、grace 内なら待つ。
pub fn decide_probe_init(
    session_start_ms: u64,
    meta_for_session_start_ms: u64,
    meta_is_calibration: bool,
    waited_ms: u64,
    grace_ms: u64,
) -> ProbeInitDecision {
    if meta_for_session_start_ms == session_start_ms {
        // この世代の session_meta を受領済み。その condition で初期化する。
        ProbeInitDecision::Start {
            calibration: meta_is_calibration,
            meta_fallback: false,
        }
    } else if waited_ms >= grace_ms {
        // meta 未受領のまま grace 超過。プローブ全滅を避け default で起動 (calibration は選ばない)。
        ProbeInitDecision::Start {
            calibration: false,
            meta_fallback: true,
        }
    } else {
        ProbeInitDecision::Wait
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
        // soft max-gap は gap_min を下回ってはならない (下回ると打ち切られた候補が
        // 常に gap で棄却され発火が止まる)。DB-15。
        debug_assert!(
            config.max_gap_ms >= config.gap_min_ms,
            "max_gap_ms ({}) must be >= gap_min_ms ({})",
            config.max_gap_ms,
            config.gap_min_ms
        );
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
    ///
    /// soft max-gap (DB-15): 間隔を `max_gap_ms` で上限クランプ (censored exponential:
    /// 打ち切り点に確率質量。再正規化なし)。候補は必ず `max_gap_ms` 以内に到来し、指数裾
    /// による数十分の枯渇を防ぐ。「均等カバレッジ」と「条件付き一様性」のトレードオフ (D3)。
    fn sample_interval_ms(rng: &mut StdRng, config: &ProbeConfig) -> u64 {
        let u: f64 = rng.gen::<f64>();
        let one_minus_u = (1.0 - u).max(f64::EPSILON);
        let interval = -one_minus_u.ln() / config.lambda_per_ms;
        // 上限 max_gap_ms で打ち切り、最低 1ms (0 間隔の連続発火を避ける)。
        interval.min(config.max_gap_ms as f64).max(1.0) as u64
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

    /// seeded で長時間シミュレートし発火時刻列を集める (default config, idle 固定)。
    fn simulate(seed: u64, horizon_ms: u64, idle_ms: u64) -> Vec<FiredProbe> {
        simulate_cfg(seed, horizon_ms, idle_ms, ProbeConfig::default())
    }

    /// config 指定版シミュレータ。
    fn simulate_cfg(
        seed: u64,
        horizon_ms: u64,
        idle_ms: u64,
        config: ProbeConfig,
    ) -> Vec<FiredProbe> {
        let mut sched = ProbeScheduler::from_seed(seed, config, SESSION_START);
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

    /// 発火列とセッション端から「連続する空白 (start→first / fire→fire / last→end)」の
    /// 最大値を求める。枯渇 (drought) の指標。
    fn max_coverage_gap_ms(fires: &[FiredProbe], horizon_ms: u64) -> u64 {
        let mut pts = vec![SESSION_START];
        pts.extend(fires.iter().map(|f| f.scheduled_ts));
        pts.push(SESSION_START + horizon_ms);
        pts.windows(2).map(|w| w[1] - w[0]).max().unwrap_or(0)
    }

    #[test]
    fn gap_between_fires_is_at_least_gap_min() {
        // 複数 seed で 8 時間シミュレート。連続発火間隔は常に ≥gap_min (既定 6 分)。
        let gap_min = ProbeConfig::default().gap_min_ms;
        for seed in 0..8u64 {
            let fires = simulate(seed, 8 * 60 * MIN, 0);
            for w in fires.windows(2) {
                let gap = w[1].scheduled_ts - w[0].scheduled_ts;
                assert!(
                    gap >= gap_min,
                    "seed {seed}: gap {gap}ms < gap_min {gap_min}ms between fires"
                );
            }
        }
    }

    #[test]
    fn cap_at_most_cap_count_per_cap_window() {
        // 任意の cap_window (既定 20 分) ローリング窓内の発火数は cap_count (既定 2) 以下。
        let cfg = ProbeConfig::default();
        for seed in 0..8u64 {
            let fires = simulate(seed, 8 * 60 * MIN, 0);
            let ts: Vec<u64> = fires.iter().map(|f| f.scheduled_ts).collect();
            for (i, &t0) in ts.iter().enumerate() {
                let count = ts[i..]
                    .iter()
                    .take_while(|&&t| t < t0 + cfg.cap_window_ms)
                    .count();
                assert!(
                    count <= cfg.cap_count,
                    "seed {seed}: {count} fires within a cap_window ({}min)",
                    cfg.cap_window_ms / MIN
                );
            }
        }
    }

    #[test]
    fn soft_max_gap_truncates_candidate_intervals() {
        // DB-15: 候補間隔は常に max_gap_ms 以下 (truncated exponential)。
        let cfg = ProbeConfig::default();
        let mut rng = StdRng::seed_from_u64(1234);
        for _ in 0..100_000 {
            let iv = ProbeScheduler::sample_interval_ms(&mut rng, &cfg);
            assert!(
                iv <= cfg.max_gap_ms,
                "candidate interval {iv}ms exceeds max_gap_ms {}ms",
                cfg.max_gap_ms
            );
        }
    }

    #[test]
    fn pure_poisson_droughts_but_default_config_does_not() {
        // 回帰 (バグ再現 + 是正): 同じ seed で旧パラメータ (純・同次 Poisson:
        // gap8/cap2-per-30min/打ち切り無効) は「初期クラスタ→以降数十分枯渇」を生み、
        // 既定 config (soft max-gap 22min + cap 20min) はカバレッジ空白を有界化する。
        let horizon = 120 * MIN;
        let old = ProbeConfig {
            lambda_per_ms: 2.0 / (30.0 * 60.0 * 1000.0),
            gap_min_ms: 8 * MIN,
            cap_window_ms: 30 * MIN,
            cap_count: 2,
            max_gap_ms: u64::MAX, // 打ち切り無効 = 純・同次 Poisson (旧挙動)
            away_idle_ms: 180_000,
            min_session_elapsed_ms: 31_000,
        };
        // 是正後は全 seed で空白が default cap_window+max_gap+小余裕 (≤45min) に収まる。
        // bound は検証対象 = default config の cap_window(20min) を使う (old の 30min ではない)。
        let bound = ProbeConfig::default().cap_window_ms + 22 * MIN + 3 * MIN; // 20+22+3 = 45min
        let mut old_max_drought = 0u64;
        for seed in 0..64u64 {
            let new_fires = simulate(seed, horizon, 0);
            let new_gap = max_coverage_gap_ms(&new_fires, horizon);
            assert!(
                new_gap <= bound,
                "seed {seed}: default config coverage gap {new_gap}ms exceeds {bound}ms"
            );
            let old_fires = simulate_cfg(seed, horizon, 0, old);
            old_max_drought = old_max_drought.max(max_coverage_gap_ms(&old_fires, horizon));
        }
        // バグ再現: 旧パラメータは (この seed 集合で) 是正後の上限を超える枯渇を生む。
        assert!(
            old_max_drought > bound,
            "expected pure-Poisson to produce a drought > {bound}ms, max was {old_max_drought}ms"
        );
    }

    #[test]
    fn fires_spread_across_whole_session_not_just_early() {
        // 一様性監査: 90 分セッションで発火がセッション後半にも十分散らばる
        // (初期クラスタ→枯渇でない)。全 seed 合算で後半 (45-90min) の発火が
        // 全体の 35% 以上を占める。
        let horizon = 90 * MIN;
        let mut first_half = 0usize;
        let mut second_half = 0usize;
        for seed in 0..200u64 {
            for f in simulate(seed, horizon, 0) {
                if f.session_elapsed_ms <= 45 * MIN {
                    first_half += 1;
                } else {
                    second_half += 1;
                }
            }
        }
        let total = first_half + second_half;
        assert!(total > 0, "no fires collected");
        let second_frac = second_half as f64 / total as f64;
        assert!(
            second_frac >= 0.35,
            "second-half fires only {:.1}% of total ({second_half}/{total}); probes clustered early",
            second_frac * 100.0
        );
    }

    #[test]
    fn default_config_never_empty_over_typical_session() {
        // 枯渇是正: アクティブな 60 分セッションで全 seed が ≥1 発火 (純 Poisson は
        // 低レートゆえ稀に 0 発火だった)。
        for seed in 0..256u64 {
            let fires = simulate(seed, 60 * MIN, 0);
            assert!(
                !fires.is_empty(),
                "seed {seed}: no probe fired over a 60min active session"
            );
        }
    }

    #[test]
    fn calibration_profile_outyields_default_for_label_collection() {
        // D1: 較正プロファイルは収量優先。同一 horizon/seed で default より多く発火する。
        let horizon = 90 * MIN;
        let mut cal_total = 0usize;
        let mut def_total = 0usize;
        for seed in 0..64u64 {
            cal_total += simulate_cfg(seed, horizon, 0, ProbeConfig::calibration()).len();
            def_total += simulate(seed, horizon, 0).len();
        }
        assert!(
            cal_total > def_total,
            "calibration ({cal_total}) should outyield default ({def_total}) over 90min×64seed"
        );
    }

    #[test]
    fn calibration_yield_supports_gate2_in_a_few_sessions() {
        // D1 収量逆算: 較正セッション (90 分) の発火 (=提示) 数は、2-3 セッションで提示 ~25
        // (compliance ~80% → 有効 ~20 = GATE2) に届くレートであること。全 seed で最低限の収量
        // を保ち (空/極端低収量なし)、平均レートで 3 セッション ≥25 提示を満たす。
        // 注: compliance 0.8 や「有効=提示×0.8」は GSE 未測定の概算 (decisions D1)。
        let horizon = 90 * MIN;
        let cfg = ProbeConfig::calibration();
        let per_session: Vec<usize> = (0..64u64)
            .map(|seed| simulate_cfg(seed, horizon, 0, cfg).len())
            .collect();
        let min_per = *per_session.iter().min().unwrap();
        let mean = per_session.iter().sum::<usize>() as f64 / per_session.len() as f64;
        // 実測 (seed 0..64, 90min): min=10 max=15 mean≈12.0。下限は collapse 検出用に
        // 余裕を持たせて ≥8、平均は 2 セッションで提示 ~24 (有効 ~19) に届くレートを保証。
        assert!(
            min_per >= 8,
            "every calibration session should yield ≥8 probes; min was {min_per}"
        );
        assert!(
            mean * 2.0 >= 20.0,
            "mean per-session yield {mean:.1} ×2 sessions should reach ≥20 presented; got {:.1}",
            mean * 2.0
        );
    }

    #[test]
    fn calibration_gap_min_respected() {
        // 較正でも隣接発火は gap_min (3 分) 以上 = 31s 分析窓の非重複を保証。
        let gap_min = ProbeConfig::calibration().gap_min_ms;
        for seed in 0..16u64 {
            let fires = simulate_cfg(seed, 90 * MIN, 0, ProbeConfig::calibration());
            for w in fires.windows(2) {
                let gap = w[1].scheduled_ts - w[0].scheduled_ts;
                assert!(
                    gap >= gap_min,
                    "seed {seed}: calibration gap {gap}ms < gap_min {gap_min}ms"
                );
            }
        }
    }

    #[test]
    fn calibration_no_drought_in_session() {
        // 短い較正セッションで枯渇しない (P007 の 21 分 drought 再発防止)。
        // カバレッジ空白は cap_window(20) + max_gap(10) + 小余裕(3) = 33 分以内。
        let horizon = 90 * MIN;
        let cfg = ProbeConfig::calibration();
        let bound = cfg.cap_window_ms + cfg.max_gap_ms + 3 * MIN;
        for seed in 0..64u64 {
            let fires = simulate_cfg(seed, horizon, 0, cfg);
            let gap = max_coverage_gap_ms(&fires, horizon);
            assert!(
                gap <= bound,
                "seed {seed}: calibration coverage gap {gap}ms exceeds {bound}ms"
            );
        }
    }

    #[test]
    fn calibration_deterministic_for_same_seed() {
        // seed 決定性 (一様性監査 D-14) は較正プロファイルでも維持。
        let a = simulate_cfg(42, 90 * MIN, 0, ProbeConfig::calibration());
        let b = simulate_cfg(42, 90 * MIN, 0, ProbeConfig::calibration());
        assert_eq!(
            a, b,
            "calibration profile must be deterministic for same seed"
        );
    }

    const GRACE: u64 = 5_000;

    #[test]
    fn decide_probe_init_waits_until_meta_for_this_session() {
        // この session_start 向けの meta が未受領 (meta_for=0) かつ grace 内 → Wait。
        assert_eq!(
            decide_probe_init(1000, 0, false, 1000, GRACE),
            ProbeInitDecision::Wait
        );
    }

    #[test]
    fn decide_probe_init_uses_calibration_when_meta_matches() {
        // meta_for == session_start かつ calibration=true → 較正で起動 (fallback でない)。
        assert_eq!(
            decide_probe_init(1000, 1000, true, 0, GRACE),
            ProbeInitDecision::Start {
                calibration: true,
                meta_fallback: false
            }
        );
        // baseline (calibration=false) → default で起動 (fallback でない)。
        assert_eq!(
            decide_probe_init(1000, 1000, false, 0, GRACE),
            ProbeInitDecision::Start {
                calibration: false,
                meta_fallback: false
            }
        );
    }

    #[test]
    fn decide_probe_init_falls_back_to_default_after_grace() {
        // meta 未受領のまま grace 到達 → default で起動 (fallback フラグ立つ・calibration は選ばない)。
        assert_eq!(
            decide_probe_init(1000, 0, true, GRACE, GRACE),
            ProbeInitDecision::Start {
                calibration: false,
                meta_fallback: true
            }
        );
    }

    #[test]
    fn decide_probe_init_ignores_stale_meta_from_other_session() {
        // 別セッション (古い meta_for=900) は照合不一致 → この session_start(1000) に適用しない。
        // grace 内なら Wait、grace 超過なら fallback (古い calibration=true を引き継がない)。
        assert_eq!(
            decide_probe_init(1000, 900, true, 1000, GRACE),
            ProbeInitDecision::Wait
        );
        assert_eq!(
            decide_probe_init(1000, 900, true, GRACE, GRACE),
            ProbeInitDecision::Start {
                calibration: false,
                meta_fallback: true
            }
        );
    }

    #[test]
    fn decide_probe_init_prefers_meta_over_grace_at_boundary() {
        // grace 到達と同時に meta も一致しているなら、fallback でなく meta の condition を優先。
        assert_eq!(
            decide_probe_init(1000, 1000, true, GRACE, GRACE),
            ProbeInitDecision::Start {
                calibration: true,
                meta_fallback: false
            }
        );
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
    fn driver_idle_treats_zero_last_key_as_away() {
        // F4: last_key==0 (未打鍵 or 失効で不明) は away_idle_ms を返し、
        // poll 側で away (idle≥away_idle_ms) と判定されてプローブが抑止される。
        let away = ProbeConfig::default().away_idle_ms;
        assert_eq!(driver_idle_ms(SESSION_START + 10_000, 0, away), away);
        assert!(driver_idle_ms(SESSION_START + 10_000, 0, away) >= away);
    }

    #[test]
    fn driver_idle_normal_growth() {
        // 通常時 (last_key>0) は now−last_key がそのまま idle になる。
        let away = ProbeConfig::default().away_idle_ms;
        let last = SESSION_START;
        assert_eq!(driver_idle_ms(SESSION_START + 5_000, last, away), 5_000);
        assert_eq!(driver_idle_ms(SESSION_START + 200_000, last, away), 200_000);
        // now < last_key (時計巻き戻し等) でも saturating で 0、パニックしない。
        assert_eq!(
            driver_idle_ms(SESSION_START, SESSION_START + 1_000, away),
            0
        );
    }

    #[test]
    fn away_series_with_transient_zero_last_key_never_fires() {
        // F4 回帰: 離席中 (idle≥away) に OS フック失効で last_key が周期的に 0 へ
        // リセットされても、driver_idle_ms が 0 を away に倒すためプローブは発火しない。
        // 旧ロジック (last_key==0 → idle=0) なら 0 リセット時に「在席」と誤判定し発火する。
        // 候補を毎秒到来させ gap/cap を無効化し、away ゲート単体を厳しく検証する。
        let config = ProbeConfig {
            lambda_per_ms: 1.0 / 1000.0, // 平均 1s 間隔 → 候補が頻繁に到来
            gap_min_ms: 0,
            cap_window_ms: 1,
            cap_count: usize::MAX,
            max_gap_ms: u64::MAX,
            away_idle_ms: 180_000,
            min_session_elapsed_ms: 0,
        };
        let mut sched = ProbeScheduler::from_seed(7, config, SESSION_START);
        // ずっと離席を表す古い last_key (session_start より away+60s 前)。
        let away_last_key = SESSION_START.saturating_sub(config.away_idle_ms + 60_000);
        let mut now = SESSION_START;
        let end = SESSION_START + 30 * MIN;
        let mut tick = 0u64;
        let mut fired = 0usize;
        while now <= end {
            // 100 tick ごとに last_key を 0 にリセット (tap 再インストールを模擬)。
            let last_key = if tick % 100 == 0 { 0 } else { away_last_key };
            let idle = driver_idle_ms(now, last_key, config.away_idle_ms);
            if sched.poll(now, idle).is_some() {
                fired += 1;
            }
            now += 1000;
            tick += 1;
        }
        assert_eq!(
            fired, 0,
            "away 中は last_key の一時的 0 リセットがあってもプローブは発火してはならない"
        );
    }

    #[test]
    fn poll_thins_at_exactly_away_threshold() {
        // driver_idle_ms が away_idle_ms ちょうどを返す前提 (poll の `>=` 境界) を固定する。
        // idle == away_idle_ms で発火しないことを保証 (この等値が崩れると保守化が無効になる)。
        let config = ProbeConfig {
            lambda_per_ms: 1.0 / 1000.0,
            gap_min_ms: 0,
            cap_window_ms: 1,
            cap_count: usize::MAX,
            max_gap_ms: u64::MAX,
            away_idle_ms: 180_000,
            min_session_elapsed_ms: 0,
        };
        let mut sched = ProbeScheduler::from_seed(11, config, SESSION_START);
        let mut now = SESSION_START;
        for _ in 0..600 {
            assert!(
                sched.poll(now, config.away_idle_ms).is_none(),
                "idle == away_idle_ms は away 扱いで発火してはならない"
            );
            now += 1000;
        }
    }

    #[test]
    fn present_then_transient_zero_does_not_fire() {
        // 保守設計の明文化: 在席中 (idle < away) に last_key が一時的に 0 化しても、
        // driver_idle_ms は 0 を away に倒すためその tick では発火しない。
        // (在席なのに 1 プローブ抑止される側の誤りは「離席中発火」より研究的に無害。decisions.md D2)
        let away = ProbeConfig::default().away_idle_ms;
        // 在席相当 (5 秒前に打鍵)。
        let present_last_key = SESSION_START + 100_000 - 5_000;
        let now = SESSION_START + 100_000;
        assert!(driver_idle_ms(now, present_last_key, away) < away); // 通常は在席
        assert_eq!(driver_idle_ms(now, 0, away), away); // 0 化した瞬間は away 側
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
    fn probe_id_is_valid_accepts_generated_rejects_malformed() {
        // 生成した ID は常に valid。
        let mut rng = StdRng::seed_from_u64(123);
        for _ in 0..100 {
            assert!(ProbeId::is_valid(ProbeId::generate(&mut rng).as_str()));
        }
        // 長さ違い・不正文字・空・本文混入は reject (DC-3 / #7)。
        assert!(ProbeId::is_valid("ABCDEFGHIJKLMNOP")); // 16 文字・全て alphabet
        assert!(!ProbeId::is_valid("")); // 空
        assert!(!ProbeId::is_valid("short")); // 長さ不足
        assert!(!ProbeId::is_valid("ABCDEFGHIJKLMNOPQ")); // 17 文字
        assert!(!ProbeId::is_valid("ABCDEFGHIJKLMNO.")); // '.' は alphabet 外
        assert!(!ProbeId::is_valid("ABCDEFGHIJKLMN あ")); // マルチバイト混入
        assert!(!ProbeId::is_valid("'; DROP TABLE--xx")); // 本文/インジェクション様
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
    fn self_marker_window_clamped_never_inverts_within_5s_of_start() {
        // 回帰: 起動 5s 以内のマーカー/プローブで終端 `t−5s` が session_start を下回り
        // `we < ws` に反転 → record_realtime_* の `we >= ws` 検証でラベルが失われていた。
        // 終端を始端以上にクランプし、ゼロ幅以上を保証する。
        for elapsed in [0u64, 1, 1_000, 4_334, 4_999] {
            let t = SESSION_START + elapsed;
            let (ws, we) = self_marker_window_clamped(t, SESSION_START);
            assert_eq!(
                ws, SESSION_START,
                "始端は session_start にクランプ (elapsed={elapsed})"
            );
            assert!(
                we >= ws,
                "窓が反転してはならない (elapsed={elapsed}): ws={ws} we={we}"
            );
            // 5s 未満は開始前データなし → ゼロ幅に畳む。
            assert_eq!(we, SESSION_START, "ゼロ幅に畳む (elapsed={elapsed})");
        }
        // ちょうど 5s: 終端が session_start に一致 (ゼロ幅境界)。
        let (ws, we) = self_marker_window_clamped(SESSION_START + 5_000, SESSION_START);
        assert_eq!((ws, we), (SESSION_START, SESSION_START));
        // 5s 超: 通常どおり終端が前進する (非ゼロ幅)。
        let (ws, we) = self_marker_window_clamped(SESSION_START + 6_000, SESSION_START);
        assert_eq!((ws, we), (SESSION_START, SESSION_START + 1_000));
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
            max_gap_ms: u64::MAX,
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
