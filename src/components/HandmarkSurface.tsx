// 手跡の案 A の小面の試作（spike・本線に入れない）。
// 打鍵のたびに中心の点から波紋を 1 つ広げて消す（表現の議論の判断 5: 28 px・250 ms・打ち切り・灰）。
// 式は見本のページの甲-2 と同じ。数値・文字は描かない（親タスク判断 16）。
// 計測を有効にして起動したときだけ、遅れと波紋の一生（描いた時刻と進み）を Rust へ返す。
import { useEffect, useRef } from "react";
import { invoke } from "@tauri-apps/api/core";
import { getCurrentWebviewWindow } from "@tauri-apps/api/webviewWindow";

interface HandmarkKeyPayload {
  seq: number;
  t_key_ms: number;
  measure: boolean;
}

/** 窓の一辺（Rust の SIDE と一致させる）。 */
const BOX_PX = 32;
/** 小面の大きさ（直径）。 */
const SIZE_PX = 28;
/** 波紋の動きの長さ。 */
const RIPPLE_MS = 250;

const COLORS = {
  light: { base: "#9aa3ab", hi: "#ffffff" },
  dark: { base: "#5e676f", hi: "#f2f4f6" },
} as const;

/** 描いている波紋。計測のために、最初と最後に描いたフレームの時刻と進みの最大を持つ。 */
interface Ripple {
  seq: number;
  startedAt: number;
  firstFrame: number | null;
  lastFrame: number | null;
  maxT: number;
  measure: boolean;
}

const ease = (t: number): number => 1 - (1 - t) * (1 - t);

/**
 * 終わった波紋を 1 行返す。打ち切られたときは clearedMs を null、
 * 描き終えたときは地だけを描いて描画を止めたフレームの時刻を渡す。
 */
function reportRipple(ripple: Ripple, truncated: boolean, clearedMs: number | null): void {
  if (!ripple.measure || ripple.firstFrame === null || ripple.lastFrame === null) {
    return;
  }
  invoke("handmark_spike_ripple", {
    seq: ripple.seq,
    startMs: ripple.firstFrame,
    endMs: ripple.lastFrame,
    maxT: ripple.maxT,
    truncated,
    clearedMs,
  }).catch(() => {
    // 計測の書き込みの失敗は小面の動作に影響させない。
  });
}

export default function HandmarkSurface() {
  const canvasRef = useRef<HTMLCanvasElement>(null);

  useEffect(() => {
    const canvas = canvasRef.current;
    const ctx = canvas?.getContext("2d") ?? null;
    if (canvas === null || ctx === null) {
      return;
    }
    const dpr = Math.min(window.devicePixelRatio || 1, 2);
    canvas.width = BOX_PX * dpr;
    canvas.height = BOX_PX * dpr;
    ctx.setTransform(dpr, 0, 0, dpr, 0, 0);

    const dark = window.matchMedia("(prefers-color-scheme: dark)");
    const center = BOX_PX / 2;
    const radius = SIZE_PX / 2;

    let ripple: Ripple | null = null;
    let frame: number | null = null;
    let unlisten: (() => void) | null = null;
    let disposed = false;

    const draw = (now: number): void => {
      const { base, hi } = dark.matches ? COLORS.dark : COLORS.light;
      ctx.clearRect(0, 0, BOX_PX, BOX_PX);
      ctx.fillStyle = base;
      ctx.beginPath();
      ctx.arc(center, center, radius * 0.32, 0, Math.PI * 2);
      ctx.fill();
      if (ripple === null) {
        return;
      }
      const t = (now - ripple.startedAt) / RIPPLE_MS;
      if (t > 1) {
        // 描き終えた。地だけを描いたこのフレームで止める。
        reportRipple(ripple, false, now);
        ripple = null;
        return;
      }
      const tc = Math.max(0, t);
      if (ripple.firstFrame === null) {
        ripple.firstFrame = now;
      }
      ripple.lastFrame = now;
      ripple.maxT = Math.max(ripple.maxT, tc);
      const e = ease(tc);
      ctx.globalAlpha = 1 - e;
      ctx.strokeStyle = hi;
      ctx.lineWidth = Math.max(1.2, radius * 0.12);
      ctx.beginPath();
      ctx.arc(center, center, radius * (0.36 + 0.7 * e), 0, Math.PI * 2);
      ctx.stroke();
      ctx.globalAlpha = 1;
    };

    // 描画のループは波紋があるあいだだけ回す。消えたら止める。
    const loop = (now: number): void => {
      draw(now);
      frame = ripple === null ? null : requestAnimationFrame(loop);
    };
    const ensureLoop = (): void => {
      if (frame === null) {
        frame = requestAnimationFrame(loop);
      }
    };

    draw(performance.now());
    const onScheme = (): void => draw(performance.now());
    dark.addEventListener("change", onScheme);

    getCurrentWebviewWindow()
      .listen<HandmarkKeyPayload>("handmark-key", (event) => {
        const { seq, t_key_ms, measure } = event.payload;
        // 続けて打ったら、前の波紋を打ち切って新しい起点から描き直す（波紋は常に 1 つ）。
        if (ripple !== null) {
          reportRipple(ripple, true, null);
        }
        ripple = {
          seq,
          startedAt: performance.now(),
          firstFrame: null,
          lastFrame: null,
          maxT: 0,
          measure,
        };
        ensureLoop();

        if (!measure) {
          return;
        }
        requestAnimationFrame(() => {
          requestAnimationFrame(() => {
            const latencyMs = Date.now() - t_key_ms;
            invoke("handmark_spike_latency", { seq, latencyMs }).catch(() => {
              // 計測の書き込みの失敗は小面の動作に影響させない。
            });
          });
        });
      })
      .then((fn) => {
        if (disposed) {
          fn();
        } else {
          unlisten = fn;
        }
      })
      .catch(() => {
        // listen に失敗したら小面は動かないだけで、他に影響させない。
      });

    return () => {
      disposed = true;
      dark.removeEventListener("change", onScheme);
      if (frame !== null) {
        cancelAnimationFrame(frame);
      }
      if (unlisten !== null) {
        unlisten();
      }
    };
  }, []);

  return (
    <canvas
      ref={canvasRef}
      style={{
        width: `${BOX_PX}px`,
        height: `${BOX_PX}px`,
        display: "block",
        background: "transparent",
        pointerEvents: "none",
      }}
    />
  );
}
