# 次セッション — AI 疲労 文献 DB: 判定の基準の確定（N-05 の範囲）→ 判定者用ファイルを仕上げる

> 作成: 2026-09-29（`.steering/20260929-ai-fatigue-surveys/` の完了時）。更新: 2026-09-30（PR #266 の merge 後。Codex の 2 巡の結果・片付け・落とし穴を足した）。⚠️ **このメモを一次資料にしない。** 数字は 2026-09-30 の値で、各行に出どころを書いた。
> ★ 研究者の方針（2026-09-29・逐語は `.steering/20260929-ai-fatigue-db-readable-and-gaps/ideas.md` 冒頭）: **サーヴェイ → サーヴェイとアイディアのまとめができた段階で判定者用ファイルを仕上げる → 判定 → 相手先に送る判定後のスプレッドシート**。
> ★ サーヴェイ A 群（S-12 → S-02 → S-08 → S-04 → S-05）は完了した（`.steering/20260929-ai-fatigue-surveys/issue-status.md`）。

## §0 打ち込む用（★ `/clear` してから。モデルは Opus）

```
.steering/_handoff/next-session-ai-fatigue-judge-file.md を読んで、AI 疲労 文献 DB の次の段（判定の基準の確定 → 判定者用ファイル）を進めてください。

⚠️ 前提: サーヴェイ A 群の成果は PR #266 で main に入った（2026-09-30・fca48e43）。この引き継ぎの更新は後続の PR（ブランチ docs/ai-fatigue-judge-handoff）で入る。gh pr list --head docs/ai-fatigue-judge-handoff --state merged で確かめる（ファイルの有無では判定しない）。
⚠️ まず git fetch → origin/main から作業ブランチ・worktree を切る（★ 作業ツリーには別トラックの未コミット作業がある）。/start-task（task 名: ai-fatigue-judge-file）。
★ 先に読む（研究者に確かめる前に、Claude が読む）: .steering/20260929-ai-fatigue-surveys/ の issue-status.md・decisions.md、
   判定案のファイル（survey-S-04-ai-judgments.md §4・survey-S-05-ai-judgments.md §2 = N-05 の範囲の論点）、
   .steering/20260929-ai-fatigue-db-readable-and-gaps/prior-draft/README.md（判定者用ファイルの下書きで直すこと 6 点）、
   .steering/20260928-ai-fatigue-db-appraisal/design.md（評価プロトコル v1.0）。
★ 最初に研究者に確かめること（§2）を AskUserQuestion で聞く。★ 判定者 1（研究者）に AI の判定案を見せない聞き方をする（§2 の注意）。
⚠️ 判定者用ファイルには AI の判定・懸念の語を 1 つも入れない（機械で確かめ、変異で赤になることも確かめる）。
⚠️ DB（xlsx）の行は足さない・変えない。追加の候補は判定者用ファイルに「追加候補（書誌だけ）」として並べるかを研究者に確かめる。
⚠️ 外部に出る操作（著者への照会・フォーム）はしない。学術 API に研究者のメールアドレスを送らない。本文・PDF・抄録の全文・尺度の項目文はコミットしない。
⚠️ git add -A / git add <dir> は使わない。.steering/20260921-media-expression-theory-audit/（別トラック）は触らない・コミットしない。
⚠️ .codex/budget.json は台帳（git checkout -- で戻さない）。Codex を回す前に当日の実消費を確かめる（実消費 = 共通祖先の当日分 ＋ Σ（各ブランチの当日分 − 共通祖先の当日分）。上限 300,000）。merge で衝突したら和を採る（二重に数えない）。
★ 完了時は /finish-task（code-reviewer＋security-checker 並列 → /cross-review 2 巡）→ git-workflow ルール 6。
応答は日本語。
```

## §1 現在の状態（2026-09-30）

| 何 | 値 | 出どころ |
|---|---|---|
| サーヴェイ A 群 | 5 本とも 3 ファイル（事実・AI の判定案・GSE の含意）を残した | `.steering/20260929-ai-fatigue-surveys/survey-S-*.md` |
| 閉じた通常 issue | N-06（データセット 2 件）・N-07（AF001 の 15 項目は本文 Table 1・事前登録は研究 2〜4） | `issue-status.md` §2 |
| DB への提案 | `db-proposals.md`（★ 判定案の一種。判定者 1 は判定の後に読む） | 同 |
| [研究者] への依頼 | `researcher-requests.md`（有料データベース 3・本文の入手 12） | 同 |
| 評価版の xlsx・issues.md | 再生成していない（状態の反映は次に xlsx を作り直すとき・`issue-status.md` §3） | 同 |
| 機械の検査 | `scripts/check_survey_files.py`（事実のファイルに判定・評価・GSE の語が無いこと等）・`--selftest`（変異 147 種がすべて赤）。★ issue-status.md・researcher-requests.md も同じ検査の対象 | `.steering/20260929-ai-fatigue-surveys/` の `tasklist.md`・`decisions.md` 判断 13・16・17 |
| 検索スクリプトの流用 | 実行した版（`evidence/S-*/*.py`）は再実行を止めてある。★ B 群のサーヴェイで検索を書くときは `evidence/common.py`（抄録を空で上書きしない・repo の外の確認・書誌と抄録の対の排他的な作成・URL の構造的な許可とリダイレクトの柵・枠の切り出し）を使う。テスト 17 件 | `evidence/README.md` |
| レビュー | code-reviewer・security-checker（判断 12〜15）と Codex の `/cross-review` 2 巡（判断 16・17）はすべて対応済み。★ Codex の 1 巡目で S-05 の抽出の 6 件が抄録なしで渡っていたことが分かり、表の 4 行を直して数え直した（実験 76 → 77 など） | `decisions.md` 判断 16・17 |
| main | PR #266 を merge（`fca48e43`・2026-09-30）。CI は緑（Windows・macOS・frontend）、main の workflow run の起動も確認 | `tasklist.md` の完了処理 |

## §2 最初に研究者に確かめること

1. **N-05 の範囲（判定の基準）**: (a) S-04 の「AI を導入して疲労・燃え尽きが減るかを測った介入研究」（医療の AI 記録支援が大半）を DB の範囲に入れるか、(b) S-05 の自動運転・航空などの自動化の監視を「AI」に含めるか、(c) サーヴェイで見つかった新しい候補（S-02・S-12・S-04）を判定の対象に入れるか。
   - ⚠️ 聞き方: 研究者は判定者 1。**AI の判定案（どれが中心-A/B か）を示さずに**、範囲の選択肢と、それぞれで判定の対象が何件増えるか（書誌の数だけ）を示す。★ 数は事実のファイルから次のように数える: S-04 は §2.4 の比較の単位の行（AI の有無を群の間で比べた無作為化 7・非無作為化 4・前後比較 19 と、道具どうし・事後の利用量・使い方どうしの比較 4 件）を分けて示す。★ 範囲の選択肢は結果の向きで分けない（判断 16）。S-02 は §1 の 11 件（うちレビュー 1）。S-12 は §4.1 の 5 件（★ うち 2 件はテクノストレス・授業の報告で疲労を測っていない＝事実のファイルの表の「疲労などの測り方」の列）と §4.2 の日本以外の新しい研究。S-05 は範囲に入れるかの論点で、件数は §7 の実験・実地 108 件のうち構成概念が受動的疲労・覚醒・慢心のもの（抽出の表で数える）。
2. **判定者 2** を誰にするか（AI の結果を見ていない人が望ましい）。
3. **研究者が既に読んだ範囲**: チャットの要約・完了報告を含め、AI の判定案をどこまで見たかを、判定の記録に書くために確かめる（★ 本タスクの完了報告は件数だけにした）。
4. **[研究者] の依頼**（`researcher-requests.md`）: 医中誌 Web の検索・本文 12 件の入手・ブラウザで ScienceDirect を読んでよいか。
5. 片付け（前回からの持ち越しを含む）: (a) 前回の worktree `C:\GSE-ai-fatigue-appraisal` の未コミットのファイルを残すか消すか（写しは `prior-draft/` にある）。(b) ローカルだけのブランチ `backup/ai-fatigue-surveys-pre-scrub` を消してよいか（★ 著者のメールアドレスを履歴から消す前の控え。**push しない**。消すなら `git branch -D`）。(c) 前タスクの worktree `C:/wt/ai-fatigue-surveys`（PR #266 と引き継ぎの更新の PR が merge 済みなら `git worktree remove` してよい）。

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
- **情報源をまたいで抄録を集めるとき `dict.update` を使わない**: 後の情報源の空の抄録が前の抄録を消し、S-05 で 6 件が抄録なしで抽出に渡った（判断 16）。`evidence/common.py` の `merge_abstract` を使う。
- **Codex の台帳は日付をまたぐと衝突する**: 分岐元の `today` を引き継いだブランチで日付が変わると、merge の時に `today` と `history` が衝突する。前日の値は main 側の和を採り、当日の値はブランチ側を採った（判断 17・`_comment_merge_2026_09_30`）。前日の合算が上限を超えていたら、Codex は日付が変わってから回す。
- **CI の Windows の check は 18 分ほどかかる**（G-GEAR の self-hosted）。`gh pr checks --watch` は 10 分の timeout に当たるので、終わるまで待つループにする。
- **完了報告は件数だけ**: 研究者は判定者 1。チャットに 1 件ごとの判定案・評価を書かない（「どういう結果が出たか」と聞かれたときも、事実と件数で答える）。
