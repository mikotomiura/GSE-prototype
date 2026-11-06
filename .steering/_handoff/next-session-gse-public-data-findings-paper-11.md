# 次のセッション —— 公開データの知見の論文 1: 草稿 v3 の後（公開物・round 3 の要否）

> 作成: 2026-11-06。worktree `/Users/johnd/GSE-prototype-public-findings`・枝 `docs/public-data-findings-paper`（push は研究者の手元・docs だけなので [skip ci]）。前の引き継ぎ `next-session-gse-public-data-findings-paper-10.md` の §2 の 1〜4 は済んだ。

## §1 状態

- 探索 X10〜X15: 済み（条件 e1ad4b99・bc9908a7 → 結果 630804e0・9fbb4739・02463420）。値は `experiments/20261106-findings-paper1-exploration/notes.md`。
- 草稿 v3: `papers/public-data-findings/manuscript/`（b8576a4b・本文 7,384 語・要旨 300 語・29 頁）。補足 S3 に推定器の全係数。
- attack-me（manuscript）round 2: major（`attack-me/manuscript-paper1/round-2/verdict.md`・6ce13027）。研究者の採否は判断 36。v3 はその直し。
- 公開（判断 35・36）: 置き場は GitHub の公開 repo＋Zenodo（作成と公開は押す前に研究者に確かめる）。推定の行と取り置きの id の一覧は CS1 の約束（再配布しない・公開は集計値だけ）のため出さず、著者に問い合わせる。下書き `.steering/20261105-public-data-findings-paper/cs1-author-request-draft.md`（研究者が Chrome で送る）。

## §2 やること（研究者に順を確かめてから）

1. 著者への問い合わせ（研究者）。返事で推定の行・id の一覧の扱いを決め、考察の Materials と限界を直す。
2. 推定器と replay の道具の公開の可否（未決・R1〜R3・E の 4/4）。公開できないなら、補足 S3 の係数だけから独立に再実装し、見た書き手の保存の行と一致することを示す案（R2・R3）。
3. 公開 repo の中身（評価と探索のコード・変換・係数の表・README〔図と日本語版〕）を repo の外に組み、研究者の OK の後に GitHub と Zenodo へ。要旨の置き字を DOI に。
4. attack-me round 3 を回すか（推移は major 2 回。止め手は E と公開）。回すなら同じ panel・Codex あり・既知の未決は round 2 の tmp/codex-input.md の 18 件を組み直す。

## §3 気をつけること

- 凍結した文書と manifest を書き換えない。推定器の係数を「学んだ」と書かない。書き手ごとの値を repo に出さない・外部の LLM に送らない。
- 外枠 v6（outline.md）は書き換えない（草稿が新しい版）。抄録の 3 句を外した理由は判断 36 の「採らなかったもの」。
- `.codex/budget.json` は台帳で未ステージのまま（巻き戻さない）。
