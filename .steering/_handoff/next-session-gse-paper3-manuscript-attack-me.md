# 引き継ぎ —— 論文 3 の本文の草稿 1 版に attack-me（stage manuscript）を回す

> 作成: 2026-11-11（Mac のセッション）。このメモを一次資料にしない。本文は `papers/per-person-learning/manuscript/main.tex`（eff4bc93）、外枠は同じ dir の `outline.md`、判断は `.steering/20261111-gse-paper3-round3-computations/decisions.md`（判断 14・15）、外枠の査読の記録は `.steering/20261107-gse-paper3-per-person-learning/attack-me/outline-paper3/round-1〜7/`。

## 0 入口の文

```
worktree /Users/johnd/GSE-prototype-paper3（枝 docs/gse-paper3-per-person-learning）で、.steering/_handoff/next-session-gse-paper3-manuscript-attack-me.md を読んで、論文 3 の本文の草稿に attack-me（stage manuscript・Codex を加える）を回してください。決めることは AskUserQuestion で 1 問ずつ、推奨と理由を添えて日本語で聞いてください。
```

## 1 いまの状態（2026-11-11）

- 本文の草稿 1 版: article クラス・natbib（投稿前に Springer Nature の様式へ移す）。序論〜結論は約 4,400 語（予算 6,800 語・`paper-write/length-log.md`）。結果（947 語・予算 2,500）と考察（491 語・予算 1,000）は薄い。図表は Table 1・Figure 1・Figure 2・Table 2 の 4 つ。`latexmk -pdf main.tex` で組める（警告 0）。
- 数は一次（第 3 段の tables.md・summary.json、最頻値の試験・目的と休止・感度・平滑なしの notes）とサブエージェント（Opus）が独立に照らし、7 件の食い違いを直した（学習の単位は「評価の直前の k 単位」、P30 の k = 30 の区間 [−2.2e−3, 3.7e−3]、重みの「at most 1%」は 15-session のパネルに限る、など）。
- 補足資料（S1〜S15）は未作成。本文は Online Resource S1〜S15 を参照している。
- 枝は eff4bc93 まで push 済み。この引き継ぎのコミットは push していない。

## 2 attack-me に添える「既知の未決」（Codex と査読者役に判定に数えないよう頼む）

1. 補足資料 S1〜S15 が未作成（本文の参照先が無い）。
2. Uto et al. 2020 の評価の設計は未確認（出版版は有料・UEC のリポジトリは 2026-10-28 から保守で停止）。新規性の文は Uto の評価に触れない。投稿前に再び試す。
3. Liu & Meng は 2016 年の雑誌版を引き、文言は arXiv 1510.08539v1 で確かめた（雑誌版の文言は未照合）。
4. 元の記号列の記録ごとのハッシュは未公開（別の引き継ぎ `next-session-gse-paper3-record-hashes.md`）。限界に 1 文ある。
5. Springer Nature の様式・プレプリントの方針・補足の番号の振り直しは投稿前の作業。
6. 外枠の round 7 の verdict §9 の「残す」に挙げたもの（同じ dir の verdict.md）。

## 3 回し方の注意

- `attack-me` Skill の stage manuscript。編集者の役 E は本文だけを読む。Codex を加える（本文の tex だけを渡す。results・notes・pickle・記号は渡さない）。wrapper は本線から回す（台帳は本線の `.codex/budget.json`・2026-11-11 は 291,097 / 2,400,000）。
- 外枠の round 1〜7 は全部 major（6・7 は R1〜R3 が minor で、E の判定）。推移を数え、minor が続いたら閉じて次の段を勧める（memory「attack-me は判定の推移を見てから回す」）。
- 直すときは足すより移す（paper-write Step 4）。結果と考察は予算に余りがあるので、外枠の 4.x と 5 の計画のうち書いていないもの（4 項目の「なぜ大事か」・推奨の根拠の節）を足してよい。

## 4 守ること

- 実データ・書き手ごとの値・pickle・npz・NDJSON を開かない。外部の LLM に打鍵の内容・書き手ごとの値を送らない。
- `papers/` に GSE の名前・内部のパス・ADR や判断や条件の番号を書かない。
- push と PR は研究者に確かめてから（PR は出さない方針・[skip ci]）。
- 返答は日本語。絵文字と記号を多用しない。報告を地の文の問いで終えない。
