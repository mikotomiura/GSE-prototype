// 手跡の帯と背景の canvas の、画素の大きさと拡大を合わせる(DOM を持たない純関数)。
// 描くたびに描く前に呼ぶ。2026-11-28、段 1 の後期の帯が横も縦も半分の大きさで描かれた(拡大が単位行列に
// 戻ったまま、resize が来ないので戻らなかった・.steering/20261128-handmark-canvas-half-scale)。
// 拡大は毎回置き直す(安い・文脈の状態に依らない)。画素の大きさは、ずれたときだけ代入する(代入は中身を消す)。
// 置き直すのは拡大だけ。文脈のほかの状態(濃さ・色・線の幅など)も描くたびに置くこと(初期化で 1 回だけ置くと、
// 文脈の状態が捨てられたときに同じ型の不具合になる)。
// テスト: scripts/handmark-canvas-fit.test.mjs(node --test・呼ぶ順の静的な確かめも含む)。

/** 画素の大きさを持つもの(HTMLCanvasElement が満たす)。 */
export interface FitCanvas {
  width: number;
  height: number;
}

/** 拡大を置けるもの(CanvasRenderingContext2D が満たす)。 */
export type FitCtx = Pick<CanvasRenderingContext2D, "setTransform">;

/** 合わせた結果。 */
export interface FitResult {
  /** 画素の大きさを代入したか(中身が消えた)。 */
  resized: boolean;
  /** 使った dpr。 */
  dpr: number;
}

/** 画素の比(今までの `Math.min(window.devicePixelRatio || 1, 2)` と同じ。有限でない値・0 以下は 1)。 */
export function canvasDpr(raw: number | undefined): number {
  if (raw === undefined || !Number.isFinite(raw) || raw <= 0) {
    return 1;
  }
  return Math.min(raw, 2);
}

/** CSS の大きさ `cssW`×`cssH` と画素の比 `rawDpr` に canvas と文脈を合わせる。 */
export function fitCanvas(
  canvas: FitCanvas,
  ctx: FitCtx,
  cssW: number,
  cssH: number,
  rawDpr: number | undefined,
): FitResult {
  const dpr = canvasDpr(rawDpr);
  const w = Math.round(cssW * dpr);
  const h = Math.round(cssH * dpr);
  const resized = canvas.width !== w || canvas.height !== h;
  if (resized) {
    canvas.width = w;
    canvas.height = h;
  }
  ctx.setTransform(dpr, 0, 0, dpr, 0, 0);
  return { resized, dpr };
}
