import React, { useEffect, useRef, useState } from "react";
import { invoke } from "@tauri-apps/api/core";

interface DayQuestionCardProps {
  cardId: number;
  /** 翌日の拾い直し（「昨日の作業に」）。 */
  delayed: boolean;
  /** トレイの終了の補助（「答えて終了／答えずに終了」）。 */
  quitFlow: boolean;
  onResize: (size: { w: number; h: number } | null) => void;
  onDone: () => void;
}

/** 目盛りの両端の文（仮の文・decisions 判断 5）。 */
const SCALE: ReadonlyArray<{ value: number; label: string }> = [
  { value: 1, label: "まったく" },
  { value: 2, label: "" },
  { value: 3, label: "" },
  { value: 4, label: "" },
  { value: 5, label: "とても" },
];

/**
 * 段 1 の日の終わりの問い（ADR-048 D3）。★ 仮の文（`dq-draft-1`・UWES-3 由来・妥当性は無いものとして扱う）。
 * ⚠️ 自由記述を置かない。答えは 1..5 の 1 項目か、答えない。
 */
const DayQuestionCard: React.FC<DayQuestionCardProps> = ({ cardId, delayed, quitFlow, onResize, onDone }) => {
  const [value, setValue] = useState<number | null>(null);
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const shownAt = useRef(Date.now());
  const firstActionAt = useRef<number | null>(null);
  const cardRef = useRef<HTMLDivElement | null>(null);

  useEffect(() => {
    const el = cardRef.current;
    if (!el) return;
    const report = () => {
      const w = el.offsetWidth;
      const h = el.offsetHeight;
      if (w > 0 && h > 0) onResize({ w, h });
    };
    report();
    const ro = new ResizeObserver(report);
    ro.observe(el);
    return () => {
      ro.disconnect();
      onResize(null);
    };
  }, [onResize]);

  const markAction = () => {
    if (firstActionAt.current === null) firstActionAt.current = Date.now();
  };

  const send = async (motivation: number | null) => {
    if (submitting) return;
    markAction();
    setSubmitting(true);
    setError(null);
    const now = Date.now();
    const first = firstActionAt.current ?? now;
    try {
      await invoke("record_day_question", {
        cardId,
        motivation,
        latencyMs: first - shownAt.current,
        durationMs: now - first,
      });
      onDone();
    } catch (e) {
      console.error("record_day_question failed (keeping card for retry):", e);
      setError(typeof e === "string" ? e : "記録に失敗しました。もう一度お試しください。");
    } finally {
      setSubmitting(false);
    }
  };

  const question = delayed
    ? "昨日の作業にどのくらい熱意を持てましたか"
    : "今日の作業にどのくらい熱意を持てましたか";
  const answerLabel = quitFlow ? "答えて終了" : "答える";
  const skipLabel = quitFlow ? "答えずに終了" : delayed ? "答えない" : "今日は答えない";

  return (
    <div
      ref={cardRef}
      className="probe-card probe-card-pop"
      style={{
        position: "absolute",
        right: 0,
        top: 0,
        width: "320px",
        padding: "1rem 1.2rem",
        background: "rgba(28, 30, 38, 0.97)",
        color: "#f2f2f4",
        borderRadius: "12px",
        boxShadow: "0 8px 28px rgba(0,0,0,0.4)",
        fontSize: "0.9rem",
        zIndex: 9999,
      }}
    >
      <div style={{ fontWeight: 600, marginBottom: "0.6rem" }}>{question}</div>
      <div role="radiogroup" aria-label={question} style={{ display: "flex", gap: "0.3rem" }}>
        {SCALE.map((s) => (
          <button
            key={s.value}
            type="button"
            role="radio"
            aria-checked={value === s.value}
            onClick={() => {
              markAction();
              setValue(s.value);
            }}
            disabled={submitting}
            style={{
              flex: 1,
              padding: "0.4rem 0",
              cursor: "pointer",
              border: value === s.value ? "2px solid #8ab4ff" : "1px solid rgba(255,255,255,0.3)",
              borderRadius: "6px",
              background: value === s.value ? "rgba(138,180,255,0.25)" : "transparent",
              color: "#f2f2f4",
            }}
          >
            {s.value}
          </button>
        ))}
      </div>
      <div style={{ display: "flex", justifyContent: "space-between", fontSize: "0.72rem", opacity: 0.7, marginTop: "0.2rem" }}>
        <span>{SCALE[0].label}</span>
        <span>{SCALE[SCALE.length - 1].label}</span>
      </div>
      <div style={{ display: "flex", gap: "0.5rem", marginTop: "0.8rem" }}>
        <button
          type="button"
          onClick={() => send(value)}
          disabled={submitting || value === null}
          style={{ flex: 1, padding: "0.5rem", cursor: "pointer" }}
        >
          {answerLabel}
        </button>
        <button
          type="button"
          onClick={() => send(null)}
          disabled={submitting}
          style={{ padding: "0.5rem", cursor: "pointer" }}
        >
          {skipLabel}
        </button>
      </div>
      {error && (
        <div role="alert" style={{ marginTop: "0.6rem", fontSize: "0.78rem", color: "#ffb4b4", lineHeight: 1.4 }}>
          {error}
        </div>
      )}
    </div>
  );
};

export default DayQuestionCard;
