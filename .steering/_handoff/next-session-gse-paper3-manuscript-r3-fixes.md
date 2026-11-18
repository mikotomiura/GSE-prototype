# 引き継ぎ —— 論文 3 の本文に manuscript round 3 の直しを入れる

> 作成: 2026-11-19（Mac のセッション）。このメモを一次資料にしない。採否は `.steering/20261111-gse-paper3-round3-computations/decisions.md` 判断 27、指摘と直す順は `.steering/20261107-gse-paper3-per-person-learning/attack-me/manuscript-paper3/round-3/verdict.md` §5。

## 0 入口の文

```
worktree /Users/johnd/GSE-prototype-paper3（枝 docs/gse-paper3-per-person-learning）で、.steering/_handoff/next-session-gse-paper3-manuscript-r3-fixes.md を読んで、論文 3 の本文に round 3 の直し（判断 27）を入れてください。
```

## 1 今の状態

- round 3 の判定は major（判定の推移 major → major → major）。重い指摘はすべて書き方で直せる（新しい計算は要らない。最頻値の値と比は保存済みの集計と本文の値から書ける）。
- 本文は c68dfc30 の版で 6,739 語（`texcount -inc -sub=section main.tex` の序論〜結論の text+headers+captions の和）。要旨 249 語。
- ⚠️ worktree の `.claude/skills/{attack-me,paper-write}` は古い（枝が 2026-11-18 の改訂 ef5e25aa・36f9952b の前に分かれた）。手順は本線の版で読む: `git -C /Users/johnd/GSE-prototype show origin/main:.claude/skills/paper-write/SKILL.md`（特に Step 0 の想定読者・Step 3b）。

## 2 やること（判断 27 の順）

1. verdict §5 の 1〜9（要旨と結論で 2 つの値を分ける・比の 1 文・「2 桁以上」「small」の限定・推奨を 2 つに分ける・帰無の作りの 1 句ずつ・本人側の割合の注意・語の統一と定義・細部を S15 へ・その他）。
2. 最頻値との比べを 4.4（入れ替え後の位置）に 1 文。108 行と 146 行の食い違いを整える。
3. 4.5 と 4.4 の順を入れ替える。最初の帰無は 2 文、2 つ目の帰無の作り方と細部は S15 へ、要旨では 1 句。
4. 方法の具体例の図（作った数・方法の節の冒頭）。実在の人の値を使わない。図の軸・凡例は本文の語で。組んだ後に目で見る。
5. 結論を「重ならない窓での逆転」と「使う側の決定」に絞る。考察の第 1 段落に決定の 2〜3 文、Relation に Uto 型との関係。
6. paper-write Step 3b の「言い換えた後の点検」を言い換えた文の全部に当て、結果を `.steering/20261107-gse-paper3-per-person-learning/paper-write/` に 1 行ずつ。
7. 語数を測り `length-log.md` に追記（測り方は上と同じ）。組んで警告 0 を確かめる。
8. 数値の独立の照合（判断 22 の形）をしてから、round 4 を回すかを attack-me の Step 5 で研究者に問う。

## 3 既知の未決（round 4 でも判定に数えない）

round 3 の context-A の「著者が把握している未決」1〜9 と同じ。ほかに Codex の 3（閾が 5 種の最大であることの不確かさ）は 1 句で書く方針（verdict §5 の 5）。

## 4 守ること

- `papers/` に GSE の名前・内部のパス・ADR や判断や条件の番号を書かない。投稿先や状態を公開物に書かない。
- 実データ・書き手ごとの値・m0 の npz は開かない。CoAuthor・CS1 の記録も値も外部の LLM（Codex を含む）に送らない。
- push は枝だけにし、PR は出さない（[skip ci]）。返答は日本語。
