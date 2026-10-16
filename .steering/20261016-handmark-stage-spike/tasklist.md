# タスクリスト

## 準備
- [x] 引き継ぎ（`.steering/_handoff/next-session-handmark-stage-and-louder-surface.md`）を読む
- [x] worktree `/Users/johnd/GSE-prototype-handmark-stage`・枝 `spike/handmark-stage` を `spike/handmark-a-surface` から切る
- [x] requirement.md

## 段 1: 右下の小面を少し主張させる
- [x] 候補台（5 候補 × 5 下地・実寸）を作り、研究者に選んでもらう → 乙（判断 1）
- [x] `HandmarkSurface.tsx` と `handmark_spike.rs` に乙を入れ、窓の大きさを輪の最大に合わせる（52 px）
- [x] tsc・cargo check が通る
- [ ] 実際の窓が明るい壁紙と暗い壁紙の上で見えるか（研究者の目・段 3 の試視にまとめる・2026-10-16 研究者）

## 段 2: 背景の層の実現性
- [x] 背景の層の技術の調べ（survey-results.md §2・この枝にあった）
- [x] design.md（研究者が承認）
- [x] デスクトップの高さの窓に描く（層の上下・全画面は確認。Spaces と複数ディスプレイは未確認・results.md §3）
- [x] 覆われたときの 1 秒ごとの更新と移り変わりの継続（results.md §2）
- [x] Chrome の画面共有（保護あり / なし・陰性対照つき・results.md §4）
- [ ] Zoom の自動・標準のスクリーンショット
- [x] 負荷（電池・低電力モード・セッション中・results.md §5）

## 段 3: 研究者の試視
- [ ] 手順書（manual-check.md）
- [ ] 研究者が背景と右下の小面を一緒に見る

## 完了処理
- [ ] results.md
- [ ] code-reviewer・security-checker・/cross-review
- [ ] git commit・push（PR は出さない）
