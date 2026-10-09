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
- [x] **Windows の機器で** `run.sh --world v1`・`--world v2` を回し、`results/` と `notes.md` に書く（G-GEAR・計器 `7c29fd8a`・Surface Pro 8 はメモリ不足で止めた・design §8）

## EH2
- [x] `windows/eh2_wallpaper.ps1`・`macos/eh2_wallpaper.swift`・README
- [x] Windows 版をこの機械で `-DryRun` だけ回した（背景がスポットライトで、替えて戻す経路は回せない）
- [x] 引き継ぎ（Windows は EH1 ＋ EH2・macOS は EH2）を `.steering/_handoff/` に書いた
- [x] **Windows の機器で** EH2 を回す（Surface Pro 8・`-Quick` → 本番・すべて戻った）
- [x] **macOS の機器で** EH2 を回す（MacBook Air M4・読み戻しを待つよう受け手が直した・notes-macos 判断 M1）
- [ ] EH2 の手の確認（仮想デスクトップ / Spaces・画面共有）—— 両 OS とも未実施（研究者がその場で回す）

## 閉じる
- [x] code-reviewer ∥ security-checker（判断 6・指摘はすべて対応か理由つきで据え置き）
- [x] /cross-review 2 巡と対応を decisions.md に（判断 7: 26 件・判断 8: 10 件。すべて妥当で対応済み。Codex は 3 本で 108,882 トークン）
- [x] 両機器の結果をまとめた（notes の検算・design §8・EH2 README・判断 9・親の判断 12・`.idea` §11.4・探索 `explore_material_info.py`）
- [x] 研究者に U-4・E1-8・次の段・古いブランチを聞いた（判断 9・すべて推奨どおり）。`feature/portrait-eh1-eh2` を消した
- [ ] まとめの `/cross-review` 2 巡（1 巡目 = 書き写しと基準の読み方・受け手の Swift の修正 ／ 2 巡目 = 足した解釈の境界）

## 次の段（判断 9 の 3・別タスクで）
- [ ] EH1 の第 2 回: 新しい固定（既定の scheduler で働く陽性対照・`recent` を固定の組に・揺らしに強い文法・攻撃者の窓）＋ `run.sh` の `.exe` と `--jobs`
- [ ] コミット・push（PR なし・計測の run の後）
