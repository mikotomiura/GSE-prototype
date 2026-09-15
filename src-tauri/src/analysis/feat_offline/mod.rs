//! `gse-replay --features` の計算本体 (ADR-030 D1: 検出器はオフライン側に置く)。
//!
//! セッション NDJSON から再構成した press/paste イベント列を、既存 `loop_step`
//! と同じ 1 Hz グリッド (`ENGINE_TICK_MS` 相当) で tick に分割し、Tier ごとの
//! 特徴行 [`FeatureRow`] を作る。**`features.rs` / `engine.rs` を変更しない**
//! (D1 逐語「検出器はオフライン側に置く」) —— 数値も `features.rs` の既存
//! パラメータ (`PAUSE_THRESHOLD_MS`) を `use` するだけで、新しい定数は作らない
//! (ADR-030 D3 逐語「新しい定数を作らず、既存パラメータを対称に再利用する」)。
//!
//! # tick への帰属規則 (SSOT はここ)
//!
//! - tick 幅は [`ENGINE_TICK_MS`] (= 1000ms・`loop_step` の 1 Hz グリッドの SSOT)。
//!   tick `k` は区間 `[grid_origin_ms + k*ENGINE_TICK_MS, grid_origin_ms + (k+1)*ENGINE_TICK_MS)`
//!   を表す (左閉右開)。`grid_origin_ms` はセッション内の最初のイベント時刻
//!   (**全チャネル**= press / paste / `ime_shadow` の最小値)。
//!   ⚠️★★★ **グリッドは「打鍵だけ」ではなく入力チャネル全部を覆う。**
//!   ★ そうしないと、打鍵より前/後にある `ime_shadow` 行が tick 配列の範囲外になる。
//!   ⚠️ **副作用を承知して使うこと** (2026-09-15・`code-reviewer` MEDIUM・実測):
//!   同じ打鍵列でも **`ime_shadow` 行が 1 本あるかどうかで原点が動き、全行の `t_ms` がずれる**
//!   (実測では 100ms シフトした)。★ `ime_shadow` は `config_gated` (環境によって丸ごと出ない) なので、
//!   **同じセッションを計器条件の違う環境で解析すると tick 割りが揃わない**。
//!   → ★ 複数セッション/複数端末の行を突き合わせるときは `t_ms` の絶対値で join し、
//!   **tick の添字で揃えない**こと。回帰は
//!   `bin/replay.rs` の `ime_shadow_events_reach_feature_rows_through_the_collector` が張る。
//!   ⚠️ 本モジュールは **1000 を再宣言しない** —— `loop_step::ENGINE_TICK_MS` を `use` する
//!   (ADR-030 D3 逐語「新しい定数を作らず、既存パラメータを対称に再利用する」)。
//! - ★ `t_ms` は **絶対 epoch ms** (`grid_origin_ms + k*ENGINE_TICK_MS`) である。
//!   ⚠️ セッション相対オフセットにしない —— `FeatSnapshot::timestamp` /
//!   `metrics::StuckEpisode` / `--metrics` 系がすべて epoch 軸なので、
//!   相対にすると **判断 2 の「episode への集約は後から join する形で足せる」が
//!   この出力単体では成立しなくなる** (原点が行に載らないため)。
//!   ⚠️ ただし本モジュールは production のゲート状態を再現するものではなく、
//!   オフライン一括計算専用である (`loop_step` の `now_ms` の刻みとは別物)。
//! - **打鍵 (`keys` / `deletes`)** は press 時刻がその tick 区間に入るものを計上する。
//! - **paste (`pastes`)** も同様に paste 時刻がその tick 区間に入るものを計上する。
//! - **打鍵間隔由来の値 (`mean_iki_ms` / `pauses`)** は、連続する press ペアの
//!   間隔を「2 打目 (再開する側) の press が属する tick」に帰属させる
//!   (`features.rs` の F5/F6 が同じペア窓で「後続イベント側」を見ているのと対称)。
//!   ⚠️ したがって tick 境界をまたぐ間隔は、間隔の開始ではなく終了側の tick に乗る。
//!   ⚠️ セッション末尾が pause のまま閉じずに終わる場合 (最後の press の後ろに
//!   何も続かない)、その末尾の沈黙は「組」にならないため計上しない
//!   (未来の press が来て初めて間隔が確定する設計)。
//!
//! # 欠測の表現
//!
//! `mean_iki_ms` は間隔が 1 件も無い tick (press が 0 or 1 件) では `null`
//! (`Option::None`) を出す。**`0.0` にフォールバックしない** — 「間隔が無い」と
//! 「間隔が 0ms だった (同時刻打鍵)」を区別する。他の 5 フィールドは常に計上可能
//! (最小値 0) なので `Option` を使わない。
//!
//! # Tier ごとの causal / retrospective の区分
//!
//! `T0` (activity) は **causal**: 各 tick の値は、その tick が閉じた時点までに
//! 実際に発生した入力だけを集計したものであり、セッション全体を見てから遡って
//! 付け直すラベルを一切含まない。将来追加する Tier (`T1a` の個人相対 surprise 等)
//! が **retrospective** (セッション全体の分布を要する事後ラベル) を持ち込む場合は、
//! `FeatureRow` の中でも causal な `T0` と混ぜず、別フィールド/別ドキュメントコメントで
//! 明示すること (「その時点で既知」と「後から付けたラベル」を tick 行の中で混ぜない)。

pub mod activity;
pub mod boundary;

pub use activity::T0Activity;
pub use boundary::{Boundary, ImeShadowEvent};

use crate::analysis::loop_step::ENGINE_TICK_MS;
use crate::analysis::metrics::{is_backspace, is_text_producing, KeyPress};

/// 1 tick ぶんの特徴行。`activity` は `T0` (Tier 0)、`boundary` は `T1b` (境界)。
#[derive(Debug, Clone, serde::Serialize)]
pub struct FeatureRow {
    /// tick 開始時刻 (**絶対 epoch ms**)。モジュール doc の「tick への帰属規則」参照。
    pub t_ms: u64,
    pub activity: T0Activity,
    pub boundary: Boundary,
}

/// 連続する press 間の間隔 1 件。`resuming_ts` はその間隔を終える (2 打目の) press 時刻。
#[derive(Debug, Clone, Copy)]
struct PressInterval {
    resuming_ts: u64,
    gap_ms: u64,
}

/// press 時刻列 (任意順でよい) から連続間隔の列を作る内部ヘルパ。
/// 昇順ソート後に `windows(2)` を取るため、入力の行順 (=時刻逆行を含む NDJSON) に依らない。
fn press_intervals(press_ts: &[u64]) -> Vec<PressInterval> {
    let mut sorted: Vec<u64> = press_ts.to_vec();
    sorted.sort_unstable();
    sorted
        .windows(2)
        .map(|w| PressInterval {
            resuming_ts: w[1],
            gap_ms: w[1].saturating_sub(w[0]),
        })
        .collect()
}

/// ★ 共有ヘルパ: 「単純 pause」(連続する press の間隔が `features.rs::PAUSE_THRESHOLD_MS`
/// 以上) を抽出し、pause を終える (再開する) press 時刻の列を返す。
///
/// 後続 issue (T1c/T1d/stall onset 等) はこの関数を再利用し、独自の pause 定義を
/// 作らないこと (Codex TASK-PRE 指摘 5)。値は `features.rs::PAUSE_THRESHOLD_MS`
/// を `use` するのみで、ここでは 1 つも数値を導入しない。
///
/// ⚠️★★★ **issue 005 (`stall onset`) がそのまま条件 B に使える関数ではない** ——
/// ★ 本関数が見るのは **press ペアの間隔**だけである。
/// 1. ⚠️ **閉じない末尾の沈黙を返さない** (再開する 2 打目が無いと「組」にならない)。
///    ADR-030 D3 は逐語「**沈黙こそ最長の停滞である**」として評価時刻に
///    `{key の t + W}` を含めるので、**005 はそこを自前で補う必要がある**。
/// 2. ⚠️ **`feat` 行の穴 (削除区間・一時停止・計器欠損) を知らない** ——
///    ADR-030 D8 (b-2) は原因を問わず穴で条件 B の連続を切ることを要求する。
///    ★ 本関数を素通しで使うと **被験者が削除を求めた位置に必ず onset が立つ**。
///    ⚠️ ただし**原因ラベルを作る方向で直さないこと** (`redaction.rs` の約束「何を消したかは
///    書かない」・ADR-030 却下リスト 9)。穴の**有無**だけを 005 側で見る。
pub fn extract_pause_resumptions(press_ts: &[u64]) -> Vec<u64> {
    use crate::analysis::features::PAUSE_THRESHOLD_MS;
    press_intervals(press_ts)
        .into_iter()
        .filter(|iv| iv.gap_ms >= PAUSE_THRESHOLD_MS)
        .map(|iv| iv.resuming_ts)
        .collect()
}

/// キー 1 件ぶんの net production 寄与 (+1 挿入 / -1 削除 / 0 その他)。
fn key_net_delta(k: &KeyPress) -> i64 {
    if is_backspace(k.vk) {
        -1
    } else if is_text_producing(k.vk) {
        1
    } else {
        0
    }
}

/// ★ 共有ヘルパ: net production = 文字生成キー press 数 − backspace/delete press 数
/// (挿入系 − 削除系。`metrics::is_text_producing` / `metrics::is_backspace` を再利用し、
/// 新しい文字分類を作らない)。削除超過の tick では負になりうる (符号付き)。
pub fn net_production(keys: &[KeyPress]) -> i64 {
    keys.iter().map(key_net_delta).sum()
}

/// tick ループ: press/paste 列から 1 Hz tick 単位の [`FeatureRow`] 列を作る。
///
/// `keys` は `bin/replay.rs` の `collect_key_events` が返す形式、`paste_ts` は
/// **すべての paste 行の時刻**(⚠️ 文字数が欠落した行も含む。`T0` は件数のみ扱うため)。
/// どちらも timestamp 昇順ソート済みを仮定しないが、内部で扱いを吸収する。
/// 空入力 (打鍵も paste も無い) では空の `Vec` を返す (境界入力: 空ログ)。
///
/// ⚠️★★★ **`max_ticks` は呼び出し側が渡す** —— tick 数は**入力のバイト数ではなく
/// 時刻スパンに比例する**ので、`MAX_SESSION_BYTES` では抑えられない。
/// ★ 実測 (2026-09-15): **251 バイト・2 行**の NDJSON に `t=0` と `t=1e8` を並べるだけで
/// **100,001 行**が出る。ADR-030 **D9**「壁時計の前方跳躍」は実際に起こりうるので、
/// 巨大ギャップは**黙って潰さず** `Err` で止める (⚠️ `saturating_sub` で吸収すると
/// D9 の危険側に落ちる)。★ 上限値そのものは `bin/replay.rs` が所有する
/// (⚠️ 本モジュールに新しい数値定数を置かないため・AC 6)。
pub fn build_feature_rows(
    keys: &[KeyPress],
    paste_ts: &[u64],
    ime_events: &[ImeShadowEvent],
    max_ticks: usize,
) -> Result<Vec<FeatureRow>, String> {
    if keys.is_empty() && paste_ts.is_empty() && ime_events.is_empty() {
        return Ok(Vec::new());
    }

    let key_ts = keys.iter().map(|k| k.timestamp);
    let paste_ts_iter = paste_ts.iter().copied();
    let ime_ts_iter = ime_events.iter().map(|e| e.t_ms);
    // unwrap: 上の early-return で空入力を排除済みなので、少なくとも1件は必ずある。
    let grid_origin_ms = key_ts
        .clone()
        .chain(paste_ts_iter.clone())
        .chain(ime_ts_iter.clone())
        .min()
        .unwrap();
    let t_last = key_ts
        .chain(paste_ts_iter)
        .chain(ime_ts_iter)
        .max()
        .unwrap();

    let tick_of =
        |t: u64| -> usize { (t.saturating_sub(grid_origin_ms) / ENGINE_TICK_MS) as usize };
    let tick_count = tick_of(t_last) + 1;
    if tick_count > max_ticks {
        return Err(format!(
            "time span too large: {} ticks exceeds limit {} ticks \
             (first event {} ms, last event {} ms). \
             The log likely contains a wall-clock jump or concatenated sessions (ADR-030 D9).",
            tick_count, max_ticks, grid_origin_ms, t_last
        ));
    }

    let mut keys_by_tick: Vec<Vec<KeyPress>> = vec![Vec::new(); tick_count];
    for k in keys {
        keys_by_tick[tick_of(k.timestamp)].push(*k);
    }
    let mut paste_counts: Vec<u64> = vec![0; tick_count];
    for t in paste_ts {
        paste_counts[tick_of(*t)] += 1;
    }

    let all_press_ts: Vec<u64> = keys.iter().map(|k| k.timestamp).collect();

    let mut iki_ms_by_tick: Vec<Vec<u64>> = vec![Vec::new(); tick_count];
    for iv in press_intervals(&all_press_ts) {
        iki_ms_by_tick[tick_of(iv.resuming_ts)].push(iv.gap_ms);
    }

    let mut pause_count_by_tick: Vec<u64> = vec![0; tick_count];
    for resuming_ts in extract_pause_resumptions(&all_press_ts) {
        pause_count_by_tick[tick_of(resuming_ts)] += 1;
    }

    let mut ime_by_tick: Vec<Vec<ImeShadowEvent>> = vec![Vec::new(); tick_count];
    for ev in ime_events {
        ime_by_tick[tick_of(ev.t_ms)].push(*ev);
    }
    let mut boundary_pairs_by_tick: Vec<Vec<boundary::PauseBoundaryPair>> =
        vec![Vec::new(); tick_count];
    for pair in boundary::pause_boundary_pairs(keys) {
        boundary_pairs_by_tick[tick_of(pair.resuming_ts)].push(pair);
    }

    Ok((0..tick_count)
        .map(|idx| FeatureRow {
            t_ms: grid_origin_ms + idx as u64 * ENGINE_TICK_MS,
            activity: activity::compute_t0_activity(
                &keys_by_tick[idx],
                paste_counts[idx],
                &iki_ms_by_tick[idx],
                pause_count_by_tick[idx],
            ),
            boundary: boundary::compute_boundary(
                &keys_by_tick[idx],
                &boundary_pairs_by_tick[idx],
                &ime_by_tick[idx],
            ),
        })
        .collect())
}

#[cfg(test)]
mod tests {
    use super::*;

    fn key_at(ms: u64) -> KeyPress {
        KeyPress {
            timestamp: ms,
            vk: 0x41, // 'A' — text-producing
        }
    }

    /// テストの既定上限。実運用の値は `bin/replay.rs::MAX_FEATURE_TICKS` が所有する。
    const TEST_MAX_TICKS: usize = 10_000;

    fn rows_of(keys: &[KeyPress], paste_ts: &[u64]) -> Vec<FeatureRow> {
        build_feature_rows(keys, paste_ts, &[], TEST_MAX_TICKS).expect("within tick limit")
    }

    /// 境界入力で `build_feature_rows` が panic しないことを確認する (AC10)。
    #[test]
    fn tick_loop_handles_degenerate_inputs() {
        // 空ログ
        assert!(rows_of(&[], &[]).is_empty());

        // 単一 key 行
        let rows = rows_of(&[key_at(0)], &[]);
        assert_eq!(rows.len(), 1);
        assert_eq!(rows[0].activity.keys, 1);
        assert_eq!(rows[0].activity.mean_iki_ms, None);

        // 同一 timestamp の多発
        let same_ts = vec![key_at(500), key_at(500), key_at(500)];
        let rows = rows_of(&same_ts, &[]);
        assert_eq!(rows.len(), 1);
        assert_eq!(rows[0].activity.keys, 3);
        // 間隔 0ms が2件 → 平均0、pause にはならない
        assert_eq!(rows[0].activity.mean_iki_ms, Some(0.0));
        assert_eq!(rows[0].activity.pauses, 0);

        // 時刻逆行 (入力順が時刻降順) でも panic せず、昇順として扱われる
        let reversed = vec![key_at(3000), key_at(1000), key_at(0)];
        let rows = rows_of(&reversed, &[]);
        assert_eq!(rows.len(), 4); // ticks 0..=3 (origin=0, t_last=3000)
        let total_keys: u64 = rows.iter().map(|r| r.activity.keys).sum();
        assert_eq!(total_keys, 3);

        // tick 境界ちょうどの打鍵 (0, 1000, 2000 の3点)
        let boundary = vec![key_at(0), key_at(1000), key_at(2000)];
        let rows = rows_of(&boundary, &[]);
        assert_eq!(rows.len(), 3);
        assert_eq!(rows[0].activity.keys, 1);
        assert_eq!(rows[1].activity.keys, 1);
        assert_eq!(rows[2].activity.keys, 1);

        // 最後の pause が閉じないまま終わるログ: 3000ms 空けて終了しても pause は計上されない
        // (再開する2打目が無いため)
        let unclosed = vec![key_at(0), key_at(100)];
        let rows = rows_of(&unclosed, &[]);
        let total_pauses: u64 = rows.iter().map(|r| r.activity.pauses).sum();
        assert_eq!(total_pauses, 0);

        // paste だけの入力 (keys が空) —— tick グリッドは paste 時刻からも張られる
        let rows = rows_of(&[], &[0, 2500]);
        assert_eq!(rows.len(), 3);
        assert_eq!(rows[0].activity.pastes, 1);
        assert_eq!(rows[2].activity.pastes, 1);
        assert_eq!(rows[0].activity.keys, 0);
    }

    /// ⚠️★★★ 時刻スパンに比例した確保を上限で止める (2026-09-15・レビュー HIGH)。
    /// ★ 入力は 2 件でも、時刻差が大きければ tick 数は跳ね上がる。
    #[test]
    fn tick_loop_rejects_time_span_beyond_limit() {
        // 0ms と 1,000,000ms → tick 0..=1000 の 1001 tick が要る
        let huge = vec![key_at(0), key_at(1_000_000)];
        assert!(build_feature_rows(&huge, &[], &[], 1001).is_ok());
        let err = build_feature_rows(&huge, &[], &[], 1000).expect_err("上限超過は Err");
        assert!(err.contains("time span too large"), "err = {}", err);
    }

    /// ★ `t_ms` が**絶対 epoch ms** であること (⚠️ セッション相対にしない)。
    #[test]
    fn t_ms_is_absolute_epoch_not_session_relative() {
        let epoch = 1_700_000_000_000_u64;
        let rows = rows_of(&[key_at(epoch), key_at(epoch + 1500)], &[]);
        assert_eq!(rows.len(), 2);
        assert_eq!(rows[0].t_ms, epoch);
        assert_eq!(rows[1].t_ms, epoch + ENGINE_TICK_MS);
    }

    /// ★ 中心規則: tick 境界をまたぐ間隔は**終了側 (再開側) の tick** に乗る。
    #[test]
    fn interval_is_attributed_to_the_resuming_tick() {
        // ⚠️ グリッド原点は**最初のイベント時刻**なので、0ms から張って境界をまたがせる。
        // 0 / 900 / 1100 → 間隔 900ms は tick 0、tick 境界をまたぐ 200ms は tick 1 (= 再開側)。
        let rows = rows_of(&[key_at(0), key_at(900), key_at(1100)], &[]);
        assert_eq!(rows.len(), 2);
        assert_eq!(rows[0].activity.mean_iki_ms, Some(900.0));
        assert_eq!(rows[1].activity.mean_iki_ms, Some(200.0));

        // 0ms と 2500ms の 2 打 → pause は再開側の tick 2 に 1 件
        let rows = rows_of(&[key_at(0), key_at(2500)], &[]);
        assert_eq!(rows.len(), 3);
        assert_eq!(rows[0].activity.pauses, 0);
        assert_eq!(rows[2].activity.pauses, 1);
    }

    #[test]
    fn extract_pause_resumptions_uses_ssot_threshold() {
        use crate::analysis::features::PAUSE_THRESHOLD_MS;
        let press_ts = vec![0, PAUSE_THRESHOLD_MS, PAUSE_THRESHOLD_MS + 500];
        let resumptions = extract_pause_resumptions(&press_ts);
        // 0 -> PAUSE_THRESHOLD_MS は閾値ちょうどで pause、続く +500 は pause でない
        assert_eq!(resumptions, vec![PAUSE_THRESHOLD_MS]);
    }

    #[test]
    fn net_production_counts_insert_minus_delete() {
        let backspace = KeyPress {
            timestamp: 0,
            vk: 0x08,
        };
        let letter = KeyPress {
            timestamp: 1,
            vk: 0x41,
        };
        let arrow = KeyPress {
            timestamp: 2,
            vk: 0x25, // navigation, どちらでもない
        };
        assert_eq!(net_production(&[letter, letter, backspace]), 1);
        assert_eq!(net_production(&[backspace, backspace]), -2);
        assert_eq!(net_production(&[arrow]), 0);
    }
}
