// 手跡の止まりの層の描画の純関数（src/components/handmarkStoppedDraw.ts・ADR-056）のテスト。
// 実行: node --test scripts/handmark-stopped-draw.test.mjs（Node 22.18 以上は .ts の型を除いて読む）
// 画面と机上の道具が drawFrame の後に同じに呼ぶので、決定性と、v = 0 で何も描かないこと、形が止まりの長さを
// 持たない（入力に経過の口が無い）ことを縛る。
import { test } from "node:test";
import assert from "node:assert/strict";
import { readFileSync } from "node:fs";
import { buildWorld, viewOf } from "../src/components/handmarkStageDraw.ts";
import { drawStopped, lerpStopped, parseStopped, stoppedIsInvisible } from "../src/components/handmarkStoppedDraw.ts";

function recorder() {
  const log = [];
  const ctx = {};
  for (const m of ["beginPath", "moveTo", "lineTo", "closePath", "quadraticCurveTo", "arc", "ellipse", "fill", "stroke", "clearRect"]) {
    ctx[m] = (...a) => log.push(`${m}(${a.map((v) => (typeof v === "number" ? v.toFixed(6) : v)).join(",")})`);
  }
  for (const p of ["globalAlpha", "fillStyle", "strokeStyle", "lineWidth"]) {
    Object.defineProperty(ctx, p, {
      set(v) {
        log.push(`${p}=${typeof v === "number" ? v.toFixed(6) : v}`);
      },
    });
  }
  return { ctx, log };
}

function draw(stopped, calm = 1, seed = 12345) {
  const view = viewOf(320, 200);
  const world = buildWorld(seed, view.W, view.H);
  const { ctx, log } = recorder();
  drawStopped(ctx, world, view, stopped, calm);
  return log;
}

const FORMS = ["band", "motes", "wind"];
const frame = (form, v = 1, ambient = [0.2, -0.3, 0.1], strength = 0.5) => ({ v, ambient, form, strength });

test("同じ入力から同じ命令の列が出て、形ごとに描く", () => {
  for (const form of FORMS) {
    const a = draw(frame(form));
    assert.deepEqual(a, draw(frame(form)));
    assert.ok(a.length > 0, form);
    // 消さない（drawFrame の上に重ねる）
    assert.ok(!a.some((l) => l.startsWith("clearRect")), form);
  }
  assert.notDeepEqual(draw(frame("band")), draw(frame("wind")));
});

test("v か強さが 0、または null なら何も描かない", () => {
  for (const form of FORMS) {
    assert.deepEqual(draw(frame(form, 0)), []);
    assert.deepEqual(draw(frame(form, 1, [0.2, -0.3, 0.1], 0)), []);
  }
  assert.deepEqual(draw(null), []);
  assert.ok(stoppedIsInvisible(null));
});

test("ambient が動きに効き、v は濃さだけに効く（大きさ・数・位置は v で変わらない）", () => {
  for (const form of FORMS) {
    assert.notDeepEqual(draw(frame(form, 1, [0.2, -0.3, 0.1])), draw(frame(form, 1, [-0.5, 0.4, 0.3])), form);
    // v を変えると globalAlpha の行だけが変わる
    const strip = (log) => log.filter((l) => !l.startsWith("globalAlpha"));
    assert.deepEqual(strip(draw(frame(form, 0.4))), strip(draw(frame(form, 1))), form);
  }
});

test("届いた値を確かめる: 知らない形・有限でない値・長さの違う ambient は捨て、範囲の外は切る", () => {
  assert.equal(parseStopped(null), null);
  assert.equal(parseStopped({ v: 1, ambient: [0, 0, 0], form: "leaf", strength: 1 }), null);
  assert.equal(parseStopped({ v: NaN, ambient: [0, 0, 0], form: "band", strength: 1 }), null);
  assert.equal(parseStopped({ v: 1, ambient: [0, 0], form: "band", strength: 1 }), null);
  assert.equal(parseStopped({ v: 1, ambient: [0, "x", 0], form: "band", strength: 1 }), null);
  assert.deepEqual(parseStopped({ v: 3, ambient: [2, -2, 0.5], form: "motes", strength: -1 }), {
    v: 1,
    ambient: [1, -1, 0.5],
    form: "motes",
    strength: 0,
  });
});

test("寄せは線形で、形と強さは寄せ先のもの", () => {
  const a = frame("band", 0, [0, 0, 0], 0.2);
  const b = frame("wind", 1, [1, -1, 0.5], 0.8);
  assert.deepEqual(lerpStopped(a, b, 0.5), { v: 0.5, ambient: [0.5, -0.5, 0.25], form: "wind", strength: 0.8 });
  assert.deepEqual(lerpStopped(a, b, 2), { ...b, ambient: [1, -1, 0.5] });
});

test("時計・乱数・画面の部品・イベントを使わない", () => {
  const raw = readFileSync(new URL("../src/components/handmarkStoppedDraw.ts", import.meta.url), "utf8");
  // コメント（禁止の語を説明に書いている）を除いた本文で見る
  const src = raw.replace(/\/\*[\s\S]*?\*\//g, "").replace(/\/\/.*$/gm, "");
  assert.ok(raw.includes("Math.random") && !src.includes("Math.random"), "コメントの除き方が空回りしている");
  for (const banned of ["performance", "Date", "Math.random", "react", "@tauri-apps", "listen", "requestAnimationFrame"]) {
    assert.ok(!src.includes(banned), banned);
  }
});

test("画面は drawFrame の後に drawStopped を呼び、その後にアイコンを重ねる（机上の道具と同じ順）", () => {
  const src = readFileSync(new URL("../src/components/HandmarkStage.tsx", import.meta.url), "utf8");
  const f = src.indexOf("drawFrame(ctx");
  const s = src.indexOf("drawStopped(ctx");
  const i = src.indexOf("drawIconsAtop(ctx");
  assert.ok(f > 0 && s > f && i > s, `${f} ${s} ${i}`);
});

test("机上の重ね描き（overlay.mjs）も画面と同じ純関数を同じ順に呼ぶ", () => {
  const src = readFileSync(
    new URL("../experiments/20261121-handmark-stopped-desk/scripts/overlay.mjs", import.meta.url),
    "utf8",
  );
  assert.ok(src.includes('from "../../../src/components/handmarkStageDraw.ts"'), "drawFrame の出どころ");
  assert.ok(src.includes('from "../../../src/components/handmarkStoppedDraw.ts"'), "drawStopped の出どころ");
  const body = src.slice(src.indexOf("export function renderLum"));
  const f = body.indexOf("drawFrame(ctx");
  const s = body.indexOf("drawStopped(ctx");
  assert.ok(f > 0 && s > f, `${f} ${s}`);
});
