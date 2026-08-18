//! ドメイン推論ヘッド (domain inference heads)
//!
//! ADR-002 (domain-local inference) / ADR-006 (task_kind → β baseline 配線) の実装。
//!
//! # 設計の骨子
//!
//! β baseline は「1 関数内の 2 択 if」ではなく **各 head の所有物**である。
//! どの head を走らせるかは `task_kind` (宣言) が決め、`ime_open` (観測) は
//! **Writing head 内部の within-writing 信号**として使う。両者の役割は直交する。
//!
//! ```text
//!   task_kind ──► head 選択 ──► head が所有する β で潜在二軸を算出
//!   ime_open  ──────────────────► Writing head 内部の β 切替 / BS ペナルティ gate
//! ```
//!
//! # trait の範囲について (ADR-002 からの意図的な逸脱)
//!
//! ADR-002 逐語の `DomainInferenceHead` は
//! `infer(&mut self, &DomainFeatureSnapshot, &SessionContext) -> WorkStateEstimate` だが、
//! `WorkStateEstimate` (`uncertainty` / `evidence_quality` 必須) は Decision Engine 境界
//! (ADR-004) とセットで導入すべきものである。本モジュールは現行 engine の形に合わせ、
//! **潜在二軸の算出だけ**を trait 化する。`infer -> WorkStateEstimate` への移行は Epic 3。
//! 判断の根拠は `.steering/20260818-adr006-head-extraction-wiring/decisions.md` D-8。
//!
//! # 関連
//!
//! - `docs/adr/ADR-002-domain-local-inference.md`
//! - `docs/adr/ADR-006-task-kind-beta-wiring.md`
//! - `docs/architecture/domain-adapter-boundary.md` §Layer 3-4

pub mod writing;

pub use writing::WritingHead;

use crate::analysis::features::Features;

/// ドメイン推論ヘッド。
///
/// 各 head は自分の β baseline を所有し、特徴量から潜在二軸
/// (X = Cognitive Friction, Y = Engagement) を算出する。
pub trait DomainInferenceHead: Send + Sync {
    /// head の識別子。どの head がそのセッションを採点したかを記録するために使う。
    fn head_id(&self) -> &'static str;

    /// 潜在二軸 (X = Friction, Y = Engagement) を算出する。
    ///
    /// `ime_open` は「今この瞬間、日本語 IME が日本語入力モード (あ/カ) か」を表す実行時フラグ。
    /// **これをどう使うか・使わないかは head が決める** (Writing head は β 切替に使い、
    /// Coding head は使わない)。
    fn latent_axes(&self, features: &Features, ime_open: bool) -> (f64, f64);

    /// backspace ペナルティビン (obs=25) を適用してよいか。
    ///
    /// ⚠️ **デフォルト実装を置かない。** 各 head に明示実装を強制する。
    /// 既定 (`!ime_open`) を置くと、新しい head を足した人が「BS ペナルティを IME で
    /// gate するか」を**判断せずに黙って継承**してしまう。β を head の所有物にしながら
    /// gate だけ暗黙の既定に落とすのは非対称であり、ADR-006 の「β は head の所有物」
    /// という決定と整合しない (code-reviewer 指摘・2026-08-18)。
    fn applies_backspace_penalty(&self, ime_open: bool) -> bool;
}
