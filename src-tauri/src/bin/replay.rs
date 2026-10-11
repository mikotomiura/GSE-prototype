//! gse-replay — セッション NDJSON リプレイ CLI (Phase 0 P0-4)
//!
//! 既存の NDJSON セッションログを入力に、`analysis::loop_step::step()` を
//! 再実行して `FeatSnapshot` 列を生成する。
//!
//! # 使い方
//!
//! ```text
//! gse-replay <session.ndjson>                        # stdout に JSON 配列を出力
//! gse-replay <session.ndjson> --snapshot <file>      # 既存スナップショットと完全一致比較
//! ```
//!
//! # 設計
//!
//! - 仮想時刻は 1 秒刻みでゲートを発火させつつ、イベントは NDJSON の `t`
//!   タイムスタンプそのものを `step()` に渡す。
//! - `ReplayEvent` は `logger::LogEntry` とは独立した Deserialize 専用 enum。
//!   書き出しと読み込みの責務を分離し、NDJSON のフィールド名 (`t` / `vk` /
//!   `press` 等) に一致させる。
//! - ime_open は NDJSON の `ime_state.on` を追跡して `step()` 引数に渡す。
//! - 出力 JSON は `serde_json::to_string_pretty`（可読性重視、`diff` 容易）。
//!
//! # 関連
//!
//! - `docs/architecture.md` §4.7 沈黙 3 状態機構
//! - `.steering/20260414-improvement-roadmap/design.md` §0.2

use std::fs::File;
use std::io::{BufRead, BufReader, Write};
use std::path::{Path, PathBuf};
use std::process::ExitCode;

use gse_next_lib::analysis::anonymize::KeyCategory;
use gse_next_lib::analysis::calibration_eval::{
    compute_calibration_metrics, format_calibration_pretty, is_valid_opaque_id, AggSpec,
    ProbeRecord, ProbeSourceKind, QuadrantKind, SessionData, SkipReasonKind, TrackKind,
    VignetteRecord, HOLDOUT_CALIBRATION_SESSIONS,
};
use gse_next_lib::analysis::engine::{CognitiveStateEngine, HMM_VERSION};
use gse_next_lib::analysis::feat_offline::{ImeShadowEvent, Pole, PoleInputs};
use gse_next_lib::analysis::features::InputEvent;
use gse_next_lib::analysis::heads::TaskDomain;
use gse_next_lib::analysis::intervention::InterventionThresholds;
use gse_next_lib::analysis::intervention_eval::{
    compute_correction_floor_report, compute_intervention_metrics, compute_intervention_sweep,
    compute_nudge_diagnostic, format_correction_floor_pretty, format_intervention_pretty,
    format_intervention_sweep_pretty, format_nudge_diagnostic_pretty, SweepInput,
    DEFAULT_DEFER_RECOVERY_WINDOW_MS, DEFAULT_SWEEP_NUDGE_NEED,
};
use gse_next_lib::analysis::loop_step::{
    step, AnalysisState, FeatSnapshot, LoopInput, ENGINE_TICK_MS,
};
use gse_next_lib::analysis::metrics::{
    compute_outcome_metrics, compute_range_metrics, compute_session_metrics, format_pretty,
    segment_stuck_episodes, KeyPress, LabelClass, OutcomeConfig, PasteEvent, RangeLabel,
    UserLabelEvent,
};
use gse_next_lib::logger::TaskKind;

/// 入力 NDJSON のサイズ上限 (500 MB)。
///
/// `BufReader::lines()` + `Vec<ReplayEvent>` 蓄積で読むため、
/// 上限なしだとメモリ枯渇で OOM する可能性がある (security-checker MEDIUM 指摘)。
/// 10 分セッションの NDJSON は通常 数 MB なので 500 MB は十分広いバッファ。
const MAX_SESSION_BYTES: u64 = 500 * 1024 * 1024;

/// `--features` が許す tick 数の上限 (= 1 Hz で約 11.5 日ぶん)。
///
/// ⚠️★★★ **`MAX_SESSION_BYTES` では防げない**別種の暴走を止めるための上限である。
/// tick 数は**入力のバイト数ではなく時刻スパンに比例する**ので、
/// ★ 実測 (2026-09-15): **251 バイト・2 行**の NDJSON に `t=0` と `t=1e8` を並べるだけで
/// **100,001 行**が出た。epoch 混入・壁時計の前方跳躍 (**ADR-030 D9**)・セッション連結の
/// いずれでも発火しうる。⚠️ ギャップを黙って潰さず `Err` で止める (D9 の危険側に落とさない)。
const MAX_FEATURE_TICKS: usize = 1_000_000;

/// `--features` (issue 007・`Q`) が許す `meta.capabilities` の直列化後サイズの上限 (バイト)。
///
/// ⚠️★★★ 2026-09-18 (判断 24・security-checker LOW-3): JSON オブジェクトでない、または
/// この上限を超えるものは「宣言が壊れている」とみなし `null` に倒さず `Err` にする
/// (`null` に倒すと「宣言が無い」と誤報になる)。
///
/// ★ 2026-09-20 (封筒・判断 3): 導入時の理由は「`capabilities` が tick 数ぶん全行へ複製され、
/// 出力 JSON が複製ぶん膨らむ」ことだった。⚠️ **その理由は封筒への移動で消えた**
/// (値は 1 回しか出ない)。★ それでも上限は残す —— **被験者が編集しうる入力**
/// (O1 の NDJSON) を無制限に読み込まないため。
const MAX_CAPABILITIES_BYTES: usize = 4096;

/// `--features` の封筒が `meta` から複写する**文字列**フィールドの上限 (バイト)。
///
/// ⚠️★★★ 2026-09-20 追加 (security-checker M1)。★ 対象は `hmm_version` / `app_version` /
/// `g1_mode` / `o1_mode` / `keyboard_layout`。
/// ⚠️ 旧版は長さも文字種も無制限に複写していた —— ★ 同じ `meta` 行の `capabilities` には
/// [`MAX_CAPABILITIES_BYTES`] があるのに、こちらには何も無かった。
///
/// ★ 実際に書かれる値は semver (`"0.5.0"`) / enum (`"g1"`) / レイアウト識別子で、
/// いずれも数十バイト。256 は十分広い。
///
/// ⚠️★★★ **超過は `Err`（`--features` は exit 1）。`None` に倒さない。**
/// ★ 倒すと出力だけを見て「未宣言」と「壊れた長大値」が区別できなくなる
/// (2026-09-20・Codex `/cross-review`)。`capabilities` と同じ規律である ——
/// **「無い」は `None` / 「壊れている」は `Err`**。
const MAX_META_STRING_BYTES: usize = 256;

/// `provenance.source_sha256_prefix` に出す 16 進の桁数 (= 8 バイトぶん)。
///
/// ⚠️★★★ **フィールド名に `_prefix` を付けている** (2026-09-20・Codex `/cross-review` 2 巡目) ——
/// ★ `source_sha256` だと**完全な SHA-256 が載っている**と読まれる。載っているのは先頭だけである。
///
/// ★ 目的は「同じ入力かどうか」の同定であって暗号学的な衝突耐性ではない。
/// 64 桁を丸ごと出しても人が読めないので先頭だけを出す。
const SOURCE_SHA256_HEX_CHARS: usize = 16;

/// `--features` 出力の封筒 (起票 2・判断 25 #14 逐語 `{ provenance, config, rows }`)。
///
/// ⚠️★★★ **2026-09-20 以前はトップレベルが `FeatureRow` の配列だった。**
/// ★ 配列のままだと**複数セッションの出力を結合したとき、どの行がどの計器条件で
/// 取れたか失われる** (起票 2)。封筒はその 1 点を直す。
///
/// ★ 封筒は **`bin/replay.rs` が組み立てる** —— 中身は `meta` 行 / 入力ファイル /
/// CLI の設定値であり、どれも「セッションの計算」ではなく「実行の由来」だからである
/// (`analysis/feat_offline/` は OS 非依存の計算層で、ファイルパスも CLI 引数も知らない)。
#[derive(Debug, serde::Serialize)]
struct FeatureEnvelope<'a> {
    provenance: FeatureProvenance,
    config: FeatureConfigDto,
    rows: &'a [gse_next_lib::analysis::feat_offline::FeatureRow],
}

/// 「この出力を共有してはいけない」ことと、**なぜ共有できないか**を出力自身に刻む
/// (起票 5・判断 5)。
///
/// ⚠️★★★ **規約は前から在ったが、機械的な門が無かった** —— `docs/glossary.md` の
/// 「特徴行」に逐語「中間成果物であり `gse-dataset` へは共有しない」と書いてあり、
/// `--features` の usage にも書いたが、**検査器が拾える鍵がどこにも無かった**。
/// ★ `.gitignore` に慣用ファイル名を足すのは**名前依存なので代替にならない**
/// (起票 5 の逐語)。→ 中身に鍵を置く。
///
/// ★ `scripts/check_no_feature_output.sh` がこのマーカーを探す。
#[derive(Debug, serde::Serialize)]
struct SharingMarker {
    /// ★ 固定値 `"prohibited"`。⚠️ **真偽値にしない** —— `false` が書ける形は
    /// 「共有してよい `--features` 出力がありうる」と読まれる。そういう出力は無い。
    gse_dataset: &'static str,
    /// ⚠️ `t_ms` を含む全行が `anonymize.rs` を**一度も通っていない**という事実。
    anonymized: bool,
    /// ⚠️ `t_ms` が**絶対 epoch ms** であるという事実 (セッション相対ではない)。
    absolute_epoch_ms: bool,
    /// 規約の在処 (逐語ではなく参照。★ 文言の SSOT は `docs/glossary.md` 側)。
    rule: &'static str,
}

impl Default for SharingMarker {
    fn default() -> Self {
        Self {
            gse_dataset: "prohibited",
            anonymized: false,
            absolute_epoch_ms: true,
            rule: "docs/glossary.md 特徴行",
        }
    }
}

/// 封筒の `provenance` —— 「どの計器条件で・どの入力から・何が出したか」。
///
/// ⚠️★★★ **載せられるのは NDJSON から読めるものだけである。**
/// ★ 起票 2 は「OS」も挙げていたが、`meta` 行に `os` は**無い** (`logger.rs::write_meta_start`
/// を 2026-09-20 に実測)。それを足すのは**計器の変更** (起票 1・ADR-032 の領域) であり、
/// ここで推測して埋めない。
#[derive(Debug, serde::Serialize)]
struct FeatureProvenance {
    sharing: SharingMarker,
    /// ★ 固定値。どのツールが出したか。
    tool: &'static str,
    /// このバイナリの `CARGO_PKG_VERSION`。
    ///
    /// ⚠️★★★ **生成時刻 (`generated_at`) は載せない** (判断 7) —— 載せると
    /// 同じ入力から同じ出力が出なくなり、「出力が変わらないこと」を検査できなくなる
    /// (`reproducibility-discipline` と衝突する)。いつ生成したかは mtime で足りる。
    tool_version: &'static str,
    /// 入力 NDJSON のファイル名 (⚠️ **ディレクトリは含めない**)。
    ///
    /// ⚠️ 実セッションでは参加者 ID (`..._P003.ndjson`) を含みうる。★ それを承知で
    /// 載せる (判断 4) —— 入力は研究者の手元にあるファイルの名前であり、
    /// **新しい漏洩先を作らない**。一方 `rows` には個人を混ぜないという規律は狭めない。
    source_basename: String,
    /// 入力 NDJSON の SHA-256 先頭 [`SOURCE_SHA256_HEX_CHARS`] 桁。
    /// ★ 名前が変わっても同じ入力を同定するため。
    source_sha256_prefix: String,
    /// 以下は `meta`(session_start) 行から読む。★ 行が無い / キーが無いなら `null`。
    /// ⚠️ **欠けていても `--features` は落とさない** (旧ログ互換。`hook_health` と同じ作法)。
    session_start: Option<u64>,
    /// ⚠️ **収集時**の `HMM_VERSION`。★ `config.hmm_version` (**解析時** = このバイナリ) とは
    /// 意味が違う。古いログを新しいバイナリで読むと食い違い、**それが読めること自体が目的**。
    hmm_version: Option<String>,
    app_version: Option<String>,
    g1_mode: Option<String>,
    o1_mode: Option<String>,
    keyboard_layout: Option<String>,
    /// `meta` 行の `capabilities` を加工せずそのまま。宣言が無ければ `null`
    /// (⚠️ 空配列・空オブジェクトで埋めない)。
    ///
    /// ⚠️★★★ **2026-09-20 (判断 3) に `rows[].quality` から移した。**
    /// ★ セッション不変の事実を行ごとに複製する意味が無いため。
    /// ⚠️ 「宣言が無い」という事実は tick 単位の欠測理由として意味を持つので、
    /// `rows[].quality.missing_reasons` の `"capability_undeclared"` は**そのまま残る**。
    capabilities: Option<serde_json::Value>,
    /// 観測区間の列 (ADR-030 D8 (b-2))。`feat` 行の**存在**だけから決まる
    /// (`stall_onset::observed_intervals`)。`feat` 行が 1 本も無ければ**空配列**
    /// (⚠️ `null` にしない —— 「観測区間が 1 つも無い」は観測できた事実である)。
    /// ★ 2026-10-08 (事前宣言 v1.2・ADR-030 補訂 4): 使う `feat` 行は、長い穴とファイルの最後の直前の
    /// 無入力の行を落とした**後の列**である (`idle_trim`・下の [`Self::idle_trim`])。
    ///
    /// ⚠️★★★ **極によって変わる** (ADR-030 D3・`config.pole`)。
    /// ★ 上の定義は `baseline` (極 A ＝ 何も抑制しない) のもの。極 B (ポインタ活動区間を抑制) では
    /// 抑制区間を除いた **実際に評価した区間**を載せる (`decisions.md` 判断 7・issue 006) —— 起票 20 (a) の
    /// 目的 (打ち切りまでの追跡時間 `b − o`) から見ても、評価していない区間は追跡時間に数えられない。
    /// ⚠️ フィールド名は変えない。**どの極の区間か**は封筒の `config.pole` から読む
    /// (⚠️ 別の極の出力と区間を突き合わせるときは、先に `config.pole` が一致することを確かめる)。
    ///
    /// ★★★ **なぜ封筒に載せるか** (2026-09-21・研究者判断・`blockers.md` 起票 20 (a)):
    /// `restart` (`T1d`) の `restop_ms` が `null` の行は**右側打ち切り**だが、
    /// ⚠️ **打ち切りまでの追跡時間 (`b − o`) が行からは読めない** —— `b` が出力に無いため。
    /// 生存解析 (`ADR-031:52` 逐語「主 criterion: … **再停止までの時間** …」) は
    /// `(時間, 事象)` の組を要するので、打ち切り行を捨てるしかなくなっていた。
    /// ★ 区間はセッション不変なので**封筒が 1 回だけ持つ**のが正しい (⚠️ 行ごとに複製しない ——
    /// `capabilities` を行から封筒へ移した判断 3 と同じ理屈)。
    ///
    /// ⚠️★★★ **新しい露出ではない。** 穴の位置と長さは
    /// `rows[].quality.observability_mask.feat` が**既に tick ごとに出している** (issue 007)。
    /// ★ 削除 / 一時停止 / 計器欠損の**原因ラベルは 1 つも無い**まま (ADR-030 D8 (b-2))。
    ///
    /// ⚠️★★★ **極 B ではこの列自体の意味が変わる** (security-checker LOW・issue 006)。
    /// baseline (極 A) では「`feat` 行の穴」(★ 2026-10-08 から: 無入力の末尾の前処理の後の穴。
    /// 前処理は**全極で** `key` / `pointer_bin` 行の時刻を読むので、baseline でも長い穴とファイルの最後ごとに
    /// 最後の入力の秒が 1 つ右端に出る・下の [`IdleTrimDto`]) を表すが、極 B では
    /// **「観測区間 − ポインタ活動区間」= 評価区間**を表す。★ そのため、極 B の
    /// `observed_intervals` から baseline の `observed_intervals` を差し引くと、
    /// **ポインタ活動があった秒の時系列** (1 秒ビン単位・活動の**存在のみ**、
    /// `moved` / `buttons` / `wheel` の値は含まない) を読み取れる —— ゼロ抑制された
    /// `pointer_bin` 行そのものは封筒に出していないが、極 B と baseline の区間差分という
    /// **間接的な形**で活動の有無と大まかなタイミングが漏れる。★ 欄は分けない (issue 006
    /// の裁定): `pole == "pointer_b"` の出力を baseline と突き合わせて読む側の責任とする。
    observed_intervals: Vec<ObservedIntervalDto>,
    /// 観測区間を作る前に落とした `feat` 行の量 (事前宣言 v1.2 §6.1・`analysis::feat_offline::idle_trim`)。
    /// ★ 極によらない (前処理は極の前に 1 回だけ掛かる)。`config.idle_trim_max_ms == 0` なら 0 行・空配列。
    idle_trim: IdleTrimDto,
    /// 長い無入力の前処理で落とした `feat` 行の量 (事前宣言 v1.3 §7.1・`idle_trim::input_gap_trim`)。
    /// ★ `idle_trim` が先に落とした行は数えない (削った行の合計は 2 つの和)。極によらない。
    /// `config.idle_trim_input_gap_ms == 0` なら 0 行・空配列。`spans` は 1 本 = 1 つの無入力の区間。
    /// 露出は [`IdleTrimDto`] と同じ種類 (左端は入力を含む秒の直後・右端は次の入力の秒の直前。
    /// ⚠️ ファイルの最初・最後に接する区間は、その境の行を含む)。加えて次が読める (security-checker LOW・2026-10-11):
    /// - 右端からは (区間の中で `feat` 行が途切れていなければ)、無入力の後の**最初の入力の秒**が読める。解放の行・キーを解決できない行・`pointer_bin` 行なら、
    ///   `rows[]` の `activity` には出ない秒である。
    /// - 「その区間に `key` も `pointer_bin` も `idle_trim_input_gap_ms` 以上無かった」という不在。24 時間のファイルでは、
    ///   `spans` の列がそのまま 1 日の入力の有無の時刻表 (長い不在の時刻) として読める。
    ///
    /// ⚠️ 落とした行は `rows[]` から消えるので、封筒全体から読める量はむしろ減る。封筒は `gse-dataset` へ共有しない。
    input_gap_trim: IdleTrimDto,
}

/// [`FeatureProvenance::idle_trim`] と [`FeatureProvenance::input_gap_trim`]。
///
/// 落とした範囲は `observed_intervals` の穴と `rows[].quality.observability_mask.feat` からも読める。
/// 範囲の左端は「最後の入力を含む秒の直後」なので、長い穴とファイルの最後ごとに次が baseline の出力にも出る
/// (security-checker LOW・2026-10-09 に訂正):
/// - 最後の入力が、キーを解決できた**押下**なら `rows[]` の `activity` から既に読める秒である。
///   ⚠️ **解放**の行・キーを解決できない行なら、`activity` には出ない秒 (押下から 1 tick 以内のずれ) が新しく出る。
/// - ⚠️ `pointer_bin` 行なら、**長い穴の直前の最後のポインタ活動の秒**が出る (存在だけ・`moved` などの値は出ない。
///   極 B の `observed_intervals` の差分と同じ種類の間接的な露出)。
/// - 30 分の上限で切られたときは、逆に「その前の 30 分は `key` も `pointer_bin` も無かった」という不在が読める。
///
/// 原因のラベルは無い (ADR-030 D8 (b-2))。封筒は `gse-dataset` へ共有しない (`sharing`)。
#[derive(Debug, serde::Serialize)]
struct IdleTrimDto {
    /// 落とした `feat` 行の数。
    dropped_feat_rows: u64,
    /// 落とした行のつながり (`[a_ms, b_ms]`・両端は落とした最初と最後の `feat` 行の時刻)。
    /// ★ 1 本 = 1 つの終わりの点 (長い穴の直前・ファイルの最後) で落とした行。本数 = 行を落とした終わりの点の数。
    /// ⚠️ 短い穴をまたぐことがあるので、`b_ms − a_ms` を削った時間として読まない (それは `dropped_feat_rows`)。
    spans: Vec<ObservedIntervalDto>,
}

/// 観測区間 1 つ (`[a_ms, b_ms]`・**両端を含む**)。
///
/// ⚠️ 右端 `b_ms` は**確定扱い**である (`stall_onset` の `t0 <= b` と対称)。
#[derive(Debug, serde::Serialize)]
struct ObservedIntervalDto {
    a_ms: u64,
    b_ms: u64,
}

/// 封筒の `config` —— この出力を再現するのに要る設定値。
///
/// ★ 判断 25 #13 (`W` / `q` / `B` / `hole_gap_ms` / `warmup_count` / 分位点の推定法 /
/// `T1a` の窓 を P1 前に 1 本の宣言文書で凍結し、**同時に CLI 注入を作る**) の**受け皿**である。
/// ★ 値は既定で**凍結 JSON (`prereg/p1-episode.json`)** から来る。`--feature-config` /
/// `--set` で外れた値は `overrides` に**明示的に**残る ([`ResolvedFeatureConfig`])。
///
/// ⚠️★★★ **θ_person の分位点はここに入れない** —— θ は**設定ではなく結果**
/// (ADR-008 D4 の `within_session_adaptive`) であり、行の `stall_onset.theta_person_ms` が持つ。
/// 設定と結果を同じ箱に入れない。
#[derive(Debug, serde::Serialize)]
struct FeatureConfigDto {
    /// 条件 A の因果窓長 (ms・ADR-030 D4)。
    w_ms: u64,
    /// θ_person の分位点 (ADR-030 D4)。
    q: f64,
    /// `t0` 直後の buffer (ms・ADR-030 D2)。
    b_ms: u64,
    /// 条件 A の産出判定閾値 (ADR-030 D3)。
    net_diff_min: u64,
    /// 観測区間を切る閾値 (ms・ADR-030 D8 (b-2))。
    hole_gap_ms: u64,
    /// θ の標本数の下限 (ADR-030 D4 点 1)。
    /// ★ 凍結 JSON 経路では常に数値 (`validate` が 0 を拒否する)。`null` は旧出力 (下限なし) との互換のため型に残す。
    warmup_count: Option<usize>,
    /// θ_person の分位点の推定法 (P1 事前宣言 §1・現状 `"nearest_rank"` だけが実装されている)。
    theta_estimator: String,
    /// `T1a` の窓長 (ms・P1 事前宣言 §1)。★ 窓の実装は issue 003。ここは値の記録だけ。
    t1a_window_ms: u64,
    /// 前処理の「長い穴」とみなす `feat` 行の間隔の下限 (ms・P1 事前宣言 v1.2 §6.2)。
    idle_trim_min_gap_ms: u64,
    /// 前処理で戻す幅の上限 (ms・P1 事前宣言 v1.2 §6.2)。`0` は前処理なしの実行 (§6.4)。
    idle_trim_max_ms: u64,
    /// 長い無入力の前処理で、落とす無入力の長さの下限 (ms・P1 事前宣言 v1.3 §7.2)。`0` は前処理なし (§7.4)。
    idle_trim_input_gap_ms: u64,
    /// この出力の**極** (ADR-030 D3・[`Pole::as_str`])。★ 1 実行 1 極で、極を持つのは**封筒だけ**
    /// (行には載せない・判断 3)。⚠️ 上の設定 11 値とは別の軸で、`--set` では変えられない (`--pole` だけ)。
    pole: &'static str,
    /// この入力で、上の極が**計算できたか**。★ 常に出る (`baseline` は常に `true`)。
    /// ⚠️ 極 B / 極 M+ の判定は**入力に依存する** (`capabilities` の宣言 / 修飾キー行の有無)。
    /// ★ 極 M+ は**入力ファイル (セッション) 単位**で、解決後の `KeyCategory` が `Modifier` の `key` 行が
    /// 1 本も無ければ `false` (`decisions.md` 判断 13)。極 B の判定は issue 006 が実装する
    /// (★ それまで極 B は `--pole` が exit 1 で止める)。
    ///
    /// ⚠️★★★ **`false` のとき、行の `stall_onset` / `restart` は baseline と恒等である** —— 修飾キーの行が 0 本なら
    /// 押下区間が 1 つも無く、極 M+ は構造的に極 M− と同じ値になる。★ 値で埋めない (別の値を出さない)。
    pole_applicable: bool,
    /// `pole_applicable == false` の理由コード。★ 適用可のとき `null`。⚠️ 極ごとに判定の根拠が違うので、
    /// 理由の語も別にする (`no_pointer_capability` / `no_pointer_rows` = 極 B・issue 006・
    /// `decisions.md` 判断 26 / `no_modifier_rows` = 極 M+)。
    ///
    /// ⚠️★★★ `no_modifier_rows` は「**計器が無かった**」(2026-08-23 より前のログ・macOS) と
    /// 「**押さなかった**」を**区別しない** (`meta` に `os` が無く、`capabilities` に修飾キーの計器を表す項目も無い)。
    /// ★ 過剰拒否だが**情報は失わない** (行が 0 本なら極 M+ = 極 M− で、上下界の幅への寄与がゼロ)。
    /// ⚠️★★★ `no_pointer_rows` も同型 —— `capabilities.rs:244-245` 逐語「0 行は判定不能」のとおり、
    /// 宣言はコンパイル時の `POINTER_AVAILABLE` でしかなく、実行時の `observe::start` は
    /// 設置に失敗しうる。「活動が無かった」と「設置に失敗した」を区別できないので、
    /// 0 行を所見として `true` にはしない (`decisions.md` 判断 26・極 M+ の判断 13 と揃えた)。
    /// ⚠️ `pointer_evidence_not_supplied`（極 B）／`modifier_evidence_not_supplied`（極 M+）は
    /// **防御の値**であり、実際には出ない (未実装の極は出力の前に止まる。呼び出し側が証拠を
    /// 渡し忘れたときだけ出る。★ 旧称 `not_implemented` は「未実装」と誤読されるため改名した
    /// — code-reviewer LOW)。
    pole_not_applicable_reason: Option<&'static str>,
    /// 極 M+ の判定に使った入力ファイルの**修飾キーの `key` 行数** (`decisions.md` 判断 13 逐語
    /// 「封筒に理由コード (`no_modifier_rows`) と `modifier` 行数を刻み」)。★ 極 M+ 以外では数えないので `null`。
    /// ⚠️ 0 のとき「計器が無かった」と「押さなかった」は区別できない (上の理由コードの doc)。
    pole_modifier_rows: Option<u64>,
    /// 極 M+ の区間の健全性: 観測区間の右端で**打ち切られた**押下区間の本数
    /// (`decisions.md` 判断 24・`stall_onset::ModifierIntervals::truncated_at_right_edge`)。
    /// ★ 極 M+ 以外では数えないので `null`。⚠️ 値の出所は既存の件数 (`collect_modifier_intervals`
    /// が `tracing::warn!` へ出しているのと同じもの) —— warn はそのまま残す。
    /// ⚠️ 0 より大きいと、その本数ぶん区間が本来より短く（＝除外が少なく）数えられている
    /// (`pole_applicable=true` のまま出力は見た目正常だが、内部で打ち切りが起きている)。
    pole_modifier_truncated: Option<u64>,
    /// 極 M+ の区間の健全性: 先行する press が無い release（孤立）の件数
    /// (`decisions.md` 判断 24・`stall_onset::ModifierIntervals::orphan_releases`)。
    /// ★ 極 M+ 以外では数えないので `null`。
    pole_modifier_orphan_releases: Option<u64>,
    /// 極 B の判定に使った入力ファイルの **`pointer_bin` 行数**。★ 極 B 以外では数えないので `null`。
    /// ⚠️★★★ **宣言があっても行が 0 本なら `pole_applicable == false`／理由 `no_pointer_rows`**
    /// (`decisions.md` 判断 26・2026-09-25 是正) —— `capabilities.rs:244-245` 逐語「0 行は判定不能」の
    /// とおり、宣言はコンパイル時の `POINTER_AVAILABLE` でしかなく、実行時の `observe::start` は
    /// 設置に失敗しうる。「活動が無かった」と「設置に失敗した」を**区別できない**ので、0 行を
    /// 所見として `true` にはしない (★ 極 M+ の判断 13 と揃えた)。
    /// ★ 宣言が無い入力 (`no_pointer_capability`) で 0 より大きければ、宣言と行が食い違う壊れたログである
    /// (⚠️ その場合も抑制は**しない** —— 適用不可の出力は baseline と恒等)。
    pole_pointer_rows: Option<u64>,
    /// 採用した事前宣言の `id` / `version` / 内容の SHA-256 先頭桁 (★ 何を読んだかの同定)。
    prereg_id: String,
    prereg_version: String,
    prereg_sha256_prefix: String,
    /// `"frozen"` (埋め込みの凍結 JSON) / `"file"` (`--feature-config`)。
    config_source: &'static str,
    /// 凍結値から**外れた**キーだけ (無指定なら空配列)。⚠️ 外れていない `--set` は載せない。
    overrides: Vec<ConfigOverride>,
    /// [`MAX_FEATURE_TICKS`]。★ この実行に効いていた上限値を記録する。
    ///
    /// ⚠️ **「上限で止められたか」はこれ単独では判別できない** (2026-09-20・code-reviewer LOW)
    /// —— 上限に当たった場合は `--features` が `Err` で **exit 1** し、そもそも出力が無い。
    /// ★ 出力がある以上 `rows.len() <= max_feature_ticks` であり、
    /// ちょうど `max_feature_ticks` 行のセッションと切り捨てを区別する必要は生じない。
    max_feature_ticks: usize,
    /// ⚠️ **解析時** (このバイナリ) の `HMM_VERSION`。`provenance.hmm_version` (収集時) と別物。
    hmm_version: &'static str,
    /// tick 幅 (`loop_step::ENGINE_TICK_MS`)。
    engine_tick_ms: u64,
    /// 「単純 pause」の閾値 (`features::PAUSE_THRESHOLD_MS`)。
    pause_threshold_ms: u64,
}

/// P1 事前宣言の凍結 JSON (`src-tauri/prereg/p1-episode.json`)。**実行ファイルへ埋め込む。**
///
/// ⚠️★★★ 埋め込みが正である (実行時にファイルを探しに行かない)。★ 理由: 出力の
/// `provenance.tool_version` と凍結値が 1 対 1 になる —— 実行時に読むと、同じバイナリが
/// 置かれた場所次第で違う値を使いうる。別の値を使いたいときは `--feature-config` で
/// **明示的に**指す (`config_source == "file"` が出力に刻まれる)。
const FROZEN_P1_EPISODE_JSON: &str = include_str!("../../prereg/p1-episode.json");

/// `--feature-config` で読む外部ファイルの上限 (バイト)。凍結 JSON は 2 KiB 程度。
const MAX_FEATURE_CONFIG_BYTES: u64 = 64 * 1024;

/// `--set` が受け取れるキー (= 凍結 JSON の `operational` の 11 キー・事前宣言 v1.2 で 2 キー、v1.3 で 1 キー足した)。
const P1_OPERATIONAL_KEYS: [&str; 11] = [
    "w_ms",
    "q",
    "b_ms",
    "hole_gap_ms",
    "warmup_count",
    "theta_estimator",
    "t1a_window_ms",
    "net_diff_min",
    "idle_trim_min_gap_ms",
    "idle_trim_max_ms",
    "idle_trim_input_gap_ms",
];

/// `idle_trim_max_ms` / `idle_trim_min_gap_ms` / `idle_trim_input_gap_ms` の上限 (24 時間・事前宣言 v1.2 §6.1・v1.3 §7.1)。
/// ⚠️ 自己 DoS の門ではなく、**24 時間を超える値 (明らかな桁の誤り) だけ**を止める。凍結値 60000 の
/// 1440 倍未満の誤り (例: 1000 倍の 60000000 = 16.7 時間) は止めない —— その値は封筒の `overrides` に残る
/// (研究者裁定 2026-10-09・上限を締めない)。
const IDLE_TRIM_LIMIT_MS: u64 = 24 * 60 * 60 * 1000;

/// 凍結 JSON の `operational` (P1 事前宣言 §1 の 8 値 ＋ v1.2 §6.2 の 2 値 ＋ v1.3 §7.2 の 1 値)。
///
/// ⚠️ `deny_unknown_fields` —— 未知のキーを黙って捨てると、綴りを間違えた設定が
/// 「効いたつもり」で走る (fail-closed)。
#[derive(Debug, Clone, PartialEq, serde::Deserialize)]
#[serde(deny_unknown_fields)]
struct P1Operational {
    w_ms: u64,
    q: f64,
    b_ms: u64,
    hole_gap_ms: u64,
    warmup_count: u64,
    theta_estimator: String,
    t1a_window_ms: u64,
    net_diff_min: u64,
    /// ⚠️ 必須 (`default` を付けない) —— 1.0.0 の形の `--feature-config` は前処理の値を持たないので拒否する
    /// (前処理を黙って無効にした出力を作らない)。
    idle_trim_min_gap_ms: u64,
    idle_trim_max_ms: u64,
    /// ⚠️ 必須 —— 1.1.0 の形の `--feature-config` は長い無入力の前処理の値を持たないので拒否する。
    idle_trim_input_gap_ms: u64,
}

/// 凍結 JSON のうち本ツールが読む部分 (`status` / `search_*` などは読まない)。
#[derive(Debug, serde::Deserialize)]
struct P1PreregFile {
    id: String,
    version: String,
    operational: P1Operational,
}

/// 凍結値から外れたキー 1 つ (`--feature-config` / `--set` の結果)。
#[derive(Debug, Clone, PartialEq, serde::Serialize)]
struct ConfigOverride {
    key: &'static str,
    /// 凍結 JSON の値。
    frozen: serde_json::Value,
    /// この実行で使った値。
    value: serde_json::Value,
}

impl P1Operational {
    /// `(キー, JSON 値)` の列 (`P1_OPERATIONAL_KEYS` と同じ順)。overrides の比較に使う。
    fn as_pairs(&self) -> [(&'static str, serde_json::Value); 11] {
        [
            ("w_ms", self.w_ms.into()),
            ("q", self.q.into()),
            ("b_ms", self.b_ms.into()),
            ("hole_gap_ms", self.hole_gap_ms.into()),
            ("warmup_count", self.warmup_count.into()),
            ("theta_estimator", self.theta_estimator.clone().into()),
            ("t1a_window_ms", self.t1a_window_ms.into()),
            ("net_diff_min", self.net_diff_min.into()),
            ("idle_trim_min_gap_ms", self.idle_trim_min_gap_ms.into()),
            ("idle_trim_max_ms", self.idle_trim_max_ms.into()),
            ("idle_trim_input_gap_ms", self.idle_trim_input_gap_ms.into()),
        ]
    }

    /// `--set <key>=<value>` を 1 件適用する。⚠️ 型が合わない値・未知のキーは `Err`
    /// (黙って無視しない)。範囲の検査は全件を適用した後の [`Self::validate`] が行う。
    fn apply_set(&mut self, key: &str, value: &str) -> Result<(), String> {
        let as_u64 = |v: &str| {
            v.parse::<u64>()
                .map_err(|_| format!("--set {key}: `{v}` は非負の整数ではない"))
        };
        match key {
            "w_ms" => self.w_ms = as_u64(value)?,
            "q" => {
                self.q = value
                    .parse::<f64>()
                    .map_err(|_| format!("--set q: `{value}` は数値ではない"))?
            }
            "b_ms" => self.b_ms = as_u64(value)?,
            "hole_gap_ms" => self.hole_gap_ms = as_u64(value)?,
            "warmup_count" => self.warmup_count = as_u64(value)?,
            "theta_estimator" => self.theta_estimator = value.to_string(),
            "t1a_window_ms" => self.t1a_window_ms = as_u64(value)?,
            "net_diff_min" => self.net_diff_min = as_u64(value)?,
            "idle_trim_min_gap_ms" => self.idle_trim_min_gap_ms = as_u64(value)?,
            "idle_trim_max_ms" => self.idle_trim_max_ms = as_u64(value)?,
            "idle_trim_input_gap_ms" => self.idle_trim_input_gap_ms = as_u64(value)?,
            _ => {
                return Err(format!(
                    "--set: 未知のキー `{key}` (許可: {})",
                    P1_OPERATIONAL_KEYS.join(", ")
                ))
            }
        }
        Ok(())
    }

    /// 物理的な範囲の検査。★ 通らない値を封筒に刻んだ出力は、下流が「計算できた」と誤読する。
    fn validate(&self) -> Result<(), String> {
        if self.w_ms == 0 {
            return Err("w_ms は 1 以上でなければならない".to_string());
        }
        if !(self.q.is_finite() && self.q > 0.0 && self.q < 1.0) {
            return Err(format!(
                "q は 0 より大きく 1 より小さくなければならない (実際: {})",
                self.q
            ));
        }
        if self.hole_gap_ms == 0 {
            return Err("hole_gap_ms は 1 以上でなければならない".to_string());
        }
        if self.warmup_count == 0 || usize::try_from(self.warmup_count).is_err() {
            return Err(
                "warmup_count は 1 以上で、この環境の usize に収まらなければならない".to_string(),
            );
        }
        if self.t1a_window_ms == 0 {
            return Err("t1a_window_ms は 1 以上でなければならない".to_string());
        }
        // ⚠️ `dispersion::pause_ms_by_window` は窓内の pause を tick ごとに具体化する
        // (`Vec<Vec<u64>>`) ので、窓を無制限に広げるとメモリが窓幅に比例して膨らむ
        // (自己 DoS 防止・security-checker LOW-1・2026-09-25)。事前宣言 (`p1-episode.json`
        // `search_space.t1a_window_ms`) の探索空間の最大は 60000ms なので、それに十分な
        // 安全マージンを取った 1 時間 (3_600_000ms) を運用上の上限に置く。
        if self.t1a_window_ms > 3_600_000 {
            return Err("t1a_window_ms は 3600000 (1 時間) 以下でなければならない".to_string());
        }
        // ⚠️ `stall_onset.rs` は `net_diff_min as i64` で比べる。`i64::MAX` を超える値は負へ丸まり、
        //   `net < net_diff_min` が常に偽になって **onset が黙って 0 本**になる (security-checker LOW・2026-09-25)。
        if self.net_diff_min == 0 || i64::try_from(self.net_diff_min).is_err() {
            return Err("net_diff_min は 1 以上で、i64 に収まらなければならない".to_string());
        }
        // ⚠️ 穴にならない間隔 (`hole_gap_ms` 以下) の前で削ると、観測区間の内側の沈黙まで落とす
        //   (事前宣言 v1.2 §6.1 の検査)。
        if self.idle_trim_min_gap_ms <= self.hole_gap_ms {
            return Err(format!(
                "idle_trim_min_gap_ms ({}) は hole_gap_ms ({}) より大きくなければならない",
                self.idle_trim_min_gap_ms, self.hole_gap_ms
            ));
        }
        if self.idle_trim_max_ms > IDLE_TRIM_LIMIT_MS {
            return Err(format!(
                "idle_trim_max_ms は {IDLE_TRIM_LIMIT_MS} (24 時間) 以下でなければならない"
            ));
        }
        // ⚠️ `idle_trim_min_gap_ms` が大きすぎると長い穴の前の削りが効かなくなり、ファイルの最後だけが削られる
        //   (code-reviewer L-7 / security-checker L3)。`idle_trim_max_ms` と同じ上限で、24 時間を超える値だけを止める
        //   (それ未満の誤りは `overrides` に残る・[`IDLE_TRIM_LIMIT_MS`])。
        if self.idle_trim_min_gap_ms > IDLE_TRIM_LIMIT_MS {
            return Err(format!(
                "idle_trim_min_gap_ms は {IDLE_TRIM_LIMIT_MS} (24 時間) 以下でなければならない"
            ));
        }
        // ⚠️ 長い無入力の前処理 (事前宣言 v1.3 §7.1)。`0` は前処理なし。それ以外は「長い穴」
        //   (`idle_trim_min_gap_ms`) 以上 —— それより短い無入力を落とすと、P1 が見たい停滞 (`W` の桁) そのものを削る。
        //   上限は他の前処理の値と同じ 24 時間 (それを超える桁の誤りだけを止める)。
        if self.idle_trim_input_gap_ms != 0
            && (self.idle_trim_input_gap_ms < self.idle_trim_min_gap_ms
                || self.idle_trim_input_gap_ms > IDLE_TRIM_LIMIT_MS)
        {
            return Err(format!(
                "idle_trim_input_gap_ms ({}) は 0 か、idle_trim_min_gap_ms ({}) 以上 {IDLE_TRIM_LIMIT_MS} (24 時間) 以下でなければならない",
                self.idle_trim_input_gap_ms, self.idle_trim_min_gap_ms
            ));
        }
        // ⚠️ 実装済みの推定法だけを通す。未実装の名前を封筒に刻むと、出力が嘘をつく。
        if self.theta_estimator != "nearest_rank" {
            // ⚠️ 外部ファイル由来の文字列は端末へそのまま出さない（`echo_untrusted`: 80 字で切り詰め・`{:?}` でエスケープ）。
            return Err(format!(
                "theta_estimator は \"nearest_rank\" だけが実装されている (実際: {})",
                echo_untrusted(&self.theta_estimator)
            ));
        }
        Ok(())
    }
}

/// 解決済みの `--features` 設定 (凍結値 → `--feature-config` → `--set` の順に重ねた結果)。
#[derive(Debug, Clone)]
struct ResolvedFeatureConfig {
    operational: P1Operational,
    prereg_id: String,
    prereg_version: String,
    prereg_sha256_prefix: String,
    config_source: &'static str,
    overrides: Vec<ConfigOverride>,
    /// ★ 極 (ADR-030 D3)。⚠️ `operational` の 11 値とは**別の軸**で、`--set` / `--feature-config` では
    /// 変えられない (凍結 JSON に極は無い)。`resolve_feature_config` は常に `Baseline` で返し、
    /// `--pole` の値は [`Self::with_pole`] で足す。
    pole: Pole,
}

impl ResolvedFeatureConfig {
    /// 極を差し替える。⚠️ 呼ぶ前に [`resolve_pole`] を通すこと (未実装の極を持ち込まない)。
    fn with_pole(mut self, pole: Pole) -> Self {
        self.pole = pole;
        self
    }

    /// 検出器へ渡す設定へ写す。⚠️ 呼ぶ前に `validate` 済みであること (`resolve_feature_config` が保証)。
    fn stall_onset_config(&self) -> gse_next_lib::analysis::feat_offline::StallOnsetConfig {
        let o = &self.operational;
        gse_next_lib::analysis::feat_offline::StallOnsetConfig {
            w_ms: o.w_ms,
            q: o.q,
            b_ms: o.b_ms,
            net_diff_min: o.net_diff_min,
            hole_gap_ms: o.hole_gap_ms,
            // `validate` が usize に収まることを確かめている。
            warmup_count: usize::try_from(o.warmup_count).ok(),
            t1a_window_ms: o.t1a_window_ms,
            pole: self.pole,
        }
    }
}

/// `--pole` の値を極へ解決する。★ 出力を 1 バイトも書く前に呼ぶこと (fail-closed)。
///
/// ⚠️★★★ **止める 3 つ** (いずれも `Err` = 呼び出し側は exit 1・stdout は空):
/// 1. `--features` 以外での指定 —— 他のモードは極を読まない。★ 指定を黙って無視すると
///    「極 B で計算した」つもりの出力が baseline になる。
/// 2. 未知の名前 —— ⚠️ 近い名前へ丸めない。
/// 3. 未実装の極 ([`Pole::is_implemented`]) —— ⚠️ **黙って baseline の値を返さない**
///    (出力が嘘をつき、極の比較が無意味になる)。
///
/// 未指定は `Baseline` (現行の計算そのもの・行の値は `--pole` 導入前と一致する)。
fn resolve_pole(features: bool, raw: Option<&str>) -> Result<Pole, String> {
    let Some(name) = raw else {
        return Ok(Pole::Baseline);
    };
    if !features {
        return Err("--pole requires --features".to_string());
    }
    let pole = Pole::from_name(name).ok_or_else(|| {
        let allowed: Vec<&str> = Pole::ALL.iter().map(|p| p.as_str()).collect();
        // ★ `{:?}` でエスケープする (制御文字・ANSI エスケープで端末表示を乱さない・security-checker LOW)。
        format!("--pole: 未知の極 {name:?} (許可: {})", allowed.join(", "))
    })?;
    if !pole.is_implemented() {
        return Err(format!(
            "--pole {name:?}: この極はまだ実装されていない (baseline の値を別の極の名前で返さないため止める)"
        ));
    }
    Ok(pole)
}

/// 封筒 `config.pole_applicable` / `pole_not_applicable_reason` の値 (`(適用可否, 理由コード)`)。
///
/// ★ 網羅 `match` (ワイルドカード無し) —— 極を足すと、ここで判定を決めるまでコンパイルが通らない。
/// `modifier_rows` は入力ファイルの**修飾キーの `key` 行数** ([`ModifierScan::rows`])。★ 極 M+ だけが読む。
/// `None` は「数えていない」 (⚠️ 「0 本」とは別) —— 極 M+ では**防御の値**で止める。
/// ⚠️ 極 B の判定 (`capabilities` の `pointer_bin`) は**この関数では確定しない** —— 入力 (`capabilities`) が
/// 要るので [`FeatureConfigDto::with_pointer_evidence`] が [`pointer_applicability`] で確定する。
fn pole_applicability(pole: Pole, modifier_rows: Option<u64>) -> (bool, Option<&'static str>) {
    match pole {
        // 極 A / 極 M− はどの入力でも計算できる (現行の計算そのもの)。
        Pole::Baseline => (true, None),
        // ⚠️ 極 B は入力 (`capabilities`) を見るまで**適用可と名乗らない** (防御の値。
        //   `with_pointer_evidence` が確定させる。呼び忘れても嘘の `true` を出さない)。
        //   ★ 旧称 `not_implemented` は「未実装」と誤読される (開通済みのため) —— 実態に
        //   合わせて改名した (code-reviewer LOW)。
        Pole::PointerB => (false, Some("pointer_evidence_not_supplied")),
        // ★ 判定単位は**入力ファイル (セッション)**・判定式は「修飾キーの行が 0 本」(判断 13)。
        Pole::ModifierMPlus => match modifier_rows {
            Some(0) => (false, Some("no_modifier_rows")),
            Some(_) => (true, None),
            // 数えずに極 M+ を名乗らせない (防御。実際には main が必ず数える)。
            // ★ 同じ理由で `not_implemented` → `modifier_evidence_not_supplied` に改名した。
            None => (false, Some("modifier_evidence_not_supplied")),
        },
    }
}

/// 封筒 `provenance.capabilities` に `pointer_bin` の**宣言があるか** (極 B の適用可否の根拠・issue 006)。
///
/// ★ `capabilities` は行種の名前の配列を群 (`unconditional` / `threshold_gated` / `config_gated`) ごとに持つ
/// オブジェクトである。**どの群に載っていても**宣言ありとする (⚠️ 群の名前を再宣言しない)。
/// ⚠️ 宣言が無いのは「**計器が無かった**」であって「活動が無かった」ではない
/// (`schema/current.json` の `pointer_bin`: 「行が無い＝活動が無かった」は宣言がある場合に限る)。
/// `None` (`capabilities` 自体が無い旧ログ) も宣言なし。
fn declares_pointer_bin(capabilities: Option<&serde_json::Value>) -> bool {
    capabilities
        .and_then(serde_json::Value::as_object)
        .is_some_and(|groups| {
            groups
                .values()
                .filter_map(serde_json::Value::as_array)
                .flatten()
                .any(|name| name.as_str() == Some("pointer_bin"))
        })
}

/// 極 B の適用可否 (`(適用可否, 理由コード)`)。★ 判定式は 3 状態 (`decisions.md` 判断 26・2026-09-25 是正):
///
/// 1. `capabilities` に `pointer_bin` の宣言が**無い** → 適用不可・`no_pointer_capability`
///    (「**計器が無かった**」)。
/// 2. 宣言は**ある**が行が **0 本** → 適用不可・`no_pointer_rows` (「**判定不能**」——
///    `capabilities.rs:244-245` 逐語「0 行は判定不能」のとおり、宣言はコンパイル時の
///    `POINTER_AVAILABLE` でしかなく、実行時の `observe::start` は設置に失敗しうる。
///    「活動が無かった」と「設置に失敗した」を区別できないので、0 行を所見として
///    `true` にはしない。★ 極 M+ の判断 13 (0 行は `not_applicable`) と揃えた)。
/// 3. 宣言があり行が **1 本以上** → 適用可・`null`。
///
/// ⚠️ 極 M+ (`no_modifier_rows`) とは**根拠が違う**ので理由の語も別にする。
/// `rows` が `None` (証拠を渡し忘れ) は防御の値 (★ 実際には呼び出し側が pole==PointerB のとき
/// 必ず数える。[`pole_applicability`] の `PointerB` 既定値と同じ語にする)。
fn pointer_applicability(declared: bool, rows: Option<u64>) -> (bool, Option<&'static str>) {
    if !declared {
        return (false, Some("no_pointer_capability"));
    }
    match rows {
        Some(0) => (false, Some("no_pointer_rows")),
        Some(_) => (true, None),
        None => (false, Some("pointer_evidence_not_supplied")),
    }
}

/// 事前宣言 JSON の `id` の最大文字数 (`^[a-z0-9][a-z0-9-]{0,63}$` = 先頭 1 + 残り 63)。
const PREREG_ID_MAX_LEN: usize = 64;

/// 事前宣言 JSON の `version` (`major.minor.patch`) の各部の最大桁数。
const PREREG_VERSION_PART_MAX_DIGITS: usize = 9;

/// 形式検査に落ちた外部の値をエラー文へ出すときの最大文字数。
/// ⚠️ 値は外部ファイル由来で、長さも中身も信用できない (端末へ制御文字を流させない・巨大な行を出さない)。
const PREREG_ECHO_MAX_CHARS: usize = 80;

/// `id` の形式: `^[a-z0-9][a-z0-9-]{0,63}$` (issue 007・`decisions.md` 判断 16)。
///
/// ⚠️ `regex` crate は足さない (新規依存は Stop)。バイトで走査するので、非 ASCII・空白・制御文字・
/// **末尾の改行** (`$` が改行の手前で止まる正規表現実装の抜け穴) は文字クラスに入らず落ちる。
fn is_wellformed_prereg_id(id: &str) -> bool {
    let bytes = id.as_bytes();
    let Some((&first, rest)) = bytes.split_first() else {
        return false;
    };
    bytes.len() <= PREREG_ID_MAX_LEN
        && (first.is_ascii_lowercase() || first.is_ascii_digit())
        && rest
            .iter()
            .all(|b| b.is_ascii_lowercase() || b.is_ascii_digit() || *b == b'-')
}

/// `version` の形式: `^[0-9]+\.[0-9]+\.[0-9]+$` (各部は 1〜[`PREREG_VERSION_PART_MAX_DIGITS`] 桁)。
///
/// ⚠️ 桁は ASCII の `0-9` だけ (全角数字・符号・空白・末尾の改行は落ちる)。
fn is_wellformed_prereg_version(version: &str) -> bool {
    let parts: Vec<&str> = version.split('.').collect();
    parts.len() == 3
        && parts.iter().all(|part| {
            (1..=PREREG_VERSION_PART_MAX_DIGITS).contains(&part.len())
                && part.bytes().all(|b| b.is_ascii_digit())
        })
}

/// エラー文へ出す外部の値: 切り詰めて `{:?}` でエスケープし、元の文字数を添える。
fn echo_untrusted(value: &str) -> String {
    let shown: String = value.chars().take(PREREG_ECHO_MAX_CHARS).collect();
    format!("{shown:?} ({} 文字)", value.chars().count())
}

/// `id` / `version` の**形式だけ**を検査する (issue 007・起票 P1-G)。
///
/// ★ 凍結 JSON との**一致は求めない** (別の config を使うこと自体は正当。区別は `config_source` /
/// `prereg_sha256_prefix` / `overrides` が担う・`decisions.md` 判断 16)。
/// 封筒 `config.prereg_id` / `config.prereg_version` へ外部の文字列をそのまま写さないための門。
fn validate_prereg_identity(file: &P1PreregFile) -> Result<(), String> {
    if !is_wellformed_prereg_id(&file.id) {
        return Err(format!(
            "事前宣言 JSON の `id` が形式に合わない (`^[a-z0-9][a-z0-9-]{{0,63}}$`): {}",
            echo_untrusted(&file.id)
        ));
    }
    if !is_wellformed_prereg_version(&file.version) {
        return Err(format!(
            "事前宣言 JSON の `version` が形式に合わない (`<数字>.<数字>.<数字>`・各部 1〜{PREREG_VERSION_PART_MAX_DIGITS} 桁): {}",
            echo_untrusted(&file.version)
        ));
    }
    Ok(())
}

/// 事前宣言 JSON の本文を読む (`id` / `version` / `operational`)。
///
/// ★ `id` / `version` の形式もここで検査する (issue 007)。埋め込みの凍結 JSON も外部ファイルも
/// **同じ 1 か所**を通るので、片方だけ検査が抜けることがない。
fn parse_prereg_text(text: &str) -> Result<P1PreregFile, String> {
    let file = serde_json::from_str::<P1PreregFile>(text)
        .map_err(|e| format!("事前宣言 JSON を読めない: {e}"))?;
    validate_prereg_identity(&file)?;
    Ok(file)
}

/// バイト列の SHA-256 先頭 [`SOURCE_SHA256_HEX_CHARS`] 桁 (`sha256_prefix_of_file` のバイト列版)。
fn sha256_prefix_of_bytes(bytes: &[u8]) -> String {
    use sha2::{Digest, Sha256};
    let digest = Sha256::digest(bytes);
    let hex: String = digest.iter().map(|b| format!("{:02x}", b)).collect();
    hex[..SOURCE_SHA256_HEX_CHARS].to_string()
}

/// `--features` の設定を解決する。★ 出力を 1 バイトも書く前に呼ぶこと (fail-closed)。
///
/// 1. 既定は**埋め込みの凍結 JSON** (`config_source = "frozen"`)。
/// 2. `feature_config_path` があればその `operational` に置き換える (`"file"`)。
/// 3. `sets` (`key=value`) を順に上書きする。
/// 4. 物理的な範囲を検査し、凍結値から**外れたキー**を `overrides` に残す。
///
/// ⚠️ 未知のキー・型の不一致・範囲外・`id` / `version` の形式違い ([`validate_prereg_identity`]) は
/// **すべて `Err`** (呼び出し側は exit 1)。
fn resolve_feature_config(
    feature_config_path: Option<&Path>,
    sets: &[String],
) -> Result<ResolvedFeatureConfig, String> {
    let frozen = parse_prereg_text(FROZEN_P1_EPISODE_JSON)
        .map_err(|e| format!("埋め込みの凍結 JSON が壊れている (ビルドの不具合): {e}"))?;
    frozen
        .operational
        .validate()
        .map_err(|e| format!("埋め込みの凍結 JSON が範囲外 (ビルドの不具合): {e}"))?;

    let (base, source, sha) = match feature_config_path {
        None => (
            parse_prereg_text(FROZEN_P1_EPISODE_JSON)?,
            "frozen",
            sha256_prefix_of_bytes(FROZEN_P1_EPISODE_JSON.as_bytes()),
        ),
        Some(path) => {
            let file = File::open(path)
                .map_err(|e| format!("--feature-config を開けない ({}): {e}", path.display()))?;
            let mut bytes = Vec::new();
            std::io::Read::read_to_end(
                &mut std::io::Read::take(file, MAX_FEATURE_CONFIG_BYTES + 1),
                &mut bytes,
            )
            .map_err(|e| format!("--feature-config を読めない ({}): {e}", path.display()))?;
            if bytes.len() as u64 > MAX_FEATURE_CONFIG_BYTES {
                return Err(format!(
                    "--feature-config が大きすぎる (上限 {MAX_FEATURE_CONFIG_BYTES} バイト)"
                ));
            }
            let text = std::str::from_utf8(&bytes)
                .map_err(|_| "--feature-config が UTF-8 ではない".to_string())?;
            (
                parse_prereg_text(text)?,
                "file",
                sha256_prefix_of_bytes(&bytes),
            )
        }
    };

    let mut operational = base.operational;
    for entry in sets {
        let (key, value) = entry.split_once('=').ok_or_else(|| {
            format!("--set は <key>=<value> の形でなければならない (実際: `{entry}`)")
        })?;
        operational.apply_set(key, value)?;
    }
    operational.validate()?;

    let overrides = frozen
        .operational
        .as_pairs()
        .into_iter()
        .zip(operational.as_pairs())
        .filter(|((_, frozen_value), (_, value))| frozen_value != value)
        .map(|((key, frozen_value), (_, value))| ConfigOverride {
            key,
            frozen: frozen_value,
            value,
        })
        .collect();

    Ok(ResolvedFeatureConfig {
        operational,
        prereg_id: base.id,
        prereg_version: base.version,
        prereg_sha256_prefix: sha,
        config_source: source,
        overrides,
        pole: Pole::Baseline,
    })
}

impl FeatureConfigDto {
    /// `modifier_rows` は入力ファイルの修飾キーの `key` 行数 (極 M+ の適用可否・[`pole_applicability`])。
    /// `modifier_truncated` / `modifier_orphan_releases` は極 M+ の区間の健全性カウンタ
    /// (`decisions.md` 判断 24・[`ModifierScan`])。
    fn from_resolved(
        resolved: &ResolvedFeatureConfig,
        max_feature_ticks: usize,
        modifier_rows: Option<u64>,
        modifier_truncated: Option<u64>,
        modifier_orphan_releases: Option<u64>,
    ) -> Self {
        let c = resolved.stall_onset_config();
        let (pole_applicable, pole_not_applicable_reason) =
            pole_applicability(c.pole, modifier_rows);
        Self {
            w_ms: c.w_ms,
            q: c.q,
            b_ms: c.b_ms,
            net_diff_min: c.net_diff_min,
            hole_gap_ms: c.hole_gap_ms,
            warmup_count: c.warmup_count,
            theta_estimator: resolved.operational.theta_estimator.clone(),
            t1a_window_ms: c.t1a_window_ms,
            idle_trim_min_gap_ms: resolved.operational.idle_trim_min_gap_ms,
            idle_trim_max_ms: resolved.operational.idle_trim_max_ms,
            idle_trim_input_gap_ms: resolved.operational.idle_trim_input_gap_ms,
            pole: c.pole.as_str(),
            pole_applicable,
            pole_not_applicable_reason,
            pole_modifier_rows: match c.pole {
                Pole::ModifierMPlus => modifier_rows,
                Pole::Baseline | Pole::PointerB => None,
            },
            pole_modifier_truncated: match c.pole {
                Pole::ModifierMPlus => modifier_truncated,
                Pole::Baseline | Pole::PointerB => None,
            },
            pole_modifier_orphan_releases: match c.pole {
                Pole::ModifierMPlus => modifier_orphan_releases,
                Pole::Baseline | Pole::PointerB => None,
            },
            // ★ 極 B の証拠 (行数・適用可否) は入力が要るので [`Self::with_pointer_evidence`] が足す。
            pole_pointer_rows: None,
            prereg_id: resolved.prereg_id.clone(),
            prereg_version: resolved.prereg_version.clone(),
            prereg_sha256_prefix: resolved.prereg_sha256_prefix.clone(),
            config_source: resolved.config_source,
            overrides: resolved.overrides.clone(),
            max_feature_ticks,
            hmm_version: HMM_VERSION,
            engine_tick_ms: ENGINE_TICK_MS,
            pause_threshold_ms: gse_next_lib::analysis::features::PAUSE_THRESHOLD_MS,
        }
    }

    /// 極 B の**適用可否と `pointer_bin` 行数**を確定する (issue 006)。★ 極 B 以外では何もしない
    /// (`pole_pointer_rows` は `null` のまま・渡された値を漏らさない)。
    ///
    /// `declared` は [`declares_pointer_bin`] (封筒 `provenance.capabilities` の宣言)、`rows` は入力の
    /// `pointer_bin` 行数。⚠️ 極 B で呼ばなければ `pole_applicable == false` /
    /// `pointer_evidence_not_supplied` の防御の値のまま (嘘の `true` を出さない)。
    /// ★ `rows` は [`pointer_applicability`] (判断 26 の 3 状態判定) にも渡す —— 宣言があっても
    /// 0 行なら `pole_applicable == false` になる (「判定不能」)。
    fn with_pointer_evidence(mut self, declared: bool, rows: Option<u64>) -> Self {
        if self.pole == Pole::PointerB.as_str() {
            let (applicable, reason) = pointer_applicability(declared, rows);
            self.pole_applicable = applicable;
            self.pole_not_applicable_reason = reason;
            self.pole_pointer_rows = rows;
        }
        self
    }
}

/// `meta`(session_start) 行から読めるセッション単位の事実 (封筒の `provenance` 用)。
///
/// ⚠️ **`os` は含まない** —— `logger.rs::write_meta_start` が書いていないため
/// (2026-09-20 実測)。★ 足すのは計器の変更 (起票 1・ADR-032) であってここではない。
#[derive(Debug, Default)]
struct MetaSessionFacts {
    session_start: Option<u64>,
    hmm_version: Option<String>,
    app_version: Option<String>,
    g1_mode: Option<String>,
    o1_mode: Option<String>,
    keyboard_layout: Option<String>,
    /// ★ **同じ `meta` 行**から取る (2026-09-20・code-reviewer MEDIUM)。
    /// ⚠️ 別関数が別条件で拾うと、連結ログで**別セグメントの宣言**が混ざる。
    capabilities: Option<serde_json::Value>,
}

/// `--calibration` で受け付ける 1 被験者あたりのセッションファイル数の上限。
///
/// 各ファイルは `MAX_SESSION_BYTES` で保護されるが、ファイル**数**が無制限だと
/// `500MB × 数 × 2 パス` のリソースを消費しうる (security-checker MEDIUM 指摘)。
/// 実運用では 1 被験者 10 セッション程度なので 64 は十分広い。
const MAX_CALIBRATION_FILES: usize = 64;

/// NDJSON の 1 行を表す Deserialize 専用 enum。
///
/// `logger::LogEntry` とは意図的に別型。`logger` は書き出し専用・`ReplayEvent`
/// は読み込み専用として責務を分離する。JSON のフィールド名は NDJSON 実形式に
/// 完全一致させる（例: `timestamp` ではなく `t`、`vk_code` ではなく `vk`）。
#[derive(Debug, serde::Deserialize)]
#[serde(tag = "type")]
enum ReplayEvent {
    /// `{"type":"meta","session_start":...,"hmm_version":"..."}` または
    /// `{"type":"meta","session_end":...}` のいずれか。
    #[serde(rename = "meta")]
    Meta {
        session_start: Option<u64>,
        #[allow(dead_code)]
        session_end: Option<u64>,
        hmm_version: Option<String>,
    },
    /// `start_session` コマンド発火時刻マーカー。replay では extractor を
    /// リセットして「session 境界」を再現するために使う。
    #[serde(rename = "session_start")]
    SessionStart { t: u64 },
    /// キーストローク。raw ログは `vk` (Windows 規約 VK コード、macOS 側はフック層で変換済み)
    /// を持つ。transfer-pipeline (#27) の `gse-package` が匿名化した NDJSON は本文再構成を
    /// 防ぐため `vk` を落とし `category` (KeyCategory 文字列) を持つ。replay は **両対応**で
    /// 同じ特徴量を再計算する (D6 Replay-as-Truth)。どちらも省略可だが、実際の行は片方を持つ。
    /// 両方欠落 / 未知 category の行は不正として読み飛ばす (`resolve_key_vk` が `None`)。
    #[serde(rename = "key")]
    Key {
        t: u64,
        #[serde(default)]
        vk: Option<u32>,
        #[serde(default)]
        category: Option<String>,
        press: bool,
    },
    /// ペーストイベント (Ctrl+V / Cmd+V) の発生時刻マーカーと文字数。
    /// features/HMM には未使用のため replay では読み飛ばす (`timestamp()==None`)。
    /// 本 variant が無いと NDJSON に paste 行があるとき deserialize でエラーになる。
    /// `external_paste_chars` は新フィールド。旧フィクスチャ (フィールド無し) 互換のため
    /// `#[serde(default)]` で欠落を許容する (None になる)。
    #[serde(rename = "paste")]
    Paste {
        #[allow(dead_code)]
        t: u64,
        #[allow(dead_code)]
        #[serde(default)]
        external_paste_chars: Option<u64>,
    },
    /// IME 状態変化。`on` は IME モード（β 切替用）、`active` は候補ウィンドウ
    /// の開閉（engine pause 用）。
    #[serde(rename = "ime_state")]
    ImeState { t: u64, on: bool, active: bool },
    /// 既存セッションの Feat エントリ。
    ///
    /// `run_replay` (snapshot 検証経路) では step() 再実行で自前生成するため、
    /// 本 variant は読み飛ばし専用 (`timestamp()` も `None` を返し時刻順ソート
    /// から除外)。metrics 経路では `collect_logged_feats()` 側で `LoggedFeatDto`
    /// を使って別途構造化パースする (clock semantic mismatch 対策、
    /// `.steering/20260416-replay-feat-alignment-bug/decisions.md` D1 参照)。
    #[serde(rename = "feat")]
    Feat(#[allow(dead_code)] serde_json::Value),
    /// Phase 1 Ground Truth ラベル。`--metrics` で評価対象として突き合わせる。
    /// `--snapshot` / デフォルト (snapshot 出力) の経路では読み飛ばす。
    #[serde(rename = "user_label")]
    UserLabel {
        t: u64,
        label: String,
        #[allow(dead_code)]
        recovered_at: Option<u64>,
    },
    /// 事後レビュー用ブックマークマーカー。`--segment` でハイライト表示に使う。
    /// `--snapshot` / `--metrics` の経路では読み飛ばす。
    #[serde(rename = "review_marker")]
    ReviewMarker {
        #[allow(dead_code)]
        t: u64,
    },
    /// Phase 2b IME Shadow Features。replay では読み飛ばす (`timestamp()` が `None`)。
    ///
    /// ⚠️★★★ **この variant を型付き構造体にしてはならない。`serde_json::Value` のまま置く。**
    ///
    /// ★ `--features` (`T1b`・issue 002) が中身を要るようになったが、構造化は
    /// [`collect_all_ime_shadow_events`] の中の専用 DTO ([`ImeShadowDto`]) が行う。
    /// ★ **同じ手法の先例は `feat` 行の [`LoggedFeatDto`]** である (本 variant の上の
    /// `ReplayEvent::Feat` の doc を参照)。
    ///
    /// ★ 理由 (2026-09-15・`code-reviewer` / `security-checker` が独立に HIGH で指摘し、
    /// **両者とも実測で再現した**): `run_replay` は**既知タグのパース失敗も `Err` にして
    /// 中断する**ので、ここを厳格にすると「読み飛ばすはずの行」が**リプレイを丸ごと殺す**。
    /// ⚠️ 実測した落ち方 (issue 002 の初版):
    /// - `"abandon":0` (整数) → 逐語 `invalid type: integer 0, expected a boolean`
    /// - `nav` 欠落 → 逐語 `missing field 'nav'`
    /// - `"dwell_ms":null` → 逐語 `invalid type: null, expected u64`
    ///
    /// ⚠️ **`Option` ＋ `#[serde(default)]` でも足りない** (★ 2026-09-15 に実測):
    /// `Option<bool>` は `0` を受け取れないので `"abandon":0` は依然 exit 1 になる。
    /// → ★ **受理集合を 1 バイトも狭めない唯一の形が `Value`** である。
    ///
    /// ★ これは `hook_health` (2026-08-09) / `activity_label` / `starve_window` (2026-09-14) で
    /// 3 度踏んだ失敗様式の 4 度目であり、回帰は
    /// [`tests::partial_ime_shadow_line_does_not_break_run_replay`] が張る。
    /// ⚠️ **issue 007 が `hook_health` を構造化するときも同じ形にすること。**
    #[serde(rename = "ime_shadow")]
    ImeShadow(#[allow(dead_code)] serde_json::Value),
    /// MVP Opportunity 判定ログ。replay では読み飛ばす。
    #[serde(rename = "intervention_decision")]
    InterventionDecision(#[allow(dead_code)] serde_json::Value),
    /// 介入応答 (dismiss 理由) ログ。features/HMM 未使用のため replay では読み飛ばす。
    /// 本 variant が無いと NDJSON に intervention_response 行があるとき deserialize でエラーになる。
    #[serde(rename = "intervention_response")]
    InterventionResponse(#[allow(dead_code)] serde_json::Value),
    /// ⚠️★★ キーボードフックの生存診断 (`input::liveness`)。features/HMM 未使用のため読み飛ばす。
    ///
    /// ★ **この variant が無いと `--snapshot` 経路が丸ごと落ちる。**
    /// `run_replay` は未知タグを `Err` にして中断するので (`--metrics` 側だけが lenient)、
    /// 行型を足したのに ここへ足し忘れると **実セッションが 1 本も replay できなくなる**
    /// (= Replay-as-Truth が切れる)。⚠️ 2026-08-09 に実測で踏んだ:
    /// `parse error at line 2: unknown variant 'hook_health'`。
    /// 回帰は `hook_health_line_is_skipped_by_run_replay` が張っている。
    #[serde(rename = "hook_health")]
    HookHealth(#[allow(dead_code)] serde_json::Value),
    /// ⚠️★★★ **沈黙窓の診断行**（`input::liveness`・`THRESHOLD_GATED`）。★ 読み飛ばし専用。
    ///
    /// ⚠️★★★ **2026-09-14 に *既存の* 欠落として発見した**（★ 新設した
    /// [`tests::every_known_line_type_is_accepted_by_replay_event`] が掘り当てた）。
    /// ★ `logger.rs` は `starve_window` を書くのに、ここに variant が無かった。
    /// → ⚠️ **`starve_window` 行を 1 本でも含む NDJSON は `--snapshot` が丸ごと落ちていた**
    /// （実測: 逐語 `parse error at line 32: unknown variant 'starve_window'`）。
    /// ★ これは `hook_health`（2026-08-09）/ `activity_label`（2026-09-14）と**同一の失敗様式で 3 件目**である。
    #[serde(rename = "starve_window")]
    StarveWindow(#[allow(dead_code)] serde_json::Value),
    /// ⚠️★★★ **O1 (R3) で足した 4 行種**。★ どれも **読み飛ばし専用**である。
    ///
    /// ## ★ なぜ variant を足さなければならないのか（⚠️ 「読まないなら不要」ではない）
    ///
    /// ★ `run_replay` は**未知タグを `Err` にして中断する**（`--metrics` 側だけが lenient）。
    /// → ⚠️★★★ **行種を足したのにここへ足し忘れると、その形式のログが 1 本も replay できなくなる**
    /// （= Replay-as-Truth が切れる）。★ 2026-08-09 に `hook_health` で実測済みの失敗様式である。
    ///
    /// ## ⚠️ 特徴量には 1 バイトも流さない（ADR-014 **D4b**）
    ///
    /// ★ `timestamp()` が `None` を返すので時刻順ソートからも外れ、`step()` を 1 度も呼ばない。
    #[serde(rename = "recording_pause")]
    RecordingPause(#[allow(dead_code)] serde_json::Value),
    /// ⚠️ 読み飛ばし専用（上記 `RecordingPause` の doc を参照）。
    #[serde(rename = "focus_transition")]
    FocusTransition(#[allow(dead_code)] serde_json::Value),
    /// ⚠️ 読み飛ばし専用（同上）。★ 例外は **`--features --pole pointer_b` の
    /// [`collect_pointer_bin_timestamps`] だけ**（issue 006）—— 行の**時刻 `t` だけ**を読み、値は読まない。
    /// ⚠️ `timestamp()` は `None` のままなので HMM 経路（`--snapshot` / `--metrics`）へは 1 バイトも流れない。
    #[serde(rename = "pointer_bin")]
    PointerBin(serde_json::Value),
    /// ⚠️ 読み飛ばし専用（同上）。
    #[serde(rename = "secure_input")]
    SecureInput(#[allow(dead_code)] serde_json::Value),
    /// ⚠️★★★ **O1 の監査 criterion**（ADR-031 D1）。★ 読み飛ばし専用。
    ///
    /// ⚠️★★★ **2026-09-14 に足し忘れて実測で踏んだ。**★ `activity_label` 行を 1 本足した
    /// NDJSON を `--snapshot` に掛けると逐語
    /// `replay failed: parse error at line 32: unknown variant 'activity_label'`
    /// で**丸ごと落ちた** —— ★ 上の `HookHealth` の doc が「2026-08-09 に実測済みの失敗様式」として
    /// 名指ししているものと**同一**である（★ 同じ轍を 2 度踏んだ）。
    /// ⚠️ **ゴールデンが緑でもこの事故は検出できない**（★ 既存 fixture に行が無いため）。
    /// → ★ 回帰は [`tests::activity_label_line_is_skipped_by_run_replay`] が張る。
    ///
    /// ★ 自己申告は **記録のみ・推論に 1 バイトも流さない**（ADR-014 D4b / ADR-031 D2）。
    #[serde(rename = "activity_label")]
    ActivityLabel(#[allow(dead_code)] serde_json::Value),
    /// v0.3 較正スモーク: セッション宣言。`--calibration` 経路で track を抽出する。
    /// snapshot/run_replay 経路では `timestamp()==None` で読み飛ばす。
    #[serde(rename = "session_meta")]
    SessionMeta {
        track: String,
        #[allow(dead_code)]
        task_kind: String,
        #[allow(dead_code)]
        #[allow(dead_code)]
        intervention_enabled: bool,
        // 新フィールド (WBS 0.11 / 0.4)。旧フィクスチャ互換のため `#[serde(default)]`。
        #[allow(dead_code)]
        #[serde(default)]
        condition: Option<String>,
        #[allow(dead_code)]
        #[serde(default)]
        label_pool: Option<String>,
        #[allow(dead_code)]
        ts: u64,
    },
    /// v0.3 較正スモーク: ランダムプローブ割当の監査記録。`--calibration` で件数を数える。
    #[serde(rename = "probe_assignment")]
    ProbeAssignment {
        #[allow(dead_code)]
        probe_id: String,
        #[allow(dead_code)]
        scheduled_ts: u64,
        #[allow(dead_code)]
        session_elapsed_ms: u64,
    },
    /// v0.3 較正スモーク: 主データ (リアルタイム/自己マーカー回答)。`--calibration` で ProbeRecord 化する。
    #[serde(rename = "realtime_label")]
    RealtimeLabel {
        #[allow(dead_code)]
        probe_id: Option<String>,
        source: String,
        q1_friction: Option<u8>,
        q2_progress: Option<u8>,
        answered: bool,
        skip_reason: String,
        latency_ms: u64,
        analysis_window_start_ms: u64,
        analysis_window_end_ms: u64,
        #[allow(dead_code)]
        ts: u64,
    },
    /// v0.3 較正スモーク: 尺度理解テスト回答。`--calibration` で VignetteRecord 化する。
    #[serde(rename = "vignette_response")]
    VignetteResponse {
        vignette_id: String,
        expected_quadrant: String,
        q1_friction: u8,
        q2_progress: u8,
        /// 2026-08-17 以降のログにのみ存在。⚠️ **旧ログでは `None`** であり、
        /// `0`（＝即答）と混同してはならない
        /// (`deny_unknown_fields` を付けていないので前方互換・後方互換とも壊れない)。
        #[serde(default)]
        elapsed_ms: Option<u64>,
        #[serde(default)]
        changes: Option<u16>,
        #[allow(dead_code)]
        ts: u64,
    },
}

impl ReplayEvent {
    /// タイムスタンプを取り出す（Meta は `session_start` フィールドから）。
    /// `None` は時刻順ソートから除外する（既存 Feat など）。
    fn timestamp(&self) -> Option<u64> {
        match self {
            ReplayEvent::Meta { session_start, .. } => *session_start,
            ReplayEvent::SessionStart { t } => Some(*t),
            ReplayEvent::Key { t, .. } => Some(*t),
            // Paste は記録専用 (回数集計用)。step() 再実行に影響しないため除外する。
            ReplayEvent::Paste { .. } => None,
            ReplayEvent::ImeState { t, .. } => Some(*t),
            ReplayEvent::Feat(_) => None,
            // UserLabel は再実行対象ではない (ゲート進行を動かさない)。
            // timestamp() から None を返して時刻順ソートから除外し、
            // metrics 算出経路で別途抽出する。
            ReplayEvent::UserLabel { .. } => None,
            ReplayEvent::ReviewMarker { .. } => None,
            ReplayEvent::ImeShadow(_) => None,
            ReplayEvent::InterventionDecision(_) => None,
            ReplayEvent::InterventionResponse(_) => None,
            // 診断行。ゲート進行を動かさないので時刻順ソートから除外する。
            ReplayEvent::HookHealth(_) => None,
            ReplayEvent::StarveWindow(_) => None,
            // ⚠️★★★ O1 (R3) の 4 行種。★ **記録のみ・推論に 1 バイトも流さない**
            //   (ADR-014 D4b) ので、`None` を返して時刻順ソートから外す。
            ReplayEvent::RecordingPause(_) => None,
            ReplayEvent::FocusTransition(_) => None,
            ReplayEvent::PointerBin(_) => None,
            ReplayEvent::SecureInput(_) => None,
            // ⚠️★★★ 監査 criterion（ADR-031）。★ 記録のみで推論へ流さない。
            ReplayEvent::ActivityLabel(_) => None,
            // v0.3 較正 variant は --calibration 専用コレクタで別途抽出する。
            // run_replay (snapshot 経路) の時刻順ソートからは除外する (UserLabel と同方針)。
            ReplayEvent::SessionMeta { .. } => None,
            ReplayEvent::ProbeAssignment { .. } => None,
            ReplayEvent::RealtimeLabel { .. } => None,
            ReplayEvent::VignetteResponse { .. } => None,
        }
    }
}

/// NDJSON の `{"type":"feat", ...}` 行を `FeatSnapshot` に変換する DTO。
///
/// metrics 経路 (`--metrics`) で production が wall-clock で書いた feat 行を
/// そのまま source of truth として使うための変換型。`run_replay` の step()
/// 再生成は virtual-clock grid のため label と時刻軸が一致せず、metrics の
/// nearest_feat 判定で大量に取りこぼす bug (decisions.md D1) の fix 用。
///
/// ## 同期対象
///
/// フィールド一式は `src-tauri/src/schema_dto.rs` の `LogEntryDto::Feat`
/// (L63-79) と一致させる必要がある。`logger::LogEntry::Feat` に新フィールド
/// が追加されたら schema_dto.rs と本 DTO の両方を更新する。同期漏れは:
/// - schema drift check (emit_schema vs `schema/current.json`) で schema_dto 側は検知可能
/// - 本 DTO 側は serde のデフォルト挙動で「未知フィールドは無視」する
///   (`#[serde(deny_unknown_fields)]` は forward-compat のため **付けない**)
/// - 必要ならテスト層1 (`logged_feat_dto_parses_schema_dto_feat_shape`) で
///   schema_dto::LogEntryDto::Feat が生成するサンプル文字列を本 DTO で
///   受けて round-trip すること。
#[derive(Debug, serde::Deserialize)]
struct LoggedFeatDto {
    #[serde(rename = "t")]
    timestamp: u64,
    f1: f64,
    f3: f64,
    f4: f64,
    f5: f64,
    f6: f64,
    p_flow: f64,
    p_inc: f64,
    p_stuck: f64,
    raw_x: f64,
    raw_y: f64,
    ewma_x: f64,
    ewma_y: f64,
    obs: usize,
    alpha: f64,
    /// ★ Tier 0 (記録のみ): 特徴量ウィンドウ内の総キー押下数。
    ///
    /// ⚠️★★★ **Tier 0 配線より前に収集された NDJSON には存在しない。**
    /// その場合 `None` → `FeatSnapshot` では `0` になる。すなわち
    /// **「旧ログで欠測」と「実測 0 打」を `--metrics` 経路では区別できない**。
    /// ★ `collect_logged_feats` が欠測行数を集計して `tracing::warn!` を 1 回出すので、
    /// CLI の出力でも気づけるようにしてある。
    ///
    /// ⚠️★★★ **窓の右端は「最後の打鍵時刻」であって `t` ではない。累積でもない。**
    /// **沈黙中は同じ値がくり返し出る**ので、**行をまたいで足し上げてはいけない**
    /// (★ 正本: `analysis/loop_step.rs` の `FeatSnapshot::keys` の doc)。
    #[serde(default)]
    keys: Option<u64>,
    /// ★ Tier 0 (記録のみ): 特徴量ウィンドウ内の BS/Del 押下数。注意点は `keys` と同じ。
    #[serde(default)]
    bs_keys: Option<u64>,
}

/// `LoggedFeatDto` → `FeatSnapshot` の安全な変換。
///
/// rust-standards Skill: `anyhow::Result` ではなく `Result<_, String>` を使う
/// (既存 `collect_user_labels` / `collect_logged_feats` と対称、bin crate 層での
/// 軽量エラー通知)。
///
/// 検証ルール (security-checker M3 対応、`decisions.md` D8 で詳細化):
/// - `p_flow`, `p_inc`, `p_stuck`: `is_finite()` かつ `[0.0, 1.0]`
/// - 確率和 `p_flow + p_inc + p_stuck`: `[0.98, 1.02]` (logger `{:.4}` 丸め誤差許容)
/// - `alpha`: `is_finite()` かつ `[0.0, 1.0]`
/// - `f1, f3, f4, f5, f6, raw_x, raw_y, ewma_x, ewma_y`: `is_finite()` かつ非負
///
/// NaN が `argmax_class` の `>=` 比較を全て false にして silent に Stuck 誤分類を
/// 招いていた問題 (`metrics.rs:270-277`) を入力側で止める。
impl TryFrom<LoggedFeatDto> for FeatSnapshot {
    type Error = String;

    fn try_from(d: LoggedFeatDto) -> Result<Self, Self::Error> {
        // 確率の範囲検証
        for (name, p) in [
            ("p_flow", d.p_flow),
            ("p_inc", d.p_inc),
            ("p_stuck", d.p_stuck),
        ] {
            if !p.is_finite() {
                return Err(format!("{} is not finite (NaN/Inf): {}", name, p));
            }
            if !(0.0..=1.0).contains(&p) {
                return Err(format!("{} out of range [0.0, 1.0]: {}", name, p));
            }
        }

        // 確率和検証 (4 桁丸め誤差許容)
        let sum = d.p_flow + d.p_inc + d.p_stuck;
        if !sum.is_finite() || !(0.98..=1.02).contains(&sum) {
            return Err(format!(
                "probability sum out of range [0.98, 1.02]: p_flow={} p_inc={} p_stuck={} sum={}",
                d.p_flow, d.p_inc, d.p_stuck, sum
            ));
        }

        // alpha
        if !d.alpha.is_finite() || !(0.0..=1.0).contains(&d.alpha) {
            return Err(format!("alpha out of range [0.0, 1.0]: {}", d.alpha));
        }

        // 特徴量: is_finite + 非負
        for (name, v) in [
            ("f1", d.f1),
            ("f3", d.f3),
            ("f4", d.f4),
            ("f5", d.f5),
            ("f6", d.f6),
            ("raw_x", d.raw_x),
            ("raw_y", d.raw_y),
            ("ewma_x", d.ewma_x),
            ("ewma_y", d.ewma_y),
        ] {
            if !v.is_finite() {
                return Err(format!("{} is not finite (NaN/Inf): {}", name, v));
            }
            if v < 0.0 {
                return Err(format!("{} is negative: {}", name, v));
            }
        }

        // ★ Tier 0: `bs_keys ≤ keys` は producer 側で構造的に成り立つ不変条件
        // (`bs_keys` は `keys` の部分集合を数えたもの)。壊れた NDJSON がこれを破ると、
        // ⚠️ 将来の消費者が `progress_proxy = keys − bs_keys` を `u64` で計算した瞬間に
        // **underflow で panic ないし巨大値**になる。入力側で止める
        // (他の検証と同じ方針: `argmax_class` の NaN 問題を入力側で止めたのと同型)。
        // ⚠️ 旧ログ (両方 None → 0/0) は `0 ≤ 0` で通るので後方互換は壊れない。
        let (keys, bs_keys) = (d.keys.unwrap_or(0), d.bs_keys.unwrap_or(0));
        if bs_keys > keys {
            return Err(format!(
                "bs_keys exceeds keys (impossible for a producer-written line): keys={} bs_keys={}",
                keys, bs_keys
            ));
        }

        Ok(FeatSnapshot {
            timestamp: d.timestamp,
            f1: d.f1,
            f3: d.f3,
            f4: d.f4,
            f5: d.f5,
            f6: d.f6,
            p_flow: d.p_flow,
            p_inc: d.p_inc,
            p_stuck: d.p_stuck,
            raw_x: d.raw_x,
            raw_y: d.raw_y,
            ewma_x: d.ewma_x,
            ewma_y: d.ewma_y,
            obs: d.obs,
            alpha: d.alpha,
            // ★ Tier 0: 旧ログ (フィールド無し) は 0 に倒す。上の doc コメントの注意を参照。
            keys,
            bs_keys,
        })
    }
}

/// vk_code から is_backspace を再計算。
///
/// 既存の hook_windows.rs:304 と hook_macos.rs:340 の判定を複製:
/// Windows 規約 0x08 (VK_BACK) / 0x2E (VK_DELETE) が true。
fn is_backspace(vk: u32) -> bool {
    vk == 0x08 || vk == 0x2E
}

/// 匿名化 NDJSON の `category` (KeyCategory 文字列) を **代表 VK コード**へ逆写像する。
///
/// `gse-package` の匿名化は個々の VK を `KeyCategory` に潰すため (本文再構成不能化)、
/// replay 側で特徴量を再計算するには代表 VK を 1 つ復元すればよい。特徴量に効くのは
/// is_backspace (F3/F6) と文字生成キー区分・(Windows) リピート検出のみで、いずれも
/// **category 単位**で決まるため、同じ category に再分類される代表値で raw と同じ
/// 特徴量が再現する。
///
/// 不変条件: 任意の既知 category `c` について
/// `KeyCategory::from_vk(category_representative_vk(c).unwrap()).as_str() == c`。
/// `category_representative_vk_roundtrips` テストが lib の `KeyCategory::from_vk` で drift を検出する。
/// 未知 category は `None` (forward-compat、呼び出し側で件数を warn してスキップ)。
///
/// **`is_text_producing` との関係 (decisions.md D-RC3 / ADR-014 判断 6)**:
/// **2026-08-23 に D-RC3 の制約は解消した。** `KeyCategory` に `Punctuation` (OEM 句読点/記号 +
/// テンキー演算子) と `Tab` を足したので、**`is_text_producing` が true な VK は 1 つ残らず
/// 非 `other` category に入る**。したがって `other` の代表 `0x07` (非 text-producing) は
/// **保守的な倒し込みではなく厳密に正しい**値になり、`--metrics` の `manual_insert` 系の
/// 過小評価 (旧: OEM 句読点/Tab/テンキー演算子の件数分) は **ゼロ**になった。
///
/// 旧仕様: これらは `Other` へ畳まれ、匿名化後に text-producing と判別できなかった。
/// `manual_contribution_ratio` は `research-positioning.md §5` **H-Y の主要アウトカム**であり、
/// 構造的な過小評価は研究上許容できない (`.steering/20260823-r3-accept-and-role-category/` D-7)。
fn category_representative_vk(category: &str) -> Option<u32> {
    // anonymize.rs `KeyCategory::from_vk` の逆。各 category の代表 VK を 1 つ選ぶ。
    let vk = match category {
        "alphabetic" => 0x41, // 'A' (0x41..=0x5A) — text-producing
        "numeric" => 0x30,    // '0' (0x30..=0x39) — text-producing
        // VK_OEM_1 (';') — text-producing。⚠️ 0xBE / 0xBC は SentencePunctuation なので使えない。
        "punctuation" => 0xBA,
        // VK_OEM_PERIOD ('.') — text-producing。boundary keys の「文間」。
        "sentence_punctuation" => 0xBE,
        "tab" => 0x09,        // VK_TAB — text-producing
        "backspace" => 0x08,  // VK_BACK — is_backspace
        "delete" => 0x2E,     // VK_DELETE — is_backspace
        "space" => 0x20,      // VK_SPACE — text-producing
        "enter" => 0x0D,      // VK_RETURN — text-producing
        "navigation" => 0x25, // VK_LEFT (0x21..=0x28)
        "modifier" => 0x10,   // VK_SHIFT
        "function" => 0x70,   // VK_F1 (0x70..=0x7B)
        "escape" => 0x1B,     // VK_ESCAPE
        // from_vk の既定 (どのレンジにも入らず Other へ)。
        // 2026-08-23 以降、raw の Other に text-producing キーは混在しない (上記 doc)。
        "other" => 0x07,
        _ => return None,
    };
    Some(vk)
}

/// `key` イベントの実効 VK コードを解決する (raw / 匿名化 両対応)。
///
/// - raw ログ: `vk` をそのまま使う。
/// - 匿名化ログ: `category` を `category_representative_vk` で代表 VK へ逆写像する。
///
/// `vk` を優先し (両方ある異常入力でも raw を尊重)、無ければ `category`、
/// どちらも解決できなければ `None`。
fn resolve_key_vk(vk: Option<u32>, category: Option<&str>) -> Option<u32> {
    vk.or_else(|| category.and_then(category_representative_vk))
}

/// コマンドライン引数をパース。
struct Args {
    session_path: PathBuf,
    snapshot_path: Option<PathBuf>,
    metrics: bool,
    json: bool,
    /// --segment: セッションを活動境界で分割し .segments.txt を生成
    segment: bool,
    /// --segments <path>: .segments.txt を読み込み範囲マッチングでメトリクス算出
    segments_path: Option<PathBuf>,
    /// --intervention: v2 介入ポリシーをオフライン反実仮想リプレイし HIR/DC 等を算出
    intervention: bool,
    /// --calibration: v0.3 較正解析 (時間隔離窓 C-index / 2段ゲート / MNAR / ビネット)。
    /// 1 被験者の複数セッションを受けるため、追加の positional を `extra_sessions` に積む。
    calibration: bool,
    /// --sweep: nudge_need を 0.50–0.90 で振り reason 別 HIR / 閾値別指標をプール出力 (Phase 0)。
    /// `--calibration` と同様に 1 被験者の複数セッションを受ける。
    sweep: bool,
    /// --nudge-diag: ACT decision を reason×GT で層別し特徴量分布を出す (FP/TP 分離診断)。
    /// `--sweep` と同様に複数セッションを受ける。
    nudge_diag: bool,
    /// --corr-floor: correction_after_pause veto floor (f4/f6) の counterfactual 候補比較 (Step 2)。
    /// `--sweep` と同様に複数セッションを受ける。
    corr_floor: bool,
    /// --features: ADR-030 の Tier 別 1 Hz tick 単位特徴行を出力する (issue 001-007)。
    /// ⚠️ 手元の解析用中間成果物であり `gse-dataset` へ共有しない (`docs/glossary.md` 逐語)。
    features: bool,
    /// --feature-config <path>: `--features` の設定を外部 JSON (凍結 JSON と同じ形) から読む。
    feature_config_path: Option<PathBuf>,
    /// --set <key>=<value> (繰り返し可): `--features` の設定を 1 キーずつ上書きする。
    /// ⚠️ 生の文字列のまま持つ。検証 (未知キー / 型 / 範囲) は `resolve_feature_config` が行う。
    feature_sets: Vec<String>,
    /// --pole <baseline|pointer_b|modifier_m_plus>: `--features` の極 (ADR-030 D3・1 実行 1 極)。
    /// ⚠️ 生の文字列のまま持つ。検証 (`--features` 専用 / 未知の名前 / 未実装) は `resolve_pole` が行う
    /// (★ `--set` と同じ作法。未知の名前は exit 1)。
    pole: Option<String>,
    /// `--calibration` / `--sweep` / `--nudge-diag` / `--corr-floor` の 2 個目以降の positional。
    extra_sessions: Vec<PathBuf>,
}

fn parse_args() -> Result<Args, String> {
    parse_args_from(std::env::args().skip(1).collect())
}

/// `parse_args()` の本体。`Vec<String>` を直接受けるため、`std::env::args()`
/// (プロセス全体で 1 つ) に依存せず単体テストできる (AC4: モード相互排他)。
fn parse_args_from(mut args: Vec<String>) -> Result<Args, String> {
    if args.is_empty() || args.iter().any(|a| a == "-h" || a == "--help") {
        return Err(usage());
    }

    let mut snapshot_path = None;
    // --snapshot <path> フラグを検出・除去
    if let Some(pos) = args.iter().position(|a| a == "--snapshot") {
        if pos + 1 >= args.len() {
            return Err("--snapshot requires a path argument".to_string());
        }
        let path = args.remove(pos + 1);
        args.remove(pos);
        snapshot_path = Some(PathBuf::from(path));
    }

    // --metrics / --json フラグを検出・除去（Phase 1 Task 2）
    // --snapshot と同じ position+remove パターンで揃え、位置引数が偶然
    // --metrics と一致するパスを持っても誤って食わないようにする。
    let metrics = if let Some(pos) = args.iter().position(|a| a == "--metrics") {
        args.remove(pos);
        true
    } else {
        false
    };
    let json = if let Some(pos) = args.iter().position(|a| a == "--json") {
        args.remove(pos);
        true
    } else {
        false
    };

    // --metrics と --snapshot は排他（役割が完全に異なる）
    if metrics && snapshot_path.is_some() {
        return Err("--metrics and --snapshot are mutually exclusive".to_string());
    }
    // --segment フラグ
    let segment = if let Some(pos) = args.iter().position(|a| a == "--segment") {
        args.remove(pos);
        true
    } else {
        false
    };

    // --segments <path> フラグ
    let segments_path = if let Some(pos) = args.iter().position(|a| a == "--segments") {
        if pos + 1 >= args.len() {
            return Err("--segments requires a path argument".to_string());
        }
        let path = args.remove(pos + 1);
        args.remove(pos);
        Some(PathBuf::from(path))
    } else {
        None
    };

    // --intervention フラグ
    let intervention = if let Some(pos) = args.iter().position(|a| a == "--intervention") {
        args.remove(pos);
        true
    } else {
        false
    };

    // --calibration フラグ (v0.3 較正解析)
    let calibration = if let Some(pos) = args.iter().position(|a| a == "--calibration") {
        args.remove(pos);
        true
    } else {
        false
    };

    // --sweep フラグ (Phase 0 nudge_need threshold sweep)
    let sweep = if let Some(pos) = args.iter().position(|a| a == "--sweep") {
        args.remove(pos);
        true
    } else {
        false
    };

    // --nudge-diag フラグ (ACT を reason×GT で層別した特徴量診断)
    let nudge_diag = if let Some(pos) = args.iter().position(|a| a == "--nudge-diag") {
        args.remove(pos);
        true
    } else {
        false
    };

    // --corr-floor フラグ (correction_after_pause veto floor の counterfactual)
    let corr_floor = if let Some(pos) = args.iter().position(|a| a == "--corr-floor") {
        args.remove(pos);
        true
    } else {
        false
    };

    // --features フラグ (ADR-030 の Tier 別 1 Hz tick 単位特徴行を出力。issue 001-007)
    let features = if let Some(pos) = args.iter().position(|a| a == "--features") {
        args.remove(pos);
        true
    } else {
        false
    };

    // --feature-config <path> / --set <key>=<value> (繰り返し可): --features 専用の設定注入。
    let feature_config_path = if let Some(pos) = args.iter().position(|a| a == "--feature-config") {
        if pos + 1 >= args.len() {
            return Err("--feature-config requires a path argument".to_string());
        }
        let path = args.remove(pos + 1);
        args.remove(pos);
        Some(PathBuf::from(path))
    } else {
        None
    };
    let mut feature_sets: Vec<String> = Vec::new();
    while let Some(pos) = args.iter().position(|a| a == "--set") {
        if pos + 1 >= args.len() {
            return Err("--set requires a <key>=<value> argument".to_string());
        }
        feature_sets.push(args.remove(pos + 1));
        args.remove(pos);
    }
    if !features && (feature_config_path.is_some() || !feature_sets.is_empty()) {
        return Err("--feature-config and --set require --features".to_string());
    }

    // --pole <name>: `--features` の極。⚠️ 名前の検証は `resolve_pole` (main が出力の前に呼ぶ)。
    let pole = if let Some(pos) = args.iter().position(|a| a == "--pole") {
        if pos + 1 >= args.len() {
            return Err("--pole requires a <name> argument".to_string());
        }
        let name = args.remove(pos + 1);
        args.remove(pos);
        // ⚠️ 2 回目の `--pole` を位置引数として残すと「positional が 3 個」という理由の分からない
        //   エラーになる (security-checker LOW・2026-09-25)。→ 重複は名指しで止める。
        if args.iter().any(|a| a == "--pole") {
            return Err("--pole may be specified only once (1 実行 1 極)".to_string());
        }
        Some(name)
    } else {
        None
    };

    // --json は集計系モード併用時のみ意味を持つ
    if json
        && !metrics
        && segments_path.is_none()
        && !intervention
        && !calibration
        && !sweep
        && !nudge_diag
        && !corr_floor
    {
        return Err(
            "--json requires --metrics, --segments, --intervention, --calibration, --sweep, --nudge-diag, or --corr-floor"
                .to_string(),
        );
    }

    // 排他チェック: 全モードは相互排他
    let mode_count = [
        metrics,
        segment,
        segments_path.is_some(),
        snapshot_path.is_some(),
        intervention,
        calibration,
        sweep,
        nudge_diag,
        corr_floor,
        features,
    ]
    .iter()
    .filter(|&&v| v)
    .count();
    if mode_count > 1 {
        return Err(
            "--metrics, --segment, --segments, --snapshot, --intervention, --calibration, --sweep, --nudge-diag, --corr-floor, --features are mutually exclusive"
                .to_string(),
        );
    }

    // positional 引数の検証。--calibration / --sweep / --nudge-diag / --corr-floor は複数セッションを
    // 受けるため ≥1 個、それ以外のモードは従来どおり厳密に 1 個。
    if args.is_empty() {
        return Err("expected at least 1 positional argument (session.ndjson)".to_string());
    }
    if !calibration && !sweep && !nudge_diag && !corr_floor && args.len() != 1 {
        return Err(format!(
            "expected 1 positional argument (session.ndjson), got {}",
            args.len()
        ));
    }
    let mut positional_iter = args.into_iter();
    let session_path = PathBuf::from(positional_iter.next().unwrap());
    let extra_sessions: Vec<PathBuf> = positional_iter.map(PathBuf::from).collect();

    Ok(Args {
        session_path,
        snapshot_path,
        metrics,
        json,
        segment,
        segments_path,
        intervention,
        calibration,
        sweep,
        nudge_diag,
        corr_floor,
        features,
        feature_config_path,
        feature_sets,
        pole,
        extra_sessions,
    })
}

fn usage() -> String {
    String::from(
        "gse-replay — NDJSON セッションを再実行し FeatSnapshot 列を生成\n\n\
         USAGE:\n    \
         gse-replay <session.ndjson> [--snapshot <golden.json>]\n    \
         gse-replay <session.ndjson> --metrics [--json]\n    \
         gse-replay <session.ndjson> --segment\n    \
         gse-replay <session.ndjson> --segments <segments.txt> [--json]\n    \
         gse-replay <session.ndjson> --intervention [--json]\n    \
         gse-replay <s1.ndjson> [s2.ndjson ...] --calibration [--json]\n    \
         gse-replay <s1.ndjson> [s2.ndjson ...] --sweep [--json]\n    \
         gse-replay <s1.ndjson> [s2.ndjson ...] --nudge-diag [--json]\n    \
         gse-replay <s1.ndjson> [s2.ndjson ...] --corr-floor [--json]\n    \
         gse-replay <session.ndjson> --features [--pole <name>] [--feature-config <cfg.json>] [--set <key>=<value> ...]\n\n\
         OPTIONS:\n    \
         --snapshot <path>   既存 JSON スナップショットと完全一致比較\n    \
         --metrics           UserLabel との混同行列・F1・中央値を算出\n    \
         --segment           活動境界で分割した .segments.txt を生成\n    \
         --segments <path>   .segments.txt を読み込み範囲マッチングでメトリクス算出\n    \
         --intervention      v2 介入ポリシーを反実仮想リプレイし HIR/Precision/Recall/DC/Burden + reason 別分解を算出\n    \
         --calibration       v0.3 較正解析 (時間隔離窓 C-index/2段ゲート/MNAR/ビネット)。1 被験者の複数セッションを時刻順に渡す\n    \
         --sweep             nudge_need を 0.50–0.90 で振り reason 別 HIR / 閾値別指標を複数セッションでプール出力 (production 不変)\n    \
         --nudge-diag        ACT decision を reason×GT で層別し決定時の特徴量分布 (min/med/max) を出力 (FP/TP 分離診断)\n    \
         --corr-floor        correction_after_pause veto floor (f4/f6) の counterfactual 候補比較 (production 不変)\n    \
         --features          ADR-030 の Tier 別 1 Hz tick 単位特徴行を出力\n    \
         出力は { provenance, config, rows } の封筒形 (2026-09-20・起票 2)\n    \
         provenance に由来 (meta 由来の事実 / 入力の basename・sha256 / capabilities)\n    \
         *** 手元の解析用中間成果物であり gse-dataset へ共有しない ***\n    \
         *** t_ms は絶対 epoch ms で、匿名化 (anonymize.rs) を通っていない ***\n    \
         *** provenance.sharing がこの 2 点を出力自身に刻む ***\n    \
         *** 門: scripts/check_no_feature_output.sh (CI で走る) ***\n    \
         設定の既定は埋め込みの凍結 JSON (src-tauri/prereg/p1-episode.json)。config.overrides に外れた値だけが残る\n    \
         --feature-config <path>  凍結 JSON と同じ形の外部ファイルから設定を読む (config.config_source = \"file\")\n    \
         --set <key>=<value>      設定を 1 キー上書きする (繰り返し可)。未知キー / 型の不一致 / 範囲外は exit 1 で出力なし\n    \
         --pole <name>            極 (ADR-030 D3): baseline (既定) / pointer_b / modifier_m_plus。1 実行 1 極で、封筒 config.pole に刻む。\n    \
         --features 以外との併用 / 未知の名前 / 未実装の極 (現状 baseline 以外はすべて) は exit 1 で出力なし\n    \
         --json              集計系モード (--metrics/--segments/--intervention/--calibration/--sweep/--nudge-diag/--corr-floor) の出力を JSON へ\n    \
         -h, --help          このヘルプを表示\n",
    )
}

/// `--sweep` / `--nudge-diag` 共通: positional セッション群を `SweepInput` 列に読み込む。
/// ファイル数が `MAX_CALIBRATION_FILES` を超えたら `Err(ExitCode::from(2))`、
/// 各セッションの読み込み失敗は `Err(ExitCode::from(1))` を返す (stderr / tracing へ出力済み)。
fn collect_sweep_inputs(
    session_path: &Path,
    extra_sessions: &[PathBuf],
) -> Result<Vec<SweepInput>, ExitCode> {
    let mut paths: Vec<PathBuf> = Vec::with_capacity(1 + extra_sessions.len());
    paths.push(session_path.to_path_buf());
    paths.extend(extra_sessions.iter().cloned());

    // ファイル数の上限 (calibration と同じ安全キャップを流用)。
    if paths.len() > MAX_CALIBRATION_FILES {
        let _ = writeln!(
            std::io::stderr(),
            "too many sessions: {} exceeds limit {}",
            paths.len(),
            MAX_CALIBRATION_FILES
        );
        return Err(ExitCode::from(2));
    }

    let mut sessions: Vec<SweepInput> = Vec::with_capacity(paths.len());
    for p in &paths {
        let feats = collect_logged_feats(p).map_err(|msg| {
            tracing::error!("failed to collect logged feats {}: {}", p.display(), msg);
            ExitCode::from(1)
        })?;
        let point_labels = collect_user_labels(p).map_err(|msg| {
            tracing::error!("failed to collect user labels {}: {}", p.display(), msg);
            ExitCode::from(1)
        })?;
        let key_press_ts = collect_key_timestamps(p);
        sessions.push(SweepInput {
            feats,
            point_labels,
            key_press_ts,
        });
    }
    Ok(sessions)
}

fn main() -> ExitCode {
    // 最小 tracing subscriber (stderr 出力、INFO 以上)。
    // rust-standards ルール 3 準拠: 警告・エラー系は tracing 経由で出す。
    // ただし CLI の「人向け結果メッセージ」(usage / OK 一致 / MISMATCH 差分) は
    // ログではなくコマンド出力として writeln!(stderr, ...) に残す。
    // `try_init` は既に subscriber が登録済みでもエラーにならない。
    let _ = tracing_subscriber::fmt()
        .with_writer(std::io::stderr)
        .with_target(false)
        .without_time()
        .try_init();

    let args = match parse_args() {
        Ok(a) => a,
        Err(msg) => {
            let _ = writeln!(std::io::stderr(), "{}", msg);
            return ExitCode::from(2);
        }
    };

    // ⚠️★★★ `--pole` は**どのモードの出力よりも前**に解決する (fail-closed)。
    // `--features` 以外での指定 / 未知の名前 / 未実装の極は exit 1 で、stdout には 1 バイトも出さない。
    // ★ 未指定なら `Baseline` (他のモードは極を読まないので何も変わらない)。
    let pole = match resolve_pole(args.features, args.pole.as_deref()) {
        Ok(v) => v,
        Err(msg) => {
            tracing::error!("invalid --pole: {}", msg);
            return ExitCode::from(1);
        }
    };

    // metrics 経路は logged feat (production wall-clock) + user_label を使う。
    // run_replay の step() 再生成 (virtual clock) は clock semantic が label と
    // 揃わず label 取りこぼしを起こすため、snapshot 検証以外には使わない
    // (decisions.md D1)。
    if args.metrics {
        let labels = match collect_user_labels(&args.session_path) {
            Ok(v) => v,
            Err(msg) => {
                tracing::error!("failed to collect user labels: {}", msg);
                return ExitCode::from(1);
            }
        };
        let feats = match collect_logged_feats(&args.session_path) {
            Ok(v) => v,
            Err(msg) => {
                tracing::error!("failed to collect logged feats: {}", msg);
                return ExitCode::from(1);
            }
        };
        let mut metrics = compute_session_metrics(&labels, &feats);
        // v0.4 アウトカム指標 (a)(b) を付与する。key/paste 行を別途収集し、p_stuck
        // エピソード上で算出する (`.steering/20260623-outcome-metrics/`)。収集が失敗した
        // 場合は outcome を **None のまま**にする (cross-review AGREE-2): 「実測ゼロ」と
        // 「データ無し」を混同させない。HMM 精度メトリクスは独立に出力される。
        let cfg = OutcomeConfig::default();
        match (
            collect_paste_events(&args.session_path),
            collect_key_events(&args.session_path),
        ) {
            (Ok((pastes, excluded_paste_count)), Ok(keys)) => {
                let episodes = segment_stuck_episodes(&feats, &cfg);
                let mut outcome = compute_outcome_metrics(&episodes, &pastes, &keys, &feats, &cfg);
                outcome.excluded_paste_count = excluded_paste_count;
                metrics.outcome = Some(outcome);
            }
            (paste_res, key_res) => {
                if let Err(msg) = &paste_res {
                    tracing::warn!("collect_paste_events failed, outcome omitted: {}", msg);
                }
                if let Err(msg) = &key_res {
                    tracing::warn!("collect_key_events failed, outcome omitted: {}", msg);
                }
                metrics
                    .warnings
                    .push("outcome metrics omitted: paste/key collection failed".to_string());
                // metrics.outcome は None のまま
            }
        }
        let stdout = std::io::stdout();
        let mut lock = stdout.lock();
        if args.json {
            match serde_json::to_string_pretty(&metrics) {
                Ok(s) => {
                    let _ = writeln!(lock, "{}", s);
                }
                Err(e) => {
                    tracing::error!("failed to serialize metrics: {}", e);
                    return ExitCode::from(1);
                }
            }
        } else {
            let _ = write!(lock, "{}", format_pretty(&metrics));
        }
        return ExitCode::SUCCESS;
    }

    // --segment 経路: セッションを活動境界で分割し .segments.txt を stdout に出力
    if args.segment {
        let feats = match collect_logged_feats(&args.session_path) {
            Ok(v) => v,
            Err(msg) => {
                tracing::error!("failed to collect logged feats: {}", msg);
                return ExitCode::from(1);
            }
        };
        let markers = collect_review_markers(&args.session_path);
        let key_timestamps = collect_key_timestamps(&args.session_path);
        let segments = build_segments(&feats, &key_timestamps, &markers);
        let stdout = std::io::stdout();
        let mut lock = stdout.lock();
        let _ = write!(
            lock,
            "{}",
            format_segments_txt(&args.session_path, &segments)
        );
        return ExitCode::SUCCESS;
    }

    // --segments 経路: .segments.txt を読み込み範囲マッチングでメトリクス算出
    if let Some(ref seg_path) = args.segments_path {
        let feats = match collect_logged_feats(&args.session_path) {
            Ok(v) => v,
            Err(msg) => {
                tracing::error!("failed to collect logged feats: {}", msg);
                return ExitCode::from(1);
            }
        };
        let range_labels = match parse_segments_file(seg_path) {
            Ok(v) => v,
            Err(msg) => {
                tracing::error!("failed to parse segments file: {}", msg);
                return ExitCode::from(1);
            }
        };
        let metrics = compute_range_metrics(&range_labels, &feats);
        let stdout = std::io::stdout();
        let mut lock = stdout.lock();
        if args.json {
            match serde_json::to_string_pretty(&metrics) {
                Ok(s) => {
                    let _ = writeln!(lock, "{}", s);
                }
                Err(e) => {
                    tracing::error!("failed to serialize metrics: {}", e);
                    return ExitCode::from(1);
                }
            }
        } else {
            let _ = write!(lock, "{}", format_pretty(&metrics));
        }
        return ExitCode::SUCCESS;
    }

    // --intervention 経路: v2 介入ポリシーをオフライン反実仮想リプレイ。
    // metrics 経路と同じく logged feat (wall-clock) を使い、decide() を時刻順に
    // ステップして HIR/Precision/DC/Burden を算出する (decisions.md D1)。
    if args.intervention {
        let feats = match collect_logged_feats(&args.session_path) {
            Ok(v) => v,
            Err(msg) => {
                tracing::error!("failed to collect logged feats: {}", msg);
                return ExitCode::from(1);
            }
        };
        let labels = match collect_user_labels(&args.session_path) {
            Ok(v) => v,
            Err(msg) => {
                tracing::error!("failed to collect user labels: {}", msg);
                return ExitCode::from(1);
            }
        };
        let key_press_ts = collect_key_timestamps(&args.session_path);
        let metrics = compute_intervention_metrics(
            &feats,
            &labels,
            &key_press_ts,
            DEFAULT_DEFER_RECOVERY_WINDOW_MS,
            &InterventionThresholds::default(),
        );
        let stdout = std::io::stdout();
        let mut lock = stdout.lock();
        if args.json {
            match serde_json::to_string_pretty(&metrics) {
                Ok(s) => {
                    let _ = writeln!(lock, "{}", s);
                }
                Err(e) => {
                    tracing::error!("failed to serialize intervention metrics: {}", e);
                    return ExitCode::from(1);
                }
            }
        } else {
            let _ = write!(lock, "{}", format_intervention_pretty(&metrics));
        }
        return ExitCode::SUCCESS;
    }

    // --features 経路: ADR-030 の Tier 別 1 Hz tick 単位特徴行を JSON 配列で出力する
    // (issue 001)。`features.rs` / `engine.rs` を経由しない独立経路 (D1)。
    if args.features {
        // ⚠️★★★ 設定は**何かを読む・書く前に**解決する (fail-closed)。
        // 未知キー / 型の不一致 / 範囲外は exit 1 で、stdout には 1 バイトも出さない。
        let resolved_config =
            match resolve_feature_config(args.feature_config_path.as_deref(), &args.feature_sets) {
                Ok(v) => v.with_pole(pole),
                Err(msg) => {
                    tracing::error!("invalid --features configuration: {}", msg);
                    return ExitCode::from(1);
                }
            };
        let keys = match collect_key_events(&args.session_path) {
            Ok(v) => v,
            Err(msg) => {
                tracing::error!("failed to collect key events: {}", msg);
                return ExitCode::from(1);
            }
        };
        // ⚠️ `collect_paste_events` ではなく**全 paste 行の時刻**を使う。
        // ★ `T0` の `pastes` は件数なので、文字数欠落の行を落とすと 0 に潰れる。
        let paste_ts = match collect_all_paste_timestamps(&args.session_path) {
            Ok(v) => v,
            Err(msg) => {
                tracing::error!("failed to collect paste events: {}", msg);
                return ExitCode::from(1);
            }
        };
        let ime_events = match collect_all_ime_shadow_events(&args.session_path) {
            Ok(v) => v,
            Err(msg) => {
                tracing::error!("failed to collect ime_shadow events: {}", msg);
                return ExitCode::from(1);
            }
        };
        let raw_feat_ts = match collect_all_feat_timestamps(&args.session_path) {
            Ok(v) => v,
            Err(msg) => {
                tracing::error!("failed to collect feat timestamps: {}", msg);
                return ExitCode::from(1);
            }
        };
        // ★ 事前宣言 v1.2 §6.1 (ADR-030 補訂 4): 長い穴とファイルの最後の直前の、入力の無い `feat` 行を落とす。
        //   ⚠️ 以後は**落とした後の列だけ**を使う (観測区間・行・品質のマスク・封筒が同じ列を見る)。
        //   入力は `key` 行 (押下・解放とも) と `pointer_bin` 行だけ (`collect_idle_trim_input_timestamps`)。
        let idle_trim_input_ts = match collect_idle_trim_input_timestamps(&args.session_path) {
            Ok(v) => v,
            Err(msg) => {
                tracing::error!("failed to collect input timestamps for idle trim: {}", msg);
                return ExitCode::from(1);
            }
        };
        let (after_idle_trim, idle_trim_summary) =
            gse_next_lib::analysis::feat_offline::idle_trim::idle_trim(
                &raw_feat_ts,
                &idle_trim_input_ts,
                resolved_config.operational.idle_trim_min_gap_ms,
                resolved_config.operational.idle_trim_max_ms,
            );
        // ★ 事前宣言 v1.3 §7.1 (ADR-030 補訂 5): 入力の間が `idle_trim_input_gap_ms` 以上空いた区間の `feat` 行を落とす。
        //   ⚠️ 境 (ファイルの最初と最後) は idle trim の**前の**列から取る —— 後の列から取ると、idle trim が
        //   末尾を削ったぶんだけ無入力が短く測られ、落とすべき区間を見落とす。落ちる行は 2 つの規則の和集合になる。
        let (feat_ts, input_gap_trim_summary) =
            match (raw_feat_ts.iter().min(), raw_feat_ts.iter().max()) {
                (Some(&first), Some(&last)) => {
                    gse_next_lib::analysis::feat_offline::idle_trim::input_gap_trim(
                        &after_idle_trim,
                        &idle_trim_input_ts,
                        first,
                        last,
                        resolved_config.operational.idle_trim_input_gap_ms,
                    )
                }
                _ => (after_idle_trim, Default::default()),
            };
        let task_kind_declarations = match collect_task_kind_declarations(&args.session_path) {
            Ok(v) => v,
            Err(msg) => {
                tracing::error!("failed to collect task_kind declarations: {}", msg);
                return ExitCode::from(1);
            }
        };
        // 起票 2 (封筒) ＋ issue 007 (`Q`): `meta`(session_start) 行から
        // セッション単位の事実と `capabilities` を **1 パスで**読む。
        // ⚠️★★★ 2026-09-20: 以前は `capabilities` を別関数が**別の条件**で拾っており、
        //   連結ログで別セグメントの宣言が混ざった (実測)。→ 同じ行から取る。
        // ⚠️ capabilities は「無い」では落とさない (AC7) が、「形が壊れている」
        // (JSON オブジェクトでない / 4096 バイト超) では落とす (判断 24・AC15)。
        let meta_facts = match collect_meta_session_facts(&args.session_path) {
            Ok(v) => v,
            Err(msg) => {
                tracing::error!("failed to collect meta session facts: {}", msg);
                return ExitCode::from(1);
            }
        };
        let capabilities = meta_facts.capabilities;
        // ⚠️ hook_health は「無い / 形が合わない」で --features を落とさない (旧ログ互換・AC12)。
        let hook_health_events = match collect_all_hook_health_events(&args.session_path) {
            Ok(v) => v,
            Err(msg) => {
                tracing::error!("failed to collect hook_health events: {}", msg);
                return ExitCode::from(1);
            }
        };
        // 起票 2 (封筒): 入力ファイルの同一性。
        // ⚠️ 「行の計算」ではなく「実行の由来」なので、`feat_offline` ではなくここ (CLI) が読む。
        let source_sha256_prefix = match sha256_prefix_of_file(&args.session_path) {
            Ok(v) => v,
            Err(msg) => {
                tracing::error!("failed to hash session file: {}", msg);
                return ExitCode::from(1);
            }
        };
        let stall_onset_config = resolved_config.stall_onset_config();
        // ★ 観測区間は 1 度だけ作り、極 M+ の打ち切りと封筒 `provenance` の両方へ渡す
        //   (⚠️ 区間の定義をここで作り直さない)。
        let observed = gse_next_lib::analysis::feat_offline::stall_onset::observed_intervals(
            &feat_ts,
            stall_onset_config.hole_gap_ms,
        );
        // ⚠️★★★ 修飾キーの押下区間を要るのは**極 M+ だけ**。他の極では走査しない
        //   (★ baseline の出力・実行経路を 1 バイトも変えない・`--snapshot` / `--metrics` へも配線しない)。
        let modifier_scan = if pole == Pole::ModifierMPlus {
            match collect_modifier_intervals(&args.session_path, &observed) {
                Ok(v) => Some(v),
                Err(msg) => {
                    tracing::error!("failed to collect modifier intervals: {}", msg);
                    return ExitCode::from(1);
                }
            }
        } else {
            None
        };
        // ⚠️★★★ 極 B の抑制区間に `pointer_bin` の行を要るのは**極 B だけ**。他の極ではここで走査しない。
        //   ⚠️ ただし 2026-10-08 から、無入力の末尾の前処理 (`collect_idle_trim_input_timestamps`) が
        //   **全極で** `pointer_bin` 行の時刻を読む (baseline の観測区間の右端にも効く・上の `idle_trim`)。
        let pointer_rows: Option<Vec<u64>> = if pole == Pole::PointerB {
            match collect_pointer_bin_timestamps(&args.session_path) {
                Ok(v) => Some(v),
                Err(msg) => {
                    tracing::error!("failed to collect pointer_bin timestamps: {}", msg);
                    return ExitCode::from(1);
                }
            }
        } else {
            None
        };
        // ★ 極 B の適用可否は `capabilities` の宣言で決める (⚠️ `analysis/` へは意味を持ち込まない)。
        //   宣言が無い入力は「計器が無かった」= 適用不可 → **抑制しない** (空を渡す = baseline と恒等)。
        let pointer_declared = declares_pointer_bin(capabilities.as_ref());
        let no_pointer_rows: Vec<u64> = Vec::new();
        let pointer_active_ts: Option<&[u64]> = match &pointer_rows {
            Some(rows) if pointer_declared => Some(rows.as_slice()),
            Some(_) => Some(no_pointer_rows.as_slice()),
            None => None,
        };
        let pole_inputs = PoleInputs {
            modifier_intervals: modifier_scan.as_ref().map(|s| s.intervals.as_slice()),
            pointer_active_ts,
        };
        // ★ 封筒の `provenance.observed_intervals` は「実際に評価した区間」。極 B では抑制区間を除いた区間で、
        //   ⚠️ 検出と**同じ 2 つの関数** (`pointer_suppression_intervals` / `evaluation_intervals`) から作る
        //   (区間の定義をここで作り直さない)。極 B 以外は観測区間そのまま。
        let evaluated_intervals: Vec<(u64, u64)> = match pointer_active_ts {
            Some(ts) => {
                use gse_next_lib::analysis::feat_offline::stall_onset::{
                    evaluation_intervals, pointer_suppression_intervals,
                };
                evaluation_intervals(
                    &observed,
                    &pointer_suppression_intervals(ts, ENGINE_TICK_MS),
                )
            }
            None => observed.clone(),
        };
        let stall_onset_inputs = gse_next_lib::analysis::feat_offline::StallOnsetInputs {
            feat_ts: &feat_ts,
            task_kind_declarations: &task_kind_declarations,
            config: stall_onset_config,
        };
        // ⚠️★★★ 2026-09-20 改訂 (判断 3・封筒): 行には `capabilities` の**値を渡さない**。
        // 宣言の有無だけが tick ごとの `missing_reasons` に効き、値は封筒が 1 回だけ持つ。
        // ★ これで 2026-09-18 に入れた `Arc` 共有 (判断 24・code-reviewer M4) も不要になった。
        let quality_inputs = gse_next_lib::analysis::feat_offline::QualityInputs {
            capabilities_declared: capabilities.is_some(),
            hook_health: &hook_health_events,
        };
        let rows = match gse_next_lib::analysis::feat_offline::build_feature_rows_with_pole_inputs(
            &keys,
            &paste_ts,
            &ime_events,
            MAX_FEATURE_TICKS,
            &stall_onset_inputs,
            &quality_inputs,
            &pole_inputs,
        ) {
            Ok(v) => v,
            Err(msg) => {
                tracing::error!("failed to build feature rows: {}", msg);
                return ExitCode::from(1);
            }
        };
        let envelope = FeatureEnvelope {
            provenance: FeatureProvenance {
                sharing: SharingMarker::default(),
                tool: "gse-replay",
                tool_version: env!("CARGO_PKG_VERSION"),
                source_basename: source_basename_of(&args.session_path),
                source_sha256_prefix,
                session_start: meta_facts.session_start,
                hmm_version: meta_facts.hmm_version,
                app_version: meta_facts.app_version,
                g1_mode: meta_facts.g1_mode,
                o1_mode: meta_facts.o1_mode,
                keyboard_layout: meta_facts.keyboard_layout,
                capabilities,
                // ★ 行と同じ SSOT (`stall_onset::observed_intervals`) から作った `observed`
                //   (極 B では抑制区間を除いた評価区間・上の `evaluated_intervals`)。
                //   ⚠️ 区間の定義をここで作り直さない。
                observed_intervals: evaluated_intervals
                    .iter()
                    .map(|&(a_ms, b_ms)| ObservedIntervalDto { a_ms, b_ms })
                    .collect(),
                idle_trim: IdleTrimDto {
                    dropped_feat_rows: idle_trim_summary.dropped_feat_rows,
                    spans: idle_trim_summary
                        .spans
                        .iter()
                        .map(|&(a_ms, b_ms)| ObservedIntervalDto { a_ms, b_ms })
                        .collect(),
                },
                input_gap_trim: IdleTrimDto {
                    dropped_feat_rows: input_gap_trim_summary.dropped_feat_rows,
                    spans: input_gap_trim_summary
                        .spans
                        .iter()
                        .map(|&(a_ms, b_ms)| ObservedIntervalDto { a_ms, b_ms })
                        .collect(),
                },
            },
            config: FeatureConfigDto::from_resolved(
                &resolved_config,
                MAX_FEATURE_TICKS,
                modifier_scan.as_ref().map(|s| s.rows),
                modifier_scan.as_ref().map(|s| s.truncated_at_right_edge),
                modifier_scan.as_ref().map(|s| s.orphan_releases),
            )
            .with_pointer_evidence(
                pointer_declared,
                pointer_rows.as_ref().map(|rows| rows.len() as u64),
            ),
            rows: &rows,
        };
        // ⚠️★★★ 2026-09-18 改訂 (判断 24・security-checker LOW-3): `to_string_pretty` で
        // 一旦 `String` に全体を確保してから書き出すのをやめ、`to_writer_pretty` で
        // `BufWriter` へ直接流す (巨大な出力を 2 重に確保しない)。
        // ★ 2026-09-20 (起票 2): 流し込む対象が配列から封筒へ変わったが、
        //   `rows` を**参照で**持つので行を複製しない点は変わらない。
        let stdout = std::io::stdout();
        let mut writer = std::io::BufWriter::new(stdout.lock());
        if let Err(e) = serde_json::to_writer_pretty(&mut writer, &envelope) {
            tracing::error!("failed to serialize feature envelope: {}", e);
            return ExitCode::from(1);
        }
        if let Err(e) = writer.write_all(b"\n") {
            tracing::error!("failed to write feature envelope: {}", e);
            return ExitCode::from(1);
        }
        if let Err(e) = writer.flush() {
            tracing::error!("failed to flush feature envelope: {}", e);
            return ExitCode::from(1);
        }
        return ExitCode::SUCCESS;
    }

    // --sweep 経路: nudge_need を 0.50–0.90 (0.05 刻み) で振り、reason 別 HIR / 閾値別の
    // HIR/Precision/Recall/DC/Burden を全セッションでプール出力する (Phase 0、production 不変)。
    // --calibration と同じく複数セッションを受け、各セッションを独立評価してプールする。
    if args.sweep {
        let sessions = match collect_sweep_inputs(&args.session_path, &args.extra_sessions) {
            Ok(s) => s,
            Err(code) => return code,
        };
        let report = compute_intervention_sweep(
            &sessions,
            &DEFAULT_SWEEP_NUDGE_NEED,
            DEFAULT_DEFER_RECOVERY_WINDOW_MS,
        );
        let stdout = std::io::stdout();
        let mut lock = stdout.lock();
        if args.json {
            match serde_json::to_string_pretty(&report) {
                Ok(s) => {
                    let _ = writeln!(lock, "{}", s);
                }
                Err(e) => {
                    tracing::error!("failed to serialize sweep report: {}", e);
                    return ExitCode::from(1);
                }
            }
        } else {
            let _ = write!(lock, "{}", format_intervention_sweep_pretty(&report));
        }
        return ExitCode::SUCCESS;
    }

    // --nudge-diag 経路: ACT decision を reason×GT で層別し決定時の特徴量分布 (min/median/max) を
    // プール出力する (Phase 0、production 不変)。FP(GT=PROTECT) と TP(GT=STALL) の分離可能性を診断する。
    if args.nudge_diag {
        let sessions = match collect_sweep_inputs(&args.session_path, &args.extra_sessions) {
            Ok(s) => s,
            Err(code) => return code,
        };
        let diag = compute_nudge_diagnostic(&sessions, &InterventionThresholds::default());
        let stdout = std::io::stdout();
        let mut lock = stdout.lock();
        if args.json {
            match serde_json::to_string_pretty(&diag) {
                Ok(s) => {
                    let _ = writeln!(lock, "{}", s);
                }
                Err(e) => {
                    tracing::error!("failed to serialize nudge diagnostic: {}", e);
                    return ExitCode::from(1);
                }
            }
        } else {
            let _ = write!(lock, "{}", format_nudge_diagnostic_pretty(&diag));
        }
        return ExitCode::SUCCESS;
    }

    // --corr-floor 経路: correction_after_pause veto floor (f4/f6) の counterfactual 候補
    // (baseline / f4 / f6 / both) を全セッションでプール評価し HIR/recall を比較する (production 不変)。
    if args.corr_floor {
        let sessions = match collect_sweep_inputs(&args.session_path, &args.extra_sessions) {
            Ok(s) => s,
            Err(code) => return code,
        };
        let report = compute_correction_floor_report(&sessions, DEFAULT_DEFER_RECOVERY_WINDOW_MS);
        let stdout = std::io::stdout();
        let mut lock = stdout.lock();
        if args.json {
            match serde_json::to_string_pretty(&report) {
                Ok(s) => {
                    let _ = writeln!(lock, "{}", s);
                }
                Err(e) => {
                    tracing::error!("failed to serialize correction floor report: {}", e);
                    return ExitCode::from(1);
                }
            }
        } else {
            let _ = write!(lock, "{}", format_correction_floor_pretty(&report));
        }
        return ExitCode::SUCCESS;
    }

    // --calibration 経路: v0.3 較正解析 (Task D)。1 被験者の複数セッション NDJSON を時刻順に受け、
    // 時間隔離窓で X/Y を集約 → 被験者内 C-index → holdout → MNAR → ビネット → 二軸性を算出する。
    // frontend を起動せず NDJSON のみを読む。被験者横断の最終ゲートは Task E。
    if args.calibration {
        let mut paths: Vec<PathBuf> = Vec::with_capacity(1 + args.extra_sessions.len());
        paths.push(args.session_path.clone());
        paths.extend(args.extra_sessions.iter().cloned());

        // ファイル数の上限 (各ファイルは MAX_SESSION_BYTES でも保護されるが、数の暴走を防ぐ)。
        if paths.len() > MAX_CALIBRATION_FILES {
            let _ = writeln!(
                std::io::stderr(),
                "too many calibration sessions: {} exceeds limit {}",
                paths.len(),
                MAX_CALIBRATION_FILES
            );
            return ExitCode::from(2);
        }
        // 前向き holdout には main セッション 3 本以上が要る (先頭 2 = 較正)。
        if paths.len() < HOLDOUT_CALIBRATION_SESSIONS + 1 {
            tracing::warn!(
                sessions = paths.len(),
                "calibration: prospective-holdout C-index requires ≥{} sessions (first {} are calibration); \
                 eval set will be empty",
                HOLDOUT_CALIBRATION_SESSIONS + 1,
                HOLDOUT_CALIBRATION_SESSIONS
            );
        }

        let mut sessions: Vec<SessionData> = Vec::with_capacity(paths.len());
        for p in &paths {
            match load_calibration_session(p) {
                Ok(s) => sessions.push(s),
                Err(msg) => {
                    tracing::error!(
                        "failed to load calibration session {}: {}",
                        p.display(),
                        msg
                    );
                    return ExitCode::from(1);
                }
            }
        }
        // 既定の窓集約スペック (ewma の中央値, 設計判断 A)。
        let report = compute_calibration_metrics(&sessions, AggSpec::default());
        let stdout = std::io::stdout();
        let mut lock = stdout.lock();
        if args.json {
            match serde_json::to_string_pretty(&report) {
                Ok(s) => {
                    let _ = writeln!(lock, "{}", s);
                }
                Err(e) => {
                    tracing::error!("failed to serialize calibration report: {}", e);
                    return ExitCode::from(1);
                }
            }
        } else {
            let _ = write!(lock, "{}", format_calibration_pretty(&report));
        }
        return ExitCode::SUCCESS;
    }

    // snapshot 経路 (デフォルト JSON 出力 / --snapshot 比較) は run_replay で
    // step() 再実行し決定論を検証する。こちらは従来通り。
    let snapshots = match run_replay(&args.session_path) {
        Ok(s) => s,
        Err(msg) => {
            tracing::error!("replay failed: {}", msg);
            return ExitCode::from(1);
        }
    };

    match args.snapshot_path {
        None => {
            // stdout に JSON 配列を出力（データ出力、ログではない）
            let json = match serde_json::to_string_pretty(&snapshots) {
                Ok(s) => s,
                Err(e) => {
                    tracing::error!("failed to serialize snapshots: {}", e);
                    return ExitCode::from(1);
                }
            };
            let stdout = std::io::stdout();
            let mut lock = stdout.lock();
            let _ = writeln!(lock, "{}", json);
            ExitCode::SUCCESS
        }
        Some(path) => {
            // 既存スナップショットと比較
            match compare_snapshots(&snapshots, &path) {
                Ok(()) => {
                    let _ = writeln!(
                        std::io::stderr(),
                        "OK: {} snapshots match {}",
                        snapshots.len(),
                        path.display()
                    );
                    ExitCode::SUCCESS
                }
                Err(msg) => {
                    let _ = writeln!(std::io::stderr(), "MISMATCH: {}", msg);
                    ExitCode::from(1)
                }
            }
        }
    }
}

/// Phase 1 Task 2: NDJSON から `{"type":"user_label", ...}` 行のみを抽出する。
///
/// `run_replay` は step() 再実行に関係するイベントのみ処理するため、UserLabel は
/// 読み飛ばされる。metrics 経路では別途抽出する (ファイルを 2 回読むがサイズ上限
/// 500MB + 通常セッション数 MB のため実害なし)。未知 label は警告にせず黙ってスキップ
/// する (将来の互換性のため)。
fn collect_user_labels(session_path: &PathBuf) -> Result<Vec<UserLabelEvent>, String> {
    let metadata = std::fs::metadata(session_path)
        .map_err(|e| format!("cannot stat {}: {}", session_path.display(), e))?;
    if metadata.len() > MAX_SESSION_BYTES {
        return Err(format!(
            "session file too large: {} bytes exceeds limit {} bytes",
            metadata.len(),
            MAX_SESSION_BYTES
        ));
    }
    let file = File::open(session_path)
        .map_err(|e| format!("cannot open {}: {}", session_path.display(), e))?;
    let reader = BufReader::new(file);
    let mut out: Vec<UserLabelEvent> = Vec::new();
    // silent skip の可視化 (security-checker MEDIUM 指摘、collect_logged_feats と同方針)
    let mut parse_failed_lines: u64 = 0;
    let mut unknown_label_count: u64 = 0;
    for (lineno, line) in reader.lines().enumerate() {
        let line = line.map_err(|e| format!("read error at line {}: {}", lineno + 1, e))?;
        if line.trim().is_empty() {
            continue;
        }
        let ev: ReplayEvent = match serde_json::from_str(&line) {
            Ok(v) => v,
            Err(_) => {
                parse_failed_lines += 1;
                continue;
            }
        };
        if let ReplayEvent::UserLabel { t, label, .. } = ev {
            if let Some(lc) = LabelClass::parse(&label) {
                out.push(UserLabelEvent {
                    timestamp: t,
                    label: lc,
                });
            } else {
                unknown_label_count += 1;
            }
        }
    }
    if parse_failed_lines > 0 {
        tracing::warn!(
            skipped = parse_failed_lines,
            "collect_user_labels: NDJSON lines failed to parse as ReplayEvent"
        );
    }
    if unknown_label_count > 0 {
        tracing::warn!(
            skipped = unknown_label_count,
            "collect_user_labels: user_label entries with unknown label class (forward-compat skip)"
        );
    }
    out.sort_by_key(|l| l.timestamp);
    Ok(out)
}

/// Phase 1: NDJSON の `{"type":"feat", ...}` 行を `FeatSnapshot` 列として抽出する。
///
/// `run_replay` が step() 再実行で生成する virtual-clock feat と異なり、production
/// が wall-clock で書いた feat 行をそのまま source of truth として使う。user_label
/// との時刻軸を揃えるのが目的 (`decisions.md` D1)。未知 type / parse error は
/// silent skip (`collect_user_labels` と同方針)。
fn collect_logged_feats(session_path: &PathBuf) -> Result<Vec<FeatSnapshot>, String> {
    let metadata = std::fs::metadata(session_path)
        .map_err(|e| format!("cannot stat {}: {}", session_path.display(), e))?;
    if metadata.len() > MAX_SESSION_BYTES {
        return Err(format!(
            "session file too large: {} bytes exceeds limit {} bytes",
            metadata.len(),
            MAX_SESSION_BYTES
        ));
    }
    let file = File::open(session_path)
        .map_err(|e| format!("cannot open {}: {}", session_path.display(), e))?;
    let reader = BufReader::new(file);
    let mut out: Vec<FeatSnapshot> = Vec::new();
    // silent skip を可視化する: parse 失敗行数をカウントし件数のみ warn で出す
    // (内容はプライバシーのため出さない)。security-checker MEDIUM 指摘対応。
    let mut parse_failed_lines: u64 = 0;
    let mut feat_decode_failed: u64 = 0;
    let mut feat_validation_failed: u64 = 0;
    // ★ Tier 0 配線以前の feat 行 (keys/bs_keys を持たない) の件数。
    let mut feat_missing_tier0: u64 = 0;
    for (lineno, line) in reader.lines().enumerate() {
        let line = line.map_err(|e| format!("read error at line {}: {}", lineno + 1, e))?;
        if line.trim().is_empty() {
            continue;
        }
        let ev: ReplayEvent = match serde_json::from_str(&line) {
            Ok(v) => v,
            Err(_) => {
                parse_failed_lines += 1;
                continue;
            }
        };
        if let ReplayEvent::Feat(val) = ev {
            let dto: LoggedFeatDto = match serde_json::from_value(val) {
                Ok(d) => d,
                Err(_) => {
                    feat_decode_failed += 1;
                    continue;
                }
            };
            // ★ Tier 0: 配線以前のログには keys/bs_keys が無く、`0` に倒れる。
            // ⚠️ 消費者 (Python / DuckDB 側) は Rust の doc コメントを読めないので、
            // 「実測 0 打ではなく欠測である」ことを CLI 出力で気づけるようにする。
            if dto.keys.is_none() || dto.bs_keys.is_none() {
                feat_missing_tier0 += 1;
            }
            // M3: TryFrom で NaN/Inf/範囲外を reject、汚染を metrics 前段で止める
            match FeatSnapshot::try_from(dto) {
                Ok(f) => out.push(f),
                Err(_) => {
                    feat_validation_failed += 1;
                    continue;
                }
            }
        }
    }
    if feat_validation_failed > 0 {
        tracing::warn!(
            skipped = feat_validation_failed,
            "collect_logged_feats: feat entries failed NaN/Inf/range validation \
             (see FeatSnapshot::try_from rules — prevents silent argmax corruption)"
        );
    }
    if parse_failed_lines > 0 {
        tracing::warn!(
            skipped = parse_failed_lines,
            "collect_logged_feats: NDJSON lines failed to parse as ReplayEvent"
        );
    }
    if feat_decode_failed > 0 {
        tracing::warn!(
            skipped = feat_decode_failed,
            "collect_logged_feats: feat entries failed to decode as LoggedFeatDto \
             (possible schema drift vs schema_dto::LogEntryDto::Feat)"
        );
    }
    if feat_missing_tier0 > 0 {
        tracing::warn!(
            missing = feat_missing_tier0,
            "collect_logged_feats: feat entries have no keys/bs_keys (pre-Tier0-wiring log). \
             They are reported as 0, which is INDISTINGUISHABLE from 'measured zero keystrokes'. \
             Do NOT compute progress_proxy (= keys - bs_keys) from this session."
        );
    }
    if out.is_empty() {
        tracing::warn!(
            "collect_logged_feats: no feat entries found — metrics will have zero support. \
             Verify session NDJSON was generated by hmm_version >= 0.2.0 with Phase 1 feat logging."
        );
    }
    out.sort_by_key(|f| f.timestamp);
    Ok(out)
}

/// v0.4: NDJSON の `{"type":"paste", ...}` 行から `PasteEvent` 列を抽出する。
///
/// `external_paste_chars` が Some の paste 行のみ収集する (capture-schema-freeze 以降)。
/// 旧 NDJSON (フィールド欠落 → None) の paste は文字数不明のため outcome 集計から除外する
/// (`.steering/20260623-outcome-metrics/decisions.md` CD-OM3)。中身は一切読まない (数値のみ)。
/// 戻り値 = (capture 済 paste 列, 文字数欠落で除外した paste 件数)。後者は
/// `OutcomeMetrics.excluded_paste_count` に載せ、偏りの透明性を確保する。
/// `--features` 用: NDJSON の `{"type":"paste", ...}` 行の**時刻をすべて**返す。
///
/// ⚠️★★★ [`collect_paste_events`] と**用途が違う**ので分けてある。
/// ★ あちらは `external_paste_chars` を持つ行だけを集める (文字数が要る `--metrics` 用)。
/// ⚠️ `T0` の `pastes` は **件数**なので、文字数が欠落した行を落とすと
/// 「paste が無かった」と「paste は在ったが文字数が取れなかった」が `0` に潰れる
/// (★ 実測: `tests/fixtures/minimal.ndjson:22` は文字数の無い paste 行で、
///  分けなかった初版では全 tick が `pastes: 0` になっていた。2026-09-15・レビュー MEDIUM)。
/// ⚠️ 中身は一切読まない (時刻のみ)。
fn collect_all_paste_timestamps(session_path: &PathBuf) -> Result<Vec<u64>, String> {
    let metadata = std::fs::metadata(session_path)
        .map_err(|e| format!("cannot stat {}: {}", session_path.display(), e))?;
    if metadata.len() > MAX_SESSION_BYTES {
        return Err(format!(
            "session file too large: {} bytes exceeds limit {} bytes",
            metadata.len(),
            MAX_SESSION_BYTES
        ));
    }
    let file = File::open(session_path)
        .map_err(|e| format!("cannot open {}: {}", session_path.display(), e))?;
    let reader = BufReader::new(file);
    let mut out: Vec<u64> = Vec::new();
    let mut parse_failed_lines: u64 = 0;
    for (lineno, line) in reader.lines().enumerate() {
        let line = line.map_err(|e| format!("read error at line {}: {}", lineno + 1, e))?;
        if line.trim().is_empty() {
            continue;
        }
        let ev: ReplayEvent = match serde_json::from_str(&line) {
            Ok(v) => v,
            Err(_) => {
                parse_failed_lines += 1;
                continue;
            }
        };
        if let ReplayEvent::Paste { t, .. } = ev {
            out.push(t);
        }
    }
    if parse_failed_lines > 0 {
        tracing::warn!(
            failed = parse_failed_lines,
            "collect_all_paste_timestamps: some lines failed to parse as ReplayEvent"
        );
    }
    out.sort_unstable();
    Ok(out)
}

/// `--features` 専用の `ime_shadow` DTO。
///
/// ⚠️★★★ **`ReplayEvent::ImeShadow` は `serde_json::Value` のまま置き、構造化はここで行う。**
/// ★ `--snapshot` / `--metrics` の受理集合を 1 バイトも狭めないための分離であり、
/// **`feat` 行の [`LoggedFeatDto`] と同じ手法**である (`ReplayEvent::ImeShadow` の doc を参照)。
/// ★ フィールド名は `logger.rs::format_ime_shadow_line` の NDJSON 実形式に一致させる。
#[derive(Debug, serde::Deserialize)]
struct ImeShadowDto {
    t: u64,
    dwell_ms: u64,
    nav: u32,
    abandon: bool,
}

/// `--features` (`T1b`・issue 002) 用: NDJSON の `{"type":"ime_shadow", ...}` 行を
/// [`ImeShadowEvent`] 列として抽出する。中身は `dwell_ms` / `nav` / `abandon` の 3 値のみ
/// (IME 局面は既存 `ime_shadow` フィールドの範囲に閉じる。`.idea/survey §6.3` の追加候補は
/// `capability matrix` (ADR-032 M7) が先)。
///
/// ⚠️★★★ **形が合わない `ime_shadow` 行は捨てる (0 に畳まない)。**
/// ★ ここで `unwrap_or(0)` すると **「変換が 0 だった」と「値が取れなかった」が同じ 0 になる** ——
/// `capabilities.rs` 逐語「0 行は依然『判定不能』であって『信号が無かった』ではない」に反する。
/// → ★ 捨てたことは**件数だけ** `warn` に残す (⚠️ 行の中身は出さない)。
/// ⚠️ 「何行捨てたか」の下流への伝達は **issue 007 (`Q`) の担当**である (本 issue では出力に載せない)。
fn collect_all_ime_shadow_events(session_path: &PathBuf) -> Result<Vec<ImeShadowEvent>, String> {
    let metadata = std::fs::metadata(session_path)
        .map_err(|e| format!("cannot stat {}: {}", session_path.display(), e))?;
    if metadata.len() > MAX_SESSION_BYTES {
        return Err(format!(
            "session file too large: {} bytes exceeds limit {} bytes",
            metadata.len(),
            MAX_SESSION_BYTES
        ));
    }
    let file = File::open(session_path)
        .map_err(|e| format!("cannot open {}: {}", session_path.display(), e))?;
    let reader = BufReader::new(file);
    let mut out: Vec<ImeShadowEvent> = Vec::new();
    let mut parse_failed_lines: u64 = 0;
    let mut incomplete_lines: u64 = 0;
    for (lineno, line) in reader.lines().enumerate() {
        let line = line.map_err(|e| format!("read error at line {}: {}", lineno + 1, e))?;
        if line.trim().is_empty() {
            continue;
        }
        let ev: ReplayEvent = match serde_json::from_str(&line) {
            Ok(v) => v,
            Err(_) => {
                parse_failed_lines += 1;
                continue;
            }
        };
        if let ReplayEvent::ImeShadow(v) = ev {
            // ⚠️ 形が合った行だけを採る。欠け・型違いは 0 に畳まず捨てる (関数 doc 参照)。
            match serde_json::from_value::<ImeShadowDto>(v) {
                Ok(dto) => out.push(ImeShadowEvent {
                    t_ms: dto.t,
                    dwell_ms: dto.dwell_ms,
                    nav: dto.nav,
                    abandon: dto.abandon,
                }),
                Err(_) => incomplete_lines += 1,
            }
        }
    }
    if parse_failed_lines > 0 {
        tracing::warn!(
            failed = parse_failed_lines,
            "collect_all_ime_shadow_events: some lines failed to parse as ReplayEvent"
        );
    }
    if incomplete_lines > 0 {
        tracing::warn!(
            skipped = incomplete_lines,
            "collect_all_ime_shadow_events: ime_shadow lines whose dwell_ms/nav/abandon did not \
             match the logger format were skipped (not folded into 0)"
        );
    }
    out.sort_by_key(|e| e.t_ms);
    Ok(out)
}

/// `meta.capabilities` の**形と大きさ**を検査する (2026-09-18・security-checker LOW-3・判断 24)。
///
/// JSON オブジェクトでない、または直列化して [`MAX_CAPABILITIES_BYTES`] を超えるなら `Err`
/// (`--features` は exit 1)。★ 理由は出すが、**値の中身は出さない**。
/// ⚠️ `null` に倒さない —— 倒すと「宣言が無い」と誤報になる。
fn validate_meta_capabilities(
    cap: &serde_json::Value,
    lineno: usize,
) -> Result<serde_json::Value, String> {
    if !cap.is_object() {
        return Err(format!(
            "line {}: meta.capabilities is not a JSON object",
            lineno
        ));
    }
    let serialized = serde_json::to_string(cap)
        .map_err(|e| format!("line {}: failed to serialize capabilities: {}", lineno, e))?;
    if serialized.len() > MAX_CAPABILITIES_BYTES {
        return Err(format!(
            "line {}: meta.capabilities serializes to {} bytes, exceeds limit {} bytes",
            lineno,
            serialized.len(),
            MAX_CAPABILITIES_BYTES
        ));
    }
    Ok(cap.clone())
}

/// `--features` の封筒用: NDJSON の `meta` 行からセッション単位の事実を **1 パスで**取り出す
/// (起票 2・`capabilities` を含む)。
///
/// ⚠️★★★ **`ReplayEvent::Meta` に型付きフィールドとして持たせない**
/// (2026-09-18 改訂・security-checker LOW-1: 型付きフィールドを足したことで `run_replay`
/// 側の受理集合が狭まった)。★ 行をまず `serde_json::Value` として読む
/// (`ImeShadow` / `HookHealth` と同じ「まず Value で受け、構造化は専用の関数が担う」手法)。
/// これにより `--snapshot` (`run_replay`) 側の `Meta` 型は元の 3 フィールドのまま変わらない。
///
/// ★ 採るのは **`session_start` を持つ最初の `meta` 行**で、`capabilities` も**その同じ行**から取る。
///
/// ⚠️★★★ **2026-09-20 改訂 (封筒・code-reviewer MEDIUM)**: 旧版は `capabilities` を
/// 別関数 (`collect_meta_capabilities`) が**別の条件**——「`capabilities` を持つ最初の `meta` 行」
/// ——で拾っており、★ **同じ行である保証が無かった**。
/// ⚠️ 実測 (2026-09-20): ローテートで 2 セグメントを連結し、前半の `meta` に `capabilities` が
/// 無い NDJSON を食わせると、封筒が **前半の `session_start` / `hmm_version` / `app_version` と
/// 後半の `capabilities`** を並べて提示した。★ 封筒は「どの計器条件で取れた行か」を保証する
/// ために入れたので、ここが混ざるのは目的を直撃する。→ **1 行・1 パスに統合した。**
/// ★ 副産物として、`meta` 行が無い入力に対する**全行パースのフルパスが 1 本減った**。
///
/// ⚠️★★★ **欠けていても `Err` にしない。** キーが無い / 値の型が違う / `meta` 行そのものが
/// 無い場合は該当フィールドが `None` になるだけである (旧ログ互換。`hook_health` と同じ作法・
/// 007 の AC12)。★ ただし `capabilities` が**在るのに壊れている**ときだけは `Err`
/// ([`validate_meta_capabilities`]・判断 24・AC15) —— 「無い」と「壊れている」は別である。
fn collect_meta_session_facts(session_path: &PathBuf) -> Result<MetaSessionFacts, String> {
    let metadata = std::fs::metadata(session_path)
        .map_err(|e| format!("cannot stat {}: {}", session_path.display(), e))?;
    if metadata.len() > MAX_SESSION_BYTES {
        return Err(format!(
            "session file too large: {} bytes exceeds limit {} bytes",
            metadata.len(),
            MAX_SESSION_BYTES
        ));
    }
    let file = File::open(session_path)
        .map_err(|e| format!("cannot open {}: {}", session_path.display(), e))?;
    let reader = BufReader::new(file);
    let mut parse_failed_lines: u64 = 0;
    for (lineno, line) in reader.lines().enumerate() {
        let line = line.map_err(|e| format!("read error at line {}: {}", lineno + 1, e))?;
        if line.trim().is_empty() {
            continue;
        }
        let raw: serde_json::Value = match serde_json::from_str(&line) {
            Ok(v) => v,
            Err(_) => {
                parse_failed_lines += 1;
                continue;
            }
        };
        if raw.get("type").and_then(|t| t.as_str()) != Some("meta") {
            continue;
        }
        // ★ `session_end` 形の `meta` 行には `session_start` が無いので、ここで弾かれる。
        let Some(session_start) = raw.get("session_start").and_then(|v| v.as_u64()) else {
            continue;
        };
        // ⚠️★★★ **自由文の上限を課す** (2026-09-20・security-checker M1)。
        //   ★ 信頼境界: O1 は被験者端末で生成された NDJSON を研究者が復号して食わせるので、
        //     `meta` 行の中身は**被験者が編集しうる入力**である。
        //   ⚠️ 旧版は長さも文字種も無制限に封筒へ複写していた —— ★ 同じ `meta` 行から採る
        //     `capabilities` には 4096 バイトの上限があるのに、ここには何も無かった。
        //
        // ⚠️★★★ **超過は `Err`。`None` に倒さない** (2026-09-20 改訂・Codex /cross-review 1 巡目)。
        //   ★ 最初は「切り詰めずに `None`」にしたが、⚠️ **出力だけを見ると「未宣言」と
        //     「壊れた長大値」が区別できない**（tracing の警告はバッチ実行で流れる）。
        //   ★ `capabilities` と同じ規律に揃える —— **「無い」は `None` / 「壊れている」は `Err`**。
        //     ⚠️ 正常な値は semver / enum / レイアウト識別子で数十バイトなので、
        //     256 を超えるのは編集された入力だけである。
        let str_field = |k: &str| -> Result<Option<String>, String> {
            let Some(v) = raw.get(k).and_then(|v| v.as_str()) else {
                return Ok(None);
            };
            if v.len() > MAX_META_STRING_BYTES {
                // ★ 理由と大きさは出すが、⚠️ **値の中身は出さない** (`capabilities` と同じ作法)。
                return Err(format!(
                    "line {}: meta.{} is {} bytes, exceeds limit {} bytes",
                    lineno + 1,
                    k,
                    v.len(),
                    MAX_META_STRING_BYTES
                ));
            }
            Ok(Some(v.to_string()))
        };
        let capabilities = match raw.get("capabilities") {
            // ★ 在るなら形を検査する。⚠️ 壊れていれば `Err`（`null` に倒さない）。
            Some(v) if !v.is_null() => Some(validate_meta_capabilities(v, lineno + 1)?),
            // キーが無い、または明示的に `null`: 宣言が無い (⚠️ 空配列・空オブジェクトで埋めない)。
            _ => None,
        };
        return Ok(MetaSessionFacts {
            session_start: Some(session_start),
            hmm_version: str_field("hmm_version")?,
            app_version: str_field("app_version")?,
            g1_mode: str_field("g1_mode")?,
            o1_mode: str_field("o1_mode")?,
            keyboard_layout: str_field("keyboard_layout")?,
            capabilities,
        });
    }
    if parse_failed_lines > 0 {
        tracing::warn!(
            failed = parse_failed_lines,
            "collect_meta_session_facts: some lines failed to parse as JSON"
        );
    }
    Ok(MetaSessionFacts::default())
}

/// `--features` の封筒用: 入力ファイルの SHA-256 先頭 [`SOURCE_SHA256_HEX_CHARS`] 桁を返す。
///
/// ⚠️ **ファイル全体をメモリに載せない** —— 8 KiB ずつ読んで流し込む
/// (`MAX_SESSION_BYTES` は 500 MB を許すので、一括読みは OOM 経路になる)。
///
/// ★ 目的は「同じ入力かどうか」の同定であって改竄検知ではない。
fn sha256_prefix_of_file(path: &Path) -> Result<String, String> {
    use sha2::{Digest, Sha256};
    let file = File::open(path).map_err(|e| format!("cannot open {}: {}", path.display(), e))?;
    let mut reader = BufReader::new(file);
    let mut hasher = Sha256::new();
    let mut buf = [0u8; 8192];
    loop {
        let n = std::io::Read::read(&mut reader, &mut buf)
            .map_err(|e| format!("read error on {}: {}", path.display(), e))?;
        if n == 0 {
            break;
        }
        hasher.update(&buf[..n]);
    }
    let digest = hasher.finalize();
    let hex: String = digest.iter().map(|b| format!("{:02x}", b)).collect();
    Ok(hex[..SOURCE_SHA256_HEX_CHARS].to_string())
}

/// `--features` の封筒用: 入力パスからファイル名だけを取り出す。
///
/// ⚠️ **ディレクトリを含めない** —— パスには利用者のホームディレクトリ名が含まれうる。
/// ★ ファイル名が取れない入力 (末尾が `..` 等) では `"<unknown>"` を返す
/// (⚠️ ここで `Err` にして `--features` を落とさない —— 由来が 1 つ欠けることは
/// 特徴行が出せない理由にならない)。
fn source_basename_of(path: &Path) -> String {
    path.file_name()
        .and_then(|s| s.to_str())
        .unwrap_or("<unknown>")
        .to_string()
}

/// `--features` (issue 007・`Q`) 専用の `hook_health` DTO。★ フィールド名は
/// `schema_dto.rs::LoggedLine::HookHealth` の NDJSON 実形式に一致させる。
/// `dropped_delta` は 2026-08-19 より前のログに無いので `#[serde(default)]` で欠落を許容する。
/// ⚠️★★★ 2026-09-18 改訂 (判断 24・code-reviewer M1): 欠落を `0` に正規化**しない**
/// (旧版はここで `0` に畳んでいたが、「値が無い」と「`0` だった」は区別できる情報であり、
/// `0` に畳むと情報が失われる)。`Option<u64>` のまま `quality::HookHealthEvent` へ渡し、
/// tick 単位の欠測判定 (`null` / 飽和加算) は `quality.rs` 側に委ねる。
#[derive(Debug, serde::Deserialize)]
struct HookHealthDto {
    t: u64,
    alive: bool,
    starved_ms: u64,
    rehook: bool,
    #[serde(default)]
    dropped_delta: Option<u64>,
}

/// `--features` (issue 007・`Q`) 用: NDJSON の `{"type":"hook_health", ...}` 行を
/// [`gse_next_lib::analysis::feat_offline::HookHealthEvent`] 列として抽出する。
///
/// ⚠️★★★ **形が合わない `hook_health` 行 (`alive` 欠落 / 型違い) は捨てる (0 に畳まない・AC12)。**
/// ★ `run_replay` 自体は `ReplayEvent::HookHealth` を `serde_json::Value` のまま読み飛ばすので
/// 落ちない (`ReplayEvent::HookHealth` の doc 参照)。ここは `--features` 専用の追加パースであり、
/// 捨てたことは件数だけ `warn` に残す (⚠️ 行の中身は出さない)。
fn collect_all_hook_health_events(
    session_path: &PathBuf,
) -> Result<Vec<gse_next_lib::analysis::feat_offline::HookHealthEvent>, String> {
    let metadata = std::fs::metadata(session_path)
        .map_err(|e| format!("cannot stat {}: {}", session_path.display(), e))?;
    if metadata.len() > MAX_SESSION_BYTES {
        return Err(format!(
            "session file too large: {} bytes exceeds limit {} bytes",
            metadata.len(),
            MAX_SESSION_BYTES
        ));
    }
    let file = File::open(session_path)
        .map_err(|e| format!("cannot open {}: {}", session_path.display(), e))?;
    let reader = BufReader::new(file);
    let mut out: Vec<gse_next_lib::analysis::feat_offline::HookHealthEvent> = Vec::new();
    let mut parse_failed_lines: u64 = 0;
    let mut incomplete_lines: u64 = 0;
    for (lineno, line) in reader.lines().enumerate() {
        let line = line.map_err(|e| format!("read error at line {}: {}", lineno + 1, e))?;
        if line.trim().is_empty() {
            continue;
        }
        let ev: ReplayEvent = match serde_json::from_str(&line) {
            Ok(v) => v,
            Err(_) => {
                parse_failed_lines += 1;
                continue;
            }
        };
        if let ReplayEvent::HookHealth(v) = ev {
            // ⚠️ 形が合った行だけを採る。欠け・型違いは 0 に畳まず捨てる (関数 doc 参照)。
            match serde_json::from_value::<HookHealthDto>(v) {
                Ok(dto) => out.push(gse_next_lib::analysis::feat_offline::HookHealthEvent {
                    t_ms: dto.t,
                    alive: dto.alive,
                    starved_ms: dto.starved_ms,
                    rehook: dto.rehook,
                    dropped_delta: dto.dropped_delta,
                }),
                Err(_) => incomplete_lines += 1,
            }
        }
    }
    if parse_failed_lines > 0 {
        tracing::warn!(
            failed = parse_failed_lines,
            "collect_all_hook_health_events: some lines failed to parse as ReplayEvent"
        );
    }
    if incomplete_lines > 0 {
        tracing::warn!(
            skipped = incomplete_lines,
            "collect_all_hook_health_events: hook_health lines whose shape did not match the \
             logger format were skipped (not folded into 0)"
        );
    }
    out.sort_by_key(|e| e.t_ms);
    Ok(out)
}

/// `--features` (issue 008) 専用の `feat` 行の `t` だけを取り出す DTO。
///
/// ⚠️★★★ `ReplayEvent::Feat` は `serde_json::Value` のまま置き、構造化はここで行う
/// (`ImeShadowDto` / `collect_all_ime_shadow_events` と同じ手法)。★ 形の合わない `feat` 行
/// (`t` 欠落 / 文字列 / `null`) を捨てても `run_replay` は影響を受けない
/// (`ReplayEvent::Feat` は既に `Value` なので、行の形に関わらずパース自体は必ず成功し、
/// `timestamp()` も `None` を返す)。
#[derive(Debug, serde::Deserialize)]
struct FeatTimestampDto {
    t: u64,
}

/// `--features` (issue 008・ADR-030 D8 (b-2)) 用: NDJSON の `{"type":"feat", ...}` 行の
/// **時刻だけ**を返す。★ `feat` 行の値 (`keys` / `bs_keys` 等) は 1 バイトも読まない
/// (D3 逐語「使ってよいのは feat 行の存在だけ」)。観測区間の判定にのみ使う。
///
/// ⚠️★★★ **形が合わない `feat` 行は捨てる (0 に畳まない)。** 件数だけ `warn` に残す
/// (`collect_all_ime_shadow_events` と同じ手法・判断 14 HIGH-1)。
fn collect_all_feat_timestamps(session_path: &PathBuf) -> Result<Vec<u64>, String> {
    let metadata = std::fs::metadata(session_path)
        .map_err(|e| format!("cannot stat {}: {}", session_path.display(), e))?;
    if metadata.len() > MAX_SESSION_BYTES {
        return Err(format!(
            "session file too large: {} bytes exceeds limit {} bytes",
            metadata.len(),
            MAX_SESSION_BYTES
        ));
    }
    let file = File::open(session_path)
        .map_err(|e| format!("cannot open {}: {}", session_path.display(), e))?;
    let reader = BufReader::new(file);
    let mut out: Vec<u64> = Vec::new();
    let mut parse_failed_lines: u64 = 0;
    let mut malformed_feat_lines: u64 = 0;
    for (lineno, line) in reader.lines().enumerate() {
        let line = line.map_err(|e| format!("read error at line {}: {}", lineno + 1, e))?;
        if line.trim().is_empty() {
            continue;
        }
        let ev: ReplayEvent = match serde_json::from_str(&line) {
            Ok(v) => v,
            Err(_) => {
                parse_failed_lines += 1;
                continue;
            }
        };
        if let ReplayEvent::Feat(v) = ev {
            match serde_json::from_value::<FeatTimestampDto>(v) {
                Ok(dto) => out.push(dto.t),
                Err(_) => malformed_feat_lines += 1,
            }
        }
    }
    if parse_failed_lines > 0 {
        tracing::warn!(
            failed = parse_failed_lines,
            "collect_all_feat_timestamps: some lines failed to parse as ReplayEvent"
        );
    }
    if malformed_feat_lines > 0 {
        tracing::warn!(
            skipped = malformed_feat_lines,
            "collect_all_feat_timestamps: feat lines whose t did not match the logger \
             format were skipped (not folded into a placeholder)"
        );
    }
    out.sort_unstable();
    Ok(out)
}

/// `--features --pole pointer_b` (issue 006) 用の `pointer_bin` 行の `t` だけを取り出す DTO。
///
/// ⚠️★★★ **`t` の 1 フィールドだけ**を持つ —— 移動量・ボタン・ホイールの値は**読まない**
/// (ゼロ抑制されているので**行の存在＝その秒に活動があった**であり、値は要らない・粗い量子化スカラでも触らない)。
/// ★ `Serialize` はテスト専用 (`cfg_attr`) —— `tests::pointer_bin_timestamp_dto_has_only_the_t_field`
/// が serde 出力キーが `["t"]` だけであることを固定する (フィールドが増える回帰を検出する門・LOW 是正)。
#[derive(Debug, serde::Deserialize)]
#[cfg_attr(test, derive(serde::Serialize))]
struct PointerBinTimestampDto {
    /// **ビンの終端時刻** (`analysis/pointer_bin.rs`)。1 行が覆うのは `(t − 1000, t]`。
    t: u64,
}

/// `--features --pole pointer_b` (issue 006) 用: NDJSON の `{"type":"pointer_bin", ...}` 行の**時刻だけ**を返す
/// (昇順)。★ `collect_all_feat_timestamps` と同じ形・**`--features` 経路からだけ呼ぶ**
/// (`--snapshot` / `--metrics` / `--calibration` へは配線しない)。
///
/// ⚠️★★★ **形が合わない行は捨てる (0 に畳まない)。** 件数だけ `warn` に残す。
fn collect_pointer_bin_timestamps(session_path: &PathBuf) -> Result<Vec<u64>, String> {
    let metadata = std::fs::metadata(session_path)
        .map_err(|e| format!("cannot stat {}: {}", session_path.display(), e))?;
    if metadata.len() > MAX_SESSION_BYTES {
        return Err(format!(
            "session file too large: {} bytes exceeds limit {} bytes",
            metadata.len(),
            MAX_SESSION_BYTES
        ));
    }
    let file = File::open(session_path)
        .map_err(|e| format!("cannot open {}: {}", session_path.display(), e))?;
    let mut out: Vec<u64> = Vec::new();
    let mut parse_failed_lines: u64 = 0;
    let mut malformed_lines: u64 = 0;
    for (lineno, line) in BufReader::new(file).lines().enumerate() {
        let line = line.map_err(|e| format!("read error at line {}: {}", lineno + 1, e))?;
        if line.trim().is_empty() {
            continue;
        }
        let ev: ReplayEvent = match serde_json::from_str(&line) {
            Ok(v) => v,
            Err(_) => {
                parse_failed_lines += 1;
                continue;
            }
        };
        if let ReplayEvent::PointerBin(v) = ev {
            match serde_json::from_value::<PointerBinTimestampDto>(v) {
                Ok(dto) => out.push(dto.t),
                Err(_) => malformed_lines += 1,
            }
        }
    }
    if parse_failed_lines > 0 {
        tracing::warn!(
            failed = parse_failed_lines,
            "collect_pointer_bin_timestamps: some lines failed to parse as ReplayEvent"
        );
    }
    if malformed_lines > 0 {
        tracing::warn!(
            skipped = malformed_lines,
            "collect_pointer_bin_timestamps: pointer_bin lines whose t did not match the \
             logger format were skipped (not folded into a placeholder)"
        );
    }
    out.sort_unstable();
    Ok(out)
}

/// `--features` の前処理 (事前宣言 v1.2 §6.1・`analysis::feat_offline::idle_trim`) が「入力」とみなす行の**時刻だけ**を返す (昇順)。
///
/// ★ 入力は **`key` 行 (押下・解放とも・`vk` / `category` を解決できない行も含む) と `pointer_bin` 行**だけ。
/// ⚠️ [`collect_key_events`] は使わない —— あちらは押下だけで、キーを解決できない行を捨てるので、
/// 「最後の `key` 行」とずれる。⚠️ `ime_*` / `focus_transition` / `clipboard` などは入れない
/// (システムが出しうる・研究者裁定 2026-10-08 判断 1)。
/// ★ 読むのは**行の種類と時刻だけ** ([`RowKindTimestampDto`]・`vk` / `category` / `press` / ポインタの値は読まない)。
/// → `press` などが欠けた `key` 行も入力に数える (行全体を [`ReplayEvent`] として読むと、読めない行が
///   「入力が無い」に化け、観測できていた `feat` 行まで削られる・Codex 指摘 2026-10-09)。
///
/// ⚠️ **fail-closed**: 種類が `key` / `pointer_bin` なのに時刻 `t` を非負の整数として読めない行があれば `Err`
/// (呼び出し側は exit 1)。入力の時刻が分からないまま削ると、削る範囲が黙って広がるため。
/// JSON として読めない行 (種類が分からない) は数えて警告し、読み飛ばす (他の収集関数と同じ)。
fn collect_idle_trim_input_timestamps(session_path: &PathBuf) -> Result<Vec<u64>, String> {
    let metadata = std::fs::metadata(session_path)
        .map_err(|e| format!("cannot stat {}: {}", session_path.display(), e))?;
    if metadata.len() > MAX_SESSION_BYTES {
        return Err(format!(
            "session file too large: {} bytes exceeds limit {} bytes",
            metadata.len(),
            MAX_SESSION_BYTES
        ));
    }
    let file = File::open(session_path)
        .map_err(|e| format!("cannot open {}: {}", session_path.display(), e))?;
    let mut out: Vec<u64> = Vec::new();
    let mut parse_failed_lines: u64 = 0;
    for (lineno, line) in BufReader::new(file).lines().enumerate() {
        let line = line.map_err(|e| format!("read error at line {}: {}", lineno + 1, e))?;
        if line.trim().is_empty() {
            continue;
        }
        let row: RowKindTimestampDto = match serde_json::from_str(&line) {
            Ok(v) => v,
            Err(_) => {
                parse_failed_lines += 1;
                continue;
            }
        };
        let kind = row.kind.as_deref();
        if kind != Some("key") && kind != Some("pointer_bin") {
            continue;
        }
        match row.t.as_ref().and_then(serde_json::Value::as_u64) {
            Some(t) => out.push(t),
            // ⚠️ 値は出さない (行番号と種類だけ)。
            None => {
                return Err(format!(
                    "line {}: a `{}` row has no readable timestamp `t`; refusing to trim feat rows \
                     without knowing the input times (idle trim is fail-closed)",
                    lineno + 1,
                    kind.unwrap_or_default()
                ))
            }
        }
    }
    if parse_failed_lines > 0 {
        tracing::warn!(
            failed = parse_failed_lines,
            "collect_idle_trim_input_timestamps: some lines were not JSON objects and were skipped"
        );
    }
    out.sort_unstable();
    Ok(out)
}

/// [`collect_idle_trim_input_timestamps`] 用: 行の**種類と時刻だけ**を読む DTO (ほかのキーは読まない)。
/// ★ `t` は `Value` で受け、非負の整数かを呼び出し側で確かめる (型の違いを「行が無い」に化けさせない)。
#[derive(Debug, serde::Deserialize)]
struct RowKindTimestampDto {
    #[serde(rename = "type", default)]
    kind: Option<String>,
    #[serde(default)]
    t: Option<serde_json::Value>,
}

/// 修飾キーの `key` 行から読んだ edge (`(時刻, press なら true)`) と、読み飛ばした行の件数。
#[derive(Debug, Default)]
struct ModifierEdges {
    /// **解決後の `KeyCategory` が `Modifier`** の `key` 行 (press と release の**両方**)。
    edges: Vec<(u64, bool)>,
    parse_failed_lines: u64,
    /// `vk` も既知の `category` も無く、種別を解決できなかった `key` 行。
    unresolved_keys: u64,
}

/// NDJSON から修飾キーの edge を 1 パスで集める ([`collect_modifier_intervals`] の読み取り部)。
///
/// ★ 旧ログ (`vk`) も匿名化ログ (`category`) も [`resolve_key_vk`] を通して同じ規則で判定する
/// (`collect_key_events` と同じ解決)。⚠️ **release の行も読む** —— `collect_key_events` は press しか
/// 残さないので、押下区間はそちらからは復元できない (ADR-030 D3「`key` 行は press と release の両方が出る」)。
fn read_modifier_edges(reader: impl BufRead) -> Result<ModifierEdges, String> {
    let mut out = ModifierEdges::default();
    for (lineno, line) in reader.lines().enumerate() {
        let line = line.map_err(|e| format!("read error at line {}: {}", lineno + 1, e))?;
        if line.trim().is_empty() {
            continue;
        }
        let ev: ReplayEvent = match serde_json::from_str(&line) {
            Ok(v) => v,
            Err(_) => {
                out.parse_failed_lines += 1;
                continue;
            }
        };
        if let ReplayEvent::Key {
            t,
            vk,
            category,
            press,
        } = ev
        {
            match resolve_key_vk(vk, category.as_deref()) {
                Some(resolved) if KeyCategory::from_vk(resolved) == KeyCategory::Modifier => {
                    out.edges.push((t, press));
                }
                Some(_) => {}
                None => out.unresolved_keys += 1,
            }
        }
    }
    Ok(out)
}

/// 修飾キーの走査結果 (`--pole modifier_m_plus` 用)。
#[derive(Debug)]
struct ModifierScan {
    /// 修飾キーの `key` 行数 (press と release の合計)。★ 極 M+ の適用可否の判定式 (判断 13)。
    rows: u64,
    /// 押下区間 (`stall_onset::modifier_press_intervals`・両端を含む)。
    intervals: Vec<(u64, u64)>,
    /// 先行する press が無い release の件数 (`decisions.md` 判断 24 の健全性カウンタ・
    /// `stall_onset::ModifierIntervals::orphan_releases` の写し)。
    orphan_releases: u64,
    /// 観測区間の右端で打ち切られた押下区間の本数 (`decisions.md` 判断 24 の健全性カウンタ・
    /// `stall_onset::ModifierIntervals::truncated_at_right_edge` の写し)。
    truncated_at_right_edge: u64,
}

/// `--features --pole modifier_m_plus` (issue 005) 用: 修飾キーの**押下区間**を 1 パスで作る。
///
/// ⚠️★★★ `KeyPress` (`metrics.rs`・HMM 経路と共有) は release を持たないので、押下区間は
/// `collect_key_events` からは作れない。★ `KeyPress` を変えず、専用の走査を足す
/// (`--snapshot` / `--metrics` / `--calibration` へ波及させない)。**`--features` 経路からだけ呼ぶ。**
/// ⚠️ 区間の作り方 (カウント方式・観測区間の右端で打ち切り) は
/// `stall_onset::modifier_press_intervals` が SSOT。`observed` はその打ち切りに使う観測区間。
///
/// ⚠️ 形の合わない行は捨てて**件数だけ `warn`** する (0 に畳まない・`collect_all_feat_timestamps` と同じ手法)。
fn collect_modifier_intervals(
    session_path: &PathBuf,
    observed: &[(u64, u64)],
) -> Result<ModifierScan, String> {
    let metadata = std::fs::metadata(session_path)
        .map_err(|e| format!("cannot stat {}: {}", session_path.display(), e))?;
    if metadata.len() > MAX_SESSION_BYTES {
        return Err(format!(
            "session file too large: {} bytes exceeds limit {} bytes",
            metadata.len(),
            MAX_SESSION_BYTES
        ));
    }
    let file = File::open(session_path)
        .map_err(|e| format!("cannot open {}: {}", session_path.display(), e))?;
    let scanned = read_modifier_edges(BufReader::new(file))?;
    if scanned.parse_failed_lines > 0 {
        tracing::warn!(
            failed = scanned.parse_failed_lines,
            "modifier scan: some lines failed to parse as ReplayEvent"
        );
    }
    if scanned.unresolved_keys > 0 {
        tracing::warn!(
            skipped = scanned.unresolved_keys,
            "modifier scan: key entries with neither vk nor a known category were skipped"
        );
    }
    let built = gse_next_lib::analysis::feat_offline::stall_onset::modifier_press_intervals(
        &scanned.edges,
        observed,
    );
    if built.orphan_releases > 0 {
        // ⚠️ 孤立 release (先行する press が無い) は区間を作らない。件数だけ残す。
        tracing::warn!(
            orphan_releases = built.orphan_releases,
            "modifier scan: modifier release rows with no preceding press made no interval"
        );
    }
    if built.truncated_at_right_edge > 0 {
        tracing::warn!(
            truncated = built.truncated_at_right_edge,
            "modifier scan: modifier presses still held at an observed interval's right edge were closed there"
        );
    }
    Ok(ModifierScan {
        rows: scanned.edges.len() as u64,
        intervals: built.intervals,
        orphan_releases: built.orphan_releases,
        truncated_at_right_edge: built.truncated_at_right_edge,
    })
}

/// `--features` (issue 008) 用: NDJSON の `{"type":"session_meta", ...}` 行から
/// `(ts, task_kind)` の宣言列を抽出する。
///
/// ⚠️ 既存 `run_replay` の「1 ファイルに相異なる `task_kind` が複数あれば Err」
/// (`declared_task_kinds` の検査) はここでは**適用しない** —— こちらは `stall_onset`
/// が `s` 時点で有効な宣言を引くための時系列そのものが要るので、複数の宣言を
/// そのまま返す (run_replay 側の制約とは別の用途)。
///
/// ⚠️★★★ **`task_kind` の検証は `logger::TaskKind::parse` を SSOT として通す**
/// (`run_replay` の `domain` 解決と同じ経路。新しい許可リストを作らない)。`None` になる
/// 未知の値は宣言として**採らない** (= その時点は未宣言のまま back-off する。値そのものは
/// 出力に出さず、捨てた件数だけ `warn` する)。
fn collect_task_kind_declarations(session_path: &PathBuf) -> Result<Vec<(u64, String)>, String> {
    let metadata = std::fs::metadata(session_path)
        .map_err(|e| format!("cannot stat {}: {}", session_path.display(), e))?;
    if metadata.len() > MAX_SESSION_BYTES {
        return Err(format!(
            "session file too large: {} bytes exceeds limit {} bytes",
            metadata.len(),
            MAX_SESSION_BYTES
        ));
    }
    let file = File::open(session_path)
        .map_err(|e| format!("cannot open {}: {}", session_path.display(), e))?;
    let reader = BufReader::new(file);
    let mut out: Vec<(u64, String)> = Vec::new();
    let mut parse_failed_lines: u64 = 0;
    let mut unknown_task_kind_lines: u64 = 0;
    for (lineno, line) in reader.lines().enumerate() {
        let line = line.map_err(|e| format!("read error at line {}: {}", lineno + 1, e))?;
        if line.trim().is_empty() {
            continue;
        }
        let ev: ReplayEvent = match serde_json::from_str(&line) {
            Ok(v) => v,
            Err(_) => {
                parse_failed_lines += 1;
                continue;
            }
        };
        if let ReplayEvent::SessionMeta { task_kind, ts, .. } = ev {
            match TaskKind::parse(&task_kind) {
                Some(kind) => out.push((ts, kind.as_str().to_string())),
                None => {
                    unknown_task_kind_lines += 1;
                }
            }
        }
    }
    if parse_failed_lines > 0 {
        tracing::warn!(
            failed = parse_failed_lines,
            "collect_task_kind_declarations: some lines failed to parse as ReplayEvent"
        );
    }
    if unknown_task_kind_lines > 0 {
        // ⚠️ 値そのものは出さない (件数だけ)。
        tracing::warn!(
            skipped = unknown_task_kind_lines,
            "collect_task_kind_declarations: some session_meta declarations had a task_kind \
             unrecognized by logger::TaskKind::parse and were dropped (treated as undeclared)"
        );
    }
    out.sort_by_key(|(ts, _)| *ts);
    Ok(out)
}

fn collect_paste_events(session_path: &PathBuf) -> Result<(Vec<PasteEvent>, u32), String> {
    let metadata = std::fs::metadata(session_path)
        .map_err(|e| format!("cannot stat {}: {}", session_path.display(), e))?;
    if metadata.len() > MAX_SESSION_BYTES {
        return Err(format!(
            "session file too large: {} bytes exceeds limit {} bytes",
            metadata.len(),
            MAX_SESSION_BYTES
        ));
    }
    let file = File::open(session_path)
        .map_err(|e| format!("cannot open {}: {}", session_path.display(), e))?;
    let reader = BufReader::new(file);
    let mut out: Vec<PasteEvent> = Vec::new();
    let mut parse_failed_lines: u64 = 0;
    let mut paste_without_chars: u64 = 0;
    for (lineno, line) in reader.lines().enumerate() {
        let line = line.map_err(|e| format!("read error at line {}: {}", lineno + 1, e))?;
        if line.trim().is_empty() {
            continue;
        }
        let ev: ReplayEvent = match serde_json::from_str(&line) {
            Ok(v) => v,
            Err(_) => {
                parse_failed_lines += 1;
                continue;
            }
        };
        if let ReplayEvent::Paste {
            t,
            external_paste_chars,
        } = ev
        {
            match external_paste_chars {
                Some(chars) => out.push(PasteEvent {
                    timestamp: t,
                    chars,
                }),
                None => paste_without_chars += 1,
            }
        }
    }
    if parse_failed_lines > 0 {
        tracing::warn!(
            skipped = parse_failed_lines,
            "collect_paste_events: NDJSON lines failed to parse as ReplayEvent"
        );
    }
    if paste_without_chars > 0 {
        tracing::warn!(
            skipped = paste_without_chars,
            "collect_paste_events: paste entries without external_paste_chars \
             (pre-capture-schema-freeze NDJSON — excluded from outcome metrics)"
        );
    }
    out.sort_by_key(|p| p.timestamp);
    // u32 で十分 (MAX_SESSION_BYTES 配下の paste 行数は u32 を超えない)。
    Ok((out, paste_without_chars.min(u32::MAX as u64) as u32))
}

/// v0.4: NDJSON の `{"type":"key", ...}` 行から press イベントを `KeyPress` 列として抽出する。
///
/// **旧ログ**は `vk` を保持し、**現行の logger と匿名化 NDJSON** は `category` を書く。
/// どちらも `resolve_key_vk` が吸収する (`vk` を優先し、無ければ代表 VK へ逆写像)。
/// Unicode 内容には触れない。
///
/// ⚠️★★★ **2026-08-23 (ADR-014 判断 6) で D-RC3 の過小評価は解消した。**
/// `KeyCategory` に `Punctuation` / `SentencePunctuation` / `Tab` を足したので、
/// **`is_text_producing` が true な VK は 1 つ残らず非 `Other` の category に入る**。
/// → **`is_backspace` も `is_text_producing` も raw と完全一致する**
/// (代表 VK `other => 0x07` は「保守的な倒し込み」ではなく**厳密に正しい**値になった)。
///
/// **旧仕様 (2026-08-23 以前)**: OEM 句読点 (0xBA-0xC0/0xDB-0xDF/0xE2)・Tab(0x09)・
/// テンキー演算子(0x6A-0x6F) が `Other` へ畳まれ、匿名化後に text-producing と判別できず、
/// `--metrics` の manual_insert 系がその件数だけ過小評価されていた
/// (`.steering/20260624-replay-category/decisions.md` D-RC3)。
/// `manual_contribution_ratio` は `research-positioning.md §5` **H-Y の主要アウトカム**である。
///
/// ★ **`--snapshot` / 特徴量再計算 (D6) には元から無影響** (run_replay は is_text_producing を使わない)。
fn collect_key_events(session_path: &PathBuf) -> Result<Vec<KeyPress>, String> {
    let metadata = std::fs::metadata(session_path)
        .map_err(|e| format!("cannot stat {}: {}", session_path.display(), e))?;
    if metadata.len() > MAX_SESSION_BYTES {
        return Err(format!(
            "session file too large: {} bytes exceeds limit {} bytes",
            metadata.len(),
            MAX_SESSION_BYTES
        ));
    }
    let file = File::open(session_path)
        .map_err(|e| format!("cannot open {}: {}", session_path.display(), e))?;
    let reader = BufReader::new(file);
    let mut out: Vec<KeyPress> = Vec::new();
    let mut parse_failed_lines: u64 = 0;
    let mut unresolved_keys: u64 = 0;
    for (lineno, line) in reader.lines().enumerate() {
        let line = line.map_err(|e| format!("read error at line {}: {}", lineno + 1, e))?;
        if line.trim().is_empty() {
            continue;
        }
        let ev: ReplayEvent = match serde_json::from_str(&line) {
            Ok(v) => v,
            Err(_) => {
                parse_failed_lines += 1;
                continue;
            }
        };
        if let ReplayEvent::Key {
            t,
            vk,
            category,
            press,
        } = ev
        {
            if press {
                match resolve_key_vk(vk, category.as_deref()) {
                    Some(resolved_vk) => out.push(KeyPress {
                        timestamp: t,
                        vk: resolved_vk,
                    }),
                    None => unresolved_keys += 1,
                }
            }
        }
    }
    if parse_failed_lines > 0 {
        tracing::warn!(
            skipped = parse_failed_lines,
            "collect_key_events: NDJSON lines failed to parse as ReplayEvent"
        );
    }
    if unresolved_keys > 0 {
        tracing::warn!(
            skipped = unresolved_keys,
            "collect_key_events: key entries with neither vk nor a known category were skipped"
        );
    }
    out.sort_by_key(|k| k.timestamp);
    Ok(out)
}

/// Task D: 1 セッション NDJSON から較正解析の入力 `SessionData` を構築する。
///
/// 1 パスで session_meta(track) / probe_assignment(件数) / realtime_label(ProbeRecord) /
/// vignette_response(VignetteRecord) を抽出し、X/Y の源となる FeatSnapshot は既存
/// `collect_logged_feats` を再利用する (計 2 パス、`--metrics` 経路と同じ前提)。
/// 未知 source / quadrant / parse 失敗は silent skip (件数のみ warn、内容はプライバシーのため出さない)。
fn load_calibration_session(session_path: &PathBuf) -> Result<SessionData, String> {
    let metadata = std::fs::metadata(session_path)
        .map_err(|e| format!("cannot stat {}: {}", session_path.display(), e))?;
    if metadata.len() > MAX_SESSION_BYTES {
        return Err(format!(
            "session file too large: {} bytes exceeds limit {} bytes",
            metadata.len(),
            MAX_SESSION_BYTES
        ));
    }
    let file = File::open(session_path)
        .map_err(|e| format!("cannot open {}: {}", session_path.display(), e))?;
    let reader = BufReader::new(file);

    let mut track = TrackKind::Main; // session_meta がなければ main 既定
    let mut session_meta_seen = false;
    let mut session_start_ms: Option<u64> = None; // session_meta.ts (時刻単調性検証用)
    let mut probes: Vec<ProbeRecord> = Vec::new();
    let mut vignettes: Vec<VignetteRecord> = Vec::new();
    let mut random_probe_assignment_count: usize = 0;

    let mut parse_failed_lines: u64 = 0;
    let mut unknown_enum_lines: u64 = 0;
    // producer は q を 1..=5 に clamp するが reader は信頼せず再検証する (security-checker MEDIUM)。
    // 手編集/破損 NDJSON で範囲外 q が集計値を静かに歪めるのを防ぐ。
    let mut out_of_range_lines: u64 = 0;

    for (lineno, line) in reader.lines().enumerate() {
        let line = line.map_err(|e| format!("read error at line {}: {}", lineno + 1, e))?;
        if line.trim().is_empty() {
            continue;
        }
        let ev: ReplayEvent = match serde_json::from_str(&line) {
            Ok(v) => v,
            Err(_) => {
                parse_failed_lines += 1;
                continue;
            }
        };
        match ev {
            ReplayEvent::SessionMeta { track: t, ts, .. } => {
                // 複数あれば最初の宣言を採用 (通常はセッション先頭に 1 件)。
                if !session_meta_seen {
                    match TrackKind::parse(&t) {
                        Some(tk) => track = tk,
                        None => unknown_enum_lines += 1,
                    }
                    session_start_ms = Some(ts);
                    session_meta_seen = true;
                }
            }
            ReplayEvent::ProbeAssignment { .. } => {
                // probe_assignment は一様ランダムプローブの監査記録 (Recall 分母の定義)。
                random_probe_assignment_count += 1;
            }
            ReplayEvent::RealtimeLabel {
                source,
                q1_friction,
                q2_progress,
                answered,
                skip_reason,
                latency_ms,
                analysis_window_start_ms,
                analysis_window_end_ms,
                ..
            } => {
                let Some(source) = ProbeSourceKind::parse(&source) else {
                    unknown_enum_lines += 1;
                    continue;
                };
                let Some(skip_reason) = SkipReasonKind::parse(&skip_reason) else {
                    unknown_enum_lines += 1;
                    continue;
                };
                // 回答済みは q1/q2 が 1..=5 必須 (producer 不変条件)。範囲外/欠落は破損とみなし skip。
                // skip 回答 (answered=false) は q=None が正常なので検証しない。
                if answered {
                    let q_valid = matches!(q1_friction, Some(q) if (1..=5).contains(&q))
                        && matches!(q2_progress, Some(q) if (1..=5).contains(&q));
                    if !q_valid {
                        out_of_range_lines += 1;
                        continue;
                    }
                }
                probes.push(ProbeRecord {
                    source,
                    answered,
                    q1_friction,
                    q2_progress,
                    skip_reason,
                    latency_ms,
                    window_start_ms: analysis_window_start_ms,
                    window_end_ms: analysis_window_end_ms,
                });
            }
            ReplayEvent::VignetteResponse {
                vignette_id,
                expected_quadrant,
                q1_friction,
                q2_progress,
                elapsed_ms,
                changes,
                ..
            } => {
                let Some(expected) = QuadrantKind::parse(&expected_quadrant) else {
                    unknown_enum_lines += 1;
                    continue;
                };
                // ビネット q1/q2 も 1..=5 を再検証 (破損 NDJSON で象限推論が歪むのを防ぐ)。
                if !(1..=5).contains(&q1_friction) || !(1..=5).contains(&q2_progress) {
                    out_of_range_lines += 1;
                    continue;
                }
                // ⚠️ `vignette_id` は `split_attempts` が施行の境界に使うため、
                //    **読込側でも**書込側 (`lib.rs`) と同じ不透明 ID 規則で検証する。
                //    本 CLI は任意のローカル NDJSON を読むので、手編集ファイル経由で
                //    任意長の文字列が入りうる (`security-checker` LOW)。
                if !is_valid_opaque_id(&vignette_id) {
                    out_of_range_lines += 1;
                    continue;
                }
                vignettes.push(VignetteRecord {
                    vignette_id,
                    elapsed_ms,
                    changes,
                    expected,
                    q1_friction,
                    q2_progress,
                });
            }
            // 較正に無関係な type は読み飛ばす。
            _ => {}
        }
    }

    if parse_failed_lines > 0 {
        tracing::warn!(
            skipped = parse_failed_lines,
            "load_calibration_session: NDJSON lines failed to parse as ReplayEvent"
        );
    }
    if unknown_enum_lines > 0 {
        tracing::warn!(
            skipped = unknown_enum_lines,
            "load_calibration_session: entries with unknown enum value (forward-compat skip)"
        );
    }
    if out_of_range_lines > 0 {
        tracing::warn!(
            skipped = out_of_range_lines,
            "load_calibration_session: entries with q1/q2 out of 1..=5 (corrupt/hand-edited NDJSON skip)"
        );
    }
    if !session_meta_seen {
        tracing::warn!(
            session = %session_path.display(),
            "load_calibration_session: no session_meta found — assuming track=main"
        );
    }

    // X/Y の源 = 記録済み feat (wall-clock)。既存コレクタを再利用する。
    let feats = collect_logged_feats(session_path)?;

    Ok(SessionData {
        track,
        probes,
        vignettes,
        feats,
        random_probe_assignment_count,
        session_start_ms,
        skipped_parse: parse_failed_lines,
        skipped_unknown_enum: unknown_enum_lines,
        skipped_out_of_range: out_of_range_lines,
    })
}

/// NDJSON を読み込み、step() を再実行して FeatSnapshot 列を返す。
fn run_replay(session_path: &PathBuf) -> Result<Vec<FeatSnapshot>, String> {
    // ファイルサイズガード (OOM 防止、security-checker MEDIUM)
    let metadata = std::fs::metadata(session_path)
        .map_err(|e| format!("cannot stat {}: {}", session_path.display(), e))?;
    if metadata.len() > MAX_SESSION_BYTES {
        return Err(format!(
            "session file too large: {} bytes exceeds limit {} bytes",
            metadata.len(),
            MAX_SESSION_BYTES
        ));
    }

    let file = File::open(session_path)
        .map_err(|e| format!("cannot open {}: {}", session_path.display(), e))?;
    let reader = BufReader::new(file);

    let mut events: Vec<ReplayEvent> = Vec::new();
    let mut meta_hmm_version: Option<String> = None;

    for (lineno, line) in reader.lines().enumerate() {
        let line = line.map_err(|e| format!("read error at line {}: {}", lineno + 1, e))?;
        if line.trim().is_empty() {
            continue;
        }
        let ev: ReplayEvent = serde_json::from_str(&line)
            .map_err(|e| format!("parse error at line {}: {}", lineno + 1, e))?;
        if let ReplayEvent::Meta {
            hmm_version: Some(v),
            ..
        } = &ev
        {
            meta_hmm_version = Some(v.clone());
        }
        events.push(ev);
    }

    // hmm_version 検証（不一致は WARN のみ、exit はしない）
    if let Some(v) = &meta_hmm_version {
        if v != HMM_VERSION {
            tracing::warn!(
                "session hmm_version = {}, current engine = {}. snapshots may not be comparable.",
                v,
                HMM_VERSION
            );
        }
    }

    // session_start を決定: Meta.session_start → SessionStart.t → 最初のイベントの t
    let session_start_ms = events
        .iter()
        .find_map(|e| match e {
            ReplayEvent::Meta {
                session_start: Some(t),
                ..
            } => Some(*t),
            _ => None,
        })
        .or_else(|| {
            events.iter().find_map(|e| match e {
                ReplayEvent::SessionStart { t } => Some(*t),
                _ => None,
            })
        })
        .or_else(|| events.iter().find_map(|e| e.timestamp()))
        .ok_or_else(|| "no events with timestamps found".to_string())?;

    // ★ ADR-006 Phase 2b: 宣言された task_kind が domain head を選ぶ。
    //   ⚠️ **この抽出を省くとリプレイが本番の挙動を再現できない** (session_meta 行は
    //     timestamp() == None で下のソート対象から落ちるため、メインループでは見えない)。
    //   ⚠️ ファイルの 2 パス読みではない。events は既に全行メモリ上にある。
    //   task_kind が無い / 未知の場合は Writing head へフォールバックする
    //   (既存 Phase1 ログはそもそも session_meta を持たない)。
    let declared_task_kinds: Vec<&str> = events
        .iter()
        .filter_map(|e| match e {
            ReplayEvent::SessionMeta { task_kind, .. } => Some(task_kind.as_str()),
            _ => None,
        })
        .collect();

    // ⚠️★ **1 ファイルに相異なる task_kind が複数あるなら、黙って先頭勝ちにしない。**
    //   非 G1 モードではログをローテートしないため、「開始 → 戻る → 別 task_kind で開始」で
    //   1 ファイルに複数の session_meta が並びうる。本番は 2 個目で head を差し替えるが、
    //   replay は区間を持たないので先頭を全区間へ適用してしまい、**本番挙動を再現しない**。
    //   再現できないものを再現したふりをするのが最悪なので、明示的に落とす。
    //   (security-checker 指摘・2026-08-18)
    let mut distinct: Vec<&str> = declared_task_kinds.clone();
    distinct.sort_unstable();
    distinct.dedup();
    if distinct.len() > 1 {
        return Err(format!(
            "session_meta declares {} different task_kinds in one file ({:?}) —              replay cannot reproduce per-session head switching. Split the file per session.",
            distinct.len(),
            distinct
        ));
    }

    // ⚠️ session_meta が 1 種類でも、session_start が複数あるなら同じ理由で再現できない
    //   (本番は start_session ごとに engine.reset() = head を Writing へ戻す)。
    let session_start_count = events
        .iter()
        .filter(|e| matches!(e, ReplayEvent::SessionStart { .. }))
        .count();
    if !declared_task_kinds.is_empty() && session_start_count > 1 {
        return Err(format!(
            "file has {session_start_count} session_start rows with a session_meta declaration —              production resets the head on each start, replay cannot. Split the file per session."
        ));
    }

    let domain = match declared_task_kinds.first() {
        None => TaskDomain::Writing,
        Some(s) => match TaskKind::parse(s) {
            Some(kind) => TaskDomain::from(kind),
            None => {
                // ⚠️ 全長を出さない (1 行は最大 MAX_SESSION_BYTES まで許容されるため)。
                let shown: String = s.chars().take(32).collect();
                tracing::warn!(
                    "unknown task_kind {:?} in session_meta — falling back to writing head",
                    shown
                );
                TaskDomain::Writing
            }
        },
    };

    // 時刻順にソート（既存 Feat は timestamp() == None で除外）
    let mut ordered: Vec<ReplayEvent> = events
        .into_iter()
        .filter(|e| e.timestamp().is_some())
        .collect();
    ordered.sort_by_key(|e| e.timestamp().unwrap_or(0));

    // state + engine を初期化
    let mut state = AnalysisState::new(session_start_ms, 600);
    let engine = CognitiveStateEngine::new_for_domain(domain);
    let mut ime_open = false;
    let mut snapshots: Vec<FeatSnapshot> = Vec::new();
    // vk も category も解決できなかった不正 key 行の件数 (内容は出さず件数のみ warn)。
    let mut unresolved_keys: u64 = 0;

    // 各イベントの前に、そのイベントの時刻までゲートを進める
    for ev in ordered {
        let ev_ms = ev.timestamp().unwrap();

        // イベント時刻に達するまでゲートを進める (1Hz 推論を仮想時刻で駆動)
        while state.next_engine_update_ms <= ev_ms {
            let tick_ms = state.next_engine_update_ms;
            let out = step(&mut state, &engine, None, tick_ms, ime_open);
            if let Some(f) = out.feat {
                snapshots.push(f);
            }
            // 無限ループ防止セーフティガード: step() が next_engine_update_ms を
            // 進めなかった場合（通常は engine pause で gate スキップ時）。
            // 通常運用では発生しないが、step() の実装に回帰があった際は
            // tracing::error + debug_assert でバグとして可視化する。
            if state.next_engine_update_ms == tick_ms {
                tracing::error!(
                    tick_ms = tick_ms,
                    "step() did not advance next_engine_update_ms — forcing +ENGINE_TICK_MS"
                );
                debug_assert!(
                    false,
                    "step() must advance next_engine_update_ms on each gate tick"
                );
                state.next_engine_update_ms = tick_ms + ENGINE_TICK_MS;
            }
        }

        // イベント処理
        match ev {
            ReplayEvent::Meta { .. }
            | ReplayEvent::Feat(_)
            | ReplayEvent::Paste { .. }
            | ReplayEvent::UserLabel { .. }
            | ReplayEvent::ReviewMarker { .. }
            | ReplayEvent::ImeShadow(_)
            | ReplayEvent::InterventionDecision(_)
            | ReplayEvent::InterventionResponse(_)
            | ReplayEvent::HookHealth(_)
            | ReplayEvent::StarveWindow(_)
            // ⚠️★★★ O1 (R3) の 4 行種は **読み飛ばす**。★ 特徴量へ流さない (ADR-014 D4b)。
            | ReplayEvent::RecordingPause(_)
            | ReplayEvent::FocusTransition(_)
            | ReplayEvent::PointerBin(_)
            | ReplayEvent::SecureInput(_)
            // ⚠️★★★ 監査 criterion (ADR-031)。★ 記録のみで推論へ流さない。
            | ReplayEvent::ActivityLabel(_)
            | ReplayEvent::SessionMeta { .. }
            | ReplayEvent::ProbeAssignment { .. }
            | ReplayEvent::RealtimeLabel { .. }
            | ReplayEvent::VignetteResponse { .. } => {
                // Paste は回数記録専用で features/HMM に未使用 → 追加処理なし。
                // Meta / Feat / UserLabel / ReviewMarker はゲート進行済み、追加処理不要
                // (UserLabel は metrics 経路で collect_user_labels 側で抽出)
                // (ReviewMarker は --segment 経路でセグメントハイライトに使用)
                // (v0.3 較正 variant は --calibration 経路の collect_calibration_session で抽出)
                // これらは timestamp()==None で ordered から除外されるが、match の網羅性のため列挙する。
            }
            ReplayEvent::SessionStart { t } => {
                // 本番の start_session リセットを再現
                state.reset(t, 600);
            }
            ReplayEvent::Key {
                t,
                vk,
                category,
                press,
            } => {
                // raw は vk、匿名化は category。代表 VK を解決して従来通り step する。
                let resolved_vk = match resolve_key_vk(vk, category.as_deref()) {
                    Some(v) => v,
                    None => {
                        // vk も category も無い / 未知 category の不正 key 行。特徴量を汚さない
                        // よう step せずスキップする (ゲートは前段で進行済み)。件数は後段で warn。
                        unresolved_keys += 1;
                        continue;
                    }
                };
                let event = InputEvent {
                    vk_code: resolved_vk,
                    timestamp: t,
                    is_press: press,
                    is_repeat: false, // step() が pressed_keys で検出する
                    is_backspace: is_backspace(resolved_vk),
                    is_paste: false, // replay は key 行から再構成。paste は別 variant で記録済み
                };
                let out = step(
                    &mut state,
                    &engine,
                    Some(LoopInput::Key(event)),
                    t,
                    ime_open,
                );
                if let Some(f) = out.feat {
                    snapshots.push(f);
                }
            }
            ReplayEvent::ImeState { t, on, active } => {
                ime_open = on;
                let out = step(
                    &mut state,
                    &engine,
                    Some(LoopInput::ImeActivate { active }),
                    t,
                    ime_open,
                );
                if let Some(f) = out.feat {
                    snapshots.push(f);
                }
            }
        }
    }

    if unresolved_keys > 0 {
        tracing::warn!(
            skipped = unresolved_keys,
            "run_replay: key entries with neither vk nor a known category were skipped \
             (malformed or future KeyCategory — features unaffected)"
        );
    }

    Ok(snapshots)
}

/// 既存スナップショットと比較。byte-equal (JSON 正規化後) を期待する。
fn compare_snapshots(actual: &[FeatSnapshot], expected_path: &PathBuf) -> Result<(), String> {
    let expected_str = std::fs::read_to_string(expected_path)
        .map_err(|e| format!("cannot read {}: {}", expected_path.display(), e))?;
    let expected: Vec<FeatSnapshot> = serde_json::from_str(&expected_str)
        .map_err(|e| format!("parse error in {}: {}", expected_path.display(), e))?;

    if actual.len() != expected.len() {
        return Err(format!(
            "length mismatch: actual={}, expected={}",
            actual.len(),
            expected.len()
        ));
    }

    for (i, (a, e)) in actual.iter().zip(expected.iter()).enumerate() {
        if a != e {
            return Err(format!(
                "snapshot[{}] differs:\n  actual   = {}\n  expected = {}",
                i,
                serde_json::to_string(a).unwrap_or_default(),
                serde_json::to_string(e).unwrap_or_default(),
            ));
        }
    }

    Ok(())
}

// =============================================================================
// Tests — `.steering/20260416-replay-feat-alignment-bug/` Phase A 回帰テスト
// =============================================================================
// 層 1 (unit):       `LoggedFeatDto` の serde デシリアライズ + FeatSnapshot 変換
// 層 2 (integration): 合成 NDJSON (tests/fixtures/phase1_minimal.ndjson) で
//                     `collect_logged_feats` + `compute_session_metrics` を通して
//                     warnings 空 + support=1 を確認
// ── Segment 関連関数 (Phase 1 GT 改善) ────────────────────────────────

/// セグメント: 活動境界 (沈黙 ≥ SILENCE_BOUNDARY_SEC) で分割された区間。
struct Segment {
    start_ms: u64,
    end_ms: u64,
    feat_count: u32,
    silence_sec: f64,
    correction_rate: f64,
    avg_flight_time_ms: f64,
    has_marker: bool,
}

/// 沈黙がこの秒数以上続いたらセグメント境界とみなす。
const SILENCE_BOUNDARY_SEC: f64 = 5.0;

/// NDJSON から review_marker の timestamp 一覧を抽出する。
fn collect_review_markers(path: &PathBuf) -> Vec<u64> {
    // MAX_SESSION_BYTES ガード (collect_logged_feats と同じ NDJSON を読むため同一上限)
    if let Ok(meta) = std::fs::metadata(path) {
        if meta.len() > MAX_SESSION_BYTES {
            tracing::warn!("session file too large for review marker scan, skipping");
            return Vec::new();
        }
    }
    let file = match File::open(path) {
        Ok(f) => f,
        Err(_) => return Vec::new(),
    };
    let reader = BufReader::new(file);
    let mut markers = Vec::new();
    for line in reader.lines() {
        let line = match line {
            Ok(l) => l,
            Err(_) => continue,
        };
        if line.contains("\"review_marker\"") {
            if let Ok(ReplayEvent::ReviewMarker { t }) = serde_json::from_str::<ReplayEvent>(&line)
            {
                markers.push(t);
            }
        }
    }
    markers
}

/// NDJSON から key press イベントのタイムスタンプ一覧を抽出する。
/// セグメント境界検出に使用 (feat は 1Hz 固定なので沈黙検出に使えない)。
fn collect_key_timestamps(path: &PathBuf) -> Vec<u64> {
    // MAX_SESSION_BYTES ガード
    if let Ok(meta) = std::fs::metadata(path) {
        if meta.len() > MAX_SESSION_BYTES {
            tracing::warn!("session file too large for key timestamp scan, skipping");
            return Vec::new();
        }
    }
    let file = match File::open(path) {
        Ok(f) => f,
        Err(_) => return Vec::new(),
    };
    let reader = BufReader::new(file);
    let mut timestamps = Vec::new();
    for line in reader.lines() {
        let line = match line {
            Ok(l) => l,
            Err(_) => continue,
        };
        if line.contains("\"key\"") {
            if let Ok(ReplayEvent::Key { t, press, .. }) =
                serde_json::from_str::<ReplayEvent>(&line)
            {
                if press {
                    timestamps.push(t);
                }
            }
        }
    }
    timestamps.sort_unstable();
    timestamps
}

/// キーストロークの沈黙 (≥ SILENCE_BOUNDARY_SEC) で区間を分割し、
/// 各区間に含まれる FeatSnapshot の統計をセグメントとして返す。
fn build_segments(feats: &[FeatSnapshot], key_timestamps: &[u64], markers: &[u64]) -> Vec<Segment> {
    if feats.is_empty() || key_timestamps.is_empty() {
        return Vec::new();
    }

    // キーストローク沈黙で区間境界を検出
    let boundary_ms = (SILENCE_BOUNDARY_SEC * 1000.0) as u64;
    let mut boundaries: Vec<(u64, u64)> = Vec::new(); // (start, end) of each active interval
    let mut seg_start = key_timestamps[0];

    for i in 1..key_timestamps.len() {
        let gap = key_timestamps[i].saturating_sub(key_timestamps[i - 1]);
        if gap >= boundary_ms {
            // 前セグメントを閉じる
            boundaries.push((seg_start, key_timestamps[i - 1]));
            seg_start = key_timestamps[i];
        }
    }
    // 最後のセグメント
    boundaries.push((seg_start, *key_timestamps.last().unwrap()));

    // 各区間に feat を割り当て
    let mut segments = Vec::new();
    for (start, end) in &boundaries {
        let seg_feats: Vec<&FeatSnapshot> = feats
            .iter()
            .filter(|f| f.timestamp >= *start && f.timestamp <= *end)
            .collect();
        segments.push(make_segment(*start, *end, &seg_feats, markers));
    }

    segments
}

fn make_segment(start_ms: u64, end_ms: u64, feats: &[&FeatSnapshot], markers: &[u64]) -> Segment {
    let feat_count = feats.len() as u32; // feat snapshots in range (1Hz → ≈ active seconds)
    let duration_sec = (end_ms.saturating_sub(start_ms)) as f64 / 1000.0;
    let silence_sec = duration_sec - feat_count as f64; // approx
    let silence_sec = if silence_sec < 0.0 { 0.0 } else { silence_sec };

    // Correction rate: average f3 across feats
    let correction_rate = if feats.is_empty() {
        0.0
    } else {
        feats.iter().map(|f| f.f3).sum::<f64>() / feats.len() as f64
    };

    // Average flight time
    let avg_flight_time_ms = if feats.is_empty() {
        0.0
    } else {
        feats.iter().map(|f| f.f1).sum::<f64>() / feats.len() as f64
    };

    let has_marker = markers.iter().any(|&m| m >= start_ms && m <= end_ms);

    Segment {
        start_ms,
        end_ms,
        feat_count,
        silence_sec,
        correction_rate,
        avg_flight_time_ms,
        has_marker,
    }
}

/// .segments.txt 形式の文字列を生成する。
fn format_segments_txt(session_path: &Path, segments: &[Segment]) -> String {
    let mut out = String::new();
    let session_name = session_path
        .file_name()
        .map(|n| n.to_string_lossy().to_string())
        .unwrap_or_else(|| "unknown".to_string());

    let total_keys: u32 = segments.iter().map(|s| s.feat_count).sum();

    out.push_str(&format!("# Session: {}\n", session_name));
    out.push_str(&format!(
        "# Segments: {}  |  Total feat snapshots: {}\n",
        segments.len(),
        total_keys,
    ));
    out.push_str("#\n");
    out.push_str("# Label: F=Flow  I=Incubation  S=Stuck  ?=Unknown  -=Skip\n");
    out.push_str("# Edit the Label column, then save.\n");
    out.push_str("# Timestamps are absolute epoch ms (used by --segments parser).\n");
    out.push_str("#\n");
    out.push_str(
        "# Seg  Start_ms         End_ms           Feats  Silence  CorrRate  AvgFT    Label\n",
    );

    for (i, seg) in segments.iter().enumerate() {
        let marker = if seg.has_marker { "*" } else { " " };
        out.push_str(&format!(
            "{}{:>3}  {:>16}  {:>16}  {:>5}  {:>6.1}s  {:>7.1}%  {:>5.0}ms   ?\n",
            marker,
            i + 1,
            seg.start_ms,
            seg.end_ms,
            seg.feat_count,
            seg.silence_sec,
            seg.correction_rate * 100.0,
            seg.avg_flight_time_ms,
        ));
    }

    out
}

/// .segments.txt をパースし RangeLabel 列を返す。
fn parse_segments_file(path: &PathBuf) -> Result<Vec<RangeLabel>, String> {
    // サイズガード: segments ファイルは通常数 KB、10 MB を上限とする
    const MAX_SEGMENTS_BYTES: u64 = 10 * 1024 * 1024;
    let meta =
        std::fs::metadata(path).map_err(|e| format!("cannot stat {}: {}", path.display(), e))?;
    if meta.len() > MAX_SEGMENTS_BYTES {
        return Err(format!(
            "{} is {} bytes, exceeds limit {} bytes",
            path.display(),
            meta.len(),
            MAX_SEGMENTS_BYTES,
        ));
    }

    let content = std::fs::read_to_string(path)
        .map_err(|e| format!("cannot read {}: {}", path.display(), e))?;

    let mut labels = Vec::new();

    for line in content.lines() {
        let trimmed = line.trim();
        // コメント行・空行をスキップ
        if trimmed.is_empty() || trimmed.starts_with('#') {
            continue;
        }

        // マーカー `*` をスキップ
        let trimmed = trimmed.trim_start_matches('*').trim();

        // フィールド分割: Seg Start_ms End_ms Feats Silence CorrRate AvgFT Label
        let fields: Vec<&str> = trimmed.split_whitespace().collect();
        if fields.len() < 8 {
            continue; // ヘッダー行やフィールド不足行をスキップ
        }

        let label_str = fields[7];
        let label = match label_str {
            "F" => LabelClass::Flow,
            "I" => LabelClass::Incubation,
            "S" => LabelClass::Stuck,
            "?" | "-" => continue, // Unknown/Skip
            _ => continue,
        };

        // start_ms / end_ms のパース — 非数値行 (ヘッダー等) は continue でスキップ
        let start_ms: u64 = match fields[1].parse() {
            Ok(v) => v,
            Err(_) => continue,
        };
        let end_ms: u64 = match fields[2].parse() {
            Ok(v) => v,
            Err(_) => continue,
        };

        if start_ms > end_ms {
            tracing::warn!(
                "segment has start_ms ({}) > end_ms ({}), skipping",
                start_ms,
                end_ms
            );
            continue;
        }

        labels.push(RangeLabel {
            start_ms,
            end_ms,
            label,
        });
    }

    Ok(labels)
}

// 層 3 (回帰):         実データから key を除去した fixture
//                     (tests/fixtures/phase1_ime_heavy.ndjson) で warnings < 2
//                     かつ confusion matrix 合計 ≥ 4 を確認。将来 metrics 経路を
//                     regen に戻す変更が入ったら CI で落とす役割。
#[cfg(test)]
mod tests {
    use super::*;
    use gse_next_lib::analysis::metrics::ResumptionOutcomeKind;
    use std::path::PathBuf;

    fn fixture_path(name: &str) -> PathBuf {
        let mut p = PathBuf::from(env!("CARGO_MANIFEST_DIR"));
        p.push("tests");
        p.push("fixtures");
        p.push(name);
        p
    }

    fn snapshot_path(name: &str) -> PathBuf {
        let mut p = PathBuf::from(env!("CARGO_MANIFEST_DIR"));
        p.push("tests");
        p.push("snapshots");
        p.push(name);
        p
    }

    /// AC4: `--features` は他のモードフラグと同時指定できない (exit ≠ 0 相当の `Err`)。
    #[test]
    fn features_mode_is_mutually_exclusive() {
        let args = vec![
            "session.ndjson".to_string(),
            "--features".to_string(),
            "--metrics".to_string(),
        ];
        assert!(parse_args_from(args).is_err());
    }

    /// `--features` 単独では受理される (mutual exclusion の対照)。
    #[test]
    fn features_mode_alone_is_accepted() {
        let args = vec!["session.ndjson".to_string(), "--features".to_string()];
        let parsed = parse_args_from(args).expect("--features alone should parse");
        assert!(parsed.features);
    }

    /// v0.4 Outcome metrics の Replay-as-Truth 回帰: outcome_metrics.ndjson を
    /// collector → segment → compute_outcome_metrics に通し、固定値を検証する。
    /// fixture 設計: 2 エピソード (10000-11000 / 200000-201000)、ep1 は manual のみで
    /// 回復、ep2 は paste(60 chars) 後に回復。t=50000 の paste は chars 欠落 (旧 NDJSON)
    /// のため outcome から除外される (null 耐性)。
    #[test]
    fn outcome_metrics_golden_fixture_fixed_values() {
        let path = fixture_path("outcome_metrics.ndjson");
        let feats = collect_logged_feats(&path).expect("collect_logged_feats");
        let (pastes, excluded) = collect_paste_events(&path).expect("collect_paste_events");
        let keys = collect_key_events(&path).expect("collect_key_events");
        // chars 欠落 paste (t=50000) は除外され、capture 済 paste(t=205000) のみ
        assert_eq!(
            pastes.len(),
            1,
            "only paste with external_paste_chars counted"
        );
        assert_eq!(excluded, 1, "one chars-less paste (t=50000) excluded");
        assert_eq!(keys.len(), 3, "three char key presses");

        let cfg = OutcomeConfig::default();
        let episodes = segment_stuck_episodes(&feats, &cfg);
        assert_eq!(episodes.len(), 2, "two stuck episodes (gap > merge_gap)");

        let mut o = compute_outcome_metrics(&episodes, &pastes, &keys, &feats, &cfg);
        o.excluded_paste_count = excluded;
        assert_eq!(o.excluded_paste_count, 1);
        assert_eq!(o.stuck_episode_count, 2);
        assert_eq!(o.pflow_exit_episode_count, 2);
        assert_eq!(o.manual_insert_chars, 3);
        assert_eq!(o.external_paste_chars_total, 60);
        assert_eq!(o.external_paste_count, 1);
        // manual=3, paste=60 → 3/63
        assert!((o.manual_contribution_ratio.unwrap() - 3.0 / 63.0).abs() < 1e-9);
        // recovered=2、productive=1 (ep1 のみ) → 0.5
        assert_eq!(o.pflow_exit_manual_gain_rate, Some(0.5));
        // self_recovery=1 (ep1)、分母=全エピソード2 → 0.5
        assert_eq!(o.pflow_exit_without_receipt, Some(0.5));
        // paste_after_stuck=1 (ep2 のみ・ep1 の窓には入らない) → 0.5
        assert_eq!(o.paste_after_stuck_rate, Some(0.5));
        // large_paste_rate: 60 >= 50 → 1.0
        assert_eq!(o.large_paste_rate, Some(1.0));
        // paste_count_per_hour: span 200000ms=0.05556h, 1 paste → 18.0/h
        assert!((o.paste_count_per_hour.unwrap() - 18.0).abs() < 1e-6);
    }

    /// ADR-024 の**主要アウトカム** `receipt_free_resumption` の Replay-as-Truth 回帰。
    ///
    /// ⚠️★★★ **これが無かった。** ★ 既存の `outcome_metrics.ndjson` は key 行が
    /// `t=12000/13000/14000` の 3 本しかなく、`away_gap_ms` (180_000) 以上の間隙を
    /// **構造的に作れない** —— つまり `receipt_free_resumption` は常に
    /// `event_count=0` / 全 `None` で、`collect_key_events → segment_resumptions →
    /// classify_resumption → CIF` の**経路が 1 度も踏まれていなかった**
    /// (2026-09-11 の `code-reviewer` HIGH 指摘・実測で確認)。
    /// ⚠️ `OutcomeMetrics` は `schema/current.json` の drift check の外にあるため、
    /// 壊れても CI は赤くならない。→ ★ ここで固定値として押さえる。
    ///
    /// **fixture 設計** (`resumption_outcomes.ndjson`): 3 エピソードがそれぞれ
    /// 離席候補ギャップ (>= 180s) を 1 本持ち、**3 分類すべて**を踏む。
    ///
    /// | 事象 | 再開時刻 | 結末 | 経過 |
    /// |---|---|---|---|
    /// | EV1 | 200_000 | `Receipt` (paste@230_000) | 30_000 |
    /// | EV2 | 600_000 | `NextAwayCandidate` (601_000 から次の離席候補) | 1_000 |
    /// | EV3 | 1_400_000 | `Censored` (観測終端 2_100_000) | 700_000 |
    ///
    /// ★ CIF は**手計算と突き合わせてある**:
    /// `t=1_000`: n=3, d2=1 → S=2/3 / `t=30_000`: n=2, d1=1 → CIF += (2/3)(1/2) = 1/3
    /// → `receipt_free = 1 - 1/3 = 2/3`。★ 5 分地平・10 分地平とも同値
    /// (`t=700_000` は両地平の外なので寄与せず、**at risk として残る**)。
    #[test]
    fn receipt_free_resumption_golden_fixture_fixed_values() {
        let path = fixture_path("resumption_outcomes.ndjson");
        let feats = collect_logged_feats(&path).expect("collect_logged_feats");
        let (pastes, _excluded) = collect_paste_events(&path).expect("collect_paste_events");
        let keys = collect_key_events(&path).expect("collect_key_events");
        assert_eq!(keys.len(), 8, "eight key presses");
        assert_eq!(pastes.len(), 2, "two external pastes");

        let cfg = OutcomeConfig::default();
        let episodes = segment_stuck_episodes(&feats, &cfg);
        assert_eq!(episodes.len(), 3, "three stuck episodes");

        let o = compute_outcome_metrics(&episodes, &pastes, &keys, &feats, &cfg);
        let r = &o.receipt_free_resumption;

        // ⚠️ ここが 0 に戻ったら、fixture が経路を踏まなくなっている (退行の本体)。
        assert_eq!(r.event_count, 3, "three resumption events");
        assert_eq!(r.source_episode_count, 3, "one event per episode");
        assert_eq!(r.receipt_count, 1);
        assert_eq!(r.next_away_candidate_count, 1);
        assert_eq!(r.censored_count, 1);
        assert_eq!(r.degenerate_count, 0, "no zero-follow-up event");

        // 打ち切りが 700_000 なので、両地平とも at risk が 1 件残る。
        assert_eq!(r.n_at_risk_at_5min, 1);
        assert_eq!(r.n_at_risk_at_10min, 1);

        // 手計算: CIF_receipt = (2/3)*(1/2) = 1/3 → receipt_free = 2/3 (両地平)。
        let five = r.receipt_free_at_5min.expect("5min horizon reached");
        let ten = r.receipt_free_at_10min.expect("10min horizon reached");
        assert!(
            (five - 2.0 / 3.0).abs() < 1e-9,
            "receipt_free_at_5min={five}"
        );
        assert!(
            (ten - 2.0 / 3.0).abs() < 1e-9,
            "receipt_free_at_10min={ten}"
        );

        // 3 分類の (経過, 種別) を固定する。
        let mut kinds: Vec<(u64, &str)> = r
            .outcomes
            .iter()
            .map(|o| {
                let k = match o.kind {
                    ResumptionOutcomeKind::Receipt => "receipt",
                    ResumptionOutcomeKind::NextAwayCandidate => "next_away_candidate",
                    ResumptionOutcomeKind::Censored => "censored",
                };
                (o.elapsed_ms, k)
            })
            .collect();
        kinds.sort_unstable();
        assert_eq!(
            kinds,
            vec![
                (1_000, "next_away_candidate"),
                (30_000, "receipt"),
                (700_000, "censored"),
            ]
        );
    }

    /// 旧 NDJSON (paste/key 行が無い既存 fixture) でも collector が panic せず空を返し、
    /// outcome が全 None / 0 になることを確認する (null 耐性・後方互換)。
    #[test]
    fn outcome_metrics_legacy_fixture_no_panic() {
        let path = fixture_path("phase1_minimal.ndjson");
        let feats = collect_logged_feats(&path).expect("collect_logged_feats");
        let (pastes, _excluded) = collect_paste_events(&path).expect("collect_paste_events");
        let keys = collect_key_events(&path).expect("collect_key_events");
        let cfg = OutcomeConfig::default();
        let episodes = segment_stuck_episodes(&feats, &cfg);
        let o = compute_outcome_metrics(&episodes, &pastes, &keys, &feats, &cfg);
        assert_eq!(o.external_paste_count, 0);
        assert!(o.manual_contribution_ratio.is_none() || o.external_paste_chars_total == 0);
        assert!(!o.paste_count_per_hour.map(|v| v.is_nan()).unwrap_or(false));
    }

    /// 層 1: NDJSON の 1 行文字列を `LoggedFeatDto` にデシリアライズし、
    /// `FeatSnapshot` への変換でフィールドが一致することを確認する。
    /// schema_dto.rs の LogEntryDto::Feat と本 DTO が乖離したら落ちる。
    #[test]
    fn logged_feat_dto_deserialize_matches_ndjson() {
        let line = r#"{"type":"feat","t":1700000001000,"f1":140.0,"f3":0.0,"f4":4.0,"f5":0.0,"f6":0.0,"p_flow":0.85,"p_inc":0.10,"p_stuck":0.05,"raw_x":0.0,"raw_y":0.6,"ewma_x":0.07,"ewma_y":0.74,"obs":3,"alpha":0.3}"#;
        let ev: ReplayEvent = serde_json::from_str(line).expect("parse ReplayEvent");
        let val = match ev {
            ReplayEvent::Feat(v) => v,
            _ => panic!("expected ReplayEvent::Feat variant"),
        };
        let dto: LoggedFeatDto = serde_json::from_value(val).expect("parse LoggedFeatDto");
        let feat: FeatSnapshot = dto.try_into().expect("valid dto converts to FeatSnapshot");
        assert_eq!(feat.timestamp, 1_700_000_001_000);
        assert!((feat.f1 - 140.0).abs() < 1e-9);
        assert!((feat.p_flow - 0.85).abs() < 1e-9);
        assert!((feat.p_inc - 0.10).abs() < 1e-9);
        assert!((feat.p_stuck - 0.05).abs() < 1e-9);
        assert_eq!(feat.obs, 3);
        assert!((feat.alpha - 0.3).abs() < 1e-9);
    }

    /// ペーストイベント行が deserialize でき、`timestamp()==None` で snapshot 再実行の
    /// 時刻順ソートから除外されることを確認する。
    /// 本 variant が無いと paste 行を含む NDJSON で gse-replay が parse エラーになる。
    /// 旧形式 (`external_paste_chars` 無し) と新形式の両方を後方互換で受理する。
    #[test]
    fn paste_event_parses_and_is_skipped_from_replay() {
        // 旧フィクスチャ形式: external_paste_chars 欠落 → serde default で None。
        let legacy = r#"{"type":"paste","t":1700000005000}"#;
        let ev: ReplayEvent =
            serde_json::from_str(legacy).expect("parse legacy ReplayEvent::Paste");
        assert!(
            matches!(
                ev,
                ReplayEvent::Paste {
                    t: 1_700_000_005_000,
                    external_paste_chars: None,
                }
            ),
            "expected legacy ReplayEvent::Paste with None, got {ev:?}"
        );
        assert_eq!(
            ev.timestamp(),
            None,
            "paste は timestamp()==None で除外する"
        );

        // 新形式: external_paste_chars あり。
        let new = r#"{"type":"paste","t":42,"external_paste_chars":7}"#;
        let ev: ReplayEvent = serde_json::from_str(new).expect("parse new ReplayEvent::Paste");
        assert!(
            matches!(
                ev,
                ReplayEvent::Paste {
                    t: 42,
                    external_paste_chars: Some(7),
                }
            ),
            "expected ReplayEvent::Paste with Some(7), got {ev:?}"
        );
    }

    /// ⚠️★★★ **O1 (R3) の 4 行種が `--snapshot` 経路を落とさない**こと。
    ///
    /// ★ `run_replay` は**未知タグを `Err` にして中断する**ので、行種を足して
    /// `ReplayEvent` に足し忘れると **その形式のログが 1 本も replay できなくなる**。
    /// ⚠️ 2026-08-09 に `hook_health` で実測した失敗様式の再発防止である。
    ///
    /// ★ 併せて **FeatSnapshot 列が 1 件も変わらない**ことを見る ——
    /// ⚠️ ADR-014 **D4b**（記録のみ・推論に 1 バイトも流さない）が実行可能な契約になる。
    #[test]
    fn o1_observation_lines_are_skipped_by_run_replay() {
        let lines = [
            r#"{"type":"recording_pause","t":120000,"paused":true}"#,
            r#"{"type":"focus_transition","t":120100}"#,
            r#"{"type":"pointer_bin","t":120200,"moved":3,"buttons":1,"wheel":0}"#,
            r#"{"type":"secure_input","t":120300,"on":true}"#,
        ];
        for line in lines {
            let ev: ReplayEvent = serde_json::from_str(line).unwrap_or_else(|e| {
                panic!("O1 の行がパースできない: {line} ({e})");
            });
            assert_eq!(
                ev.timestamp(),
                None,
                "O1 の行は時刻順ソートから除外する: {line}"
            );
        }

        let mut ndjson =
            std::fs::read_to_string(fixture_path("minimal.ndjson")).expect("read minimal fixture");
        for line in lines {
            ndjson.push_str(line);
            ndjson.push('\n');
        }
        let tmp = std::env::temp_dir().join(format!(
            "gse_o1_observation_replay_{}.ndjson",
            std::process::id()
        ));
        std::fs::write(&tmp, &ndjson).expect("write temp fixture");

        let with_lines = run_replay(&tmp).expect("run_replay must accept O1 observation lines");
        let baseline = run_replay(&fixture_path("minimal.ndjson")).expect("baseline replay");
        assert_eq!(
            with_lines, baseline,
            "O1 の観測行は FeatSnapshot 列を 1 ビットも変えてはならない (ADR-014 D4b)"
        );
        let _ = std::fs::remove_file(&tmp);
    }

    /// ⚠️★★ `hook_health` 行 (フック生存診断) を含む NDJSON が **`run_replay` を通る**こと。
    ///
    /// ★ この回帰が要る理由 (2026-08-09 に実測で踏んだ): `run_replay` は未知タグを
    /// `Err` にして**中断する**ため、`logger.rs` に行型を足して `ReplayEvent` に足し忘れると
    /// **その版のアプリで採った実セッションが 1 本も replay できなくなる**
    /// (`parse error: unknown variant 'hook_health'`)。
    /// ⚠️ ゴールデン fixture は全て旧形式なので、**ゴールデンが緑でもこの事故は検出できない**。
    #[test]
    fn hook_health_line_is_skipped_by_run_replay() {
        let line =
            r#"{"type":"hook_health","t":120000,"alive":false,"starved_ms":120000,"rehook":true}"#;
        let ev: ReplayEvent = serde_json::from_str(line).expect("parse hook_health");
        assert!(
            matches!(ev, ReplayEvent::HookHealth(_)),
            "expected ReplayEvent::HookHealth, got {ev:?}"
        );
        assert_eq!(
            ev.timestamp(),
            None,
            "hook_health は時刻順ソートから除外する"
        );

        // ★ 単体の deserialize だけでは足りない: **run_replay 全体が通ること**を確かめる。
        let mut ndjson =
            std::fs::read_to_string(fixture_path("minimal.ndjson")).expect("read minimal fixture");
        ndjson.push_str(line);
        ndjson.push('\n');
        // ★ 同一ファイル内の他テストと同じく PID を付ける (並行実行での衝突回避)。
        let tmp = std::env::temp_dir().join(format!(
            "gse_hook_health_replay_{}.ndjson",
            std::process::id()
        ));
        std::fs::write(&tmp, &ndjson).expect("write temp fixture");

        let with_line = run_replay(&tmp).expect("run_replay must accept hook_health lines");
        let baseline = run_replay(&fixture_path("minimal.ndjson")).expect("baseline replay");
        assert_eq!(
            with_line.len(),
            baseline.len(),
            "hook_health 行は FeatSnapshot 列を 1 件も変えてはならない"
        );
        let _ = std::fs::remove_file(&tmp);
    }

    /// ⚠️★★★ **形の崩れた `ime_shadow` 行が `run_replay` を落とさない**
    /// （2026-09-15・`code-reviewer` / `security-checker` が独立に HIGH で指摘した M1 の回帰）。
    ///
    /// ★ issue 002 の初版は `ReplayEvent::ImeShadow` を `serde_json::Value` から
    /// **4 フィールド必須の構造体**へ変えた。⚠️ `run_replay` は**既知タグのパース失敗も
    /// `Err` にして中断する**ため、崩れた行が 1 本あるだけで**リプレイが丸ごと落ちた**
    /// （★ `hook_health` / `starve_window` / `activity_label` と同じ失敗様式で 4 度目）。
    ///
    /// ⚠️★★★ **`Option` ＋ `#[serde(default)]` でも足りなかった**（★ 2026-09-15 に実測）——
    /// `Option<bool>` は `0` を受け取れないので `"abandon":0` は依然 exit 1 になる。
    /// → ★ variant を `Value` に戻し、構造化は `ImeShadowDto` が担う形にした。
    ///
    /// ⚠️ **ゴールデンが緑でもこの事故は検出できない**（★ 既存 fixture に崩れた行が無いため）。
    /// → ★ **行を足して通す**形でなければ回帰にならない。
    #[test]
    fn partial_ime_shadow_line_does_not_break_run_replay() {
        // ★ 3 つとも「issue 002 の初版が実際に落ちた形」である（⚠️ 想像で並べていない）。
        let broken = [
            // 欠落 → 旧実装は `missing field 'nav'`
            r#"{"type":"ime_shadow","t":1700000002500,"dwell_ms":300}"#,
            // 整数 bool → 旧実装は `invalid type: integer 0, expected a boolean`
            r#"{"type":"ime_shadow","t":1700000002500,"dwell_ms":300,"nav":1,"abandon":0}"#,
            // null → 旧実装は `invalid type: null, expected u64`
            r#"{"type":"ime_shadow","t":1700000002500,"dwell_ms":null,"nav":1,"abandon":true}"#,
        ];
        let baseline = run_replay(&fixture_path("minimal.ndjson")).expect("baseline replay");

        for (i, line) in broken.iter().enumerate() {
            let ev: ReplayEvent = serde_json::from_str(line)
                .unwrap_or_else(|e| panic!("崩れた ime_shadow 行も受理すること ({line}): {e}"));
            assert!(
                matches!(ev, ReplayEvent::ImeShadow(_)),
                "expected ReplayEvent::ImeShadow, got {ev:?}"
            );
            assert_eq!(
                ev.timestamp(),
                None,
                "ime_shadow は時刻順ソートから除外する"
            );

            let mut ndjson = std::fs::read_to_string(fixture_path("minimal.ndjson"))
                .expect("read minimal fixture");
            ndjson.push_str(line);
            ndjson.push('\n');
            let tmp = std::env::temp_dir().join(format!(
                "gse_partial_ime_shadow_replay_{}_{}.ndjson",
                std::process::id(),
                i
            ));
            std::fs::write(&tmp, &ndjson).expect("write temp fixture");

            let with_line = run_replay(&tmp).unwrap_or_else(|e| {
                panic!("run_replay must accept broken ime_shadow ({line}): {e}")
            });
            assert_eq!(
                with_line.len(),
                baseline.len(),
                "ime_shadow 行は FeatSnapshot 列を 1 件も変えてはならない ({line})"
            );

            // ★ `--features` 側は**形の合わない行を捨てる**（⚠️ 0 に畳まない）。
            let collected = collect_all_ime_shadow_events(&tmp).expect("collect must not fail");
            assert!(
                collected.is_empty(),
                "形が合わない ime_shadow 行は採らない (0 埋めしない): {collected:?} ({line})"
            );
            let _ = std::fs::remove_file(&tmp);
        }
    }

    /// AC17 (issue 008): 形の合わない `feat` 行 (`t` 欠落 / 文字列 / `null`) があっても
    /// `run_replay` の `FeatSnapshot` 列は 1 件も変わらず (`ReplayEvent::Feat` が既に
    /// `serde_json::Value` なので、形に関わらずパース自体は常に成功する)、`--features` 側の
    /// `collect_all_feat_timestamps` はその行を採らない (0 件のまま)。
    #[test]
    fn malformed_feat_line_does_not_break_run_replay() {
        let broken = [
            // t 欠落
            r#"{"type":"feat","keys":3}"#,
            // 文字列
            r#"{"type":"feat","t":"not-a-number"}"#,
            // null
            r#"{"type":"feat","t":null}"#,
        ];
        let baseline = run_replay(&fixture_path("minimal.ndjson")).expect("baseline replay");

        for (i, line) in broken.iter().enumerate() {
            let ev: ReplayEvent = serde_json::from_str(line)
                .unwrap_or_else(|e| panic!("崩れた feat 行も受理すること ({line}): {e}"));
            assert!(
                matches!(ev, ReplayEvent::Feat(_)),
                "expected ReplayEvent::Feat, got {ev:?}"
            );
            assert_eq!(ev.timestamp(), None, "feat は時刻順ソートから除外する");

            let mut ndjson = std::fs::read_to_string(fixture_path("minimal.ndjson"))
                .expect("read minimal fixture");
            ndjson.push_str(line);
            ndjson.push('\n');
            let tmp = std::env::temp_dir().join(format!(
                "gse_malformed_feat_replay_{}_{}.ndjson",
                std::process::id(),
                i
            ));
            std::fs::write(&tmp, &ndjson).expect("write temp fixture");

            let with_line = run_replay(&tmp)
                .unwrap_or_else(|e| panic!("run_replay must accept broken feat ({line}): {e}"));
            assert_eq!(
                with_line.len(),
                baseline.len(),
                "feat 行は FeatSnapshot 列を 1 件も変えてはならない ({line})"
            );

            let collected = collect_all_feat_timestamps(&tmp).expect("collect must not fail");
            assert!(
                collected.is_empty(),
                "形が合わない feat 行は採らない: {collected:?} ({line})"
            );
            let _ = std::fs::remove_file(&tmp);
        }
    }

    /// AC12 / M3 (issue 007): 形の合わない `hook_health` 行 (`alive` 欠落 / 型違い) があっても
    /// `run_replay` の `FeatSnapshot` 列は 1 件も (**内容も**) 変わらず (`ReplayEvent::HookHealth`
    /// は既に `serde_json::Value` なので、形に関わらずパース自体は常に成功する)、`--features`
    /// 側の `collect_all_hook_health_events` はその行を採らない。
    ///
    /// ⚠️★★★ 2026-09-18 改訂 (判断 24・code-reviewer M3): **形の正しい対照行を 1 本混ぜ**、
    /// collector がちょうどそれだけを採ることを確かめる (★ 旧版は壊れた行だけを足していたので
    /// 「collector が hook_health を丸ごと読み飛ばす」変異でも `collected.is_empty()` が
    /// 誤って緑になった)。`FeatSnapshot` 列の比較も `.len()` だけでなく**内容**で行う。
    #[test]
    fn malformed_hook_health_line_does_not_break_run_replay() {
        let broken = [
            // alive 欠落
            r#"{"type":"hook_health","t":1700000002500,"starved_ms":0,"rehook":false,"dropped_delta":0}"#,
            // alive の型違い (整数)
            r#"{"type":"hook_health","t":1700000002500,"alive":1,"starved_ms":0,"rehook":false,"dropped_delta":0}"#,
        ];
        // ★ 形の正しい対照行。壊れた行と混ぜても collector はこれだけをちょうど 1 件採ること。
        let control = r#"{"type":"hook_health","t":1700000002600,"alive":true,"starved_ms":10,"rehook":false,"dropped_delta":1}"#;
        let baseline = run_replay(&fixture_path("minimal.ndjson")).expect("baseline replay");

        for (i, line) in broken.iter().enumerate() {
            let ev: ReplayEvent = serde_json::from_str(line)
                .unwrap_or_else(|e| panic!("崩れた hook_health 行も受理すること ({line}): {e}"));
            assert!(
                matches!(ev, ReplayEvent::HookHealth(_)),
                "expected ReplayEvent::HookHealth, got {ev:?}"
            );
            assert_eq!(
                ev.timestamp(),
                None,
                "hook_health は時刻順ソートから除外する"
            );

            let mut ndjson = std::fs::read_to_string(fixture_path("minimal.ndjson"))
                .expect("read minimal fixture");
            ndjson.push_str(line);
            ndjson.push('\n');
            ndjson.push_str(control);
            ndjson.push('\n');
            let tmp = std::env::temp_dir().join(format!(
                "gse_malformed_hook_health_replay_{}_{}.ndjson",
                std::process::id(),
                i
            ));
            std::fs::write(&tmp, &ndjson).expect("write temp fixture");

            let with_line = run_replay(&tmp).unwrap_or_else(|e| {
                panic!("run_replay must accept broken hook_health ({line}): {e}")
            });
            assert_eq!(
                with_line, baseline,
                "hook_health 行は FeatSnapshot 列を 1 件も (内容も) 変えてはならない ({line})"
            );

            let collected = collect_all_hook_health_events(&tmp).expect("collect must not fail");
            assert_eq!(
                collected.len(),
                1,
                "壊れた行は捨て、形の正しい対照行だけをちょうど 1 件採ること: {collected:?} ({line})"
            );
            assert!(collected[0].alive, "対照行は alive=true のはず");
            assert_eq!(collected[0].dropped_delta, Some(1));
            let _ = std::fs::remove_file(&tmp);
        }
    }

    /// 判断 24 (code-reviewer M1) の収集側回帰: 旧形式の `hook_health` 行 (`dropped_delta`
    /// フィールド自体が無い) を `collect_all_hook_health_events` に通しても `0` に正規化
    /// しない。★ `quality.rs` 側の単体テスト (`missing_dropped_delta_is_null_not_zero`) は
    /// 集約ロジックだけを見るので、収集側が `unwrap_or(0)` に戻る回帰はここでしか捕まえられない。
    #[test]
    fn collect_all_hook_health_events_preserves_missing_dropped_delta_as_none() {
        let ndjson = concat!(
            "{\"type\":\"meta\",\"session_start\":1700000000000,\"hmm_version\":\"0.2.0\"}\n",
            // dropped_delta フィールドが無い (2026-08-19 より前のログ形式)。
            "{\"type\":\"hook_health\",\"t\":1700000001000,\"alive\":true,\"starved_ms\":0,\
             \"rehook\":false}\n",
        );
        let tmp = std::env::temp_dir().join(format!(
            "gse_hook_health_missing_dropped_delta_{}.ndjson",
            std::process::id()
        ));
        std::fs::write(&tmp, ndjson).expect("write temp fixture");

        let collected = collect_all_hook_health_events(&tmp).expect("collect must not fail");
        assert_eq!(collected.len(), 1);
        assert_eq!(
            collected[0].dropped_delta, None,
            "dropped_delta が無い行を 0 に正規化してはならない"
        );
        let _ = std::fs::remove_file(&tmp);
    }

    /// AC15 (issue 007・判断 24・security-checker LOW-3): `meta.capabilities` が JSON
    /// オブジェクトでない、または直列化して 4096 バイトを超えるなら `collect_meta_session_facts`
    /// は `Err` を返す (`--features` は exit 1)。⚠️ `null` に倒すと「宣言が無い」と誤報になる
    /// ため、`Ok(None)` にしない。
    #[test]
    fn non_object_or_oversized_capabilities_is_an_error() {
        // 非オブジェクト (文字列)。
        let non_object = "{\"type\":\"meta\",\"session_start\":1700000000000,\
             \"hmm_version\":\"0.2.0\",\"capabilities\":\"x\"}\n";
        let tmp1 = std::env::temp_dir().join(format!(
            "gse_capabilities_non_object_{}.ndjson",
            std::process::id()
        ));
        std::fs::write(&tmp1, non_object).expect("write temp fixture");
        let err =
            collect_meta_session_facts(&tmp1).expect_err("非オブジェクトの capabilities は Err");
        assert!(
            err.contains("not a JSON object"),
            "エラー文言が理由を示していない: {err}"
        );
        let _ = std::fs::remove_file(&tmp1);

        // 4096 バイトを超えるオブジェクト。
        let padding = "a".repeat(5000);
        let oversized = format!(
            "{{\"type\":\"meta\",\"session_start\":1700000000000,\"hmm_version\":\"0.2.0\",\
             \"capabilities\":{{\"padding\":\"{padding}\"}}}}\n"
        );
        let tmp2 = std::env::temp_dir().join(format!(
            "gse_capabilities_oversized_{}.ndjson",
            std::process::id()
        ));
        std::fs::write(&tmp2, &oversized).expect("write temp fixture");
        let err =
            collect_meta_session_facts(&tmp2).expect_err("4096 バイトを超える capabilities は Err");
        assert!(
            err.contains("exceeds limit"),
            "エラー文言が理由を示していない: {err}"
        );
        let _ = std::fs::remove_file(&tmp2);

        // 対照: 通常の (規範) capabilities は Ok(Some(_)) のまま。
        let path = fixture_path("instrument_rich.ndjson");
        let ok = collect_meta_session_facts(&path).expect("正常な capabilities は Err にならない");
        assert!(ok.capabilities.is_some());
    }

    /// AC18 (issue 007): `collect_meta_session_facts` / `collect_all_hook_health_events` →
    /// `build_feature_rows` の**配線**を `instrument_rich.ndjson` から通して固定する
    /// (`ime_shadow_events_reach_feature_rows_through_the_collector` と同型)。
    #[test]
    fn quality_inputs_reach_feature_rows_through_the_collectors() {
        let path = fixture_path("instrument_rich.ndjson");

        let keys = collect_key_events(&path).expect("collect keys");
        let paste_ts = collect_all_paste_timestamps(&path).expect("collect pastes");
        let ime_events = collect_all_ime_shadow_events(&path).expect("collect ime_shadow");
        let feat_ts = collect_all_feat_timestamps(&path).expect("collect feat timestamps");
        let task_kind_declarations =
            collect_task_kind_declarations(&path).expect("collect task_kind declarations");
        let capabilities = collect_meta_session_facts(&path)
            .expect("collect meta facts")
            .capabilities;
        assert!(
            capabilities.is_some(),
            "instrument_rich の meta は capabilities を持つはず"
        );
        let hook_health_events =
            collect_all_hook_health_events(&path).expect("collect hook_health events");

        let stall_onset_inputs = gse_next_lib::analysis::feat_offline::StallOnsetInputs {
            feat_ts: &feat_ts,
            task_kind_declarations: &task_kind_declarations,
            config: gse_next_lib::analysis::feat_offline::StallOnsetConfig::default(),
        };
        let quality_inputs = gse_next_lib::analysis::feat_offline::QualityInputs {
            capabilities_declared: capabilities.is_some(),
            hook_health: &hook_health_events,
        };
        let rows = gse_next_lib::analysis::feat_offline::build_feature_rows(
            &keys,
            &paste_ts,
            &ime_events,
            MAX_FEATURE_TICKS,
            &stall_onset_inputs,
            &quality_inputs,
        )
        .expect("build rows");

        assert_eq!(rows.len(), 15, "instrument_rich は 15 tick のはず");

        let hh_ticks: Vec<usize> = rows
            .iter()
            .enumerate()
            .filter(|(_, r)| r.quality.hook_health.is_some())
            .map(|(i, _)| i)
            .collect();
        assert_eq!(
            hh_ticks,
            vec![5, 13],
            "hook_health が非 null の tick は 5 / 13 だけのはず"
        );

        assert_eq!(
            rows[13].quality.missing_reasons,
            vec!["dropped_events".to_string()],
            "tick 13 だけ dropped_events が立つこと"
        );
        for (i, row) in rows.iter().enumerate() {
            if i != 13 {
                assert!(
                    row.quality.missing_reasons.is_empty(),
                    "tick {i} に理由が立ってはならない: {:?}",
                    row.quality.missing_reasons
                );
            }
        }

        // ⚠️★★★ 2026-09-20 (判断 3・封筒): `capabilities` は行から封筒へ移した。
        // ★ ここでは「行に漏れていないこと」だけを固定し、値が `meta` と等しいことは
        //   `envelope_carries_meta_facts_and_sharing_marker` が封筒側で固定する。
        let rows_json = serde_json::to_string(&rows).expect("serialize rows");
        assert!(
            !rows_json.contains("capabilities"),
            "行に capabilities が残っている (封筒へ移したはず)"
        );
    }

    /// 起票 2 / 5 の回帰: `--features` の封筒が `meta` 由来の事実・入力の同一性・
    /// 「共有しない」のマーカーを持ち、**同じ入力から同じ出力**になること。
    ///
    /// ⚠️ ここは配線 (`collect_meta_session_facts` / `sha256_prefix_of_file` /
    /// `FeatureEnvelope`) の固定であり、封筒の受け入れ検査そのものは
    /// `.steering/20260920-envelope-issues/envelope-acceptance.sh` が持つ。
    #[test]
    fn envelope_carries_meta_facts_and_sharing_marker() {
        let path = fixture_path("instrument_rich.ndjson");

        let facts = collect_meta_session_facts(&path).expect("collect meta facts");
        assert!(
            facts.session_start.is_some(),
            "instrument_rich の meta は session_start を持つはず"
        );
        // ⚠️★★★ **収集時と解析時の `hmm_version` は食い違いうる。**
        // ★ `instrument_rich.ndjson` の `meta.hmm_version` は "0.2.0"、現行バイナリの
        //   `HMM_VERSION` は "0.5.0" (2026-09-20 実測)。★ 封筒が両方を別フィールドで
        //   持つ理由がまさにこれで、**食い違いが読めること自体が目的**である
        //   (`provenance.hmm_version` = 収集時 / `config.hmm_version` = 解析時)。
        assert_eq!(
            facts.hmm_version.as_deref(),
            Some("0.2.0"),
            "fixture の meta.hmm_version をそのまま読むこと (現行バイナリの値へ寄せない)"
        );
        assert_ne!(
            facts.hmm_version.as_deref(),
            Some(HMM_VERSION),
            "★ この fixture では収集時と解析時が食い違う —— 揃ってしまったら、\
             封筒が 2 つのフィールドを持つ意味を別の fixture で張り直すこと"
        );

        // ★ sha256 は 16 桁の 16 進で、2 回読んでも同じ。
        let h1 = sha256_prefix_of_file(&path).expect("hash once");
        let h2 = sha256_prefix_of_file(&path).expect("hash twice");
        assert_eq!(h1, h2, "同じファイルのハッシュは変わらない");
        assert_eq!(h1.len(), SOURCE_SHA256_HEX_CHARS);
        assert!(
            h1.chars().all(|c| c.is_ascii_hexdigit()),
            "16 進以外の文字が出た: {h1}"
        );

        // ★ basename はディレクトリを含まない。
        let base = source_basename_of(&path);
        assert_eq!(base, "instrument_rich.ndjson");
        assert!(!base.contains('/') && !base.contains('\\'));

        // ★ マーカーは固定値で、真偽値 2 つは「匿名化を通っていない・絶対 epoch」を意味する。
        let marker = serde_json::to_value(SharingMarker::default()).expect("serialize marker");
        assert_eq!(marker["gse_dataset"], "prohibited");
        assert_eq!(marker["anonymized"], false);
        assert_eq!(marker["absolute_epoch_ms"], true);

        // ★ config は解析時の値で、埋め込みの凍結 JSON をそのまま映す。
        let resolved = resolve_feature_config(None, &[]).expect("frozen config resolves");
        let cfg = resolved.stall_onset_config();
        let dto = serde_json::to_value(FeatureConfigDto::from_resolved(
            &resolved,
            MAX_FEATURE_TICKS,
            None,
            None,
            None,
        ))
        .expect("serialize config");
        assert_eq!(dto["w_ms"], cfg.w_ms);
        assert_eq!(dto["hole_gap_ms"], cfg.hole_gap_ms);
        assert_eq!(dto["max_feature_ticks"], MAX_FEATURE_TICKS);
        assert_eq!(dto["hmm_version"], HMM_VERSION);
        assert_eq!(dto["engine_tick_ms"], ENGINE_TICK_MS);
    }

    /// 凍結 JSON の `operational` (テストの期待値の元)。★ 実装が読むのと同じ埋め込みを、
    /// 別経路 (`serde_json::Value`) で引き直す —— `P1Operational` の写しを信用しない。
    fn frozen_operational_value() -> serde_json::Value {
        let v: serde_json::Value =
            serde_json::from_str(FROZEN_P1_EPISODE_JSON).expect("frozen JSON parses");
        v["operational"].clone()
    }

    /// AC1 / AC2: 無指定なら凍結値の 11 個 (v1.2 で 2 つ、v1.3 で 1 つ足した) がそのまま出て、`overrides` は空・由来は `frozen`。
    #[test]
    fn resolve_without_flags_reproduces_the_frozen_values() {
        let resolved = resolve_feature_config(None, &[]).expect("frozen resolves");
        let dto = serde_json::to_value(FeatureConfigDto::from_resolved(
            &resolved, 1, None, None, None,
        ))
        .expect("serialize config");
        let want = frozen_operational_value();
        for key in P1_OPERATIONAL_KEYS {
            assert_eq!(dto[key], want[key], "config.{key} は凍結値と一致する");
        }
        assert_eq!(dto["config_source"], "frozen");
        assert_eq!(dto["overrides"], serde_json::json!([]));
        assert_eq!(dto["prereg_id"], "p1-episode");
        assert_eq!(dto["prereg_version"], "1.2.0");
        let sha = dto["prereg_sha256_prefix"]
            .as_str()
            .expect("sha is a string");
        assert_eq!(sha.len(), SOURCE_SHA256_HEX_CHARS);
        // ★ warmup_count は凍結値どおり 100 (既定の `None` ではない) —— issue 001 の要点。
        assert_eq!(dto["warmup_count"], 100);
    }

    /// AC3: `--set` は凍結値から**外れた**キーだけを `overrides` に残す。
    /// ⚠️ 凍結値と同じ値の `--set` は外れていないので載せない (対照)。
    #[test]
    fn set_records_only_deviations_from_the_frozen_values() {
        let sets = vec!["q=0.995".to_string()];
        let resolved = resolve_feature_config(None, &sets).expect("q=0.995 resolves");
        assert_eq!(resolved.operational.q, 0.995);
        assert_eq!(resolved.config_source, "frozen", "--set は由来を変えない");
        assert_eq!(resolved.overrides.len(), 1);
        assert_eq!(resolved.overrides[0].key, "q");
        assert_eq!(resolved.overrides[0].frozen, serde_json::json!(0.99));
        assert_eq!(resolved.overrides[0].value, serde_json::json!(0.995));

        let same = vec!["q=0.99".to_string(), "warmup_count=100".to_string()];
        let resolved = resolve_feature_config(None, &same).expect("same values resolve");
        assert!(
            resolved.overrides.is_empty(),
            "外れていない --set は載らない"
        );
    }

    /// AC4: 未知キー / 型の不一致 / 範囲外 / 形式違いは**すべて `Err`** (fail-closed)。
    /// ★ 正常な `--set` が通る陰性対照を先に置く (`Err` を返すだけの実装を通さない)。
    #[test]
    fn set_is_fail_closed_on_unknown_key_bad_type_and_out_of_range() {
        assert!(resolve_feature_config(None, &["hole_gap_ms=3000".to_string()]).is_ok());
        // 陰性対照 (security LOW-1): 上限ちょうど (3600000 = 1 時間) は Ok。
        assert!(resolve_feature_config(None, &["t1a_window_ms=3600000".to_string()]).is_ok());
        for bad in [
            "bogus=1",                          // 未知キー
            "q=abc",                            // 型の不一致
            "w_ms=-1",                          // 型の不一致 (負)
            "w_ms=1.5",                         // 型の不一致 (小数)
            "w_ms=0",                           // 範囲外
            "q=0",                              // 範囲外
            "q=1",                              // 範囲外 (⌈1/(1−q)⌉ が発散する)
            "q=NaN",                            // 範囲外 (非有限)
            "warmup_count=0",                   // 範囲外
            "net_diff_min=0",                   // 範囲外
            "net_diff_min=9223372036854775808", // 範囲外 (i64::MAX + 1 ・ `as i64` で負に丸まる)
            "t1a_window_ms=3600001",            // 範囲外 (security LOW-1・1 時間超)
            "theta_estimator=linear",           // 未実装の推定法
            "q",                                // `=` が無い
        ] {
            assert!(
                resolve_feature_config(None, &[bad.to_string()]).is_err(),
                "`--set {bad}` は Err でなければならない"
            );
        }
    }

    /// AC5: `--feature-config` は外部ファイルの値を採り、由来を `file` にする。
    /// ⚠️ 未知キー・欠けたキーを持つファイルは `Err` (黙って凍結値で埋めない)。
    #[test]
    fn feature_config_file_is_read_and_labelled_file() {
        let dir = envelope_tmp_dir("feature_config");
        let mut value: serde_json::Value =
            serde_json::from_str(FROZEN_P1_EPISODE_JSON).expect("frozen JSON parses");
        value["operational"]["hole_gap_ms"] = serde_json::json!(5000);
        let path = dir.join("cfg.json");
        std::fs::write(&path, serde_json::to_vec(&value).expect("serialize")).expect("write");

        let resolved = resolve_feature_config(Some(&path), &[]).expect("file resolves");
        assert_eq!(resolved.config_source, "file");
        assert_eq!(resolved.operational.hole_gap_ms, 5000);
        assert_eq!(resolved.overrides.len(), 1);
        assert_eq!(resolved.overrides[0].key, "hole_gap_ms");
        // `--set` はファイルの上に重なる。
        let both = resolve_feature_config(Some(&path), &["q=0.995".to_string()]).expect("resolves");
        assert_eq!(both.config_source, "file");
        assert_eq!(both.overrides.len(), 2);

        value["operational"]["bogus"] = serde_json::json!(1);
        let unknown = dir.join("unknown.json");
        std::fs::write(&unknown, serde_json::to_vec(&value).expect("serialize")).expect("write");
        assert!(resolve_feature_config(Some(&unknown), &[]).is_err());

        value["operational"] = serde_json::json!({ "w_ms": 30000 });
        let partial = dir.join("partial.json");
        std::fs::write(&partial, serde_json::to_vec(&value).expect("serialize")).expect("write");
        assert!(resolve_feature_config(Some(&partial), &[]).is_err());

        assert!(resolve_feature_config(Some(&dir.join("missing.json")), &[]).is_err());
        let _ = std::fs::remove_dir_all(&dir);
    }

    /// 凍結 JSON の `id` / `version` だけを差し替えた `--feature-config` 用ファイルを書く (issue 007)。
    /// ★ 値は `serde_json` に渡すので、制御文字・改行・引用符も JSON として正しくエスケープされる。
    fn write_feature_config_with_identity(
        dir: &Path,
        name: &str,
        id: &str,
        version: &str,
    ) -> PathBuf {
        let mut value: serde_json::Value =
            serde_json::from_str(FROZEN_P1_EPISODE_JSON).expect("frozen JSON parses");
        value["id"] = serde_json::json!(id);
        value["version"] = serde_json::json!(version);
        let path = dir.join(name);
        std::fs::write(&path, serde_json::to_vec(&value).expect("serialize")).expect("write");
        path
    }

    /// issue 007 AC1: 形式に合わない `id` の `--feature-config` は `Err` (fail-closed・P1-G)。
    /// ★ 陽性対照 (境界ちょうどの 64 文字・先頭が数字) を先に置く —— `Err` を返すだけの実装を通さない。
    #[test]
    fn feature_config_rejects_malformed_id() {
        let dir = envelope_tmp_dir("feature_config_bad_id");
        let max_len = "a".repeat(64);
        for ok in ["p1-episode", "0", "9x-", max_len.as_str(), "p1-episode-alt"] {
            let path = write_feature_config_with_identity(&dir, "ok.json", ok, "1.0.0");
            assert!(
                resolve_feature_config(Some(&path), &[]).is_ok(),
                "id `{ok}` は形式に合うので受理される"
            );
        }
        let too_long = "a".repeat(65);
        for bad in [
            "",                // 空
            "P1-episode",      // 大文字
            "p1 episode",      // 空白
            "p1/episode",      // `/`
            "../x",            // 経路っぽい値
            "p1\u{7}x",        // 制御文字
            "p1-episode\n",    // 末尾の改行 (`$` が改行の手前で止まる実装を通さない)
            "-p1",             // 先頭が `-`
            "p1_episode",      // `_`
            "p1-épisode",      // 非 ASCII
            too_long.as_str(), // 65 文字
        ] {
            let path = write_feature_config_with_identity(&dir, "bad.json", bad, "1.0.0");
            let err = resolve_feature_config(Some(&path), &[])
                .expect_err(&format!("id {bad:?} は Err でなければならない"));
            assert!(err.contains("`id`"), "エラーが id を名指しする: {err}");
        }
        let _ = std::fs::remove_dir_all(&dir);
    }

    /// issue 007 AC2: 形式に合わない `version` の `--feature-config` は `Err` (fail-closed・P1-G)。
    #[test]
    fn feature_config_rejects_malformed_version() {
        let dir = envelope_tmp_dir("feature_config_bad_version");
        for ok in ["1.0.0", "0.0.0", "2.3.4", "999999999.999999999.999999999"] {
            let path = write_feature_config_with_identity(&dir, "ok.json", "p1-episode", ok);
            assert!(
                resolve_feature_config(Some(&path), &[]).is_ok(),
                "version `{ok}` は形式に合うので受理される"
            );
        }
        for bad in [
            "",               // 空
            "1.0",            // 2 部
            "1.0.0.0",        // 4 部
            "v1.0.0",         // 接頭辞
            "1.0.0-rc",       // 接尾辞
            "1..0",           // 空の部
            "1.0.",           // 末尾が空
            ".1.0",           // 先頭が空
            "1.0.0\n",        // 末尾の改行
            "1.0.0 ",         // 末尾の空白
            "1.0.-1",         // 符号
            "1.0.\u{FF10}",   // 全角数字 (`char::is_numeric` 系の実装を通さない)
            "1234567890.0.0", // 10 桁 (各部は 1〜9 桁)
        ] {
            let path = write_feature_config_with_identity(&dir, "bad.json", "p1-episode", bad);
            let err = resolve_feature_config(Some(&path), &[])
                .expect_err(&format!("version {bad:?} は Err でなければならない"));
            assert!(
                err.contains("`version`"),
                "エラーが version を名指しする: {err}"
            );
        }
        let _ = std::fs::remove_dir_all(&dir);
    }

    /// issue 007 AC3: 形式に合う**別の** `id` / `version` は受理され、封筒へそのまま写り、由来は `file`。
    /// ★ 検証は形式だけで、凍結 JSON との一致は求めない (`decisions.md` 判断 16)。
    #[test]
    fn feature_config_accepts_wellformed_other_id() {
        let dir = envelope_tmp_dir("feature_config_other_id");
        let path = write_feature_config_with_identity(&dir, "alt.json", "p1-episode-alt", "2.3.4");
        let resolved = resolve_feature_config(Some(&path), &[]).expect("well-formed other id");
        assert_eq!(resolved.config_source, "file");
        assert_eq!(resolved.prereg_id, "p1-episode-alt");
        assert_eq!(resolved.prereg_version, "2.3.4");
        let dto = serde_json::to_value(FeatureConfigDto::from_resolved(
            &resolved, 1, None, None, None,
        ))
        .expect("serialize config");
        assert_eq!(dto["prereg_id"], "p1-episode-alt");
        assert_eq!(dto["prereg_version"], "2.3.4");
        assert_eq!(dto["config_source"], "file");
        let _ = std::fs::remove_dir_all(&dir);
    }

    /// issue 007 AC4: 埋め込みの凍結 JSON の `id` / `version` は形式の検査を通る (既定の実行が変わらない)。
    /// ⚠️ 通らなければ `resolve_feature_config` の全経路が「ビルドの不具合」で落ちる —— その先回りの検知。
    #[test]
    fn frozen_json_id_version_are_wellformed() {
        // ★ 実装が読むのと同じ埋め込みを別経路 (`serde_json::Value`) で引き直す。
        let value: serde_json::Value =
            serde_json::from_str(FROZEN_P1_EPISODE_JSON).expect("frozen JSON parses");
        let id = value["id"].as_str().expect("frozen id is a string");
        let version = value["version"]
            .as_str()
            .expect("frozen version is a string");
        assert!(is_wellformed_prereg_id(id), "凍結 JSON の id {id:?}");
        assert!(
            is_wellformed_prereg_version(version),
            "凍結 JSON の version {version:?}"
        );

        let resolved = resolve_feature_config(None, &[]).expect("frozen resolves");
        assert_eq!(resolved.config_source, "frozen");
        assert_eq!(resolved.prereg_id, id);
        assert_eq!(resolved.prereg_version, version);
    }

    /// `--set` / `--feature-config` は `--features` 専用: 単独では `Err`、併用なら受理される。
    #[test]
    fn feature_flags_require_features_mode() {
        let alone = vec![
            "s.ndjson".to_string(),
            "--set".to_string(),
            "q=0.995".to_string(),
        ];
        assert!(parse_args_from(alone).is_err());

        let with_features = vec![
            "s.ndjson".to_string(),
            "--features".to_string(),
            "--set".to_string(),
            "q=0.995".to_string(),
            "--set".to_string(),
            "w_ms=15000".to_string(),
            "--feature-config".to_string(),
            "cfg.json".to_string(),
        ];
        let parsed = parse_args_from(with_features).expect("--features with flags parses");
        assert_eq!(parsed.feature_sets, vec!["q=0.995", "w_ms=15000"]);
        assert_eq!(parsed.feature_config_path, Some(PathBuf::from("cfg.json")));

        let dangling = vec![
            "s.ndjson".to_string(),
            "--features".to_string(),
            "--set".to_string(),
        ];
        assert!(parse_args_from(dangling).is_err());
    }

    /// issue 004: `--pole <name>` は生の文字列のまま `Args` に載る (検証は `resolve_pole`)。
    /// ★ 値の無い `--pole` は `Err`。⚠️ 指定が無ければ `None` (= baseline)。
    #[test]
    fn pole_flag_is_carried_as_a_raw_string() {
        let with_pole = vec![
            "s.ndjson".to_string(),
            "--features".to_string(),
            "--pole".to_string(),
            "pointer_b".to_string(),
        ];
        let parsed = parse_args_from(with_pole).expect("--pole parses");
        assert_eq!(parsed.pole.as_deref(), Some("pointer_b"));
        // ★ 値は位置引数に混ざらない (session_path は `s.ndjson` のまま)。
        assert_eq!(parsed.session_path, PathBuf::from("s.ndjson"));

        // ★ 未知の名前もここでは弾かない (raw のまま持つ・exit 1 は `resolve_pole`)。
        let bogus = vec![
            "s.ndjson".to_string(),
            "--features".to_string(),
            "--pole".to_string(),
            "bogus".to_string(),
        ];
        assert_eq!(
            parse_args_from(bogus).expect("raw").pole.as_deref(),
            Some("bogus")
        );

        // ★ 重複指定は名指しで `Err` (位置引数に紛れて「positional が 3 個」にならない)。
        let twice = vec![
            "s.ndjson".to_string(),
            "--features".to_string(),
            "--pole".to_string(),
            "baseline".to_string(),
            "--pole".to_string(),
            "pointer_b".to_string(),
        ];
        let err = match parse_args_from(twice) {
            Ok(_) => panic!("--pole の重複は Err でなければならない"),
            Err(e) => e,
        };
        assert!(err.contains("only once"), "重複を名指しする: {err}");

        let none = vec!["s.ndjson".to_string(), "--features".to_string()];
        assert_eq!(parse_args_from(none).expect("parses").pole, None);

        let dangling = vec![
            "s.ndjson".to_string(),
            "--features".to_string(),
            "--pole".to_string(),
        ];
        assert!(parse_args_from(dangling).is_err());
    }

    /// issue 004 AC1〜5: `resolve_pole` は fail-closed。★ 陰性対照 (通るもの) を先に置く。
    #[test]
    fn resolve_pole_is_fail_closed() {
        // 通る: 未指定 (どのモードでも baseline) / `--features` での `baseline`。
        assert_eq!(resolve_pole(true, None), Ok(Pole::Baseline));
        assert_eq!(resolve_pole(false, None), Ok(Pole::Baseline));
        assert_eq!(resolve_pole(true, Some("baseline")), Ok(Pole::Baseline));

        // AC5: `--features` 以外での指定は、名前が正しくても止める。
        for name in ["baseline", "pointer_b", "modifier_m_plus", "bogus"] {
            let err = resolve_pole(false, Some(name)).expect_err("--features 以外は Err");
            assert!(err.contains("--features"), "理由が出る: {err}");
        }

        // AC3: 未実装の極は止める (⚠️ baseline の値を返さない)。★ 未実装の極はもう無い
        //   (極 M+ は issue 005・極 B は issue 006 で開通)。→ 全部通る。門の中身は `Pole::is_implemented` の単体テストが固定する。
        assert_eq!(
            resolve_pole(true, Some("pointer_b")),
            Ok(Pole::PointerB),
            "issue 006: 極 B は通る (⚠️ ただし `--features` 以外では上の AC5 が止める)"
        );
        // issue 005: 極 M+ は通る (⚠️ ただし `--features` 以外では上の AC5 が止める)。
        assert_eq!(
            resolve_pole(true, Some("modifier_m_plus")),
            Ok(Pole::ModifierMPlus)
        );

        // AC4: 未知の名前 (丸めない)。
        for name in ["bogus", "", "Baseline", "baseline ", "pointer"] {
            let err = resolve_pole(true, Some(name)).expect_err("未知の名前は Err");
            assert!(err.contains("未知"), "未知と分かる: {err}");
        }
    }

    /// issue 004 AC1 / AC6: 封筒 `config` に極の 3 キーが**常に**出て、`baseline` は
    /// `pole_applicable == true` / `pole_not_applicable_reason == null` になる。
    #[test]
    fn envelope_config_always_carries_the_pole_keys() {
        let resolved = resolve_feature_config(None, &[]).expect("frozen resolves");
        assert_eq!(resolved.stall_onset_config().pole, Pole::Baseline);
        let dto = serde_json::to_value(FeatureConfigDto::from_resolved(
            &resolved, 1, None, None, None,
        ))
        .expect("serialize config");
        for key in ["pole", "pole_applicable", "pole_not_applicable_reason"] {
            assert!(dto.get(key).is_some(), "config.{key} は常に出る");
        }
        assert_eq!(dto["pole"], "baseline");
        assert_eq!(dto["pole_applicable"], true);
        // ★ `null` である (キーが無いのでも空文字でもない)。
        assert!(dto["pole_not_applicable_reason"].is_null());
    }

    /// issue 004: 極は `--set` の 11 値とは別の軸で、`--set` / `--feature-config` から変えられない。
    #[test]
    fn pole_is_not_settable_through_set() {
        assert!(!P1_OPERATIONAL_KEYS.contains(&"pole"));
        for entry in ["pole=pointer_b", "pole=baseline", "pole_applicable=false"] {
            assert!(
                resolve_feature_config(None, &[entry.to_string()]).is_err(),
                "`--set {entry}` は未知のキー"
            );
        }
        // ★ 凍結 JSON へ `pole` を書いても `deny_unknown_fields` が拒む。
        let dir = std::env::temp_dir();
        let path = dir.join(format!(
            "gse-replay-pole-in-config-{}.json",
            std::process::id()
        ));
        let mut v: serde_json::Value =
            serde_json::from_str(FROZEN_P1_EPISODE_JSON).expect("frozen JSON parses");
        v["operational"]["pole"] = serde_json::json!("pointer_b");
        std::fs::write(&path, v.to_string()).expect("write temp config");
        let result = resolve_feature_config(Some(&path), &[]);
        let _ = std::fs::remove_file(&path);
        assert!(result.is_err(), "operational.pole は未知のキー");
    }

    /// ⚠️ 防御の値: 未実装の極を (何かの間違いで) 封筒へ写しても `applicable == true` とは言わない。
    /// 実際には `resolve_pole` が出力の前に止める。
    /// ⚠️ 理由コードは根拠が違うので**極ごとに別の語** (code-reviewer LOW・旧称 `not_implemented` から改名):
    /// 極 B = `pointer_evidence_not_supplied` / 極 M+ = `modifier_evidence_not_supplied`。
    #[test]
    fn unimplemented_pole_never_claims_to_be_applicable() {
        let base = resolve_feature_config(None, &[]).expect("frozen resolves");
        // ★ 極 B は入力 (`with_pointer_evidence`)・極 M+ は修飾キー行数 (`None`) を渡されていないとき、防御の値を出す。
        for (pole, modifier_rows, expected_reason) in [
            (Pole::PointerB, None, "pointer_evidence_not_supplied"),
            (Pole::ModifierMPlus, None, "modifier_evidence_not_supplied"),
        ] {
            let resolved = base.clone().with_pole(pole);
            let dto = serde_json::to_value(FeatureConfigDto::from_resolved(
                &resolved,
                1,
                modifier_rows,
                None,
                None,
            ))
            .expect("serialize config");
            assert_eq!(dto["pole"], pole.as_str());
            assert_eq!(dto["pole_applicable"], false);
            assert_eq!(dto["pole_not_applicable_reason"], expected_reason);
        }
    }

    /// issue 005 AC6: 極 M+ の適用可否は**修飾キーの `key` 行数**で決まる (入力ファイル単位・判断 13)。
    /// ★ 0 本なら `false` ＋ 理由 `no_modifier_rows`、1 本でもあれば `true` ＋ `null`。
    /// ⚠️ 陰性対照: baseline は行数に依らず常に `true`。
    #[test]
    fn modifier_m_plus_applicability_follows_the_modifier_row_count() {
        assert_eq!(
            pole_applicability(Pole::ModifierMPlus, Some(0)),
            (false, Some("no_modifier_rows"))
        );
        assert_eq!(
            pole_applicability(Pole::ModifierMPlus, Some(1)),
            (true, None)
        );
        assert_eq!(
            pole_applicability(Pole::ModifierMPlus, Some(240)),
            (true, None)
        );
        assert_eq!(
            pole_applicability(Pole::ModifierMPlus, None),
            (false, Some("modifier_evidence_not_supplied")),
            "数えていない極 M+ は適用可と名乗らない"
        );
        for rows in [None, Some(0), Some(5)] {
            assert_eq!(pole_applicability(Pole::Baseline, rows), (true, None));
        }
        // ★ 封筒の JSON にも出る (`null` は欠落でも空文字でもない)。
        let base = resolve_feature_config(None, &[]).expect("frozen resolves");
        let resolved = base.with_pole(Pole::ModifierMPlus);
        let no_rows = serde_json::to_value(FeatureConfigDto::from_resolved(
            &resolved,
            1,
            Some(0),
            Some(2),
            Some(3),
        ))
        .expect("serialize config");
        assert_eq!(no_rows["pole"], "modifier_m_plus");
        assert_eq!(no_rows["pole_applicable"], false);
        assert_eq!(no_rows["pole_not_applicable_reason"], "no_modifier_rows");
        let some_rows = serde_json::to_value(FeatureConfigDto::from_resolved(
            &resolved,
            1,
            Some(4),
            Some(5),
            Some(6),
        ))
        .expect("serialize config");
        assert_eq!(some_rows["pole_applicable"], true);
        assert!(some_rows["pole_not_applicable_reason"].is_null());
        // ★ 判断 13: 修飾キーの行数も封筒に刻む (0 でも `null` にしない)。
        assert_eq!(no_rows["pole_modifier_rows"], 0);
        assert_eq!(some_rows["pole_modifier_rows"], 4);
        // ★ 判断 24: 区間の健全性カウンタ（右端打ち切り本数・孤立 release 件数）も封筒に刻む
        // (0 でも `null` にしない・極 M+ で値が入る)。
        assert_eq!(no_rows["pole_modifier_truncated"], 2);
        assert_eq!(no_rows["pole_modifier_orphan_releases"], 3);
        assert_eq!(some_rows["pole_modifier_truncated"], 5);
        assert_eq!(some_rows["pole_modifier_orphan_releases"], 6);
        // ★ 極 M+ 以外では数えないので `null` (★ 渡された値を漏らさない)。
        let base_again = resolve_feature_config(None, &[]).expect("frozen resolves");
        let baseline = serde_json::to_value(FeatureConfigDto::from_resolved(
            &base_again,
            1,
            Some(7),
            Some(8),
            Some(9),
        ))
        .expect("serialize config");
        assert!(baseline["pole_modifier_rows"].is_null());
        assert!(baseline["pole_modifier_truncated"].is_null());
        assert!(baseline["pole_modifier_orphan_releases"].is_null());
    }

    /// issue 006 AC7 ＋ `decisions.md` 判断 26: 極 B の適用可否は 3 状態
    /// (宣言なし / 宣言ありだが 0 行 / 宣言ありで 1 行以上) で決まる。
    /// ★ 理由コードは極 M+ (`no_modifier_rows`) と別の語。⚠️★★★ 2026-09-25 是正: 宣言があっても
    /// 行が 0 本なら**判定不能** (`no_pointer_rows`) —— 「宣言があれば 0 行でも適用可 (所見)」だった
    /// 旧仕様は、宣言はコンパイル時の可否でしかなく実行時の設置失敗と区別できないため裁定で覆った。
    #[test]
    fn pointer_b_applicability_follows_the_capability_declaration() {
        let declared = serde_json::json!({
            "unconditional": ["key"],
            "config_gated": ["focus_transition", "pointer_bin"],
        });
        let other_group = serde_json::json!({ "threshold_gated": ["pointer_bin"] });
        let undeclared = serde_json::json!({
            "unconditional": ["key", "feat"],
            "config_gated": ["focus_transition", "secure_input"],
        });
        assert!(declares_pointer_bin(Some(&declared)));
        assert!(
            declares_pointer_bin(Some(&other_group)),
            "どの群でも宣言は宣言"
        );
        assert!(!declares_pointer_bin(Some(&undeclared)));
        assert!(
            !declares_pointer_bin(None),
            "capabilities が無い旧ログは宣言なし"
        );
        for not_an_object in [
            serde_json::json!("pointer_bin"),
            serde_json::json!(["pointer_bin"]),
        ] {
            assert!(
                !declares_pointer_bin(Some(&not_an_object)),
                "オブジェクトでない capabilities は宣言と読まない"
            );
        }
        // 判断 26: 3 状態 (宣言なし / 宣言ありだが 0 行 / 宣言ありで 1 行以上)。
        assert_eq!(
            pointer_applicability(false, Some(0)),
            (false, Some("no_pointer_capability")),
            "宣言が無ければ行数に関わらず計器が無かった扱い"
        );
        assert_eq!(
            pointer_applicability(false, Some(5)),
            (false, Some("no_pointer_capability")),
            "宣言と行が食い違っていても (壊れたログ) 抑制はしない"
        );
        assert_eq!(
            pointer_applicability(true, Some(0)),
            (false, Some("no_pointer_rows")),
            "判断26: 宣言があっても 0 行は判定不能 (所見として true にはしない)"
        );
        assert_eq!(pointer_applicability(true, Some(1)), (true, None));
        assert_eq!(pointer_applicability(true, Some(240)), (true, None));
        assert_eq!(
            pointer_applicability(true, None),
            (false, Some("pointer_evidence_not_supplied")),
            "証拠 (行数) を渡し忘れても適用可と名乗らない (防御の値)"
        );

        // ★ 封筒の JSON: 宣言あり・0 行 → 判定不能 / 宣言あり・1 行以上 → 適用可 / 宣言なし → 適用不可。
        //   極 B 以外は行数が `null`。
        let base = resolve_feature_config(None, &[]).expect("frozen resolves");
        let dto = |pole: Pole, declared: bool, rows: Option<u64>| {
            serde_json::to_value(
                FeatureConfigDto::from_resolved(&base.clone().with_pole(pole), 1, None, None, None)
                    .with_pointer_evidence(declared, rows),
            )
            .expect("serialize config")
        };
        let idle = dto(Pole::PointerB, true, Some(0));
        assert_eq!(idle["pole"], "pointer_b");
        assert_eq!(
            idle["pole_applicable"], false,
            "判断26: 宣言あり・0 行は判定不能"
        );
        assert_eq!(idle["pole_not_applicable_reason"], "no_pointer_rows");
        assert_eq!(idle["pole_pointer_rows"], 0, "0 行でも null にしない");
        let active = dto(Pole::PointerB, true, Some(2));
        assert_eq!(
            active["pole_applicable"], true,
            "宣言あり・1 行以上は適用可"
        );
        assert!(active["pole_not_applicable_reason"].is_null());
        assert_eq!(active["pole_pointer_rows"], 2);
        let none = dto(Pole::PointerB, false, Some(3));
        assert_eq!(none["pole_applicable"], false);
        assert_eq!(none["pole_not_applicable_reason"], "no_pointer_capability");
        assert_ne!(none["pole_not_applicable_reason"], "no_modifier_rows");
        assert_ne!(none["pole_not_applicable_reason"], "no_pointer_rows");
        assert_eq!(none["pole_pointer_rows"], 3);
        // 極 B 以外では何も足さない (渡された値を漏らさない)。
        for pole in [Pole::Baseline, Pole::ModifierMPlus] {
            let other = dto(pole, false, Some(9));
            assert!(other["pole_pointer_rows"].is_null());
            assert_ne!(other["pole_not_applicable_reason"], "no_pointer_capability");
        }
        // 極 B で証拠を渡し忘れても、適用可とは名乗らない (防御の値)。
        let unset = serde_json::to_value(FeatureConfigDto::from_resolved(
            &base.clone().with_pole(Pole::PointerB),
            1,
            None,
            None,
            None,
        ))
        .expect("serialize config");
        assert_eq!(unset["pole_applicable"], false);
        assert_eq!(
            unset["pole_not_applicable_reason"],
            "pointer_evidence_not_supplied"
        );
        assert!(unset["pole_pointer_rows"].is_null());
    }

    /// 判断 26 の付随確認: `pole_applicable == false` (宣言あり・0 行の判定不能を含む) のとき、
    /// `stall_onset` 列が baseline と恒等であること。★ 値では埋めない (既存の not_applicable の作法)。
    /// ⚠️ これは `pointer_active_ts` の合成側 (main の分岐: 宣言なし/宣言あり0行のどちらも空の
    /// `pointer_ts` を渡す) で保証されている構造的な事実であり、`pointer_suppression_intervals(&[], _)`
    /// が空を返すことから導かれる (回帰させないための固定)。
    #[test]
    fn pointer_b_not_applicable_zero_rows_suppresses_nothing() {
        use gse_next_lib::analysis::feat_offline::stall_onset::{
            evaluation_intervals, pointer_suppression_intervals,
        };
        // 判定不能 (宣言あり・0 行) のとき、main は空の pointer_ts を渡す
        // (`replay.rs` の `pointer_active_ts` 合成: `Some(rows) if pointer_declared` の rows が
        // 空ベクタであっても、抑制区間は必ず空になる)。
        let empty_rows: Vec<u64> = Vec::new();
        let suppressed = pointer_suppression_intervals(&empty_rows, ENGINE_TICK_MS);
        assert!(
            suppressed.is_empty(),
            "0 行からは抑制区間が 1 つも作られない"
        );
        let observed = vec![(0u64, 100_000u64)];
        assert_eq!(
            evaluation_intervals(&observed, &suppressed),
            observed,
            "抑制が空なら評価区間は観測区間そのまま (= baseline と恒等)"
        );
    }

    /// issue 006: `pointer_bin` の collector は**時刻 `t` だけ**を読み、形の合わない行は捨てる (0 に畳まない)。
    /// ★ 他の行種は拾わない・順不同の入力は昇順で返す。
    #[test]
    fn pointer_bin_collector_reads_only_the_timestamp() {
        let path = std::env::temp_dir().join(format!(
            "gse-replay-pointer-bin-collector-{}.ndjson",
            std::process::id()
        ));
        let ndjson = "\
{\"type\":\"pointer_bin\",\"t\":6000,\"moved\":3,\"buttons\":1,\"wheel\":0}\n\
{\"type\":\"pointer_bin\",\"t\":5000}\n\
{\"type\":\"pointer_bin\",\"t\":\"oops\"}\n\
{\"type\":\"pointer_bin\",\"moved\":1}\n\
{\"type\":\"feat\",\"t\":7000}\n\
not json\n";
        std::fs::write(&path, ndjson).expect("write temp session");
        let got = collect_pointer_bin_timestamps(&path);
        let _ = std::fs::remove_file(&path);
        assert_eq!(got, Ok(vec![5_000, 6_000]));
    }

    /// LOW 是正 (code-reviewer): [`PointerBinTimestampDto`] のフィールドが **`t` だけ**であることを
    /// 構造そのもので固定する (将来フィールドが増える回帰を検出する門)。
    /// ★ 余分なフィールドを持つ JSON をデシリアライズしても `t` 以外は保持されず、
    /// 逆シリアライズした serde 出力のキー集合も `["t"]` だけであることを見る。
    #[test]
    fn pointer_bin_timestamp_dto_has_only_the_t_field() {
        let with_extra: PointerBinTimestampDto =
            serde_json::from_str(r#"{"t":6000,"moved":3,"buttons":1,"wheel":0}"#)
                .expect("extra fields are ignored, not an error");
        assert_eq!(with_extra.t, 6_000);
        let value = serde_json::to_value(&with_extra).expect("serialize back");
        let obj = value.as_object().expect("dto serializes as a JSON object");
        assert_eq!(
            obj.keys().collect::<Vec<_>>(),
            vec!["t"],
            "PointerBinTimestampDto は t 以外のキーを持たないはず: {obj:?}"
        );
    }

    /// 事前宣言 v1.2 §6.1: 前処理の「入力」は `key` 行 (押下・解放とも・キーを解決できない行も) と
    /// `pointer_bin` 行の時刻だけ。⚠️ `ime_*` / `focus_transition` / `hook_health` / `feat` は拾わない。
    #[test]
    fn idle_trim_input_collector_reads_only_key_and_pointer_rows() {
        let path = std::env::temp_dir().join(format!(
            "gse-replay-idle-trim-input-{}.ndjson",
            std::process::id()
        ));
        let ndjson = "\
{\"type\":\"key\",\"t\":1000,\"vk\":65,\"press\":true}\n\
{\"type\":\"key\",\"t\":1080,\"vk\":65,\"press\":false}\n\
{\"type\":\"key\",\"t\":2000,\"category\":\"no_such_category\",\"press\":true}\n\
{\"type\":\"key\",\"t\":2500}\n\
{\"type\":\"pointer_bin\",\"t\":3000,\"moved\":3,\"buttons\":0,\"wheel\":0}\n\
{\"type\":\"ime_state\",\"t\":4000,\"open\":true}\n\
{\"type\":\"focus_transition\",\"t\":5000}\n\
{\"type\":\"hook_health\",\"t\":6000,\"alive\":false,\"starved_ms\":120000,\"rehook\":true,\"dropped\":0,\"dropped_delta\":0}\n\
{\"type\":\"feat\",\"t\":7000}\n\
{\"type\":\"meta\",\"session_start\":1}\n\
not json\n";
        std::fs::write(&path, ndjson).expect("write temp session");
        let got = collect_idle_trim_input_timestamps(&path);
        let _ = std::fs::remove_file(&path);
        // ★ `press` の無い `key` 行 (2500) も数える (行の種類と時刻だけを読む)。
        assert_eq!(got, Ok(vec![1_000, 1_080, 2_000, 2_500, 3_000]));
    }

    /// fail-closed: 種類が `key` / `pointer_bin` なのに時刻を読めない行があれば `Err`
    /// (入力の時刻が分からないまま削らない・Codex 指摘 2026-10-09)。★ ほかの種類の行の壊れた時刻は無関係 (対照)。
    #[test]
    fn idle_trim_input_collector_refuses_rows_without_a_readable_time() {
        for (tag, bad) in [
            ("ptr-str", "{\"type\":\"pointer_bin\",\"t\":\"oops\"}"),
            ("key-missing", "{\"type\":\"key\",\"press\":true}"),
            ("key-negative", "{\"type\":\"key\",\"t\":-1,\"press\":true}"),
            ("key-float", "{\"type\":\"key\",\"t\":1.5,\"press\":true}"),
        ] {
            let path = std::env::temp_dir().join(format!(
                "gse-replay-idle-trim-input-bad-{}-{tag}.ndjson",
                std::process::id()
            ));
            let ndjson = format!("{{\"type\":\"key\",\"t\":1000,\"press\":true}}\n{bad}\n");
            std::fs::write(&path, ndjson).expect("write temp session");
            let got = collect_idle_trim_input_timestamps(&path);
            let _ = std::fs::remove_file(&path);
            assert!(
                got.is_err(),
                "{tag}: 時刻を読めない入力行は Err でなければならない: {got:?}"
            );
        }
        let path = std::env::temp_dir().join(format!(
            "gse-replay-idle-trim-input-other-{}.ndjson",
            std::process::id()
        ));
        std::fs::write(
            &path,
            "{\"type\":\"key\",\"t\":1000,\"press\":true}\n{\"type\":\"ime_state\",\"t\":\"oops\"}\n",
        )
        .expect("write temp session");
        let got = collect_idle_trim_input_timestamps(&path);
        let _ = std::fs::remove_file(&path);
        assert_eq!(got, Ok(vec![1_000]));
    }

    /// 事前宣言 v1.2 §6.4: `--set idle_trim_max_ms=0` (前処理なしの実行) は凍結値から外れたキーとして
    /// `overrides` に残る。★ 凍結値と同じ `--set` は載らない (対照)。
    #[test]
    fn set_idle_trim_max_zero_is_recorded_as_an_override() {
        let resolved = resolve_feature_config(None, &["idle_trim_max_ms=0".to_string()])
            .expect("idle_trim_max_ms=0 resolves");
        assert_eq!(resolved.operational.idle_trim_max_ms, 0);
        assert_eq!(resolved.overrides.len(), 1);
        assert_eq!(resolved.overrides[0].key, "idle_trim_max_ms");
        assert_eq!(resolved.overrides[0].frozen, serde_json::json!(1_800_000));
        assert_eq!(resolved.overrides[0].value, serde_json::json!(0));

        let same = resolve_feature_config(None, &["idle_trim_max_ms=1800000".to_string()])
            .expect("frozen value resolves");
        assert!(same.overrides.is_empty());
    }

    /// 事前宣言 v1.2 §6.1 の検査: `idle_trim_min_gap_ms > hole_gap_ms`・`idle_trim_max_ms <= 24 時間`。
    /// ★ 境界ちょうどの陽性対照を先に置く。
    #[test]
    fn idle_trim_values_are_range_checked() {
        for ok in [
            vec!["idle_trim_min_gap_ms=2001"],
            vec!["idle_trim_max_ms=86400000"],
            // ★ v1.3: `idle_trim_input_gap_ms` は `idle_trim_min_gap_ms` 以上なので、長い穴を 30 分より長くするなら一緒に動かす。
            vec![
                "idle_trim_min_gap_ms=86400000",
                "idle_trim_input_gap_ms=86400000",
            ],
            vec!["hole_gap_ms=5000", "idle_trim_min_gap_ms=5001"],
        ] {
            let sets: Vec<String> = ok.iter().map(|s| s.to_string()).collect();
            assert!(
                resolve_feature_config(None, &sets).is_ok(),
                "{ok:?} は通らなければならない"
            );
        }
        for bad in [
            vec!["idle_trim_min_gap_ms=2000"], // = hole_gap_ms
            vec!["idle_trim_min_gap_ms=0"],    // < hole_gap_ms
            vec!["hole_gap_ms=60000"],         // 凍結の 60000 と等しくなる
            vec!["idle_trim_max_ms=86400001"], // 24 時間超
            // ⚠️ `idle_trim_input_gap_ms=0` を添える —— 添えないと v1.3 の「長い穴 ≤ 入力の間の閾値」で先に落ち、
            //   24 時間の上限の検査を消しても緑のままになる (code-reviewer M-2)。
            vec!["idle_trim_min_gap_ms=86400001", "idle_trim_input_gap_ms=0"], // 24 時間超
            vec!["idle_trim_max_ms=-1"],                                       // 型の不一致
            vec!["idle_trim_min_gap_ms=60000.5"],                              // 型の不一致
        ] {
            let sets: Vec<String> = bad.iter().map(|s| s.to_string()).collect();
            assert!(
                resolve_feature_config(None, &sets).is_err(),
                "{bad:?} は Err でなければならない"
            );
        }
    }

    /// 事前宣言 v1.3 §7.4: `--set idle_trim_input_gap_ms=0` (長い無入力の前処理なしの実行 = v1.2 の主) は
    /// `overrides` に残る。★ 凍結値と同じ `--set` は載らない (対照)。
    #[test]
    fn set_idle_trim_input_gap_zero_is_recorded_as_an_override() {
        let resolved = resolve_feature_config(None, &["idle_trim_input_gap_ms=0".to_string()])
            .expect("idle_trim_input_gap_ms=0 resolves");
        assert_eq!(resolved.operational.idle_trim_input_gap_ms, 0);
        assert_eq!(resolved.overrides.len(), 1);
        assert_eq!(resolved.overrides[0].key, "idle_trim_input_gap_ms");
        assert_eq!(resolved.overrides[0].frozen, serde_json::json!(1_800_000));
        assert_eq!(resolved.overrides[0].value, serde_json::json!(0));

        let same = resolve_feature_config(None, &["idle_trim_input_gap_ms=1800000".to_string()])
            .expect("frozen value resolves");
        assert!(same.overrides.is_empty());
    }

    /// 事前宣言 v1.3 §7.1 の検査: `idle_trim_input_gap_ms` は 0 か、`idle_trim_min_gap_ms` 以上 24 時間以下。
    /// ★ 境界ちょうどの陽性対照を先に置く。
    #[test]
    fn idle_trim_input_gap_is_range_checked() {
        for ok in [
            vec!["idle_trim_input_gap_ms=0"],
            vec!["idle_trim_input_gap_ms=60000"], // = idle_trim_min_gap_ms
            vec!["idle_trim_input_gap_ms=86400000"],
        ] {
            let sets: Vec<String> = ok.iter().map(|s| s.to_string()).collect();
            assert!(
                resolve_feature_config(None, &sets).is_ok(),
                "{ok:?} は通らなければならない"
            );
        }
        for bad in [
            vec!["idle_trim_input_gap_ms=1"],        // 0 でなく、長い穴より短い
            vec!["idle_trim_input_gap_ms=59999"],    // 長い穴より 1 ms 短い
            vec!["idle_trim_input_gap_ms=86400001"], // 24 時間超
            vec!["idle_trim_min_gap_ms=1800001"],    // 凍結の 1800000 が長い穴より短くなる
            vec!["idle_trim_input_gap_ms=-1"],       // 型の不一致
        ] {
            let sets: Vec<String> = bad.iter().map(|s| s.to_string()).collect();
            assert!(
                resolve_feature_config(None, &sets).is_err(),
                "{bad:?} は Err でなければならない"
            );
        }
    }

    /// 事前宣言 v1.3: 長い無入力の前処理の値を持たない (1.1.0 の形の) `--feature-config` は `Err`
    /// (前処理を黙って無効にした出力を作らない)。★ 値を足せば通る (対照)。
    #[test]
    fn feature_config_without_idle_trim_input_gap_is_rejected() {
        let dir = envelope_tmp_dir("feature_config_no_input_gap");
        let mut value: serde_json::Value =
            serde_json::from_str(FROZEN_P1_EPISODE_JSON).expect("frozen JSON parses");
        let ok = dir.join("ok.json");
        std::fs::write(&ok, serde_json::to_vec(&value).expect("serialize")).expect("write");
        assert!(resolve_feature_config(Some(&ok), &[]).is_ok());

        value["operational"]
            .as_object_mut()
            .expect("operational is an object")
            .remove("idle_trim_input_gap_ms");
        let old = dir.join("old.json");
        std::fs::write(&old, serde_json::to_vec(&value).expect("serialize")).expect("write");
        assert!(resolve_feature_config(Some(&old), &[]).is_err());
        let _ = std::fs::remove_dir_all(&dir);
    }

    /// 事前宣言 v1.2: 前処理の 2 値を持たない (1.0.0 の形の) `--feature-config` は `Err`
    /// (前処理を黙って無効にした出力を作らない)。★ 2 値を足せば通る (対照)。
    #[test]
    fn feature_config_without_idle_trim_values_is_rejected() {
        let dir = envelope_tmp_dir("feature_config_no_idle_trim");
        let mut value: serde_json::Value =
            serde_json::from_str(FROZEN_P1_EPISODE_JSON).expect("frozen JSON parses");
        let ok = dir.join("ok.json");
        std::fs::write(&ok, serde_json::to_vec(&value).expect("serialize")).expect("write");
        assert!(resolve_feature_config(Some(&ok), &[]).is_ok());

        let ops = value["operational"]
            .as_object_mut()
            .expect("operational is an object");
        ops.remove("idle_trim_min_gap_ms");
        ops.remove("idle_trim_max_ms");
        let old = dir.join("old.json");
        std::fs::write(&old, serde_json::to_vec(&value).expect("serialize")).expect("write");
        assert!(resolve_feature_config(Some(&old), &[]).is_err());
        let _ = std::fs::remove_dir_all(&dir);
    }

    /// issue 005: 修飾キーの edge は press と release の**両方**を、旧ログ (`vk`) と匿名化ログ (`category`) の
    /// **両方の形**から同じ規則で集める。⚠️ 修飾キー以外の行・解決できない行・壊れた行は edge にしない。
    #[test]
    fn modifier_edges_read_both_press_and_release_in_both_log_formats() {
        let ndjson = "\
{\"type\":\"key\",\"t\":100,\"vk\":162,\"press\":true}\n\
{\"type\":\"key\",\"t\":150,\"category\":\"alphabetic\",\"press\":true}\n\
{\"type\":\"key\",\"t\":200,\"vk\":162,\"press\":false}\n\
{\"type\":\"key\",\"t\":300,\"category\":\"modifier\",\"press\":true}\n\
{\"type\":\"key\",\"t\":350,\"category\":\"modifier\",\"press\":false}\n\
{\"type\":\"key\",\"t\":400,\"press\":true}\n\
{\"type\":\"key\",\"t\":410,\"vk\":16,\"press\":true}\n\
not json\n";
        let scanned = read_modifier_edges(ndjson.as_bytes()).expect("reads");
        assert_eq!(
            scanned.edges,
            vec![
                (100, true),
                (200, false),
                (300, true),
                (350, false),
                (410, true)
            ],
            "vk=162 (左 Ctrl)・category=modifier・vk=16 (Shift) が edge。文字キーは edge にしない"
        );
        assert_eq!(
            scanned.unresolved_keys, 1,
            "vk も category も無い行は数えて捨てる"
        );
        assert_eq!(scanned.parse_failed_lines, 1);

        // 修飾キーの行が 0 本の入力（旧形式の文字キーだけ）。
        let plain = "{\"type\":\"key\",\"t\":1,\"vk\":65,\"press\":true}\n\
                     {\"type\":\"key\",\"t\":2,\"vk\":65,\"press\":false}\n";
        assert!(read_modifier_edges(plain.as_bytes())
            .expect("reads")
            .edges
            .is_empty());
    }

    /// ⚠️ `meta` 行が無い / `session_start` を持たない NDJSON でも封筒は落ちない
    /// (旧ログ互換・`hook_health` と同じ作法)。★ 由来が読めないことは、
    /// 特徴行が出せない理由にならない。
    #[test]
    fn meta_facts_are_all_none_when_meta_is_absent() {
        // ⚠️ テストは同一プロセスの複数スレッドで走るので、pid だけだと名前が衝突する
        // (2026-09-20・code-reviewer LOW)。★ テスト名を接尾に入れて分ける。
        let dir = envelope_tmp_dir("meta_absent");
        let path = dir.join("no_meta.ndjson");
        std::fs::write(
            &path,
            "{\"type\":\"key\",\"t\":1,\"vk\":65,\"press\":true}\n\
             {\"type\":\"meta\",\"session_end\":9}\n\
             not json at all\n",
        )
        .expect("write");

        let facts = collect_meta_session_facts(&path).expect("collect meta facts");
        assert!(facts.session_start.is_none());
        assert!(facts.hmm_version.is_none());
        assert!(facts.app_version.is_none());
        assert!(facts.g1_mode.is_none());
        assert!(facts.o1_mode.is_none());
        assert!(facts.keyboard_layout.is_none());
        assert!(facts.capabilities.is_none());

        let _ = std::fs::remove_file(&path);
        let _ = std::fs::remove_dir(&dir);
    }

    /// 封筒用の一時ディレクトリ。★ pid ＋ テスト名で分ける (同一プロセス内の並列実行対策)。
    fn envelope_tmp_dir(tag: &str) -> PathBuf {
        let dir = std::env::temp_dir().join(format!("gse-envelope-{}-{}", std::process::id(), tag));
        std::fs::create_dir_all(&dir).expect("mkdir");
        dir
    }

    /// ⚠️★★★ 回帰 (2026-09-20・code-reviewer MEDIUM): **連結ログで `capabilities` が
    /// 別セグメントから混ざらないこと。**
    ///
    /// ★ 旧実装は `capabilities` を「`capabilities` を持つ最初の `meta` 行」から、
    /// それ以外を「`session_start` を持つ最初の `meta` 行」から取っており、
    /// ⚠️ **同じ行である保証が無かった**。実測では前半の `session_start` / `hmm_version` と
    /// 後半の `capabilities` が封筒に並んだ。★ 封筒は「どの計器条件で取れた行か」を
    /// 保証するために入れたので、これは目的を直撃する。
    #[test]
    fn capabilities_never_come_from_a_different_meta_segment() {
        let dir = envelope_tmp_dir("concat");
        let path = dir.join("concat.ndjson");
        std::fs::write(
            &path,
            "{\"type\":\"meta\",\"session_start\":1700000000000,\"hmm_version\":\"0.2.0\"}\n\
             {\"type\":\"key\",\"t\":1700000000100,\"vk\":65,\"press\":true}\n\
             {\"type\":\"meta\",\"session_end\":1700000001000}\n\
             {\"type\":\"meta\",\"session_start\":1700000002000,\"hmm_version\":\"0.5.0\",\
             \"capabilities\":{\"unconditional\":[\"key\"]}}\n",
        )
        .expect("write");

        let facts = collect_meta_session_facts(&path).expect("collect meta facts");
        assert_eq!(facts.session_start, Some(1_700_000_000_000));
        assert_eq!(facts.hmm_version.as_deref(), Some("0.2.0"));
        assert!(
            facts.capabilities.is_none(),
            "⚠️ 後半セグメントの capabilities が前半の封筒に混ざっている"
        );

        let _ = std::fs::remove_file(&path);
        let _ = std::fs::remove_dir(&dir);
    }

    /// ⚠️★★★ 回帰 (2026-09-20・security-checker M1 / Codex `/cross-review`):
    /// **`meta` の文字列に上限があり、超過は `Err` になる。**
    ///
    /// ★ 信頼境界: O1 の NDJSON は被験者端末で生成されるので、`meta` 行の中身は
    /// **被験者が編集しうる入力**である。⚠️ 上限が無いと、封筒が
    /// (a) 巨大な文字列の複写経路 (b) 自由文が解析成果物に入る唯一の経路 になる。
    ///
    /// ⚠️ **`None` に倒さない** —— 倒すと出力だけを見て「未宣言」と「壊れた長大値」が
    /// 区別できない。★ `capabilities` と同じ規律（「無い」は `None` /「壊れている」は `Err`）。
    #[test]
    fn oversized_meta_strings_are_an_error_not_silently_dropped() {
        let dir = envelope_tmp_dir("longstr");
        let long = "a".repeat(MAX_META_STRING_BYTES + 1);
        let at_limit = "b".repeat(MAX_META_STRING_BYTES);

        // (1) 超過 → Err（★ 理由は出すが、値の中身は出さない）。
        let over = dir.join("over.ndjson");
        std::fs::write(
            &over,
            format!(
                "{{\"type\":\"meta\",\"session_start\":1700000000000,\
                 \"hmm_version\":\"{long}\"}}\n"
            ),
        )
        .expect("write");
        let err = collect_meta_session_facts(&over).expect_err("上限超過は Err のはず");
        assert!(
            err.contains("exceeds limit") && err.contains("hmm_version"),
            "エラー文言が理由とフィールド名を示していない: {err}"
        );
        assert!(!err.contains(&long), "⚠️ エラー文言に値の中身が漏れている");

        // (2) ちょうど上限 → 通る（★ 境界を 1 バイトずらしていないか）。
        let ok_path = dir.join("at_limit.ndjson");
        std::fs::write(
            &ok_path,
            format!(
                "{{\"type\":\"meta\",\"session_start\":1700000000000,\
                 \"app_version\":\"{at_limit}\"}}\n"
            ),
        )
        .expect("write");
        let facts = collect_meta_session_facts(&ok_path).expect("ちょうど上限は Ok のはず");
        assert_eq!(facts.app_version.as_deref(), Some(at_limit.as_str()));
        // ★ 宣言が無いフィールドは `None`（⚠️ 「無い」と「壊れている」を分ける）。
        assert!(facts.hmm_version.is_none());

        let _ = std::fs::remove_file(&over);
        let _ = std::fs::remove_file(&ok_path);
        let _ = std::fs::remove_dir(&dir);
    }

    /// ★ `collect_all_ime_shadow_events` → `build_feature_rows` の**配線**が生きていること
    /// （2026-09-15・`code-reviewer` MEDIUM「新しい配線に `cargo test` 上の網が無い」の回帰）。
    ///
    /// ⚠️ `boundary.rs` の単体テストは `compute_boundary` を直接叩くだけなので、
    /// **`ime_events` 引数を落としても緑のまま**だった。★ ここで NDJSON から通して固定する。
    ///
    /// ★ 併せて、**IME 行がグリッド原点/終端を動かす**ことも固定する
    /// （`build_feature_rows` の doc 参照。⚠️ `config_gated` チャネルの有無で tick 割りが変わる）。
    #[test]
    fn ime_shadow_events_reach_feature_rows_through_the_collector() {
        let base = 1_700_000_000_000_u64;
        // ⚠️ 先頭と末尾を **ime_shadow** にして、グリッドが打鍵より広く張ることを確かめる。
        let ndjson = format!(
            concat!(
                r#"{{"type":"meta","session_start":{0},"hmm_version":"0.2.0"}}"#,
                "
",
                r#"{{"type":"ime_shadow","t":{0},"dwell_ms":400,"nav":2,"abandon":false}}"#,
                "
",
                r#"{{"type":"key","t":{1},"vk":65,"press":true}}"#,
                "
",
                r#"{{"type":"key","t":{2},"vk":65,"press":false}}"#,
                "
",
                r#"{{"type":"ime_shadow","t":{3},"dwell_ms":600,"nav":1,"abandon":true}}"#,
                "
",
            ),
            base,
            base + 1_500,
            base + 1_580,
            base + 2_500,
        );
        let tmp =
            std::env::temp_dir().join(format!("gse_ime_wiring_{}.ndjson", std::process::id()));
        std::fs::write(&tmp, &ndjson).expect("write temp fixture");

        let keys = collect_key_events(&tmp).expect("collect keys");
        let paste_ts = collect_all_paste_timestamps(&tmp).expect("collect pastes");
        let ime = collect_all_ime_shadow_events(&tmp).expect("collect ime_shadow");
        assert_eq!(ime.len(), 2, "ime_shadow 2 行が採れること");

        let stall_onset_inputs = gse_next_lib::analysis::feat_offline::StallOnsetInputs {
            feat_ts: &[],
            task_kind_declarations: &[],
            config: gse_next_lib::analysis::feat_offline::StallOnsetConfig::default(),
        };
        let quality_inputs = gse_next_lib::analysis::feat_offline::QualityInputs {
            capabilities_declared: false,
            hook_health: &[],
        };
        let rows = gse_next_lib::analysis::feat_offline::build_feature_rows(
            &keys,
            &paste_ts,
            &ime,
            MAX_FEATURE_TICKS,
            &stall_onset_inputs,
            &quality_inputs,
        )
        .expect("build rows");

        // ★ 原点は ime_shadow(base)、終端も ime_shadow(base+2500) なので tick は 0..=2 の 3 本。
        assert_eq!(
            rows.len(),
            3,
            "グリッドは ime_shadow の時刻まで張る: {rows:?}"
        );
        assert_eq!(rows[0].t_ms, base, "原点は最初の ime_shadow 行の時刻");

        let dwell: u64 = rows.iter().map(|r| r.boundary.ime_dwell_ms).sum();
        let nav: u64 = rows.iter().map(|r| r.boundary.ime_nav).sum();
        let abandon: u64 = rows.iter().map(|r| r.boundary.ime_abandon).sum();
        assert_eq!(dwell, 1_000, "400 + 600");
        assert_eq!(nav, 3, "2 + 1");
        assert_eq!(abandon, 1, "false + true");

        // ★ tick 帰属も固定する（⚠️ 全部を tick 0 に寄せていないこと）。
        assert_eq!(rows[0].boundary.ime_dwell_ms, 400);
        assert_eq!(rows[2].boundary.ime_dwell_ms, 600);
        let _ = std::fs::remove_file(&tmp);
    }

    /// MEDIUM-4: `collect_all_feat_timestamps` / `collect_task_kind_declarations` →
    /// `build_feature_rows` の**配線**を NDJSON から通して固定する (issue 008)。
    /// `session_meta` の `task_kind` 宣言が onset 行の `task_kind` まで届くこと。
    #[test]
    fn task_kind_declaration_reaches_stall_onset_through_the_collectors() {
        let base = 1_700_000_000_000_u64;
        let mut ndjson = format!(
            concat!(
                "{{\"type\":\"meta\",\"session_start\":{0},\"hmm_version\":\"0.5.0\"}}\n",
                "{{\"type\":\"session_meta\",\"track\":\"main\",\"task_kind\":\"argumentative\",\
                 \"intervention_enabled\":false,\"ts\":{0}}}\n",
                "{{\"type\":\"key\",\"t\":{0},\"vk\":65,\"press\":true}}\n",
                "{{\"type\":\"key\",\"t\":{1},\"vk\":65,\"press\":true}}\n",
                "{{\"type\":\"key\",\"t\":{2},\"vk\":65,\"press\":true}}\n",
            ),
            base,
            base + 100,
            base + 200,
        );
        // feat 行: base..=base+31000 を 1000ms 刻み (小さな立ち上がりを観測区間に収める)。
        let mut t = base;
        while t <= base + 31_000 {
            ndjson.push_str(&format!("{{\"type\":\"feat\",\"t\":{t}}}\n"));
            t += 1_000;
        }

        let tmp = std::env::temp_dir().join(format!(
            "gse_task_kind_wiring_{}.ndjson",
            std::process::id()
        ));
        std::fs::write(&tmp, &ndjson).expect("write temp fixture");

        let keys = collect_key_events(&tmp).expect("collect keys");
        let feat_ts = collect_all_feat_timestamps(&tmp).expect("collect feat timestamps");
        let task_kind_declarations =
            collect_task_kind_declarations(&tmp).expect("collect task_kind declarations");
        assert_eq!(
            task_kind_declarations,
            vec![(base, "argumentative".to_string())]
        );

        let stall_onset_inputs = gse_next_lib::analysis::feat_offline::StallOnsetInputs {
            feat_ts: &feat_ts,
            task_kind_declarations: &task_kind_declarations,
            config: gse_next_lib::analysis::feat_offline::StallOnsetConfig::default(),
        };
        let quality_inputs = gse_next_lib::analysis::feat_offline::QualityInputs {
            capabilities_declared: false,
            hook_health: &[],
        };
        let rows = gse_next_lib::analysis::feat_offline::build_feature_rows(
            &keys,
            &[],
            &[],
            MAX_FEATURE_TICKS,
            &stall_onset_inputs,
            &quality_inputs,
        )
        .expect("build rows");

        let onset_row = rows
            .iter()
            .find(|r| r.stall_onset.is_onset)
            .expect("onset should fire through the wired collectors");
        assert_eq!(
            onset_row.stall_onset.task_kind,
            Some("argumentative".to_string()),
            "collect_task_kind_declarations → build_feature_rows の配線で \
             宣言値が onset 行に届くこと"
        );
        let _ = std::fs::remove_file(&tmp);
    }

    /// LOW-5: 未知の `task_kind` は `logger::TaskKind::parse` の SSOT を通し、`None` になる
    /// 値は宣言として採らない (= 未宣言扱いで back-off。値は出力しない)。
    #[test]
    fn unknown_task_kind_is_not_emitted() {
        let ndjson = concat!(
            "{\"type\":\"meta\",\"session_start\":1700000000000,\"hmm_version\":\"0.5.0\"}\n",
            "{\"type\":\"session_meta\",\"track\":\"main\",\
             \"task_kind\":\"underwater_basket_weaving\",\"intervention_enabled\":false,\
             \"ts\":1700000000000}\n",
            "{\"type\":\"session_meta\",\"track\":\"main\",\"task_kind\":\"vibe_coding\",\
             \"intervention_enabled\":false,\"ts\":1700000001000}\n",
        );
        let tmp = std::env::temp_dir().join(format!(
            "gse_unknown_task_kind_{}.ndjson",
            std::process::id()
        ));
        std::fs::write(&tmp, ndjson).expect("write temp fixture");

        let declarations = collect_task_kind_declarations(&tmp)
            .expect("collect must not fail on unknown task_kind");
        assert_eq!(
            declarations,
            vec![(1_700_000_001_000, "vibe_coding".to_string())],
            "未知の task_kind (\"underwater_basket_weaving\") は宣言として採らず、\
             既知の宣言だけが残るはず"
        );
        let _ = std::fs::remove_file(&tmp);
    }

    /// ⚠️★★★ **`activity_label` 行が `run_replay` を落とさない**（ADR-031 D1）。
    ///
    /// ★ 2026-09-14 に足し忘れて実測で踏んだ失敗様式の回帰である
    /// （逐語 `unknown variant 'activity_label'` で `--snapshot` が丸ごと落ちた）。
    /// ⚠️ **ゴールデンが緑でも検出できない**ので、**行を足して通す**形でなければ意味がない。
    #[test]
    fn activity_label_line_is_skipped_by_run_replay() {
        let line = r#"{"type":"activity_label","t":120000,"probe_id":"p-1","category":"conversation","answered":true,"latency_ms":120}"#;
        let ev: ReplayEvent = serde_json::from_str(line).expect("parse activity_label");
        assert!(
            matches!(ev, ReplayEvent::ActivityLabel(_)),
            "expected ReplayEvent::ActivityLabel, got {ev:?}"
        );
        assert_eq!(
            ev.timestamp(),
            None,
            "activity_label は時刻順ソートから除外する"
        );

        let mut ndjson =
            std::fs::read_to_string(fixture_path("minimal.ndjson")).expect("read minimal fixture");
        ndjson.push_str(line);
        ndjson.push('\n');
        let tmp = std::env::temp_dir().join(format!(
            "gse_activity_label_replay_{}.ndjson",
            std::process::id()
        ));
        std::fs::write(&tmp, &ndjson).expect("write temp fixture");

        let with_line = run_replay(&tmp).expect("run_replay must accept activity_label lines");
        let baseline = run_replay(&fixture_path("minimal.ndjson")).expect("baseline replay");
        assert_eq!(
            with_line.len(),
            baseline.len(),
            "activity_label 行は FeatSnapshot 列を 1 件も変えてはならない"
        );
        let _ = std::fs::remove_file(&tmp);
    }

    /// ⚠️★★★ **3 度目を止める**: `KNOWN_LINE_TYPES` の全行種が `ReplayEvent` で受理できること。
    ///
    /// ★ `hook_health`（2026-08-09）と `activity_label`（2026-09-14）で **同じ失敗を 2 回**踏んだ。
    /// ⚠️ どちらも「新しい行種を足したのに `replay.rs` へ足し忘れる」形で、
    /// **ゴールデンが緑のまま**すり抜けた。→ ★ **宣言側から機械的に当てる。**
    ///
    /// ⚠️ 本テストは「**タグを受理できるか**」だけを見る（★ 中身の妥当性は各行種のテストが見る）。
    /// ★ `meta` は `session_start` / `session_end` の 2 形状があるので代表を 1 つ置く。
    #[test]
    fn every_known_line_type_is_accepted_by_replay_event() {
        // ★ 行種ごとの**最小の代表行**。⚠️ 新しい行種を足したらここにも足す
        //   （足さないと下の網羅チェックが赤になるので、忘れられない）。
        let samples: &[(&str, &str)] = &[
            (
                "meta",
                r#"{"type":"meta","session_start":1,"hmm_version":"0.5.0"}"#,
            ),
            ("session_start", r#"{"type":"session_start","t":1}"#),
            (
                "key",
                r#"{"type":"key","t":1,"category":"alphabetic","press":true}"#,
            ),
            (
                "paste",
                r#"{"type":"paste","t":1,"external_paste_chars":3}"#,
            ),
            (
                "feat",
                r#"{"type":"feat","t":1,"f1":0.0,"f3":0.0,"f4":0.0,"f5":0.0,"f6":0.0,"p_flow":0.0,"p_inc":0.0,"p_stuck":0.0,"raw_x":0.0,"raw_y":0.0,"ewma_x":0.0,"ewma_y":0.0,"obs":0,"alpha":0.0,"keys":0,"bs_keys":0}"#,
            ),
            (
                "ime_state",
                r#"{"type":"ime_state","t":1,"on":false,"active":false}"#,
            ),
            (
                "ime_shadow",
                r#"{"type":"ime_shadow","t":1,"dwell_ms":0,"nav":0,"abandon":false}"#,
            ),
            (
                "hook_health",
                r#"{"type":"hook_health","t":1,"alive":true,"starved_ms":0,"rehook":false,"dropped":0,"dropped_delta":0}"#,
            ),
            (
                "starve_window",
                r#"{"type":"starve_window","t":1,"win_ms":1,"n_lt30":0,"sum_lt30_ms":0}"#,
            ),
            (
                "user_label",
                r#"{"type":"user_label","t":1,"label":"stuck","recovered_at":null}"#,
            ),
            ("review_marker", r#"{"type":"review_marker","t":1}"#),
            (
                "session_meta",
                r#"{"type":"session_meta","track":"main","task_kind":"writing","intervention_enabled":false,"condition":null,"label_pool":null,"head_id":"writing","ts":1}"#,
            ),
            (
                "probe_assignment",
                r#"{"type":"probe_assignment","probe_id":"p","scheduled_ts":1,"session_elapsed_ms":1,"stratum":"random"}"#,
            ),
            (
                "realtime_label",
                r#"{"type":"realtime_label","probe_id":"p","source":"random_probe","q1_friction":3,"q2_progress":3,"answered":true,"skip_reason":"none","latency_ms":1,"analysis_window_start_ms":0,"analysis_window_end_ms":0,"ts":1}"#,
            ),
            (
                "vignette_response",
                r#"{"type":"vignette_response","vignette_id":"v","expected_quadrant":"flow","q1_friction":3,"q2_progress":3,"elapsed_ms":1,"changes":0,"ts":1}"#,
            ),
            (
                "activity_label",
                r#"{"type":"activity_label","t":1,"probe_id":null,"category":"away","answered":true,"latency_ms":1}"#,
            ),
            (
                "intervention_decision",
                r#"{"type":"intervention_decision","t":1,"action":"none","need_score":0.0,"opportunity_score":0.0,"p_stuck":0.0,"idle_ms":0,"reason":"x","suppressed_by":null}"#,
            ),
            (
                "intervention_response",
                r#"{"type":"intervention_response","t":1,"action":"nudge","reason":"silent"}"#,
            ),
            (
                "recording_pause",
                r#"{"type":"recording_pause","t":1,"paused":true}"#,
            ),
            ("focus_transition", r#"{"type":"focus_transition","t":1}"#),
            (
                "pointer_bin",
                r#"{"type":"pointer_bin","t":1,"moved":0,"buttons":0,"wheel":0}"#,
            ),
            ("secure_input", r#"{"type":"secure_input","t":1,"on":true}"#),
        ];

        // ★ (1) 代表行がすべて deserialize できること。
        for (name, line) in samples {
            serde_json::from_str::<ReplayEvent>(line).unwrap_or_else(|e| {
                panic!(
                    "{name} が ReplayEvent で受理できない: {e}
★ replay.rs に variant を足すこと (Replay-as-Truth が切れる)"
                )
            });
        }

        // ★ (2) ⚠️ 宣言側 (`KNOWN_LINE_TYPES`) に対して**取りこぼしが無い**こと。
        //   → ★ これが「足し忘れ」を止める本体である。
        let covered: std::collections::BTreeSet<&str> = samples.iter().map(|(n, _)| *n).collect();
        let missing: Vec<&str> = gse_next_lib::capabilities::KNOWN_LINE_TYPES
            .iter()
            .copied()
            .filter(|t| !covered.contains(t))
            .collect();
        assert!(
            missing.is_empty(),
            "KNOWN_LINE_TYPES にあるのに replay の受理検査から漏れている行種: {missing:?}"
        );
    }

    /// `intervention_response` 行 (Phase A2 の Wall 応答 + 旧 Nudge dismiss) が deserialize でき、
    /// `timestamp()==None` で snapshot 再実行のソートから除外されることを確認する。
    /// `ReplayEvent::InterventionResponse(Value)` の catch-all により、新 reason 値
    /// (early_unlock/completed/idle_timeout) や新フィールド (elapsed_ms) を後方互換で受理する。
    #[test]
    fn intervention_response_parses_and_is_skipped_from_replay() {
        // 旧形式 (Nudge dismiss): elapsed_ms 欠落・既存 reason。
        let legacy =
            r#"{"type":"intervention_response","t":1500,"action":"nudge","reason":"not_stuck"}"#;
        let ev: ReplayEvent =
            serde_json::from_str(legacy).expect("parse legacy intervention_response");
        assert!(
            matches!(ev, ReplayEvent::InterventionResponse(_)),
            "expected ReplayEvent::InterventionResponse, got {ev:?}"
        );
        assert_eq!(ev.timestamp(), None, "intervention_response は除外する");

        // 新形式 (Wall 早期解除): action=wall・新 reason・elapsed_ms あり。
        let wall = r#"{"type":"intervention_response","t":67890,"action":"wall","reason":"early_unlock","elapsed_ms":45000}"#;
        let ev: ReplayEvent = serde_json::from_str(wall).expect("parse wall intervention_response");
        assert!(
            matches!(ev, ReplayEvent::InterventionResponse(_)),
            "expected ReplayEvent::InterventionResponse, got {ev:?}"
        );
        assert_eq!(ev.timestamp(), None);
    }

    /// 層 2: 合成 NDJSON fixture で `collect_logged_feats` +
    /// `compute_session_metrics` のパスを通す。warnings 空 + flow support=1 を
    /// 期待する (label と feat が ±100ms で揃っている設計)。
    #[test]
    fn collect_logged_feats_plus_metrics_matches_minimal_fixture() {
        let path = fixture_path("phase1_minimal.ndjson");
        let labels = collect_user_labels(&path).expect("collect_user_labels");
        let feats = collect_logged_feats(&path).expect("collect_logged_feats");
        assert_eq!(feats.len(), 3, "minimal fixture has 3 feat lines");
        assert_eq!(labels.len(), 1, "minimal fixture has 1 user_label line");
        let m = compute_session_metrics(&labels, &feats);
        assert_eq!(m.total_labels, 1);
        assert!(
            m.warnings.is_empty(),
            "warnings should be empty on aligned fixture, got {:?}",
            m.warnings
        );
        // Flow label @t=2100 の最近傍 feat @t=2000 で p_flow=0.88 → argmax flow → tp=1
        let flow_metrics = m
            .per_class
            .iter()
            .find(|c| c.class == LabelClass::Flow)
            .expect("flow per_class");
        assert_eq!(flow_metrics.support, 1);
    }

    /// 層 3 (実データ回帰): key 行を除去した real fixture で alignment を確認する。
    /// 元 `gse_20260415_144120.ndjson` は 6 labels × 96 feat (wall-clock 1Hz)。
    /// 全ラベルが ±500ms 以内に feat を持つため warnings は **0 (第一 assert)** が
    /// 期待。将来 regen 経路に戻る / IME auto-reset semantics が再度ずれる regression
    /// があれば warnings > 0 で落ちる。
    /// - fix 前 (regen): warnings=6 / matched=0
    /// - fix 後 (logged): warnings=0 / matched=6 (Phase D-2 実測、2026-04-16)
    ///
    /// matched 閾値は 6 件全マッチを要件に格上げ (code-reviewer M5 対応)。
    #[test]
    fn real_ime_heavy_fixture_warnings_minimal_and_matches_most_labels() {
        const EXPECTED_LABELS: usize = 6;
        const EXPECTED_MIN_FEATS: usize = 90; // 元 96 件、fixture 切り出しで微減許容
        const EXPECTED_MATCHED_LABELS: u32 = 6; // 全 label が ±1000ms 内に logged feat を持つ

        let path = fixture_path("phase1_ime_heavy.ndjson");
        let labels = collect_user_labels(&path).expect("collect_user_labels");
        let feats = collect_logged_feats(&path).expect("collect_logged_feats");
        assert_eq!(labels.len(), EXPECTED_LABELS);
        assert!(
            feats.len() >= EXPECTED_MIN_FEATS,
            "expected ~96 logged feats, got {}",
            feats.len()
        );
        let m = compute_session_metrics(&labels, &feats);
        assert_eq!(m.total_labels, EXPECTED_LABELS as u32);
        // 第一 assert: warnings 0 (alignment 完全成立が要件)
        assert!(
            m.warnings.is_empty(),
            "expected warnings == 0 on aligned real fixture (regression would indicate \
             regen feat path re-introduced or IME pause semantics changed), got {}: {:?}",
            m.warnings.len(),
            m.warnings
        );
        let matched: u32 = m.confusion.matrix.iter().flatten().sum();
        assert_eq!(
            matched, EXPECTED_MATCHED_LABELS,
            "expected all {} labels matched into confusion matrix, got {}",
            EXPECTED_MATCHED_LABELS, matched
        );
    }

    /// 層 1 拡張 (M2 対応): `schema_dto::LogEntryDto::Feat` が生成する JSON を
    /// `LoggedFeatDto` で受けて round-trip する。両者のフィールド定義が drift
    /// したら serde が落とす or 無視で値が 0 になるため CI で検知できる。
    /// (obs: schema_dto は u64 / LoggedFeatDto は usize で型差あり。serde_json は
    /// u64 → usize の範囲内変換を許すため実用上問題ない点も同時に担保)。
    #[test]
    fn logged_feat_dto_round_trips_schema_dto_feat_shape() {
        use gse_next_lib::schema_dto::LogEntryDto;
        let src = LogEntryDto::Feat {
            t: 1_700_000_042_000,
            f1: 120.5,
            f3: 0.125,
            f4: 7.0,
            f5: 2.5,
            f6: 0.333,
            p_flow: 0.6,
            p_inc: 0.25,
            p_stuck: 0.15,
            raw_x: 0.1,
            raw_y: 0.8,
            ewma_x: 0.05,
            ewma_y: 0.7,
            obs: 11,
            alpha: 0.2,
            keys: Some(48),
            bs_keys: Some(6),
        };
        let json = serde_json::to_string(&src).expect("serialize LogEntryDto::Feat");
        let ev: ReplayEvent =
            serde_json::from_str(&json).expect("parse as ReplayEvent (type=feat)");
        let val = match ev {
            ReplayEvent::Feat(v) => v,
            _ => panic!(
                "expected ReplayEvent::Feat from schema_dto::LogEntryDto::Feat, json = {}",
                json
            ),
        };
        let dto: LoggedFeatDto = serde_json::from_value(val).expect("LoggedFeatDto from_value");
        let feat: FeatSnapshot = dto.try_into().expect("valid schema_dto converts");
        assert_eq!(feat.timestamp, 1_700_000_042_000);
        assert!((feat.f1 - 120.5).abs() < 1e-9);
        assert!((feat.p_flow - 0.6).abs() < 1e-9);
        assert_eq!(feat.obs, 11);
        assert!((feat.alpha - 0.2).abs() < 1e-9);
        // ★ Tier 0: schema_dto ↔ LoggedFeatDto ↔ FeatSnapshot の 3 者で drift しないこと。
        assert_eq!(feat.keys, 48);
        assert_eq!(feat.bs_keys, 6);
    }

    /// ★ Tier 0 後方互換: **新フィールドを持たない旧 NDJSON** の feat 行が読めること。
    /// 読めなくなると `--metrics` 経路が既存 gse-dataset の全ログで落ちる。
    #[test]
    fn logged_feat_dto_accepts_legacy_line_without_tier0_fields() {
        let legacy = r#"{"type":"feat","t":1700000001000,"f1":140.0,"f3":0.0,"f4":4.0,"f5":0.0,"f6":0.0,"p_flow":0.85,"p_inc":0.10,"p_stuck":0.05,"raw_x":0.0,"raw_y":0.6,"ewma_x":0.07,"ewma_y":0.74,"obs":3,"alpha":0.3}"#;
        let val: serde_json::Value = serde_json::from_str(legacy).expect("parse legacy feat line");
        let dto: LoggedFeatDto = serde_json::from_value(val).expect("legacy line must still parse");
        assert!(dto.keys.is_none());
        assert!(dto.bs_keys.is_none());
        let feat: FeatSnapshot = dto.try_into().expect("legacy line converts");
        // ⚠️ 欠測は 0 に倒れる。「実測 0 打」と区別できない点は LoggedFeatDto の doc を参照。
        assert_eq!(feat.keys, 0);
        assert_eq!(feat.bs_keys, 0);
    }

    /// ★ Tier 0: 片方だけ欠けた行も落とさずに読む (forward/backward 互換)。
    #[test]
    fn logged_feat_dto_accepts_partially_missing_tier0_fields() {
        let mut dto = valid_dto();
        dto.bs_keys = None;
        let feat: FeatSnapshot = dto.try_into().expect("keys only must convert");
        assert_eq!(feat.keys, 21);
        assert_eq!(feat.bs_keys, 0);

        let mut dto = valid_dto();
        dto.keys = None; // keys 欠測 → 0。bs_keys=2 > 0 なので不変条件で reject される
        let err = FeatSnapshot::try_from(dto).expect_err("bs_keys > keys must be rejected");
        assert!(
            err.contains("bs_keys exceeds keys"),
            "unexpected error: {}",
            err
        );
    }

    /// ★ Tier 0: `bs_keys > keys` は producer では起こり得ない。壊れた行は入力側で止める。
    /// ⚠️ 通すと将来の `progress_proxy = keys − bs_keys` が u64 underflow する。
    #[test]
    fn bs_keys_greater_than_keys_rejected() {
        let mut dto = valid_dto();
        dto.keys = Some(3);
        dto.bs_keys = Some(4);
        let err = FeatSnapshot::try_from(dto).expect_err("must reject bs_keys > keys");
        assert!(
            err.contains("bs_keys exceeds keys"),
            "unexpected error: {}",
            err
        );

        // 境界: 等しい場合は正常 (全打鍵が BS のウィンドウは実在しうる)
        let mut dto = valid_dto();
        dto.keys = Some(4);
        dto.bs_keys = Some(4);
        let feat: FeatSnapshot = dto.try_into().expect("bs_keys == keys is valid");
        assert_eq!(feat.keys - feat.bs_keys, 0);
    }

    // =========================================================================
    // M3: TryFrom validation tests (security-checker MEDIUM)
    // =========================================================================

    /// Helper: 合法な LoggedFeatDto を返す。各テストで異常値だけ差し替える。
    fn valid_dto() -> LoggedFeatDto {
        LoggedFeatDto {
            timestamp: 1_700_000_000_000,
            f1: 140.0,
            f3: 0.0,
            f4: 4.0,
            f5: 0.0,
            f6: 0.0,
            p_flow: 0.85,
            p_inc: 0.10,
            p_stuck: 0.05,
            raw_x: 0.0,
            raw_y: 0.6,
            ewma_x: 0.07,
            ewma_y: 0.74,
            obs: 3,
            alpha: 0.3,
            keys: Some(21),
            bs_keys: Some(2),
        }
    }

    /// M3: NaN が確率フィールドに入った場合は Err で reject。
    /// `argmax_class` が NaN で silent に Stuck を選ぶ問題を入力側で止める。
    #[test]
    fn nan_probability_rejected() {
        let mut dto = valid_dto();
        dto.p_flow = f64::NAN;
        let err = FeatSnapshot::try_from(dto).expect_err("NaN must be rejected");
        assert!(
            err.contains("p_flow") && err.contains("not finite"),
            "error should mention field + not finite: {}",
            err
        );
    }

    /// M3: Inf が特徴量に入った場合は Err で reject。
    #[test]
    fn inf_feature_rejected() {
        let mut dto = valid_dto();
        dto.f4 = f64::INFINITY;
        let err = FeatSnapshot::try_from(dto).expect_err("Inf must be rejected");
        assert!(
            err.contains("f4") && err.contains("not finite"),
            "error should mention f4 + not finite: {}",
            err
        );
    }

    /// M3: 確率和が許容範囲 [0.98, 1.02] を外れた場合は Err。
    /// 4 桁丸め誤差 (logger の {:.4}) は許容、本質的な壊れ値のみ reject。
    #[test]
    fn prob_sum_out_of_range_rejected() {
        let mut dto = valid_dto();
        // 和が 1.5 になる壊れ値 (明確に範囲外)
        dto.p_flow = 0.5;
        dto.p_inc = 0.5;
        dto.p_stuck = 0.5;
        let err = FeatSnapshot::try_from(dto).expect_err("sum=1.5 must be rejected");
        assert!(
            err.contains("probability sum") && err.contains("1.5"),
            "error should mention probability sum: {}",
            err
        );
    }

    /// M3: alpha が `[0, 1]` を外れた場合は Err。
    #[test]
    fn alpha_out_of_range_rejected() {
        let mut dto = valid_dto();
        dto.alpha = 1.5;
        let err = FeatSnapshot::try_from(dto).expect_err("alpha=1.5 must be rejected");
        assert!(
            err.contains("alpha") && err.contains("1.5"),
            "error should mention alpha out of range: {}",
            err
        );
    }

    /// M3: 丸め誤差レベル (sum=0.99 等) は許容される (回帰保護)。
    #[test]
    fn rounding_error_tolerated() {
        let mut dto = valid_dto();
        // logger の {:.4} で端数が 0.9999 や 1.0001 になるケースを許容
        dto.p_flow = 0.8499;
        dto.p_inc = 0.1000;
        dto.p_stuck = 0.0500;
        // sum = 0.9999 → [0.98, 1.02] 内、通るべき
        let feat = FeatSnapshot::try_from(dto).expect("rounding-level sum must be tolerated");
        assert!((feat.p_flow - 0.8499).abs() < 1e-9);
    }

    // =========================================================================
    // Task D: --calibration 抽出経路の統合テスト (合成 NDJSON fixture)
    // =========================================================================

    /// `load_calibration_session` が新 4 type を正しく抽出することを確認する。
    #[test]
    fn load_calibration_session_extracts_new_variants() {
        let s3 = load_calibration_session(&fixture_path("calib_subject_s3_eval.ndjson"))
            .expect("load s3");
        assert_eq!(s3.track, TrackKind::Main);
        assert_eq!(s3.probes.len(), 3, "s3 has 3 realtime_label probes");
        assert_eq!(
            s3.random_probe_assignment_count, 3,
            "s3 has 3 probe_assignment audit records"
        );
        assert!(s3.vignettes.is_empty(), "s3 has no vignettes");
        assert_eq!(s3.feats.len(), 6, "s3 has 6 feat lines");
        // 全 probe が random_probe・回答済み。
        assert!(s3
            .probes
            .iter()
            .all(|p| p.source == ProbeSourceKind::RandomProbe && p.answered));

        let s1 =
            load_calibration_session(&fixture_path("calib_subject_s1.ndjson")).expect("load s1");
        assert_eq!(s1.vignettes.len(), 8, "s1 carries the 8 vignettes");
        assert_eq!(s1.probes.len(), 1);
    }

    /// 3 セッション (s1/s2 = 較正・s3 = 評価) を `--calibration` 相当で通し、
    /// 抽出 → 窓集約 → 被験者内 C-index → holdout → ビネット採点を end-to-end 検証する。
    /// s3 は X(ewma) を q1 に単調対応させてあり C-index = 1.0 になる (決定論)。
    #[test]
    fn calibration_pipeline_end_to_end_strong_concordance() {
        let sessions = vec![
            load_calibration_session(&fixture_path("calib_subject_s1.ndjson")).unwrap(),
            load_calibration_session(&fixture_path("calib_subject_s2.ndjson")).unwrap(),
            load_calibration_session(&fixture_path("calib_subject_s3_eval.ndjson")).unwrap(),
        ];
        let report = compute_calibration_metrics(&sessions, AggSpec::default());

        // holdout: 先頭 2 (s1/s2) = 較正、s3 = 評価。
        assert_eq!(report.main_session_count, 3);
        assert_eq!(report.calibration_session_count, 2);
        assert_eq!(report.evaluation_session_count, 1);

        // 評価セッション s3 の X↔Q1: ewma_x=(0.1,0.5,0.9) ↔ q1=(1,3,5) → 完全一致。
        assert_eq!(report.cindex.x_q1_pooled, Some(1.0));
        // Y↔Q2: ewma_y=(0.9,0.5,0.1) ↔ q2=(5,3,1) → 完全一致。
        assert_eq!(report.cindex.y_q2_pooled, Some(1.0));

        // 測定法: 全 5 random probe (s1:1 + s2:1 + s3:3) が回答済み。
        assert_eq!(report.measurement.random_probe_total, 5);
        assert_eq!(report.measurement.random_probe_answered, 5);
        assert!((report.measurement.answer_rate - 1.0).abs() < 1e-9);

        // ビネット (s1 の 8 問) はすべて想定象限。
        assert_eq!(report.vignette.total, 8);
        assert_eq!(report.vignette.matched, 8);
        assert!(report.vignette.passed);

        // 無回答なし → MNAR 上下限は点推定と一致。
        assert_eq!(report.mnar.point, Some(1.0));
        assert_eq!(report.mnar.lower, Some(1.0));
        assert_eq!(report.mnar.upper, Some(1.0));

        // Recall は withheld。
        assert!(!report.recall.reported);

        // JSON シリアライズが通る (metrics.json 出力経路)。
        let json = serde_json::to_string(&report).expect("serialize CalibrationReport");
        assert!(json.contains("\"schema\":\"calibration/v0.3\""));
    }

    /// exploratory セッションは主指標から除外される (§1.3)。
    #[test]
    fn calibration_excludes_exploratory_track() {
        // s3 を exploratory 扱いにするため、track を書き換えた SessionData を直接合成する。
        let mut s3 =
            load_calibration_session(&fixture_path("calib_subject_s3_eval.ndjson")).unwrap();
        s3.track = TrackKind::Exploratory;
        let sessions = vec![
            load_calibration_session(&fixture_path("calib_subject_s1.ndjson")).unwrap(),
            load_calibration_session(&fixture_path("calib_subject_s2.ndjson")).unwrap(),
            s3,
        ];
        let report = compute_calibration_metrics(&sessions, AggSpec::default());
        assert_eq!(report.exploratory_session_count, 1);
        assert_eq!(report.main_session_count, 2);
        // main は s1/s2 のみ → 両方較正に取られ評価集合は空。
        assert_eq!(report.evaluation_session_count, 0);
        assert_eq!(report.cindex.x_q1_pooled, None);
    }

    // =========================================================================
    // replay-category: 匿名化 NDJSON (key の vk→category) の Replay-as-Truth (D6)
    // =========================================================================
    use gse_next_lib::analysis::anonymize::{anonymize_ndjson, find_session_start, KeyCategory};

    /// `category_representative_vk` は `KeyCategory::from_vk` の正しい逆である。
    /// 全 category について「代表 VK を from_vk に通すと同じ category 文字列へ戻る」ことと、
    /// is_backspace 判定が backspace/delete のみ true になることを検証する。drift 防止の要。
    #[test]
    fn category_representative_vk_roundtrips() {
        let categories = [
            "alphabetic",
            "numeric",
            "punctuation",
            "sentence_punctuation",
            "tab",
            "backspace",
            "delete",
            "space",
            "enter",
            "navigation",
            "modifier",
            "function",
            "escape",
            "other",
        ];
        for cat in categories {
            let vk = category_representative_vk(cat).unwrap_or_else(|| {
                panic!("known category {cat} must resolve to a representative vk")
            });
            // 逆写像の不変条件: from_vk(repr(c)) == c
            assert_eq!(
                KeyCategory::from_vk(vk).as_str(),
                cat,
                "representative vk 0x{vk:02X} for {cat} must re-categorize to {cat}"
            );
            // is_backspace は backspace/delete のみ true
            let expect_bs = cat == "backspace" || cat == "delete";
            assert_eq!(
                is_backspace(vk),
                expect_bs,
                "is_backspace mismatch for category {cat}"
            );
            // is_text_producing 不変条件 (ADR-014 判断 6): text-producing category は
            // alphabetic/numeric/punctuation/tab/space/enter。`other` は厳密に非 text-producing
            // (text-producing な VK は 1 つ残らず上記 6 category のいずれかに入るため)。
            let expect_text = matches!(
                cat,
                "alphabetic"
                    | "numeric"
                    | "punctuation"
                    | "sentence_punctuation"
                    | "tab"
                    | "space"
                    | "enter"
            );
            assert_eq!(
                gse_next_lib::analysis::metrics::is_text_producing(vk),
                expect_text,
                "is_text_producing mismatch for category {cat}"
            );
        }
        // 未知 category は None (forward-compat)
        assert_eq!(category_representative_vk("future_category"), None);
    }

    /// `ReplayEvent::Key` が raw (`vk`) と匿名化 (`category`) の両 JSON 形をデシリアライズし、
    /// `resolve_key_vk` が双方で妥当な VK を返すことを確認する。
    #[test]
    fn replay_event_key_accepts_vk_and_category() {
        // raw 形
        let raw = r#"{"type":"key","t":1700000000200,"vk":72,"press":true}"#;
        match serde_json::from_str::<ReplayEvent>(raw).expect("parse raw key") {
            ReplayEvent::Key {
                t,
                vk,
                category,
                press,
            } => {
                assert_eq!(t, 1_700_000_000_200);
                assert_eq!(vk, Some(72));
                assert_eq!(category, None);
                assert!(press);
                assert_eq!(resolve_key_vk(vk, category.as_deref()), Some(72));
            }
            other => panic!("expected Key, got {other:?}"),
        }

        // 匿名化形 (backspace は is_backspace を保持)
        let anon = r#"{"type":"key","t":1300,"category":"backspace","press":true}"#;
        match serde_json::from_str::<ReplayEvent>(anon).expect("parse anon key") {
            ReplayEvent::Key {
                t,
                vk,
                category,
                press,
            } => {
                assert_eq!(t, 1300);
                assert_eq!(vk, None);
                assert_eq!(category.as_deref(), Some("backspace"));
                assert!(press);
                let resolved = resolve_key_vk(vk, category.as_deref()).expect("resolve category");
                assert!(
                    is_backspace(resolved),
                    "backspace category keeps is_backspace"
                );
            }
            other => panic!("expected Key, got {other:?}"),
        }
    }

    /// FeatSnapshot 列を timestamp を 0 に潰して比較可能にする (相対化で timestamp のみ差が出るため)。
    fn snapshots_without_timestamp(snaps: &[FeatSnapshot]) -> Vec<FeatSnapshot> {
        snaps
            .iter()
            .map(|f| {
                let mut f = f.clone();
                f.timestamp = 0;
                f
            })
            .collect()
    }

    /// **核心テスト (D6 Replay-as-Truth)**: raw を replay した FeatSnapshot と、その raw を
    /// production の `anonymize_ndjson` (= gse-package が適用する変換) で匿名化した NDJSON を
    /// replay した FeatSnapshot が、timestamp を除く全特徴量で一致する。
    ///
    /// 匿名化は絶対 epoch を session_start 相対へ一律オフセットするため timestamp のみ定数分
    /// ずれるが、特徴量はイベント間隔のみに依存するため値は不変。
    #[test]
    fn replay_anonymized_matches_raw_features() {
        let raw_path = fixture_path("minimal.ndjson");
        let raw_snaps = run_replay(&raw_path).expect("replay raw minimal");
        assert!(!raw_snaps.is_empty(), "raw replay must produce snapshots");

        // raw を実 anonymizer で匿名化 (gse-package と同一の変換)。
        let raw_text = std::fs::read_to_string(&raw_path).expect("read raw fixture");
        let session_start = find_session_start(&raw_text).expect("minimal has meta.session_start");
        assert!(
            session_start > 0,
            "session_start offset must be non-trivial"
        );
        let (anon_text, skipped) = anonymize_ndjson(&raw_text, session_start);
        assert_eq!(skipped, 0, "no lines should fail to anonymize");
        assert!(
            !anon_text.contains("\"vk\""),
            "anonymized NDJSON must not contain raw vk"
        );
        assert!(
            anon_text.contains("\"category\""),
            "anonymized NDJSON must carry category"
        );

        // 一時ファイルに書いて replay (run_replay はパス入力)。
        let anon_path =
            std::env::temp_dir().join(format!("gse_replay_anon_{}.ndjson", std::process::id()));
        std::fs::write(&anon_path, &anon_text).expect("write anon temp");
        let anon_snaps = run_replay(&anon_path).expect("replay anonymized minimal");
        let _ = std::fs::remove_file(&anon_path);
        assert!(
            !anon_snaps.is_empty(),
            "anonymized replay must produce snapshots"
        );

        // 特徴量値が一致 (timestamp は相対化で異なるため除外)。
        assert_eq!(
            snapshots_without_timestamp(&raw_snaps),
            snapshots_without_timestamp(&anon_snaps),
            "anonymized replay must reproduce raw feature values (D6 Replay-as-Truth)"
        );
        // timestamp は実際に session_start 分ずれていること (相対化が起きた証拠)。
        // raw は絶対 epoch・anon は相対なので raw >= anon が不変 (checked_sub で underflow を明示防御)。
        assert_eq!(
            raw_snaps[0].timestamp.checked_sub(anon_snaps[0].timestamp),
            Some(session_start),
            "raw and anonymized timestamps differ exactly by session_start offset"
        );
    }

    /// **全 category を網羅した特徴量等価性**: 各 KeyCategory を 1 つずつ含む raw fixture
    /// (`category_coverage.ndjson`: alphabetic/numeric/space/enter/OEM 句読点/Tab/テンキー演算子/
    /// navigation/modifier/function/escape/backspace/delete) を replay した特徴量と、その匿名化版を
    /// replay した特徴量が timestamp を除いて完全一致する。run_replay は is_text_producing を使わず
    /// is_backspace + リピート検出のみに依存するため、`Other` に畳まれる OEM 句読点等を含めても
    /// 特徴量は不変であることを保証する (D6 の核心)。
    #[test]
    fn replay_anonymized_matches_raw_features_all_categories() {
        let raw_path = fixture_path("category_coverage.ndjson");
        let raw_snaps = run_replay(&raw_path).expect("replay raw category_coverage");
        assert!(!raw_snaps.is_empty());

        let raw_text = std::fs::read_to_string(&raw_path).expect("read raw");
        let ss = find_session_start(&raw_text).expect("session_start");
        let (anon_text, skipped) = anonymize_ndjson(&raw_text, ss);
        assert_eq!(skipped, 0);
        assert!(!anon_text.contains("\"vk\""));

        let anon_path =
            std::env::temp_dir().join(format!("gse_replay_anon_cov_{}.ndjson", std::process::id()));
        std::fs::write(&anon_path, &anon_text).expect("write anon temp");
        let anon_snaps = run_replay(&anon_path).expect("replay anonymized category_coverage");
        let _ = std::fs::remove_file(&anon_path);

        assert_eq!(
            snapshots_without_timestamp(&raw_snaps),
            snapshots_without_timestamp(&anon_snaps),
            "feature values must match across all key categories incl. Other-folded keys"
        );
    }

    /// **Epic 2 安全網: `--snapshot` ゴールデン回帰を CLI 手動でなく cargo test で強制する**。
    /// これまで `gse-replay <fixture> --snapshot <golden>` は手動実行のみで、`engine.rs` /
    /// `features.rs` / `loop_step.rs` の挙動変更を byte-equal (FeatSnapshot 構造体等価) で守る
    /// 唯一の門が CI/test の外にあった。既存の `replay_anonymized_matches_raw_features` 系は
    /// raw==anon の *相対* 比較のため、両辺が同時にずれる絶対ドリフト (β / EWMA α / 放出行列
    /// 変更など) を検出できない。本テストは各 fixture の現行出力を **コミット済みゴールデンの
    /// 絶対値**と突き合わせ、`run_replay` + `compare_snapshots` (main の `--snapshot` 経路と同一
    /// 関数) を駆動する。ゴールデンは `gse-replay <fixture> > tests/snapshots/<name>.json` で再生成。
    /// HMM_VERSION bump 時はゴールデン再生成が設計上必須 (差分意図を .steering に記録)。
    ///
    /// カバレッジ (② golden 監査より):
    /// - `minimal`          : active-typing 特徴量 (F1/F3/F4/obs/EWMA・alpha=0.3)
    /// - `phase1_ime_heavy` : IME pause + 沈黙経路 (alpha=0.15・f5 pause 蓄積・f1 沈黙フロア・β-writing)
    /// - `category_coverage`: resolve_key_vk + Other 畳み込み + obs 量子化
    /// - `deep_silence`     : 深い沈黙フロア (loop_step.rs 8/10/30s 分岐)。約43秒沈黙で TransitionPath の
    ///   ctx フロア (f6/f3 = ctx × time_scale ランプ) を踏む。従来 fixture は
    ///   f6 が常に 0 で完全未ガードだった領域 (② golden 監査 row 3)。
    ///   ⚠️★ **2026-08-16 訂正**: 本 fixture は **SilencePath を踏まない**。
    ///   `FeatureExtractor` は IME pause 遷移でしか `reset()` されず、
    ///   窓の右端も「最後の打鍵時刻」なので、沈黙が何秒続いても
    ///   `f1` は 150.0 のまま (= 全 51 行が TransitionPath)。
    ///   ★ SilencePath (`f1` = 2000.0) を踏むのは `phase1_ime_heavy` だけである。
    ///   ★ SilencePath の分岐そのものは `analysis/loop_step.rs` の
    ///   unit test が直接カバーしている。
    /// - `vibe_coding_ime_mixed`: ★ **ADR-006 Phase 2b** (`task_kind` → head 配線)。
    ///   `task_kind=vibe_coding` の宣言により Coding head v0 が選ばれ、
    ///   **IME on/off に関わらず β が切り替わらない**ことを固定する。
    ///   ⚠️ 実測 (2026-08-18): 1〜8s の IME off 区間は Writing head と**完全一致**する
    ///   (β_writing_latin と Coding シードが同値のため)。判別が出るのは 9〜24s の
    ///   IME **on** 区間で、ここが `research-positioning.md §8` の交絡そのものである。
    ///   16〜20s の backspace 16 連打は IME on なので obs=25 は**出ない** (D-3 の gate)。
    ///   28〜30s の IME off 区間でのみ obs=25 が発火する。
    /// - `argumentative_ime_mixed`: ★ **ルーティング表そのものの回帰保護**。
    ///   ⚠️ 既存 4 本は `session_meta` を 1 行も持たないため、`Argumentative → Coding` に
    ///   ルーティングが壊れても**全て緑のまま通ってしまう**（code-reviewer 実測・2026-08-18）。
    ///   本 fixture は `vibe_coding_ime_mixed` と `task_kind` **だけ**が違う双子で、
    ///   「宣言があっても Writing 挙動は不変」を固定する。2 本を対で維持すること
    ///   （片方だけ再生成すると、ルーティングの壊れが差分として現れなくなる）。
    ///
    /// ⚠️ **1 ファイルに相異なる `task_kind` が並んだら、黙って先頭勝ちにせず落とす。**
    ///
    /// 非 G1 モードはログをローテートしないため「開始 → 戻る → 別 task_kind で開始」で
    /// 実際に起こりうる。本番は 2 個目の `session_meta` で head を差し替えるが replay は
    /// 区間を持たないので再現できない。**再現できないものを再現したふりをする**のが
    /// 一番危ないので、明示的に `Err` にする (security-checker 指摘・2026-08-18)。
    #[test]
    fn multiple_distinct_task_kinds_in_one_file_is_rejected() {
        let dir = std::env::temp_dir();
        let path = dir.join(format!(
            "gse_replay_multi_meta_{}.ndjson",
            std::process::id()
        ));
        std::fs::write(
            &path,
            concat!(
                r#"{"type":"meta","session_start":1700000000000,"hmm_version":"0.4.0"}"#,
                "
",
                r#"{"type":"session_meta","track":"main","task_kind":"argumentative","intervention_enabled":false,"ts":1700000000000}"#,
                "
",
                r#"{"type":"session_meta","track":"main","task_kind":"vibe_coding","intervention_enabled":false,"ts":1700000010000}"#,
                "
",
                r#"{"type":"key","t":1700000000200,"vk":65,"press":true}"#,
                "
",
            ),
        )
        .expect("write temp fixture");

        let result = run_replay(&path);
        let _ = std::fs::remove_file(&path);

        let err = result.expect_err("相異なる task_kind が 2 つあるファイルは Err になるべき");
        assert!(
            err.contains("different task_kinds"),
            "エラー文が理由を説明していない: {err}"
        );
    }

    /// `session_meta` が 1 種類でも、`session_start` が複数あれば同じ理由で再現できない
    /// (本番は start_session ごとに `engine.reset()` = head を Writing へ戻す)。
    #[test]
    fn multiple_session_starts_with_declared_task_kind_is_rejected() {
        let dir = std::env::temp_dir();
        let path = dir.join(format!(
            "gse_replay_multi_start_{}.ndjson",
            std::process::id()
        ));
        std::fs::write(
            &path,
            concat!(
                r#"{"type":"meta","session_start":1700000000000,"hmm_version":"0.4.0"}"#,
                "
",
                r#"{"type":"session_meta","track":"main","task_kind":"vibe_coding","intervention_enabled":false,"ts":1700000000000}"#,
                "
",
                r#"{"type":"session_start","t":1700000000000}"#,
                "
",
                r#"{"type":"session_start","t":1700000020000}"#,
                "
",
                r#"{"type":"key","t":1700000000200,"vk":65,"press":true}"#,
                "
",
            ),
        )
        .expect("write temp fixture");

        let result = run_replay(&path);
        let _ = std::fs::remove_file(&path);

        let err = result.expect_err("session_start が 2 つあるファイルは Err になるべき");
        assert!(
            err.contains("session_start rows"),
            "エラー文が理由を説明していない: {err}"
        );
    }

    #[test]
    fn replay_snapshot_goldens_byte_equal() {
        let cases = [
            ("minimal.ndjson", "minimal.json"),
            ("phase1_ime_heavy.ndjson", "phase1_ime_heavy.json"),
            ("category_coverage.ndjson", "category_coverage.json"),
            ("deep_silence.ndjson", "deep_silence.json"),
            ("vibe_coding_ime_mixed.ndjson", "vibe_coding_ime_mixed.json"),
            (
                "argumentative_ime_mixed.ndjson",
                "argumentative_ime_mixed.json",
            ),
        ];
        for (fixture, golden) in cases {
            let snaps = run_replay(&fixture_path(fixture))
                .unwrap_or_else(|e| panic!("replay {fixture}: {e}"));
            assert!(
                !snaps.is_empty(),
                "{fixture}: golden fixture must produce snapshots"
            );
            compare_snapshots(&snaps, &snapshot_path(golden)).unwrap_or_else(|e| {
                panic!(
                    "{golden} drift — replay output diverged from committed golden.\n{e}\n\
                     意図した変更なら `gse-replay tests/fixtures/{fixture} > tests/snapshots/{golden}` \
                     で再生成し .steering に差分意図を記録すること (HMM_VERSION bump 時は必須)。"
                )
            });
        }
    }

    /// **`--metrics` 経路の text-producing 判定が匿名化後も raw と完全一致することを回帰ロックする**
    /// (ADR-014 判断 6 / `.steering/20260823-r3-accept-and-role-category/` D-7)。
    ///
    /// **旧仕様 (2026-08-23 以前)**: 匿名化は `is_text_producing` より粗い `KeyCategory` を使い、
    /// OEM 句読点・Tab・テンキー演算子 (= raw では text-producing だが匿名化で `Other`) が
    /// 匿名化後に判別できず、`collect_key_events` → manual_insert 系がその件数だけ過小評価された。
    /// `manual_contribution_ratio` は `research-positioning.md §5` **H-Y の主要アウトカム**であり、
    /// 構造的な過小評価は研究上許容できない。
    ///
    /// **現仕様**: `Punctuation` / `SentencePunctuation` / `Tab` category を足したので過小評価は **ゼロ**。
    /// **backspace/delete 判定が完全一致**することも併せて確認する。
    #[test]
    fn anonymized_metrics_text_producing_matches_raw_exactly() {
        use gse_next_lib::analysis::metrics::{is_backspace, is_text_producing};

        let raw_path = fixture_path("category_coverage.ndjson");
        let raw_keys = collect_key_events(&raw_path).expect("collect raw keys");

        let raw_text = std::fs::read_to_string(&raw_path).expect("read raw");
        let ss = find_session_start(&raw_text).expect("session_start");
        let (anon_text, _n) = anonymize_ndjson(&raw_text, ss);
        let anon_path = std::env::temp_dir().join(format!(
            "gse_replay_anon_metrics_{}.ndjson",
            std::process::id()
        ));
        std::fs::write(&anon_path, &anon_text).expect("write anon temp");
        let anon_keys = collect_key_events(&anon_path).expect("collect anon keys");
        let _ = std::fs::remove_file(&anon_path);

        // press イベント数は不変 (両方 14 キー press)。
        assert_eq!(raw_keys.len(), anon_keys.len());

        let raw_text_keys = raw_keys.iter().filter(|k| is_text_producing(k.vk)).count();
        let anon_text_keys = anon_keys.iter().filter(|k| is_text_producing(k.vk)).count();
        // raw の text-producing: A,0,numpad7,space,enter,comma,Tab,numpad* = 8。
        // 匿名化後も 8 — comma は `sentence_punctuation`、numpad* は `punctuation`、
        // Tab は `tab` へ入るため。
        assert_eq!(raw_text_keys, 8, "raw text-producing key count");
        assert_eq!(
            anon_text_keys, raw_text_keys,
            "anonymized text-producing count must match raw exactly (no Other-folding loss)"
        );

        // backspace/delete 判定は完全一致 (専用 category)。raw に backspace+delete = 2。
        let raw_bs = raw_keys.iter().filter(|k| is_backspace(k.vk)).count();
        let anon_bs = anon_keys.iter().filter(|k| is_backspace(k.vk)).count();
        assert_eq!(raw_bs, 2, "backspace + delete in fixture");
        assert_eq!(anon_bs, raw_bs, "backspace/delete classification is exact");
    }

    /// コミット済み (人手検査用) golden `minimal.anon.ndjson` が実 `anonymize_ndjson` 出力と byte 一致する
    /// ことを保証する drift-guard。匿名化ロジックが変わったら落ちて再生成を促す。
    #[test]
    fn anonymized_minimal_fixture_matches_anonymizer() {
        let raw_text = std::fs::read_to_string(fixture_path("minimal.ndjson")).expect("read raw");
        let session_start = find_session_start(&raw_text).expect("session_start");
        let (anon_text, _skipped) = anonymize_ndjson(&raw_text, session_start);
        let committed =
            std::fs::read_to_string(fixture_path("minimal.anon.ndjson")).expect("read anon golden");
        // 改行差 (CRLF/LF) を吸収して比較する。
        assert_eq!(
            anon_text.replace("\r\n", "\n"),
            committed.replace("\r\n", "\n"),
            "committed minimal.anon.ndjson is stale; regenerate from minimal.ndjson via anonymize_ndjson"
        );
    }
}
