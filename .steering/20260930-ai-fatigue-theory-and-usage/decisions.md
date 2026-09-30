# 重要な判断

## 判断 1: 開始時の研究者の決定（2026-09-30・AskUserQuestion・すべて推奨どおり）

- **背景**: 引き継ぎ（`.steering/_handoff/next-session-ai-fatigue-after-appraisal.md` §2）が「研究者に先に聞いて決める」とした次の段と、`/start-task` の範囲。
- **聞く前に確かめた事実**（issue の SSOT `../20260929-ai-fatigue-db-readable-and-gaps/scripts/issues_data.py` の `depends`）: S-01 は N-05 に依存する（N-05 は未着手）。S-06 も N-05 に依存する。S-09 は S-05（済）、S-11 は S-02（済）に依存する。判定者 2 は前タスクの時点で未定。
- **決定**:
  1. 次の段は **S-09 と S-11**（示した他の案: S-06 警報疲れ／N-05 → S-01 本検索／判定者 2 のファイル）。推奨の理由として示したこと: 依存先が済んでいて N-05 を待たずに始められる・手間が小さい・判定中の 225 件に候補をほとんど足さず判定の負担を増やさない。
  2. タスク名 `ai-fatigue-theory-and-usage`。
  3. S-09 の範囲は **issue の 4 本 ＋ DB と候補が依拠する枠組み**（示した他の案: issue の 4 本だけ）。推奨の理由: AI の燃え尽きの研究が依拠する JD-R・資源保存・テクノストレスが抜けると、査読でそこを突かれる。
  4. S-11 の対象は **DB 34 件と候補 225 件のうち題名・抄録で語を使う記録すべて ＋ サーヴェイで記録した用法の例**（示した他の案: DB 34 件だけ）。AI の見立て（E1〜E3）で絞らない（研究者の既定の方針）。
  5. /reimagine は使わない。
- **影響範囲**: requirement.md・design.md の範囲。

## 判断 2: 作業の場所と入力（2026-09-30）

- **作業の場所**: worktree `C:\wt\ai-fatigue-judge-file` を origin/main（`d759a7c8`・PR #273 の merge）から切った `docs/ai-fatigue-theory-and-usage` に切り替えた（worktree は clean だった）。main の作業ツリー（`C:\GSE-prototype`）には別トラックの未コミット作業があるので触らない。
- **入力**: 259 件の鍵・題名・DOI は、判定者用ファイルの archive の写し（SHA-256 `6984472e…`）から読む。★ Downloads の判定中のファイルは開かない（同じ SHA-256 の写しが repo にあるので不要）。
- **openpyxl**: 既定の Python に無いので、本セッションの scratchpad に venv を作った（openpyxl 3.1.5・前タスクと同じ版）。
- **中央書誌（`docs/references.md`）には登録しない**: 本タスクの成果物はサーヴェイの steering の文書で、GSE の文書（`docs/`）は書き換えない。A 群と同じく、出典は DOI で示す。GSE の文書が引くときに citation-ssot で登録する（`-gse.md` に候補として書く）。
