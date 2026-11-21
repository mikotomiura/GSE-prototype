# 次セッション — p321 の改訂（JSS へ）の S1 から

> 作成: 2026-11-21（S0 を終えたところで区切った）。⚠️ **このメモを一次資料にしない。** 状態は着手時に測り直す（git・照会を送ったか・論文用リポジトリ）。

## §0 打ち込む用

```
git fetch origin してから MSYS_NO_PATHCONV=1 git show origin/docs/p321-emse-desk-reject:.steering/_handoff/next-session-p321-revision.md を読んで、§2 の S1 から進めてください。
worktree は C:/GSE-wt/p321-desk-reject（ブランチ docs/p321-emse-desk-reject）。タスクは .steering/20261121-p321-paper-revision/（requirement・decisions 判断 1〜12・design.md（ハイブリッド）・tasklist）。
着手時にまず確かめる: (1) 研究者が原著者への照会を送ったか・その日付（S0c。送っていれば decisions に記録する） (2) 論文用リポジトリ C:/self-resolution-measure の git status が clean で、main が 728e81c か。
```

## §1 守ること（CLAUDE.md・memory から）

- 返答は日本語。★ や ⚠️ を多用しない。
- 調べもの（文献・規程・ウェブ横断）はサブエージェントへ。Sonnet の汎用エージェントは model を明示し、入れ子を禁止し、締切を書く（Skill `subagent-delegation`）。判断の根拠にする行は、戻ってきた後にメインが一次で確かめる。出版社のページは WebFetch では 403 になるので、Chrome の `javascript_tool` で読む（Skill `browser-verification` を先に読む）。
- 有料の本文は使わない。無料の版は OpenAlex と Google Scholar の「すべての版」で探す（journal 版は NSF PAR で読めた）。
- 公開物（論文用リポジトリ・Zenodo）には GSE への言及を入れない。学術的な英語にする。
- 凍結を壊さない: 既存の `results/metrics.json` のキーと値は変えない。足すのは新しいキーだけにし、`NOTES.md` に post hoc と記録する。
- git は明示のパスで add する（`-A` は禁止）。`.steering` だけの変更は push だけでよい（PR 不要）。論文用リポジトリの変更は作業ブランチ `revision-jss` で行う。
- 外に出る行為（メールの送信・Zenodo の publish・投稿）は研究者がする。

## §2 残りの段（design.md §3）

| 段 | 何を | 注意 |
|---|---|---|
| S0c | 研究者が照会を送る（`inquiry-alaboudi-latoza-draft.md`）→ 日付を記録 | 2 週間を待つ目安にする。返事を待たずに S1〜S8 を進める |
| S1 | `main.tex` → `body.tex` ＋ `main-jss.tex`（elsarticle・1 段組・author-year）。本文の差分 0。`build.sh` の Springer の zip とハッシュの検査を elsarticle に替える。36 頁未満を確かめる。JSS の投稿画面に推薦の査読者の欄があるかを確かめる（研究者に聞く）。Open Science Initiative に参加するかを研究者に聞く | elsarticle は Tectonic が CTAN から取れる見込み（未確認） |
| S2 | 並列のサブエージェント 3 本: B（誤読の実例の検索。先に手順を decisions に書く）／ H（クラスタが少ないときの区間。「役に立たない」も選べるようにする）／ F（先行研究の系統） | 戻りは一次で裏取りする |
| S3 | 補助解析を追加だけで足す（A の感度 3 通りと [R0′, R0]・k・DF3 の位置・M・I・H）。「DF3 を除く」と「DF3 を解決に数え直す」は名前を分ける。K（figshare のライセンスを Chrome で確かめ、URL・名前を除いた派生表） | 旧い値の不変を自己検査に足す |
| S4〜S9 | 名前の辞書 → 本文 → 題・要旨・Highlights → 研究者の通読 → attack-me round 2 と `/cross-review` 2 巡 → タグ・Zenodo・投稿 | design.md §3 |

## §3 S0 で分かったこと（判断 12）

- journal 版の本文は、committed・fresh の件数を書いていない。v1 は 10・79 と書いている。journal 版の「committed の半分は修正に至らなかった」は 10 件中 5 件と合う。→ 原稿の「33% と 24.7% が合わない」は、「v1 の件数を仮定すると」という条件つきで書く。
- JSS も「査読の依頼が 20 件に届くと範囲外とみなして不採択」（arXiv 2601.19217v2 の逐語）。題・要旨・キーワードで分野を明確にし、推薦の査読者を用意する。
