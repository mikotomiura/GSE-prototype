# タスクリスト

## 準備
- [x] 引き継ぎ（`.steering/_handoff/next-session-ai-fatigue-candidates-appraisal.md`）・前タスクの decisions（判断 1〜21）・評価プロトコル v1.0・9/29 の評価版の Claude のシートを読む
- [x] origin/main から worktree（`C:\wt\ai-fatigue-judge-file`）でブランチ `docs/ai-fatigue-candidates-appraisal` を切る
- [x] 研究者に先に聞く 4 点（タスク名・S-04 の範囲・判定の順番・評価の深さ）→ 判断 1
- [x] Downloads の判定者用ファイルが未記入か SHA-256 で確かめる（開始時と作り直す直前）

## 候補の突き合わせと追加
- [x] 206 件と既存の AI の判定案（ai-judgments.md・db-proposals.md）を cid で突き合わせる
- [x] 漏れの発見（S-08 §5・S-12 §4.1・S-12 の E1〜E3）→ 研究者に聞いて足す（判断 2）
- [x] 4 条件で 1 件ずつ仕分け（抄録を取り直した・repo の外）→ 19 件を足す・足さなかった記録と理由（判断 3）
- [x] 事実のファイル（S-12 §3.2・§3.3・§4.2・§4.3・S-08 §8）に DOI と抄録の事実を足す → `check_survey_files.py` 違反 0
- [x] `candidates.py`（225 件）・`judge_xlsx.bib_index()`（題名の無い記録・S-08・DOI の無い記録の鍵）・書誌と OpenAlex の足し分

## 評価版
- [x] design.md で形と語彙を固定してから書く
- [x] 225 件の 1 件ずつの案（`scripts/appraisal_data.py`）。種類ごとの案は写さず 1 件ずつ判定。薄い行（S-05 §6・S-13〜S-15 の表に載せなかった行・質的研究）は抄録を取り直して確かめた
- [x] 生成（`scripts/appraisal_xlsx.py`）と検査（`scripts/check_appraisal_xlsx.py`・data / rows / cells / golden / words）
- [x] 変異試験（`--selftest` PASS・陰性対照 6・変異 20）。空振り 2 件（読み直しで増える空の行・同じ値の変異）を直した
- [x] LibreOffice で概要の数式を再計算（エラーなし）
- [x] archive に置き、Downloads に写す（SHA-256 が同じ）

## 判定者用ファイル
- [x] 『はじめに』を判断 21 に合わせる（判定者 1: 追加候補も判定の前に評価版を読んだ／判定者 2: 評価版も開かない）
- [x] 作り直す（`check_judge_xlsx.py` 違反 0・`--selftest` PASS・集計の数式を再計算）

## レビュー
- [ ] code-reviewer ＋ security-checker（並列）
- [ ] HIGH 指摘への対応
- [ ] /cross-review 2 巡（Codex の予算を先に確かめる）

## 完了処理
- [x] decisions.md（判断 1〜5）
- [ ] コミット（明示的に add）・push・PR・CI 緑なら merge・main の CI 発火確認
- [ ] 完了報告（研究者に伝えること: 19 件の追加と内訳・S-08 §6 の追加の理由・既存の案と違う判定 37 件・評価版と判定者用ファイルの場所）
