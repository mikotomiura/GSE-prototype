# 引き継ぎ: 相対のタイミングの写像の机上の検査を G-GEAR で始める（タンジビリティ・案 D）

作成 2026-10-17（Windows・G-GEAR）。返答・記録・AskUserQuestion の引数は日本語で書く。記号（★・⚠️）は多用しない。AskUserQuestion には推奨と理由を添える。

元の引き継ぎは `origin/docs/tangibility-design` の `.steering/_handoff/next-session-tangibility-relative-timing-desk-check.md`（2026-10-15・Mac・2026-10-16 に G-GEAR での始め方を追記）。このメモはそれを置き換えず、始める条件と、その後（10-15〜10-17）に G-GEAR で分かったことを足す。問いの論点（元の §3 の 0〜6）は元のメモを全文で読む。

## 0. 始める条件と、新しいセッションで最初に打ち込む文

研究者の決定（2026-10-17）: 公開データでの照合の論文（PoPETs 2027 Issue 3・締切 2026-11-30 AoE・worktree `C:\GSE-wt-matching-prereg`）の重い処理（A4 の GPU の生成と CPU の本計算）が終わってから、価値があれば始める。CPU を本計算と取り合わないため。

始める前に一次で確かめる（どれかが満たされなければ始めず、研究者に状態を伝える）。

1. `Get-CimInstance Win32_Process` に `a4_keytar`・`a4_run_resumable`・照合の論文の本計算（`run_main.py` など）の処理が無い。
2. `C:\GSE-wt-matching-prereg\.steering\20261013-public-keystroke-matching-main\tasklist.md` の「本計算（主の表 500 人 → 補遺の全員）」が済んでいる。
3. `gh run list` で CI が走っていない（G-GEAR は self-hosted の Windows の runner を兼ねる）。

```
.steering/_handoff/next-session-tangibility-relative-timing-desk-check-ggear.md を読んで、§0 の条件を確かめてから、/start-task で相対のタイミングの机上の検査のタスクを立てて。
```

このメモはブランチ `docs/rhythm-stage-summary` にある（2026-10-17 の時点で PR なし）。背景のステージの 3 本（`docs/rhythm-stage-speed-confound` → `docs/rhythm-stage-speed-shape` → `docs/rhythm-stage-summary`）が main に入っていれば main から、入っていなければ `docs/rhythm-stage-summary` から作業のブランチを切る（計器が最新の段にあるため）。元のメモのある `docs/tangibility-design` は Mac のブランチで、G-GEAR では読むだけにする（`MSYS_NO_PATHCONV=1 git show origin/docs/tangibility-design:<パス>`）。

## 1. 価値の見立て（Claude・2026-10-17・決定ではない）

案 D は「打ち方の全体の速さを割り引いた相対のタイミング（間隔の比など）を形に写せば、速さを写さず、状態も写さない」という仮説の上にある（`.steering/20261015-tangibility-design/` 判断 14・17）。背景のステージの机上の検査では、打鍵 1 つずつの時刻から作ったテンポの秒ごとの揺れ（`r_absdiff`・`r_sd`）に、A_speed の要約を超える停滞の手がかりが残った（`.steering/20261017-rhythm-stage-summary/summary.md` §4。合成の world での結果・探索的な読みを含む）。相対のタイミングはこの種の量なので、仮説の (b)（停滞と速さを写さないか）は検査する価値がある。始めるときに、研究者にこの見立てを示して始めるかを聞く。

## 2. 元のメモ（10-15）の後に分かったこと（一次）

- **6 回のまとめ**: `.steering/20261017-rhythm-stage-summary/summary.md`。主表は `check_summary.py` が一次の JSON と照らす。
- **揺れの形の回**（元のメモでは「grill 済み」だった・10-17 に本番まで終わった）: `experiments/20261015-rhythm-stage-speed-shape-world/notes.md`。
  - 倍率だけの world `f(c)`（セッションごとの速さの倍率だけ・セッションの中では速さが揺れない）は、c = 1 で天井、c = 2 で 24 本のうち 16 本が判定不能（PC-stall が帯に届かない）。漂いだけの world `d(c)` では c = 1・2 とも L300 に赤が出た。
  - 案 D にとっては、`f(c)` は「全体の速さを割り引く写像なら、倍率に左右されないはず」を試す舞台になりうる。ただし今の作りでは A_speed が強く（`f(2)` の L300 の hgb 0.979）、判定不能が多い。
  - `r` の側を通る陽性の対照（PCr-level・PCr-var）がある（同 design §1.3）。相対のタイミングの写像の漏れを `r` の側で拾えるかの確かめに使える。
- **元の §3 の 0（重なり）について**: 描画の候補 `rank` は、駆動の値（打鍵の数・間隔から作る `u_a`・`u_r`）を「そのセッションのその時刻までの動いている時点の値の経験分位」に置き換える写像で（第 1 回 design §1.3）、セッションの中の順位だけを使う。セッション全体の速さの水準を割り引く点で相対のタイミングに近いが、打鍵の間隔の比そのものではない。揺れの world と揺れの形では、`rank` の `res=sub` は赤・未確認か赤・検出に入り、`R2` を落としてもほとんど下がらなかった（原因の切り分けの notes・揺れの形の notes）。この結果を、案 D の写像を立てる前の材料として読む。
- **計器の性質**: 下見 1 の時間の 6 割強が `rank` の候補だった（`d(1)`・揺れの形の notes）。λ の格子の上端（0.3）に張り付く候補は判定不能になりやすい。L60 は L300 の λ を当てるので判定不能が多い。1 段 約 14〜15 時間（下見・本番・読み）。
- **背景のステージの次の段**: 次のセッション（`next-session-rhythm-stage-next-step.md`）で、試作・机上でもう一段・保留を研究者が決める。案 D の検査と計器や問い（同じ world・同じ攻撃者）を共有するかもそこで考える。決まっていれば、その決定を先に読む。

## 3. 決めること（元の §3 に足すもの）

元の §3 の 0〜6（重なり・問いの立て方・相対のタイミングの定義・world・合格の定義・個人の再識別・個人ごとの読み手）に、次を足す。

- 基準: A_speed を基準にすると、停滞が打鍵の時刻に出る world では天井に当たる（中間の world）。元の §3 の 1 の立て直し（比べる基準は速さの写像）に加え、`f(c)`・`d(c)` のように速さの揺れを重ねた world を使うか。
- `rank` との関係: 案 D の写像を `rank` と並べて測るか（同じ world・同じ攻撃者・同じ陽性対照）。
- 計器の写し元: 揺れの形の計器（`experiments/20261015-rhythm-stage-speed-shape-world/`）を写して直すか。`rank` の遅さを固定の前に直すか（直すなら出力が変わらないことを確かめてから）。
- 所要: 1 段 約 15 時間 × 段の数。段を絞るか。

## 4. 守ること

- 元の §4（このトラックは今は論文にしない・notes は方法の章や付録に再利用できる形で残す）。
- 合成の列だけを使う。NDJSON の生ログ（合成も）・キーストロークの内容を外部の LLM（Codex を含む）に送らない。
- 背景のステージの 6 回とまとめの入れ物・判定・notes・design を書き換えない。`src-tauri/`・EH3 のファイルに触れない。
- Mac のブランチ（`docs/tangibility-design` ほか）を G-GEAR で書き換えない。
- 照合の論文の worktree（`C:\GSE-wt-matching-prereg`）と、その計算に触れない。
- `.codex/budget.json` を `git checkout --` で戻さない。回す前に worktree の台帳と origin/main の台帳を見る（予算ガードの hook は `C:\GSE-prototype` の台帳を読む）。
- `git add -A`・`git add <dir>` を使わない。計測の run の最中は PR を出さない（push だけ）。
- 設計は、どの結果（下見を含む）よりも前に固定する。固定の前に `/cross-review` 2 巡。
- バックグラウンドの実行の「completed」の通知は終わりより早く届くことがある。結果のファイルとログを一次で確かめてから報告する。
