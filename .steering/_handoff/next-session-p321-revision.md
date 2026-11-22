# 次セッション — p321 の改訂（JSS へ）: S9（投稿の準備）から

> 作成: 2026-11-21 夜。書き直し: 2026-11-22 夜（2 回目・Surface）。このメモを一次資料にしない。着手するときに状態を測り直す（git・照会の返事・論文用リポジトリ）。
>
> 2026-11-22 夜にしたこと: round 2 の残りの minor・nit（判断 29）／ 所属を Independent researcher に・`/cross-review` 2 巡・要旨の 1 文に限定（判断 30）。論文用リポジトリは `27a8ef2` → `84a9eb5`（6 件・未 push）。

## §0 打ち込む用

```
git fetch origin してから MSYS_NO_PATHCONV=1 git show origin/docs/p321-emse-desk-reject:.steering/_handoff/next-session-p321-revision.md を読んで、§2 の上から進めてください。
worktree は C:/GSE-wt/p321-desk-reject（ブランチ docs/p321-emse-desk-reject）。タスクは .steering/20261121-p321-paper-revision/（decisions 判断 1〜30・tasklist の S9）。
論文用リポジトリは C:/self-resolution-measure のブランチ revision-jss（未 push。S9 まで push しない）。着手時に git status が clean で、HEAD が 84a9eb5 かを確かめる。
Tectonic は scratchpad の C:\Users\johnd\AppData\Local\Temp\claude\bb8fe8b6e5b059fc\44c71abd-ca0b-4676-a1d8-9754bb08e6b5\scratchpad\tectonic\tectonic.exe。消えていたら GitHub のリリース（0.17.0）から取り直し、TECTONIC=<path> bash paper/build.sh で使う。
照会（2026-11-21 に送信・待つ目安は 12-05）に返事が来ているかを研究者に聞く（11-22 夜の時点では来ていない）。
```

## §1 守ること（CLAUDE.md と memory から）

- 返答は日本語で書く。★ や ⚠️ を多用しない。
- 調べものはサブエージェントへ出す（model を明示・入れ子は禁止・締切を書く）。戻ってきた行は、使う前にメインが一次で確かめる。有料の本文は使わない。
- 公開物には GSE への言及を入れない。学術的な英語で書く。
- 凍結を壊さない。新しい解析は `post_review` にだけ足し、NOTES.md の Deviations に追記する（いまは 13 まで）。`run.sh` は値が変わると止まる → 意図した追加の後だけ `ALLOW_RESULT_CHANGE=1`。
- 本文の数字は `\R{...}` だけで出す。新しい質的な文には、`make_results.py` に検査と変異を足す。
- バックスラッシュを含む置き換えは heredoc や sed でやらない。Edit か、Write で作った .py を使う。
- git は明示のパスで add する。論文用リポジトリのコミットにも Co-Authored-By と Claude-Session の行を付ける。外に出る行為（push・タグ・Zenodo の publish・投稿）は、研究者がするか、研究者の確認の後にする。

## §2 残り（S9）

| 順 | 何を | 注意 |
|---|---|---|
| 1 | 照会の結果を RQ4 に（返事が無ければ今の文 "at the time of submission we had not received a reply" のまま） | 返事が来たら §6.3 の RQ4 の段落と §8 も見る |
| 2 | README の引用（題が旧い: "outcome-agnostic self-resolution measures"）と Data availability の DOI（`10.5281/zenodo.23029603` は旧い版）を新しい版に | 版の DOI（concept DOI でない）。Zenodo の下書きで DOI を予約してから本文に入れる（memory: Zenodo token・下書きは自動で可、publish は都度確認） |
| 3 | タグ → push（研究者）→ Zenodo の新しい版 → 研究者が publish | 出力はファイルに保存して 1 回だけ（memory: Capture output of state-changing calls） |
| 4 | JSS への投稿（研究者）→ 原稿 ID を記録 → GSE 側の PR | `survey-s2.md` に推薦の査読者の候補 |
| 任意 | 文献検索 B の NOT-READ のうち機関リポジトリの 4 件（K53・K59・K61・K143）をブラウザで読む | 読んだら `keyword-hits.tsv` を直す。§2.5 の数は make_results が追う |

## §3 2026-11-22 夜に分かったこと・決めたこと（判断 29・30）

- 所属は "Independent researcher, Hiroshima, Japan"（研究者の決定）。
- D2 の未解決の 4 件は、原典が各タスクの終わり方を書いていない（配信者は諦めても終わる）。本文は「study period の中で解決しなかった」とだけ書く。
- 要旨の実例の文は "Our searches found one published instance, outside debugging, reading unrecorded help as no help."（研究者の選択）。249 語で、余裕は 1 語。
- 派生表 `results/d1_episodes.csv` は make_results が数えて 8 つの 2×2 表と照合する（値の形も検査する）。
- 頁数 29（上限 35）。Codex の消費は 2026-11-22 に 100,803 / 2 回（ブランチの台帳）。
