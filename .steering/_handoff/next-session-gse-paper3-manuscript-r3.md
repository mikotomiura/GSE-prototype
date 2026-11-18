# 引き継ぎ —— 論文 3 の manuscript round 3（計算 (f) を本文に入れた後）

> 作成: 2026-11-18（Mac のセッション）。このメモを一次資料にしない。採否は `.steering/20261111-gse-paper3-round3-computations/decisions.md` 判断 26、結果は `experiments/20261113-null-from-shared/notes.md`。

## 0 入口の文

```
worktree /Users/johnd/GSE-prototype-paper3（枝 docs/gse-paper3-per-person-learning）で、.steering/_handoff/next-session-gse-paper3-manuscript-r3.md を読んで、論文 3 の本文に attack-me（stage manuscript・round 3・Codex 込み）を回してください。
```

## 1 今の状態

- 計算 (f)（実データの全員の共通から作った帰無）は R2: 実データの残りは検出されず、L80' は無し。帰無の平滑の効きは実データの約 2.4 倍で、帰無の残りは実データの 2〜4 倍（条件の外の所見・本文の 4.4 と限界に書いた）。
- 本文は判断 26 の直しを入れた版。要旨 249 語・本文（texcount）6,587 語・警告 0。
- round 2 の記録: `.steering/20261107-gse-paper3-per-person-learning/attack-me/manuscript-paper3/round-2/verdict.md`。round 3 は同じ階層の `round-3/` に。

## 2 round 3 で見てほしいこと

- Y2（帰無が実データの平滑を再現しない）への答えが十分か。特に帰無の行き過ぎ（約 2.4 倍）で R2 の読みが弱まらないか、4.4 と限界の書き方で足りるか。
- 本文が 6,587 語に増えた。3.5 の新しい段落と 4.4 の第 2 段落の細部を補足 S15 へ移せるか（paper-write の「簡潔に・細部は補足へ」）。
- Codex には round 2 で保留した既知の論点の一覧を添え、判定に数えないよう頼む（R2 m6 など・§3）。

## 3 既知の未決（判定に数えない）

- R2 m6: Data availability で書き手ごとの値を出さない理由（研究者に確かめる）。
- E の提案の未対応: 推奨の一般化の条件の段落・Table 3 を 3 列に・方法の細部を補足へ。
- Code availability の URL と DOI・事前の記録の公開の場所・補足 S1〜S16 の中身・Uto 2020 の評価の設計・Liu & Meng の版・記録ごとのハッシュ・残差の点検の要約の図・Table 2 の e 表記。
- `outline.md` は round 1 の頃のままで、本文と合っていない（本文が正）。

## 4 守ること

- `papers/` に GSE の名前・内部のパス・ADR や判断や条件の番号を書かない。投稿先や状態を公開物に書かない。
- 実データ・書き手ごとの値・m0 の npz は開かない。CoAuthor・CS1 の記録も値も、外部の LLM（Codex を含む）に送らない。
- push は枝だけにし、PR は出さない（[skip ci]）。返答は日本語。
