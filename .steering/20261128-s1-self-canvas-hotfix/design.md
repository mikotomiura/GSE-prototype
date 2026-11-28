# 設計

- `v0.1.42` から枝 `fix/s1-self-canvas-hotfix` を切り、e656ca62 を cherry-pick する。
- 食い違いは 3 か所。v0.1.42 の側を残し、直しの行だけを足す。
  - package.json: `test:handmark` に `handmark-canvas-fit.test.mjs` を足す。
  - handmark_guard.rs: `DRAW` は `handmarkStageDraw.ts`・`handmarkCanvasFit.ts` の 2 つ。
  - HandmarkStage.tsx: 閉じたときの `clearRect` の前と、`loop` の `drawFrame` の前に `fit()`。
- テストの順の確かめは、閉じたときの塊の起点を v0.1.43 の `clearIconLayer(icons);` から、v0.1.42 にある「窓が閉じた」のコメントに変える。
- 版は 0.1.45（タグ v0.1.45）。中身は v0.1.42 を元にしている。この枝は main の祖先にならないので、段 1 の配布の門（`check-s1-release-readiness.sh`）のタグの節は v0.1.44 を選び、赤になる。この点は承知のうえで、ほかの節が緑かを見る。
- CI の Release は既定で「最新版」になるので、作った後に v0.1.45 をプレリリースにし、v0.1.44 を最新版に戻す。
- ロールバック: 退避した v0.1.42 の `gse-next.app` を戻す。

## テスト
- `npm run test:handmark`（50 件）、`npx tsc --noEmit`、`cargo test --lib handmark_store::guard`（36 件）。
- 陽性対照: `handmarkCanvasFit.ts` に `window.localStorage` を足すと、guard が赤になる。
