# 次のセッション —— 背景のステージ: 人ごとのリズムの型を持つ world（個人の再識別・個人ごとの読み手）

> 書いた日: 2026-11-23（G-GEAR）。前のタスク: `.steering/20261122-rhythm-stage-relative-timing/`（相対のタイミングの写像・案 D の机上の検査）。そのタスクの判断 5 で、研究者が「人ごとのリズムの型を持つ world での検査は、このタスクが終わった後の次の段として行う」と決めた。このメモはその段の始め方である。

## 0. 始める前に確かめる（一次で）

1. ブランチ `docs/rhythm-stage-relative-timing` が main に入ったか、まだ枝のままかを `git fetch` してから確かめる。計器の写し元は、その時点で最新の `experiments/20261122-rhythm-stage-relative-timing/` にする。
2. 前のタスクの `notes.md`（`experiments/20261122-rhythm-stage-relative-timing/notes.md`）を**全文で**読む。1 節だけで代表させない。
3. 前のタスクの `decisions.md` の判断 5・14 と、design §1.2 の「塞がない道」、§3.3 への追加 (c2) を読む。
4. 研究者に、この段を今始めるか、ほかの段（照合の論文・手跡）を先にするかを聞く。

## 1. 前のタスクで分かったこと（合成の world の上だけ）

- 案 D の 2 本（`D-run-hold-sec`・`D-all-hold-sec`）は、`g050`・`f200` の両方で、基準 A（打鍵の有無）の上で `red_detected` だった（利得 0.22〜0.23）。読みは「案 D の画は打鍵の有無を超えて停滞を写した」で、「相対のタイミングで写した」とは書かない（design §3.3 への追加 (c2)）。
- 副の問い（A_speed の上）は 2 段とも判定できなかった。g050 は A_speed が天井で、f200 は A_speed の上で PC-stall が働かなかった（`weak_stall_pc`・λ は格子の上端 0.3）。
- 見込みと違った点として、f200 で案 D の画はセッションの倍率 `u` を R² 0.45〜0.47 で運んだ。その大半は滑らかさの 6 量（`a_sd`・`a_absdiff`・`a_ac1`・`r_sd`・`r_absdiff`・`r_ac1`）だけで出た（0.39〜0.42）。窓の統計量は倍率に不変でも、1 秒あたりの窓の入れ替わりを通して、秒ごとの系列の時間方向の量が速さを運ぶ（判断 14 の「塞がない道」）。
- 人ごとの違いに当たるものが倍率しか無い world で、倍率を運んだ。人ごとのリズムの型を持つ world で、画から人を再識別できるかを測る理由の 1 つになる（推論）。

## 2. この段で決めること（研究者と・grill）

- 人ごとのリズムの型をどう合成するか。これ自体が結果を決めるので、どの型を入れるか（速さの倍率・間隔の分布の形・burst の長さ・休止の型・2 つの間隔の相関など）と、型の大きさを、結果より前に固定する（判断 5 の理由）。
- 問い: (5) 個人の再識別（画の特徴から人を当てる・セッションを跨いで）と、(6) 個人ごとの読み手（人ごとに較正した攻撃者が停滞をどれだけ読めるか）。元の引き継ぎ（`origin/docs/tangibility-design:.steering/_handoff/next-session-tangibility-relative-timing-desk-check.md` §3 の 5・6）を全文で読んでから決める。
- 塞がない道への手当てを候補に入れるか（例: 秒ごとの値を作り直す間隔を打鍵の数で決める・滑らかさの量を描画に使わない）。入れるなら、前のタスクの案 D と並べる。
- f200 の副の問いを読むために、A_speed の上の PC-stall の格子を延ばすか（前のタスクの notes「逸脱・気づいたこと」）。

## 3. 進め方（前の 7 回と同じ型）

`/start-task` → grill → design → `/reimagine` → 計器を写して直す → 自己検査と変異 → 使い捨ての試作（本番と別の seed）で時間を測る → code-reviewer・security-checker を並列 → `/cross-review` 2 巡（パス限定・出力は scratchpad）→ 固定のコミット → 研究者の許可 → 下見 0 → 下見 1 → スモーク → 本番 → notes と `check_notes.py` → 引き継ぎ → `/finish-task`。

## 4. 守ること（CLAUDE.md と前のタスクから）

- 合成の列だけを使う。NDJSON（合成も）・キーストロークの内容を外部の LLM（Codex を含む）に送らない。Codex は repo を読めないので、資料はプロンプトに貼る。
- 前の 7 回とまとめの入れ物・判定・notes・design を書き換えない（写し元の dir で python を動かすときは `PYTHONDONTWRITEBYTECODE=1`）。`src-tauri/`・`src/`・EH3・Mac のブランチ・照合の論文の worktree に触れない。
- `.codex/budget.json` を `git checkout --` で戻さない。回す前に origin/main の台帳も見る。`git add -A`・`git add <dir>` を使わない。
- heredoc でクォートや複雑な置換を書かない。Python の置換は Write で .py を作るか Edit。書き戻しは `newline="\n"`。
- バックグラウンドの completed の通知を信じず、結果のファイルとログを一次で確かめる。
- 本番と同じ seed の列は固定の前に開かない。試作の値は design の判断に使わない。
- 計測の run の最中は PR を出さない（push だけ）。下見と本番の前に `gh run list` と重い処理が無いことを見て記録する。
- 返事・記録・AskUserQuestion の引数は日本語で、記号（★・⚠️）を控える。AskUserQuestion には推奨と理由を必ず添える。
