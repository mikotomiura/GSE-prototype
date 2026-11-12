// 手跡の下の縁の帯の、描く間隔の決め方・状態への寄せ方・近さの濃さのテスト（ADR-051）。
// 実行: node --test scripts/handmark-edge-strip.test.mjs（Node 22.18 以上は .ts の型を除いて読む）
import { test } from "node:test";
import assert from "node:assert/strict";
import {
  ACTIVE_FRAME_MS,
  IDLE_FRAME_MS,
  NEAR_MAX,
  NEAR_MIN_ALPHA,
  NEAR_TAU_MS,
  STATE_TICK_MS,
  approachFade,
  blendShown,
  clampNear,
  fadeIsSettling,
  nearTarget,
  nextFrameMs,
} from "../src/components/handmarkStripFrame.ts";

const near = (a, b, eps = 1e-9) => assert.ok(Math.abs(a - b) <= eps, `${a} vs ${b}`);
const calm = { open: true, visible: true, speed: 0, speedTo: 0, fadeSettling: false };

test("nextFrameMs: 見えていなければ描かない", () => {
  assert.equal(nextFrameMs({ ...calm, visible: false }), null);
  // 風があっても、寄せの途中でも、見えていなければ描かない
  assert.equal(nextFrameMs({ ...calm, visible: false, speed: 0.4, speedTo: 0.4, fadeSettling: true }), null);
});

test("nextFrameMs: 閉じたら描かない", () => {
  assert.equal(nextFrameMs({ ...calm, open: false }), null);
  assert.equal(nextFrameMs({ ...calm, open: false, speed: 0.4, speedTo: 0.4, fadeSettling: true }), null);
});

test("nextFrameMs: 風があるか、近さの薄れが寄せの途中なら 33", () => {
  assert.equal(ACTIVE_FRAME_MS, 33);
  assert.equal(nextFrameMs({ ...calm, speed: 0.1 }), 33);
  // 届いた速さだけが 0 より大きい（これから風が立つ）
  assert.equal(nextFrameMs({ ...calm, speedTo: 0.1 }), 33);
  // 風が止んでも、寄せている速さが残っている間は 33
  assert.equal(nextFrameMs({ ...calm, speed: 1e-6, speedTo: 0 }), 33);
  assert.equal(nextFrameMs({ ...calm, fadeSettling: true }), 33);
});

test("nextFrameMs: それ以外は 100", () => {
  assert.equal(IDLE_FRAME_MS, 100);
  assert.equal(nextFrameMs(calm), 100);
});

test("寄せ: 0 で from・250ms 以上で to・その間は線形", () => {
  const a = { speed: 0.2, irreg: 0.1, phase: 3, drift: 10 };
  const b = { speed: 0.6, irreg: 0.5, phase: 5, drift: 11 };
  assert.deepEqual(blendShown(a, b, 0), a);
  assert.deepEqual(blendShown(a, b, STATE_TICK_MS), b);
  assert.deepEqual(blendShown(a, b, STATE_TICK_MS * 10), b);
  assert.deepEqual(blendShown(a, b, -50), a);
  const mid = blendShown(a, b, STATE_TICK_MS / 2);
  near(mid.speed, 0.4);
  near(mid.phase, 4);
  near(mid.drift, 10.5);
  // 非有限の経過は届いた状態をそのまま見せる
  assert.deepEqual(blendShown(a, b, Number.NaN), b);
});

test("寄せは描画の回数に依らない: 同じ時刻の見た目は、何回に分けて呼んでも同じ", () => {
  const a = { speed: 0.2, irreg: 0.1, phase: 3, drift: 10 };
  const b = { speed: 0.6, irreg: 0.5, phase: 5, drift: 11 };
  const t = 170;
  const once = blendShown(a, b, t);
  // 33 ms ごと・100 ms ごと・不規則に何回呼んでも、最後の時刻の値は同じ（積み上げていない）
  for (const steps of [[33, 33, 33, 33, 38], [100, 70], [1, 169], [17, 3, 41, 9, 100]]) {
    let at = 0;
    let last = null;
    for (const s of steps) {
      at += s;
      last = blendShown(a, b, at);
    }
    assert.equal(at, t);
    assert.deepEqual(last, once);
  }
});

test("近さの丸め: 0〜10 に収め、非有限は 0", () => {
  assert.equal(NEAR_MAX, 10);
  assert.equal(clampNear(0), 0);
  assert.equal(clampNear(4.5), 4.5);
  assert.equal(clampNear(10), 10);
  assert.equal(clampNear(11), 10);
  assert.equal(clampNear(1e9), 10);
  assert.equal(clampNear(-3), 0);
  assert.equal(clampNear(Number.NaN), 0);
  assert.equal(clampNear(Number.POSITIVE_INFINITY), 0);
  assert.equal(clampNear(Number.NEGATIVE_INFINITY), 0);
});

test("近さの濃さの目標: 1 − 0.75 × 近さ/10", () => {
  assert.equal(NEAR_MIN_ALPHA, 0.25);
  assert.equal(nearTarget(0), 1);
  near(nearTarget(10), 0.25);
  near(nearTarget(5), 1 - 0.75 * 0.5);
  // 範囲外は丸めてから
  near(nearTarget(99), 0.25);
  near(nearTarget(-5), 1);
  near(nearTarget(Number.NaN), 1);
});

test("濃さの寄せ: 120ms の時定数・目標が同じなら刻みに依らない", () => {
  assert.equal(NEAR_TAU_MS, 120);
  near(approachFade(1, 0.25, 0), 1);
  // 1 時定数で差の 1 − 1/e だけ進む
  near(approachFade(1, 0.25, 120), 0.25 + 0.75 * Math.exp(-1));
  // 1 回で 300ms 進めた値と、細かく分けて進めた値が同じ
  const whole = approachFade(1, 0.25, 300);
  for (const steps of [[33, 33, 33, 33, 33, 33, 33, 33, 36], [100, 100, 100], [150, 150]]) {
    let f = 1;
    for (const s of steps) f = approachFade(f, 0.25, s);
    near(f, whole, 1e-12);
  }
  // 負・非有限の dt は進めない
  near(approachFade(0.6, 0.25, -10), 0.6);
  near(approachFade(0.6, 0.25, Number.NaN), 0.6);
  // 目標が上がれば戻る
  assert.ok(approachFade(0.3, 1, 100) > 0.3);
});

test("寄せの途中かの判定は、目標との差の小ささで決まる", () => {
  assert.equal(fadeIsSettling(1, 1), false);
  assert.equal(fadeIsSettling(0.995, 1), false);
  assert.equal(fadeIsSettling(0.98, 1), true);
  assert.equal(fadeIsSettling(0.25, 1), true);
  // 十分に時間が経てば寄せ終わる
  let f = 1;
  for (let i = 0; i < 40; i++) f = approachFade(f, 0.25, 33);
  assert.equal(fadeIsSettling(f, 0.25), false);
});
