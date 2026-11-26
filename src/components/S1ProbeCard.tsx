import React, { useEffect, useRef, useState } from "react";
import { invoke } from "@tauri-apps/api/core";
import { listen } from "@tauri-apps/api/event";
import type {
  ActivityCategory,
  ProbeStep,
  S1AnswerKeys,
  SkipReason,
} from "../probeTypes";
import { ACTIVITY_CHOICES } from "../probeTypes";

interface S1ProbeCardProps {
  probeId: string;
  /** いま尋ねている問い（backend が決める・ADR-057）。 */
  step: ProbeStep;
  /** カードの実寸（logical px）を親へ。非表示時は null。 */
  onResize: (size: { w: number; h: number } | null) => void;
  /** 記録できたら親に状態を取り直させる。 */
  onDone: () => void;
}

/** 問いが替わってから押下を受けるまでの間（ms）。ダブルクリックの間隔（100〜300 ms 程度）を越える長さ。 */
const STEP_SETTLE_MS = 400;

/** Q1・Q2 の問いの文と両端の言葉（ADR-057 で答え方だけを変えた。文は今までと同じ）。 */
const SCALE_QUESTIONS: Record<
  "q1" | "q2",
  { text: string; low: string; high: string }
> = {
  q1: {
    text: "どれだけ詰まっていた感覚ですか?",
    low: "詰まってない",
    high: "とても詰まった",
  },
  q2: {
    text: "どれだけ前に進んでいる感覚ですか?",
    low: "進んでない",
    high: "とても進んだ",
  },
};

/**
 * 段 1 のプローブのカード（ADR-057）。1 回押せば送る（「回答する」は無い）。
 * Q3（7 択）→ 詰まり・熟考・作業なら Q1 摩擦 → Q2 前進（どれも初期値なし）。
 * ★ 段と記録は backend が持つ（キーで答えても同じ道を通る）。ここはボタンを描いて押下を送るだけ。
 * ⚠️ 自由記述を置かない・理由を問わない（ADR-031 D3・data-privacy ルール 7）。
 */
const S1ProbeCard: React.FC<S1ProbeCardProps> = ({
  probeId,
  step,
  onResize,
  onDone,
}) => {
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [keys, setKeys] = useState<S1AnswerKeys | null>(null);
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

  useEffect(() => {
    let alive = true;
    // ★ 先に listen を張り終えてから今の状態を読む（間に来た emit を取りこぼさない）
    const unlisten = listen<S1AnswerKeys>("s1_answer_keys", (event) => {
      if (alive) setKeys(event.payload);
    });
    unlisten
      .then(() => invoke<S1AnswerKeys>("get_s1_answer_keys"))
      .then((k) => {
        if (alive) setKeys(k);
      })
      // ⚠️ 読めないときはキーの表示を出さない（ボタンで答えられる）
      .catch((e) => console.warn("s1 answer keys not read:", e));
    return () => {
      alive = false;
      unlisten.then((f) => f()).catch(() => undefined);
    };
  }, []);

  // 問いが替わった時刻（★ 直後の押下は前の問いへの連打とみなして捨てる・/cross-review の Codex）
  const stepChangedAt = useRef(0);
  // 問いが替わったら前の問いのエラーを消す
  useEffect(() => {
    setError(null);
    stepChangedAt.current = performance.now();
  }, [step]);

  const send = async (command: string, args: Record<string, unknown>) => {
    if (submitting) return;
    // ★ ダブルクリックの 2 回目が、替わったばかりの次の問いの同じ位置のボタンに入らないように
    if (performance.now() - stepChangedAt.current < STEP_SETTLE_MS) return;
    setSubmitting(true);
    setError(null);
    try {
      await invoke(command, args);
    } catch (e) {
      console.error(`${command} failed (keeping card for retry):`, e);
      setError(
        typeof e === "string"
          ? e
          : "記録に失敗しました。もう一度お試しください。",
      );
    } finally {
      setSubmitting(false);
      // ★ 成否に関わらず backend の状態を取り直す（キーで先に答えていた等で問いが替わっていることがある）
      onDone();
    }
  };

  const answerActivity = (category: ActivityCategory) =>
    send("answer_s1_probe", { probeId, step: "q3", category, scale: null });
  const answerScale = (value: number) =>
    send("answer_s1_probe", { probeId, step, category: null, scale: value });
  const skip = (reason: SkipReason) =>
    send("record_probe_skip", { probeId, skipReason: reason });

  // ★ 1 文字の記号（⌥）は数字に付け、名前（Ctrl＋Alt）は「＋」でつなぐ
  const keyLabel = (digit: number): string | null =>
    keys?.active
      ? keys.modifier.length === 1
        ? `${keys.modifier}${digit}`
        : `${keys.modifier}＋${digit}`
      : null;

  const keyBadge = (digit: number) => {
    const label = keyLabel(digit);
    return label ? (
      <span
        style={{
          fontSize: "0.7rem",
          opacity: 0.6,
          fontVariantNumeric: "tabular-nums",
        }}
      >
        {label}
      </span>
    ) : null;
  };

  const choiceButton: React.CSSProperties = {
    display: "flex",
    alignItems: "baseline",
    gap: "0.5rem",
    width: "100%",
    padding: "0.45rem 0.6rem",
    textAlign: "left",
    cursor: "pointer",
    fontSize: "0.86rem",
    color: "#f2f2f4",
    background: "rgba(255,255,255,0.08)",
    border: "1px solid rgba(255,255,255,0.16)",
    borderRadius: "8px",
  };

  const scaleButton: React.CSSProperties = {
    flex: 1,
    display: "flex",
    flexDirection: "column",
    alignItems: "center",
    gap: "0.1rem",
    padding: "0.55rem 0",
    cursor: "pointer",
    fontSize: "1rem",
    fontWeight: 600,
    color: "#f2f2f4",
    background: "rgba(255,255,255,0.08)",
    border: "1px solid rgba(255,255,255,0.16)",
    borderRadius: "8px",
  };

  const subButton: React.CSSProperties = {
    padding: "0.35rem 0.7rem",
    cursor: "pointer",
    fontSize: "0.78rem",
    color: "#d8d8de",
    background: "transparent",
    border: "1px solid rgba(255,255,255,0.22)",
    borderRadius: "6px",
  };

  const body =
    step === "q3" ? (
      <>
        <div style={{ fontSize: "0.86rem", margin: "0 0 0.45rem" }}>
          カードが出る前の30秒、何をしていましたか?
        </div>
        <div
          role="group"
          aria-label="何をしていたか"
          style={{ display: "grid", gap: "0.3rem" }}
        >
          {ACTIVITY_CHOICES.map((c, i) => (
            <button
              key={c.value}
              type="button"
              onClick={() => answerActivity(c.value)}
              disabled={submitting}
              style={choiceButton}
            >
              <strong style={{ minWidth: "3.2em" }}>{c.label}</strong>
              <span style={{ flex: 1, fontSize: "0.74rem", opacity: 0.72 }}>
                {c.note}
              </span>
              {keyBadge(i + 1)}
            </button>
          ))}
        </div>
      </>
    ) : (
      <>
        <div style={{ fontSize: "0.86rem", margin: "0 0 0.45rem" }}>
          {SCALE_QUESTIONS[step].text}
        </div>
        <div
          role="group"
          aria-label={SCALE_QUESTIONS[step].text}
          style={{ display: "flex", gap: "0.3rem" }}
        >
          {[1, 2, 3, 4, 5].map((v) => (
            <button
              key={v}
              type="button"
              onClick={() => answerScale(v)}
              disabled={submitting}
              style={scaleButton}
            >
              <span>{v}</span>
              {keyBadge(v)}
            </button>
          ))}
        </div>
        <div
          style={{
            display: "flex",
            justifyContent: "space-between",
            fontSize: "0.72rem",
            opacity: 0.7,
            marginTop: "0.25rem",
          }}
        >
          <span>{SCALE_QUESTIONS[step].low}</span>
          <span>{SCALE_QUESTIONS[step].high}</span>
        </div>
      </>
    );

  const closeKey = keyLabel(0);

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
        padding: "0.9rem 1rem",
        background: "rgba(28, 30, 38, 0.97)",
        color: "#f2f2f4",
        borderRadius: "12px",
        boxShadow: "0 8px 28px rgba(0,0,0,0.4)",
        fontSize: "0.9rem",
        zIndex: 9999,
      }}
    >
      <div
        style={{
          fontWeight: 600,
          fontSize: "0.8rem",
          opacity: 0.75,
          marginBottom: "0.45rem",
        }}
      >
        カードが出る前の30秒について
        {step === "q1" ? "（あと 2 問）" : step === "q2" ? "（あと 1 問）" : ""}
      </div>

      {body}

      <div
        style={{
          display: "flex",
          gap: "0.4rem",
          justifyContent: "flex-end",
          marginTop: "0.7rem",
        }}
      >
        {step === "q3" && (
          <button
            type="button"
            onClick={() => skip("dont_remember")}
            disabled={submitting}
            style={subButton}
          >
            思い出せない
          </button>
        )}
        <button
          type="button"
          onClick={() => skip("dismissed")}
          disabled={submitting}
          style={subButton}
        >
          閉じる{closeKey ? `（${closeKey}）` : ""}
        </button>
      </div>

      {error && (
        <div
          role="alert"
          style={{
            marginTop: "0.6rem",
            fontSize: "0.78rem",
            color: "#ffb4b4",
            lineHeight: 1.4,
          }}
        >
          {error}
        </div>
      )}
    </div>
  );
};

export default S1ProbeCard;
