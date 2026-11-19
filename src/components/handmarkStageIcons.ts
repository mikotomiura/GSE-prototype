// 手跡の背景の窓に、デスクトップのアイコンの写しを重ねる層(Windows だけ・判断 9・10)。
// Rust(src-tauri/src/handmark_desktop_windows.rs)が、デスクトップの一覧の絵のうち変わった 64×64 の区画だけを
// 送る(`handmark-icons`)。ここは区画を画面の大きさの画面外の canvas に置き、模様を描いた後に
// `source-atop` で重ねるだけ(模様のある画素にだけアイコンが乗る = 模様がアイコンの後ろを流れて見える)。
// 模様の無い所には何も描かないので、本物のアイコンがそのまま見える(写しが二重にかからない)。
// 受け取った画素は保存せず、送り返さず、窓が閉じたら消す。macOS では何も届かないので層は空のまま。

/** アイコンの区画のイベント名(src-tauri/src/handmark_stage.rs の ICONS_EVENT)。 */
export const ICONS_EVENT = "handmark-icons";

/** 区画 1 つ。`rgba` は straight の RGBA の base64。空なら消す。 */
export interface IconTileMessage {
  x: number;
  y: number;
  w: number;
  h: number;
  rgba: string;
}

/** 画面の大きさ(物理ピクセル)と、変わった区画。 */
export interface IconsMessage {
  screenW: number;
  screenH: number;
  tiles: IconTileMessage[];
}

export interface IconLayer {
  canvas: HTMLCanvasElement | null;
  ctx: CanvasRenderingContext2D | null;
  /** 何か描いてある(重ねる必要がある)。 */
  any: boolean;
}

export function makeIconLayer(): IconLayer {
  return { canvas: null, ctx: null, any: false };
}

/** 画面の大きさの上限(物理ピクセル)。これを超える値は壊れているとみなす。 */
const MAX_SIDE = 16384;

function validSide(v: number): boolean {
  return Number.isInteger(v) && v > 0 && v <= MAX_SIDE;
}

/** base64 を、長さが `n` のバイト列に直す。長さが合わなければ null。 */
function decode(b64: string, n: number): Uint8ClampedArray | null {
  let bin: string;
  try {
    bin = atob(b64);
  } catch {
    return null;
  }
  if (bin.length !== n) {
    return null;
  }
  const out = new Uint8ClampedArray(n);
  for (let i = 0; i < n; i += 1) {
    out[i] = bin.charCodeAt(i);
  }
  return out;
}

/** 区画を層に置く。何か変わったら true。壊れた区画は飛ばす。 */
export function applyIcons(layer: IconLayer, msg: IconsMessage): boolean {
  if (!validSide(msg.screenW) || !validSide(msg.screenH) || !Array.isArray(msg.tiles)) {
    return false;
  }
  if (layer.canvas === null || layer.canvas.width !== msg.screenW || layer.canvas.height !== msg.screenH) {
    const c = document.createElement("canvas");
    c.width = msg.screenW;
    c.height = msg.screenH;
    layer.canvas = c;
    layer.ctx = c.getContext("2d");
    layer.any = false;
  }
  const ctx = layer.ctx;
  if (ctx === null) {
    return false;
  }
  let changed = false;
  for (const t of msg.tiles) {
    const inside =
      Number.isInteger(t.x) &&
      Number.isInteger(t.y) &&
      Number.isInteger(t.w) &&
      Number.isInteger(t.h) &&
      t.x >= 0 &&
      t.y >= 0 &&
      t.w > 0 &&
      t.h > 0 &&
      t.x + t.w <= msg.screenW &&
      t.y + t.h <= msg.screenH;
    if (!inside || typeof t.rgba !== "string") {
      continue;
    }
    if (t.rgba.length === 0) {
      ctx.clearRect(t.x, t.y, t.w, t.h);
      changed = true;
      continue;
    }
    const px = decode(t.rgba, t.w * t.h * 4);
    if (px === null) {
      continue;
    }
    ctx.putImageData(new ImageData(px, t.w, t.h), t.x, t.y);
    layer.any = true;
    changed = true;
  }
  return changed;
}

/** 層を消す(窓が閉じたとき)。 */
export function clearIconLayer(layer: IconLayer): void {
  if (layer.ctx !== null && layer.canvas !== null) {
    layer.ctx.clearRect(0, 0, layer.canvas.width, layer.canvas.height);
  }
  layer.canvas = null;
  layer.ctx = null;
  layer.any = false;
}

/** 模様を描いた後に呼ぶ。模様のある画素にだけ、アイコンの写しを重ねる(`source-atop`)。 */
export function drawIconsAtop(ctx: CanvasRenderingContext2D, layer: IconLayer, w: number, h: number): void {
  if (!layer.any || layer.canvas === null) {
    return;
  }
  ctx.save();
  ctx.globalCompositeOperation = "source-atop";
  ctx.drawImage(layer.canvas, 0, 0, w, h);
  ctx.restore();
}
