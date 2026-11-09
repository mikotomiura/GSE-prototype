// 手跡の背景の層の跡の枠・受け取りの判定・場の補間のテスト（ADR-050 D4）。試作の件の写し＋場の件。
// 実行: node --test scripts/handmark-stage-trace.test.mjs（Node 22.18 以上は .ts の型を除いて読む）
// ホイールは PR 5（このファイルにもホイールの件は無い）。
import { test } from "node:test";
import assert from "node:assert/strict";
import {
  BEND_MAX,
  CELLS,
  CELL,
  GRID_H,
  GRID_W,
  MOTE_MAX,
  RIPPLE_MS,
  RIPPLE_SLOTS,
  STALE_MS,
  TRACE_TTL_MS,
  addRipple,
  clearField,
  clearRipples,
  decodeCells,
  fieldIsZero,
  lerpField,
  makeField,
  makeReceiver,
  makeRipples,
  receive,
  receiveRipple,
  rippleAge,
  sampleField,
  sweepRipples,
  traceExpired,
} from "../src/components/handmarkStageTrace.ts";

const empty = (s) => s.x === 0 && s.y === 0 && s.t0 === null;
const near = (a, b, eps = 1e-6) => assert.ok(Math.abs(a - b) <= eps, `${a} vs ${b}`);

test("枠の数は増えず、古いものから上書きする", () => {
  const r = makeRipples();
  for (let i = 0; i < 20; i++) addRipple(r, i, i, 1000 + i);
  assert.equal(r.ripples.length, RIPPLE_SLOTS);
  assert.deepEqual(
    r.ripples.map((s) => s.x).sort((a, b) => a - b),
    [14, 15, 16, 17, 18, 19],
  );
});

test("寿命を過ぎた枠は、入力が来なくても位置と時刻が消える", () => {
  const r = makeRipples();
  addRipple(r, 300, 200, 1000);
  addRipple(r, 50, 60, 1500);
  sweepRipples(r, 1000 + RIPPLE_MS - 1);
  assert.equal(r.ripples.filter(empty).length, RIPPLE_SLOTS - 2);
  sweepRipples(r, 1000 + RIPPLE_MS);
  assert.ok(empty(r.ripples[0]));
  assert.equal(r.ripples[1].x, 50);
  sweepRipples(r, 1500 + RIPPLE_MS);
  assert.ok(r.ripples.every(empty));
  // 陽性対照: 掃除を呼ばなければ位置は残る（描かないだけでは消えない）
  const kept = makeRipples();
  addRipple(kept, 300, 200, 1000);
  assert.equal(rippleAge(kept.ripples[0], 1000 + RIPPLE_MS), null);
  assert.equal(kept.ripples[0].x, 300);
});

test("切ったら全部の枠が消え、入れ直しても前の跡は出ない", () => {
  const r = makeRipples();
  addRipple(r, 1, 2, 10);
  addRipple(r, 3, 4, 20);
  clearRipples(r);
  assert.ok(r.ripples.every(empty));
  assert.ok(r.ripples.every((s) => rippleAge(s, 30) === null));
  assert.equal(r.next, 0);
});

const msg = (over) => ({ epoch: 0, tMs: 0, ...over });

test("古い世代の値は捨て、世代が進んだことを知らせる", () => {
  const rc = makeReceiver();
  // 最初の値は基準になる（世代は -1 から 0 へ進んだ扱いで、消すものは無い）
  assert.deepEqual(receive(rc, msg({ epoch: 0, tMs: 0 }), 100), { use: true, reset: true });
  assert.deepEqual(receive(rc, msg({ epoch: 0, tMs: 16 }), 116), { use: true, reset: false });
  const adv = receive(rc, msg({ epoch: 1, tMs: 32 }), 132);
  assert.deepEqual(adv, { use: true, reset: true });
  // 切る前に送られて遅れて届いた値
  assert.deepEqual(receive(rc, msg({ epoch: 0, tMs: 40 }), 141), { use: false, reset: false });
  assert.equal(rc.epoch, 1);
  // 進んだ世代は受ける
  assert.deepEqual(receive(rc, msg({ epoch: 2, tMs: 48 }), 148), { use: true, reset: true });
});

test("描画が止まっていた間などに遅れて届いた値は描かない", () => {
  const rc = makeReceiver();
  assert.equal(receive(rc, msg({ tMs: 0 }), 100).use, true);
  assert.equal(receive(rc, msg({ tMs: 16 }), 116 + STALE_MS).use, true);
  assert.equal(receive(rc, msg({ tMs: 32 }), 133 + STALE_MS).use, false);
  // 遅れが解けたら受ける
  assert.equal(receive(rc, msg({ tMs: 48 }), 150).use, true);
});

test("世代を進める知らせは、遅れて届いても効く", () => {
  const rc = makeReceiver();
  receive(rc, msg({ tMs: 0 }), 100);
  const v = receive(rc, msg({ epoch: 1, tMs: 16 }), 5000);
  assert.equal(v.use, false);
  assert.equal(v.reset, true);
  assert.equal(rc.epoch, 1);
});

test("波紋の種も、遅れすぎたものは捨てる（場と同じ基準）", () => {
  const rc = makeReceiver();
  assert.equal(receiveRipple(rc, 0, 100), true);
  assert.equal(receiveRipple(rc, 16, 116 + STALE_MS), true);
  assert.equal(receiveRipple(rc, 32, 133 + STALE_MS), false);
  // 場の受け取りと基準を共有する
  receive(rc, msg({ tMs: 48 }), 148);
  assert.equal(receiveRipple(rc, 64, 164), true);
});

test("最後に場を受け取ってから 1 秒で、場を 0 にする時になる", () => {
  assert.equal(traceExpired(1000, 1000 + TRACE_TTL_MS - 1), false);
  assert.equal(traceExpired(1000, 1000 + TRACE_TTL_MS), true);
  // まだ場を受け取っていない
  assert.equal(traceExpired(-Infinity, 0), true);
  assert.equal(TRACE_TTL_MS, 1000);
  // 場を 0 にすると、補間の読みも 0 になる（消した後に前の跡が出ない）
  const f = makeField();
  f.bend.fill(0.5);
  f.pullX.fill(0.02);
  assert.ok(!fieldIsZero(f));
  clearField(f);
  assert.ok(fieldIsZero(f));
  const v = sampleField(f, 0.8, 0.5);
  assert.deepEqual([v.bend, v.pullX, v.pullY], [0, 0, 0]);
});

test("i8 の値を戻す（bend は × BEND_MAX / 127・pull は × MOTE_MAX / 127）", () => {
  const cells = new Array(CELLS * 3).fill(0);
  cells[0] = 127;
  cells[1] = -127;
  cells[2] = 64;
  cells[3] = -127;
  cells[(CELLS - 1) * 3 + 2] = 127;
  const f = makeField();
  assert.equal(decodeCells(cells, f), true);
  near(f.bend[0], BEND_MAX);
  near(f.pullX[0], -MOTE_MAX);
  near(f.pullY[0], (64 * MOTE_MAX) / 127);
  near(f.bend[1], -BEND_MAX);
  near(f.pullY[CELLS - 1], MOTE_MAX);
  // 範囲の外の値は 127 で切る
  cells[0] = 1000;
  assert.equal(decodeCells(cells, f), true);
  near(f.bend[0], BEND_MAX);
});

test("長さが違う・数でない場は受けず、書き込まない", () => {
  const f = makeField();
  f.bend.fill(0.25);
  assert.equal(decodeCells(new Array(CELLS * 3 - 1).fill(0), f), false);
  const bad = new Array(CELLS * 3).fill(0);
  bad[7] = Number.NaN;
  assert.equal(decodeCells(bad, f), false);
  assert.equal(f.bend[0], 0.25);
});

/** マスごとに違う値の場（2 の冪の分数なので f32 でも正確）。 */
function patterned() {
  const f = makeField();
  for (let j = 0; j < GRID_H; j++) {
    for (let c = 0; c < GRID_W; c++) {
      const i = j * GRID_W + c;
      f.bend[i] = ((c * 7 + j * 3) % 16) / 16 - 0.5;
      f.pullX[i] = (c - 8) / 256;
      f.pullY[i] = (j - 5) / 256;
    }
  }
  return f;
}

test("補間: マスの中心では、そのマスの値そのもの", () => {
  const f = patterned();
  for (let j = 0; j < GRID_H; j++) {
    for (let c = 0; c < GRID_W; c++) {
      const v = sampleField(f, (c + 0.5) * CELL, (j + 0.5) * CELL);
      const i = j * GRID_W + c;
      near(v.bend, f.bend[i]);
      near(v.pullX, f.pullX[i]);
      near(v.pullY, f.pullY[i]);
    }
  }
  // 陽性対照: マスの中心でなければ、値そのものにはならない
  const mid = sampleField(f, 0.15, 0.05);
  assert.notEqual(mid.bend, f.bend[1]);
});

test("補間: マスの境で連続し、境の中点は両隣の平均になる", () => {
  const f = patterned();
  const eps = 1e-7;
  for (let k = 1; k < GRID_W; k++) {
    const x = k * CELL;
    const y = 0.35;
    const a = sampleField(f, x - eps, y);
    const b = sampleField(f, x + eps, y);
    near(a.bend, b.bend, 1e-5);
    near(a.pullX, b.pullX, 1e-5);
    const l = sampleField(f, x - CELL / 2, y);
    const r = sampleField(f, x + CELL / 2, y);
    near((l.bend + r.bend) / 2, sampleField(f, x, y).bend, 1e-6);
  }
  for (let k = 1; k < GRID_H; k++) {
    const y = k * CELL;
    const a = sampleField(f, 0.7, y - eps);
    const b = sampleField(f, 0.7, y + eps);
    near(a.bend, b.bend, 1e-5);
    near(a.pullY, b.pullY, 1e-5);
  }
});

test("補間: 箱の外は端のマスに丸める（外挿しない）", () => {
  const f = patterned();
  const at = (c, j) => j * GRID_W + c;
  const row = (j) => (j + 0.5) * CELL;
  const col = (c) => (c + 0.5) * CELL;
  near(sampleField(f, -5, row(3)).bend, f.bend[at(0, 3)]);
  near(sampleField(f, 100, row(3)).bend, f.bend[at(GRID_W - 1, 3)]);
  near(sampleField(f, col(4), -5).bend, f.bend[at(4, 0)]);
  near(sampleField(f, col(4), 100).bend, f.bend[at(4, GRID_H - 1)]);
  near(sampleField(f, -5, -5).bend, f.bend[at(0, 0)]);
  near(sampleField(f, 100, 100).bend, f.bend[at(GRID_W - 1, GRID_H - 1)]);
  // 数でない座標は 0 とみなす（NaN が値に混ざらない）
  assert.ok(Number.isFinite(sampleField(f, Number.NaN, Number.NaN).bend));
});

test("場の寄せ: 0 → 1 の間を線形に進み、範囲の外は丸める", () => {
  const a = makeField();
  const b = makeField();
  const out = makeField();
  b.bend.fill(0.8);
  lerpField(a, b, 0.25, out);
  near(out.bend[10], 0.2);
  lerpField(a, b, 2, out);
  near(out.bend[10], 0.8);
  lerpField(a, b, -1, out);
  near(out.bend[10], 0);
});
