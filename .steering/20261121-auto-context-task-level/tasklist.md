# tasklist（auto-context-task-level）

## 準備
- [x] 枝 `feature/auto-context-task-level` を `feature/auto-context-segmentation` から切る（判断 1）
- [x] 作業の記録の雛形を `experiments/20261121-auto-context-task-level/work/diary.md` に置く（コミットしない・判断 3）
- [ ] 研究者が 11-22〜11-24 の作業の記録を書く（書き終えるまで 11-22 以降の区間を見せない）

## 設計
- [x] design.md（v1）を研究者と決める（判断 6）
- [x] /reimagine を 1 回回して比べる・ハイブリッドを採用（判断 7）
- [x] git のコミットの取り方を決める（worktree の reflog・内容は読まない・判断 6）

## 実装（experiments/）
- [x] 実験のディレクトリを整える（run.sh の Step 0・SEED・config・env）
- [x] `act_hmm.py`: カテゴリの出力の HMM（前向き後ろ向き・Baum–Welch・Viterbi・欠測・リセット・BIC）
- [x] `test_act_hmm.py`: 小さな列で総当たりの尤度と比べる・欠測・リセット・K=1 と同じになる場合
- [x] `act_window.py`（v1・記述用）: 30 分の窓の割合 → 混合ガウス → 平滑化
- [x] `gen_synth_task.py`: 作業 = 様式の混ぜ方の 24 時間の記録（陽性・陰性）と、合成の作業の記録・コミットの列（一致・不一致・区切りが少ない）
- [x] `git_commits.py`: worktree の reflog から時刻と worktree の名前だけを `work/` に書き出す
- [x] `evaluate.py`: synth / real（主の問い・照合・循環の検査・識別子の見積もり）（照合・循環の検査・判定・識別子の見積もり）
- [x] 合成の対照（主の問いの 4 経路 × seed 6 本・v2 の 3 本は記述）を終了コードで確かめる（判断 14）
- [x] `criteria.json` を研究者と確定し、実データより前にコミットする（判断 15）
- [ ] 本人の入力の写しを取って固定し、`data.md` に SHA-256 の要約値を書く

## 実データ
- [ ] 本人と O1 の 3 人の判定を notes.md に書く
- [ ] 識別子の要否の見積もりを decisions に残す（判断 4）

## レビュー・完了
- [ ] code-reviewer と security-checker を並列で回す
- [ ] /finish-task で /cross-review（diff だけを Codex へ）
- [ ] コミット。push と PR は研究者に確かめてから
