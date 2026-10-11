pub mod anonymize;
pub mod calibration_eval;
pub mod cohort;
pub mod engine;
// ★ ADR-030 D1: stall onset 検出器の下準備となる T0 (activity) 等の特徴量計算 (オフライン専用)。
// `gse-replay --features` が呼ぶ。⚠️ `features.rs` / `engine.rs` とは独立 (HMM_VERSION 非依存)。
pub mod feat_offline;
pub mod features;
pub mod heads;
pub mod intervention;
pub mod intervention_eval;
// EH3 の招待（Physical Anchor の PC 面）を出すかどうかの状態機械。応答を入力に持たない（ADR-033）。
pub mod invitation;
// ★★★ 特徴量へ流すキーの集合 (ADR-016 D8 のゲート分割の「内側」)。
// ⚠️ 本番と gse-replay の**両方**がここを通る。
pub mod key_gate;
pub mod loop_step;
pub mod metrics;
// ★ ポインタ活動の 1 秒ビン量子化 (O1 / ADR-014 D4 の L-b)。⚠️ OS API を呼ばない純関数。
pub mod pointer_bin;
pub mod probe_scheduler;
