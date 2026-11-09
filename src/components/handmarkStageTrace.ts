// 手跡の背景の層の跡の枠と、跡の場の受け取り・読みの判定（DOM を持たない・ADR-050 D4）。
// 枠は名前を決めた固定の数（波紋 6）。寿命を過ぎた枠と、世代が進んだときの枠から位置と時刻を消す。
// 場は Rust が持つ 16 × 10 の格子（正準の箱: 横 1.6・縦 1.0・1 マス 0.1）の写しで、窓は届いた値を
// 読むだけ（積まない）。受け取りは、古い世代の値と、描画が止まっていた間などに遅れて届いた値を捨てる。
// テスト: scripts/handmark-stage-trace.test.mjs（node --test）。検査: src-tauri/src/handmark_guard.rs。
// ホイールの処理は無い（PR 5）。

/** 波紋の枠の数。 */
export const RIPPLE_SLOTS = 6;
/** 波紋の寿命。 */
export const RIPPLE_MS = 1600;
/** これより遅れて届いた値は描かずに捨てる。 */
export const STALE_MS = 250;
/** 最後に場を受け取ってからこれだけ経ったら、場を 0 にする（入力が来ない間にも消える・ADR-050 D4）。
 * Rust は場が 0 でない間 32ms ごと（2 刻み）に送るので、1 秒途絶えたら古い。 */
export const TRACE_TTL_MS = 1000;
/** Rust が場を送る間隔（src-tauri/src/handmark_pointer_thread.rs の TRACE_SEND_MS）。届いた場へこの時間をかけて寄せる。 */
export const TRACE_TICK_MS = 32;

/** 格子（src-tauri/src/analysis/handmark/trace.rs と同じ）。 */
export const GRID_W = 16;
export const GRID_H = 10;
export const CELLS = GRID_W * GRID_H;
/** 正準の箱（横 1.6・縦 1.0）と、1 マスの辺。 */
export const BOX_W = 1.6;
export const BOX_H = 1.0;
export const CELL = 0.1;
/** 量子化の上限（trace.rs の BEND_MAX・MOTE_MAX）。i8 の 127 がこの値。 */
export const BEND_MAX = 0.9;
export const MOTE_MAX = 0.08;

/** 場を 0 にする時か。まだ場を受け取っていない（`-Infinity`）なら真。 */
export function traceExpired(lastTraceAt: number, now: number): boolean {
  return now - lastTraceAt >= TRACE_TTL_MS;
}

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

/** 世代が進んだ・窓が閉じたときに呼ぶ。全部の枠を消す。 */
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

/** 場。マスごとの 3 つの値（`i = j * GRID_W + col`）。bend = 草を倒す量・pullX/pullY = 粒を寄せる量（正準の単位）。 */
export interface Field {
  readonly bend: Float32Array;
  readonly pullX: Float32Array;
  readonly pullY: Float32Array;
}

export function makeField(): Field {
  return {
    bend: new Float32Array(CELLS),
    pullX: new Float32Array(CELLS),
    pullY: new Float32Array(CELLS),
  };
}

export function clearField(f: Field): void {
  f.bend.fill(0);
  f.pullX.fill(0);
  f.pullY.fill(0);
}

/** 場が全部 0 か。 */
export function fieldIsZero(f: Field): boolean {
  for (let i = 0; i < CELLS; i++) {
    if (f.bend[i] !== 0 || f.pullX[i] !== 0 || f.pullY[i] !== 0) {
      return false;
    }
  }
  return true;
}

/** Rust から届く場（src-tauri/src/handmark_stage.rs の TracePayload と同じ形）。
 * `cells` は `i * 3` から bend・pullX・pullY（各 −127〜127）。 */
export interface TraceMessage {
  epoch: number;
  tMs: number;
  cells: ReadonlyArray<number>;
}

/** Rust から届く波紋の種（RipplePayload）。x・y は正準の箱。 */
export interface RippleMessage {
  epoch: number;
  tMs: number;
  x: number;
  y: number;
}

/** i8 を戻して `into` に書く。長さが違う・数でない値があれば何も書かず false。 */
export function decodeCells(cells: ReadonlyArray<number>, into: Field): boolean {
  if (cells.length !== CELLS * 3) {
    return false;
  }
  for (const v of cells) {
    if (!Number.isFinite(v)) {
      return false;
    }
  }
  for (let i = 0; i < CELLS; i++) {
    into.bend[i] = (Math.max(-127, Math.min(127, cells[i * 3])) * BEND_MAX) / 127;
    into.pullX[i] = (Math.max(-127, Math.min(127, cells[i * 3 + 1])) * MOTE_MAX) / 127;
    into.pullY[i] = (Math.max(-127, Math.min(127, cells[i * 3 + 2])) * MOTE_MAX) / 127;
  }
  return true;
}

/** `out = a + (b - a) * k`（k は 0〜1 に丸める）。 */
export function lerpField(a: Field, b: Field, k: number, out: Field): void {
  const t = Math.max(0, Math.min(1, k));
  for (let i = 0; i < CELLS; i++) {
    out.bend[i] = a.bend[i] + (b.bend[i] - a.bend[i]) * t;
    out.pullX[i] = a.pullX[i] + (b.pullX[i] - a.pullX[i]) * t;
    out.pullY[i] = a.pullY[i] + (b.pullY[i] - a.pullY[i]) * t;
  }
}

export interface FieldValue {
  bend: number;
  pullX: number;
  pullY: number;
}

/** 正準の座標 (x, y) で場を双一次補間して読む。マスの中心で値そのもの・箱の外は端のマスに丸める。 */
export function sampleField(f: Field, x: number, y: number): FieldValue {
  const gx = Math.max(0, Math.min(GRID_W - 1, (Number.isFinite(x) ? x : 0) / CELL - 0.5));
  const gy = Math.max(0, Math.min(GRID_H - 1, (Number.isFinite(y) ? y : 0) / CELL - 0.5));
  const c0 = Math.min(GRID_W - 2, Math.floor(gx));
  const r0 = Math.min(GRID_H - 2, Math.floor(gy));
  const fx = gx - c0;
  const fy = gy - r0;
  const i00 = r0 * GRID_W + c0;
  const i10 = i00 + 1;
  const i01 = i00 + GRID_W;
  const i11 = i01 + 1;
  const at = (a: Float32Array): number => {
    const top = a[i00] * (1 - fx) + a[i10] * fx;
    const bottom = a[i01] * (1 - fx) + a[i11] * fx;
    return top * (1 - fy) + bottom * fy;
  };
  return { bend: at(f.bend), pullX: at(f.pullX), pullY: at(f.pullY) };
}

/** 遅れの判定が続けて「捨てる」になったら基準（`minLag`）を取り直す回数。送り手（Rust の単調な時計）と
 * 窓（performance.now）の時計のずれが、スリープなどで一度に大きく変わったときに回復する。 */
export const REBASE_AFTER = 5;

export interface Receiver {
  epoch: number;
  /** 届くまでのずれ（時計の差を含む）の最小。これより STALE_MS 以上遅れたら捨てる。最初の値が基準。 */
  minLag: number;
  /** 続けて「遅すぎる」と判定した回数（受け取れたら 0 に戻る）。 */
  lateRun: number;
}

export function makeReceiver(): Receiver {
  return { epoch: -1, minLag: Infinity, lateRun: 0 };
}

export interface Verdict {
  /** 値を描画に使ってよいか。 */
  use: boolean;
  /** 世代が進んだ（場と波紋を消す）。遅れて届いても効く。 */
  reset: boolean;
}

/** 遅れで受けるかを決める（場と波紋で共通）。`minLag` を更新する。遅すぎる判定が `REBASE_AFTER` 回続いたら、
 * その値を新しい基準にして受ける（時計のずれが一度に変わった場合の回復）。 */
function judgeLag(rc: Receiver, tMs: number, now: number): boolean {
  const lag = now - tMs;
  rc.minLag = Math.min(rc.minLag, lag);
  if (lag - rc.minLag <= STALE_MS) {
    rc.lateRun = 0;
    return true;
  }
  rc.lateRun += 1;
  if (rc.lateRun >= REBASE_AFTER) {
    rc.minLag = lag;
    rc.lateRun = 0;
    return true;
  }
  return false;
}

/** 届いた場を受けるかを決める。`now` は受け取った時刻（窓の時計）。 */
export function receive(rc: Receiver, m: { epoch: number; tMs: number }, now: number): Verdict {
  if (m.epoch < rc.epoch) {
    // 切る前の世代の値（配送待ちだったもの）は捨てる。
    return { use: false, reset: false };
  }
  let reset = false;
  if (m.epoch > rc.epoch) {
    // 最初の値（rc.epoch が -1）も世代が進んだ扱いになるが、消すものは無い。
    // 世代が進むときは、時計のずれも取り直す（切る間に窓がスリープしていたかもしれない）。
    reset = true;
    rc.epoch = m.epoch;
    rc.minLag = Infinity;
    rc.lateRun = 0;
  }
  return { use: judgeLag(rc, m.tMs, now), reset };
}

/** 届いた波紋の種を受けるか。今の世代より古いものは捨て、遅れは場と同じ規則で決める。 */
export function receiveRipple(rc: Receiver, m: { epoch: number; tMs: number }, now: number): boolean {
  if (m.epoch < rc.epoch) {
    return false;
  }
  return judgeLag(rc, m.tMs, now);
}
