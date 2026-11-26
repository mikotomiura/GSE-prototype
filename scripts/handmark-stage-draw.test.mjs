// 手跡の背景の描画の純関数（src/components/handmarkStageDraw.ts・手跡の PR 4）のテスト。
// 実行: node --test scripts/handmark-stage-draw.test.mjs（Node 22.18 以上は .ts の型を除いて読む）
// 画面と机上の道具が同じ関数を呼ぶので、同じ入力から同じ描画の命令の列が出ること（決定性）と、
// 時計・乱数・画面の部品に依らないことを縛る。
import { test } from "node:test";
import assert from "node:assert/strict";
import { createHash } from "node:crypto";
import { readFileSync } from "node:fs";
import { buildWorld, drawFrame, viewOf } from "../src/components/handmarkStageDraw.ts";
import { CELLS, makeField } from "../src/components/handmarkStageTrace.ts";

/** 描画の命令を文字列の列に書き留める偽の文脈。 */
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

const SHOWN = { speed: 0.31, irreg: 0.4, phase: 12.5, drift: 300.25 };

function draw(shown, field, ripples, calm = 1, seed = 12345) {
  const view = viewOf(320, 200);
  const world = buildWorld(seed, view.W, view.H);
  const { ctx, log } = recorder();
  drawFrame(ctx, world, view, shown, field, ripples, calm);
  return log;
}

test("同じ入力から同じ命令の列が出る", () => {
  const f = makeField();
  f.bend[17] = 0.4;
  f.pullX[40] = 0.02;
  const a = draw(SHOWN, f, [{ x: 0.8, y: 0.5, t: 0.3 }]);
  const b = draw(SHOWN, f, [{ x: 0.8, y: 0.5, t: 0.3 }]);
  assert.deepEqual(a, b);
  assert.equal(a[0], "clearRect(0.000000,0.000000,320.000000,200.000000)");
});

test("配置は種と大きさだけで決まり、数は固定", () => {
  const w1 = buildWorld(7, 320, 200);
  const w2 = buildWorld(7, 320, 200);
  assert.deepEqual(w1, w2);
  assert.equal(w1.blades.length, 34 + 44 + 54 + 64 + 74);
  assert.equal(w1.motes.length, 140);
  assert.notDeepEqual(buildWorld(8, 320, 200).motes[0], w1.motes[0]);
});

test("状態・場・波紋が描画に効き、波紋の経過 1 以上は描かない", () => {
  const zero = makeField();
  const base = draw(SHOWN, zero, []);
  assert.notDeepEqual(draw({ ...SHOWN, speed: 0.6 }, zero, []), base);
  const f = makeField();
  for (let i = 0; i < CELLS; i++) f.bend[i] = 0.5;
  assert.notDeepEqual(draw(SHOWN, f, []), base);
  const withRipple = draw(SHOWN, zero, [{ x: 0.8, y: 0.5, t: 0.3 }]);
  assert.equal(withRipple.filter((l) => l.startsWith("ellipse(")).length, 2);
  assert.deepEqual(draw(SHOWN, zero, [{ x: 0.8, y: 0.5, t: 1 }]), base);
  assert.deepEqual(draw(SHOWN, zero, [{ x: 0.8, y: 0.5, t: Number.NaN }]), base);
  // 「動きを減らす」は漂いと流れを遅くする
  assert.notDeepEqual(draw(SHOWN, zero, [], 0.3), base);
});

test("描画の命令の列の SHA-256（写像を変えたら意図して更新する・机上の画素に効く）", () => {
  const f = makeField();
  f.bend[33] = 0.7;
  f.pullY[90] = -0.05;
  const log = draw(SHOWN, f, [{ x: 1.2, y: 0.3, t: 0.55 }]);
  const sha = createHash("sha256").update(log.join("\n")).digest("hex");
  assert.equal(sha, GOLDEN_SHA);
});

test("時計・乱数・画面の部品を使わない", () => {
  const src = readFileSync(new URL("../src/components/handmarkStageDraw.ts", import.meta.url), "utf8");
  // 注釈の行を除いて調べる
  const code = src
    .split("\n")
    .filter((l) => !l.trim().startsWith("//"))
    .join("\n");
  for (const bad of ["performance", "Date", "Math.random", "react", "@tauri-apps", "window", "document"]) {
    assert.equal(code.includes(bad), false, bad);
  }
});

// 2026-11-15 に、切り出す前の HandmarkStage.tsx の描画の行をそのまま写したものと、12 組の入力で命令の列が一致することを確かめた後の値。
const GOLDEN_SHA = "a071a2655b0a76658ff1ca408a4707abf53543d0f099175e1c3e4c6003e61a16";
