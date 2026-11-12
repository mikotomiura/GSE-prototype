// 手跡の下の縁の帯の、描く間隔の決め方と寄せ方（DOM を持たない・ADR-051）。
// 帯の窓は背景と同じ状態（Rust の StageState）を受け、届いた状態へ線形に寄せるだけで、窓の中で位相や漂いを積まない。
// 描く回数（30／10／止める）は見た目に影響しない: 同じ時刻の見た目は、何回に分けて描いても同じ。
// テスト: scripts/handmark-edge-strip.test.mjs（node --test）。検査: src-tauri/src/handmark_guard.rs。

/** 状態が届く間隔（src-tauri/src/analysis/handmark/state.rs の TICK_MS）。届いた状態へこの時間をかけて寄せる。 */
export const STATE_TICK_MS = 250;
/** 風がある間の描く間隔（約 30 回／秒）と、無い間の描く間隔（約 10 回／秒）。 */
export const ACTIVE_FRAME_MS = 33;
export const IDLE_FRAME_MS = 100;
/** 風が最大になる速さ（毎秒 12 打・背景と同じ）。 */
export const FULL_WIND_SPEED = 0.6;
/** カーソルの近さの上限（src-tauri/src/handmark_pointer_thread.rs の strip_near は 0〜10）。 */
export const NEAR_MAX = 10;
/** カーソルが帯の上にあるとき、ここまで薄くする（濃さの係数の下限・1 − 0.75）。 */
export const NEAR_MIN_ALPHA = 0.25;
/** 濃さの係数を目標へ寄せる時定数。 */
export const NEAR_TAU_MS = 120;
/** 濃さの係数が目標からこれ以内なら、寄せ終わったとみなす。 */
export const NEAR_SETTLE_EPS = 0.01;

/** 窓が見せている状態（Rust の StageState のうち帯が使う 4 つ）。 */
export interface Shown {
  speed: number;
  irreg: number;
  phase: number;
  drift: number;
}

/** from から to へ、経過した時間（届いた時刻からの ms）に応じて線形に寄せた値。経過は 0〜STATE_TICK_MS に丸める。 */
export function blendShown(from: Shown, to: Shown, elapsedMs: number): Shown {
  const raw = Number.isFinite(elapsedMs) ? elapsedMs / STATE_TICK_MS : 1;
  const k = Math.min(1, Math.max(0, raw));
  return {
    speed: from.speed + (to.speed - from.speed) * k,
    irreg: from.irreg + (to.irreg - from.irreg) * k,
    phase: from.phase + (to.phase - from.phase) * k,
    drift: from.drift + (to.drift - from.drift) * k,
  };
}

/** 届いた近さを 0〜NEAR_MAX に丸める（非有限は 0）。 */
export function clampNear(v: number): number {
  if (!Number.isFinite(v)) {
    return 0;
  }
  return Math.min(NEAR_MAX, Math.max(0, v));
}

/** 近さ 0〜10 から、濃さの係数の目標（1 から 0.25 まで）。 */
export function nearTarget(near: number): number {
  return 1 - (1 - NEAR_MIN_ALPHA) * (clampNear(near) / NEAR_MAX);
}

/** 濃さの係数を目標へ寄せる（指数・時定数 NEAR_TAU_MS）。目標が同じなら、dt を何回に分けても結果は同じ。 */
export function approachFade(fade: number, target: number, dtMs: number): number {
  const dt = Number.isFinite(dtMs) ? Math.max(0, dtMs) : 0;
  return fade + (target - fade) * (1 - Math.exp(-dt / NEAR_TAU_MS));
}

/**
 * 濃さの係数の状態。近さが届いた時刻とそのときの濃さ(f0)・目標を持つ。
 * 今の濃さは `f0 + (target − f0)(1 − e^(−Δ/τ))` の閉じた式で、描画の時刻にだけ依る(描いた回数・間隔に依らない)。
 */
export interface FadeState {
  f0: number;
  target: number;
  since: number;
}

export function initialFade(now: number): FadeState {
  return { f0: 1, target: 1, since: now };
}

/** 時刻 now の濃さの係数。 */
export function fadeAt(st: FadeState, now: number): number {
  return approachFade(st.f0, st.target, now - st.since);
}

/** 近さが届いた(時刻 now)。いまの濃さから新しい目標へ寄せ直す。 */
export function fadeReceive(st: FadeState, nearValue: number, now: number): FadeState {
  return { f0: fadeAt(st, now), target: nearTarget(nearValue), since: now };
}

/** 濃さの係数がまだ目標へ寄せている途中か。 */
export function fadeIsSettling(fade: number, target: number): boolean {
  return Math.abs(target - fade) > NEAR_SETTLE_EPS;
}

export interface FrameInput {
  /** 状態を受けて開いている（閉じたときの null で偽）。 */
  open: boolean;
  /** 帯が見えている（全部覆われたら偽）。 */
  visible: boolean;
  /** いま見せている風の速さと、届いた風の速さ。 */
  speed: number;
  speedTo: number;
  /** 濃さの係数が寄せの途中。 */
  fadeSettling: boolean;
}

/** 次に描くまでの ms。描かない（閉じた・全部覆われた）なら null。 */
export function nextFrameMs(input: FrameInput): number | null {
  if (!input.open || !input.visible) {
    return null;
  }
  if (input.speed > 0 || input.speedTo > 0 || input.fadeSettling) {
    return ACTIVE_FRAME_MS;
  }
  return IDLE_FRAME_MS;
}

/**
 * 窓が見せる状態の遷移(DOM を持たない)。from から to へ、届いた時刻(recvAt)から STATE_TICK_MS かけて線形に寄せる。
 * `shown` は最後に描いた値で、描くために持つだけ。次の寄せの起点には使わない
 * (覆われていて描かない間に凍った値から、見えたとき最新へ一気に流れないように)。
 */
export interface StripState {
  active: boolean;
  from: Shown;
  to: Shown;
  recvAt: number;
  shown: Shown;
}

const ZERO: Shown = { speed: 0, irreg: 0, phase: 0, drift: 0 };

/** 閉じている(まだ何も届いていない)状態。窓が閉じた(null)ときの戻しにも使う。 */
export function closedStrip(now: number): StripState {
  return { active: false, from: ZERO, to: ZERO, recvAt: now, shown: ZERO };
}

/** 時刻 now の見た目の値。届いた列と now だけで決まり、描いた回数・間隔に依らない。 */
export function shownAt(st: StripState, now: number): Shown {
  return blendShown(st.from, st.to, now - st.recvAt);
}

/** 描いた(時刻 now)。描く値を `shown` に置く。 */
export function drawStrip(st: StripState, now: number): StripState {
  return { ...st, shown: shownAt(st, now) };
}

/**
 * 状態が届いた(時刻 now)。開いていない・種が替わった(日が変わった・取り直した)ときは寄せずに置き、
 * それ以外は「今の時刻での見た目の値」から寄せ直す。
 */
export function receiveStrip(st: StripState, next: Shown, now: number, seedChanged: boolean): StripState {
  if (!st.active || seedChanged) {
    return { active: true, from: next, to: next, recvAt: now, shown: next };
  }
  return { ...st, from: shownAt(st, now), to: next, recvAt: now };
}
