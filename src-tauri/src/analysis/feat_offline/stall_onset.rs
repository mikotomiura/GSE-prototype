//! `stall onset`（`t0`）検出器（ADR-030 D2 / D3 / D4 / D5 / D6）。
//!
//! **causal**（`super` のモジュール doc の区分に従う）: 各時刻の判定は、その時刻までに
//! 実際に発生した `key` 行だけから決まる。未来の `key` 行を 1 行も参照しない
//! (AC2: `tests::detection_is_causal_no_lookahead` が入力末尾を切っても既出の判定が
//! 変わらないことを固定する)。
//!
//! 条件 A（産出）・条件 B（持続）・`t0 = s + θ_person` の定義は ADR-030 D3 / D4 逐語のまま。
//! `net`（挿入系 − 削除系）は `super::net_production`（issue 001 の共有ヘルパ）をそのまま使い、
//! 独自の産出判定を作らない（ADR-030 D3・Codex TASK-PRE 指摘 5）。
//!
//! # 実装が一意に決まらなかった箇所（★ 推測せず、ここに明記する）
//!
//! - **`W` / `q` / `B` の値**: ADR-030 D4 は「決め方」だけを凍結し、値は P1 前の事前宣言に
//!   委ねている。本モジュールは [`StallOnsetConfig`] で受け取り、コードに焼かない
//!   （Scope: 「値をコードに焼かない」）。既定値は特徴量窓 (30s) と時間尺度を揃えただけの
//!   プレースホルダである。
//! - **分位点の推定法**（D4 点 3「nearest-rank か線形補間かを事前宣言する」）: 本モジュールは
//!   **nearest-rank**（`dispersion.rs::quantile` と同じ規約）を採用した。線形補間との差は
//!   小標本で顕在化しうるので、P1 の事前宣言で確定させること。
//! - **修飾キー押下中の文字キー除外**（D3 逐語「修飾キーが押されている間の文字キーは
//!   挿入系に数えない」）: `super::net_production` は `press == true` の `KeyPress`
//!   （`{t, vk}` のみ）を受け取り、修飾キーの押下区間を復元できる release 情報を持たない。
//!   これを実装するには `bin/replay.rs` に新しい `collect_*` 関数を足す必要があるが、
//!   本 issue の Allowed Files はそこを「`task_kind`/`phase` を `session_meta` から
//!   読み出す必要が生じたときだけ」に限定しており、範囲外である。ADR-030 自身が
//!   この経路の残差（`Ctrl+V` の突き合わせ・IME 確定）を「既知の系統誤差として受ける」と
//!   明記しているのと同じ扱いとし、**基本の写像**（D3 前段・`net_production` がそのまま実装
//!   している写像）のみを用いる。
//! - **1Hz 特徴列の欠測区間（原因を問わず条件 B の連続を切る規則。ADR-030 D8 (b-2)）**: Goal は
//!   D2/D3/D4/D5/D6 の実装と明記しており、D8 は対象外。Scope Out にも episode 集約は
//!   含まれない。実装するには欠測の原因を列挙する語彙に触れることになりかねず、
//!   D8 (b-2) 自身が「原因を問わず、原因ラベルを作らない」ことを求めている以上、
//!   本 issue の範囲を超える別 issue で扱うべき事項である。よって未実装のまま引き継ぐ。

use crate::analysis::metrics::{KeyPress, OutcomeConfig};

/// `stall onset` 検出のパラメータ。★ `W` / `q` / `B` は値をコードに焼かず、ここで受け取る
/// (ADR-030 D4)。既定値は P1 前の事前宣言が確定するまでのプレースホルダ。
#[derive(Debug, Clone, Copy)]
pub struct StallOnsetConfig {
    /// 条件 A の因果窓長 (ms)。ADR-030 D4: 特徴量窓と同じ 30 秒系列から選ぶ。
    pub w_ms: u64,
    /// θ_person の分位点 (0.0-1.0)。ADR-030 D4: p99 以上から選ぶ。
    pub q: f64,
    /// `t0` 直後の buffer (ms、ADR-030 D2)。★ 本 issue は tick 単位の出力のみで
    /// 期 (episode) を刻まないため未使用。将来の episode 集約 issue のために設定として
    /// 保持する (Scope: 「W/q/B は設定構造体で受け取る」)。
    pub b_ms: u64,
    /// 条件 A の産出判定閾値。★ 新しい定数ではなく既存 `OutcomeConfig::net_diff_min`
    /// の値をそのまま引く (ADR-030 D3)。
    pub net_diff_min: u64,
}

impl Default for StallOnsetConfig {
    fn default() -> Self {
        Self {
            w_ms: 30_000,
            q: 0.99,
            b_ms: 30_000,
            net_diff_min: OutcomeConfig::default().net_diff_min,
        }
    }
}

/// `stall onset` の 1 tick ぶんの値。onset が起きた tick だけ `is_onset = true` で
/// 他 5 フィールドが埋まる。他の tick は `is_onset = false` で `s_ms` / `t0_ms` /
/// `theta_person_ms` / `task_kind` は `null`（欠測を 0 で埋めない）。
/// `phase` は自然セッションでは常に `"unspecified"` (ADR-030 D5)。
#[derive(Debug, Clone, serde::Serialize)]
pub struct StallOnset {
    pub is_onset: bool,
    pub s_ms: Option<u64>,
    pub t0_ms: Option<u64>,
    pub theta_person_ms: Option<u64>,
    /// ★ 未宣言は `None`。「5 値目」を新設しない (ADR-030 D6) — 未宣言でも
    /// 個人全体の分布 (= このセッション内の分布) をそのまま使い、鍵を分けない。
    pub task_kind: Option<String>,
    /// ADR-030 D5: 自然セッション (O1) では常に `"unspecified"` に collapse する。
    pub phase: String,
}

impl StallOnset {
    fn none_row(task_kind: Option<&str>) -> Self {
        Self {
            is_onset: false,
            s_ms: None,
            t0_ms: None,
            theta_person_ms: None,
            task_kind: task_kind.map(str::to_owned),
            phase: "unspecified".to_string(),
        }
    }
}

/// 確定した 1 つの `stall onset`（条件 A が `s` で立ち上がり、`θ_person` 継続して
/// `t0` で確定したもの）。
#[derive(Debug, Clone, Copy, PartialEq)]
struct OnsetEvent {
    s_ms: u64,
    t0_ms: u64,
    theta_person_ms: u64,
}

/// nearest-rank 法で分位点を取る (`dispersion.rs::quantile` と同じ規約。線形補間なし。
/// `rank = ceil(q * n)`、1-indexed、`[1, n]` にクランプ)。★ このクランプは分位点の
/// **順位のインデックス範囲**を保証するものであり、ADR-030 D4 が禁じる θ_person への
/// 床/天井とは別物 (対象はインデックスであって θ_person の値ではない)。
/// `sorted_ascending` は昇順ソート済みを仮定する。要素 0 個なら `None`。
fn quantile_nearest_rank(sorted_ascending: &[u64], q: f64) -> Option<u64> {
    let n = sorted_ascending.len();
    if n == 0 {
        return None;
    }
    let rank = (q * n as f64).ceil() as usize;
    let idx = rank.clamp(1, n) - 1;
    Some(sorted_ascending[idx])
}

/// θ_person を `s` 時点までに観測された隣接 press 間隔から因果的に推定する (ADR-030 D4)。
/// `s` **以後**に確定する間隔 (2 打目が `s` より後) は使わない —— そうしないと、後から
/// 追加された `key` 行が既に確定した `s` の θ_person を変え、AC2 の因果性を破る。
/// サンプルが 1 件も無ければ `None` (床で埋めず「推定できない」を伝える。Stop Conditions:
/// 「単一セッション内では θ_person が推定できないとき → null を返す」)。
fn theta_person_causal(sorted_press_ts: &[u64], s: u64, q: f64) -> Option<u64> {
    let mut gaps: Vec<u64> = sorted_press_ts
        .windows(2)
        .filter(|w| w[1] <= s)
        .map(|w| w[1].saturating_sub(w[0]))
        .collect();
    if gaps.is_empty() {
        return None;
    }
    gaps.sort_unstable();
    quantile_nearest_rank(&gaps, q)
}

/// 時刻 `t` における条件 A の産出 (net) を、因果窓 `(t - w_ms, t]` で計算する。
/// ★ `t.saturating_sub(w_ms)` を窓の下端にしない —— セッション開始直後 (`t < w_ms`) では
/// 下端が 0 に飽和し、`t == 0` の打鍵が自分自身の評価窓から排除される回帰を生む
/// (2026-09-15 実装時に発見)。`t - k.timestamp < w_ms` の形で書けば `k.timestamp <= t` の
/// 前提のもとで飽和が要らない。
fn net_at(sorted_keys: &[KeyPress], t: u64, w_ms: u64) -> i64 {
    let in_window: Vec<KeyPress> = sorted_keys
        .iter()
        .filter(|k| k.timestamp <= t && t - k.timestamp < w_ms)
        .copied()
        .collect();
    super::net_production(&in_window)
}

/// `stall onset` 列を検出する純関数 (ADR-030 D2/D3 の中心アルゴリズム)。
///
/// 評価時刻の集合は ADR-030 D3 逐語のとおり `{key行のt} ∪ {key行のt+W} ∪ {s+θ_person}`
/// だが、後者は「条件 A が `s` から `t0` まで途切れず持続したか」を**既存の 2 集合上の
/// 評価だけで**確認できるため (条件 A が変わる時刻はこの 2 集合に尽きる)、明示的な
/// 第 3 集合を構築せず「`s` から `t0` までの区間に落ちる既存の評価時刻をすべて確認する」
/// 形で実装する。
///
/// 初期状態 (最初の評価時刻より前) は条件 A = false (産出あり) とみなす —— ADR-030 は
/// セッション開始前の状態を定義していないため、本関数の実装上の約束として明記する。
fn detect_stall_onsets(keys: &[KeyPress], config: &StallOnsetConfig) -> Vec<OnsetEvent> {
    if keys.is_empty() {
        return Vec::new();
    }
    let mut sorted: Vec<KeyPress> = keys.to_vec();
    sorted.sort_by_key(|k| k.timestamp);
    let press_ts: Vec<u64> = sorted.iter().map(|k| k.timestamp).collect();

    let mut instants: Vec<u64> = Vec::with_capacity(sorted.len() * 2);
    for k in &sorted {
        instants.push(k.timestamp);
        instants.push(k.timestamp + config.w_ms);
    }
    instants.sort_unstable();
    instants.dedup();

    let net_diff_min = config.net_diff_min as i64;
    let mut onsets = Vec::new();
    let mut prev_cond_a = false;

    for i in 0..instants.len() {
        let t = instants[i];
        let cond_a = net_at(&sorted, t, config.w_ms) < net_diff_min;
        if cond_a && !prev_cond_a {
            let s = t;
            if let Some(theta) = theta_person_causal(&press_ts, s, config.q) {
                let t0 = s + theta;
                let mut confirmed = true;
                for &later in &instants[(i + 1)..] {
                    if later > t0 {
                        break;
                    }
                    if net_at(&sorted, later, config.w_ms) >= net_diff_min {
                        confirmed = false;
                        break;
                    }
                }
                if confirmed {
                    onsets.push(OnsetEvent {
                        s_ms: s,
                        t0_ms: t0,
                        theta_person_ms: theta,
                    });
                }
            }
        }
        prev_cond_a = cond_a;
    }
    onsets
}

/// 1 Hz tick 単位の `stall_onset` 列を作る。`super::build_feature_rows` から呼ばれる。
/// `tick_count` / `grid_origin_ms` / `tick_ms` は呼び出し側の tick グリッドと揃える
/// (帰属先を `t0_ms` から逆算する)。範囲外 (グリッド外) に落ちる `t0` は帰属先が無いため
/// 黙って捨てる (境界入力で panic しない)。
pub fn stall_onset_column(
    keys: &[KeyPress],
    tick_count: usize,
    grid_origin_ms: u64,
    tick_ms: u64,
    config: &StallOnsetConfig,
    task_kind: Option<&str>,
) -> Vec<StallOnset> {
    let mut column: Vec<StallOnset> = (0..tick_count)
        .map(|_| StallOnset::none_row(task_kind))
        .collect();
    for ev in detect_stall_onsets(keys, config) {
        if ev.t0_ms < grid_origin_ms {
            continue;
        }
        let idx = ((ev.t0_ms - grid_origin_ms) / tick_ms) as usize;
        if idx < tick_count {
            column[idx] = StallOnset {
                is_onset: true,
                s_ms: Some(ev.s_ms),
                t0_ms: Some(ev.t0_ms),
                theta_person_ms: Some(ev.theta_person_ms),
                task_kind: task_kind.map(str::to_owned),
                phase: "unspecified".to_string(),
            };
        }
    }
    column
}

#[cfg(test)]
mod tests {
    use super::*;

    fn key(t: u64) -> KeyPress {
        KeyPress {
            timestamp: t,
            vk: 0x41, // 'A' — text-producing
        }
    }

    /// 既定 config (W=30_000ms, q=0.99, net_diff_min=1) で、3 打鍵 (0/100/200ms) の後
    /// 沈黙する短い合成セッション。手計算 (モジュール doc 参照):
    /// s = 30_200 (最後の press 200 が窓から抜ける瞬間) / θ_person = 100 (隣接間隔 [100,100]
    /// の p99 = nearest-rank で 100) / t0 = 30_300。
    fn small_onset_keys() -> Vec<KeyPress> {
        vec![key(0), key(100), key(200)]
    }

    /// AC2: 入力の末尾を切っても、既に確定した (早い時刻の) onset の判定が変わらないこと。
    #[test]
    fn detection_is_causal_no_lookahead() {
        let config = StallOnsetConfig::default();
        let short = small_onset_keys();
        let short_onsets = detect_stall_onsets(&short, &config);
        assert_eq!(short_onsets.len(), 1);
        assert_eq!(
            short_onsets[0],
            OnsetEvent {
                s_ms: 30_200,
                t0_ms: 30_300,
                theta_person_ms: 100,
            }
        );

        // 最初の onset (t0=30_300) が確定した「後」に、さらに打鍵を足した長い入力。
        let mut long = short.clone();
        long.push(key(40_000));
        long.push(key(40_100));
        let long_onsets = detect_stall_onsets(&long, &config);

        assert_eq!(
            long_onsets[0], short_onsets[0],
            "末尾に打鍵を足しても、既に確定した早い onset の s/t0/theta は変わらない"
        );
    }

    /// AC3: `t0 = s + theta_person` が成り立つ (ADR-030 D2: `t0` は「継続の開始 s」ではない)。
    #[test]
    fn t0_is_s_plus_theta() {
        let config = StallOnsetConfig::default();
        let onsets = detect_stall_onsets(&small_onset_keys(), &config);
        assert_eq!(onsets.len(), 1);
        assert_eq!(onsets[0].t0_ms, onsets[0].s_ms + onsets[0].theta_person_ms);
        assert_ne!(
            onsets[0].t0_ms, onsets[0].s_ms,
            "t0 は s と同一であってはならない (D2: 検出時点は継続開始時点ではない)"
        );
    }

    /// AC4: θ_person に床も天井も無い (ADR-030 D4 逐語)。極端に小さい/大きい単一サンプルが
    /// そのまま (クランプされず) 返ることを確認する。
    #[test]
    fn theta_has_no_floor_or_ceiling() {
        // 単一サンプル 3ms —— 小さすぎるからと引き上げられない。
        let tiny = theta_person_causal(&[0, 3], 3, 0.99);
        assert_eq!(tiny, Some(3));

        // 単一サンプル 5,000,000ms —— 大きすぎるからと切り下げられない。
        let huge = theta_person_causal(&[0, 5_000_000], 5_000_000, 0.99);
        assert_eq!(huge, Some(5_000_000));
    }

    /// AC6: task_kind が未宣言 (`None`) でも「5 値目」の鍵を作らず、宣言時と同じ分布
    /// (このセッション内の分布) を使う —— 計算結果 (is_onset/s_ms/t0_ms/theta_person_ms) は
    /// task_kind の有無に依らず同一になる。記録される task_kind だけが入力を反映する。
    #[test]
    fn undeclared_task_kind_backs_off_not_new_key() {
        let config = StallOnsetConfig::default();
        let keys = small_onset_keys();
        let tick_count = 40;
        let grid_origin_ms = 0;
        let tick_ms = crate::analysis::loop_step::ENGINE_TICK_MS;

        let undeclared =
            stall_onset_column(&keys, tick_count, grid_origin_ms, tick_ms, &config, None);
        let declared = stall_onset_column(
            &keys,
            tick_count,
            grid_origin_ms,
            tick_ms,
            &config,
            Some("writing"),
        );

        let onset_idx = undeclared
            .iter()
            .position(|row| row.is_onset)
            .expect("onset should fire");
        assert!(declared[onset_idx].is_onset);
        assert_eq!(undeclared[onset_idx].s_ms, declared[onset_idx].s_ms);
        assert_eq!(undeclared[onset_idx].t0_ms, declared[onset_idx].t0_ms);
        assert_eq!(
            undeclared[onset_idx].theta_person_ms, declared[onset_idx].theta_person_ms,
            "task_kind の宣言有無で計算結果 (theta_person) が変わってはいけない (D6: 鍵を作らない)"
        );

        assert_eq!(undeclared[onset_idx].task_kind, None);
        assert_eq!(declared[onset_idx].task_kind, Some("writing".to_string()));
    }

    /// AC7: `phase` は自然セッション (O1) では常に `"unspecified"` に collapse する (ADR-030 D5)。
    #[test]
    fn phase_collapses_to_unspecified_for_natural_sessions() {
        let config = StallOnsetConfig::default();
        let keys = small_onset_keys();
        let column = stall_onset_column(&keys, 40, 0, 1000, &config, Some("writing"));
        let onset_row = column.iter().find(|row| row.is_onset).expect("onset row");
        assert_eq!(onset_row.phase, "unspecified");
        // onset が起きていない行も phase フィールド自体は持つ (AC1: 全行が 6 フィールドを持つ)。
        assert_eq!(column[0].phase, "unspecified");
    }

    /// 境界: 打鍵が無ければ onset も無い (panic しない)。
    #[test]
    fn empty_keys_produce_no_onsets() {
        let config = StallOnsetConfig::default();
        assert!(detect_stall_onsets(&[], &config).is_empty());
        let column = stall_onset_column(&[], 5, 0, 1000, &config, None);
        assert_eq!(column.len(), 5);
        assert!(column.iter().all(|row| !row.is_onset));
    }
}
