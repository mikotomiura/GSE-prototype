# 次セッション — AI 疲労 文献 DB: N-05 プロトコルのタスクの続き（間引きの反映・判定者用ファイルの作り直し・プロトコルの草稿）

> 作成: 2026-09-30 23:55（`.steering/20260930-ai-fatigue-protocol/` の途中。コンテキストが約半分になったので区切った）。⚠️ **このメモを一次資料にしない。** 決定は `decisions.md` 判断 1〜7、手順は `design.md` §1・§2・§7。
> ★ ユーザーは **判定者 1 の立場**。判定者 2 の人選など研究者が決めることは、ユーザーに聞かない（「研究者の決定待ち」と書く・記憶 `project_ai_fatigue_judge1_saw_appraisal`）。
> ★ 判定者用ファイルは **まだ未記入**（ユーザーの答え・判断 3）。作り直す直前に Downloads の写しの SHA-256 が archive（`6984472e…`）と同じかを確かめ、違えば止まって聞く。

## §0 打ち込む用（★ `/clear` してから。モデルは Opus）

```
.steering/_handoff/next-session-ai-fatigue-protocol-cont.md を読んで、AI 疲労 文献 DB の N-05 プロトコルのタスク（.steering/20260930-ai-fatigue-protocol/）の続きを進めてください。まず §1 の 1（判定者用ファイルの作り直し）から。

⚠️ 作業は worktree C:\wt\ai-fatigue-judge-file のブランチ docs/ai-fatigue-protocol で行う（main の作業ツリー C:\GSE-prototype には別トラックの未コミット作業がある）。先に git fetch と origin/main を確かめる。git add -A / git add <dir> は使わない。
⚠️ Downloads の AI_fatigue_judge-sheet_2026-09-30_judge1.xlsx は、作り直す直前の SHA-256 の確認と、judge_xlsx.py の --copy-to（記入があれば上書きしない柵つき）以外で触らない。
⚠️ 外部に出る操作（著者への照会・フォーム・OSF への登録）はしない。学術 API に研究者のメールアドレスを送らない。本文・PDF・抄録の全文はコミットしない。有料のデータベース・有料の本文は使わない。候補を AI の見立て（E1〜E3）で絞らない（同じ報告の版違いを寄せるのは判断 3 で許された）。
⚠️ Codex を回す前に当日の実消費を確かめる（台帳はブランチごと・合算で上限 300,000・予算ガードの hook は C:\GSE-prototype の台帳を読む・.codex/budget.json を git checkout -- で戻さない）。
★ 完了時は code-reviewer ＋ security-checker（並列）・/cross-review 2 巡・git-workflow ルール 6（push → PR → CI 緑なら merge → main の CI 発火確認）。応答は日本語。
```

## §1 残っていること（順に）

1. **判定者用ファイルの作り直し**（判断 3・design.md §7.5）
   - `../20260930-ai-fatigue-judge-file/scripts/judge_xlsx.py` に、`evidence/dedup/classification_2026-09-30_final.json` と `content_groups_2026-09-30_final.json`（内容の群）を読む処理を足す。
   - 『追加候補』から寄せる 5 件（S04-44・S04-79・S12-16・S12-12・S14-51）を外す（225 → 220）。『寄せた記録』シートを足す（寄せた記録・代表・一致点。`dedup-259.md` §2）。
   - 両方のシートに「同じ研究の群」の列（G01〜G11・U1〜U2 と一致点・違う点。`dedup-259.md` §3）と「内容の群（機械の分類・並べ替えのため）」の列を足す。
   - 『はじめに』に、間引きの規則と、群の列が判定の材料ではないこと（E5 は判定者が決める）を書く。判定者 2 の「開かないもの」は変えない（`dedup-259.md` は判定者 2 も読んでよい）。
   - `check_judge_xlsx.py`（見出し・golden・selftest）を合わせ、変異で赤を確かめる。追加候補の評価版（AI の評価の xlsx）は作り直さない（寄せた記録の行が残ることを『はじめに』に書く）。
2. **内容の群の全件の確かめ**（判断 6 の続き）: 抜き取り 30 件で 20 件しか正しくなかった。全 259 件をメインが確かめるか、規則を直して抜き取りをし直すかを決め、`decisions.md` に書く。⚠️ 1 より先にやるなら、判定者用ファイルに入れる値が変わる。
3. **プロトコルの草稿** `protocol-ja.md`（design.md §1）: GSRR 65 項目（PMC10514995 で確かめた名前は design.md §1.1 と `decisions.md` の前の記録）。付録 A の年表は、サブエージェントの材料（`tasklist.md` 準備の 5 行目）を一次（ノート・コミット時刻）で裏取りしてから書く。★ 間引き（判断 3〜7）と、本検索でも判定者 1 が AI の評価を先に読むこと（判断 2）を必ず書く。
4. **検索式の開発**: `evidence/search_dev.py seeds` → `counts` → `fetch` → `recall`（design.md §2）。Semantic Scholar は 429 が出やすい（ほかの取得と同時に回さない）。
5. **理論の文献の貼れる xlsx**（design.md §4・判断 1）。
6. `issue-status.md`・レビュー・/cross-review 2 巡・出荷。

## §2 いまの数（2026-09-30 23:55）

| 何 | 値 | 出どころ |
|---|---|---|
| 間引き | 同じ報告 5 件を寄せる（追加候補 225 → 220・DB 34 は変えない）。同じ研究の群 11 群・要確認 2 群 | `dedup-259.md`・`evidence/dedup/classification_2026-09-30_final.json` |
| 第 2 の読み | 同じ報告・訂正は一致。食い違いは群の広さの 10 組（メインの読み方を採った） | `dedup-259.md` §5・判断 7 |
| 内容の群 | 79 群。不明 22 件。抜き取り 30 件で 20 件が正しい | `dedup-259.md` §6・判断 6 |
| 検索式の開発 | 道具と種 25 件まで（まだ回していない） | `evidence/search_dev.py`・`seeds.json` |

## §3 落とし穴（本セッションで起きたこと）

- heredoc の中のバックスラッシュ（正規表現の `\b` など）を置き換えに使うと空振りする（判断 6）。Python の置き換えは Edit で行う。`;` や改行でつなぐと、失敗しても次のコマンドが走る（`&&` でつなぐ）。
- Windows のコンソールは日本語を cp932 で出して化ける → `PYTHONIOENCODING=utf-8` を付ける。
- 独立の読み手に渡す束に著者を先頭の 10 名しか出さなかったので、読み手は重なりを少なく数えた（S04-16・S04-66）。束には著者の全員を出す。
- 実行の後に規則を直したことが 2 回ある（判断 4・6）。直すときは、先に決めた規則との差と失うものを書く。
