# 次セッション — p321 の改訂（JSS へ）: round 2 の残りの minor・nit から

> 作成: 2026-11-21 夜。書き直し: 2026-11-22 夜（Surface）。このメモを一次資料にしない。着手するときに状態を測り直す（git・照会の返事・論文用リポジトリ）。
>
> 2026-11-22 にしたこと: 文献検索 B（OpenAlex）・付録・§2.5（判断 26）／ 研究者の D2 の手での数え直し（一致・判断 27）／ round 2 の重い直し（判断 28）。論文用リポジトリは `75e8e76` → `27a8ef2`（12 件・未 push）。

## §0 打ち込む用

```
git fetch origin してから MSYS_NO_PATHCONV=1 git show origin/docs/p321-emse-desk-reject:.steering/_handoff/next-session-p321-revision.md を読んで、§2 の上から進めてください。
worktree は C:/GSE-wt/p321-desk-reject（ブランチ docs/p321-emse-desk-reject）。タスクは .steering/20261121-p321-paper-revision/（decisions 判断 1〜28・tasklist の S8 の下・attack-me/manuscript-jss/round-2/verdict.md §4・search-log/）。
論文用リポジトリは C:/self-resolution-measure のブランチ revision-jss（未 push。S9 まで push しない）。着手時に git status が clean で、HEAD が 27a8ef2 かを確かめる。
Tectonic は scratchpad の C:\Users\johnd\AppData\Local\Temp\claude\bb8fe8b6e5b059fc\44c71abd-ca0b-4676-a1d8-9754bb08e6b5\scratchpad\tectonic\tectonic.exe。消えていたら GitHub のリリース（0.17.0）から取り直し、TECTONIC=<path> bash paper/build.sh で使う。
照会（2026-11-21 に送信・待つ目安は 12-05）に返事が来ているかを研究者に聞く。
```

## §1 守ること（CLAUDE.md と memory から）

- 返答は日本語で書く（2026-11-22 にも英語で答えてしまい、指摘された）。★ や ⚠️ を多用しない。
- 調べものはサブエージェントへ出す（model を明示・入れ子は禁止・締切を書く）。戻ってきた行は、使う前にメインが一次で確かめる。有料の本文は使わない。
- 公開物には GSE への言及を入れない。学術的な英語で書く。
- 凍結を壊さない。新しい解析は `post_review` にだけ足し、NOTES.md の Deviations に追記する（いまは 13 まで）。`run.sh` は値が変わると止まる → 意図した追加の後だけ `ALLOW_RESULT_CHANGE=1` を付け、既存の値の変化が 0 であることを比べて確かめる。
- 本文の数字は `\R{...}` だけで出す。新しい質的な文には、`make_results.py` に検査と変異を足す。他の論文から引いた数で計算した値も `make_results.py` で出す（Hellas の 52.5% がその例）。
- バックスラッシュを含む置き換えは、heredoc でも sed でもやらない（2026-11-22 に sed で `\R` の `\` が落ちた。`check_frontmatter.py` がいまは止める）。Edit か、Write で作った .py を使う。`python -I` は `PYTHONIOENCODING` を無視する → 印字は `sys.stdout.reconfigure(encoding='utf-8')`。
- git は明示のパスで add する。論文用リポジトリのコミットにも Co-Authored-By と Claude-Session の行を付ける（それまでのコミットと揃える）。外に出る行為は、研究者がするか、研究者の確認の後にする。

## §2 残り

| 順 | 何を | 注意 |
|---|---|---|
| 1 | round 2 の minor・nit の残り（下の §2a） | 直したら build・`make_results --selftest`・`check_frontmatter` |
| 2 | `/cross-review` 2 巡（1 巡目 = 文書の中と文書どうしの矛盾、2 巡目 = 足した規則の境界条件） | 論文用リポジトリの差分は `75e8e76..HEAD`。GSE の worktree に fetch して、ラッパーを範囲を限って呼ぶ（memory: Codex review of another repo・cross-review は 2 巡）。予算の台帳は origin/main のものも見る |
| 3 | S9: 照会の結果を RQ4 に ／ README の引用と Data availability の DOI を新しい版に ／ タグ ／ Zenodo の新しい版 ／ 投稿 ／ GSE 側の PR | `survey-s2.md` に推薦の査読者の候補がある。DOI `10.5281/zenodo.23029603` は旧い版を指している |
| 任意 | 文献検索 B の NOT-READ のうち機関リポジトリの 4 件（K53・K59・K61・K143）をブラウザで読む | 読んだら `supplement/literature-search/keyword-hits.tsv` を直し、§2.5 の数は make_results が追う |
| 任意 | round 3 | 回すなら context-B に判断 24〜28 を入れる（round 2 で監査役の偽陽性 2 件の原因になった） |

## §2a round 2 の残り（verdict.md §4 の minor・nit のうち、まだ手を付けていないもの）

- Highlight 4 と Highlight 2 の限定（観察した単位の中・D2 は打ち切りだけで成り立つこと）。
- κ が何の一致かを書く。単一コーダーの限界を Consultation の段落にも書く。
- 表 1 の "formative" の語。help の範囲（AI・同僚・事前の知識）は表 1 の caption に書いた。足りるかを見る。
- 派生表（`results/d1_episodes.csv`）を読むスクリプトがあるか、「手で」読むのかを書く。
- 序論の "with one command"。
- 古い言い方の残り: `sec:related` の参照（body 10 行あたり）・"resolved without help"・"effect"（FORBIDDEN の語に注意）・README の旧い名前。
- §8 の "direction"。"doubles" の断定。
- 要旨の D2 と、持ち帰りの 3 つ目（道具を評価する人）。道具を評価する人への提言（§7.4）を厚くする。
- 倫理: "agreed to be observed" は直した（`abd08f7`）。D1・D2 の倫理審査や同意を本文がどう書いているかは見ていない。
- nit: 表 3（tab:minimal）の duration の行・"Its complement"・"every definition" の範囲・pp と % の使い分け・所属の書き方。

## §3 2026-11-22 に分かったこと・決めたこと（判断 26〜28）

- 文献検索 B: 171 件から INSTANCE 1 件（Sychev 2022・CS1 の小テスト）。研究者の決定で INSTANCE として数えた（基準は動かさない）。要旨は "Our searches found one published instance, outside debugging." 引用している側の 70 件は INSTANCE 0 件。
- D2 の手での数え直し: 研究者の数（表 5 だけ a=9 b=2 ／ 表 5 と本文 a=8 b=1）がコードと一致した。
- D2 で 4 件すべてを打ち切りにすると、差は 0。D2 の差は、観察が終わった時点でまだ開いていた件だけでできている。
- CV3 は CR2-BM とほぼ同じ（D1 [6.2, 16.2]）。WCR は足していない。
- Beller 2018 は ICSE '18 の本会議（OpenAlex の Companion という表示は誤り。Crossref で確かめた）。
- 頁数 28・要旨 246 語（上限 250）。
