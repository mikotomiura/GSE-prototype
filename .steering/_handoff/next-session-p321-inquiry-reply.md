# 次セッション — p321: 原著者（Alaboudi・LaToza）の照会への返事を本文に入れる

> 作成: 2026-11-22 夜（Surface）。このメモを一次資料にしない。着手するときに状態を測り直す（git・論文用リポジトリの HEAD・返事の本文）。
> 前提: round 2 と `/cross-review` 2 巡は済んだ（判断 29・30）。論文用リポジトリ `revision-jss` の HEAD は `84a9eb5`（未 push）。
> 対になる引き継ぎ: `next-session-p321-revision.md`（S9 = DOI・タグ・Zenodo・投稿）。このメモは、その §2 の順 1 を詳しくしたもの。

## §0 打ち込む用

```
git fetch origin してから MSYS_NO_PATHCONV=1 git show origin/docs/p321-emse-desk-reject:.steering/_handoff/next-session-p321-inquiry-reply.md を読んで進めてください。
worktree は C:/GSE-wt/p321-desk-reject（ブランチ docs/p321-emse-desk-reject）。タスクは .steering/20261121-p321-paper-revision/（decisions 判断 1〜30・照会の文面は inquiry-alaboudi-latoza-draft.md の「改稿」）。
論文用リポジトリは C:/self-resolution-measure のブランチ revision-jss。着手時に git status が clean で、HEAD が 84a9eb5（またはその後の自分のコミット）かを確かめる。
返事の本文は研究者がチャットに貼る（Gmail の mmiura.network 側に届く）。
```

## §1 どちらの枝か（最初に決める）

| 枝 | 条件 | すること |
|---|---|---|
| A | 返事が来た | §2 → §3 → §4 → その後 `next-session-p321-revision.md` の S9 |
| B | 2026-12-05 までに来なかった（判断 5 の目安・送信は 11-21） | 本文は変えない（RQ4 の "On 2026-11-21 we asked the original authors … at the time of submission we had not received a reply" のまま）。判断を 1 行記録して、すぐ S9 へ |
| B' | 投稿の後に返事が来た | 本文は変えない。査読の返答か改訂のときに使う。返事を記録しておく |

## §2 返事を受け取る（枝 A）

- 研究者に返事を貼ってもらい、`.steering/20261121-p321-paper-revision/inquiry-reply.md` に逐語で置く（受け取った日・差出人・どの問いに答えたか）。私信なので、論文用リポジトリ（公開）には入れない。
- 4 問のどれに答えたかを表にする。答えが一部だけでもよい（メールでも "a short answer to any one of these questions would already help" と書いた）。
- 返事が、こちらの読み違いを指摘している場合は、本文を直す前に研究者と一次（`rowData.json`・codebook・journal 版の本文）で確かめる。

## §3 問いごとの本文の置き場所

| 問い | 本文の場所 | 答えによって変わること |
|---|---|---|
| 1. consultation に数えたコード | §6.4 RQ4 の D1 の段落（"We could not determine how the journal version's figures were obtained"）・表 tab:emse・§7.5 | ルールが分かれば「原著者の答えでは X を数えた」と書く。そのルールが 4 つの定義のどれとも違うなら、5 つ目の定義を足すかは研究者が決める。足すなら `post_review` にだけ足し、NOTES.md に Deviations 14 を書く（凍結した値は変えない・`run.sh` は `ALLOW_RESULT_CHANGE=1` で 1 回だけ・既存の値の変化 0 を確かめる） |
| 2. episode の件数・committed と fresh の割り当て | §6.4 の 2 段落目（報告値どうしの算術 22/89）と make_results の `emse/arith` | 割り当てが違ったなら「算術の食い違いは割り当ての違いで説明される」と書く。make_results の検査（"do not add up"）を、答えに合わせて書き直すか外す |
| 3. コーディングの改訂 | §4.1（activities 2,136 と 2,137・2,135）・§6.4・§8 Reliability | 改訂版のコーディングが手に入るなら大きな変更になる（新しい入力・hash・再解析）。今回の投稿でやるか、次の版に回すかは研究者が決める。手に入らないなら「改訂した、ただし公開されていない」と書くだけ |
| 4. DF3 の episode のその後 | §5.4 Bounds・RQ1 の "How much of the difference rests on DF3"・§7.1・結論・要旨 | 後で解決したと分かった件があれば、範囲 [A, U] を狭められる。その件数を本文の数（`\R{}`）として出すなら make_results に入れる（手で書かない）。分からないという答えなら「原著者にも分からない」と一文足す |

共通:
- RQ4 の "at the time of submission we had not received a reply" を、返事の日付と要点に書き換える。
- 謝辞（Acknowledgements）を足す（いまは無い）。名前を出してよいかは返事の中で確かめるか、研究者が尋ねる。
- メールで "I will of course check any description with you if you wish" と約束している。原著者が確認を望んだら、本文の該当段落を研究者が送り、その返事を待ってから投稿する。望まなかったら、そのまま進めてよい。

## §4 直した後の検査

- 新しい質的な文には `make_results.py` に検査と変異を足す。要旨を触ったら語数（いま 249・上限 250）。
- `bash run.sh`（結果が変わらないこと、または意図した追加だけ）→ `TECTONIC=<path> bash paper/build.sh`。
- 変更が RQ4 の文の差し替えだけなら `/cross-review` は 1 巡（範囲は `84a9eb5..HEAD`）。定義や解析を足したら 2 巡。
- 判断を decisions.md に記録してから S9 へ。

## §5 守ること

`next-session-p321-revision.md` の §1 と同じ（日本語で答える・公開物に GSE を書かない・凍結を壊さない・数字は `\R{}`・バックスラッシュの置き換えは Edit か .py・明示のパスで add・外に出る行為は研究者が）。返事の逐語は、本人の許可なく公開物に引かない。
