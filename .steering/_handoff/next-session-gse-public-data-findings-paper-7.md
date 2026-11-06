# 次のセッション —— 公開データの知見の論文 1: 関連研究の調べ・外枠の attack-me round 2・草稿

> 作成: 2026-11-06。worktree `/Users/johnd/GSE-prototype-public-findings`・枝 `docs/public-data-findings-paper`（push は研究者の手元・docs だけなので [skip ci]）。前の引き継ぎ `next-session-gse-public-data-findings-paper-6.md` の §2 は 1〜3 の途中まで済んだ。

## §1 状態

- OSF の 5 つ目の登録（結果と来歴）: `https://osf.io/uj6cy`（公開・添付 4 つの SHA-256 を全桁で照合済み）。notes は `experiments/20261105-findings-paper1-prefreeze/notes.md` の末尾。
- CoAuthor の探索（付録 F の残り）: 済み。H1 の型は 4 つとも精度が足りず判定できない（実効の書き手 1.5 人）・H2 の型は 2 つとも分岐 4。条件 X6・X7、門 G1・G2、/cross-review の直し（ed548609）。`experiments/20261106-findings-paper1-exploration/notes.md`。
- 外枠: 結果を入れて確定（判断 24）→ attack-me outline round 1 は major（`attack-me/outline-paper1/round-1/verdict.md`）→ 研究者の採否で直した（判断 25・commit c948d0ad）。枠組みは「同等の確認が主・評価の手順が従」、貢献 2 つ、C3 は考察へ。

## §2 やること（この順）

1. **関連研究の 3 つの柱の /literature-review**（外枠の「関連研究」の節）: (1) CS1 のプログラミングの過程からの struggle 検出、(2) 打鍵の休止の測定（流暢な打鍵との比・位置・個人化・直列と並列）、(3) 検出器の評価の方法論（指標の選び方・実用上の同等の判定 ROPE・事例対照のそろえ方・時間のリーク）。references.md にある文献は番号を挙げるだけにし、未登録の文献を探す（memory「文献のラウンドで既存の文献を入れ直さない」）。メインは検索を叩かず、/literature-review かサブエージェントの並列で。Pelánek 2015・Gardner 2018・Guo 2020・Roeser 2025・Lakens 2017 は attack-me の接地に使った文献で、論文で引くなら citation-ssot で登録する。
2. **外枠を文献の結果で埋め、attack-me outline round 2**（同じ panel・同じ接地。本文は `attack-me/outline-paper1/round-1/tmp/sources/` に残してある。round 2 の dir に写して使う）。役ごとの引き継ぎ（carryover）と、Codex に既知の未決の一覧を添える。Step 5 の基準: major なら直してもう 1 回、minor が 2 回続いたら閉じて草稿へ。
3. **草稿**（英語・MacTeX・7,000 語・補足 S1〜S9 は参考文献の後の付録）。paper-write の Step 2〜6。

## §3 気をつけること

- 凍結した文書と manifest のファイルを書き換えない。取り置きの手順は完走で止まっている（再実行しない）。
- 書き手ごとの値を repo に出さない・外部の LLM に送らない。
- `.codex/budget.json` は台帳で、未ステージのまま（巻き戻さない）。
- 推定器と gse-replay の公開の形（場所）は研究者が決める（外枠の「資源」）。
