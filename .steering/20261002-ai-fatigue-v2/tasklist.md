# タスクリスト

## 準備
- [x] grill（AskUserQuestion 3 回・11 問）→ requirement.md・decisions.md 判断 1
- [x] worktree `C:\wt\ai-fatigue-v2`（`docs/ai-fatigue-v2`・origin/main `f04b4995` から）
- [x] design.md の承認（2026-10-02）
- [x] 抄録の取得（`fetch_abstracts.py`・無料の API・メールアドレスなし）→ 取れなかった件は Chrome でなく `fetch_landing.py`（判断 2 の逸脱）→ 250 / 259

## 抄録段
- [x] 道具: `common.py`・`build_ta_sheet.py`・`check_ta_sheet.py`（selftest 37 PASS・メタ変異 15 規則 PASS）・`read_ta_sheet.py`（試作で通した）
- [x] 記入表 1 を作り、検査違反 0 → 判定者 1 に渡す（`515c18e7…`・2026-10-02）
- [x] 記入表 2 の道具: `build_ta2_sheet.py`・`check_ta2_sheet.py`（selftest 23 PASS・メタ変異 10 規則 PASS）・`read_ta2_sheet.py`（試作で通した）
- [x] ~~記入表 1 を読む~~ → 判断 3: 問いで聞き Claude が写す形に変えた（`dump_ta_rows.py`・`ta_from_session.py`）
- [x] 抄録段の問い: 71 件で止めた（判断 5）→ `data/ta-answers.json`（含める 49・保留 15・除外 7）
- [x] ~~『探索の記録』43 件~~ → 判断 4: このタスクでは足さない
- [x] ~~記入表 2~~ → 判断 5: しない（一致の表に替える）
- [x] 判定者 1 の「除外 E4 背景」の読み方を聞く → 判断 6（範囲の外・背景として残す・注記して残す）
- [x] 残り 142 件に評価版の予備判定を写す（AI と明記）→ ログ（`ta1`=判定者 1・`ai_ta`=AI）: `build_log.py`・`check_log.py`（12 規則・selftest・メタ変異 PASS・`--session` 一致）→ 214 行

## 全文段
- [x] ~~全文段~~ → 判断 5: このタスクではしない（未実施と書く）

## まとめ
- [x] ~~34 件のメモの論点の見直し~~ → 判断 5: 全文段が無いので未実施と書く
- [x] 残り 142 件の群ごとの一覧（対象者 × AI の種類 × デザイン）・71 件の判定者 1 と AI の一致の表（表の『群ごとの一覧』『一致の表』・提案 §7）
- [x] 追加候補の表を作り直す（`build_candidates.py`・`0d830c1f…`）→ `check_candidates.py --final` 違反 0・`--selftest`・メタ変異 20 規則 PASS（判断 8）
- [x] 提案のドキュメント v2（`anthropic-skills:docx` Skill を読む → 原稿 → .docx `99678b75…` → `check_proposal.py` 違反 0・selftest・目で見た〈LibreOffice で PDF → 画像・35 頁〉）
- [x] Downloads の退避ファイルの一覧 → 判定者 1 の確認 → 削除（判断 7・38 個）

## 完了
- [ ] 元の資料 4 つの SHA・前の 2 タスクのディレクトリに差分なし・ステージに抄録と本文なし
- [ ] code-reviewer ＋ security-checker（並列）→ /cross-review 2 巡
- [ ] 出荷（git-workflow ルール 6）
