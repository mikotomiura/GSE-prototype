# 引き継ぎ —— 論文 3 の本文に manuscript round 4 の直しを入れ、round 5 を回す

> 作成: 2026-11-19（Mac のセッション）。このメモを一次資料にしない。採否は `.steering/20261111-gse-paper3-round3-computations/decisions.md` 判断 30。

## 0 入口の文

```
worktree /Users/johnd/GSE-prototype-paper3（枝 docs/gse-paper3-per-person-learning）で、.steering/_handoff/next-session-gse-paper3-manuscript-round4-fixes.md を読んで、論文 3 の本文に manuscript round 4 の直し（判断 30）を入れてください。
```

## 1 今の状態
- round 4 の判定は major（推移 major ×4）。記録は `.steering/20261107-gse-paper3-per-person-learning/attack-me/manuscript-paper3/round-4/verdict.md`（直す順は §5、問いは §7）。対象は d6587f21・本文 6,939 語・要旨 250 語。
- 研究者が決めたこと（判断 30）: A 決定を固定の平滑に限り推奨 (2) の版と並べ、費用の文を失う精度の文に替え、発見を考察の冒頭と結論に戻す／B 2 つ目の帰無の植えた差の下での振る舞いを 4.5 に 1〜2 文／C 要旨の推奨に範囲の語。直した後に round 5。

## 2 やること
1. verdict §5 の書き方の直し 1〜11 を研究者に見せて承認を取る（判断 30 では問うていない）。
2. paper-write（本線の版）の手順で直す。足す文には同じ節で削る文を添える（Y4 の但し書きの繰り返しを削って語を空ける）。要旨は 250 語を超えない。
3. 値の出どころ: 両側の当て直しの τ は `experiments/20261112-selection-split-and-smoothing/notes.md` 65 行（全員格子の中・∞ は 0 人。τ の値と重みの換算は notes に無いので、summary.json の集計で確かめる。書き手ごとの pickle は開かない）。誤警報率 FA' = 0 は `experiments/20261113-null-from-shared/notes.md` 28〜33 行。
4. 言い換えた後の点検（paper-write Step 3b）を `paper-write/rewording-check-r4.md` に。数値は独立に照合する（判断 28 と同じ）。
5. round 5 は本線の attack-me で、round 4 の dir を土台に。Codex には既知の未決の一覧（round 4 の codex-input の 1〜20）に判断 30 の保留を足して添える。round 4 の Codex は 42,536 tokens（1 回の上限 30,000 を超える）。

## 3 守ること
- `papers/` に GSE の名前・内部のパス・ADR や判断や条件の番号を書かない。投稿先や状態を公開物に書かない。
- 実データ・書き手ごとの値・m0 の npz は開かない。CoAuthor・CS1 の記録も値も外部の LLM（Codex を含む）に送らない。
- push は枝だけにし、PR は出さない（[skip ci]）。返答は日本語。
