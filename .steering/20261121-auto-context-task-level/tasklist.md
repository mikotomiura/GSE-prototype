# tasklist（auto-context-task-level）

## 準備
- [x] 枝 `feature/auto-context-task-level` を `feature/auto-context-segmentation` から切る（判断 1）
- [x] 作業の記録の雛形を `experiments/20261121-auto-context-task-level/work/diary.md` に置く（コミットしない・判断 3）
- [ ] 研究者が 11-22〜11-24 の作業の記録を書く（書き終えるまで 11-22 以降の区間を見せない）

## 設計
- [ ] design.md（窓の長さ・様式の割合のまとめ方・境界・判定の経路）を研究者と決める
- [ ] /reimagine を 1 回回して比べる（判断 5）
- [ ] git のコミットの repo と時刻の取り方を決める（内容は読まない）

## 実装（experiments/）
- [ ] 合成の対照（陽性・陰性・壊した入力・宣言と作業の記録の経路）を終了コードで確かめる
- [ ] `criteria.json` を研究者と確定し、実データより前にコミットする
- [ ] 本人の入力の写しを取って固定し、`data.md` に SHA-256 の要約値を書く

## 実データ
- [ ] 本人と O1 の 3 人の判定を notes.md に書く
- [ ] 識別子の要否の見積もりを decisions に残す（判断 4）

## レビュー・完了
- [ ] code-reviewer と security-checker を並列で回す
- [ ] /finish-task で /cross-review（diff だけを Codex へ）
- [ ] コミット。push と PR は研究者に確かめてから
