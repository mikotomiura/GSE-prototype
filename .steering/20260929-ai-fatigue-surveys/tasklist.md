# タスクリスト

## 準備
- [x] PR #263 が MERGED であることを `gh pr view 263 --json state` で確かめる（2026-09-29T05:14:33Z）
- [x] origin/main（`681f51a0`）から worktree `C:\wt\ai-fatigue-surveys`・ブランチ `docs/ai-fatigue-surveys` を切る
- [x] 引き継ぎ・issues.md・ideas.md・decisions.md（判断 11〜13）・評価プロトコル v1.0 を読む
- [x] Skill: verify-before-claiming・subagent-delegation
- [x] requirement.md / design.md §0（共通）/ §1（S-12 の手順・検索前に固定）
- [x] `scripts/check_survey_files.py`（禁止語・引用の長さ・注意書き・evidence の鍵）と `--selftest`（初回は S-12 だけで緑・変異はすべて赤。最終の数は「検査」の節）

## サーヴェイ（A 群）
- [x] S-12 日本語の文献（検索 → ふるい → 事実 / 判定案 / GSE の 3 ファイル）→ コミット `5007316a`
- [x] S-02 検索漏れ候補 11 件の抄録（＋ Sci Rep と Acta Psychologica の標本の重なり・N-06 データセット 2 件）→ design §2 を先に固定 → コミット `630bca48`（判断 12 の書き換えの前は `801a81d5`）
- [x] S-08 AI 疲労の尺度の一覧（＋ N-07 AF001 の補足資料）→ design §3 を先に固定 → コミット `2fbb52dc`（同 `1aea8597`）
- [x] S-04 疲れが減る側の証拠 → design §4 を先に固定 → 0 段目の機械ふるい（判断 9）・補い（判断 10）→ 抽出 4 本（うち抄録の直し 1 本・判断 11）→ メインの確認 → コミット
- [x] S-05 自動化を見張る疲労 → design §5 を先に固定 → 検索（22:08）→ 抽出 → メインの確認 → コミット
- [x] `db-proposals.md`（DB への追加・修正の提案・A〜G 節）
- [x] `researcher-requests.md`（[研究者] 有料データベース 3・本文の入手 12）

## 検査
- [x] `python scripts/check_survey_files.py` が緑（事実 7 本・判定案 6 本・違反 0）・`--selftest` で変異 147 種がすべて赤（レビュー後に検査を強めた・判断 13・16・17）
- [x] 本文・PDF・抄録の全文・尺度の項目文がコミットに無いこと（`git diff --stat` と evidence の鍵の検査）—— 2026-09-30: `origin/main...HEAD` の名前に pdf・xlsx・docx・html・abstracts が無い。evidence の鍵・値の検査は緑
- [x] DB の xlsx が変わっていないこと（`git diff --stat` に xlsx が無い）—— 2026-09-30 に確認

## 完了処理
- [x] 前回の steering の tasklist・issues の状態への反映 —— issues.md は再生成せず `issue-status.md` に状態と反映の候補を書いた（再生成は評価版の xlsx の作り直しを伴うため）。前回の tasklist の A 群の行を閉じた
- [x] 引き継ぎ `.steering/_handoff/next-session-ai-fatigue-judge-file.md` と索引の更新
- [ ] /finish-task（code-reviewer＋security-checker 並列 → /cross-review 2 巡）→ git-workflow ルール 6
