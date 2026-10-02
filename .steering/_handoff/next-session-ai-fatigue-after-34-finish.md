# 次セッション — AI 疲労 文献 DB: 34 件の後のタスクの完了（PR #288 の Codex と merge・本タスクのレビューと出荷）

> ✅ **完了（2026-10-02・2 つ目のセッション）。** §2 の 1〜5 は済んだ（PR #288 は merge `8cf19570`・本タスクは判断 10〜12）。⚠️ 下の SHA（34 件の写し `38124cd3…`・追加候補の表 `0b9363b7…`）と「判断 1〜9」は当時の値で、今は `3499b70f…`・`00aeee92…`・判断 1〜12。§3 の「6 枚は誤りで 5 枚」は当時の事実で、写しは判断 14（34 件のタスク）で 6 枚になった。**次は `next-session-ai-fatigue-v2.md`。**

> 作成: 2026-10-02（`ai-fatigue-after-34` の 1 つ目のセッションの終わり・コンテキストが半分ほどで区切った）。⚠️ **このメモを一次資料にしない。** 一次は `.steering/20261002-ai-fatigue-after-34/`（requirement・design・decisions 判断 1〜9・tasklist・novelty-check・review-search）。
> ★ ユーザーは **判定者 1**。DB を作ったのは「相手の研究者」。研究者が決めることはユーザーに聞かない（「研究者の決定待ち」と書く）。

## §0 打ち込む用（★ `/clear` してから。モデルは Opus）

```
.steering/_handoff/next-session-ai-fatigue-after-34-finish.md を読んで、AI 疲労 文献 DB の 34 件の後のタスク（.steering/20261002-ai-fatigue-after-34/）の完了の手順を進めてください。worktree C:\wt\ai-fatigue-judge-file のブランチ docs/ai-fatigue-after-34 で作業する。まず tasklist.md と decisions.md 判断 1〜9 を読む。

⚠️ 順: (1) PR #288 の Codex 2 巡（道具・記録）と指摘への対応 → #288 の merge（main の CI 確認）→ (2) 本ブランチを main に追随 → 本タスクの code-reviewer ＋ security-checker（並列）→ /cross-review 2 巡 → 出荷（git-workflow ルール 6）。Codex の当日の実消費を先に確かめる（足りなければ上限を引き上げてよい＝34 件のタスクの判断 3。tokens_used は触らない）。台帳はブランチごと（記憶 project_codex_ledger_branch_split）。
⚠️ git add -A / git add <dir> は使わない。C:\GSE-prototype は別のトラックの作業ツリー。
⚠️ 研究者の元のファイル（48ba8b90…）・判定者用ファイル（10107fcf…）・評価版（ed788f53…）・34 件の写し（38124cd3…）は変えない。追加候補の表は scripts/build_candidates.py だけで書く。提案のドキュメントは scripts/build_proposal.py だけで書く。
⚠️ 外部に出る操作（研究者・著者への送信・フォーム・OSF）はしない（提案のドキュメントと 2 つの xlsx を研究者に渡すのはユーザー）。本文・PDF・抄録の全文はコミットしない（本文は git の外の C:\Users\johnd\Downloads\ai-fatigue-fulltext\）。
★ 応答は日本語。サブエージェントの前に subagent-delegation Skill、Chrome の前に browser-verification Skill。
```

## §1 このセッションで終わったこと（2026-10-02）

| 何 | 状態 | どこ |
|---|---|---|
| grill | 8 問とも推奨どおり＋記録先を新しい表に変更（ユーザーの提案） | decisions 判断 1・2 |
| 追加候補 8 件の判定（2 段） | S02-08 除外 E4／X01 除外 E4（AI の判定なし）／S08-03 保留 E6／S15-23 保留／S13-20 保留／S12-05 保留／S12-19 除外 E1／S12-23 除外 E1。抽出の確定 6 件。ログ 17 行 | `screening-log.jsonl`・`data/extract-rows.json` |
| 追加候補の表 | `AI_fatigue_additional_candidates_judge1.xlsx`（Downloads と archive・`0b9363b7…`）。220 件＋X01 の全行・判定した 8 行・AI判定比較 7 行・探索の一覧 5,721 行 | `check_candidates.py --final` 違反 0・`--selftest` PASS |
| レビューを狙った探索 | 4 API・5,721 件 → 題名の層 → 読む一覧 46 件（判断 4〜7）。OpenAlex は 16 回が 429 で抜けた | `review-search.md`・`data/search-*.json` |
| 新規性の確認（本タスクの版） | 本文 37 本（レビュー 33）。既にあるもの・無いもの（候補 1〜4）を書き直した | `novelty-check.md` |
| C の決定 | **研究者に構想を示してから決める**（判断 9）。原稿の作業はしない | decisions 判断 9 |
| 提案のドキュメント v1 | `AI疲労DB_判定者1からの提案_v1.docx`（Downloads と archive）。§0〜§9・付録は 2 つの表から作り直す | `check_proposal.py` 違反 0・`--selftest` PASS |

## §2 次にやること（順）

1. **PR #288 の Codex 2 巡**（34 件のタスクの判断 13 の手順の控え）: worktree で `bash scripts/run-codex-review.sh 9f5796d5..5107b009 -- <34 件のタスクの scripts 7 本・requirement.md・design.md>`（出力は scratchpad）→ 2 回目（記録: decisions.md・novelty-check.md・tasklist.md・measurement-issues.md・requirement.md・_handoff の 2 ファイル）。⚠️ `.xlsx`・`wave1/`・`screening-log.jsonl`・`data/*.json` は渡さない。2 巡目は 1 巡目の直しで足した規則の境界条件だけ。「codex exec error」なら最小のプロンプトで `codex exec --json` を 1 回試して JSON の `error` を読む。⚠️ #288 の直しで前のタスクの道具（`write_workbook.py` など）を変えたら、34 件の写しを作り直すことになり、本タスクの `common.py` の 34 件の写しの SHA-256 の照合（`copy-sha256.txt` を読む）は自動で追随する。追加候補の表と提案のドキュメントの付録も作り直す（`build_candidates.py`・`build_proposal.py`）。
2. #288 を merge（CI 緑の後）→ main の CI 発火確認。
3. 本ブランチを main に追随（rebase か merge）→ 本タスクの範囲（`5107b009..HEAD` のうち本タスクのもの）で code-reviewer ＋ security-checker を並列（範囲・禁止・締切の 5 点を書く。`--selftest` は 1 分近くかかるので回させない）。
4. /cross-review 2 巡（Codex には xlsx・docx・`screening-log.jsonl`・`data/search-records.json`〈2.3 MB〉を渡さない。テキストの道具と記録だけ）。
5. 出荷（push → PR → CI 緑なら merge → main の CI 確認）。PR の本文に「研究者への送信はユーザーが行う」と書く。
6. 次のタスクの引き継ぎ: 残りの 213 件の判定（34 件と同じ 2 段・同じ表に記入）と提案のドキュメント v2・研究者の返事（Q1〜Q10）を待つこと。

## §3 落とし穴（このセッションで起きたこと）

- **探索の定義が広すぎた**（判断 5）: AI の語に machine learning・algorithm・automation を入れ、語境界なし・抄録込みで照合したため、5,721 件の大半が技術系（材料の疲労・疲労の検出）だった。ユーザーに「全部 ML 関連での技術的な話により初めてない？」と指摘された。次に探索を定義するときは、題名での照合と語の群ごとの見込み件数を先に小さく試す。
- **OpenAlex はメールを送らない匿名の利用で 429 が続く**（当日の上限）。広い語での取り直しは 30 分の上限で止められ、結果をファイルに書く前だった → 長い取り直しは逐次ファイルに書く（`python -u`・1 問い合わせごとに保存）。
- **サブエージェントの締切は守られない**ことがある（探索は 20 分の指定で約 35 分）。抽出の 4 本は 4〜8 分で完走。
- **curl は止まるが Chrome では開ける**記録が多い（SSRN・Cureus・MDPI・SHS）。Chrome の PDF はユーザーに Ctrl+S で保存してもらう。Turkish Studies は iframe の中の PDF の URL を curl で取れた。EKB の記事のページの PDF のリンクが別の論文を指していた（R03）。
- **Chrome のタブの番号は途中で振り直される**ことがある（`tabs_close_mcp` が「グループに無い」で失敗）→ `tabs_context_mcp` で取り直す。ユーザーがタブを閉じることもある。
- **git-bash の heredoc でバックスラッシュが壊れる**（JSON の `Downloads\ai-…` が `\a`＝ベルになり openpyxl が IllegalCharacterError）→ Python の文字列は Write で置いたスクリプトから。研究者に渡す表には手元のパスを書かない。
- **AskUserQuestion の問いの文をエスケープで書くと誤字が出る**（「抽録」）。問いの文は日本語のまま、ログには逐語。
- **python-docx の表の列幅**: セルの幅だけでは LibreOffice・Word の一部は変わらない → `table.columns[j].width`（gridCol）も設定する。
- 前の引き継ぎの「足したシート 6 枚」は誤りで 5 枚（判断 8）。
- **Downloads の直下に `shsconf_sdmc2022_03022.pdf`**（R47 と同じ中身・`cmp` で一致）が残っている。ユーザーが保存したものとみられるので消していない（ユーザーに伝える）。
