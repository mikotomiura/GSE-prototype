pub mod anonymize;
pub mod calibration_eval;
pub mod cohort;
pub mod engine;
pub mod features;
pub mod heads;
pub mod intervention;
pub mod intervention_eval;
// ★★★ 特徴量へ流すキーの集合 (ADR-016 D8 のゲート分割の「内側」)。
// ⚠️ 本番と gse-replay の**両方**がここを通る。
pub mod key_gate;
pub mod loop_step;
pub mod metrics;
// ★ ポインタ活動の 1 秒ビン量子化 (O1 / ADR-014 D4 の L-b)。⚠️ OS API を呼ばない純関数。
pub mod pointer_bin;
pub mod probe_scheduler;
