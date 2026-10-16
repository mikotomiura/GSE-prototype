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
/** 直近 1 秒の打鍵 1 つあたりの位相の速さ（ラジアン毎秒・前の版の 1 秒の進みと同じ量）。 */
const SPEED_PER_KEY = 0.05;
/** これより遅くなったら止める。 */
const MIN_SPEED = 0.002;
/** 振れ幅 1 のときの線の揺れ（画面の高さに対する割合）。 */
const AMP_GAIN = 0.05;

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
    // 位相は描くたびに速さ × 経過時間で進める（チョイチョイ打っても流れが途切れない・判断 3）。
    // 速さの目標は 1 秒ごとに決め（res=sec）、その 1 秒のあいだに滑らかに移す。
    let phase = 0;
    let speed = 0;
    let speedFrom = 0;
    let speedTo = 0;
    let lastFrameAt: number | null = null;
    let tickAt = performance.now();
    // 移り変わりを始めた刻みだけ期限を延ばす（毎秒の刻みと切り離して、止まるべきときに確実に止める）。
    let transitionUntil = 0;
    let frame: number | null = null;
    let framesThisTick = 0;
    let tickIndex = 0;
    let disposed = false;
    let unlisten: (() => void) | null = null;

    const draw = (now: number): void => {
      const k = Math.min(1, (now - tickAt) / TICK_MS);
      const e = k * k * (3 - 2 * k);
      amp = ampFrom + (ampTo - ampFrom) * e;
      speed = speedFrom + (speedTo - speedFrom) * e;
      // 描画が止まっていた間（全画面のアプリなど）の分は進めない。
      const dt = lastFrameAt === null ? 0 : Math.min(now - lastFrameAt, 100);
      lastFrameAt = now;
      phase += (speed * dt) / 1000;
      ctx.clearRect(0, 0, width, height);
      for (let i = 0; i < LINES; i++) {
        const y0 = (height * (i + 1)) / (LINES + 1);
        const a = (6 + amp * height * AMP_GAIN) * (0.6 + 0.4 * Math.sin(i * 1.7));
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

    // 流れているあいだと、振れ幅の移り変わりのあいだだけ描画のループを回す（負荷を抑える）。
    const loop = (now: number): void => {
      draw(now);
      if (now < transitionUntil || speed > 0) {
        frame = requestAnimationFrame(loop);
      } else {
        frame = null;
        lastFrameAt = null;
      }
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
      speedFrom = speed;
      ampTo = stopped ? amp * 0.85 : Math.min(1, presses.length / 150);
      // 振れ幅の変化が 1 画素に満たなくなったら 0 に切る（見えない変化のために描き続けない）。
      if (stopped && ampTo * height * AMP_GAIN < 0.5) {
        ampTo = 0;
      }
      // 直近 1 秒に打鍵があれば、その数の速さへ半分だけ寄せる。無ければ 0.6 倍ずつ落とす（数秒で止まる）。
      const rate = Math.min(lastSec, 10) * SPEED_PER_KEY;
      const nextSpeed = lastSec > 0 ? 0.5 * speed + 0.5 * rate : speed * 0.6;
      speedTo = nextSpeed < MIN_SPEED ? 0 : nextSpeed;
      tickAt = now;
      // 目に見える変化（0.5 画素以上）があるときだけ描き直す。
      if (Math.abs(ampTo - ampFrom) * height * AMP_GAIN > 0.5 || speedFrom > 0 || speedTo > 0) {
        transitionUntil = now + TICK_MS;
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
    // canvas の大きさを変えると中身が消えるので、描き直す。止まっているときは位相を進めない。
    const onResize = (): void => {
      resize();
      draw(performance.now());
      if (frame === null) {
        lastFrameAt = null;
      }
    };
    window.addEventListener("resize", onResize);

    // 計測するかは起動時に問い合わせる（最初の打鍵の前の秒も記録する）。
    invoke<boolean>("handmark_stage_measure_enabled")
      .then((on) => {
        measure = measure || on;
      })
      .catch(() => {
        // 問い合わせの失敗は背景の動作に影響させない（最初の打鍵で分かる）。
      });

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
      window.removeEventListener("resize", onResize);
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
