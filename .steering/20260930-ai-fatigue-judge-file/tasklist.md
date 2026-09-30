# tasklist

## A. メモの issue 化と研究者の確認
- [x] 研究者のメモの 8 点を一次資料で確かめ、`memo-issues.md` に新しい issue 7 件（S-13・S-14・S-15・N-11〜N-14）を起こす
- [x] `survey-S-08.md` の節の番号を直す（§4 → §3.2.2）
- [x] 研究者に確かめる（N-05 の範囲・判定者 2・依頼・ブラウザ・片付け・有料を使わない・サーヴェイの順番）→ `decisions.md` 判断 1〜7
- [x] `researcher-requests.md` を更新（有料を外す・無料の 4 件）
- [x] 片付け（古い worktree 2 つ・退避ブランチ）
- [x] サーヴェイの手順を検索の前に `design.md` に固定

## B. 深掘りとサーヴェイ（判断 7 の順）
- [x] N-12: AF016 の補足資料（ブラウザでリンクを見つけて取得）で、全体の指標の 22 研究の内訳を研究単位で再現（memo-issues.md §2.6）
- [x] 検索スクリプト `evidence/search_round.py`（common.py を使う）と検査 `scripts/check_surveys_here.py`
- [x] S-15 過信と疲労: 検索 641 → 0 段目 192 → 抽出 187 → 表 11・質的 8（種文献 2/2）
- [x] S-14 燃え尽き: 検索 延べ 157（補いを含む・判断 8。重なりを除くと 131）→ 抽出 106 → 表 30・質的 4・介入 4
- [x] S-13 組織の水準: 検索 270 → 抽出 110 → 表 7・質的 9（組織を単位にした AI の研究 0）
- [x] 無料の本文 4 件（B5・B9・B10・B12）を読み、事実のファイルに要点を足す（2026-09-30 の次のセッション・判断 14・15）
- [x] B9 の採択研究 28 件のふるい（`evidence/B9/`）→ 一次研究 2 件を S-02 §7 と追加候補に足した（159 件）・判定者用ファイルを作り直した（未記入を確かめてから・検査 違反 0・selftest 43 PASS）
- [x] `check_survey_files.py`（本タスクと前タスクのディレクトリ）が違反 0

## C. 判定者用ファイル
- [x] `scripts/candidates.py`（追加候補のデータ・132 件 → レビュー後 157 件・判断 13 → 159 件・判断 15 → 193 件・判断 17）
- [x] `scripts/fetch_oa.py` → `evidence/oa_2026-09-30.json`（164 件すべて取得）
- [x] `scripts/judge_xlsx.py`（出力の保護・DOI の quote・行の高さ）
- [x] `scripts/check_judge_xlsx.py`（レビュー後: 語・構造・生成物との一致の 3 検査。selftest 43 項目 = 陰性対照 1・変異 30〈それぞれ指定の検査だけで赤〉・陽性対照 2・zip の変異 4・出力の保護 6）
- [x] 判定者 1 用のファイルを作り、Downloads に写した（`archive/judge/` と同一・違反 0・集計の数式を LibreOffice で再計算して確認）

## D. 完了
- [x] code-reviewer ＋ security-checker（並列）・指摘対応（判断 13）
- [ ] /finish-task で /cross-review 2 巡 → ★ 次のセッション（当日の実消費が合算で約 304,946 / 300,000・研究者の決定 2026-09-30）→ ★ 同日のうちに上限を一時的に引き上げて回す（判断 14）
- [x] 引き継ぎ `.steering/_handoff/next-session-ai-fatigue-crossreview.md` と索引の更新
- [x] push（PR・merge は /cross-review の後 → 次のセッション）
