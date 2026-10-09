# タスクリスト

## 準備
- [x] grill（AskUserQuestion 1 回・4 問・すべて推奨どおり）→ requirement.md・decisions.md 判断 2
- [x] worktree `C:/wt/portrait-eh1-eh2`・ブランチ `docs/portrait-eh1-eh2`（`docs/portrait-invitation-constraints` から。最初は `feature/` で切って CI が走ったので改名した・判断 4）
- [x] IME 論文との関係を一次で確かめる（判断 1）
- [x] design.md に合否の基準を書き、**結果の前にコミットして固定する**（`abfb2c45`・11:50）

## EH1（計器はここで作り、本番は Windows の機器で回す・判断 5）
- [x] `gse-replay` をビルドする（target は worktree の外）
- [x] `gen_sessions.py`（合成の記録・ラベル・capabilities つき meta・dwell は押す打鍵と一緒に引く）
- [x] `portrait.py`（scheduler・生成器 3 × 2・陽性対照 2・探索の scheduler `recent`）
- [x] `checks.py`（E1-3・E1-6・順序の感度・E1-4・E1-7・E1-2 の記述）
- [x] `render_e18.py`（E1-8 の候補・見本の画像）
- [x] `selftest.py`（E1-1・E1-5・scheduler の境界・統計・変異 3 つ）
- [x] `run.sh --smoke` で全段を通す（v1・v2）。3 つ目の変異は全数の記録の先頭 60 本で確かめた
- [x] 逸脱を design §8 に記録した（world v2・探索・raw の向き・dwell・止めた本番は開かずに消した）
- [ ] **Windows の機器で** `run.sh --world v1`・`--world v2` を回し、`results/` と `notes.md` に書く（引き継ぎ `next-session-portrait-eh1-eh2-windows.md`）

## EH2
- [x] `windows/eh2_wallpaper.ps1`・`macos/eh2_wallpaper.swift`・README
- [x] Windows 版をこの機械で `-DryRun` だけ回した（背景がスポットライトで、替えて戻す経路は回せない）
- [x] 引き継ぎ（Windows は EH1 ＋ EH2・macOS は EH2）を `.steering/_handoff/` に書いた
- [ ] **Windows の機器で** EH2 を回す（`-Quick` で戻ることを確かめてから本番）
- [ ] **macOS の機器で** EH2 を回す（最初に `swiftc -typecheck`）

## 閉じる
- [x] code-reviewer ∥ security-checker（判断 6・指摘はすべて対応か理由つきで据え置き）
- [ ] /cross-review 2 巡と対応を decisions.md に
- [ ] 両機器の結果が来たら: design §8・README の実行の表・notes をまとめ、親タスクの decisions.md と `.idea` §11 に還元する（研究者の決定 U-4・E1-8 の材料として）
- [ ] コミット・push（PR なし・計測の run の後）
