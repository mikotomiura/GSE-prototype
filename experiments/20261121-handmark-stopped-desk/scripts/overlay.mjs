// 止まりの層（ADR-056）を重ねた画素の特徴。画面（HandmarkStage.tsx）と同じ順で、今のコマの画
// （handmarkStageDraw.ts の drawFrame）に止まりの層（handmarkStoppedDraw.ts の drawStopped）を重ねる。
// 漏れの机上の道具の pixels.mjs は書き換えず、読みと窓の値の関数だけを借りる。
//
//   node overlay.mjs windows <frames.bin> <stopped.bin> <samples> <out.ndjson>
//       窓のコマ（gse-replay --frames）と止まりの層のコマ（--stopped-frames）を同じ順に読み、pixels.mjs と同じ
//       窓の値（325）を出す。漏れの検査（ADR-051 D3）の B_pixel′ に使う。
//   node overlay.mjs queries <qframes.bin> <q.ndjson> <out.f32> [--layer final|base|stopped] [--control none|clock_stop|clock_start]
//       問い合わせのコマ（--stopped-query-frames）を 1 枚ずつ描き、16 × 10 の明るさ（float32 × 160）を順に書く。
//       --layer: final（既定・基層と跡と止まりの層）・base（止まりの層なし）・stopped（止まりの層だけ・透明の上）
//       --control: 経過を運ぶ印を上の端に足す陽性対照（clock_stop = 止まりの始まりからの経過、clock_start =
//       手跡を出し始めた時刻からの経過。10 分・2 時間で端まで）。人の記録には使わない（run.sh が止める）。
//
// 限界: 画面は状態と止まりの層を 250 ms かけて寄せるが、ここはその時刻の値をそのまま描く（pixels.mjs と同じ）。
import { readFileSync, writeFileSync } from "node:fs";
import { resolve } from "node:path";
import { pathToFileURL } from "node:url";
import { createCanvas } from "@napi-rs/canvas";
import { buildWorld, drawFrame, viewOf } from "../../../src/components/handmarkStageDraw.ts";
import { drawStopped } from "../../../src/components/handmarkStoppedDraw.ts";
import { CELLS, decodeCells, makeField, RIPPLE_MS } from "../../../src/components/handmarkStageTrace.ts";
import { GX, GY, H, W, readFrames, windowVector } from "../../20261115-handmark-leak-desk/scripts/pixels.mjs";

const BG = 128;
const PAIR_GAP_MS = 250;
const TAIL = 41; // v・ambient × 3・strength（f64）と form（u8）
const FORMS = { 1: "band", 2: "motes", 3: "wind" };

/** 止まりの層の尾（replay.rs の write_stopped）を読む。 */
export function readTail(dv, o) {
  const v = dv.getFloat64(o, true);
  const ambient = [dv.getFloat64(o + 8, true), dv.getFloat64(o + 16, true), dv.getFloat64(o + 24, true)];
  const strength = dv.getFloat64(o + 32, true);
  const form = FORMS[dv.getUint8(o + 40)];
  if (form === undefined) throw new Error(`壊れた尾（形 ${dv.getUint8(o + 40)}）`);
  return { v, ambient, form, strength };
}

/** 止まりの層のコマ（id u32・t u64・尾）の列を読む。 */
export function* readStopped(buf) {
  const dv = new DataView(buf.buffer, buf.byteOffset, buf.byteLength);
  for (let o = 0; o < buf.byteLength; o += 12 + TAIL) {
    yield { id: dv.getUint32(o, true), t: Number(dv.getBigUint64(o + 4, true)), stopped: readTail(dv, o + 12) };
  }
}

/** 問い合わせのコマ（基層のコマ＋尾）の列を読む。基層の並びは replay.rs の write_frame（pixels.mjs と同じ）。 */
export function* readQueryFrames(buf) {
  const dv = new DataView(buf.buffer, buf.byteOffset, buf.byteLength);
  let o = 0;
  while (o < buf.byteLength) {
    const start = o;
    o += 4 + 8 + 32 + 4;
    const hasField = dv.getUint8(o);
    o += 1 + (hasField === 1 ? CELLS * 3 : 0);
    if (hasField !== 0 && hasField !== 1) throw new Error(`壊れたコマ（場の印 ${hasField}）`);
    const n = dv.getUint8(o);
    o += 1 + n * 10;
    const base = readFrames(buf.subarray(start, o)).next().value;
    const stopped = readTail(dv, o);
    o += TAIL;
    yield { ...base, stopped };
  }
}

const finite = (v, f) => (Number.isFinite(v) ? v : f);

/** 1 コマを描き、灰色に重ねた明るさのマスの平均（GX × GY）を返す（pixels.mjs の renderLum と同じ計算）。 */
export function renderLum(ctx, worlds, fr, layer = "final", mark = null) {
  let world = worlds.get(fr.layoutSeed);
  if (world === undefined) {
    world = buildWorld(fr.layoutSeed, W, H);
    worlds.set(fr.layoutSeed, world);
  }
  const view = viewOf(W, H);
  if (layer === "stopped") {
    ctx.clearRect(0, 0, W, H);
  } else {
    const field = makeField();
    if (fr.cells !== null) decodeCells(Array.from(fr.cells), field);
    const shown = {
      speed: Math.max(0, finite(fr.shown.speed, 0)),
      irreg: Math.max(0, Math.min(1, finite(fr.shown.irreg, 0))),
      phase: finite(fr.shown.phase, 0),
      drift: finite(fr.shown.drift, 0),
    };
    drawFrame(ctx, world, view, shown, field, fr.ripples, 1);
  }
  // 画面と同じ順: drawFrame の後に drawStopped
  if (layer !== "base") drawStopped(ctx, world, view, fr.stopped, 1);
  if (mark !== null) {
    ctx.globalAlpha = 1;
    ctx.fillStyle = "#000000";
    ctx.fillRect(0, 0, W * Math.max(0, Math.min(1, mark)), 12);
  }
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
      out[gy * GX + Math.floor(x / bw)] += (a * lum + (1 - a) * BG) / 255;
    }
  }
  for (let k = 0; k < out.length; k++) out[k] /= bw * bh;
  return out;
}

function windowsMain(framesPath, stoppedPath, samples, outPath) {
  const base = readFrames(readFileSync(framesPath));
  const st = readStopped(readFileSync(stoppedPath));
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
    if (k !== 2 * samples || pairs.length !== samples) throw new Error(`窓 ${cur} のコマが ${k} 枚`);
    lines.push(JSON.stringify({ id: cur, v: windowVector(pairs) }));
  };
  for (const fr of base) {
    const s = st.next();
    if (s.done || s.value.id !== fr.id || s.value.t !== fr.t) throw new Error(`止まりの層のコマが窓のコマと揃わない（窓 ${fr.id}）`);
    if (fr.id !== cur) {
      flush();
      if (seen.has(fr.id)) throw new Error(`窓 ${fr.id} のコマが続いていない`);
      seen.add(fr.id);
      cur = fr.id;
      pairs = [];
      k = 0;
    }
    const lum = renderLum(ctx, worlds, { ...fr, stopped: s.value.stopped });
    if (k % 2 === 0) {
      prev = lum;
      prevT = fr.t;
    } else {
      if (fr.t - prevT !== PAIR_GAP_MS) throw new Error(`窓 ${cur} の組の間が ${fr.t - prevT} ms`);
      pairs.push([prev, lum]);
    }
    k++;
  }
  if (!st.next().done) throw new Error("止まりの層のコマが余る");
  flush();
  const head = JSON.stringify({ kind: "header", samples, windows: lines.length, w: W, h: H, gx: GX, gy: GY, overlay: "stopped" });
  writeFileSync(outPath, [head, ...lines].join("\n") + "\n");
}

function queriesMain(qframesPath, queriesPath, outPath, layer, control) {
  const qs = readFileSync(queriesPath, "utf-8").split("\n").filter((l) => l.trim() !== "").map((l) => JSON.parse(l));
  const canvas = createCanvas(W, H);
  const ctx = canvas.getContext("2d");
  const worlds = new Map();
  const out = new Float32Array(qs.length * GX * GY);
  let n = 0;
  for (const fr of readQueryFrames(readFileSync(qframesPath))) {
    const q = qs[n];
    if (q === undefined || fr.id !== n || fr.t !== q.q) throw new Error(`問い合わせ ${n} のコマが揃わない`);
    let mark = null;
    if (control === "clock_stop") mark = q.e / 600_000;
    else if (control === "clock_start") mark = q.s0 / 7_200_000;
    out.set(renderLum(ctx, worlds, fr, layer, mark), n * GX * GY);
    n++;
  }
  if (n !== qs.length) throw new Error(`コマが ${n} 枚・問い合わせが ${qs.length} 件`);
  writeFileSync(outPath, Buffer.from(out.buffer));
}

function main() {
  const [mode, ...rest] = process.argv.slice(2);
  if (mode === "windows") {
    const [f, s, samples, o] = rest;
    const n = Number(samples);
    if (!f || !s || !o || !Number.isInteger(n) || n <= 0) throw new Error("使い方: overlay.mjs windows <frames> <stopped> <samples> <out>");
    windowsMain(f, s, n, o);
    return;
  }
  if (mode === "queries") {
    const [qf, qn, o, ...opts] = rest;
    let layer = "final";
    let control = "none";
    for (let i = 0; i < opts.length; i += 2) {
      if (opts[i] === "--layer") layer = opts[i + 1];
      else if (opts[i] === "--control") control = opts[i + 1];
      else throw new Error(`知らない引数 ${opts[i]}`);
    }
    if (!["final", "base", "stopped"].includes(layer)) throw new Error(`--layer ${layer}`);
    if (!["none", "clock_stop", "clock_start"].includes(control)) throw new Error(`--control ${control}`);
    if (!qf || !qn || !o) throw new Error("使い方: overlay.mjs queries <qframes> <q.ndjson> <out.f32>");
    queriesMain(qf, qn, o, layer, control);
    return;
  }
  throw new Error("使い方: overlay.mjs windows|queries …");
}

if (process.argv[1] !== undefined && import.meta.url === pathToFileURL(resolve(process.argv[1])).href) {
  main();
}

export { RIPPLE_MS };
