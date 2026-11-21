# 次のセッション: auto-context-task-level の実データを回す（作業の記録がそろった後）

## ここまで（2026-11-22・`.steering/20261121-auto-context-task-level/`・worktree `~/GSE-prototype-auto-context`・枝 `feature/auto-context-task-level`・push なし）

- 主の問いは「作業の記録で区切った作業ごとに、様式の連なりの出方が違うか」（判断 11）。基準は凍結済み（criteria v1.1・判断 15・17）。
- 合成の対照は seed 6 本 × 4 経路ですべて期待どおり（判断 18）。v2（自動のまとめ）は記述（長い陽性で 4/6）。
- レビュー（code-reviewer・security-checker）の指摘は対応済み（判断 16）。

## 次にやること

1. 研究者の作業の記録（`experiments/20261121-auto-context-task-level/work/diary.md`・11-22〜11-24）が書き終わったか確かめ、書き終えた時刻を判断 3 の下に追記する。それまで 11-22 以降の区間を見せない。
2. 本人の記録（`~/Documents/GSE-sessions/`）の写しを取って固定し、`data.md` に人ごとの本数・合計バイト・SHA-256 の要約値を書く（1 段目の data.md の形）。O1 の 3 人は 1 段目と同じ復号（P009 は外す）。
3. `python3 -I git_commits.py --root ~ --since 2026-10-09 --out work/commits.json` を回し直す。
4. `work/people.json`（id・files・本人だけ diary と commits）を作り、`GSE_REPLAY=... PEOPLE_JSON=work/people.json bash run.sh real`。
5. notes.md に集計だけを写す（作業名・枝の名前・区間は写さない）。識別子の見積もり（判断 4）を decisions に書く。
6. /finish-task（/cross-review は diff だけを Codex へ）。PR は 1 段目の PR を先に出し、main へは squash（判断 17）。push と PR は研究者に確かめる。

## 注意

- gse-replay の debug ビルドが `src-tauri/target`（1.7 GB）にある。実データの後に消す（自前ランナーの空きの下限 8 GiB）。
- 1 段目の枝の `results/capabilities.json` の漏れは、この枝で消してある。マージの後に前の枝を消す。ゲートの file_id の作り方は別のタスク。
