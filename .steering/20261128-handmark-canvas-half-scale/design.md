# 設計（v1）

## 根本原因

`HandmarkEdgeStrip.tsx`・`HandmarkStage.tsx` は、canvas の画素の大きさ（`canvas.width`/`height` = CSS の大きさ × dpr）と 2D の文脈の拡大（`ctx.setTransform(dpr, 0, 0, dpr, 0, 0)`）を `resize()` の中でだけ設定する。`resize()` は起動時と `window` の `resize` イベントでしか呼ばれない。描くときは座標を CSS の px（W×H）で渡すので、拡大が単位行列に戻ると、描いたものが canvas の左上の 1/dpr（Retina では横も縦も半分）に縮む。

2026-11-28 の画面の観測（requirement.md）は、横がちょうど半分・線が帯の上の端に寄る、の 2 点でこの形に合う。窓・WebView の大きさは全幅で正しく、`resize` が来なかっただけ（W が古い）なら CSS の拡大で全幅に伸びて見えるはずなので、それでは説明できない。拡大が戻った理由（WebKit が 2D の文脈を作り直す・状態を捨てる）は確かめていない。直しはこの理由に依らない形にする。

## アプローチ

描くたびに、描く前に「大きさと拡大を合わせる」を通す。

- 新しい純関数 `fitCanvas(canvas, ctx, cssW, cssH, rawDpr)`（`src/components/handmarkCanvasFit.ts`）:
  - `dpr = min(有限で正の rawDpr か 1, 2)`（今の `Math.min(window.devicePixelRatio || 1, 2)` と同じ値）
  - 画素の大きさ `round(cssW × dpr)`・`round(cssH × dpr)` が今の `canvas.width`/`height` と違うときだけ代入する（代入は中身を消すので毎回はしない）。
  - 拡大は毎回 `ctx.setTransform(dpr, 0, 0, dpr, 0, 0)` で置き直す（安い・状態に依らない）。
  - 大きさを変えたかを返す。
- 帯: `draw()` の頭で `fitCanvas(…, window.innerWidth, window.innerHeight, window.devicePixelRatio)` を呼び、W・H を更新する。大きさが変わったら粒の配置を作り直す（今の `resize()` と同じ）。
- 背景: `loop` の `drawFrame` の前で同じものを呼び、`view` が変わったら `rebuild`（今の `resize()` と同じ）。
- `resize()` は `fitCanvas` を呼ぶ形に置き換える（同じ処理を 2 か所に持たない）。`resize` イベントの受けは残す。

## 変更対象

- 新規 `src/components/handmarkCanvasFit.ts` — `fitCanvas`・`canvasDpr`
- `src/components/HandmarkEdgeStrip.tsx` — `resize()` と `draw()` の頭
- `src/components/HandmarkStage.tsx` — `resize()` と `loop` の描く前
- 新規 `scripts/handmark-canvas-fit.test.mjs`・`package.json` の `test:handmark` に足す

## 既存パターンとの整合

- 描画の判定を純関数にして node のテストで確かめる形は `handmarkStripFrame.ts`・`handmarkStageDraw.ts` と同じ。
- 写像（`drawFrame`・帯の `draw` の式）は変えない。机上の道具 `pixels.mjs` は node の canvas で大きさを決めて描くので影響しない。

## テスト戦略

- `scripts/handmark-canvas-fit.test.mjs`（偽の canvas と文脈）:
  1. 拡大が単位行列に戻った文脈で、大きさが合っていれば代入せず、拡大だけ (2,0,0,2,0,0) に戻す（今回の不具合の形）。
  2. `width`/`height` がずれていれば代入し、拡大も置く。
  3. 大きさが合っていれば `width`/`height` を一度も代入しない（setter で数える）。
  4. dpr: 未定義・0・NaN・3 → 1・1・1・2。
- 変異: `fitCanvas` の拡大を「大きさを変えたときだけ」にすると 1 が赤になることを確かめる。
- `npm run test:handmark`・`npx tsc --noEmit`。
- 手動: 開発版（`GSE_DEBUG=1` で手跡を出す手順）で帯と背景が全幅に描かれることを画面で見る。リセットそのものは再現できないので、開発者ツールが使えれば `ctx.resetTransform()` を手で呼んで戻ることを見る（できなければその旨を記録する）。

## ロールバック計画

1 コミットを revert する。版（タグ）は作らないので配布物には影響しない。

## 設計判断の履歴
- 実行回数: 1 回目
- 採用: v1
- 根拠: 研究者の選択（2026-11-28）。原因が推測のままでも次の 1 枚で戻り、今回の形を node のテストで再現できる。v2 の比べは design-comparison.md。
