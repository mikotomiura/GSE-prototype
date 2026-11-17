import React, { useEffect, useRef, useState } from "react";
import { invoke } from "@tauri-apps/api/core";
import type { ActivityCategory, SkipReason } from "../probeTypes";
import { ACTIVITY_CHOICES } from "../probeTypes";

interface S1ProbeCardProps {
  probeId: string;
  /** カードの実寸（logical px）を親へ。非表示時は null。 */
  onResize: (size: { w: number; h: number } | null) => void;
  /** 記録できたら親に状態を取り直させる。 */
  onDone: () => void;
}

/**
 * 段 1 のプローブのカード（3 問を 1 枚: 摩擦・前進・7 択・ADR-055）。
 * ★ 判断は backend（どのカードを出すか・`stratum`・窓）。ここは答えを送るだけ。
 * ⚠️ 自由記述を置かない・理由を問わない（ADR-031 D3・data-privacy ルール 7）。
 */
const S1ProbeCard: React.FC<S1ProbeCardProps> = ({ probeId, onResize, onDone }) => {
  const [q1, setQ1] = useState(3);
  const [q2, setQ2] = useState(3);
  const [category, setCategory] = useState<ActivityCategory | null>(null);
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const shownAt = useRef(Date.now());
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

  const submitAnswer = async () => {
    if (submitting || category === null) return;
    setSubmitting(true);
    setError(null);
    try {
      await invoke("record_probe_response", {
        probeId,
        q1Friction: q1,
        q2Progress: q2,
        category,
        latencyMs: Date.now() - shownAt.current,
      });
      onDone();
    } catch (e) {
      console.error("record_probe_response failed (keeping card for retry):", e);
      setError(typeof e === "string" ? e : "記録に失敗しました。もう一度お試しください。");
    } finally {
      setSubmitting(false);
    }
  };

  const submitSkip = async (reason: SkipReason) => {
    if (submitting) return;
    setSubmitting(true);
    setError(null);
    try {
      await invoke("record_probe_skip", {
        probeId,
        skipReason: reason,
        latencyMs: Date.now() - shownAt.current,
      });
      onDone();
    } catch (e) {
      console.error("record_probe_skip failed (keeping card for retry):", e);
      setError(typeof e === "string" ? e : "記録に失敗しました。もう一度お試しください。");
    } finally {
      setSubmitting(false);
    }
  };

  const slider = (
    value: number,
    setValue: (v: number) => void,
    lowLabel: string,
    highLabel: string,
    ariaLabel: string
  ) => (
    <div style={{ margin: "0.3rem 0" }}>
      <input
        type="range"
        min={1}
        max={5}
        step={1}
        value={value}
        aria-label={ariaLabel}
        onChange={(e) => setValue(Number(e.target.value))}
        style={{ width: "100%" }}
      />
      <div style={{ display: "flex", justifyContent: "space-between", fontSize: "0.72rem", opacity: 0.7 }}>
        <span>{lowLabel}</span>
        <strong style={{ opacity: 1 }}>{value}</strong>
        <span>{highLabel}</span>
      </div>
    </div>
  );

  return (
    <div
      ref={cardRef}
      className="probe-card probe-card-pop"
      style={{
        position: "absolute",
        right: 0,
        top: 0,
        width: "340px",
        maxHeight: "640px",
        overflowY: "auto",
        padding: "1rem 1.2rem",
        background: "rgba(28, 30, 38, 0.97)",
        color: "#f2f2f4",
        borderRadius: "12px",
        boxShadow: "0 8px 28px rgba(0,0,0,0.4)",
        fontSize: "0.9rem",
        zIndex: 9999,
      }}
    >
      <div style={{ fontWeight: 600, marginBottom: "0.5rem" }}>直前の30秒について教えてください</div>

      <div style={{ fontSize: "0.82rem" }}>Q1. どれだけ詰まっていた感覚ですか?</div>
      {slider(q1, setQ1, "詰まってない", "とても詰まった", "Q1 詰まり")}

      <div style={{ fontSize: "0.82rem", marginTop: "0.4rem" }}>Q2. どれだけ前に進んでいる感覚ですか?</div>
      {slider(q2, setQ2, "進んでない", "とても進んだ", "Q2 前進")}

      <div style={{ fontSize: "0.82rem", margin: "0.5rem 0 0.3rem" }}>Q3. 直前の30秒、何をしていましたか?（いくつか当てはまるときは、いちばん長かったもの。同時にしていたときは、詰まっていたなら詰まり、そうでなく手が動いていたなら作業）</div>
      <div role="radiogroup" aria-label="Q3 何をしていたか" style={{ display: "grid", gap: "0.25rem" }}>
        {ACTIVITY_CHOICES.map((c) => (
          <label
            key={c.value}
            style={{
              display: "flex",
              gap: "0.4rem",
              alignItems: "baseline",
              cursor: "pointer",
              fontSize: "0.82rem",
            }}
          >
            <input
              type="radio"
              name="s1-activity"
              value={c.value}
              checked={category === c.value}
              onChange={() => setCategory(c.value)}
            />
            <span>
              <strong>{c.label}</strong>
              <span style={{ opacity: 0.75 }}>（{c.note}）</span>
            </span>
          </label>
        ))}
      </div>

      <div style={{ display: "flex", gap: "0.5rem", marginTop: "0.8rem" }}>
        <button
          onClick={submitAnswer}
          disabled={submitting || category === null}
          style={{ flex: 1, padding: "0.5rem", cursor: "pointer" }}
          title={category === null ? "Q3 を選ぶと送れます" : undefined}
        >
          回答する
        </button>
        <button
          onClick={() => submitSkip("dont_remember")}
          disabled={submitting}
          style={{ padding: "0.5rem", cursor: "pointer" }}
        >
          思い出せない
        </button>
        <button
          onClick={() => submitSkip("dismissed")}
          disabled={submitting}
          style={{ padding: "0.5rem", cursor: "pointer" }}
        >
          閉じる
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

export default S1ProbeCard;
