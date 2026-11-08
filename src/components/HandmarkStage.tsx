// 手跡の背景の層(段 1 の後期・ADR-051)。デスクトップの高さの透明な窓の全面に、自然世界(霧・草・粒)を描く。
// 写し方は試作(見本 Version 5)の打鍵の部分と同じ。ポインタ・クリック・ホイールの処理は無い(PR 3・5)。
// - 風・位相・漂い・配置の種は、Rust が打鍵の時刻だけから 250 ms ごとに計算して送る(StageState)。
//   この窓は performance.now() や描画の間隔(dt)から位相・漂い・位置を積まない。粒の位置も草の揺れも、
//   届いた drift・phase・layout_seed の関数で、届いた状態へ 250 ms かけて線形に寄せるだけ
//   (描画の回数は見た目に影響しない・机上の描き直しと一致する)。
// - 霧: どの入力にも依らない基層(漂いは Rust の drift)。
// 窓は何も保存せず、何も返さない。推定は受け取らない。数値・文字は描かない。
import { useEffect, useRef } from "react";
import { getCurrentWebviewWindow } from "@tauri-apps/api/webviewWindow";

/** 状態を知らせるイベント名(src-tauri/src/handmark_stage.rs の STATE_EVENT)。閉じたときは null。 */
const STATE_EVENT = "handmark-state";

/** 状態が届く間隔(analysis/handmark/state.rs の TICK_MS)。受け取った状態へこの時間をかけて寄せる。 */
const STATE_TICK_MS = 250;
/** 風が最大になる速さ(毎秒 12 打)。 */
const FULL_WIND_SPEED = 0.6;
/** 霧の帯の本数と、いちばん上の帯の高さ・帯の間隔(画面の高さに対する割合)。 */
const FOG_BANDS = 3;
const FOG_TOP = 0.12;
const FOG_STEP = 0.18;
/** 入力が無い間の描く間隔。 */
const IDLE_FRAME_MS = 100;

/** Rust の StageState(src-tauri/src/analysis/handmark/state.rs)。 */
interface StageStateMessage {
  speed: number;
  irreg: number;
  phase: number;
  drift: number;
  layout_seed: number;
}

interface Shown {
  speed: number;
  irreg: number;
  phase: number;
  drift: number;
}

interface Blade {
  x: number;
  y: number;
  h: number;
  w: number;
  seed: number;
  depth: number;
}

interface Mote {
  /** 初期位置(layout_seed から決まる)。 */
  x0: number;
  y0: number;
  r: number;
  seed: number;
  k: number;
}

function finite(v: number, fallback: number): number {
  return Number.isFinite(v) ? v : fallback;
}

// ---- 周期の無いノイズ（版 4 と同じ） ----
function hash2(i: number, j: number): number {
  let h = Math.imul(i | 0, 0x27d4eb2d) ^ Math.imul(((j | 0) + 0x3c6ef372) | 0, 0x165667b1);
  h = Math.imul(h ^ (h >>> 15), 0x85ebca6b);
  h = Math.imul(h ^ (h >>> 13), 0xc2b2ae35);
  return (h ^ (h >>> 16)) >>> 0;
}
function grad(i: number, j: number, x: number, y: number): number {
  const a = (hash2(i, j) / 4294967296) * Math.PI * 2;
  return Math.cos(a) * x + Math.sin(a) * y;
}
function fade(t: number): number {
  return t * t * t * (t * (t * 6 - 15) + 10);
}
function noise2(x: number, y: number): number {
  const ix = Math.floor(x);
  const iy = Math.floor(y);
  const fx = x - ix;
  const fy = y - iy;
  const u = fade(fx);
  const v = fade(fy);
  const n00 = grad(ix, iy, fx, fy);
  const n10 = grad(ix + 1, iy, fx - 1, fy);
  const n01 = grad(ix, iy + 1, fx, fy - 1);
  const n11 = grad(ix + 1, iy + 1, fx - 1, fy - 1);
  const nx0 = n00 + (n10 - n00) * u;
  const nx1 = n01 + (n11 - n01) * u;
  return (nx0 + (nx1 - nx0) * v) * 1.41;
}
function fbm(x: number, y: number): number {
  return noise2(x, y) * 0.68 + noise2(x * 2.07 + 17.3, y * 2.13 + 5.1) * 0.32;
}

export default function HandmarkStage() {
  const canvasRef = useRef<HTMLCanvasElement>(null);

  useEffect(() => {
    const canvas = canvasRef.current;
    const ctx = canvas?.getContext("2d") ?? null;
    if (canvas === null || ctx === null) {
      return;
    }
    const reduceMotion = window.matchMedia("(prefers-reduced-motion: reduce)").matches;

    let W = 0;
    let H = 0;
    let S = 1;

    // ---- 自然世界の要素(数は固定・配置は layout_seed から) ----
    let blades: Blade[] = [];
    let motes: Mote[] = [];
    let layoutSeed = -1;
    const buildWorld = (seedIn: number): void => {
      layoutSeed = seedIn;
      // 1 以上 2147483646 以下の種にする
      let seed = (seedIn % 2147483646) + 1;
      const rnd = (): number => {
        seed = (seed * 16807) % 2147483647;
        return seed / 2147483647;
      };
      blades = [];
      const rows = 5;
      for (let r = 0; r < rows; r++) {
        const depth = r / (rows - 1);
        const y = H * (0.66 + depth * 0.32);
        const n = 34 + r * 10;
        for (let i = 0; i < n; i++) {
          blades.push({
            x: ((i + rnd() * 0.9) / n) * W,
            y: y + (rnd() - 0.5) * H * 0.03,
            h: H * (0.05 + rnd() * 0.05) * (0.55 + depth * 0.6),
            w: 0.55 + depth * 0.75,
            seed: rnd() * 6.28,
            depth,
          });
        }
      }
      motes = [];
      for (let i = 0; i < 140; i++) {
        motes.push({ x0: rnd() * W, y0: rnd() * H * 0.9, r: 1 + rnd() * 2.2, seed: rnd() * 6.28, k: 0.5 + rnd() });
      }
    };

    const resize = (): void => {
      const dpr = Math.min(window.devicePixelRatio || 1, 2);
      W = window.innerWidth;
      H = window.innerHeight;
      canvas.width = Math.round(W * dpr);
      canvas.height = Math.round(H * dpr);
      ctx.setTransform(dpr, 0, 0, dpr, 0, 0);
      S = H / 900;
      buildWorld(layoutSeed < 0 ? 11 : layoutSeed);
    };
    resize();

    // ---- 状態(Rust から届く)。from から to へ STATE_TICK_MS かけて線形に寄せる ----
    let active = false;
    let from: Shown = { speed: 0, irreg: 0, phase: 0, drift: 0 };
    let to: Shown = { speed: 0, irreg: 0, phase: 0, drift: 0 };
    let shown: Shown = { speed: 0, irreg: 0, phase: 0, drift: 0 };
    let recvAt = performance.now();

    const dualStroke = (width: number, darkA: number, lightA: number): void => {
      ctx.globalAlpha = darkA;
      ctx.strokeStyle = "#12161b";
      ctx.lineWidth = width * 2.5;
      ctx.stroke();
      ctx.globalAlpha = lightA;
      ctx.strokeStyle = "#ffffff";
      ctx.lineWidth = width;
      ctx.stroke();
      ctx.globalAlpha = 1;
    };

    // 基層の漂い。drift は入力に依らない基層の時間(Rust が決める)。
    const fogEdge = (b: number, x: number, lower: boolean, drift: number): number => {
      const a = H * 0.055 * (1 + b * 0.2);
      return lower
        ? a * fbm((x / W) * 1.3 + b * 3.1 + 40, drift * 0.09 + b * 23)
        : a * fbm((x / W) * 1.6 + b * 7.3, drift * 0.105 * (1 + b * 0.2) + b * 11);
    };
    const baseSway = (seed: number, drift: number): number => fbm(seed * 13.7, drift * 0.35) * 0.1;
    /** 粒の縦のゆらぎ。drift だけの関数(積み上げない)。 */
    const moteBob = (seed: number, drift: number): number => fbm(seed * 9.1 + 300, drift * 0.25);
    const gustAt = (x: number, drift: number, irreg: number): number =>
      Math.max(0, 1 + 0.9 * irreg * fbm((x / W) * 2.2 + 500, drift * 1.1));

    const drawNature = (calm: number): void => {
      const { speed, irreg, phase } = shown;
      // 「動きを減らす」は基層の漂いと粒の流れを遅くする(係数を掛けるだけ・積まない)。
      const drift = shown.drift * calm;
      const flow = phase * calm;
      const wind = Math.min(1, speed / FULL_WIND_SPEED);

      // 霧の帯。基層だけで動き、どの入力でも変わらない。
      const step = Math.max(8, Math.round(10 * S));
      for (let b = 0; b < FOG_BANDS; b++) {
        const yc = H * (FOG_TOP + b * FOG_STEP);
        ctx.beginPath();
        for (let x = 0; x <= W + step; x += step) ctx.lineTo(x, yc + fogEdge(b, x, false, drift));
        for (let x = W + step; x >= 0; x -= step) ctx.lineTo(x, yc + H * 0.05 + fogEdge(b, x, true, drift));
        ctx.closePath();
        // 墨の薄い塗りの上に白の塗りを重ね、壁紙の明暗に依らずどの帯も見えるようにする。
        ctx.fillStyle = "rgba(18,22,27,0.08)";
        ctx.fill();
        ctx.fillStyle = "rgba(255,255,255,0.12)";
        ctx.fill();
      }

      // 漂う粒。位置は drift(基層の流れ)と phase(打鍵の風の積分)の関数で、幅で折り返す。
      //   横のずれ = (基層 6/秒 × drift + 打鍵の風 70/秒 × phase/FULL_WIND_SPEED) × 粒ごとの係数。
      const span = W + 20;
      for (const m of motes) {
        const dx = (6 * drift + (70 * flow) / FULL_WIND_SPEED) * m.k * S;
        const x = ((((m.x0 + dx) % span) + span) % span) - 10;
        const y = m.y0 + 40 * S * moteBob(m.seed, drift);
        const r = m.r * S;
        ctx.beginPath();
        ctx.arc(x, y, r * 1.9, 0, Math.PI * 2);
        ctx.fillStyle = "rgba(18,22,27,0.14)";
        ctx.fill();
        ctx.beginPath();
        ctx.arc(x, y, r, 0, Math.PI * 2);
        ctx.fillStyle = "rgba(255,255,255,0.7)";
        ctx.fill();
      }

      // 草の群れ。基層の小さな揺れ＋打鍵の風。
      for (const bl of blades) {
        const sway = baseSway(bl.seed, drift);
        const gust = wind * gustAt(bl.x, drift, irreg) * (0.32 + 0.22 * Math.sin((bl.x / W) * 9 - phase * 3 + bl.depth));
        const bend = (sway + gust) * bl.h;
        ctx.beginPath();
        ctx.moveTo(bl.x, bl.y);
        ctx.quadraticCurveTo(bl.x + bend * 0.25, bl.y - bl.h * 0.55, bl.x + bend, bl.y - bl.h + Math.abs(bend) * 0.25);
        dualStroke(bl.w * S, 0.14, 0.45 + bl.depth * 0.2);
      }
    };

    // 届いた状態を受け取り、いま見せている値からその状態へ寄せ始める。null は窓が閉じたこと。
    const onState = (msg: StageStateMessage | null): void => {
      if (msg === null) {
        active = false;
        ctx.clearRect(0, 0, W, H);
        return;
      }
      const next: Shown = {
        speed: Math.max(0, finite(msg.speed, 0)),
        irreg: Math.max(0, Math.min(1, finite(msg.irreg, 0))),
        phase: finite(msg.phase, 0),
        drift: finite(msg.drift, 0),
      };
      // 種が替わったとき(日が変わった・取り直した)は、寄せずにそのまま置く。
      const seedChanged = Number.isFinite(msg.layout_seed) && msg.layout_seed !== layoutSeed;
      if (seedChanged) {
        buildWorld(msg.layout_seed);
      }
      if (!active || seedChanged) {
        // 開いたとき・種が替わったときは、現在値をそのまま置く。
        from = next;
        shown = next;
        active = true;
        kick();
      } else {
        from = shown;
      }
      to = next;
      recvAt = performance.now();
    };

    let frame: number | null = null;
    let idleTimer: number | null = null;
    const loop = (now: number): void => {
      frame = null;
      if (!active) {
        return;
      }
      const k = Math.min(1, (now - recvAt) / STATE_TICK_MS);
      shown = {
        speed: from.speed + (to.speed - from.speed) * k,
        irreg: from.irreg + (to.irreg - from.irreg) * k,
        phase: from.phase + (to.phase - from.phase) * k,
        drift: from.drift + (to.drift - from.drift) * k,
      };
      ctx.clearRect(0, 0, W, H);
      drawNature(reduceMotion ? 0.3 : 1);
      if (shown.speed > 0 || to.speed > 0) {
        frame = requestAnimationFrame(loop);
      } else {
        // 風が無い間は霧と粒の漂いだけを 1 秒に約 10 回描く(負荷を抑える)。
        idleTimer = window.setTimeout(() => {
          idleTimer = null;
          frame = requestAnimationFrame(loop);
        }, IDLE_FRAME_MS);
      }
    };
    // 風が起きたら、絞っていた描画をすぐ戻す。
    function kick(): void {
      if (idleTimer !== null) {
        window.clearTimeout(idleTimer);
        idleTimer = null;
      }
      if (frame === null) {
        frame = requestAnimationFrame(loop);
      }
    }

    const onResize = (): void => {
      resize();
    };
    window.addEventListener("resize", onResize);

    let disposed = false;
    let unlisten: (() => void) | null = null;
    const win = getCurrentWebviewWindow();
    // listen に失敗したら背景は動かないだけ。
    win
      .listen<StageStateMessage | null>(STATE_EVENT, (event) => {
        onState(event.payload);
      })
      .then((fn) => {
        if (disposed) fn();
        else unlisten = fn;
      })
      .catch(() => {});

    return () => {
      disposed = true;
      active = false;
      window.removeEventListener("resize", onResize);
      if (frame !== null) cancelAnimationFrame(frame);
      if (idleTimer !== null) window.clearTimeout(idleTimer);
      if (unlisten !== null) unlisten();
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
