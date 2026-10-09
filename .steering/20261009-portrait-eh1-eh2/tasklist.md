# タスクリスト

## 準備
- [x] grill（AskUserQuestion 1 回・4 問・すべて推奨どおり）→ requirement.md・decisions.md 判断 2
- [x] worktree `C:/wt/portrait-eh1-eh2`・ブランチ `feature/portrait-eh1-eh2`（`docs/portrait-invitation-constraints` から）
- [x] IME 論文との関係を一次で確かめる（判断 1）
- [x] design.md に合否の基準を書き、**結果の前にコミットして固定する**

## EH1
- [ ] `gse-replay` をビルドする（target は worktree の外）
- [ ] `gen_sessions.py`（合成の記録・ラベル・capabilities つき meta）
- [ ] `portrait.py`（scheduler・生成器 3 × 2・陽性対照 2）
- [ ] `checks.py`（E1-3・E1-6・順序の感度・E1-4・E1-7・E1-2 の記述）
- [ ] `render_e18.py`（E1-8 の候補）
- [ ] `selftest.py`（E1-1・E1-5・変異・scheduler の境界）
- [ ] `run.sh --smoke` で全段を通す
- [ ] 本番を回し、`results/` と `notes.md` に基準どおりに書く

## EH2
- [ ] `windows/eh2_wallpaper.ps1`・`macos/eh2_wallpaper.swift`・README
- [ ] Windows 版をこの機械で `-Quick` で回し、元の壁紙に戻ったことを確かめる
- [ ] 引き継ぎ（Windows・macOS）を `.steering/_handoff/` に書く

## 閉じる
- [ ] code-reviewer ∥ security-checker
- [ ] /cross-review 2 巡と対応を decisions.md に
- [ ] 親タスクの decisions.md・`.idea` §11 に結果を還元する（研究者の決定 U-4・E1-8 の材料として）
- [ ] コミット・push（PR なし）
