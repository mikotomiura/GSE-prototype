// 手跡の下の縁の帯の試作（spike・本線に入れない）。
// 主画面の下の縁の高さ 14 点の透明な窓に、風で揺れる線 1 本・その下の薄い霧 1 本・粒を少し描く
// （.steering/20261030-handmark-edge-strip-impl/・設計のタスクの論点 2〜5）。
// - 風: 背景の層と同じ目標を Rust から受け取る（src-tauri/src/handmark_wind.rs・判断 1）。
// - 打鍵の合図: 描画を起こすだけ（キーの種類は受け取らない）。
// - カーソル: 座標は受け取らず、帯への近さの数 1 つだけを受け取って薄くする（判断 2）。
// - 描く回数: 最後の入力から 4 秒の間は 1 秒に約 30 回、それ以外は約 10 回。帯が全部覆われたら止める。
// この窓は値を保存も返送もしない（検査は src-tauri/src/handmark_stage_guard.rs）。推定は受け取らない。数値・文字は描かない。
import { useEffect, useRef } from "react";
import { getCurrentWebviewWindow } from "@tauri-apps/api/webviewWindow";

/** 打鍵の合図（src-tauri/src/handmark_stage_spike.rs）。 */
const KEY_EVENT = "handmark-stage-key";
/** 風の目標（src-tauri/src/handmark_stage_spike.rs）。 */
const WIND_EVENT = "handmark-wind";
/** 帯へのカーソルの近さ 0〜10（src-tauri/src/handmark_stage_pointer.rs・この窓専用）。 */
const NEAR_EVENT = "handmark-strip-near";
/** 帯が見えているか（src-tauri/src/handmark_edge_strip.rs・occlusionState）。 */
const VISIBLE_EVENT = "handmark-strip-visible";

/** 受け取った風の目標へ寄せる時間（handmark_wind.rs の TICK_MS）。 */
const WIND_TICK_MS = 250;
/** 風が最大になる速さ（背景と同じ）。 */
const FULL_WIND_SPEED = 0.6;
/** 入力がある間と無い間の描く間隔（論点 3）。 */
const ACTIVE_FRAME_MS = 33;
const IDLE_FRAME_MS = 100;
/** 最後の入力からこの間は、入力がある間とみなす（背景の ACTIVE_HOLD_MS と同じ）。 */
const ACTIVE_HOLD_MS = 4000;
/** 線の濃さ（仮・論点 5）。 */
const LINE_ALPHA = 0.7;
/** カーソルが帯の上にあるとき、ここまで薄くする（0 で消える）。 */
const NEAR_MIN_ALPHA = 0.25;
/** 粒の数。 */
const MOTE_COUNT = 10;

/** 風の目標（src-tauri/src/handmark_wind.rs の WindTarget）。 */
interface WindMessage {
  speed: number;
  irreg: number;
}

interface Mote {
  x: number;
  y: number;
  k: number;
  seed: number;
}

export default function HandmarkEdgeStrip() {
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
    let motes: Mote[] = [];
    const resize = (): void => {
      const dpr = Math.min(window.devicePixelRatio || 1, 2);
      W = window.innerWidth;
      H = window.innerHeight;
      canvas.width = Math.round(W * dpr);
      canvas.height = Math.round(H * dpr);
      ctx.setTransform(dpr, 0, 0, dpr, 0, 0);
      let seed = 7;
      const rnd = (): number => {
        seed = (seed * 16807) % 2147483647;
        return seed / 2147483647;
      };
      motes = [];
      for (let i = 0; i < MOTE_COUNT; i++) {
        motes.push({ x: rnd() * W, y: 0.2 + rnd() * 0.6, k: 0.5 + rnd(), seed: rnd() * 6.28 });
      }
    };
    resize();

    // ---- 風（Rust から目標が届く・背景と同じ寄せ方） ----
    let speed = 0;
    let speedFrom = 0;
    let speedTo = 0;
    let irreg = 0;
    let irregFrom = 0;
    let irregTo = 0;
    let tickAt = performance.now();
    let phase = 0;
    let drift = 0;
    let lastInputAt = -Infinity;
    // カーソルの近さ（0〜1）と、いま描いている濃さの係数。
    let near = 0;
    let fade = 1;
    let visible = true;

    const wave = (x: number): number => {
      const u = x / Math.max(W, 1);
      const wind = Math.min(1, speed / FULL_WIND_SPEED);
      const base = 0.35 * Math.sin(u * 23 + drift * 0.6) * Math.sin(u * 5.3 - drift * 0.21);
      const gust = wind * (0.55 + 0.45 * irreg * Math.sin(u * 41 + drift * 1.7)) * Math.sin(u * 17 - phase * 3);
      return Math.max(-1, Math.min(1, base + gust));
    };

    const draw = (dt: number): void => {
      const slow = reduceMotion ? 0.3 : 1;
      drift += (dt * slow) / 1000;
      phase += (speed * dt * slow) / 1000;
      const target = 1 - (1 - NEAR_MIN_ALPHA) * near;
      fade += (target - fade) * (1 - Math.exp(-dt / 120));
      ctx.clearRect(0, 0, W, H);
      const step = 6;

      // 霧: 帯の下半分に薄い墨と白を重ねた塗り。明るい背景でも暗い背景でも帯の在りかが分かるように。
      ctx.beginPath();
      ctx.moveTo(0, H);
      for (let x = 0; x <= W + step; x += step) {
        ctx.lineTo(x, H * (0.45 + 0.12 * Math.sin(x / 140 + drift * 0.3)));
      }
      ctx.lineTo(W, H);
      ctx.closePath();
      ctx.globalAlpha = fade;
      ctx.fillStyle = "rgba(18,22,27,0.22)";
      ctx.fill();
      ctx.fillStyle = "rgba(255,255,255,0.10)";
      ctx.fill();

      // 粒: 風で横へ流れる。
      const wind = Math.min(1, speed / FULL_WIND_SPEED);
      for (const m of motes) {
        m.x += ((4 + 60 * wind) * m.k * dt * slow) / 1000;
        if (m.x > W + 4) m.x -= W + 8;
        const y = H * (m.y + 0.12 * Math.sin(drift * 0.8 + m.seed));
        ctx.beginPath();
        ctx.arc(m.x, y, 1.1, 0, Math.PI * 2);
        ctx.fillStyle = "rgba(255,255,255,0.75)";
        ctx.fill();
      }

      // 線: 風で揺れる 1 本。墨の太い線の上に白の細い線を重ねる。
      ctx.beginPath();
      for (let x = 0; x <= W + step; x += step) {
        const y = H * 0.5 + H * 0.32 * wave(x);
        if (x === 0) ctx.moveTo(x, y);
        else ctx.lineTo(x, y);
      }
      ctx.globalAlpha = fade * LINE_ALPHA * 0.5;
      ctx.strokeStyle = "#12161b";
      ctx.lineWidth = 4;
      ctx.stroke();
      ctx.globalAlpha = fade * LINE_ALPHA;
      ctx.strokeStyle = "#ffffff";
      ctx.lineWidth = 1.8;
      ctx.stroke();
      ctx.globalAlpha = 1;
    };

    let timer: number | null = null;
    let last: number | null = null;
    const busy = (now: number): boolean => speed > 0 || speedTo > 0 || now - lastInputAt < ACTIVE_HOLD_MS;
    const frame = (): void => {
      timer = null;
      if (!visible) {
        // 全部覆われている間は描かない（見えるようになったら kick で戻る）。
        last = null;
        return;
      }
      const now = performance.now();
      const dt = last === null ? IDLE_FRAME_MS : Math.min(now - last, 200);
      last = now;
      const k = Math.min(1, (now - tickAt) / WIND_TICK_MS);
      const e = k * k * (3 - 2 * k);
      speed = speedFrom + (speedTo - speedFrom) * e;
      irreg = irregFrom + (irregTo - irregFrom) * e;
      draw(dt);
      timer = window.setTimeout(frame, busy(now) ? ACTIVE_FRAME_MS : IDLE_FRAME_MS);
    };
    // 入力が来たら、絞っていた描画をすぐ戻す。
    const kick = (): void => {
      if (!visible) return;
      if (timer !== null) window.clearTimeout(timer);
      timer = window.setTimeout(frame, 0);
    };
    frame();

    window.addEventListener("resize", resize);

    let disposed = false;
    // 列を持たないように、受け取りの解除は 1 つの関数へつないでいく（ADR-040 D4 の検査）。
    let unlistenAll = (): void => {};
    const keep = (p: Promise<() => void>): void => {
      p.then((fn) => {
        if (disposed) {
          fn();
        } else {
          const prev = unlistenAll;
          unlistenAll = (): void => {
            prev();
            fn();
          };
        }
      }).catch(() => {});
    };
    const win = getCurrentWebviewWindow();
    keep(
      win.listen(KEY_EVENT, () => {
        lastInputAt = performance.now();
        kick();
      })
    );
    keep(
      win.listen<WindMessage>(WIND_EVENT, (event) => {
        const w = event.payload;
        speedFrom = speed;
        irregFrom = irreg;
        speedTo = Number.isFinite(w.speed) ? Math.max(0, w.speed) : 0;
        irregTo = Number.isFinite(w.irreg) ? Math.max(0, Math.min(1, w.irreg)) : 0;
        tickAt = performance.now();
      })
    );
    keep(
      win.listen<number>(NEAR_EVENT, (event) => {
        const n = event.payload;
        near = Number.isFinite(n) ? Math.max(0, Math.min(10, n)) / 10 : 0;
        kick();
      })
    );
    keep(
      win.listen<boolean>(VISIBLE_EVENT, (event) => {
        visible = event.payload !== false;
        if (visible) kick();
      })
    );

    return () => {
      disposed = true;
      if (timer !== null) window.clearTimeout(timer);
      window.removeEventListener("resize", resize);
      unlistenAll();
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
