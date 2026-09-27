# タスクリスト

- [x] grill: 不具合 1 は案 A、不具合 2 は docs だけ、検証は stub ハーネスと変異テスト（decisions.md）
- [x] 回帰テスト P1 / P2 を追加 → **旧実装で P1 だけが赤**（合格 90 / 不合格 1。events は blockers.md §1 の実測と同じ形）
- [x] `loop-run.sh` を修正 → **合格 92 / 不合格 0**（P1 / P2 / M-prog 緑）
- [x] M-prog 変異テスト（旧実装を戻すと赤になる）
- [x] `check-shell-portability.sh` 12/12 ・ `check-tests-are-wired.sh` 23/23（loop-run-guard-test は ci.yml:641/753 で走る）・ `check_doc_lexicon.py` 違反なし
- [x] `docs/loop-engineering.md` に是正節を追加（モデル割当表・実行モード節と矛盾しないことを目で確認済み。モデル割当の変更はなし）
- [x] 1 巡目レビュー: security-checker（MEDIUM 1 / LOW 3）・/cross-review（Codex: MEDIUM 2 はテストの厳密さ／Claude: MEDIUM 1 は既存挙動）。CRITICAL/HIGH なし
  - ⚠️ cross-reviewer に Task ツールが無く、code-reviewer を並列起動できなかった（自身でレビューした）→ 最終 diff に code-reviewer を別途起動
- [x] 対応: 境界侵害で run を中止（P3 / M-bnd）・token_ceiling をバッチ前に確認（P4）・`grep -F`・001 の attempt 列を完全一致で検査・M-prog で旧不具合に固有の結果を確認・docs に merge ゲートの前提と再実行の注意を追記 → **合格 95 / 不合格 0**
- [x] 最終 diff の code-reviewer（MEDIUM 2 / LOW 5・HIGH なし）→ 判断 6 のとおり対応 → **合格 98 / 不合格 0**
  - その場の変異で確認: ラッパーの再確認を外す → P3c 赤／`-F` を外す → P5 赤／予算の事前確認を外す → P4 赤（すべて元に戻して緑）
- [ ] ⚠️ Codex の 2 巡目は回せない（当日の残り 23,045 < 1 回分の上限 30,000・`.codex/budget.json`）→ 完了報告に明記
- [ ] commit → PR → CI → merge
