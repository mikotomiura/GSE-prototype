//! `stall onset`（`t0`）検出器（ADR-030 D2 / D3 / D4 / D5 / D6 / D8 (b-2)）。
//!
//! **causal（`key` 行について、`super` のモジュール doc の区分に従う）**: 各時刻の判定は、
//! その時刻までに実際に発生した `key` 行だけから決まる。未来の `key` 行を 1 行も参照しない
//! (`tests::no_lookahead_in_net` / `tests::no_lookahead_in_theta` が条件 A の産出 (net) と
//! θ の標本のそれぞれで個別に固定する。`tests::prefix_stable_at_every_cut` は入力を
//! 任意の時刻で切っても、切った時刻以前に確定する onset の集合が変わらないことを
//! 全体として固定する)。
//!
//! ⚠️ **`feat` 行は先読みする** —— ただし内容は読まず (D3 逐語「使ってよいのは feat 行の
//! *存在* だけ」)、観測区間の右端 `b`（`t0 <= b` の確定）を決めるためだけに使う。区間が
//! そこで終わるか続くかを判定するには、構造上「最大 `hole_gap_ms` 程度先」の `feat` 行の
//! **存在**を見る必要がある (`observed_intervals` 参照)。
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
//! (issue 008 「規範となる定義」の θ 標本節の逐語 ＋ `decisions.md` 判断 18 の正解表で確定。
//! 「確定」節の「`s` **と同じ**観測区間の右端 `b`」は `t0` の上限にだけ使う別の制約であり、
//! 混同しない)。
//!
//! # 実装が一意に決まらなかった箇所（★ 推測せず、ここに明記する）
//!
//! - **`W` / `q` / `B` / `hole_gap_ms` / `warmup_count` の値**: ADR-030 D4 は「決め方」だけを
//!   凍結し、値は P1 前の事前宣言に委ねている。`w_ms` / `b_ms` は既存
//!   `OutcomeConfig::merge_gap_ms` から借りたプレースホルダ、`warmup_count` は `None`
//!   （無効化）のままである —— **値そのものを決めたわけではない** (`blockers.md` 起票 14)。
//!   `hole_gap_ms` は `2 * ENGINE_TICK_MS`（1Hz の予定行が少なくとも 1 本欠けたと言える
//!   構造的な下限）から借りたプレースホルダであり、同じく値を決めたわけではない
//!   (`blockers.md` 起票 15)。
//! - **分位点の推定法**（D4 点 3「nearest-rank か線形補間かを事前宣言する」）: 本モジュールは
//!   **nearest-rank**（`dispersion.rs::quantile` と同じ規約）を採用した。線形補間との差は
//!   小標本で顕在化しうるので、P1 の事前宣言で確定させること。
//! - **修飾キー押下中の文字キー除外**（D3）: `KeyCategory::Modifier` は Shift を含むため、
//!   逐語どおり実装すると大文字・記号の入力まで産出から外れる。★ **それが極 M+ の定義である**
//!   (ADR-030 補訂 1 項目 3)。極 M− (baseline) は除外しない。実装は [`Pole::ModifierMPlus`] /
//!   [`modifier_press_intervals`] / [`apply_modifier_m_plus`] (issue 005)。
//! - **IME 変換中の抑制**（D3 抑制表 2 行目）: 区間の定義と「抑制」の意味が未確定。
//!   研究者判断待ち (`blockers.md` 起票 12)。
//! - **ポインタ活動の両極**（D3 抑制表 3 行目）: 出力の形は**別モード (`--pole`・1 実行 1 極)** に
//!   裁定済み (`decisions.md` 判断 3・[`Pole`])。極 B は**観測区間と同じ構造で切る**と裁定済みで
//!   (判断 7)、実装は [`pointer_suppression_intervals`] / [`evaluation_intervals`] (issue 006)。
//!
//! # 極 B の入れ方（issue 006）
//!
//! ★ 検出の**中には極の分岐を持たない**。極 B は検出へ渡す**評価区間の側**で表す: `pointer_bin` 行が覆う
//! 秒の極大連続を**抑制区間**とし、観測区間から抑制区間を除いた各片を 1 つの観測区間として検出へ渡す
//! ([`evaluation_intervals`])。→ 各片で (1) 条件 A の直前状態が `false` に戻り (2) 頭の `W` を評価せず
//! (3) θ の標本も**片の内側の隣接 press 対だけ**になる —— **新しい機構は 1 つも無い**
//! (観測区間と同じ規則をそのまま再利用する)。
//! ⚠️ **onset が増えることもある**: 長い沈黙の途中にポインタ活動が入ると、片が 2 つに割れて
//! 後ろの片で `a + W` 後に条件 A が改めて立つ (`feat` 行の穴と同じ扱い)。極 B が baseline の
//! 部分集合になるとは**限らない** (活動が停滞の途中で止めさせる典型形では減る)。
//!
//! # 極 M+ の入れ方（issue 005）
//!
//! ★ 検出 (条件 A / B・θ) の**中には極の分岐を持たない**。極 M+ は**検出へ渡す `key` 列の側**で
//! 「修飾キーの押下区間の中の挿入系 press」を修飾キーの VK へ置き換えて表す ([`apply_modifier_m_plus`])。
//! ⚠️ press の**時刻は 1 本も変えない** —— θ の標本 (隣接 press の間隔) は極に依らず、
//! 変わるのは条件 A の産出 (`net`) の**挿入系の側だけ**である (`−1` の削除系は外さない)。
//! - **`phase`**: 構造化セッションの block id は未実装。自然セッション (O1) では常に
//!   `"unspecified"` に collapse する (ADR-030 D5)。

use crate::analysis::anonymize::KeyCategory;
use crate::analysis::loop_step::ENGINE_TICK_MS;
use crate::analysis::metrics::{KeyPress, OutcomeConfig};

/// ADR-030 D3 の「極」—— 抑制規則の置き方を名前で区別する。
///
/// ⚠️★★★ **enum である**ことが、極を掛け合わせた直積を**構造的に作れなくする**
/// (ADR-030 D3 の囲みの要約: 極は他の極と直積に組まず、独立に報告する ——
/// ⚠️ 原文は ADR-030 D3 を参照。ここに逐語で写さない (code-reviewer MEDIUM・2026-09-25)。理由: 掛け算で組むと
/// 極の数が増えて幅が解釈不能になる)。→ **1 実行 1 極**で、出す組は次の 3 つだけ
/// (`decisions.md` 判断 3):
///
/// | 名前 | ポインタ | 修飾キー | 実装 |
/// |---|---|---|---|
/// | `baseline` | 極 A (抑制しない) | 極 M− (規則なし) | ★ 現行の計算そのもの |
/// | `pointer_b` | 極 B (ポインタ活動区間を抑制) | 極 M− | ★ 実装済み (issue 006) |
/// | `modifier_m_plus` | 極 A | 極 M+ (押下区間中の文字キーを挿入系に数えない) | ★ 実装済み (issue 005) |
///
/// ⚠️ 極は `--set` で変える 8 値 (`StallOnsetConfig` の他のフィールド) とは**別の軸**であり、
/// `--set` の対象にしない (CLI は `--pole` だけが持つ)。
#[derive(Debug, Clone, Copy, PartialEq, Eq, Default)]
pub enum Pole {
    #[default]
    Baseline,
    PointerB,
    ModifierMPlus,
}

impl Pole {
    /// 全ての極 (定義順)。
    pub const ALL: [Pole; 3] = [Pole::Baseline, Pole::PointerB, Pole::ModifierMPlus];

    /// CLI (`--pole`) と封筒 `config.pole` に出す名前。
    pub const fn as_str(self) -> &'static str {
        match self {
            Pole::Baseline => "baseline",
            Pole::PointerB => "pointer_b",
            Pole::ModifierMPlus => "modifier_m_plus",
        }
    }

    /// [`Self::as_str`] の逆。⚠️ 未知の名前は `None` (近い名前へ丸めない)。
    pub fn from_name(name: &str) -> Option<Self> {
        Self::ALL.into_iter().find(|p| p.as_str() == name)
    }

    /// 中身が実装済みの極か。
    ///
    /// ⚠️★★★ **`false` の極を黙って `baseline` の値で返してはならない** —— 出力が嘘をつき、
    /// 極の比較が無意味になる。呼び出し側 (`build_feature_rows` / CLI) は `false` なら**止める**
    /// (fail-closed)。★ issue 005 / 006 がそれぞれ 1 極ずつここを `true` にして開通させた
    /// (★ 極 M+ は issue 005・極 B は issue 006)。今は全部 `true` だが、極を足したときの
    /// 門としてこの関数と網羅 `match` を残す。
    pub const fn is_implemented(self) -> bool {
        match self {
            Pole::Baseline | Pole::PointerB | Pole::ModifierMPlus => true,
        }
    }
}

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
    /// 観測区間を切る閾値 (ms、ADR-030 D8 (b-2))。隣接する `feat` 行の間隔が**これを超えたら**
    /// 区間を分ける（＝ ちょうど `hole_gap_ms` なら同じ区間のまま）。既定は 2 tick。
    /// ⚠️ 予定行が 1 本だけ欠けた場合 (差がちょうど 2 tick 前後) は、遅延による揺らぎと
    /// 本当の欠測を区別できない —— 切れるかどうかは揺らぎ次第になる。値そのものは
    /// 事前宣言事項 (`blockers.md` 起票 15)。
    pub hole_gap_ms: u64,
    /// θ の標本数がこれ未満なら個人分位点を使わない (`None` を返す)。`None` は無効化
    /// (下限を課さない) を表す (ADR-030 D4 点 1)。
    pub warmup_count: Option<usize>,
    /// `T1a` の窓長 (ms・P1 事前宣言 §1 の `t1a_window_ms`)。
    /// ★ 本モジュールは `T1a` の窓を実装していない (issue 003) ため未使用。`b_ms` と同じく
    /// **設定の器だけ**を持ち、封筒 `config` に載せて値を再現可能にする。
    pub t1a_window_ms: u64,
    /// 極 (ADR-030 D3・[`Pole`])。既定は [`Pole::Baseline`] (現行の計算)。
    /// ⚠️ 他の 8 値と違い `--set` では変えられない (`bin/replay.rs` の `--pole` だけが持つ)。
    /// ★ 本モジュールの検出そのものは極を読まない —— 極 M+ は検出へ渡す `key` 列の側で表す
    /// ([`apply_modifier_m_plus`]・モジュール doc 「極 M+ の入れ方」)。未実装の極は
    /// `build_feature_rows` が入口で `Err` にするので、ここへは届かない ([`Pole::is_implemented`])。
    pub pole: Pole,
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
            t1a_window_ms: outcome.merge_gap_ms,
            pole: Pole::Baseline,
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
    /// `theta_person_ms` を算出した時点の標本数 `n` (`resuming_ts <= s` の隣接 press 対の数)。
    /// ★ `warmup_count` は `q` の従属変数 `ceil(1 / (1 - q))` なので、将来 `warmup_count` を
    /// 変えても**過去の出力を読み直せる**ようにするために行が持つ。
    /// ⚠️ `theta_person_ms` と同じく**設定ではなく結果** (ADR-030 D4) —— 封筒 `config` には入れない。
    /// `theta_person_ms` が非 `None` の行では必ず非 `None`、それ以外は `None`。
    pub theta_sample_n: Option<u64>,
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
            theta_sample_n: None,
            task_kind: None,
            phase: "unspecified".to_string(),
        }
    }
}

/// 確定した 1 つの `stall onset`（条件 A が `s` で立ち上がり、`θ_person` 継続して
/// `t0` で確定したもの）。
#[derive(Debug, Clone, Copy, PartialEq)]
pub(super) struct OnsetEvent {
    pub s_ms: u64,
    pub t0_ms: u64,
    pub theta_person_ms: u64,
    /// `theta_person_ms` を算出した時点の標本数 (`StallOnset::theta_sample_n` の元)。
    pub theta_sample_n: u64,
}

/// 観測区間 1 つぶんの条件 A の評価結果。
///
/// ⚠️★★★ **issue 006 (`T1d`) のために出している**（★ 判断 2 の **V2**）——
/// `restart` は「条件 A が `false` へ落ちる / `true` へ立ち上がる」辺を要するが、
/// 条件 A の評価は本モジュールの非公開関数にある。★ ここで出さないと
/// **`restart.rs` が条件 A を再実装することになり、定義が二重になる**
/// （Codex TASK-PRE 指摘 5 と同型）。
///
/// ★ `changes` は**変化点だけ**を持つ（先頭はこの区間の最初の評価時刻とその値）。
/// ⚠️ 条件 A は評価時刻の間で一定である（`net` が変わるのは `key の t` と `key の t + W` だけ）
/// ので、**この列だけで区間内の任意時刻の値を復元できる**（★ `t` 以下で最後の変化点を引く）。
#[derive(Debug, Clone)]
pub(super) struct ConditionAInterval {
    /// 観測区間の左端（ADR-030 D8 (b-2)）。
    pub a: u64,
    /// 観測区間の右端。⚠️ **右端ちょうどは確定扱い**（`t0 <= b` と対称・V2 の裁定）。
    pub b: u64,
    /// 条件 A の変化点 `(時刻, 値)`。時刻昇順・重複なし。値は必ず交互に変わる。
    pub changes: Vec<(u64, bool)>,
    /// この区間で確定した onset（`s` 昇順）。⚠️ **tick グリッドで捨てられた分も含む**
    /// （★ 集計窓の右端は「次に onset が立った事実」で決まるのであって、tick 割りの都合ではない）。
    pub onsets: Vec<OnsetEvent>,
}

/// nearest-rank 法で分位点を取る (`dispersion.rs::quantile` と同じ規約。線形補間なし。
/// `rank = ceil(q * n)`、1-indexed、`[1, n]` にクランプ)。★ このクランプは分位点の
/// **順位のインデックス範囲**を保証するものであり、ADR-030 D4 が禁じる θ_person への
/// 床/天井とは別物 (対象はインデックスであって θ_person の値ではない)。
/// `sorted_ascending` は昇順ソート済みを仮定する。要素 0 個なら `None`。
///
/// ⚠️ 本番経路 (`ThetaAccumulator::find_kth`) はこの規則を Fenwick 木上で独立に再実装して
/// いるため、本関数自体は呼ばない (issue 008 HIGH-1)。テストと素朴な参照実装専用。
#[cfg(test)]
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
///
/// ★ 2026-09-21 に `pub(super)` → `pub` へ広げた（★ 研究者判断・`blockers.md` 起票 20 (a)）——
/// `bin/replay.rs` が**封筒の `provenance.observed_intervals`** に載せるためである。
/// ⚠️ 新しい露出ではない: 穴の位置と長さは `rows[].quality.observability_mask.feat`
/// が既に tick ごとに出している（issue 007）。★ 封筒の列はその**再表現**であり、
/// 「どの行が観測区間のどこに居るか」を解析側が引けるようにするだけである。
pub fn observed_intervals(feat_ts: &[u64], hole_gap_ms: u64) -> Vec<(u64, u64)> {
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

/// `pointer_bin` の 1 ビンの幅 (ms)。★ 値は `input/observe_*.rs` の `BIN_MS` (= 1000・各 OS のテストが固定)。
///
/// ⚠️ `ENGINE_TICK_MS` (1 Hz の tick) と**同じ値だが別の事実**である —— 数値を再宣言しないために
/// ここへ束ねているだけで、`BIN_MS` が変わったらこの定数を**追随させる** (`decisions.md` 判断 7 の見直しタイミング)。
pub const POINTER_BIN_MS: u64 = ENGINE_TICK_MS;

/// 極 B: `pointer_bin` 行の時刻から**抑制区間**を作る (ADR-030 D3・`decisions.md` 判断 7)。
///
/// ★ 1 行 `t` が覆うのは `(t − bin_ms, t]` である (`analysis/pointer_bin.rs`: `timestamp` は**ビンの終端時刻**)。
/// ⚠️ ゼロ抑制なので**行が在る＝その秒に活動があった**。★ 行の**値は読まない** (存在だけを使う)。
/// 覆う区間の**極大連続**を 1 本に畳む: ちょうど `bin_ms` 離れた 2 行 `(t−bin, t]` と `(t, t+bin]` は接して 1 本になり、
/// それより離れた行は別の区間になる (整数 ms で 1 ms でも空けば別)。
///
/// 戻り値は `(下端を含まない, 上端を含む)` の組 (開始昇順・互いに素)。`pointer_ts` は順不同・重複ありでよい。
/// `bin_ms == 0` は覆う秒が無いので空 (⚠️ 空の区間で観測区間を割らない)。
pub fn pointer_suppression_intervals(pointer_ts: &[u64], bin_ms: u64) -> Vec<(u64, u64)> {
    if bin_ms == 0 {
        return Vec::new();
    }
    let mut sorted = pointer_ts.to_vec();
    sorted.sort_unstable();
    sorted.dedup();

    let mut out: Vec<(u64, u64)> = Vec::new();
    for t in sorted {
        let lo = t.saturating_sub(bin_ms);
        match out.last_mut() {
            // 前の区間の上端 (含む) に、この行の下端 (含まない) が届いていれば接している。
            Some(last) if lo <= last.1 => last.1 = t,
            _ => out.push((lo, t)),
        }
    }
    out
}

/// 観測区間から抑制区間を除いた**評価区間**を返す (両端を含む・開始昇順・互いに素)。
///
/// ★ 極 B が検出へ渡す区間である。**極 A (baseline) は抑制が空なので観測区間そのまま**が返る。
/// 観測区間 `[a, b]` から `(lo, hi]` を除くと `[.., lo]` と `[hi + 1, ..]` に割れる (整数 ms)。
/// ⚠️ 抑制が観測区間の外にあれば何も変わらない。⚠️ 抑制が区間全体を覆えば、その区間は消える。
/// `observed` / `suppressed` はどちらも開始昇順・互いに素 ([`observed_intervals`] /
/// [`pointer_suppression_intervals`] の戻り値) を仮定する。計算量は `O((I + S) + I log S)`。
pub fn evaluation_intervals(observed: &[(u64, u64)], suppressed: &[(u64, u64)]) -> Vec<(u64, u64)> {
    let mut out: Vec<(u64, u64)> = Vec::with_capacity(observed.len());
    for &(a, b) in observed {
        // この観測区間に届きうる最初の抑制 (上端が `a` 以上のもの)。
        let mut i = suppressed.partition_point(|&(_, hi)| hi < a);
        let mut cursor = a;
        while let Some(&(lo, hi)) = suppressed.get(i) {
            // 抑制は (lo, hi] = [lo + 1, hi]。`b` より後ろから始まるなら、以降は全部区間の外。
            if lo >= b {
                break;
            }
            if cursor <= lo {
                out.push((cursor, lo));
            }
            cursor = cursor.max(hi.saturating_add(1));
            i += 1;
        }
        if cursor <= b {
            out.push((cursor, b));
        }
    }
    out
}

/// [`modifier_press_intervals`] の結果。押下区間と、区間を作れなかった行の件数。
#[derive(Debug, Clone, PartialEq, Eq, Default)]
pub struct ModifierIntervals {
    /// 修飾キーの押下区間 `[開始, 終了]`（**両端を含む**）。開始昇順・互いに素。
    pub intervals: Vec<(u64, u64)>,
    /// 先行する press が無い release の件数（★ 区間を作らなかったもの）。
    pub orphan_releases: u64,
    /// 観測区間の右端まで**「release の並びの最後」に達せず開いたまま**終わり、
    /// **右端で閉じた**区間の本数（打ち切り）。
    pub truncated_at_right_edge: u64,
}

/// 修飾キーの edge 列（`(時刻, press なら true / release なら false)`・順不同でよい）から
/// **押下区間**を作る（ADR-030 補訂 1 項目 3・極 M+）。
///
/// ⚠️★★★ **「連続する release の並びの最後」で閉じる**（`decisions.md` 判断 23。
/// 2026-09-25 に旧カウント方式 [press で `depth+=1`・release で `depth-=1`] から是正した）。
/// `category:"modifier"` は `Ctrl` / `Shift` / `Win` を区別しないので、`Ctrl+Shift+X` の
/// ような入れ子では**どの release がどの press に対応するかが原理的に読めない**。加えて
/// Windows では修飾キーの押しっぱなしの自動リピートも `press:true` 行としてログに残る
/// (`hook_windows.rs` は `is_repeat: false` 固定で送り、`loop_step.rs` のリピート判定は
/// ログに書く `KeyRecord` の生成には関係しない)。旧カウント方式では `P×N → R` で `depth` が
/// `N-1` 残ってしまい、区間が**観測区間の右端まで閉じず** onset を水増しする（系統誤差）。
///
/// - **開く**: 開いていないときの press で開く（★ 開いている間に来る 2 本目以降の press は
///   無視する —— リピート・持ち替えの重ね押しを区間の継続として扱う）。
/// - **閉じる**: 開いている状態で release が来たとき、その release が
///   **「release の連続する並びの最後」**（＝次の edge が press、または次の edge が無い）
///   なら**そこで閉じる**。次の edge も release なら（並びの途中なので）閉じずに開いたまま
///   並びの次の release を待つ。
///   例: `P P R R` → 2 つ目の R で閉じる／`P R P R` → 1 つ目の R で閉じ、次の P で開き直す。
/// - ⚠️ 観測区間の右端に達しても、release の並びの最後に届かず**開いたまま**なら
///   **そこで閉じる**（打ち切り。`t0 <= b` と対称）。一方、release の並びがちょうど
///   観測区間の終わりで終わった場合はそれ自体が「次の edge が無い」なので**通常どおり
///   閉じる**（打ち切りではない）。
/// - ⚠️ 開いていないときに来た release は区間を作らない（件数だけ返す・孤立 release）。
///
/// ★ **観測区間ごとに開閉の状態を最初から数え直す**（D8 (b)「跨いで足し上げない」と同じ規律）。
/// ⚠️ したがって観測区間の**外**の edge は読まず、区間の左端より前に押された修飾キーの release は
/// 孤立 release になる（★ 押下区間を作らない側＝挿入系を**外さない**側に倒れる）。
/// ⚠️ 同時刻は press を先に処理する（Ctrl → Shift の持ち替えで孤立 release を作らない）。
///
/// ⚠️★★★ **誤る向きは常に baseline 側（除外しない側）に倒れる**（判断 23）: `Ctrl` を押した
/// まま `Shift` を離して押し直す、のような操作で edge の並びが実際の押しっぱなしと違う形
/// （release の並びの途中に次の press が来ない形）に見えると、区間が本来より早く割れることが
/// ある。★ その場合も割れた分だけ**除外しない**側（挿入系をそのまま数える側）に倒れるので、
/// 旧カウント方式が持っていた「区間が右端まで閉じず onset を水増しする」向きの誤りは起きない。
///
/// `observed` は [`observed_intervals`] の戻り値（開始昇順・互いに素）を仮定する。
pub fn modifier_press_intervals(
    edges: &[(u64, bool)],
    observed: &[(u64, u64)],
) -> ModifierIntervals {
    let mut sorted: Vec<(u64, bool)> = edges.to_vec();
    sorted.sort_by_key(|&(t, press)| (t, !press));

    let mut out = ModifierIntervals::default();
    for &(a, b) in observed {
        let lo = sorted.partition_point(|&(t, _)| t < a);
        let hi = sorted.partition_point(|&(t, _)| t <= b);
        let window = &sorted[lo..hi];
        let mut open = false;
        let mut start = a;
        for (i, &(t, press)) in window.iter().enumerate() {
            if press {
                if !open {
                    open = true;
                    start = t;
                }
                // 既に開いている区間中の 2 本目以降の press は無視する
                // (リピート・持ち替えの重ね押しを区間の継続として扱う。判断 23)。
            } else if !open {
                out.orphan_releases += 1;
            } else {
                // release の連続する並びの最後か = 次の edge が press、または次が無い。
                let is_last_of_run = window.get(i + 1).map(|&(_, p)| p).unwrap_or(true);
                if is_last_of_run {
                    out.intervals.push((start, t));
                    open = false;
                }
                // 最後でなければ何もしない（開いたまま並びの次の release を待つ）。
            }
        }
        if open {
            out.intervals.push((start, b));
            out.truncated_at_right_edge += 1;
        }
    }
    out
}

/// 極 M+ が「挿入系に数えない」press の置き換え先の VK（★ `KeyCategory::Modifier` に属する最初の VK）。
///
/// ⚠️ 数値を**ここに再宣言しない** —— 匿名化の写像（`KeyCategory::from_vk`・SSOT）から引く。
/// ★ 置き換え先は `key_net_delta == 0`（挿入系にも削除系にも数えない）で、
/// `restart` の 3 件数（挿入 / 削除 / 移動）のどれにも入らない。
fn modifier_neutral_vk() -> u32 {
    (0..=u32::from(u8::MAX))
        .find(|&vk| KeyCategory::from_vk(vk) == KeyCategory::Modifier)
        .expect("KeyCategory::from_vk maps at least one VK to Modifier")
}

/// 極 M+（ADR-030 補訂 1 項目 3）: `modifier_intervals` の中の**挿入系（`+1`）の press** を
/// 検出が挿入系に数えないもの（修飾キーの VK）へ置き換えた `key` 列を返す。
///
/// ⚠️★★★ **削除系（`−1`）は外さない。** ADR-030 D3 の逐語は「修飾キーが押されている間の
/// *文字キー* は挿入系に数えない」で、削除系には触れていない。`Ctrl+Backspace`（単語削除）まで
/// 外すと `net` が上振れし、**逆向きの系統誤差**が入る。外すのは `key_net_delta` の `+1` の側だけ。
/// ⚠️ press の**時刻・件数・順序は変えない**（★ θ の標本は極に依らない）。
/// ★ `modifier_intervals` は両端を含む。順不同・重なりがあってもよい（内部で併合する）。
pub fn apply_modifier_m_plus(
    keys: &[KeyPress],
    modifier_intervals: &[(u64, u64)],
) -> Vec<KeyPress> {
    let mut merged: Vec<(u64, u64)> = Vec::with_capacity(modifier_intervals.len());
    let mut sorted = modifier_intervals.to_vec();
    sorted.sort_unstable();
    for (s, e) in sorted {
        match merged.last_mut() {
            Some(last) if s <= last.1 => last.1 = last.1.max(e),
            _ => merged.push((s, e)),
        }
    }
    let covered = |t: u64| {
        let idx = merged.partition_point(|&(s, _)| s <= t);
        idx > 0 && t <= merged[idx - 1].1
    };
    let neutral_vk = modifier_neutral_vk();
    keys.iter()
        .map(|k| {
            if super::key_net_delta(k) == 1 && covered(k.timestamp) {
                KeyPress {
                    timestamp: k.timestamp,
                    vk: neutral_vk,
                }
            } else {
                *k
            }
        })
        .collect()
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
/// 伝える)。呼び出し側が「同じ観測区間に入る対だけ」を候補列として渡す (`pooled_theta_gaps`)。
///
/// ⚠️ **本番経路 (`detect_stall_onsets`) はこの関数を直接呼ばない** —— 立ち上がりのたびに
/// プール全体を filter し直すと `O(R・P log P)` になる (issue 008 HIGH-1)。同じ規則
/// (`rank = ceil(q*n)` を `[1, n]` にクランプ、1-indexed) を [`ThetaAccumulator`] が
/// 座標圧縮 Fenwick 木で `O(log N)` に再実装している。本関数はテストからのみ使う。
#[cfg(test)]
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
/// あれば全区間からプールする** (モジュール doc 冒頭。規範定義の θ 標本節の逐語 ＋
/// `decisions.md` 判断 18 の正解表で確定)。`sorted_press_ts` は昇順ソート済みを仮定する。
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

/// gap 値の頻度を座標圧縮した Fenwick 木 (Binary Indexed Tree) で管理し、θ_person を
/// `O(log N)` で求める累積器 (issue 008 HIGH-1)。
///
/// ★ **前提**: `s` はこの累積器への呼び出し全体を通して単調非減少である。観測区間は
/// (`observed_intervals` により) 時刻順・重複無しに並び、各区間内の評価時刻も昇順で
/// 処理されるため、`detect_stall_onsets` がこの前提を満たす唯一の呼び出し元となる。
/// この前提のもとでは、`pooled`（`resuming_ts` 昇順）を指すポインタ `pos` を前進させる
/// だけで「`resuming_ts <= s` の集合」を管理でき、`s` が増えるたびにプール全体を
/// filter し直す必要が無くなる (旧実装は立ち上がり 1 回ごとに `O(P)` の filter+sort を
/// 行い、立ち上がり `R` 回で `O(R・P log P)` になっていた)。
struct ThetaAccumulator {
    /// (resuming_ts, gap_ms) の全プール。`resuming_ts` 昇順 (`pooled_theta_gaps` の出力)。
    pooled: Vec<(u64, u64)>,
    /// `pooled` のうち、まだ Fenwick 木に加えていない先頭の添字。
    pos: usize,
    /// 昇順・重複除去した gap 値 (座標圧縮の軸)。`sorted_values[i]` が Fenwick 木の
    /// 1-indexed 位置 `i + 1` に対応する。
    sorted_values: Vec<u64>,
    /// Fenwick 木本体 (1-indexed。`tree[0]` は未使用)。
    tree: Vec<u64>,
    /// Fenwick 木上の k 番目探索 (binary lifting) で使う最上位ビット
    /// (`floor(log2(sorted_values.len()))`)。
    log_n: u32,
    /// 累積器に既に加えた件数 (= 現在の `n`。`sorted_values.len()` とは別 — 同じ gap 値が
    /// 複数回加わりうる)。
    n_added: usize,
}

impl ThetaAccumulator {
    /// `pooled`（`resuming_ts` 昇順）から空の累積器を作る。まだ何も Fenwick 木に加えない
    /// (`theta_at` が `s` に応じて遅延的に加える)。
    fn new(pooled: &[(u64, u64)]) -> Self {
        let mut sorted_values: Vec<u64> = pooled.iter().map(|&(_, gap_ms)| gap_ms).collect();
        sorted_values.sort_unstable();
        sorted_values.dedup();
        let size = sorted_values.len();
        let log_n = if size == 0 {
            0
        } else {
            usize::BITS - 1 - size.leading_zeros()
        };
        Self {
            pooled: pooled.to_vec(),
            pos: 0,
            sorted_values,
            tree: vec![0u64; size + 1],
            log_n,
            n_added: 0,
        }
    }

    /// gap 値 1 件を Fenwick 木に加える (`O(log N)`)。
    fn add(&mut self, gap_ms: u64) {
        // `gap_ms` は `new` で構築した `sorted_values` から取った値なので必ず見つかる。
        let idx = self
            .sorted_values
            .binary_search(&gap_ms)
            .expect("gap_ms must be a value seen when building sorted_values");
        let mut i = idx + 1; // Fenwick 木は 1-indexed
        let len = self.tree.len();
        while i < len {
            self.tree[i] += 1;
            i += i & i.wrapping_neg(); // 最下位ビットを加える (Fenwick 木の標準更新)
        }
        self.n_added += 1;
    }

    /// Fenwick 木上で `k` 番目 (1-indexed) に小さい値を二分探索 (binary lifting) で求める
    /// (`O(log N)`)。`k` が総和 (`n_added`) を超えないことは呼び出し側が保証する。
    fn find_kth(&self, k: u64) -> u64 {
        let mut pos = 0usize;
        let mut remaining = k;
        let mut pw = 1usize << self.log_n;
        while pw > 0 {
            let next = pos + pw;
            if next < self.tree.len() && self.tree[next] < remaining {
                pos = next;
                remaining -= self.tree[next];
            }
            pw >>= 1;
        }
        self.sorted_values[pos]
    }

    /// `s` 時点で有効な θ_person を、**その標本数 `n` とともに** `(θ, n)` で返す。
    /// `theta_person_from_gaps` と**完全に同じ規則**
    /// (`rank = ceil(q * n)` を `[1, n]` にクランプ、1-indexed の nearest-rank) を、
    /// プール全体の filter+sort の代わりに Fenwick 木で計算する。
    /// ★ `n` は `warmup_count` の判定に使った件数と同じもの (`n_added`) である。
    ///
    /// ⚠️ `s` はこのインスタンスへの呼び出し全体を通して単調非減少でなければならない
    /// (構造体 doc 参照)。降順で呼ぶと `pos` を巻き戻せずに壊れる —— この前提を破る
    /// 呼び出し方をした場合の検出は `tests::matches_naive_reference_on_random_inputs`
    /// (素朴な参照実装との全数比較) に委ねる。
    fn theta_at(&mut self, s: u64, q: f64, warmup_count: Option<usize>) -> Option<(u64, u64)> {
        while self.pos < self.pooled.len() && self.pooled[self.pos].0 <= s {
            let gap_ms = self.pooled[self.pos].1;
            self.add(gap_ms);
            self.pos += 1;
        }
        let n = self.n_added;
        if n == 0 {
            return None;
        }
        if let Some(m) = warmup_count {
            if n < m {
                return None;
            }
        }
        let rank = (q * n as f64).ceil() as usize;
        let rank = rank.clamp(1, n);
        Some((self.find_kth(rank as u64), n as u64))
    }
}

/// 1 つの観測区間 `[a, b]` の中で `stall onset` を検出する (ADR-030 D8 (b) 「連続を切る」
/// を区間単位で満たす)。評価時刻は `{key の t} ∪ {key の t + W} ∪ {a + W}` を
/// `[a + W, b]` に制限したものだけ (D3 逐語 ＋ issue 008 の観測区間の規範)。
/// 区間の直前状態 (立ち上がり判定の `prev`) はここで `false` にリセットする。
///
/// ★ 戻り値は onset の列と**条件 A の変化点の列**である（⚠️ 変化点は issue 006 の `restart` が
/// 使う —— 判断 2 の V2。★ 条件 A を 2 度評価しないよう、検出と同じ 1 回の走査で作る）。
fn detect_stall_onsets_for_interval(
    a: u64,
    b: u64,
    global_instants: &[u64],
    sorted_keys: &[KeyPress],
    prefix: &[i64],
    theta_acc: &mut ThetaAccumulator,
    config: &StallOnsetConfig,
) -> (Vec<OnsetEvent>, Vec<(u64, bool)>) {
    let w = config.w_ms;
    let net_diff_min = config.net_diff_min as i64;

    // 区間が W に届かない (a + W > b) なら、この区間では 1 度も評価されない
    // (ADR-030 D8 (b) 「区間の終了後 W の間も条件 A を評価しない」の裏面)。
    let Some(start) = a.checked_add(w) else {
        return (Vec::new(), Vec::new());
    };
    if start > b {
        return (Vec::new(), Vec::new());
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
    // ★ 条件 A の変化点 (先頭はこの区間の最初の評価時刻とその値)。V2 のために同じ走査で作る。
    let mut changes: Vec<(u64, bool)> = Vec::new();
    let mut prev = false;
    for i in 0..instants.len() {
        if i == 0 || cond_a[i] != cond_a[i - 1] {
            changes.push((instants[i], cond_a[i]));
        }
        if cond_a[i] && !prev {
            let s = instants[i];
            if let Some((theta, theta_sample_n)) =
                theta_acc.theta_at(s, config.q, config.warmup_count)
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
                                theta_sample_n,
                            });
                        }
                    }
                }
            }
        }
        prev = cond_a[i];
    }
    (onsets, changes)
}

/// `stall onset` 列を検出する純関数 (ADR-030 D2/D3/D4/D8 (b-2) の中心アルゴリズム)。
/// `feat_ts` が空なら観測区間が無いので `onset` は 1 つも立たない (AC3)。
///
/// 計算量は `O(N log N)` (`N` = `keys.len()`)。内訳:
/// - 観測区間ごとの条件 A は `net_at_fast` (累積和 ＋ 二分探索) で評価時刻あたり `O(log N)`。
/// - θ_person は [`ThetaAccumulator`] を**全区間を通して 1 つだけ**作り、立ち上がり `s` の
///   たびにポインタを前進させながら Fenwick 木で引く (`s` は呼び出し全体で単調非減少 —
///   区間は時刻順、区間内の評価時刻も昇順)。立ち上がり `R` 回でも `O(R log P)` に収まる
///   (`P` = press 数。issue 008 AC18/AC18b —— 旧実装は立ち上がりのたびにプール全体を
///   filter+sort し直す `O(R・P log P)` だった)。
///
/// ★ 2026-09-20 (issue 006 V2): 本関数は [`condition_a_timeline`] の薄い包みになり、
/// **本番経路からは呼ばれなくなった** (`stall_onset_column_with_timeline` が直接 timeline を使う)。
/// ⚠️ **検出のアルゴリズムは 1 文字も変えていない** —— 同じ走査が変化点も返すようにしただけである。
/// ★ 既存のテスト (onset の集合を直接検算するもの) がこの形を使うので残す。
#[cfg(test)]
fn detect_stall_onsets(
    keys: &[KeyPress],
    feat_ts: &[u64],
    config: &StallOnsetConfig,
) -> Vec<OnsetEvent> {
    condition_a_timeline(keys, feat_ts, config)
        .into_iter()
        .flat_map(|interval| interval.onsets)
        .collect()
}

/// 観測区間ごとの条件 A の評価結果（変化点 ＋ 確定した onset）を返す。
/// ★ [`detect_stall_onsets`] と **同じ 1 回の走査**であり、条件 A を 2 度評価しない
/// （⚠️ issue 008 AC18 / AC18b の計算量の門があるため、二重走査にしない）。
///
/// ★ 本番経路は評価区間を自分で合成する [`stall_onset_column_with_timeline`] を使うので、**テスト専用**
/// (`detect_stall_onsets` の入口)。⚠️ 観測区間そのまま (= 抑制なし) の検出である。
#[cfg(test)]
pub(super) fn condition_a_timeline(
    keys: &[KeyPress],
    feat_ts: &[u64],
    config: &StallOnsetConfig,
) -> Vec<ConditionAInterval> {
    condition_a_timeline_over(
        keys,
        observed_intervals(feat_ts, config.hole_gap_ms),
        config,
    )
}

/// [`condition_a_timeline`] の本体。**評価する区間を呼び出し側が渡す** (開始昇順・互いに素・両端を含む)。
///
/// ★ 極 B は観測区間から抑制区間を除いた区間 ([`evaluation_intervals`]) をここへ渡す。⚠️ 検出の中身
/// (条件 A・θ の標本・`t0 <= b`) は**区間の由来を知らない** —— 観測区間と同じ規則が抑制の各片にそのまま効く。
/// 区間が 1 本も無ければ (`feat` 行が 1 本も無い入力・全部が抑制) onset は 1 つも立たない。
fn condition_a_timeline_over(
    keys: &[KeyPress],
    intervals: Vec<(u64, u64)>,
    config: &StallOnsetConfig,
) -> Vec<ConditionAInterval> {
    if intervals.is_empty() {
        return Vec::new();
    }
    let mut sorted_keys: Vec<KeyPress> = keys.to_vec();
    sorted_keys.sort_by_key(|k| k.timestamp);
    let press_ts: Vec<u64> = sorted_keys.iter().map(|k| k.timestamp).collect();
    let prefix = net_prefix(&sorted_keys);
    let global_instants = build_global_instants(&sorted_keys, config.w_ms);
    let pooled_gaps = pooled_theta_gaps(&press_ts, &intervals);
    let mut theta_acc = ThetaAccumulator::new(&pooled_gaps);

    intervals
        .into_iter()
        .map(|(a, b)| {
            let (onsets, changes) = detect_stall_onsets_for_interval(
                a,
                b,
                &global_instants,
                &sorted_keys,
                &prefix,
                &mut theta_acc,
                config,
            );
            ConditionAInterval {
                a,
                b,
                changes,
                onsets,
            }
        })
        .collect()
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
            theta_sample_n: Some(ev.theta_sample_n),
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
    stall_onset_column_with_timeline(
        keys,
        feat_ts,
        &[],
        task_kind_declarations,
        tick_count,
        grid_origin_ms,
        tick_ms,
        config,
    )
    .0
}

/// [`stall_onset_column`] と**同じ 1 回の走査**で、tick 列と条件 A の時系列の両方を返す。
///
/// ⚠️★★★ **2 度走らせないためにある**（★ issue 006 V2 / 008 AC18 の計算量の門）——
/// `restart` (`T1d`) は条件 A の辺を要するが、`condition_a_timeline` を別に呼ぶと
/// 大入力で検出が 2 回走る。★ `build_feature_rows` はこちらを使う。
///
/// `suppressed` は極 B の**抑制区間** ([`pointer_suppression_intervals`])。★ 空なら観測区間そのまま
/// (極 A / 極 M+ / [`stall_onset_column`] が渡す値)。空でなければ観測区間から除いた評価区間で検出する。
#[allow(clippy::too_many_arguments)]
pub(super) fn stall_onset_column_with_timeline(
    keys: &[KeyPress],
    feat_ts: &[u64],
    suppressed: &[(u64, u64)],
    task_kind_declarations: &[(u64, String)],
    tick_count: usize,
    grid_origin_ms: u64,
    tick_ms: u64,
    config: &StallOnsetConfig,
) -> (Vec<StallOnset>, Vec<ConditionAInterval>) {
    let observed = observed_intervals(feat_ts, config.hole_gap_ms);
    let timeline =
        condition_a_timeline_over(keys, evaluation_intervals(&observed, suppressed), config);
    let onsets: Vec<OnsetEvent> = timeline
        .iter()
        .flat_map(|interval| interval.onsets.iter().copied())
        .collect();
    let column = column_from_onsets(
        &onsets,
        task_kind_declarations,
        tick_count,
        grid_origin_ms,
        tick_ms,
    );
    (column, timeline)
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
                theta_sample_n: 2,
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

    /// LOW-1: 隣接差が**ちょうど** `hole_gap_ms` なら同じ区間のまま (規範「これを超えたら
    /// 切る」＝ 以下なら切らない)。境界のどちら側で切れるかを固定する。
    #[test]
    fn gap_equal_to_hole_gap_does_not_split() {
        let config = StallOnsetConfig::default();
        let feat = vec![0, config.hole_gap_ms];
        let intervals = observed_intervals(&feat, config.hole_gap_ms);
        assert_eq!(
            intervals,
            vec![(0, config.hole_gap_ms)],
            "隣接差がちょうど hole_gap_ms なら区間は割れないはず"
        );
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

    /// MEDIUM-1 是正: 上の対照 (short_feat) は区間そのものが評価不能 (a+W > b) になるだけで、
    /// 「区間開始 (a) からの抑制」を外しても赤にならない (評価時刻が 1 つも生まれないため)。
    /// ⚠️ 穴の後に長い沈黙が続き、区間開始 `a` から評価すると onset が立ってしまう形にする
    /// (抑制を外すと `s=50000`〈区間開始〉になり、この test は赤くなる)。
    #[test]
    fn no_evaluation_within_w_after_hole_produces_wrong_s_if_suppression_removed() {
        let config = StallOnsetConfig::default();
        // 区間1: feat 0..5000。key は 1000/1100 (gap=100、θ の種として使うだけ)。
        // 穴: 5000..50000 (feat 行なし)。
        // 区間2: feat 50000..90000。打鍵は 1 つも無い (長い沈黙)。
        let mut feat = feat_ts_range(0, 5_000, 1_000);
        feat.extend(feat_ts_range(50_000, 90_000, 1_000));
        let keys = vec![key(1_000), key(1_100)];

        let onsets = detect_stall_onsets(&keys, &feat, &config);
        assert_eq!(
            onsets.len(),
            1,
            "区間2 の長い沈黙で onset が 1 つ立つはず: {onsets:?}"
        );
        assert_eq!(
            onsets[0].s_ms, 80_000,
            "区間開始 (50000) ではなく区間開始+W (80000) で立ち上がるはず \
             (a+W の抑制を外すと s=50000 になる): {onsets:?}"
        );
        assert_eq!(onsets[0].t0_ms, 80_100);
        assert_eq!(onsets[0].theta_person_ms, 100);
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

    /// θ の標本は `s` が属する観測区間だけに限定せず、**同じ観測区間に入る対であれば
    /// 他の区間からもプール**する (issue 008「規範となる定義」の θ 標本節の逐語 ＋
    /// `decisions.md` 判断 18 の正解表)。規範文の θ 標本節は「同じ観測区間」と書くだけで
    /// 「`s` と同じ区間」に限定していない (「確定」節の t0<=b とは別の制約)。
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

    /// HIGH-2 是正: 規範定義の 2 項目 —「連続を切る: 直前状態を各観測区間の評価開始時点で
    /// false に戻す」と「評価時刻に `{a+W}` を含める」— を外しても既存テストが緑のままだった。
    /// 区間2 に打鍵を 1 つも置かず (a2+W だけが評価時刻になる)、直前区間の cond_a=true を
    /// 引きずらない/引きずるかで区間2 の onset の有無自体が変わる形にして両方を同時に固定する。
    #[test]
    fn onset_after_hole_rises_at_interval_start_plus_w() {
        let config = StallOnsetConfig::default();
        let keys = small_onset_keys(); // 0, 100, 200
        let mut feat = feat_ts_range(0, 40_000, 1_000);
        feat.extend(feat_ts_range(50_000, 100_000, 1_000));

        let onsets = detect_stall_onsets(&keys, &feat, &config);
        assert_eq!(
            onsets.len(),
            2,
            "区間1 (0..40000) と区間2 (50000..100000) それぞれで onset が 1 つずつ立つはず: {onsets:?}"
        );
        assert_eq!(
            onsets[0],
            OnsetEvent {
                s_ms: 30_200,
                t0_ms: 30_300,
                theta_person_ms: 100,
                theta_sample_n: 2,
            }
        );
        assert_eq!(
            onsets[1],
            OnsetEvent {
                s_ms: 80_000,
                t0_ms: 80_100,
                theta_person_ms: 100,
                theta_sample_n: 2,
            },
            "区間2 に打鍵が無いので、a2+W (=80000) の評価時刻自体が無ければ onset 2 は \
             立たず (評価時刻に {{a+W}} を含める規則)、区間1 の cond_a=true を \
             引きずれば a2+W での立ち上がりが検出されない (直前状態リセットの規則): {onsets:?}"
        );
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
        assert_eq!(config.t1a_window_ms, outcome.merge_gap_ms);
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

    /// HIGH-3 是正: 条件 A (net) の計算が未来の `key` 行を覗いていないこと。s=30200 の
    /// 確定を汚染しない位置 (t0=30300 の 1ms 後) に文字キーを 1 つ足す。
    /// (先読みすると net の窓が誤って広がり、s=30200 が立ち上がらなくなる。)
    #[test]
    fn no_lookahead_in_net() {
        let config = StallOnsetConfig::default();
        let mut keys = small_onset_keys(); // 0, 100, 200
        keys.push(key(30_301)); // t0 (30300) の 1ms 後
        let feat = feat_ts_range(0, 60_000, 1_000);

        let onsets = detect_stall_onsets(&keys, &feat, &config);
        assert!(
            onsets
                .iter()
                .any(|ev| ev.s_ms == 30_200 && ev.t0_ms == 30_300 && ev.theta_person_ms == 100),
            "net が未来の key (30301) を先読みすると s=30200 の立ち上がりが消えるはず: {onsets:?}"
        );
    }

    /// HIGH-3 是正: θ の標本 (press gap) が未来の `key` 行を覗いていないこと。
    /// `s` (30200) と `t0` (30300) の間に navigation キー (net に寄与しない) を挟むと、
    /// その resuming_ts (30250) は `s` より後なので θ の標本には入らないはず。
    /// (先読みすると gap=30050 が混入し θ が 30050 になる。)
    #[test]
    fn no_lookahead_in_theta() {
        let config = StallOnsetConfig::default();
        let mut keys = small_onset_keys(); // 0, 100, 200
        keys.push(KeyPress {
            timestamp: 30_250,
            vk: 0x25, // navigation, net に寄与しない
        });
        let feat = feat_ts_range(0, 60_000, 1_000);

        let onsets = detect_stall_onsets(&keys, &feat, &config);
        assert!(
            onsets
                .iter()
                .any(|ev| ev.s_ms == 30_200 && ev.t0_ms == 30_300 && ev.theta_person_ms == 100),
            "θ が未来の press (30250) を先読みすると theta_person が 30050 になるはず: {onsets:?}"
        );
    }

    /// 決定論的 xorshift64 PRNG (crate を足さずテスト内だけで完結させる)。
    struct XorShift64(u64);

    impl XorShift64 {
        fn new(seed: u64) -> Self {
            // 0 は不動点 (x^=x<<13 等が 0 のまま) なので回避する。
            Self(seed | 1)
        }

        fn next_u64(&mut self) -> u64 {
            let mut x = self.0;
            x ^= x << 13;
            x ^= x >> 7;
            x ^= x << 17;
            self.0 = x;
            x
        }

        /// `[0, bound)` の一様乱数 (`bound > 0`)。
        fn next_range(&mut self, bound: u64) -> u64 {
            self.next_u64() % bound
        }
    }

    /// テスト専用: ランダム入力のタイムライン長 (ms)。
    const TEST_RANDOM_TIMELINE_MS: u64 = 90_000;
    /// テスト専用: `feat` 行 1 本を欠落させる確率 (パーセント)。
    const TEST_RANDOM_HOLE_PERCENT: u64 = 20;
    /// テスト専用: ランダム入力の生成回数。
    const TEST_RANDOM_CASES: usize = 220;

    /// `matches_naive_reference_on_random_inputs` 用のランダム入力を 1 件作る。
    /// feat 行の穴・同一時刻の打鍵・BS・navigation を混ぜる。
    fn random_stall_onset_input(rng: &mut XorShift64) -> (Vec<KeyPress>, Vec<u64>) {
        let mut feat_ts = Vec::new();
        let mut t = 0u64;
        while t <= TEST_RANDOM_TIMELINE_MS {
            if rng.next_range(100) >= TEST_RANDOM_HOLE_PERCENT {
                feat_ts.push(t);
            }
            t += ENGINE_TICK_MS;
        }

        let key_count = 5 + rng.next_range(36) as usize;
        let mut keys = Vec::with_capacity(key_count);
        let mut last_ts: Option<u64> = None;
        for _ in 0..key_count {
            let ts = match last_ts {
                // 同一時刻の打鍵を時々混ぜる。
                Some(prev) if rng.next_range(10) == 0 => prev,
                _ => rng.next_range(TEST_RANDOM_TIMELINE_MS + 1),
            };
            let roll = rng.next_range(10);
            let vk: u32 = if roll < 6 {
                0x41 // 文字キー (text-producing)
            } else if roll < 8 {
                0x08 // backspace
            } else {
                0x25 // navigation
            };
            keys.push(KeyPress { timestamp: ts, vk });
            last_ts = Some(ts);
        }
        (keys, feat_ts)
    }

    /// 素朴な参照実装: 規範定義を逐語どおりに書いたもの。評価時刻ごとに全キーを走査し
    /// (`naive_net_at`)、θ も毎回全 gap から集め直す (`naive_theta_at`)。最適化 (Fenwick 木・
    /// 累積和二分探索) と実装戦略を完全に分けることで、[`ThetaAccumulator`] / `net_at_fast`
    /// への信頼を `detect_stall_onsets` の出力そのものと比較して検証する
    /// (`matches_naive_reference_on_random_inputs`)。
    ///
    /// ★ `observed_intervals` / `build_global_instants` は共有する —— これらは今回の
    /// 二乗バグ (θ の再計算) と無関係であり、既に個別のテストで固定済み。
    fn naive_net_at(keys: &[KeyPress], t: u64, w_ms: u64) -> i64 {
        keys.iter()
            .filter(|k| {
                k.timestamp <= t
                    && k.timestamp
                        .checked_add(w_ms)
                        .map(|end| end > t)
                        .unwrap_or(true)
            })
            .map(super::super::key_net_delta)
            .sum()
    }

    fn naive_theta_at(
        sorted_press_ts: &[u64],
        intervals: &[(u64, u64)],
        s: u64,
        q: f64,
        warmup_count: Option<usize>,
    ) -> Option<(u64, u64)> {
        let mut gaps: Vec<u64> = Vec::new();
        for w in sorted_press_ts.windows(2) {
            let (k_i, k_ip1) = (w[0], w[1]);
            if k_ip1 > s {
                continue; // 因果性: s より後に確定する対は使わない
            }
            let same_interval = intervals.iter().any(|&(a, b)| a <= k_i && k_ip1 <= b);
            if same_interval {
                gaps.push(k_ip1.saturating_sub(k_i));
            }
        }
        if gaps.is_empty() {
            return None;
        }
        if let Some(m) = warmup_count {
            if gaps.len() < m {
                return None;
            }
        }
        gaps.sort_unstable();
        // ★ 標本数 `n` は素朴な参照側でも独立に数える (Fenwick 木の `n_added` を信用しない)。
        let n = gaps.len() as u64;
        quantile_nearest_rank(&gaps, q).map(|theta| (theta, n))
    }

    fn naive_detect_stall_onsets(
        keys: &[KeyPress],
        feat_ts: &[u64],
        config: &StallOnsetConfig,
    ) -> Vec<OnsetEvent> {
        if feat_ts.is_empty() {
            return Vec::new();
        }
        let mut sorted_keys: Vec<KeyPress> = keys.to_vec();
        sorted_keys.sort_by_key(|k| k.timestamp);
        let sorted_press_ts: Vec<u64> = sorted_keys.iter().map(|k| k.timestamp).collect();
        let global_instants = build_global_instants(&sorted_keys, config.w_ms);
        let intervals = observed_intervals(feat_ts, config.hole_gap_ms);

        let mut onsets = Vec::new();
        for &(a, b) in &intervals {
            let Some(start) = a.checked_add(config.w_ms) else {
                continue;
            };
            if start > b {
                continue;
            }
            let lo = global_instants.partition_point(|&t| t < start);
            let hi = global_instants.partition_point(|&t| t <= b);
            let mut instants: Vec<u64> = Vec::with_capacity(hi - lo + 1);
            instants.push(start);
            instants.extend_from_slice(&global_instants[lo..hi]);
            instants.sort_unstable();
            instants.dedup();

            // ★ 評価時刻ごとに全キーを走査する (naive・O(N) per instant)。
            let cond_a: Vec<bool> = instants
                .iter()
                .map(|&t| naive_net_at(&sorted_keys, t, config.w_ms) < config.net_diff_min as i64)
                .collect();

            let mut prev = false;
            for i in 0..instants.len() {
                if cond_a[i] && !prev {
                    let s = instants[i];
                    // ★ θ も毎回全 gap から集め直す (naive・s ごとに再走査・再ソート)。
                    if let Some((theta, theta_sample_n)) = naive_theta_at(
                        &sorted_press_ts,
                        &intervals,
                        s,
                        config.q,
                        config.warmup_count,
                    ) {
                        if let Some(t0) = s.checked_add(theta) {
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
                                        theta_sample_n,
                                    });
                                }
                            }
                        }
                    }
                }
                prev = cond_a[i];
            }
        }
        onsets
    }

    /// HIGH-3 是正: 本番 (`detect_stall_onsets`、Fenwick 木 ＋ 累積和二分探索) と
    /// 素朴な参照実装 (`naive_detect_stall_onsets`、規範定義を逐語どおりに書いたもの) を、
    /// シード固定の xorshift64 で作った 220 件のランダム入力 (穴・同一時刻・BS・navigation を
    /// 混ぜる) について比較し、出力 (`s`/`t0`/`theta_person_ms` の列) が完全一致することを
    /// 固定する。
    #[test]
    fn matches_naive_reference_on_random_inputs() {
        let mut config = StallOnsetConfig::default();
        // ★ タイムラインを圧縮した既定より短い W を使い、220 件の中で立ち上がりが
        //   十分な頻度で起きるようにする (`OutcomeConfig::merge_gap_ms` 由来の既定は
        //   このタイムラインに対して大きすぎる)。
        config.w_ms /= 8;

        let mut rng = XorShift64::new(0x9E3779B97F4A7C15);
        for case in 0..TEST_RANDOM_CASES {
            let (keys, feat_ts) = random_stall_onset_input(&mut rng);
            let fast = detect_stall_onsets(&keys, &feat_ts, &config);
            let naive = naive_detect_stall_onsets(&keys, &feat_ts, &config);
            assert_eq!(
                fast, naive,
                "case {case}: fast (Fenwick 木) と naive (素朴な参照実装) の出力が \
                 食い違う (keys={keys:?}, feat_ts={feat_ts:?})"
            );
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

    /// MEDIUM-2 是正: 上のテストは `s` と `t0` (θ=100ms) が偶然同じ tick に乗るため、
    /// 「onset を `s` の tick に載せる」誤りとの区別が付かない。θ >= 1000ms にして
    /// `s` と `t0` を別々の tick に置き、tick 帰属が `t0` 基準であることを直接固定する。
    #[test]
    fn onset_tick_uses_t0_not_s_when_they_differ() {
        let config = StallOnsetConfig::default();
        let keys = vec![key(0), key(20_000)]; // gap 20000 → θ = 20000 (単一標本)
        let feat = feat_ts_range(0, 71_000, 1_000);
        let column = stall_onset_column(&keys, &feat, &[], 80, 0, ENGINE_TICK_MS, &config);

        let idx = column
            .iter()
            .position(|r| r.is_onset)
            .expect("onset should fire");
        let s = column[idx].s_ms.expect("onset row has s");
        let t0 = column[idx].t0_ms.expect("onset row has t0");
        assert_ne!(
            s / ENGINE_TICK_MS,
            t0 / ENGINE_TICK_MS,
            "この test の前提: s と t0 が異なる tick に乗ること (s={s}, t0={t0})"
        );

        let t_ms = idx as u64 * ENGINE_TICK_MS; // grid_origin=0
        assert!(
            t_ms <= t0 && t0 < t_ms + ENGINE_TICK_MS,
            "onset は t0 の tick に載るはず (s の tick に載せると idx が s 側にずれる): \
             idx={idx} t_ms={t_ms} s={s} t0={t0}"
        );
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
            theta_sample_n: 7,
        };
        let later = OnsetEvent {
            s_ms: 2_000,
            t0_ms: 5_800, // earlier と同じ tick (5000..6000)
            theta_person_ms: 3_800,
            theta_sample_n: 9,
        };
        let column = column_from_onsets(&[earlier, later], &[], 10, 0, 1000);
        assert!(column[5].is_onset);
        assert_eq!(column[5].t0_ms, Some(5_500), "先に確定した onset を残す");
        assert_eq!(column[5].s_ms, Some(1_000));
        assert_eq!(
            column[5].theta_sample_n,
            Some(7),
            "θ と標本数は同じ onset のものが残る (後の onset の 9 が混ざらない)"
        );
    }

    /// 等間隔 `step_ms` の press を `count` 個 (`t = 0, step, 2*step, ...`) 並べる。
    /// 隣接対は `count - 1` 個 (どれも gap = `step_ms`)。
    fn evenly_spaced_keys(step_ms: u64, count: u64) -> Vec<KeyPress> {
        (0..count).map(|i| key(i * step_ms)).collect()
    }

    /// AC6: `theta_sample_n` は `theta_person_ms` と**同時にだけ**立つ。onset 行では標本数
    /// (`resuming_ts <= s` の隣接対の数) と一致し、onset でない行は `null`。
    #[test]
    fn theta_sample_n_is_present_exactly_when_theta_is() {
        let config = StallOnsetConfig::default();
        let feat = feat_ts_range(0, 31_000, 1_000);
        let column = stall_onset_column(&small_onset_keys(), &feat, &[], 40, 0, 1_000, &config);

        assert!(
            column.iter().any(|r| r.is_onset),
            "対照: onset が 1 つは立つ"
        );
        for row in &column {
            assert_eq!(
                row.theta_person_ms.is_some(),
                row.theta_sample_n.is_some(),
                "θ と標本数は同時に立つ: {row:?}"
            );
        }
        let onset_row = column.iter().find(|r| r.is_onset).expect("onset row");
        // 0→100 / 100→200 の 2 対 (手計算・モジュール doc 参照)。
        assert_eq!(onset_row.theta_sample_n, Some(2));
        assert!(column
            .iter()
            .filter(|r| !r.is_onset)
            .all(|r| r.theta_sample_n.is_none()));
    }

    /// AC7: `warmup_count` は標本数 `n` が下限に**届くまで** θ を出さず、届いた onset は
    /// `theta_sample_n >= warmup_count` を満たす (`n == warmup_count` ちょうどでも出る)。
    /// ★ 対照 (`Some(n)` → onset あり / `Some(n + 1)` → onset なし) で、
    /// 「そもそも onset が立たない入力だった」と区別する。
    #[test]
    fn warmup_count_blocks_theta_below_the_floor() {
        // 101 press = 100 対 (gap 100ms)。最後の press (t=10_000) が窓から抜ける
        // s = 40_000 で条件 A が立ち、θ = 100 → t0 = 40_100。
        let keys = evenly_spaced_keys(100, 101);
        let feat = feat_ts_range(0, 41_000, 1_000);

        let floor_met = StallOnsetConfig {
            warmup_count: Some(100),
            ..StallOnsetConfig::default()
        };
        let onsets = detect_stall_onsets(&keys, &feat, &floor_met);
        assert_eq!(
            onsets.len(),
            1,
            "n = warmup_count ちょうどなら出る: {onsets:?}"
        );
        assert_eq!(onsets[0].theta_sample_n, 100);
        assert!(onsets[0].theta_sample_n >= 100);

        let floor_missed = StallOnsetConfig {
            warmup_count: Some(101),
            ..StallOnsetConfig::default()
        };
        assert!(
            detect_stall_onsets(&keys, &feat, &floor_missed).is_empty(),
            "n = 100 < warmup_count = 101 なら θ を出さず、onset も立たない"
        );
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

    /// 極の既定は `Baseline` (現行の計算)。`StallOnsetConfig` の既定にも及ぶ。
    #[test]
    fn pole_defaults_to_baseline() {
        assert_eq!(Pole::default(), Pole::Baseline);
        assert_eq!(StallOnsetConfig::default().pole, Pole::Baseline);
    }

    /// 名前の往復と、未知の名前の拒否。★ 大文字小文字・前後の空白・近い綴りを丸めない。
    #[test]
    fn pole_names_round_trip_and_unknown_is_none() {
        for pole in Pole::ALL {
            assert_eq!(Pole::from_name(pole.as_str()), Some(pole));
        }
        assert_eq!(
            Pole::ALL.map(Pole::as_str),
            ["baseline", "pointer_b", "modifier_m_plus"]
        );
        for bad in [
            "",
            "bogus",
            "Baseline",
            " baseline",
            "baseline ",
            "pointer",
            "modifier",
            "pointer_b+modifier_m_plus",
        ] {
            assert_eq!(Pole::from_name(bad), None, "`{bad}` は未知の極");
        }
    }

    /// 中身があるのは `baseline` と `modifier_m_plus`（issue 005 で開通）。⚠️ issue 006 が極 B を
    /// `true` にする（そのとき本テストの期待を変える —— 開通したことを意図して書き換えさせるための固定）。
    #[test]
    fn baseline_and_modifier_m_plus_are_implemented() {
        assert!(Pole::Baseline.is_implemented());
        assert!(Pole::ModifierMPlus.is_implemented());
        // ★ 極 B は issue 006 で開通した (未実装の極が 1 つも無くなった)。
        assert!(Pole::PointerB.is_implemented());
        assert!(Pole::ALL.into_iter().all(Pole::is_implemented));
    }

    // ── 極 M+（issue 005）────────────────────────────────────────────────

    /// 修飾キーの VK（左 Ctrl）。★ `KeyCategory::Modifier` に入る。
    const TEST_CTRL_VK: u32 = 0xA2;
    const TEST_BACKSPACE_VK: u32 = 0x08;

    fn key_vk(t: u64, vk: u32) -> KeyPress {
        KeyPress { timestamp: t, vk }
    }

    /// `KeyPress` は `PartialEq` を持たない（`metrics.rs` は本 issue の対象外）ので `(時刻, VK)` で比べる。
    fn pairs(keys: &[KeyPress]) -> Vec<(u64, u32)> {
        keys.iter().map(|k| (k.timestamp, k.vk)).collect()
    }

    /// AC3: ⚠️★★★ **削除系（`−1`）を外さない。** `Ctrl+Backspace`（修飾キー押下中の backspace）は
    /// 極 M+ でも `−1` のまま数えられる。外すのは挿入系（`+1`）だけである。
    #[test]
    fn m_plus_does_not_drop_deletions() {
        let keys = vec![
            key_vk(1000, TEST_CTRL_VK),      // 押下区間の開始（どれにも数えない）
            key_vk(1100, TEST_BACKSPACE_VK), // Ctrl+Backspace ★ −1 のまま
            key_vk(1200, 0x41),              // Ctrl+A ★ 区間内の +1 → 数えない
            key_vk(1300, 0x41),              // 同上
            key_vk(5000, 0x41),              // 区間の外 ★ +1 のまま
            key_vk(6000, TEST_BACKSPACE_VK), // 区間の外 ★ −1 のまま
        ];
        let observed = [(0_u64, 10_000_u64)];
        let intervals = modifier_press_intervals(&[(1000, true), (1400, false)], &observed);
        assert_eq!(intervals.intervals, vec![(1000, 1400)]);

        let mapped = apply_modifier_m_plus(&keys, &intervals.intervals);

        // 陰性対照（baseline の写像）: −1 +1 +1 +1 −1 = +1。
        assert_eq!(super::super::net_production(&keys), 1);
        // 極 M+: 区間内の +1 が 2 本消えるだけ → −1 +0 +0 +1 −1 = −1。
        assert_eq!(super::super::net_production(&mapped), -1);

        // ★ 削除系は 1 本も外れていない（VK も 1 文字も変わらない）。
        assert_eq!(pairs(&mapped[1..2]), pairs(&keys[1..2]));
        assert_eq!(super::super::key_net_delta(&mapped[1]), -1);
        assert_eq!(pairs(&mapped[5..]), pairs(&keys[5..]));
        assert_eq!(super::super::key_net_delta(&mapped[2]), 0);
        assert_eq!(super::super::key_net_delta(&mapped[3]), 0);
        assert_eq!(super::super::key_net_delta(&mapped[4]), 1);

        // ★ press の時刻・件数・順序は変えない（θ の標本は極に依らない）。
        assert_eq!(
            mapped.iter().map(|k| k.timestamp).collect::<Vec<_>>(),
            keys.iter().map(|k| k.timestamp).collect::<Vec<_>>()
        );
    }

    /// AC4 (判断 23 是正後): 入れ子（`Ctrl` 押下中に `Shift` 押下/離上）・持ち替えのいずれでも
    /// **区間は 1 本**になる（＝ release の並びの最後まで開いたまま繋がる）。
    #[test]
    fn modifier_depth_merges_nested_presses() {
        let observed = [(0_u64, 10_000_u64)];
        let run = |edges: &[(u64, bool)]| modifier_press_intervals(edges, &observed);

        // Ctrl 押下 → Shift 押下 → Shift 離上 → Ctrl 離上（入れ子。P P R R）。
        // ★ 2 つ目の release (400) が「release の並びの最後」なのでそこで閉じる。
        // ⚠️ `category:"modifier"` は Ctrl/Shift を区別しないため、「離す順が逆」
        // （Ctrl を先に離す/Shift を先に離す）は edge 列として区別できない —— どちらも
        // 同じ `(t, press)` 列になる（★ 旧テストの `crossed` は `nested` と同一の入力で
        // 何も別に検証していなかったため削除した）。
        let nested = run(&[(100, true), (200, true), (300, false), (400, false)]);
        assert_eq!(nested.intervals, vec![(100, 400)]);

        // 持ち替え（Ctrl 離上と Shift 押下が同時刻）。★ 同時刻は press を先に処理するので途切れない。
        let handoff = run(&[(100, true), (300, false), (300, true), (500, false)]);
        assert_eq!(handoff.intervals, vec![(100, 500)]);
        assert_eq!(handoff.orphan_releases, 0);

        // 重ならない 2 回の押下は 2 本のまま（陰性対照）。
        let separate = run(&[(100, true), (150, false), (400, true), (450, false)]);
        assert_eq!(separate.intervals, vec![(100, 150), (400, 450)]);

        // 順不同で渡しても同じ（内部で時刻順に直す）。
        let shuffled = run(&[(400, false), (200, true), (100, true), (300, false)]);
        assert_eq!(shuffled.intervals, vec![(100, 400)]);
        for r in [&nested, &separate, &shuffled] {
            assert_eq!(r.orphan_releases, 0);
            assert_eq!(r.truncated_at_right_edge, 0);
        }
    }

    /// 判断 23 (a): Windows の自動リピートで press が多数連続しても、区間は
    /// **release の並びの最後**（本テストでは release 1 本）で閉じる —— 旧カウント方式
    /// （press で `depth+=1`）だと `depth` が `N-1` 残り、観測区間の右端まで閉じず
    /// `truncated_at_right_edge` が立ってしまう（系統誤差・水増し）。
    #[test]
    fn modifier_repeat_presses_close_on_release_not_right_edge() {
        let observed = [(0_u64, 100_000_u64)];
        // 150ms 間隔で press を 20 本（リピート）→ 最後に release 1 本。
        let mut edges: Vec<(u64, bool)> = (0..20).map(|i| (100 + i * 150, true)).collect();
        let release_t = 100 + 19 * 150 + 150;
        edges.push((release_t, false));

        let result = modifier_press_intervals(&edges, &observed);

        assert_eq!(
            result.intervals,
            vec![(100, release_t)],
            "release で閉じる（観測区間の右端 100_000 までは伸びない）"
        );
        assert_eq!(
            result.truncated_at_right_edge, 0,
            "リピートを depth として数えていたら、この release では閉じず右端で打ち切られる"
        );
        assert_eq!(result.orphan_releases, 0);
    }

    /// 判断 23 (c): `P R P R` は 1 つ目の R で閉じ、次の P で開き直すので **2 区間**になる
    /// （★ 旧カウント方式なら `depth` が 1→0→1→0 と動き、たまたま同じ 2 区間になるので、
    /// 本テストは新規則そのものではなく「開いたまま release の並びを待つ」ことの陰性対照
    /// —— 判断 23 (a) の変異テストが新旧の違いを検出する）。
    #[test]
    fn modifier_alternating_press_release_makes_two_intervals() {
        let observed = [(0_u64, 10_000_u64)];
        let alternating = modifier_press_intervals(
            &[(100, true), (200, false), (300, true), (400, false)],
            &observed,
        );
        assert_eq!(alternating.intervals, vec![(100, 200), (300, 400)]);
        assert_eq!(alternating.orphan_releases, 0);
        assert_eq!(alternating.truncated_at_right_edge, 0);
    }

    /// AC5: ⚠️ 孤立した release（先行する press が無い）は区間を作らず、閉じない押下は
    /// **観測区間の右端で打ち切る**（判断 23 (d)(e)）。
    #[test]
    fn unmatched_modifier_release_and_open_press() {
        // 孤立 release: 区間ができない（件数だけ数える）。
        let orphan = modifier_press_intervals(&[(50, false)], &[(0, 1000)]);
        assert!(orphan.intervals.is_empty());
        assert_eq!(orphan.orphan_releases, 1);
        assert_eq!(orphan.truncated_at_right_edge, 0);

        // 孤立 release の後の press/release は普通に 1 本になる（開いていない状態が
        // 孤立 release をまたいでも壊れない）。
        let recovered =
            modifier_press_intervals(&[(100, false), (200, true), (300, false)], &[(0, 1000)]);
        assert_eq!(recovered.intervals, vec![(200, 300)]);
        assert_eq!(recovered.orphan_releases, 1);

        // 閉じない押下: 観測区間の右端 `b` で閉じる（★ 右端ちょうどは確定扱い）。
        let open = modifier_press_intervals(&[(900, true)], &[(0, 1000)]);
        assert_eq!(open.intervals, vec![(900, 1000)]);
        assert_eq!(open.truncated_at_right_edge, 1);

        // ⚠️ 打ち切りは穴を越えない・開閉の状態は区間ごとに最初から数え直す:
        // 1 つ目の区間で開いた押下は 1000 で閉じ、2 つ目の区間の release は孤立になる。
        let across =
            modifier_press_intervals(&[(800, true), (5500, false)], &[(0, 1000), (5000, 6000)]);
        assert_eq!(across.intervals, vec![(800, 1000)]);
        assert_eq!(across.orphan_releases, 1);
        assert_eq!(across.truncated_at_right_edge, 1);

        // 観測区間の外の edge は読まない（区間が無ければ何も作らない）。
        let outside = modifier_press_intervals(&[(100, true), (200, false)], &[(1000, 2000)]);
        assert!(outside.intervals.is_empty());
        assert_eq!(outside.orphan_releases, 0);
        assert!(modifier_press_intervals(&[(100, true)], &[])
            .intervals
            .is_empty());
    }

    /// 区間の端は**含む**・区間の外は触らない・空の区間は恒等・重なる/順不同の区間は併合する。
    #[test]
    fn m_plus_mapping_boundaries_and_identity() {
        let keys = vec![key(99), key(100), key(150), key(200), key(201), key(300)];
        let mapped = apply_modifier_m_plus(&keys, &[(100, 200)]);
        let deltas: Vec<i64> = mapped.iter().map(super::super::key_net_delta).collect();
        // 99 と 201 は区間の外（+1 のまま）、100 / 150 / 200 は区間内（両端を含む）。
        assert_eq!(deltas, vec![1, 0, 0, 0, 1, 1]);

        // 空の区間: 恒等（★ 修飾キーの行が 0 本の入力で baseline と一致する根拠）。
        assert_eq!(pairs(&apply_modifier_m_plus(&keys, &[])), pairs(&keys));

        // 重なる・順不同の区間は併合して同じ結果になる。
        let merged = apply_modifier_m_plus(&keys, &[(150, 200), (100, 160)]);
        assert_eq!(pairs(&merged), pairs(&mapped));
    }

    /// 置き換え先の VK は `KeyCategory::Modifier` で、挿入系にも削除系にも数えない。
    #[test]
    fn m_plus_neutral_vk_counts_nowhere() {
        let vk = modifier_neutral_vk();
        assert_eq!(KeyCategory::from_vk(vk), KeyCategory::Modifier);
        let k = key_vk(0, vk);
        assert_eq!(super::super::key_net_delta(&k), 0);
        assert!(!crate::analysis::metrics::is_backspace(vk));
    }

    /// ⚠️★★★ 極 M+ は onset を**広げる**（baseline の onset を 1 本も失わず、M+ にしか立たない onset がある）。
    ///
    /// 手計算（`W` = 30 秒・`q` = 0.99・`net_diff_min` = 1・warmup 無し）:
    /// - 打鍵: 平文 200ms 刻み ×130（〜26_000）→ Ctrl+文字 5 本（40_100〜40_900）→ 平文 1 本（65_000）。
    /// - baseline: Ctrl+文字が +5 で窓に居続け、平文 65_000 が抜ける 95_000 まで条件 A は立たない → onset 1 本。
    /// - M+: 40_100〜40_900 を数えないので最後の平文 26_000 が窓を抜ける **56_000** で条件 A が立ち、
    ///   65_000 の平文で一度落ち、95_000 でもう一度立つ → onset 2 本（95_000 は baseline と共通）。
    ///
    /// ★ 両極の θ は同じ press 時刻から作るので、共通の onset は θ も一致する。
    #[test]
    fn m_plus_widens_onsets_and_keeps_every_baseline_onset() {
        let mut keys: Vec<KeyPress> = (1..=130).map(|i| key(i * 200)).collect();
        keys.push(key_vk(40_000, TEST_CTRL_VK));
        keys.extend((0..5).map(|i| key(40_100 + i * 200)));
        keys.push(key(65_000));
        let feat_ts = feat_ts_range(1000, 115_000, 1000);
        let config = StallOnsetConfig {
            warmup_count: None,
            ..StallOnsetConfig::default()
        };

        let baseline = detect_stall_onsets(&keys, &feat_ts, &config);

        let observed = observed_intervals(&feat_ts, config.hole_gap_ms);
        let modifier = modifier_press_intervals(&[(40_000, true), (41_000, false)], &observed);
        let mapped = apply_modifier_m_plus(&keys, &modifier.intervals);
        let m_plus = detect_stall_onsets(&mapped, &feat_ts, &config);

        assert_eq!(
            baseline.iter().map(|o| o.s_ms).collect::<Vec<_>>(),
            vec![95_000],
            "baseline は 95_000 の 1 本だけ"
        );
        assert_eq!(
            m_plus.iter().map(|o| o.s_ms).collect::<Vec<_>>(),
            vec![56_000, 95_000],
            "M+ は 56_000 が増える（★ 逆向きなら写像が逆）"
        );
        for onset in &baseline {
            assert!(
                m_plus.contains(onset),
                "baseline の onset {onset:?} が M+ に無い（★ θ も含めて一致するはず）"
            );
        }
        assert!(m_plus.len() > baseline.len());
    }

    // ── 極 B（issue 006）────────────────────────────────────────────────

    /// 抑制区間つきで検出する (テスト専用)。★ 本番 (`stall_onset_column_with_timeline`) と同じ合成。
    fn detect_with_suppression(
        keys: &[KeyPress],
        feat_ts: &[u64],
        suppressed: &[(u64, u64)],
        config: &StallOnsetConfig,
    ) -> Vec<OnsetEvent> {
        let observed = observed_intervals(feat_ts, config.hole_gap_ms);
        condition_a_timeline_over(keys, evaluation_intervals(&observed, suppressed), config)
            .into_iter()
            .flat_map(|interval| interval.onsets)
            .collect()
    }

    /// AC4: 抑制区間は `pointer_bin` 行の `(t − 1000, t]` の**極大連続**である。
    /// ★ 隣接する 2 行は 1 本に畳まれ、1 ms でも空けば別の区間になる。
    #[test]
    fn pointer_bins_merge_into_maximal_intervals() {
        assert_eq!(
            POINTER_BIN_MS, 1_000,
            "ビン幅は observe_*.rs の BIN_MS と同じ 1 秒"
        );
        // 隣接 2 行 (5000, 6000) は (4000, 5000] と (5000, 6000] が接して 1 本になる。
        assert_eq!(
            pointer_suppression_intervals(&[5_000, 6_000], POINTER_BIN_MS),
            vec![(4_000, 6_000)]
        );
        // 3 行の連鎖も 1 本。
        assert_eq!(
            pointer_suppression_intervals(&[5_000, 6_000, 7_000], 1_000),
            vec![(4_000, 7_000)]
        );
        // 順不同・重複は吸収され、離れた行は別の区間になる。
        assert_eq!(
            pointer_suppression_intervals(&[9_000, 5_000, 6_000, 5_000], 1_000),
            vec![(4_000, 6_000), (8_000, 9_000)]
        );
        // ⚠️ 境界: ちょうど 1 ビン離れは接する (上で確認)／1 ms 空けば別 ((5000, 5001] が未被覆)。
        assert_eq!(
            pointer_suppression_intervals(&[5_000, 6_001], 1_000),
            vec![(4_000, 5_000), (5_001, 6_001)]
        );
        // 空・ビン幅 0 (覆う秒が無い) は空。先頭がビン幅より小さければ下端は 0 に飽和する。
        assert!(pointer_suppression_intervals(&[], 1_000).is_empty());
        assert!(pointer_suppression_intervals(&[5_000], 0).is_empty());
        assert_eq!(pointer_suppression_intervals(&[300], 1_000), vec![(0, 300)]);
    }

    /// 観測区間から抑制区間を除く合成の境界 (`(lo, hi]` は整数 ms で `[lo + 1, hi]`)。
    #[test]
    fn evaluation_intervals_cut_observed_by_suppression() {
        let observed = vec![(0, 100_000)];
        // 抑制が空なら観測区間そのまま (★ 極 A / 極 M+ が baseline と恒等になる根拠)。
        assert_eq!(evaluation_intervals(&observed, &[]), observed);
        // 途中を抜くと 2 片に割れ、抑制の上端の**次の ms**から次の片が始まる。
        assert_eq!(
            evaluation_intervals(&observed, &[(55_000, 57_000)]),
            vec![(0, 55_000), (57_001, 100_000)]
        );
        // 1 つの観測区間に複数の抑制。
        assert_eq!(
            evaluation_intervals(&[(0, 100)], &[(10, 20), (30, 40)]),
            vec![(0, 10), (21, 30), (41, 100)]
        );
        // 抑制が区間の境界をまたぐ／区間全体を覆う。
        assert_eq!(
            evaluation_intervals(&[(10, 20), (30, 40)], &[(15, 35)]),
            vec![(10, 15), (36, 40)]
        );
        assert!(evaluation_intervals(&[(20, 30)], &[(10, 40)]).is_empty());
        // 抑制が区間の外なら変わらない: 終端ちょうどから始まる (`b + 1` 以降を覆う) / 始端の直前で終わる。
        assert_eq!(evaluation_intervals(&[(0, 10)], &[(10, 20)]), vec![(0, 10)]);
        assert_eq!(
            evaluation_intervals(&[(11, 20)], &[(0, 10)]),
            vec![(11, 20)]
        );
        // 始端ちょうどを覆う抑制は、その ms を除く。
        assert_eq!(
            evaluation_intervals(&[(10, 20)], &[(0, 10)]),
            vec![(11, 20)]
        );
    }

    /// AC5: θ の標本は**抑制区間をまたがない** (ADR-030 D4 の標本規則: 抑制・除外区間をまたぐ gap は入れない)。
    /// ★ 抑制区間の**内側**の press を含む対も入らない。baseline との対照で θ が変わることを見る。
    #[test]
    fn theta_sample_excludes_pairs_across_pointer_suppression() {
        let config = StallOnsetConfig::default();
        let feat = feat_ts_range(0, 115_000, 1_000);
        // 1000/1100/1200 (gap 100 ×2) → 20500/20600 (抑制区間 (20000, 21000] の内側) → 41000/41100。
        let keys = vec![
            key(1_000),
            key(1_100),
            key(1_200),
            key(20_500),
            key(20_600),
            key(41_000),
            key(41_100),
        ];

        // baseline: 標本は 6 対 (100, 100, 19300, 100, 20400, 100)。p99 = 最大 = 20400。
        let baseline = detect_stall_onsets(&keys, &feat, &config);
        assert_eq!(
            baseline.len(),
            1,
            "baseline は s=71100 の 1 本だけ: {baseline:?}"
        );
        assert_eq!(baseline[0].s_ms, 71_100);
        assert_eq!(baseline[0].theta_person_ms, 20_400);
        assert_eq!(baseline[0].theta_sample_n, 6);

        // 極 B: 抑制の内側の press (20500/20600) と、抑制をまたぐ対 (1200→41000 / 1200→20500) は標本に入らない。
        // 残るのは同じ片の内側の 3 対 (100 ×3) だけ → θ = 100。
        let suppressed = pointer_suppression_intervals(&[21_000], POINTER_BIN_MS);
        assert_eq!(suppressed, vec![(20_000, 21_000)]);
        let pole_b = detect_with_suppression(&keys, &feat, &suppressed, &config);
        assert_eq!(
            pole_b,
            vec![OnsetEvent {
                s_ms: 71_100,
                t0_ms: 71_200,
                theta_person_ms: 100,
                theta_sample_n: 3,
            }],
            "抑制をまたぐ gap が標本に混ざると θ が 20400 に跳ね上がる (θ_person が過大になり episode yield が落ちる)"
        );
    }

    /// AC6: 抑制区間の直後の片も、観測区間と同じく**頭の `W` を評価しない**
    /// (補訂 1 項目 1-3)。片の開始 (50001) ではなく `開始 + W` (80001) で条件 A が立ち上がる。
    /// ★ 同時に、直前状態が `false` に戻ること・長い沈黙の途中の抑制で onset が**増える**ことも固定する。
    #[test]
    fn pointer_suppression_skips_the_leading_w() {
        let config = StallOnsetConfig::default();
        let feat = feat_ts_range(0, 90_000, 1_000);
        let keys = vec![key(1_000), key(1_100)];

        let baseline = detect_stall_onsets(&keys, &feat, &config);
        assert_eq!(
            baseline.iter().map(|o| o.s_ms).collect::<Vec<_>>(),
            vec![31_100],
            "baseline は 1 本の沈黙で onset 1 つ"
        );

        // 沈黙の途中 (49000, 50000] に活動。→ 片は [0, 49000] と [50001, 90000]。
        let suppressed = pointer_suppression_intervals(&[50_000], POINTER_BIN_MS);
        let pole_b = detect_with_suppression(&keys, &feat, &suppressed, &config);
        assert_eq!(
            pole_b.iter().map(|o| o.s_ms).collect::<Vec<_>>(),
            vec![31_100, 80_001],
            "後ろの片は開始 50001 ではなく開始+W=80001 で立つはず \
             (W の抑制を外すと 50001 になる): {pole_b:?}"
        );
        assert_eq!(pole_b[1].t0_ms, 80_101);
        // 前の片の onset は baseline と同じ (θ の標本も同じ 1 対)。
        assert_eq!(pole_b[0], baseline[0]);

        // ⚠️ 片が W に届かなければ、その片は 1 度も評価されない (直後の片が短い場合)。
        let short_tail = detect_with_suppression(
            &keys,
            &feat_ts_range(0, 70_000, 1_000),
            &suppressed,
            &config,
        );
        assert_eq!(
            short_tail.iter().map(|o| o.s_ms).collect::<Vec<_>>(),
            vec![31_100],
            "後ろの片 [50001, 70000] は W=30000 に届かず評価されない"
        );
    }
}
