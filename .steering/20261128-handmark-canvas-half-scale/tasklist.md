## tasklist

- [x] 回帰テスト `scripts/handmark-canvas-fit.test.mjs` を先に書き、赤を確かめる（`fitCanvas` が無い）
- [x] `src/components/handmarkCanvasFit.ts` を書いてテストを緑に
- [x] 帯（`HandmarkEdgeStrip.tsx`）: `resize()` を `fitCanvas` に置き換え、`draw()` の頭でも呼ぶ
- [x] 背景（`HandmarkStage.tsx`）: 同じ
- [x] 変異: 拡大を「大きさを変えたときだけ」にすると赤になることを確かめて戻す
- [x] `npm run test:handmark`（64 件）・`npx tsc --noEmit`・`cargo test --lib handmark_store::guard`（42 件・禁止語を植えると赤）
- [x] Chrome で崩れ方と直りを canvas の画素で確かめる（判断 5）
- [x] code-reviewer ＋ security-checker（判断 4）
- [ ] /finish-task（/cross-review を含む）・main へ
- [ ] 直した版のタグを作り、配布物で入れ替える（判断 6）
- [ ] 入れ替えた版で帯が全幅に描かれることを画面で見る
