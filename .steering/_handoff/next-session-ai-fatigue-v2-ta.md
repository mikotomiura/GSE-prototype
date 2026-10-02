# 次セッション — AI 疲労 文献 DB v2: 記入表 1 を読む → 記入表 2 → 全文段

> ⏸ **2026-10-03 に `next-session-ai-fatigue-v2-finish.md` へ置き換えた。** 記入表 1 は未記入のまま使わず、問いで聞いた（判断 3）。判定者 1 は 71 件で止め、残り 142 件は評価版の予備判定を AI と明記して使い、全文段はしない（判断 4・5）。以下は当時の記述。

> 作成: 2026-10-02（`ai-fatigue-v2` の 1 つ目のセッションの終わり）。⚠️ **このメモを一次資料にしない。** 一次は `.steering/20261002-ai-fatigue-v2/`（requirement・design〈聞く前に固定〉・decisions 判断 1〜2・tasklist）。
> ★ ユーザーは **判定者 1**。DB を作ったのは「相手の研究者」。研究者が決めることはユーザーに聞かない。★ **3 つのファイルはまだ研究者に渡していない**（ユーザーは全部仕上げてから渡す・記憶 `project_ai_fatigue_handover_when_complete`）→ 研究者の返事を聞かない。

## §0 打ち込む用（★ `/clear` してから。モデルは Opus）

```
.steering/_handoff/next-session-ai-fatigue-v2-ta.md を読んで、AI 疲労 DB v2 の続き（記入表 1 を読む → 記入表 2 → 全文段）を進めてください。worktree は C:\wt\ai-fatigue-v2（ブランチ docs/ai-fatigue-v2）。C:\GSE-prototype は別のトラックの作業ツリーなので触らない。

⚠️ 記入表 1（Downloads\AI_fatigue_TA_sheet1_judge1.xlsx）をユーザーが保存し終えたかを最初に聞く。読み込みは check_ta_sheet.py --filled --final が違反 0 のときだけ。
⚠️ 評価版（AI の予備判定）の値や件数を、その記録の判定者 1 の最終の段の 1 回目より前に見せない（集計の数も）。
⚠️ git add -A / git add <dir> は使わない。抄録・本文・記入表はコミットしない。外部に出る操作はしない。
★ 応答は日本語。サブエージェントの前に subagent-delegation Skill、Chrome の前に browser-verification Skill。
```

## §1 このセッションで終わったこと（2026-10-02）

| 何 | 状態 | どこ |
|---|---|---|
| grill（11 問・推奨どおり）・設計の承認 | ✅ | decisions 判断 1・design.md（記入表 1 を渡す前に固定） |
| 抄録の取得（無料の API・メールなし） | ✅ 259 件中 250 件。設計 §4 からの逸脱（出版社のページの抄録の meta を道具で読む・DOI なしは題名の完全一致だけ）を記録 | decisions 判断 2・`data/abstract-status.json`（本文は git の外） |
| 記入表 1 | ✅ **判定者 1 に渡した**（`515c18e7…`・213 件＋探索 46 件）。検査違反 0・selftest 37・メタ変異 15 規則 PASS | `Downloads\AI_fatigue_TA_sheet1_judge1.xlsx`・原本は `Downloads\ai-fatigue-fulltext\_abstracts\ta_sheet1_original.xlsx` |
| 記入表 1 を読む道具 | ✅ 試作で通した（258 行・X02〜を R の順に振る・二重に写さない） | `scripts/read_ta_sheet.py` |
| 記入表 2 の道具 | ✅ 作った・selftest 23・メタ変異 10 規則 PASS・読み込みの試作も通した | `scripts/build_ta2_sheet.py`・`check_ta2_sheet.py`・`read_ta2_sheet.py` |
| コミット | ✅ ブランチ `docs/ai-fatigue-v2`（未 push） | — |

## §2 次にやること（この順）

1. **記入表 1 を読む**: `check_ta_sheet.py --filled`（途中なら終了コード 2 と未記入の件数）→ `--filled --final` 違反 0 → `read_ta_sheet.py`（ログ `screening-log.jsonl` と `data/extra-records.json`）→ コミット。抄録段の結果の数（含める・保留・除外）をユーザーに伝える（★ AI の数は言わない）。
2. **記入表 2**: `build_ta2_sheet.py` → `check_ta2_sheet.py`（記入前）→ 判定者 1 に渡す → 保存の後 `--filled --final` → `read_ta2_sheet.py` → コミット。
3. **全文段**（design §8）: 対象 = 抄録段で含める・保留（＋ 記入表 2 で含める・保留に変えた件〈1 問だけ・`after_ai`〉＋ 探索で足して含める・保留の件〈1 問だけ・AI なし〉）。群は記入表 1 の行の順のまとまり。
   - 道具がまだ無い: `log_add.py`（前のタスクのものを写す・段 `1`・`1e`・`2`・`2e`・`q`・`x`）。全文段の問いの禁止語の検査は前の 2 タスクと同じ（`stage1_banned`）。
   - 本文の確保と抽出の下書き: サブエージェント（sonnet 明示・入れ子禁止・締切 25 分・束 8〜10 件・契約は design §8）。1 回目の問いに載せる事実はメインが本文で確かめる。Q1・Q2 の印（design §8 の定義）を事実の欄に載せる。
4. その後: メモの論点の見直し（design §10）→ 追加候補の表（`build_candidates.py`・`check_candidates.py` を前のタスクから写して広げる・design §9）→ 提案のドキュメント v2（design §11）→ 退避ファイルの整理（design §13）→ 完了のレビューと出荷。
- コンテキストが半分ほどになったら、群の切れ目で引き継ぎを書いて区切る。

## §3 落とし穴

- **git-bash から `uv run python -c` にパスを渡すときは Windows の形（`C:/Users/...`）**。`/c/Users/...` は Python で開けない（このセッションで 1 回踏んだ）。
- **`… | tail` は終了コードを隠す**。selftest・メタ変異の成否は出力の `selftest PASS`・`meta PASS` で見る。selftest は 1 回 3〜5 分、メタ変異は 5 並列で 10 分ほど（裏で回す）。
- **メタ変異で「通る」規則が出たら、その規則だけが拾う変異を足す**（このセッションで `r_sheets`・`r_search_rows` が別の規則の例外で隠れていた）。
- **抄録の取り直しは `fetch_landing.py`**。og:description・description は切れた文やサイトの説明文を返す（読むのは抄録の meta だけ）。和文の抄録を題名と取り違えない規則に直してある（判断 2）。
- 記入表は **作った時点の原本**（git の外）と比べて「記入欄の外が変わっていない」を確かめる。原本を消さない。記入が始まった記入表は作り直さない（道具は SHA の記録と違えば止まる）。
- 前のタスクの落とし穴（`next-session-ai-fatigue-v2.md` §3）はそのまま有効: 台帳の CRLF・メタ変異・同じ型の穴・理由の問いを独立に残す・数字は記録と照合・openpyxl の入力規則の範囲・heredoc のバックスラッシュ・Downloads の退避ファイル。
- ⚠️ メインはこのセッションで評価版の題名・抄録段の予備判定の集計を一度見た（記入表 2 の道具を書くため・ユーザーには見せていない）。判定者 1 への問いや報告に、記入表 1 を読む前の AI の数を混ぜない。
