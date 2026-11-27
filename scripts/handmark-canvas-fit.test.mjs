// 手跡の帯と背景の canvas の大きさと拡大の合わせ方のテスト（.steering/20261128-handmark-canvas-half-scale）。
// 実行: node --test scripts/handmark-canvas-fit.test.mjs（Node 22.18 以上は .ts の型を除いて読む）
import { test } from "node:test";
import assert from "node:assert/strict";
import { readFileSync } from "node:fs";
import { canvasDpr, fitCanvas } from "../src/components/handmarkCanvasFit.ts";

/** width・height の代入を数える偽の canvas。 */
function fakeCanvas(width, height) {
  let w = width;
  let h = height;
  const c = { assigns: 0 };
  Object.defineProperty(c, "width", {
    get: () => w,
    set: (v) => {
      w = v;
      c.assigns += 1;
    },
  });
  Object.defineProperty(c, "height", {
    get: () => h,
    set: (v) => {
      h = v;
      c.assigns += 1;
    },
  });
  return c;
}

/** 最後に置いた拡大を覚える偽の文脈。初めは単位行列（文脈の状態が捨てられた後と同じ）。 */
function fakeCtx() {
  return {
    m: [1, 0, 0, 1, 0, 0],
    setTransform(a, b, c, d, e, f) {
      this.m = [a, b, c, d, e, f];
    },
  };
}

test("拡大が単位行列に戻った文脈を、大きさが合っていれば代入せずに拡大だけ戻す（2026-11-28 の半分の大きさ）", () => {
  const canvas = fakeCanvas(2940, 28);
  const ctx = fakeCtx();
  const r = fitCanvas(canvas, ctx, 1470, 14, 2);
  assert.deepEqual(ctx.m, [2, 0, 0, 2, 0, 0]);
  assert.equal(r.resized, false);
  assert.equal(canvas.assigns, 0);
  assert.equal(r.dpr, 2);
});

test("画素の大きさがずれていれば代入し、拡大も置く", () => {
  const canvas = fakeCanvas(1600, 28);
  const ctx = fakeCtx();
  const r = fitCanvas(canvas, ctx, 1470, 14, 2);
  assert.equal(r.resized, true);
  assert.equal(canvas.width, 2940);
  assert.equal(canvas.height, 28);
  assert.deepEqual(ctx.m, [2, 0, 0, 2, 0, 0]);
});

test("合っている間は何度呼んでも width・height を代入しない（代入は中身を消す）", () => {
  const canvas = fakeCanvas(0, 0);
  const ctx = fakeCtx();
  fitCanvas(canvas, ctx, 1470, 956, 2);
  const after = canvas.assigns;
  for (let i = 0; i < 5; i++) {
    const r = fitCanvas(canvas, ctx, 1470, 956, 2);
    assert.equal(r.resized, false);
  }
  assert.equal(canvas.assigns, after);
});

test("dpr だけが変わったら画素の大きさと拡大を合わせ直す", () => {
  const canvas = fakeCanvas(2940, 1912);
  const ctx = fakeCtx();
  const r = fitCanvas(canvas, ctx, 1470, 956, 1);
  assert.equal(r.resized, true);
  assert.equal(canvas.width, 1470);
  assert.equal(canvas.height, 956);
  assert.deepEqual(ctx.m, [1, 0, 0, 1, 0, 0]);
});

test("画素の大きさは四捨五入（今の resize と同じ）", () => {
  const canvas = fakeCanvas(0, 0);
  fitCanvas(canvas, fakeCtx(), 100.3, 10.25, 1.5);
  assert.equal(canvas.width, Math.round(100.3 * 1.5));
  assert.equal(canvas.height, Math.round(10.25 * 1.5));
});

test("canvasDpr: 今の Math.min(devicePixelRatio || 1, 2) と同じで、有限でない値・0 以下は 1", () => {
  assert.equal(canvasDpr(2), 2);
  assert.equal(canvasDpr(1.5), 1.5);
  assert.equal(canvasDpr(3), 2);
  assert.equal(canvasDpr(undefined), 1);
  assert.equal(canvasDpr(0), 1);
  assert.equal(canvasDpr(Number.NaN), 1);
  assert.equal(canvasDpr(-1), 1);
  assert.equal(canvasDpr(Number.POSITIVE_INFINITY), 1);
});

// ---- 呼ぶ順の静的な確かめ（描く経路から合わせ直しが消えたら赤にする・code-reviewer の指摘） ----
const read = (name) => readFileSync(new URL(`../src/components/${name}`, import.meta.url), "utf8");

/** `start` で始まる塊（次の `end` まで）の中で、`first` が `then` より前にあるか。 */
function orderedIn(src, start, end, first, then) {
  const s = src.indexOf(start);
  assert.notEqual(s, -1, `見つからない: ${start}`);
  const e = src.indexOf(end, s + start.length);
  assert.notEqual(e, -1, `塊の終わりが見つからない: ${start}`);
  const block = src.slice(s, e);
  const a = block.indexOf(first);
  const b = block.indexOf(then);
  return a !== -1 && b !== -1 && a < b;
}

const STRIP_ORDERS = [
  // 描く本体: 合わせてから消して描く
  ["    const draw = (): void => {", "\n    };\n", "fit();", "ctx.clearRect("],
  // 閉じたとき: 合わせてから消す
  ["      if (msg === null) {", "\n        return;\n", "fit();", "ctx.clearRect("],
];
const STAGE_ORDERS = [
  // 描く本体: 合わせてから描く
  ["    const loop = (now: number): void => {", "\n    };\n", "fit();", "drawFrame("],
  // 閉じたとき: 合わせてから消す
  ["// 窓が閉じた: 状態も、場も波紋も消す", "\n        return;\n", "fit();", "ctx.clearRect("],
];

test("帯: 描く前と閉じたときの消す前に fit() を呼ぶ", () => {
  const src = read("HandmarkEdgeStrip.tsx");
  for (const [start, end, first, then] of STRIP_ORDERS) {
    assert.ok(orderedIn(src, start, end, first, then), `${start} の中で ${first} が ${then} より前にない`);
  }
});

test("背景: 描く前と閉じたときの消す前に fit() を呼ぶ", () => {
  const src = read("HandmarkStage.tsx");
  for (const [start, end, first, then] of STAGE_ORDERS) {
    assert.ok(orderedIn(src, start, end, first, then), `${start} の中で ${first} が ${then} より前にない`);
  }
});

test("陽性対照: fit() を消すと順の確かめが赤になる", () => {
  for (const [name, orders] of [
    ["HandmarkEdgeStrip.tsx", STRIP_ORDERS],
    ["HandmarkStage.tsx", STAGE_ORDERS],
  ]) {
    const src = read(name);
    for (const [start, end, first, then] of orders) {
      const s = src.indexOf(start);
      const e = src.indexOf(end, s + start.length);
      const cut = src.slice(0, s) + src.slice(s, e).replace(first, "") + src.slice(e);
      assert.equal(orderedIn(cut, start, end, first, then), false, `${name}: ${start}`);
    }
  }
});
