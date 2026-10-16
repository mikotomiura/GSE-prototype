// 手跡の背景の層の試作（spike・本線に入れない）。
// デスクトップの高さの透明な窓の全面に、等高線の波を描く（写し方は仮・見本台の背景のステージと同じ式）。
// 材料は直近 30 秒の打鍵の時刻だけ。1 秒ごとに目標を決め、その 1 秒のあいだに滑らかに近づく
// （表現の議論の判断 2・3: 打鍵だけで動かし推定を受け取らない・res=sec）。数値・文字は描かない。
// 計測を有効にして起動したときだけ、1 秒ごとに描いたフレームの数と刻みの遅れを Rust へ返す。
import { useEffect, useRef } from "react";
import { invoke } from "@tauri-apps/api/core";
import { getCurrentWebviewWindow } from "@tauri-apps/api/webviewWindow";

interface StageKeyPayload {
  measure: boolean;
}

/** 線の本数。 */
const LINES = 9;
/** 振れ幅の材料にする窓の長さ。 */
const WINDOW_MS = 30_000;
/** 止まったとみなすまでの間。 */
const STOP_MS = 2_000;
/** 1 秒の刻み。 */
const TICK_MS = 1_000;

export default function HandmarkStage() {
  const canvasRef = useRef<HTMLCanvasElement>(null);

  useEffect(() => {
    const canvas = canvasRef.current;
    const ctx = canvas?.getContext("2d") ?? null;
    if (canvas === null || ctx === null) {
      return;
    }
    let width = 0;
    let height = 0;
    const resize = (): void => {
      const dpr = Math.min(window.devicePixelRatio || 1, 2);
      width = window.innerWidth;
      height = window.innerHeight;
      canvas.width = Math.round(width * dpr);
      canvas.height = Math.round(height * dpr);
      ctx.setTransform(dpr, 0, 0, dpr, 0, 0);
    };
    resize();

    // 打鍵の時刻だけを持つ（キーの種類は受け取らない）。
    const presses: number[] = [];
    let measure = false;
    let amp = 0;
    let ampFrom = 0;
    let ampTo = 0;
    let phase = 0;
    let phaseFrom = 0;
    let phaseTo = 0;
    let tickAt = performance.now();
    let frame: number | null = null;
    let framesThisTick = 0;
    let tickIndex = 0;
    let disposed = false;
    let unlisten: (() => void) | null = null;

    const draw = (now: number): void => {
      const k = Math.min(1, (now - tickAt) / TICK_MS);
      const e = k * k * (3 - 2 * k);
      amp = ampFrom + (ampTo - ampFrom) * e;
      phase = phaseFrom + (phaseTo - phaseFrom) * e;
      ctx.clearRect(0, 0, width, height);
      for (let i = 0; i < LINES; i++) {
        const y0 = (height * (i + 1)) / (LINES + 1);
        const a = (6 + amp * height * 0.05) * (0.6 + 0.4 * Math.sin(i * 1.7));
        ctx.beginPath();
        for (let x = 0; x <= width; x += 6) {
          const y = y0 + a * Math.sin((x / width) * Math.PI * (2 + i * 0.35) + phase * (1 + i * 0.13) + i);
          if (x === 0) {
            ctx.moveTo(x, y);
          } else {
            ctx.lineTo(x, y);
          }
        }
        // 壁紙の明暗に依らず見えるよう、暗い太い線の上に白い細い線を重ねる（小面の乙と同じ考え）。
        ctx.globalAlpha = 0.16;
        ctx.strokeStyle = "#12161b";
        ctx.lineWidth = 3;
        ctx.stroke();
        ctx.globalAlpha = i % 3 === 0 ? 0.55 : 0.35;
        ctx.strokeStyle = "#ffffff";
        ctx.lineWidth = 1.2;
        ctx.stroke();
      }
      ctx.globalAlpha = 1;
      framesThisTick += 1;
    };

    // 移り変わりのあいだだけ描画のループを回す。目標に着いたら止める（負荷を抑える）。
    const loop = (now: number): void => {
      draw(now);
      frame = now - tickAt < TICK_MS ? requestAnimationFrame(loop) : null;
    };
    const ensureLoop = (): void => {
      if (frame === null) {
        frame = requestAnimationFrame(loop);
      }
    };

    let expectedTick = performance.now() + TICK_MS;
    const tick = (): void => {
      const now = performance.now();
      const lagMs = now - expectedTick;
      expectedTick = now + TICK_MS;
      while (presses.length > 0 && now - presses[0] > WINDOW_MS) {
        presses.shift();
      }
      const lastSec = presses.filter((t) => now - t <= TICK_MS).length;
      const stopped = presses.length === 0 || now - presses[presses.length - 1] > STOP_MS;
      ampFrom = amp;
      phaseFrom = phase;
      ampTo = stopped ? amp * 0.85 : Math.min(1, presses.length / 150);
      phaseTo = phase + (stopped ? 0 : Math.min(lastSec, 10) * 0.05);
      tickAt = now;
      // 目に見える変化があるときだけ描き直す。
      if (Math.abs(ampTo - ampFrom) > 1e-3 || phaseTo !== phaseFrom) {
        ensureLoop();
      }
      if (measure) {
        invoke("handmark_stage_tick", {
          tick: tickIndex,
          tMs: now,
          frames: framesThisTick,
          docVisible: document.visibilityState === "visible",
          lagMs,
        }).catch(() => {
          // 計測の書き込みの失敗は背景の動作に影響させない。
        });
      }
      tickIndex += 1;
      framesThisTick = 0;
    };
    const timer = window.setInterval(tick, TICK_MS);

    draw(performance.now());
    window.addEventListener("resize", resize);

    getCurrentWebviewWindow()
      .listen<StageKeyPayload>("handmark-stage-key", (event) => {
        measure = event.payload.measure;
        presses.push(performance.now());
      })
      .then((fn) => {
        if (disposed) {
          fn();
        } else {
          unlisten = fn;
        }
      })
      .catch(() => {
        // listen に失敗したら背景は動かないだけで、他に影響させない。
      });

    return () => {
      disposed = true;
      window.clearInterval(timer);
      window.removeEventListener("resize", resize);
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
        position: "fixed",
        inset: 0,
        width: "100vw",
        height: "100vh",
        display: "block",
        background: "transparent",
        pointerEvents: "none",
      }}
    />
  );
}
