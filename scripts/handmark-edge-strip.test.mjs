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
  closedStrip,
  drawStrip,
  fadeAt,
  fadeIsSettling,
  fadeReceive,
  initialFade,
  kickDelayMs,
  nearTarget,
  nextFrameMs,
  receiveStrip,
  shownAt,
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

// ---- 状態の遷移(M1)と濃さの閉じた式(L3): 描画のスケジュールに依らない ----

const S = (speed, irreg, phase, drift) => ({ speed, irreg, phase, drift });
// 届き方の列: [時刻 ms, 状態, 種が替わったか]
const ARRIVALS = [
  [0, S(0.0, 0.0, 0, 0), false],
  [250, S(0.3, 0.2, 1, 2), false],
  [500, S(0.6, 0.5, 3, 5), false],
  [750, S(0.1, 0.1, 4, 6), false],
  [1000, S(0.0, 0.0, 4, 7), false],
  [1250, S(0.5, 0.9, 6, 9), false],
  [1500, S(0.2, 0.3, 7, 10), false],
];
const PROBES = [0, 10, 120, 260, 333, 499, 640, 1100, 1260, 1333, 1499, 1620, 2400];

// 描画のスケジュール: draw(t) が真の時刻だけ描く。届く・描く・見る(PROBES)を時刻順に並べて走らせる。
function run(drawAt, arrivals = ARRIVALS) {
  let st = closedStrip(0);
  const out = [];
  const events = [
    ...arrivals.map(([t, m, c]) => ({ t, k: 0, m, c })),
    ...[...new Set([...Array(2500).keys()].filter(drawAt))].map((t) => ({ t, k: 1 })),
    ...PROBES.map((t) => ({ t, k: 2 })),
  ].sort((a, b) => a.t - b.t || a.k - b.k);
  for (const e of events) {
    if (e.k === 0) st = receiveStrip(st, e.m, e.t, e.c);
    else if (e.k === 1) st = drawStrip(st, e.t);
    else out.push(shownAt(st, e.t));
  }
  return out;
}

test("状態の遷移: 描画 0 回・33ms ごと・100ms ごと・覆われた間は描かない、のどれでも同じ時刻の見た目は等しい", () => {
  const none = run(() => false);
  const every33 = run((t) => t % 33 === 0);
  const every100 = run((t) => t % 100 === 0);
  // 300〜1400 ms は覆われていて描かない(その後見えるようになって描く)
  const covered = run((t) => t % 33 === 0 && (t < 300 || t >= 1400));
  assert.deepEqual(every33, none);
  assert.deepEqual(every100, none);
  assert.deepEqual(covered, none);
});

test("状態の遷移: 届いた状態へ寄せる起点は『今の時刻での寄せた値』(途中で届いても連続する)", () => {
  let st = receiveStrip(closedStrip(0), S(0, 0, 0, 0), 0, false);
  st = receiveStrip(st, S(1, 0, 10, 0), 0, false); // 0 で届いた到達点 (1,.,10)
  // 125ms(半分)の時点で次が届く: 起点はそのときの見た目(0.5, 5)
  st = receiveStrip(st, S(0, 0, 20, 0), 125, false);
  assert.deepEqual(st.from, S(0.5, 0, 5, 0));
  near(shownAt(st, 125).phase, 5);
  near(shownAt(st, 375).phase, 20);
  // 描かずに 1 秒置いてから見ても、起点は凍らない(届いた 2 つ目の寄せは 125〜375 で終わっている)
  assert.deepEqual(shownAt(st, 1125), S(0, 0, 20, 0));
});

test("状態の遷移: 開いていない・種が替わったときは寄せずに置く / 閉じたら戻す", () => {
  let st = receiveStrip(closedStrip(0), S(0.4, 0.5, 8, 9), 100, false);
  assert.equal(st.active, true);
  assert.deepEqual(shownAt(st, 100), S(0.4, 0.5, 8, 9));
  st = receiveStrip(st, S(0.1, 0.1, 1, 1), 200, true);
  assert.deepEqual(shownAt(st, 200), S(0.1, 0.1, 1, 1));
  const c = closedStrip(300);
  assert.equal(c.active, false);
  assert.deepEqual(c.shown, S(0, 0, 0, 0));
  // 閉じた後の最初の状態は寄せずに置く
  assert.deepEqual(shownAt(receiveStrip(c, S(0.2, 0.2, 2, 2), 400, false), 400), S(0.2, 0.2, 2, 2));
});

const NEARS = [
  [100, 10],
  [180, 10],
  [420, 0],
  [900, 5],
];
function runFade(drawAt) {
  let st = initialFade(0);
  const out = [];
  const events = [
    ...NEARS.map(([t, n]) => ({ t, k: 0, n })),
    ...[...Array(1500).keys()].filter(drawAt).map((t) => ({ t, k: 1 })),
    ...PROBES.map((t) => ({ t, k: 2 })),
  ].sort((a, b) => a.t - b.t || a.k - b.k);
  for (const e of events) {
    if (e.k === 0) st = fadeReceive(st, e.n, e.t);
    else if (e.k === 2) out.push(fadeAt(st, e.t));
  }
  return out;
}

test("濃さ: 描画の時刻に依らず、近さの届いた時刻とそのときの濃さからの閉じた式", () => {
  assert.deepEqual(runFade(() => false), runFade((t) => t % 33 === 0));
  assert.deepEqual(runFade(() => false), runFade((t) => t % 100 === 0));
  // 閉じた式そのもの: 100ms で 10 が届く → f0=1, target=0.25
  let st = fadeReceive(initialFade(0), 10, 100);
  near(fadeAt(st, 100), 1);
  near(fadeAt(st, 220), 0.25 + 0.75 * Math.exp(-1));
  // 途中(220)で同じ目標が届いても連続し、後の値も変わらない(指数は記憶を持たない)
  const mid = fadeReceive(st, 10, 220);
  near(fadeAt(mid, 220), fadeAt(st, 220));
  near(fadeAt(mid, 700), fadeAt(st, 700), 1e-12);
  // 目標が変わっても、そのときの濃さから連続して動く
  const back = fadeReceive(st, 0, 220);
  near(fadeAt(back, 220), fadeAt(st, 220));
  assert.ok(fadeAt(back, 600) > fadeAt(back, 220));
  // 時刻が戻っても濃さは f0 を超えて戻らない(負の経過は進めない)
  near(fadeAt(st, 50), 1);
});

test("kickDelayMs: 描いていなければすぐ描く", () => {
  assert.equal(kickDelayMs(null, null, 1000), 0);
});

test("kickDelayMs: 最後に描いてから ACTIVE_FRAME_MS は空ける", () => {
  assert.equal(kickDelayMs(1000, null, 1010), ACTIVE_FRAME_MS - 10);
  assert.equal(kickDelayMs(1000, null, 1000 + ACTIVE_FRAME_MS + 5), 0);
});

test("kickDelayMs: 今の予約が十分早ければ動かさない、遅ければ早める", () => {
  // 風の無い間の 100ms の予約は、33ms まで早める
  assert.equal(kickDelayMs(1000, 1000 + IDLE_FRAME_MS, 1005), ACTIVE_FRAME_MS - 5);
  // 既に 33ms で予約していれば動かさない
  assert.equal(kickDelayMs(1000, 1000 + ACTIVE_FRAME_MS, 1005), null);
});

test("kickDelayMs: 16ms ごとに近さが届いても、1 秒の描画は 30 回まで", () => {
  // 描画と予約を時間の上で模す（frame は予約の時刻に描き、次を IDLE_FRAME_MS で予約する最も遅い場合）
  let lastDrawAt = null;
  let pendingAt = null;
  let draws = 0;
  for (let t = 0; t <= 1000; t += 1) {
    if (pendingAt !== null && t >= pendingAt) {
      lastDrawAt = t;
      draws += 1;
      pendingAt = t + IDLE_FRAME_MS;
    }
    if (t % 16 === 0) {
      const w = kickDelayMs(lastDrawAt, pendingAt, t);
      if (w !== null) pendingAt = t + w;
    }
  }
  assert.ok(draws <= Math.ceil(1000 / ACTIVE_FRAME_MS), `draws=${draws}`);
  assert.ok(draws >= 25, `draws=${draws}`);
});
