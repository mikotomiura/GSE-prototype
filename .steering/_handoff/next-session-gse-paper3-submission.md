# 引き継ぎ —— 論文 3 を投稿する準備（PDF・ESM_1・カバーレター・投稿画面の項目・校正刷り）

> 作成: 2026-11-20。このメモは入口で一次ではない。決まったことは `.steering/20261111-gse-paper3-round3-computations/decisions.md` 判断 46 と `.steering/20261120-gse-paper3-public-repo/decisions.md` 判断 1〜7。

## 0. 入口の文
```
worktree /Users/johnd/GSE-prototype-paper3（枝 docs/gse-paper3-per-person-learning）で、.steering/_handoff/next-session-gse-paper3-submission.md を読んで、論文 3 の投稿の準備をしてください。
```

## 1. 今の状態（2026-11-20）
- 投稿前の未決 1〜7 は閉じた（判断 46）。原稿は Springer Nature の様式（sn-jnl・sn-basic）で `papers/per-person-learning/manuscript/`（main.tex・supplement.tex）。
- 公開 repo は公開済み: GitHub mikotomiura/per-person-keystroke-models（v1.0.0）・Zenodo 10.5281/zenodo.24395569。本文の Code availability に URL と DOI が入っている（変更不要）。公開物には投稿先と状態を書いていない（補足の \journalline は公開の写しだけ空。GSE の原本には誌名が入っている）。
- GSE の枝の未 push のコミット: b14da6d1（kit の README）・74be2248（公開 repo の記録）。push は研究者に確かめる。

## 2. やること
1. 規程を一次で読み直す（UMUAI の Submission guidelines・Editorial Manager の項目。判断 46 の未決 1 の逐語の要点を出発点に、変わっていないかを Chrome で確かめる）。カバーレターの要否、要旨 150〜250 語・キーワード 4〜6、補足は "Online Resource"・連番のファイル名（ESM_1.pdf）・各ファイルに題・誌名・著者・連絡先、LLM の利用は Methods に記載、LaTeX は source と PDF を出す。
2. 本文と補足を組み直す（誤り 0・未定義の参照 0・overfull を数える）。補足の PDF を ESM_1.pdf の名前に。source の zip（main.tex・references.bib・sn-jnl.cls・sn-basic.bst・figdata/）を作り、zip だけから組めることを確かめる。
3. 要旨の語数・キーワードの数を数え直す。宣言（Funding・Competing interests・Ethics・Consent・Data/Code availability・Use of AI tools）が規程の項目と合うかを確かめる。
4. カバーレター（要るなら）を書く。研究者の確認を受ける。投稿画面に貼る文（題・要旨・キーワード・著者・所属 Independent Researcher, Hiroshima, Japan・ORCID）を 1 枚にまとめる。
5. 投稿は研究者が Editorial Manager で行う。Submit の前に、合成された校正刷り（proof）の全頁、特に補足の部分を研究者に見てもらう（memory: feedback-check-proof-before-submit）。CSV などの機械向けのファイルは上げない（DOI で示す）。

## 3. 注意
- 新しい値や文献を足さない（照合は済んでいる。直すなら数値の照合をやり直す）。
- 投稿先は目的から選んだ（memory: feedback-venue-by-purpose）。変える話になったら研究者に聞く。
- 投稿後は、受付番号と日付を memory と作業記録に書き、返事を待つ引き継ぎを作る。
