# 次セッション — AI 疲労 文献 DB: 判定の基準の確定（N-05 の範囲）→ 判定者用ファイルを仕上げる

> 作成: 2026-09-29（`.steering/20260929-ai-fatigue-surveys/` の完了時）。⚠️ **このメモを一次資料にしない。** 数字は 2026-09-29 の値で、各行に出どころを書いた。
> ★ 研究者の方針（2026-09-29・逐語は `.steering/20260929-ai-fatigue-db-readable-and-gaps/ideas.md` 冒頭）: **サーヴェイ → サーヴェイとアイディアのまとめができた段階で判定者用ファイルを仕上げる → 判定 → 相手先に送る判定後のスプレッドシート**。
> ★ サーヴェイ A 群（S-12 → S-02 → S-08 → S-04 → S-05）は完了した（`.steering/20260929-ai-fatigue-surveys/issue-status.md`）。

## §0 打ち込む用（★ `/clear` してから。モデルは Opus）

```
.steering/_handoff/next-session-ai-fatigue-judge-file.md を読んで、AI 疲労 文献 DB の次の段（判定の基準の確定 → 判定者用ファイル）を進めてください。

⚠️ 前提: サーヴェイ A 群の成果は PR（ブランチ docs/ai-fatigue-surveys）で main に入る。gh pr list --head docs/ai-fatigue-surveys --state merged で確かめる（ファイルの有無では判定しない）。未マージならそのブランチから切る。
⚠️ まず git fetch → origin/main から作業ブランチ・worktree を切る（★ 作業ツリーには別トラックの未コミット作業がある）。/start-task（task 名: ai-fatigue-judge-file）。
★ 先に読む（研究者に確かめる前に、Claude が読む）: .steering/20260929-ai-fatigue-surveys/ の issue-status.md・decisions.md、
   判定案のファイル（survey-S-04-ai-judgments.md §4・survey-S-05-ai-judgments.md §2 = N-05 の範囲の論点）、
   .steering/20260929-ai-fatigue-db-readable-and-gaps/prior-draft/README.md（判定者用ファイルの下書きで直すこと 6 点）、
   .steering/20260928-ai-fatigue-db-appraisal/design.md（評価プロトコル v1.0）。
★ 最初に研究者に確かめること（§2）を AskUserQuestion で聞く。★ 判定者 1（研究者）に AI の判定案を見せない聞き方をする（§2 の注意）。
⚠️ 判定者用ファイルには AI の判定・懸念の語を 1 つも入れない（機械で確かめ、変異で赤になることも確かめる）。
⚠️ DB（xlsx）の行は足さない・変えない。追加の候補は判定者用ファイルに「追加候補（書誌だけ）」として並べるかを研究者に確かめる。
⚠️ 外部に出る操作（著者への照会・フォーム）はしない。学術 API に研究者のメールアドレスを送らない。本文・PDF・抄録の全文・尺度の項目文はコミットしない。
⚠️ git add -A / git add <dir> は使わない。.codex/budget.json は台帳（git checkout -- で戻さない）。
★ 完了時は /finish-task（code-reviewer＋security-checker 並列 → /cross-review 2 巡）→ git-workflow ルール 6。
応答は日本語。
```

## §1 現在の状態（2026-09-29）

| 何 | 値 | 出どころ |
|---|---|---|
| サーヴェイ A 群 | 5 本とも 3 ファイル（事実・AI の判定案・GSE の含意）を残した | `.steering/20260929-ai-fatigue-surveys/survey-S-*.md` |
| 閉じた通常 issue | N-06（データセット 2 件）・N-07（AF001 の 15 項目は本文 Table 1・事前登録は研究 2〜4） | `issue-status.md` §2 |
| DB への提案 | `db-proposals.md`（★ 判定案の一種。判定者 1 は判定の後に読む） | 同 |
| [研究者] への依頼 | `researcher-requests.md`（有料データベース 3・本文の入手 9） | 同 |
| 評価版の xlsx・issues.md | 再生成していない（状態の反映は次に xlsx を作り直すとき・`issue-status.md` §3） | 同 |
| 機械の検査 | `scripts/check_survey_files.py`（事実のファイルに判定・評価・GSE の語が無いこと等）・`--selftest`（変異 63 種がすべて赤） | 同 |

## §2 最初に研究者に確かめること

1. **N-05 の範囲（判定の基準）**: (a) S-04 の「AI を導入して疲労・燃え尽きが減るかを測った介入研究」（医療の AI 記録支援が大半）を DB の範囲に入れるか、(b) S-05 の自動運転・航空などの自動化の監視を「AI」に含めるか、(c) サーヴェイで見つかった新しい候補（S-02・S-12・S-04）を判定の対象に入れるか。
   - ⚠️ 聞き方: 研究者は判定者 1。**AI の判定案（どれが中心-A/B か）を示さずに**、範囲の選択肢と、それぞれで判定の対象が何件増えるか（書誌の数だけ）を示す。★ 数は `survey-S-04.md` §2（比較のある 34 件）・`survey-S-02.md` §1（11 件）・`survey-S-12.md` §4.1（5 件）・`survey-S-05.md` §7 から数えられる（いずれも事実のファイル）。
2. **判定者 2** を誰にするか（AI の結果を見ていない人が望ましい）。
3. **研究者が既に読んだ範囲**: チャットの要約・完了報告を含め、AI の判定案をどこまで見たかを、判定の記録に書くために確かめる（★ 本タスクの完了報告は件数だけにした）。
4. **[研究者] の依頼**（`researcher-requests.md`）: 医中誌 Web の検索・本文 9 件の入手・ブラウザで ScienceDirect を読んでよいか。
5. 前回の worktree `C:\GSE-ai-fatigue-appraisal` の未コミットのファイルを残すか消すか（写しは `prior-draft/` にある・前回からの持ち越し）。

## §3 判定者用ファイルを仕上げる（N-02）

- 出発点: `.steering/20260929-ai-fatigue-db-readable-and-gaps/prior-draft/judge_xlsx.py`（⚠️ 仕上げるときに直すことは同じ場所の `README.md`）。
- 判定の対象: DB の 34 件 ＋（§2-1 で決めた）追加候補。追加候補の欄は**書誌と、事実のファイルの抄録の要点だけ**（`survey-S-xx.md` の記述）。
- AI の判定・懸念の語を 1 つも含めない（語の一覧は `.steering/20260929-ai-fatigue-surveys/scripts/check_survey_files.py` の `JUDGE`・`EVAL`・`GSE` を出発点にし、xlsx の全セル・コメント・定義名・文書のプロパティに当てる。変異で赤になることを格納先ごとに確かめる＝前回の引き継ぎ §4-5 と同じ作法）。

## §4 その後の段（★ このセッションではやらない）

判定（判定者 1・2）→ 不一致の調整 → 相手先に送る判定後のスプレッドシート（許可リストから組み立て・格納先ごとの変異試験。前の引き継ぎ `next-session-ai-fatigue-surveys.md` §4-5）。B 群のサーヴェイ（S-01 本検索・S-06・S-09・S-11）は N-05 の後。

## §5 落とし穴（★ 2026-09-29 に実際に起きたこと）

- **抄録の前処理**: `re.sub(r"<[^>]+>", " ", …)` は「p < .001」の `<` から次の `>` までを消す。タグの名前を限って消す（`decisions.md` 判断 11）。
- **機械のふるいは種文献で確かめる**: 種文献が通らなければ正規表現の漏れ（判断 10）。
- **OpenAlex**: 匿名の `search` は時間帯によって 503。通ったときも AND・OR・引用符を期待どおりに解釈しないことがある（判断 3・9）。1 件の取得（`/works/doi:…`）は使える。
- **Zenodo**: 続けて取得すると 403（大量アクセスの制限）。
- **時刻は `date` か記録（JSON の executed・コミットの時刻）から書く**（推測で書いて 1 時間半ずれた・判断 8）。
- **サブエージェントの抽出は一次で確かめる**: S-02 で 1 点（本調査の対象）が一次と合わなかった（判断 6）。
