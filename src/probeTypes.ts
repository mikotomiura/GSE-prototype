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

// ---------------------------------------------------------------------------
// 段 1（ADR-043・M5 の 2 本目）: backend の `s1_driver::S1CardView` と同期する。
// ★ カードの真実は backend が持つ。画面はこの状態を描くだけ（`get_s1_card` / `s1_card_state`）。
// ---------------------------------------------------------------------------

/** いま出すカード（backend が 1 つだけ決める）。`stratum`・対象の日・契機は本人に見せない。 */
export type S1CardState =
  | { kind: "none" }
  | {
      kind: "probe";
      probe_id: string;
      window_start_ms: number;
      window_end_ms: number;
    }
  | {
      kind: "day";
      card_id: number;
      /** 翌日の拾い直し（「昨日の作業に」と尋ねる）。 */
      delayed: boolean;
      /** トレイの終了の補助（ボタンが「答えて終了／答えずに終了」）。 */
      quit_flow: boolean;
    };

/** backend `get_s1_mode` と同期。 */
export interface S1ModeDto {
  s1: boolean;
  consent: boolean;
}

/** 7 択の値（backend `logger::ActivityCategory` と同じ・ADR-031 D3 と ADR-055 の固定 7 択）。 */
export type ActivityCategory =
  | "deliberating"
  | "stuck"
  | "external_material"
  | "conversation"
  | "away"
  | "working"
  | "cannot_answer";

/**
 * 7 択の表示の文（ADR-031 の「熟考・詰まり・外部資料・会話・離席・回答不能」に ADR-055 が「作業」を
 * 足した。`logger::ActivityCategory` の doc）。並びは ADR-055 D3（既存 5 つの位置と、回答不能が最後を保つ）。
 * ⚠️ 選択肢を足すには別 ADR が要る・自由記述を置かない（data-privacy ルール 7）。
 */
export const ACTIVITY_CHOICES: ReadonlyArray<{
  value: ActivityCategory;
  label: string;
  note: string;
}> = [
  { value: "deliberating", label: "熟考", note: "手は止まっていたが考えていた" },
  { value: "stuck", label: "詰まり", note: "先に進めずにいた" },
  { value: "external_material", label: "外部資料", note: "本・書類・画面などを読んでいた" },
  { value: "conversation", label: "会話", note: "会話・通話・打ち合わせをしていた" },
  { value: "away", label: "離席", note: "その場を離れていた" },
  { value: "working", label: "作業", note: "手を動かして作業を進めていた。入力・編集・単純作業を含む" },
  // ↑ カードは説明を（）で包むので、括弧を二重にしない（同意文書とフォームは「〜（入力・編集・単純作業を含む）」）。
  { value: "cannot_answer", label: "回答不能", note: "思い出せない・当てはまらない" },
];
