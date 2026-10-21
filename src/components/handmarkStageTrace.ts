// 手跡の背景の層の跡の枠と、ポインタの値の受け取りの判定（spike・DOM を持たない・ADR-040 D4）。
// 枠は名前を決めた固定の数（波紋 6）。寿命を過ぎた枠と、入力を切ったときの枠から位置と時刻を消す。
// 受け取りは、古い世代の値と、描画が止まっていた間などに遅れて届いた値を捨てる。
// テスト: scripts/handmark-stage-trace.test.mjs（node --test）。検査: src-tauri/src/handmark_stage_guard.rs。

/** 波紋の枠の数。 */
export const RIPPLE_SLOTS = 6;
/** 波紋の寿命。 */
export const RIPPLE_MS = 1600;
/** これより遅れて届いた値は描かずに捨てる。 */
export const STALE_MS = 250;

export interface RippleSlot {
  x: number;
  y: number;
  /** 始まりの時刻。空の枠は null（位置も 0 に戻す）。 */
  t0: number | null;
}

export interface Ripples {
  readonly ripples: ReadonlyArray<RippleSlot>;
  next: number;
}

export function makeRipples(): Ripples {
  const ripples = Array.from({ length: RIPPLE_SLOTS }, (): RippleSlot => ({ x: 0, y: 0, t0: null }));
  return { ripples, next: 0 };
}

function clearSlot(s: RippleSlot): void {
  s.x = 0;
  s.y = 0;
  s.t0 = null;
}

/** 古いものから上書きする（数が増えない）。 */
export function addRipple(r: Ripples, x: number, y: number, now: number): void {
  const s = r.ripples[r.next];
  s.x = x;
  s.y = y;
  s.t0 = now;
  r.next = (r.next + 1) % RIPPLE_SLOTS;
}

/** 寿命を過ぎた枠から位置と時刻を消す。入力が来ない間も呼ぶ。 */
export function sweepRipples(r: Ripples, now: number): void {
  for (const s of r.ripples) {
    if (s.t0 !== null && now - s.t0 >= RIPPLE_MS) {
      clearSlot(s);
    }
  }
}

/** 入力を切ったときに呼ぶ。全部の枠を消す。 */
export function clearRipples(r: Ripples): void {
  for (const s of r.ripples) {
    clearSlot(s);
  }
  r.next = 0;
}

/** 0 から 1 へ進む波紋の経過。描かない枠は null。 */
export function rippleAge(s: RippleSlot, now: number): number | null {
  if (s.t0 === null) {
    return null;
  }
  const t = (now - s.t0) / RIPPLE_MS;
  return t >= 0 && t < 1 ? t : null;
}

/** Rust から届く値（src-tauri/src/handmark_stage_pointer.rs の PointerPayload と同じ形）。 */
export interface PointerMessage {
  epoch: number;
  tMs: number;
  cursorOn: boolean;
  clickOn: boolean;
  wheelOn: boolean;
  /** 主画面の左下が原点の座標。 */
  x: number;
  y: number;
  moved: boolean;
  clicked: boolean;
  /** 前の送りから回した量（1 回ぶんを 1・画面を下へ送る向きを正）。 */
  wheel: number;
}

export interface Receiver {
  epoch: number;
  /** 届くまでのずれ（時計の差を含む）の最小。これより STALE_MS 以上遅れたら捨てる。 */
  minLag: number;
  cursorOn: boolean;
  clickOn: boolean;
  wheelOn: boolean;
}

export function makeReceiver(): Receiver {
  return { epoch: -1, minLag: Infinity, cursorOn: false, clickOn: false, wheelOn: false };
}

export interface Verdict {
  /** 位置と押下を描画に使ってよいか。 */
  use: boolean;
  /** いまカーソルが切られた（跡を消す）。 */
  cursorOff: boolean;
  /** いまクリックが切られた（跡を消す）。 */
  clickOff: boolean;
  /** いまホイールが切られた（跡を消す）。 */
  wheelOff: boolean;
}

/** 届いた値を受けるかを決める。`now` は受け取った時刻（窓の時計）。 */
export function receive(rc: Receiver, m: PointerMessage, now: number): Verdict {
  if (m.epoch < rc.epoch) {
    // 切る前の世代の値（配送待ちだったもの）は捨てる。
    return { use: false, cursorOff: false, clickOff: false, wheelOff: false };
  }
  let cursorOff = false;
  let clickOff = false;
  let wheelOff = false;
  if (m.epoch > rc.epoch) {
    cursorOff = rc.cursorOn && !m.cursorOn;
    clickOff = rc.clickOn && !m.clickOn;
    wheelOff = rc.wheelOn && !m.wheelOn;
    rc.epoch = m.epoch;
    rc.cursorOn = m.cursorOn;
    rc.clickOn = m.clickOn;
    rc.wheelOn = m.wheelOn;
  }
  const lag = now - m.tMs;
  rc.minLag = Math.min(rc.minLag, lag);
  return { use: lag - rc.minLag <= STALE_MS, cursorOff, clickOff, wheelOff };
}
