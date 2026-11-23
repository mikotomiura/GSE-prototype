// 手跡の背景の層(段 1 の後期・ADR-051)。デスクトップの高さの透明な窓の全面に、自然世界(霧・草・粒)を描く。
// 写し方は試作(見本 Version 5)と同じ。ホイールの処理だけが無い(PR 5)。
// - 風・位相・漂い・配置の種は、Rust が打鍵の時刻だけから 250 ms ごとに計算して送る(StageState)。
//   この窓は performance.now() や描画の間隔(dt)から位相・漂い・位置を積まない。粒の位置も草の揺れも、
//   届いた drift・phase・layout_seed の関数で、届いた状態へ 250 ms かけて線形に寄せるだけ
//   (描画の回数は見た目に影響しない・机上の描き直しと一致する)。
// - ポインタ(PR 3): Rust が 16 × 10 の格子の「跡の場」を持ち、32 ms ごとに送る(`handmark-trace`)。窓はそれを
//   次の写しまで線形に寄せ、草 1 本・粒 1 つの位置で双一次補間して読むだけで、跡の値を積まない。
//   場が 1 秒来なければ 0 にする。クリックの波紋は `handmark-ripple` で届き、6 枠に入れて 1.6 秒で消す。
// - 霧: どの入力にも依らない基層(漂いは Rust の drift)。
// - Windows だけ: デスクトップのアイコンの写しが窓の受け口(`__gseHandmarkIcons`)に届き、模様のある画素にだけ重ねる
//   (handmarkStageIcons.ts・模様がアイコンの後ろを流れて見える)。
// 窓は何も保存せず、何も返さない。推定は受け取らない。数値・文字は描かない。
// 描く部分は handmarkStageDraw.ts の純関数(机上の道具と同じ関数・手跡の PR 4)。この部品は受け取りと寄せと時計だけ。
import { useEffect, useRef } from "react";
import { getCurrentWebviewWindow } from "@tauri-apps/api/webviewWindow";
import {
  TRACE_TICK_MS,
  addRipple,
  clearField,
  clearRipples,
  decodeCells,
  fieldIsZero,
  lerpField,
  makeField,
  makeReceiver,
  makeRipples,
  receive,
  receiveRipple,
  rippleAge,
  rippleStart,
  sweepRipples,
  traceExpired,
} from "./handmarkStageTrace";
import type { RippleMessage, TraceMessage } from "./handmarkStageTrace";
import { buildWorld, drawFrame, viewOf } from "./handmarkStageDraw";
import type { RippleView, Shown, View, World } from "./handmarkStageDraw";
import { clearIconLayer, drawIconsAtop, handleIconsMessage, installIconsHook, makeIconLayer } from "./handmarkStageIcons";
import type { IconsHookMessage } from "./handmarkStageIcons";

/** 状態を知らせるイベント名(src-tauri/src/handmark_stage.rs の STATE_EVENT)。閉じたときは null。 */
const STATE_EVENT = "handmark-state";
/** 跡の場・波紋の種のイベント名(src-tauri/src/handmark_stage.rs の TRACE_EVENT・RIPPLE_EVENT)。 */
const TRACE_EVENT = "handmark-trace";
const RIPPLE_EVENT = "handmark-ripple";
/** 寿命を過ぎた波紋・古い場を、描画が止まっていても消すための時計の知らせの間隔。 */
const CLOCK_TICK_MS = 250;

/** 状態が届く間隔(analysis/handmark/state.rs の TICK_MS)。受け取った状態へこの時間をかけて寄せる。 */
const STATE_TICK_MS = 250;
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

function finite(v: number, fallback: number): number {
  return Number.isFinite(v) ? v : fallback;
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

    let view: View = viewOf(0, 0);

    // ---- 自然世界の要素(数は固定・配置は layout_seed から) ----
    let layoutSeed = -1;
    let world: World = buildWorld(11, 0, 0);
    const rebuild = (seedIn: number): void => {
      layoutSeed = seedIn;
      world = buildWorld(seedIn, view.W, view.H);
    };

    const resize = (): void => {
      const dpr = Math.min(window.devicePixelRatio || 1, 2);
      view = viewOf(window.innerWidth, window.innerHeight);
      canvas.width = Math.round(view.W * dpr);
      canvas.height = Math.round(view.H * dpr);
      ctx.setTransform(dpr, 0, 0, dpr, 0, 0);
      rebuild(layoutSeed < 0 ? 11 : layoutSeed);
    };
    resize();

    // ---- 状態(Rust から届く)。from から to へ STATE_TICK_MS かけて線形に寄せる ----
    let active = false;
    let from: Shown = { speed: 0, irreg: 0, phase: 0, drift: 0 };
    let to: Shown = { speed: 0, irreg: 0, phase: 0, drift: 0 };
    let shown: Shown = { speed: 0, irreg: 0, phase: 0, drift: 0 };
    let recvAt = performance.now();

    // ---- ポインタ(Rust から届く跡の場と波紋)。窓は積まず、届いた値を寄せて読むだけ ----
    const fieldFrom = makeField();
    const fieldTo = makeField();
    const fieldShown = makeField();
    const rippleSlots = makeRipples();
    const receiver = makeReceiver();
    // デスクトップのアイコンの写し(Windows だけ届く)。
    const icons = makeIconLayer();
    let traceRecvAt = performance.now();
    /** 最後に場を受け取った時刻。まだなら -Infinity(期限切れ扱い)。 */
    let lastTraceAt = -Infinity;
    /** 場に 0 でない値がある(描画を絞らない)。 */
    let fieldLive = false;

    const resetPointer = (): void => {
      clearField(fieldFrom);
      clearField(fieldTo);
      clearField(fieldShown);
      clearRipples(rippleSlots);
      lastTraceAt = -Infinity;
      fieldLive = false;
    };

    // 波紋の枠(6 つ)を、描く関数へ渡す形(0〜1 の経過)にする。毎回作り直し、溜めない。
    const rippleViews = (now: number) => {
      const ripples: RippleView[] = [];
      for (const rp of rippleSlots.ripples) {
        const t = rippleAge(rp, now);
        if (t !== null) ripples.push({ x: rp.x, y: rp.y, t });
      }
      return ripples;
    };

    // 届いた状態を受け取り、いま見せている値からその状態へ寄せ始める。null は窓が閉じたこと。
    const onState = (msg: StageStateMessage | null): void => {
      if (msg === null) {
        // 窓が閉じた: 状態も、場も波紋も消す(世代は次に開いたとき進んだ値が届く)。
        active = false;
        resetPointer();
        clearIconLayer(icons);
        ctx.clearRect(0, 0, view.W, view.H);
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
        rebuild(msg.layout_seed);
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
      // 跡の場: 届いた場へ次の写しまで線形に寄せる。1 秒来なければ 0(描画の回数では積まない)。
      sweepPointer(now);
      lerpField(fieldFrom, fieldTo, (now - traceRecvAt) / TRACE_TICK_MS, fieldShown);
      drawFrame(ctx, world, view, shown, fieldShown, rippleViews(now), reduceMotion ? 0.3 : 1);
      drawIconsAtop(ctx, icons, view.W, view.H);
      if (
        shown.speed > 0 ||
        to.speed > 0 ||
        fieldLive ||
        now - traceRecvAt < TRACE_TICK_MS * 2 ||
        rippleSlots.ripples.some((rp) => rippleAge(rp, now) !== null)
      ) {
        frame = requestAnimationFrame(loop);
      } else {
        // 風が無い間は霧と粒の漂いだけを 1 秒に約 10 回描く(負荷を抑える)。
        idleTimer = window.setTimeout(() => {
          idleTimer = null;
          frame = requestAnimationFrame(loop);
        }, IDLE_FRAME_MS);
      }
    };
    // 寿命を過ぎた波紋を消し、場が 1 秒来なければ場を 0 にする(描画が止まっていても時計の知らせで呼ぶ)。
    const sweepPointer = (now: number): void => {
      sweepRipples(rippleSlots, now);
      if (fieldLive && traceExpired(lastTraceAt, now)) {
        clearField(fieldFrom);
        clearField(fieldTo);
        clearField(fieldShown);
        fieldLive = false;
      }
    };

    // 届いた場を受ける。世代が進んだら場と波紋を消し、古い・遅れすぎた値は捨てる。
    const onTrace = (msg: TraceMessage): void => {
      const now = performance.now();
      const v = receive(receiver, msg, now);
      if (v.reset) {
        resetPointer();
      }
      if (!v.use) {
        return;
      }
      // 寄せ始める値は、いま見せている値
      lerpField(fieldFrom, fieldTo, (now - traceRecvAt) / TRACE_TICK_MS, fieldShown);
      fieldFrom.bend.set(fieldShown.bend);
      fieldFrom.pullX.set(fieldShown.pullX);
      fieldFrom.pullY.set(fieldShown.pullY);
      if (!decodeCells(msg.cells, fieldTo)) {
        return;
      }
      traceRecvAt = now;
      lastTraceAt = now;
      fieldLive = !fieldIsZero(fieldTo);
      if (active) kick();
    };

    // 届いた波紋の種を 6 枠のどれかへ入れる(窓の時計で年齢を決める)。
    const onRipple = (msg: RippleMessage): void => {
      const now = performance.now();
      if (!receiveRipple(receiver, msg, now)) {
        return;
      }
      if (Number.isFinite(msg.x) && Number.isFinite(msg.y)) {
        // 始まりは押された時刻(届くまでの遅れの違いで出始めがばらつかないように)
        addRipple(rippleSlots, msg.x, msg.y, rippleStart(receiver, msg.tMs, now));
        if (active) kick();
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
    const clockTimer = window.setInterval(() => {
      sweepPointer(performance.now());
    }, CLOCK_TICK_MS);

    let disposed = false;
    let unlisten: (() => void) | null = null;
    let unlistenTrace: (() => void) | null = null;
    let unlistenRipple: (() => void) | null = null;
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
    win
      .listen<TraceMessage>(TRACE_EVENT, (event) => {
        onTrace(event.payload);
      })
      .then((fn) => {
        if (disposed) fn();
        else unlistenTrace = fn;
      })
      .catch(() => {});
    win
      .listen<RippleMessage>(RIPPLE_EVENT, (event) => {
        onRipple(event.payload);
      })
      .then((fn) => {
        if (disposed) fn();
        else unlistenRipple = fn;
      })
      .catch(() => {});
    // 開いた直後の最初の区画は状態より先に届くことがあるので、active を待たずに置く。閉じるときは Rust が
    // 先に送り手を止めてから null を送り、null で層を消す。次に開いた最初の区画は層を消してから置く(reset)。
    const uninstallIcons = installIconsHook((msg: IconsHookMessage) => {
      if (handleIconsMessage(icons, msg) && active) kick();
    });

    return () => {
      disposed = true;
      active = false;
      window.removeEventListener("resize", onResize);
      if (frame !== null) cancelAnimationFrame(frame);
      if (idleTimer !== null) window.clearTimeout(idleTimer);
      window.clearInterval(clockTimer);
      if (unlisten !== null) unlisten();
      if (unlistenTrace !== null) unlistenTrace();
      if (unlistenRipple !== null) unlistenRipple();
      uninstallIcons();
      clearIconLayer(icons);
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
