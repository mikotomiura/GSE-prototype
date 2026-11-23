// 画素の特徴（設計 v2 §3・判断 2）。gse-replay --handmark-windows --frames のコマを、画面と同じ描画の純関数
// （src/components/handmarkStageDraw.ts）と同じ場の戻し方（handmarkStageTrace.ts の decodeCells）で描く。
// 実行: node pixels.mjs <frames.bin> <samples> <out.ndjson>（Node 22.18 以上は .ts の型を除いて読む）
//
// 1 コマ: 320 × 200・dpr 1 で描き、透明の上の描画を灰色 #808080 に重ねた明るさ（壁紙に依らないため）を、
// 16 × 10 のマスで平均して L とする。動き M = |L(τ) − L(τ − 250 ms)|。
// 窓の値: M の平均（160）・L の平均（160）・全体の 5 つ（M の平均・最大・SD、下の 40% と上の 60% の M の平均）。
// 出力: 1 行 {"id": 窓, "v": [325]}。画面との違い（限界）: 画面は状態を 250 ms かけて寄せるが、ここはその時刻の状態をそのまま描く。
// ノード の Skia と WebKit の画素は完全には一致しない。
import { readFileSync, writeFileSync } from "node:fs";
import { resolve } from "node:path";
import { pathToFileURL } from "node:url";
import { createCanvas } from "@napi-rs/canvas";
import { buildWorld, drawFrame, viewOf } from "../../../src/components/handmarkStageDraw.ts";
import { CELLS, decodeCells, makeField, RIPPLE_MS } from "../../../src/components/handmarkStageTrace.ts";

export const W = 320;
export const H = 200;
export const GX = 16;
export const GY = 10;
const BG = 128;
const PAIR_GAP_MS = 250; // desk.rs の PAIR_GAP_MS（τ − 250 と τ の 2 枚）

/** コマの列を読む（replay.rs の write_frame と同じ並び）。 */
export function* readFrames(buf) {
  const dv = new DataView(buf.buffer, buf.byteOffset, buf.byteLength);
  let o = 0;
  while (o < buf.byteLength) {
    const id = dv.getUint32(o, true);
    o += 4;
    const t = Number(dv.getBigUint64(o, true));
    o += 8;
    const speed = dv.getFloat64(o, true);
    const irreg = dv.getFloat64(o + 8, true);
    const phase = dv.getFloat64(o + 16, true);
    const drift = dv.getFloat64(o + 24, true);
    o += 32;
    const layoutSeed = dv.getUint32(o, true);
    o += 4;
    const hasField = dv.getUint8(o);
    o += 1;
    let cells = null;
    if (hasField === 1) {
      cells = new Int8Array(buf.buffer, buf.byteOffset + o, CELLS * 3);
      o += CELLS * 3;
    } else if (hasField !== 0) {
      throw new Error(`壊れたコマ（場の印 ${hasField}）`);
    }
    const n = dv.getUint8(o);
    o += 1;
    const ripples = [];
    for (let i = 0; i < n; i++) {
      const x = dv.getFloat32(o, true);
      const y = dv.getFloat32(o + 4, true);
      const age = dv.getUint16(o + 8, true);
      o += 10;
      ripples.push({ x, y, t: age / RIPPLE_MS });
    }
    yield { id, t, shown: { speed, irreg, phase, drift }, layoutSeed, cells, ripples };
  }
}

const finite = (v, f) => (Number.isFinite(v) ? v : f);

/** 1 コマを描いて、灰色に重ねた明るさのマスの平均（GX × GY）を返す。 */
export function renderLum(ctx, worlds, fr) {
  let world = worlds.get(fr.layoutSeed);
  if (world === undefined) {
    world = buildWorld(fr.layoutSeed, W, H);
    worlds.set(fr.layoutSeed, world);
  }
  const field = makeField();
  if (fr.cells !== null) decodeCells(Array.from(fr.cells), field);
  // 画面の onState と同じ丸め
  const shown = {
    speed: Math.max(0, finite(fr.shown.speed, 0)),
    irreg: Math.max(0, Math.min(1, finite(fr.shown.irreg, 0))),
    phase: finite(fr.shown.phase, 0),
    drift: finite(fr.shown.drift, 0),
  };
  drawFrame(ctx, world, viewOf(W, H), shown, field, fr.ripples, 1);
  const img = ctx.getImageData(0, 0, W, H).data;
  const out = new Float64Array(GX * GY);
  const bw = W / GX;
  const bh = H / GY;
  for (let y = 0; y < H; y++) {
    const gy = Math.floor(y / bh);
    for (let x = 0; x < W; x++) {
      const i = (y * W + x) * 4;
      const a = img[i + 3] / 255;
      const lum = 0.2126 * img[i] + 0.7152 * img[i + 1] + 0.0722 * img[i + 2];
      const comp = a * lum + (1 - a) * BG;
      out[gy * GX + Math.floor(x / bw)] += comp / 255;
    }
  }
  for (let k = 0; k < out.length; k++) out[k] /= bw * bh;
  return out;
}

/** 窓のコマ（τ − 250 と τ の組の列）から窓の値（325）を作る。 */
export function windowVector(pairs) {
  const n = GX * GY;
  const mSum = new Float64Array(n);
  const lSum = new Float64Array(n);
  const frameMotion = [];
  let lower = 0;
  let upper = 0;
  const lowerRow = Math.round(GY * 0.6);
  for (const [prev, cur] of pairs) {
    let fm = 0;
    for (let k = 0; k < n; k++) {
      const m = Math.abs(cur[k] - prev[k]);
      mSum[k] += m;
      lSum[k] += cur[k];
      fm += m;
      if (Math.floor(k / GX) >= lowerRow) lower += m;
      else upper += m;
    }
    frameMotion.push(fm / n);
  }
  const s = pairs.length;
  const mean = frameMotion.reduce((a, b) => a + b, 0) / s;
  const sd = Math.sqrt(frameMotion.reduce((a, b) => a + (b - mean) ** 2, 0) / s);
  const v = [];
  for (let k = 0; k < n; k++) v.push(mSum[k] / s);
  for (let k = 0; k < n; k++) v.push(lSum[k] / s);
  v.push(mean, Math.max(...frameMotion), sd, lower / (s * (GY - lowerRow) * GX), upper / (s * lowerRow * GX));
  return v.map((x) => Math.round(x * 1e7) / 1e7);
}

function main() {
  const [framesPath, samplesArg, outPath] = process.argv.slice(2);
  const samples = Number(samplesArg);
  if (!framesPath || !outPath || !Number.isInteger(samples) || samples <= 0) {
    throw new Error("使い方: node pixels.mjs <frames.bin> <samples> <out.ndjson>");
  }
  const buf = readFileSync(framesPath);
  const canvas = createCanvas(W, H);
  const ctx = canvas.getContext("2d");
  const worlds = new Map();
  const lines = [];
  let cur = null;
  let pairs = [];
  let prev = null;
  let prevT = 0;
  let k = 0;
  const seen = new Set();
  const flush = () => {
    if (cur === null) return;
    if (k !== 2 * samples || pairs.length !== samples) {
      throw new Error(`窓 ${cur} のコマが ${k} 枚・${pairs.length} 組（${2 * samples} 枚・${samples} 組のはず）`);
    }
    lines.push(JSON.stringify({ id: cur, v: windowVector(pairs) }));
  };
  for (const fr of readFrames(buf)) {
    if (fr.id !== cur) {
      flush();
      if (seen.has(fr.id)) throw new Error(`窓 ${fr.id} のコマが続いていない`);
      seen.add(fr.id);
      cur = fr.id;
      pairs = [];
      k = 0;
    }
    const lum = renderLum(ctx, worlds, fr);
    if (k % 2 === 0) {
      prev = lum;
      prevT = fr.t;
    } else {
      if (fr.t - prevT !== PAIR_GAP_MS) throw new Error(`窓 ${cur} の組の間が ${fr.t - prevT} ms（${PAIR_GAP_MS} のはず）`);
      pairs.push([prev, lum]);
    }
    k++;
  }
  flush();
  // 1 行目はヘッダ（stats.py が窓の表と照らす）
  const head = JSON.stringify({ kind: "header", samples, windows: lines.length, w: W, h: H, gx: GX, gy: GY });
  writeFileSync(outPath, [head, ...lines].join("\n") + "\n");
}

if (process.argv[1] !== undefined && import.meta.url === pathToFileURL(resolve(process.argv[1])).href) {
  main();
}
