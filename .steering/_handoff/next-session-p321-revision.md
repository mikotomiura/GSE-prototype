# 次セッション — p321 の改訂（JSS へ）の S5 後半から

> 作成: 2026-11-21（S0〜S4 と S5 の前半を終え、コンテキストが半分に近づいたので区切った）。⚠️ **このメモを一次資料にしない。** 状態は着手時に測り直す（git・照会の返事・論文用リポジトリ）。

## §0 打ち込む用

```
git fetch origin してから MSYS_NO_PATHCONV=1 git show origin/docs/p321-emse-desk-reject:.steering/_handoff/next-session-p321-revision.md を読んで、§2 の S5 後半から進めてください。
worktree は C:/GSE-wt/p321-desk-reject（ブランチ docs/p321-emse-desk-reject）。タスクは .steering/20261121-p321-paper-revision/（decisions 判断 1〜18・design.md・tasklist・survey-s2.md）。
論文用リポジトリは C:/self-resolution-measure のブランチ revision-jss（未 push・S8 まで push しない）。着手時に git status が clean で HEAD が c84c86b かを確かめる。
Tectonic は scratchpad から消えている可能性がある → 0.17.0 を GitHub のリリースから取り直し、TECTONIC=<path> bash paper/build.sh。
照会（2026-11-21 送信・待つ目安 12-05）に返事が来ているか研究者に聞く。
```

## §1 守ること（CLAUDE.md・memory から）

- 返答は日本語。★ や ⚠️ を多用しない。
- 調べものはサブエージェントへ（Sonnet の汎用・model を明示・入れ子禁止・締切）。戻りの行は使う前にメインが一次で確かめる。出版社のページは Chrome の `javascript_tool`（Skill `browser-verification` を先に読む）。有料の本文は使わない。
- 公開物には GSE への言及を入れない。学術的な英語にする。
- 凍結を壊さない: `analyze.py` が提出版の値と凍結した config をハッシュで守っている。新しい解析は `post_review_additions` と `post_review` にだけ足し、NOTES.md の Deviation 8 に追記する。`run.sh` は値が変わると止まる → 意図した追加の後だけ `ALLOW_RESULT_CHANGE=1`。
- 本文の数字は `\R{...}` だけ。新しい質的な文は `make_results.py` の `post_claims` に検査を足し、selftest に変異を 1 本足す。
- バックスラッシュを含む置き換えは heredoc や sed でやらない（今回 3 回壊れた）。Edit か、Write で作った .py で行う。
- git は明示のパスで add する。`.steering` だけの変更は push だけでよい。外に出る行為（送信・publish・投稿・公開リポジトリへの push）は研究者がするか、研究者の確認の後。

## §2 残り（tasklist の S5 後半〜S9）

| 何を | 注意 |
|---|---|
| 序論・§2: B（2 回の検索で実例 0 件 → 判断 3 のとおり「予防的な報告の推奨」に絞り、検索の範囲と 0 件を §2.5 に書く）／ F（`survey-s2.md` の 5 系統。抄録しか読んでいない → 引く前に一次を確かめる）／ L（貢献 (i) の分解は恒等式だと認める書き方） | Marwan et al. 2020 の逐語は PDF で確かめてから |
| §5.5 の LLM（E） | モデルの版・使った日付・用途ごとのプロンプト・人が確かめた範囲・文献検索の手順。⚠️ 研究者に聞く（何を通読し・手を入れたか。S7 と結びつく） |
| RQ4（G） | short 22 件の根拠・報告値どうしの算術（committed 10・fresh 79 を仮定すると約 25%・条件つきで書く・判断 12）・journal 版の値を人が照合したこと・照会（S9 で返事か未回答） |
| 要旨 | 符号（"changed the measure by only −3.5" → 絞ると +3.5 上がる）・250 語以内・新しい名前（U・A・A|R） |
| 声明 | JSS の形（competing interest・CRediT・Funding・Data availability）。生成 AI の申告の節を文献表の直前に |
| minor の残り | L256 の範囲を D1 と D2 で分ける（`all/ce` → データセットごとのキーを make_results に足す）／ L160 の合わせ込みの的と検査の区別／ 再現一式の文言（config の `_comment` "frozen BEFORE"・`analyze.py` の docstring・NOTES の "other project"・"drift"・L10） |
| K | 派生表 `results/d1_episodes.csv`（URL・名前・セッション ID なし）を実装する。§8 の倫理の節がすでに約束している |
| citation-ssot | 新しく引いた文献を GSE の `docs/references.md` に登録する |
| S6〜S9 | 題の案 2〜3 本 → 研究者 ／ Highlights（3〜5 本・85 字）とキーワード ／ S7 研究者の通読 ／ S8 attack-me round 2 と `/cross-review` 2 巡 ／ S9 タグ・Zenodo・投稿（推薦の査読者の欄を確かめる・候補は `survey-s2.md`） |

## §3 今回分かったこと（判断 13〜18 の要点）

- 照会は 2026-11-21 に研究者が mmiura.network の Gmail から送った。待つ目安は 12-05。Open Science Initiative に参加する。
- 原稿は elsarticle（12pt・A4・余白 25mm）で 22 頁。本文は `abstract.tex`・`body.tex`・`declarations.tex` に分かれている。
- 名前: U（unconsulted share）・A（unaided-resolution share）・A|R（rate among resolved units）。差は unresolved-unconsulted share・conditioning difference・denominator difference。"effect" は使わない。概念は unaided resolution。
- 追加の解析の主な値: D1 で DF3 を除くと 2.6pp・DF3 と DF5 を除くと 1.3pp・k = 7/11・CR2 の区間 [5.9, 16.6]（df 6.8）・時間で重みをつけると 19.1pp。D2 の CR2 は下限が 0 未満。P1TA を未解決に数えると table のみの値が 17.6pp。
- figshare の 2 項目は CC BY 4.0 で、どちらも非公開リンクでの共有（Chrome で一次）。
