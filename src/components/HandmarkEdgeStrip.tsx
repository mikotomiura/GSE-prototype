// 手跡の下の縁の帯（段 1 の後期・ADR-051）。主画面の下の縁の高さ 14 点の透明な窓に、風で揺れる線 1 本・
// その下の薄い霧 1 本・粒 10 個を描く。写し方は試作（見本の帯）と同じ。
// - 風・位相・漂い・配置の種は、背景と同じく Rust が打鍵の時刻だけから 250 ms ごとに計算して送る(StageState)。
//   この窓は performance.now() や描画の間隔(dt)から位相・漂い・位置を積まない。線も粒も、届いた
//   phase・drift・layout_seed の関数で、届いた状態へ 250 ms かけて線形に寄せるだけ（描画の回数は見た目に影響しない）。
// - カーソル: 座標は受け取らず、Rust が帯への近さを 0〜10 の数 1 つにして送る。近いほど薄くする（120 ms の時定数）。
// - 描く間隔は handmarkStripFrame.ts の nextFrameMs（風がある間 約 30 回／秒・無い間 約 10 回／秒・全部覆われたら止める）。
// 窓は何も保存せず、何も返さない。推定は受け取らない。数値・文字は描かない。
import { useEffect, useRef } from "react";
import { getCurrentWebviewWindow } from "@tauri-apps/api/webviewWindow";
import {
  FULL_WIND_SPEED,
  clampNear,
  closedStrip,
  drawStrip,
  fadeAt,
  fadeIsSettling,
  fadeReceive,
  initialFade,
  kickDelayMs,
  nextFrameMs,
  receiveStrip,
} from "./handmarkStripFrame";
import type { Shown } from "./handmarkStripFrame";
import { fitCanvas } from "./handmarkCanvasFit";

/** 状態を知らせるイベント名(src-tauri/src/handmark_stage.rs の STATE_EVENT)。閉じたときは null。 */
const STATE_EVENT = "handmark-state";
/** 帯へのカーソルの近さ 0〜10(src-tauri/src/handmark_edge_strip.rs・この窓専用)。 */
const NEAR_EVENT = "handmark-strip-near";
/** 帯が見えているか(src-tauri/src/handmark_edge_strip.rs・occlusionState)。 */
const VISIBLE_EVENT = "handmark-strip-visible";

/** 線の濃さ。 */
const LINE_ALPHA = 0.7;
/** 粒の数。 */
const MOTE_COUNT = 10;
/** 配置の種が届く前の種。 */
const DEFAULT_SEED = 7;

/** Rust の StageState(src-tauri/src/analysis/handmark/state.rs)。 */
interface StageStateMessage {
  speed: number;
  irreg: number;
  phase: number;
  drift: number;
  layout_seed: number;
}

interface Mote {
  /** 初期の横の位置(幅に対する割合)・縦の位置(高さに対する割合)。 */
  x0: number;
  y: number;
  k: number;
  seed: number;
}

function finite(v: number, fallback: number): number {
  return Number.isFinite(v) ? v : fallback;
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
    let layoutSeed = -1;
    let motes: Mote[] = [];
    const buildMotes = (seedIn: number): void => {
      layoutSeed = seedIn;
      // 1 以上 2147483646 以下の種にする
      let seed = (seedIn % 2147483646) + 1;
      const rnd = (): number => {
        seed = (seed * 16807) % 2147483647;
        return seed / 2147483647;
      };
      motes = [];
      for (let i = 0; i < MOTE_COUNT; i++) {
        motes.push({ x0: rnd(), y: 0.2 + rnd() * 0.6, k: 0.5 + rnd(), seed: rnd() * 6.28 });
      }
    };
    // 画素の大きさと拡大を今の窓に合わせる。描くたびに呼ぶ（拡大が単位行列に戻っても次の 1 枚で戻る・
    // handmarkCanvasFit.ts）。粒の配置は幅に対する割合なので、大きさが変わっても作り直さない。
    const fit = (): void => {
      W = window.innerWidth;
      H = window.innerHeight;
      fitCanvas(canvas, ctx, W, H, window.devicePixelRatio);
    };
    const resize = (): void => {
      fit();
      buildMotes(layoutSeed < 0 ? DEFAULT_SEED : layoutSeed);
    };
    resize();

    // ---- 状態(Rust から届く)。遷移は handmarkStripFrame.ts の純関数(届いた列と時刻だけで見た目が決まる) ----
    let strip = closedStrip(performance.now());
    // カーソルの近さが届いた時刻とそのときの濃さ。今の濃さは時刻の閉じた式。
    let fadeSt = initialFade(performance.now());
    // 直近に描いた値(描くためだけ・寄せの起点には使わない)。
    let shown: Shown = strip.shown;
    let fade = 1;
    let visible = true;

    const wave = (x: number, drift: number, phase: number): number => {
      const u = x / Math.max(W, 1);
      const wind = Math.min(1, shown.speed / FULL_WIND_SPEED);
      const base = 0.35 * Math.sin(u * 23 + drift * 0.6) * Math.sin(u * 5.3 - drift * 0.21);
      const gust = wind * (0.55 + 0.45 * shown.irreg * Math.sin(u * 41 + drift * 1.7)) * Math.sin(u * 17 - phase * 3);
      return Math.max(-1, Math.min(1, base + gust));
    };

    const draw = (): void => {
      // 「動きを減らす」は漂いと粒の流れを遅くする(係数を掛けるだけ・積まない)。
      const calm = reduceMotion ? 0.3 : 1;
      const drift = shown.drift * calm;
      const phase = shown.phase * calm;
      fit();
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

      // 粒: 位置は drift(基層の流れ)と phase(打鍵の風の積分)の関数で、幅で折り返す。
      const span = W + 8;
      for (const m of motes) {
        const dx = (4 * drift + (60 * phase) / FULL_WIND_SPEED) * m.k;
        const x = ((((m.x0 * W + dx) % span) + span) % span) - 4;
        const y = H * (m.y + 0.12 * Math.sin(drift * 0.8 + m.seed));
        ctx.beginPath();
        ctx.arc(x, y, 1.1, 0, Math.PI * 2);
        ctx.fillStyle = "rgba(255,255,255,0.75)";
        ctx.fill();
      }

      // 線: 風で揺れる 1 本。墨の太い線の上に白の細い線を重ねる。
      ctx.beginPath();
      for (let x = 0; x <= W + step; x += step) {
        const y = H * 0.5 + H * 0.32 * wave(x, drift, phase);
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
    // 予約した時刻と最後に描いた時刻（performance.now の時計だけ・Rust の時計と混ぜない）。
    let pendingAt: number | null = null;
    let lastDrawAt: number | null = null;
    const frame = (): void => {
      timer = null;
      pendingAt = null;
      if (!strip.active || !visible) {
        // 閉じた・全部覆われている間は描かない（見えるようになったら kick で戻る）。
        return;
      }
      const now = performance.now();
      strip = drawStrip(strip, now);
      shown = strip.shown;
      fade = fadeAt(fadeSt, now);
      draw();
      lastDrawAt = now;
      const wait = nextFrameMs({
        open: strip.active,
        visible,
        speed: shown.speed,
        speedTo: strip.to.speed,
        fadeSettling: fadeIsSettling(fade, fadeSt.target),
      });
      if (wait !== null) {
        timer = window.setTimeout(frame, wait);
        pendingAt = now + wait;
      }
    };
    // 状態・近さ・見えるようになったときに、絞っていた描画をすぐ戻す。
    // 最後に描いてから ACTIVE_FRAME_MS は空ける（kickDelayMs）ので、30 回／秒を超えない。
    const kick = (): void => {
      if (!strip.active || !visible) return;
      const now = performance.now();
      const wait = kickDelayMs(lastDrawAt, timer === null ? null : pendingAt, now);
      if (wait === null) return;
      if (timer !== null) window.clearTimeout(timer);
      timer = window.setTimeout(frame, wait);
      pendingAt = now + wait;
    };

    // 届いた状態を受け取り、今の時刻での見た目の値からその状態へ寄せ始める。null は窓が閉じたこと。
    const onState = (msg: StageStateMessage | null): void => {
      if (msg === null) {
        const t = performance.now();
        strip = closedStrip(t);
        fadeSt = initialFade(t);
        shown = strip.shown;
        // 閉じたら見えている側に戻す: 開き直したとき、見張りの最初の読み（必ず送られる）が届くまで描く。
        // 偽に戻すと、窓の listen より先に最初の読みが届いた場合に、見えているのに描かないままになる。
        visible = true;
        fade = 1;
        if (timer !== null) {
          window.clearTimeout(timer);
          timer = null;
        }
        pendingAt = null;
        fit();
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
        buildMotes(msg.layout_seed);
      }
      strip = receiveStrip(strip, next, performance.now(), seedChanged);
      kick();
    };

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
      win.listen<StageStateMessage | null>(STATE_EVENT, (event) => {
        onState(event.payload);
      })
    );
    keep(
      win.listen<number>(NEAR_EVENT, (event) => {
        fadeSt = fadeReceive(fadeSt, clampNear(event.payload), performance.now());
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
      strip = closedStrip(performance.now());
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
