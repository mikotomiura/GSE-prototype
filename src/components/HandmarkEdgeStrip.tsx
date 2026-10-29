// 手跡の下の縁の帯の試作（spike・本線に入れない）。
// 主画面の下の縁の高さ 14 点の透明な窓に、揺れる線を描く（.steering/20261030-handmark-edge-strip-impl/）。
// 段 1 は線 1 本だけで、入力は受け取らない。1 秒に約 10 回描く。
// この窓は値を保存も返送もしない。推定は受け取らない。数値・文字は描かない。
import { useEffect, useRef } from "react";

/** 描く間隔（段 1 は入力が無いので、背景の入力が無い間と同じ 10 回/秒）。 */
const FRAME_MS = 100;
/** 線の濃さ（仮・設計の論点 5）。 */
const LINE_ALPHA = 0.7;

export default function HandmarkEdgeStrip() {
  const canvasRef = useRef<HTMLCanvasElement>(null);

  useEffect(() => {
    const canvas = canvasRef.current;
    const ctx = canvas?.getContext("2d") ?? null;
    if (canvas === null || ctx === null) {
      return;
    }
    let W = 0;
    let H = 0;
    const resize = (): void => {
      const dpr = Math.min(window.devicePixelRatio || 1, 2);
      W = window.innerWidth;
      H = window.innerHeight;
      canvas.width = Math.round(W * dpr);
      canvas.height = Math.round(H * dpr);
      ctx.setTransform(dpr, 0, 0, dpr, 0, 0);
    };
    resize();

    const draw = (now: number): void => {
      const t = now / 1000;
      ctx.clearRect(0, 0, W, H);
      ctx.beginPath();
      const step = 8;
      for (let x = 0; x <= W + step; x += step) {
        const y = H * 0.5 + H * 0.25 * Math.sin(x / 90 + t * 0.6) * Math.sin(x / 370 - t * 0.2);
        if (x === 0) ctx.moveTo(x, y);
        else ctx.lineTo(x, y);
      }
      // 背景の草と同じく、墨の太い線の上に白の細い線を重ね、壁紙や窓の明暗に依らず見えるようにする。
      ctx.globalAlpha = LINE_ALPHA * 0.4;
      ctx.strokeStyle = "#12161b";
      ctx.lineWidth = 3;
      ctx.stroke();
      ctx.globalAlpha = LINE_ALPHA;
      ctx.strokeStyle = "#ffffff";
      ctx.lineWidth = 1.2;
      ctx.stroke();
      ctx.globalAlpha = 1;
    };
    const timer = window.setInterval(() => draw(performance.now()), FRAME_MS);
    window.addEventListener("resize", resize);
    return () => {
      window.clearInterval(timer);
      window.removeEventListener("resize", resize);
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
