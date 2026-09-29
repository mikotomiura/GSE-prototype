# tasklist

## A. メモの issue 化と研究者の確認
- [x] 研究者のメモの 8 点を一次資料で確かめ、`memo-issues.md` に新しい issue 7 件（S-13・S-14・S-15・N-11〜N-14）を起こす
- [x] `survey-S-08.md` の節の番号を直す（§4 → §3.2.2）
- [x] 研究者に確かめる（N-05 の範囲・判定者 2・依頼・ブラウザ・片付け・有料を使わない・サーヴェイの順番）→ `decisions.md` 判断 1〜7
- [x] `researcher-requests.md` を更新（有料を外す・無料の 4 件）
- [x] 片付け（古い worktree 2 つ・退避ブランチ）
- [x] サーヴェイの手順を検索の前に `design.md` に固定

## B. 深掘りとサーヴェイ（判断 7 の順）
- [ ] N-12: AF016 の補足資料 S1・S3（ブラウザ）で、全体の指標の 22 研究を研究単位で照合
- [ ] 検索スクリプト `evidence/search_round.py`（common.py を使う）と検査 `scripts/check_surveys_here.py`
- [ ] S-15 過信と疲労: 検索 → 0 段目（種文献で確認）→ 抽出（Sonnet）→ メインの確認 → 3 ファイル
- [ ] S-14 燃え尽き: 同上
- [ ] S-13 組織の水準: 同上
- [ ] 無料の本文 4 件（B5・B9・B10・B12）を読み、事実のファイルに要点を足す
- [ ] `check_survey_files.py`（本タスクと前タスクのディレクトリ）が違反 0

## C. 判定者用ファイル
- [ ] `scripts/candidates.py`（追加候補のデータ）
- [ ] `scripts/fetch_oa.py` → `evidence/oa_2026-09-30.json`
- [ ] `scripts/judge_xlsx.py`（出力の保護・DOI の quote・行の高さ）
- [ ] `scripts/check_judge_xlsx.py`（格納先ごとの検査・要点の出どころ・`--selftest` の変異と陰性対照）
- [ ] 判定者 1 用のファイルを作り、Downloads に写す（上書きしない）

## D. 完了
- [ ] code-reviewer ＋ security-checker（並列）・指摘対応
- [ ] /finish-task で /cross-review 2 巡（Codex の当日の実消費を先に確かめる）
- [ ] 引き継ぎの更新・git-workflow ルール 6（push → PR → CI 緑なら merge）
