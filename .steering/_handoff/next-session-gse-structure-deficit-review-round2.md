# 引き継ぎ —— 構造の足りなさの試験：notes のレビュー 2 巡目と、PR の前まで（Mac）

> 作成: 2026-11-10（Mac のセッション）。このメモを一次資料にしない。条件は `experiments/20261107-structure-deficit-test/conditions.md`、判断は `.steering/20261107-gse-structure-deficit-test/decisions.md`（判断 1〜13）、結果は `experiments/20261107-structure-deficit-test/notes.md` と `tables.md`。前の引き継ぎは `next-session-gse-structure-deficit-after-run.md`（§2 の門・§4 の但し書き・§7 の守ること はそのまま生きている）。

## 0 入口の文（Mac の Claude Code に打ち込む）

```
.steering/_handoff/next-session-gse-structure-deficit-review-round2.md を読み、structure-deficit-test の notes に残っているレビューの指摘 4 件を直して、/cross-review（Codex も加える）の 2 巡目を通してください。push と PR は私が確かめてから。
```

作業は worktree `/Users/johnd/GSE-prototype-structure-deficit`（枝 `exp/gse-structure-deficit-test`）。

## 1 最初に確かめること

1. **同じ worktree を別のセッションが触っていないか。** 2026-11-10 の 01 時台に、2 つのセッションが同時にこの worktree で notes を直していた（1 つは notes を書いて `9d4edcba` まで進め、もう 1 つはレビューを回しただけで notes に手を入れずに止まった）。`git -C /Users/johnd/GSE-prototype-structure-deficit log --format='%h %ad %s' --date=iso -5` と `git -C … status -s` を見る。HEAD が `9d4edcba` より先に進んでいたら、その先のコミットを読み、下の 4 件がもう直っていないかを照らしてから始める。他のセッションがまだ動いているか分からなければ研究者に聞く。
2. `git -C /Users/johnd/GSE-prototype-structure-deficit fetch origin` の後、`HEAD..origin/exp/gse-structure-deficit-test` に新しいコミットが無いこと（この時点で Mac は origin より先にいる・push していない）。

## 2 ここまでに済んだこと（2026-11-10）

- 前の引き継ぎ §2 の門は全部通った（run_id 3 ファイル一致・`git diff eb8bdfd9 48137cbe` の 5 パスは空・dirty なし・manifest sha 一致・Python 3.11.9／numpy 2.4.4／JOBS 16・manifest 0/0・P-D1 不一致 0・selftest 19 対照緑・変異 16 個すべて hit・P-Q 外れ 0・P-REPRO tau 6,741／mli 1,363 の葉で外れ 0・6 組 × 2 データ・NaN なし・結果のコミットは results/ と §7 だけ）。
- `python3 -I scripts/report.py results/summary.json <別の場所>` の出力は、コミット済みの `tables.md` と同じだった。
- notes: 骨組み `f6d554bd`（値の前）→ 本文 `667bf2ce` → 1 巡目のレビューの直し `9d4edcba`（判断 13）。形の判定は CoAuthor の主のセル 3 つが形 B、CS1 C5 k = 5 が形 C。これは D5 と判断 11 と forms.py のとおりで、2 つのレビューとも誤りを指摘していない。
- 1 巡目のレビューは 2 系統あった。
  - (a) notes を書いたセッションのレビュー: 判断 13 に記録済み（Codex 32,379 tokens）。
  - (b) もう 1 つのセッションのレビュー: 範囲 `cb571b11..667bf2ce`。code-reviewer は HIGH なし。Codex は P2 が 3 件。Codex の 2 回目（約 32,361 tokens）は `.codex/budget.json` に記帳されたが**未コミット**（today 2026-11-10・64,740／2 回）。
- (b) の指摘の多くは `9d4edcba` で直っていた。残りが下の §3 の 4 件。

## 3 残りの指摘（9d4edcba の notes.md の行番号）

1. **142 行（Codex P2）**: 「G_p が残った分がどちらによるかは、この試験では分けられない」。並べ替えで消した 2 つ（1 次の依存とゆっくりした頻度の変化）を、残った分の原因の候補に挙げており、筋が通らない。
   - 直し方の案: 「並べ替えで減った分が、1 次の依存とゆっくりした変化のどちらによるかは分けられない。残った分（G_p）の出どころも、この試験では分からない。」
2. **84 行（code-reviewer）**: 「τ 他人で選ばれた τ は 0・100・1,000 の下の方に集まった」。主のセルの hmm3 で選ばれた τ は 0 と 100 だけ（summary の `chosen_tau_other`）で、1,000 が出るのは k = 1 と CS1 だけ。
   - 2026-11-10 に 26 記号（q5_o）だけ確かめた: P15 k = 5・15 は 17 人とも 0、P30 k = 30 は 0 が 4 人・100 が 5 人。CoAuthor P15 k = 1 は 100 と 1,000、CS1 C5 k = 5 は 1,000 が 22 人・0 が 1 人。
   - 直し方: 10 記号と 50 記号の列も summary で確かめてから、「0 と 100 だけ」と書く。
3. **62 行（code-reviewer）**: 「26 記号のそのままの組（q5_o）の値は、前の 2 つの試験と同じである」。P-REPRO が照らしたのは、前の試験の summary に射影した葉（tau 6,741・mli 1,363）だけ。S0・G0r・D は前の試験に無い量。
   - 直し方: 「前の試験の summary と重なる葉（…）の値は同じである」と限る。
4. **100 行・判断 13 の 3 つ目（code-reviewer）**: 「共通の局所解の説明は、この結果からは寄与を分けられない（gap12 がほぼ並ぶ）」と、gap12 が小さいことを局所解の説明が残る根拠のように使っている。gap12 が小さいのは、上位 2 つの開始点が同じ尤度に落ちたということで、ふつうは悪い局所解の材料にならない。
   - 補足: 共通が悪い局所解にあれば、S0 は上がる側に動く。だから S0 が負という結果は、この説明では作れない（667 版の論理はこちら）。
   - 直し方: 向きを確かめ、文を直す。あわせて、CS1 の並べ替えた列の gap12（`pool_full_diag.hmm3.gap12`、10・26・50 記号で 1.2e-7・6.6e-9・0.0024。2026-11-10 に summary で確かめた）と、CS1 のそのままの列の 10 記号の gap12 が 0.133 と大きいことを添えるかを決める（添えるなら記述だけ）。

直すのは notes.md だけ。tables.md・読みの形・区切り（1/2・1/10）・条件・前の試験の notes は変えない。数値は summary を `python3 -I -c` で引いて確かめる（書き手ごとの値の pkl は開かない・Mac に無い）。

## 4 その後

1. 判断 14 を decisions.md に書く（(b) のレビューの記録と Codex の 2 回目の tokens、§3 の 4 件の扱い）。tasklist の「結果の後」に 2 巡目の行を足す。
2. code-reviewer と `/cross-review` の 2 巡目（Codex も加える）。範囲は `9d4edcba..<直しのコミット>`、`scripts/run-codex-review.sh <range> -- experiments/20261107-structure-deficit-test/notes.md`。Codex には、既に直した点と §3 の扱い（直した／直さない理由）を「既知の未決」として添え、判定に数えないよう頼む（memory: feedback-codex-gets-known-open-items）。CoAuthor・CS1 の記録と pkl は送らない。
3. `.codex/budget.json` の記帳と一緒にコミットする（`[skip ci]`）。push と PR は研究者が確かめてから。
4. **PR の順番は研究者に AskUserQuestion で聞く。** この枝は origin/main から 52 コミット先にいる。その下にある前の試験の 3 つの枝（`exp/gse-tau-mode-candidate`・`exp/gse-timeseries-tau-extend`・`exp/gse-coauthor-ml-improve`）は、2026-11-10 の時点でどれも origin/main に入っていない。このまま PR を出すと 4 つの試験が 1 つにまとまる。
5. 論文 3 への持ち込みは論文 3 の側（`docs/gse-paper3-per-person-learning` の枝・その判断 11）で行う。この枝では notes に書いた以上のことをしない。

## 5 守ること

- 前の引き継ぎ §7 と同じ（pkl・holdout を開かない、集計値だけ、書き手・セッション・課題の番号を書かない）。
- 結果を段 1 の候補の採否や ADR-047 の根拠にしない。EM の状態に名前を付けない。
- 返答・問いは日本語で。決めることは AskUserQuestion で 1 問ずつ、推奨と理由を添えて。記号を多用しない。
