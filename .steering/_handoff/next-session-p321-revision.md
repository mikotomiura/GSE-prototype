# 次セッション — p321 の改訂（JSS へ）: 文献検索 B のやり直しから

> 作成: 2026-11-21 夜（S7 の修正案を採り、判断 21〜23 まで実施した）。このメモを一次資料にしない。着手するときに状態を測り直す（git・照会の返事・論文用リポジトリ）。

## §0 打ち込む用

```
git fetch origin してから MSYS_NO_PATHCONV=1 git show origin/docs/p321-emse-desk-reject:.steering/_handoff/next-session-p321-revision.md を読んで、§2 の上から進めてください。
worktree は C:/GSE-wt/p321-desk-reject（ブランチ docs/p321-emse-desk-reject）。タスクは .steering/20261121-p321-paper-revision/（decisions 判断 1〜23・design.md・tasklist・survey-s2.md・search-log/）。
論文用リポジトリは C:/self-resolution-measure のブランチ revision-jss（未 push。S9 まで push しない）。着手時に git status が clean で、HEAD が bab36eb かを確かめる。研究者の PDF 照合の結果を聞き、済んでいれば §5.3 の文を直す。
Tectonic 0.17.0 が scratchpad から消えていたら、GitHub のリリースから取り直し、TECTONIC=<path> bash paper/build.sh で使う。
照会（2026-11-21 に送信・待つ目安は 12-05）に返事が来ているかを研究者に聞く。
```

## §1 守ること（CLAUDE.md と memory から）

- 返答は日本語で書く。★ や ⚠️ を多用しない。
- 調べものはサブエージェントへ出す（model を明示・入れ子は禁止・締切を書く）。戻ってきた行は、使う前にメインが一次で確かめる。有料の本文は使わない。
- 公開物には GSE への言及を入れない。学術的な英語で書く。
- 凍結を壊さない。新しい解析は `post_review` にだけ足し、NOTES.md の Deviations に追記する。`run.sh` は値が変わると止まる → 意図した追加の後だけ `ALLOW_RESULT_CHANGE=1` を付ける。
- 本文の数字は `\R{...}` だけで出す。新しい質的な文には、`make_results.py` に検査と変異を足す。
- バックスラッシュを含む置き換えは heredoc でやらない（今回も壊れた）。Edit か、Write で作った .py を使う。
- git は明示のパスで add する。外に出る行為は、研究者がするか、研究者の確認の後にする。

## §2 残り

| 順 | 何を | 注意 |
|---|---|---|
| 1 | 文献検索 B（キーワード）を、記録を付けてやり直す。`search-log/README.md` の 7 問を OpenAlex で（日本時間 9 時以降に。上限は UTC 0 時に戻る） | Sonnet に出す。scratchpad の `search-log/downloads` は消えているかもしれない。表と台本は `.steering/.../search-log/` にある |
| 2 | 付録を作る。`supplement/literature-search/` を論文用リポジトリに置き、`citing-works.tsv`・`keyword-queries.tsv`・README（基準の文・日付・情報源・重複の規則・数・抜け）を入れる。PDF と本文の txt は入れない | 1 回目（58 件・本文 36）は 1 件ごとの記録が無い。2 回目（70 件・本文 43・NEAR 2・INSTANCE 0）を付録にする。§2.5 には両方の数を書き、差は説明できていないと書く |
| 3 | §2.5 と §5.5 (3) を書き換える。ビルドし、`check_frontmatter` を通す | 「見つからなかった」を「存在しない」にしない |
| 4 | 研究者に聞く: 生成 AI の申告に「使った後に著者が読み、必要に応じて直した」を足してよいか ／ journal 版の 8 つの値を PDF と照合するか | |
| 5 | S8: attack-me round 2 → `/cross-review` 2 巡 | 今回足した節（§3.1・RQ1・§7「Beyond」・audit）を重点に見る |
| 6 | S9: 照会の結果を RQ4 に ／ タグ ／ Zenodo の新しい版 ／ DOI ／ 投稿 ／ GSE 側の PR | `survey-s2.md` に推薦の査読者の候補がある |

## §3 今回分かったこと（判断 21〜23 の要点）

- 研究者は修正案をすべて採った。採らなかったのは、題と RQ の全面的な書き換えだけ。
- 独立に数え直した結果（`audit/independent-recount/`）: 一致しなかったのは、DF3 がセッションの最後かどうかだけ。原因は Video8 で、ファイルの並びが時刻順になっていない。いまの解析は時刻の順で並べており、こちらが正しい。
- LODO: D1 は 10.3〜12.5pp、D2 の table+text は 0〜7.1pp。b/(a+b) は D1 で 14.3%。
- 新しい文献: Shihab ほか 2025 [P641]。Hellas 2023 は既に引いていた [P435]。
