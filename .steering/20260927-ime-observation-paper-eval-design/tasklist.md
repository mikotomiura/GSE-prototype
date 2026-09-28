# タスクリスト

## 本タスク（評価設計と外枠）
- [x] grill で投稿先・正解の源・入力・範囲・公開・貢献・時期を確定（decisions.md 判断 1–8）
- [x] requirement.md / design.md 初版
- [x] paper-suggest.md（論文の案・タイトル案・投稿計画）と次セッションへの handoff を作成（2026-09-27）
- [x] 一次で接地が要る箇所を確認（2026-09-28）: MS（IMM 互換は文書に列挙なし → 2 経路を試す）/ Apple（呼び出し順は文書に無い・`unmarkText` は確定側）/ CPU 0.98% は無効 / BRM の規程
- [x] 研究者が design.md 初版を承認（訂正 4 点入り・判断 10）＋ 較正パイロット（判断 11）・E3 の範囲（判断 12）・CHI の開示（判断 13）
- [x] `/reimagine` 1 回目で v2 案と比較 → ハイブリッドを採用（判断 14・`design-comparison.md`）
- [x] タイトル T1・ライセンス Apache-2.0 / CC BY 4.0（判断 15）
- [x] BRM の規程（非アーカイブ発表・code availability）を確認（判断 13・design.md §4 / §5）
- [x] [P321] 2 本目の再検討（サーヴェイ 4 本 ＋ 一次の裏取り → 判断 16: 並行で進める）→ 別トラックの handoff `next-session-p321-reanalysis-paper.md`
- [x] 後続 issue を `issues/` に分解（2026-09-28・Opus・`issue-slicing`）: **27 本**（うち任意 3 本は blocked）＋ `_acceptance-lib.sh` ＋ 各 `NNN-acceptance.sh` ＋ `_issue-plan.md`（DAG・交差表・機械の割り当て・マイルストーン M0〜M13）＋ `_loop-config.json`（モード C・G-GEAR のパス）。分解の前に研究者が判断 17–21 を確定、slicer の裁定は判断 22
- [ ] ⚠️ **ループの実行は別セッション**（`/clear` → `.steering/_handoff/next-session-ime-paper-loop.md`）。W1（001）→ merge → W2 … の順（`_issue-plan.md` §4）
  - [x] base `feature/ime-eval-kit` を origin/main（afe6b0d7）から作って push（2026-09-28）
  - [x] **W1（001）**: モード C・attempt 1 で `issue_done`（6.17M トークン・$2.68）。merge ゲート（clean な checkout で acceptance 失敗 0 件・verify 3 本・変異・code-reviewer ∥ security-checker）→ 契約の指摘を研究者に問い判断 23〜26 → メインが直して `32b3fdc2` で base へ merge。`papers/.gitignore` を base に追加。詰まりは `blockers.md` B1〜B4
  - [x] **判断 25**: `plan/1` / `oracle/1` / `corpus/1` の型をメインが `FORMATS.md` に足し、研究者が差分を承認して base へ（2026-09-28）
  - [ ] W2（G-GEAR: 002 003 008 010 011 015 016 ／ Mac: 004 007）。⚠️ token_ceiling は run ごと（B4）→ 2〜3 回の run に分ける
- [ ] M0〜M13（`_issue-plan.md` §5）。★ 凍結物は **`papers/ime-observation/experiment/preregistration.md`**（判断 21 で `experiments/<date>-…/` から変更）
- [ ] 論文の外枠（節構成・主張 ↔ 根拠の対応表）を `papers/ime-observation/manuscript/outline.md` に置く（★ 判断 21）
- [ ] /finish-task
