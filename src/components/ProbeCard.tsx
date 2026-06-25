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
}

/// v0.3 較正のプローブ回答カード (Task C / §4)。
/// backend が emit する probe_triggered を listen し、Q1摩擦/Q2前進 (1-5) を回答 or skip する。
/// 原則5: モデル出力 (X/Y/p_stuck/推定状態) は一切表示しない。
const ProbeCard: React.FC<ProbeCardProps> = ({ onActiveChange }) => {
  const [probe, setProbe] = useState<ActiveProbe | null>(null);
  const [q1, setQ1] = useState(3); // 摩擦 (1=詰まってない .. 5=とても詰まった)
  const [q2, setQ2] = useState(3); // 前進 (1=まったく進んでない .. 5=とても進んだ)
  const [submitting, setSubmitting] = useState(false); // 送信中フラグ (二重送信防止)
  // DIAG TEMP: クリック/ポインタが webview(DOM) に届いているかを白黒つける計器。
  // pointerDown = カード上の任意のポインタ押下、click = 「回答する」ボタンの onClick。
  // 数字が増えれば DOM まで届いている (原因は記録/ロジック側)、増えなければ届いていない
  // (= ウィンドウ構造のクリック配送問題)。検証後に削除する。
  const [diagPointer, setDiagPointer] = useState(0);
  const [diagClick, setDiagClick] = useState(0);
  // 記録失敗時のインラインエラー文言。null = エラーなし。失敗時はカードを保持し
  // これを表示してボタン再押下でリトライさせる (較正データを静かに失わない + 死んだボタン化を防ぐ)。
  const [error, setError] = useState<string | null>(null);
  // listen コールバックは古い closure を捕捉するため、表示中判定は ref で行う。
  const probeRef = useRef<ActiveProbe | null>(null);

  useEffect(() => {
    probeRef.current = probe;
    onActiveChange(probe !== null);
  }, [probe, onActiveChange]);

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
      className="probe-card probe-card-pop"
      onPointerDown={() => {
        setDiagPointer((n) => n + 1);
        console.log("[DIAG] probe card pointerDown");
      }}
      style={{
        position: "fixed",
        right: "1.25rem",
        top: "1.25rem",
        width: "320px",
        // box モード窓 (PROBE_BOX_H) からはみ出して回答ボタンが透過領域に隠れるのを防ぐ。
        maxHeight: "calc(100vh - 2.5rem)",
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

      {/* DIAG TEMP: クリック到達計器。検証後に削除する。 */}
      <div
        style={{
          margin: "0 0 0.6rem",
          padding: "0.3rem 0.5rem",
          background: "#7c3aed",
          color: "#fff",
          fontWeight: 700,
          borderRadius: "6px",
          textAlign: "center",
        }}
      >
        DIAG pointer:{diagPointer} / click:{diagClick}
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
          onClick={() => {
            // DIAG TEMP: onClick が発火したか (= クリックがボタンに届いたか) を計測。
            setDiagClick((n) => n + 1);
            console.log("[DIAG] probe 回答する onClick fired");
            void submitAnswer();
          }}
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
