import React, { useEffect, useRef, useState } from "react";
import { invoke } from "@tauri-apps/api/core";
import { listen } from "@tauri-apps/api/event";
import type { ProbeTriggered, SkipReason } from "../probeTypes";

interface ActiveProbe extends ProbeTriggered {
  shownAt: number; // カード表示時刻 (latency 計測の基点)
}

interface ProbeCardProps {
  // カードの表示/非表示を親 (Overlay) に伝え、cursor events と可視性を制御させる。
  onActiveChange: (active: boolean) => void;
  // カードの実描画サイズ (logical px) を親へ通知する。親は overlay 窓をこの実寸に縮め、
  // 透明余白 (Windows でクリックを奪う) を物理的に無くす。非表示時は null。
  onResize: (size: { w: number; h: number } | null) => void;
}

/// v0.3 較正のプローブ回答カード (Task C / §4)。
/// backend が emit する probe_triggered を listen し、Q1摩擦/Q2前進 (1-5) を回答 or skip する。
/// 原則5: モデル出力 (X/Y/p_stuck/推定状態) は一切表示しない。
const ProbeCard: React.FC<ProbeCardProps> = ({ onActiveChange, onResize }) => {
  const [probe, setProbe] = useState<ActiveProbe | null>(null);
  const [q1, setQ1] = useState(3); // 摩擦 (1=詰まってない .. 5=とても詰まった)
  const [q2, setQ2] = useState(3); // 前進 (1=まったく進んでない .. 5=とても進んだ)
  const [submitting, setSubmitting] = useState(false); // 送信中フラグ (二重送信防止)
  // 記録失敗時のインラインエラー文言。null = エラーなし。失敗時はカードを保持し
  // これを表示してボタン再押下でリトライさせる (較正データを静かに失わない + 死んだボタン化を防ぐ)。
  const [error, setError] = useState<string | null>(null);
  // listen コールバックは古い closure を捕捉するため、表示中判定は ref で行う。
  const probeRef = useRef<ActiveProbe | null>(null);
  // カード本体 (実寸測定用)。overlay 窓をこの実寸へ縮めるために親へ通知する。
  const cardRef = useRef<HTMLDivElement | null>(null);

  useEffect(() => {
    probeRef.current = probe;
    onActiveChange(probe !== null);
  }, [probe, onActiveChange]);

  // カード実寸を ResizeObserver で測り親へ通知 (overlay 窓を実寸に縮め透明余白を消す)。
  // 表示が消えたら null を通知。サイズ未変化なら通知しない (窓再配置の churn 抑制)。
  useEffect(() => {
    const el = cardRef.current;
    if (!probe || !el) {
      onResize(null);
      return;
    }
    const report = () => {
      // offsetWidth/Height は layout 寸法で CSS transform (pop-in の scale) の影響を受けない。
      // getBoundingClientRect だとアニメ中の縮小値を拾い窓が小さく確定→カード切れになる。
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
  }, [probe, onResize]);

  useEffect(() => {
    const unlisten = listen<ProbeTriggered>("probe_triggered", (event) => {
      // 既にカード表示中なら新規プローブは無視 (多重表示しない)。
      // 取りこぼしを可視化する (回答中に self_marker を押した等。MNAR 観点)。
      if (probeRef.current) {
        console.warn(
          "probe_triggered ignored: a probe card is already showing",
          event.payload.source
        );
        return;
      }
      setProbe({ ...event.payload, shownAt: Date.now() });
      setQ1(3);
      setQ2(3);
      setError(null); // 新規プローブ表示で前回のエラー表示をクリア。
    });
    return () => {
      unlisten.then((f) => f());
    };
  }, []);

  if (!probe) return null;

  const commonArgs = () => ({
    probeId: probe.probe_id,
    source: probe.source,
    windowStartMs: probe.analysis_window_start_ms,
    windowEndMs: probe.analysis_window_end_ms,
    latencyMs: Date.now() - probe.shownAt,
  });

  // 送信成功後にのみカードを閉じる。失敗 (例: log channel full) 時はカードを残し、
  // 較正データを静かに失わない (MNAR バイアス回避)。
  const submitAnswer = async () => {
    if (submitting) return; // 二重送信防止
    setSubmitting(true);
    setError(null);
    try {
      await invoke("record_realtime_answer", {
        ...commonArgs(),
        q1Friction: q1,
        q2Progress: q2,
      });
      setProbe(null);
    } catch (e) {
      console.error("record_realtime_answer failed (keeping card for retry):", e);
      setError("記録に失敗しました。もう一度お試しください。");
    } finally {
      setSubmitting(false);
    }
  };

  const submitSkip = async (reason: SkipReason) => {
    if (submitting) return; // 二重送信防止
    setSubmitting(true);
    setError(null);
    try {
      await invoke("record_realtime_skip", { ...commonArgs(), skipReason: reason });
      setProbe(null);
    } catch (e) {
      console.error("record_realtime_skip failed (keeping card for retry):", e);
      setError("記録に失敗しました。もう一度お試しください。");
    } finally {
      setSubmitting(false);
    }
  };

  // 注: この 1–5 スライダーは F3 リアルタイムプローブ (Q1摩擦/Q2前進) であり、X1 較正の
  // 正解ラベル。4 件法化した自作 TSE 尺度 (F2-C/F5・Form 側) とは別系統なので偶数化しない (FD10)。
  const slider = (
    value: number,
    setValue: (v: number) => void,
    lowLabel: string,
    highLabel: string
  ) => (
    <div style={{ margin: "0.4rem 0" }}>
      <input
        type="range"
        min={1}
        max={5}
        step={1}
        value={value}
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
        // overlay 窓の右上に密着 (窓は本カード実寸へ縮むため余白=透明クリック奪取を作らない)。
        position: "absolute",
        right: 0,
        top: 0,
        width: "320px",
        // maxHeight は viewport(100vh) 依存にしない: 窓を実寸へ縮めると 100vh も縮み、
        // maxHeight→content クランプ→さらに縮小…の無限ループになるため固定上限にする。
        // 通常画面では到達せず、極小画面でのみ効いて overflowY でスクロール可能に保つ。
        maxHeight: "600px",
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
      <div style={{ fontWeight: 600, marginBottom: "0.6rem" }}>
        直前の30秒について教えてください
      </div>

      <div style={{ fontSize: "0.82rem", marginBottom: "0.1rem" }}>
        Q1. どれだけ詰まっていた感覚ですか?
      </div>
      {slider(q1, setQ1, "詰まってない", "とても詰まった")}

      <div style={{ fontSize: "0.82rem", margin: "0.5rem 0 0.1rem" }}>
        Q2. どれだけ前に進んでいる感覚ですか?
      </div>
      {slider(q2, setQ2, "進んでない", "とても進んだ")}

      <div style={{ display: "flex", gap: "0.5rem", marginTop: "0.9rem" }}>
        <button
          onClick={submitAnswer}
          disabled={submitting}
          style={{ flex: 1, padding: "0.5rem", cursor: "pointer" }}
        >
          回答する
        </button>
        <button
          onClick={() => submitSkip("dont_remember")}
          disabled={submitting}
          style={{ padding: "0.5rem", cursor: "pointer" }}
          title="直前の状態を思い出せない"
        >
          思い出せない
        </button>
        <button
          onClick={() => submitSkip("dismissed")}
          disabled={submitting}
          style={{ padding: "0.5rem", cursor: "pointer" }}
          title="今は答えない"
        >
          ✕
        </button>
      </div>

      {/* 記録失敗時のインラインエラー。死んだボタンに見せず、再押下でリトライ可能と伝える。 */}
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

export default ProbeCard;
