// Task C: v0.3 較正スモークの収集経路で共有する型定義。
// backend (logger.rs / lib.rs commands) の固定カテゴリと一致させる。
// 本文・タイトル・選択文字列は一切扱わない (data-privacy)。

export type ProbeSource = "random_probe" | "self_marker";
export type SkipReason = "dont_remember" | "dismissed";
export type TaskKind =
  | "argumentative"
  | "correspondence"
  | "creative"
  | "vibe_coding"
  // ★ O1 の宣言 UI だけに出す (ADR-037)。G1 の開始画面には出さない。
  | "other";
export type Track = "main" | "exploratory";
export type ExpectedQuadrant = "flow" | "stuck" | "incubation" | "idle";

/// backend (probe scheduler / self-marker hotkey) が emit する probe_triggered の payload (DB-4)。
export interface ProbeTriggered {
  probe_id: string | null; // self_marker は null
  source: ProbeSource;
  analysis_window_start_ms: number;
  analysis_window_end_ms: number;
}
