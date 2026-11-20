# 引き継ぎ —— 論文 3 を Springer Nature の様式（sn-jnl）へ移す

> 作成: 2026-11-20。このメモを一次資料にしない。採否は `.steering/20261111-gse-paper3-round3-computations/decisions.md` 判断 45、作業記録は `.steering/20261120-gse-paper3-supplement/`、分量は `.steering/20261107-gse-paper3-per-person-learning/paper-write/length-log.md`。

## 入口の文
```
worktree /Users/johnd/GSE-prototype-paper3（枝 docs/gse-paper3-per-person-learning）で、.steering/_handoff/next-session-gse-paper3-springer-template.md を読んで、論文 3 の本文と補足を Springer Nature の様式へ移してください。
```

## 今の状態（167cbd47）
- 本文 main.tex: 序論〜結論 6,916 語（予算 6,800）・要旨 249 語（上限 250）・17 頁。補足 supplement.tex（Online Resource S1〜S13・14 頁・本文の初出の順）。どちらも組んで警告 0（本文に 3 pt の overfull が 4.4 の見出しに 1 つ）。
- AI の利用の宣言を Statements に 1 文足した（研究者の選択）。

## やること
1. sn-jnl の様式は投稿規程の原文から取る（記憶で決めない・paper-write Step 0 の作法）。移した後に要旨の語数（250 以下）・本文の語数・頁を測り直し、length-log に書く。
2. 補足の置き場（1 つの PDF で Online Resource と呼ぶか）を規程で確かめる。
3. 残る未決: Code availability の URL と DOI・記録ごとのハッシュ・Uto 2020 の評価の設計（本文は触れない）・Liu & Meng の雑誌版の文言・Data availability の理由。検索語と選別の数は記録に残っていない（S1 にそう書いた）。

## 守ること
- papers/ に GSE の名前・内部のパス・判断の番号を書かない。投稿先や状態を公開物に書かない。
- 実データ・書き手ごとの値は開かない。CoAuthor の記録も値も Codex に送らない。
- push は枝だけ・PR は出さない（[skip ci]）。worktree の .codex/budget.json はコミットしない。
