// 手跡の背景の窓のアイコンの層(src/components/handmarkStageIcons.ts・Windows 版・判断 10・13)のテスト。
// 実行: node --test scripts/handmark-stage-icons.test.mjs(Node 22.18 以上は .ts の型を除いて読む)
// 世代の規則を縛る: 新しい番は層を消す区画(reset)から始まる・古い世代と閉じた後の区画は捨てる・
// 閉じる前に一度も区画を受けていなくても、閉じた知らせより前の世代は受けない。
// canvas の無い所で走るよう、区画の無い(tiles が空の)知らせと、層の世代の値だけを見る。
import { test } from "node:test";
import assert from "node:assert/strict";
import { acceptGen, closeIcons, handleIconsMessage, makeIconLayer } from "../src/components/handmarkStageIcons.ts";

const msg = (gen, reset) => ({ gen, screenW: 64, screenH: 64, reset, tiles: [] });

test("a new keeper is accepted only from its reset", () => {
  const layer = makeIconLayer();
  assert.equal(acceptGen(layer, msg(3, false)), false);
  assert.equal(layer.gen, 0);
  assert.equal(acceptGen(layer, msg(3, true)), true);
  assert.equal(layer.gen, 3);
  // 同じ世代の続きは reset でなくても受ける
  assert.equal(acceptGen(layer, msg(3, false)), true);
});

test("an older generation is dropped", () => {
  const layer = makeIconLayer();
  assert.equal(acceptGen(layer, msg(5, true)), true);
  assert.equal(acceptGen(layer, msg(4, true)), false);
  assert.equal(layer.gen, 5);
});

test("after close, the closing keeper's late tiles are dropped even if none arrived before", () => {
  // 開いてすぐ閉じた: 番 G=7 の区画は 1 つも届いていない(layer.gen = 0)。閉じた知らせは stop の後の世代 8。
  const layer = makeIconLayer();
  closeIcons(layer, 8);
  assert.equal(acceptGen(layer, msg(7, true)), false, "閉じた番の遅れた reset を受けた");
  // 次の番(世代 9 以上)の reset は受ける
  assert.equal(acceptGen(layer, msg(10, true)), true);
});

test("close without a closeGen still drops the current generation", () => {
  const layer = makeIconLayer();
  assert.equal(acceptGen(layer, msg(2, true)), true);
  closeIcons(layer, Number.NaN);
  assert.equal(acceptGen(layer, msg(2, true)), false);
  assert.equal(acceptGen(layer, msg(4, true)), true);
});

test("unsafe or missing generations are dropped", () => {
  const layer = makeIconLayer();
  for (const g of [Number.NaN, 2 ** 60, -1.5, undefined, "3"]) {
    assert.equal(acceptGen(layer, msg(g, true)), false, String(g));
  }
});

test("the hook handles a close message and rejects junk", () => {
  const layer = makeIconLayer();
  assert.equal(handleIconsMessage(layer, { closeGen: 6 }), true);
  assert.equal(layer.minGen, 6);
  assert.equal(handleIconsMessage(layer, null), false);
  assert.equal(handleIconsMessage(layer, { gen: 7, screenW: 0, screenH: 64, reset: true, tiles: [] }), false);
  assert.equal(handleIconsMessage(layer, { gen: 7, screenW: 64, screenH: 64, reset: true, tiles: "x" }), false);
});
