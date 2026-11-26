//! 手跡（Handmark）の段 1 の後期（ADR-051）の、OS 非依存の純粋な部分。
//!
//! IO は持たない（バイト列と値を受けて返す）。ファイルの読み書きは `crate::handmark_store`。
//! 1a では `lib.rs` に配線しない（窓・トレイと一緒に 1b で配線する）。

pub mod assignment;
pub mod day;
pub mod desk;
pub mod gate;
pub mod state;
pub mod stopped;
pub mod trace;
pub mod trace_replay;
