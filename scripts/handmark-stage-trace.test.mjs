// 手跡の背景の層の跡の枠と受け取りの判定のテスト（ADR-040 D4）。
// 実行: node --test scripts/handmark-stage-trace.test.mjs（Node 22.18 以上は .ts の型を除いて読む）
import { test } from "node:test";
import assert from "node:assert/strict";
import {
  RIPPLE_MS,
  RIPPLE_SLOTS,
  STALE_MS,
  addRipple,
  clearRipples,
  makeReceiver,
  makeRipples,
  receive,
  rippleAge,
  sweepRipples,
} from "../src/components/handmarkStageTrace.ts";

const empty = (s) => s.x === 0 && s.y === 0 && s.t0 === null;

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

const msg = (over) => ({
  epoch: 0, tMs: 0, cursorOn: true, clickOn: true, wheelOn: true, x: 0, y: 0, moved: true, clicked: false, wheel: 0,
  ...over,
});

test("古い世代の値は捨て、切ったことを知らせる", () => {
  const rc = makeReceiver();
  assert.deepEqual(receive(rc, msg({ epoch: 0, tMs: 0 }), 100), {
    use: true, cursorOff: false, clickOff: false, wheelOff: false,
  });
  const off = receive(rc, msg({ epoch: 1, tMs: 16, cursorOn: false, moved: false }), 116);
  assert.deepEqual(off, { use: true, cursorOff: true, clickOff: false, wheelOff: false });
  // 切る前に送られて遅れて届いた値
  assert.equal(receive(rc, msg({ epoch: 0, tMs: 10 }), 117).use, false);
  assert.equal(rc.cursorOn, false);
  // 入れ直した世代は受ける
  assert.equal(receive(rc, msg({ epoch: 2, tMs: 32 }), 132).use, true);
  assert.equal(rc.cursorOn, true);
});

test("描画が止まっていた間などに遅れて届いた値は描かない", () => {
  const rc = makeReceiver();
  assert.equal(receive(rc, msg({ tMs: 0 }), 100).use, true);
  assert.equal(receive(rc, msg({ tMs: 16 }), 116 + STALE_MS).use, true);
  assert.equal(receive(rc, msg({ tMs: 32 }), 133 + STALE_MS).use, false);
  // 遅れが解けたら受ける
  assert.equal(receive(rc, msg({ tMs: 48 }), 150).use, true);
});

test("切った知らせは遅れて届いても効く", () => {
  const rc = makeReceiver();
  receive(rc, msg({ tMs: 0 }), 100);
  const v = receive(rc, msg({ epoch: 1, tMs: 16, clickOn: false, moved: false }), 5000);
  assert.equal(v.use, false);
  assert.equal(v.clickOff, true);
  assert.equal(rc.clickOn, false);
});

test("ホイールを切った知らせも届き、切る前に回した量は捨てる", () => {
  const rc = makeReceiver();
  receive(rc, msg({ tMs: 0 }), 100);
  const v = receive(rc, msg({ epoch: 1, tMs: 16, wheelOn: false, moved: false }), 116);
  assert.equal(v.wheelOff, true);
  assert.equal(receive(rc, msg({ epoch: 0, tMs: 10, wheel: 1 }), 117).use, false);
});
