// 手跡の止まりの層の描画(純関数・ADR-056・.steering/20261121-handmark-stopped-state-prototype/)。
// 画面(HandmarkStage.tsx)が handmarkStageDraw.ts の drawFrame の後に呼ぶ。机上の道具(experiments/20261121-handmark-stopped-desk/scripts/overlay.mjs)も同じ順に呼ぶ。
// React・Tauri・performance・Date・Math.random を使わない。入力は、そのときに見せる止まりの層(寄せた後)・
// 配置・大きさだけ。何も積まない。
// - 見えの度合い v は Rust が決める(止まりの始まりからの短い立ち上がりだけ・止まりの長さを持たない)。
// - 動きは Rust の ambient(日の種と絶対の時刻から作る記憶の短い値)だけで決まる。時刻の関数(sin(t) など)を
//   使わない。大きさ・速さ・明るさ・数を v 以外で変えない。衰えや疲れの形・評価の色を使わない。
import type { StageCtx, View, World } from "./handmarkStageDraw.ts";

/** 見た目の形(Rust の StoppedForm)。 */
export type StoppedForm = "band" | "motes" | "wind";

/** そのときに見せる止まりの層(Rust の StoppedFrame)。 */
export interface StoppedShown {
  v: number;
  ambient: readonly [number, number, number];
  form: StoppedForm;
  strength: number;
}

/** 届いた値を確かめて、描ける形にする(形が知らないもの・値が有限でないものは null)。 */
export function parseStopped(msg: unknown): StoppedShown | null {
  if (typeof msg !== "object" || msg === null) return null;
  const m = msg as { v?: unknown; ambient?: unknown; form?: unknown; strength?: unknown };
  if (m.form !== "band" && m.form !== "motes" && m.form !== "wind") return null;
  // 値を読むだけ(列を作らない・窓の列の検査 handmark_guard.rs の `the_window_lists_only_named_slots`)。
  // 添字で読む(配列でない値が届いても分割代入で落ちない)。
  const amb = m.ambient instanceof Object ? (m.ambient as ReadonlyArray<unknown>) : null;
  if (amb === null || amb.length !== 3) return null;
  const a0 = amb[0];
  const a1 = amb[1];
  const a2 = amb[2];
  const num = (x: unknown): x is number => typeof x === "number" && Number.isFinite(x);
  if (!num(m.v) || !num(m.strength) || !num(a0) || !num(a1) || !num(a2)) return null;
  const clamp = (x: number, lo: number, hi: number): number => Math.max(lo, Math.min(hi, x));
  return {
    v: clamp(m.v, 0, 1),
    ambient: [clamp(a0, -1, 1), clamp(a1, -1, 1), clamp(a2, -1, 1)],
    form: m.form,
    strength: clamp(m.strength, 0, 1),
  };
}

/** from から to へ k(0〜1)だけ寄せる。形と強さは to のもの(切り替えは研究者の設定で、寄せない)。 */
export function lerpStopped(from: StoppedShown, to: StoppedShown, k: number): StoppedShown {
  const t = Math.max(0, Math.min(1, k));
  const l = (a: number, b: number): number => a + (b - a) * t;
  return {
    v: l(from.v, to.v),
    ambient: [l(from.ambient[0], to.ambient[0]), l(from.ambient[1], to.ambient[1]), l(from.ambient[2], to.ambient[2])],
    form: to.form,
    strength: to.strength,
  };
}

/** 見えない(v か強さが 0)。 */
export function stoppedIsInvisible(s: StoppedShown | null): boolean {
  return s === null || s.v <= 0 || s.strength <= 0;
}

/** 帯: 草と粒の場の下を流れる淡い 1 本の帯。高さ・傾き・反りが ambient で動く。 */
function drawBand(ctx: StageCtx, view: View, s: StoppedShown, alpha: number, calm: number): void {
  const { W, H, S } = view;
  const [a0, a1, a2] = s.ambient;
  const yc = H * (0.5 + 0.07 * a0 * calm);
  const tilt = H * 0.05 * a1 * calm;
  const bow = H * 0.04 * a2 * calm;
  const thick = H * 0.045;
  const step = Math.max(8, Math.round(12 * S));
  const yAt = (x: number): number => {
    const u = x / W - 0.5;
    return yc + tilt * 2 * u + bow * (1 - 4 * u * u);
  };
  ctx.beginPath();
  for (let x = 0; x <= W + step; x += step) ctx.lineTo(x, yAt(x));
  for (let x = W + step; x >= 0; x -= step) ctx.lineTo(x, yAt(x) + thick);
  ctx.closePath();
  ctx.globalAlpha = alpha;
  ctx.fillStyle = "rgba(18,22,27,0.10)";
  ctx.fill();
  ctx.fillStyle = "rgba(255,255,255,0.22)";
  ctx.fill();
  ctx.globalAlpha = 1;
}

/** 粒の漂い: 配置の粒の一部(数は固定)の位置に、ambient でゆっくりずれる淡い輪を重ねる。 */
const VISITOR_STRIDE = 6;
function drawMotes(ctx: StageCtx, world: World, view: View, s: StoppedShown, alpha: number, calm: number): void {
  const { W, H, S } = view;
  const [a0, a1, a2] = s.ambient;
  for (let i = 0; i < world.motes.length; i += VISITOR_STRIDE) {
    const m = world.motes[i];
    const c = Math.cos(m.seed);
    const sn = Math.sin(m.seed);
    const x = m.x0 + W * 0.05 * (a0 * c + a1 * sn) * calm;
    const y = m.y0 + H * 0.04 * (a1 * c - a2 * sn) * calm;
    const r = (m.r + 2.5) * S;
    ctx.beginPath();
    ctx.arc(x, y, r, 0, Math.PI * 2);
    ctx.globalAlpha = alpha;
    ctx.strokeStyle = "#12161b";
    ctx.lineWidth = 2.2 * S;
    ctx.stroke();
    ctx.strokeStyle = "#ffffff";
    ctx.lineWidth = 1 * S;
    ctx.stroke();
    ctx.globalAlpha = 1;
  }
}

/** 風の向きの揺らぎ: 上の空に、向きと位置が ambient で揺らぐ細い流れの線(本数は固定)。 */
const STREAKS = 9;
function drawWind(ctx: StageCtx, view: View, s: StoppedShown, alpha: number, calm: number): void {
  const { W, H, S } = view;
  const [a0, a1, a2] = s.ambient;
  const angle = 0.5 * a0 * calm;
  const dx = Math.cos(angle);
  const dy = Math.sin(angle);
  const len = W * 0.16;
  for (let i = 0; i < STREAKS; i++) {
    // 位置は格子に置き、ambient で横と縦に少しずらす(時刻では動かない)。
    const gx = ((i % 3) + 0.5) / 3;
    const gy = (Math.floor(i / 3) + 0.5) / 3;
    const x = W * (gx + 0.06 * a1 * calm);
    const y = H * (0.1 + 0.45 * gy + 0.04 * a2 * calm);
    ctx.beginPath();
    ctx.moveTo(x - (dx * len) / 2, y - (dy * len) / 2);
    ctx.quadraticCurveTo(x, y - H * 0.012 * a2 * calm, x + (dx * len) / 2, y + (dy * len) / 2);
    ctx.globalAlpha = alpha;
    ctx.strokeStyle = "#12161b";
    ctx.lineWidth = 2.6 * S;
    ctx.stroke();
    ctx.strokeStyle = "#ffffff";
    ctx.lineWidth = 1.1 * S;
    ctx.stroke();
    ctx.globalAlpha = 1;
  }
}

/** 止まりの層を重ねる(消さない・drawFrame の後に呼ぶ)。`calm` は「動きを減らす」の係数(1 か 0.3)。 */
export function drawStopped(
  ctx: StageCtx,
  world: World,
  view: View,
  stopped: StoppedShown | null,
  calm: number,
): void {
  if (stopped === null || stoppedIsInvisible(stopped)) return;
  const alpha = Math.max(0, Math.min(1, stopped.v * stopped.strength));
  switch (stopped.form) {
    case "band":
      drawBand(ctx, view, stopped, alpha, calm);
      return;
    case "motes":
      drawMotes(ctx, world, view, stopped, alpha, calm);
      return;
    case "wind":
      drawWind(ctx, view, stopped, alpha, calm);
      return;
  }
}
