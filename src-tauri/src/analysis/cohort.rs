//! cohort — 被験者横断 (cohort) 較正判定 (v0.3 較正スモーク Task E)
//!
//! Task D の `compute_calibration_metrics` は **1 被験者**の複数セッションを解析し
//! `CalibrationReport` (= per-被験者 metrics.json) を出力する。本モジュールはその
//! per-被験者レポートを **複数被験者ぶん集約**し、凍結済みの純関数
//! [`calibration_eval::model_gate`] / [`calibration_eval::measurement_gate`] を再利用して
//! コホート全体の Go/Kill/INCONCLUSIVE を判定する。
//!
//! # 設計 (`.steering/20260617-probe-e2e/design.md` v2)
//!
//! - **D には一切触れない**: cohort が必要とするのは `CalibrationReport` のごく一部
//!   (C-index 中央値・回答率・件数等の数スカラ) だけ。serde は既定で未知フィールドを
//!   無視するため、必要フィールドだけを宣言した read-model ([`SubjectCalibrationView`]) を
//!   用意すれば D の出力 JSON をそのままパースできる。`calibration_eval.rs` の構造体に
//!   `Deserialize` 派生を足す必要はない (D 凍結)。
//! - **凍結契約に従う**: ゲート駆動は PreReg-4 文言「各人の C-index **中央値**」に従い
//!   `x_q1_session_median`。`x_q1_pooled` は頑健性参考値として併記するがゲートには使わない
//!   (forking paths 排除)。session_median が `None` (セッション不足) の被験者は判定母数から
//!   除外し notes に記録する (値を捏造しない・§11 主張限界)。
//! - **無理に Go と言わない**: PreReg-5 (評価セッション≥6/人・ランダムプローブ≥16/人) を
//!   満たさない被験者はモデルゲート母数から外す。充足被験者が一部だけなら `INCONCLUSIVE`
//!   (データ拡充) に留め、Go に昇格させない。
//!
//! # 関連
//! - `docs/preregistration-v0.3.md` (PreReg-1..8・Go/Kill/INCONCLUSIVE 契約・凍結)
//! - `.steering/20260616-probe-analysis/decisions.md` (D の DD-1..DD-9)

use serde::{Deserialize, Serialize};

use crate::analysis::calibration_eval::{measurement_gate, model_gate, MeasurementGate, ModelGate};

/// PreReg-1 尺度理解ゲートのコホート通過率 (被験者の 80% 以上が通過)。
pub const VIGNETTE_COHORT_PASS_FRACTION: f64 = 0.80;
/// PreReg-5 評価設計の最低要件: 評価セッション数 (≥6/人)。
pub const PREREG5_MIN_EVAL_SESSIONS: usize = 6;
/// PreReg-5 評価設計の最低要件: 提示ランダムプローブ数 (≥16/人)。
pub const PREREG5_MIN_RANDOM_PROBES: usize = 16;
/// D が出力する per-被験者レポートの schema 識別子。
pub const SUBJECT_SCHEMA: &str = "calibration/v0.3";
/// コホートレポートの schema 識別子。
pub const COHORT_SCHEMA: &str = "cohort/v0.3";

// =============================================================================
// 入力: D の calibration JSON を読む read-model (必要フィールドのみ)
// =============================================================================
//
// serde は既定で未知フィールドを無視するため、CalibrationReport 全体ではなく
// cohort 判定に必要なフィールドだけを宣言する。各フィールドは #[serde(default)] で
// 欠落耐性を持たせる (D が将来フィールドを増減しても cohort が壊れない)。

#[derive(Debug, Clone, Default, Deserialize)]
struct MeasurementView {
    #[serde(default)]
    random_probe_total: usize,
    #[serde(default)]
    random_probe_answered: usize,
    #[serde(default)]
    answer_rate: f64,
    #[serde(default)]
    per_subject_pass: bool,
}

#[derive(Debug, Clone, Default, Deserialize)]
struct CindexView {
    #[serde(default)]
    x_q1_pooled: Option<f64>,
    #[serde(default)]
    x_q1_session_median: Option<f64>,
}

#[derive(Debug, Clone, Default, Deserialize)]
struct MnarView {
    #[serde(default)]
    caution: bool,
    #[serde(default)]
    invalid: bool,
}

#[derive(Debug, Clone, Default, Deserialize)]
struct VignetteView {
    #[serde(default)]
    passed: bool,
}

#[derive(Debug, Clone, Default, Deserialize)]
struct BidimView {
    #[serde(default)]
    verifiable: bool,
}

/// D が出力する per-被験者 calibration JSON の read-model (必要フィールドのみ)。
///
/// `serde_json::from_str::<SubjectCalibrationView>(json)` で D の `CalibrationReport`
/// JSON をそのままパースできる (未知フィールドは無視される)。
#[derive(Debug, Clone, Default, Deserialize)]
pub struct SubjectCalibrationView {
    #[serde(default)]
    pub schema: String,
    /// 主指標に含めるか (track=main のセッションが存在するか)。
    #[serde(default)]
    pub included_in_primary: bool,
    #[serde(default)]
    pub evaluation_session_count: usize,
    #[serde(default)]
    measurement: MeasurementView,
    #[serde(default)]
    cindex: CindexView,
    #[serde(default)]
    mnar: MnarView,
    #[serde(default)]
    vignette: VignetteView,
    #[serde(default)]
    bidimensionality: BidimView,
}

/// cohort 判定への 1 被験者ぶんの入力 (被験者 ID は gse-dataset の P000/.. ディレクトリ由来)。
#[derive(Debug, Clone)]
pub struct CohortSubject {
    pub subject_id: String,
    pub view: SubjectCalibrationView,
}

// =============================================================================
// 出力: コホートレポート (Serialize)
// =============================================================================

/// コホート全体の最終判定。PreReg §2 判定フローの合成結果。
#[derive(Debug, Clone, Copy, PartialEq, Eq, Serialize)]
#[serde(rename_all = "snake_case")]
pub enum CohortDecision {
    /// モデルゲート Go (かつ全充足被験者が条件を満たす)。
    Go,
    /// 測定法 Kill (PreReg-2) またはモデル Kill (PreReg-4)。`decision_reason` で区別。
    Kill,
    /// それ以外 (無理に成果と言わない)。
    Inconclusive,
    /// 主指標被験者なし、または PreReg-5 最低要件を満たす被験者がなく評価不能 (データ拡充)。
    DataInsufficient,
}

/// PreReg-1 尺度理解ゲート (コホート)。
#[derive(Debug, Clone, Serialize)]
pub struct CohortVignetteGate {
    pub passed_subjects: usize,
    pub total_subjects: usize,
    pub pass_fraction: f64,
    /// 被験者の 80% 以上が通過したか。
    pub passed: bool,
}

/// PreReg-2 測定法ゲート (コホート)。
#[derive(Debug, Clone, Serialize)]
pub struct CohortMeasurementGate {
    /// 全被験者プールの回答率 (Σ回答 / Σ提示)。
    pub overall_answer_rate: f64,
    pub per_subject_answer_rates: Vec<f64>,
    pub verdict: MeasurementGate,
}

/// PreReg-4 モデルゲート (コホート)。
#[derive(Debug, Clone, Serialize)]
pub struct CohortModelGate {
    /// ゲートに投入した被験者別 C-index 中央値 (session-median・PreReg-4 文言準拠)。
    pub session_median_cindices: Vec<f64>,
    /// 投入値の中央値 (参考表示)。
    pub cohort_median: Option<f64>,
    /// session_median が None で除外した被験者数。
    pub excluded_for_missing_median: usize,
    /// PreReg-5 最低要件未達で除外した被験者数。
    pub excluded_for_insufficient_data: usize,
    /// PreReg-2 被験者要件 (per_subject_pass=false: latency/有効件数/回答率) 未達で除外した被験者数。
    pub excluded_for_measurement_quality: usize,
    pub verdict: ModelGate,
}

/// 被験者別サマリ (監査・データ品質可視化用)。
#[derive(Debug, Clone, Serialize)]
pub struct CohortSubjectSummary {
    pub subject_id: String,
    pub included_in_primary: bool,
    pub x_q1_session_median: Option<f64>,
    pub x_q1_pooled: Option<f64>,
    pub answer_rate: f64,
    /// PreReg-2 被験者要件 (回答率≥0.80 & latency≤10s & 有効≥20)。
    pub per_subject_pass: bool,
    pub evaluation_session_count: usize,
    pub random_probe_total: usize,
    /// PreReg-5: 評価セッション ≥6。
    pub prereg5_eval_ok: bool,
    /// PreReg-5: 提示ランダムプローブ ≥16。
    pub prereg5_probe_ok: bool,
    /// モデルゲート母数に含めたか (included & median有 & PreReg-5 充足)。
    pub gate_eligible: bool,
    pub vignette_passed: bool,
    /// PreReg-7 MNAR: 無回答率 >20%。
    pub mnar_caution: bool,
    /// PreReg-7 MNAR: 無回答率 >30% (主分析不成立)。
    pub mnar_invalid: bool,
    /// PreReg-8 二軸性: 非対角象限 ≥10% で検証可能。
    pub bidimensionality_verifiable: bool,
}

/// コホート較正レポート (`gse-cohort` が出力する JSON)。
#[derive(Debug, Clone, Serialize)]
pub struct CohortReport {
    pub schema: String,
    pub subject_count: usize,
    /// 主指標対象 (included_in_primary == true) の被験者数。
    pub included_subject_count: usize,
    /// モデルゲート母数に入った被験者数。
    pub gate_eligible_count: usize,
    pub vignette: CohortVignetteGate,
    pub measurement: CohortMeasurementGate,
    pub model: CohortModelGate,
    pub overall: CohortDecision,
    pub decision_reason: String,
    /// PreReg-7: 無回答率 >30% (主分析不成立) の主指標被験者数。
    pub mnar_invalid_count: usize,
    /// PreReg-7: 無回答率 >20% (注意) の主指標被験者数。
    pub mnar_caution_count: usize,
    /// PreReg-8: 二軸性が検証可能 (非対角象限 ≥10%) の主指標被験者数。
    pub bidimensionality_verifiable_count: usize,
    pub subjects: Vec<CohortSubjectSummary>,
    pub notes: Vec<String>,
}

// =============================================================================
// 判定の中核 (純関数)
// =============================================================================

/// per-被験者 calibration レポート集合からコホート判定を組み立てる。
///
/// 凍結された純関数 [`model_gate`] / [`measurement_gate`] を再利用し、再実装しない。
/// 判定フロー (`decide_overall` の優先順位):
/// 1. 主指標被験者なし → `DataInsufficient`。
/// 2. 提示ランダムプローブ 0 件 → `DataInsufficient` (測定不能。回答率0を Kill と誤断定しないため
///    PreReg-1 より前に置く)。
/// 3. PreReg-1 尺度理解未達 (通過率 <80%) → `Inconclusive` (教示再設計)。
/// 4. PreReg-2 測定法 Kill → `Kill`。
/// 5. PreReg-5 充足被験者なし → `DataInsufficient` (データ拡充)。
/// 6. モデルゲート結果。ただし充足被験者が一部だけなら Go に昇格させず `Inconclusive`。
pub fn cohort_verdict(subjects: &[CohortSubject]) -> CohortReport {
    let mut notes: Vec<String> = Vec::new();

    // schema 不一致は処理は続けるが監査ノートに残す。
    for s in subjects {
        if s.view.schema != SUBJECT_SCHEMA {
            notes.push(format!(
                "subject {}: unexpected schema {:?} (expected {:?})",
                s.subject_id, s.view.schema, SUBJECT_SCHEMA
            ));
        }
    }

    // 主指標対象 (track=main を含む) のみをコホート判定に使う (§1.3)。
    let included: Vec<&CohortSubject> = subjects
        .iter()
        .filter(|s| s.view.included_in_primary)
        .collect();
    let excluded_non_primary = subjects.len() - included.len();
    if excluded_non_primary > 0 {
        notes.push(format!(
            "{} subject(s) excluded from cohort (no main-track session, §1.3)",
            excluded_non_primary
        ));
    }

    // ---- PreReg-1 尺度理解ゲート (コホート) ----
    let vignette_passed_subjects = included.iter().filter(|s| s.view.vignette.passed).count();
    let vignette_total = included.len();
    let vignette_fraction = if vignette_total == 0 {
        0.0
    } else {
        vignette_passed_subjects as f64 / vignette_total as f64
    };
    let vignette_gate = CohortVignetteGate {
        passed_subjects: vignette_passed_subjects,
        total_subjects: vignette_total,
        pass_fraction: vignette_fraction,
        passed: vignette_total > 0 && vignette_fraction >= VIGNETTE_COHORT_PASS_FRACTION,
    };

    // ---- PreReg-2 測定法ゲート (コホート) ----
    let total_presented: usize = included
        .iter()
        .map(|s| s.view.measurement.random_probe_total)
        .sum();
    let total_answered: usize = included
        .iter()
        .map(|s| s.view.measurement.random_probe_answered)
        .sum();
    let overall_answer_rate = if total_presented == 0 {
        0.0
    } else {
        total_answered as f64 / total_presented as f64
    };
    let per_subject_answer_rates: Vec<f64> = included
        .iter()
        .map(|s| s.view.measurement.answer_rate)
        .collect();
    let measurement_verdict = measurement_gate(overall_answer_rate, &per_subject_answer_rates);
    let measurement_gate_report = CohortMeasurementGate {
        overall_answer_rate,
        per_subject_answer_rates,
        verdict: measurement_verdict,
    };

    // ---- PreReg-2/4/5 モデルゲート母数の選別 ----
    // ゲート母数 = 主指標対象 & session_median 有 & PreReg-5 充足 (eval≥6 & probe≥16)
    //            & PreReg-2 被験者要件充足 (per_subject_pass: 回答率≥0.80 & latency≤10s & 有効≥20)。
    // PreReg-2 の latency/有効件数は D が per_subject_pass に畳み込んでいる。これを母数条件に
    // 含めないと、測定品質が不十分な被験者の C-index が Go 母数に混入してしまう (code-reviewer HIGH)。
    let mut excluded_missing_median = 0usize;
    let mut excluded_insufficient = 0usize;
    let mut excluded_measurement_quality = 0usize;
    let mut gate_cindices: Vec<f64> = Vec::new();
    let mut subject_summaries: Vec<CohortSubjectSummary> = Vec::with_capacity(subjects.len());

    for s in subjects {
        let v = &s.view;
        let prereg5_eval_ok = v.evaluation_session_count >= PREREG5_MIN_EVAL_SESSIONS;
        let prereg5_probe_ok = v.measurement.random_probe_total >= PREREG5_MIN_RANDOM_PROBES;
        let has_median = v.cindex.x_q1_session_median.is_some();
        let prereg5_ok = prereg5_eval_ok && prereg5_probe_ok;
        let gate_eligible =
            v.included_in_primary && has_median && prereg5_ok && v.measurement.per_subject_pass;

        if v.included_in_primary {
            if !has_median {
                excluded_missing_median += 1;
                notes.push(format!(
                    "subject {}: no session-median C-index (insufficient eval sessions) → excluded from model gate",
                    s.subject_id
                ));
            } else if !prereg5_ok {
                excluded_insufficient += 1;
                notes.push(format!(
                    "subject {}: PreReg-5 unmet (eval_sessions={} need≥{}, random_probes={} need≥{}) → excluded from model gate (データ拡充)",
                    s.subject_id,
                    v.evaluation_session_count,
                    PREREG5_MIN_EVAL_SESSIONS,
                    v.measurement.random_probe_total,
                    PREREG5_MIN_RANDOM_PROBES
                ));
            } else if !v.measurement.per_subject_pass {
                excluded_measurement_quality += 1;
                notes.push(format!(
                    "subject {}: PreReg-2 per-subject requirement unmet (per_subject_pass=false: 回答率/latency/有効件数) → excluded from model gate",
                    s.subject_id
                ));
            }
        }

        if gate_eligible {
            // has_median は確認済み。
            gate_cindices.push(v.cindex.x_q1_session_median.unwrap());
        }

        subject_summaries.push(CohortSubjectSummary {
            subject_id: s.subject_id.clone(),
            included_in_primary: v.included_in_primary,
            x_q1_session_median: v.cindex.x_q1_session_median,
            x_q1_pooled: v.cindex.x_q1_pooled,
            answer_rate: v.measurement.answer_rate,
            per_subject_pass: v.measurement.per_subject_pass,
            evaluation_session_count: v.evaluation_session_count,
            random_probe_total: v.measurement.random_probe_total,
            prereg5_eval_ok,
            prereg5_probe_ok,
            gate_eligible,
            vignette_passed: v.vignette.passed,
            mnar_caution: v.mnar.caution,
            mnar_invalid: v.mnar.invalid,
            bidimensionality_verifiable: v.bidimensionality.verifiable,
        });
    }

    let model_verdict = model_gate(&gate_cindices);
    let cohort_median = median_f64(&gate_cindices);
    let model_gate_report = CohortModelGate {
        session_median_cindices: gate_cindices.clone(),
        cohort_median,
        excluded_for_missing_median: excluded_missing_median,
        excluded_for_insufficient_data: excluded_insufficient,
        excluded_for_measurement_quality: excluded_measurement_quality,
        verdict: model_verdict,
    };

    // MNAR / 二軸性は報告併走 (PreReg-7/8)。コホート全体の注意を notes に集約 + 機械可読カウント。
    let mnar_invalid_count = included.iter().filter(|s| s.view.mnar.invalid).count();
    let mnar_caution_count = included.iter().filter(|s| s.view.mnar.caution).count();
    let bidimensionality_verifiable_count = included
        .iter()
        .filter(|s| s.view.bidimensionality.verifiable)
        .count();
    if mnar_invalid_count > 0 {
        notes.push("PreReg-7: 無回答率 >30% の被験者あり (該当被験者の主分析は不成立)".to_string());
    } else if mnar_caution_count > 0 {
        notes.push("PreReg-7: 無回答率 >20% の被験者あり (MNAR 注意)".to_string());
    }
    if bidimensionality_verifiable_count == 0 && !included.is_empty() {
        notes.push(
            "PreReg-8: 非対角象限 <10% のため二軸性は検証不能 (単軸とも二軸とも結論しない)"
                .to_string(),
        );
    }

    // ---- 最終判定の合成 (PreReg §2 フロー) ----
    let gate_eligible_count = gate_cindices.len();
    let (overall, decision_reason) = decide_overall(
        included.len(),
        &vignette_gate,
        measurement_verdict,
        overall_answer_rate,
        total_presented,
        gate_eligible_count,
        model_verdict,
    );

    CohortReport {
        schema: COHORT_SCHEMA.to_string(),
        subject_count: subjects.len(),
        included_subject_count: included.len(),
        gate_eligible_count,
        vignette: vignette_gate,
        measurement: measurement_gate_report,
        model: model_gate_report,
        overall,
        decision_reason,
        mnar_invalid_count,
        mnar_caution_count,
        bidimensionality_verifiable_count,
        subjects: subject_summaries,
        notes,
    }
}

/// PreReg §2 の判定フローを合成して最終判定と理由文字列を返す。
fn decide_overall(
    included_count: usize,
    vignette: &CohortVignetteGate,
    measurement: MeasurementGate,
    overall_answer_rate: f64,
    total_presented_probes: usize,
    gate_eligible_count: usize,
    model: ModelGate,
) -> (CohortDecision, String) {
    if included_count == 0 {
        return (
            CohortDecision::DataInsufficient,
            "no main-track subjects in primary set → データ拡充".to_string(),
        );
    }
    // プローブ提示 0 件は「測定不能」であって「測定法 Kill」ではない。回答率 0.0 を Kill と
    // 誤断定しないよう DataInsufficient に分岐する (code-reviewer MEDIUM)。
    if total_presented_probes == 0 {
        return (
            CohortDecision::DataInsufficient,
            "提示ランダムプローブ 0 件のため回答率を測定できない → データ拡充".to_string(),
        );
    }
    if !vignette.passed {
        return (
            CohortDecision::Inconclusive,
            format!(
                "PreReg-1 尺度理解未達: 通過率 {:.2} < {:.2} → 教示文再設計・本番データ不可",
                vignette.pass_fraction, VIGNETTE_COHORT_PASS_FRACTION
            ),
        );
    }
    if measurement == MeasurementGate::Kill {
        return (
            CohortDecision::Kill,
            format!(
                "PreReg-2 測定法 Kill: 全体回答率 {:.2} (モデル評価に進まない)",
                overall_answer_rate
            ),
        );
    }
    if gate_eligible_count == 0 {
        return (
            CohortDecision::DataInsufficient,
            format!(
                "PreReg-5 未達: eval≥{}/人 & probe≥{}/人 を満たす被験者なし → データ拡充",
                PREREG5_MIN_EVAL_SESSIONS, PREREG5_MIN_RANDOM_PROBES
            ),
        );
    }
    match model {
        ModelGate::Go => {
            if gate_eligible_count < included_count {
                (
                    CohortDecision::Inconclusive,
                    format!(
                        "モデルゲート Go だが PreReg-5 充足が {}/{} 被験者のみ。無理に Go としない → データ拡充",
                        gate_eligible_count, included_count
                    ),
                )
            } else {
                (
                    CohortDecision::Go,
                    "PreReg-4 モデルゲート Go (全充足被験者: C-index 中央値≥0.65 & 全員>0.55)"
                        .to_string(),
                )
            }
        }
        ModelGate::Kill => (
            CohortDecision::Kill,
            "PreReg-4 モデルゲート Kill (C-index 中央値≤0.55 または 2人以上≤0.50)".to_string(),
        ),
        ModelGate::Inconclusive => (
            CohortDecision::Inconclusive,
            "PreReg-4 モデルゲート INCONCLUSIVE (Go/Kill いずれの閾値も満たさず)".to_string(),
        ),
    }
}

/// f64 スライスの中央値 (空なら None)。NaN は含まれない前提 (C-index は有限値)。
///
/// `calibration_eval` の private `median_f64` と実装はほぼ同一だが、D を凍結 (本モジュールは
/// `calibration_eval.rs` に触れない) する方針のため意図的に分離している。共通 stats 切り出しは
/// 将来の別タスク (DD 受容メモ参照)。
fn median_f64(values: &[f64]) -> Option<f64> {
    if values.is_empty() {
        return None;
    }
    let mut v: Vec<f64> = values.to_vec();
    v.sort_by(|a, b| a.partial_cmp(b).unwrap_or(std::cmp::Ordering::Equal));
    let n = v.len();
    if n % 2 == 1 {
        Some(v[n / 2])
    } else {
        Some((v[n / 2 - 1] + v[n / 2]) / 2.0)
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    /// D の `CalibrationReport` JSON 形を模した per-被験者 JSON を生成して read-model に
    /// パースする。cohort が読まない未知フィールド (agg/recall/dont_remember 等) も混ぜ、
    /// serde の subset パース (未知フィールド無視) が D の実出力形で機能することを検証する。
    #[allow(clippy::too_many_arguments)]
    fn subject(
        id: &str,
        included: bool,
        vignette_passed: bool,
        answer_rate: f64,
        random_probe_total: usize,
        random_probe_answered: usize,
        eval_sessions: usize,
        session_median: Option<f64>,
    ) -> CohortSubject {
        subject_pp(
            id,
            included,
            vignette_passed,
            answer_rate,
            random_probe_total,
            random_probe_answered,
            eval_sessions,
            session_median,
            true,
        )
    }

    /// `subject` の拡張版: PreReg-2 被験者要件 (`per_subject_pass`) を指定できる。
    #[allow(clippy::too_many_arguments)]
    fn subject_pp(
        id: &str,
        included: bool,
        vignette_passed: bool,
        answer_rate: f64,
        random_probe_total: usize,
        random_probe_answered: usize,
        eval_sessions: usize,
        session_median: Option<f64>,
        per_subject_pass: bool,
    ) -> CohortSubject {
        let median_json = match session_median {
            Some(v) => format!("{v}"),
            None => "null".to_string(),
        };
        let json = format!(
            r#"{{
                "schema": "calibration/v0.3",
                "included_in_primary": {included},
                "session_count": 10,
                "main_session_count": 10,
                "exploratory_session_count": 0,
                "calibration_session_count": 2,
                "evaluation_session_count": {eval_sessions},
                "agg": {{ "source": "ewma", "stat": "median" }},
                "measurement": {{
                    "random_probe_total": {random_probe_total},
                    "random_probe_answered": {random_probe_answered},
                    "answer_rate": {answer_rate},
                    "latency_median_ms": 3000,
                    "valid_count": {random_probe_answered},
                    "no_answer_rate": 0.05,
                    "dont_remember_count": 0,
                    "random_probe_assigned": {random_probe_total},
                    "assigned_without_label": 0,
                    "per_subject_pass": {per_subject_pass}
                }},
                "cindex": {{
                    "x_q1_pooled": 0.66,
                    "x_q1_session_median": {median_json},
                    "y_q2_pooled": null,
                    "y_q2_session_median": null,
                    "eval_pair_source_count": 20
                }},
                "mnar": {{ "point": 0.66, "lower": 0.5, "upper": 0.8, "no_answer_rate": 0.05, "caution": false, "invalid": false }},
                "vignette": {{ "total": 8, "matched": 7, "passed": {vignette_passed} }},
                "bidimensionality": {{ "flow": 1, "stuck": 1, "incubation": 1, "idle": 1, "ambiguous": 0, "incubation_fraction": 0.25, "off_diagonal_fraction": 0.3, "verifiable": true }},
                "recall": {{ "reported": false, "positive_episode_count": 3, "reason": "withheld" }},
                "notes": []
            }}"#
        );
        let view: SubjectCalibrationView = serde_json::from_str(&json).expect("read-model parse");
        CohortSubject {
            subject_id: id.to_string(),
            view,
        }
    }

    /// read-model を D の **実シリアライザ**出力に結合させる drift ガード。
    /// D が `CalibrationReport` のフィールド名を変えたら本テストが落ちる。
    ///
    /// 空入力だけだと全フィールドが既定値 (0/None/false) になり、フィールド名 rename を
    /// read-model の `#[serde(default)]` が静かに飲み込んで検出できない (code-reviewer MEDIUM)。
    /// そこで **非ゼロ値を持つ実レポート**も併せて検証し、`measurement.*` 等の名前 drift を
    /// 実値で検出する。
    #[test]
    fn read_model_matches_real_calibration_report() {
        use crate::analysis::calibration_eval::{
            compute_calibration_metrics, AggSpec, ProbeRecord, ProbeSourceKind, SessionData,
            SkipReasonKind, TrackKind,
        };

        // (a) 空入力: トップレベルのフィールド名整合。
        let empty = compute_calibration_metrics(&[], AggSpec::default());
        let v0: SubjectCalibrationView =
            serde_json::from_str(&serde_json::to_string(&empty).unwrap()).unwrap();
        assert_eq!(v0.schema, empty.schema);
        assert_eq!(v0.included_in_primary, empty.included_in_primary);

        // (b) 非ゼロ入力: main track + 回答済み random_probe を 2 件持つ 1 セッション。
        //     measurement.random_probe_total / random_probe_answered / answer_rate が非ゼロになり、
        //     read-model がその実値を正しく取り出すことを確認する。
        let probe = |answered: bool| ProbeRecord {
            source: ProbeSourceKind::RandomProbe,
            answered,
            q1_friction: if answered { Some(4) } else { None },
            q2_progress: if answered { Some(2) } else { None },
            skip_reason: SkipReasonKind::None,
            latency_ms: 3000,
            window_start_ms: 0,
            window_end_ms: 30_000,
        };
        let session = SessionData {
            track: TrackKind::Main,
            probes: vec![probe(true), probe(true)],
            vignettes: Vec::new(),
            feats: Vec::new(),
            random_probe_assignment_count: 2,
            session_start_ms: Some(0),
            skipped_parse: 0,
            skipped_unknown_enum: 0,
            skipped_out_of_range: 0,
        };
        let report = compute_calibration_metrics(&[session], AggSpec::default());
        let json = serde_json::to_string(&report).expect("serialize real D report");
        let view: SubjectCalibrationView =
            serde_json::from_str(&json).expect("parse real D report into read-model");
        // read-model の実値が D のレポートと一致 (フィールド名 drift があればここで落ちる)。
        assert_eq!(
            view.measurement.random_probe_total,
            report.measurement.random_probe_total
        );
        assert_eq!(
            view.measurement.random_probe_answered,
            report.measurement.random_probe_answered
        );
        assert!((view.measurement.answer_rate - report.measurement.answer_rate).abs() < 1e-12);
        assert_eq!(
            view.measurement.per_subject_pass,
            report.measurement.per_subject_pass
        );
        assert_eq!(view.included_in_primary, report.included_in_primary);
        // evaluation_session_count は PreReg-5 ゲートを駆動する最重要フィールド。
        // rename されると全被験者が静かにゲート除外されるため drift を実値で固定する (cross-review M-1)。
        assert_eq!(
            view.evaluation_session_count,
            report.evaluation_session_count
        );
        assert!(view.measurement.random_probe_total >= 2);
    }

    #[test]
    fn cohort_excludes_subject_failing_prereg2_per_subject() {
        // 3 名のうち 1 名が per_subject_pass=false (latency/有効件数不足) → ゲート母数から除外。
        // 残り 2 名で model Go 相当だが、充足が 2/3 のため Go 昇格させず Inconclusive。
        let subjects = vec![
            subject("P000", true, true, 0.9, 20, 18, 8, Some(0.70)),
            subject("P001", true, true, 0.9, 20, 18, 8, Some(0.72)),
            subject_pp("P002", true, true, 0.9, 20, 18, 8, Some(0.71), false),
        ];
        let r = cohort_verdict(&subjects);
        assert_eq!(r.model.excluded_for_measurement_quality, 1);
        assert_eq!(r.gate_eligible_count, 2);
        assert_eq!(r.overall, CohortDecision::Inconclusive);
        assert!(r
            .notes
            .iter()
            .any(|n| n.contains("P002") && n.contains("PreReg-2 per-subject")));
    }

    #[test]
    fn cohort_data_insufficient_when_no_probes_presented() {
        // 提示プローブ 0 件 → 回答率 0.0 を測定法 Kill と誤断定せず DataInsufficient。
        let subjects = vec![
            subject("P000", true, true, 0.0, 0, 0, 8, Some(0.70)),
            subject("P001", true, true, 0.0, 0, 0, 8, Some(0.72)),
        ];
        let r = cohort_verdict(&subjects);
        assert_eq!(r.overall, CohortDecision::DataInsufficient);
        assert!(r.decision_reason.contains("提示ランダムプローブ 0 件"));
    }

    /// read-model が D の JSON 形から正しい値を取り出すこと (フィールド名 drift 検出)。
    #[test]
    fn read_model_parses_d_json_shape() {
        let s = subject("P000", true, true, 0.9, 20, 18, 8, Some(0.70));
        assert_eq!(s.view.schema, "calibration/v0.3");
        assert!(s.view.included_in_primary);
        assert_eq!(s.view.evaluation_session_count, 8);
        assert_eq!(s.view.measurement.random_probe_total, 20);
        assert_eq!(s.view.measurement.random_probe_answered, 18);
        assert!((s.view.measurement.answer_rate - 0.9).abs() < 1e-9);
        assert_eq!(s.view.cindex.x_q1_session_median, Some(0.70));
    }

    #[test]
    fn cohort_go_when_all_eligible_and_model_go() {
        let subjects = vec![
            subject("P000", true, true, 0.9, 20, 18, 8, Some(0.70)),
            subject("P001", true, true, 0.9, 20, 18, 8, Some(0.68)),
            subject("P002", true, true, 0.9, 20, 18, 8, Some(0.72)),
        ];
        let r = cohort_verdict(&subjects);
        assert_eq!(r.overall, CohortDecision::Go);
        assert_eq!(r.model.verdict, ModelGate::Go);
        assert_eq!(r.gate_eligible_count, 3);
        assert_eq!(r.measurement.verdict, MeasurementGate::Pass);
    }

    #[test]
    fn cohort_model_kill_when_median_low() {
        let subjects = vec![
            subject("P000", true, true, 0.9, 20, 18, 8, Some(0.50)),
            subject("P001", true, true, 0.9, 20, 18, 8, Some(0.52)),
            subject("P002", true, true, 0.9, 20, 18, 8, Some(0.51)),
        ];
        let r = cohort_verdict(&subjects);
        assert_eq!(r.model.verdict, ModelGate::Kill);
        assert_eq!(r.overall, CohortDecision::Kill);
        assert!(r.decision_reason.contains("モデルゲート Kill"));
    }

    #[test]
    fn cohort_measurement_kill_takes_precedence_over_model() {
        // overall answer rate 36/60 = 0.60 < 0.80 → 測定法 Kill。C-index は Go 相当でも止まる。
        let subjects = vec![
            subject("P000", true, true, 0.60, 20, 12, 8, Some(0.70)),
            subject("P001", true, true, 0.60, 20, 12, 8, Some(0.68)),
            subject("P002", true, true, 0.60, 20, 12, 8, Some(0.72)),
        ];
        let r = cohort_verdict(&subjects);
        assert_eq!(r.measurement.verdict, MeasurementGate::Kill);
        assert_eq!(r.overall, CohortDecision::Kill);
        assert!(r.decision_reason.contains("測定法 Kill"));
    }

    #[test]
    fn cohort_data_insufficient_when_prereg5_unmet() {
        // 測定法・尺度は通過するが評価セッション数が 4 (<6) → ゲート母数 0 → データ拡充。
        let subjects = vec![
            subject("P000", true, true, 0.9, 20, 18, 4, Some(0.70)),
            subject("P001", true, true, 0.9, 20, 18, 4, Some(0.68)),
        ];
        let r = cohort_verdict(&subjects);
        assert_eq!(r.gate_eligible_count, 0);
        assert_eq!(r.model.excluded_for_insufficient_data, 2);
        assert_eq!(r.overall, CohortDecision::DataInsufficient);
        assert!(r.decision_reason.contains("PreReg-5"));
    }

    #[test]
    fn cohort_data_insufficient_when_probes_too_few() {
        // probe_total 10 (<16) → PreReg-5 unmet。
        let subjects = vec![
            subject("P000", true, true, 0.9, 10, 9, 8, Some(0.70)),
            subject("P001", true, true, 0.9, 10, 9, 8, Some(0.68)),
        ];
        let r = cohort_verdict(&subjects);
        assert_eq!(r.gate_eligible_count, 0);
        assert_eq!(r.overall, CohortDecision::DataInsufficient);
    }

    #[test]
    fn cohort_partial_eligibility_downgrades_go_to_inconclusive() {
        // 2/3 が PreReg-5 充足で model Go 相当だが、1 名が eval 不足 → 無理に Go としない。
        let subjects = vec![
            subject("P000", true, true, 0.9, 20, 18, 8, Some(0.70)),
            subject("P001", true, true, 0.9, 20, 18, 8, Some(0.72)),
            subject("P002", true, true, 0.9, 20, 18, 4, Some(0.71)),
        ];
        let r = cohort_verdict(&subjects);
        assert_eq!(r.gate_eligible_count, 2);
        assert_eq!(r.included_subject_count, 3);
        assert_eq!(r.model.verdict, ModelGate::Go);
        assert_eq!(r.overall, CohortDecision::Inconclusive);
        assert!(r.decision_reason.contains("無理に Go としない"));
    }

    #[test]
    fn cohort_missing_median_excluded_with_note() {
        let subjects = vec![
            subject("P000", true, true, 0.9, 20, 18, 8, Some(0.70)),
            subject("P001", true, true, 0.9, 20, 18, 8, None),
            subject("P002", true, true, 0.9, 20, 18, 8, Some(0.72)),
        ];
        let r = cohort_verdict(&subjects);
        assert_eq!(r.model.excluded_for_missing_median, 1);
        assert_eq!(r.gate_eligible_count, 2);
        assert!(r
            .notes
            .iter()
            .any(|n| n.contains("P001") && n.contains("no session-median")));
    }

    #[test]
    fn cohort_vignette_fail_blocks_with_inconclusive() {
        // 通過率 1/3 ≈ 0.33 < 0.80 → 尺度理解未達。
        let subjects = vec![
            subject("P000", true, true, 0.9, 20, 18, 8, Some(0.70)),
            subject("P001", true, false, 0.9, 20, 18, 8, Some(0.68)),
            subject("P002", true, false, 0.9, 20, 18, 8, Some(0.72)),
        ];
        let r = cohort_verdict(&subjects);
        assert!(!r.vignette.passed);
        assert_eq!(r.overall, CohortDecision::Inconclusive);
        assert!(r.decision_reason.contains("尺度理解未達"));
    }

    #[test]
    fn cohort_excludes_non_primary_subjects() {
        let subjects = vec![
            subject("P000", true, true, 0.9, 20, 18, 8, Some(0.70)),
            subject("P001", true, true, 0.9, 20, 18, 8, Some(0.72)),
            subject("P002", false, true, 0.9, 20, 18, 8, Some(0.71)),
        ];
        let r = cohort_verdict(&subjects);
        assert_eq!(r.subject_count, 3);
        assert_eq!(r.included_subject_count, 2);
        assert!(r.notes.iter().any(|n| n.contains("excluded from cohort")));
    }

    #[test]
    fn cohort_data_insufficient_when_no_primary_subjects() {
        let subjects = vec![subject("P000", false, true, 0.9, 20, 18, 8, Some(0.70))];
        let r = cohort_verdict(&subjects);
        assert_eq!(r.included_subject_count, 0);
        assert_eq!(r.overall, CohortDecision::DataInsufficient);
    }

    #[test]
    fn cohort_report_serializes_to_json() {
        let subjects = vec![subject("P000", true, true, 0.9, 20, 18, 8, Some(0.70))];
        let r = cohort_verdict(&subjects);
        let json = serde_json::to_string(&r).expect("serialize");
        assert!(json.contains("\"schema\":\"cohort/v0.3\""));
        assert!(json.contains("\"overall\":"));
    }
}
