// 手跡の背景の層の描画(純関数・手跡の PR 4・ADR-051 決めずに残すもの 2)。
// 画面(HandmarkStage.tsx)と机上の道具(experiments/20261115-handmark-leak-desk/scripts/pixels.mjs)が
// 同じ関数を呼ぶ(写像を 1 つに保つ)。React・Tauri・performance・Date・Math.random を使わない。
// 入力は、そのときに見せる状態(寄せた後)・場(寄せた後)・波紋の経過(0〜1)・大きさだけ。何も積まない。
import { BOX_W, sampleField } from "./handmarkStageTrace.ts";
import type { Field } from "./handmarkStageTrace.ts";

/** 風が最大になる速さ(毎秒 12 打)。 */
export const FULL_WIND_SPEED = 0.6;
/** 霧の帯の本数と、いちばん上の帯の高さ・帯の間隔(画面の高さに対する割合)。 */
const FOG_BANDS = 3;
const FOG_TOP = 0.12;
const FOG_STEP = 0.18;

/** 描くのに使う 2D の文脈の部分(画面の canvas と、机上の node の canvas の両方が満たす)。 */
export type StageCtx = Pick<
  CanvasRenderingContext2D,
  | "beginPath"
  | "moveTo"
  | "lineTo"
  | "closePath"
  | "quadraticCurveTo"
  | "arc"
  | "ellipse"
  | "fill"
  | "stroke"
  | "clearRect"
  | "globalAlpha"
  | "fillStyle"
  | "strokeStyle"
  | "lineWidth"
>;

/** そのときに見せる状態(Rust の StageState から layout_seed を除いたもの)。 */
export interface Shown {
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

/** 自然世界の要素(数は固定・配置は layout_seed と大きさから)。 */
export interface World {
  readonly layoutSeed: number;
  readonly blades: readonly Blade[];
  readonly motes: readonly Mote[];
}

/** 描く大きさ(CSS の px)。`S = H / 900`。 */
export interface View {
  W: number;
  H: number;
  S: number;
}

/** 波紋 1 つ(正準の箱の位置と、0〜1 の経過)。 */
export interface RippleView {
  x: number;
  y: number;
  t: number;
}

export function viewOf(W: number, H: number): View {
  return { W, H, S: H / 900 };
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

/** 配置を作る。`seedIn` は Rust の layout_seed。 */
export function buildWorld(seedIn: number, W: number, H: number): World {
  // 1 以上 2147483646 以下の種にする
  let seed = (seedIn % 2147483646) + 1;
  const rnd = (): number => {
    seed = (seed * 16807) % 2147483647;
    return seed / 2147483647;
  };
  const blades: Blade[] = [];
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
  const motes: Mote[] = [];
  for (let i = 0; i < 140; i++) {
    motes.push({ x0: rnd() * W, y0: rnd() * H * 0.9, r: 1 + rnd() * 2.2, seed: rnd() * 6.28, k: 0.5 + rnd() });
  }
  return { layoutSeed: seedIn, blades, motes };
}

function dualStroke(ctx: StageCtx, width: number, darkA: number, lightA: number): void {
  ctx.globalAlpha = darkA;
  ctx.strokeStyle = "#12161b";
  ctx.lineWidth = width * 2.5;
  ctx.stroke();
  ctx.globalAlpha = lightA;
  ctx.strokeStyle = "#ffffff";
  ctx.lineWidth = width;
  ctx.stroke();
  ctx.globalAlpha = 1;
}

/** 霧・粒・草を描く。`calm` は「動きを減らす」の係数(1 か 0.3)。 */
export function drawNature(ctx: StageCtx, world: World, view: View, shown: Shown, field: Field, calm: number): void {
  const { W, H, S } = view;
  const { speed, irreg, phase } = shown;
  // 「動きを減らす」は基層の漂いと粒の流れを遅くする(係数を掛けるだけ・積まない)。
  const drift = shown.drift * calm;
  const flow = phase * calm;
  const wind = Math.min(1, speed / FULL_WIND_SPEED);

  // 基層の漂い。drift は入力に依らない基層の時間(Rust が決める)。
  const fogEdge = (b: number, x: number, lower: boolean): number => {
    const a = H * 0.055 * (1 + b * 0.2);
    return lower
      ? a * fbm((x / W) * 1.3 + b * 3.1 + 40, drift * 0.09 + b * 23)
      : a * fbm((x / W) * 1.6 + b * 7.3, drift * 0.105 * (1 + b * 0.2) + b * 11);
  };
  const baseSway = (seed: number): number => fbm(seed * 13.7, drift * 0.35) * 0.1;
  /** 粒の縦のゆらぎ。drift だけの関数(積み上げない)。 */
  const moteBob = (seed: number): number => fbm(seed * 9.1 + 300, drift * 0.25);
  const gustAt = (x: number): number => Math.max(0, 1 + 0.9 * irreg * fbm((x / W) * 2.2 + 500, drift * 1.1));

  // 霧の帯。基層だけで動き、どの入力でも変わらない。
  const step = Math.max(8, Math.round(10 * S));
  for (let b = 0; b < FOG_BANDS; b++) {
    const yc = H * (FOG_TOP + b * FOG_STEP);
    ctx.beginPath();
    for (let x = 0; x <= W + step; x += step) ctx.lineTo(x, yc + fogEdge(b, x, false));
    for (let x = W + step; x >= 0; x -= step) ctx.lineTo(x, yc + H * 0.05 + fogEdge(b, x, true));
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
  for (const m of world.motes) {
    const dx = (6 * drift + (70 * flow) / FULL_WIND_SPEED) * m.k * S;
    const x0 = ((((m.x0 + dx) % span) + span) % span) - 10;
    const y0 = m.y0 + 40 * S * moteBob(m.seed);
    // 跡の場: いまの位置で読み、描く位置に足す(粒の本体の位置は積まない)。
    const pulled = sampleField(field, (x0 / W) * BOX_W, y0 / H);
    const x = x0 + pulled.pullX * H;
    const y = y0 + pulled.pullY * H;
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
  for (const bl of world.blades) {
    const sway = baseSway(bl.seed);
    const gust = wind * gustAt(bl.x) * (0.32 + 0.22 * Math.sin((bl.x / W) * 9 - phase * 3 + bl.depth));
    // 跡の場: 草 1 本の根元と先の中ほどの正準の位置で読み、倒しに足す。
    const pushed = sampleField(field, (bl.x / W) * BOX_W, (bl.y - bl.h / 2) / H).bend;
    const bend = (sway + gust + pushed) * bl.h;
    ctx.beginPath();
    ctx.moveTo(bl.x, bl.y);
    ctx.quadraticCurveTo(bl.x + bend * 0.25, bl.y - bl.h * 0.55, bl.x + bend, bl.y - bl.h + Math.abs(bend) * 0.25);
    dualStroke(ctx, bl.w * S, 0.14, 0.45 + bl.depth * 0.2);
  }
}

/** 波紋。押した点から 2 重の輪が広がり、経過 1 で消える。位置は正準の箱から画面へ戻す。 */
export function drawRipples(ctx: StageCtx, view: View, ripples: readonly RippleView[]): void {
  const { W, H, S } = view;
  const ring = (px: number, py: number, e: number, a: number, k: number, lag: number): void => {
    const tt = Math.max(0, e - lag);
    if (tt <= 0) return;
    ctx.beginPath();
    ctx.ellipse(px, py, (8 + 150 * tt) * S * k, (5 + 90 * tt) * S * k, 0, 0, Math.PI * 2);
    dualStroke(ctx, 1.3 * S, 0.18 * a, 0.7 * a);
  };
  for (const rp of ripples) {
    const t = rp.t;
    if (!(t >= 0 && t < 1)) continue;
    const px = (rp.x / BOX_W) * W;
    const py = rp.y * H;
    const e = 1 - Math.pow(1 - t, 3);
    const a = Math.pow(1 - t, 1.5);
    ring(px, py, e, a, 1, 0);
    ring(px, py, e, a, 0.62, 0.18);
  }
}

/** 1 枚を描く(消してから霧・粒・草・波紋の順)。 */
export function drawFrame(
  ctx: StageCtx,
  world: World,
  view: View,
  shown: Shown,
  field: Field,
  ripples: readonly RippleView[],
  calm: number,
): void {
  ctx.clearRect(0, 0, view.W, view.H);
  drawNature(ctx, world, view, shown, field, calm);
  drawRipples(ctx, view, ripples);
}
