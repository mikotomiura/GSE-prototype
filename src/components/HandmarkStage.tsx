// 手跡の背景の層の試作（spike・本線に入れない）。
// デスクトップの高さの透明な窓の全面に、自然世界（霧・草・粒・波紋）を描く。写し方は見本 Version 5
// （枝 docs/tangibility-design の .steering/20261020-handmark-multi-input/handmark-nature-multi.html）と同じ。
// - 打鍵: 直近 30 秒の打鍵の時刻だけ。風（草のなびき・粒の横の流れ）。
// - カーソル: 近くの草が動いた向きへなびき、動かしている間だけ近くの粒が寄る。数秒で戻る。
// - クリック（左だけ）: その場に一回きりの波紋。枠は 6 で、1.6 秒で消す。
// - ホイール（macOS）: 粒全体の描く位置を縦にずらし、1 秒で半分に戻す。
// - 霧: どの入力にも依らない基層。帯は 3 本（見本は 4 本で、明るい壁紙で見えるのは 2 本だった。試視で見える帯を 1 本足した・判断 13）。
// 入力の跡も打鍵の風も無い間は、霧と粒の漂いだけを 1 秒に約 10 回描く（負荷を抑える・判断 10）。
// ポインタの値は Rust が読んで送る（窓はマウスを受けない）。この窓は値を保存も返送もしない
// （ADR-040 D2〜D4・検査は src-tauri/src/handmark_stage_guard.rs）。推定は受け取らない。数値・文字は描かない。
import { useEffect, useRef } from "react";
import { getCurrentWebviewWindow } from "@tauri-apps/api/webviewWindow";
import {
  addRipple,
  clearRipples,
  decayFactor,
  makeReceiver,
  makeRipples,
  receive,
  rippleAge,
  sweepRipples,
  tracesExpired,
  type PointerMessage,
} from "./handmarkStageTrace";

/** 打鍵を知らせるイベント名（src-tauri/src/handmark_stage_spike.rs）。 */
const KEY_EVENT = "handmark-stage-key";
/** ポインタを知らせるイベント名（src-tauri/src/handmark_stage_pointer.rs・この窓専用）。 */
const POINTER_EVENT = "handmark-stage-pointer";

// 打鍵の写し方（版 4 と同じ・強さ 1）。
const WINDOW_MS = 30_000;
const STOP_MS = 2_000;
/** 打鍵の数を数える窓（直近 1 秒）。 */
const TICK_MS = 1_000;
/** 風の目標を決める間隔（試視で版 4 の 1 秒は鈍いとされた・判断 12）。 */
const WIND_TICK_MS = 250;
const SPEED_PER_KEY = 0.05;
/** 1 秒の打鍵の数の頭打ち（版 4 は 10）。 */
const MAX_KEYS_PER_SEC = 14;
/** 風が最大になる速さ（版 4 は 0.4 = 毎秒 8 打。いまは毎秒 12 打）。 */
const FULL_WIND_SPEED = 0.6;
/** 霧の帯の本数と、いちばん上の帯の高さ・帯の間隔（画面の高さに対する割合）。 */
const FOG_BANDS = 3;
const FOG_TOP = 0.12;
const FOG_STEP = 0.18;
/** 打鍵が無い 0.25 秒ごとの減り（版 4 の 1 秒に 0.6 倍とほぼ同じ）。 */
const WIND_DECAY = 0.88;
const MIN_SPEED = 0.002;
const IRREG_MS = 10_000;
const IRREG_MIN_GAPS = 4;

// カーソルの写し方（見本 Version 5）。距離・上限は画面の高さに対する割合。
const CURSOR_R = 0.16;
const CURSOR_HALF_MS = 700;
const CURSOR_PUSH = 6;
const CURSOR_MAX = 0.9;
/** これより遅い速さ（画面の高さ/秒）は止まっているとみなす。 */
const CURSOR_STILL = 0.01;
const MOTE_R = 0.18;
const MOTE_HALF_MS = 900;
const MOTE_PULL = 0.0006;
const MOTE_MAX = 0.08;
// ホイールの写し方（見本 Version 5）。
const WHEEL_STEP = 0.05;
const WHEEL_MAX = 0.15;
const WHEEL_HALF_MS = 1000;
/** 入力が無い間の描く間隔。 */
const IDLE_FRAME_MS = 100;
/** 最後の入力からこの間は、跡が戻りきるまで毎フレーム描く。 */
const ACTIVE_HOLD_MS = 4000;

interface Blade {
  x: number;
  y: number;
  h: number;
  w: number;
  seed: number;
  depth: number;
  push: number;
}

interface Mote {
  x: number;
  y: number;
  r: number;
  seed: number;
  k: number;
  ox: number;
  oy: number;
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

    // ---- 自然世界の要素（数は固定） ----
    let blades: Blade[] = [];
    let motes: Mote[] = [];
    const buildWorld = (): void => {
      let seed = 11;
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
            push: 0,
          });
        }
      }
      motes = [];
      for (let i = 0; i < 140; i++) {
        motes.push({ x: rnd() * W, y: rnd() * H * 0.9, r: 1 + rnd() * 2.2, seed: rnd() * 6.28, k: 0.5 + rnd(), ox: 0, oy: 0 });
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
      buildWorld();
    };
    resize();

    // ---- 打鍵の材料（時刻だけ・版 4 と同じ） ----
    const presses: number[] = [];
    let speed = 0;
    let speedFrom = 0;
    let speedTo = 0;
    let phase = 0;
    let irreg = 0;
    let irregFrom = 0;
    let irregTo = 0;
    let tickAt = performance.now();


    const irregularity = (now: number): number | null => {
      let n = 0;
      let sum = 0;
      let sumSq = 0;
      for (let i = 1; i < presses.length; i++) {
        if (now - presses[i] > IRREG_MS) continue;
        const g = presses[i] - presses[i - 1];
        if (g < STOP_MS) {
          n += 1;
          sum += g;
          sumSq += g * g;
        }
      }
      if (n < IRREG_MIN_GAPS) return null;
      const mean = sum / n;
      const sd = Math.sqrt(Math.max(0, sumSq / n - mean * mean));
      return Math.max(0, Math.min(1, (sd / mean - 0.1) / 0.9));
    };

    // ---- ポインタ。最後の 1 点と、数秒で 0 へ戻る値だけを持つ（列を持たない） ----
    const cursor = { x: 0, y: 0, px: 0, py: 0, inside: false, fresh: false, vx: 0, vy: 0 };
    const rippleSlots = makeRipples();
    const receiver = makeReceiver();
    // ホイール: 粒全体の縦のずれ 1 つ。
    let wheelOff = 0;
    let wheelShown = 0;
    let lastInputAt = -Infinity;
    // ポインタの最後の入力（打鍵は含めない。打ち続けている間も、ポインタの跡は消す）。
    let lastPointerAt = -Infinity;
    let tracesCleared = true;

    const clearCursorTrace = (): void => {
      for (const bl of blades) bl.push = 0;
      for (const m of motes) {
        m.ox = 0;
        m.oy = 0;
      }
      cursor.x = 0;
      cursor.y = 0;
      cursor.px = 0;
      cursor.py = 0;
      cursor.inside = false;
      cursor.fresh = false;
      cursor.vx = 0;
      cursor.vy = 0;
    };

    const onPointer = (m: PointerMessage): void => {
      const now = performance.now();
      const v = receive(receiver, m, now);
      if (v.cursorOff) clearCursorTrace();
      if (v.clickOff) clearRipples(rippleSlots);
      if (v.wheelOff) {
        wheelOff = 0;
        wheelShown = 0;
      }
      if (!v.use) return;
      lastInputAt = now;
      lastPointerAt = now;
      tracesCleared = false;
      kick();
      // 主画面の左下が原点の座標を、窓の左上が原点に直す（窓は主画面の全体を覆う）。
      const x = m.x;
      const y = H - m.y;
      const inside = x >= 0 && x <= W && y >= 0 && y <= H;
      if (m.moved && receiver.cursorOn) {
        cursor.x = x;
        cursor.y = y;
        cursor.inside = inside;
      }
      if (m.clicked && receiver.clickOn && inside) {
        addRipple(rippleSlots, x, y, now);
      }
      if (m.wheel !== 0 && receiver.wheelOn) {
        // 下へ回すと粒は上へ（見本と同じ）。
        wheelOff = Math.max(-WHEEL_MAX, Math.min(WHEEL_MAX, wheelOff - m.wheel * WHEEL_STEP));
      }
    };

    // dt は動きに使う（頭打ちあり）。elapsed は戻っていく値の減衰に使う実際の経過時間（頭打ちなし）。
    const updatePointer = (dt: number, elapsed: number): void => {
      // 描画のたびに最後の 1 点を見て、前の点との差から速さを出す。平滑化は実時間。
      if (receiver.cursorOn && cursor.inside && cursor.fresh) {
        const v = ((cursor.x - cursor.px) / Math.max(dt, 1)) * 1000;
        const w = ((cursor.y - cursor.py) / Math.max(dt, 1)) * 1000;
        const a = 1 - Math.pow(0.6, dt / 16.7);
        cursor.vx += (v - cursor.vx) * a;
        cursor.vy += (w - cursor.vy) * a;
        if (Math.hypot(cursor.vx, cursor.vy) < CURSOR_STILL * H) {
          cursor.vx = 0;
          cursor.vy = 0;
        }
      } else {
        cursor.vx = 0;
        cursor.vy = 0;
      }
      cursor.px = cursor.x;
      cursor.py = cursor.y;
      cursor.fresh = cursor.inside;
      wheelOff *= decayFactor(WHEEL_HALF_MS, elapsed);
      wheelShown += (wheelOff - wheelShown) * (1 - Math.exp(-elapsed / 150));
    };

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

    // 基層の漂い（版 4 と同じ）。drift は入力に依らない基層の時間。
    let drift = 0;
    const fogEdge = (b: number, x: number, lower: boolean): number => {
      const a = H * 0.055 * (1 + b * 0.2);
      return lower
        ? a * fbm((x / W) * 1.3 + b * 3.1 + 40, drift * 0.09 + b * 23)
        : a * fbm((x / W) * 1.6 + b * 7.3, drift * 0.105 * (1 + b * 0.2) + b * 11);
    };
    const baseSway = (seed: number): number => fbm(seed * 13.7, drift * 0.35) * 0.1;
    const baseLift = (seed: number): number => fbm(seed * 9.1 + 300, drift * 0.25) * 6;
    const gustAt = (x: number): number => Math.max(0, 1 + 0.9 * irreg * fbm((x / W) * 2.2 + 500, drift * 1.1));

    const drawNature = (dt: number, elapsed: number, slow: number): void => {
      const wind = Math.min(1, speed / FULL_WIND_SPEED);
      // 「動きを減らす」は基層の漂いと粒の流れだけを遅くする（跡の減衰は実時間のまま）。
      const mdt = dt * slow;
      drift += mdt / 1000;

      // 霧の帯。基層だけで動き、どの入力でも変わらない。
      const step = Math.max(8, Math.round(10 * S));
      for (let b = 0; b < FOG_BANDS; b++) {
        const yc = H * (FOG_TOP + b * FOG_STEP);
        ctx.beginPath();
        for (let x = 0; x <= W + step; x += step) ctx.lineTo(x, yc + fogEdge(b, x, false));
        for (let x = W + step; x >= 0; x -= step) ctx.lineTo(x, yc + H * 0.05 + fogEdge(b, x, true));
        ctx.closePath();
        // 墨の薄い塗りの上に白の塗りを重ね、壁紙の明暗に依らずどの帯も見えるようにする（草の線の二重と同じ考え）。
        // 見本は白と墨の交互で、明るい壁紙では白の帯が透明に見えた（判断 14）。
        ctx.fillStyle = "rgba(18,22,27,0.08)";
        ctx.fill();
        ctx.fillStyle = "rgba(255,255,255,0.12)";
        ctx.fill();
      }

      // 漂う粒。基層の流れ＋打鍵の風（横）＋カーソルへ寄るずれ＋ホイールの縦のずれ（描く位置だけ）。
      const lift = receiver.wheelOn ? wheelShown * H : 0;
      const mdecay = decayFactor(MOTE_HALF_MS, elapsed);
      const mR = MOTE_R * H;
      const mMax = MOTE_MAX * H;
      const pullMotes = receiver.cursorOn && (cursor.vx !== 0 || cursor.vy !== 0);
      for (const m of motes) {
        m.ox *= mdecay;
        m.oy *= mdecay;
        if (pullMotes) {
          const dx = cursor.x - (m.x + m.ox);
          const dy = cursor.y - (m.y + m.oy + lift * m.k);
          const d = Math.hypot(dx, dy);
          if (d < mR && d > 1) {
            const f = 1 - d / mR;
            // 寄る量はカーソルの速さに比例。残りの距離に対する上限を実時間で決め、カーソルを追い越さない。
            const pull = Math.min(d * (1 - Math.pow(0.8, dt / 16.7)), Math.hypot(cursor.vx, cursor.vy) * f * MOTE_PULL * dt);
            m.ox += (dx / d) * pull;
            m.oy += (dy / d) * pull;
            const o = Math.hypot(m.ox, m.oy);
            if (o > mMax) {
              m.ox *= mMax / o;
              m.oy *= mMax / o;
            }
          }
        }
        const vx = (6 + 70 * wind * gustAt(m.x)) * m.k * S;
        const vy = baseLift(m.seed) * S;
        m.x += (vx * mdt) / 1000;
        m.y += (vy * mdt) / 1000;
        // 端から反対側へ回り込んだ粒は、カーソルのずれを持ち越さない。
        if (m.x > W + 10) {
          m.x -= W + 20;
          m.ox = 0;
          m.oy = 0;
        }
        if (m.y < -10) {
          m.y += H * 0.9;
          m.ox = 0;
          m.oy = 0;
        } else if (m.y > H * 0.9 + 10) {
          m.y -= H * 0.9;
          m.ox = 0;
          m.oy = 0;
        }
        const x = m.x + m.ox;
        const y = m.y + m.oy + lift * m.k;
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

      // 草の群れ。基層の小さな揺れ＋打鍵の風＋カーソルの押し（近くの草だけ・数秒で戻る）。
      const decay = decayFactor(CURSOR_HALF_MS, elapsed);
      const R = CURSOR_R * H;
      const cv = receiver.cursorOn ? Math.max(-1, Math.min(1, cursor.vx / (W * 0.4))) : 0;
      for (const bl of blades) {
        bl.push *= decay;
        if (cv !== 0) {
          const d = Math.hypot(cursor.x - bl.x, cursor.y - (bl.y - bl.h * 0.5));
          if (d < R) {
            const f = (1 - d / R) * (1 - d / R);
            bl.push = Math.max(-CURSOR_MAX, Math.min(CURSOR_MAX, bl.push + (cv * f * CURSOR_PUSH * dt) / 1000));
          }
        }
        const sway = baseSway(bl.seed);
        const gust = wind * gustAt(bl.x) * (0.32 + 0.22 * Math.sin((bl.x / W) * 9 - phase * 3 + bl.depth));
        const bend = (sway + gust + bl.push) * bl.h;
        ctx.beginPath();
        ctx.moveTo(bl.x, bl.y);
        ctx.quadraticCurveTo(bl.x + bend * 0.25, bl.y - bl.h * 0.55, bl.x + bend, bl.y - bl.h + Math.abs(bend) * 0.25);
        dualStroke(bl.w * S, 0.14, 0.45 + bl.depth * 0.2);
      }
    };

    // 波紋。押した点から 2 重の輪が広がり、1.6 秒で消える。
    const drawRipples = (now: number): void => {
      for (const rp of rippleSlots.ripples) {
        const t = rippleAge(rp, now);
        if (t === null) continue;
        const e = 1 - Math.pow(1 - t, 3);
        const a = Math.pow(1 - t, 1.5);
        for (const [k, lag] of [
          [1, 0],
          [0.62, 0.18],
        ]) {
          const tt = Math.max(0, e - lag);
          if (tt <= 0) continue;
          ctx.beginPath();
          ctx.ellipse(rp.x, rp.y, (8 + 150 * tt) * S * k, (5 + 90 * tt) * S * k, 0, 0, Math.PI * 2);
          dualStroke(1.3 * S, 0.18 * a, 0.7 * a);
        }
      }
    };

    const tick = (): void => {
      const now = performance.now();
      while (presses.length > 0 && now - presses[0] > WINDOW_MS) presses.shift();
      const lastSec = presses.filter((t) => now - t <= TICK_MS).length;
      speedFrom = speed;
      irregFrom = irreg;
      const rate = Math.min(lastSec, MAX_KEYS_PER_SEC) * SPEED_PER_KEY;
      const next = lastSec > 0 ? 0.5 * speed + 0.5 * rate : speed * WIND_DECAY;
      speedTo = next < MIN_SPEED ? 0 : next;
      const ir = irregularity(now);
      // 打鍵の間合いが足りない間の減りは、版 4 の 1 秒に 0.85 倍と同じ（0.25 秒ごとに 0.96 倍）。
      irregTo = ir === null ? irreg * 0.96 : 0.5 * irreg + 0.5 * ir;
      if (irregTo < 0.002) irregTo = 0;
      tickAt = now;
      // 描画が止まっている間（全画面のアプリなど）も、寿命を過ぎた波紋の枠を消す。
      sweepRipples(rippleSlots, now);
      // 同じく、入力が途絶えて十分経ったら、戻っていく値と最後の一点を消す（D4）。
      if (!tracesCleared && tracesExpired(lastPointerAt, now)) {
        clearCursorTrace();
        wheelOff = 0;
        wheelShown = 0;
        tracesCleared = true;
      }
    };
    const timer = window.setInterval(tick, WIND_TICK_MS);

    let last: number | null = null;
    let frame: number | null = null;
    let idleTimer: number | null = null;
    const busy = (now: number): boolean =>
      speed > 0 ||
      speedTo > 0 ||
      now - lastInputAt < ACTIVE_HOLD_MS ||
      rippleSlots.ripples.some((rp) => rippleAge(rp, now) !== null);
    // 入力が来たら、絞っていた描画をすぐ戻す。
    const kick = (): void => {
      if (idleTimer !== null) {
        window.clearTimeout(idleTimer);
        idleTimer = null;
        frame = requestAnimationFrame(loop);
      }
    };
    const loop = (now: number): void => {
      // 描画が止まっていた間の分は、動きには進めない（dt）。戻っていく値は実時間で減らす（elapsed）。
      const elapsed = last === null ? 16 : now - last;
      const dt = Math.min(elapsed, 100);
      last = now;
      const k = Math.min(1, (now - tickAt) / WIND_TICK_MS);
      const e = k * k * (3 - 2 * k);
      speed = speedFrom + (speedTo - speedFrom) * e;
      irreg = irregFrom + (irregTo - irregFrom) * e;
      phase += (speed * dt) / 1000;
      updatePointer(dt, elapsed);
      sweepRipples(rippleSlots, now);
      ctx.clearRect(0, 0, W, H);
      drawNature(dt, elapsed, reduceMotion ? 0.3 : 1);
      drawRipples(now);
      if (busy(now)) {
        frame = requestAnimationFrame(loop);
      } else {
        idleTimer = window.setTimeout(() => {
          idleTimer = null;
          frame = requestAnimationFrame(loop);
        }, IDLE_FRAME_MS);
      }
    };
    frame = requestAnimationFrame(loop);

    const onResize = (): void => {
      resize();
      last = null;
    };
    window.addEventListener("resize", onResize);

    let disposed = false;
    let unlistenKey: (() => void) | null = null;
    let unlistenPointer: (() => void) | null = null;
    const win = getCurrentWebviewWindow();
    // 打鍵の時刻だけを持つ（キーの種類は受け取らない）。listen に失敗したら背景は動かないだけ。
    win
      .listen(KEY_EVENT, () => {
        const now = performance.now();
        presses.push(now);
        lastInputAt = now;
        kick();
      })
      .then((fn) => {
        if (disposed) fn();
        else unlistenKey = fn;
      })
      .catch(() => {});
    win
      .listen<PointerMessage>(POINTER_EVENT, (event) => {
        onPointer(event.payload);
      })
      .then((fn) => {
        if (disposed) fn();
        else unlistenPointer = fn;
      })
      .catch(() => {});

    return () => {
      disposed = true;
      window.clearInterval(timer);
      window.removeEventListener("resize", onResize);
      if (frame !== null) {
        cancelAnimationFrame(frame);
      }
      if (idleTimer !== null) {
        window.clearTimeout(idleTimer);
      }
      if (unlistenKey !== null) unlistenKey();
      if (unlistenPointer !== null) unlistenPointer();
      clearRipples(rippleSlots);
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
