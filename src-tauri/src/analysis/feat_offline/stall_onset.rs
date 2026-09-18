//! `stall onset`（`t0`）検出器（ADR-030 D2 / D3 / D4 / D5 / D6 / D8 (b-2)）。
//!
//! **causal**（`super` のモジュール doc の区分に従う）: 各時刻の判定は、その時刻までに
//! 実際に発生した `key` 行だけから決まる。未来の `key` 行を 1 行も参照しない
//! (`tests::prefix_stable_at_every_cut` が入力を任意の時刻で切っても、切った時刻以前に
//! 確定する onset の集合が変わらないことを固定する)。
//!
//! 条件 A（産出）・条件 B（持続）・`t0 = s + θ_person` の定義は ADR-030 D3 / D4 逐語のまま。
//! `net`（挿入系 − 削除系）は `super::net_production` / `super::key_net_delta`（issue 001 の
//! 共有ヘルパ）をそのまま使い、独自の産出判定を作らない（ADR-030 D3・Codex TASK-PRE 指摘 5）。
//!
//! # 観測区間（ADR-030 D8 (b-2)）
//!
//! `feat` 行（1Hz 特徴列）の**存在**だけを使い、隣接差が [`StallOnsetConfig::hole_gap_ms`]
//! 以下の極大な連続を 1 つの観測区間とする。条件 A / B の評価は**観測区間の内側だけ**
//! で行い（区間をまたがない）、各区間の評価開始時点で条件 A の直前状態を `false` に戻す
//! (D8 (b) 「跨いで足し上げない」)。★ `feat` 行に穴が生じる原因は 1 つも区別しない
//! (D8 (b-2) 「原因は問わない。原因ラベルを作らない」)。`feat` 行が 1 本も無い入力には
//! 観測区間が無く、onset は 1 つも立たない。
//!
//! θ の標本は**同じ観測区間に入る隣接 press 対**だけを使う（穴をまたぐ対は使わない）が、
//! ⚠️ **`s` が属する区間に限定はしない** —— 規範文の θ 標本節は「同じ観測区間 `[a, b]`」と
//! 書くだけで「`s` と同じ区間」とは書いておらず、対象は**全観測区間からプール**する
//! (issue 008 再裁定。「確定」節の「`s` **と同じ**観測区間の右端 `b`」は `t0` の上限にだけ
//! 使う別の制約であり、混同しない)。
//!
//! # 実装が一意に決まらなかった箇所（★ 推測せず、ここに明記する）
//!
//! - **`W` / `q` / `B` / `hole_gap_ms` / `warmup_count` の値**: ADR-030 D4 は「決め方」だけを
//!   凍結し、値は P1 前の事前宣言に委ねている。`w_ms` / `b_ms` は既存
//!   `OutcomeConfig::merge_gap_ms` から、`hole_gap_ms` は `2 * ENGINE_TICK_MS`（1Hz の予定行が
//!   少なくとも 1 本欠けたと言える構造的な下限）から借りたプレースホルダであり、
//!   `warmup_count` は `None`（無効化）のままである —— **いずれも値そのものを決めたわけではない**
//!   (`blockers.md` 起票 15)。
//! - **分位点の推定法**（D4 点 3「nearest-rank か線形補間かを事前宣言する」）: 本モジュールは
//!   **nearest-rank**（`dispersion.rs::quantile` と同じ規約）を採用した。線形補間との差は
//!   小標本で顕在化しうるので、P1 の事前宣言で確定させること。
//! - **修飾キー押下中の文字キー除外**（D3）: `KeyCategory::Modifier` は Shift を含むため、
//!   逐語どおり実装すると大文字・記号の入力まで産出から外れる。研究者判断待ち
//!   (`blockers.md` 起票 11)。
//! - **IME 変換中の抑制**（D3 抑制表 2 行目）: 区間の定義と「抑制」の意味が未確定。
//!   研究者判断待ち (`blockers.md` 起票 12)。
//! - **ポインタ活動の両極**（D3 抑制表 3 行目）: 出力の形が未確定。研究者判断待ち
//!   (`blockers.md` 起票 13)。
//! - **`phase`**: 構造化セッションの block id は未実装。自然セッション (O1) では常に
//!   `"unspecified"` に collapse する (ADR-030 D5)。

use crate::analysis::loop_step::ENGINE_TICK_MS;
use crate::analysis::metrics::{KeyPress, OutcomeConfig};

/// `stall onset` 検出のパラメータ。★ `W` / `q` / `B` / `hole_gap_ms` / `warmup_count` は
/// 値をコードに焼かず、ここで受け取る (ADR-030 D4)。既定値は P1 前の事前宣言が確定するまでの
/// プレースホルダ。
#[derive(Debug, Clone, Copy)]
pub struct StallOnsetConfig {
    /// 条件 A の因果窓長 (ms)。ADR-030 D4: 特徴量窓と同じ 30 秒系列から選ぶ。
    pub w_ms: u64,
    /// θ_person の分位点 (0.0-1.0)。ADR-030 D4: p99 以上から選ぶ。
    pub q: f64,
    /// `t0` 直後の buffer (ms、ADR-030 D2)。★ 本モジュールは tick 単位の出力のみで
    /// 期 (episode) を刻まないため未使用。将来の episode 集約のために設定として保持する。
    pub b_ms: u64,
    /// 条件 A の産出判定閾値。★ 新しい定数ではなく既存 `OutcomeConfig::net_diff_min`
    /// の値をそのまま引く (ADR-030 D3)。
    pub net_diff_min: u64,
    /// 観測区間を切る閾値 (ms)。隣接する `feat` 行の間隔がこれを超えたら区間を分ける
    /// (ADR-030 D8 (b-2))。
    pub hole_gap_ms: u64,
    /// θ の標本数がこれ未満なら個人分位点を使わない (`None` を返す)。`None` は無効化
    /// (下限を課さない) を表す (ADR-030 D4 点 1)。
    pub warmup_count: Option<usize>,
}

impl Default for StallOnsetConfig {
    fn default() -> Self {
        let outcome = OutcomeConfig::default();
        Self {
            w_ms: outcome.merge_gap_ms,
            q: 0.99,
            b_ms: outcome.merge_gap_ms,
            net_diff_min: outcome.net_diff_min,
            hole_gap_ms: 2 * ENGINE_TICK_MS,
            warmup_count: None,
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
    /// onset 行には `s` 時点で有効な宣言 (`ts <= s` の最新) を記録する。宣言が無ければ
    /// `None`。onset でない行は常に `None` (他の 4 フィールドと揃える)。
    pub task_kind: Option<String>,
    /// ADR-030 D5: 自然セッション (O1) では常に `"unspecified"` に collapse する。
    pub phase: String,
}

impl StallOnset {
    fn none_row() -> Self {
        Self {
            is_onset: false,
            s_ms: None,
            t0_ms: None,
            theta_person_ms: None,
            task_kind: None,
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

/// `feat` 行の時刻 (`t` だけ・値は読まない) から観測区間を作る (ADR-030 D8 (b-2))。
/// 昇順・重複除去した上で、隣接差が `hole_gap_ms` を超えたところで区間を分ける。
/// `feat_ts` が空なら観測区間は無い (空 `Vec`)。
fn observed_intervals(feat_ts: &[u64], hole_gap_ms: u64) -> Vec<(u64, u64)> {
    if feat_ts.is_empty() {
        return Vec::new();
    }
    let mut sorted = feat_ts.to_vec();
    sorted.sort_unstable();
    sorted.dedup();

    let mut intervals = Vec::new();
    let mut start = sorted[0];
    let mut prev = sorted[0];
    for &t in &sorted[1..] {
        if t - prev > hole_gap_ms {
            intervals.push((start, prev));
            start = t;
        }
        prev = t;
    }
    intervals.push((start, prev));
    intervals
}

/// `sorted_keys` (timestamp 昇順) の net production 累積和。`prefix[i]` は
/// `sorted_keys[0..i]` の net 合計 (`prefix[0] == 0`)。区間 `(lo, hi]` の net は
/// `prefix[hi] - prefix[lo]` で `O(1)` に求まる (計算量対策・issue 008 AC18)。
fn net_prefix(sorted_keys: &[KeyPress]) -> Vec<i64> {
    let mut prefix = Vec::with_capacity(sorted_keys.len() + 1);
    let mut acc = 0i64;
    prefix.push(acc);
    for k in sorted_keys {
        acc += super::key_net_delta(k);
        prefix.push(acc);
    }
    prefix
}

/// 時刻 `t` における条件 A の産出 (net) を、因果窓 `(t - w_ms, t]` で `O(log N)` に計算する
/// (`net_prefix` の累積和 ＋ 二分探索。旧実装の `O(N)` フィルタを置き換える)。
///
/// ★ `t.saturating_sub(w_ms)` を窓の下端にしない —— セッション開始直後 (`t < w_ms`) では
/// 下端が 0 に飽和し、`t == 0` の打鍵が自分自身の評価窓から排除される回帰を生む
/// (2026-09-15 実装時に発見)。下限判定は `timestamp + w_ms <= t` を `checked_add` で行い、
/// オーバーフロー (`timestamp` が `u64::MAX` 付近) は「窓の外に出ない」側 (= 含める) に倒す。
fn net_at_fast(sorted_keys: &[KeyPress], prefix: &[i64], t: u64, w_ms: u64) -> i64 {
    let idx_hi = sorted_keys.partition_point(|k| k.timestamp <= t);
    let idx_lo = sorted_keys.partition_point(|k| {
        k.timestamp
            .checked_add(w_ms)
            .map(|sum| sum <= t)
            .unwrap_or(false)
    });
    prefix[idx_hi] - prefix[idx_lo]
}

/// `sorted_keys` の全打鍵から評価時刻候補 `{key の t} ∪ {key の t + W}` を作る
/// (ADR-030 D3 逐語)。観測区間ごとの範囲制限は呼び出し側 (`detect_stall_onsets`) が行う。
/// `t + W` の加算オーバーフローは候補から落とす (AC16: panic しない)。
fn build_global_instants(sorted_keys: &[KeyPress], w_ms: u64) -> Vec<u64> {
    let mut instants = Vec::with_capacity(sorted_keys.len() * 2);
    for k in sorted_keys {
        instants.push(k.timestamp);
        if let Some(t_plus_w) = k.timestamp.checked_add(w_ms) {
            instants.push(t_plus_w);
        }
    }
    instants.sort_unstable();
    instants.dedup();
    instants
}

/// θ_person を、`(resuming_ts, gap_ms)` の候補列から因果的に推定する (ADR-030 D4)。
/// `s` **以後**に確定する間隔 (2 打目が `s` より後) は使わない —— そうしないと、後から
/// 追加された `key` 行が既に確定した `s` の θ_person を変え、因果性を破る。サンプルが
/// 1 件も無い、または `warmup_count` に届かない場合は `None` (床で埋めず「推定できない」を
/// 伝える)。呼び出し側が「同じ観測区間に入る対だけ」を候補列として渡す (`pooled_theta_gaps`
/// / `theta_person_for_interval` のいずれか)。
fn theta_person_from_gaps(
    gaps: &[(u64, u64)],
    s: u64,
    q: f64,
    warmup_count: Option<usize>,
) -> Option<u64> {
    let mut values: Vec<u64> = gaps
        .iter()
        .filter(|&&(resuming_ts, _)| resuming_ts <= s)
        .map(|&(_, gap_ms)| gap_ms)
        .collect();
    if values.is_empty() {
        return None;
    }
    if let Some(n) = warmup_count {
        if values.len() < n {
            return None;
        }
    }
    values.sort_unstable();
    quantile_nearest_rank(&values, q)
}

/// 全観測区間を通して、区間内 (穴をまたがない) の隣接 press 間隔だけを集めたプール
/// (`resuming_ts` 昇順)。θ の標本は `s` が属する区間に限定せず、**同じ観測区間に入る対で
/// あれば全区間からプールする** (モジュール doc 冒頭・issue 008 再裁定)。
/// `sorted_press_ts` は昇順ソート済みを仮定する。
fn pooled_theta_gaps(sorted_press_ts: &[u64], intervals: &[(u64, u64)]) -> Vec<(u64, u64)> {
    let mut pooled = Vec::new();
    for &(a, b) in intervals {
        let lo = sorted_press_ts.partition_point(|&t| t < a);
        let hi = sorted_press_ts.partition_point(|&t| t <= b);
        pooled.extend(
            super::press_intervals(&sorted_press_ts[lo..hi])
                .into_iter()
                .map(|iv| (iv.resuming_ts, iv.gap_ms)),
        );
    }
    pooled.sort_unstable_by_key(|&(resuming_ts, _)| resuming_ts);
    pooled
}

/// 1 つの観測区間 `[a, b]` の中で `stall onset` を検出する (ADR-030 D8 (b) 「連続を切る」
/// を区間単位で満たす)。評価時刻は `{key の t} ∪ {key の t + W} ∪ {a + W}` を
/// `[a + W, b]` に制限したものだけ (D3 逐語 ＋ issue 008 の観測区間の規範)。
/// 区間の直前状態 (立ち上がり判定の `prev`) はここで `false` にリセットする。
fn detect_stall_onsets_for_interval(
    a: u64,
    b: u64,
    global_instants: &[u64],
    sorted_keys: &[KeyPress],
    prefix: &[i64],
    pooled_gaps: &[(u64, u64)],
    config: &StallOnsetConfig,
) -> Vec<OnsetEvent> {
    let w = config.w_ms;
    let net_diff_min = config.net_diff_min as i64;

    // 区間が W に届かない (a + W > b) なら、この区間では 1 度も評価されない
    // (ADR-030 D8 (b) 「区間の終了後 W の間も条件 A を評価しない」の裏面)。
    let Some(start) = a.checked_add(w) else {
        return Vec::new();
    };
    if start > b {
        return Vec::new();
    }

    let lo = global_instants.partition_point(|&t| t < start);
    let hi = global_instants.partition_point(|&t| t <= b);
    let mut instants: Vec<u64> = Vec::with_capacity(hi - lo + 1);
    instants.push(start);
    instants.extend_from_slice(&global_instants[lo..hi]);
    instants.sort_unstable();
    instants.dedup();

    let cond_a: Vec<bool> = instants
        .iter()
        .map(|&t| net_at_fast(sorted_keys, prefix, t, w) < net_diff_min)
        .collect();

    let mut onsets = Vec::new();
    let mut prev = false;
    for i in 0..instants.len() {
        if cond_a[i] && !prev {
            let s = instants[i];
            if let Some(theta) =
                theta_person_from_gaps(pooled_gaps, s, config.q, config.warmup_count)
            {
                if let Some(t0) = s.checked_add(theta) {
                    // t0 が区間の右端を越える onset は立てない
                    // (D3「セッションが終わった場合は第 3 項を置かない」の issue 008 実装)。
                    if t0 <= b {
                        let mut confirmed = true;
                        let mut j = i + 1;
                        while j < instants.len() && instants[j] <= t0 {
                            if !cond_a[j] {
                                confirmed = false;
                                break;
                            }
                            j += 1;
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
            }
        }
        prev = cond_a[i];
    }
    onsets
}

/// `stall onset` 列を検出する純関数 (ADR-030 D2/D3/D4/D8 (b-2) の中心アルゴリズム)。
/// `feat_ts` が空なら観測区間が無いので `onset` は 1 つも立たない (AC3)。
/// 計算量は `O(N log N)` (`N` = `keys.len()`。`net_at_fast` の二分探索 ＋ 各観測区間 1 回の
/// ソート。issue 008 AC18 —— 旧実装は評価時刻ごとに `O(N)` フィルタする `O(N^2)` だった)。
fn detect_stall_onsets(
    keys: &[KeyPress],
    feat_ts: &[u64],
    config: &StallOnsetConfig,
) -> Vec<OnsetEvent> {
    if feat_ts.is_empty() {
        return Vec::new();
    }
    let mut sorted_keys: Vec<KeyPress> = keys.to_vec();
    sorted_keys.sort_by_key(|k| k.timestamp);
    let press_ts: Vec<u64> = sorted_keys.iter().map(|k| k.timestamp).collect();
    let prefix = net_prefix(&sorted_keys);
    let global_instants = build_global_instants(&sorted_keys, config.w_ms);
    let intervals = observed_intervals(feat_ts, config.hole_gap_ms);
    let pooled_gaps = pooled_theta_gaps(&press_ts, &intervals);

    let mut onsets = Vec::new();
    for (a, b) in intervals {
        onsets.extend(detect_stall_onsets_for_interval(
            a,
            b,
            &global_instants,
            &sorted_keys,
            &prefix,
            &pooled_gaps,
            config,
        ));
    }
    onsets
}

/// `s` 時点で有効な `task_kind` 宣言 (`ts <= s` の最新) を返す。宣言が無ければ `None`。
/// `sorted_declarations` は `ts` 昇順ソート済みを仮定する。
fn declaration_in_effect(sorted_declarations: &[(u64, String)], s: u64) -> Option<String> {
    let idx = sorted_declarations.partition_point(|(ts, _)| *ts <= s);
    if idx == 0 {
        None
    } else {
        Some(sorted_declarations[idx - 1].1.clone())
    }
}

/// 確定した onset 列を 1 Hz tick グリッドへ写像する。検出アルゴリズムから分離してあるのは
/// テスト容易性のため (`tests::same_tick_collision_keeps_the_first` が合成した `OnsetEvent`
/// だけでタイル衝突を検査できる)。
///
/// 同じ tick に 2 つ目の onset が落ちても**上書きしない** —— 先に確定した (時刻順で早い)
/// onset を残し、件数だけ `tracing::warn!` で報告する。
fn column_from_onsets(
    onsets: &[OnsetEvent],
    task_kind_declarations: &[(u64, String)],
    tick_count: usize,
    grid_origin_ms: u64,
    tick_ms: u64,
) -> Vec<StallOnset> {
    let mut column: Vec<StallOnset> = (0..tick_count).map(|_| StallOnset::none_row()).collect();
    let mut sorted_decls: Vec<(u64, String)> = task_kind_declarations.to_vec();
    sorted_decls.sort_by_key(|d| d.0);

    let mut collisions: u64 = 0;
    for ev in onsets {
        if ev.t0_ms < grid_origin_ms {
            continue;
        }
        let idx = ((ev.t0_ms - grid_origin_ms) / tick_ms) as usize;
        if idx >= tick_count {
            continue;
        }
        if column[idx].is_onset {
            collisions += 1;
            continue;
        }
        column[idx] = StallOnset {
            is_onset: true,
            s_ms: Some(ev.s_ms),
            t0_ms: Some(ev.t0_ms),
            theta_person_ms: Some(ev.theta_person_ms),
            task_kind: declaration_in_effect(&sorted_decls, ev.s_ms),
            phase: "unspecified".to_string(),
        };
    }
    if collisions > 0 {
        tracing::warn!(
            collisions,
            "stall_onset_column: multiple onsets landed on the same tick; kept the first"
        );
    }
    column
}

/// 1 Hz tick 単位の `stall_onset` 列を作る。`super::build_feature_rows` から呼ばれる。
/// `feat_ts` は 1Hz 特徴列の時刻 (値は読まない・観測区間の判定にだけ使う)。
/// `task_kind_declarations` は `(ts, task_kind)` の宣言列 (順不同でよい)。
/// `tick_count` / `grid_origin_ms` / `tick_ms` は呼び出し側の tick グリッドと揃える
/// (帰属先を `t0_ms` から逆算する)。範囲外 (グリッド外) に落ちる `t0` は帰属先が無いため
/// 黙って捨てる (境界入力で panic しない)。
pub fn stall_onset_column(
    keys: &[KeyPress],
    feat_ts: &[u64],
    task_kind_declarations: &[(u64, String)],
    tick_count: usize,
    grid_origin_ms: u64,
    tick_ms: u64,
    config: &StallOnsetConfig,
) -> Vec<StallOnset> {
    let onsets = detect_stall_onsets(keys, feat_ts, config);
    column_from_onsets(
        &onsets,
        task_kind_declarations,
        tick_count,
        grid_origin_ms,
        tick_ms,
    )
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

    /// 3 打鍵 (0/100/200ms) の後に沈黙する短い合成キー列。手計算 (モジュール doc 参照):
    /// s = 30_200 (最後の press 200 が窓から抜ける瞬間) / θ_person = 100 (隣接間隔 [100,100]
    /// の p99 = nearest-rank で 100) / t0 = 30_300。
    fn small_onset_keys() -> Vec<KeyPress> {
        vec![key(0), key(100), key(200)]
    }

    /// `feat` 行を `start..=end` の範囲で `step` ms ごとに生成するテスト専用ヘルパ
    /// (観測区間を連続にするため。値は読まれないのでダミー生成でよい)。
    fn feat_ts_range(start: u64, end_inclusive: u64, step: u64) -> Vec<u64> {
        let mut v = Vec::new();
        let mut t = start;
        while t <= end_inclusive {
            v.push(t);
            t += step;
        }
        v
    }

    /// 昇順 press 時刻列を `theta_person_from_gaps` が受け取る `(resuming_ts, gap_ms)` 列に
    /// 変換するテスト専用ヘルパ (単一区間を仮定するテストで `pooled_theta_gaps` を経由せず
    /// 直接 `theta_person_from_gaps` を検査するため)。
    fn gaps_from_presses(sorted_press_ts: &[u64]) -> Vec<(u64, u64)> {
        super::super::press_intervals(sorted_press_ts)
            .into_iter()
            .map(|iv| (iv.resuming_ts, iv.gap_ms))
            .collect()
    }

    /// AC13 の前提にもなる基本テスト: 入力の末尾を切っても、既に確定した (早い時刻の)
    /// onset の判定が変わらないこと。
    #[test]
    fn detection_is_causal_no_lookahead() {
        let config = StallOnsetConfig::default();
        let feat = feat_ts_range(0, 41_000, 1_000);
        let short = small_onset_keys();
        let short_onsets = detect_stall_onsets(&short, &feat, &config);
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
        let long_onsets = detect_stall_onsets(&long, &feat, &config);

        assert_eq!(
            long_onsets[0], short_onsets[0],
            "末尾に打鍵を足しても、既に確定した早い onset の s/t0/theta は変わらない"
        );
    }

    /// `t0 = s + theta_person` が成り立つ (ADR-030 D2: `t0` は「継続の開始 s」ではない)。
    #[test]
    fn t0_is_s_plus_theta() {
        let config = StallOnsetConfig::default();
        let feat = feat_ts_range(0, 31_000, 1_000);
        let onsets = detect_stall_onsets(&small_onset_keys(), &feat, &config);
        assert_eq!(onsets.len(), 1);
        assert_eq!(onsets[0].t0_ms, onsets[0].s_ms + onsets[0].theta_person_ms);
        assert_ne!(
            onsets[0].t0_ms, onsets[0].s_ms,
            "t0 は s と同一であってはならない (D2: 検出時点は継続開始時点ではない)"
        );
    }

    /// θ_person に床も天井も無い (ADR-030 D4 逐語)。極端に小さい/大きい単一サンプルが
    /// そのまま (クランプされず) 返ることを確認する。
    #[test]
    fn theta_has_no_floor_or_ceiling() {
        // 単一サンプル 3ms —— 小さすぎるからと引き上げられない。
        let tiny = theta_person_from_gaps(&gaps_from_presses(&[0, 3]), 3, 0.99, None);
        assert_eq!(tiny, Some(3));

        // 単一サンプル 5,000,000ms —— 大きすぎるからと切り下げられない。
        let huge =
            theta_person_from_gaps(&gaps_from_presses(&[0, 5_000_000]), 5_000_000, 0.99, None);
        assert_eq!(huge, Some(5_000_000));
    }

    /// task_kind が未宣言 (`None`) でも計算結果 (is_onset/s_ms/t0_ms/theta_person_ms) は
    /// 変わらない —— 記録される task_kind だけが宣言の有無を反映する (ADR-030 D6)。
    #[test]
    fn undeclared_task_kind_backs_off_not_new_key() {
        let config = StallOnsetConfig::default();
        let keys = small_onset_keys();
        let feat = feat_ts_range(0, 31_000, 1_000);
        let tick_count = 40;
        let grid_origin_ms = 0;
        let tick_ms = ENGINE_TICK_MS;

        let undeclared = stall_onset_column(
            &keys,
            &feat,
            &[],
            tick_count,
            grid_origin_ms,
            tick_ms,
            &config,
        );
        let declared = stall_onset_column(
            &keys,
            &feat,
            &[(0, "writing".to_string())],
            tick_count,
            grid_origin_ms,
            tick_ms,
            &config,
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

    /// `phase` は自然セッション (O1) では常に `"unspecified"` に collapse する (ADR-030 D5)。
    #[test]
    fn phase_collapses_to_unspecified_for_natural_sessions() {
        let config = StallOnsetConfig::default();
        let keys = small_onset_keys();
        let feat = feat_ts_range(0, 31_000, 1_000);
        let column = stall_onset_column(
            &keys,
            &feat,
            &[(0, "writing".to_string())],
            40,
            0,
            1000,
            &config,
        );
        let onset_row = column.iter().find(|row| row.is_onset).expect("onset row");
        assert_eq!(onset_row.phase, "unspecified");
        // onset が起きていない行も phase フィールド自体は持つ (全行が 6 フィールドを持つ)。
        assert_eq!(column[0].phase, "unspecified");
    }

    /// 境界: 打鍵が無ければ onset も無い (panic しない)。
    #[test]
    fn empty_keys_produce_no_onsets() {
        let config = StallOnsetConfig::default();
        let feat = feat_ts_range(0, 5_000, 1_000);
        assert!(detect_stall_onsets(&[], &feat, &config).is_empty());
        let column = stall_onset_column(&[], &feat, &[], 5, 0, 1000, &config);
        assert_eq!(column.len(), 5);
        assert!(column.iter().all(|row| !row.is_onset));
    }

    /// AC2 (ADR-030 D8 (b-2)): `feat` 列に穴があると、穴をまたいだ「産出なし」の連続は
    /// 生まれない —— 穴が無ければ立つはずの onset が、穴のせいで消える。
    #[test]
    fn feat_hole_cuts_condition_b() {
        let config = StallOnsetConfig::default();
        let keys = small_onset_keys(); // 0, 100, 200

        // 対照: feat が 0..31000 で連続なら (穴が無い単一の観測区間) onset が 1 つ立つ。
        let continuous_feat = feat_ts_range(0, 31_000, 1_000);
        let baseline = detect_stall_onsets(&keys, &continuous_feat, &config);
        assert_eq!(baseline.len(), 1, "穴が無ければ onset が 1 つ立つはず");

        // 同じ key 列で、s (30200) が乗るはずの区間に feat の穴を作る
        // (10000..50000 に feat 行が無い)。
        let mut holed_feat = feat_ts_range(0, 10_000, 1_000);
        holed_feat.extend(feat_ts_range(50_000, 52_000, 1_000));
        let holed = detect_stall_onsets(&keys, &holed_feat, &config);
        assert!(
            holed.is_empty(),
            "feat の穴のせいで s+W (=30000) が乗る観測区間が消え、onset が 1 つも立たないはず: {holed:?}"
        );
    }

    /// AC3: `feat` 行が 1 本も無ければ観測区間が無く、onset は 1 つも立たない。
    #[test]
    fn no_feat_rows_means_no_onset() {
        let config = StallOnsetConfig::default();
        let keys = small_onset_keys();
        assert!(detect_stall_onsets(&keys, &[], &config).is_empty());
        let column = stall_onset_column(&keys, &[], &[], 40, 0, ENGINE_TICK_MS, &config);
        assert!(column.iter().all(|row| !row.is_onset));
    }

    /// AC4: 観測区間の長さが `W` に届かなければ (`a + W > b`)、その区間は 1 度も評価
    /// されない —— 区間を `a + W` まで伸ばした対照では同じ key 列で onset が立つ。
    #[test]
    fn no_evaluation_within_w_after_hole() {
        let config = StallOnsetConfig::default();
        let keys = small_onset_keys(); // 何も遮らなければ s=30200, t0=30300 で立つ

        let short_feat = feat_ts_range(0, 20_000, 1_000); // b=20000 < a+W=30000
        assert!(
            detect_stall_onsets(&keys, &short_feat, &config).is_empty(),
            "観測区間が a+W に届かないのに onset が立った"
        );

        let long_feat = feat_ts_range(0, 31_000, 1_000); // b=31000 >= a+W=30000
        assert_eq!(detect_stall_onsets(&keys, &long_feat, &config).len(), 1);
    }

    /// AC5: θ の標本は同じ観測区間に属する隣接 press だけから取り、区間をまたぐ間隔
    /// (feat の穴の前後をつなぐ間隔) は混ざらない。
    #[test]
    fn theta_sample_excludes_gaps_across_holes() {
        let config = StallOnsetConfig::default();
        // 区間1: feat 0..5000。key は 1000 のみ (区間1 の内側)。
        // 穴: 5000..40000 (feat 行なし)。
        // 区間2: feat 40000..72000。key は 41000, 41100 (小さな gap=100)。
        let mut feat = feat_ts_range(0, 5_000, 1_000);
        feat.extend(feat_ts_range(40_000, 72_000, 1_000));
        let keys = vec![key(1_000), key(41_000), key(41_100)];

        let onsets = detect_stall_onsets(&keys, &feat, &config);
        assert_eq!(
            onsets.len(),
            1,
            "区間2 だけで onset が 1 つ立つはず: {onsets:?}"
        );
        assert_eq!(
            onsets[0].theta_person_ms, 100,
            "区間をまたぐ gap (1000→41000 = 40000ms) が混ざると θ が跳ね上がるはず"
        );
        assert_eq!(onsets[0].s_ms, 71_100);
        assert_eq!(onsets[0].t0_ms, 71_200);
    }

    /// issue 008 再裁定: θ の標本は `s` が属する観測区間だけに限定せず、**同じ観測区間に
    /// 入る対であれば他の区間からもプール**する。規範文の θ 標本節は「同じ観測区間」と
    /// 書くだけで「`s` と同じ区間」に限定していない (「確定」節の t0<=b とは別の制約)。
    #[test]
    fn theta_sample_pools_from_other_intervals_too() {
        let config = StallOnsetConfig::default();
        // 区間1: feat 0..6000。key は 0, 5000 (gap=5000、区間1 の内側に収まる)。
        // 穴: 6000..40000 (feat 行なし)。
        // 区間2: feat 40000..77000 (s はここで立つ)。key は 41000, 41100 (gap=100)。
        let mut feat = feat_ts_range(0, 6_000, 1_000);
        feat.extend(feat_ts_range(40_000, 77_000, 1_000));
        let keys = vec![key(0), key(5_000), key(41_000), key(41_100)];

        let onsets = detect_stall_onsets(&keys, &feat, &config);
        assert_eq!(
            onsets.len(),
            1,
            "区間2 だけで onset が 1 つ立つはず: {onsets:?}"
        );
        assert_eq!(onsets[0].s_ms, 71_100);
        assert_eq!(
            onsets[0].theta_person_ms, 5_000,
            "θ の標本が s の区間 (区間2、gap=100 だけ) に限定されていて、\
             区間1 の gap=5000 がプールされていない可能性がある: {onsets:?}"
        );
        assert_eq!(onsets[0].t0_ms, 76_100);
    }

    /// AC6 (D3「セッションが終わった場合は第 3 項を置かない」): `t0` が観測区間の右端を
    /// 越える onset は立たない —— 区間を `t0` まで伸ばした対照では同じ `s`/`θ` で確定する。
    #[test]
    fn onset_beyond_last_feat_is_not_confirmed() {
        let config = StallOnsetConfig::default();
        let keys = vec![key(0), key(20_000)]; // gap 20000 → θ = 20000 (単一標本)

        // b=51000: s=50000 で立ち上がるが t0=70000 は区間の右端 (51000) を越える。
        let short_feat = feat_ts_range(0, 51_000, 1_000);
        assert!(
            detect_stall_onsets(&keys, &short_feat, &config).is_empty(),
            "t0 が観測区間の右端を越えるのに onset が確定した"
        );

        // 区間を t0 (70000) まで伸ばせば、同じ s / θ で onset が確定する (対照)。
        let long_feat = feat_ts_range(0, 71_000, 1_000);
        let onsets = detect_stall_onsets(&keys, &long_feat, &config);
        assert_eq!(onsets.len(), 1);
        assert_eq!(onsets[0].s_ms, 50_000);
        assert_eq!(onsets[0].theta_person_ms, 20_000);
        assert_eq!(onsets[0].t0_ms, 70_000);
    }

    /// AC7: onset 行の `task_kind` は `s` 時点で有効な最新の宣言を記録する。
    #[test]
    fn task_kind_is_the_declaration_in_effect_at_s() {
        let config = StallOnsetConfig::default();
        let keys = small_onset_keys(); // onset: s=30200, t0=30300
        let feat = feat_ts_range(0, 31_000, 1_000);

        // s=30200 の時点で有効な宣言は 2 個目 (ts=20000) のはず。
        let declarations = vec![(0, "writing".to_string()), (20_000, "coding".to_string())];
        let column =
            stall_onset_column(&keys, &feat, &declarations, 40, 0, ENGINE_TICK_MS, &config);
        let onset_row = column
            .iter()
            .find(|r| r.is_onset)
            .expect("onset should fire");
        assert_eq!(onset_row.task_kind, Some("coding".to_string()));

        // s より後の宣言 (ts=31000) は s 時点でまだ有効でないので反映されない。
        let declarations2 = vec![(0, "writing".to_string()), (31_000, "coding".to_string())];
        let column2 =
            stall_onset_column(&keys, &feat, &declarations2, 40, 0, ENGINE_TICK_MS, &config);
        let onset_row2 = column2
            .iter()
            .find(|r| r.is_onset)
            .expect("onset should fire");
        assert_eq!(onset_row2.task_kind, Some("writing".to_string()));
    }

    /// AC8: 既定値が既存パラメータ由来であること (生リテラルを直書きしない)。
    #[test]
    fn defaults_come_from_existing_params() {
        let config = StallOnsetConfig::default();
        let outcome = OutcomeConfig::default();
        assert_eq!(config.w_ms, outcome.merge_gap_ms);
        assert_eq!(config.b_ms, outcome.merge_gap_ms);
        assert_eq!(config.hole_gap_ms, 2 * ENGINE_TICK_MS);
        assert_eq!(config.warmup_count, None);
        assert_eq!(config.net_diff_min, outcome.net_diff_min);
    }

    /// AC9: `warmup_count` が `Some(n)` で標本数が `n` 未満なら onset を立てない。
    #[test]
    fn warmup_count_suppresses_small_sample() {
        let mut config = StallOnsetConfig::default();
        let feat = feat_ts_range(0, 31_000, 1_000);

        // small_onset_keys の θ 標本は 2 件 (0→100, 100→200)。
        config.warmup_count = Some(2);
        let onsets_ok = detect_stall_onsets(&small_onset_keys(), &feat, &config);
        assert_eq!(onsets_ok.len(), 1, "標本 2 件は warmup_count=2 を満たす");

        config.warmup_count = Some(3);
        let onsets_blocked = detect_stall_onsets(&small_onset_keys(), &feat, &config);
        assert!(
            onsets_blocked.is_empty(),
            "標本 2 件は warmup_count=3 に届かないので onset を立てないはず"
        );
    }

    /// AC10 (不応期): `navigation` だけが続く長い停滞では onset は 1 回しか立たず、
    /// 条件 A が実際の産出キーで一度 `false` に戻れば 2 回目の onset が立つ。
    #[test]
    fn refractory_one_onset_per_rise() {
        let config = StallOnsetConfig::default();
        let mut keys = small_onset_keys(); // 0, 100, 200
                                           // navigation キー (net に寄与しない) を長い沈黙の途中に挟む。
        keys.push(KeyPress {
            timestamp: 35_000,
            vk: 0x25, // navigation, どちらでもない
        });
        keys.push(KeyPress {
            timestamp: 40_000,
            vk: 0x25,
        });
        keys.push(KeyPress {
            timestamp: 45_000,
            vk: 0x25,
        });
        // 実際の産出キーを 1 つ挟んで条件 A を一度 false に戻す。
        keys.push(key(100_000));

        let feat = feat_ts_range(0, 190_000, 1_000);
        let onsets = detect_stall_onsets(&keys, &feat, &config);
        assert_eq!(
            onsets.len(),
            2,
            "navigation キーだけの沈黙では 2 回目の onset が立たず (不応期)、\
             実際の産出キーで条件 A が false に戻った後だけ 2 つ目が立つ: {onsets:?}"
        );
        assert_eq!(onsets[0].s_ms, 30_200);
        assert_eq!(
            onsets[1].s_ms, 130_000,
            "2 つ目の立ち上がりは実キー(100000)の窓が抜けた時刻"
        );
    }

    /// AC11: `t0` より前 (`(s, t0]` の間) に文字キーが来たら、その onset は確定しない。
    #[test]
    fn production_before_t0_cancels_onset() {
        let config = StallOnsetConfig::default();
        let feat = feat_ts_range(0, 91_000, 1_000);

        // 対照: 何も挟まなければ s=30200 → t0=30300 で確定する。
        let baseline = detect_stall_onsets(&small_onset_keys(), &feat, &config);
        assert_eq!(baseline.len(), 1);
        assert_eq!(baseline[0].s_ms, 30_200);

        // s (30200) と t0 (30300) の間 (30250) に文字キーを挟むと、その onset は確定しない。
        let mut keys = small_onset_keys();
        keys.push(key(30_250));
        let onsets = detect_stall_onsets(&keys, &feat, &config);
        assert!(
            onsets.iter().all(|ev| ev.s_ms != 30_200),
            "s=30200 の onset は t0 到達前の産出キーで取り消されるべき: {onsets:?}"
        );
    }

    /// AC12: `q` を実際に使っている —— 標本 101 件以上なら θ は最大値と一致しない。
    #[test]
    fn quantile_uses_q_not_max() {
        let mut ts: Vec<u64> = (0..=100).collect(); // 100 個の gap=1ms
        ts.push(100_100); // 101 個目の gap = 100000ms (突出した外れ値)
        let s = *ts.last().unwrap();
        let theta = theta_person_from_gaps(&gaps_from_presses(&ts), s, 0.99, None);
        assert_eq!(
            theta,
            Some(1),
            "n=101 では q=0.99 (nearest-rank) は最大値 (100000) でなく 100 番目 (1ms) を選ぶ"
        );
    }

    /// AC13 (prefix 安定性): 入力 (key と feat) を任意の時刻 `c` (★ 全 key 時刻で切る) で
    /// 切ったとき、`c` 以下の最後の feat 行を `b'` として、`t0 <= b'` の onset の集合が
    /// 元の入力と一致する。
    #[test]
    fn prefix_stable_at_every_cut() {
        let config = StallOnsetConfig::default();
        let mut keys = small_onset_keys();
        keys.push(KeyPress {
            timestamp: 35_000,
            vk: 0x25,
        });
        keys.push(KeyPress {
            timestamp: 40_000,
            vk: 0x25,
        });
        keys.push(KeyPress {
            timestamp: 45_000,
            vk: 0x25,
        });
        keys.push(key(100_000));
        let feat = feat_ts_range(0, 190_000, 1_000);

        let full = detect_stall_onsets(&keys, &feat, &config);
        assert_eq!(full.len(), 2, "前提: 全区間では onset が 2 つ");

        let mut key_times: Vec<u64> = keys.iter().map(|k| k.timestamp).collect();
        key_times.sort_unstable();
        key_times.dedup();

        for &c in &key_times {
            let cut_keys: Vec<KeyPress> =
                keys.iter().copied().filter(|k| k.timestamp <= c).collect();
            let cut_feat: Vec<u64> = feat.iter().copied().filter(|&t| t <= c).collect();
            let Some(&b_prime) = cut_feat.iter().max() else {
                continue;
            };
            let cut_onsets = detect_stall_onsets(&cut_keys, &cut_feat, &config);

            let expected: Vec<&OnsetEvent> = full.iter().filter(|ev| ev.t0_ms <= b_prime).collect();
            let actual: Vec<&OnsetEvent> =
                cut_onsets.iter().filter(|ev| ev.t0_ms <= b_prime).collect();
            assert_eq!(
                actual.len(),
                expected.len(),
                "c={c} で t0<=b'={b_prime} の onset 数が元と一致しない: actual={actual:?} expected={expected:?}"
            );
            for (a, e) in actual.iter().zip(expected.iter()) {
                assert_eq!(a.s_ms, e.s_ms, "c={c}");
                assert_eq!(a.t0_ms, e.t0_ms, "c={c}");
                assert_eq!(a.theta_person_ms, e.theta_person_ms, "c={c}");
            }
        }
    }

    /// AC14: onset はちょうど `t0` を含む tick に載る (`t_ms <= t0 < t_ms + tick`)。
    #[test]
    fn onset_is_attributed_to_the_t0_tick() {
        let config = StallOnsetConfig::default();
        let feat = feat_ts_range(0, 31_000, 1_000);
        let column = stall_onset_column(
            &small_onset_keys(),
            &feat,
            &[],
            40,
            0,
            ENGINE_TICK_MS,
            &config,
        );
        let idx = column
            .iter()
            .position(|r| r.is_onset)
            .expect("onset should fire");
        let t0 = column[idx].t0_ms.expect("onset row has t0");
        let t_ms = idx as u64 * ENGINE_TICK_MS; // grid_origin=0
        assert!(t_ms <= t0 && t0 < t_ms + ENGINE_TICK_MS);
    }

    /// AC15: 同じ tick に 2 つ目の onset が落ちても上書きせず、先に確定した onset を残す。
    /// ★ 検出アルゴリズムから独立に、tick 写像だけを検査する
    /// (自然な入力では `W` の下限により同一 tick 衝突がほぼ起こらないため、合成 `OnsetEvent`
    /// で構造だけを固定する)。
    #[test]
    fn same_tick_collision_keeps_the_first() {
        let earlier = OnsetEvent {
            s_ms: 1_000,
            t0_ms: 5_500,
            theta_person_ms: 4_500,
        };
        let later = OnsetEvent {
            s_ms: 2_000,
            t0_ms: 5_800, // earlier と同じ tick (5000..6000)
            theta_person_ms: 3_800,
        };
        let column = column_from_onsets(&[earlier, later], &[], 10, 0, 1000);
        assert!(column[5].is_onset);
        assert_eq!(column[5].t0_ms, Some(5_500), "先に確定した onset を残す");
        assert_eq!(column[5].s_ms, Some(1_000));
    }

    /// AC16: `u64` 上限付近の時刻で panic しない (加算オーバーフローを `checked_add` で防ぐ)。
    #[test]
    fn timestamp_near_u64_max_does_not_panic() {
        let config = StallOnsetConfig::default();
        let near_max = u64::MAX - 100;
        let keys = vec![key(near_max), key(near_max + 50)];
        let feat = vec![near_max, near_max + 50, u64::MAX];

        // panic しないことだけを確認する (結果の中身は問わない: W を足すと u64::MAX を
        // 越えるので、この観測区間は評価不能になり onset は立たないのが正しい)。
        let onsets = detect_stall_onsets(&keys, &feat, &config);
        assert!(onsets.is_empty());
        let _ = stall_onset_column(&keys, &feat, &[], 5, near_max, 1000, &config);
    }
}
