# 次セッション — p321 の改訂（JSS へ）の S7 から

> 作成: 2026-11-21（S0〜S6 を終えた。S7 は研究者の通読なので区切った）。このメモを一次資料にしない。状態は着手時に測り直す（git・照会の返事・論文用リポジトリ）。

## §0 打ち込む用

```
git fetch origin してから MSYS_NO_PATHCONV=1 git show origin/docs/p321-emse-desk-reject:.steering/_handoff/next-session-p321-revision.md を読んで、§2 の S7 から進めてください。
worktree は C:/GSE-wt/p321-desk-reject（ブランチ docs/p321-emse-desk-reject）。タスクは .steering/20261121-p321-paper-revision/（decisions 判断 1〜20・design.md・tasklist・survey-s2.md）。
論文用リポジトリは C:/self-resolution-measure のブランチ revision-jss（未 push・S9 まで push しない）。着手時に git status が clean で HEAD が 6d0d3b4 かを確かめる。
Tectonic 0.17.0 が scratchpad から消えていれば GitHub のリリースから取り直し、TECTONIC=<path> bash paper/build.sh。
照会（2026-11-21 送信・待つ目安 12-05）に返事が来ているか研究者に聞く。
```

## §1 守ること（CLAUDE.md・memory から）

- 返答は日本語。★ や ⚠️ を多用しない。
- 調べものはサブエージェントへ（model を明示・入れ子禁止・締切）。戻りの行は使う前にメインが一次で確かめる。有料の本文は使わない。
- 公開物には GSE への言及を入れない。学術的な英語にする。
- 凍結を壊さない: `analyze.py` が提出版の値と凍結した config をハッシュで守る。新しい解析は `post_review` にだけ足し、NOTES.md の Deviations に追記する。`run.sh` は値が変わると止まる → 意図した追加の後だけ `ALLOW_RESULT_CHANGE=1`。
- 本文の数字は `\R{...}` だけ。新しい質的な文は `make_results.py` に検査と変異を足す。要旨・Highlights・声明・禁止する文言は `paper/check_frontmatter.py`（build.sh の Step 2）が見る。
- バックスラッシュを含む置き換えや検査は heredoc でやらない（今回も 1 回壊れた）。Edit か Write で作った .py で。
- git は明示のパスで add する。外に出る行為は研究者がするか、研究者の確認の後。

## §2 残り

| 段 | 何を | 注意 |
|---|---|---|
| S7 | 研究者が `paper/main-jss.pdf`（24 頁）を通読し手を入れる。記録する | 研究者に頼むこと: (1) journal 版の 8 つの報告値を PDF と照合するか（すれば §5.3 の "the author has not compared them with the PDF" を直す）(2) Highlights 5 本（`paper/highlights.tex`）とキーワード 6 つを見る (3) 通読の後、生成 AI の申告に「使った後に読み、必要に応じて直した」を足してよいか |
| S8 | attack-me round 2（席は再解析と測定の妥当性・クラスタが少ないときの推論・debugging の人的要因）→ 研究者が採否 → `/cross-review` 2 巡（論文用リポジトリの差分を GSE の worktree に fetch して範囲指定・memory `reference_codex_review_other_repo`） | S7 で読んだ箇所が変われば研究者が読み直す |
| S9 | 照会の返事か未回答を RQ4 に（いまは "had not received a reply"）／ 新しいタグ ／ Zenodo の新しい版（23029603 の new version）と preprint の下書き → DOI を Data availability と README の bibtex に → 研究者が publish と JSS への投稿（推薦の査読者の欄を確かめる・候補は `survey-s2.md`）→ 原稿 ID を記録 | Highlights は投稿用の別ファイル（txt か docx）に起こす |
| 最後 | GSE 側のブランチ（`docs/references.md` の [P635]〜[P640] を含む）を PR にする | |

## §3 今回分かったこと（判断 19・20 の要点）

- モデルの版は commit の Co-Authored-By の行から: 09-06 = Opus 5、09-28 以降 = Opus 5.5、11 月の委譲 = Sonnet 5.5、9 月の委譲の版は記録なし。
- 研究者は解析のコードを読んでいない（§5.5 と §8 にそう書いた）。
- journal 版: long = "23 episodes" は本文にある。short は件数なし。committed 10・fresh 79 だと 22/89 = 24.7% で 33% と合わない（`emse/arith/*`）。
- D1 の派生表 `results/d1_episodes.csv` を入れた（Deviation 9）。metrics.json は不変。
- 題: "When “no help” is not “solved”: unconsulted shares and unaided resolution in two public debugging datasets"。
